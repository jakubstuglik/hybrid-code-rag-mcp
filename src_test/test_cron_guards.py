# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Decision logic of ``refresh_guard.py`` and ``git_pull_guard.py``.

Regression tests for the formal model of the cron path:

* H1  git_pull_guard counted itself / its cron shell, skipped, then killed itself;
* H2  two refresh_guard runs could both start an indexer (scan and start not atomic);
* H3  the skip counter was not tied to a pid, so a fresh run was killed early;
* H3b the kill hit only a wrapper process and a second indexer was started;
* H4  git_pull_guard pulled while the previous tick's indexer was still running;
* H17 refresh_guard started an indexer while an earlier tick's pull guard was
      still fetching; that guard then pulled under the running indexer.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import threading
import time
import uuid
from pathlib import Path

import pytest

from guard_common import find_process

import refresh_guard as rg

_SRC = Path(__file__).resolve().parent.parent / "src"


class _FakeProc:
    def __init__(self, code: int = 0) -> None:
        self.code = code

    def wait(self):
        return self.code


@pytest.fixture
def guard(tmp_path, monkeypatch):
    """refresh_guard with a scripted process table."""
    state_path = tmp_path / "refresh_guard_state.json"
    world = {"running": [], "pull_guards": [], "start_times": {}, "started": [], "killed": []}

    def _scan(config_name):
        return min(world["running"]) if world["running"] else None

    def _scan_pull(config_name):
        return min(world["pull_guards"]) if world["pull_guards"] else None

    def _start(args):
        world["started"].append(list(args))
        return _FakeProc(0)

    def _kill(pid):
        world["killed"].append(pid)
        for key in ("running", "pull_guards"):
            if pid in world[key]:
                world[key].remove(pid)

    monkeypatch.setattr(rg, "_resolve_state_path", lambda name: state_path)
    monkeypatch.setattr(rg, "_find_indexer_pid", _scan)
    monkeypatch.setattr(rg, "_find_pull_guard_pid", _scan_pull, raising=False)
    monkeypatch.setattr(rg, "_start_indexer", _start)
    monkeypatch.setattr(rg, "_kill_process", _kill)
    monkeypatch.setattr(rg, "process_start_time", lambda pid: world["start_times"].get(pid, 1.0))
    monkeypatch.setattr(rg.time, "sleep", lambda s: None)

    def run():
        monkeypatch.setattr(sys, "argv", ["refresh_guard.py", "--config", "cfg", "--yes"])
        return rg.main()

    world["run"] = run
    world["state_path"] = state_path
    return world


def _state(guard) -> dict:
    return json.loads(guard["state_path"].read_text(encoding="utf-8"))


def test_starts_when_nothing_runs_and_resets_counter(guard):
    guard["state_path"].write_text('{"consecutive_skips": 2, "pid": 7}', encoding="utf-8")
    assert guard["run"]() == 0
    assert guard["started"] == [["--config", "cfg", "--yes"]]
    assert _state(guard) == {"consecutive_skips": 0}


def test_kills_the_same_run_on_third_sighting(guard):
    guard["running"].append(100)
    assert guard["run"]() == 0 and guard["run"]() == 0
    assert guard["killed"] == [] and guard["started"] == []
    assert guard["run"]() == 0
    assert guard["killed"] == [100]
    assert len(guard["started"]) == 1
    assert _state(guard)["consecutive_skips"] == 0


def test_fresh_run_is_not_killed_after_one_sighting(guard):
    """H3: two sightings of run A, then a new run B; B must start at 1."""
    guard["running"].append(100)
    guard["run"]()
    guard["run"]()
    guard["running"].remove(100)  # A finished between ticks ...
    guard["running"].append(200)  # ... and someone started B by hand
    guard["run"]()
    assert guard["killed"] == []
    assert _state(guard)["consecutive_skips"] == 1 and _state(guard)["pid"] == 200
    guard["run"]()
    guard["run"]()
    assert guard["killed"] == [200]


