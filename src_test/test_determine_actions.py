"""
Unit tests for the determine_actions() git-diff fast path in index_rag.py.

Since index_rag.py has heavy module-level side effects (argparse, Docker,
Qdrant, torch), we cannot import it in tests.  Instead, we replicate the
four helper functions and the determine_actions() core logic here, injecting
mock git functions.  This tests the algorithm, not the I/O.

Coverage targets:
- _git_prefix_paths: root placeholder normalisation
- _build_repo_group_file_map: entry grouping by repo key
- _file_key_to_git_path: forward mapping (canon → git path)
- _git_path_to_file_key: reverse mapping (git path → canon)
- determine_actions: Case A (commits match), Case B (commits differ),
  Case C (no stored commit / source_set / git error fallback),
  threshold boundary, mtime guard, extension filter, rename handling,
  multi-repo config, branch overlay caller (no manifest → always Case C)
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ─────────────────────────────────────────────────────────────────────────────
# Helpers replicated from index_rag.py
# ─────────────────────────────────────────────────────────────────────────────


def _git_prefix_paths(group: dict) -> list | None:
    """Replicate index_rag._git_prefix_paths."""
    prefixes = group.get("git_prefixes", [])
    if not prefixes:
        return None
    cleaned = [p for p in prefixes if p and p != "."]
    return cleaned if cleaned else None


def _build_repo_group_file_map(resolved_entries: list) -> dict:
    """Replicate index_rag._build_repo_group_file_map."""
    from shared.manifest import make_repo_key

    result: dict = {}
    for entry in resolved_entries:
        if entry["_entry_type"] != "git_repo":
            continue
        repo_key = make_repo_key(entry["_repo_path"])
        result.setdefault(repo_key, []).append(entry)
    return result


def _file_key_to_git_path(file_key: str, entry: dict) -> str | None:
    """Replicate index_rag._file_key_to_git_path."""
    from shared.manifest import _get_canonical_prefix

    canon_prefix = _get_canonical_prefix(entry)
    git_prefix = entry.get("_git_prefix", "") or ""
    if git_prefix == ".":
        git_prefix = ""

    if canon_prefix:
        if not file_key.startswith(canon_prefix + "/"):
            return None
        relative = file_key[len(canon_prefix) + 1 :]
    else:
        relative = file_key

    if git_prefix:
        return f"{git_prefix}/{relative}"
    return relative


def _git_path_to_file_key(git_path: str, entries: list) -> str | None:
    """Replicate index_rag._git_path_to_file_key."""
    from shared.manifest import _get_canonical_prefix

    git_norm = git_path.replace("\\", "/")

    for entry in entries:
        git_prefix = entry.get("_git_prefix", "") or ""
        if git_prefix == ".":
            git_prefix = ""

        if git_prefix:
            if not (git_norm.startswith(git_prefix + "/") or git_norm == git_prefix):
                continue
            relative = git_norm[len(git_prefix) + 1 :] if git_prefix else git_norm
        else:
            relative = git_norm

        ext = "." + relative.rsplit(".", 1)[-1].lower() if "." in relative else ""
        exts_lower = [e.lower() for e in entry.get("extensions", [])]
        if ext not in exts_lower:
            continue

        canon_prefix = _get_canonical_prefix(entry)
        if canon_prefix:
            return f"{canon_prefix}/{relative}"
        return relative

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Fake GitError for testing
# ─────────────────────────────────────────────────────────────────────────────


class _GitError(Exception):
    """Stand-in for shared.git_ops.GitError."""


# ─────────────────────────────────────────────────────────────────────────────
# determine_actions replicated with injectable git functions
# ─────────────────────────────────────────────────────────────────────────────


def _determine_actions(
    old_files: dict,
    current_states: dict,
    manifest: dict | None = None,
    *,
    # Injected dependencies (for testing)
    repo_groups: list | None = None,
    resolved_entries: list | None = None,
    git_validate_fn=None,
    git_head_fn=None,
    git_diff_fn=None,
    threshold: float = 0.5,
    GitError=_GitError,
) -> dict:
    """
    Replicated logic of index_rag.determine_actions().

    The production version calls get_repo_groups(config), resolve_source_entries(config),
    validate_git_repo(...), get_branch_head(...), diff_commits(...) etc.  Here those
    are passed as injectable parameters so tests can supply mocks without importing
    index_rag.py.
    """
    from shared.manifest import make_repo_key

    actions: dict = {"add": [], "modify": [], "delete": []}
    skip_hash_check: set = set()

    if manifest is not None and repo_groups is not None:
        repo_commits = manifest.get("repo_commits", {})
        resolved = resolved_entries or []
        repo_entry_map = _build_repo_group_file_map(resolved)

        for group in repo_groups:
            repo_path = group["repo_path"]
            main_branch = group["main_branch"]
            repo_key = make_repo_key(repo_path)
            entries_for_repo = repo_entry_map.get(repo_key, [])

            stored_entry = repo_commits.get(repo_key)
            if not stored_entry:
                continue  # Case C

            stored_commit = stored_entry.get("commit", "")
            if not stored_commit:
                continue  # Case C

            # Get current HEAD
            try:
                if git_validate_fn and not git_validate_fn(repo_path):
                    continue
                current_commit = (
                    git_head_fn(repo_path, main_branch)
                    if git_head_fn
                    else stored_commit
                )
            except GitError as exc:
                continue  # Case C fallback

            if current_commit == stored_commit:
                # ── Case A ──
                for path_key, old_entry in old_files.items():
                    if path_key not in current_states:
                        continue
                    current = current_states[path_key]
                    belongs = any(
                        _file_key_to_git_path(path_key, e) is not None
                        for e in entries_for_repo
                    )
                    if not belongs:
                        continue
                    stored_mtime = old_entry.get("mtime", 0)
                    current_mtime = current.get("mtime", 0)
                    if int(stored_mtime) == int(current_mtime):
                        skip_hash_check.add(path_key)

            else:
                # ── Case B ──
                git_paths = _git_prefix_paths(group)
                try:
                    changes = (
                        git_diff_fn(
                            repo_path, stored_commit, current_commit, paths=git_paths
                        )
                        if git_diff_fn
                        else []
                    )
                except GitError:
                    continue  # Case C fallback

                repo_manifest_keys = {
                    k
                    for k in old_files
                    if any(
                        _file_key_to_git_path(k, e) is not None
                        for e in entries_for_repo
                    )
                }

                total_in_manifest = len(repo_manifest_keys)
                changed_file_keys = set()
                for status, git_path in changes:
                    fk = _git_path_to_file_key(git_path, entries_for_repo)
                    if fk:
                        changed_file_keys.add(fk)

                if total_in_manifest > 0:
                    ratio = len(changed_file_keys) / total_in_manifest
                    if ratio > threshold:
                        continue  # Case C fallback

                for path_key in repo_manifest_keys:
                    if path_key in current_states and path_key not in changed_file_keys:
                        old_entry = old_files[path_key]
                        current = current_states[path_key]
                        if int(old_entry.get("mtime", 0)) == int(
                            current.get("mtime", 0)
                        ):
                            skip_hash_check.add(path_key)

    # ── Main comparison loop ──
    for path_key, current in current_states.items():
        if path_key not in old_files:
            actions["add"].append(path_key)
        elif path_key in skip_hash_check:
            pass  # fast path: assume unchanged
        else:
            old_entry = old_files[path_key]
            if current["hash"] != old_entry.get("hash", ""):
                actions["modify"].append(path_key)

    # Find deletes
    for path_key in old_files:
        if path_key not in current_states:
            actions["delete"].append(path_key)

    return actions


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures and helpers
# ─────────────────────────────────────────────────────────────────────────────

REPO_PATH = "/fake/repo"
REPO_KEY = "repo"  # make_repo_key("/fake/repo") -> "repo"


def _make_entry(path="delphi_src", git_prefix="delphi_src", exts=(".pas", ".dfm")):
    """Build a minimal resolved git_repo entry."""
    return {
        "path": f"{REPO_PATH}/{path}",
        "extensions": list(exts),
        "exclude": [],
        "_entry_type": "git_repo",
        "_repo_path": REPO_PATH,
        "_git_prefix": git_prefix,
        "_main_branch": "develop",
        "_branches": [],
        "_diff_threshold": 0.5,
    }


def _make_group(
    path=REPO_PATH,
    main_branch="develop",
    git_prefixes=None,
    branches=None,
):
    """Build a minimal repo group dict."""
    return {
        "repo_path": path,
        "main_branch": main_branch,
        "branches": branches or [],
        "git_prefixes": git_prefixes or ["delphi_src"],
        "resolved_entries": [],
    }


def _state(hash_val="abc123", mtime=1000):
    return {"hash": hash_val, "mtime": mtime}


def _old_entry(hash_val="abc123", mtime=1000):
    return {"hash": hash_val, "mtime": mtime}


STORED_COMMIT = "aaa" * 13 + "aa"  # 40 chars
CURRENT_COMMIT = "bbb" * 13 + "bb"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _git_prefix_paths
# ─────────────────────────────────────────────────────────────────────────────


class TestGitPrefixPaths:
    def test_empty_prefixes_returns_none(self):
        group = {"git_prefixes": []}
        assert _git_prefix_paths(group) is None

    def test_missing_key_returns_none(self):
        assert _git_prefix_paths({}) is None

    def test_root_placeholder_dot_filtered(self):
        group = {"git_prefixes": ["."]}
        assert _git_prefix_paths(group) is None

    def test_empty_string_filtered(self):
        group = {"git_prefixes": [""]}
        assert _git_prefix_paths(group) is None

    def test_normal_prefix_returned(self):
        group = {"git_prefixes": ["delphi_src"]}
        assert _git_prefix_paths(group) == ["delphi_src"]

    def test_mixed_filters_root_keeps_real(self):
        group = {"git_prefixes": [".", "delphi_src", ""]}
        assert _git_prefix_paths(group) == ["delphi_src"]

    def test_multiple_prefixes(self):
        group = {"git_prefixes": ["src", "lib"]}
        assert _git_prefix_paths(group) == ["src", "lib"]

    def test_all_root_placeholders_returns_none(self):
        group = {"git_prefixes": [".", "", "."]}
        assert _git_prefix_paths(group) is None


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _build_repo_group_file_map
# ─────────────────────────────────────────────────────────────────────────────


class TestBuildRepoGroupFileMap:
    def test_empty_input(self):
        assert _build_repo_group_file_map([]) == {}

    def test_source_set_excluded(self):
        entries = [
            {
                "_entry_type": "source_set",
                "_repo_path": None,
                "path": "/some/dir",
            }
        ]
        assert _build_repo_group_file_map(entries) == {}

    def test_git_repo_entry_included(self):
        entry = _make_entry()
        result = _build_repo_group_file_map([entry])
        assert REPO_KEY in result
        assert result[REPO_KEY] == [entry]

    def test_multiple_entries_same_repo(self):
        e1 = _make_entry("src1", "src1")
        e2 = _make_entry("src2", "src2")
        result = _build_repo_group_file_map([e1, e2])
        assert len(result[REPO_KEY]) == 2

    def test_two_repos_separate_keys(self):
        e1 = _make_entry()
        e2 = {
            **_make_entry(),
            "_repo_path": "/other/repo2",
            "path": "/other/repo2/src",
        }
        result = _build_repo_group_file_map([e1, e2])
        assert len(result) == 2


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _file_key_to_git_path
# ─────────────────────────────────────────────────────────────────────────────


class TestFileKeyToGitPath:
    def test_simple_mapping(self):
        entry = _make_entry("delphi_src", "delphi_src")
        result = _file_key_to_git_path("delphi_src/Unit1.pas", entry)
        assert result == "delphi_src/Unit1.pas"

    def test_no_git_prefix_returns_relative(self):
        entry = {
            **_make_entry(".", "."),
            "_git_prefix": ".",
        }
        # canon prefix from path="../fake/repo/." → last segment = "."
        # Actually path is REPO_PATH+"/" + "." => we need a specific case
        # Use a path whose last segment is the prefix
        entry2 = _make_entry("mydir", "")
        # _get_canonical_prefix("REPO_PATH/mydir") → "mydir"
        result = _file_key_to_git_path("mydir/File.pas", entry2)
        assert result == "File.pas"

    def test_wrong_prefix_returns_none(self):
        entry = _make_entry("delphi_src", "delphi_src")
        result = _file_key_to_git_path("other/Unit1.pas", entry)
        assert result is None

    def test_dot_git_prefix_stripped(self):
        entry = {
            "path": REPO_PATH,
            "extensions": [".pas"],
            "exclude": [],
            "_entry_type": "git_repo",
            "_repo_path": REPO_PATH,
            "_git_prefix": ".",
            "_main_branch": "develop",
            "_branches": [],
            "_diff_threshold": 0.5,
            "map_to_path": "root",  # explicit canon prefix
        }
        result = _file_key_to_git_path("root/Unit1.pas", entry)
        # git_prefix "." is stripped → just "Unit1.pas"
        assert result == "Unit1.pas"

    def test_map_to_path_used_as_canon_prefix(self):
        entry = {
            **_make_entry("delphi_src", "sources"),
            "map_to_path": "my_sources",
        }
        result = _file_key_to_git_path("my_sources/Unit1.pas", entry)
        assert result == "sources/Unit1.pas"

    def test_nested_file(self):
        entry = _make_entry("delphi_src", "delphi_src")
        result = _file_key_to_git_path("delphi_src/sub/dir/Unit1.pas", entry)
        assert result == "delphi_src/sub/dir/Unit1.pas"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _git_path_to_file_key
# ─────────────────────────────────────────────────────────────────────────────


class TestGitPathToFileKey:
    def test_simple_reverse(self):
        entry = _make_entry("delphi_src", "delphi_src")
        result = _git_path_to_file_key("delphi_src/Unit1.pas", [entry])
        assert result == "delphi_src/Unit1.pas"

    def test_extension_not_indexed_returns_none(self):
        entry = _make_entry("delphi_src", "delphi_src", exts=(".pas",))
        result = _git_path_to_file_key("delphi_src/readme.txt", [entry])
        assert result is None

    def test_wrong_prefix_returns_none(self):
        entry = _make_entry("delphi_src", "delphi_src")
        result = _git_path_to_file_key("other_dir/Unit1.pas", [entry])
        assert result is None

    def test_backslash_normalised(self):
        entry = _make_entry("delphi_src", "delphi_src")
        result = _git_path_to_file_key("delphi_src\\Unit1.pas", [entry])
        assert result == "delphi_src/Unit1.pas"

    def test_no_git_prefix_root_entry(self):
        entry = {
            "path": REPO_PATH,
            "extensions": [".pas"],
            "exclude": [],
            "_entry_type": "git_repo",
            "_repo_path": REPO_PATH,
            "_git_prefix": "",
            "_main_branch": "develop",
            "_branches": [],
            "_diff_threshold": 0.5,
            "map_to_path": "root_src",
        }
        result = _git_path_to_file_key("Unit1.pas", [entry])
        assert result == "root_src/Unit1.pas"

    def test_multiple_entries_first_match_wins(self):
        e1 = _make_entry("src1", "src1", exts=(".pas",))
        e2 = _make_entry("src2", "src2", exts=(".pas",))
        # src1/Unit1.pas → should match e1
        result = _git_path_to_file_key("src1/Unit1.pas", [e1, e2])
        assert result == "src1/Unit1.pas"

    def test_map_to_path_in_file_key(self):
        entry = {
            **_make_entry("delphi_src", "sources"),
            "map_to_path": "custom",
        }
        result = _git_path_to_file_key("sources/Unit1.pas", [entry])
        assert result == "custom/Unit1.pas"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: determine_actions — Case C (no fast path)
# ─────────────────────────────────────────────────────────────────────────────


class TestDetermineActionsBasic:
    """Basic behaviour with no manifest (always Case C)."""

    def test_new_file_added(self):
        actions = _determine_actions(
            old_files={},
            current_states={"src/a.pas": _state("h1")},
        )
        assert actions["add"] == ["src/a.pas"]
        assert actions["modify"] == []
        assert actions["delete"] == []

    def test_deleted_file(self):
        actions = _determine_actions(
            old_files={"src/a.pas": _old_entry("h1")},
            current_states={},
        )
        assert actions["delete"] == ["src/a.pas"]
        assert actions["add"] == []

    def test_modified_file(self):
        actions = _determine_actions(
            old_files={"src/a.pas": _old_entry("h1")},
            current_states={"src/a.pas": _state("h2")},
        )
        assert actions["modify"] == ["src/a.pas"]

    def test_unchanged_file(self):
        actions = _determine_actions(
            old_files={"src/a.pas": _old_entry("h1")},
            current_states={"src/a.pas": _state("h1")},
        )
        assert actions["add"] == []
        assert actions["modify"] == []
        assert actions["delete"] == []

    def test_no_manifest_no_fast_path(self):
        """Passing manifest=None always does full hash scan."""
        actions = _determine_actions(
            old_files={"src/a.pas": _old_entry("h1")},
            current_states={"src/a.pas": _state("h2")},
            manifest=None,
        )
        assert actions["modify"] == ["src/a.pas"]

    def test_manifest_but_no_repo_groups_is_case_c(self):
        """Manifest with empty repo_commits → full hash scan."""
        actions = _determine_actions(
            old_files={"src/a.pas": _old_entry("h1")},
            current_states={"src/a.pas": _state("h2")},
            manifest={"repo_commits": {}},
            repo_groups=[],
            resolved_entries=[],
        )
        assert actions["modify"] == ["src/a.pas"]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: determine_actions — Case A (commits match)
# ─────────────────────────────────────────────────────────────────────────────


class TestDetermineActionsCaseA:
    """Case A: stored_commit == current_HEAD → only re-hash mtime-changed files."""

    def _run(self, old_files, current_states, mtime_match=True):
        entry = _make_entry()
        group = _make_group()
        manifest = {
            "repo_commits": {
                REPO_KEY: {"commit": STORED_COMMIT, "main_branch": "develop"}
            }
        }
        return _determine_actions(
            old_files=old_files,
            current_states=current_states,
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=lambda p: True,
            git_head_fn=lambda p, b: STORED_COMMIT,  # same commit → Case A
        )

    def test_unchanged_file_skipped(self):
        """File with same hash and mtime is not checked and not added to modify."""
        actions = self._run(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h1", mtime=1000)},
        )
        assert actions["modify"] == []

    def test_mtime_changed_hash_changed_is_modify(self):
        """File with mtime change and hash change → modify."""
        actions = self._run(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h2", mtime=2000)},
        )
        assert actions["modify"] == ["delphi_src/Unit1.pas"]

    def test_mtime_changed_hash_unchanged_is_not_modify(self):
        """mtime drift but same content hash → not a modification (mtime-only drift)."""
        actions = self._run(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h1", mtime=2000)},
        )
        # mtime drift → hash IS checked → same hash → not in modify
        assert actions["modify"] == []

    def test_new_file_added(self):
        """New on-disk file not in manifest → add."""
        actions = self._run(
            old_files={},
            current_states={"delphi_src/New.pas": _state("h1", mtime=1000)},
        )
        assert actions["add"] == ["delphi_src/New.pas"]

    def test_deleted_file_removed(self):
        """File in manifest but not on disk → delete."""
        actions = self._run(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={},
        )
        assert actions["delete"] == ["delphi_src/Unit1.pas"]

    def test_non_repo_file_still_hash_checked(self):
        """source_set file (not in repo group) uses full hash scan."""
        # The file key doesn't belong to any entry in entries_for_repo
        actions = self._run(
            old_files={"other_source/Doc.txt": _old_entry("h1", mtime=1000)},
            current_states={"other_source/Doc.txt": _state("h2", mtime=1000)},
        )
        # Not in skip_hash_check → hash compared → modify
        assert actions["modify"] == ["other_source/Doc.txt"]

    def test_git_validate_fails_falls_back_to_case_c(self):
        """If validate_git_repo returns False, Case C: full hash scan."""
        entry = _make_entry()
        group = _make_group()
        manifest = {
            "repo_commits": {
                REPO_KEY: {"commit": STORED_COMMIT, "main_branch": "develop"}
            }
        }
        actions = _determine_actions(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h2", mtime=1000)},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=lambda p: False,  # validation fails
            git_head_fn=lambda p, b: STORED_COMMIT,
        )
        # Case C: hash comparison → h1 != h2 → modify
        assert actions["modify"] == ["delphi_src/Unit1.pas"]

    def test_git_head_raises_falls_back_to_case_c(self):
        """If get_branch_head raises GitError, Case C fallback."""
        entry = _make_entry()
        group = _make_group()
        manifest = {
            "repo_commits": {
                REPO_KEY: {"commit": STORED_COMMIT, "main_branch": "develop"}
            }
        }

        def _raise(p, b):
            raise _GitError("not a repo")

        actions = _determine_actions(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h2", mtime=1000)},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=lambda p: True,
            git_head_fn=_raise,
            GitError=_GitError,
        )
        assert actions["modify"] == ["delphi_src/Unit1.pas"]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: determine_actions — Case B (commits differ)
# ─────────────────────────────────────────────────────────────────────────────


class TestDetermineActionsCaseB:
    """Case B: commits differ → git diff narrows candidate set."""

    def _run(
        self,
        old_files,
        current_states,
        diff_changes=None,  # list of (status, git_path)
        threshold=0.5,
    ):
        entry = _make_entry()
        group = _make_group()
        manifest = {
            "repo_commits": {
                REPO_KEY: {"commit": STORED_COMMIT, "main_branch": "develop"}
            }
        }
        return _determine_actions(
            old_files=old_files,
            current_states=current_states,
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=lambda p: True,
            git_head_fn=lambda p, b: CURRENT_COMMIT,  # different → Case B
            git_diff_fn=lambda p, a, b, paths=None: diff_changes or [],
            threshold=threshold,
        )

    def test_unchanged_file_not_in_diff_skipped(self):
        """File not in diff and mtime unchanged → skip hash check."""
        actions = self._run(
            old_files={
                "delphi_src/Unit1.pas": _old_entry("h1", mtime=1000),
                "delphi_src/Unit2.pas": _old_entry("h2", mtime=1000),
            },
            current_states={
                "delphi_src/Unit1.pas": _state("h1", mtime=1000),
                "delphi_src/Unit2.pas": _state("h2", mtime=1000),
            },
            diff_changes=[("M", "delphi_src/Unit1.pas")],
        )
        # Unit1 is in diff → hash checked → h1==h1 → not modify
        # Unit2 not in diff + mtime same → skipped
        assert actions["modify"] == []

    def test_file_in_diff_with_hash_change_is_modify(self):
        """File in diff with hash change → modify."""
        actions = self._run(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h2", mtime=1000)},
            diff_changes=[("M", "delphi_src/Unit1.pas")],
        )
        assert actions["modify"] == ["delphi_src/Unit1.pas"]

    def test_file_in_diff_no_hash_change_not_modify(self):
        """File in diff but hash unchanged → not modify (content same)."""
        actions = self._run(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h1", mtime=2000)},
            diff_changes=[("M", "delphi_src/Unit1.pas")],
        )
        assert actions["modify"] == []

    def test_threshold_exceeded_falls_back_to_full_hash(self):
        """If changed / total > threshold, fall back to full hash scan."""
        # 3 files in manifest, 2 changed → 2/3 = 67% > 50% threshold
        old = {
            "delphi_src/A.pas": _old_entry("h1", mtime=1000),
            "delphi_src/B.pas": _old_entry("h2", mtime=1000),
            "delphi_src/C.pas": _old_entry("h3", mtime=1000),
        }
        current = {
            "delphi_src/A.pas": _state("h1", mtime=1000),
            "delphi_src/B.pas": _state("h2_new", mtime=1000),
            "delphi_src/C.pas": _state("h3_new", mtime=1000),
        }
        actions = self._run(
            old_files=old,
            current_states=current,
            diff_changes=[
                ("M", "delphi_src/B.pas"),
                ("M", "delphi_src/C.pas"),
            ],
            threshold=0.5,
        )
        # Threshold exceeded → Case C fallback → full hash → B and C modified
        assert sorted(actions["modify"]) == ["delphi_src/B.pas", "delphi_src/C.pas"]

    def test_threshold_not_exceeded_skips_unchanged(self):
        """If changed / total <= threshold, fast path applies."""
        # 10 files, 1 changed → 1/10 = 10% <= 50%
        old = {
            f"delphi_src/U{i}.pas": _old_entry(f"h{i}", mtime=1000) for i in range(10)
        }
        current = {k: _state(v["hash"], mtime=1000) for k, v in old.items()}
        # Change U0
        current["delphi_src/U0.pas"] = _state("h0_new", mtime=1000)

        actions = self._run(
            old_files=old,
            current_states=current,
            diff_changes=[("M", "delphi_src/U0.pas")],
            threshold=0.5,
        )
        assert actions["modify"] == ["delphi_src/U0.pas"]
        # Other 9 files skipped (in fast path)
        assert len(actions["add"]) == 0
        assert len(actions["delete"]) == 0

    def test_threshold_boundary_exact_not_exceeded(self):
        """Exactly at threshold (ratio == threshold) → fast path (not > threshold)."""
        # 2 files, 1 changed → 1/2 = 50% == threshold (not strictly >)
        old = {
            "delphi_src/A.pas": _old_entry("h1", mtime=1000),
            "delphi_src/B.pas": _old_entry("h2", mtime=1000),
        }
        current = {
            "delphi_src/A.pas": _state("h1_new", mtime=1000),
            "delphi_src/B.pas": _state("h2", mtime=1000),
        }
        actions = self._run(
            old_files=old,
            current_states=current,
            diff_changes=[("M", "delphi_src/A.pas")],
            threshold=0.5,
        )
        # 1/2 = 0.5 == threshold → not > → fast path
        # A in diff → hash checked → h1 != h1_new → modify
        # B not in diff + mtime same → skipped
        assert actions["modify"] == ["delphi_src/A.pas"]

    def test_git_diff_raises_falls_back_to_case_c(self):
        """If diff_commits raises GitError, fall back to full hash scan."""
        entry = _make_entry()
        group = _make_group()
        manifest = {
            "repo_commits": {
                REPO_KEY: {"commit": STORED_COMMIT, "main_branch": "develop"}
            }
        }

        def _raise(p, a, b, paths=None):
            raise _GitError("shallow clone")

        actions = _determine_actions(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h2", mtime=1000)},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=lambda p: True,
            git_head_fn=lambda p, b: CURRENT_COMMIT,
            git_diff_fn=_raise,
            GitError=_GitError,
        )
        # Case C fallback: full hash → h1 != h2 → modify
        assert actions["modify"] == ["delphi_src/Unit1.pas"]

    def test_mtime_guard_in_case_b(self):
        """In Case B, mtime change on non-diff file still causes hash check."""
        # U0 in diff, U1 NOT in diff but mtime changed
        old = {
            "delphi_src/U0.pas": _old_entry("h0", mtime=1000),
            "delphi_src/U1.pas": _old_entry("h1", mtime=1000),
        }
        current = {
            "delphi_src/U0.pas": _state("h0", mtime=1000),
            "delphi_src/U1.pas": _state(
                "h1_new", mtime=2000
            ),  # mtime changed + hash changed
        }
        actions = self._run(
            old_files=old,
            current_states=current,
            diff_changes=[("M", "delphi_src/U0.pas")],
        )
        # U1 not in diff, but mtime changed → not in skip_hash_check → h1 != h1_new → modify
        assert "delphi_src/U1.pas" in actions["modify"]

    def test_new_file_not_in_manifest_added(self):
        """New on-disk file not in old manifest → add (regardless of diff)."""
        actions = self._run(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={
                "delphi_src/Unit1.pas": _state("h1", mtime=1000),
                "delphi_src/NewFile.pas": _state("hN", mtime=1000),
            },
            diff_changes=[("A", "delphi_src/NewFile.pas")],
        )
        assert actions["add"] == ["delphi_src/NewFile.pas"]

    def test_deleted_file_caught_regardless_of_diff(self):
        """File in manifest but not on disk → delete (main loop always runs)."""
        actions = self._run(
            old_files={
                "delphi_src/Unit1.pas": _old_entry("h1", mtime=1000),
                "delphi_src/Gone.pas": _old_entry("hG", mtime=1000),
            },
            current_states={
                "delphi_src/Unit1.pas": _state("h1", mtime=1000),
            },
            diff_changes=[("D", "delphi_src/Gone.pas")],
        )
        assert actions["delete"] == ["delphi_src/Gone.pas"]

    def test_rename_delete_and_add(self):
        """Rename produces a delete of the old key and add of the new key."""
        actions = self._run(
            old_files={"delphi_src/OldName.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/NewName.pas": _state("h1", mtime=1000)},
            diff_changes=[
                ("D", "delphi_src/OldName.pas"),
                ("A", "delphi_src/NewName.pas"),
            ],
        )
        assert actions["delete"] == ["delphi_src/OldName.pas"]
        assert actions["add"] == ["delphi_src/NewName.pas"]

    def test_extension_not_indexed_ignored_in_diff(self):
        """Git-diff path with un-indexed extension is not added to changed_file_keys."""
        entry = _make_entry(exts=(".pas",))  # only .pas indexed
        group = _make_group()
        manifest = {
            "repo_commits": {
                REPO_KEY: {"commit": STORED_COMMIT, "main_branch": "develop"}
            }
        }
        actions = _determine_actions(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h1", mtime=1000)},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=lambda p: True,
            git_head_fn=lambda p, b: CURRENT_COMMIT,
            git_diff_fn=lambda p, a, b, paths=None: [
                ("M", "delphi_src/readme.txt"),  # not indexed
            ],
        )
        # Unit1.pas not in diff, mtime same → skip → no modify
        assert actions["modify"] == []


# ─────────────────────────────────────────────────────────────────────────────
# Tests: determine_actions — Case C (no stored commit / source_set)
# ─────────────────────────────────────────────────────────────────────────────


class TestDetermineActionsCaseC:
    def test_no_repo_commits_in_manifest(self):
        """Manifest with no repo_commits key → Case C for all files."""
        entry = _make_entry()
        group = _make_group()
        manifest = {}  # no repo_commits
        actions = _determine_actions(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h2", mtime=1000)},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=lambda p: True,
            git_head_fn=lambda p, b: CURRENT_COMMIT,
        )
        assert actions["modify"] == ["delphi_src/Unit1.pas"]

    def test_empty_stored_commit_is_case_c(self):
        """Empty stored commit string → Case C."""
        entry = _make_entry()
        group = _make_group()
        manifest = {
            "repo_commits": {REPO_KEY: {"commit": "", "main_branch": "develop"}}
        }
        actions = _determine_actions(
            old_files={"delphi_src/Unit1.pas": _old_entry("h1", mtime=1000)},
            current_states={"delphi_src/Unit1.pas": _state("h2", mtime=1000)},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
        )
        assert actions["modify"] == ["delphi_src/Unit1.pas"]

    def test_source_set_entry_not_affected_by_fast_path(self):
        """source_set entries are excluded from _build_repo_group_file_map → Case C."""
        source_entry = {
            "path": "/some/dir",
            "extensions": [".pas"],
            "exclude": [],
            "_entry_type": "source_set",
            "_repo_path": None,
            "_git_prefix": None,
            "_main_branch": None,
            "_branches": [],
            "_diff_threshold": None,
        }
        group = _make_group()
        manifest = {
            "repo_commits": {
                REPO_KEY: {"commit": STORED_COMMIT, "main_branch": "develop"}
            }
        }
        actions = _determine_actions(
            old_files={"some_dir/A.pas": _old_entry("h1", mtime=1000)},
            current_states={"some_dir/A.pas": _state("h2", mtime=1000)},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[source_entry],
            git_validate_fn=lambda p: True,
            git_head_fn=lambda p, b: STORED_COMMIT,
        )
        # source_set not in repo_entry_map → file not in skip_hash_check → hash compared
        assert actions["modify"] == ["some_dir/A.pas"]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: determine_actions — multi-repo config
# ─────────────────────────────────────────────────────────────────────────────


class TestDetermineActionsMultiRepo:
    """Tests with two independent repos in config."""

    def _make_two_repo_setup(self):
        repo1 = "/fake/repo1"
        repo2 = "/fake/repo2"
        key1 = "repo1"  # make_repo_key("/fake/repo1")
        key2 = "repo2"  # make_repo_key("/fake/repo2")

        entry1 = {
            "path": f"{repo1}/src",
            "extensions": [".pas"],
            "exclude": [],
            "_entry_type": "git_repo",
            "_repo_path": repo1,
            "_git_prefix": "src",
            "_main_branch": "develop",
            "_branches": [],
            "_diff_threshold": 0.5,
        }
        entry2 = {
            "path": f"{repo2}/lib",
            "extensions": [".pas"],
            "exclude": [],
            "_entry_type": "git_repo",
            "_repo_path": repo2,
            "_git_prefix": "lib",
            "_main_branch": "main",
            "_branches": [],
            "_diff_threshold": 0.5,
        }
        group1 = {
            "repo_path": repo1,
            "main_branch": "develop",
            "branches": [],
            "git_prefixes": ["src"],
            "resolved_entries": [],
        }
        group2 = {
            "repo_path": repo2,
            "main_branch": "main",
            "branches": [],
            "git_prefixes": ["lib"],
            "resolved_entries": [],
        }
        return repo1, repo2, key1, key2, entry1, entry2, group1, group2

    def test_two_repos_independent_fast_path(self):
        """Repo1 at same commit (Case A), Repo2 at different commit (Case B)."""
        repo1, repo2, key1, key2, entry1, entry2, group1, group2 = (
            self._make_two_repo_setup()
        )

        commit_r1 = "aaa" * 13 + "aa"
        commit_r2_old = "bbb" * 13 + "bb"
        commit_r2_new = "ccc" * 13 + "cc"

        manifest = {
            "repo_commits": {
                key1: {"commit": commit_r1, "main_branch": "develop"},
                key2: {"commit": commit_r2_old, "main_branch": "main"},
            }
        }

        def head_fn(p, b):
            if "repo1" in p:
                return commit_r1  # same → Case A
            return commit_r2_new  # different → Case B

        def diff_fn(p, a, b, paths=None):
            if "repo2" in p:
                return [("M", "lib/Changed.pas")]
            return []

        old = {
            "src/Unit1.pas": _old_entry("h1", mtime=1000),
            "lib/Changed.pas": _old_entry("hC", mtime=1000),
            "lib/Stable.pas": _old_entry("hS", mtime=1000),
        }
        current = {
            "src/Unit1.pas": _state("h1", mtime=1000),
            "lib/Changed.pas": _state("hC_new", mtime=1000),
            "lib/Stable.pas": _state("hS", mtime=1000),
        }

        actions = _determine_actions(
            old_files=old,
            current_states=current,
            manifest=manifest,
            repo_groups=[group1, group2],
            resolved_entries=[entry1, entry2],
            git_validate_fn=lambda p: True,
            git_head_fn=head_fn,
            git_diff_fn=diff_fn,
        )

        # repo1/Unit1.pas: Case A, mtime same → skipped → not modify
        assert "src/Unit1.pas" not in actions["modify"]
        # repo2/Changed.pas: Case B, in diff, hash changed → modify
        assert "lib/Changed.pas" in actions["modify"]
        # repo2/Stable.pas: Case B, not in diff, mtime same → skipped
        assert "lib/Stable.pas" not in actions["modify"]

    def test_one_repo_no_stored_commit_case_c(self):
        """If one repo has no stored commit, it uses full hash; other uses fast path."""
        repo1, repo2, key1, key2, entry1, entry2, group1, group2 = (
            self._make_two_repo_setup()
        )

        commit_r1 = "aaa" * 13 + "aa"
        manifest = {
            "repo_commits": {
                key1: {"commit": commit_r1, "main_branch": "develop"},
                # key2 absent → Case C
            }
        }

        old = {
            "src/Unit1.pas": _old_entry("h1", mtime=1000),
            "lib/Unit2.pas": _old_entry("h2", mtime=1000),
        }
        current = {
            "src/Unit1.pas": _state("h1", mtime=1000),
            "lib/Unit2.pas": _state("h2_new", mtime=1000),
        }

        actions = _determine_actions(
            old_files=old,
            current_states=current,
            manifest=manifest,
            repo_groups=[group1, group2],
            resolved_entries=[entry1, entry2],
            git_validate_fn=lambda p: True,
            git_head_fn=lambda p, b: commit_r1 if "repo1" in p else "xxx",
            git_diff_fn=lambda p, a, b, paths=None: [],
        )

        # repo1/Unit1.pas: Case A, mtime same → skipped → not modify
        assert "src/Unit1.pas" not in actions["modify"]
        # repo2/Unit2.pas: Case C (no stored commit) → full hash → h2 != h2_new → modify
        assert "lib/Unit2.pas" in actions["modify"]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: branch overlay caller (no manifest → always Case C)
# ─────────────────────────────────────────────────────────────────────────────


class TestDetermineActionsBranchOverlayCaller:
    """Simulates how run_branch_overlay_indexing calls determine_actions(old, new)
    without a manifest.  Must always do full hash scan."""

    def test_no_manifest_hash_scan(self):
        """No manifest supplied → pure hash comparison."""
        old = {"src/A.pas": _old_entry("h1", mtime=1000)}
        current = {"src/A.pas": _state("h2", mtime=1000)}
        actions = _determine_actions(
            old_files=old,
            current_states=current,
            # No manifest, no repo_groups
        )
        assert actions["modify"] == ["src/A.pas"]

    def test_none_manifest_hash_scan(self):
        """Explicit manifest=None → Case C for everything."""
        old = {"src/A.pas": _old_entry("h1", mtime=1000)}
        current = {"src/A.pas": _state("h2", mtime=1000)}
        actions = _determine_actions(
            old_files=old,
            current_states=current,
            manifest=None,
        )
        assert actions["modify"] == ["src/A.pas"]
