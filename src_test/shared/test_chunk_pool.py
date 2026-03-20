"""
Tests for shared/chunk_pool.py — cross-file chunk pooling and histogram.

Tests cover:
    - FileEntry: dataclass construction, default global_start
    - ChunkPool: empty state, add single/multiple files, global_start offsets,
      chunk_count, file_count, is_empty, should_flush thresholds,
      should_flush with max_chunks=0, collect, distribute (dense only and
      dense+sparse), clear, files() returns copy
    - ChunkHistogram: empty state, add_char_lengths, add_token_lengths,
      increment_files (default and custom), total_chunks property,
      to_dict with/without lengths, save to JSON, save creates dirs,
      log_summary with chars only and chars+tokens, log_summary empty early return
    - _percentile: empty list, single element, exact percentile, interpolation
    - _compute_stats: empty list, correct statistics, overflow bucket
"""

import json
import math
from pathlib import Path
from unittest.mock import patch

import pytest

import shared.chunk_pool as chunk_pool_mod
from shared.chunk_pool import (
    ChunkHistogram,
    ChunkPool,
    FileEntry,
    _compute_stats,
    _percentile,
)


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_file_data(key: str, n_docs: int, prefix: str = "doc") -> dict:
    """Build add() kwargs for a file with n_docs documents."""
    return {
        "file_key": key,
        "file_info": {"file_path": f"src/{key}", "hash": "abc123"},
        "nodes": [f"node_{prefix}_{i}" for i in range(n_docs)],
        "ids": [f"id_{key}_{i}" for i in range(n_docs)],
        "documents": [f"{prefix}_{key}_{i}" for i in range(n_docs)],
        "action_type": "add",
    }


# ────────────────────────────────────────────────
# FileEntry
# ────────────────────────────────────────────────


class TestFileEntry:
    """Tests for the FileEntry dataclass."""

    def test_construction_with_defaults(self):
        """FileEntry sets global_start=0 by default."""
        entry = FileEntry(
            file_key="a.pas",
            file_info={"path": "a.pas"},
            nodes=["n1"],
            ids=["id1"],
            documents=["doc1"],
            action_type="add",
        )
        assert entry.file_key == "a.pas"
        assert entry.global_start == 0

    def test_construction_with_explicit_global_start(self):
        """FileEntry accepts an explicit global_start value."""
        entry = FileEntry(
            file_key="b.pas",
            file_info={},
            nodes=[],
            ids=[],
            documents=[],
            action_type="modify",
            global_start=42,
        )
        assert entry.global_start == 42
        assert entry.action_type == "modify"


# ────────────────────────────────────────────────
# ChunkPool
# ────────────────────────────────────────────────


class TestChunkPoolEmpty:
    """Tests for a fresh, empty ChunkPool."""

    def test_empty_is_empty(self):
        """A new pool reports is_empty=True."""
        pool = ChunkPool()
        assert pool.is_empty is True

    def test_empty_chunk_count(self):
        """A new pool has chunk_count=0."""
        pool = ChunkPool()
        assert pool.chunk_count == 0

    def test_empty_file_count(self):
        """A new pool has file_count=0."""
        pool = ChunkPool()
        assert pool.file_count == 0

    def test_empty_files_returns_empty_list(self):
        """files() on empty pool returns an empty list."""
        pool = ChunkPool()
        assert pool.files() == []

    def test_empty_collect(self):
        """collect() on empty pool returns empty docs and empty entries."""
        pool = ChunkPool()
        docs, entries = pool.collect()
        assert docs == []
        assert entries == []


