# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Classic (indented) manifest saves are atomic too (``MANIFEST_SAVE_INTERVAL_S = 0``).

Before, the default mode rewrote the manifest in place; a kill inside
``json.dump`` left truncated JSON and every later run died in
``load_manifest``. The bytes on disk must stay exactly the classic format.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from shared import manifest_saver as ms
from shared.manifest_saver import (
    read_json_file,
    remove_stale_temp_files,
    write_json_indented_atomic,
    write_manifest_file,
)

_SRC = Path(__file__).resolve().parents[2] / "src"


def _classic_bytes(tmp_path: Path, obj) -> bytes:
    ref = tmp_path / "classic_reference.json"
    with open(ref, "w", encoding="utf-8") as f:  # the pre-change write
        json.dump(obj, f, indent=2, sort_keys=True)
    data = ref.read_bytes()
    ref.unlink()
    return data


def _leftovers(directory: Path) -> list[str]:
    return sorted(p.name for p in directory.iterdir() if p.name.endswith(".tmp"))


@pytest.mark.parametrize(
    "obj",
    [
        {},
        {"files": {}},
        {"files": {"zażółć/ü.c": {"hash": "ą", "vector_ids": ["x"]}}},
        {"files": {f"k{i}": {"mtime": i + 0.5, "e": None, "t": True} for i in range(50)}},
        {"text": "line1\nline2\r\n", "list": [1, [2, {"b": 1, "a": 2}]]},
    ],
)
def test_indented_bytes_identical_to_classic(tmp_path, obj):
    out = tmp_path / "m.json"
    size = write_manifest_file(out, obj, compact=False)
    assert out.read_bytes() == _classic_bytes(tmp_path, obj)
    assert size == out.stat().st_size
    assert _leftovers(tmp_path) == []


def test_kill_inside_dump_keeps_previous_manifest(tmp_path, monkeypatch):
    out = tmp_path / "m.json"
    write_manifest_file(out, {"files": {"old": {}}}, compact=False)
    before = out.read_bytes()
    real_dump = json.dump

    def _dump_then_die(obj, fp, **kw):
        fp.write('{\n  "files": {\n    "new')
        raise KeyboardInterrupt()  # BaseException, like a signal

    monkeypatch.setattr(ms.json, "dump", _dump_then_die)
    with pytest.raises(KeyboardInterrupt):
        write_manifest_file(out, {"files": {"new": {}}}, compact=False)
    monkeypatch.setattr(ms.json, "dump", real_dump)
    assert out.read_bytes() == before
    assert json.loads(out.read_text(encoding="utf-8")) == {"files": {"old": {}}}
    assert _leftovers(tmp_path) == []


def test_permission_error_on_replace_is_retried(tmp_path, monkeypatch):
    out = tmp_path / "m.json"
    real_replace = os.replace
    calls = {"n": 0}

    def _flaky(src, dst):
        calls["n"] += 1
        if calls["n"] < 3:
            raise PermissionError("held by a reader")
        real_replace(src, dst)

    monkeypatch.setattr(ms.os, "replace", _flaky)
    monkeypatch.setattr(ms.time, "sleep", lambda s: None)
    write_json_indented_atomic(out, {"a": 1})
    assert calls["n"] == 3
    assert json.loads(out.read_text(encoding="utf-8")) == {"a": 1}


def test_replace_retries_exhausted_keeps_old_and_cleans_up(tmp_path, monkeypatch):
    out = tmp_path / "m.json"
    out.write_text('{"old": 1}', encoding="utf-8")

    def _always(src, dst):
        raise PermissionError("locked")

    monkeypatch.setattr(ms.os, "replace", _always)
    monkeypatch.setattr(ms.time, "sleep", lambda s: None)
    with pytest.raises(PermissionError):
        write_json_indented_atomic(out, {"new": 1}, retries=1)
    assert json.loads(out.read_text(encoding="utf-8")) == {"old": 1}
    assert _leftovers(tmp_path) == []


def test_unserialisable_value_keeps_old_file(tmp_path):
    out = tmp_path / "m.json"
    write_manifest_file(out, {"a": 1}, compact=False)
    with pytest.raises(TypeError):
        write_manifest_file(out, {"a": object()}, compact=False)
    assert json.loads(out.read_text(encoding="utf-8")) == {"a": 1}
    assert _leftovers(tmp_path) == []


# ── stale temp files ─────────────────────────────────────────────────────────


def _dead_pid() -> int:
    import psutil

    pid = 999_999
    while psutil.pid_exists(pid):
        pid += 1
    return pid


def test_stale_temp_of_dead_writer_is_removed(tmp_path):
    target = tmp_path / "index_manifest.json"
    dead = tmp_path / f"index_manifest.json.{_dead_pid()}.123.tmp"
    mine = tmp_path / f"index_manifest.json.{os.getpid()}.456.tmp"
    other = tmp_path / "index_manifest_branch_x.json.1.2.tmp"
    odd = tmp_path / "index_manifest.json.abc.1.tmp"
    for p in (dead, mine, other, odd):
        p.write_text("{", encoding="utf-8")
    assert remove_stale_temp_files(target) == 1
    assert not dead.exists()
    assert mine.exists() and other.exists() and odd.exists()


