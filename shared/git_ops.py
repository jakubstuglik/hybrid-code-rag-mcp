"""Git subprocess wrappers for branch-aware indexing.

Thin, stateless functions that shell out to ``git`` for:
- Repository validation and branch info
- Commit hash lookups
- Diff between branches / commits
- Reading file content from arbitrary branches (without checkout)
- Writing branch files to a temp directory for reader consumption

All functions accept a ``repo_path`` which is the on-disk path to the
git repository root.  They raise ``GitError`` on failure so callers
get clear diagnostics.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from shared.log import log, log_warn


class GitError(Exception):
    """Raised when a git subprocess fails."""

    def __init__(self, message: str, returncode: int = 1, stderr: str = ""):
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(message)


# ── Helpers ──────────────────────────────────────────────────────


def _run_git(
    args: List[str],
    repo_path: str,
    *,
    capture_stdout: bool = True,
    binary: bool = False,
    timeout: int = 60,
) -> subprocess.CompletedProcess:
    """Run a git command in the given repo directory.

    Args:
        args: Git subcommand and arguments (e.g. ["rev-parse", "HEAD"]).
        repo_path: Path to the git repository root.
        capture_stdout: Whether to capture stdout.
        binary: If True, don't decode stdout (for raw file content).
        timeout: Timeout in seconds.

    Returns:
        CompletedProcess instance.

    Raises:
        GitError: If the command fails (non-zero exit code).
    """
    cmd = ["git", "-C", str(repo_path)] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=not binary,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitError(
            f"git command timed out after {timeout}s: {' '.join(cmd)}"
        ) from exc
    except FileNotFoundError as exc:
        raise GitError(
            "git executable not found. Ensure git is installed and in PATH."
        ) from exc

    if result.returncode != 0:
        stderr = (
            result.stderr
            if isinstance(result.stderr, str)
            else result.stderr.decode("utf-8", errors="replace")
        )
        raise GitError(
            f"git command failed (exit {result.returncode}): {' '.join(args)}\n{stderr.strip()}",
            returncode=result.returncode,
            stderr=stderr.strip(),
        )

    return result


# ── Repository info ──────────────────────────────────────────────


def validate_git_repo(repo_path: str) -> bool:
    """Check whether the given path is a valid git repository.

    Returns True if valid, False otherwise.
    """
    try:
        result = _run_git(["rev-parse", "--git-dir"], repo_path)
        return result.returncode == 0
    except GitError:
        return False


def get_current_branch(repo_path: str) -> str:
    """Get the currently checked-out branch name.

    Returns the branch name, or "HEAD" if in detached state.
    """
    result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
    return result.stdout.strip()


def get_branch_head(repo_path: str, branch: str) -> str:
    """Get the commit hash at the HEAD of a branch.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name (e.g. "develop", "feature/T12549").

    Returns:
        Full commit hash (40 hex chars).

    Raises:
        GitError: If the branch doesn't exist.
    """
    result = _run_git(["rev-parse", branch], repo_path)
    return result.stdout.strip()


def branch_exists(repo_path: str, branch: str) -> bool:
    """Check whether a branch exists in the repository."""
    try:
        _run_git(["rev-parse", "--verify", f"refs/heads/{branch}"], repo_path)
        return True
    except GitError:
        # Also check remote tracking branches
        try:
            _run_git(
                ["rev-parse", "--verify", f"refs/remotes/origin/{branch}"], repo_path
            )
            return True
        except GitError:
            return False


def get_merge_base(repo_path: str, branch_a: str, branch_b: str) -> str:
    """Find the best common ancestor (merge-base) of two branches.

    Args:
        repo_path: Path to the git repository.
        branch_a: First branch name.
        branch_b: Second branch name.

    Returns:
        Merge-base commit hash.

    Raises:
        GitError: If no merge-base found (unrelated histories).
    """
    result = _run_git(["merge-base", branch_a, branch_b], repo_path)
    return result.stdout.strip()


# ── Diff operations ──────────────────────────────────────────────


def diff_commits(
    repo_path: str,
    base_commit: str,
    target_commit: str,
    paths: Optional[List[str]] = None,
) -> List[Tuple[str, str]]:
    """Get the list of changed files between two commits.

    Args:
        repo_path: Path to the git repository.
        base_commit: Base commit hash (or branch name).
        target_commit: Target commit hash (or branch name).
        paths: Optional list of path prefixes to restrict the diff.

    Returns:
        List of (status, file_path) tuples.
        Status is one of: "A" (added), "M" (modified), "D" (deleted),
        "R" (renamed — reported as two entries: D old + A new).
    """
    args = ["diff", "--name-status", base_commit, target_commit]
    if paths:
        args.append("--")
        args.extend(paths)

    result = _run_git(args, repo_path)
    changes = []

    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue

        status = parts[0][0]  # First char: A, M, D, R, C, T
        file_path = parts[1]

        if status == "R" and len(parts) >= 3:
            # Rename: old_path -> new_path
            old_path = parts[1]
            new_path = parts[2]
            changes.append(("D", old_path))
            changes.append(("A", new_path))
        elif status in ("A", "M", "D", "T"):
            changes.append((status, file_path))
        elif status == "C":
            # Copy: treat as add of the new path
            if len(parts) >= 3:
                changes.append(("A", parts[2]))
            else:
                changes.append(("A", file_path))
        else:
            # Unknown status — treat as modified
            changes.append(("M", file_path))

    return changes


def diff_branches(
    repo_path: str,
    main_branch: str,
    feature_branch: str,
    paths: Optional[List[str]] = None,
) -> List[Tuple[str, str]]:
    """Get files changed on a feature branch relative to main.

    Uses the merge-base to find the diff (i.e., only changes made ON
    the feature branch, not changes on main since divergence).

    This is equivalent to: git diff --name-status $(git merge-base main feature)..feature

    Args:
        repo_path: Path to the git repository.
        main_branch: Main branch name (e.g. "develop").
        feature_branch: Feature branch name.
        paths: Optional path prefixes to restrict the diff.

    Returns:
        List of (status, file_path) tuples.
    """
    merge_base = get_merge_base(repo_path, main_branch, feature_branch)
    return diff_commits(repo_path, merge_base, feature_branch, paths=paths)


# ── File content from branches ───────────────────────────────────


def read_file_from_branch(repo_path: str, branch: str, file_path: str) -> bytes:
    """Read the content of a file from a specific branch without checkout.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name or commit hash.
        file_path: Path to the file relative to the repository root.

    Returns:
        Raw file content as bytes.

    Raises:
        GitError: If the file doesn't exist on the branch.
    """
    # Normalize path separators for git
    git_path = file_path.replace("\\", "/")
    result = _run_git(["show", f"{branch}:{git_path}"], repo_path, binary=True)
    return result.stdout


def read_files_to_temp_dir(
    repo_path: str,
    branch: str,
    file_list: List[str],
    *,
    base_temp_dir: Optional[str] = None,
) -> str:
    """Read multiple files from a branch and write them to a temp directory.

    Creates a temp directory mirroring the repository structure for the
    requested files.  This allows existing file-based readers to process
    branch content without any changes.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name or commit hash.
        file_list: List of file paths relative to the repo root.
        base_temp_dir: Optional parent directory for the temp dir.

    Returns:
        Path to the temp directory (caller is responsible for cleanup).

    Raises:
        GitError: If any file cannot be read (logged as warning, skipped).
    """
    temp_dir = tempfile.mkdtemp(
        prefix=f"rag_branch_{branch.replace('/', '_')}_",
        dir=base_temp_dir,
    )

    read_count = 0
    error_count = 0

    for file_path in file_list:
        try:
            content = read_file_from_branch(repo_path, branch, file_path)
            dest = Path(temp_dir) / file_path.replace("\\", "/")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            read_count += 1
        except GitError as exc:
            log_warn(f"Cannot read {branch}:{file_path}: {exc}")
            error_count += 1

    log(f"Read {read_count} files from {branch} to temp dir ({error_count} errors)")
    return temp_dir


# ── Blob hash (for change detection) ────────────────────────────


def get_blob_hash(repo_path: str, branch: str, file_path: str) -> Optional[str]:
    """Get the git blob hash for a file on a specific branch.

    This is useful for change detection — if the blob hash hasn't changed,
    the file content is identical (no need to re-embed).

    Args:
        repo_path: Path to the git repository.
        branch: Branch name or commit hash.
        file_path: Path relative to the repository root.

    Returns:
        Blob hash (40 hex chars) or None if the file doesn't exist on the branch.
    """
    git_path = file_path.replace("\\", "/")
    try:
        result = _run_git(["ls-tree", branch, "--", git_path], repo_path)
        line = result.stdout.strip()
        if not line:
            return None
        # Format: "<mode> <type> <hash>\t<filename>"
        parts = line.split()
        if len(parts) >= 3:
            return parts[2]
        return None
    except GitError:
        return None


def list_files_on_branch(
    repo_path: str,
    branch: str,
    paths: Optional[List[str]] = None,
) -> List[str]:
    """List all files on a branch, optionally restricted to certain paths.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name or commit hash.
        paths: Optional list of path prefixes to restrict listing.

    Returns:
        List of file paths relative to the repository root.
    """
    args = ["ls-tree", "-r", "--name-only", branch]
    if paths:
        args.append("--")
        args.extend(paths)

    result = _run_git(args, repo_path)
    files = [line for line in result.stdout.strip().splitlines() if line.strip()]
    return files


# ── Utility ──────────────────────────────────────────────────────


def sanitize_branch_name(branch: str) -> str:
    """Sanitize a branch name for use in file names.

    Replaces characters not safe for file names with underscores.

    Args:
        branch: Git branch name (e.g. "feature/T12549").

    Returns:
        Sanitized string safe for filenames (e.g. "feature_T12549").
    """
    # Replace common unsafe characters
    safe = branch
    for ch in '/\\:*?"<>| ':
        safe = safe.replace(ch, "_")
    return safe
