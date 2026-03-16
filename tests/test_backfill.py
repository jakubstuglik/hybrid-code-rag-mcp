"""
Tests for branch-related logic in index_rag.py.

Since index_rag.py has heavy module-level side effects (argparse, Docker,
Qdrant connections), we cannot import it in tests.  Instead, we test:

1. The UUID generation logic directly (same formula as make_branch_point_id /
   make_qdrant_point_id — trivial uuid5 calls).
2. The Qdrant filter patterns used by backfill_branch_payload() by constructing
   them directly with qdrant_client.models (same code as in index_rag.py).
3. The canonical prefix map logic via shared.manifest._get_canonical_prefix
   and the _resolve_branch pattern replicated here.

Bug regression tests:
    - IsEmptyCondition vs IsNullCondition (#BUG-1): backfill scroll filter must
      use BOTH IsEmptyCondition (field absent) and IsNullCondition (field
      present with null value) via a ``should`` filter.
    - Canonical prefix mismatch (#BUG-2): prefix map must use
      ``_get_canonical_prefix(entry)`` (e.g. "delphi_src"), NOT raw
      ``entry["path"]`` (e.g. "../my_project/delphi_src").
"""

import uuid

import pytest
from qdrant_client import models


# ────────────────────────────────────────────────
# UUID generation (replicates index_rag.py logic)
# ────────────────────────────────────────────────


def _make_qdrant_point_id(file_key: str, index: int) -> str:
    """Replicate make_qdrant_point_id from index_rag.py."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{file_key}:{index}"))


def _make_branch_point_id(branch: str, file_key: str, index: int) -> str:
    """Replicate make_branch_point_id from index_rag.py."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{branch}::{file_key}:{index}"))


class TestMakeBranchPointId:
    """Tests for branch-namespaced UUID generation."""

    def test_returns_valid_uuid(self):
        """Result is a valid UUID string."""
        result = _make_branch_point_id("feature/foo", "delphi_src/Unit1.pas", 0)
        uuid.UUID(result)  # raises if invalid

    def test_deterministic(self):
        """Same inputs always produce the same UUID."""
        a = _make_branch_point_id("feature/foo", "delphi_src/Unit1.pas", 0)
        b = _make_branch_point_id("feature/foo", "delphi_src/Unit1.pas", 0)
        assert a == b

    def test_different_branch_different_id(self):
        """Different branch names produce different UUIDs."""
        a = _make_branch_point_id("feature/foo", "delphi_src/Unit1.pas", 0)
        b = _make_branch_point_id("feature/bar", "delphi_src/Unit1.pas", 0)
        assert a != b

    def test_different_file_different_id(self):
        """Different file keys produce different UUIDs."""
        a = _make_branch_point_id("feature/foo", "delphi_src/Unit1.pas", 0)
        b = _make_branch_point_id("feature/foo", "delphi_src/Unit2.pas", 0)
        assert a != b

    def test_different_index_different_id(self):
        """Different chunk indices produce different UUIDs."""
        a = _make_branch_point_id("feature/foo", "delphi_src/Unit1.pas", 0)
        b = _make_branch_point_id("feature/foo", "delphi_src/Unit1.pas", 1)
        assert a != b

    def test_never_collides_with_main_id(self):
        """Branch point ID never equals main point ID for same file+index.

        Guaranteed by the ``{branch}::`` prefix in the UUID seed.
        """
        file_key = "delphi_src/Unit1.pas"
        idx = 0
        branch_id = _make_branch_point_id("develop", file_key, idx)
        main_id = _make_qdrant_point_id(file_key, idx)
        assert branch_id != main_id

    def test_special_chars_in_branch_name(self):
        """Branch names with slashes produce valid UUIDs."""
        result = _make_branch_point_id("task/T37523", "delphi_src/Unit1.pas", 0)
        uuid.UUID(result)  # valid UUID

    def test_uuid5_seed_format(self):
        """Verify the UUID seed format is '{branch}::{file_key}:{index}'."""
        expected = str(
            uuid.uuid5(uuid.NAMESPACE_URL, "feature/foo::delphi_src/Unit1.pas:0")
        )
        result = _make_branch_point_id("feature/foo", "delphi_src/Unit1.pas", 0)
        assert result == expected

    def test_main_id_seed_format(self):
        """Verify main UUID seed format is '{file_key}:{index}' (no branch prefix)."""
        expected = str(uuid.uuid5(uuid.NAMESPACE_URL, "delphi_src/Unit1.pas:0"))
        result = _make_qdrant_point_id("delphi_src/Unit1.pas", 0)
        assert result == expected


# ────────────────────────────────────────────────
# Backfill scroll filter pattern (#BUG-1)
# ────────────────────────────────────────────────


def _build_backfill_scroll_filter():
    """Replicate the scroll filter from backfill_branch_payload() in index_rag.py.

    This is the exact pattern used in index_rag.py lines ~649-658.
    """
    return models.Filter(
        should=[
            models.IsNullCondition(
                is_null=models.PayloadField(key="branch"),
            ),
            models.IsEmptyCondition(
                is_empty=models.PayloadField(key="branch"),
            ),
        ],
    )