class TestChunkPoolAdd:
    """Tests for ChunkPool.add() and related state changes."""

    def test_add_single_file(self):
        """Adding one file updates chunk_count and file_count."""
        pool = ChunkPool()
        data = _make_file_data("file_a.pas", 5)
        pool.add(**data)
        assert pool.chunk_count == 5
        assert pool.file_count == 1
        assert pool.is_empty is False

    def test_add_multiple_files_global_start_offsets(self):
        """Adding multiple files sets correct global_start offsets."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 3))
        pool.add(**_make_file_data("b.pas", 5))
        pool.add(**_make_file_data("c.pas", 2))

        entries = pool.files()
        assert len(entries) == 3
        assert entries[0].global_start == 0
        assert entries[1].global_start == 3
        assert entries[2].global_start == 8
        assert pool.chunk_count == 10

    def test_add_file_with_zero_documents(self):
        """Adding a file with zero documents is valid."""
        pool = ChunkPool()
        pool.add(**_make_file_data("empty.pas", 0))
        assert pool.chunk_count == 0
        assert pool.file_count == 1
        # is_empty checks chunk_count, not file_count
        assert pool.is_empty is True


class TestChunkPoolShouldFlush:
    """Tests for ChunkPool.should_flush() threshold logic."""

    def test_below_thresholds_returns_false(self):
        """should_flush is False when under both limits."""
        pool = ChunkPool(max_chunks=512, max_files=50)
        pool.add(**_make_file_data("a.pas", 10))
        assert pool.should_flush() is False

    def test_at_chunk_threshold_returns_true(self):
        """should_flush is True when chunk_count >= max_chunks."""
        pool = ChunkPool(max_chunks=10, max_files=50)
        pool.add(**_make_file_data("a.pas", 10))
        assert pool.should_flush() is True

    def test_above_chunk_threshold_returns_true(self):
        """should_flush is True when chunk_count exceeds max_chunks."""
        pool = ChunkPool(max_chunks=5, max_files=50)
        pool.add(**_make_file_data("a.pas", 10))
        assert pool.should_flush() is True

    def test_at_file_threshold_returns_true(self):
        """should_flush is True when file_count >= max_files."""
        pool = ChunkPool(max_chunks=9999, max_files=3)
        pool.add(**_make_file_data("a.pas", 1))
        pool.add(**_make_file_data("b.pas", 1))
        pool.add(**_make_file_data("c.pas", 1))
        assert pool.should_flush() is True

    def test_max_chunks_zero_always_true(self):
        """When max_chunks=0 (pooling disabled), should_flush always returns True."""
        pool = ChunkPool(max_chunks=0, max_files=50)
        # True even with zero chunks
        assert pool.should_flush() is True

    def test_max_chunks_zero_true_even_empty(self):
        """max_chunks=0 returns True even before any adds."""
        pool = ChunkPool(max_chunks=0, max_files=50)
        assert pool.should_flush() is True


class TestChunkPoolCollect:
    """Tests for ChunkPool.collect() — flat document list assembly."""

    def test_collect_single_file(self):
        """collect() returns documents from a single file."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 3, prefix="A"))
        docs, entries = pool.collect()
        assert docs == ["A_a.pas_0", "A_a.pas_1", "A_a.pas_2"]
        assert len(entries) == 1

    def test_collect_multiple_files_concatenated(self):
        """collect() concatenates documents from all files in order."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 2, prefix="A"))
        pool.add(**_make_file_data("b.pas", 2, prefix="B"))
        docs, entries = pool.collect()
        assert docs == ["A_a.pas_0", "A_a.pas_1", "B_b.pas_0", "B_b.pas_1"]
        assert len(entries) == 2

    def test_collect_returns_same_file_entries_as_internal(self):
        """collect() returns the actual internal _files list reference."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 1))
        _, entries = pool.collect()
        # collect() returns self._files directly (not a copy)
        assert entries is pool._files


