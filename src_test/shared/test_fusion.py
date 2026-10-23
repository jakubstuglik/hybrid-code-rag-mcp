"""Tests for shared/fusion.py -- HYBRID_FUSION (minmax | rrf | dbsf) and HYBRID_RRF_K."""

import math
import types
from unittest.mock import MagicMock, patch

import pytest
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores.types import VectorStoreQueryResult

from shared.fusion import (
    DEFAULT_RRF_K,
    dbsf_fuse,
    hybrid_fusion_fn,
    make_dbsf_fusion,
    make_rrf_fusion,
    resolve_hybrid_fusion,
    rrf_fuse,
)


def _cfg(**kw):
    return types.SimpleNamespace(**kw)


def _res(pairs):
    """VectorStoreQueryResult from [(node_id, score), ...] in the given order."""
    nodes = [TextNode(id_=nid, text=nid) for nid, _ in pairs]
    return VectorStoreQueryResult(
        nodes=nodes, similarities=[s for _, s in pairs], ids=[n for n, _ in pairs]
    )


# ── resolve_hybrid_fusion ───────────────────────────────────────────


class TestResolve:
    def test_defaults_without_settings(self):
        assert resolve_hybrid_fusion(_cfg()) == ("minmax", float(DEFAULT_RRF_K))
        assert resolve_hybrid_fusion(None) == ("minmax", 60.0)

    def test_none_means_default(self):
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION=None))[0] == "minmax"

    @pytest.mark.parametrize("raw", ["rrf", "RRF", " Rrf ", "rrf\n"])
    def test_case_and_whitespace_insensitive(self, raw):
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION=raw))[0] == "rrf"

    @pytest.mark.parametrize("raw", ["", "rank", "min-max", "relative", 1, True, ["rrf"]])
    def test_invalid_mode_raises_clear_error(self, raw):
        with pytest.raises(ValueError, match="HYBRID_FUSION must be one of 'minmax', 'rrf'"):
            resolve_hybrid_fusion(_cfg(HYBRID_FUSION=raw))

    @pytest.mark.parametrize("k", [0, 0.0, 1, 10, 60, 1e6, 2.5])
    def test_valid_k(self, k):
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION="rrf", HYBRID_RRF_K=k)) == ("rrf", float(k))

    @pytest.mark.parametrize("k", [-1, -0.001, math.nan, math.inf, -math.inf, "60", True, False, [60]])
    def test_invalid_k_raises_in_rrf_mode(self, k):
        with pytest.raises(ValueError, match="HYBRID_RRF_K"):
            resolve_hybrid_fusion(_cfg(HYBRID_FUSION="rrf", HYBRID_RRF_K=k))

    def test_k_none_uses_default(self):
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION="rrf", HYBRID_RRF_K=None)) == ("rrf", 60.0)

    def test_k_ignored_in_minmax_mode(self):
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION="minmax", HYBRID_RRF_K=-5))[0] == "minmax"

    @pytest.mark.parametrize("raw", ["dbsf", "DBSF", " Dbsf ", "dbsf\n"])
    def test_dbsf_case_and_whitespace_insensitive(self, raw):
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION=raw))[0] == "dbsf"

    def test_dbsf_ignores_k_even_when_invalid(self):
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION="dbsf", HYBRID_RRF_K=-5)) == ("dbsf", 60.0)
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION="dbsf", HYBRID_RRF_K=None)) == ("dbsf", 60.0)
        assert resolve_hybrid_fusion(_cfg(HYBRID_FUSION="dbsf", HYBRID_RRF_K="nope")) == ("dbsf", 60.0)

    def test_invalid_mode_names_dbsf(self):
        with pytest.raises(ValueError, match="'minmax', 'rrf', 'dbsf'"):
            resolve_hybrid_fusion(_cfg(HYBRID_FUSION="rank"))


class TestHybridFusionFn:
    def test_minmax_returns_none_so_store_keeps_its_default(self):
        assert hybrid_fusion_fn(_cfg()) is None
        assert hybrid_fusion_fn(_cfg(HYBRID_FUSION="minmax")) is None
        assert hybrid_fusion_fn(None) is None

    def test_rrf_returns_callable_with_k(self):
        fn = hybrid_fusion_fn(_cfg(HYBRID_FUSION="rrf", HYBRID_RRF_K=20))
        assert callable(fn) and fn.rrf_k == 20.0

    def test_dbsf_returns_callable(self):
        fn = hybrid_fusion_fn(_cfg(HYBRID_FUSION="dbsf", HYBRID_RRF_K=-5))
        assert callable(fn) and fn.fusion_mode == "dbsf"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            hybrid_fusion_fn(_cfg(HYBRID_FUSION="bogus"))


