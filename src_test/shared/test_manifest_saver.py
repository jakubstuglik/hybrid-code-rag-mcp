# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for ``shared.manifest_saver`` (encoding, atomic writes, saver)."""

from __future__ import annotations

import json
import os
import threading
import time
import types
import uuid
from pathlib import Path

import pytest

from shared import manifest_saver as ms
from shared.manifest_saver import (
    ManifestSaver,
    encode_manifest_compact,
    manifest_save_interval,
    snapshot_manifest,
    write_bytes_atomic,
    write_manifest_file,
)


def _manifest(n_files: int, ids_per_file: int = 3) -> dict:
    files = {}
    for i in range(n_files):
        key = f"proj/dir{i % 7}/f{i:05d}.c"
        files[key] = {
            "file_path": key,
            "mtime": 1_700_000_000 + i,
            "hash": f"{i:064x}",
            "vector_ids": [
                str(uuid.uuid5(uuid.NAMESPACE_URL, f"{key}:{j}"))
                for j in range(ids_per_file)
            ],
        }
    return {
        "files": files,
        "repo_commits": {"proj": "a" * 40},
        "index_run": {"mode": "full", "at": "2026-01-01T00:00:00"},
        "tombstones": ["x", "y"],
    }


def _reference_compact(m) -> bytes:
    return json.dumps(m, sort_keys=True, separators=(",", ":")).encode("ascii")


# ── manifest_save_interval ─────────────────────────────────────────


class TestInterval:
    @pytest.mark.parametrize("raw", [None, 0, 0.0, -5, "0", float("nan"), True, False])
    def test_off_values(self, raw):
        assert (
            manifest_save_interval(types.SimpleNamespace(MANIFEST_SAVE_INTERVAL_S=raw))
            == 0.0
        )

    def test_missing_attribute_is_off(self):
        assert manifest_save_interval(types.SimpleNamespace()) == 0.0

    @pytest.mark.parametrize(
        "raw, expected", [(60, 60.0), ("30", 30.0), (2.5, 2.5), ("0.25", 0.25)]
    )
    def test_positive_values(self, raw, expected):
        assert (
            manifest_save_interval(types.SimpleNamespace(MANIFEST_SAVE_INTERVAL_S=raw))
            == expected
        )

    @pytest.mark.parametrize("raw", ["soon", "", [60]])
    def test_non_numeric_fails_fast(self, raw):
        with pytest.raises((ValueError, TypeError)):
            manifest_save_interval(types.SimpleNamespace(MANIFEST_SAVE_INTERVAL_S=raw))


# ── encode_manifest_compact ────────────────────────────────────────


class TestEncodeCompact:
    @pytest.mark.parametrize("n", [0, 1, 255, 256, 1000])
    def test_matches_json_dumps(self, n):
        m = _manifest(n)
        assert encode_manifest_compact(m) == _reference_compact(m)

    def test_empty_manifest(self):
        assert encode_manifest_compact({}) == b"{}"

    def test_non_ascii_keys_are_escaped(self):
        m = {
            "files": {
                f"proj/zażółć_{i}.c": {"hash": "ą", "vector_ids": []}
                for i in range(300)
            }
        }
        out = encode_manifest_compact(m)
        assert out == _reference_compact(m)
        out.decode("ascii")  # pure ASCII
        assert json.loads(out) == m

    def test_mixed_value_types(self):
        m = {"b": [1, 2, {"z": 1, "a": None}], "a": 1.5, "c": None, "d": "s", "e": True}
        assert encode_manifest_compact(m) == _reference_compact(m)

    def test_large_nested_non_files_dict(self):
        m = {"other": {f"k{i}": {"v": i} for i in range(400)}, "files": {}}
        assert encode_manifest_compact(m) == _reference_compact(m)

    def test_key_order_independent_of_insertion(self):
        a = {"files": {f"k{i}": {"x": i} for i in range(300)}}
        b = {"files": dict(reversed(list(a["files"].items())))}
        assert encode_manifest_compact(a) == encode_manifest_compact(b)


# ── write_bytes_atomic / write_manifest_file ──────────────────────


def _tmp_leftovers(directory: Path) -> list[str]:
    return [p.name for p in directory.iterdir() if p.name.endswith(".tmp")]


