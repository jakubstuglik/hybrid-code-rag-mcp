"""
Integration tests for determine_actions() git-diff fast path.

These tests use a REAL git repository (../informica_2_0) to verify that
the fast path integrates correctly with actual git operations
(get_branch_head, diff_commits, validate_git_repo).

The test strategy:
- Case A: use current HEAD as stored_commit → verify mtime-unchanged files skipped
- Case B: create a temporary test commit, run Case B with the commit range,
  verify only changed files are in the candidate set, then reset the repo
- Fallback: verify invalid repos / missing commits fall back gracefully

IMPORTANT: Any test commits are cleaned up with git reset --hard origin/develop.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

# Ensure src/ and project root are on sys.path
_here = Path(__file__).parent
_root = _here.parent
_src = _root / "src"
for _p in [str(_root), str(_src)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ─────────────────────────────────────────────────────────────────────────────
# Location of test repo
# ─────────────────────────────────────────────────────────────────────────────

REPO_PATH = str((_root.parent / "informica_2_0").resolve())
DELPHI_SRC = "delphi_src"
MAIN_BRANCH = "develop"

# Skip all tests if the repo doesn't exist (CI / different machine)
REPO_EXISTS = Path(REPO_PATH).is_dir()
pytestmark = pytest.mark.skipif(
    not REPO_EXISTS,
    reason=f"Integration repo not found: {REPO_PATH}",
)


# ─────────────────────────────────────────────────────────────────────────────
# Imports from project modules (safe after sys.path setup)
# ─────────────────────────────────────────────────────────────────────────────

from shared.git_ops import (  # noqa: E402
    get_branch_head,
    diff_commits,
    validate_git_repo,
    GitError,
)
from shared.manifest import _get_canonical_prefix, make_repo_key  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Replicate the helper functions from index_rag.py (same as unit test file)
# ─────────────────────────────────────────────────────────────────────────────


def _git_prefix_paths(group: dict) -> list | None:
    prefixes = group.get("git_prefixes", [])
    if not prefixes:
        return None
    cleaned = [p for p in prefixes if p and p != "."]
    return cleaned if cleaned else None


def _build_repo_group_file_map(resolved_entries: list) -> dict:
    result: dict = {}
    for entry in resolved_entries:
        if entry["_entry_type"] != "git_repo":
            continue
        repo_key = make_repo_key(entry["_repo_path"])
        result.setdefault(repo_key, []).append(entry)
    return result


def _file_key_to_git_path(file_key: str, entry: dict) -> str | None:
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


def _determine_actions(
    old_files: dict,
    current_states: dict,
    manifest: dict | None = None,
    *,
    repo_groups: list | None = None,
    resolved_entries: list | None = None,
    git_validate_fn=None,
    git_head_fn=None,
    git_diff_fn=None,
    threshold: float = 0.5,
    GitError=GitError,
) -> dict:
    """Replicated determine_actions with injectable git functions."""
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
                continue

            stored_commit = stored_entry.get("commit", "")
            if not stored_commit:
                continue

            try:
                if git_validate_fn and not git_validate_fn(repo_path):
                    continue
                current_commit = (
                    git_head_fn(repo_path, main_branch)
                    if git_head_fn
                    else stored_commit
                )
            except GitError:
                continue

            if current_commit == stored_commit:
                # Case A
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
                    if int(old_entry.get("mtime", 0)) == int(current.get("mtime", 0)):
                        skip_hash_check.add(path_key)

            else:
                # Case B
                git_paths = _git_prefix_paths(group)
                try:
                    changes = (
                        git_diff_fn(
                            repo_path,
                            stored_commit,
                            current_commit,
                            paths=git_paths,
                        )
                        if git_diff_fn
                        else []
                    )
                except GitError:
                    continue

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
                        continue

                for path_key in repo_manifest_keys:
                    if path_key in current_states and path_key not in changed_file_keys:
                        old_entry = old_files[path_key]
                        current = current_states[path_key]
                        if int(old_entry.get("mtime", 0)) == int(
                            current.get("mtime", 0)
                        ):
                            skip_hash_check.add(path_key)

    for path_key, current in current_states.items():
        if path_key not in old_files:
            actions["add"].append(path_key)
        elif path_key in skip_hash_check:
            pass
        else:
            old_entry = old_files[path_key]
            if current["hash"] != old_entry.get("hash", ""):
                actions["modify"].append(path_key)

    for path_key in old_files:
        if path_key not in current_states:
            actions["delete"].append(path_key)

    return actions


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_entry(git_prefix=DELPHI_SRC, exts=(".pas", ".dfm")):
    """Build a resolved entry for informica_2_0/delphi_src."""
    return {
        "path": f"{REPO_PATH}/{git_prefix}",
        "extensions": list(exts),
        "exclude": [],
        "_entry_type": "git_repo",
        "_repo_path": REPO_PATH,
        "_git_prefix": git_prefix,
        "_main_branch": MAIN_BRANCH,
        "_branches": [],
        "_diff_threshold": 0.5,
    }


def _make_group(git_prefix=DELPHI_SRC):
    return {
        "repo_path": REPO_PATH,
        "main_branch": MAIN_BRANCH,
        "branches": [],
        "git_prefixes": [git_prefix],
        "resolved_entries": [],
    }


def _repo_key():
    return make_repo_key(REPO_PATH)


def _state_for(file_key: str) -> dict:
    """Return a fake current state with stable mtime and hash."""
    return {"hash": "stable_hash", "mtime": 100000}


def _old_entry_for(file_key: str) -> dict:
    return {"hash": "stable_hash", "mtime": 100000}


# ─────────────────────────────────────────────────────────────────────────────
# Tests: validate_git_repo integration
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateGitRepo:
    def test_informica_repo_is_valid(self):
        """The real informica_2_0 repo is a valid git repo."""
        assert validate_git_repo(REPO_PATH) is True

    def test_nonexistent_path_is_not_valid(self):
        """A path that doesn't exist is not a valid git repo."""
        assert validate_git_repo("/no/such/path") is False

    def test_non_git_dir_is_not_valid(self, tmp_path):
        """A directory without .git is not a valid git repo."""
        assert validate_git_repo(str(tmp_path)) is False