# ── rrf_fuse (pure ranking) ─────────────────────────────────────────


class TestRrfFuse:
    def test_rank_one_in_both_scores_one(self):
        fused = dict(rrf_fuse(["a"], ["a"], alpha=0.5, k=60))
        assert fused["a"] == pytest.approx(1.0)

    def test_single_leg_rank_one_scores_its_weight(self):
        assert dict(rrf_fuse(["a"], [], alpha=0.7, k=60))["a"] == pytest.approx(0.7)
        assert dict(rrf_fuse([], ["a"], alpha=0.7, k=60))["a"] == pytest.approx(0.3)

    def test_formula(self):
        fused = dict(rrf_fuse(["a", "b"], ["b", "c"], alpha=0.5, k=10))
        assert fused["a"] == pytest.approx(11 * 0.5 / 11)
        assert fused["b"] == pytest.approx(11 * (0.5 / 12 + 0.5 / 11))
        assert fused["c"] == pytest.approx(11 * 0.5 / 12)
        assert [i for i, _ in rrf_fuse(["a", "b"], ["b", "c"], alpha=0.5, k=10)] == ["b", "a", "c"]

    def test_alpha_half_matches_classic_rrf_order(self):
        dense = ["a", "b", "c", "d", "e"]
        sparse = ["e", "c", "x", "a"]
        k = 60
        classic = {}
        for lst in (dense, sparse):
            for r, nid in enumerate(lst, 1):
                classic[nid] = classic.get(nid, 0) + 1 / (k + r)
        ours = rrf_fuse(dense, sparse, alpha=0.5, k=k)
        assert [i for i, _ in ours] == sorted(classic, key=lambda n: -classic[n])

    def test_both_empty(self):
        assert rrf_fuse([], [], alpha=0.5, k=60) == []

    def test_one_leg_empty_keeps_other_order(self):
        assert [i for i, _ in rrf_fuse(["a", "b", "c"], [], 0.5, 60)] == ["a", "b", "c"]
        assert [i for i, _ in rrf_fuse([], ["c", "b", "a"], 0.5, 60)] == ["c", "b", "a"]

    def test_duplicates_across_lists_are_summed_once(self):
        fused = rrf_fuse(["a", "b"], ["a", "b"], 0.5, 60)
        assert [i for i, _ in fused] == ["a", "b"] and len(fused) == 2

    def test_duplicate_within_a_list_keeps_best_rank(self):
        fused = dict(rrf_fuse(["a", "b", "a"], [], 1.0, 0))
        assert fused["a"] == pytest.approx(1.0)  # rank 1 only, not 1 + 1/3
        assert fused["b"] == pytest.approx(0.5)

    def test_ties_broken_by_best_rank_then_first_seen(self):
        # a: dense 1 + sparse 3; c: dense 3 + sparse 1 -> same score with alpha 0.5
        # b: dense 2 + sparse 2 -> slightly different, but check exact ties only
        fused = rrf_fuse(["a", "b", "c"], ["c", "b", "a"], 0.5, 60)
        scores = dict(fused)
        assert scores["a"] == pytest.approx(scores["c"])
        order = [i for i, _ in fused]
        assert order.index("a") < order.index("c")  # same best rank, dense seen first
        # exact equal score, different best rank: x dense#1 only vs y sparse#1 only
        tie = rrf_fuse(["x"], ["y"], 0.5, 60)
        assert [i for i, _ in tie] == ["x", "y"]

    def test_alpha_one_and_zero(self):
        assert [i for i, _ in rrf_fuse(["a", "b"], ["b", "c"], 1.0, 60)][:2] == ["a", "b"]
        fused0 = dict(rrf_fuse(["a"], ["b"], 0.0, 60))
        assert fused0["a"] == 0.0 and fused0["b"] == pytest.approx(1.0)

    def test_alpha_none_is_half(self):
        assert rrf_fuse(["a"], ["b"], None, 60) == rrf_fuse(["a"], ["b"], 0.5, 60)

    @pytest.mark.parametrize("k", [0, 1, 60, 1e9])
    def test_k_edges_are_finite_and_monotone(self, k):
        fused = rrf_fuse(["a", "b", "c"], [], 1.0, k)
        s = [v for _, v in fused]
        assert all(math.isfinite(v) for v in s)
        assert s[0] == pytest.approx(1.0)
        assert s[0] >= s[1] >= s[2]

    def test_k_zero_is_reciprocal_rank(self):
        s = [v for _, v in rrf_fuse(["a", "b", "c", "d"], [], 1.0, 0)]
        assert s == pytest.approx([1.0, 0.5, 1 / 3, 0.25])

    def test_huge_k_flattens(self):
        s = [v for _, v in rrf_fuse(["a", "b", "c"], [], 1.0, 1e9)]
        assert s[-1] == pytest.approx(1.0, rel=1e-6)

    def test_small_k_rewards_top_more(self):
        dense, sparse = ["a", "b"], ["c", "x", "b"]
        # b is #2 dense and #3 sparse; a/c are #1 in one leg only
        assert rrf_fuse(dense, sparse, 0.5, 0)[0][0] == "a"
        assert rrf_fuse(dense, sparse, 0.5, 1000)[0][0] == "b"


