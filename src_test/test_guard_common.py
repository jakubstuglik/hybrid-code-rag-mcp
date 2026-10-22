# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Process helpers of the cron guards (``src/guard_common.py``).

Uses real child processes: the bugs these helpers fix are about which
processes a scan sees (itself, its cron shell) and which ones a kill stops.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
import time
import uuid
from pathlib import Path

import psutil
import pytest

import guard_common as gc_mod
from guard_common import (
    GuardLock,
    ancestor_pids,
    cmdline_matches,
    find_process,
    kill_process_tree,
    process_start_time,
    read_state,
    register_sighting,
    reset_sightings,
    write_state,
)

_SRC = Path(__file__).resolve().parent.parent / "src"
SLEEP = "import time; time.sleep(60)"


def _cfg() -> str:
    return f"cfg_{uuid.uuid4().hex[:10]}"


def _spawn(*extra: str, code: str = SLEEP) -> subprocess.Popen:
    return subprocess.Popen([sys.executable, "-c", code, *extra])


def _wait_visible(pid: int, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if psutil.Process(pid).cmdline():
                return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        time.sleep(0.05)


def _stop(*procs: subprocess.Popen) -> None:
    for p in procs:
        if p.poll() is None:
            p.kill()
        p.wait(timeout=30)


# ── matching and scanning ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "cmdline,expected",
    [
        (["python", "src/x_guard.py", "--config", "c1"], True),
        (["python", "src/x_guard.py", "--config", "c10"], True),  # substring, as before
        (["python", "src/x_guard.py", "--config=c1"], False),
        (["python", "src/other.py", "--config", "c1"], False),
        ([], False),
    ],
)
def test_cmdline_matches(cmdline, expected):
    assert cmdline_matches(cmdline, "x_guard.py", "c1") is expected


def test_ancestors_include_self_and_parent():
    pids = ancestor_pids()
    assert os.getpid() in pids
    assert os.getppid() in pids


def test_ancestors_of_gone_pid_is_just_that_pid():
    proc = _spawn(code="pass")
    proc.wait(timeout=30)
    assert ancestor_pids(proc.pid) == {proc.pid}


def test_finds_another_matching_process():
    cfg = _cfg()
    proc = _spawn("x_guard.py", "--config", cfg)
    try:
        _wait_visible(proc.pid)
        assert find_process("x_guard.py", cfg) == proc.pid
        assert find_process("x_guard.py", cfg + "_other") is None
        assert find_process("x_guard.py", cfg, exclude={proc.pid}) is None
    finally:
        _stop(proc)


# Plays the Windows venv launcher: starts the interpreter as a child with the
# same arguments and waits for it.
_LAUNCHER = textwrap.dedent(
    """
    import subprocess, sys
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)", *sys.argv[1:]]
    )
    print(child.pid, flush=True)
    child.wait()
    """
)


def test_launcher_and_its_child_count_as_one_run_at_the_top():
    """A run whose interpreter is a child with the same command line is
    reported by its topmost process, whatever the pid order."""
    cfg = _cfg()
    proc = subprocess.Popen(
        [sys.executable, "-c", _LAUNCHER, "x_guard.py", "--config", cfg],
        stdout=subprocess.PIPE, text=True,
    )
    try:
        child_pid = int(proc.stdout.readline())
        _wait_visible(child_pid)
        assert find_process("x_guard.py", cfg) == proc.pid
        assert find_process("x_guard.py", cfg, exclude={proc.pid}) is None
    finally:
        kill_process_tree(proc.pid, lambda _msg: None, timeout=5)
        _stop(proc)
        proc.stdout.close()


class _FakeProc:
    def __init__(self, pid: int, ppid: int, cmdline: list[str]):
        self.pid = pid
        self.info = {"pid": pid, "ppid": ppid, "cmdline": cmdline}


def test_child_with_lower_pid_than_its_launcher_is_not_reported(monkeypatch):
    """Windows reuses pids, so the interpreter child can have a lower pid
    than the launcher that started it; the launcher is still the run."""
    cmd = ["python", "x_guard.py", "--config", "c1"]
    procs = [
        _FakeProc(100, 900, cmd),     # interpreter, child of 900
        _FakeProc(900, 50, cmd),      # venv launcher
        _FakeProc(700, 650, ["python", "other.py"]),
    ]
    monkeypatch.setattr(gc_mod.psutil, "process_iter", lambda attrs=None: iter(procs))
    monkeypatch.setattr(gc_mod, "ancestor_pids", lambda pid=None: {1})
    assert find_process("x_guard.py", "c1") == 900
    assert find_process("x_guard.py", "c1", exclude={900}) is None
    assert find_process("x_guard.py", "c1", exclude={100}) == 900


