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
        (["python", "x_guard.py", "--config", "c1", "--yes"], True),
        ([r"C:\venv\python.exe", r"C:\repo\src\x_guard.py", "--config", "c1"], True),
        (["python", "src/x_guard.py", "--config=c1"], True),
        (["python", "src/x_guard.py", "--config", "c10"], False),  # exact name
        (["python", "src/x_guard.py", "--config"], False),
        (["python", "src/my_x_guard.py", "--config", "c1"], False),
        (["python", "src/other.py", "--config", "c1"], False),
        (["python", "src/x_guard.py.bak", "--config", "c1"], False),
        # H14: shell wrappers carry the whole command as one argument
        (["/bin/sh", "-c", "cd /r && python src/x_guard.py --config c1 && python y.py"], False),
        (["bash", "-c", "python src/x_guard.py --config c1"], False),
        (["cmd.exe", "/c", "python src\\x_guard.py --config c1"], False),
        (["C:\\Windows\\system32\\cmd.exe", "/c", "python", "src\\x_guard.py", "--config", "c1",
          "&&", "python", "y.py"], False),  # unquoted cmd /c: split arguments
        (["/usr/bin/bash", "-c", "x", "x_guard.py", "--config", "c1"], False),
        (["pwsh", "-Command", "python", "x_guard.py", "--config", "c1"], False),
        (["python3.12", "x_guard.py", "--config", "c1"], True),
        (["py.exe", "x_guard.py", "--config", "c1"], True),
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
    """A process-table row: ``info`` from the listing, ``cmdline()`` read later."""

    def __init__(self, pid: int, ppid: int, cmdline: list[str] | Exception,
                 name: str | None = "python"):
        self.pid = pid
        self.info = {"pid": pid, "ppid": ppid, "name": name}
        self._cmdline = cmdline
        self.cmdline_calls = 0

    def cmdline(self) -> list[str]:
        self.cmdline_calls += 1
        if isinstance(self._cmdline, Exception):
            raise self._cmdline
        return self._cmdline


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


# ── name filter: read the command line only of possible interpreters ─────────


@pytest.mark.parametrize(
    "name",
    [
        "python", "python3", "python3.12", "python3.13t", "python3.12-dbg",
        "pythonw", "pypy3", "pypy3.10", "Python",  # macOS framework build
        "python.exe", "PYTHON.EXE", "Python.Exe", "pythonw.exe", "python_d.exe",
        "python3.12.exe", "py.exe", "PY.EXE", "pyw.exe", "py",
        r"C:\venv\Scripts\python.exe", "/usr/bin/python3",
        "uv", "uv.exe", "uvx", "conda.exe", "micromamba", "pixi", "poetry",
        "flock", "timeout", "nohup",
        None, "",  # unreadable: decide by the command line
        "index_rag.py",  # Linux: script started through its shebang line
    ],
)
def test_candidate_names(name):
    assert gc_mod.is_candidate_name(name, "index_rag.py")


def test_truncated_linux_name_of_a_long_script_is_a_candidate():
    # Linux keeps 15 characters of the name: "git_pull_guard.py" -> "git_pull_guard."
    assert gc_mod.is_candidate_name("git_pull_guard.", "git_pull_guard.py")
    assert not gc_mod.is_candidate_name("git_pull_guard.", "index_rag.py")
    assert not gc_mod.is_candidate_name("git_pull", "git_pull_guard.py")  # too short to be cut


@pytest.mark.parametrize(
    "name",
    [
        "git", "git.exe", "bash", "sh", "cmd.exe", "powershell.exe", "pwsh",
        "conhost.exe", "svchost.exe", "explorer.exe", "node", "docker",
        "pythonista", "mypython", "python-language-server", "index_rag.pyc",
        "vmmemWSL", "System",
    ],
)
def test_non_candidate_names(name):
    assert not gc_mod.is_candidate_name(name, "index_rag.py")


def test_extra_names_are_case_insensitive_and_ignore_exe():
    assert gc_mod.is_candidate_name("MyIndexer.EXE", "index_rag.py", ["myindexer"])
    assert gc_mod.is_candidate_name("myindexer", "index_rag.py", ["MyIndexer.exe"])
    assert not gc_mod.is_candidate_name("myindexer", "index_rag.py", ["other"])


def _table(monkeypatch, procs, ancestors=frozenset({1})):
    monkeypatch.setattr(gc_mod.psutil, "process_iter", lambda attrs=None: iter(procs))
    monkeypatch.setattr(gc_mod, "ancestor_pids", lambda pid=None: set(ancestors))
    monkeypatch.delenv(gc_mod.PROCESS_NAMES_ENV, raising=False)


def test_non_candidates_never_have_their_command_line_read(monkeypatch):
    cmd = ["python", "index_rag.py", "--config", "c1"]
    others = [
        _FakeProc(10 + i, 1, ["x"], name=n)
        for i, n in enumerate(["svchost.exe", "git.exe", "bash", "cmd.exe", "chrome.exe", "node"])
    ]
    target = _FakeProc(500, 1, cmd, name="python.exe")
    _table(monkeypatch, [*others, target])
    assert find_process("index_rag.py", "c1") == 500
    assert [p.cmdline_calls for p in others] == [0] * len(others)
    assert target.cmdline_calls == 1


