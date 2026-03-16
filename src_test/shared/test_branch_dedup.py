"""
Tests for shared/branch_dedup.py — branch-aware query filtering and dedup.

Tests cover:
    - build_branch_filter(): Qdrant filter construction with IsEmptyCondition
      (NOT IsNullCondition) for absent branch fields, MatchAny for branch values,
      main-only vs main+feature filter shapes
    - dedup_branch_results(): feature-branch preference, tombstone filtering,
      non-git chunk passthrough, score re-sorting, desired_top_k trimming,
      empty input handling
    - get_branch_tombstones(): manifest loading, missing file, corrupt JSON
    - get_main_branch_name(): git_repo extraction, no git_repo fallback

Bug regression tests:
    - IsEmptyCondition vs IsNullCondition (#BUG-1): Pre-existing vectors had no
      ``branch`` key at all (absent from payload). ``IsNullCondition`` matches
      field-present-with-null-value, NOT field-absent. ``IsEmptyCondition``
      matches field-absent. The fix uses ``IsEmptyCondition``.
"""

import json
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import shared.branch_dedup as branch_dedup_mod


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_node_with_score(file_path: str, branch=None, score: float = 1.0):
    """Create a fake NodeWithScore with metadata."""
    node = MagicMock()
    metadata = {"file_path": file_path}
    if branch is not None:
        metadata["branch"] = branch
    node.metadata = metadata
    nws = MagicMock()
    nws.node = node
    nws.score = score
    return nws


def _make_cfg(**kwargs) -> types.ModuleType:
    """Create a fake config module."""
    cfg = types.ModuleType("fake_config")
    for key, value in kwargs.items():
        setattr(cfg, key, value)
    return cfg


# ────────────────────────────────────────────────
# build_branch_filter()
# ────────────────────────────────────────────────


class TestBuildBranchFilter:
    """Tests for build_branch_filter() — Qdrant filter construction."""

    def test_main_only_filter_structure(self):
        """Main-only filter has exactly 2 should clauses."""
        f = branch_dedup_mod.build_branch_filter("develop")
        assert f.should is not None
        assert len(f.should) == 2

    def test_main_only_match_values(self):
        """Main-only filter matches only the main branch name."""
        f = branch_dedup_mod.build_branch_filter("develop")
        field_cond = f.should[0]
        assert field_cond.key == "branch"
        assert field_cond.match.any == ["develop"]

    def test_feature_branch_match_values(self):
        """Feature branch filter includes both main and feature in MatchAny."""
        f = branch_dedup_mod.build_branch_filter("develop", "task/T37523")
        field_cond = f.should[0]
        assert field_cond.match.any == ["develop", "task/T37523"]

    def test_feature_branch_filter_has_two_should_clauses(self):
        """Feature branch filter still has exactly 2 should clauses."""
        f = branch_dedup_mod.build_branch_filter("develop", "task/T37523")
        assert len(f.should) == 2

    # ── BUG REGRESSION: IsEmptyCondition vs IsNullCondition (#BUG-1) ──

    def test_uses_is_empty_condition_not_is_null(self):
        """REGRESSION: Filter must use IsEmptyCondition for absent branch field.

        Pre-existing vectors have no ``branch`` key in their payload at all.
        Qdrant distinguishes between:
          - IsNullCondition: field EXISTS with null value
          - IsEmptyCondition: field is ABSENT from payload entirely

        Using IsNullCondition would match 0 vectors. The fix uses
        IsEmptyCondition.
        """
        from qdrant_client import models

        f = branch_dedup_mod.build_branch_filter("develop")
        empty_clause = f.should[1]

        # Must be IsEmptyCondition, NOT IsNullCondition
        assert isinstance(empty_clause, models.IsEmptyCondition), (
            f"Expected IsEmptyCondition but got {type(empty_clause).__name__}. "
            "This is a regression of BUG-1: IsNullCondition does not match "
            "vectors where the 'branch' field is entirely absent."
        )

    def test_is_empty_targets_branch_field(self):
        """IsEmptyCondition targets the 'branch' field specifically."""
        f = branch_dedup_mod.build_branch_filter("develop")
        empty_clause = f.should[1]
        assert empty_clause.is_empty.key == "branch"

    def test_no_is_null_condition_anywhere(self):
        """Filter must NOT contain any IsNullCondition at all."""
        from qdrant_client import models

        f = branch_dedup_mod.build_branch_filter("develop", "feature/foo")
        for clause in f.should:
            assert not isinstance(clause, models.IsNullCondition), (
                "Filter contains IsNullCondition — this is a regression of BUG-1."
            )

    def test_none_feature_branch_same_as_omitted(self):
        """Passing feature_branch=None is same as not passing it."""
        f1 = branch_dedup_mod.build_branch_filter("master", None)
        f2 = branch_dedup_mod.build_branch_filter("master")
        assert f1.should[0].match.any == f2.should[0].match.any

    def test_empty_string_feature_branch_same_as_omitted(self):
        """Passing feature_branch='' is same as not passing it."""
        f = branch_dedup_mod.build_branch_filter("master", "")
        assert f.should[0].match.any == ["master"]


