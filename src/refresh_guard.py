#!/usr/bin/env python3
"""Cron-safe wrapper for index_rag.py refresh runs.

Prevents concurrent indexing runs from stacking up. Intended to be called
from cron instead of index_rag.py directly.

Behaviour
---------
- If no prior indexing run is active: run normally, reset skip counter.
- If a run is active and this is the 1st or 2nd consecutive skipped invocation:
  log a warning and exit without starting a new run.
- If a run is active and this is the 3rd consecutive skipped invocation:
  kill the stale run (with its child processes) and start a new one.
- The skip counter belongs to one process (pid + start time): a run that was
  not seen before starts at 1, so a fresh run is never killed early.
- The scan never matches this guard or its ancestors (the cron shell).
- A lock file next to the state file (``refresh_guard_state.json.lock``) is
  held from the scan until the new indexer has started, so two overlapping
  guard invocations cannot both start one.
- While a ``git_pull_guard.py`` run for the same config is alive (for
  example an earlier tick's pull whose fetch outlasts the cron period), no
  indexer is started: the pull could change the working tree under it. The
  same 3-strike rule applies: on the 3rd consecutive sighting of the same
  pull guard its process tree is killed and the guard goes on as usual. These
  sightings have their own counter (``pull_guard`` in the state file).

State file
----------
A small JSON file ``<index_path>/refresh_guard_state.json`` tracks the
consecutive skip count so the counter survives across cron invocations.

Usage
-----
    python src/refresh_guard.py --config config_myproject [--yes]

All extra flags (``--yes``, ``--log-to-file``, etc.) are forwarded verbatim
to ``index_rag.py``.

Example crontab (every hour)::

    0 * * * * cd /home/user/hybrid-code-rag-mcp && \\
        /home/user/hybrid-code-rag-mcp/.venv/bin/python src/refresh_guard.py \\
        --config config_myproject --yes >> /home/user/index_refresh.log 2>&1
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from guard_common import (  # noqa: E402
    GuardLock,
    find_process,
    kill_process_tree,
    process_start_time,
    read_state,
    register_sighting,
    reset_sightings,
    write_state,
)

# ── Constants ────────────────────────────────────────────────────────────────

MAX_SKIPS_BEFORE_KILL = 3  # kill the stale process on the Nth consecutive skip
LOCK_TIMEOUT_S = 120  # wait this long for another guard's decision to finish
PULL_GUARD_STATE_KEY = "pull_guard"  # sightings of a running git_pull_guard

# ── Helpers ──────────────────────────────────────────────────────────────────


def _log(msg: str) -> None:
    """Print a timestamped log line (no dependency on shared.log)."""
    from datetime import datetime

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [refresh_guard] {msg}", flush=True)


def _find_pull_guard_pid(config_name: str) -> Optional[int]:
    """Return the PID of a running git_pull_guard.py for *config_name*, or None."""
    return find_process("git_pull_guard.py", config_name)


def _find_indexer_pid(config_name: str) -> Optional[int]:
    """Return the PID of a running index_rag.py process for *config_name*, or None.

    Matches any process whose command line contains both ``index_rag.py`` and
    ``--config <config_name>``, except this process and its ancestors.
    """
    return find_process("index_rag.py", config_name)


def _read_state(state_path: Path) -> dict:
    """Load guard state from JSON, returning defaults if missing or corrupt."""
    return read_state(state_path)


def _write_state(state_path: Path, state: dict) -> None:
    """Persist guard state to JSON."""
    write_state(state_path, state)


def _kill_process(pid: int) -> None:
    """Terminate a process and its children (SIGTERM, then SIGKILL after 10 s)."""
    kill_process_tree(pid, _log)


def _start_indexer(indexer_args: List[str]) -> subprocess.Popen:
    """Start index_rag.py with *indexer_args* and return the process."""
    script = Path(__file__).parent / "index_rag.py"
    cmd = [sys.executable, str(script)] + indexer_args
    _log(f"Starting indexer: {' '.join(cmd)}")
    return subprocess.Popen(cmd)


def _run_indexer(indexer_args: List[str]) -> int:
    """Run index_rag.py with *indexer_args* and return its exit code."""
    return _start_indexer(indexer_args).wait()


def _resolve_state_path(config_name: str) -> Path:
    """Derive the state file path from the config directory.

    Tries to locate the project-configs or self-index directory for the given
    config name, falling back to a path next to this script.
    """
    repo_root = Path(__file__).parent.parent

    # project-configs/<name>/qdrant/
    candidate = repo_root / "project-configs" / config_name / "qdrant"
    if candidate.is_dir():
        return candidate / "refresh_guard_state.json"

    # self-index/qdrant/
    candidate = repo_root / "self-index" / "qdrant"
    if candidate.is_dir() and config_name == "self-index":
        return candidate / "refresh_guard_state.json"

    # Fallback: next to this script
    return Path(__file__).parent / f"refresh_guard_state_{config_name}.json"


# ── Main ─────────────────────────────────────────────────────────────────────


def _pull_guard_cleared(config_name: str, state: dict) -> bool:
    """Return True when no git_pull_guard for *config_name* is (still) running.

    A running pull guard is skipped twice; on the 3rd consecutive sighting of
    the same process its tree is killed. Updates the ``pull_guard`` sightings
    in *state* in place (the caller writes the state).
    """
    pull_pid = _find_pull_guard_pid(config_name)
    if pull_pid is None:
        state.pop(PULL_GUARD_STATE_KEY, None)
        return True

    sightings = state.get(PULL_GUARD_STATE_KEY)
    if not isinstance(sightings, dict):
        sightings = {}
    state[PULL_GUARD_STATE_KEY] = sightings
    count = register_sighting(sightings, pull_pid, process_start_time(pull_pid))
    if count < MAX_SKIPS_BEFORE_KILL:
        _log(
            f"git_pull_guard PID {pull_pid} is running for config '{config_name}'. "
            f"Not starting the indexer under a pull "
            f"(consecutive skips: {count}/{MAX_SKIPS_BEFORE_KILL - 1})."
        )
        return False

    _log(
        f"git_pull_guard PID {pull_pid} has been running for {count} consecutive "
        f"cron periods for config '{config_name}'. Killing it."
    )
    _kill_process(pull_pid)
    time.sleep(2)
    state.pop(PULL_GUARD_STATE_KEY, None)
    still_running = _find_pull_guard_pid(config_name)
    if still_running is not None:
        _log(
            f"git_pull_guard PID {still_running} for config '{config_name}' is "
            f"still running after the kill. Not starting the indexer."
        )
        return False
    return True


def _decide(config_name: str, state_path: Path, args: List[str]):
    """Scan, update the skip counter and maybe kill; return a started process or None.

    Runs while the guard lock is held, so no other guard can scan or start
    between this guard's scan and its start.
    """
    state = _read_state(state_path)
    if not _pull_guard_cleared(config_name, state):
        _write_state(state_path, state)
        return None
    running_pid = _find_indexer_pid(config_name)

    if running_pid is None:
        # ── No active run — start fresh ───────────────────────────────────
        _log(f"No active indexer found for config '{config_name}'. Starting fresh run.")
        reset_sightings(state)
        _write_state(state_path, state)
        return _start_indexer(args)

    # ── An active run exists ──────────────────────────────────────────────
    # The counter is tied to this pid (and its start time): a run that was
    # not seen before starts again at 1.
    skip_count = register_sighting(state, running_pid, process_start_time(running_pid))
    _write_state(state_path, state)

    if skip_count < MAX_SKIPS_BEFORE_KILL:
        _log(
            f"Indexer PID {running_pid} still running for config '{config_name}'. "
            f"Skipping this run (consecutive skips: {skip_count}/{MAX_SKIPS_BEFORE_KILL - 1})."
        )
        return None

    # Third consecutive skip — kill and restart.
    _log(
        f"Indexer PID {running_pid} has been running for {skip_count} consecutive "
        f"cron periods for config '{config_name}'. Killing stale process and restarting."
    )
    _kill_process(running_pid)

    # Brief pause to let Qdrant/TEI connections close cleanly.
    time.sleep(2)

    reset_sightings(state)
    _write_state(state_path, state)
    still_running = _find_indexer_pid(config_name)
    if still_running is not None:
        _log(
            f"Indexer PID {still_running} for config '{config_name}' is still "
            f"running after the kill. Not starting a second run."
        )
        return None
    return _start_indexer(args)


def main() -> int:
    args = sys.argv[1:]

    # Extract --config value (required).
    try:
        config_idx = args.index("--config")
        config_name = args[config_idx + 1]
    except (ValueError, IndexError):
        print(
            "Usage: refresh_guard.py --config <config_name> [extra index_rag.py args...]",
            file=sys.stderr,
        )
        return 2

    state_path = _resolve_state_path(config_name)
    lock = GuardLock(state_path.with_name(state_path.name + ".lock"))
    if not lock.acquire(timeout_s=LOCK_TIMEOUT_S):
        _log(
            f"Another refresh_guard for config '{config_name}' is still deciding "
            f"after {LOCK_TIMEOUT_S}s. Skipping this run."
        )
        return 0
    try:
        proc = _decide(config_name, state_path, args)
    finally:
        # The started indexer is visible to the next scan from here on.
        lock.release()
    if proc is None:
        return 0
    return proc.wait()


if __name__ == "__main__":
    sys.exit(main())