# ── make_rrf_fusion (llama-index callable) ──────────────────────────


class TestRrfCallable:
    def test_both_empty_returns_empty_result(self):
        fn = make_rrf_fusion(60)
        for empty in (VectorStoreQueryResult(nodes=None, similarities=None, ids=None),
                      VectorStoreQueryResult(nodes=[], similarities=[], ids=[])):
            out = fn(empty, empty, alpha=0.5, top_k=8)
            assert out.nodes is None and out.ids is None

    def test_empty_dense(self):
        out = make_rrf_fusion(60)(_res([]), _res([("a", 3.0), ("b", 1.0)]), alpha=0.5, top_k=8)
        assert out.ids == ["a", "b"]
        assert out.similarities[0] == pytest.approx(0.5)

    def test_empty_sparse_none_nodes(self):
        sparse = VectorStoreQueryResult(nodes=None, similarities=None, ids=None)
        out = make_rrf_fusion(60)(_res([("a", 0.9), ("b", 0.8)]), sparse, alpha=0.5, top_k=8)
        assert out.ids == ["a", "b"]

    def test_single_result(self):
        out = make_rrf_fusion(60)(_res([("a", 0.9)]), _res([("a", 12.0)]), alpha=0.5, top_k=8)
        assert out.ids == ["a"] and out.similarities == [pytest.approx(1.0)]
        assert out.nodes[0].node_id == "a"

    def test_unsorted_input_is_ranked_by_score(self):
        out = make_rrf_fusion(60)(_res([("b", 0.1), ("a", 0.9)]), _res([]), alpha=0.5, top_k=8)
        assert out.ids == ["a", "b"]

    def test_equal_scores_keep_leg_order(self):
        out = make_rrf_fusion(60)(_res([("b", 0.5), ("a", 0.5)]), _res([]), alpha=0.5, top_k=8)
        assert out.ids == ["b", "a"]

    def test_missing_similarities_keep_leg_order(self):
        dense = VectorStoreQueryResult(nodes=[TextNode(id_="b"), TextNode(id_="a")],
                                       similarities=None, ids=["b", "a"])
        assert make_rrf_fusion(60)(dense, _res([]), alpha=0.5, top_k=8).ids == ["b", "a"]

    def test_top_k_truncates(self):
        dense = _res([(f"d{i}", 1 - i / 100) for i in range(10)])
        sparse = _res([(f"s{i}", 10 - i) for i in range(10)])
        out = make_rrf_fusion(60)(dense, sparse, alpha=0.5, top_k=3)
        assert len(out.ids) == 3 and len(out.nodes) == 3 and len(out.similarities) == 3

    def test_duplicates_across_lists_become_one_node(self):
        out = make_rrf_fusion(60)(_res([("a", 0.9), ("b", 0.8)]), _res([("b", 5.0), ("a", 4.0)]),
                                  alpha=0.5, top_k=8)
        assert sorted(out.ids) == ["a", "b"] and len(out.nodes) == 2

    def test_rank_not_raw_score_decides(self):
        # a huge BM25 score for a sparse-only hit does not beat a dense+sparse hit
        dense = _res([("a", 0.80), ("b", 0.79)])
        sparse = _res([("x", 1000.0), ("b", 1.0)])
        out = make_rrf_fusion(60)(dense, sparse, alpha=0.5, top_k=8)
        assert out.ids[0] == "b"

    def test_scores_stay_in_unit_range(self):
        dense = _res([(f"d{i}", 1 - i / 100) for i in range(50)])
        sparse = _res([(f"d{i}", 50 - i) for i in range(50)])
        out = make_rrf_fusion(60)(dense, sparse, alpha=0.5, top_k=100)
        assert all(0.0 < s <= 1.0 + 1e-12 for s in out.similarities)

    def test_extra_kwargs_accepted(self):
        out = make_rrf_fusion(60)(_res([("a", 1.0)]), _res([]), alpha=0.5, top_k=1, unused=1)
        assert out.ids == ["a"]


# ── dbsf_fuse (pure distribution-based fusion) ──────────────────────