def test_a_matching_command_line_behind_a_non_candidate_name_is_not_read(monkeypatch):
    # A shell wrapper never matched (cmdline_matches); now it is not even read.
    shell = _FakeProc(20, 1, ["bash", "-c", "python index_rag.py --config c1"], name="bash")
    _table(monkeypatch, [shell])
    assert find_process("index_rag.py", "c1") is None
    assert shell.cmdline_calls == 0


def test_unreadable_name_falls_back_to_the_command_line(monkeypatch):
    # process_iter reports a name it may not read (AccessDenied) as None.
    hidden = _FakeProc(30, 1, ["python", "index_rag.py", "--config", "c1"], name=None)
    _table(monkeypatch, [hidden])
    assert find_process("index_rag.py", "c1") == 30
    assert hidden.cmdline_calls == 1


def test_process_gone_between_name_and_command_line_is_skipped(monkeypatch):
    cmd = ["python", "index_rag.py", "--config", "c1"]
    gone = _FakeProc(40, 1, psutil.NoSuchProcess(40), name="python.exe")
    zombie = _FakeProc(41, 1, psutil.ZombieProcess(41), name="python3")
    alive = _FakeProc(42, 1, cmd, name="python3")
    _table(monkeypatch, [gone, zombie, alive])
    assert find_process("index_rag.py", "c1") == 42
    _table(monkeypatch, [gone, zombie])
    assert find_process("index_rag.py", "c1") is None


def test_command_line_access_denied_matches_nothing_and_does_not_crash(monkeypatch):
    denied = _FakeProc(50, 1, psutil.AccessDenied(50), name="python.exe")
    other = _FakeProc(51, 1, ["python", "index_rag.py", "--config", "c1"], name="python.exe")
    _table(monkeypatch, [denied, other])
    assert find_process("index_rag.py", "c1") == 51
    _table(monkeypatch, [denied])
    assert find_process("index_rag.py", "c1") is None


def test_renamed_interpreter_needs_the_names_setting(monkeypatch):
    cmd = ["myindexer.exe", "index_rag.py", "--config", "c1"]
    renamed = _FakeProc(60, 1, cmd, name="myindexer.exe")
    _table(monkeypatch, [renamed])
    assert find_process("index_rag.py", "c1") is None
    monkeypatch.setenv(gc_mod.PROCESS_NAMES_ENV, " MyIndexer , other ")
    assert find_process("index_rag.py", "c1") == 60
    monkeypatch.setenv(gc_mod.PROCESS_NAMES_ENV, "*")  # every command line, as before
    assert find_process("index_rag.py", "c1") == 60
    monkeypatch.setenv(gc_mod.PROCESS_NAMES_ENV, " , ")
    assert find_process("index_rag.py", "c1") is None


def _old_find_process(procs, script, config_name, skip, exclude=()):
    """The scan before the name filter: every command line is read."""
    excluded = set(exclude)
    matches = {}
    for proc in procs:
        if proc.pid in skip:
            continue
        try:
            cmdline = proc.cmdline() or []
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if cmdline_matches(cmdline, script, config_name):
            matches[proc.pid] = proc.info["ppid"]
    while True:
        dropped = {p for p, pp in matches.items() if p in excluded or pp in excluded}
        if not dropped:
            break
        excluded |= dropped
        for p in dropped:
            matches.pop(p, None)
    roots = [p for p, pp in matches.items() if pp not in matches]
    return min(roots or matches) if matches else None


def _synthetic_table():
    """A busy process table: runs started every way the guards meet them."""
    procs = []
    pid = iter(range(1000, 100000, 7))

    def add(ppid, cmd, name):
        p = _FakeProc(next(pid), ppid, cmd, name=name)
        procs.append(p)
        return p.pid

    for i in range(300):  # unrelated processes
        add(4, [f"svc{i}.exe", "-k", "netsvcs"], f"svc{i}.exe")
    add(4, psutil.AccessDenied(0), "LsaIso.exe")
    add(4, psutil.AccessDenied(0), None)
    for cfg in ("c1", "c2", "c3", "c10"):
        # cron shell -> venv launcher -> interpreter (Windows)
        sh = add(1, ["cmd.exe", "/c", f"python src\\index_rag.py --config {cfg}"], "cmd.exe")
        launcher = add(sh, [r"C:\v\Scripts\python.exe", r"src\index_rag.py", "--config", cfg],
                       "python.exe")
        add(launcher, [r"C:\py\python.exe", r"src\index_rag.py", "--config", cfg], "python.exe")
    add(1, ["/usr/bin/python3.12", "src/git_pull_guard.py", "--config", "c1"], "python3.12")
    add(1, ["/usr/bin/python3", "./git_pull_guard.py", "--config", "c2"], "git_pull_guard.")
    uv = add(1, ["uv", "run", "src/refresh_guard.py", "--config", "c3", "--yes"], "uv")
    add(uv, ["/v/bin/python", "src/refresh_guard.py", "--config", "c3", "--yes"], "python")
    fl = add(1, ["flock", "/tmp/l", "python3", "src/index_rag.py", "--config", "c4"], "flock")
    add(fl, ["python3", "src/index_rag.py", "--config", "c4"], "python3")
    add(1, ["py.exe", "-3.12", "src\\index_rag.py", "--config", "c5"], "py.exe")
    add(1, ["Python", "src/index_rag.py", "--config=c6"], "Python")
    add(1, ["python", "src/index_rag.py", "--config", "c7"], None)  # name hidden
    add(1, psutil.NoSuchProcess(0), "python.exe")  # exited meanwhile
    add(1, ["git.exe", "fetch", "--all", "--prune"], "git.exe")
    add(1, ["bash", "-c", "python src/index_rag.py --config c8"], "bash")
    return procs


