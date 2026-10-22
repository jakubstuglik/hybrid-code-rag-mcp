# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Start-up of an index run: one source scan, and LOG_REFRESH_CHANGES_MAX.

``run_full_indexing`` / ``run_refresh_indexing`` scan the sources once and
hand the states to ``perform_refresh_qdrant``; a second scan used to re-walk
and re-hash the whole tree before the first embedding request.
``LOG_REFRESH_CHANGES_MAX`` caps the per-action path list of the change
summary (0 = list all, the default). Embedding, Qdrant and readers are faked.
"""

from __future__ import annotations

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


def _states(root: Path, count: int) -> dict[str, dict]:
    states = {}
    for i in range(count):
        p = root / f"f{i:03d}.py"
        p.write_text(f"def f{i}():\n    return {i}\n", encoding="utf-8")
        key = f"proj/f{i:03d}.py"
        states[key] = {"file_path": key, "full_path": str(p), "mtime": 0, "hash": f"h{i}"}
    return states


def _loader():
    from llama_index.core.schema import TextNode

    def _load(info):
        return [TextNode(text=f"{info['file_path']} chunk", metadata={"file_path": info["file_path"]})]

    return _load


class _Scan:
    def __init__(self, states):
        self.states = states
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return dict(self.states)


def _wire(env, states):
    client = FakeQdrantClient()
    install_refresh_fakes(env.mod, env.mp, client, load_nodes=_loader())
    scan = _Scan(states)
    env.mp.setattr(env.mod, "get_current_file_states", scan)
    env.mp.setattr(env.mod, "resolve_source_entries", lambda cfg: [])
    env.mp.setattr(env.mod, "_finalize_manifest_bookkeeping", lambda m, mode: None)
    saved = []
    env.mp.setattr(env.mod, "save_manifest", lambda m: saved.append(len(m["files"])))
    seen = {}
    real = env.mod.perform_refresh_qdrant

    def _spy(actions, manifest, **kw):
        seen.update(kw)
        return real(actions, manifest, **kw)

    env.mp.setattr(env.mod, "perform_refresh_qdrant", _spy)
    return client, scan, seen, saved


class TestScanOnce:
    def test_full_indexing_scans_once(self, env):
        states = _states(env.tmp, 7)
        client, scan, seen, _ = _wire(env, states)
        env.mod.run_full_indexing()
        assert scan.calls == 1
        assert seen["file_states"] == states
        assert len(client.upserted_ids) == 7

    def test_refresh_indexing_scans_once(self, env):
        states = _states(env.tmp, 5)
        client, scan, seen, _ = _wire(env, states)
        manifest = {"files": {"proj/gone.py": {"hash": "x", "vector_ids": []}}}
        env.mp.setattr(env.mod, "load_manifest", lambda: manifest)
        env.mod.run_refresh_indexing()
        assert scan.calls == 1
        assert seen["file_states"] == states
        assert len(client.upserted_ids) == 5
        assert "proj/gone.py" not in manifest["files"]

    def test_refresh_without_manifest_routes_to_full_and_scans_once(self, env):
        states = _states(env.tmp, 3)
        _, scan, _, _ = _wire(env, states)
        env.mp.setattr(env.mod, "load_manifest", lambda: None)
        env.mod.run_refresh_indexing()
        assert scan.calls == 1

    def test_refresh_noop_scans_once_and_skips_refresh(self, env):
        states = _states(env.tmp, 2)
        _, scan, seen, _ = _wire(env, states)
        manifest = {"files": {k: {"hash": v["hash"]} for k, v in states.items()}}
        env.mp.setattr(env.mod, "load_manifest", lambda: manifest)
        env.mod.run_refresh_indexing()
        assert scan.calls == 1 and seen == {}

    def test_perform_refresh_without_states_still_scans(self, env):
        # Direct callers that pass no states keep the old behaviour.
        states = _states(env.tmp, 4)
        client, scan, _, _ = _wire(env, states)
        env.mod.perform_refresh_qdrant(
            {"add": list(states), "modify": [], "delete": []}, {"files": {}}
        )
        assert scan.calls == 1
        assert len(client.upserted_ids) == 4


# ── LOG_REFRESH_CHANGES_MAX ─────────────────────────────────────────


def _log_env(env, n_add=0, n_mod=0, n_del=0):
    lines: list[str] = []
    env.mp.setattr(env.mod, "log_raw", lambda msg="": lines.append(str(msg)))
    env.mp.setattr(
        env.mod, "resolve_source_entries", lambda cfg: [{"path": "proj"}, {"path": "lib"}]
    )
    add = [f"proj/a{i}.py" for i in range(n_add)] + [f"lib/b{i}.py" for i in range(n_add)]
    mod = [f"proj/m{i}.py" for i in range(n_mod)]
    dele = [f"lib/d{i}.py" for i in range(n_del)]
    states = {k: {"file_path": k} for k in add + mod}
    old = {k: {"file_path": k} for k in dele}
    actions = {"add": add, "modify": mod, "delete": dele}
    return lines, actions, states, old


def _paths(lines):
    return [ln.strip()[2:] for ln in lines if ln.strip().startswith("- ")]


class TestLogRefreshChangesMax:
    def test_default_lists_everything_exactly_as_before(self, env):
        lines, actions, states, old = _log_env(env, n_add=3, n_mod=2, n_del=2)
        assert not hasattr(env.cfg, "LOG_REFRESH_CHANGES_MAX")
        env.mod.log_refresh_changes(actions, states, old)
        assert lines == [
            "\n  [ADD]",
            "    proj: 3",
            "      - proj/a0.py",
            "      - proj/a1.py",
            "      - proj/a2.py",
            "    lib: 3",
            "      - lib/b0.py",
            "      - lib/b1.py",
            "      - lib/b2.py",
            "\n  [MODIFY]",
            "    proj: 2",
            "      - proj/m0.py",
            "      - proj/m1.py",
            "\n  [DELETE]",
            "    lib: 2",
            "      - lib/d0.py",
            "      - lib/d1.py",
        ]

    @pytest.mark.parametrize("raw", [0, "0", -5, None, "abc", True])
    def test_zero_negative_or_invalid_means_unlimited(self, env, raw):
        lines, actions, states, old = _log_env(env, n_add=4)
        env.cfg.LOG_REFRESH_CHANGES_MAX = raw
        env.mod.log_refresh_changes(actions, states, old)
        assert len(_paths(lines)) == 8
        assert not any("more" in ln for ln in lines)

    def test_cap_spans_groups_per_action(self, env):
        lines, actions, states, old = _log_env(env, n_add=4, n_mod=3, n_del=1)
        env.cfg.LOG_REFRESH_CHANGES_MAX = 5
        env.mod.log_refresh_changes(actions, states, old)
        paths = _paths(lines)
        # ADD: 5 of 8 (4 proj + 1 lib); MODIFY: all 3; DELETE: 1
        assert paths == [
            "proj/a0.py", "proj/a1.py", "proj/a2.py", "proj/a3.py", "lib/b0.py",
            "proj/m0.py", "proj/m1.py", "proj/m2.py",
            "lib/d0.py",
        ]
        # group counts still report the full totals
        assert "    proj: 4" in lines and "    lib: 4" in lines
        more = [ln for ln in lines if "more" in ln]
        assert more == [
            "    ... 3 more add path(s) not listed "
            "(LOG_REFRESH_CHANGES_MAX=5; VERBOSE lists all)"
        ]

    def test_cap_of_one(self, env):
        lines, actions, states, old = _log_env(env, n_add=2)
        env.cfg.LOG_REFRESH_CHANGES_MAX = 1
        env.mod.log_refresh_changes(actions, states, old)
        assert _paths(lines) == ["proj/a0.py"]
        assert any("3 more add" in ln for ln in lines)

    def test_cap_larger_than_list_prints_all_without_note(self, env):
        lines, actions, states, old = _log_env(env, n_add=2, n_del=2)
        env.cfg.LOG_REFRESH_CHANGES_MAX = 50
        env.mod.log_refresh_changes(actions, states, old)
        assert len(_paths(lines)) == 6
        assert not any("more" in ln for ln in lines)

    def test_cap_equal_to_list_prints_all_without_note(self, env):
        lines, actions, states, old = _log_env(env, n_add=2)
        env.cfg.LOG_REFRESH_CHANGES_MAX = 4
        env.mod.log_refresh_changes(actions, states, old)
        assert len(_paths(lines)) == 4
        assert not any("more" in ln for ln in lines)

    def test_verbose_lists_everything(self, env):
        lines, actions, states, old = _log_env(env, n_add=4)
        env.cfg.LOG_REFRESH_CHANGES_MAX = 1
        env.mp.setattr(env.mod, "VERBOSE", True)
        env.mod.log_refresh_changes(actions, states, old)
        assert len(_paths(lines)) == 8

    def test_branch_suffix_kept_on_listed_paths(self, env):
        lines, actions, states, old = _log_env(env, n_add=2)
        env.cfg.LOG_REFRESH_CHANGES_MAX = 1
        env.mod.log_refresh_changes(actions, states, old, branch_label="feature/x")
        assert _paths(lines) == ["proj/a0.py [feature/x]"]

    def test_empty_actions_print_nothing(self, env):
        lines, actions, states, old = _log_env(env)
        env.cfg.LOG_REFRESH_CHANGES_MAX = 3
        env.mod.log_refresh_changes(actions, states, old)
        assert lines == []


class TestConfigDefaults:
    def test_base_config_defaults_keep_old_behaviour(self):
        import ast

        root = Path(__file__).resolve().parent.parent
        tree = ast.parse((root / "config.py").read_text(encoding="utf-8"))
        values = {
            node.targets[0].id: ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id
            in ("LOG_REFRESH_CHANGES_MAX", "SYMBOLS_PER_SPLIT_PART", "SYMBOLS_MAX_PER_CHUNK")
        }
        assert values == {
            "LOG_REFRESH_CHANGES_MAX": 0,
            "SYMBOLS_PER_SPLIT_PART": False,
            "SYMBOLS_MAX_PER_CHUNK": 0,
        }

    @pytest.mark.parametrize(
        "raw,expected", [(None, 0), (0, 0), (7, 7), ("12", 12), (-1, 0), ("x", 0), (True, 0), (2.9, 2)]
    )
    def test_refresh_changes_log_limit_parsing(self, env, raw, expected):
        cfg = types.SimpleNamespace(LOG_REFRESH_CHANGES_MAX=raw)
        assert env.mod.refresh_changes_log_limit(cfg) == expected
        assert env.mod.refresh_changes_log_limit(types.SimpleNamespace()) == 0