def _norms_of(pairs, alpha=1.0):
    return dict(dbsf_fuse(pairs, [], alpha=alpha))


class TestDbsfFuse:
    def test_two_distinct_scores_are_one_third_and_two_thirds(self):
        # For any two distinct scores, sigma = |hi - lo| / 2, so the
        # lower score is exactly one sigma below the mean and normalises
        # to 1/3; the higher normalises to 2/3. Min-max would map them to 0 and 1.
        fused = _norms_of([("lo", -100.0), ("hi", 0.2)])
        assert fused["lo"] == pytest.approx(1.0 / 3.0)
        assert fused["hi"] == pytest.approx(2.0 / 3.0)

    def test_population_std_for_three_scores(self):
        # scores 1, 2, 3: mu = 2, population variance = 2/3.
        # Sample std would be 1 and would map 3 to 2/3.
        sigma = math.sqrt(2.0 / 3.0)

        def expect(score):
            return (score - (2.0 - 3.0 * sigma)) / (6.0 * sigma)

        fused = _norms_of([("a", 1.0), ("b", 2.0), ("c", 3.0)])
        assert fused["a"] == pytest.approx(expect(1.0))
        assert fused["b"] == pytest.approx(0.5)  # the mean always lands on 0.5
        assert fused["c"] == pytest.approx(expect(3.0))
        sample = (3.0 - (2.0 - 3.0 * 1.0)) / 6.0
        assert abs(fused["c"] - sample) > 0.02

    def test_high_outlier_clips_to_one_and_does_not_squash_the_rest(self):
        # 10 zeros and one 1. The outlier's z-score is sqrt(10) > 3, so it
        # clips to 1. Each zero stays near the middle of 0..1.
        raw_high = 0.5 + 5.0 / (3.0 * math.sqrt(10.0))
        assert raw_high > 1.0
        pairs = [(f"z{i}", 0.0) for i in range(10)] + [("hi", 1.0)]
        fused = dbsf_fuse(pairs, [], alpha=1.0)
        scores = dict(fused)
        assert scores["hi"] == 1.0
        assert scores["z0"] == pytest.approx(0.5 - 1.0 / (6.0 * math.sqrt(10.0)))
        assert 0.0 < scores["z0"] < 1.0
        assert [i for i, _ in fused] == ["hi"] + [f"z{i}" for i in range(10)]

    def test_low_outlier_clips_to_zero(self):
        pairs = [(f"h{i}", 1.0) for i in range(10)] + [("lo", 0.0)]
        scores = dict(dbsf_fuse(pairs, [], alpha=1.0))
        assert scores["lo"] == 0.0
        assert scores["h0"] == pytest.approx(0.5 + 1.0 / (6.0 * math.sqrt(10.0)))

    def test_weighted_sum_and_missing_leg_is_zero(self):
        # dense 0 < 1 -> 1/3, 2/3; sparse 10 < 40 -> 1/3, 2/3
        dense = [("a", 0.0), ("b", 1.0)]
        sparse = [("b", 10.0), ("c", 40.0)]
        alpha = 0.25
        fused = dict(dbsf_fuse(dense, sparse, alpha=alpha))
        assert fused["a"] == pytest.approx(alpha * (1.0 / 3.0))
        assert fused["b"] == pytest.approx(alpha * (2.0 / 3.0) + (1.0 - alpha) * (1.0 / 3.0))
        assert fused["c"] == pytest.approx((1.0 - alpha) * (2.0 / 3.0))
        assert [i for i, _ in dbsf_fuse(dense, sparse, alpha=alpha)] == ["c", "b", "a"]

    def test_both_empty(self):
        assert dbsf_fuse([], [], alpha=0.5) == []
        assert dbsf_fuse(None, None, alpha=0.5) == []

    def test_one_leg_empty_is_normalised_and_weighted(self):
        # Not the raw scores (minmax's empty-leg special case). A lone
        # sparse leg is still divided by its distribution and by (1 - alpha).
        fused = dict(dbsf_fuse([], [("a", 12.0), ("b", 3.0)], alpha=0.5))
        assert fused["a"] == pytest.approx(0.5 * (2.0 / 3.0))
        assert fused["b"] == pytest.approx(0.5 * (1.0 / 3.0))
        assert fused["a"] < 1.0
        order = [i for i, _ in dbsf_fuse([("a", 12.0), ("b", 3.0)], [], alpha=0.25)]
        assert order == ["a", "b"]

    def test_single_score_and_all_equal_scores_normalise_to_one(self):
        assert dict(dbsf_fuse([("a", 0.2)], [], 0.7))["a"] == pytest.approx(0.7)
        assert dict(dbsf_fuse([], [("a", 99.0)], 0.7))["a"] == pytest.approx(0.3)
        assert dict(dbsf_fuse([("a", 0.2)], [("a", 99.0)], 0.7))["a"] == pytest.approx(1.0)
        fused = dbsf_fuse([("a", 5.0), ("b", 5.0), ("c", 5.0)], [], alpha=1.0)
        assert [i for i, _ in fused] == ["a", "b", "c"]
        assert [s for _, s in fused] == [1.0, 1.0, 1.0]

    def test_none_nan_and_inf_are_skipped(self):
        plain = dbsf_fuse([("a", 1.0), ("b", 4.0)], [], 1.0)
        with_holes = dbsf_fuse(
            [("a", 1.0), ("x", None), ("b", 4.0), ("n", math.nan),
             ("i", math.inf), ("j", -math.inf)],
            [],
            1.0,
        )
        assert with_holes == plain
        assert dbsf_fuse([("a", None), ("b", math.nan)], [("c", math.inf)], 0.5) == []

    def test_non_finite_duplicate_keeps_the_finite_score(self):
        fused = dict(dbsf_fuse([("a", math.inf), ("b", 1.0), ("a", 3.0)], [], alpha=1.0))
        assert fused["a"] == pytest.approx(2.0 / 3.0)
        assert fused["b"] == pytest.approx(1.0 / 3.0)

    def test_bool_string_and_malformed_rows_are_skipped(self):
        fused = dict(dbsf_fuse(
            [("a", True), ("b", "5"), ("c", 2.0), "nope", ("only",), None, (None, 3.0)],
            [],
            1.0,
        ))
        assert list(fused) == ["c"]
        assert fused["c"] == 1.0

    def test_duplicate_keeps_best_score(self):
        # a=100 (not the earlier 1), b=3 -> two-point norms 2/3 and 1/3.
        fused = dict(dbsf_fuse([("a", 1.0), ("b", 3.0), ("a", 100.0)], [], alpha=1.0))
        assert fused["a"] == pytest.approx(2.0 / 3.0)
        assert fused["b"] == pytest.approx(1.0 / 3.0)
        assert len(fused) == 2

    def test_duplicate_equal_scores_keep_earliest_order(self):
        fused = dbsf_fuse([("b", 5.0), ("a", 5.0), ("b", 5.0)], [], alpha=1.0)
        assert [i for i, _ in fused] == ["b", "a"]

    def test_ties_broken_by_best_rank_then_first_seen(self):
        # Every finite score on a leg is equal, so every norm is 1.
        # a is in both legs (score 1). b is dense-only rank 2 (score 0.5).
        # c is sparse rank 1 (score 0.5). c outranks b despite b appearing first.
        fused = dbsf_fuse([("a", 1.0), ("b", 1.0)], [("c", 4.0), ("a", 4.0)], alpha=0.5)
        assert [i for i, _ in fused] == ["a", "c", "b"]
        scores = dict(fused)
        assert scores["a"] == pytest.approx(1.0)
        assert scores["b"] == pytest.approx(0.5)
        assert scores["c"] == pytest.approx(0.5)
        # Same best rank and same score: the dense leg's id comes first.
        tie = dbsf_fuse([("x", 2.0)], [("y", 9.0)], alpha=0.5)
        assert [i for i, _ in tie] == ["x", "y"]
        assert dict(tie)["x"] == pytest.approx(dict(tie)["y"])

    def test_alpha_zero_and_one(self):
        dense = [("a", 0.0), ("b", 1.0)]
        sparse = [("c", 5.0), ("b", 1.0)]
        only_dense = dict(dbsf_fuse(dense, sparse, alpha=1.0))
        assert only_dense["b"] == pytest.approx(2.0 / 3.0)
        assert only_dense["a"] == pytest.approx(1.0 / 3.0)
        assert only_dense["c"] == 0.0
        assert [i for i, _ in dbsf_fuse(dense, sparse, alpha=1.0)] == ["b", "a", "c"]
        only_sparse = dict(dbsf_fuse(dense, sparse, alpha=0.0))
        assert only_sparse["c"] == pytest.approx(2.0 / 3.0)
        assert only_sparse["b"] == pytest.approx(1.0 / 3.0)
        assert only_sparse["a"] == 0.0
        assert [i for i, _ in dbsf_fuse(dense, sparse, alpha=0.0)] == ["c", "b", "a"]

    def test_alpha_none_is_half(self):
        assert dbsf_fuse([("a", 1.0)], [("b", 2.0)], None) == dbsf_fuse(
            [("a", 1.0)], [("b", 2.0)], 0.5
        )

    def test_unsorted_input_follows_score(self):
        fused = dbsf_fuse([("b", 1.0), ("a", 3.0), ("c", 2.0)], [], alpha=1.0)
        assert [i for i, _ in fused] == ["a", "c", "b"]

    def test_scores_stay_in_unit_interval(self):
        dense = [(f"d{i}", float(i)) for i in range(20)]
        sparse = [(f"d{i}", 100.0 - i) for i in range(15)] + [("s", 4.0)]
        fused = dbsf_fuse(dense, sparse, alpha=0.5)
        scores = [score for _, score in fused]
        assert scores == sorted(scores, reverse=True)
        assert all(0.0 <= score <= 1.0 for score in scores)

    def test_string_leg_is_empty(self):
        assert dbsf_fuse("abc", [], alpha=0.5) == []


