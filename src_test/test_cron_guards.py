# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Decision logic of ``refresh_guard.py`` and ``git_pull_guard.py``.

Regression tests for the formal model of the cron path:

* H1  git_pull_guard counted itself / its cron shell, skipped, then killed itself;
* H2  two refresh_guard runs could both start an indexer (scan and start not atomic);
* H3  the skip counter was not tied to a pid, so a fresh run was killed early;
* H3b the kill hit only a wrapper process and a second indexer was started.
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
    world = {"running": [], "start_times": {}, "started": [], "killed": []}

    def _scan(config_name):
        return min(world["running"]) if world["running"] else None

    def _start(args):
        world["started"].append(list(args))
        return _FakeProc(0)

    def _kill(pid):
        world["killed"].append(pid)
        if pid in world["running"]:
            world["running"].remove(pid)

    monkeypatch.setattr(rg, "_resolve_state_path", lambda name: state_path)
    monkeypatch.setattr(rg, "_find_indexer_pid", _scan)
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
    g._pull_repo = lambda info: (pulled.append(1) or
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
        lambda info: pulled.append(1)
        or {"repo_path": "r", "fetch_ok": True, "pull_ok": True, "errors": []},
    )
    monkeypatch.setattr(g, "_resolve_state_path", lambda name: state)
    monkeypatch.setattr(g, "_find_guard_pid", lambda name: 4242)
    monkeypatch.setattr(g, "process_start_time", lambda pid: 7.0)
    monkeypatch.setattr(g, "_kill_process", killed.append)
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "argv", ["git_pull_guard.py", "--config", "c"])
    assert [g._main() for _ in range(3)] == [0, 0, 0]
    assert killed == [4242]
    assert pulled == [1]
    assert json.loads(state.read_text(encoding="utf-8"))["consecutive_skips"] == 0
