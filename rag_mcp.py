# rag_mcp.py
"""MCP server for RAG search. Tool name, description, and server name
are driven by config values (MCP_TOOL_NAME, MCP_TOOL_DESCRIPTION,
MCP_SERVER_NAME, MCP_HOST, MCP_PORT)."""

import argparse
import asyncio
import logging
import os
import sys
import time
from pathlib import Path

import config_loader
from shared.log import configure as log_configure, log


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

    # Suppress noisy INFO logging from httpx (Qdrant HTTP client) and
    # sentence_transformers — only warnings and errors should reach stderr.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    # Load config before anything else so all values are available
    config = config_loader.get_config(config_path=args.config)

    # ── FastMCP server (config-driven) ────────────────────────────
    from mcp.server.fastmcp import FastMCP
    from llama_index.core import VectorStoreIndex
    from shared.embedding import get_embed_model

    server_name = getattr(config, "MCP_SERVER_NAME", "informica-rag")
    host = getattr(config, "MCP_HOST", "0.0.0.0")
    port = getattr(config, "MCP_PORT", 8123)
    tool_name = getattr(config, "MCP_TOOL_NAME", "search_informica")
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

    def _build_index() -> VectorStoreIndex:
        nonlocal _is_hybrid
        start = time.perf_counter()
        embed_model = get_embed_model(device=config.MCP_EMBED_DEVICE, cfg=config)

        from qdrant.vector_store import get_qdrant_vector_store, detect_collection_mode
        from qdrant_client import QdrantClient

        # Detect collection mode to decide query strategy
        if config.QDRANT_USE_DOCKER:
            detect_client = QdrantClient(
                host=config.QDRANT_HOST, port=config.QDRANT_PORT
            )
        else:
            detect_client = QdrantClient(path=config.get_index_path())
        collection_mode = detect_collection_mode(detect_client, config.COLLECTION_NAME)
        _is_hybrid = collection_mode == "hybrid"
        log(f"[MCP] Collection mode: {collection_mode}")

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
                    _index = _build_index()
        return _index

    def _safe_int(value):
        try:
            return int(value)
        except Exception:
            return None

    def _load_snippet_from_file(meta, max_chars: int = 4000) -> str:
        mapped_file_path = meta.get("file_path") if isinstance(meta, dict) else None
        if not mapped_file_path:
            return ""

        from shared.manifest import map_path_from_qdrant

        file_path = map_path_from_qdrant(mapped_file_path, cfg=config)

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
    async def _search_tool(query: str, top_k: int = 8) -> str:
        start = time.perf_counter()
        log(f"[MCP] {tool_name} start (top_k={top_k}, query_len={len(query)})")

        index = await get_index()
        log(f"[MCP] index available after {time.perf_counter() - start:.2f}s")

        # Over-fetch for overview queries so the reranker has more candidates
        from shared.reranker import get_retrieval_top_k

        fetch_k = get_retrieval_top_k(query, top_k)
        if fetch_k != top_k:
            log(
                f"[MCP] overview query detected, over-fetching {fetch_k} candidates (desired {top_k})"
            )

        # Use hybrid query mode when collection has sparse vectors
        if _is_hybrid:
            from llama_index.core.vector_stores.types import VectorStoreQueryMode

            alpha = getattr(config, "HYBRID_ALPHA", 0.5)
            retriever = index.as_retriever(
                similarity_top_k=fetch_k,
                vector_store_query_mode=VectorStoreQueryMode.HYBRID,
                alpha=alpha,
                sparse_top_k=fetch_k,
            )
            log(f"[MCP] retriever ready (hybrid, alpha={alpha})")
        else:
            retriever = index.as_retriever(similarity_top_k=fetch_k)
            log("[MCP] retriever ready (dense)")

        timeout_raw = os.getenv("MCP_QUERY_TIMEOUT_SECONDS", "")
        timeout = float(timeout_raw) if timeout_raw else None
        if timeout:
            nodes = await asyncio.wait_for(retriever.aretrieve(query), timeout=timeout)
        else:
            nodes = await retriever.aretrieve(query)

        log(f"[MCP] retrieved {len(nodes)} nodes in {time.perf_counter() - start:.2f}s")

        # Post-retrieval reranking: boost overview chunks for "What is X?" queries
        from shared.reranker import rerank_results

        nodes = rerank_results(nodes, query, desired_top_k=top_k, verbose=True)

        formatted = []
        from shared.manifest import map_path_from_qdrant

        for n in nodes:
            meta = n.node.metadata
            content = n.node.get_content() or ""
            mapped_file_path = meta.get("file_path") if isinstance(meta, dict) else None
            local_file_path = (
                map_path_from_qdrant(mapped_file_path, cfg=config)
                if mapped_file_path
                else None
            )

            if (
                not content
                or (local_file_path and content.strip() == local_file_path)
                or (mapped_file_path and content.strip() == mapped_file_path)
            ):
                content = _load_snippet_from_file(meta)

            formatted.append(
                f"FILE: {meta.get('file_path', 'unknown')}\n"
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

    # ── Eagerly build index unless --lazy-init ────────────────────
    if not args.lazy_init:
        _index = _build_index()

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