# ── make_dbsf_fusion (llama-index callable) ─────────────────────────


class TestDbsfCallable:
    def test_both_empty_returns_empty_result(self):
        fn = make_dbsf_fusion()
        for empty in (
            VectorStoreQueryResult(nodes=None, similarities=None, ids=None),
            VectorStoreQueryResult(nodes=[], similarities=[], ids=[]),
        ):
            out = fn(empty, empty, alpha=0.5, top_k=8)
            assert out.nodes is None and out.ids is None and out.similarities is None

    def test_one_empty_leg_is_normalised_and_weighted(self):
        out = make_dbsf_fusion()(
            _res([]), _res([("a", 12.0), ("b", 3.0)]), alpha=0.5, top_k=8
        )
        assert out.ids == ["a", "b"]
        assert out.similarities[0] == pytest.approx(1.0 / 3.0)
        assert out.similarities[1] == pytest.approx(1.0 / 6.0)
        assert out.nodes[0].node_id == "a"

    def test_single_result_in_both_legs_scores_one(self):
        out = make_dbsf_fusion()(
            _res([("a", 0.2)]), _res([("a", 50.0)]), alpha=0.3, top_k=4
        )
        assert out.ids == ["a"]
        assert out.similarities == [pytest.approx(1.0)]
        assert out.nodes[0].node_id == "a"

    def test_top_k_truncates(self):
        dense = _res([(f"d{i}", float(i)) for i in range(8)])
        sparse = _res([(f"s{i}", float(i)) for i in range(8)])
        out = make_dbsf_fusion()(dense, sparse, alpha=0.5, top_k=3)
        assert len(out.ids) == len(out.nodes) == len(out.similarities) == 3

    def test_duplicate_id_keeps_best_node(self):
        low = TextNode(id_="a", text="low")
        high = TextNode(id_="a", text="high")
        other = TextNode(id_="b", text="other")
        dense = VectorStoreQueryResult(
            nodes=[low, other, high],
            similarities=[0.1, 0.0, 5.0],
            ids=["a", "b", "a"],
        )
        out = make_dbsf_fusion()(dense, _res([]), alpha=1.0, top_k=8)
        assert out.ids == ["a", "b"]
        assert out.nodes[0].text == "high"
        assert out.similarities[0] == pytest.approx(2.0 / 3.0)
        assert out.similarities[1] == pytest.approx(1.0 / 3.0)

    def test_later_worse_or_missing_score_keeps_the_best_node(self):
        best = TextNode(id_="a", text="best")
        worse = TextNode(id_="a", text="worse")
        dense = VectorStoreQueryResult(
            nodes=[best, worse], similarities=[5.0, 1.0], ids=["a", "a"]
        )
        out = make_dbsf_fusion()(dense, _res([]), alpha=1.0, top_k=2)
        assert out.nodes[0].text == "best"

        missing = TextNode(id_="a", text="missing")
        found = TextNode(id_="a", text="found")
        recovered = VectorStoreQueryResult(
            nodes=[missing, found], similarities=[None, 2.0], ids=["a", "a"]
        )
        out = make_dbsf_fusion()(recovered, _res([]), alpha=1.0, top_k=2)
        assert out.ids == ["a"]
        assert out.nodes[0].text == "found"
        assert out.similarities == [pytest.approx(1.0)]

    def test_prefers_dense_node_when_id_is_in_both_legs(self):
        dense_node = TextNode(id_="a", text="from-dense")
        sparse_node = TextNode(id_="a", text="from-sparse")
        dense = VectorStoreQueryResult(nodes=[dense_node], similarities=[0.2], ids=["a"])
        sparse = VectorStoreQueryResult(nodes=[sparse_node], similarities=[20.0], ids=["a"])
        out = make_dbsf_fusion()(dense, sparse, alpha=0.5, top_k=4)
        assert out.nodes[0].text == "from-dense"
        assert out.similarities == [pytest.approx(1.0)]

    def test_missing_similarities_drop_the_leg(self):
        dense = VectorStoreQueryResult(
            nodes=[TextNode(id_="b"), TextNode(id_="a")],
            similarities=None,
            ids=["b", "a"],
        )
        out = make_dbsf_fusion()(dense, _res([("s", 3.0)]), alpha=0.25, top_k=8)
        assert out.ids == ["s"]
        assert out.similarities == [pytest.approx(0.75)]

    def test_mismatched_similarities_drop_the_leg(self):
        dense = VectorStoreQueryResult(
            nodes=[TextNode(id_="a"), TextNode(id_="b")],
            similarities=[0.9],
            ids=["a", "b"],
        )
        out = make_dbsf_fusion()(dense, _res([("s", 1.0)]), alpha=0.5, top_k=8)
        assert out.ids == ["s"]

    def test_none_nan_scores_are_skipped(self):
        dense = VectorStoreQueryResult(
            nodes=[TextNode(id_="a"), TextNode(id_="b"), TextNode(id_="c")],
            similarities=[1.0, None, math.nan],
            ids=["a", "b", "c"],
        )
        out = make_dbsf_fusion()(dense, _res([("d", math.inf)]), alpha=1.0, top_k=8)
        assert out.ids == ["a"]
        assert out.similarities == [pytest.approx(1.0)]

    def test_alpha_zero_and_one(self):
        dense = _res([("a", 1.0), ("b", 1.0)])
        sparse = _res([("c", 5.0), ("b", 8.0)])
        one = make_dbsf_fusion()(dense, sparse, alpha=1.0, top_k=8)
        assert one.ids == ["a", "b", "c"]
        assert one.similarities[0] == pytest.approx(1.0)
        assert one.similarities[1] == pytest.approx(1.0)
        assert one.similarities[2] == 0.0
        zero = make_dbsf_fusion()(dense, sparse, alpha=0.0, top_k=8)
        assert zero.ids == ["b", "c", "a"]
        assert zero.similarities[0] == pytest.approx(2.0 / 3.0)
        assert zero.similarities[1] == pytest.approx(1.0 / 3.0)
        assert zero.similarities[2] == 0.0

    def test_top_k_and_extra_kwargs(self):
        out = make_dbsf_fusion()(
            _res([("a", 1.0), ("b", 2.0)]), _res([]), alpha=1.0, top_k=1, unused=1
        )
        assert out.ids == ["b"]

    def test_unsorted_input_follows_score(self):
        out = make_dbsf_fusion()(_res([("b", 0.1), ("a", 0.9)]), _res([]), alpha=1.0, top_k=8)
        assert out.ids == ["a", "b"]

    def test_equal_scores_keep_leg_order(self):
        out = make_dbsf_fusion()(_res([("b", 0.5), ("a", 0.5)]), _res([]), alpha=1.0, top_k=8)
        assert out.ids == ["b", "a"]
        assert out.similarities == [pytest.approx(1.0), pytest.approx(1.0)]


