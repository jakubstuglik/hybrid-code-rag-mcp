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


# ── Edge cases: check_ignored_paths ─────────────────────────────────


def _completed(returncode: int, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(
        args=["git"], returncode=returncode, stdout=stdout, stderr=stderr
    )


class TestCheckIgnoredPathsEdgeCases:
    def test_non_git_directory_returns_empty(self, tmp_path: Path):
        plain = tmp_path / "plain"
        plain.mkdir()
        (plain / "a.py").write_text("x\n", encoding="utf-8")
        assert git_ops.check_ignored_paths(str(plain), ["a.py"]) == set()

    def test_missing_git_binary_returns_empty(self):
        with patch(
            "shared.git_ops.subprocess.run",
            side_effect=FileNotFoundError("git not found"),
        ):
            assert git_ops.check_ignored_paths("/any", ["a.py"]) == set()

    def test_timeout_returns_empty(self):
        with patch(
            "shared.git_ops.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1),
        ):
            assert git_ops.check_ignored_paths("/any", ["a.py"], timeout=1) == set()

    @pytest.mark.parametrize("stderr", ["fatal: boom", ""])
    def test_unexpected_exit_code_returns_empty(self, stderr: str):
        with patch(
            "shared.git_ops.subprocess.run",
            return_value=_completed(128, stdout="a.py\0", stderr=stderr),
        ):
            assert git_ops.check_ignored_paths("/any", ["a.py"]) == set()

    def test_exit_one_means_nothing_ignored(self):
        with patch("shared.git_ops.subprocess.run", return_value=_completed(1)):
            assert git_ops.check_ignored_paths("/any", ["a.py"]) == set()

    def test_only_blank_paths_skip_git(self):
        with patch("shared.git_ops.subprocess.run") as run:
            assert git_ops.check_ignored_paths("/any", ["", "./"]) == set()
            run.assert_not_called()

    def test_payload_is_normalised_and_deduplicated(self):
        with patch(
            "shared.git_ops.subprocess.run", return_value=_completed(1)
        ) as run:
            git_ops.check_ignored_paths(
                "/repo", ["src\\a.py", "./src/a.py", "src/a.py", "b.py"]
            )
        kwargs = run.call_args.kwargs
        assert kwargs["input"] == "src/a.py\0b.py\0"
        assert run.call_args.args[0] == [
            "git", "-C", "/repo", "check-ignore", "-z", "--stdin",
        ]
        assert kwargs["check"] is False

    def test_backslashes_in_output_are_normalised(self):
        with patch(
            "shared.git_ops.subprocess.run",
            return_value=_completed(0, stdout="build\\x.py\0\0"),
        ):
            assert git_ops.check_ignored_paths("/repo", ["build/x.py"]) == {"build/x.py"}

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Known bug: check_ignored_paths uses str.lstrip('./'), which strips the "
            "leading dot of dot-directories ('.venv/x' -> 'venv/x'), so ignored "
            "files under .venv/, .idea/ etc. are not filtered. Remove with the fix."
        ),
    )
    def test_filter_drops_ignored_files_in_dot_directory(self, git_repo: Path):
        (git_repo / ".gitignore").write_text(".venv/\n", encoding="utf-8")
        venv = git_repo / ".venv" / "lib"
        venv.mkdir(parents=True)
        site = venv / "site.py"
        site.write_text("x\n", encoding="utf-8")
        out = filter_out_gitignored(
            [git_repo / "src" / "main.py", site],
            {"_entry_type": "git_repo", "_repo_path": str(git_repo)},
        )
        assert out == [git_repo / "src" / "main.py"]


# ── Edge cases: filter_out_gitignored ───────────────────────────────