def test_two_separate_runs_report_the_lowest_top_pid(monkeypatch):
    cmd = ["python", "x_guard.py", "--config", "c1"]
    procs = [_FakeProc(300, 1, cmd), _FakeProc(200, 300, cmd), _FakeProc(400, 1, cmd)]
    monkeypatch.setattr(gc_mod.psutil, "process_iter", lambda attrs=None: iter(procs))
    monkeypatch.setattr(gc_mod, "ancestor_pids", lambda pid=None: {1})
    assert find_process("x_guard.py", "c1") == 300


def test_returns_lowest_pid_of_several():
    cfg = _cfg()
    procs = [_spawn("x_guard.py", "--config", cfg) for _ in range(3)]
    try:
        for p in procs:
            _wait_visible(p.pid)
        assert find_process("x_guard.py", cfg) == min(p.pid for p in procs)
    finally:
        _stop(*procs)


_SELF_SCAN = textwrap.dedent(
    """
    import json, subprocess, sys
    sys.path.insert(0, sys.argv[1])
    import guard_common, psutil
    cfg = sys.argv[2]
    if sys.argv[3] == "parent":
        # Plays the cron shell: same script and config on its command line.
        out = subprocess.run([sys.executable, "-c", sys.argv[4], sys.argv[1], cfg, "child",
                              sys.argv[4], "x_guard.py", "--config", cfg],
                             capture_output=True, text=True)
        print(out.stdout.strip())
    else:
        naive = [p.pid for p in psutil.process_iter(["cmdline"])
                 if guard_common.cmdline_matches(p.info.get("cmdline") or [], "x_guard.py", cfg)]
        print(json.dumps({"found": guard_common.find_process("x_guard.py", cfg),
                          "naive": len(naive)}))
    """
)


def test_scan_never_finds_itself_or_its_cron_shell():
    """H1: the guard and its ``sh -c`` parent match the scan; neither may count."""
    cfg = _cfg()
    out = subprocess.run(
        [sys.executable, "-c", _SELF_SCAN, str(_SRC), cfg, "parent", _SELF_SCAN,
         "x_guard.py", "--config", cfg],
        capture_output=True, text=True, timeout=120,
        check=False,
    )
    result = json.loads(out.stdout.strip().splitlines()[-1])
    assert result["naive"] >= 2  # the old scan saw itself and its parent
    assert result["found"] is None


# ── skip counter tied to a process ──────────────────────────────────────────


def test_counter_grows_for_the_same_process():
    state: dict = {"consecutive_skips": 0}
    assert [register_sighting(state, 10, 1.0) for _ in range(3)] == [1, 2, 3]
    assert state["pid"] == 10 and state["pid_start_time"] == 1.0


def test_counter_restarts_for_another_pid():
    state = {"consecutive_skips": 2, "pid": 10, "pid_start_time": 1.0}
    assert register_sighting(state, 11, 5.0) == 1


def test_counter_restarts_when_pid_was_reused():
    state = {"consecutive_skips": 2, "pid": 10, "pid_start_time": 1.0}
    assert register_sighting(state, 10, 2.0) == 1


def test_legacy_state_without_pid_restarts_at_one():
    state = {"consecutive_skips": 2}
    assert register_sighting(state, 10, 1.0) == 1


def test_counter_after_reset_starts_at_one():
    state = {"consecutive_skips": 2, "pid": 10, "pid_start_time": 1.0}
    reset_sightings(state)
    assert state == {"consecutive_skips": 0}
    assert register_sighting(state, 10, 1.0) == 1


def test_process_start_time():
    assert process_start_time(os.getpid()) == psutil.Process().create_time()
    proc = _spawn(code="pass")
    proc.wait(timeout=30)
    assert process_start_time(proc.pid) is None


# ── state file ───────────────────────────────────────────────────────────────