def test_reused_pid_counts_as_a_new_run(guard):
    guard["running"].append(100)
    guard["run"]()
    guard["run"]()
    guard["start_times"][100] = 99.0  # same pid, other process
    guard["run"]()
    assert guard["killed"] == []
    assert _state(guard)["consecutive_skips"] == 1


def test_no_second_indexer_when_kill_left_one_running(guard, monkeypatch):
    """H3b: if a process for the config survives the kill, do not start another."""
    guard["running"].extend([100, 101])
    monkeypatch.setattr(rg, "_kill_process", lambda pid: guard["killed"].append(pid))
    for _ in range(3):
        guard["run"]()
    assert guard["killed"] == [100]
    assert guard["started"] == []


def test_returns_indexer_exit_code(guard, monkeypatch):
    monkeypatch.setattr(rg, "_start_indexer", lambda args: _FakeProc(3))
    assert guard["run"]() == 3


def test_usage_error_without_config(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["refresh_guard.py", "--yes"])
    assert rg.main() == 2
    assert "Usage" in capsys.readouterr().err


def test_skips_when_another_guard_holds_the_lock(guard, monkeypatch):
    from guard_common import GuardLock

    monkeypatch.setattr(rg, "LOCK_TIMEOUT_S", 0.2)
    lock = GuardLock(guard["state_path"].with_name("refresh_guard_state.json.lock"))
    assert lock.acquire(timeout_s=1)
    try:
        assert guard["run"]() == 0
    finally:
        lock.release()
    assert guard["started"] == []
    assert not guard["state_path"].exists()  # did not even scan


