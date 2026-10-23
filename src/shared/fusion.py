"""
shared.fusion -- How the dense and sparse (BM25) hybrid legs are combined.

``HYBRID_FUSION`` selects the method (per project config):

``"minmax"`` (default)
    llama-index Relative Score Fusion, exactly the previous behaviour: each
    leg's raw scores are min-max normalised to [0, 1] and the fused score is
    ``alpha * dense + (1 - alpha) * sparse`` (a chunk missing from a leg gets
    0 for that leg).  When one leg returns nothing, the other leg's result is
    returned unchanged.

``"rrf"``
    Weighted Reciprocal Rank Fusion: only the rank of a chunk in each leg
    counts, not its raw score::

        score = (k + 1) * (alpha / (k + rank_dense) + (1 - alpha) / (k + rank_sparse))

    ranks start at 1; a chunk missing from a leg gets no term for it.
    ``k`` is ``HYBRID_RRF_K`` (default 60): larger values flatten the
    rank curve, smaller values reward the very top of each list more.
    ``alpha`` (``HYBRID_ALPHA``) weighs the dense term against the sparse
    term; 0.5 ranks exactly like classic unweighted RRF.  The ``(k + 1)``
    factor only rescales: a chunk ranked first in both legs scores 1.0, a
    chunk ranked first in one leg only scores ``alpha`` or ``1 - alpha`` --
    the same range as min-max fusion, so the reranker's additive
    bonuses and penalties keep their meaning.
"""

import math
from typing import Any, Callable, Dict, List, Optional, Tuple

FUSION_MODES = ("minmax", "rrf")
DEFAULT_FUSION = "minmax"
DEFAULT_RRF_K = 60


def resolve_hybrid_fusion(cfg: Any) -> Tuple[str, float]:
    """Validated ``(mode, k)`` from a config (``None`` -> defaults).

    Raises ValueError for an unknown ``HYBRID_FUSION`` or an invalid
    ``HYBRID_RRF_K`` (must be a finite number >= 0; checked in rrf mode only).
    """
    raw = getattr(cfg, "HYBRID_FUSION", None) if cfg is not None else None
    if raw is None:
        mode = DEFAULT_FUSION
    elif isinstance(raw, str):
        mode = raw.strip().lower()
    else:
        mode = None
    if mode not in FUSION_MODES:
        raise ValueError(
            f"HYBRID_FUSION must be one of {', '.join(repr(m) for m in FUSION_MODES)}, "
            f"got {raw!r}."
        )
    k_raw = getattr(cfg, "HYBRID_RRF_K", None) if cfg is not None else None
    if k_raw is None:
        return mode, float(DEFAULT_RRF_K)
    if mode != "rrf":
        # minmax ignores k; do not fail a working config over an unused value
        return mode, float(DEFAULT_RRF_K)
    if isinstance(k_raw, bool) or not isinstance(k_raw, (int, float)):
        raise ValueError(f"HYBRID_RRF_K must be a number >= 0, got {k_raw!r}.")
    k = float(k_raw)
    if not math.isfinite(k) or k < 0:
        raise ValueError(f"HYBRID_RRF_K must be a finite number >= 0, got {k_raw!r}.")
    return mode, k


def _ranked_ids(result: Any) -> Tuple[List[str], Dict[str, Any]]:
    """Node ids of one leg in rank order (best first) plus id -> node.

    Sorted by score descending; equal scores keep the leg's own order.  A
    node id that appears twice keeps its best (first) rank.
    """
    nodes = list(getattr(result, "nodes", None) or [])
    sims = list(getattr(result, "similarities", None) or [])
    if len(sims) != len(nodes):
        sims = [None] * len(nodes)
    order = sorted(
        range(len(nodes)),
        key=lambda i: (-(sims[i] if sims[i] is not None else -math.inf), i),
    )
    ids: List[str] = []
    by_id: Dict[str, Any] = {}
    for i in order:
        node = nodes[i]
        nid = node.node_id
        if nid in by_id:
            continue
        by_id[nid] = node
        ids.append(nid)
    return ids, by_id


def rrf_fuse(
    dense_ids: List[str],
    sparse_ids: List[str],
    alpha: float = 0.5,
    k: float = DEFAULT_RRF_K,
) -> List[Tuple[str, float]]:
    """Weighted RRF over two ranked id lists -> ``[(id, score)]`` best first.

    Ties on the fused score are broken by the better single-leg rank, then
    by first appearance (dense list before sparse list), so the result is
    deterministic.
    """
    if alpha is None:
        alpha = 0.5
    alpha = float(alpha)
    scale = k + 1.0
    scores: Dict[str, float] = {}
    best_rank: Dict[str, int] = {}
    first_seen: Dict[str, int] = {}
    for weight, ids in ((alpha, dense_ids), (1.0 - alpha, sparse_ids)):
        seen_here = set()
        for pos, nid in enumerate(ids):
            if nid in seen_here:
                continue
            seen_here.add(nid)
            rank = pos + 1
            if nid not in first_seen:
                first_seen[nid] = len(first_seen)
            scores[nid] = scores.get(nid, 0.0) + scale * weight / (k + rank)
            best_rank[nid] = min(best_rank.get(nid, rank), rank)
    return sorted(
        scores.items(), key=lambda kv: (-kv[1], best_rank[kv[0]], first_seen[kv[0]])
    )


def make_rrf_fusion(k: float = DEFAULT_RRF_K) -> Callable[..., Any]:
    """A llama-index ``HybridFusionCallable`` doing weighted RRF with this k."""

    def rrf_fusion(dense_result: Any, sparse_result: Any, alpha: Optional[float] = 0.5,
                   top_k: int = 2, **_: Any) -> Any:
        from llama_index.core.vector_stores.types import VectorStoreQueryResult

        dense_ids, dense_nodes = _ranked_ids(dense_result)
        sparse_ids, sparse_nodes = _ranked_ids(sparse_result)
        if not dense_ids and not sparse_ids:
            return VectorStoreQueryResult(nodes=None, similarities=None, ids=None)
        fused = rrf_fuse(dense_ids, sparse_ids, alpha=alpha, k=k)
        if top_k is not None and top_k > 0:
            fused = fused[:top_k]
        nodes = [dense_nodes.get(nid) or sparse_nodes[nid] for nid, _ in fused]
        return VectorStoreQueryResult(
            nodes=nodes,
            similarities=[s for _, s in fused],
            ids=[nid for nid, _ in fused],
        )

    rrf_fusion.rrf_k = k  # type: ignore[attr-defined]
    return rrf_fusion


def hybrid_fusion_fn(cfg: Any) -> Optional[Callable[..., Any]]:
    """Fusion callable for ``QdrantVectorStore(hybrid_fusion_fn=...)``.

    ``None`` for min-max: the vector store then uses llama-index's own
    relative score fusion, unchanged.
    """
    mode, k = resolve_hybrid_fusion(cfg)
    if mode == "minmax":
        return None
    return make_rrf_fusion(k)