class TestBackfillScrollFilter:
    """Tests for the Qdrant scroll filter used by backfill_branch_payload().

    BUG-1 REGRESSION: The filter must use BOTH IsEmptyCondition and
    IsNullCondition combined with ``should`` (OR). Pre-existing vectors
    have no ``branch`` key at all (IS EMPTY), while edge cases might have
    an explicit null (IS NULL). Using only one would miss vectors.
    """

    def test_filter_uses_should_clause(self):
        """Filter uses a ``should`` (OR) clause, not ``must``."""
        f = _build_backfill_scroll_filter()
        assert f.should is not None
        assert len(f.should) == 2

    def test_filter_contains_is_null_condition(self):
        """Filter includes IsNullCondition for field-present-with-null-value."""
        f = _build_backfill_scroll_filter()
        types_found = [type(c) for c in f.should]
        assert models.IsNullCondition in types_found, (
            "Filter is missing IsNullCondition"
        )

    def test_filter_contains_is_empty_condition(self):
        """REGRESSION: Filter includes IsEmptyCondition for field-absent.

        Pre-existing vectors have no ``branch`` key at all (absent from payload).
        IsNullCondition alone would match 0 such vectors. IsEmptyCondition
        matches field-absent vectors.
        """
        f = _build_backfill_scroll_filter()
        types_found = [type(c) for c in f.should]
        assert models.IsEmptyCondition in types_found, (
            "Filter is missing IsEmptyCondition — this is a regression of BUG-1: "
            "pre-existing vectors have no 'branch' key, IsNullCondition alone "
            "won't match them."
        )

    def test_both_conditions_target_branch_field(self):
        """Both conditions target the 'branch' field."""
        f = _build_backfill_scroll_filter()
        for clause in f.should:
            if isinstance(clause, models.IsNullCondition):
                assert clause.is_null.key == "branch"
            elif isinstance(clause, models.IsEmptyCondition):
                assert clause.is_empty.key == "branch"

    def test_must_is_none(self):
        """Filter has no ``must`` clause (only ``should``)."""
        f = _build_backfill_scroll_filter()
        assert f.must is None

    def test_must_not_is_none(self):
        """Filter has no ``must_not`` clause."""
        f = _build_backfill_scroll_filter()
        assert f.must_not is None


# ────────────────────────────────────────────────
# Canonical prefix map (#BUG-2)
# ────────────────────────────────────────────────


def _build_prefix_map(entries: list) -> dict:
    """Replicate the prefix map construction from backfill_branch_payload()
    and perform_refresh_qdrant().

    Uses _get_canonical_prefix (the FIX), not raw entry["path"] (the BUG).
    """
    from shared.manifest import _get_canonical_prefix

    prefix_map = {}
    for entry in entries:
        prefix = _get_canonical_prefix(entry)
        if entry.get("_entry_type") == "git_repo":
            prefix_map[prefix] = entry.get("_main_branch")
        else:
            prefix_map[prefix] = None
    return prefix_map


def _resolve_branch(file_key: str, prefix_map: dict) -> str | None:
    """Replicate the _resolve_branch logic from perform_refresh_qdrant().

    This is the exact pattern used in index_rag.py lines ~1271-1283.
    """
    normalized = file_key.replace("\\", "/")
    for prefix, label in prefix_map.items():
        if not prefix or prefix == ".":
            return label
        if normalized.startswith(prefix + "/") or normalized.startswith(prefix + "\\"):
            return label
    return None