def test_overlapping_guards_start_one_indexer(guard, monkeypatch):
    """H2: two guards scan at the same time; only one may start an indexer."""
    lock_ready = threading.Barrier(2)

    def _slow_scan(config_name):
        time.sleep(0.3)  # both guards would be past the scan before either starts
        return min(guard["running"]) if guard["running"] else None

    def _start(args):
        guard["started"].append(list(args))
        guard["running"].append(500 + len(guard["started"]))
        return _FakeProc(0)

    monkeypatch.setattr(rg, "_find_indexer_pid", _slow_scan)
    monkeypatch.setattr(rg, "_start_indexer", _start)
    monkeypatch.setattr(sys, "argv", ["refresh_guard.py", "--config", "cfg"])

    errors: list[BaseException] = []

    def _guard():
        lock_ready.wait()
        try:
            rg.main()
        except BaseException as exc:  # noqa: BLE001 - reported below
            errors.append(exc)

    threads = [threading.Thread(target=_guard) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert errors == []
    assert len(guard["started"]) == 1


def test_real_scan_ignores_the_guard_itself(tmp_path, monkeypatch):
    """The refresh guard's own command line never counts as an indexer."""
    cfg = f"cfg_{uuid.uuid4().hex[:8]}"
    assert rg._find_indexer_pid(cfg) is None


# ── git_pull_guard: H1 on the real scan ──────────────────────────────────────

_PULL_GUARD_TICKS = textwrap.dedent(
    """
    import json, os, sys, types
    from pathlib import Path
    src, state, cfg = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    sys.path[:0] = [os.path.dirname(src), src]
    pkg = types.ModuleType("shared")  # skip shared/__init__ (indexing stack)
    pkg.__path__ = [os.path.join(src, "shared")]
    sys.modules["shared"] = pkg
    import git_pull_guard as g
    pulled = []
    g.get_config = lambda config_name: object()
    g.get_repo_groups = lambda c: [{"repo_path": "r", "main_branch": "main", "branches": []}]
    g._pull_repo = lambda info, *checks: (pulled.append(1) or
        {"repo_path": "r", "fetch_ok": True, "pull_ok": True, "errors": []})
    g._resolve_state_path = lambda name: state
    g.time.sleep = lambda s: None
    sys.argv = ["git_pull_guard.py", "--config", cfg]
    codes = [g._main() for _ in range(3)]
    print(json.dumps({"pulled": len(pulled), "codes": codes}), flush=True)
    """
)


def test_pull_guard_does_not_skip_or_kill_itself(tmp_path):
    """H1: the guard's own command line (and its cron shell) contain
    ``git_pull_guard.py --config X``; three ticks must pull three times."""
    cfg = f"cfg_{uuid.uuid4().hex[:8]}"
    out = subprocess.run(
        [sys.executable, "-c", _PULL_GUARD_TICKS, str(_SRC), str(tmp_path / "s.json"),
         cfg, "git_pull_guard.py", "--config", cfg],
        capture_output=True, text=True, timeout=180,
        check=False,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    result = json.loads(out.stdout.strip().splitlines()[-1])
    assert result == {"pulled": 3, "codes": [0, 0, 0]}


def test_pull_guard_counts_and_kills_another_guard(tmp_path, monkeypatch):
    import git_pull_guard as g

    state = tmp_path / "s.json"
    killed: list[int] = []
    pulled: list[int] = []
    monkeypatch.setattr(g, "get_config", lambda config_name: object())
    monkeypatch.setattr(g, "get_repo_groups", lambda c: [{"repo_path": "r"}])
    monkeypatch.setattr(
        g,
        "_pull_repo",
        lambda info, *checks: pulled.append(1)
        or {"repo_path": "r", "fetch_ok": True, "pull_ok": True, "errors": []},
    )
    monkeypatch.setattr(g, "_resolve_state_path", lambda name: state)
    monkeypatch.setattr(g, "_find_guard_pid", lambda name: 4242)
    monkeypatch.setattr(g, "_find_indexer_pid", lambda name: None)
    monkeypatch.setattr(g, "process_start_time", lambda pid: 7.0)
    monkeypatch.setattr(g, "_kill_process", killed.append)
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "argv", ["git_pull_guard.py", "--config", "c"])
    assert [g._main() for _ in range(3)] == [0, 0, 0]
    assert killed == [4242]
    assert pulled == [1]
    assert json.loads(state.read_text(encoding="utf-8"))["consecutive_skips"] == 0


# ── git_pull_guard: H4, no pull under a running indexer ─────────────────────


@pytest.fixture
def pull(tmp_path, monkeypatch, capsys):
    import git_pull_guard as g

    world = {"pulled": 0, "indexer": None, "state": tmp_path / "s.json"}

    def _pull(info, *checks):
        world["pulled"] += 1
        return {"repo_path": "r", "fetch_ok": True, "pull_ok": True, "errors": []}

    monkeypatch.setattr(g, "get_config", lambda config_name: object())
    monkeypatch.setattr(g, "get_repo_groups", lambda c: [{"repo_path": "r"}])
    monkeypatch.setattr(g, "_pull_repo", _pull)
    monkeypatch.setattr(g, "_resolve_state_path", lambda name: world["state"])
    monkeypatch.setattr(g, "_find_guard_pid", lambda name: None)
    monkeypatch.setattr(g, "_find_indexer_pid", lambda name: world["indexer"])
    monkeypatch.setattr(sys, "argv", ["git_pull_guard.py", "--config", "c"])
    world["main"] = g._main
    return world


def test_pull_is_skipped_while_the_indexer_runs(pull, capsys):
    pull["indexer"] = 555
    assert pull["main"]() == 0  # exit 0: the cron chain goes on to refresh_guard
    assert pull["pulled"] == 0
    out = capsys.readouterr().out
    assert "Indexer PID 555" in out and "Skipping the pull" in out


def test_next_tick_pulls_once_the_indexer_is_gone(pull):
    pull["indexer"] = 555
    pull["main"]()
    pull["main"]()
    pull["indexer"] = None
    assert pull["main"]() == 0
    assert pull["pulled"] == 1


def test_indexer_skip_does_not_count_towards_a_guard_kill(pull):
    pull["indexer"] = 555
    for _ in range(5):
        pull["main"]()
    state = json.loads(pull["state"].read_text(encoding="utf-8"))
    assert state["consecutive_skips"] == 0


def test_real_indexer_of_previous_tick_blocks_the_pull(tmp_path):
    """H4 on the real process scan: tick N's index_rag.py is still running;
    the pull guard ticks must not pull and must not touch the indexer."""
    cfg = f"cfg_{uuid.uuid4().hex[:8]}"
    indexer = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)", "index_rag.py", "--config", cfg]
    )
    try:
        deadline = time.monotonic() + 10
        import psutil

        while time.monotonic() < deadline:
            try:
                if psutil.Process(indexer.pid).cmdline():
                    break
            except psutil.Error:
                pass
            time.sleep(0.05)
        out = subprocess.run(
            [sys.executable, "-c", _PULL_GUARD_TICKS, str(_SRC), str(tmp_path / "s.json"),
             cfg, "git_pull_guard.py", "--config", cfg],
            capture_output=True, text=True, timeout=180, check=False,
        )
        assert out.returncode == 0, out.stderr[-2000:]
        assert json.loads(out.stdout.strip().splitlines()[-1]) == {"pulled": 0, "codes": [0, 0, 0]}
        assert indexer.poll() is None
    finally:
        indexer.kill()
        indexer.wait(timeout=30)


