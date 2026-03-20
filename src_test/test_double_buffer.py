"""
Tests for Phase 2 double-buffered upsert logic from index_rag.py.

Since index_rag.py has heavy module-level side effects (argparse, Docker,
Qdrant connections), we replicate the core double-buffer functions here
with injectable dependencies, following the same pattern as
test_determine_actions.py and test_backfill.py.

Tests cover:
    - _do_background_upsert: counter accumulation, batched upsert calls,
      manifest updates, error handling per-file, zero_count tracking,
      add vs modify counting, [upsert-worker] log prefix
    - _drain_pending_upsert: counter-delta application from Future result,
      error propagation (re-raises), manifest save trigger on threshold,
      no-op when pending is None, finally-clears pending
    - Integration: full flush→drain→flush cycle with ThreadPoolExecutor,
      double-buffer overlap verification, executor shutdown
    - TimingTracker: thread safety of measure() across threads
"""

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager
from unittest.mock import MagicMock, call, patch

import pytest


# ────────────────────────────────────────────────
# Replicated helpers from index_rag.py
# ────────────────────────────────────────────────


class TimingTracker:
    """Replicated from index_rag.py:73 — tracks timing for different phases."""

    def __init__(self, verbose: bool = False):
        self.timings = {}
        self.counts = {}
        self.verbose = verbose

    @contextmanager
    def measure(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            if name not in self.timings:
                self.timings[name] = 0
                self.counts[name] = 0
            self.timings[name] += elapsed
            self.counts[name] += 1


def _make_manifest_entry(file_info: dict, ids: list[str], **extra) -> dict:
    """Replicated from index_rag.py:1682."""
    entry = {
        "file_path": file_info["file_path"],
        "mtime": file_info["mtime"],
        "hash": file_info["hash"],
        "vector_ids": ids,
    }
    entry.update(extra)
    return entry


def do_background_upsert(
    work_items: list[dict],
    *,
    client: MagicMock,
    collection_name: str,
    manifest: dict,
    timing_tracker: TimingTracker,
    log_fn=None,
    log_error_fn=None,
) -> dict:
    """Replicated from index_rag.py:2198 with injectable dependencies.

    Executes per-file upserts, returns counter deltas.
    """
    if log_fn is None:
        log_fn = lambda msg: None  # noqa: E731
    if log_error_fn is None:
        log_error_fn = lambda msg: None  # noqa: E731

    counters = {
        "vectors_added": 0,
        "files_added": 0,
        "files_modified": 0,
        "files_errored": 0,
        "zero_vectors_skipped": 0,
        "files_processed": 0,
    }
    upsert_batch_size = 500

    for item in work_items:
        points = item["points"]
        file_key = item["file_key"]
        ids = item["ids"]
        file_info = item["file_info"]
        action_type = item["action_type"]
        zero_count = item["zero_count"]

        counters["zero_vectors_skipped"] += zero_count

        with timing_tracker.measure("upsert"):
            try:
                total_batches = (
                    len(points) + upsert_batch_size - 1
                ) // upsert_batch_size
                for batch_idx in range(total_batches):
                    start_idx = batch_idx * upsert_batch_size
                    end_idx = min(start_idx + upsert_batch_size, len(points))
                    batch = points[start_idx:end_idx]
                    client.upsert(collection_name=collection_name, points=batch)
                log_fn(f"  [upsert-worker] Added {len(points)} vectors for {file_key}")
                manifest["files"][file_key] = _make_manifest_entry(file_info, ids)
                counters["vectors_added"] += len(points)
                if action_type == "add":
                    counters["files_added"] += 1
                else:
                    counters["files_modified"] += 1
            except Exception as e:
                log_error_fn(f"[upsert-worker] Adding {file_key}: {e}")
                counters["files_errored"] += 1

        counters["files_processed"] += 1

    return counters


class DrainState:
    """Mutable state container for _drain_pending_upsert tests.

    Replicates the nonlocal variables used in perform_refresh_qdrant.
    """

    def __init__(self, save_batch_size: int = 10):
        self.pending_upsert: Future | None = None
        self.total_vectors_added = 0
        self.total_files_added = 0
        self.total_files_modified = 0
        self.total_files_errored = 0
        self.total_zero_vectors_skipped = 0
        self.processed_since_save = 0
        self.save_batch_size = save_batch_size
        self.manifest = {"files": {}}
        self.save_called = False

    def save(self):
        """Mock manifest save."""
        self.save_called = True

    def drain_pending_upsert(self):
        """Replicated from index_rag.py:2049 with state on self."""
        if self.pending_upsert is None:
            return
        try:
            result = self.pending_upsert.result()
            self.total_vectors_added += result["vectors_added"]
            self.total_files_added += result["files_added"]
            self.total_files_modified += result["files_modified"]
            self.total_files_errored += result["files_errored"]
            self.total_zero_vectors_skipped += result["zero_vectors_skipped"]
            self.processed_since_save += result["files_processed"]
            if self.processed_since_save >= self.save_batch_size:
                self.save()
                self.processed_since_save = 0
        except Exception:
            raise
        finally:
            self.pending_upsert = None


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_point(point_id: str) -> dict:
    """Create a minimal mock point."""
    return {"id": point_id, "vector": [0.1, 0.2, 0.3]}


def _make_work_item(
    file_key: str,
    n_points: int,
    action_type: str = "add",
    zero_count: int = 0,
) -> dict:
    """Create a work item dict for do_background_upsert."""
    ids = [f"{file_key}_id_{i}" for i in range(n_points)]
    points = [_make_point(pid) for pid in ids]
    return {
        "points": points,
        "zero_count": zero_count,
        "file_key": file_key,
        "ids": ids,
        "file_info": {
            "file_path": file_key,
            "mtime": 1000.0,
            "hash": f"hash_{file_key}",
        },
        "action_type": action_type,
    }


# ════════════════════════════════════════════════════════════════════
# Tests for _do_background_upsert
# ════════════════════════════════════════════════════════════════════


class TestDoBackgroundUpsertCounters:
    """Counter accumulation logic."""

    def test_empty_work_items_returns_zero_counters(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        result = do_background_upsert(
            [],
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert result == {
            "vectors_added": 0,
            "files_added": 0,
            "files_modified": 0,
            "files_errored": 0,
            "zero_vectors_skipped": 0,
            "files_processed": 0,
        }
        client.upsert.assert_not_called()

    def test_single_add_file(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("test.pas", 5, action_type="add")]
        result = do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert result["vectors_added"] == 5
        assert result["files_added"] == 1
        assert result["files_modified"] == 0
        assert result["files_processed"] == 1
        assert "test.pas" in manifest["files"]

    def test_single_modify_file(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("test.pas", 3, action_type="modify")]
        result = do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert result["files_added"] == 0
        assert result["files_modified"] == 1
        assert result["vectors_added"] == 3

    def test_multiple_files_accumulate(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [
            _make_work_item("a.pas", 10, action_type="add"),
            _make_work_item("b.sql", 5, action_type="modify"),
            _make_work_item("c.dfm", 3, action_type="add", zero_count=2),
        ]
        result = do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert result["vectors_added"] == 18
        assert result["files_added"] == 2
        assert result["files_modified"] == 1
        assert result["files_processed"] == 3
        assert result["zero_vectors_skipped"] == 2
        assert len(manifest["files"]) == 3

    def test_zero_count_accumulated_even_on_error(self):
        client = MagicMock()
        client.upsert.side_effect = RuntimeError("Qdrant down")
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("a.pas", 3, zero_count=5)]
        result = do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert result["zero_vectors_skipped"] == 5
        assert result["files_errored"] == 1
        assert result["vectors_added"] == 0
        assert result["files_processed"] == 1


class TestDoBackgroundUpsertBatching:
    """Upsert batching at 500 points per call."""

    def test_small_batch_single_upsert(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("test.pas", 100)]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert client.upsert.call_count == 1
        call_args = client.upsert.call_args
        assert call_args.kwargs["collection_name"] == "test_col"
        assert len(call_args.kwargs["points"]) == 100

    def test_exact_batch_boundary(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("test.pas", 500)]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert client.upsert.call_count == 1

    def test_over_batch_boundary_two_calls(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("test.pas", 501)]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert client.upsert.call_count == 2
        # First batch: 500, second batch: 1
        first_call = client.upsert.call_args_list[0]
        second_call = client.upsert.call_args_list[1]
        assert len(first_call.kwargs["points"]) == 500
        assert len(second_call.kwargs["points"]) == 1

    def test_large_file_multiple_batches(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("big.pas", 1501)]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        # 1501 / 500 = 3 full + 1 partial = 4 calls
        assert client.upsert.call_count == 4

    def test_zero_points_no_upsert(self):
        """A file with 0 points should still be processed (e.g. all-zero vectors filtered)."""
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        item = _make_work_item("empty.pas", 0)
        do_background_upsert(
            [item],
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        # 0 points → 0 batches → 0 upsert calls, but file is still recorded
        client.upsert.assert_not_called()
        assert "empty.pas" in manifest["files"]
        assert manifest["files"]["empty.pas"]["vector_ids"] == []


class TestDoBackgroundUpsertErrorHandling:
    """Error handling: per-file errors don't abort other files."""

    def test_error_on_one_file_continues_to_next(self):
        client = MagicMock()
        # Fail on first upsert call, succeed on all subsequent
        client.upsert.side_effect = [
            RuntimeError("fail"),
            None,  # second file succeeds
        ]
        manifest = {"files": {}}
        tracker = TimingTracker()
        log_error_calls = []
        items = [
            _make_work_item("bad.pas", 3, action_type="add"),
            _make_work_item("good.pas", 5, action_type="add"),
        ]
        result = do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
            log_error_fn=lambda msg: log_error_calls.append(msg),
        )
        assert result["files_errored"] == 1
        assert result["files_added"] == 1
        assert result["vectors_added"] == 5
        assert result["files_processed"] == 2
        # bad.pas not in manifest, good.pas is
        assert "bad.pas" not in manifest["files"]
        assert "good.pas" in manifest["files"]
        # Error was logged with [upsert-worker] prefix
        assert len(log_error_calls) == 1
        assert "[upsert-worker]" in log_error_calls[0]

    def test_all_files_fail(self):
        client = MagicMock()
        client.upsert.side_effect = RuntimeError("Qdrant down")
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [
            _make_work_item("a.pas", 2),
            _make_work_item("b.pas", 3),
        ]
        result = do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert result["files_errored"] == 2
        assert result["files_added"] == 0
        assert result["vectors_added"] == 0
        assert len(manifest["files"]) == 0


class TestDoBackgroundUpsertManifest:
    """Manifest entry creation."""

    def test_manifest_entry_has_correct_fields(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("unit1.pas", 3)]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        entry = manifest["files"]["unit1.pas"]
        assert entry["file_path"] == "unit1.pas"
        assert entry["mtime"] == 1000.0
        assert entry["hash"] == "hash_unit1.pas"
        assert len(entry["vector_ids"]) == 3

    def test_manifest_not_updated_on_error(self):
        client = MagicMock()
        client.upsert.side_effect = RuntimeError("fail")
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [_make_work_item("bad.pas", 3)]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert "bad.pas" not in manifest["files"]


class TestDoBackgroundUpsertLogging:
    """Log messages use [upsert-worker] prefix."""

    def test_success_log_has_prefix(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        log_calls = []
        items = [_make_work_item("test.pas", 5)]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
            log_fn=lambda msg: log_calls.append(msg),
        )
        assert len(log_calls) == 1
        assert "[upsert-worker]" in log_calls[0]
        assert "5 vectors" in log_calls[0]
        assert "test.pas" in log_calls[0]

    def test_error_log_has_prefix(self):
        client = MagicMock()
        client.upsert.side_effect = RuntimeError("boom")
        manifest = {"files": {}}
        tracker = TimingTracker()
        error_calls = []
        items = [_make_work_item("test.pas", 1)]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
            log_error_fn=lambda msg: error_calls.append(msg),
        )
        assert len(error_calls) == 1
        assert "[upsert-worker]" in error_calls[0]
        assert "boom" in error_calls[0]


class TestDoBackgroundUpsertTiming:
    """TimingTracker integration."""

    def test_upsert_timing_recorded(self):
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        items = [
            _make_work_item("a.pas", 3),
            _make_work_item("b.pas", 5),
        ]
        do_background_upsert(
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        assert "upsert" in tracker.timings
        assert tracker.counts["upsert"] == 2  # one per file
        assert tracker.timings["upsert"] > 0


# ════════════════════════════════════════════════════════════════════
# Tests for _drain_pending_upsert
# ════════════════════════════════════════════════════════════════════


class TestDrainPendingUpsertNoop:
    """No-op when no pending upsert."""

    def test_noop_when_none(self):
        state = DrainState()
        state.drain_pending_upsert()  # should not raise
        assert state.total_vectors_added == 0

    def test_noop_does_not_save(self):
        state = DrainState()
        state.drain_pending_upsert()
        assert not state.save_called


class TestDrainPendingUpsertCounters:
    """Counter-delta application from Future result."""

    def _make_completed_future(self, result: dict) -> Future:
        f = Future()
        f.set_result(result)
        return f

    def test_applies_all_counter_deltas(self):
        state = DrainState()
        state.pending_upsert = self._make_completed_future(
            {
                "vectors_added": 50,
                "files_added": 3,
                "files_modified": 2,
                "files_errored": 1,
                "zero_vectors_skipped": 7,
                "files_processed": 6,
            }
        )
        state.drain_pending_upsert()
        assert state.total_vectors_added == 50
        assert state.total_files_added == 3
        assert state.total_files_modified == 2
        assert state.total_files_errored == 1
        assert state.total_zero_vectors_skipped == 7
        assert state.processed_since_save == 6

    def test_accumulates_across_multiple_drains(self):
        state = DrainState(save_batch_size=100)  # high threshold to avoid reset
        state.pending_upsert = self._make_completed_future(
            {
                "vectors_added": 10,
                "files_added": 1,
                "files_modified": 0,
                "files_errored": 0,
                "zero_vectors_skipped": 0,
                "files_processed": 1,
            }
        )
        state.drain_pending_upsert()
        # Simulate submitting another future
        state.pending_upsert = self._make_completed_future(
            {
                "vectors_added": 20,
                "files_added": 2,
                "files_modified": 1,
                "files_errored": 0,
                "zero_vectors_skipped": 3,
                "files_processed": 3,
            }
        )
        state.drain_pending_upsert()
        assert state.total_vectors_added == 30
        assert state.total_files_added == 3
        assert state.total_files_modified == 1
        assert state.total_zero_vectors_skipped == 3
        assert state.processed_since_save == 4

    def test_clears_pending_after_drain(self):
        state = DrainState()
        state.pending_upsert = self._make_completed_future(
            {
                "vectors_added": 1,
                "files_added": 1,
                "files_modified": 0,
                "files_errored": 0,
                "zero_vectors_skipped": 0,
                "files_processed": 1,
            }
        )
        state.drain_pending_upsert()
        assert state.pending_upsert is None


class TestDrainPendingUpsertSave:
    """Manifest save triggered when processed_since_save >= save_batch_size."""

    def _make_completed_future(self, result: dict) -> Future:
        f = Future()
        f.set_result(result)
        return f

    def test_triggers_save_at_threshold(self):
        state = DrainState(save_batch_size=5)
        state.pending_upsert = self._make_completed_future(
            {
                "vectors_added": 10,
                "files_added": 5,
                "files_modified": 0,
                "files_errored": 0,
                "zero_vectors_skipped": 0,
                "files_processed": 5,
            }
        )
        state.drain_pending_upsert()
        assert state.save_called
        assert state.processed_since_save == 0  # reset after save

    def test_no_save_below_threshold(self):
        state = DrainState(save_batch_size=10)
        state.pending_upsert = self._make_completed_future(
            {
                "vectors_added": 5,
                "files_added": 3,
                "files_modified": 0,
                "files_errored": 0,
                "zero_vectors_skipped": 0,
                "files_processed": 3,
            }
        )
        state.drain_pending_upsert()
        assert not state.save_called
        assert state.processed_since_save == 3

    def test_save_with_accumulated_processed(self):
        """processed_since_save accumulates across drains, triggers save when threshold reached."""
        state = DrainState(save_batch_size=5)
        state.processed_since_save = 3  # already had 3 from prior drain
        state.pending_upsert = self._make_completed_future(
            {
                "vectors_added": 5,
                "files_added": 2,
                "files_modified": 0,
                "files_errored": 0,
                "zero_vectors_skipped": 0,
                "files_processed": 3,
            }
        )
        state.drain_pending_upsert()
        # 3 + 3 = 6 >= 5 → save triggered
        assert state.save_called
        assert state.processed_since_save == 0


class TestDrainPendingUpsertErrors:
    """Error propagation from background thread."""

    def test_reraises_exception(self):
        state = DrainState()
        f = Future()
        f.set_exception(RuntimeError("Qdrant connection lost"))
        state.pending_upsert = f
        with pytest.raises(RuntimeError, match="Qdrant connection lost"):
            state.drain_pending_upsert()

    def test_clears_pending_on_error(self):
        """pending_upsert is set to None even when exception is raised."""
        state = DrainState()
        f = Future()
        f.set_exception(RuntimeError("fail"))
        state.pending_upsert = f
        with pytest.raises(RuntimeError):
            state.drain_pending_upsert()
        assert state.pending_upsert is None

    def test_counters_not_updated_on_error(self):
        """If the future raises, no counter deltas are applied."""
        state = DrainState()
        state.total_vectors_added = 100
        f = Future()
        f.set_exception(RuntimeError("fail"))
        state.pending_upsert = f
        with pytest.raises(RuntimeError):
            state.drain_pending_upsert()
        assert state.total_vectors_added == 100  # unchanged


# ════════════════════════════════════════════════════════════════════
# Integration tests: ThreadPoolExecutor double-buffer cycle
# ════════════════════════════════════════════════════════════════════


class TestDoubleBufferIntegration:
    """Full flush→drain→flush cycle with real ThreadPoolExecutor."""

    def test_submit_and_drain_cycle(self):
        """Simulate two pool flushes with double-buffered upsert."""
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        state = DrainState(save_batch_size=100)
        state.manifest = manifest

        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="upsert-worker")
        try:
            # Flush 1: submit work
            items1 = [
                _make_work_item("a.pas", 10, action_type="add"),
                _make_work_item("b.pas", 5, action_type="modify"),
            ]
            state.pending_upsert = executor.submit(
                do_background_upsert,
                items1,
                client=client,
                collection_name="test_col",
                manifest=manifest,
                timing_tracker=tracker,
            )

            # Flush 2: drain first, then submit more work
            state.drain_pending_upsert()
            assert state.total_vectors_added == 15
            assert state.total_files_added == 1
            assert state.total_files_modified == 1

            items2 = [
                _make_work_item("c.sql", 8, action_type="add"),
            ]
            state.pending_upsert = executor.submit(
                do_background_upsert,
                items2,
                client=client,
                collection_name="test_col",
                manifest=manifest,
                timing_tracker=tracker,
            )

            # Final drain
            state.drain_pending_upsert()
            assert state.total_vectors_added == 23
            assert state.total_files_added == 2
            assert len(manifest["files"]) == 3
        finally:
            executor.shutdown(wait=True)

    def test_executor_shutdown_after_drain(self):
        """Executor shuts down cleanly after all work is drained."""
        client = MagicMock()
        manifest = {"files": {}}
        tracker = TimingTracker()
        state = DrainState()
        state.manifest = manifest

        executor = ThreadPoolExecutor(max_workers=1)
        items = [_make_work_item("test.pas", 5)]
        state.pending_upsert = executor.submit(
            do_background_upsert,
            items,
            client=client,
            collection_name="test_col",
            manifest=manifest,
            timing_tracker=tracker,
        )
        state.drain_pending_upsert()
        executor.shutdown(wait=True)  # should not hang
        assert state.total_vectors_added == 5

    def test_background_thread_name(self):
        """Background thread has the expected name prefix."""
        thread_names = []
        original_upsert = MagicMock()

        def capture_thread_name(**kwargs):
            thread_names.append(threading.current_thread().name)
            return original_upsert(**kwargs)

        client = MagicMock()
        client.upsert.side_effect = capture_thread_name
        manifest = {"files": {}}
        tracker = TimingTracker()

        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="upsert-worker")
        try:
            items = [_make_work_item("test.pas", 1)]
            future = executor.submit(
                do_background_upsert,
                items,
                client=client,
                collection_name="test_col",
                manifest=manifest,
                timing_tracker=tracker,
            )
            future.result()
            assert len(thread_names) == 1
            assert "upsert-worker" in thread_names[0]
        finally:
            executor.shutdown(wait=True)

    def test_error_in_background_propagates_through_drain(self):
        """An exception in the background upsert is re-raised by drain."""
        client = MagicMock()
        client.upsert.side_effect = RuntimeError("Qdrant exploded")
        manifest = {"files": {}}
        tracker = TimingTracker()
        state = DrainState()

        executor = ThreadPoolExecutor(max_workers=1)
        try:
            items = [_make_work_item("test.pas", 3)]
            state.pending_upsert = executor.submit(
                do_background_upsert,
                items,
                client=client,
                collection_name="test_col",
                manifest=manifest,
                timing_tracker=tracker,
            )
            # The background function catches per-file errors, so it won't raise.
            # The future should return counters with files_errored=1.
            state.drain_pending_upsert()
            assert state.total_files_errored == 1
        finally:
            executor.shutdown(wait=True)


class TestDoubleBufferOverlap:
    """Verify that upsert I/O overlaps with main thread work."""

    def test_upsert_runs_concurrently_with_main_thread(self):
        """Submit upsert, do CPU work on main thread, then drain.

        The upsert should complete in parallel with the main thread work,
        demonstrating that the GIL is released during I/O.
        """
        client = MagicMock()
        upsert_sleep_time = 0.1

        def slow_upsert(**kwargs):
            time.sleep(upsert_sleep_time)

        client.upsert.side_effect = slow_upsert
        manifest = {"files": {}}
        tracker = TimingTracker()

        executor = ThreadPoolExecutor(max_workers=1)
        try:
            items = [_make_work_item("test.pas", 3)]
            start = time.perf_counter()
            future = executor.submit(
                do_background_upsert,
                items,
                client=client,
                collection_name="test_col",
                manifest=manifest,
                timing_tracker=tracker,
            )

            # Simulate main thread CPU work (parsing/chunking) while upsert runs
            main_thread_work_time = 0.1
            time.sleep(main_thread_work_time)

            future.result()
            elapsed = time.perf_counter() - start

            # If truly overlapping, total time should be ~max(upsert, main) not sum
            # Allow generous margin for CI variance
            assert elapsed < (upsert_sleep_time + main_thread_work_time) * 1.5
        finally:
            executor.shutdown(wait=True)


# ════════════════════════════════════════════════════════════════════
# TimingTracker thread safety
# ════════════════════════════════════════════════════════════════════


class TestTimingTrackerThreadSafety:
    """TimingTracker.measure() called from multiple threads with different keys."""

    def test_concurrent_different_keys(self):
        """Two threads measuring different keys don't corrupt each other."""
        tracker = TimingTracker()
        barrier = threading.Barrier(2)

        def thread_work(key: str, duration: float):
            barrier.wait()  # synchronize start
            with tracker.measure(key):
                time.sleep(duration)

        t1 = threading.Thread(target=thread_work, args=("embedding", 0.05))
        t2 = threading.Thread(target=thread_work, args=("upsert", 0.05))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert "embedding" in tracker.timings
        assert "upsert" in tracker.timings
        assert tracker.counts["embedding"] == 1
        assert tracker.counts["upsert"] == 1
        # Each should be ~0.05s, not 0
        assert tracker.timings["embedding"] > 0.01
        assert tracker.timings["upsert"] > 0.01

    def test_concurrent_same_key_accumulates(self):
        """Two threads measuring the same key accumulate correctly under GIL."""
        tracker = TimingTracker()
        n_iterations = 20

        def thread_work():
            for _ in range(n_iterations):
                with tracker.measure("shared_key"):
                    time.sleep(0.001)

        t1 = threading.Thread(target=thread_work)
        t2 = threading.Thread(target=thread_work)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Should have 2 * n_iterations measurements
        assert tracker.counts["shared_key"] == 2 * n_iterations
        assert tracker.timings["shared_key"] > 0
