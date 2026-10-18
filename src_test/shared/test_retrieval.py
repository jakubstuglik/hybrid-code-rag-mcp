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