# ── H17: refresh_guard waits for a running pull guard ───────────────────────


def test_no_indexer_while_a_pull_guard_runs(guard):
    """H17: tick N's pull guard is still fetching; tick N+1's refresh must not
    start the indexer (the pull would then change the tree under it)."""
    guard["pull_guards"].append(300)
    assert guard["run"]() == 0
    assert guard["started"] == [] and guard["killed"] == []
    state = _state(guard)
    assert state["pull_guard"]["consecutive_skips"] == 1
    assert state["pull_guard"]["pid"] == 300
    assert state["consecutive_skips"] == 0  # the indexer counter is untouched


def test_starts_once_the_pull_guard_is_gone(guard):
    guard["pull_guards"].append(300)
    guard["run"]()
    guard["pull_guards"].remove(300)
    assert guard["run"]() == 0
    assert len(guard["started"]) == 1
    assert "pull_guard" not in _state(guard)


def test_kills_a_hung_pull_guard_on_third_sighting_then_starts(guard):
    guard["pull_guards"].append(300)
    guard["run"]()
    guard["run"]()
    assert guard["killed"] == [] and guard["started"] == []
    guard["run"]()
    assert guard["killed"] == [300]
    assert len(guard["started"]) == 1
    assert "pull_guard" not in _state(guard)


def test_new_pull_guard_restarts_the_pull_count(guard):
    guard["pull_guards"].append(300)
    guard["run"]()
    guard["run"]()
    guard["pull_guards"][:] = [301]  # 300 finished, the next tick's guard runs
    guard["run"]()
    assert guard["killed"] == []
    assert _state(guard)["pull_guard"] == {"consecutive_skips": 1, "pid": 301, "pid_start_time": 1.0}


def test_reused_pid_of_a_pull_guard_is_a_new_guard(guard):
    guard["pull_guards"].append(300)
    guard["run"]()
    guard["run"]()
    guard["start_times"][300] = 42.0
    guard["run"]()
    assert guard["killed"] == []
    assert _state(guard)["pull_guard"]["consecutive_skips"] == 1


def test_no_indexer_when_the_pull_guard_survives_the_kill(guard, monkeypatch):
    guard["pull_guards"].append(300)
    monkeypatch.setattr(rg, "_kill_process", lambda pid: guard["killed"].append(pid))
    for _ in range(3):
        guard["run"]()
    assert guard["killed"] == [300]
    assert guard["started"] == []


def test_after_the_pull_kill_a_running_indexer_is_still_counted(guard):
    """The pull kill does not bypass the indexer rule: a running indexer is
    a first sighting, not a reason to start a second one."""
    guard["pull_guards"].append(300)
    guard["running"].append(100)
    for _ in range(3):
        guard["run"]()
    assert guard["killed"] == [300]
    assert guard["started"] == []
    state = _state(guard)
    assert state["consecutive_skips"] == 1 and state["pid"] == 100


