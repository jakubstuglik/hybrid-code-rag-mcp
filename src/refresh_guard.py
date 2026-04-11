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
  kill the stale run and start a new one.

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

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

import psutil

# ── Constants ────────────────────────────────────────────────────────────────

MAX_SKIPS_BEFORE_KILL = 3  # kill the stale process on the Nth consecutive skip

# ── Helpers ──────────────────────────────────────────────────────────────────


def _log(msg: str) -> None:
    """Print a timestamped log line (no dependency on shared.log)."""
    from datetime import datetime

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [refresh_guard] {msg}", flush=True)


def _find_indexer_pid(config_name: str) -> Optional[int]:
    """Return the PID of a running index_rag.py process for *config_name*, or None.

    Matches any process whose command line contains both ``index_rag.py`` and
    ``--config <config_name>``.
    """
    for proc in psutil.process_iter(["pid", "cmdline"]):
        try:
            cmdline: List[str] = proc.info.get("cmdline") or []
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        cmdline_str = " ".join(cmdline)
        if "index_rag.py" in cmdline_str and f"--config {config_name}" in cmdline_str:
            return proc.pid

    return None


def _read_state(state_path: Path) -> dict:
    """Load guard state from JSON, returning defaults if missing or corrupt."""
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"consecutive_skips": 0}


def _write_state(state_path: Path, state: dict) -> None:
    """Persist guard state to JSON."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _kill_process(pid: int) -> None:
    """Terminate a process gracefully (SIGTERM), then SIGKILL after 10 s."""
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

    # Wait up to 10 seconds for graceful exit.
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


def _run_indexer(indexer_args: List[str]) -> int:
    """Run index_rag.py with *indexer_args* and return its exit code."""
    script = Path(__file__).parent / "index_rag.py"
    cmd = [sys.executable, str(script)] + indexer_args
    _log(f"Starting indexer: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


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
    state = _read_state(state_path)

    running_pid = _find_indexer_pid(config_name)

    if running_pid is None:
        # ── No active run — start fresh ───────────────────────────────────
        _log(f"No active indexer found for config '{config_name}'. Starting fresh run.")
        state["consecutive_skips"] = 0
        _write_state(state_path, state)
        return _run_indexer(args)

    # ── An active run exists ──────────────────────────────────────────────
    state["consecutive_skips"] = state.get("consecutive_skips", 0) + 1
    skip_count = state["consecutive_skips"]
    _write_state(state_path, state)

    if skip_count < MAX_SKIPS_BEFORE_KILL:
        _log(
            f"Indexer PID {running_pid} still running for config '{config_name}'. "
            f"Skipping this run (consecutive skips: {skip_count}/{MAX_SKIPS_BEFORE_KILL - 1})."
        )
        return 0

    # Third consecutive skip — kill and restart.
    _log(
        f"Indexer PID {running_pid} has been running for {skip_count} consecutive "
        f"cron periods for config '{config_name}'. Killing stale process and restarting."
    )
    _kill_process(running_pid)

    # Brief pause to let Qdrant/TEI connections close cleanly.
    time.sleep(2)

    state["consecutive_skips"] = 0
    _write_state(state_path, state)
    return _run_indexer(args)


if __name__ == "__main__":
    sys.exit(main())
