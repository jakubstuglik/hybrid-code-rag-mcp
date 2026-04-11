#!/usr/bin/env python3
"""Cron-safe wrapper that pulls all git_repos defined in a config.

Intended to be called from cron before (or alongside) refresh_guard.py.
Ensures the working directory is on the configured main branch so that
index_rag.py indexes the correct content.

Behaviour
---------
- For each ``git_repo`` entry in the config:
    1. ``git fetch --all --prune`` — update all remote refs
    2. For every configured branch (main + feature overlays):
       - If not checked out: ``git fetch origin <branch>:<branch>`` fast-forwards the local
         ref to match origin (works whether or not the branch existed locally before).
       - If checked out (current working branch): stash uncommitted changes, ``git pull``,
         restore stash.
- If on a detached HEAD: only fetch + non-checkout fast-forwards, skip pull.
- If the working branch is not in the configured list: fetch + fast-forward all others,
  skip pull for the working branch.
- A concurrency guard prevents concurrent git_pull_guard runs for the same
  config (same stale-process detection as refresh_guard.py).

State file
----------
A small JSON file ``<index_path>/git_pull_guard_state.json`` tracks the
consecutive skip count so the counter survives across cron invocations.

Usage
-----
    python src/git_pull_guard.py --config config_myproject

Example crontab (every hour, before refresh_guard)::

    0 * * * * cd /home/user/hybrid-code-rag-mcp && \\
        /home/user/hybrid-code-rag-mcp/.venv/bin/python src/git_pull_guard.py \\
        --config config_myproject >> /home/user/git_pull.log 2>&1
"""

import json
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import psutil

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
for _p in (_root, _here):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config_loader import get_config, get_repo_groups
from shared.git_ops import _run_git, GitError

MAX_SKIPS_BEFORE_KILL = 3


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [git_pull_guard] {msg}", flush=True)


def _find_guard_pid(config_name: str) -> Optional[int]:
    for proc in psutil.process_iter(["pid", "cmdline"]):
        try:
            cmdline: List[str] = proc.info.get("cmdline") or []
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        cmdline_str = " ".join(cmdline)
        if (
            "git_pull_guard.py" in cmdline_str
            and f"--config {config_name}" in cmdline_str
        ):
            return proc.pid
    return None


def _read_state(state_path: Path) -> dict:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"consecutive_skips": 0}


