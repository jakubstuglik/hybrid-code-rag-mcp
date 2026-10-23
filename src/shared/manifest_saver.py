# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Manifest persistence: compact atomic writes and a throttled background saver.

The indexer keeps the whole manifest (every file with its point IDs) in
memory and persists it periodically, so an interrupted run can resume. On a
large index the classic per-pool rewrite (pretty-printed JSON, written on the
main thread) becomes the dominant serial cost. ``MANIFEST_SAVE_INTERVAL_S``
opts into a cheaper scheme:

* at most one periodic save every N seconds, done by one background thread
  on a cheap shallow snapshot, so the main thread keeps feeding the GPU;
* compact JSON (C encoder) instead of the indented format;
* synchronous saves at the end of a run and when the run fails.

With the default (``0``) every save request writes immediately on the
calling thread, in the indented format, as before. Every write (both modes)
goes to a temp file that is renamed into place, so a crash can never leave
a truncated manifest behind.
"""

from __future__ import annotations

import json
import math
import os
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shared.log import log, log_warn

# Dicts larger than this are encoded item by item so a background encode
# gives the GIL back between items instead of holding it for the whole file.
_CHUNKED_DICT_MIN_ITEMS = 256
_COMPACT_SEPARATORS = (",", ":")


def manifest_save_interval(cfg: Any) -> float:
    """Return ``MANIFEST_SAVE_INTERVAL_S`` from *cfg* as seconds (``0`` = off).

    Missing, ``None``, zero, negative and NaN values mean "off" (the classic
    save-after-every-batch behaviour). A non-numeric value raises
    ``ValueError`` so a typo fails fast instead of silently disabling it.
    """
    raw = getattr(cfg, "MANIFEST_SAVE_INTERVAL_S", 0)
    if raw is None or isinstance(raw, bool):
        return 0.0
    value = float(raw)
    if math.isnan(value) or value <= 0:
        return 0.0
    return value


def encode_manifest_compact(manifest: dict) -> bytes:
    """Encode *manifest* as compact, key-sorted JSON (ASCII bytes).

    The output is identical to ``json.dumps(manifest, sort_keys=True,
    separators=(",", ":"))``. Large nested dicts (the ``files`` map) are
    encoded entry by entry, which keeps each C-encoder call short.
    """
    dumps = json.dumps
    parts: list[str] = ["{"]
    first = True
    for key in sorted(manifest):
        value = manifest[key]
        if not first:
            parts.append(",")
        first = False
        parts.append(dumps(key))
        parts.append(":")
        if isinstance(value, dict) and len(value) >= _CHUNKED_DICT_MIN_ITEMS:
            parts.append("{")
            inner_first = True
            for inner_key in sorted(value):
                if not inner_first:
                    parts.append(",")
                inner_first = False
                parts.append(dumps(inner_key))
                parts.append(":")
                parts.append(
                    dumps(
                        value[inner_key], sort_keys=True, separators=_COMPACT_SEPARATORS
                    )
                )
            parts.append("}")
        else:
            parts.append(dumps(value, sort_keys=True, separators=_COMPACT_SEPARATORS))
    parts.append("}")
    return "".join(parts).encode("ascii")


def _replace_with_retries(tmp: Path, path: Path, retries: int, retry_delay_s: float) -> None:
    attempt = 0
    while True:
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            attempt += 1
            if attempt > retries:
                raise
            time.sleep(retry_delay_s * min(attempt, 10))


def _temp_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")


def remove_stale_temp_files(path: Path) -> int:
    """Delete temp files of *path* left by writers that no longer run.

    A writer killed between creating its temp file and the rename leaves
    ``<name>.<pid>.<thread>.tmp`` behind. Files whose pid is a running
    process are kept (another writer may own them). Returns the number of
    files removed.
    """
    path = Path(path)
    removed = 0
    try:
        candidates = list(path.parent.glob(f"{path.name}.*.*.tmp"))
    except OSError:
        return 0
    for tmp in candidates:
        parts = tmp.name[len(path.name) + 1 :].split(".")
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        pid = int(parts[0])
        if pid == os.getpid() or _pid_running(pid):
            continue
        try:
            tmp.unlink()
            removed += 1
        except OSError:
            pass
    return removed


def _pid_running(pid: int) -> bool:
    try:
        import psutil
    except ImportError:  # pragma: no cover - psutil is a project dependency
        return True
    return psutil.pid_exists(pid)


def read_json_file(
    path: Path,
    *,
    retries: int = 20,
    retry_delay_s: float = 0.05,
) -> Any:
    """Load the JSON file *path*, retrying a transient ``PermissionError``.

    On Windows opening a file fails with ``PermissionError`` for a short
    moment while another process renames a new version into place (see
    :func:`write_json_indented_atomic`) or right after a writer was killed.
    That is retried with the same growing delay as the writer's
    ``os.replace``; other errors (missing file, invalid JSON) are raised at
    once.
    """
    attempt = 0
    while True:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except PermissionError:
            attempt += 1
            if attempt > retries:
                raise
            time.sleep(retry_delay_s * min(attempt, 10))


def write_bytes_atomic(
    path: Path,
    data: bytes,
    *,
    retries: int = 20,
    retry_delay_s: float = 0.05,
    fsync: bool = True,
) -> None:
    """Write *data* to *path* via a temp file in the same dir + ``os.replace``.

    Readers see either the old or the new file, never a partial one. On
    Windows ``os.replace`` fails with ``PermissionError`` while another
    process holds the target open; that is retried with a growing delay.
    The temp file is removed when the write fails.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = _temp_path(path)
    try:
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            if fsync:
                os.fsync(f.fileno())
        _replace_with_retries(tmp, path, retries, retry_delay_s)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def write_json_indented_atomic(
    path: Path,
    obj: Any,
    *,
    retries: int = 20,
    retry_delay_s: float = 0.05,
    fsync: bool = True,
) -> int:
    """Write *obj* as indented, key-sorted JSON via temp file + ``os.replace``.

    The bytes are the same as the classic in-place
    ``json.dump(obj, open(path, "w", encoding="utf-8"), indent=2,
    sort_keys=True)`` (text mode, so platform newlines), streamed to the temp
    file. A kill during the write leaves the previous file intact. Returns
    the size of the written file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = _temp_path(path)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, sort_keys=True)
            f.flush()
            if fsync:
                os.fsync(f.fileno())
        size = tmp.stat().st_size
        _replace_with_retries(tmp, path, retries, retry_delay_s)
        return size
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def write_manifest_file(path: Path, manifest: dict, *, compact: bool) -> int:
    """Persist *manifest* to *path*; return the number of bytes written.

    ``compact=False`` is the classic format (pretty-printed, key-sorted JSON,
    byte-identical to earlier releases). ``compact=True`` writes compact JSON.
    Both are written to a temp file and renamed into place, so a crash never
    leaves a truncated manifest, and both load with ``json.load``.
    """
    path = Path(path)
    remove_stale_temp_files(path)
    if not compact:
        return write_json_indented_atomic(path, manifest)
    data = encode_manifest_compact(manifest)
    write_bytes_atomic(path, data)
    return len(data)


def snapshot_manifest(manifest: dict) -> dict:
    """Return a shallow, point-in-time copy safe to encode on another thread.

    Top-level dicts and lists (``files``, ``repo_commits``, ...) are copied;
    their values are shared. This relies on the indexer contract that a
    ``files`` entry is replaced, never mutated in place, once stored. A
    C-level ``dict()`` copy is atomic under the GIL, so it is consistent even
    while another thread inserts entries.
    """
    snap: dict = {}
    for key, value in list(manifest.items()):
        if isinstance(value, dict):
            snap[key] = dict(value)
        elif isinstance(value, list):
            snap[key] = list(value)
        else:
            snap[key] = value
    return snap


@dataclass
class SaveStats:
    """Counters for one saver (seconds are wall time of ``save_fn``)."""

    sync_count: int = 0
    sync_total_s: float = 0.0
    sync_max_s: float = 0.0
    background_count: int = 0
    background_total_s: float = 0.0
    background_max_s: float = 0.0
    background_errors: int = 0
    skipped: int = 0
    snapshot_total_s: float = 0.0

    def summary(self) -> str:
        return (
            f"sync={self.sync_count} ({self.sync_total_s:.2f}s, max "
            f"{self.sync_max_s:.2f}s), background={self.background_count} "
            f"({self.background_total_s:.2f}s, max {self.background_max_s:.2f}s, "
            f"errors={self.background_errors}), throttled={self.skipped}, "
            f"snapshot={self.snapshot_total_s:.3f}s"
        )


class ManifestSaver:
    """Decide when a manifest is written, and on which thread.

    ``interval_s <= 0``: every :meth:`request` writes synchronously (classic
    behaviour). ``interval_s > 0``: :meth:`request` writes at most once per
    interval, on a single background thread, from a snapshot taken on the
    calling thread; a request is skipped while the previous background write
    is still running. :meth:`save_now` always writes synchronously after the
    background writer is idle. A lock serialises every write, so two writes
    of the same manifest never overlap.
    """

    def __init__(
        self,
        save_fn: Callable[[dict], Any],
        interval_s: float = 0.0,
        *,
        clock: Callable[[], float] = time.monotonic,
        label: str = "manifest",
    ) -> None:
        self._save_fn = save_fn
        self.interval_s = float(interval_s) if interval_s and interval_s > 0 else 0.0
        self._clock = clock
        self._label = label
        self._write_lock = threading.Lock()
        self._executor: ThreadPoolExecutor | None = None
        self._future: Future | None = None
        self._last_save = clock()
        self._closed = False
        self.stats = SaveStats()

    @property
    def background(self) -> bool:
        return self.interval_s > 0

    def request(self, manifest: dict) -> bool:
        """Periodic save point. Return True when a save was done or queued."""
        if manifest is None:
            return True
        if not self.background:
            self._write(manifest, background=False)
            return True
        self._collect_background()
        if self._future is not None:
            self.stats.skipped += 1
            return False  # single writer: previous save still running
        if self._clock() - self._last_save < self.interval_s:
            self.stats.skipped += 1
            return False
        snap = self._snapshot(manifest)
        self._last_save = self._clock()
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=1, thread_name_prefix=f"{self._label}-save"
            )
        self._future = self._executor.submit(self._write, snap, background=True)
        return True

    def save_now(self, manifest: dict) -> None:
        """Write synchronously (end of run, error path). Raises on failure."""
        if manifest is None:
            return
        self.wait()
        data = self._snapshot(manifest) if self.background else manifest
        self._write(data, background=False)
        self._last_save = self._clock()

    def wait(self) -> None:
        """Block until the background writer is idle (errors are logged)."""
        future = self._future
        if future is None:
            return
        try:
            future.result()
        except Exception as exc:  # noqa: BLE001 - logged, next save retries
            self.stats.background_errors += 1
            log_warn(f"[{self._label}] background save failed: {exc}")
        finally:
            self._future = None

    def close(self) -> None:
        """Wait for a pending write and stop the background thread."""
        if self._closed:
            return
        self._closed = True
        self.wait()
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None

    def _collect_background(self) -> None:
        if self._future is not None and self._future.done():
            self.wait()

    def _snapshot(self, manifest: dict) -> dict:
        t0 = time.perf_counter()
        snap = snapshot_manifest(manifest)
        self.stats.snapshot_total_s += time.perf_counter() - t0
        return snap

    def _write(self, manifest: dict, *, background: bool) -> None:
        with self._write_lock:
            t0 = time.perf_counter()
            self._save_fn(manifest)
            elapsed = time.perf_counter() - t0
        st = self.stats
        if background:
            st.background_count += 1
            st.background_total_s += elapsed
            st.background_max_s = max(st.background_max_s, elapsed)
        else:
            st.sync_count += 1
            st.sync_total_s += elapsed
            st.sync_max_s = max(st.sync_max_s, elapsed)

    def log_summary(self) -> None:
        mode = f"interval={self.interval_s:g}s" if self.background else "every batch"
        log(f"[{self._label}] saves ({mode}): {self.stats.summary()}")
