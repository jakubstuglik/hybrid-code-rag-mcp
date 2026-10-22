# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0
"""Process helpers shared by the cron guards (refresh_guard, git_pull_guard).

Kept free of heavy imports (only ``psutil`` and the standard library) so the
guards start fast and do not load the indexing stack.

* :func:`find_process` scans the process table in pid order and never matches
  the calling process or any of its ancestors (the cron ``sh -c`` shell that
  started it), so a guard cannot mistake itself for another run.
* :func:`register_sighting` keeps the consecutive-skip counter tied to one
  process (pid + start time): a different process starts again at 1.
* :func:`kill_process_tree` terminates a process and all its descendants, so
  killing a shell wrapper or a Windows venv launcher also stops the Python
  process it started.
* :class:`GuardLock` is an exclusive lock file held while a guard decides and
  starts a run, so two guard invocations cannot both start one.
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections.abc import Callable, Iterable
from pathlib import Path

import psutil

LogFn = Callable[[str], None]


def ancestor_pids(pid: int | None = None) -> set[int]:
    """Return *pid* (default: this process) and the pids of all its ancestors."""
    pid = os.getpid() if pid is None else pid
    result = {pid}
    try:
        proc = psutil.Process(pid)
        for parent in proc.parents():
            result.add(parent.pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return result


def cmdline_matches(cmdline: Iterable[str], script: str, config_name: str) -> bool:
    """True when *cmdline* runs *script* with ``--config <config_name>``."""
    cmdline_str = " ".join(cmdline)
    return script in cmdline_str and f"--config {config_name}" in cmdline_str


def find_process(
    script: str,
    config_name: str,
    *,
    exclude: set[int] | None = None,
) -> int | None:
    """Return the lowest pid whose command line runs *script* for *config_name*.

    The calling process and its ancestors are always excluded, as are the
    pids in *exclude* and the matching processes they started. A match whose
    parent is also a match is a child of the same run (the venv launcher on
    Windows starts the real interpreter with the same command line), so only
    the topmost process of each run counts; killing its tree stops the whole
    run.
    """
    skip = ancestor_pids()
    excluded = set(exclude or ())
    matches: dict[int, int | None] = {}
    for proc in psutil.process_iter(["pid", "ppid", "cmdline"]):
        try:
            if proc.pid in skip:
                continue
            cmdline = proc.info.get("cmdline") or []
            ppid = proc.info.get("ppid")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if cmdline_matches(cmdline, script, config_name):
            matches[proc.pid] = ppid
    while True:
        dropped = {pid for pid, ppid in matches.items() if pid in excluded or ppid in excluded}
        if not dropped:
            break
        excluded |= dropped
        for pid in dropped:
            matches.pop(pid, None)
    roots = [pid for pid, ppid in matches.items() if ppid not in matches]
    return min(roots or matches) if matches else None


def process_start_time(pid: int) -> float | None:
    """Return the start time of *pid*, or None when it is gone or hidden."""
    try:
        return psutil.Process(pid).create_time()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def register_sighting(state: dict, pid: int, start_time: float | None) -> int:
    """Count one more consecutive sighting of *pid* in *state*; return the count.

    The counter only grows while the same process (same pid and start time)
    is seen; any other process restarts it at 1. Updates *state* in place.
    """
    same = (
        state.get("pid") == pid
        and state.get("pid_start_time") == start_time
        and int(state.get("consecutive_skips", 0) or 0) > 0
    )
    count = int(state.get("consecutive_skips", 0) or 0) + 1 if same else 1
    state["consecutive_skips"] = count
    state["pid"] = pid
    state["pid_start_time"] = start_time
    return count


def reset_sightings(state: dict) -> None:
    """Clear the skip counter and the process it was counting."""
    state["consecutive_skips"] = 0
    state.pop("pid", None)
    state.pop("pid_start_time", None)


def read_state(state_path: Path) -> dict:
    """Load guard state from JSON, returning defaults if missing or corrupt."""
    if state_path.exists():
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
    return {"consecutive_skips": 0}


def write_state(state_path: Path, state: dict) -> None:
    """Persist guard state as JSON (temp file + rename, never half written)."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_name(
        f"{state_path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    )
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    for attempt in range(20):
        try:
            os.replace(tmp, state_path)
            return
        except PermissionError:
            time.sleep(0.05 * (attempt + 1))
    os.replace(tmp, state_path)


def kill_process_tree(pid: int, log: LogFn, *, timeout: float = 10.0) -> None:
    """Terminate *pid* and all its descendants; SIGKILL what is left after *timeout*."""
    try:
        root = psutil.Process(pid)
    except psutil.NoSuchProcess:
        log(f"Process {pid} already gone before kill attempt.")
        return
    try:
        children = root.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        children = []
    procs = [root] + children
    names = ", ".join(str(p.pid) for p in procs)
    log(f"Sending SIGTERM to PID {pid} and its child processes ({names})...")
    for proc in procs:
        try:
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    _, alive = psutil.wait_procs(procs, timeout=timeout)
    if alive:
        log(
            "Processes "
            + ", ".join(str(p.pid) for p in alive)
            + " did not exit after SIGTERM — sending SIGKILL."
        )
        for proc in alive:
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        psutil.wait_procs(alive, timeout=5)
    log(f"Process {pid} killed.")


class GuardLock:
    """Exclusive lock on a small file, released on close or process exit.

    ``acquire(timeout_s)`` waits up to *timeout_s* seconds and returns False
    when another process still holds the lock. The OS drops the lock when the
    holder dies, so a killed guard never leaves it stuck.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._fh = None

    def acquire(self, timeout_s: float = 60.0, poll_s: float = 0.2) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(self.path, "a+b")
        deadline = time.monotonic() + max(0.0, timeout_s)
        while True:
            if _try_lock(fh):
                self._fh = fh
                try:
                    fh.seek(0)
                    fh.truncate()
                    fh.write(str(os.getpid()).encode("ascii"))
                    fh.flush()
                except OSError:
                    pass
                return True
            if time.monotonic() >= deadline:
                fh.close()
                return False
            time.sleep(poll_s)

    def release(self) -> None:
        fh, self._fh = self._fh, None
        if fh is None:
            return
        try:
            _unlock(fh)
        finally:
            fh.close()

    def __enter__(self) -> GuardLock:
        if not self.acquire():
            raise TimeoutError(f"could not lock {self.path}")
        return self

    def __exit__(self, *exc) -> None:
        self.release()


if os.name == "nt":  # pragma: no cover - exercised on Windows
    import msvcrt

    def _try_lock(fh) -> bool:
        try:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    def _unlock(fh) -> None:
        try:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass

else:
    import fcntl

    def _try_lock(fh) -> bool:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def _unlock(fh) -> None:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