def _write_state(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _kill_process(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        _log(f"Process {pid} already gone before kill attempt.")
        return

    _log(f"Sending SIGTERM to PID {pid}...")
    try:
        proc.terminate()
    except psutil.NoSuchProcess:
        return

    gone, alive = psutil.wait_procs([proc], timeout=10)
    if alive:
        _log(f"Process {pid} did not exit after SIGTERM — sending SIGKILL.")
        for p in alive:
            try:
                p.kill()
            except psutil.NoSuchProcess:
                pass
        psutil.wait_procs(alive, timeout=5)

    _log(f"Process {pid} killed.")


def _resolve_state_path(config_name: str) -> Path:
    repo_root = Path(__file__).parent.parent
    candidate = repo_root / "project-configs" / config_name / "qdrant"
    if candidate.is_dir():
        return candidate / "git_pull_guard_state.json"

    candidate = repo_root / "self-index" / "qdrant"
    if candidate.is_dir() and config_name == "self-index":
        return candidate / "git_pull_guard_state.json"

    return Path(__file__).parent / f"git_pull_guard_state_{config_name}.json"


def _git_fast_forward_branch(repo_path: str, branch: str) -> Tuple[str, bool, str]:
    """Fast-forward a local branch ref to match origin without checking it out.

    Works for both new (creates the local branch) and existing (advances it) cases.
    Uses ``git fetch origin <branch>:<branch>`` which git refuses if the branch is
    currently checked out — callers must use ``_git_stash_and_pull`` instead for the
    working branch.
    """
    try:
        _run_git(["fetch", "origin", f"{branch}:{branch}"], repo_path, timeout=60)
        return (repo_path, True, "")
    except GitError as exc:
        return (repo_path, False, str(exc))


def _local_branch_exists(repo_path: str, branch: str) -> bool:
    try:
        _run_git(["rev-parse", "--verify", f"refs/heads/{branch}"], repo_path)
        return True
    except GitError:
        return False


def _git_fetch_all(repo_path: str) -> Tuple[str, bool, str]:
    try:
        _run_git(["fetch", "--all", "--prune"], repo_path, timeout=120)
        return (repo_path, True, "")
    except GitError as exc:
        return (repo_path, False, str(exc))


def _git_pull(repo_path: str, branch: str) -> Tuple[str, bool, str]:
    try:
        _run_git(["pull", "origin", branch], repo_path, timeout=120)
        return (repo_path, True, "")
    except GitError as exc:
        return (repo_path, False, str(exc))


def _git_stash_and_pull(repo_path: str, branch: str) -> Tuple[str, bool, str, bool]:
    stashed = False
    try:
        status_result = _run_git(["status", "--porcelain"], repo_path)
        has_changes = bool(status_result.stdout.strip())
        if has_changes:
            _run_git(["stash", "-q"], repo_path, timeout=30)
            stashed = True
            _log(f"  Stashed uncommitted changes in {repo_path}")
    except GitError as exc:
        return (repo_path, False, f"stash check failed: {exc}", False)

    pulled = False
    try:
        _run_git(["pull", "origin", branch], repo_path, timeout=120)
        pulled = True
    except GitError as exc:
        return (repo_path, False, str(exc), stashed)

    if stashed:
        try:
            _run_git(["stash", "pop", "-q"], repo_path, timeout=30)
            _log(f"  Restored stashed changes in {repo_path}")
        except GitError as exc:
            return (
                repo_path,
                False,
                f"pull succeeded but stash pop failed: {exc}",
                stashed,
            )

    return (repo_path, True, "", stashed)


def _get_current_branch(repo_path: str) -> Optional[str]:
    try:
        result = _run_git(["branch", "--show-current"], repo_path)
        branch = result.stdout.strip()
        return branch if branch else None
    except GitError:
        return None


def _pull_repo(repo_info: dict) -> dict:
    repo_path = repo_info["repo_path"]
    main_branch = repo_info["main_branch"]
    configured_branches = repo_info["branches"]

    _log(f"Processing repo: {repo_path}")
    results = {
        "repo_path": repo_path,
        "fetch_ok": False,
        "pull_ok": False,
        "errors": [],
    }

    fetch_ok, _, fetch_err = _git_fetch_all(repo_path)
    results["fetch_ok"] = fetch_ok
    if not fetch_ok:
        results["errors"].append(f"fetch: {fetch_err}")

    current_branch = _get_current_branch(repo_path)

    # Fast-forward every configured branch that is NOT currently checked out.
    # git fetch origin <branch>:<branch> both creates missing local branches and
    # advances existing ones — no checkout required.
    all_branches_to_sync = [main_branch] + configured_branches
    for branch in all_branches_to_sync:
        if branch == current_branch:
            # Checked-out branch must be updated via pull (handled below).
            continue
        existed = _local_branch_exists(repo_path, branch)
        ok, _, err = _git_fast_forward_branch(repo_path, branch)
        if ok:
            action = "updated" if existed else "created"
            _log(f"  Branch '{branch}': {action} to origin/{branch}.")
        else:
            _log(f"  Branch '{branch}': fast-forward failed — {err}")
            results["errors"].append(f"fast-forward {branch}: {err}")

    # Pull the working branch (stash uncommitted changes first if needed).
    if current_branch is None:
        _log(f"  {repo_path}: detached HEAD — skipping pull, fetch only.")
    elif current_branch not in all_branches_to_sync:
        _log(
            f"  {repo_path}: on branch '{current_branch}' (not main/feature) — skipping pull."
        )
    else:
        repo_ok, pull_ok, pull_err, stashed = _git_stash_and_pull(
            repo_path, current_branch
        )
        results["pull_ok"] = pull_ok
        if pull_err:
            results["errors"].append(f"pull: {pull_err}")
        if stashed:
            results["stash_restored"] = True

    return results


def _main() -> int:
    args = sys.argv[1:]

    try:
        config_idx = args.index("--config")
        config_name = args[config_idx + 1]
    except (ValueError, IndexError):
        print(
            "Usage: git_pull_guard.py --config <config_name>",
            file=sys.stderr,
        )
        return 2

    cfg = get_config(config_name=config_name)
    repo_groups = get_repo_groups(cfg)

    if not repo_groups:
        _log(f"No git_repo entries found in config '{config_name}'. Nothing to pull.")
        return 0

    state_path = _resolve_state_path(config_name)
    state = _read_state(state_path)

    running_pid = _find_guard_pid(config_name)

    if running_pid is None:
        _log(f"No active git_pull_guard found for config '{config_name}'. Starting.")
        state["consecutive_skips"] = 0
        _write_state(state_path, state)
    else:
        state["consecutive_skips"] = state.get("consecutive_skips", 0) + 1
        skip_count = state["consecutive_skips"]
        _write_state(state_path, state)

        if skip_count < MAX_SKIPS_BEFORE_KILL:
            _log(
                f"git_pull_guard PID {running_pid} still running for config "
                f"'{config_name}'. Skipping (consecutive: {skip_count}/{MAX_SKIPS_BEFORE_KILL - 1})."
            )
            return 0

        _log(
            f"Stale git_pull_guard PID {running_pid} ({skip_count} consecutive skips). Killing."
        )
        _kill_process(running_pid)
        time.sleep(2)
        state["consecutive_skips"] = 0
        _write_state(state_path, state)

    _log(f"Pulling {len(repo_groups)} git_repo(s) for config '{config_name}'...")

    all_ok = True
    with ThreadPoolExecutor(max_workers=min(len(repo_groups), 4)) as executor:
        futures = {executor.submit(_pull_repo, group): group for group in repo_groups}
        for future in as_completed(futures):
            result = future.result()
            rp = result["repo_path"]
            if result["fetch_ok"] and result["pull_ok"]:
                _log(f"  {rp}: fetch + pull OK")
            elif result["fetch_ok"]:
                _log(f"  {rp}: fetch OK, pull skipped or failed — {result['errors']}")
            else:
                _log(f"  {rp}: fetch FAILED — {result['errors']}")
                all_ok = False

    _log("Done." if all_ok else "Done with errors.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(_main())