class TestChunkPoolDistribute:
    """Tests for ChunkPool.distribute() — splitting embeddings back per-file."""

    def test_distribute_dense_only(self):
        """distribute() slices dense embeddings correctly, sparse is None."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 3))
        pool.add(**_make_file_data("b.pas", 2))

        dense = [f"dense_{i}" for i in range(5)]
        result = pool.distribute(dense)

        assert len(result) == 2
        entry_a, dense_a, sparse_a = result[0]
        assert entry_a.file_key == "a.pas"
        assert dense_a == ["dense_0", "dense_1", "dense_2"]
        assert sparse_a is None

        entry_b, dense_b, sparse_b = result[1]
        assert entry_b.file_key == "b.pas"
        assert dense_b == ["dense_3", "dense_4"]
        assert sparse_b is None

    def test_distribute_dense_and_sparse(self):
        """distribute() slices both dense and sparse embeddings correctly."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 2))
        pool.add(**_make_file_data("b.pas", 3))

        dense = [f"d{i}" for i in range(5)]
        sparse = [f"s{i}" for i in range(5)]
        result = pool.distribute(dense, sparse_dicts=sparse)

        entry_a, dense_a, sparse_a = result[0]
        assert dense_a == ["d0", "d1"]
        assert sparse_a == ["s0", "s1"]

        entry_b, dense_b, sparse_b = result[1]
        assert dense_b == ["d2", "d3", "d4"]
        assert sparse_b == ["s2", "s3", "s4"]

    def test_distribute_empty_pool(self):
        """distribute() on empty pool returns empty list."""
        pool = ChunkPool()
        result = pool.distribute([])
        assert result == []

    def test_distribute_file_with_zero_docs(self):
        """distribute() handles files with zero documents (empty slices)."""
        pool = ChunkPool()
        pool.add(**_make_file_data("empty.pas", 0))
        pool.add(**_make_file_data("a.pas", 2))

        dense = ["d0", "d1"]
        sparse = ["s0", "s1"]
        result = pool.distribute(dense, sparse_dicts=sparse)

        assert len(result) == 2
        _, dense_empty, sparse_empty = result[0]
        assert dense_empty == []
        assert sparse_empty == []

        _, dense_a, sparse_a = result[1]
        assert dense_a == ["d0", "d1"]
        assert sparse_a == ["s0", "s1"]


class TestChunkPoolClear:
    """Tests for ChunkPool.clear() — resetting the pool."""

    def test_clear_resets_to_empty(self):
        """clear() resets chunk_count, file_count, and is_empty."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 5))
        pool.add(**_make_file_data("b.pas", 3))
        assert pool.chunk_count == 8
        assert pool.file_count == 2

        pool.clear()
        assert pool.chunk_count == 0
        assert pool.file_count == 0
        assert pool.is_empty is True
        assert pool.files() == []


class TestChunkPoolFiles:
    """Tests for ChunkPool.files() — returns a copy of the internal list."""

    def test_files_returns_copy(self):
        """files() returns a new list (not the internal reference)."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 2))
        files_list = pool.files()
        assert files_list is not pool._files
        assert len(files_list) == 1
        assert files_list[0].file_key == "a.pas"

    def test_mutating_files_copy_does_not_affect_pool(self):
        """Mutating the returned list does not change the pool."""
        pool = ChunkPool()
        pool.add(**_make_file_data("a.pas", 2))
        files_list = pool.files()
        files_list.clear()
        assert pool.file_count == 1  # Internal list unchanged


# ────────────────────────────────────────────────
# ChunkHistogram
# ────────────────────────────────────────────────


class TestChunkHistogramEmpty:
    """Tests for an empty ChunkHistogram."""

    def test_empty_total_chunks(self):
        """A new histogram has total_chunks=0."""
        h = ChunkHistogram()
        assert h.total_chunks == 0

    def test_empty_total_files(self):
        """A new histogram has total_files=0."""
        h = ChunkHistogram()
        assert h.total_files == 0

    def test_empty_char_lengths(self):
        """A new histogram has empty char_lengths."""
        h = ChunkHistogram()
        assert h.char_lengths == []

    def test_empty_token_lengths(self):
        """A new histogram has empty token_lengths."""
        h = ChunkHistogram()
        assert h.token_lengths == []


