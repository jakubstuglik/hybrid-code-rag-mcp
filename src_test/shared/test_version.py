# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0
"""Tests for the single version source and its manifest bookkeeping."""

from __future__ import annotations

import copy
import json
import re
import types
from pathlib import Path

import shared.index_state as index_state
from shared.version import (
    MANIFEST_FIRST_VERSION_KEY,
    MANIFEST_VERSION_KEY,
    __version__,
    manifest_version_line,
    stamp_manifest_version,
)

_ROOT = Path(__file__).resolve().parents[2]


def _old_manifest() -> dict:
    """A manifest written before versioning existed."""
    return {
        "files": {"src/a.py": {"hash": "h", "mtime": 1.0, "vector_ids": ["id"]}},
        "repo_commits": {"repo": {"main_branch": "main", "commit": "c" * 40}},
        "index_run": {"completed_at": "2026-01-01T00:00:00Z", "mode": "refresh"},
    }


class TestVersionString:
    def test_semver(self):
        assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)

    def test_matches_latest_changelog_release(self):
        text = (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        releases = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", text, flags=re.M)
        assert releases, "CHANGELOG.md has no released versions"
        assert releases[0] == __version__

    def test_changelog_link_references_cover_every_release(self):
        """Each release needs a ``[X.Y.Z]: .../compare/vPREV...vX.Y.Z`` link and
        ``[Unreleased]`` must compare from the latest release tag."""
        text = (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        releases = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", text, flags=re.M)
        refs = dict(re.findall(r"^\[([^\]]+)\]: (\S+)$", text, flags=re.M))
        assert refs.get("Unreleased", "").endswith(f"/compare/v{releases[0]}...HEAD")
        for newer, older in zip(releases, releases[1:]):
            assert refs.get(newer, "").endswith(f"/compare/v{older}...v{newer}"), newer
        assert refs.get(releases[-1], "").endswith(f"/releases/tag/v{releases[-1]}")

    def test_changelog_has_unreleased_section(self):
        text = (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        assert re.search(r"^## \[Unreleased\]", text, flags=re.M)


class TestStampManifestVersion:
    def test_new_manifest_gets_both_fields(self):
        manifest = {"files": {}}
        stamp_manifest_version(manifest)
        assert manifest[MANIFEST_VERSION_KEY] == __version__
        assert manifest[MANIFEST_FIRST_VERSION_KEY] == __version__

    def test_first_version_is_kept(self):
        manifest = {"files": {}}
        stamp_manifest_version(manifest, "0.10.0")
        stamp_manifest_version(manifest, "0.11.2")
        assert manifest[MANIFEST_VERSION_KEY] == "0.11.2"
        assert manifest[MANIFEST_FIRST_VERSION_KEY] == "0.10.0"

    def test_old_manifest_only_gains_fields(self):
        """Old manifests stay valid: nothing used for change detection changes."""
        manifest = _old_manifest()
        before = copy.deepcopy(manifest)
        stamp_manifest_version(manifest)
        for key, value in before.items():
            assert manifest[key] == value
        assert set(manifest) - set(before) == {
            MANIFEST_VERSION_KEY,
            MANIFEST_FIRST_VERSION_KEY,
        }

    def test_json_roundtrip(self):
        manifest = _old_manifest()
        stamp_manifest_version(manifest)
        assert json.loads(json.dumps(manifest)) == manifest


class TestManifestVersionLine:
    def test_unknown_for_old_manifest(self):
        line = manifest_version_line(_old_manifest(), "0.10.0")
        assert "indexer_version: unknown" in line
        assert "server_version: 0.10.0" in line

    def test_same_first_and_last(self):
        manifest = {}
        stamp_manifest_version(manifest, "0.10.0")
        line = manifest_version_line(manifest, "0.10.0")
        assert line == "- indexer_version: 0.10.0 | server_version: 0.10.0"

    def test_first_shown_when_different(self):
        manifest = {}
        stamp_manifest_version(manifest, "0.10.0")
        stamp_manifest_version(manifest, "0.11.0")
        line = manifest_version_line(manifest, "0.11.1")
        assert "indexer_version: 0.11.0 (first: 0.10.0)" in line
        assert "server_version: 0.11.1" in line

    def test_non_dict_manifest(self):
        assert "unknown" in manifest_version_line(None)  # type: ignore[arg-type]


def _cfg(tmp_path: Path) -> types.SimpleNamespace:
    index_dir = tmp_path / "qdrant" / "idx"
    index_dir.mkdir(parents=True)
    return types.SimpleNamespace(
        BASE_PATH=str(tmp_path / "qdrant"),
        MODEL_PATH="idx",
        COLLECTION_NAME="c",
        QDRANT_HOST="localhost",
        QDRANT_PORT=6333,
        MCP_SERVER_NAME="srv",
        SOURCE_DIRS=[],
        get_index_path=lambda: str(index_dir),
    )


class TestIndexStateReportVersion:
    def test_old_manifest_loads_and_reports_unknown(self, tmp_path):
        cfg = _cfg(tmp_path)
        index_state.get_main_manifest_path(cfg).write_text(
            json.dumps(_old_manifest()), encoding="utf-8"
        )
        assert index_state.load_main_manifest(cfg)["files"]
        report = index_state.build_index_state_report(cfg)
        assert "indexer_version: unknown" in report
        assert f"server_version: {__version__}" in report

    def test_stamped_manifest_reports_version(self, tmp_path):
        cfg = _cfg(tmp_path)
        manifest = _old_manifest()
        stamp_manifest_version(manifest, "0.10.0")
        index_state.get_main_manifest_path(cfg).write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        report = index_state.build_index_state_report(cfg)
        assert "indexer_version: 0.10.0" in report