# ────────────────────────────────────────────────
# dedup_branch_results()
# ────────────────────────────────────────────────


class TestDedupBranchResults:
    """Tests for dedup_branch_results() — post-retrieval deduplication."""

    def test_empty_input_returns_empty(self):
        """Empty list input returns empty list."""
        result = branch_dedup_mod.dedup_branch_results([], "feature", [])
        assert result == []

    def test_none_input_returns_none(self):
        """None input returns None."""
        result = branch_dedup_mod.dedup_branch_results(None, "feature", [])
        assert result is None

    def test_feature_branch_preferred_over_main(self):
        """When same file_path has both main and feature chunks, feature wins."""
        main_node = _make_node_with_score("src/foo.pas", "develop", 0.9)
        feat_node = _make_node_with_score("src/foo.pas", "feature", 0.8)

        result = branch_dedup_mod.dedup_branch_results(
            [main_node, feat_node], "feature", [], desired_top_k=10
        )

        # Only feature-branch chunk should remain
        branches = [n.node.metadata.get("branch") for n in result]
        assert "feature" in branches
        assert "develop" not in branches

    def test_main_kept_when_no_feature_version(self):
        """Files only on main branch are kept."""
        main_node = _make_node_with_score("src/bar.pas", "develop", 0.9)

        result = branch_dedup_mod.dedup_branch_results(
            [main_node], "feature", [], desired_top_k=10
        )
        assert len(result) == 1
        assert result[0].node.metadata["branch"] == "develop"

    def test_non_git_chunks_always_kept(self):
        """Chunks without branch metadata (non-git source_set) always kept."""
        no_branch = _make_node_with_score("docs/readme.md", None, 0.7)

        result = branch_dedup_mod.dedup_branch_results(
            [no_branch], "feature", [], desired_top_k=10
        )
        assert len(result) == 1

    def test_tombstone_filtering(self):
        """Files in tombstone list are removed from results."""
        node = _make_node_with_score("src/deleted.pas", "develop", 0.9)

        result = branch_dedup_mod.dedup_branch_results(
            [node], "feature", ["src/deleted.pas"], desired_top_k=10
        )
        assert len(result) == 0

    def test_tombstone_removes_both_main_and_feature(self):
        """Tombstone applies to all branches of a file."""
        main = _make_node_with_score("src/old.pas", "develop", 0.9)
        feat = _make_node_with_score("src/old.pas", "feature", 0.8)

        result = branch_dedup_mod.dedup_branch_results(
            [main, feat], "feature", ["src/old.pas"], desired_top_k=10
        )
        assert len(result) == 0

    def test_desired_top_k_trims_results(self):
        """Results are trimmed to desired_top_k."""
        nodes = [
            _make_node_with_score(f"src/file{i}.pas", "develop", 1.0 - i * 0.1)
            for i in range(10)
        ]

        result = branch_dedup_mod.dedup_branch_results(
            nodes, "feature", [], desired_top_k=3
        )
        assert len(result) == 3

    def test_results_sorted_by_score_descending(self):
        """Output is sorted by score descending after dedup."""
        n1 = _make_node_with_score("src/a.pas", "develop", 0.5)
        n2 = _make_node_with_score("src/b.pas", "feature", 0.9)
        n3 = _make_node_with_score("src/c.pas", "develop", 0.7)

        result = branch_dedup_mod.dedup_branch_results(
            [n1, n2, n3], "feature", [], desired_top_k=10
        )
        scores = [n.score for n in result]
        assert scores == sorted(scores, reverse=True)

    def test_multiple_chunks_same_file_feature_all_kept(self):
        """Multiple feature-branch chunks from same file are all kept."""
        feat1 = _make_node_with_score("src/foo.pas", "feature", 0.9)
        feat2 = _make_node_with_score("src/foo.pas", "feature", 0.8)
        main1 = _make_node_with_score("src/foo.pas", "develop", 0.95)

        result = branch_dedup_mod.dedup_branch_results(
            [main1, feat1, feat2], "feature", [], desired_top_k=10
        )
        # Both feature chunks kept, main chunk dropped
        assert len(result) == 2
        for n in result:
            assert n.node.metadata["branch"] == "feature"

    def test_no_file_path_nodes_kept(self):
        """Nodes without file_path metadata are preserved."""
        node = _make_node_with_score("", None, 0.5)

        result = branch_dedup_mod.dedup_branch_results(
            [node], "feature", [], desired_top_k=10
        )
        assert len(result) == 1

    def test_mixed_scenario(self):
        """Complex scenario: main, feature, non-git, tombstone, mixed files."""
        # file1: both branches → feature wins
        main_f1 = _make_node_with_score("src/file1.pas", "develop", 0.9)
        feat_f1 = _make_node_with_score("src/file1.pas", "feature", 0.85)
        # file2: only main → kept
        main_f2 = _make_node_with_score("src/file2.pas", "develop", 0.8)
        # file3: tombstoned → removed
        main_f3 = _make_node_with_score("src/file3.pas", "develop", 0.95)
        # file4: non-git → kept
        non_git = _make_node_with_score("docs/help.md", None, 0.7)

        result = branch_dedup_mod.dedup_branch_results(
            [main_f3, main_f1, feat_f1, main_f2, non_git],
            "feature",
            ["src/file3.pas"],
            desired_top_k=10,
        )

        file_paths = [n.node.metadata["file_path"] for n in result]
        # file3 tombstoned → absent
        assert "src/file3.pas" not in file_paths
        # file1 → only feature version
        f1_results = [
            n for n in result if n.node.metadata["file_path"] == "src/file1.pas"
        ]
        assert all(n.node.metadata["branch"] == "feature" for n in f1_results)
        # file2 → main kept
        assert "src/file2.pas" in file_paths
        # non-git → kept
        assert "docs/help.md" in file_paths