class TestAtomicWrite:
    def test_creates_parent_and_writes(self, tmp_path):
        target = tmp_path / "a" / "b" / "m.json"
        write_bytes_atomic(target, b"{}")
        assert target.read_bytes() == b"{}"
        assert _tmp_leftovers(target.parent) == []

    def test_replaces_existing(self, tmp_path):
        target = tmp_path / "m.json"
        target.write_bytes(b"old")
        write_bytes_atomic(target, b"new", fsync=False)
        assert target.read_bytes() == b"new"

    def test_failed_write_keeps_old_file_and_removes_temp(self, tmp_path, monkeypatch):
        target = tmp_path / "m.json"
        target.write_bytes(b"old")

        class _Boom:
            def __init__(self, *a, **k):
                self._f = open(*a, **k)  # noqa: SIM115 - wrapped file

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                self._f.close()

            def write(self, data):
                self._f.write(data[:3])
                raise OSError("disk full")

            def flush(self):
                pass

            def fileno(self):
                return self._f.fileno()

        monkeypatch.setattr(ms, "open", _Boom, raising=False)
        with pytest.raises(OSError, match="disk full"):
            write_bytes_atomic(target, b"new-content")
        assert target.read_bytes() == b"old"
        assert _tmp_leftovers(tmp_path) == []

    def test_permission_error_on_replace_is_retried(self, tmp_path, monkeypatch):
        target = tmp_path / "m.json"
        real_replace = os.replace
        calls = {"n": 0}

        def _flaky(src, dst):
            calls["n"] += 1
            if calls["n"] < 3:
                raise PermissionError("target busy")
            real_replace(src, dst)

        monkeypatch.setattr(ms.os, "replace", _flaky)
        monkeypatch.setattr(ms.time, "sleep", lambda s: None)
        write_bytes_atomic(target, b"data")
        assert calls["n"] == 3
        assert target.read_bytes() == b"data"
        assert _tmp_leftovers(tmp_path) == []

    def test_temp_cleanup_failure_does_not_mask_error(self, tmp_path, monkeypatch):
        target = tmp_path / "m.json"

        def _always(src, dst):
            raise PermissionError("locked")

        def _no_unlink(self, *a, **k):
            raise OSError("still open")

        monkeypatch.setattr(ms.os, "replace", _always)
        monkeypatch.setattr(ms.time, "sleep", lambda s: None)
        monkeypatch.setattr(ms.Path, "unlink", _no_unlink)
        with pytest.raises(PermissionError):
            write_bytes_atomic(target, b"new", retries=0)
        assert not target.exists()

    def test_retries_exhausted_raises_and_cleans_up(self, tmp_path, monkeypatch):
        target = tmp_path / "m.json"
        target.write_bytes(b"old")

        def _always(src, dst):
            raise PermissionError("locked")

        monkeypatch.setattr(ms.os, "replace", _always)
        monkeypatch.setattr(ms.time, "sleep", lambda s: None)
        with pytest.raises(PermissionError):
            write_bytes_atomic(target, b"new", retries=2)
        assert target.read_bytes() == b"old"
        assert _tmp_leftovers(tmp_path) == []


class TestWriteManifestFile:
    def test_classic_format_is_byte_identical_to_previous_code(self, tmp_path):
        m = _manifest(20)
        ref = tmp_path / "ref.json"
        with open(ref, "w", encoding="utf-8") as f:  # pre-change save_manifest body
            json.dump(m, f, indent=2, sort_keys=True)
        out = tmp_path / "out.json"
        size = write_manifest_file(out, m, compact=False)
        assert out.read_bytes() == ref.read_bytes()
        assert size == out.stat().st_size

    def test_compact_round_trips(self, tmp_path):
        m = _manifest(300)
        out = tmp_path / "sub" / "m.json"
        size = write_manifest_file(out, m, compact=True)
        assert json.loads(out.read_text(encoding="utf-8")) == m
        assert size == out.stat().st_size
        assert b"\n" not in out.read_bytes()

    def test_compact_smaller_than_classic(self, tmp_path):
        m = _manifest(50)
        a = write_manifest_file(tmp_path / "a.json", m, compact=False)
        b = write_manifest_file(tmp_path / "b.json", m, compact=True)
        assert b < a

    def test_compact_overwrites_classic(self, tmp_path):
        out = tmp_path / "m.json"
        write_manifest_file(out, {"files": {"a": {}}}, compact=False)
        write_manifest_file(out, {"files": {"b": {}}}, compact=True)
        assert json.loads(out.read_text()) == {"files": {"b": {}}}


# ── snapshot_manifest ─────────────────────────────────────────────