class TestFilterOutGitignoredEdgeCases:
    def test_empty_file_list(self, git_repo: Path):
        with patch("shared.git_ops.check_ignored_paths") as mock_check:
            out = filter_out_gitignored(
                [], {"_entry_type": "git_repo", "_repo_path": str(git_repo)}
            )
        assert out == []
        mock_check.assert_not_called()

    def test_git_repo_without_repo_path_unchanged(self, tmp_path: Path):
        f = tmp_path / "a.py"
        f.write_text("x\n", encoding="utf-8")
        with patch("shared.git_ops.check_ignored_paths") as mock_check:
            out = filter_out_gitignored([f], {"_entry_type": "git_repo"})
        assert out == [f]
        mock_check.assert_not_called()

    def test_nothing_ignored_returns_same_list(self, git_repo: Path):
        files = [git_repo / "src" / "main.py", git_repo / "keep.log"]
        out = filter_out_gitignored(
            files, {"_entry_type": "git_repo", "_repo_path": str(git_repo)}
        )
        assert out is files

    def test_file_outside_repo_is_kept(self, git_repo: Path, tmp_path: Path):
        outside = tmp_path / "outside.py"
        outside.write_text("x\n", encoding="utf-8")
        files = [outside, git_repo / "build" / "Generated.java", git_repo / "src" / "main.py"]
        out = filter_out_gitignored(
            files, {"_entry_type": "git_repo", "_repo_path": str(git_repo)}
        )
        assert out == [outside, git_repo / "src" / "main.py"]

    def test_order_is_preserved(self, git_repo: Path):
        files = [
            git_repo / "keep.log",
            git_repo / "debug.log",
            git_repo / "src" / "main.py",
        ]
        out = filter_out_gitignored(
            files, {"_entry_type": "git_repo", "_repo_path": str(git_repo)}
        )
        assert out == [git_repo / "keep.log", git_repo / "src" / "main.py"]

    def test_default_respects_gitignore(self, git_repo: Path):
        out = filter_out_gitignored(
            [git_repo / "build" / "Generated.java"],
            {"_entry_type": "git_repo", "_repo_path": str(git_repo)},
        )
        assert out == []

    def test_git_unavailable_keeps_everything(self, git_repo: Path):
        files = [git_repo / "build" / "Generated.java"]
        with patch("shared.git_ops.subprocess.run", side_effect=OSError("no git")):
            out = filter_out_gitignored(
                files, {"_entry_type": "git_repo", "_repo_path": str(git_repo)}
            )
        assert out == files


# ── Callers: get_source_files and load_all_sources ─────────────────


def _git_entry(repo: Path) -> dict:
    return {
        "path": str(repo),
        "extensions": [".py", ".java"],
        "exclude": [],
        "_entry_type": "git_repo",
        "_repo_path": str(repo),
    }


class TestGitignoreCallers:
    @pytest.mark.parametrize(
        "flag, expect_build",
        [(None, False), (True, False), (False, True)],
    )
    def test_get_source_files(self, git_repo: Path, flag, expect_build):
        import types

        import config_loader
        from shared import manifest as manifest_mod

        cfg = types.SimpleNamespace()
        if flag is not None:
            cfg.RESPECT_GITIGNORE = flag
        with patch.object(
            config_loader, "resolve_source_entries", return_value=[_git_entry(git_repo)]
        ):
            files = manifest_mod.get_source_files(cfg)
        names = {f.name for f in files}
        assert "main.py" in names
        assert ("Generated.java" in names) is expect_build
        assert ("secret.py" in names) is expect_build
        assert files == sorted(files)

    @pytest.mark.parametrize(
        "flag, expect_build",
        [(None, False), (True, False), (False, True)],
    )
    def test_load_all_sources(self, git_repo: Path, flag, expect_build):
        import types

        import config_loader
        from shared import indexing

        cfg = types.SimpleNamespace(SOURCE_DIRS=[])
        if flag is not None:
            cfg.RESPECT_GITIGNORE = flag
        seen: list[bool] = []
        real_filter = indexing.filter_out_gitignored

        def _spy(files, source_dir, *, respect_gitignore=True):
            seen.append(respect_gitignore)
            return real_filter(files, source_dir, respect_gitignore=respect_gitignore)

        with patch.object(
            config_loader, "resolve_source_entries", return_value=[_git_entry(git_repo)]
        ), patch.object(indexing, "filter_out_gitignored", _spy), patch.object(
            indexing,
            "normalize_file_key",
            side_effect=lambda base, rel, source_dir=None: rel,
        ):
            _, states = indexing.load_all_sources(cfg)
        assert seen == [flag is not False]
        assert ("build/Generated.java" in states) is expect_build
        assert "src/main.py" in states
