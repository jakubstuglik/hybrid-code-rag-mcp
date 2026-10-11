"""Throwaway git repos for overlay tests. No network and no extra tools."""

from __future__ import annotations

import subprocess
from pathlib import Path


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def git_out(repo: Path, *args: str) -> str:
    return git(repo, *args).stdout.strip()


def init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.email", "overlay-test@example.com")
    git(path, "config", "user.name", "Overlay Test")
    git(path, "config", "core.autocrlf", "false")
    git(path, "config", "commit.gpgsign", "false")
    git(path, "config", "diff.renames", "true")
    git(path, "config", "core.quotepath", "false")
    return path


def write_files(repo: Path, files: dict[str, str | bytes]) -> None:
    for rel, content in files.items():
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            dest.write_bytes(content.encode("utf-8"))
        else:
            dest.write_bytes(content)


def commit_files(repo: Path, files: dict[str, str | bytes], message: str) -> str:
    write_files(repo, files)
    git(repo, "add", "--", *files.keys())
    git(repo, "commit", "-m", message)
    return git_out(repo, "rev-parse", "HEAD")


def head(repo: Path) -> str:
    return git_out(repo, "rev-parse", "HEAD")


def worktree_count(repo: Path) -> int:
    lines = [line for line in git_out(repo, "worktree", "list").splitlines() if line.strip()]
    return len(lines)