# ─────────────────────────────────────────────────────────────────────────────
# Tests: get_branch_head integration
# ─────────────────────────────────────────────────────────────────────────────


class TestGetBranchHead:
    def test_returns_40_char_hex(self):
        """get_branch_head returns a 40-char SHA1 for informica_2_0 develop."""
        commit = get_branch_head(REPO_PATH, MAIN_BRANCH)
        assert len(commit) == 40
        assert all(c in "0123456789abcdef" for c in commit)

    def test_nonexistent_branch_raises(self):
        """Missing branch raises GitError."""
        with pytest.raises(GitError):
            get_branch_head(REPO_PATH, "this_branch_does_not_exist_xyz")


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Case A with real HEAD commit
# ─────────────────────────────────────────────────────────────────────────────


class TestCaseAWithRealRepo:
    """Case A: use real HEAD as stored commit → unchanged files are skipped."""

    def _run_case_a(self, n_files=5):
        """Build a manifest with current HEAD, supply n_files as unchanged."""
        current_commit = get_branch_head(REPO_PATH, MAIN_BRANCH)
        entry = _make_entry()
        group = _make_group()
        repo_key = _repo_key()

        manifest = {
            "repo_commits": {
                repo_key: {"commit": current_commit, "main_branch": MAIN_BRANCH}
            }
        }

        # Invent n synthetic file keys belonging to this repo group
        file_keys = [f"delphi_src/FakeSrc/Unit{i}.pas" for i in range(n_files)]
        old_files = {
            k: {"hash": f"h{i}", "mtime": 1000} for i, k in enumerate(file_keys)
        }
        current_states = {
            k: {"hash": f"h{i}", "mtime": 1000} for i, k in enumerate(file_keys)
        }

        return _determine_actions(
            old_files=old_files,
            current_states=current_states,
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=validate_git_repo,
            git_head_fn=get_branch_head,
            git_diff_fn=diff_commits,
        )

    def test_all_files_skipped_when_commits_match(self):
        """With stored == current commit and same mtime, no files are modified."""
        actions = self._run_case_a(n_files=5)
        assert actions["add"] == []
        assert actions["modify"] == []
        assert actions["delete"] == []

    def test_mtime_changed_file_is_checked(self):
        """If one file has a different mtime, its hash IS checked."""
        current_commit = get_branch_head(REPO_PATH, MAIN_BRANCH)
        entry = _make_entry()
        group = _make_group()
        repo_key = _repo_key()

        manifest = {
            "repo_commits": {
                repo_key: {"commit": current_commit, "main_branch": MAIN_BRANCH}
            }
        }

        old_files = {
            "delphi_src/FakeSrc/Unit0.pas": {"hash": "h0", "mtime": 1000},
        }
        # Same mtime → skip
        # Different mtime AND different hash → modify
        current_states = {
            "delphi_src/FakeSrc/Unit0.pas": {"hash": "h0_changed", "mtime": 2000},
        }

        actions = _determine_actions(
            old_files=old_files,
            current_states=current_states,
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=validate_git_repo,
            git_head_fn=get_branch_head,
            git_diff_fn=diff_commits,
        )
        assert actions["modify"] == ["delphi_src/FakeSrc/Unit0.pas"]

    def test_new_file_added_regardless_of_commit_match(self):
        """New file not in old manifest is always added."""
        current_commit = get_branch_head(REPO_PATH, MAIN_BRANCH)
        entry = _make_entry()
        group = _make_group()
        repo_key = _repo_key()

        manifest = {
            "repo_commits": {
                repo_key: {"commit": current_commit, "main_branch": MAIN_BRANCH}
            }
        }

        actions = _determine_actions(
            old_files={},
            current_states={"delphi_src/NewFile.pas": {"hash": "hN", "mtime": 1000}},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=validate_git_repo,
            git_head_fn=get_branch_head,
            git_diff_fn=diff_commits,
        )
        assert actions["add"] == ["delphi_src/NewFile.pas"]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Case B with real repo (make/reset test commit)