def test_detection_parity_with_the_old_scan_on_a_synthetic_table(monkeypatch):
    procs = _synthetic_table()
    skip = {1}
    scripts = ("index_rag.py", "git_pull_guard.py", "refresh_guard.py")
    configs = ("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c10", "c99")
    compared = found = 0
    for script in scripts:
        for cfg in configs:
            old = _old_find_process(procs, script, cfg, skip)
            for p in procs:
                p.cmdline_calls = 0
            _table(monkeypatch, procs, skip)
            new = find_process(script, cfg)
            assert new == old, (script, cfg)
            compared += 1
            found += new is not None
            reads = sum(p.cmdline_calls for p in procs)
            assert reads <= 20, reads  # not ~320
            # Excluding the reported run gives the same answer as well.
            if old is not None:
                assert find_process(script, cfg, exclude={old}) == _old_find_process(
                    procs, script, cfg, skip, exclude={old}
                )
    assert compared == 30 and found >= 9


def test_real_scan_reads_few_command_lines(monkeypatch):
    """On the real process table only candidate names have their command line read."""
    calls = {"n": 0}
    real = psutil.Process.cmdline

    def _counting(self):
        calls["n"] += 1
        return real(self)

    monkeypatch.setattr(psutil.Process, "cmdline", _counting)
    monkeypatch.delenv(gc_mod.PROCESS_NAMES_ENV, raising=False)
    total = len(list(psutil.process_iter(["name"])))
    proc = _spawn("x_guard.py", "--config", (cfg := _cfg()))
    try:
        _wait_visible(proc.pid)
        # Linux psutil reads the command line to complete a 15-character
        # name; count those separately, they are part of the listing.
        calls["n"] = 0
        names = [p.info.get("name") for p in psutil.process_iter(["name"])]
        listing = calls["n"]
        calls["n"] = 0
        assert find_process("x_guard.py", cfg) == proc.pid
        candidates = sum(1 for n in names if gc_mod.is_candidate_name(n, "x_guard.py"))
        assert calls["n"] - listing <= candidates + 5
        assert candidates < total
    finally:
        _stop(proc)


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


# ── H14: the cron shell of an earlier tick is not a guard ───────────────────

_FAKE_REFRESH = textwrap.dedent(
    """
    import subprocess, sys
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)",
                      "index_rag.py", "--config", sys.argv[2]]).wait()
    """
)


def test_earlier_ticks_cron_shell_is_not_a_competing_guard(tmp_path):
    """H14: tick 1's ``sh -c "... git_pull_guard.py --config X && ...
    refresh_guard.py --config X"`` stays alive while its refresh guard waits
    for the indexer. Tick 2 must not see it as another pull guard (it used
    to skip twice and then kill the whole tree, indexer included)."""
    cfg = _cfg()
    (tmp_path / "git_pull_guard.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "refresh_guard.py").write_text(_FAKE_REFRESH, encoding="utf-8")
    py = sys.executable if " " not in sys.executable else f'"{sys.executable}"'
    # shell=True: ``/bin/sh -c "..."`` on POSIX, ``cmd.exe /c "..."`` on Windows,
    # the way cron and the Windows task scheduler wrap the two guards.
    command = (
        f"{py} git_pull_guard.py --config {cfg} "
        f"&& {py} refresh_guard.py --config {cfg} --yes"
    )
    shell = subprocess.Popen(command, shell=True, cwd=tmp_path)
    try:
        deadline = time.monotonic() + 20
        indexer = None
        while time.monotonic() < deadline and indexer is None:
            indexer = find_process("index_rag.py", cfg)
            time.sleep(0.1)
        assert indexer is not None, "fake indexer did not start"
        assert shell.poll() is None  # the shell waits for its refresh guard
        assert find_process("git_pull_guard.py", cfg) is None
        refresh = find_process("refresh_guard.py", cfg)
        assert refresh is not None and refresh != shell.pid
        assert psutil.Process(indexer).ppid() != shell.pid
    finally:
        kill_process_tree(shell.pid, lambda _msg: None, timeout=5)
        _stop(shell)
