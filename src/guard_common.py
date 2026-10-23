# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0
"""Process helpers shared by the cron guards (refresh_guard, git_pull_guard).

Kept free of heavy imports (only ``psutil`` and the standard library) so the
guards start fast and do not load the indexing stack.

* :func:`find_process` scans the process table in pid order and never matches
  the calling process or any of its ancestors (the cron ``sh -c`` shell that
  started it), so a guard cannot mistake itself for another run. It reads
  process names first (cheap) and the command line only of processes that
  can run a Python script (:func:`is_candidate_name`): reading every command
  line takes seconds on a busy Windows machine.
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
import re
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


# Executables that only wrap a command line (cron ``sh -c``, ``cmd /c``):
# never the guard or indexer process itself.
_SHELLS = frozenset({"sh", "bash", "dash", "zsh", "ksh", "fish", "cmd", "powershell", "pwsh"})


def _base_name(arg: str) -> str:
    return arg.replace("\\", "/").rsplit("/", 1)[-1]


def cmdline_matches(cmdline: Iterable[str], script: str, config_name: str) -> bool:
    """True when *cmdline* runs *script* with ``--config <config_name>``.

    The script and the config must be separate arguments, as in the
    interpreter process (``python .../index_rag.py --config X``). A shell
    wrapper (``sh -c "... git_pull_guard.py --config X && ..."``,
    ``cmd /c "..."``) never matches, whether the shell keeps the command
    as one argument or (unquoted ``cmd /c``) splits it: the cron shell of an earlier tick stays alive while its
    refresh_guard waits for the indexer, and must not count as a guard.
    The config name must match exactly (``c1`` does not match ``c10``).
    """
    args = list(cmdline)
    if not args:
        return False
    exe = _base_name(args[0]).lower()
    if exe.endswith(".exe"):
        exe = exe[:-4]
    if exe in _SHELLS:
        return False
    has_script = any(_base_name(arg) == script for arg in args)
    if not has_script:
        return False
    for i, arg in enumerate(args):
        if arg == "--config" and i + 1 < len(args) and args[i + 1] == config_name:
            return True
        if arg == f"--config={config_name}":
            return True
    return False


# Process names that can run a guard or indexer script, compared lower case
# without ``.exe``: CPython and PyPy interpreters (``python``, ``python3``,
# ``python3.12``, ``python3.13t``, ``pythonw``, ``python_d``, ``pypy3.10``,
# macOS ``Python``), the Windows ``py``/``pyw`` launcher (a venv's
# ``python.exe`` launcher is named like the interpreter) ...
_INTERPRETER_NAME = re.compile(
    r"^(?:python|pythonw|pypy|pyw?)(?:\d+(?:\.\d+)*)?(?:t|d|_d|w|-dbg)?$"
)
# ... tools that start a script through ``run`` (``uv run src/index_rag.py``
# keeps the script on its own command line) and command wrappers that fork
# the interpreter (``flock``, ``timeout``) or exec it. A wrapper's command line
# matches like the interpreter's, so keeping them keeps the reported pid the
# topmost process of the run, as before.
_LAUNCHER_NAMES = frozenset(
    {
        "uv", "uvx", "conda", "mamba", "micromamba", "pixi", "poetry", "pipenv",
        "hatch", "pdm", "rye", "pipx",
        "flock", "timeout", "time", "chronic", "run-one", "nice", "nohup", "env",
        "setsid", "ionice", "taskset", "stdbuf", "caffeinate",
    }
)
# Extra names (comma separated) for an interpreter with another name; ``*``
# reads every command line (the scan before the name filter).
PROCESS_NAMES_ENV = "HCR_GUARD_PROCESS_NAMES"
# Linux keeps at most 15 characters of a process name (``comm``).
_COMM_LEN = 15


def _normalized_name(name: str) -> str:
    name = _base_name(name).lower()
    return name[:-4] if name.endswith(".exe") else name


def _extra_names() -> tuple[frozenset[str], bool]:
    """Names from ``HCR_GUARD_PROCESS_NAMES`` and whether it asks for all (``*``)."""
    raw = os.environ.get(PROCESS_NAMES_ENV, "")
    items = {item.strip() for item in raw.split(",") if item.strip()}
    scan_all = "*" in items
    return frozenset(_normalized_name(i) for i in items if i != "*"), scan_all


def is_candidate_name(
    name: str | None, script: str, extra: Iterable[str] = ()
) -> bool:
    """True when a process called *name* may be running *script*.

    Unknown names (``None`` or empty: access denied, process exiting) are
    candidates, so the command line decides as before. So is the script
    itself: on Linux a script started through its shebang line is named
    after the script (``comm``, cut to 15 characters).
    """
    if not name:
        return True
    norm = _normalized_name(name)
    if not norm:
        return True
    if _INTERPRETER_NAME.match(norm) or norm in _LAUNCHER_NAMES:
        return True
    if norm in {_normalized_name(e) for e in extra}:
        return True
    script_l = script.lower()
    return norm == script_l or (len(norm) >= _COMM_LEN and script_l.startswith(norm))


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

    Only processes whose name passes :func:`is_candidate_name` (plus the
    names in ``HCR_GUARD_PROCESS_NAMES``; ``*`` checks every process) have
    their command line read. A process that exits between the two steps is
    skipped; a command line that cannot be read matches nothing, as before.
    """
    skip = ancestor_pids()
    excluded = set(exclude or ())
    extra, scan_all = _extra_names()
    matches: dict[int, int | None] = {}
    for proc in psutil.process_iter(["pid", "ppid", "name"]):
        try:
            if proc.pid in skip:
                continue
            ppid = proc.info.get("ppid")
            if not scan_all and not is_candidate_name(proc.info.get("name"), script, extra):
                continue
            cmdline = proc.cmdline() or []
        except psutil.AccessDenied:
            continue
        except psutil.NoSuchProcess:  # gone (or a zombie) since the listing
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