class TestSnapshot:
    def test_top_level_containers_are_copied(self):
        m = _manifest(5)
        snap = snapshot_manifest(m)
        m["files"]["new"] = {"vector_ids": []}
        del m["files"]["proj/dir0/f00000.c"]
        m["tombstones"].append("z")
        m["repo_commits"]["proj"] = "b" * 40
        m["index_run"] = "replaced"
        assert "new" not in snap["files"]
        assert "proj/dir0/f00000.c" in snap["files"]
        assert snap["tombstones"] == ["x", "y"]
        assert snap["repo_commits"]["proj"] == "a" * 40
        assert snap["index_run"]["mode"] == "full"

    def test_entries_are_shared_not_copied(self):
        m = _manifest(3)
        snap = snapshot_manifest(m)
        key = next(iter(m["files"]))
        assert snap["files"][key] is m["files"][key]

    def test_empty(self):
        assert snapshot_manifest({}) == {}

    def test_scalars_are_kept(self):
        m = {"files": {}, "version": "0.13.0", "count": 3, "none": None}
        assert snapshot_manifest(m) == m

    def test_concurrent_inserts_never_break_snapshot(self):
        m = {"files": {}}
        stop = threading.Event()

        def _writer():
            i = 0
            while not stop.is_set():
                m["files"][f"k{i}"] = {"vector_ids": [str(i)]}
                m["files"].pop(f"k{i - 500}", None)  # bounded size, keeps churning
                i += 1

        th = threading.Thread(target=_writer)
        th.start()
        try:
            for _ in range(200):
                snap = snapshot_manifest(m)
                encode_manifest_compact(snap)  # never "changed size during iteration"
        finally:
            stop.set()
            th.join()


# ── ManifestSaver ─────────────────────────────────────────────────


class _Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class _Recorder:
    """save_fn that records copies, threads and overlap."""

    def __init__(self, delay: float = 0.0, gate: threading.Event | None = None):
        self.saved: list[dict] = []
        self.threads: list[str] = []
        self.active = 0
        self.max_active = 0
        self._lock = threading.Lock()
        self.delay = delay
        self.gate = gate
        self.started = threading.Event()

    def __call__(self, m):
        with self._lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        self.started.set()
        try:
            if self.gate is not None:
                assert self.gate.wait(5)
            if self.delay:
                time.sleep(self.delay)
            self.saved.append(json.loads(json.dumps(m)))
            self.threads.append(threading.current_thread().name)
        finally:
            with self._lock:
                self.active -= 1


class TestSaverDefault:
    def test_every_request_saves_synchronously(self):
        rec = _Recorder()
        saver = ManifestSaver(rec)
        assert not saver.background
        m = {"files": {}}
        for i in range(5):
            m["files"][f"k{i}"] = {}
            assert saver.request(m) is True
            assert len(rec.saved) == i + 1  # written before request returns
        assert set(rec.threads) == {threading.current_thread().name}
        saver.close()
        assert saver.stats.sync_count == 5 and saver.stats.background_count == 0

    def test_default_passes_live_object_not_snapshot(self):
        seen = []
        saver = ManifestSaver(seen.append)
        m = {"files": {}}
        saver.request(m)
        saver.save_now(m)
        assert seen[0] is m and seen[1] is m
        assert saver._executor is None  # no background thread in default mode

    @pytest.mark.parametrize("interval", [0, -1, None])
    def test_non_positive_interval_is_default(self, interval):
        assert ManifestSaver(lambda m: None, interval_s=interval).background is False

    def test_errors_propagate_in_default_mode(self):
        def _boom(m):
            raise OSError("disk full")

        saver = ManifestSaver(_boom)
        with pytest.raises(OSError):
            saver.request({"files": {}})

    def test_none_manifest_is_ignored(self):
        rec = _Recorder()
        saver = ManifestSaver(rec, interval_s=5)
        assert saver.request(None) is True
        saver.save_now(None)
        saver.close()
        assert rec.saved == []


