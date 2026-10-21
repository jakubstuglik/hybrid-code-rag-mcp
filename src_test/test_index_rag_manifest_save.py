# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""MANIFEST_SAVE_INTERVAL_S: manifest saves in ``perform_refresh_qdrant``.

The default (``0``) must keep the classic save-after-every-batch behaviour.
A positive interval throttles periodic saves onto a background thread, and
the end of a run and a failed run always save synchronously. Embedding,
Qdrant and readers are faked (no GPU, TEI or network).
"""

from __future__ import annotations

import json
import threading
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
    # Small pools so a run has many batches (and therefore many save points).
    cfg = make_fake_config(tmp_path, EMBED_POOL_MAX_FILES=5)
    mod = load_index_rag(cfg)
    return types.SimpleNamespace(mod=mod, cfg=cfg, tmp=tmp_path, mp=monkeypatch)


def _make_files(root: Path, count: int) -> dict[str, dict]:
    states = {}
    for i in range(count):
        p = root / f"f{i:03d}.py"
        p.write_text(f"def f{i}():\n    return {i}\n", encoding="utf-8")
        key = f"proj/f{i:03d}.py"
        states[key] = {
            "file_path": key,
            "full_path": str(p),
            "mtime": 0,
            "hash": f"h{i}",
        }
    return states


def _loader(fail_key=None, interrupt_key=None):
    from llama_index.core.schema import TextNode

    def _load(info):
        key = info["file_path"]
        if key == fail_key:
            raise RuntimeError(f"simulated parse failure in {key}")
        return [
            TextNode(text=f"{key} chunk {j}", metadata={"file_path": key})
            for j in range(2)
        ]

    return _load


class _SaveLog:
    """save_fn recording a deep copy, the thread, and Qdrant state at save time."""

    def __init__(self, client: FakeQdrantClient):
        self.client = client
        self.copies: list[dict] = []
        self.threads: list[str] = []
        self.upserted_at_save: list[set[str]] = []
        self.active = 0
        self.max_active = 0
        self._lock = threading.Lock()

    def __call__(self, m):
        with self._lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        try:
            self.upserted_at_save.append(set(self.client.upserted_ids))
            self.copies.append(json.loads(json.dumps(m)))
            self.threads.append(threading.current_thread().name)
        finally:
            with self._lock:
                self.active -= 1


def _run(
    env, states, *, interval=None, depth=0, loader=None, manifest=None, delete=None
):
    if interval is not None:
        env.cfg.MANIFEST_SAVE_INTERVAL_S = interval
    env.cfg.EMBED_PIPELINE_DEPTH = depth
    client = FakeQdrantClient()
    install_refresh_fakes(env.mod, env.mp, client, load_nodes=loader or _loader())
    saves = _SaveLog(client)
    manifest = manifest if manifest is not None else {"files": {}}
    env.mod.perform_refresh_qdrant(
        actions={"add": list(states), "modify": [], "delete": list(delete or [])},
        manifest=manifest,
        file_states=states,
        save_fn=saves,
    )
    return client, manifest, saves


def _assert_never_claims_missing_points(saves: _SaveLog) -> None:
    for copy, upserted in zip(saves.copies, saves.upserted_at_save):
        for key, entry in copy["files"].items():
            missing = set(entry.get("vector_ids", [])) - upserted
            assert not missing, f"{key} claims points not upserted yet: {missing}"


class TestDefaultKeepsClassicBehaviour:
    @pytest.mark.parametrize("depth", [0, 2])
    def test_unset_equals_explicit_zero(self, env, depth):
        states = _make_files(env.tmp, 40)
        _, m_unset, s_unset = _run(env, states, depth=depth)
        assert not hasattr(env.cfg, "MANIFEST_SAVE_INTERVAL_S")
        _, m_zero, s_zero = _run(env, states, interval=0, depth=depth)
        assert m_unset == m_zero
        assert len(s_unset.copies) == len(s_zero.copies)

    @pytest.mark.parametrize("depth", [0, 2])
    def test_saves_after_every_batch_on_main_thread(self, env, depth):
        states = _make_files(env.tmp, 40)
        _, manifest, saves = _run(env, states, depth=depth)
        # 40 files / save batch of 10 -> at least 4 periodic saves + final save
        assert len(saves.copies) >= 5
        assert set(saves.threads) == {threading.current_thread().name}
        assert sorted(saves.copies[-1]["files"]) == sorted(states)
        assert manifest == saves.copies[-1]
        # periodic saves show progress (not only the final one)
        sizes = [len(c["files"]) for c in saves.copies]
        assert sizes == sorted(sizes) and sizes[0] < len(states)

    def test_failure_does_not_add_a_save(self, env):
        # Classic mode never saved on the error path; keep it that way.
        states = _make_files(env.tmp, 3)
        client = FakeQdrantClient()
        install_refresh_fakes(
            env.mod, env.mp, client, load_nodes=_loader(fail_key="proj/f000.py")
        )
        saves = _SaveLog(client)
        with pytest.raises(RuntimeError):
            env.mod.perform_refresh_qdrant(
                actions={"add": list(states), "modify": [], "delete": []},
                manifest={"files": {}},
                file_states=states,
                save_fn=saves,
            )
        assert saves.copies == []


class TestIntervalMode:
    @pytest.mark.parametrize("depth", [0, 2])
    def test_long_interval_only_final_sync_save(self, env, depth):
        states = _make_files(env.tmp, 40)
        _, manifest, saves = _run(env, states, interval=3600, depth=depth)
        assert len(saves.copies) == 2  # after the loop + end of run
        assert set(saves.threads) == {threading.current_thread().name}
        assert sorted(saves.copies[-1]["files"]) == sorted(states)
        assert saves.copies[-1] == manifest

    @pytest.mark.parametrize("depth", [0, 2])
    def test_tiny_interval_saves_in_background_consistently(self, env, depth):
        states = _make_files(env.tmp, 60)
        _, manifest, saves = _run(env, states, interval=1e-9, depth=depth)
        bg = [t for t in saves.threads if t.startswith("manifest-save")]
        assert bg, "periodic saves expected on the background thread"
        assert saves.threads[-1] == threading.current_thread().name  # final is sync
        assert saves.max_active == 1
        assert saves.copies[-1] == manifest
        _assert_never_claims_missing_points(saves)

    @pytest.mark.parametrize("depth", [0, 2])
    def test_same_final_manifest_and_points_as_default(self, env, depth):
        states = _make_files(env.tmp, 33)
        c0, m0, _ = _run(env, states, interval=0, depth=depth)
        c1, m1, _ = _run(env, states, interval=1e-9, depth=depth)
        assert m0 == m1
        assert sorted(c0.upserted_ids) == sorted(c1.upserted_ids)

    @pytest.mark.parametrize("depth", [0, 2])
    def test_exception_saves_progress_synchronously(self, env, depth):
        states = _make_files(env.tmp, 30)
        client = FakeQdrantClient()
        env.cfg.MANIFEST_SAVE_INTERVAL_S = 3600
        env.cfg.EMBED_PIPELINE_DEPTH = depth
        install_refresh_fakes(
            env.mod, env.mp, client, load_nodes=_loader(fail_key="proj/f020.py")
        )
        saves = _SaveLog(client)
        manifest = {"files": {}}
        with pytest.raises(RuntimeError, match="simulated parse failure"):
            env.mod.perform_refresh_qdrant(
                actions={"add": list(states), "modify": [], "delete": []},
                manifest=manifest,
                file_states=states,
                save_fn=saves,
            )
        assert len(saves.copies) == 1  # the failure-path save
        assert saves.threads == [threading.current_thread().name]
        # With EMBED_PIPELINE_DEPTH=0 a background upsert may still finish and
        # record its files after the failure save; the save is then a subset.
        assert set(saves.copies[0]["files"]) <= set(manifest["files"])
        assert saves.copies[0]["files"], "progress before the failure is kept"
        assert "proj/f025.py" not in saves.copies[0]["files"]
        _assert_never_claims_missing_points(saves)

    def test_keyboard_interrupt_saves_and_propagates(self, env):
        states = _make_files(env.tmp, 20)
        client = FakeQdrantClient()
        env.cfg.MANIFEST_SAVE_INTERVAL_S = 3600
        install_refresh_fakes(env.mod, env.mp, client, load_nodes=_loader())
        calls = {"n": 0}

        def _embed(model, docs, **kw):
            calls["n"] += 1
            if calls["n"] == 3:
                raise KeyboardInterrupt
            return [[0.1, 0.2, 0.3] for _ in docs]

        env.mp.setattr(env.mod, "embed_dense_batch", _embed)
        saves = _SaveLog(client)
        manifest = {"files": {}}
        with pytest.raises(KeyboardInterrupt):
            env.mod.perform_refresh_qdrant(
                actions={"add": list(states), "modify": [], "delete": []},
                manifest=manifest,
                file_states=states,
                save_fn=saves,
            )
        assert len(saves.copies) == 1
        assert 0 < len(saves.copies[0]["files"]) < len(states)
        _assert_never_claims_missing_points(saves)

    def test_failure_save_error_keeps_original_exception(self, env):
        states = _make_files(env.tmp, 3)
        env.cfg.MANIFEST_SAVE_INTERVAL_S = 3600
        client = FakeQdrantClient()
        install_refresh_fakes(
            env.mod, env.mp, client, load_nodes=_loader(fail_key="proj/f001.py")
        )

        def _boom(m):
            raise OSError("disk full")

        with pytest.raises(RuntimeError, match="simulated parse failure"):
            env.mod.perform_refresh_qdrant(
                actions={"add": list(states), "modify": [], "delete": []},
                manifest={"files": {}},
                file_states=states,
                save_fn=_boom,
            )

    def test_deletes_are_persisted_immediately(self, env):
        manifest = {"files": {"proj/gone.py": {"vector_ids": ["x"]}}}
        _, manifest, saves = _run(
            env, {}, interval=3600, manifest=manifest, delete=["proj/gone.py"]
        )
        assert saves.copies[0]["files"] == {}

    def test_invalid_value_fails_before_touching_collection(self, env):
        states = _make_files(env.tmp, 2)
        env.cfg.MANIFEST_SAVE_INTERVAL_S = "soon"
        client = FakeQdrantClient()
        install_refresh_fakes(env.mod, env.mp, client, load_nodes=_loader())
        with pytest.raises(ValueError):
            env.mod.perform_refresh_qdrant(
                actions={"add": list(states), "modify": [], "delete": []},
                manifest={"files": {}},
                file_states=states,
                save_fn=lambda m: None,
            )
        assert client.update_collection_calls == []
        assert client.upserted_ids == []


class TestManifestFiles:
    def test_default_writes_classic_indented_json(self, env):
        m = {"files": {"proj/a.py": {"file_path": "proj/a.py", "vector_ids": ["1"]}}}
        env.mod.save_manifest(m)
        raw = env.mod.get_manifest_path().read_text(encoding="utf-8")
        assert raw == json.dumps(m, indent=2, sort_keys=True)

    def test_interval_writes_compact_and_loads_back(self, env):
        env.cfg.MANIFEST_SAVE_INTERVAL_S = 60
        env.mp.setattr(env.mod, "normalize_manifest_key", lambda p: p)
        m = {
            "files": {
                "proj/a.py": {
                    "file_path": "proj/a.py",
                    "mtime": 1,
                    "hash": "h",
                    "vector_ids": ["1"],
                }
            }
        }
        env.mod.save_manifest(m)
        path = env.mod.get_manifest_path()
        raw = path.read_bytes()
        assert b"\n" not in raw and b": " not in raw
        assert env.mod.load_manifest() == m
        assert not [p for p in path.parent.iterdir() if p.name.endswith(".tmp")]

    def test_save_logs_timing(self, env):
        lines = []
        env.mp.setattr(env.mod, "log", lines.append)
        env.mod.save_manifest({"files": {"a": {}}})
        assert any(
            line.startswith("[MANIFEST] main: saved 1 files") and " in " in line
            for line in lines
        )

    def test_none_manifest_is_noop(self, env):
        env.mod.save_manifest(None)
        assert not env.mod.get_manifest_path().exists()

    @pytest.mark.parametrize("interval", [0, 60])
    def test_branch_manifest_round_trip(self, env, interval):
        env.cfg.MANIFEST_SAVE_INTERVAL_S = interval
        env.mp.setattr(
            env.mod,
            "_get_branch_manifest_path",
            lambda b: env.tmp / "index" / f"index_manifest_branch_{b}.json",
        )
        m = {"branch": "feat", "files": {"a": {"vector_ids": ["1"]}}, "tombstones": []}
        env.mod._save_branch_manifest("feat", m)
        assert env.mod._load_branch_manifest("feat") == m
        raw = (env.tmp / "index" / "index_manifest_branch_feat.json").read_text()
        assert ("\n" in raw) is (interval == 0)


class TestConfigDefault:
    def test_base_config_default_is_zero(self):
        import ast

        root = Path(__file__).resolve().parent.parent
        tree = ast.parse((root / "config.py").read_text(encoding="utf-8"))
        values = {
            node.targets[0].id: node.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        }
        assert ast.literal_eval(values["MANIFEST_SAVE_INTERVAL_S"]) == 0