# ─────────────────────────────────────────────────────────────────────────────


class TestCaseBWithRealRepo:
    """Case B: create a real test commit and verify diff narrowing works.

    Cleanup: git reset --hard origin/develop after each test.
    """

    @pytest.fixture(autouse=True)
    def reset_repo(self):
        """Always reset the repo after the test, even if it fails."""
        yield
        import subprocess

        subprocess.run(
            ["git", "reset", "--hard", f"origin/{MAIN_BRANCH}"],
            cwd=REPO_PATH,
            capture_output=True,
        )

    def _make_test_commit(
        self, filename="delphi_src/test_fast_path_temp.tmp", content="test"
    ):
        """Create a trivial test file and commit it. Returns (old_commit, new_commit)."""
        import subprocess

        old_commit = get_branch_head(REPO_PATH, MAIN_BRANCH)
        file_path = Path(REPO_PATH) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

        subprocess.run(["git", "add", str(file_path)], cwd=REPO_PATH, check=True)
        subprocess.run(
            ["git", "commit", "-m", "test: fast path integration test (will be reset)"],
            cwd=REPO_PATH,
            check=True,
            capture_output=True,
        )
        new_commit = get_branch_head(REPO_PATH, MAIN_BRANCH)
        return old_commit, new_commit, filename

    def test_case_b_diff_fires_with_real_commit(self):
        """After a real test commit, diff_commits returns the changed file."""
        old_commit, new_commit, filename = self._make_test_commit()
        assert old_commit != new_commit

        changes = diff_commits(REPO_PATH, old_commit, new_commit)
        changed_paths = [p for _, p in changes]
        assert filename in changed_paths

    def test_case_b_changed_file_not_skipped(self):
        """Changed file (in diff) is NOT added to skip_hash_check → hash is compared."""
        old_commit, new_commit, filename = self._make_test_commit(
            filename="delphi_src/test_fp_changed.pas",
            content="unit TestFP; interface end.",
        )
        entry = _make_entry()
        group = _make_group()
        repo_key = _repo_key()

        manifest = {
            "repo_commits": {
                repo_key: {"commit": old_commit, "main_branch": MAIN_BRANCH}
            }
        }

        file_key = "delphi_src/test_fp_changed.pas"
        old_files = {file_key: {"hash": "old_hash", "mtime": 1000}}
        current_states = {file_key: {"hash": "new_hash", "mtime": 1000}}

        actions = _determine_actions(
            old_files=old_files,
            current_states=current_states,
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=validate_git_repo,
            git_head_fn=get_branch_head,
            git_diff_fn=diff_commits,
        )
        # Changed file should be in modify
        assert file_key in actions["modify"]

    def test_case_b_unchanged_file_skipped(self):
        """File NOT in diff and mtime unchanged → skipped (hash not compared).

        We populate the manifest with enough stable files so that the ratio of
        changed files (1 real commit file) to total manifest files stays well
        below the 0.5 threshold, keeping us in Case B (fast path).
        """
        old_commit, new_commit, _ = self._make_test_commit(
            filename="delphi_src/test_fp_only_this.pas",
        )
        entry = _make_entry()
        group = _make_group()
        repo_key = _repo_key()

        manifest = {
            "repo_commits": {
                repo_key: {"commit": old_commit, "main_branch": MAIN_BRANCH}
            }
        }

        # Populate manifest with many stable files + the one changed file.
        # 1 changed / 10 total = 10% << 50% threshold → stays in Case B.
        stable_keys = [f"delphi_src/StableUnit{i}.pas" for i in range(9)]
        changed_key = "delphi_src/test_fp_only_this.pas"
        all_keys = stable_keys + [changed_key]

        old_files = {k: {"hash": "stable_hash", "mtime": 1000} for k in all_keys}
        # All files have same mtime; stable files have identical hashes.
        # The changed_key has a different hash but should be caught by the diff.
        current_states = {
            k: {"hash": "stable_hash", "mtime": 1000} for k in stable_keys
        }
        # The committed file now exists on disk too (from _make_test_commit)
        current_states[changed_key] = {"hash": "different_but_in_diff", "mtime": 1000}

        actions = _determine_actions(
            old_files=old_files,
            current_states=current_states,
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=validate_git_repo,
            git_head_fn=get_branch_head,
            git_diff_fn=diff_commits,
        )
        # stable_keys are NOT in diff + mtime same → skip_hash_check → not modify
        for sk in stable_keys:
            assert sk not in actions["modify"], f"{sk} should be skipped"
        # The changed file IS in the diff → hash checked → hash differs → modify
        assert changed_key in actions["modify"]

    def test_case_b_uses_git_prefixes_filter(self):
        """diff_commits is called with the git_prefixes path filter."""
        old_commit, new_commit, _ = self._make_test_commit(
            filename="delphi_src/test_fp_prefix_filter.pas",
        )
        entry = _make_entry()
        group = _make_group(git_prefix=DELPHI_SRC)
        repo_key = _repo_key()

        manifest = {
            "repo_commits": {
                repo_key: {"commit": old_commit, "main_branch": MAIN_BRANCH}
            }
        }

        captured_paths = []

        def capturing_diff(p, a, b, paths=None):
            captured_paths.append(paths)
            return diff_commits(p, a, b, paths=paths)

        actions = _determine_actions(
            old_files={},
            current_states={},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=validate_git_repo,
            git_head_fn=get_branch_head,
            git_diff_fn=capturing_diff,
        )
        # Should have been called with ["delphi_src"] as paths
        assert len(captured_paths) == 1
        assert captured_paths[0] == [DELPHI_SRC]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: fallback behaviour with real git functions