class TestSaverInterval:
    def test_throttles_by_interval(self):
        clock = _Clock()
        rec = _Recorder()
        saver = ManifestSaver(rec, interval_s=60, clock=clock)
        m = {"files": {"a": {}}}
        assert saver.request(m) is False  # interval starts at construction
        clock.now += 59.9
        assert saver.request(m) is False
        clock.now += 0.2
        assert saver.request(m) is True
        saver.wait()
        assert saver.request(m) is False  # just saved
        clock.now += 60
        assert saver.request(m) is True
        saver.close()
        assert len(rec.saved) == 2
        assert all(t.startswith("manifest-save") for t in rec.threads)
        assert saver.stats.background_count == 2
        assert saver.stats.skipped == 3

    def test_skips_while_writer_busy_single_writer(self):
        clock = _Clock()
        gate = threading.Event()
        rec = _Recorder(gate=gate)
        saver = ManifestSaver(rec, interval_s=1, clock=clock)
        m = {"files": {}}
        clock.now += 2
        assert saver.request(m) is True
        assert rec.started.wait(5)
        for _ in range(5):
            clock.now += 10
            assert saver.request(m) is False  # previous write still running
        gate.set()
        saver.wait()
        clock.now += 10
        assert saver.request(m) is True
        saver.close()
        assert rec.max_active == 1
        assert len(rec.saved) == 2

    def test_snapshot_taken_at_request_time(self):
        clock = _Clock()
        gate = threading.Event()
        rec = _Recorder(gate=gate)
        saver = ManifestSaver(rec, interval_s=1, clock=clock)
        m = {"files": {"a": {"vector_ids": ["1"]}}}
        clock.now += 5
        assert saver.request(m)
        m["files"]["b"] = {"vector_ids": ["2"]}  # main thread keeps going
        del m["files"]["a"]
        gate.set()
        saver.close()
        assert rec.saved == [{"files": {"a": {"vector_ids": ["1"]}}}]

    def test_save_now_waits_for_background_and_writes_latest(self):
        clock = _Clock()
        rec = _Recorder(delay=0.05)
        saver = ManifestSaver(rec, interval_s=1, clock=clock)
        m = {"files": {"a": {}}}
        clock.now += 5
        saver.request(m)
        m["files"]["b"] = {}
        saver.save_now(m)
        saver.close()
        assert rec.max_active == 1
        assert [sorted(s["files"]) for s in rec.saved] == [["a"], ["a", "b"]]
        assert rec.threads[-1] == threading.current_thread().name
        assert saver.stats.sync_count == 1 and saver.stats.background_count == 1

    def test_save_now_resets_interval(self):
        clock = _Clock()
        rec = _Recorder()
        saver = ManifestSaver(rec, interval_s=60, clock=clock)
        clock.now += 100
        saver.save_now({"files": {}})
        assert saver.request({"files": {}}) is False
        saver.close()

    def test_background_error_is_logged_and_next_save_works(self, monkeypatch):
        warnings = []
        monkeypatch.setattr(ms, "log_warn", warnings.append)
        clock = _Clock()
        calls = {"n": 0}

        def _flaky(m):
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError("disk full")

        saver = ManifestSaver(_flaky, interval_s=1, clock=clock)
        clock.now += 5
        assert saver.request({"files": {}})
        saver.wait()
        assert saver.stats.background_errors == 1
        assert any("disk full" in w for w in warnings)
        clock.now += 5
        assert saver.request({"files": {}})
        saver.close()
        assert calls["n"] == 2

    def test_save_now_error_propagates(self):
        def _boom(m):
            raise OSError("read-only")

        saver = ManifestSaver(_boom, interval_s=10)
        with pytest.raises(OSError):
            saver.save_now({"files": {}})
        saver.close()

    def test_close_is_idempotent_and_waits(self):
        clock = _Clock()
        rec = _Recorder(delay=0.05)
        saver = ManifestSaver(rec, interval_s=1, clock=clock)
        clock.now += 5
        saver.request({"files": {}})
        saver.close()
        saver.close()
        assert len(rec.saved) == 1
        assert saver._executor is None

    def test_stress_no_concurrent_writers(self):
        rec = _Recorder(delay=0.002)
        saver = ManifestSaver(rec, interval_s=1e-9)
        m = {"files": {}}
        for i in range(300):
            m["files"][f"k{i}"] = {"vector_ids": [str(i)]}
            saver.request(m)
            if i % 50 == 0:
                saver.save_now(m)
        saver.save_now(m)
        saver.close()
        assert rec.max_active == 1
        assert len(rec.saved[-1]["files"]) == 300
        # every save is a consistent prefix of the insertion order
        for s in rec.saved:
            n = len(s["files"])
            assert sorted(s["files"]) == sorted(f"k{i}" for i in range(n))

    def test_log_summary_mentions_mode(self, monkeypatch):
        lines = []
        monkeypatch.setattr(ms, "log", lines.append)
        ManifestSaver(lambda m: None, interval_s=60, label="x").log_summary()
        ManifestSaver(lambda m: None).log_summary()
        assert "interval=60s" in lines[0] and "every batch" in lines[1]