class TestChunkHistogramAddAndIncrement:
    """Tests for add_char_lengths, add_token_lengths, increment_files."""

    def test_add_char_lengths_single_batch(self):
        """add_char_lengths extends the list."""
        h = ChunkHistogram()
        h.add_char_lengths([100, 200, 300])
        assert h.char_lengths == [100, 200, 300]
        assert h.total_chunks == 3

    def test_add_char_lengths_multiple_batches(self):
        """Multiple calls to add_char_lengths accumulate."""
        h = ChunkHistogram()
        h.add_char_lengths([10, 20])
        h.add_char_lengths([30])
        assert h.char_lengths == [10, 20, 30]
        assert h.total_chunks == 3

    def test_add_token_lengths_single_batch(self):
        """add_token_lengths extends the list."""
        h = ChunkHistogram()
        h.add_token_lengths([50, 100])
        assert h.token_lengths == [50, 100]

    def test_add_token_lengths_multiple_batches(self):
        """Multiple calls to add_token_lengths accumulate."""
        h = ChunkHistogram()
        h.add_token_lengths([10])
        h.add_token_lengths([20, 30])
        assert h.token_lengths == [10, 20, 30]

    def test_increment_files_default(self):
        """increment_files() adds 1 by default."""
        h = ChunkHistogram()
        h.increment_files()
        assert h.total_files == 1

    def test_increment_files_custom_count(self):
        """increment_files(count=N) adds N."""
        h = ChunkHistogram()
        h.increment_files(count=5)
        assert h.total_files == 5

    def test_increment_files_accumulates(self):
        """Multiple increment_files calls accumulate."""
        h = ChunkHistogram()
        h.increment_files(3)
        h.increment_files(2)
        assert h.total_files == 5


class TestChunkHistogramToDict:
    """Tests for ChunkHistogram.to_dict()."""

    def test_to_dict_empty(self):
        """Empty histogram dict has no char_lengths or token_lengths keys."""
        h = ChunkHistogram()
        d = h.to_dict()
        assert d["total_chunks"] == 0
        assert d["total_files"] == 0
        assert "char_lengths" not in d
        assert "token_lengths" not in d

    def test_to_dict_has_generated_at(self):
        """to_dict() includes a generated_at timestamp string."""
        h = ChunkHistogram()
        d = h.to_dict()
        assert "generated_at" in d
        # Format: YYYY-MM-DDTHH:MM:SS
        assert "T" in d["generated_at"]

    def test_to_dict_with_config_and_model(self):
        """to_dict() includes config_name and model_name."""
        h = ChunkHistogram()
        d = h.to_dict(config_name="test-config", model_name="jina-v2")
        assert d["config_name"] == "test-config"
        assert d["model_name"] == "jina-v2"

    def test_to_dict_with_char_lengths_only(self):
        """to_dict() includes char_lengths stats when present, no token_lengths."""
        h = ChunkHistogram()
        h.add_char_lengths([100, 200, 300, 400, 500])
        h.increment_files(2)
        d = h.to_dict()
        assert d["total_chunks"] == 5
        assert d["total_files"] == 2
        assert "char_lengths" in d
        assert "token_lengths" not in d
        # Verify stats structure
        char_stats = d["char_lengths"]
        assert "min" in char_stats
        assert "max" in char_stats
        assert "mean" in char_stats
        assert "buckets" in char_stats

    def test_to_dict_with_both_lengths(self):
        """to_dict() includes both char_lengths and token_lengths."""
        h = ChunkHistogram()
        h.add_char_lengths([100, 200])
        h.add_token_lengths([50, 100])
        d = h.to_dict()
        assert "char_lengths" in d
        assert "token_lengths" in d

    def test_to_dict_branch_field_default_empty(self):
        """to_dict() has empty branch field by default."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        d = h.to_dict()
        assert d["branch"] == ""

    def test_to_dict_branch_field_populated(self):
        """to_dict() includes branch field when provided."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        d = h.to_dict(branch="feature/T12345")
        assert d["branch"] == "feature/T12345"


