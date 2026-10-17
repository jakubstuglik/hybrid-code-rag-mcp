"""Cleanup of overlays removed from config: label by kind, histogram path.

``index_rag`` parses CLI arguments on import, so the cleanup loop itself is
covered by the indexing runs; these tests cover the helpers it relies on.
"""

from __future__ import annotations

from pathlib import Path

from shared.overlay import overlay_histogram_path, overlay_kind_from_manifest


def test_stored_kind_wins():
    assert overlay_kind_from_manifest({"kind": "tag"}) == "tag"
    assert overlay_kind_from_manifest({"kind": "branch", "last_resolved_commit": "x"}) == "branch"


def test_old_manifest_without_kind_is_inferred():
    assert overlay_kind_from_manifest({"last_resolved_commit": "abc"}) == "tag"
    assert overlay_kind_from_manifest({"merge_base": "abc", "last_branch_commit": "d"}) == "branch"
    assert overlay_kind_from_manifest({}) == "branch"


def test_histogram_sits_next_to_the_manifest():
    manifest = Path("idx") / "index_manifest_branch_task_T1.json"
    assert overlay_histogram_path(manifest) == Path("idx") / "chunk_histogram_branch_task_T1.json"


def test_main_manifest_has_no_overlay_histogram():
    manifest = Path("idx") / "index_manifest.json"
    assert overlay_histogram_path(manifest) == manifest
