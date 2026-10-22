# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Refresh keeps Qdrant and the manifest in sync across kills and Qdrant errors.

Regression tests for the findings of the formal model of the refresh path
(manifest vs Qdrant): each scenario replays a trace the model found, on the
real ``perform_refresh_qdrant`` with an in-memory Qdrant (``qdrant_client``
local mode) and real files. After a later run that finishes without errors,
Qdrant must hold exactly the chunks of the files on disk.

* kill after an upsert, before the manifest save (orphan points);
* kill after a delete, before the manifest save (missing points);
* failed delete of a modified file's old points (stale chunks);
* file changed between the scan and the read (wrong hash in the manifest);
* failed deletes and upserts of a run that keeps going.
"""

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

pytest.importorskip("qdrant_client")
from qdrant_client import QdrantClient, models  # noqa: E402

from src_test._index_rag_loader import (  # noqa: E402
    install_refresh_fakes,
    load_index_rag,
    make_fake_config,
)

COLLECTION = "unit_test_collection"


class Killed(BaseException):
    """Stands in for SIGKILL: not an Exception, so nothing handles it."""


class FlakyQdrant:
    """Local in-memory Qdrant with injectable delete/upsert failures."""

    def __init__(self) -> None:
        self.inner = QdrantClient(":memory:")
        self.inner.create_collection(
            COLLECTION,
            vectors_config=models.VectorParams(size=3, distance=models.Distance.COSINE),
        )
        self.fail_delete_for: set[str] = set()
        self.fail_upsert_for: set[str] = set()
        self.kill_after_upsert = False
        self.delete_calls = 0

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def delete(self, collection_name, points_selector, **kwargs):
        self.delete_calls += 1
        paths = _filter_paths(points_selector)
        if paths & self.fail_delete_for:
            raise RuntimeError(f"simulated delete failure for {sorted(paths)}")
        return self.inner.delete(collection_name=collection_name, points_selector=points_selector)

    def upsert(self, collection_name, points, **kwargs):
        paths = {p.payload.get("file_path") for p in points}
        if paths & self.fail_upsert_for:
            raise RuntimeError(f"simulated upsert failure for {sorted(paths)}")
        result = self.inner.upsert(collection_name=collection_name, points=points)
        if self.kill_after_upsert:
            raise Killed()
        return result

    def chunks(self) -> set[tuple[str, str]]:
        points, _ = self.inner.scroll(COLLECTION, limit=10_000, with_payload=True)
        return {(p.payload["file_path"], p.payload["text"]) for p in points}


def _filter_paths(selector) -> set[str]:
    out: set[str] = set()
    for cond in getattr(selector, "must", None) or []:
        if getattr(cond, "key", None) == "file_path":
            out |= set(cond.match.any)
    return out


@pytest.fixture(params=[0, 2], ids=["serial", "pipelined"])
def env(request, tmp_path, monkeypatch):
    cfg = make_fake_config(
        tmp_path, EMBED_POOL_MAX_FILES=1, EMBED_PIPELINE_DEPTH=request.param
    )
    mod = load_index_rag(cfg)
    client = FlakyQdrant()
    src = tmp_path / "src"
    src.mkdir()
    reads: list[str] = []
    hooks: dict = {}

    from llama_index.core.schema import TextNode

    def _load(info):
        key = info["file_path"]
        hook = hooks.pop(key, None)
        if hook is not None:
            hook()
        path = Path(info["full_path"])
        if not path.exists():
            return []
        reads.append(key)
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln]
        return [TextNode(text=ln, metadata={"file_path": key}) for ln in lines]

    install_refresh_fakes(mod, monkeypatch, client, load_nodes=_load)
    return types.SimpleNamespace(
        mod=mod, cfg=cfg, client=client, src=src, tmp=tmp_path, hooks=hooks, reads=reads
    )


def _write(env, name: str, *lines: str) -> None:
    (env.src / name).write_text("".join(f"{ln}\n" for ln in lines), encoding="utf-8")


def _scan(env) -> dict[str, dict]:
    states = {}
    for path in sorted(env.src.glob("*.py")):
        key = f"proj/{path.name}"
        states[key] = {
            "file_path": key,
            "full_path": str(path),
            "mtime": path.stat().st_mtime,
            "hash": env.mod.compute_file_hash(path),
        }
    return states


def _manifest_path(env) -> Path:
    return Path(env.cfg.get_index_path()) / "index_manifest.json"


def _load_manifest(env) -> dict:
    path = _manifest_path(env)
    if not path.exists():
        return {"files": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _run(env, *, kill_on_save: int | None = None) -> bool | None:
    """One refresh as ``run_refresh_indexing`` does it; return the outcome."""
    mod = env.mod
    manifest = _load_manifest(env)
    mod.recover_pending_points(manifest, client=env.client)
    states = _scan(env)
    actions = mod.determine_actions(manifest["files"], states)
    saves = {"n": 0}

    def _save(m):
        saves["n"] += 1
        if kill_on_save is not None and saves["n"] == kill_on_save:
            raise Killed()
        mod.save_manifest(m)

    complete = mod.perform_refresh_qdrant(
        actions, manifest, file_states=states, save_fn=_save
    )
    mod.save_manifest(manifest)
    return complete


def _expected(env) -> set[tuple[str, str]]:
    out = set()
    for path in env.src.glob("*.py"):
        for ln in path.read_text(encoding="utf-8").splitlines():
            if ln:
                out.add((f"proj/{path.name}", ln))
    return out


def _journal(env) -> Path:
    return _manifest_path(env).with_name("index_manifest.json.pending.jsonl")


# ── kill after upsert, before the manifest save (H10) ───────────────────────


def test_kill_after_upsert_then_file_deleted_leaves_no_orphans(env):
    _write(env, "a.py", "a1", "a2")
    env.client.kill_after_upsert = True
    with pytest.raises(Killed):
        _run(env)
    assert env.client.chunks() == {("proj/a.py", "a1"), ("proj/a.py", "a2")}
    assert "proj/a.py" not in _load_manifest(env)["files"]
    assert _journal(env).exists()

    env.client.kill_after_upsert = False
    (env.src / "a.py").unlink()
    assert _run(env) is True
    assert env.client.chunks() == set() == _expected(env)
    assert not _journal(env).exists()


def test_kill_after_upsert_then_fewer_chunks_leaves_no_stale_chunk(env):
    _write(env, "a.py", "a1", "a2")
    env.client.kill_after_upsert = True
    with pytest.raises(Killed):
        _run(env)
    env.client.kill_after_upsert = False
    _write(env, "a.py", "b1")
    assert _run(env) is True
    assert env.client.chunks() == _expected(env) == {("proj/a.py", "b1")}


def test_kill_after_modify_upsert_then_revert_is_repaired(env):
    _write(env, "a.py", "v1")
    assert _run(env) is True
    _write(env, "a.py", "v2", "v2b")
    env.client.kill_after_upsert = True
    with pytest.raises(Killed):
        _run(env)
    env.client.kill_after_upsert = False
    _write(env, "a.py", "v1")  # back to the content the manifest still lists
    assert _run(env) is True
    assert env.client.chunks() == _expected(env) == {("proj/a.py", "v1")}


def test_kill_at_manifest_save_keeps_saved_files(env):
    """Files saved before the kill are not re-indexed; only unsaved ones are."""
    names = [f"f{i:02d}.py" for i in range(12)]
    for name in names:
        _write(env, name, f"{name} v1")
    assert _run(env) is True
    for name in names:
        _write(env, name, f"{name} v2")
    # Save 1 = periodic save after 10 files; save 2 (the final one) is killed.
    with pytest.raises(Killed):
        _run(env, kill_on_save=2)
    env.reads.clear()
    assert _run(env) is True
    assert env.client.chunks() == _expected(env)
    assert 0 < len(env.reads) < len(names)


# ── kill after a delete, before the manifest save (H11) ─────────────────────


def test_kill_after_delete_then_file_restored_is_reindexed(env):
    _write(env, "a.py", "a1")
    _write(env, "b.py", "b1")
    assert _run(env) is True
    saved = (env.src / "a.py").read_text(encoding="utf-8")
    (env.src / "a.py").unlink()
    with pytest.raises(Killed):
        _run(env, kill_on_save=1)  # the save right after the deletes
    assert ("proj/a.py", "a1") not in env.client.chunks()
    assert "proj/a.py" in _load_manifest(env)["files"]
    (env.src / "a.py").write_text(saved, encoding="utf-8")
    assert _run(env) is True
    assert env.client.chunks() == _expected(env)


def test_kill_after_modify_delete_then_revert_is_reindexed(env):
    _write(env, "a.py", "v1")
    assert _run(env) is True
    _write(env, "a.py", "v2")

    # Kill right after the old points were deleted: the upsert never runs.
    original = env.client.delete

    def _delete_then_kill(*a, **k):
        original(*a, **k)
        raise Killed()

    env.client.delete = _delete_then_kill
    with pytest.raises(Killed):
        _run(env)
    env.client.delete = original
    _write(env, "a.py", "v1")
    assert _run(env) is True
    assert env.client.chunks() == _expected(env) == {("proj/a.py", "v1")}


# ── failed modify-delete (H6b) ───────────────────────────────────────────────


def test_failed_modify_delete_skips_upsert_and_keeps_old_entry(env):
    _write(env, "a.py", "o1", "o2", "o3")
    assert _run(env) is True
    old_entry = _load_manifest(env)["files"]["proj/a.py"]
    _write(env, "a.py", "n1")
    env.client.fail_delete_for = {"proj/a.py"}
    assert _run(env) is False
    entry = _load_manifest(env)["files"]["proj/a.py"]
    assert entry["hash"] == old_entry["hash"]
    # Qdrant still has the old chunks only (no mix of old and new).
    assert env.client.chunks() == {("proj/a.py", t) for t in ("o1", "o2", "o3")}

    env.client.fail_delete_for = set()
    assert _run(env) is True
    assert env.client.chunks() == _expected(env) == {("proj/a.py", "n1")}


def test_failed_modify_delete_does_not_block_other_files(env):
    _write(env, "a.py", "a1")
    _write(env, "b.py", "b1")
    assert _run(env) is True
    _write(env, "a.py", "a2")
    _write(env, "b.py", "b2")
    env.client.fail_delete_for = {"proj/a.py"}
    assert _run(env) is False
    assert ("proj/b.py", "b2") in env.client.chunks()
    env.client.fail_delete_for = set()
    assert _run(env) is True
    assert env.client.chunks() == _expected(env)


# ── file changed between scan and read (H9) ─────────────────────────────────


def test_file_changed_after_scan_gets_reindexed_after_revert(env):
    _write(env, "a.py", "v1")

    def _delete_during_run():
        (env.src / "a.py").unlink()

    env.hooks["proj/a.py"] = _delete_during_run
    _run(env)
    assert _load_manifest(env)["files"]["proj/a.py"]["hash"] == ""
    _write(env, "a.py", "v1")  # same content as at the scan
    assert _run(env) is True
    assert env.client.chunks() == _expected(env) == {("proj/a.py", "v1")}


def test_file_edited_after_scan_entry_never_matches_old_hash(env):
    _write(env, "a.py", "v1")

    def _edit():
        _write(env, "a.py", "v2", "v2b")

    env.hooks["proj/a.py"] = _edit
    _run(env)
    assert _load_manifest(env)["files"]["proj/a.py"]["hash"] == ""
    _write(env, "a.py", "v1")
    assert _run(env) is True
    assert env.client.chunks() == _expected(env)


def test_unchanged_file_keeps_scan_hash(env):
    _write(env, "a.py", "v1")
    assert _run(env) is True
    entry = _load_manifest(env)["files"]["proj/a.py"]
    assert entry["hash"] == env.mod.compute_file_hash(env.src / "a.py")


# ── failed deletes and upserts during a run ─────────────────────────────────


def test_failed_upsert_of_new_file_is_repaired_next_run(env):
    _write(env, "a.py", "a1", "a2")
    env.client.fail_upsert_for = {"proj/a.py"}
    assert _run(env) is False
    assert _journal(env).exists()
    env.client.fail_upsert_for = set()
    _write(env, "a.py", "b1")
    assert _run(env) is True
    assert env.client.chunks() == _expected(env)
    assert not _journal(env).exists()


def test_failed_delete_of_removed_file_is_retried(env):
    _write(env, "a.py", "a1")
    _write(env, "b.py", "b1")
    assert _run(env) is True
    (env.src / "a.py").unlink()
    env.client.fail_delete_for = {"proj/a.py"}
    assert _run(env) is False
    env.client.fail_delete_for = set()
    assert _run(env) is True
    assert env.client.chunks() == _expected(env)


def test_clean_runs_leave_no_journal(env):
    _write(env, "a.py", "a1")
    assert _run(env) is True
    _write(env, "a.py", "a2")
    _write(env, "b.py", "b1")
    assert _run(env) is True
    (env.src / "a.py").unlink()
    assert _run(env) is True
    assert not _journal(env).exists()
    assert env.client.chunks() == _expected(env)


def test_qdrant_unreachable_returns_false_and_changes_nothing(env, monkeypatch):
    _write(env, "a.py", "a1")

    def _down():
        raise ConnectionError("down")

    monkeypatch.setattr(env.client, "get_collections", _down, raising=False)
    manifest = {"files": {}}
    states = _scan(env)
    actions = env.mod.determine_actions(manifest["files"], states)
    assert env.mod.perform_refresh_qdrant(actions, manifest, file_states=states) is False
    assert manifest["files"] == {}


# ── recover_pending_points ──────────────────────────────────────────────────


def test_recover_keeps_journal_when_qdrant_fails(env):
    _write(env, "a.py", "a1")
    env.client.kill_after_upsert = True
    with pytest.raises(Killed):
        _run(env)
    env.client.kill_after_upsert = False
    env.client.fail_delete_for = {"proj/a.py"}
    manifest = _load_manifest(env)
    assert env.mod.recover_pending_points(manifest, client=env.client) == []
    assert _journal(env).exists()
    env.client.fail_delete_for = set()
    assert env.mod.recover_pending_points(manifest, client=env.client) == ["proj/a.py"]
    assert not _journal(env).exists()
    assert env.client.chunks() == set()


def test_recover_without_journal_is_a_no_op(env):
    manifest = {"files": {"proj/x.py": {"hash": "h", "vector_ids": []}}}
    assert env.mod.recover_pending_points(manifest, client=env.client) == []
    assert env.client.delete_calls == 0
    assert "proj/x.py" in manifest["files"]


def test_recover_overlay_uses_branch_filter_and_overlay_journal(env, monkeypatch):
    calls = []

    class _Rec:
        def delete(self, **kw):
            calls.append(kw)

    path = env.mod._pending_journal_path("feature/x")
    path.write_text('{"k":"proj/a.py","h":"abc"}\n', encoding="utf-8")
    saved = []
    manifest = {"files": {"proj/a.py": {"hash": "old"}}}
    stale = env.mod.recover_pending_points(
        manifest, branch_label="feature/x", client=_Rec(), save_fn=saved.append
    )
    assert stale == ["proj/a.py"]
    assert manifest["files"] == {}
    assert saved and not path.exists()
    must = calls[0]["points_selector"].must
    assert {c.key for c in must} == {"file_path", "branch"}
