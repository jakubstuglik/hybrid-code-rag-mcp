"""Tests for shared/retrieval.py -- retriever kwargs and fusion depth."""

import types

from llama_index.core.vector_stores.types import VectorStoreQueryMode

from shared.retrieval import build_retriever_kwargs, hybrid_prefetch_k


def _cfg(**kw):
    return types.SimpleNamespace(**kw)


def test_default_legs_equal_fetch_k():
    kw = build_retriever_kwargs(_cfg(HYBRID_ALPHA=0.5), 8, hybrid=True)
    assert kw["similarity_top_k"] == 8 and kw["sparse_top_k"] == 8
    assert "hybrid_top_k" not in kw
    assert kw["vector_store_query_mode"] == VectorStoreQueryMode.HYBRID
    assert kw["alpha"] == 0.5


def test_prefetch_deepens_legs_but_keeps_fused_size():
    kw = build_retriever_kwargs(_cfg(HYBRID_PREFETCH_K=30), 8, hybrid=True, alpha=0.3)
    assert kw["similarity_top_k"] == 30 and kw["sparse_top_k"] == 30
    assert kw["hybrid_top_k"] == 8
    assert kw["alpha"] == 0.3


def test_prefetch_never_below_fetch_k():
    assert hybrid_prefetch_k(_cfg(HYBRID_PREFETCH_K=20), 80) == 80
    assert hybrid_prefetch_k(None, 8) == 8


def test_dense_ignores_prefetch_and_passes_filter():
    kw = build_retriever_kwargs(_cfg(HYBRID_PREFETCH_K=30), 8, hybrid=False, qdrant_filters="F")
    assert kw == {"similarity_top_k": 8, "vector_store_kwargs": {"qdrant_filters": "F"}}


# ── symbol lookup ─────────────────────────────────────────────

from shared.retrieval import (
    add_symbol_candidates,
    fetch_symbol_candidates,
    merge_symbol_candidates,
    query_symbol_names,
)


class _N:
    def __init__(self, nid):
        self.node_id = nid
        self.metadata = {}


class _NWS:
    def __init__(self, nid, score):
        self.node = _N(nid)
        self.score = score


def test_query_symbol_names_keeps_case_and_forms():
    names = query_symbol_names("Where is try_to_wake_up defined and what does struct rq hold?")
    assert "try_to_wake_up" in names and "rq" not in names  # too short
    assert query_symbol_names("How does schedule() pick a task?") == ["schedule"]
    assert "DocumentStore" in query_symbol_names("What does DocumentStore::save do?")
    assert "save" in query_symbol_names("What does DocumentStore::save do?")
    assert "page_pool" in query_symbol_names("what is struct page_pool")
    assert query_symbol_names("how are pages reclaimed") == []


def test_query_symbol_names_skips_stop_words():
    assert query_symbol_names("which function that handles timers") == []


def test_merge_symbol_candidates_dedup_and_bar_score():
    pool = [_NWS("a", 0.9), _NWS("b", 0.5), _NWS("c", 0.3)]
    extra = [_NWS("b", None), _NWS("x", None)]
    out = merge_symbol_candidates(pool, extra, top_k=2)
    assert [n.node.node_id for n in out] == ["a", "b", "c", "x"]
    assert out[-1].score == 0.5
    out = merge_symbol_candidates(pool[:], [_NWS("y", None)], top_k=8, mode="top")
    assert out[-1].score == 0.9


def test_fetch_disabled_by_default():
    assert fetch_symbol_candidates(object(), "find try_to_wake_up", _cfg()) == []


def test_add_symbol_candidates_noop_without_names():
    pool = [_NWS("a", 0.9)]
    assert add_symbol_candidates(None, pool, "how are pages reclaimed", _cfg(SYMBOL_LOOKUP_K=4), 8) is pool


def test_fetch_builds_filter_and_parses():
    calls = {}

    class Client:
        def query_points(self, **kw):
            calls.update(kw)
            return types.SimpleNamespace(points=["p1"])

    class Store:
        client = Client()
        collection_name = "c"
        dense_vector_name = "text-dense"
        enable_hybrid = True

        def parse_to_query_result(self, pts):
            from llama_index.core.schema import TextNode
            return types.SimpleNamespace(nodes=[TextNode(id_="p1", text="x")])

    out = fetch_symbol_candidates(Store(), "find try_to_wake_up", _cfg(SYMBOL_LOOKUP_K=3), query_embedding=[0.1])
    assert len(out) == 1 and out[0].node.node_id == "p1"
    assert calls["limit"] == 3 and calls["using"] == "text-dense"
    cond = calls["query_filter"].must[0]
    assert cond.key == "object_name" and cond.match.any == ["try_to_wake_up"]
