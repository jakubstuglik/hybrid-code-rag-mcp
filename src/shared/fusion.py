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

``"dbsf"``
    Distribution-Based Score Fusion.  Each leg is normalised on its own
    with the mean ``mu`` and the population standard deviation ``sigma``
    (divisor ``n``, not ``n - 1``) of that leg's finite scores::

        norm = clip01( (s - (mu - 3*sigma)) / (6*sigma) )

    When ``sigma`` is 0 (a single score, or every finite score on the leg
    equal), every candidate on that leg is normalised to 1.0.  The fused
    score is ``alpha * dense_norm + (1 - alpha) * sparse_norm``.  A chunk
    missing from a leg contributes 0 for that leg.  An entirely empty leg
    uses that same rule: the other leg is still normalised and weighted,
    so scores stay in [0, 1] for alpha in [0, 1].  Min-max fusion instead
    returns the other leg's raw scores unchanged.  Raw BM25 scores sit
    outside [0, 1], and the reranker adds fixed bonuses on the assumption
    that fusion scores are inside that range, so DBSF keeps the weighted
    formula for an empty leg too.  ``HYBRID_RRF_K`` is ignored.
"""

import math
import numbers
from typing import Any, Callable, Dict, List, Optional, Tuple

FUSION_MODES = ("minmax", "rrf", "dbsf")
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
        # minmax and dbsf ignore k; do not fail a working config over an unused value
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


def _finite_score(score: Any) -> Optional[float]:
    """Finite real score, or None when the value cannot be used.

    ``None``, booleans, non-numeric values, NaN and infinities are
    missing scores: the candidate is left out of that leg.
    """
    if isinstance(score, bool) or not isinstance(score, numbers.Real):
        return None
    value = float(score)
    if not math.isfinite(value):
        return None
    return value


def _clip01(value: float) -> float:
    """Clip to [0, 1].  NaN and negative infinity become 0; +infinity becomes 1."""
    if not value >= 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _prepare_leg(pairs: Any) -> List[Tuple[Any, float, int]]:
    """``(id, best finite score, 1-based rank)`` best first.

    Duplicate ids keep the highest finite score.  Equal scores keep the
    earliest occurrence, and that order is the rank order.  Malformed
    rows and non-finite scores are skipped.
    """
    if not pairs or isinstance(pairs, (str, bytes)):
        return []
    best: Dict[Any, Tuple[float, int]] = {}
    for index, item in enumerate(pairs):
        if (
            isinstance(item, (str, bytes))
            or not isinstance(item, (tuple, list))
            or len(item) != 2
        ):
            continue
        nid, raw = item
        if nid is None:
            continue
        score = _finite_score(raw)
        if score is None:
            continue
        current = best.get(nid)
        if current is None or score > current[0]:
            best[nid] = (score, index)
    ordered = sorted(best.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
    return [(nid, score, rank) for rank, (nid, (score, _index)) in enumerate(ordered, start=1)]


def _normalise_leg(scores: List[float]) -> List[float]:
    """DBSF normalisation of one leg's finite scores, in the given order.

    Population standard deviation (divisor ``n``).  ``sigma == 0`` -- one
    score, or a single score level -- maps every score to 1.0.
    """
    count = len(scores)
    if count == 0:
        return []
    mean = sum(scores) / count
    variance = sum((score - mean) ** 2 for score in scores) / count
    if variance <= 0.0:
        return [1.0] * count
    sigma = math.sqrt(variance)
    centre = mean - 3.0 * sigma
    width = 6.0 * sigma
    return [_clip01((score - centre) / width) for score in scores]


def dbsf_fuse(
    dense: Optional[List[Tuple[Any, Any]]],
    sparse: Optional[List[Tuple[Any, Any]]],
    alpha: Optional[float] = 0.5,
) -> List[Tuple[Any, float]]:
    """Distribution-based score fusion of two ``(id, score)`` lists.

    See the module docstring for the formula, the ``sigma == 0`` rule and
    why an empty leg is weighted as zeros instead of returned raw.

    Ties on the fused score break by the better single-leg rank (1 is
    best), then by first appearance (dense rank order, then sparse rank
    order).  ``alpha is None`` means 0.5.

    Returns ``[(id, score)]`` best first.  Both legs empty (or with no
    finite scores) returns ``[]``.
    """
    if alpha is None:
        alpha = 0.5
    alpha = float(alpha)
    dense_leg = _prepare_leg(dense)
    sparse_leg = _prepare_leg(sparse)
    dense_norm = _normalise_leg([score for _nid, score, _rank in dense_leg])
    sparse_norm = _normalise_leg([score for _nid, score, _rank in sparse_leg])

    scores: Dict[Any, float] = {}
    best_rank: Dict[Any, int] = {}
    first_seen: Dict[Any, int] = {}
    for weight, leg, norms in (
        (alpha, dense_leg, dense_norm),
        (1.0 - alpha, sparse_leg, sparse_norm),
    ):
        for (nid, _score, rank), norm in zip(leg, norms):
            if nid not in first_seen:
                first_seen[nid] = len(first_seen)
            scores[nid] = scores.get(nid, 0.0) + weight * norm
            best_rank[nid] = min(best_rank.get(nid, rank), rank)
    return sorted(
        scores.items(), key=lambda kv: (-kv[1], best_rank[kv[0]], first_seen[kv[0]])
    )


def _leg_pairs_and_nodes(result: Any) -> Tuple[List[Tuple[Any, Any]], Dict[Any, Any]]:
    """``(id, score)`` pairs in leg order, and id -> node.

    The node kept for an id is the one with the highest finite score
    (earliest occurrence on a tie).  A missing similarities list, or one
    whose length differs from ``nodes``, is treated as every score missing.
    """
    nodes = list(getattr(result, "nodes", None) or [])
    sims = getattr(result, "similarities", None)
    if sims is None or len(sims) != len(nodes):
        sim_list: List[Any] = [None] * len(nodes)
    else:
        sim_list = list(sims)
    pairs: List[Tuple[Any, Any]] = []
    by_id: Dict[Any, Any] = {}
    best: Dict[Any, float] = {}
    for node, score in zip(nodes, sim_list):
        nid = node.node_id
        pairs.append((nid, score))
        finite = _finite_score(score)
        if nid not in by_id:
            by_id[nid] = node
            if finite is not None:
                best[nid] = finite
            continue
        if finite is not None and (nid not in best or finite > best[nid]):
            by_id[nid] = node
            best[nid] = finite
    return pairs, by_id


def make_dbsf_fusion() -> Callable[..., Any]:
    """A llama-index ``HybridFusionCallable`` doing distribution-based fusion."""

    def dbsf_fusion(dense_result: Any, sparse_result: Any, alpha: Optional[float] = 0.5,
                    top_k: int = 2, **_: Any) -> Any:
        from llama_index.core.vector_stores.types import VectorStoreQueryResult

        dense_pairs, dense_nodes = _leg_pairs_and_nodes(dense_result)
        sparse_pairs, sparse_nodes = _leg_pairs_and_nodes(sparse_result)
        fused = dbsf_fuse(dense_pairs, sparse_pairs, alpha=alpha)
        if not fused:
            return VectorStoreQueryResult(nodes=None, similarities=None, ids=None)
        if top_k is not None and top_k > 0:
            fused = fused[:top_k]
        nodes = [dense_nodes.get(nid) or sparse_nodes[nid] for nid, _score in fused]
        return VectorStoreQueryResult(
            nodes=nodes,
            similarities=[score for _nid, score in fused],
            ids=[nid for nid, _score in fused],
        )

    dbsf_fusion.fusion_mode = "dbsf"  # type: ignore[attr-defined]
    return dbsf_fusion


def hybrid_fusion_fn(cfg: Any) -> Optional[Callable[..., Any]]:
    """Fusion callable for ``QdrantVectorStore(hybrid_fusion_fn=...)``.

    ``None`` for min-max: the vector store then uses llama-index's own
    relative score fusion, unchanged.  ``"rrf"`` and ``"dbsf"`` return a
    callable.
    """
    mode, k = resolve_hybrid_fusion(cfg)
    if mode == "minmax":
        return None
    if mode == "dbsf":
        return make_dbsf_fusion()
    return make_rrf_fusion(k)
