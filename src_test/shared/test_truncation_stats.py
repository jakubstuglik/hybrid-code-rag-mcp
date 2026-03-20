"""
Tests for TruncationInfo and TruncationStats in shared/embedding.py.

Tests cover:
    - TruncationInfo: dataclass fields
    - TruncationStats: default values, properties (tokens_lost, truncation_pct),
      merge() with accumulation, token_lengths, edge cases (zero totals)
"""

import pytest

from shared.embedding import TruncationInfo, TruncationStats


# ────────────────────────────────────────────────
# TruncationInfo
# ────────────────────────────────────────────────


class TestTruncationInfo:
    """Tests for the TruncationInfo dataclass."""

    def test_fields_stored(self):
        """All constructor arguments are stored as attributes."""
        info = TruncationInfo(
            index=3,
            token_count=512,
            max_length=256,
            char_count=2048,
            text_preview="def foo():",
        )
        assert info.index == 3
        assert info.token_count == 512
        assert info.max_length == 256
        assert info.char_count == 2048
        assert info.text_preview == "def foo():"

    def test_equality(self):
        """Two TruncationInfo with same fields are equal (dataclass)."""
        a = TruncationInfo(0, 100, 50, 400, "abc")
        b = TruncationInfo(0, 100, 50, 400, "abc")
        assert a == b

    def test_inequality(self):
        """Different fields produce unequal instances."""
        a = TruncationInfo(0, 100, 50, 400, "abc")
        b = TruncationInfo(1, 100, 50, 400, "abc")
        assert a != b


# ────────────────────────────────────────────────
# TruncationStats — defaults
# ────────────────────────────────────────────────


class TestTruncationStatsDefaults:
    """Tests for TruncationStats default values."""

    def test_default_counts_are_zero(self):
        """All numeric fields default to zero."""
        stats = TruncationStats()
        assert stats.total_chunks == 0
        assert stats.truncated_chunks == 0
        assert stats.total_tokens_before == 0
        assert stats.total_tokens_after == 0
        assert stats.max_length == 0

    def test_default_lists_are_empty(self):
        """List fields default to empty lists."""
        stats = TruncationStats()
        assert stats.token_lengths == []
        assert stats.truncated_details == []

    def test_list_defaults_are_independent(self):
        """Each instance gets its own list (no shared mutable default)."""
        a = TruncationStats()
        b = TruncationStats()
        a.token_lengths.append(42)
        a.truncated_details.append("x")
        assert b.token_lengths == []
        assert b.truncated_details == []


# ────────────────────────────────────────────────
# TruncationStats — properties
# ────────────────────────────────────────────────


class TestTruncationStatsProperties:
    """Tests for tokens_lost and truncation_pct properties."""

    def test_tokens_lost_no_truncation(self):
        """tokens_lost is 0 when before == after."""
        stats = TruncationStats(total_tokens_before=1000, total_tokens_after=1000)
        assert stats.tokens_lost == 0

    def test_tokens_lost_with_truncation(self):
        """tokens_lost = before - after."""
        stats = TruncationStats(total_tokens_before=1000, total_tokens_after=800)
        assert stats.tokens_lost == 200

    def test_truncation_pct_zero_when_no_tokens(self):
        """truncation_pct is 0.0 when total_tokens_before is 0."""
        stats = TruncationStats()
        assert stats.truncation_pct == 0.0

    def test_truncation_pct_zero_when_no_loss(self):
        """truncation_pct is 0.0 when no tokens were lost."""
        stats = TruncationStats(total_tokens_before=500, total_tokens_after=500)
        assert stats.truncation_pct == 0.0

    def test_truncation_pct_with_loss(self):
        """truncation_pct = 100 * lost / before."""
        stats = TruncationStats(total_tokens_before=1000, total_tokens_after=800)
        # 200 / 1000 * 100 = 20.0
        assert stats.truncation_pct == pytest.approx(20.0)

    def test_truncation_pct_all_lost(self):
        """truncation_pct is 100% when all tokens are lost."""
        stats = TruncationStats(total_tokens_before=500, total_tokens_after=0)
        assert stats.truncation_pct == pytest.approx(100.0)

    def test_truncation_pct_small_fraction(self):
        """Handles small fractional percentages correctly."""
        stats = TruncationStats(total_tokens_before=10000, total_tokens_after=9999)
        assert stats.truncation_pct == pytest.approx(0.01)


# ────────────────────────────────────────────────
# TruncationStats — merge()
# ────────────────────────────────────────────────


