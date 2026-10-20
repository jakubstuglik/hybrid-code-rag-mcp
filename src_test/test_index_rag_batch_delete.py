# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Batched Qdrant deletes (QDRANT_DELETE_CHUNK_SIZE + MatchAny) in index_rag.

Covers both callers:
- ``perform_refresh_qdrant`` (main-branch refresh and overlays),
- ``run_branch_overlay_indexing`` (stale overlay files).

All Qdrant access goes to an in-memory fake; no ports or containers are used.
"""

from __future__ import annotations

import types

import pytest

from src_test._index_rag_loader import (
    FakeQdrantClient,
    delete_filter_parts,
    install_refresh_fakes,
    load_index_rag,
    make_fake_config,
)


@pytest.fixture
def env(tmp_path, monkeypatch):
    cfg = make_fake_config(tmp_path)
    mod = load_index_rag(cfg)
    return types.SimpleNamespace(mod=mod, cfg=cfg, tmp=tmp_path, mp=monkeypatch)


def _manifest(keys):
    return {"files": {k: {"vector_ids": [f"{k}#0", f"{k}#1"]} for k in keys}}


def _run_refresh(env, delete_keys, *, client=None, manifest=None, branch_label=None):
    client = client or FakeQdrantClient()
    install_refresh_fakes(env.mod, env.mp, client)
    saves: list[dict] = []
    manifest = manifest if manifest is not None else _manifest(delete_keys)
    env.mod.perform_refresh_qdrant(
        actions={"add": [], "modify": [], "delete": list(delete_keys)},
        manifest=manifest,
        branch_label=branch_label,
        file_states={},
        save_fn=lambda m: saves.append(dict(m["files"])),
    )
    return client, manifest, saves


class TestRefreshBatchDelete:
    def test_empty_delete_list_issues_no_delete(self, env):
        client, manifest, _ = _run_refresh(env, [])
        assert client.delete_calls == []
        assert manifest == {"files": {}}

    def test_default_chunk_size_is_500(self, env):
        keys = [f"pkg/f{i}.py" for i in range(1200)]
        client, manifest, _ = _run_refresh(env, keys)
        sizes = [len(delete_filter_parts(c)[0]) for c in client.delete_calls]
        assert sizes == [500, 500, 200]
        sent = [k for c in client.delete_calls for k in delete_filter_parts(c)[0]]
        assert sent == keys
        assert manifest["files"] == {}

    @pytest.mark.parametrize(
        "count, chunk, expected",
        [
            (1, 3, [1]),
            (3, 3, [3]),
            (4, 3, [3, 1]),
            (6, 3, [3, 3]),
            (5, 1, [1, 1, 1, 1, 1]),
        ],
    )
    def test_chunk_boundaries(self, env, count, chunk, expected):
        env.cfg.QDRANT_DELETE_CHUNK_SIZE = chunk
        keys = [f"f{i}.py" for i in range(count)]
        client, _, _ = _run_refresh(env, keys)
        assert [len(delete_filter_parts(c)[0]) for c in client.delete_calls] == expected

    @pytest.mark.parametrize("bad", [0, -5, None])
    def test_invalid_chunk_size_falls_back_to_500(self, env, bad):
        env.cfg.QDRANT_DELETE_CHUNK_SIZE = bad
        keys = [f"f{i}.py" for i in range(501)]
        client, _, _ = _run_refresh(env, keys)
        assert [len(delete_filter_parts(c)[0]) for c in client.delete_calls] == [500, 1]

    def test_chunk_size_given_as_string_is_parsed(self, env):
        env.cfg.QDRANT_DELETE_CHUNK_SIZE = "2"
        client, _, _ = _run_refresh(env, ["a.py", "b.py", "c.py"])
        assert [len(delete_filter_parts(c)[0]) for c in client.delete_calls] == [2, 1]

    def test_uses_match_any_and_timeout(self, env):
        from qdrant_client import models

        env.cfg.QDRANT_DELETE_TIMEOUT = 17
        client, _, _ = _run_refresh(env, ["a.py", "b.py"])
        (call,) = client.delete_calls
        assert call["collection_name"] == env.cfg.COLLECTION_NAME
        assert call["timeout"] == 17
        (cond,) = call["points_selector"].must
        assert isinstance(cond.match, models.MatchAny)
        assert cond.match.any == ["a.py", "b.py"]

    def test_branch_label_adds_branch_condition(self, env):
        client, _, _ = _run_refresh(env, ["a.py"], branch_label="feature/x")
        paths, branch = delete_filter_parts(client.delete_calls[0])
        assert paths == ["a.py"]
        assert branch == "feature/x"

    def test_no_branch_label_has_no_branch_condition(self, env):
        client, _, _ = _run_refresh(env, ["a.py"])
        assert delete_filter_parts(client.delete_calls[0])[1] is None

    def test_failed_chunk_keeps_manifest_entries(self, env):
        env.cfg.QDRANT_DELETE_CHUNK_SIZE = 2
        keys = [f"f{i}.py" for i in range(6)]
        client = FakeQdrantClient(fail_delete_on_calls={2})
        _, manifest, saves = _run_refresh(env, keys, client=client)
        assert len(client.delete_calls) == 3
        # Only the failed chunk (f2, f3) stays in the manifest
        assert sorted(manifest["files"]) == ["f2.py", "f3.py"]
        # Manifest saved after the delete phase with the failed keys kept
        assert "f2.py" in saves[0] and "f0.py" not in saves[0]

    def test_all_chunks_fail_keeps_whole_manifest(self, env):
        keys = ["a.py", "b.py"]
        client = FakeQdrantClient(fail_delete_on_calls={1})
        _, manifest, _ = _run_refresh(env, keys, client=client)
        assert sorted(manifest["files"]) == keys

    def test_keys_missing_from_manifest_are_tolerated(self, env):
        manifest = _manifest(["known.py"])
        client, manifest, _ = _run_refresh(
            env, ["known.py", "unknown.py"], manifest=manifest
        )
        assert delete_filter_parts(client.delete_calls[0])[0] == [
            "known.py",
            "unknown.py",
        ]
        assert manifest["files"] == {}


class TestRefreshModifyDeletesOldVectors:
    def test_modify_deletes_previous_points_for_file(self, env, tmp_path):
        from llama_index.core.schema import TextNode

        src = tmp_path / "m.py"
        src.write_text("x = 1\n", encoding="utf-8")
        client = FakeQdrantClient()
        install_refresh_fakes(
            env.mod,
            env.mp,
            client,
            load_nodes=lambda info: [TextNode(text="x = 1", metadata={"file_path": "m.py"})],
        )
        manifest = _manifest(["m.py"])
        env.mod.perform_refresh_qdrant(
            actions={"add": [], "modify": ["m.py"], "delete": []},
            manifest=manifest,
            file_states={"m.py": {"file_path": "m.py", "full_path": str(src), "mtime": 0, "hash": "h"}},
            save_fn=lambda m: None,
        )
        assert [delete_filter_parts(c)[0] for c in client.delete_calls] == [["m.py"]]


# ── run_branch_overlay_indexing ─────────────────────────────────────


def _setup_overlay(env, old_keys, *, client):
    import config_loader
    import shared.overlay as overlay

    mod, mp = env.mod, env.mp
    group = {"repo_path": str(env.tmp / "repo"), "main_branch": "master", "git_prefixes": []}
    branch_manifest = {"files": {k: {"vector_ids": [f"{k}#0"]} for k in old_keys}}
    saved: list[dict] = []

    mp.setattr(config_loader, "get_repo_groups", lambda cfg: [group])
    mp.setattr(overlay, "configured_overlays", lambda g: [{"name": "feature/x", "kind": "branch"}])
    mp.setattr(
        overlay,
        "diff_overlay",
        lambda *a, **k: types.SimpleNamespace(
            changes=[("D", "gone.py")], merge_base="mb", resolved_commit="rc", read_at="rc"
        ),
    )
    mp.setattr(overlay, "overlay_signature", lambda *a, **k: None)
    mp.setattr(overlay, "skip_when_diff_empty", lambda kind: True)
    mp.setattr(
        overlay,
        "reconcile_overlay_actions",
        lambda old, new: {"add": [], "modify": [], "delete": []},
    )
    mp.setattr(mod, "_collect_branch_extensions", lambda g: {".py"})
    mp.setattr(mod, "_map_git_path_to_file_key", lambda p, g: (p, {}))
    mp.setattr(mod, "_load_branch_manifest", lambda b: branch_manifest)
    mp.setattr(mod, "_save_branch_manifest", lambda b, m: saved.append(dict(m["files"])))
    mp.setattr(mod, "_stamp_overlay_manifest", lambda m, **kw: None)
    mp.setattr(mod, "_cleanup_stale_branches", lambda configured: None)
    mp.setattr(mod, "log_refresh_changes", lambda *a, **k: None)
    mp.setattr(mod, "get_qdrant_client", lambda cfg: client)

    def _no_refresh(**kw):
        raise AssertionError("perform_refresh_qdrant must not run for delete-only overlays")

    mp.setattr(mod, "perform_refresh_qdrant", _no_refresh)
    return branch_manifest, saved


class TestOverlayBatchDelete:
    def test_stale_overlay_files_deleted_in_chunks(self, env):
        env.cfg.QDRANT_DELETE_CHUNK_SIZE = 2
        env.cfg.QDRANT_DELETE_TIMEOUT = 9
        keys = [f"o{i}.py" for i in range(5)]
        client = FakeQdrantClient()
        manifest, saved = _setup_overlay(env, keys, client=client)
        env.mod.run_branch_overlay_indexing()

        parts = [delete_filter_parts(c) for c in client.delete_calls]
        assert [p for p, _ in parts] == [["o0.py", "o1.py"], ["o2.py", "o3.py"], ["o4.py"]]
        assert {b for _, b in parts} == {"feature/x"}
        assert {c["timeout"] for c in client.delete_calls} == {9}
        assert manifest["files"] == {}
        assert manifest["tombstones"] == ["gone.py"]
        assert saved and saved[-1] == {}

    def test_failed_overlay_chunk_keeps_branch_manifest_entries(self, env):
        env.cfg.QDRANT_DELETE_CHUNK_SIZE = 2
        keys = ["o0.py", "o1.py", "o2.py"]
        client = FakeQdrantClient(fail_delete_on_calls={1})
        manifest, _ = _setup_overlay(env, keys, client=client)
        env.mod.run_branch_overlay_indexing()
        assert len(client.delete_calls) == 2
        assert sorted(manifest["files"]) == ["o0.py", "o1.py"]

    @pytest.mark.parametrize("bad", [0, -1, None])
    def test_invalid_chunk_size_falls_back_to_500(self, env, bad):
        env.cfg.QDRANT_DELETE_CHUNK_SIZE = bad
        keys = [f"o{i}.py" for i in range(501)]
        client = FakeQdrantClient()
        _setup_overlay(env, keys, client=client)
        env.mod.run_branch_overlay_indexing()
        assert [len(delete_filter_parts(c)[0]) for c in client.delete_calls] == [500, 1]

    def test_default_chunk_size_when_unset(self, env):
        keys = [f"o{i}.py" for i in range(3)]
        client = FakeQdrantClient()
        _setup_overlay(env, keys, client=client)
        env.mod.run_branch_overlay_indexing()
        assert [len(delete_filter_parts(c)[0]) for c in client.delete_calls] == [3]
        assert client.delete_calls[0]["timeout"] == 60
