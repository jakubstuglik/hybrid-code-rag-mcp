# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0
"""One retrieval pipeline for the MCP search tool and the validation runner.

``asearch`` owns the path from ``begin_query_rank`` through ``rank.finish``:
the branch filter, overview and branch over-fetch, the retriever, sparse
query precompute, symbol lookup, branch dedup and rerank. Callers format
the nodes themselves. The same config, query and ``top_k`` therefore return
the same ordered nodes and scores from the tool and from ``run_query``.

``verbose`` only adds rerank log lines. It does not change scores or order.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Callable, Optional

# ``timeout`` omitted: read ``MCP_QUERY_TIMEOUT_SECONDS``, as the MCP tool did.
_TIMEOUT_UNSET = object()


def _has_git_sources(cfg: Any) -> bool:
    """True when config lists at least one ``git_repo`` source."""
    return any(
        isinstance(entry, dict) and entry.get("type") == "git_repo"
        for entry in (getattr(cfg, "SOURCE_DIRS", None) or [])
    )


def _state_doc(loaded: Any) -> Any:
    """Index-state document from a provider result.

    ``IndexStateCache.state`` returns ``(document, source)``. A provider
    may also return the document itself.
    """
    if isinstance(loaded, tuple):
        return loaded[0] if loaded else None
    return loaded


def _state_doc_from_index(index: Any, cfg: Any) -> Any:
    """Published index state on the index's Qdrant client, or None."""
    store = getattr(index, "vector_store", None)
    client = getattr(store, "client", None) if store is not None else None
    collection = getattr(cfg, "COLLECTION_NAME", None)
    if client is None or not collection:
        return None
    from shared.index_meta import read_index_state

    try:
        doc, _source = read_index_state(client, collection)
    except Exception:  # noqa: BLE001 — a missing client must not break search
        return None
    return doc


def _default_tombstones(index: Any, cfg: Any, feature_branch: str) -> list:
    """Overlay tombstones: Qdrant state when the index has a client, else the manifest."""
    from shared.branch_dedup import get_branch_tombstones

    def fallback() -> list:
        return list(get_branch_tombstones(feature_branch, cfg) or [])

    store = getattr(index, "vector_store", None)
    client = getattr(store, "client", None) if store is not None else None
    collection = getattr(cfg, "COLLECTION_NAME", None)
    if client is None or not collection:
        return fallback()
    from shared.index_meta import IndexStateCache, serving_tombstones

    cache = IndexStateCache(lambda: client, collection, ttl_s=0.0)
    return list(serving_tombstones(cache, feature_branch, fallback) or [])


def _emit(log_fn: Optional[Callable[[str], None]], message: str) -> None:
    if log_fn is not None:
        log_fn(message)


def _resolve_timeout(timeout: Any) -> Optional[float]:
    """Seconds for ``asyncio.wait_for``, or None when retrieval is not limited.

    The default reads ``MCP_QUERY_TIMEOUT_SECONDS`` (empty means no limit).
    Pass ``None`` to ignore the variable. ``0`` is the same as unset: the
    MCP tool treated it as false and did not wrap the retrieval.
    """
    if timeout is _TIMEOUT_UNSET:
        raw = os.getenv("MCP_QUERY_TIMEOUT_SECONDS", "")
        return float(raw) if raw else None
    return timeout


async def _resolve_main_branch(
    index: Any,
    cfg: Any,
    state_provider: Optional[Callable[[], Any]],
) -> str:
    """Main-branch label the MCP tool uses for an empty ``branch`` argument.

    A ``git_repo`` source supplies the name (``get_main_branch_name``).
    A serving-only config uses the label the indexer published
    (``main_branch_from_state``), then the same fallback.
    """
    from shared.branch_dedup import get_main_branch_name
    from shared.index_meta import main_branch_from_state

    main_branch = get_main_branch_name(cfg)
    if _has_git_sources(cfg):
        return main_branch
    if state_provider is not None:
        loaded = await asyncio.to_thread(state_provider)
    else:
        loaded = await asyncio.to_thread(_state_doc_from_index, index, cfg)
    return main_branch_from_state(_state_doc(loaded)) or main_branch


