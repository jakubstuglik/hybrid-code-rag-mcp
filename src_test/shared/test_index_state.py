# Copyright (c) 2025-2026 hybrid-code-rag-mcp contributors
# SPDX-License-Identifier: MIT
"""Unit tests for shared.index_state (manifest-only hot path)."""

from __future__ import annotations

import json
import types
from pathlib import Path

import shared.index_state as index_state


def _cfg(tmp_path: Path, **extra) -> types.SimpleNamespace:
    base = tmp_path / "qdrant"
    model = "idx"
    (base / model).mkdir(parents=True, exist_ok=True)

    def get_index_path() -> str:
        return str(base / model)

    ns = types.SimpleNamespace(
        BASE_PATH=str(base),
        MODEL_PATH=model,
        COLLECTION_NAME="test_coll",
        QDRANT_HOST="localhost",
        QDRANT_PORT=6333,
        MCP_SERVER_NAME="test-rag",
        SOURCE_DIRS=[],
        get_index_path=get_index_path,
    )
    for k, v in extra.items():
        setattr(ns, k, v)
    return ns


def _write_manifest(cfg, data: dict) -> Path:
    path = index_state.get_main_manifest_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class TestFingerprint:
    def test_stable(self):
        files = {"b.py": {"hash": "h2"}, "a.py": {"hash": "h1"}}
        assert index_state.fingerprint_files(files) == index_state.fingerprint_files(
            dict(reversed(list(files.items())))
        )

    def test_empty(self):
        assert index_state.fingerprint_files({}) == "empty"


class TestBuildIndexStateReport:
    def test_missing_manifest(self, tmp_path):
        cfg = _cfg(tmp_path)
        report = index_state.build_index_state_report(cfg)
        assert "Index state — test-rag" in report
        assert "no manifest" in report.lower() or "No index manifest" in report

    def test_old_manifest_no_live_io(self, tmp_path):
        """Old production manifest works; default path does not call git/Qdrant."""
        cfg = _cfg(tmp_path)
        _write_manifest(
            cfg,
            {
                "files": {
                    "src/foo.py": {
                        "hash": "abc",
                        "mtime": 1_700_000_000.0,
                        "vector_ids": ["id1"],
                    }
                },
                "repo_commits": {
                    "myrepo": {
                        "main_branch": "master",
                        "commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    }
                },
            },
        )
        report = index_state.build_index_state_report(cfg, check_live_git=False)
        assert "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" in report
        assert "indexed_files: 1" in report
        assert "last_index_completed_at:" in report
        # No live git section when check_live_git=False
        assert "matches_indexed" not in report

    def test_index_run_fields(self, tmp_path):
        cfg = _cfg(tmp_path)
        _write_manifest(
            cfg,
            {
                "files": {"a.py": {"hash": "x"}},
                "repo_commits": {},
                "index_run": {
                    "completed_at": "2026-01-01T00:00:00Z",
                    "embed_backend": "tei",
                },
            },
        )
        report = index_state.build_index_state_report(cfg)
        assert "2026-01-01T00:00:00Z" in report
        assert "embed_backend: tei" in report

    def test_branch_overlay_listed(self, tmp_path):
        cfg = _cfg(tmp_path)
        _write_manifest(
            cfg,
            {
                "files": {},
                "repo_commits": {
                    "repo": {
                        "main_branch": "master",
                        "commit": "cccccccccccccccccccccccccccccccccccccccc",
                    }
                },
            },
        )
        branch_path = (
            index_state.get_manifest_dir(cfg) / "index_manifest_branch_feature_foo.json"
        )
        branch_path.write_text(
            json.dumps(
                {
                    "branch": "feature/foo",
                    "last_branch_commit": "dddddddddddddddddddddddddddddddddddddddd",
                    "files": {"a.py": {"hash": "h"}},
                }
            ),
            encoding="utf-8",
        )
        report = index_state.build_index_state_report(cfg)
        assert "feature/foo" in report
        assert "overlays:" in report

    def test_dir_snapshot_from_manifest(self, tmp_path):
        cfg = _cfg(tmp_path)
        _write_manifest(
            cfg,
            {
                "files": {"docs/a.md": {"hash": "h1", "mtime": 1.0}},
                "repo_commits": {},
                "source_snapshots": {
                    "docs": {
                        "type": "directory",
                        "file_count": 1,
                        "latest_mtime": 1.0,
                        "fingerprint": "abcd1234efgh",
                    }
                },
            },
        )
        report = index_state.build_index_state_report(cfg)
        assert "### dir: docs" in report
        assert "fingerprint: abcd1234efgh" in report
