"""
shared.retrieval -- Retriever construction shared by the MCP server and the
validation runner, so both search paths behave identically.

Hybrid fusion depth
-------------------
By default each hybrid leg (dense and sparse) fetches as many candidates as
the reranker receives (``fetch_k``).  A chunk that is, say, 15th in both
legs is then never seen by the fusion step even though it would rank in the
fused top-8.  ``HYBRID_PREFETCH_K`` lets each leg fetch more candidates
before fusion; the fused list is still cut to ``fetch_k`` so the reranker
input size (and its cost) does not change.
"""

from typing import Any, Dict, Optional


def hybrid_prefetch_k(cfg: Any, fetch_k: int) -> int:
    """Per-leg candidate count for hybrid search (never below ``fetch_k``)."""
    raw = getattr(cfg, "HYBRID_PREFETCH_K", None) if cfg is not None else None
    if not raw:
        return fetch_k
    return max(fetch_k, int(raw))


def build_retriever_kwargs(
    cfg: Any,
    fetch_k: int,
    hybrid: bool,
    alpha: Optional[float] = None,
    qdrant_filters: Any = None,
) -> Dict[str, Any]:
    """Keyword arguments for ``VectorStoreIndex.as_retriever``.

    Args:
        cfg: Loaded config module (may be None: defaults apply).
        fetch_k: Number of fused candidates handed to the reranker.
        hybrid: True for collections with sparse vectors.
        alpha: Hybrid alpha (defaults to ``HYBRID_ALPHA`` or 0.5).
        qdrant_filters: Optional Qdrant filter applied to every leg.
    """
    kwargs: Dict[str, Any] = {"similarity_top_k": fetch_k}
    if qdrant_filters is not None:
        kwargs["vector_store_kwargs"] = {"qdrant_filters": qdrant_filters}
    if not hybrid:
        return kwargs

    from llama_index.core.vector_stores.types import VectorStoreQueryMode

    if alpha is None:
        alpha = getattr(cfg, "HYBRID_ALPHA", 0.5) if cfg is not None else 0.5
    leg_k = hybrid_prefetch_k(cfg, fetch_k)
    kwargs.update(
        {
            "vector_store_query_mode": VectorStoreQueryMode.HYBRID,
            "alpha": alpha,
            "similarity_top_k": leg_k,
            "sparse_top_k": leg_k,
        }
    )
    if leg_k != fetch_k:
        kwargs["hybrid_top_k"] = fetch_k
    return kwargs