async def _load_tombstones(
    index: Any,
    cfg: Any,
    feature_branch: str,
    tombstones_for: Optional[Callable[..., Any]],
) -> list:
    """Tombstones for one overlay. Sync providers run off the event loop."""
    if tombstones_for is None:
        return await asyncio.to_thread(_default_tombstones, index, cfg, feature_branch)
    if asyncio.iscoroutinefunction(tombstones_for):
        found = await tombstones_for(feature_branch)
    else:
        found = await asyncio.to_thread(tombstones_for, feature_branch)
    return list(found or [])


async def asearch(
    index: Any,
    query: str,
    *,
    cfg: Any,
    top_k: int = 8,
    hybrid: bool,
    base_alpha: Optional[float] = None,
    profiles: Any = None,
    branch: str = "",
    state_provider: Optional[Callable[[], Any]] = None,
    tombstones_for: Optional[Callable[..., Any]] = None,
    timeout: Any = _TIMEOUT_UNSET,
    verbose: bool = False,
    log: Optional[Callable[[str], None]] = None,
    started_at: Optional[float] = None,
) -> list:
    """Retrieve and rerank one query the way the MCP search tool does.

    Args:
        index: LlamaIndex ``VectorStoreIndex`` (or a test double with
            ``as_retriever``).
        query: Query text.
        cfg: Project config. Required. Rerank profiles, the branch filter,
            hybrid alpha and symbol lookup all come from it.
        top_k: Results after rerank.
        hybrid: True when the collection has a sparse leg.
        base_alpha: Hybrid alpha override. ``None`` (the MCP tool) uses
            ``HYBRID_ALPHA``. In fixed mode that number is the alpha for
            every query. In adaptive mode it is the mixed / natural
            fallback; ``HYBRID_ALPHA_IDENT`` is unchanged. Passing the
            config's ``HYBRID_ALPHA`` selects the same alpha as ``None``.
        profiles: Active rerank profiles. ``None`` means
            ``rerank_profiles_for_config(cfg)``, never every registered
            profile. An empty list is left as given.
        branch: Overlay name. Empty searches the main branch only (and
            chunks with no branch). A non-empty name over-fetches, keeps
            the overlay copy of a file and drops tombstones. Symbol-lookup
            hits follow that same dedup.
        state_provider: Sync callable returning the published index-state
            document, or ``(document, source)`` as
            ``IndexStateCache.state`` does. Used only when ``cfg`` has no
            ``git_repo`` source. ``None`` reads the state from
            ``index.vector_store.client`` when that client exists.
        tombstones_for: Callable ``(overlay_name) -> list[str]``, sync or
            async. The MCP server passes its cached tombstone lookup.
            ``None`` uses Qdrant state, then the overlay manifest.
        timeout: Seconds for the retrieval await. Omit to read
            ``MCP_QUERY_TIMEOUT_SECONDS``. ``None`` disables the limit.
        verbose: Passed to ``rank.finish``. Log lines only.
        log: Optional ``log(message)`` for the MCP progress lines. The
            lines keep the ``[MCP]`` prefix. The branch-dedup line also
            counts symbol hits dropped for the overlay.
        started_at: ``time.perf_counter`` value for the "retrieved N nodes"
            line. The MCP tool passes the timestamp from the start of the
            request so the line still includes index setup.

    Returns:
        Reranked ``NodeWithScore`` objects, trimmed to ``top_k``.

    Raises:
        ValueError: If ``cfg`` is None, or a config value the rank step
            validates is illegal.
    """
    if cfg is None:
        raise ValueError(
            "cfg is required so retrieval matches the MCP search tool "
            "(rerank profiles, branch filter, hybrid alpha and symbol lookup)"
        )

    if profiles is None:
        from shared.reranker import rerank_profiles_for_config

        profiles = rerank_profiles_for_config(cfg)

    origin = time.perf_counter() if started_at is None else started_at
    limit = _resolve_timeout(timeout)

    from shared.branch_dedup import (
        build_branch_filter,
        dedup_branch_results,
        filter_symbol_candidates,
    )

    main_branch = await _resolve_main_branch(index, cfg, state_provider)
    feature_branch = branch.strip() if branch else ""
    qdrant_filter = build_branch_filter(
        main_branch=main_branch,
        feature_branch=feature_branch or None,
    )
    _emit(
        log,
        f"[MCP] branch filter: main={main_branch}, feature={feature_branch or 'none'}",
    )

    # Over-fetch for overview queries so the reranker has more candidates.
    # The cross-encoder pool (when a model is set) widens the fused size
    # and never shrinks the heuristic fetch. Branch over-fetch is applied
    # after that, so dedup still leaves the widened pool to be scored.
    from shared.cross_encoder import begin_query_rank

    rank = begin_query_rank(cfg, query, top_k, profiles)
    fetch_k = rank.fetch_k
    if rank.base_fetch_k != top_k:
        _emit(
            log,
            f"[MCP] overview query detected, over-fetching {rank.base_fetch_k} "
            f"candidates (desired {top_k})",
        )
    if rank.enabled and rank.fetch_k != rank.base_fetch_k:
        _emit(
            log,
            f"[MCP] cross-encoder pool {rank.fetch_k} "
            f"(heuristic fetch {rank.base_fetch_k})",
        )

    # When a feature branch is specified, over-fetch 2x for dedup headroom.
    branch_overfetch = 1
    if feature_branch:
        branch_overfetch = 2
        fetch_k = fetch_k * branch_overfetch
        _emit(log, f"[MCP] branch over-fetch: {fetch_k} candidates")

    # Hybrid alpha: fixed mode reads HYBRID_ALPHA inside
    # build_retriever_kwargs unless base_alpha is set (the validation
    # --alpha override). Adaptive mode passes this query's alpha. A new
    # retriever is built either way; a shared retriever's alpha is never
    # written.
    from shared.retrieval import open_query_retriever, retriever_ready_message

    retriever, retriever_kwargs, query_shape, alpha_mode = open_query_retriever(
        index,
        cfg,
        query,
        fetch_k,
        hybrid=bool(hybrid),
        qdrant_filters=qdrant_filter,
        base_alpha=base_alpha,
    )
    _emit(
        log,
        retriever_ready_message(bool(hybrid), retriever_kwargs, alpha_mode, query_shape),
    )

    # Main retrieval and the exact symbol lookup share one query embedding
    # and run concurrently. With an overlay, both lists are deduped together
    # before the symbol hits are scored and merged.
    from shared.retrieval import aretrieve_with_symbol_lookup, merge_symbol_candidates

    if hybrid:
        store = getattr(index, "vector_store", None)
        if store is not None:
            # BM25 query encoding in a worker thread (aquery would run it on
            # the event loop); same encoder, same result.
            from qdrant.vector_store import precompute_sparse_query

            await precompute_sparse_query(store, query)
    retrieval = aretrieve_with_symbol_lookup(
        index, retriever, query, cfg, qdrant_filter
    )
    if limit:
        nodes, symbol_extra = await asyncio.wait_for(retrieval, timeout=limit)
    else:
        nodes, symbol_extra = await retrieval

    _emit(log, f"[MCP] retrieved {len(nodes)} nodes in {time.perf_counter() - origin:.2f}s")

    if feature_branch:
        tombstones = await _load_tombstones(index, cfg, feature_branch, tombstones_for)
        pre_dedup_count = len(nodes)
        symbol_before = len(symbol_extra)
        # Union decision first, then the same trim the main pool used before.
        # Symbol hits stay unscored until merge_symbol_candidates reads the bar.
        symbol_extra = filter_symbol_candidates(
            nodes, symbol_extra, feature_branch, tombstones
        )
        # Dedup wants the desired count BEFORE reranker trims it.
        dedup_target = top_k * (fetch_k // (top_k * branch_overfetch) if top_k else 1)
        # Use a generous target so the reranker still has candidates.
        dedup_target = max(dedup_target, fetch_k // branch_overfetch)
        nodes = dedup_branch_results(
            nodes,
            feature_branch=feature_branch,
            tombstones=tombstones,
            desired_top_k=dedup_target,
        )
        _emit(
            log,
            f"[MCP] branch dedup: {pre_dedup_count} -> {len(nodes)} "
            f"(tombstones={len(tombstones)}, "
            f"symbol_dropped={symbol_before - len(symbol_extra)})",
        )

    nodes = merge_symbol_candidates(
        nodes,
        symbol_extra,
        top_k,
        mode=getattr(cfg, "SYMBOL_LOOKUP_SCORE", "bar"),
    )
    # Off the event loop: the heuristic is pure Python and the
    # cross-encoder (when enabled) runs ONNX in this same thread.
    return await asyncio.to_thread(rank.finish, nodes, verbose=verbose)


def search(index: Any, query: str, **kwargs: Any) -> list:
    """Run :func:`asearch` from synchronous code.

    The caller must not already be inside an event loop. ``run_query``
    uses this wrapper.
    """
    return asyncio.run(asearch(index, query, **kwargs))
