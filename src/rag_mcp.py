# rag_mcp.py
"""MCP server for RAG search. Tool name, description, and server name
are driven by config values (MCP_TOOL_NAME, MCP_TOOL_DESCRIPTION,
MCP_SERVER_NAME, MCP_HOST, MCP_PORT)."""

import os
import sys

# Ensure the project root (for `import config`) and src/ (for `import shared`,
# `import config_loader`, etc.) are on sys.path when this script is invoked
# directly as `python src/rag_mcp.py` from the project root.
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
for _p in (_root, _here):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import argparse
import asyncio
import logging
import time
from pathlib import Path
from typing import Annotated

import config_loader
from shared.log import configure as log_configure, log, log_error
from shared.qdrant_client import get_qdrant_client
from shared.docker_utils import ensure_qdrant_running, ensure_tei_running
from shared.index_meta import ProvenanceMismatchError  # noqa: E402


def _fatal_provenance(config, exc: Exception, *, hard: bool = False) -> None:
    """Log the mismatch and stop the process (``hard``: from a request task)."""
    log_error(
        "[MCP] FATAL: embedding provenance mismatch for collection "
        f"'{getattr(config, 'COLLECTION_NAME', '?')}':\n{exc}\n"
        "  Queries would be embedded differently from the indexed documents.\n"
        "  Fix MODEL_NAME / EMBEDDING_QUANT / EMBEDDING_URL / prefixes to match the "
        "indexer, or re-index the collection with this setup."
    )
    if hard:
        # --lazy-init: raised inside a request; SystemExit would only end the task.
        os._exit(1)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        help="Config name (e.g., 'self-index') or path to config file",
    )
    parser.add_argument(
        "--lazy-init",
        action="store_true",
        help="Defer loading the embed model/index until first request.",
    )
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "stdio"],
        default="streamable-http",
        help="MCP transport mode (default: streamable-http).",
    )
    from shared.version import __version__

    parser.add_argument(
        "--version",
        action="version",
        version=f"hybrid-code-rag-mcp {__version__}",
    )
    args = parser.parse_args()

    # When using stdio transport, stdout is the JSON-RPC channel.
    # Save the real stdout for FastMCP, then redirect sys.stdout to
    # stderr so stray print() calls from third-party libraries
    # (e.g., HuggingFace, sentence-transformers) cannot corrupt the
    # protocol stream.
    _real_stdout = sys.stdout
    if args.transport == "stdio":
        sys.stdout = sys.stderr

    # All log output goes to stderr (safe for both stdio and HTTP transport)
    log_configure(stream=sys.stderr)
    log(f"[MCP] hybrid-code-rag-mcp {__version__}")

    # Suppress noisy INFO logging from httpx (Qdrant HTTP client) and
    # sentence_transformers — only warnings and errors should reach stderr.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    # Load config before anything else so all values are available
    config = config_loader.get_config(config_path=args.config)

    # Rerank profiles of the readers that index this project's files
    # (or the config's RERANK_PROFILES override).
    from shared.reranker import rerank_profiles_for_config

    rerank_profiles = rerank_profiles_for_config(config)
    log(f"[MCP] rerank profiles: {', '.join(rerank_profiles.names)}")

    # Ensure Qdrant is running (auto-start Docker for local mode)
    if not ensure_qdrant_running(config, stderr_prefix="[MCP]"):
        log("[MCP] ERROR: Qdrant is not available. Cannot start MCP server.")
        sys.exit(1)

    # Ensure TEI is running if configured (auto-start Docker container).
    # EMBEDDING_MODE = "remote" ignores every TEI setting.
    from shared.embedding import resolve_embedding_mode, uses_tei_container

    log(f"[MCP] embedding mode: {resolve_embedding_mode(config)}")
    if uses_tei_container(config):
        if not ensure_tei_running(config):
            log(
                "[MCP] ERROR: TEI embedding server is not available. Cannot start MCP server."
            )
            sys.exit(1)

    # ── FastMCP server (config-driven) ────────────────────────────
    from mcp.server.fastmcp import FastMCP
    from llama_index.core import VectorStoreIndex
    from shared.embedding import get_embed_model

    server_name = getattr(config, "MCP_SERVER_NAME", "rag-server")
    host = getattr(config, "MCP_HOST", "0.0.0.0")
    port = getattr(config, "MCP_PORT", 8123)
    tool_name = getattr(config, "MCP_TOOL_NAME", "search_rag")
    tool_desc = getattr(
        config, "MCP_TOOL_DESCRIPTION", "Search your codebase for relevant context."
    )

    mcp = FastMCP(
        server_name,
        host=host,
        port=port,
        json_response=True,
    )

    _index = None
    _is_hybrid = False
    _index_lock = asyncio.Lock()
    # Reused for optional status queries — never construct a second client
    # inside get_index_state (client open was part of the slow path).
    _qdrant_client = None
    _provenance_lines: list[str] = []

    def _state_client():
        nonlocal _qdrant_client
        if _qdrant_client is None:
            _qdrant_client = get_qdrant_client(config)
        return _qdrant_client

    # Index state and overlay tombstones published by the indexer into
    # Qdrant (a serving-only server has no manifest files).
    from shared.index_meta import IndexStateCache

    _state_cache = IndexStateCache(
        _state_client,
        config.COLLECTION_NAME,
        ttl_s=float(getattr(config, "INDEX_STATE_CACHE_S", 10.0) or 0.0),
    )

    def _verify_embedding_provenance(client, embed_model) -> None:
        """Fatal check that this server embeds queries like the indexer did."""
        from shared.index_meta import check_serving_provenance

        _provenance_lines[:] = check_serving_provenance(
            client, config.COLLECTION_NAME, config, embed_model
        )

    def _build_index() -> VectorStoreIndex:
        nonlocal _is_hybrid, _qdrant_client
        start = time.perf_counter()
        embed_model = get_embed_model(device=config.MCP_EMBED_DEVICE, cfg=config)

        from qdrant.vector_store import get_qdrant_vector_store, detect_collection_mode

        # Detect collection mode to decide query strategy
        detect_client = get_qdrant_client(config)
        _qdrant_client = detect_client
        collection_mode = detect_collection_mode(detect_client, config.COLLECTION_NAME)
        _is_hybrid = collection_mode == "hybrid"
        log(f"[MCP] Collection mode: {collection_mode}")

        # Embedding provenance: any mismatch is fatal (ProvenanceMismatchError)
        _verify_embedding_provenance(detect_client, embed_model)

        storage_context, _, _ = get_qdrant_vector_store(
            text_key="text", cfg=config, device=config.MCP_EMBED_DEVICE
        )
        vector_store = storage_context.vector_store

        index = VectorStoreIndex.from_vector_store(
            vector_store, embed_model=embed_model
        )
        elapsed = time.perf_counter() - start
        log(f"[MCP] Index ready in {elapsed:.2f}s (store=qdrant, hybrid={_is_hybrid})")
        return index

    async def get_index() -> VectorStoreIndex:
        nonlocal _index
        if _index is None:
            async with _index_lock:
                if _index is None:
                    log("[MCP] Building index on first request...")
                    # Model load and the provenance check block; keep the
                    # event loop serving other clients meanwhile.
                    try:
                        _index = await asyncio.to_thread(_build_index)
                    except ProvenanceMismatchError as exc:
                        _fatal_provenance(config, exc, hard=True)
        return _index

    from shared.index_meta import main_branch_from_state

    _has_git_sources = any(
        isinstance(e, dict) and e.get("type") == "git_repo"
        for e in (getattr(config, "SOURCE_DIRS", None) or [])
    )

    def _overlay_tombstones(feature_branch: str) -> list:
        """Tombstones from Qdrant; the local manifest only for old collections."""
        from shared.branch_dedup import get_branch_tombstones
        from shared.index_meta import serving_tombstones

        return serving_tombstones(
            _state_cache, feature_branch, lambda: get_branch_tombstones(feature_branch, config)
        )

    def _safe_int(value):
        try:
            return int(value)
        except Exception:
            return None

    def _load_snippet_from_file(meta, max_chars: int = 4000) -> str:
        mapped_file_path = meta.get("file_path") if isinstance(meta, dict) else None
        if not mapped_file_path:
            return ""

        # Prefer disk_path stored at index time; fall back to runtime resolution
        file_path = meta.get("disk_path") if isinstance(meta, dict) else None
        if not file_path:
            from shared.manifest import resolve_key_to_disk_path

            file_path = resolve_key_to_disk_path(mapped_file_path, cfg=config)

        path = Path(file_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parent / file_path

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""

        start_line = (
            _safe_int(meta.get("start_line")) if isinstance(meta, dict) else None
        )
        end_line = _safe_int(meta.get("end_line")) if isinstance(meta, dict) else None
        if start_line and end_line and start_line <= end_line:
            lines = text.splitlines()
            snippet = "\n".join(lines[start_line - 1 : end_line])
        else:
            snippet = text

        return snippet[:max_chars]

    # ── Register the search tool with config-driven name ──────────
    from pydantic import Field
    from shared.branch_dedup import BRANCH_PARAMETER_DESCRIPTION

    async def _search_tool(
        query: Annotated[
            str,
            Field(
                description="Natural language or identifier-focused search query. "
                "Examples: class/method names ('PrepareDataSet'), overviews "
                "('What is TdmOrders?'), concepts ('SFTP connection handling', "
                "'chunk pool flush'). Prefer concrete symbols when known."
            ),
        ],
        top_k: Annotated[
            int,
            Field(
                description="How many chunks to return after reranking (default 8). "
                "Use 5–8 for exact symbol lookups; 12–20 for broad or overview queries "
                "so class_summary / procedure_header style chunks can surface.",
                default=8,
            ),
        ] = 8,
        branch: Annotated[
            str,
            Field(
                description=BRANCH_PARAMETER_DESCRIPTION,
                default="",
            ),
        ] = "",
    ) -> str:
        start = time.perf_counter()
        log(
            f"[MCP] {tool_name} start (top_k={top_k}, query_len={len(query)}, branch={branch!r})"
        )

        index = await get_index()
        log(f"[MCP] index available after {time.perf_counter() - start:.2f}s")

        # ── Branch filter construction ────────────────────────────
        from shared.branch_dedup import (
            build_branch_filter,
            dedup_branch_results,
            get_main_branch_name,
        )

        main_branch = get_main_branch_name(config)
        if not _has_git_sources:
            # Serving-only config without SOURCE_DIRS: use the main branch
            # label the indexer published (falls back to "master").
            state, _ = await asyncio.to_thread(_state_cache.state)
            main_branch = main_branch_from_state(state) or main_branch
        feature_branch = branch.strip() if branch else ""
        qdrant_filter = build_branch_filter(
            main_branch=main_branch,
            feature_branch=feature_branch or None,
        )
        log(
            f"[MCP] branch filter: main={main_branch}, feature={feature_branch or 'none'}"
        )

        # Over-fetch for overview queries so the reranker has more candidates
        from shared.reranker import get_retrieval_top_k

        fetch_k = get_retrieval_top_k(query, top_k, rerank_profiles)
        if fetch_k != top_k:
            log(
                f"[MCP] overview query detected, over-fetching {fetch_k} candidates (desired {top_k})"
            )

        # When a feature branch is specified, over-fetch 2x for dedup headroom
        branch_overfetch = 1
        if feature_branch:
            branch_overfetch = 2
            fetch_k = fetch_k * branch_overfetch
            log(f"[MCP] branch over-fetch: {fetch_k} candidates")

        # Hybrid alpha: fixed mode reads HYBRID_ALPHA inside
        # build_retriever_kwargs (one retriever, today's kwargs). Adaptive
        # mode passes this query's alpha. A new retriever is built either
        # way; a shared retriever's alpha is never written.
        from shared.retrieval import open_query_retriever, retriever_ready_message

        retriever, retriever_kwargs, query_shape, alpha_mode = open_query_retriever(
            index,
            config,
            query,
            fetch_k,
            hybrid=bool(_is_hybrid),
            qdrant_filters=qdrant_filter,
        )
        log(
            retriever_ready_message(
                bool(_is_hybrid), retriever_kwargs, alpha_mode, query_shape
            )
        )

        # Main retrieval and the exact symbol lookup (chunks that declare an
        # identifier the query names) share one query embedding and run
        # concurrently; the symbol candidates are merged after branch dedup.
        from shared.retrieval import aretrieve_with_symbol_lookup, merge_symbol_candidates

        timeout_raw = os.getenv("MCP_QUERY_TIMEOUT_SECONDS", "")
        timeout = float(timeout_raw) if timeout_raw else None
        if _is_hybrid:
            # BM25 query encoding in a worker thread (aquery would run it on
            # the event loop); same encoder, same result.
            from qdrant.vector_store import precompute_sparse_query

            await precompute_sparse_query(index.vector_store, query)
        retrieval = aretrieve_with_symbol_lookup(
            index, retriever, query, config, qdrant_filter
        )
        if timeout:
            nodes, symbol_extra = await asyncio.wait_for(retrieval, timeout=timeout)
        else:
            nodes, symbol_extra = await retrieval

        log(f"[MCP] retrieved {len(nodes)} nodes in {time.perf_counter() - start:.2f}s")

        # ── Branch dedup (when feature branch is specified) ───────
        if feature_branch:
            tombstones = await asyncio.to_thread(_overlay_tombstones, feature_branch)
            pre_dedup_count = len(nodes)
            # Dedup wants the desired count BEFORE reranker trims it
            dedup_target = top_k * (
                fetch_k // (top_k * branch_overfetch) if top_k else 1
            )
            # Use a generous target so the reranker still has candidates
            dedup_target = max(dedup_target, fetch_k // branch_overfetch)
            nodes = dedup_branch_results(
                nodes,
                feature_branch=feature_branch,
                tombstones=tombstones,
                desired_top_k=dedup_target,
            )
            log(
                f"[MCP] branch dedup: {pre_dedup_count} -> {len(nodes)} "
                f"(tombstones={len(tombstones)})"
            )

        # Exact symbol lookup candidates (fetched together with the retrieval)
        nodes = merge_symbol_candidates(
            nodes, symbol_extra, top_k, mode=getattr(config, "SYMBOL_LOOKUP_SCORE", "bar")
        )

        # Post-retrieval reranking: boost overview chunks for "What is X?" queries
        from shared.reranker import rerank_results, rerank_options_for_config

        # Pure-Python scoring; in a thread so concurrent clients are not
        # serialized behind it on the event loop.
        nodes = await asyncio.to_thread(
            rerank_results,
            nodes,
            query,
            desired_top_k=top_k,
            verbose=True,
            profiles=rerank_profiles,
            options=rerank_options_for_config(config),
        )

        formatted = []
        from shared.manifest import resolve_key_to_disk_path

        for n in nodes:
            meta = n.node.metadata
            content = n.node.get_content() or ""
            mapped_file_path = meta.get("file_path") if isinstance(meta, dict) else None

            # Prefer disk_path stored at index time; fall back to runtime resolution
            local_file_path = meta.get("disk_path") if isinstance(meta, dict) else None
            if not local_file_path and mapped_file_path:
                local_file_path = resolve_key_to_disk_path(mapped_file_path, cfg=config)

            if (
                not content
                or (local_file_path and content.strip() == local_file_path)
                or (mapped_file_path and content.strip() == mapped_file_path)
            ):
                content = _load_snippet_from_file(meta)

            # Include branch info in output when available
            branch_info = meta.get("branch", "")
            branch_line = f"BRANCH: {branch_info}\n" if branch_info else ""

            # Include resolved disk path for cross-repo file access
            disk_path_line = (
                f"DISK_PATH: {local_file_path}\n" if local_file_path else ""
            )

            formatted.append(
                f"FILE: {meta.get('file_path', 'unknown')}\n"
                f"{branch_line}"
                f"{disk_path_line}"
                f"TYPE: {meta.get('type', meta.get('node_type', 'text'))}\n"
                f"LINES: {meta.get('start_line', '?')}"
                f"–{meta.get('end_line', '?')}\n"
                f"{content[:4000]}"
            )

        context_str = "\n\n---\n\n".join(formatted)
        total = time.perf_counter() - start
        log(f"[MCP] {tool_name} done in {total:.2f}s")
        return f"**Relevant context ({server_name}):**\n\n{context_str}"

    # Set the function name so FastMCP registers it under the right name
    _search_tool.__name__ = tool_name
    _search_tool.__qualname__ = tool_name
    _search_tool.__doc__ = tool_desc
    mcp.tool()(_search_tool)

    # ── Index state tool (manifest + optional Qdrant; no embed model) ──
    state_tool_name = getattr(config, "MCP_INDEX_STATE_TOOL_NAME", "get_index_state")
    state_tool_desc = getattr(
        config,
        "MCP_INDEX_STATE_TOOL_DESCRIPTION",
        "Report what repository state this RAG index is serving.",
    )

    def _index_state_report() -> str:
        from shared.index_state import build_index_state_report

        state, source = _state_cache.state()
        if state is None:
            # Collections published before index state existed: local manifest
            return build_index_state_report(config, provenance_lines=_provenance_lines or None)
        return build_index_state_report(
            config,
            state=state,
            state_source=source,
            provenance_lines=_provenance_lines or None,
        )

    async def _index_state_tool() -> str:
        """Index state from Qdrant (published by the indexer), else the manifest.

        No embedding model, git or source walk. The Qdrant read (cached for
        INDEX_STATE_CACHE_S seconds) runs in a worker thread.
        """
        t0 = time.perf_counter()
        log(f"[MCP] {state_tool_name} enter")
        try:
            report = await asyncio.to_thread(_index_state_report)
        except Exception as exc:
            report = f"# Index state error\n\n{exc}\n"
        log(f"[MCP] {state_tool_name} {time.perf_counter() - t0:.3f}s")
        return report

    _index_state_tool.__name__ = state_tool_name
    _index_state_tool.__qualname__ = state_tool_name
    _index_state_tool.__doc__ = state_tool_desc
    mcp.tool()(_index_state_tool)

    # ── Eagerly build index unless --lazy-init ────────────────────
    if not args.lazy_init:
        try:
            _index = _build_index()
        except ProvenanceMismatchError as exc:
            _fatal_provenance(config, exc)

    # For stdio transport, run with the saved real stdout so the
    # JSON-RPC channel works even though sys.stdout was redirected.
    if args.transport == "stdio":
        import anyio
        from io import TextIOWrapper
        from mcp.server.stdio import stdio_server

        async def _run_stdio():
            real_stdin = anyio.wrap_file(
                TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
            )
            real_stdout = anyio.wrap_file(
                TextIOWrapper(_real_stdout.buffer, encoding="utf-8")
            )
            async with stdio_server(stdin=real_stdin, stdout=real_stdout) as (
                read_stream,
                write_stream,
            ):
                await mcp._mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp._mcp_server.create_initialization_options(),
                )

        anyio.run(_run_stdio)
    else:
        mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