# ────────────────────────────────────────────────
# get_branch_tombstones()
# ────────────────────────────────────────────────


class TestGetBranchTombstones:
    """Tests for get_branch_tombstones() — branch manifest tombstone loading."""

    def test_returns_tombstones_from_manifest(self, tmp_path):
        """Loads tombstones list from branch manifest JSON."""
        manifest = {
            "branch": "task/T37523",
            "tombstones": ["src/deleted.pas", "src/old.pas"],
            "files": {},
        }
        manifest_path = tmp_path / "index_manifest_branch_task_T37523.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        cfg = _make_cfg()
        cfg.get_index_path = lambda: str(tmp_path)

        with patch("shared.git_ops.sanitize_branch_name", return_value="task_T37523"):
            result = branch_dedup_mod.get_branch_tombstones("task/T37523", cfg)

        assert result == ["src/deleted.pas", "src/old.pas"]

    def test_missing_manifest_returns_empty(self, tmp_path):
        """Missing manifest file returns empty list."""
        cfg = _make_cfg()
        cfg.get_index_path = lambda: str(tmp_path)

        with patch("shared.git_ops.sanitize_branch_name", return_value="task_T37523"):
            result = branch_dedup_mod.get_branch_tombstones("task/T37523", cfg)

        assert result == []

    def test_corrupt_json_returns_empty(self, tmp_path):
        """Corrupt JSON manifest returns empty list without crashing."""
        manifest_path = tmp_path / "index_manifest_branch_feature_foo.json"
        manifest_path.write_text("{corrupt", encoding="utf-8")

        cfg = _make_cfg()
        cfg.get_index_path = lambda: str(tmp_path)

        with patch("shared.git_ops.sanitize_branch_name", return_value="feature_foo"):
            result = branch_dedup_mod.get_branch_tombstones("feature/foo", cfg)

        assert result == []

    def test_manifest_without_tombstones_key(self, tmp_path):
        """Manifest with no 'tombstones' key returns empty list."""
        manifest = {"branch": "feature/foo", "files": {}}
        manifest_path = tmp_path / "index_manifest_branch_feature_foo.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        cfg = _make_cfg()
        cfg.get_index_path = lambda: str(tmp_path)

        with patch("shared.git_ops.sanitize_branch_name", return_value="feature_foo"):
            result = branch_dedup_mod.get_branch_tombstones("feature/foo", cfg)

        assert result == []


