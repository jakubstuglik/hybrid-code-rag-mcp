# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Overlay signature is stored only after a run whose Qdrant work all succeeded.

The signature lets the next run skip an overlay whose refs did not move. If
it were stored after a failed embed or delete (Qdrant restart, timeout), the
overlay would stay incomplete until the branch moved again.
"""

from __future__ import annotations

import types
from pathlib import Path

import pytest

from src_test._index_rag_loader import FakeQdrantClient, load_index_rag, make_fake_config


@pytest.fixture
def env(tmp_path, monkeypatch):
    cfg = make_fake_config(tmp_path)
    mod = load_index_rag(cfg)
    return types.SimpleNamespace(mod=mod, cfg=cfg, tmp=tmp_path, mp=monkeypatch)


def _setup(env, *, changes, old_keys=(), refresh_result=True, client=None):
    import config_loader
    import shared.git_ops as git_ops
    import shared.overlay as overlay

    mod, mp = env.mod, env.mp
    group = {"repo_path": str(env.tmp / "repo"), "main_branch": "master", "git_prefixes": []}
    manifest = {"files": {k: {"hash": "old", "vector_ids": [f"{k}#0"]} for k in old_keys}}
    stamps: list[dict] = []
    refresh_calls: list[dict] = []

    def _read_to_temp(repo, ref, paths):
        d = env.tmp / "blobs"
        d.mkdir(exist_ok=True)
        for p in paths:
            (d / p).write_text(f"# {p}\n", encoding="utf-8")
        return str(d)

    mp.setattr(config_loader, "get_repo_groups", lambda cfg: [group])
    mp.setattr(overlay, "configured_overlays", lambda g: [{"name": "feature/x", "kind": "branch"}])
    mp.setattr(
        overlay,
        "diff_overlay",
        lambda *a, **k: types.SimpleNamespace(
            changes=changes, merge_base="mb", resolved_commit="rc", read_at="rc"
        ),
    )
    mp.setattr(overlay, "overlay_signature", lambda *a, **k: "sig-1")
    mp.setattr(overlay, "skip_when_diff_empty", lambda kind: True)
    mp.setattr(git_ops, "read_files_to_temp_dir", _read_to_temp)
    mp.setattr(mod, "_overlay_unchanged_since_last_run", lambda label, sig: False)
    mp.setattr(mod, "_collect_branch_extensions", lambda g: {".py"})
    mp.setattr(mod, "_map_git_path_to_file_key", lambda p, g: (p, {}))
    mp.setattr(mod, "_load_branch_manifest", lambda b: manifest)
    mp.setattr(mod, "_save_branch_manifest", lambda b, m: None)
    mp.setattr(mod, "_stamp_overlay_manifest", lambda m, **kw: stamps.append(kw))
    mp.setattr(mod, "_cleanup_stale_branches", lambda configured: None)
    mp.setattr(mod, "log_refresh_changes", lambda *a, **k: None)
    mp.setattr(mod, "get_qdrant_client", lambda cfg: client or FakeQdrantClient())

    def _refresh(**kw):
        refresh_calls.append(kw)
        return refresh_result

    mp.setattr(mod, "perform_refresh_qdrant", _refresh)
    return stamps, refresh_calls


def test_signature_stamped_after_successful_embed(env):
    stamps, calls = _setup(env, changes=[("A", "a.py")], refresh_result=True)
    env.mod.run_branch_overlay_indexing()
    assert calls and stamps[-1]["signature"] == "sig-1"


@pytest.mark.parametrize("result", [False, None])
def test_signature_not_stamped_after_failed_embed(env, result):
    stamps, calls = _setup(env, changes=[("A", "a.py")], refresh_result=result)
    env.mod.run_branch_overlay_indexing()
    assert calls
    assert stamps[-1]["signature"] is None
    # Progress fields are still recorded.
    assert stamps[-1]["merge_base"] == "mb"


def test_signature_not_stamped_after_failed_overlay_delete(env):
    client = FakeQdrantClient(fail_delete_on_calls={1})
    stamps, calls = _setup(
        env, changes=[("D", "gone.py")], old_keys=["stale.py"], client=client
    )
    env.mod.run_branch_overlay_indexing()
    assert not calls  # delete-only overlay
    assert stamps[-1]["signature"] is None


def test_signature_stamped_after_successful_overlay_delete(env):
    stamps, _ = _setup(env, changes=[("D", "gone.py")], old_keys=["stale.py"])
    env.mod.run_branch_overlay_indexing()
    assert stamps[-1]["signature"] == "sig-1"


def test_overlay_delete_is_journaled_before_qdrant(env):
    seen: list[bool] = []
    journal = env.mod._pending_journal_path("feature/x")

    class _Client(FakeQdrantClient):
        def delete(self, **kwargs):
            seen.append(journal.exists())
            raise RuntimeError("down")

    _setup(env, changes=[("D", "gone.py")], old_keys=["stale.py"], client=_Client())
    env.mod.run_branch_overlay_indexing()
    assert seen == [True]
    # The failed delete stays in the journal for the next run.
    assert journal.exists()


def test_unchanged_check_is_false_while_journal_exists(env, monkeypatch):
    mod = env.mod
    monkeypatch.setattr(
        mod, "_load_branch_manifest", lambda b: {"overlay_signature": "s", "files": {}}
    )
    assert mod._overlay_unchanged_since_last_run("feature/x", "s") is True
    path: Path = mod._pending_journal_path("feature/x")
    path.write_text('{"k":"a.py","h":null}\n', encoding="utf-8")
    assert mod._overlay_unchanged_since_last_run("feature/x", "s") is False