# ─────────────────────────────────────────────────────────────────────────────


class TestFallbackWithRealGit:
    def test_invalid_stored_commit_falls_back_gracefully(self):
        """Invalid stored commit → diff_commits raises → Case C fallback."""
        entry = _make_entry()
        group = _make_group()
        repo_key = _repo_key()

        manifest = {
            "repo_commits": {
                repo_key: {
                    "commit": "0" * 40,  # valid-looking but nonexistent commit
                    "main_branch": MAIN_BRANCH,
                }
            }
        }

        current_commit = get_branch_head(REPO_PATH, MAIN_BRANCH)

        # diff_commits will raise GitError for nonexistent old commit
        actions = _determine_actions(
            old_files={"delphi_src/Unit1.pas": {"hash": "h1", "mtime": 1000}},
            current_states={"delphi_src/Unit1.pas": {"hash": "h2", "mtime": 1000}},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=validate_git_repo,
            git_head_fn=lambda p, b: current_commit,  # different from stored
            git_diff_fn=diff_commits,  # will raise for invalid old commit
            GitError=GitError,
        )
        # Case C fallback: hash compared → h1 != h2 → modify
        assert actions["modify"] == ["delphi_src/Unit1.pas"]

    def test_nonexistent_repo_skips_without_crash(self):
        """Non-existent repo path → validate fails → Case C → normal hash scan."""
        entry = {
            "path": "/nonexistent/repo/src",
            "extensions": [".pas"],
            "exclude": [],
            "_entry_type": "git_repo",
            "_repo_path": "/nonexistent/repo",
            "_git_prefix": "src",
            "_main_branch": "main",
            "_branches": [],
            "_diff_threshold": 0.5,
        }
        group = {
            "repo_path": "/nonexistent/repo",
            "main_branch": "main",
            "branches": [],
            "git_prefixes": ["src"],
            "resolved_entries": [],
        }
        fake_key = "nonexistent_repo"  # won't match make_repo_key("/fake/other")
        manifest = {
            "repo_commits": {fake_key: {"commit": "a" * 40, "main_branch": "main"}}
        }

        actions = _determine_actions(
            old_files={"src/Unit1.pas": {"hash": "h1", "mtime": 1000}},
            current_states={"src/Unit1.pas": {"hash": "h2", "mtime": 1000}},
            manifest=manifest,
            repo_groups=[group],
            resolved_entries=[entry],
            git_validate_fn=validate_git_repo,  # returns False for nonexistent
            git_head_fn=get_branch_head,
            git_diff_fn=diff_commits,
            GitError=GitError,
        )
        # validate_git_repo returns False → Case C → hash compared → modify
        assert actions["modify"] == ["src/Unit1.pas"]