# ────────────────────────────────────────────────
# get_main_branch_name()
# ────────────────────────────────────────────────


class TestGetMainBranchName:
    """Tests for get_main_branch_name() — extract main branch from config."""

    def test_extracts_main_branch_from_git_repo(self):
        """Returns main_branch from first git_repo entry."""
        cfg = _make_cfg(
            SOURCE_DIRS=[
                {"type": "git_repo", "main_branch": "develop", "path": "/repo"},
            ]
        )
        assert branch_dedup_mod.get_main_branch_name(cfg) == "develop"

    def test_defaults_to_master_when_main_branch_absent(self):
        """git_repo without explicit main_branch defaults to 'master'."""
        cfg = _make_cfg(SOURCE_DIRS=[{"type": "git_repo", "path": "/repo"}])
        assert branch_dedup_mod.get_main_branch_name(cfg) == "master"

    def test_no_git_repo_falls_back_to_master(self):
        """Config with only source_set entries falls back to 'master'."""
        cfg = _make_cfg(
            SOURCE_DIRS=[
                {"type": "source_set", "path": "docs"},
            ]
        )
        assert branch_dedup_mod.get_main_branch_name(cfg) == "master"

    def test_empty_source_dirs_falls_back_to_master(self):
        """Empty SOURCE_DIRS falls back to 'master'."""
        cfg = _make_cfg(SOURCE_DIRS=[])
        assert branch_dedup_mod.get_main_branch_name(cfg) == "master"

    def test_no_source_dirs_attr_falls_back_to_master(self):
        """Config without SOURCE_DIRS attribute falls back to 'master'."""
        cfg = _make_cfg()
        assert branch_dedup_mod.get_main_branch_name(cfg) == "master"

    def test_multiple_git_repos_returns_first(self):
        """With multiple git_repo entries, returns the first one's main_branch."""
        cfg = _make_cfg(
            SOURCE_DIRS=[
                {"type": "git_repo", "main_branch": "develop", "path": "/repo1"},
                {"type": "git_repo", "main_branch": "main", "path": "/repo2"},
            ]
        )
        assert branch_dedup_mod.get_main_branch_name(cfg) == "develop"

    def test_skips_non_git_entries(self):
        """Returns main_branch from git_repo even if source_set comes first."""
        cfg = _make_cfg(
            SOURCE_DIRS=[
                {"type": "source_set", "path": "docs"},
                {"type": "git_repo", "main_branch": "trunk", "path": "/repo"},
            ]
        )
        assert branch_dedup_mod.get_main_branch_name(cfg) == "trunk"
