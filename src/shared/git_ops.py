# Copyright (c) 2025-2026 hybrid-code-rag-mcp contributors
# SPDX-License-Identifier: MIT

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from shared.log import log, log_error, log_warn


class GitError(Exception):
    """Raised when a git command fails."""

    pass


def _run_git(
    cmd: List[str],
    repo_path: str,
    timeout: int = 60,
    binary: bool = False,
) -> subprocess.CompletedProcess:
    """Run a git command and return the result.

    Args:
        cmd: Git command arguments (e.g. ["status", "--porcelain"]).
        repo_path: Path to the repository.
        timeout: Timeout in seconds.
        binary: If True, return stdout as bytes (for binary content).

    Returns:
        subprocess.CompletedProcess with stdout/stderr.

    Raises:
        GitError: If the git command fails.
    """
    full_cmd = ["git", "-C", repo_path] + cmd
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=not binary,
            timeout=timeout,
            check=True,
        )
        return result
    except subprocess.TimeoutExpired as exc:
        raise GitError(
            f"git command timed out after {timeout}s: {' '.join(full_cmd)}"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise GitError(
            f"git command failed (exit {exc.returncode}): {' '.join(full_cmd)}\n"
            f"stdout: {exc.stdout}\nstderr: {exc.stderr}"
        ) from exc


def sanitize_branch_name(branch: str) -> str:
    """Convert a branch name to a safe filesystem string.

    Args:
        branch: Branch name (e.g. "feature/my-branch").

    Returns:
        Sanitized string suitable for use in filenames (e.g. "feature_my_branch").
    """
    return branch.replace("/", "_").replace("\\", "_").replace(":", "_")


def get_current_branch(repo_path: str) -> str:
    """Get the current branch of the repository.

    Args:
        repo_path: Path to the git repository.

    Returns:
        Current branch name (e.g. "develop").

    Raises:
        GitError: If the current branch cannot be determined.
    """
    result = _run_git(["branch", "--show-current"], repo_path)
    return result.stdout.strip()


def checkout_file(repo_path: str, branch: str, file_path: str, dest_path: str) -> None:
    """Checkout a single file from a specific branch to a destination path.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name.
        file_path: Relative path to the file within the repository.
        dest_path: Absolute destination path.

    Raises:
        GitError: If the checkout fails.
    """
    _run_git(["checkout", branch, "--", file_path], repo_path)
    repo_file = Path(repo_path) / file_path
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    repo_file.rename(dest)


def get_file_hash(repo_path: str, branch: str, file_path: str) -> str:
    """Get the hash of a file at a specific branch.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name.
        file_path: Relative path to the file within the repository.

    Returns:
        SHA-256 hash of the file content.

    Raises:
        GitError: If the hash cannot be determined.
    """
    content = read_file_from_branch(repo_path, branch, file_path)
    import hashlib

    return hashlib.sha256(content).hexdigest()


def get_working_copy_hash(file_path: str) -> str:
    """Get the SHA-256 hash of a file on disk.

    Args:
        file_path: Absolute path to the file.

    Returns:
        SHA-256 hash of the file content.
    """
    import hashlib

    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def get_branch_head(repo_path: str, branch: str) -> str:
    """Get the commit hash at the HEAD of a branch.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name (e.g. "develop", "feature/T12549").
            Supports both local and remote-only branches (e.g. origin/task/T37523).

    Returns:
        Full commit hash (40 hex chars).

    Raises:
        GitError: If the branch doesn't exist.
    """
    return _resolve_branch(repo_path, branch)


def branch_exists(repo_path: str, branch: str) -> bool:
    """Check whether a branch exists in the repository."""
    try:
        _run_git(["rev-parse", "--verify", f"refs/heads/{branch}"], repo_path)
        return True
    except GitError:
        try:
            _run_git(
                ["rev-parse", "--verify", f"refs/remotes/origin/{branch}"], repo_path
            )
            return True
        except GitError:
            return False


def _resolve_branch(repo_path: str, branch: str) -> str:
    """Resolve a branch name to a commit hash.

    Tries local branch first, then refs/remotes/origin/<branch>.
    """
    try:
        return _run_git(["rev-parse", branch], repo_path).stdout.strip()
    except GitError:
        pass
    try:
        return _run_git(
            ["rev-parse", f"refs/remotes/origin/{branch}"], repo_path
        ).stdout.strip()
    except GitError:
        pass
    raise GitError(f"Cannot resolve branch '{branch}' to a commit")


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
    resolved_a = _resolve_branch(repo_path, branch_a)
    resolved_b = _resolve_branch(repo_path, branch_b)
    result = _run_git(["merge-base", resolved_a, resolved_b], repo_path)
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
        base_commit: Base commit (e.g. merge-base or parent).
        target_commit: Target commit (the feature branch HEAD).
        paths: Optional path prefixes to restrict the diff.

    Returns:
        List of (status, file_path) tuples.
    """
    cmd = ["diff", "--name-status", base_commit, target_commit]
    if paths:
        for p in paths:
            cmd.extend(["--", p])
    else:
        cmd.append("--")

    result = _run_git(cmd, repo_path)
    changes: List[Tuple[str, str]] = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        status, file_path = parts
        changes.append((status, file_path))
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
    resolved_feature = get_branch_head(repo_path, feature_branch)
    return diff_commits(repo_path, merge_base, resolved_feature, paths=paths)


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
    git_path = file_path.replace("\\", "/")
    resolved = _resolve_branch(repo_path, branch)
    result = _run_git(["show", f"{resolved}:{git_path}"], repo_path, binary=True)
    return result.stdout


def read_files_to_temp_dir(
    repo_path: str,
    branch: str,
    file_list: List[str],
    *,
    temp_dir: Optional[str] = None,
) -> str:
    """Read multiple files from a branch into a temporary directory.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name or commit hash.
        file_list: List of file paths relative to the repository root.
        temp_dir: Optional existing temp directory path. If None, a new one
            is created and returned.

    Returns:
        Path to the temporary directory containing the files.

    Raises:
        GitError: If any file cannot be read.
    """
    import tempfile

    if temp_dir:
        os_dir = Path(temp_dir)
    else:
        os_dir = Path(tempfile.mkdtemp(prefix="rag_branch_"))

    errors: List[str] = []
    for file_path in file_list:
        try:
            content = read_file_from_branch(repo_path, branch, file_path)
            dest = os_dir / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
        except GitError as exc:
            errors.append(str(exc))
            log_warn(f"Cannot read {branch}:{file_path}: {exc}")

    if errors:
        log_warn(
            f"Read {len(file_list) - len(errors)}/{len(file_list)} files from {branch} (errors: {len(errors)})"
        )
    else:
        log(f"Read {len(file_list)} files from {branch} to temp dir (0 errors)")

    return str(os_dir)


def delete_branch_vectors(
    repo_path: str,
    branch: str,
    qdrant_client: Any,
    collection_name: str,
    score_threshold: float = 0.5,
) -> int:
    """Delete all vectors for files that were modified on a branch.

    This removes the OLD (main branch) versions of files that were changed
    on the feature branch, so only the feature branch versions remain in the
    index.  It finds files by looking at file paths that appear in both
    the main and feature branch manifests, where the feature branch has a
    different hash for the same path.

    Args:
        repo_path: Path to the git repository.
        branch: Feature branch name.
        qdrant_client: Qdrant client instance.
        collection_name: Collection name.
        score_threshold: Minimum match score for file path search.

    Returns:
        Number of vectors deleted.

    Raises:
        GitError: If branch operations fail.
    """
    main_branch = _get_main_branch(repo_path)
    merge_base = get_merge_base(repo_path, main_branch, branch)

    main_files = _list_branch_files(repo_path, main_branch, merge_base)
    branch_files = _list_branch_files(repo_path, branch)

    common_paths = set(main_files.keys()) & set(branch_files.keys())
    changed_paths = [p for p in common_paths if main_files[p] != branch_files[p]]

    deleted = 0
    for path in changed_paths:
        deleted += _delete_vectors_by_path(
            qdrant_client, collection_name, path, main_branch
        )

    return deleted


def get_tombstones(
    repo_path: str,
    branch: str,
    main_branch: str,
    paths: Optional[List[str]] = None,
) -> List[str]:
    """Get list of files deleted on the feature branch (vs main).

    These are files that exist on main but were removed on the branch.
    Their vectors should be deleted from the branch overlay so they don't
    appear in branch-aware searches.

    Args:
        repo_path: Path to the git repository.
        branch: Feature branch name.
        main_branch: Main branch name.
        paths: Optional path prefixes to restrict the search.

    Returns:
        List of relative file paths that were deleted on the branch.
    """
    changes = diff_branches(repo_path, main_branch, branch, paths=paths)
    return [path for status, path in changes if status == "D"]


# ── Helpers ───────────────────────────────────────────────────────


def _get_main_branch(repo_path: str) -> str:
    """Get the main branch name for the repository.

    Returns "master" if no origin HEAD is found.
    """
    try:
        result = _run_git(
            ["symbolic-ref", "refs/remotes/origin/HEAD", "--short"], repo_path
        )
        return result.stdout.strip()
    except GitError:
        return "master"


def _list_branch_files(
    repo_path: str,
    branch: str,
    commit: Optional[str] = None,
) -> Dict[str, str]:
    """List all tracked files on a branch with their content hashes.

    Args:
        repo_path: Path to the git repository.
        branch: Branch name.
        commit: Optional specific commit hash. If None, uses branch HEAD.

    Returns:
        Dict mapping relative file paths to SHA-256 content hashes.
    """
    if commit is None:
        commit = get_branch_head(repo_path, branch)

    resolved = _resolve_branch(repo_path, branch)
    result = _run_git(["ls-tree", "-r", "--name-only", resolved], repo_path)
    files: Dict[str, str] = {}
    for file_path in result.stdout.strip().split("\n"):
        if not file_path:
            continue
        try:
            files[file_path] = get_file_hash(repo_path, resolved, file_path)
        except GitError:
            pass
    return files


def _delete_vectors_by_path(
    qdrant_client: Any,
    collection_name: str,
    file_path: str,
    branch: str,
) -> int:
    """Delete vectors for a specific file from the branch.

    Uses filter: file_path = X AND branch = Y.
    """
    try:
        result = qdrant_client.delete(
            collection_name=collection_name,
            points_selector={
                "filter": {
                    "must": [
                        {"key": "file_path", "match": {"value": file_path}},
                        {"key": "branch", "match": {"value": branch}},
                    ]
                }
            },
        )
        deleted = getattr(result, "operation_id", None)
        log(f"  Deleted vectors for {file_path} on {branch}")
        return deleted or 0
    except Exception as exc:
        log_warn(f"  Could not delete vectors for {file_path}: {exc}")
        return 0