# ── vector store wiring ─────────────────────────────────────────────


def _vs_cfg(**kw):
    cfg = types.ModuleType("fake_config")
    kw.setdefault("INDEXING_MODE", "hybrid")
    kw.setdefault("COLLECTION_NAME", "c")
    for k, v in kw.items():
        setattr(cfg, k, v)
    return cfg


def _build(cfg):
    import qdrant.vector_store as vs_mod

    with patch.object(vs_mod, "get_qdrant_client_pair", return_value=(MagicMock(), MagicMock())), \
         patch.object(vs_mod, "get_sparse_encoder", return_value=lambda texts: ([], [])), \
         patch.object(vs_mod, "QdrantVectorStore") as store, \
         patch.object(vs_mod, "StorageContext"):
        vs_mod.get_qdrant_vector_store(cfg=cfg)
    return store.call_args.kwargs


class TestVectorStoreWiring:
    def test_minmax_passes_no_fusion_fn(self):
        assert "hybrid_fusion_fn" not in _build(_vs_cfg())
        assert "hybrid_fusion_fn" not in _build(_vs_cfg(HYBRID_FUSION="minmax"))

    def test_rrf_passes_fusion_fn(self):
        kw = _build(_vs_cfg(HYBRID_FUSION="rrf", HYBRID_RRF_K=15))
        assert kw["hybrid_fusion_fn"].rrf_k == 15.0

    def test_dbsf_passes_fusion_fn(self):
        kw = _build(_vs_cfg(HYBRID_FUSION="dbsf", HYBRID_RRF_K=-1))
        assert kw["hybrid_fusion_fn"].fusion_mode == "dbsf"

    def test_dense_collection_ignores_rrf(self):
        assert "hybrid_fusion_fn" not in _build(_vs_cfg(INDEXING_MODE="dense", HYBRID_FUSION="rrf"))

    def test_dense_collection_ignores_dbsf(self):
        built = _build(_vs_cfg(INDEXING_MODE="dense", HYBRID_FUSION="dbsf"))
        assert "hybrid_fusion_fn" not in built

    def test_invalid_value_fails_even_for_dense(self):
        with pytest.raises(ValueError, match="HYBRID_FUSION"):
            _build(_vs_cfg(INDEXING_MODE="dense", HYBRID_FUSION="rank"))

    def test_minmax_store_uses_llama_relative_score_fusion(self):
        """End-to-end: an unconfigured hybrid store keeps llama-index's default fusion."""
        from llama_index.vector_stores.qdrant import QdrantVectorStore
        from llama_index.vector_stores.qdrant.utils import relative_score_fusion
        from qdrant_client import QdrantClient

        store = QdrantVectorStore(client=QdrantClient(location=":memory:"), collection_name="t",
                                  enable_hybrid=True, sparse_doc_fn=lambda t: ([], []),
                                  sparse_query_fn=lambda t: ([], []),
                                  hybrid_fusion_fn=hybrid_fusion_fn(_cfg()))
        assert store._hybrid_fusion_fn is relative_score_fusion


