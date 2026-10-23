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

Query alpha
-----------
``retriever_kwargs_for_query`` is the alpha decision for both paths.
``HYBRID_ALPHA_MODE = "fixed"`` (the default) keeps today's kwargs:
``HYBRID_ALPHA`` for every query, or ``base_alpha`` when the validation
runner passes an ``--alpha`` override. ``"adaptive"`` passes the per-query
alpha from ``shared.query_shape``. A dense collection skips that choice.
``open_query_retriever`` builds a new retriever for the call. It does not
cache one and it does not write alpha onto a retriever another query is
using, so concurrent adaptive queries stay independent. The MCP server and
the validation runner both go through these helpers.
"""

from typing import Any, Dict, List, Optional, Tuple


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


def retriever_kwargs_for_query(
    cfg: Any,
    fetch_k: int,
    hybrid: bool,
    query: str,
    qdrant_filters: Any = None,
    base_alpha: Optional[float] = None,
) -> Tuple[Dict[str, Any], Optional[str], str]:
    """Retriever kwargs for one query, plus ``(query_shape, alpha_mode)``.

    ``query_shape`` is set only for a hybrid collection in adaptive mode.
    Fixed mode and dense collections leave it ``None``.

    Fixed mode passes ``base_alpha`` through when the caller has one (the
    validation ``--alpha`` override) and otherwise lets
    ``build_retriever_kwargs`` read ``HYBRID_ALPHA`` itself. Adaptive mode
    passes the class alpha. ``base_alpha`` replaces ``HYBRID_ALPHA`` as the
    mixed / natural fallback; ``HYBRID_ALPHA_IDENT`` is unchanged.

    A dense collection ignores alpha mode. The kwargs match
    ``build_retriever_kwargs(..., hybrid=False)``.
    """
    from shared.query_shape import alpha_for_query, resolve_hybrid_alpha_mode

    mode = resolve_hybrid_alpha_mode(cfg)
    if not hybrid:
        kwargs = build_retriever_kwargs(
            cfg, fetch_k, hybrid=False, qdrant_filters=qdrant_filters
        )
        return kwargs, None, mode
    if mode != "adaptive":
        if base_alpha is None:
            kwargs = build_retriever_kwargs(
                cfg, fetch_k, hybrid=True, qdrant_filters=qdrant_filters
            )
        else:
            kwargs = build_retriever_kwargs(
                cfg,
                fetch_k,
                hybrid=True,
                alpha=base_alpha,
                qdrant_filters=qdrant_filters,
            )
        return kwargs, None, mode
    shape, used = alpha_for_query(cfg, query, base_alpha=base_alpha)
    kwargs = build_retriever_kwargs(
        cfg,
        fetch_k,
        hybrid=True,
        alpha=used,
        qdrant_filters=qdrant_filters,
    )
    return kwargs, shape, mode


def open_query_retriever(
    index: Any,
    cfg: Any,
    query: str,
    fetch_k: int,
    hybrid: bool,
    qdrant_filters: Any = None,
    base_alpha: Optional[float] = None,
) -> Tuple[Any, Dict[str, Any], Optional[str], str]:
    """Build a new retriever for this query.

    Each call calls ``index.as_retriever`` once. Nothing is cached and no
    retriever returned earlier is updated, so concurrent queries can carry
    different alphas. Leg depth and the branch filter also vary per call.
    """
    kwargs, shape, mode = retriever_kwargs_for_query(
        cfg,
        fetch_k,
        hybrid,
        query,
        qdrant_filters=qdrant_filters,
        base_alpha=base_alpha,
    )
    return index.as_retriever(**kwargs), kwargs, shape, mode


def retriever_ready_message(
    hybrid: bool,
    kwargs: Dict[str, Any],
    alpha_mode: str,
    query_shape: Optional[str] = None,
) -> str:
    """MCP log line once the retriever for this query exists."""
    if not hybrid:
        return "[MCP] retriever ready (dense)"
    shape_bit = f", shape={query_shape}" if query_shape else ""
    return (
        f"[MCP] retriever ready (hybrid, alpha={kwargs['alpha']}, "
        f"mode={alpha_mode}{shape_bit}, legs={kwargs['sparse_top_k']})"
    )


# ────────────────────────────────────────────────────────────────────
# Exact symbol lookup (extra candidate leg)
# ────────────────────────────────────────────────────────────────────
#
# Neither embeddings nor BM25 reliably put the chunk that *defines* a named
# identifier into the candidate pool: a long body is a weak dense match and
# BM25 favours short chunks that merely mention the name many times.  When a
# query names code identifiers, the chunks whose reader metadata declares
# exactly that name are fetched directly by a payload filter and added to the
# pool; the reranker then decides (its declared-name rules apply as usual).

import re as _re

# "struct foo", "enum bar_flags", "class Baz", "macro FOO" ...
_KEYWORD_TARGET = _re.compile(
    r"\b(?:struct|class|enum|union|interface|record|trait|typedef|macro|"
    r"function|method|procedure|func)\s+`?([A-Za-z_][\w$]*)"
)
# "foo()" -- a call form marks even an all-lowercase word as code
_CALL_FORM = _re.compile(r"(?<![\w$.])([A-Za-z_][\w$]{2,})\(\)")
# `name` in backticks
_BACKTICKED = _re.compile(r"`([A-Za-z_][\w$]*)`")

_SYMBOL_STOP_WORDS = frozenset(
    "the that this which what where when with from into for and how does are "
    "used uses using type types defined define definition declared".split()
)


_PROFILE_CACHE: dict = {}


def _profiles_for(cfg: Any):
    """Rerank profiles of a project config (cached per config object)."""
    if cfg is None:
        return None
    hit = _PROFILE_CACHE.get(id(cfg))
    if hit is not None and hit[0] is cfg:
        return hit[1]
    try:
        from shared.reranker import rerank_profiles_for_config

        pset = rerank_profiles_for_config(cfg)
    except Exception:  # noqa: BLE001 - lookup must never break search
        pset = None
    _PROFILE_CACHE[id(cfg)] = (cfg, pset)
    return pset


def query_symbol_names(query: str, profiles: Any = None) -> List[str]:
    """Identifiers a query names explicitly, in their original case.
    ``profiles`` adds the identifier shapes of the active rerank profiles."""
    from shared.reranker import extract_code_identifiers

    names: List[str] = []
    for owner, name in extract_code_identifiers(query or "", keep_case=True, profiles=profiles):
        if owner and len(owner) >= 3:
            names.append(owner)
        names.append(name)
    for pat in (_KEYWORD_TARGET, _CALL_FORM, _BACKTICKED):
        for m in pat.finditer(query or ""):
            name = m.group(1)
            if len(name) >= 3 and name.lower() not in _SYMBOL_STOP_WORDS:
                names.append(name)
    seen = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def symbol_lookup_k(cfg: Any) -> int:
    return int(getattr(cfg, "SYMBOL_LOOKUP_K", 0) or 0) if cfg is not None else 0


def fetch_symbol_candidates(
    vector_store: Any,
    query: str,
    cfg: Any,
    query_embedding: Optional[List[float]] = None,
    qdrant_filters: Any = None,
) -> list:
    """Chunks whose ``SYMBOL_LOOKUP_FIELDS`` payload equals a name from the query.

    Returns NodeWithScore objects with score None (the caller assigns one).
    Ordered by dense similarity when ``query_embedding`` is given.  Works
    without a payload index (Qdrant then filters by scanning); collections
    created by the indexer get a keyword index on the field.
    """
    limit = symbol_lookup_k(cfg)
    if limit <= 0 or vector_store is None:
        return []
    names = query_symbol_names(query, _profiles_for(cfg))
    if not names:
        return []
    from qdrant_client import models as qm
    from llama_index.core.schema import NodeWithScore

    fields = getattr(cfg, "SYMBOL_LOOKUP_FIELDS", None) or ("object_name",)
    if isinstance(fields, str):
        fields = (fields,)
    conds = [qm.FieldCondition(key=f, match=qm.MatchAny(any=names)) for f in fields]
    if len(conds) == 1:
        must: list = conds
    else:
        must = [qm.Filter(should=conds)]
    if qdrant_filters is not None:
        must.append(qdrant_filters)
    flt = qm.Filter(must=must)
    client = vector_store.client
    collection = vector_store.collection_name
    try:
        if query_embedding is not None:
            using = getattr(vector_store, "dense_vector_name", None)
            if not getattr(vector_store, "enable_hybrid", False):
                using = None
            points = client.query_points(
                collection_name=collection,
                query=query_embedding,
                using=using,
                query_filter=flt,
                limit=limit,
                with_payload=True,
            ).points
        else:
            points, _ = client.scroll(
                collection_name=collection,
                scroll_filter=flt,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
    except Exception as exc:  # lookup is best-effort; never break search
        from shared.log import log_warn

        log_warn(f"[retrieval] symbol lookup failed: {exc}")
        return []
    if not points:
        return []
    result = vector_store.parse_to_query_result(points)
    return [NodeWithScore(node=n, score=None) for n in result.nodes]


def merge_symbol_candidates(nodes: list, extra: list, top_k: int, mode: str = "bar") -> list:
    """Append symbol-lookup candidates that are not already in the pool.

    Their score is the pool's entry bar (score of the ``top_k``-th
    candidate, ``mode="bar"``) or its best score (``mode="top"``), so
    they only reach the top when the reranker's own rules favour them.
    """
    if not extra:
        return nodes
    have = {n.node.node_id for n in nodes}
    scores = sorted((n.score or 0.0 for n in nodes), reverse=True)
    if not scores:
        base = 1.0
    elif mode == "top":
        base = scores[0]
    else:
        base = scores[min(len(scores), max(top_k, 1)) - 1]
    out = list(nodes)
    for n in extra:
        if n.node.node_id in have:
            continue
        have.add(n.node.node_id)
        n.score = base
        out.append(n)
    return out


def symbol_lookup_applies(index: Any, query: str, cfg: Any) -> bool:
    """True when the symbol-lookup leg would run for ``query`` on ``index``:
    ``SYMBOL_LOOKUP_K`` > 0, the query names an identifier and the index is
    backed by a Qdrant vector store."""
    if symbol_lookup_k(cfg) <= 0 or not query_symbol_names(query, _profiles_for(cfg)):
        return False
    vector_store = getattr(index, "vector_store", None)
    return vector_store is not None and hasattr(vector_store, "parse_to_query_result")


def add_symbol_candidates(index: Any, nodes: list, query: str, cfg: Any, top_k: int,
                          qdrant_filters: Any = None,
                          query_embedding: Optional[List[float]] = None) -> list:
    """Run the symbol-lookup leg for ``index`` (a VectorStoreIndex) and merge
    its candidates into ``nodes``.  No-op unless ``SYMBOL_LOOKUP_K`` > 0 and
    the query names an identifier.

    Pass ``query_embedding`` (the one the main retrieval used) to avoid a
    second embedding request; without it the query is embedded here.
    """
    if not symbol_lookup_applies(index, query, cfg):
        return nodes
    embedding = query_embedding
    if embedding is None:
        try:
            embedding = index._embed_model.get_query_embedding(query)
        except Exception:
            embedding = None
    extra = fetch_symbol_candidates(
        index.vector_store, query, cfg, query_embedding=embedding, qdrant_filters=qdrant_filters
    )
    mode = getattr(cfg, "SYMBOL_LOOKUP_SCORE", "bar")
    return merge_symbol_candidates(nodes, extra, top_k, mode=mode)


async def aretrieve_with_symbol_lookup(
    index: Any,
    retriever: Any,
    query: str,
    cfg: Any,
    qdrant_filters: Any = None,
) -> Tuple[list, list]:
    """Main retrieval plus the symbol-lookup leg, sharing one query embedding.

    The query is embedded once (exactly as the retriever would do it) and
    the embedding is handed to both the retriever and the symbol lookup;
    the lookup's Qdrant request runs concurrently with the main retrieval.
    Returns ``(nodes, symbol_candidates)``; merge them with
    ``merge_symbol_candidates`` after any post-processing of ``nodes``
    (the result is the same as running ``add_symbol_candidates`` afterwards,
    minus one embedding request and one sequential Qdrant round trip).
    """
    if not symbol_lookup_applies(index, query, cfg):
        return await retriever.aretrieve(query), []

    import asyncio

    from llama_index.core.schema import QueryBundle

    embedding = None
    embed_model = getattr(index, "_embed_model", None)
    if embed_model is not None:
        try:
            embedding = await embed_model.aget_agg_embedding_from_queries([query])
        except Exception:
            embedding = None
    if embedding is None:
        # Let the retriever embed (and raise) as usual; the lookup then
        # orders its candidates without dense similarity, as before.
        bundle: Any = query
    else:
        bundle = QueryBundle(query_str=query, embedding=embedding)
    lookup = asyncio.to_thread(
        fetch_symbol_candidates,
        index.vector_store,
        query,
        cfg,
        embedding,
        qdrant_filters,
    )
    nodes, extra = await asyncio.gather(retriever.aretrieve(bundle), lookup)
    return nodes, extra