class TestTruncationStatsMerge:
    """Tests for TruncationStats.merge()."""

    def test_merge_accumulates_counts(self):
        """Numeric fields are summed."""
        a = TruncationStats(
            total_chunks=10,
            truncated_chunks=2,
            total_tokens_before=5000,
            total_tokens_after=4800,
        )
        b = TruncationStats(
            total_chunks=5,
            truncated_chunks=1,
            total_tokens_before=2000,
            total_tokens_after=1900,
        )
        a.merge(b)
        assert a.total_chunks == 15
        assert a.truncated_chunks == 3
        assert a.total_tokens_before == 7000
        assert a.total_tokens_after == 6700

    def test_merge_extends_token_lengths(self):
        """token_lengths lists are concatenated."""
        a = TruncationStats(token_lengths=[100, 200])
        b = TruncationStats(token_lengths=[300, 400])
        a.merge(b)
        assert a.token_lengths == [100, 200, 300, 400]

    def test_merge_extends_truncated_details(self):
        """truncated_details lists are concatenated."""
        info1 = TruncationInfo(0, 500, 256, 2000, "chunk1")
        info2 = TruncationInfo(1, 600, 256, 2400, "chunk2")
        a = TruncationStats(truncated_details=[info1])
        b = TruncationStats(truncated_details=[info2])
        a.merge(b)
        assert a.truncated_details == [info1, info2]

    def test_merge_max_length_uses_other_when_nonzero(self):
        """max_length takes other's value when other.max_length is truthy."""
        a = TruncationStats(max_length=512)
        b = TruncationStats(max_length=256)
        a.merge(b)
        assert a.max_length == 256

    def test_merge_max_length_keeps_self_when_other_zero(self):
        """max_length keeps self's value when other.max_length is 0 (falsy)."""
        a = TruncationStats(max_length=512)
        b = TruncationStats(max_length=0)
        a.merge(b)
        assert a.max_length == 512

    def test_merge_max_length_both_zero(self):
        """max_length stays 0 when both are 0."""
        a = TruncationStats()
        b = TruncationStats()
        a.merge(b)
        assert a.max_length == 0

    def test_merge_into_empty(self):
        """Merging into default stats works correctly."""
        a = TruncationStats()
        b = TruncationStats(
            total_chunks=10,
            truncated_chunks=3,
            total_tokens_before=5000,
            total_tokens_after=4500,
            max_length=256,
            token_lengths=[100, 200, 300],
        )
        a.merge(b)
        assert a.total_chunks == 10
        assert a.truncated_chunks == 3
        assert a.tokens_lost == 500
        assert a.max_length == 256
        assert a.token_lengths == [100, 200, 300]

    def test_merge_empty_into_populated(self):
        """Merging empty stats changes nothing."""
        a = TruncationStats(
            total_chunks=10,
            truncated_chunks=2,
            total_tokens_before=5000,
            total_tokens_after=4800,
            max_length=512,
            token_lengths=[100],
        )
        b = TruncationStats()
        a.merge(b)
        assert a.total_chunks == 10
        assert a.truncated_chunks == 2
        assert a.total_tokens_before == 5000
        assert a.total_tokens_after == 4800
        assert a.max_length == 512  # other.max_length=0 → keeps self
        assert a.token_lengths == [100]

    def test_merge_multiple_sequential(self):
        """Multiple merges accumulate correctly."""
        total = TruncationStats()
        for i in range(5):
            chunk = TruncationStats(
                total_chunks=10,
                truncated_chunks=1,
                total_tokens_before=1000,
                total_tokens_after=950,
                max_length=256,
                token_lengths=[200 + i],
            )
            total.merge(chunk)
        assert total.total_chunks == 50
        assert total.truncated_chunks == 5
        assert total.total_tokens_before == 5000
        assert total.total_tokens_after == 4750
        assert total.tokens_lost == 250
        assert total.truncation_pct == pytest.approx(5.0)
        assert total.token_lengths == [200, 201, 202, 203, 204]

    def test_merge_does_not_modify_other(self):
        """Merging does not mutate the 'other' instance."""
        a = TruncationStats(total_chunks=5, token_lengths=[1, 2])
        b = TruncationStats(total_chunks=3, token_lengths=[3, 4])
        a.merge(b)
        # b should be unchanged
        assert b.total_chunks == 3
        assert b.token_lengths == [3, 4]

    def test_properties_after_merge(self):
        """Properties compute correctly on merged data."""
        a = TruncationStats(total_tokens_before=1000, total_tokens_after=900)
        b = TruncationStats(total_tokens_before=2000, total_tokens_after=1800)
        a.merge(b)
        assert a.tokens_lost == 300
        assert a.truncation_pct == pytest.approx(10.0)  # 300/3000 * 100
