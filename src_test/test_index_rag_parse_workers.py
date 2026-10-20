# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""INDEX_PARSE_WORKERS: sequential default and opt-in parallel parsing.

Covers ``get_current_file_states`` (file scan + hashing) and the parse-ahead
thread of ``perform_refresh_qdrant``. Embedding, Qdrant and readers are faked,
so the tests stay CPU-light and never touch the GPU, TEI or real ports.
"""

from __future__ import annotations

import random
import threading
import time
import types
from pathlib import Path

import pytest

from src_test._index_rag_loader import (
    FakeQdrantClient,
    install_refresh_fakes,
    load_index_rag,
    make_fake_config,
)


@pytest.fixture
def env(tmp_path, monkeypatch):
    cfg = make_fake_config(tmp_path)
    mod = load_index_rag(cfg)
    return types.SimpleNamespace(mod=mod, cfg=cfg, tmp=tmp_path, mp=monkeypatch)


# ── get_current_file_states ─────────────────────────────────────────


def _make_tree(root: Path, count: int) -> Path:
    src = root / "proj"
    for i in range(count):
        sub = src / f"pkg{i % 5}"
        sub.mkdir(parents=True, exist_ok=True)
        (sub / f"m{i}.py").write_text(f"value = {i}\n", encoding="utf-8")
    (src / "notes.txt").write_text("not indexed\n", encoding="utf-8")
    return src


def _patch_sources(env, entries):
    env.mp.setattr(env.mod, "resolve_source_entries", lambda cfg: entries)
    env.mp.setattr(
        env.mod,
        "normalize_file_key",
        lambda base, rel, source_dir=None: f"proj/{rel}",
    )
    env.mp.setattr(env.mod, "sql_dialect_for_file", lambda sd, name: {})


def _entry(path: Path, **extra):
    return {"path": str(path), "extensions": [".py"], "exclude": [], "_entry_type": "local", **extra}


class TestFileStatesWorkers:
    def test_default_is_sequential(self, env):
        assert not hasattr(env.cfg, "INDEX_PARSE_WORKERS")
        src = _make_tree(env.tmp, 40)
        _patch_sources(env, [_entry(src)])

        def _boom(*a, **k):
            raise AssertionError("thread pool must not be used by default")

        env.mp.setattr(env.mod, "ThreadPoolExecutor", _boom)
        states = env.mod.get_current_file_states()
        assert len(states) == 40

    @pytest.mark.parametrize("workers", [2, 8, "4"])
    def test_parallel_matches_sequential(self, env, workers):
        src = _make_tree(env.tmp, 60)
        _patch_sources(env, [_entry(src)])
        env.cfg.INDEX_PARSE_WORKERS = 1
        sequential = env.mod.get_current_file_states()
        env.cfg.INDEX_PARSE_WORKERS = workers
        parallel = env.mod.get_current_file_states()
        assert parallel == sequential
        assert list(parallel) == list(sequential)  # same insertion order
        assert len(parallel) == 60
        state = parallel["proj/pkg0/m0.py"]
        assert set(state) >= {"file_path", "full_path", "mtime", "hash"}

    def test_parallel_pool_used_from_32_files(self, env):
        src = _make_tree(env.tmp, 32)
        _patch_sources(env, [_entry(src)])
        env.cfg.INDEX_PARSE_WORKERS = 4
        used: list[int] = []
        real_pool = env.mod.ThreadPoolExecutor

        def _spy(max_workers=None, **kw):
            used.append(max_workers)
            return real_pool(max_workers=max_workers, **kw)

        env.mp.setattr(env.mod, "ThreadPoolExecutor", _spy)
        env.mod.get_current_file_states()
        assert used == [4]

    def test_small_source_stays_sequential(self, env):
        src = _make_tree(env.tmp, 31)
        _patch_sources(env, [_entry(src)])
        env.cfg.INDEX_PARSE_WORKERS = 8

        def _boom(*a, **k):
            raise AssertionError("pool not expected below 32 files")

        env.mp.setattr(env.mod, "ThreadPoolExecutor", _boom)
        assert len(env.mod.get_current_file_states()) == 31

    @pytest.mark.parametrize("bad", [0, -3, None])
    def test_invalid_low_values_fall_back_to_sequential(self, env, bad):
        src = _make_tree(env.tmp, 40)
        _patch_sources(env, [_entry(src)])
        env.cfg.INDEX_PARSE_WORKERS = bad

        def _boom(*a, **k):
            raise AssertionError("pool not expected")

        env.mp.setattr(env.mod, "ThreadPoolExecutor", _boom)
        assert len(env.mod.get_current_file_states()) == 40

    def test_non_numeric_value_fails_fast(self, env):
        _patch_sources(env, [])
        env.cfg.INDEX_PARSE_WORKERS = "many"
        with pytest.raises(ValueError):
            env.mod.get_current_file_states()

    @pytest.mark.parametrize("workers", [1, 4])
    def test_unreadable_file_is_skipped(self, env, workers):
        src = _make_tree(env.tmp, 40)
        _patch_sources(env, [_entry(src)])
        env.cfg.INDEX_PARSE_WORKERS = workers
        real_hash = env.mod.compute_file_hash

        def _hash(path):
            if Path(path).name == "m7.py":
                raise OSError("simulated read error")
            return real_hash(path)

        env.mp.setattr(env.mod, "compute_file_hash", _hash)
        states = env.mod.get_current_file_states()
        assert len(states) == 39
        assert "proj/pkg2/m7.py" not in states

    def test_missing_source_dir_is_skipped(self, env):
        _patch_sources(env, [_entry(env.tmp / "does-not-exist")])
        assert env.mod.get_current_file_states() == {}

    @pytest.mark.parametrize("flag, expected", [(None, True), (True, True), (False, False)])
    def test_respect_gitignore_flag_is_forwarded(self, env, flag, expected):
        src = _make_tree(env.tmp, 3)
        entry = _entry(src, _entry_type="git_repo", _repo_path=str(src))
        _patch_sources(env, [entry])
        if flag is not None:
            env.cfg.RESPECT_GITIGNORE = flag
        seen: list[bool] = []

        def _filter(files, source_dir, *, respect_gitignore=True):
            seen.append(respect_gitignore)
            return [f for f in files if f.name != "m1.py"]

        env.mp.setattr(env.mod, "filter_out_gitignored", _filter)
        states = env.mod.get_current_file_states()
        assert seen == [expected]
        assert "proj/pkg1/m1.py" not in states
        assert len(states) == 2


# ── perform_refresh_qdrant parse-ahead thread ──────────────────────


def _make_files(root: Path, count: int) -> dict[str, dict]:
    states = {}
    for i in range(count):
        p = root / f"f{i:03d}.py"
        p.write_text(f"def f{i}():\n    return {i}\n", encoding="utf-8")
        key = f"proj/f{i:03d}.py"
        states[key] = {"file_path": key, "full_path": str(p), "mtime": 0, "hash": f"h{i}"}
    return states


def _node_loader(threads_seen=None, jitter=False, fail_key=None, empty_key=None):
    from llama_index.core.schema import TextNode

    rnd = random.Random(1234)

    def _load(info):
        if threads_seen is not None:
            threads_seen.add(threading.current_thread().name)
        key = info["file_path"]
        if jitter:
            time.sleep(rnd.random() * 0.004)
        if key == fail_key:
            raise RuntimeError(f"simulated parse failure in {key}")
        if key == empty_key:
            return []
        return [
            TextNode(text=f"{key} chunk {j}", metadata={"file_path": key})
            for j in range(2)
        ]

    return _load


def _refresh(env, states, *, workers, loader, add=None, modify=None):
    if workers is not _UNSET:
        env.cfg.INDEX_PARSE_WORKERS = workers
    client = FakeQdrantClient()
    order: list[str] = []
    install_refresh_fakes(
        env.mod,
        env.mp,
        client,
        load_nodes=loader,
        on_parsed=lambda docs: order.append(docs[0].split(" ")[0]),
    )
    manifest = {"files": {}}
    env.mod.perform_refresh_qdrant(
        actions={
            "add": list(states) if add is None else add,
            "modify": modify or [],
            "delete": [],
        },
        manifest=manifest,
        file_states=states,
        save_fn=lambda m: None,
    )
    return client, manifest, order


_UNSET = object()


class TestParseAheadWorkers:
    def test_default_parses_on_single_parse_ahead_thread(self, env):
        states = _make_files(env.tmp, 12)
        threads: set[str] = set()
        _, manifest, order = _refresh(env, states, workers=_UNSET, loader=_node_loader(threads))
        assert threads == {"parse-ahead"}
        assert order == list(states)
        assert sorted(manifest["files"]) == sorted(states)

    @pytest.mark.parametrize("bad", [0, -2, None])
    def test_invalid_low_values_stay_sequential(self, env, bad):
        states = _make_files(env.tmp, 6)
        threads: set[str] = set()
        _, manifest, _ = _refresh(env, states, workers=bad, loader=_node_loader(threads))
        assert threads == {"parse-ahead"}
        assert len(manifest["files"]) == 6

    def test_non_numeric_value_fails_fast(self, env):
        states = _make_files(env.tmp, 2)
        with pytest.raises(ValueError):
            _refresh(env, states, workers="many", loader=_node_loader())

    def test_non_numeric_value_fails_before_hnsw_is_deferred(self, env):
        # A bad INDEX_PARSE_WORKERS must not leave the collection with HNSW
        # indexing deferred (indexing_threshold raised and never restored).
        states = _make_files(env.tmp, 2)
        client = FakeQdrantClient()
        install_refresh_fakes(env.mod, env.mp, client, load_nodes=_node_loader())
        env.cfg.INDEX_PARSE_WORKERS = "many"
        with pytest.raises(ValueError):
            env.mod.perform_refresh_qdrant(
                actions={"add": list(states), "modify": [], "delete": []},
                manifest={"files": {}},
                file_states=states,
                save_fn=lambda m: None,
            )
        assert client.update_collection_calls == []

    @pytest.mark.parametrize("workers", [1, 4])
    def test_hnsw_deferred_then_restored_on_success(self, env, workers):
        states = _make_files(env.tmp, 3)
        client, _, _ = _refresh(env, states, workers=workers, loader=_node_loader())
        thresholds = [
            c["optimizers_config"].indexing_threshold
            for c in client.update_collection_calls
        ]
        assert thresholds == [200_000, 10_000]

    @pytest.mark.parametrize("workers", [2, 8])
    def test_parallel_is_deterministic(self, env, workers):
        states = _make_files(env.tmp, 50)
        base_client, base_manifest, base_order = _refresh(
            env, states, workers=1, loader=_node_loader()
        )
        threads: set[str] = set()
        client, manifest, order = _refresh(
            env, states, workers=workers, loader=_node_loader(threads, jitter=True)
        )
        assert any(t != "parse-ahead" for t in threads), "pool threads expected"
        assert order == base_order == list(states)
        assert client.upserted_ids == base_client.upserted_ids
        assert manifest == base_manifest

    @pytest.mark.parametrize("workers", [1, 4])
    def test_skips_keys_without_state(self, env, workers):
        states = _make_files(env.tmp, 5)
        add = ["proj/missing.py"] + list(states)
        _, manifest, order = _refresh(
            env, states, workers=workers, loader=_node_loader(), add=add
        )
        assert "proj/missing.py" not in order
        assert sorted(manifest["files"]) == sorted(states)

    def test_parallel_only_missing_states(self, env):
        _, manifest, order = _refresh(
            env, {}, workers=4, loader=_node_loader(), add=["proj/a.py", "proj/b.py"]
        )
        assert order == [] and manifest["files"] == {}

    @pytest.mark.parametrize("workers", [1, 4])
    def test_parse_exception_propagates(self, env, workers):
        states = _make_files(env.tmp, 20)
        loader = _node_loader(fail_key="proj/f010.py")
        with pytest.raises(RuntimeError, match="simulated parse failure"):
            _refresh(env, states, workers=workers, loader=loader)

    @pytest.mark.parametrize("workers", [1, 4])
    def test_empty_file_recorded_in_manifest(self, env, workers):
        states = _make_files(env.tmp, 6)
        Path(states["proj/f002.py"]["full_path"]).write_text("", encoding="utf-8")
        _, manifest, _ = _refresh(
            env, states, workers=workers, loader=_node_loader(empty_key="proj/f002.py")
        )
        assert manifest["files"]["proj/f002.py"].get("empty") is True

    @pytest.mark.parametrize("workers", [1, 4])
    def test_no_content_file_recorded_in_manifest(self, env, workers):
        states = _make_files(env.tmp, 6)
        _, manifest, _ = _refresh(
            env, states, workers=workers, loader=_node_loader(empty_key="proj/f003.py")
        )
        assert manifest["files"]["proj/f003.py"].get("no_content") is True

    def test_vanished_file_counts_as_no_content(self, env):
        states = _make_files(env.tmp, 3)
        Path(states["proj/f001.py"]["full_path"]).unlink()
        _, manifest, _ = _refresh(
            env, states, workers=1, loader=_node_loader(empty_key="proj/f001.py")
        )
        assert manifest["files"]["proj/f001.py"].get("no_content") is True

    def test_action_type_add_vs_modify(self, env):
        states = _make_files(env.tmp, 4)
        keys = list(states)
        _, manifest, order = _refresh(
            env, states, workers=4, loader=_node_loader(), add=keys[:2], modify=keys[2:]
        )
        assert order == keys
        assert sorted(manifest["files"]) == sorted(keys)


class TestConfigDefaults:
    """Defaults in the base config.py keep the pre-0.12 behaviour."""

    @staticmethod
    def _assignments():
        import ast

        root = Path(__file__).resolve().parent.parent
        tree = ast.parse((root / "config.py").read_text(encoding="utf-8"))
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    try:
                        values[target.id] = ast.literal_eval(node.value)
                    except ValueError:
                        pass
        return values

    def test_index_parse_workers_defaults_to_one(self):
        assert self._assignments()["INDEX_PARSE_WORKERS"] == 1

    def test_delete_chunk_size_default(self):
        assert self._assignments()["QDRANT_DELETE_CHUNK_SIZE"] == 500

    def test_respect_gitignore_default_true(self):
        assert self._assignments()["RESPECT_GITIGNORE"] is True