class TestChunkHistogramSave:
    """Tests for ChunkHistogram.save()."""

    def test_save_creates_file(self, tmp_path):
        """save() creates chunk_histogram.json in the index directory."""
        h = ChunkHistogram()
        h.add_char_lengths([100, 200, 300])
        h.increment_files(1)

        result_path = h.save(str(tmp_path), config_name="test", model_name="jina")
        assert result_path.exists()
        assert result_path.name == "chunk_histogram.json"
        assert result_path.parent == tmp_path

    def test_save_valid_json(self, tmp_path):
        """save() writes valid JSON."""
        h = ChunkHistogram()
        h.add_char_lengths([256, 512])
        h.increment_files(1)

        result_path = h.save(str(tmp_path))
        content = result_path.read_text(encoding="utf-8")
        data = json.loads(content)
        assert data["total_chunks"] == 2
        assert "char_lengths" in data

    def test_save_creates_parent_dirs(self, tmp_path):
        """save() creates parent directories if they don't exist."""
        nested_path = tmp_path / "deep" / "nested" / "index"
        h = ChunkHistogram()
        h.add_char_lengths([100])

        result_path = h.save(str(nested_path))
        assert result_path.exists()
        assert result_path.parent == nested_path

    def test_save_returns_path_object(self, tmp_path):
        """save() returns a Path object pointing to the file."""
        h = ChunkHistogram()
        result_path = h.save(str(tmp_path))
        assert isinstance(result_path, Path)

    def test_save_accepts_path_object(self, tmp_path):
        """save() accepts both str and Path for index_path."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        result_path = h.save(tmp_path)
        assert result_path.exists()

    def test_save_with_config_and_model(self, tmp_path):
        """save() passes config_name and model_name through to JSON."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        h.increment_files(1)

        result_path = h.save(str(tmp_path), config_name="myconf", model_name="mymodel")
        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data["config_name"] == "myconf"
        assert data["model_name"] == "mymodel"

    def test_save_no_branch_uses_default_filename(self, tmp_path):
        """save() without branch produces chunk_histogram.json."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        result_path = h.save(tmp_path)
        assert result_path.name == "chunk_histogram.json"

    def test_save_with_branch_uses_branded_filename(self, tmp_path):
        """save() with branch produces chunk_histogram_branch_<name>.json."""
        h = ChunkHistogram()
        h.add_char_lengths([100, 200])
        h.increment_files(1)
        result_path = h.save(tmp_path, branch="task/T37523")
        assert result_path.name == "chunk_histogram_branch_task_T37523.json"
        assert result_path.exists()

    def test_save_with_branch_sanitizes_special_chars(self, tmp_path):
        """save() sanitizes branch names with special characters."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        result_path = h.save(tmp_path, branch='feature/my branch:name*"test')
        assert (
            result_path.name
            == "chunk_histogram_branch_feature_my_branch_name__test.json"
        )
        assert result_path.exists()

    def test_save_branch_does_not_overwrite_main(self, tmp_path):
        """Branch save does not overwrite the main-branch histogram."""
        main_h = ChunkHistogram()
        main_h.add_char_lengths([100, 200, 300])
        main_h.increment_files(3)
        main_path = main_h.save(tmp_path, config_name="main")

        branch_h = ChunkHistogram()
        branch_h.add_char_lengths([400, 500])
        branch_h.increment_files(2)
        branch_path = branch_h.save(tmp_path, config_name="branch", branch="feature/x")

        # Both files should exist independently
        assert main_path.exists()
        assert branch_path.exists()
        assert main_path != branch_path

        # Main histogram should still have original data
        main_data = json.loads(main_path.read_text(encoding="utf-8"))
        assert main_data["total_chunks"] == 3
        assert main_data["config_name"] == "main"

        # Branch histogram should have branch data
        branch_data = json.loads(branch_path.read_text(encoding="utf-8"))
        assert branch_data["total_chunks"] == 2
        assert branch_data["config_name"] == "branch"
        assert branch_data["branch"] == "feature/x"

    def test_save_branch_empty_string_uses_default_filename(self, tmp_path):
        """save() with branch='' produces chunk_histogram.json (same as no branch)."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        result_path = h.save(tmp_path, branch="")
        assert result_path.name == "chunk_histogram.json"

    def test_save_branch_includes_branch_in_json(self, tmp_path):
        """save() with branch includes branch field in JSON output."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        h.increment_files(1)
        result_path = h.save(tmp_path, branch="develop")
        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data["branch"] == "develop"

    def test_save_no_branch_has_empty_branch_in_json(self, tmp_path):
        """save() without branch has empty string branch in JSON output."""
        h = ChunkHistogram()
        h.add_char_lengths([100])
        result_path = h.save(tmp_path)
        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data["branch"] == ""