def test_pull_guard_wait_does_not_count_indexer_skips(guard):
    guard["running"].append(100)
    guard["pull_guards"].append(300)
    guard["run"]()
    guard["run"]()
    assert _state(guard)["consecutive_skips"] == 0  # the indexer was not scanned
    guard["pull_guards"].remove(300)
    guard["run"]()
    assert _state(guard)["consecutive_skips"] == 1 and guard["killed"] == []


def test_corrupt_pull_guard_state_is_reset(guard):
    guard["state_path"].write_text('{"consecutive_skips": 0, "pull_guard": 5}', encoding="utf-8")
    guard["pull_guards"].append(300)
    guard["run"]()
    assert _state(guard)["pull_guard"]["consecutive_skips"] == 1


def test_real_pull_guard_scan_ignores_the_refresh_guard_itself():
    assert rg._find_pull_guard_pid(f"cfg_{uuid.uuid4().hex[:8]}") is None


# ── H17: the pull guard rechecks for an indexer right before the pull ───────


@pytest.fixture
def repo_git(monkeypatch):
    import git_pull_guard as g

    calls: list[list[str]] = []

    def _fake_git(cmd, repo_path, timeout=60, binary=False):
        calls.append(list(cmd))
        stdout = "main\n" if cmd[:2] == ["branch", "--show-current"] else ""
        return subprocess.CompletedProcess(["git", *cmd], 0, stdout, "")

    monkeypatch.setattr(g, "_run_git", _fake_git)
    info = {"repo_path": "r", "main_branch": "main", "branches": []}
    return g, info, calls


def _pulled(calls) -> bool:
    return any(c[:1] == ["pull"] for c in calls)


def test_pull_is_skipped_when_an_indexer_started_meanwhile(repo_git):
    g, info, calls = repo_git
    result = g._pull_repo(info, lambda: 777)
    assert not _pulled(calls)
    assert not any(c[:1] == ["status"] or c[:1] == ["stash"] for c in calls)  # tree untouched
    assert result["pull_ok"] is False and result["fetch_ok"] is True
    assert result["pull_skipped"] == "indexer PID 777 running"


def test_pull_runs_when_the_recheck_finds_no_indexer(repo_git):
    g, info, calls = repo_git
    checks: list[int] = []
    result = g._pull_repo(info, lambda: checks.append(1))
    assert _pulled(calls) and result["pull_ok"] is True
    assert checks == [1]
    assert "pull_skipped" not in result


def test_recheck_happens_after_the_slow_fetches(repo_git):
    g, info, calls = repo_git
    order: list[str] = []
    g_run = g._run_git

    def _ordered(cmd, *a, **kw):
        order.append(cmd[0])
        return g_run(cmd, *a, **kw)

    g._run_git = _ordered
    try:
        g._pull_repo(info, lambda: order.append("check"))
    finally:
        g._run_git = g_run
    assert order.index("check") > max(i for i, c in enumerate(order) if c == "fetch")
    assert order.index("check") < order.index("pull")


def test_pull_without_recheck_keeps_the_old_behaviour(repo_git):
    g, info, calls = repo_git
    assert g._pull_repo(info)["pull_ok"] is True
    assert _pulled(calls)


def test_main_passes_an_indexer_recheck(pull, monkeypatch):
    import git_pull_guard as g

    scans = iter([None, 888])  # no indexer at the start, one by the time of the pull
    monkeypatch.setattr(g, "_find_indexer_pid", lambda name: next(scans))
    seen: list = []
    monkeypatch.setattr(
        g,
        "_pull_repo",
        lambda info, check=None: seen.append(check() if check else "none")
        or {"repo_path": "r", "fetch_ok": True, "pull_ok": False, "errors": []},
    )
    assert pull["main"]() == 0
    assert seen == [888]


# ── H17 on real processes: slow fetch, cron chain, refresh guard ────────────