def test_stale_temp_is_removed_on_next_save(tmp_path):
    target = tmp_path / "m.json"
    stale = tmp_path / f"m.json.{_dead_pid()}.1.tmp"
    stale.write_text("{ torn", encoding="utf-8")
    write_manifest_file(target, {"a": 1}, compact=False)
    assert not stale.exists()


def test_stale_cleanup_in_missing_dir_is_harmless(tmp_path):
    assert remove_stale_temp_files(tmp_path / "nope" / "m.json") == 0


# ── real hard kill of a writer process ──────────────────────────────────────


_WRITER = textwrap.dedent(
    """
    import os, sys, types
    sys.path.insert(0, sys.argv[1])
    # Bare package: skip shared/__init__ (it loads the indexing stack).
    pkg = types.ModuleType("shared")
    pkg.__path__ = [os.path.join(sys.argv[1], "shared")]
    sys.modules["shared"] = pkg
    from shared.manifest_saver import write_manifest_file
    big = {"files": {f"src/f{i}.c": {"file_path": f"src/f{i}.c", "hash": "x" * 64,
            "mtime": i, "vector_ids": [f"{i}-{j}-" + "0" * 30 for j in range(8)]}
            for i in range(20000)}}
    target = sys.argv[2]
    print("ready", flush=True)
    while True:
        write_manifest_file(target, big, compact=False)
    """
)


@pytest.mark.parametrize("delay_s", [0.3, 0.9, 1.7])
def test_hard_kill_during_classic_save_leaves_loadable_manifest(tmp_path, delay_s):
    target = tmp_path / "index_manifest.json"
    target.write_text('{"files": {}}', encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-c", _WRITER, str(_SRC), str(target)],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert proc.stdout.readline().strip() == "ready"
        time.sleep(delay_s)
    finally:
        proc.kill()  # SIGKILL / TerminateProcess
        proc.wait(timeout=30)
        proc.stdout.close()
    # On Windows the file can be locked for a moment after the kill; the
    # loader retries that (see test_read_json_file_retries_permission_error).
    data = read_json_file(target)
    assert set(data) == {"files"}
    assert len(data["files"]) in (0, 20000)


# ── reading while a writer replaces the file ────────────────────────────────


def test_read_json_file_retries_permission_error(tmp_path, monkeypatch):
    target = tmp_path / "m.json"
    target.write_text('{"a": 1}', encoding="utf-8")
    real_open = open  # the builtin; the patch only shadows it in manifest_saver
    calls = {"n": 0}
    delays: list[float] = []

    def _locked_twice(path, *args, **kwargs):
        if Path(path) == target:
            calls["n"] += 1
            if calls["n"] < 3:
                raise PermissionError(13, "Permission denied", str(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(ms, "open", _locked_twice, raising=False)
    monkeypatch.setattr(ms.time, "sleep", delays.append)
    assert read_json_file(target) == {"a": 1}
    assert calls["n"] == 3
    assert delays == [0.05, 0.1]


def test_read_json_file_gives_up_after_retries(tmp_path, monkeypatch):
    target = tmp_path / "m.json"
    target.write_text('{"a": 1}', encoding="utf-8")
    calls = {"n": 0}

    def _always_locked(path, *args, **kwargs):
        calls["n"] += 1
        raise PermissionError(13, "Permission denied", str(path))

    monkeypatch.setattr(ms, "open", _always_locked, raising=False)
    monkeypatch.setattr(ms.time, "sleep", lambda s: None)
    with pytest.raises(PermissionError):
        read_json_file(target, retries=2)
    assert calls["n"] == 3


def test_read_json_file_zero_retries_raises_at_once(tmp_path, monkeypatch):
    target = tmp_path / "m.json"
    target.write_text("{}", encoding="utf-8")

    def _locked(path, *args, **kwargs):
        raise PermissionError(13, "Permission denied", str(path))

    monkeypatch.setattr(ms, "open", _locked, raising=False)
    monkeypatch.setattr(ms.time, "sleep", lambda s: pytest.fail("slept"))
    with pytest.raises(PermissionError):
        read_json_file(target, retries=0)


def test_read_json_file_does_not_retry_other_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(ms.time, "sleep", lambda s: pytest.fail("slept"))
    with pytest.raises(FileNotFoundError):
        read_json_file(tmp_path / "missing.json")
    torn = tmp_path / "torn.json"
    torn.write_text('{"files": {', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        read_json_file(torn)


@pytest.mark.parametrize("text", ["{}", "[]", "null", '{"zażółć": "ü"}'])
def test_read_json_file_returns_any_json_value(tmp_path, text):
    target = tmp_path / "m.json"
    target.write_text(text, encoding="utf-8")
    assert read_json_file(target) == json.loads(text)


def test_reader_never_sees_a_partial_file_while_writer_replaces(tmp_path):
    """A reader in this process polls while a writer process keeps replacing
    the file: every read returns a complete manifest (no PermissionError
    escapes, no torn JSON)."""
    target = tmp_path / "index_manifest.json"
    target.write_text('{"files": {}}', encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-c", _WRITER, str(_SRC), str(target)],
        stdout=subprocess.PIPE,
        text=True,
    )
    reads = 0
    try:
        assert proc.stdout.readline().strip() == "ready"
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            data = read_json_file(target)
            assert len(data["files"]) in (0, 20000)
            reads += 1
    finally:
        proc.kill()
        proc.wait(timeout=30)
        proc.stdout.close()
    assert reads > 0