def test_state_roundtrip_and_no_temp_left(tmp_path):
    path = tmp_path / "sub" / "state.json"
    write_state(path, {"consecutive_skips": 2, "pid": 5})
    assert read_state(path) == {"consecutive_skips": 2, "pid": 5}
    assert [p.name for p in path.parent.iterdir()] == ["state.json"]


@pytest.mark.parametrize("content", ["{not json", "[1, 2]", ""])
def test_bad_state_reads_as_default(tmp_path, content):
    path = tmp_path / "state.json"
    path.write_text(content, encoding="utf-8")
    assert read_state(path) == {"consecutive_skips": 0}


def test_missing_state_reads_as_default(tmp_path):
    assert read_state(tmp_path / "none.json") == {"consecutive_skips": 0}


# ── killing a process tree ──────────────────────────────────────────────────

_PARENT = textwrap.dedent(
    """
    import subprocess, sys, time
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    print(child.pid, flush=True)
    time.sleep(60)
    """
)


def test_kill_tree_stops_wrapper_and_child():
    """H3b: killing a wrapper (shell, venv launcher) must stop its Python child too."""
    parent = subprocess.Popen([sys.executable, "-c", _PARENT], stdout=subprocess.PIPE, text=True)
    try:
        child_pid = int(parent.stdout.readline())
        logs: list[str] = []
        kill_process_tree(parent.pid, logs.append, timeout=5)
        parent.wait(timeout=30)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                if psutil.Process(child_pid).status() == psutil.STATUS_ZOMBIE:
                    break
            except psutil.NoSuchProcess:
                break
            time.sleep(0.1)
        else:
            pytest.fail("child process survived the tree kill")
        assert any("killed" in m for m in logs)
    finally:
        _stop(parent)
        parent.stdout.close()
        try:
            psutil.Process(child_pid).kill()
        except (psutil.NoSuchProcess, NameError, UnboundLocalError):
            pass


def test_kill_tree_of_gone_pid_logs_and_returns():
    proc = _spawn(code="pass")
    proc.wait(timeout=30)
    logs: list[str] = []
    kill_process_tree(proc.pid, logs.append)
    assert logs and "already gone" in logs[0]


def test_kill_tree_escalates_to_sigkill(monkeypatch):
    proc = _spawn()
    try:
        _wait_visible(proc.pid)
        monkeypatch.setattr(gc_mod.psutil.Process, "terminate", lambda self: None)
        logs: list[str] = []
        kill_process_tree(proc.pid, logs.append, timeout=0.5)
        assert proc.wait(timeout=30) is not None
        assert any("SIGKILL" in m for m in logs)
    finally:
        _stop(proc)


# ── lock ─────────────────────────────────────────────────────────────────────

_HOLDER = textwrap.dedent(
    """
    import sys, time
    sys.path.insert(0, sys.argv[1])
    from guard_common import GuardLock
    lock = GuardLock(sys.argv[2])
    assert lock.acquire(timeout_s=5)
    print("locked", flush=True)
    time.sleep(float(sys.argv[3]))
    """
)


def _holder(path: Path, seconds: float) -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, "-c", _HOLDER, str(_SRC), str(path), str(seconds)],
        stdout=subprocess.PIPE,
        text=True,
    )
    assert proc.stdout.readline().strip() == "locked"
    return proc


def test_lock_is_exclusive_across_processes(tmp_path):
    path = tmp_path / "g.lock"
    holder = _holder(path, 60)
    try:
        assert GuardLock(path).acquire(timeout_s=0.3) is False
    finally:
        _stop(holder)
        holder.stdout.close()
    lock = GuardLock(path)
    assert lock.acquire(timeout_s=5) is True  # released when the holder died
    lock.release()


def test_lock_waits_for_release(tmp_path):
    path = tmp_path / "g.lock"
    holder = _holder(path, 1.0)
    try:
        lock = GuardLock(path)
        t0 = time.monotonic()
        assert lock.acquire(timeout_s=20) is True
        assert time.monotonic() - t0 > 0.3
        lock.release()
    finally:
        _stop(holder)
        holder.stdout.close()


def test_lock_context_manager_and_double_release(tmp_path):
    path = tmp_path / "x" / "g.lock"
    with GuardLock(path) as lock:
        assert path.exists()
        assert GuardLock(path).acquire(timeout_s=0) is False
    lock.release()  # no-op
    with GuardLock(path):
        pass