_PULL_TICK = textwrap.dedent(
    """
    import os, subprocess, sys, time, types
    from pathlib import Path
    src, state, events, slow, cfg = sys.argv[1:6]
    sys.path[:0] = [os.path.dirname(src), src]
    pkg = types.ModuleType("shared")  # skip shared/__init__ (indexing stack)
    pkg.__path__ = [os.path.join(src, "shared")]
    sys.modules["shared"] = pkg
    import git_pull_guard as g

    def ev(name, pid=None):
        with open(events, "a", encoding="utf-8") as fh:
            fh.write(f"{time.time():.3f} {name} {pid or os.getpid()}\\n")

    def fake_git(cmd, repo_path, timeout=60, binary=False):
        if cmd[:2] == ["fetch", "--all"] and os.path.exists(slow):
            secs = float(Path(slow).read_text())
            os.remove(slow)  # only the first fetch is slow
            child = subprocess.Popen([sys.executable, "-c", f"import time; time.sleep({secs})"])
            ev("fetch_start", child.pid)
            child.wait()
            ev("fetch_end")
        if cmd[:1] == ["pull"]:
            ev("pull_start")
            time.sleep(0.5)
            ev("pull_end")
        out = "main\\n" if cmd[:2] == ["branch", "--show-current"] else ""
        return subprocess.CompletedProcess(["git", *cmd], 0, out, "")

    g._run_git = fake_git
    g.get_config = lambda config_name: object()
    g.get_repo_groups = lambda c: [{"repo_path": "r", "main_branch": "main", "branches": []}]
    g._resolve_state_path = lambda name: Path(state)
    sys.argv = ["git_pull_guard.py", "--config", cfg]
    sys.exit(g._main())
    """
)

_REFRESH_TICK = textwrap.dedent(
    """
    import os, subprocess, sys
    from pathlib import Path
    src, state, events, secs, cfg = sys.argv[1:6]
    sys.path.insert(0, src)
    import refresh_guard as rg

    code = (
        "import os, sys, time\\n"
        "def ev(n):\\n"
        f"    open({events!r}, 'a', encoding='utf-8').write(f'{{time.time():.3f}} {{n}} {{os.getpid()}}\\\\n')\\n"
        "ev('index_start')\\n"
        f"time.sleep({secs})\\n"
        "ev('index_end')\\n"
    )
    rg._start_indexer = lambda args: subprocess.Popen(
        [sys.executable, "-c", code, "index_rag.py", "--config", cfg])
    rg._resolve_state_path = lambda name: Path(state)
    sys.argv = ["refresh_guard.py", "--config", cfg, "--yes"]
    sys.exit(rg.main())
    """
)