class TestChunkHistogramLogSummary:
    """Tests for ChunkHistogram.log_summary()."""

    def test_log_summary_empty_returns_early(self):
        """log_summary() returns immediately when char_lengths is empty."""
        h = ChunkHistogram()
        with patch.object(chunk_pool_mod, "log") as mock_log:
            with patch.object(chunk_pool_mod, "log_raw") as mock_log_raw:
                h.log_summary()
                mock_log.assert_not_called()
                mock_log_raw.assert_not_called()

    def test_log_summary_chars_only(self):
        """log_summary() logs char percentiles when only char_lengths present."""
        h = ChunkHistogram()
        h.add_char_lengths([100, 200, 300, 400, 500])
        h.increment_files(2)

        with patch.object(chunk_pool_mod, "log") as mock_log:
            with patch.object(chunk_pool_mod, "log_raw") as mock_log_raw:
                h.log_summary()
                # log_raw called for blank line and chars line
                assert mock_log_raw.call_count == 2
                # log called once for the header
                mock_log.assert_called_once()
                header = mock_log.call_args[0][0]
                assert "5 chunks" in header
                assert "2 files" in header
                # Verify chars line
                chars_line = mock_log_raw.call_args_list[1][0][0]
                assert "Chars:" in chars_line
                assert "P50=" in chars_line
                assert "Max=" in chars_line

    def test_log_summary_chars_and_tokens(self):
        """log_summary() logs both char and token percentiles when both present."""
        h = ChunkHistogram()
        h.add_char_lengths([100, 200, 300])
        h.add_token_lengths([50, 100, 150])
        h.increment_files(1)

        with patch.object(chunk_pool_mod, "log") as mock_log:
            with patch.object(chunk_pool_mod, "log_raw") as mock_log_raw:
                h.log_summary()
                # log_raw: blank line + chars line + tokens line = 3 calls
                assert mock_log_raw.call_count == 3
                tokens_line = mock_log_raw.call_args_list[2][0][0]
                assert "Tokens:" in tokens_line
                assert "P50=" in tokens_line
                assert "Max=" in tokens_line


# ────────────────────────────────────────────────
# _percentile()
# ────────────────────────────────────────────────