# ── end to end through an in-memory Qdrant hybrid query ────────────


def _vocab_sparse(texts):
    """Tiny deterministic sparse encoder: token id = position in a fixed vocab."""
    vocab = ["alpha", "beta", "gamma", "delta", "omega"]
    idx, val = [], []
    for t in texts:
        words = t.lower().split()
        ids = sorted({vocab.index(w) for w in words if w in vocab})
        idx.append(ids)
        val.append([float(words.count(vocab[i])) for i in ids])
    return idx, val


def _memory_store(fusion_cfg):
    from llama_index.vector_stores.qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient

    kwargs = dict(client=QdrantClient(location=":memory:"), collection_name="fusion_e2e",
                  enable_hybrid=True, sparse_doc_fn=_vocab_sparse, sparse_query_fn=_vocab_sparse)
    fn = hybrid_fusion_fn(fusion_cfg)
    if fn is not None:
        kwargs["hybrid_fusion_fn"] = fn
    store = QdrantVectorStore(**kwargs)
    docs = [
        ("n1", "alpha", [1.0, 0.0, 0.0]),
        ("n2", "beta", [0.9, 0.1, 0.0]),
        ("n3", "alpha alpha alpha gamma", [0.0, 1.0, 0.0]),
        ("n4", "alpha beta", [0.7, 0.7, 0.0]),
        ("n5", "omega", [0.0, 0.0, 1.0]),
    ]
    nodes = [TextNode(id_=f"00000000-0000-0000-0000-00000000000{i + 1}", text=t, embedding=e,
                      metadata={"name": n}) for i, (n, t, e) in enumerate(docs)]
    store.add(nodes)
    return store


