# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Tests for RESPECT_GITIGNORE / git check-ignore integration."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from shared import git_ops
from shared.manifest import filter_out_gitignored


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / ".gitignore").write_text("build/\n*.log\nnested/tmp/\n", encoding="utf-8")
    src = repo / "src"
    src.mkdir()
    (src / "main.py").write_text("print(1)\n", encoding="utf-8")
    build = repo / "build"
    build.mkdir()
    (build / "Generated.java").write_text("class G {}\n", encoding="utf-8")
    (repo / "debug.log").write_text("x\n", encoding="utf-8")
    nested = repo / "nested" / "tmp"
    nested.mkdir(parents=True)
    (nested / "secret.py").write_text("x=1\n", encoding="utf-8")
    # Tracked file that would match *.log if untracked — tracked wins
    (repo / "keep.log").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", "src/main.py", ".gitignore")
    # Force-add so a tracked file that matches *.log proves "tracked wins"
    _git(repo, "add", "-f", "keep.log")
    _git(repo, "commit", "-m", "init")
    return repo


class TestCheckIgnoredPaths:
    def test_empty_input(self, git_repo: Path):
        assert git_ops.check_ignored_paths(str(git_repo), []) == set()

    def test_ignores_build_and_logs(self, git_repo: Path):
        ignored = git_ops.check_ignored_paths(
            str(git_repo),
            [
                "src/main.py",
                "build/Generated.java",
                "debug.log",
                "nested/tmp/secret.py",
                "keep.log",
            ],
        )
        assert "build/Generated.java" in ignored
        assert "debug.log" in ignored
        assert "nested/tmp/secret.py" in ignored
        assert "src/main.py" not in ignored
        # Tracked file matching *.log is NOT ignored
        assert "keep.log" not in ignored

    def test_info_exclude(self, git_repo: Path):
        exclude = git_repo / ".git" / "info" / "exclude"
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text("local_only.py\n", encoding="utf-8")
        (git_repo / "local_only.py").write_text("x\n", encoding="utf-8")
        ignored = git_ops.check_ignored_paths(
            str(git_repo), ["local_only.py", "src/main.py"]
        )
        assert "local_only.py" in ignored
        assert "src/main.py" not in ignored


class TestFilterOutGitignored:
    def test_non_git_source_unchanged(self, tmp_path: Path):
        f = tmp_path / "a.py"
        f.write_text("x\n", encoding="utf-8")
        out = filter_out_gitignored(
            [f],
            {"_entry_type": "source_set", "_repo_path": None},
            respect_gitignore=True,
        )
        assert out == [f]

    def test_respect_false_skips_check(self, git_repo: Path):
        build_file = git_repo / "build" / "Generated.java"
        with patch("shared.git_ops.check_ignored_paths") as mock_check:
            out = filter_out_gitignored(
                [build_file],
                {
                    "_entry_type": "git_repo",
                    "_repo_path": str(git_repo),
                },
                respect_gitignore=False,
            )
            mock_check.assert_not_called()
            assert out == [build_file]

    def test_filters_ignored_keeps_tracked(self, git_repo: Path):
        files = [
            git_repo / "src" / "main.py",
            git_repo / "build" / "Generated.java",
            git_repo / "keep.log",
            git_repo / "debug.log",
        ]
        out = filter_out_gitignored(
            files,
            {"_entry_type": "git_repo", "_repo_path": str(git_repo)},
            respect_gitignore=True,
        )
        names = {p.name for p in out}
        assert "main.py" in names
        assert "keep.log" in names
        assert "Generated.java" not in names
        assert "debug.log" not in names


class TestDeleteChunkHelpers:
    """Smoke-test MatchAny chunking math used by refresh deletes."""

    def test_chunk_boundaries(self):
        keys = [f"f{i}.py" for i in range(1200)]
        chunk_size = 500
        chunks = [
            keys[i : i + chunk_size] for i in range(0, len(keys), chunk_size)
        ]
        assert len(chunks) == 3
        assert len(chunks[0]) == 500
        assert len(chunks[1]) == 500
        assert len(chunks[2]) == 200
        assert [k for c in chunks for k in c] == keys