class TestPercentile:
    """Tests for _percentile() helper."""

    def test_empty_list_returns_zero(self):
        """_percentile on empty list returns 0."""
        assert _percentile([], 50) == 0

    def test_single_element(self):
        """_percentile on a single-element list always returns that element."""
        assert _percentile([42], 0) == 42
        assert _percentile([42], 50) == 42
        assert _percentile([42], 100) == 42

    def test_exact_percentile_no_interpolation(self):
        """When k lands exactly on an index, return that value without interpolation."""
        # sorted_data with 5 elements: indices 0,1,2,3,4
        # P50: k = 4 * 50/100 = 2.0 -> exact -> sorted_data[2] = 30
        data = [10, 20, 30, 40, 50]
        assert _percentile(data, 50) == 30

    def test_p0_returns_first_element(self):
        """P0 returns the minimum value."""
        data = [10, 20, 30]
        assert _percentile(data, 0) == 10

    def test_p100_returns_last_element(self):
        """P100 returns the maximum value."""
        data = [10, 20, 30]
        assert _percentile(data, 100) == 30

    def test_interpolated_percentile(self):
        """When k is fractional, _percentile interpolates between adjacent values."""
        # sorted_data = [10, 20], P50: k = 1 * 50/100 = 0.5
        # f=0, c=1 -> round(10 * (1 - 0.5) + 20 * 0.5) = round(15) = 15
        data = [10, 20]
        assert _percentile(data, 50) == 15

    def test_interpolated_percentile_non_round(self):
        """Test interpolation with a non-trivial fractional k."""
        # sorted_data = [0, 100], P25: k = 1 * 25/100 = 0.25
        # f=0, c=1 -> round(0 * 0.75 + 100 * 0.25) = round(25) = 25
        data = [0, 100]
        assert _percentile(data, 25) == 25

    def test_percentile_larger_dataset(self):
        """Verify percentile on a 10-element dataset."""
        # [1..10], P90: k = 9 * 90/100 = 8.1
        # f=8, c=9 -> round(9 * (9-8.1) + 10 * (8.1-8)) = round(9*0.9 + 10*0.1) = round(9.1) = 9
        data = list(range(1, 11))
        assert _percentile(data, 90) == 9


# ────────────────────────────────────────────────
# _compute_stats()
# ────────────────────────────────────────────────


class TestComputeStats:
    """Tests for _compute_stats() helper."""

    def test_empty_values_returns_empty_dict(self):
        """_compute_stats on empty list returns {}."""
        result = _compute_stats(
            [], chunk_pool_mod._CHAR_BUCKETS, chunk_pool_mod._CHAR_BUCKET_LABELS
        )
        assert result == {}

    def test_basic_stats(self):
        """Verify min, max, mean, median are computed correctly."""
        values = [100, 200, 300, 400, 500]
        result = _compute_stats(
            values, chunk_pool_mod._CHAR_BUCKETS, chunk_pool_mod._CHAR_BUCKET_LABELS
        )
        assert result["min"] == 100
        assert result["max"] == 500
        assert result["mean"] == 300  # round(1500/5)
        assert result["median"] == 300  # middle value

    def test_percentile_keys_present(self):
        """Result contains all expected percentile keys."""
        values = [100, 200, 300]
        result = _compute_stats(
            values, chunk_pool_mod._CHAR_BUCKETS, chunk_pool_mod._CHAR_BUCKET_LABELS
        )
        for key in ("p10", "p25", "p50", "p75", "p90", "p95", "p99"):
            assert key in result, f"Missing key: {key}"

    def test_bucket_counts(self):
        """Values are placed into correct buckets."""
        # 50 -> 0-128, 200 -> 128-256, 600 -> 512-1024
        values = [50, 200, 600]
        result = _compute_stats(
            values, chunk_pool_mod._CHAR_BUCKETS, chunk_pool_mod._CHAR_BUCKET_LABELS
        )
        buckets = result["buckets"]
        assert buckets["0-128"] == 1
        assert buckets["128-256"] == 1
        assert buckets["512-1024"] == 1
        # All other buckets should be 0
        assert buckets["256-512"] == 0
        assert buckets["1024-2048"] == 0

    def test_overflow_bucket(self):
        """Values exceeding all bucket ranges go to the overflow (last) bucket."""
        # 10000 > 8192 -> overflow to "8192+"
        values = [10000, 20000]
        result = _compute_stats(
            values, chunk_pool_mod._CHAR_BUCKETS, chunk_pool_mod._CHAR_BUCKET_LABELS
        )
        buckets = result["buckets"]
        assert buckets["8192+"] == 2
        # All regular buckets empty
        for label in chunk_pool_mod._CHAR_BUCKET_LABELS[:-1]:
            assert buckets[label] == 0

    def test_token_buckets(self):
        """Verify token bucket assignment with token-specific buckets."""
        # 30 -> 0-64, 100 -> 64-128, 5000 -> overflow 4096+
        values = [30, 100, 5000]
        result = _compute_stats(
            values, chunk_pool_mod._TOKEN_BUCKETS, chunk_pool_mod._TOKEN_BUCKET_LABELS
        )
        buckets = result["buckets"]
        assert buckets["0-64"] == 1
        assert buckets["64-128"] == 1
        assert buckets["4096+"] == 1

    def test_boundary_value_goes_to_correct_bucket(self):
        """Boundary value: a value exactly at a bucket boundary belongs to the next bucket."""
        # 128 is NOT in [0, 128) — it's in [128, 256)
        values = [128]
        result = _compute_stats(
            values, chunk_pool_mod._CHAR_BUCKETS, chunk_pool_mod._CHAR_BUCKET_LABELS
        )
        buckets = result["buckets"]
        assert buckets["0-128"] == 0
        assert buckets["128-256"] == 1

    def test_single_value_stats(self):
        """Single-value list produces min==max==mean==median."""
        values = [256]
        result = _compute_stats(
            values, chunk_pool_mod._CHAR_BUCKETS, chunk_pool_mod._CHAR_BUCKET_LABELS
        )
        assert result["min"] == 256
        assert result["max"] == 256
        assert result["mean"] == 256
        assert result["median"] == 256

    def test_unsorted_input_is_handled(self):
        """_compute_stats sorts the input internally."""
        values = [500, 100, 300]
        result = _compute_stats(
            values, chunk_pool_mod._CHAR_BUCKETS, chunk_pool_mod._CHAR_BUCKET_LABELS
        )
        assert result["min"] == 100
        assert result["max"] == 500