def _hybrid_query(store, top_k=5, alpha=0.5):
    from llama_index.core.vector_stores.types import VectorStoreQuery, VectorStoreQueryMode

    q = VectorStoreQuery(query_embedding=[1.0, 0.0, 0.0], query_str="alpha", mode=VectorStoreQueryMode.HYBRID,
                         similarity_top_k=5, sparse_top_k=5, hybrid_top_k=top_k, alpha=alpha)
    res = store.query(q)
    return [n.metadata["name"] for n in res.nodes], list(res.similarities)


class TestEndToEnd:
    def test_rrf_ranks_by_leg_ranks(self):
        names, sims = _hybrid_query(_memory_store(_cfg(HYBRID_FUSION="rrf", HYBRID_RRF_K=60)))
        # dense order: n1, n2, n4, n3, n5 ; sparse ("alpha"): n3 (tf 3), then n1 / n4 (tf 1)
        assert names[0] == "n1"  # 1st dense, top-3 sparse
        # n3 / n4 are in both legs, n2 only in the dense leg, n5 last
        assert set(names[:3]) == {"n1", "n3", "n4"}
        assert names[3] == "n2"
        assert all(0.0 < s <= 1.0 for s in sims)
        assert sims == sorted(sims, reverse=True)

    def test_rrf_respects_hybrid_top_k(self):
        names, _ = _hybrid_query(_memory_store(_cfg(HYBRID_FUSION="rrf")), top_k=2)
        assert len(names) == 2

    def test_minmax_unchanged_from_llama_default(self):
        ours, our_sims = _hybrid_query(_memory_store(_cfg(HYBRID_FUSION="minmax")))
        ref = _memory_store(None)  # no setting at all
        assert ours == _hybrid_query(ref)[0]
        assert our_sims == pytest.approx(_hybrid_query(ref)[1])