class TestCanonicalPrefixMap:
    """Tests for the prefix map construction used by backfill and perform_refresh.

    BUG-2 REGRESSION: The prefix map must use _get_canonical_prefix(entry)
    to get the canonical prefix (e.g. "delphi_src"), NOT the raw entry["path"]
    (e.g. "../my_project/delphi_src"). Qdrant file_path payloads use
    canonical prefixes.
    """

    def test_canonical_prefix_used_not_raw_path(self):
        """REGRESSION: Canonical prefix extracts last segment of path."""
        from shared.manifest import _get_canonical_prefix

        entry = {
            "path": "../my_project/delphi_src",
            "_entry_type": "git_repo",
            "_main_branch": "develop",
        }

        prefix = _get_canonical_prefix(entry)
        assert prefix == "delphi_src", (
            f"Expected 'delphi_src' but got '{prefix}'. "
            "Raw path would be '../my_project/delphi_src' which doesn't "
            "match Qdrant file_path payloads."
        )

    def test_prefix_map_matches_qdrant_file_paths(self):
        """Prefix map entries match canonical file_path prefixes in Qdrant."""
        entries = [
            {
                "path": "../my_project/delphi_src",
                "_entry_type": "git_repo",
                "_main_branch": "develop",
            },
            {
                "path": "../my_project/sql",
                "_entry_type": "git_repo",
                "_main_branch": "develop",
            },
        ]

        prefix_map = _build_prefix_map(entries)
        assert prefix_map == {
            "delphi_src": "develop",
            "sql": "develop",
        }

    def test_resolve_branch_matches_canonical_file_path(self):
        """File paths stored in Qdrant (canonical form) match the prefix map."""
        entries = [
            {
                "path": "../my_project/delphi_src",
                "_entry_type": "git_repo",
                "_main_branch": "develop",
            },
        ]
        prefix_map = _build_prefix_map(entries)

        # Canonical file_path as stored in Qdrant
        assert _resolve_branch("delphi_src/Unit1.pas", prefix_map) == "develop"

    def test_raw_path_does_not_match(self):
        """Raw disk paths should NOT match the canonical prefix map.

        This verifies the bug would manifest if raw paths were used.
        """
        entries = [
            {
                "path": "../my_project/delphi_src",
                "_entry_type": "git_repo",
                "_main_branch": "develop",
            },
        ]
        prefix_map = _build_prefix_map(entries)

        # Raw path — should NOT match canonical prefix "delphi_src"
        assert _resolve_branch("../my_project/delphi_src/Unit1.pas", prefix_map) is None

    def test_non_git_entry_maps_to_none(self):
        """Non-git source_set entries map to None (no branch label)."""
        entries = [
            {
                "path": "docs",
                "_entry_type": "source_set",
            },
        ]
        prefix_map = _build_prefix_map(entries)
        assert prefix_map == {"docs": None}
        assert _resolve_branch("docs/readme.md", prefix_map) is None

    def test_map_to_path_overrides_raw_path(self):
        """When entry has map_to_path, canonical prefix uses it."""
        from shared.manifest import _get_canonical_prefix

        entry = {
            "path": "../my_project/delphi_src",
            "map_to_path": "custom_prefix",
            "_entry_type": "git_repo",
            "_main_branch": "develop",
        }

        prefix = _get_canonical_prefix(entry)
        assert prefix == "custom_prefix"

        prefix_map = _build_prefix_map([entry])
        assert _resolve_branch("custom_prefix/Unit1.pas", prefix_map) == "develop"
        # Raw path doesn't match
        assert _resolve_branch("delphi_src/Unit1.pas", prefix_map) is None

    def test_root_path_matches_everything(self):
        """Root path (empty string) matches all files."""
        entries = [
            {
                "path": "",
                "_entry_type": "git_repo",
                "_main_branch": "master",
            },
        ]
        prefix_map = _build_prefix_map(entries)
        assert _resolve_branch("any/file.pas", prefix_map) == "master"

    def test_dot_path_matches_everything(self):
        """Dot path ('.') matches all files."""
        entries = [
            {
                "path": ".",
                "_entry_type": "git_repo",
                "_main_branch": "master",
            },
        ]
        prefix_map = _build_prefix_map(entries)
        assert _resolve_branch("any/file.pas", prefix_map) == "master"

    def test_deeply_nested_path_uses_last_segment(self):
        """Deeply nested path extracts only the last segment."""
        from shared.manifest import _get_canonical_prefix

        entry = {"path": "../../very/deep/nested/source"}
        assert _get_canonical_prefix(entry) == "source"

    def test_mixed_git_and_source_set(self):
        """Prefix map correctly handles mixed entry types."""
        entries = [
            {
                "path": "../repo/delphi_src",
                "_entry_type": "git_repo",
                "_main_branch": "develop",
            },
            {
                "path": "extra_docs",
                "_entry_type": "source_set",
            },
        ]

        prefix_map = _build_prefix_map(entries)
        assert _resolve_branch("delphi_src/Unit1.pas", prefix_map) == "develop"
        assert _resolve_branch("extra_docs/readme.md", prefix_map) is None

    def test_backslash_paths_normalized(self):
        """Windows-style backslash paths are normalized to forward slash."""
        entries = [
            {
                "path": "../repo/delphi_src",
                "_entry_type": "git_repo",
                "_main_branch": "develop",
            },
        ]
        prefix_map = _build_prefix_map(entries)
        # Windows-style path
        assert _resolve_branch("delphi_src\\Unit1.pas", prefix_map) == "develop"

    def test_unmatched_file_returns_none(self):
        """Files not matching any prefix return None."""
        entries = [
            {
                "path": "../repo/delphi_src",
                "_entry_type": "git_repo",
                "_main_branch": "develop",
            },
        ]
        prefix_map = _build_prefix_map(entries)
        assert _resolve_branch("unknown/file.pas", prefix_map) is None

    def test_correct_branch_label_per_entry(self):
        """Each git_repo entry contributes its own main_branch to the prefix map."""
        entries = [
            {
                "path": "../repo1/src",
                "_entry_type": "git_repo",
                "_main_branch": "develop",
            },
            {
                "path": "../repo2/lib",
                "_entry_type": "git_repo",
                "_main_branch": "main",
            },
        ]
        prefix_map = _build_prefix_map(entries)
        assert _resolve_branch("src/file.pas", prefix_map) == "develop"
        assert _resolve_branch("lib/file.pas", prefix_map) == "main"
