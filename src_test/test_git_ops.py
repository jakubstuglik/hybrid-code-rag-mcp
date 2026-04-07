"""
Tests for shared/git_ops.py — focusing on diff_commits rename/copy handling.

The bug: git diff --name-status emits renames as three tab-separated fields:
    R093\told_path\tnew_path
The original split("\t", 1) produced file_path = "old_path\tnew_path" (a
tab-joined string), which was then passed verbatim to git show, causing a
fatal error every run when the branch contained a rename.

Tests cover:
    - diff_commits: normal add/modify/delete lines
    - diff_commits: rename (R) lines split into D + A entries
    - diff_commits: copy (C) lines split into D + A entries (C keeps original)
    - diff_commits: empty output
    - diff_commits: lines with unexpected format are skipped
    - diff_commits: paths argument appended correctly
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import shared.git_ops as git_ops
from shared.git_ops import GitError, diff_commits


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_result(stdout: str) -> MagicMock:
    """Create a mock CompletedProcess with the given stdout."""
    result = MagicMock()
    result.stdout = stdout
    return result


def _run_diff_commits(stdout: str, base="abc123", target="def456", paths=None):
    """Run diff_commits with mocked _run_git returning the given stdout."""
    with patch.object(
        git_ops, "_run_git", return_value=_make_result(stdout)
    ) as mock_run:
        result = diff_commits("/repo", base, target, paths=paths)
    return result, mock_run


# ────────────────────────────────────────────────
# TestDiffCommitsNormal
# ────────────────────────────────────────────────


class TestDiffCommitsNormal:
    def test_add_line(self):
        result, _ = _run_diff_commits("A\tsrc/foo.pas")
        assert result == [("A", "src/foo.pas")]

    def test_modify_line(self):
        result, _ = _run_diff_commits("M\tsrc/foo.pas")
        assert result == [("M", "src/foo.pas")]

    def test_delete_line(self):
        result, _ = _run_diff_commits("D\tsrc/foo.pas")
        assert result == [("D", "src/foo.pas")]

    def test_multiple_lines(self):
        stdout = "A\tsrc/new.pas\nM\tsrc/mod.pas\nD\tsrc/del.pas"
        result, _ = _run_diff_commits(stdout)
        assert result == [
            ("A", "src/new.pas"),
            ("M", "src/mod.pas"),
            ("D", "src/del.pas"),
        ]

    def test_empty_output(self):
        result, _ = _run_diff_commits("")
        assert result == []

    def test_blank_lines_skipped(self):
        stdout = "A\tsrc/foo.pas\n\n\nM\tsrc/bar.pas"
        result, _ = _run_diff_commits(stdout)
        assert result == [("A", "src/foo.pas"), ("M", "src/bar.pas")]

    def test_lines_without_tab_skipped(self):
        stdout = "no-tab-here\nA\tsrc/valid.pas"
        result, _ = _run_diff_commits(stdout)
        assert result == [("A", "src/valid.pas")]

    def test_single_tab_field_skipped(self):
        # Only one part after split — status only, no path
        stdout = "M"
        result, _ = _run_diff_commits(stdout)
        assert result == []


# ────────────────────────────────────────────────
# TestDiffCommitsRename
# ────────────────────────────────────────────────


class TestDiffCommitsRename:
    def test_rename_emits_delete_and_add(self):
        """R line should produce D(old) + A(new), not a tab-joined garbage path."""
        stdout = "R093\tsrc/Common/OldName.pas\tsrc/Common/NewName.pas"
        result, _ = _run_diff_commits(stdout)
        assert result == [
            ("D", "src/Common/OldName.pas"),
            ("A", "src/Common/NewName.pas"),
        ]

    def test_rename_100_percent(self):
        stdout = "R100\tsrc/a.pas\tsrc/b.pas"
        result, _ = _run_diff_commits(stdout)
        assert result == [("D", "src/a.pas"), ("A", "src/b.pas")]

    def test_rename_mixed_with_other_lines(self):
        """The real-world case from the bug: rename plus normal modifications."""
        stdout = (
            "M\tdelphi_src/Common/GridWithSearchFrame.pas\n"
            "R093\tdelphi_src/Common/DISP_File/DISPFileInterfaces.pas"
            "\tdelphi_src/Common/Progress/UTaskProgressInterfaces.pas\n"
            "D\tdelphi_src/Common/OldFile.pas\n"
            "A\tdelphi_src/Common/NewFile.pas"
        )
        result, _ = _run_diff_commits(stdout)
        assert result == [
            ("M", "delphi_src/Common/GridWithSearchFrame.pas"),
            ("D", "delphi_src/Common/DISP_File/DISPFileInterfaces.pas"),
            ("A", "delphi_src/Common/Progress/UTaskProgressInterfaces.pas"),
            ("D", "delphi_src/Common/OldFile.pas"),
            ("A", "delphi_src/Common/NewFile.pas"),
        ]

    def test_no_tab_in_emitted_paths(self):
        """Ensure no emitted path contains a tab character (the original bug)."""
        stdout = "R050\tsrc/old.pas\tsrc/new.pas"
        result, _ = _run_diff_commits(stdout)
        for _status, path in result:
            assert "\t" not in path, f"Tab found in path: {repr(path)}"

    def test_rename_without_new_path_skipped(self):
        """A malformed R line with only two parts (no new path) should be skipped."""
        # Only status + old_path, no new_path — can't meaningfully handle it
        stdout = "R093\tsrc/old.pas"
        result, _ = _run_diff_commits(stdout)
        # With our fix: parts = ["R093", "src/old.pas"], len==2, not startswith R with len==3
        # Falls through to the else branch: status="R093", file_path="src/old.pas"
        assert result == [("R093", "src/old.pas")]


# ────────────────────────────────────────────────
# TestDiffCommitsCopy
# ────────────────────────────────────────────────


class TestDiffCommitsCopy:
    def test_copy_emits_delete_and_add(self):
        """C line (copy) also has old + new path; treat same as rename."""
        stdout = "C100\tsrc/template.pas\tsrc/new_copy.pas"
        result, _ = _run_diff_commits(stdout)
        assert result == [
            ("D", "src/template.pas"),
            ("A", "src/new_copy.pas"),
        ]


# ────────────────────────────────────────────────
# TestDiffCommitsCommandBuilding
# ────────────────────────────────────────────────


class TestDiffCommitsCommandBuilding:
    def test_no_paths_appends_double_dash(self):
        with patch.object(
            git_ops, "_run_git", return_value=_make_result("")
        ) as mock_run:
            diff_commits("/repo", "abc", "def", paths=None)
        cmd = mock_run.call_args[0][0]
        assert cmd == ["diff", "--name-status", "abc", "def", "--"]

    def test_with_paths_appends_each_path(self):
        with patch.object(
            git_ops, "_run_git", return_value=_make_result("")
        ) as mock_run:
            diff_commits("/repo", "abc", "def", paths=["src/", "lib/"])
        cmd = mock_run.call_args[0][0]
        assert cmd == [
            "diff",
            "--name-status",
            "abc",
            "def",
            "--",
            "src/",
            "--",
            "lib/",
        ]

    def test_repo_path_passed_through(self):
        with patch.object(
            git_ops, "_run_git", return_value=_make_result("")
        ) as mock_run:
            diff_commits("/my/repo", "abc", "def")
        assert mock_run.call_args[0][1] == "/my/repo"
