"""Config normalization for git overlays.

`branches: ["feature/example"]` stays kind branch. `overlays` adds tags.
The name is a label. It is not parsed as a ref type.
"""

import types

import pytest

from config_loader import (
    _validate_source_dirs_entries,
    get_repo_groups,
    normalize_overlays,
)


def _git_entry(**extra) -> dict:
    entry = {
        "type": "git_repo",
        "path": "/repos/sample",
        "main_branch": "main",
        "sources": [{"path": "src", "extensions": [".py"]}],
    }
    entry.update(extra)
    return entry


def _cfg(*entries) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        SOURCE_DIRS=list(entries),
        DIFF_FULL_REINDEX_THRESHOLD=0.5,
    )


class TestNormalizeOverlays:
    def test_branches_list_is_kind_branch(self):
        specs = normalize_overlays({"branches": ["feature/example"]})
        assert specs == [
            {"name": "feature/example", "kind": "branch", "diff": "merge_base"}
        ]

    def test_branches_list_matches_explicit_branch_overlay(self):
        from_list = normalize_overlays({"branches": ["feature/example"]})
        from_overlays = normalize_overlays(
            {"overlays": [{"name": "feature/example", "kind": "branch"}]}
        )
        assert from_list == from_overlays

    def test_tag_overlay_requires_against_main_tip(self):
        specs = normalize_overlays(
            {
                "overlays": [
                    {
                        "name": "current_release",
                        "kind": "tag",
                        "diff": "against_main_tip",
                    }
                ]
            }
        )
        assert specs == [
            {
                "name": "current_release",
                "kind": "tag",
                "diff": "against_main_tip",
            }
        ]

    def test_branches_and_overlays_combine_without_duplicating_branch_names(self):
        specs = normalize_overlays(
            {
                "branches": ["feature/example"],
                "overlays": [
                    {
                        "name": "current_release",
                        "kind": "tag",
                        "diff": "against_main_tip",
                    }
                ],
            }
        )
        assert [item["name"] for item in specs] == [
            "current_release",
            "feature/example",
        ]
        assert specs[1]["kind"] == "branch"

    def test_same_branch_name_in_both_forms_is_one_spec(self):
        specs = normalize_overlays(
            {
                "branches": ["feature/example"],
                "overlays": [{"name": "feature/example", "kind": "branch"}],
            }
        )
        assert specs == [
            {"name": "feature/example", "kind": "branch", "diff": "merge_base"}
        ]

    def test_name_is_kept_verbatim(self):
        specs = normalize_overlays({"branches": ["feature/example"]})
        assert specs[0]["name"] == "feature/example"

    def test_tag_without_diff_is_rejected(self):
        with pytest.raises(RuntimeError, match="against_main_tip"):
            normalize_overlays(
                {"overlays": [{"name": "current_release", "kind": "tag"}]}
            )

    def test_branch_cannot_use_tag_diff(self):
        with pytest.raises(RuntimeError, match="merge-base"):
            normalize_overlays(
                {
                    "overlays": [
                        {
                            "name": "feature/example",
                            "kind": "branch",
                            "diff": "against_main_tip",
                        }
                    ]
                }
            )

    def test_conflicting_kind_for_one_name_is_rejected(self):
        with pytest.raises(RuntimeError, match="current_release"):
            normalize_overlays(
                {
                    "branches": ["current_release"],
                    "overlays": [
                        {
                            "name": "current_release",
                            "kind": "tag",
                            "diff": "against_main_tip",
                        }
                    ],
                }
            )

    def test_duplicate_overlay_name_is_rejected(self):
        with pytest.raises(RuntimeError, match="duplicate"):
            normalize_overlays(
                {
                    "overlays": [
                        {"name": "feature/example", "kind": "branch"},
                        {"name": "feature/example", "kind": "branch"},
                    ]
                }
            )

    def test_validate_source_dirs_rejects_bad_tag(self):
        cfg = _cfg(
            _git_entry(overlays=[{"name": "current_release", "kind": "tag"}])
        )
        with pytest.raises(RuntimeError, match="against_main_tip"):
            _validate_source_dirs_entries(cfg, "cfg.py")


class TestRepoGroups:
    def test_branches_list_group_matches_kind_branch_group(self):
        listed = get_repo_groups(_cfg(_git_entry(branches=["feature/example"])))
        explicit = get_repo_groups(
            _cfg(
                _git_entry(
                    overlays=[{"name": "feature/example", "kind": "branch"}]
                )
            )
        )
        assert listed[0]["branches"] == ["feature/example"]
        assert explicit[0]["branches"] == ["feature/example"]
        assert listed[0]["overlays"] == explicit[0]["overlays"]
        assert listed[0]["main_branch"] == "main"

    def test_tag_name_is_not_a_branch_sync_name(self):
        groups = get_repo_groups(
            _cfg(
                _git_entry(
                    branches=["feature/example"],
                    overlays=[
                        {
                            "name": "current_release",
                            "kind": "tag",
                            "diff": "against_main_tip",
                        }
                    ],
                )
            )
        )
        group = groups[0]
        assert group["branches"] == ["feature/example"]
        assert [item["name"] for item in group["overlays"]] == [
            "current_release",
            "feature/example",
        ]

    def test_source_set_has_no_overlays(self):
        groups = get_repo_groups(
            _cfg({"type": "source_set", "path": "docs", "extensions": [".md"]})
        )
        assert groups == []