# ────────────────────────────────────────────────
# Integration: ChunkPool lifecycle
# ────────────────────────────────────────────────


class TestChunkPoolLifecycle:
    """Integration test: full add → flush → collect → distribute → clear cycle."""

    def test_full_lifecycle(self):
        """Exercise the complete pool lifecycle."""
        pool = ChunkPool(max_chunks=5, max_files=10)

        # Add files
        pool.add(**_make_file_data("a.pas", 3, prefix="A"))
        assert pool.should_flush() is False

        pool.add(**_make_file_data("b.pas", 3, prefix="B"))
        # 6 chunks >= max_chunks=5
        assert pool.should_flush() is True

        # Collect
        docs, entries = pool.collect()
        assert len(docs) == 6
        assert len(entries) == 2

        # Simulate embeddings
        dense = [f"emb_{i}" for i in range(6)]
        sparse = [f"sp_{i}" for i in range(6)]
        result = pool.distribute(dense, sparse_dicts=sparse)

        # Verify per-file distribution
        entry_a, dense_a, sparse_a = result[0]
        assert entry_a.file_key == "a.pas"
        assert len(dense_a) == 3
        assert len(sparse_a) == 3

        entry_b, dense_b, sparse_b = result[1]
        assert entry_b.file_key == "b.pas"
        assert len(dense_b) == 3
        assert len(sparse_b) == 3

        # Clear and verify reset
        pool.clear()
        assert pool.is_empty is True
        assert pool.chunk_count == 0
        assert pool.file_count == 0

    def test_reuse_after_clear(self):
        """Pool can be reused after clear()."""
        pool = ChunkPool(max_chunks=10, max_files=10)
        pool.add(**_make_file_data("a.pas", 5))
        pool.clear()

        pool.add(**_make_file_data("b.pas", 3))
        assert pool.chunk_count == 3
        assert pool.file_count == 1
        # global_start should be 0 for the first file after clear
        entries = pool.files()
        assert entries[0].global_start == 0