class _Cron:
    """Runs ``pull_tick && refresh_tick`` through a shell, like one cron tick."""

    def __init__(self, tmp_path: Path, index_secs: float = 4.0) -> None:
        self.cfg = f"cfg_{uuid.uuid4().hex[:8]}"
        self.tmp = tmp_path
        self.events = tmp_path / "events.txt"
        self.slow = tmp_path / "slow_fetch"
        (tmp_path / "pull_tick.py").write_text(_PULL_TICK, encoding="utf-8")
        (tmp_path / "refresh_tick.py").write_text(_REFRESH_TICK, encoding="utf-8")
        self.index_secs = index_secs
        self.py = sys.executable if " " not in sys.executable else f'"{sys.executable}"'

    def _args(self, script: str, state: str, extra: str, marker: str) -> str:
        return (
            f'{self.py} {script} "{_SRC}" "{self.tmp / state}" "{self.events}" '
            f'"{extra}" {self.cfg} {marker} --config {self.cfg}'
        )

    def pull_cmd(self) -> str:
        return self._args("pull_tick.py", "pull_state.json", str(self.slow), "git_pull_guard.py")

    def refresh_cmd(self) -> str:
        return self._args("refresh_tick.py", "refresh_state.json", str(self.index_secs), "refresh_guard.py")

    def tick(self) -> subprocess.Popen:
        return subprocess.Popen(
            f"{self.pull_cmd()} && {self.refresh_cmd()}",
            shell=True, cwd=self.tmp, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def read(self) -> list[tuple[float, str, int]]:
        if not self.events.exists():
            return []
        rows = []
        for line in self.events.read_text(encoding="utf-8").splitlines():
            ts, name, pid = line.split()
            rows.append((float(ts), name, int(pid)))
        return rows

    def wait_for(self, name: str, timeout: float = 60.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for row in self.read():
                if row[1] == name:
                    return row
            time.sleep(0.05)
        raise AssertionError(f"event {name} not seen; events: {self.read()}")


def _intervals(rows, start: str, end: str) -> list[tuple[float, float]]:
    starts = [r[0] for r in rows if r[1] == start]
    ends = [r[0] for r in rows if r[1] == end]
    return list(zip(starts, ends + [float("inf")] * (len(starts) - len(ends))))


def _finish(proc: subprocess.Popen, timeout: float = 90.0) -> str:
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        from guard_common import kill_process_tree

        kill_process_tree(proc.pid, lambda _msg: None, timeout=5)
        out, _ = proc.communicate(timeout=30)
    return out or ""


def test_real_cron_slow_fetch_does_not_pull_under_the_indexer(tmp_path):
    """H17 end to end: tick 1's pull guard is stuck in a slow fetch; tick 2's
    pull guard skips and (exit 0, ``&&``) its refresh guard runs. It must not
    start the indexer, so tick 1 pulls with no indexer running and only then
    starts the indexer itself."""
    # The indexer outlasts the fetch, so without the fix tick 2's indexer is
    # still running when tick 1 reaches ``git pull``.
    cron = _Cron(tmp_path, index_secs=10.0)
    cron.slow.write_text("5", encoding="utf-8")
    tick1 = cron.tick()
    tick2 = None
    try:
        cron.wait_for("fetch_start", timeout=60)
        tick2 = cron.tick()
        out2 = _finish(tick2)
        out1 = _finish(tick1)
    finally:
        for proc in (tick1, tick2):
            if proc is not None and proc.poll() is None:
                _finish(proc, timeout=1)
    rows = cron.read()
    pulls = _intervals(rows, "pull_start", "pull_end")
    indexes = _intervals(rows, "index_start", "index_end")
    logs = f"tick1:\n{out1}\ntick2:\n{out2}\nevents: {rows}"
    assert pulls, "tick 1 never pulled\n" + logs
    assert indexes, "no indexer ran\n" + logs
    for p0, p1 in pulls:
        for i0, i1 in indexes:
            assert p1 < i0 or i1 < p0, "pull overlapped a running indexer\n" + logs
    assert "Not starting the indexer under a pull" in out2, logs


def test_real_cron_hung_pull_guard_is_killed_on_third_refresh(tmp_path):
    """Three refresh ticks see the same hung pull guard: two skips, then its
    whole process tree (the guard and its git child) is killed and the
    indexer starts."""
    import psutil

    cron = _Cron(tmp_path, index_secs=0.5)
    cron.slow.write_text("300", encoding="utf-8")
    hung = subprocess.Popen(cron.pull_cmd(), shell=True, cwd=tmp_path,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        git_child = cron.wait_for("fetch_start", timeout=60)[2]
        guard_pid = find_process("git_pull_guard.py", cron.cfg)
        assert guard_pid is not None
        outs = []
        for n in range(3):
            run = subprocess.run(cron.refresh_cmd(), shell=True, cwd=tmp_path,
                                 capture_output=True, text=True, timeout=120, check=False)
            outs.append(run.stdout + run.stderr)
            started = [r for r in cron.read() if r[1] == "index_start"]
            if n < 2:
                assert not started, outs
                assert psutil.pid_exists(git_child)
        assert [r for r in cron.read() if r[1] == "index_end"], outs
        assert "Killing it" in outs[2], outs
        for pid in (guard_pid, git_child):
            assert not _alive(pid), f"{pid} survived: {outs}"
    finally:
        _finish(hung, timeout=1)


def _alive(pid: int) -> bool:
    import psutil

    try:
        return psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False
