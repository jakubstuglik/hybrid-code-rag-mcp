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
from shared.log import configure as log_configure, log
from shared.qdrant_client import get_qdrant_client
from shared.docker_utils import ensure_qdrant_running, ensure_tei_running


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

    # Ensure Qdrant is running (auto-start Docker for local mode)
    if not ensure_qdrant_running(config, stderr_prefix="[MCP]"):
        log("[MCP] ERROR: Qdrant is not available. Cannot start MCP server.")
        sys.exit(1)

    # Ensure TEI is running if configured (auto-start Docker container)
    if getattr(config, "USE_TEI", False):
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

        # Check embedding provenance — warn if mismatched (don't block MCP startup)
        from shared.embedding import check_provenance_for_query

        check_provenance_for_query(detect_client, config.COLLECTION_NAME, config)

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

    async def _search_tool(
        query: Annotated[
            str,
            Field(
                description="Natural language or identifier-focused search query. "
                "Examples: class/method names ('PrepareDataSet'), overviews "
                "('What is TdmMain?'), concepts ('SFTP connection handling', "
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
                description="Feature branch for branch-aware search. When set, results "
                "include main branch plus this overlay; feature versions win on "
                "conflicts. Pass `git branch --show-current` when not on main. "
                "Leave empty to search the configured main branch only.",
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
            get_branch_tombstones,
            get_main_branch_name,
        )

        main_branch = get_main_branch_name(config)
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

        fetch_k = get_retrieval_top_k(query, top_k)
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

        # Use hybrid query mode when collection has sparse vectors
        retriever_kwargs = {
            "similarity_top_k": fetch_k,
            "vector_store_kwargs": {"qdrant_filters": qdrant_filter},
        }
        if _is_hybrid:
            from llama_index.core.vector_stores.types import VectorStoreQueryMode

            alpha = getattr(config, "HYBRID_ALPHA", 0.5)
            retriever_kwargs.update(
                {
                    "vector_store_query_mode": VectorStoreQueryMode.HYBRID,
                    "alpha": alpha,
                    "sparse_top_k": fetch_k,
                }
            )
            retriever = index.as_retriever(**retriever_kwargs)
            log(f"[MCP] retriever ready (hybrid, alpha={alpha})")
        else:
            retriever = index.as_retriever(**retriever_kwargs)
            log("[MCP] retriever ready (dense)")

        timeout_raw = os.getenv("MCP_QUERY_TIMEOUT_SECONDS", "")
        timeout = float(timeout_raw) if timeout_raw else None
        if timeout:
            nodes = await asyncio.wait_for(retriever.aretrieve(query), timeout=timeout)
        else:
            nodes = await retriever.aretrieve(query)

        log(f"[MCP] retrieved {len(nodes)} nodes in {time.perf_counter() - start:.2f}s")

        # ── Branch dedup (when feature branch is specified) ───────
        if feature_branch:
            tombstones = get_branch_tombstones(feature_branch, config)
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

        # Post-retrieval reranking: boost overview chunks for "What is X?" queries
        from shared.reranker import rerank_results

        nodes = rerank_results(nodes, query, desired_top_k=top_k, verbose=True)

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

    async def _index_state_tool() -> str:
        """Read index_manifest.json only — no git, Qdrant, TEI, or source walk.

        Async like the search tool (avoids FastMCP sync-tool executor quirks).
        Work is pure stdlib file I/O; must finish in milliseconds.
        """
        import json as _json

        t0 = time.perf_counter()
        log(f"[MCP] {state_tool_name} enter")
        try:
            manifest_path = Path(config.get_index_path()) / "index_manifest.json"
            server = getattr(config, "MCP_SERVER_NAME", "rag-server")
            collection = getattr(config, "COLLECTION_NAME", "unknown")
            host = getattr(config, "QDRANT_HOST", "localhost")
            port = getattr(config, "QDRANT_PORT", "?")
            lines = [
                f"# Index state — {server}",
                "",
                f"- collection: {collection} @ {host}:{port}",
            ]
            if not manifest_path.is_file():
                lines.append(f"- last_index_completed_at: unknown (no {manifest_path})")
                lines.append("- indexed_files: 0")
                lines.append("")
                lines.append("No index manifest. Run the indexer for this config.")
                report = "\n".join(lines) + "\n"
            else:
                with open(manifest_path, "r", encoding="utf-8") as fh:
                    manifest = _json.load(fh)
                files = manifest.get("files") or {}
                n_files = len(files) if isinstance(files, dict) else 0
                index_run = manifest.get("index_run") or {}
                completed = (
                    index_run.get("completed_at")
                    if isinstance(index_run, dict)
                    else None
                )
                if not completed:
                    completed = f"{manifest_path.stat().st_mtime:.0f} (mtime epoch)"
                backend = (
                    index_run.get("embed_backend")
                    if isinstance(index_run, dict)
                    else None
                )
                lines.append(f"- last_index_completed_at: {completed}")
                lines.append(f"- indexed_files: {n_files}")
                if backend:
                    lines.append(f"- embed_backend: {backend}")
                lines.append("")
                lines.append("## Sources")
                repo_commits = manifest.get("repo_commits") or {}
                if isinstance(repo_commits, dict) and repo_commits:
                    for repo_key, rc in sorted(repo_commits.items()):
                        if not isinstance(rc, dict):
                            continue
                        lines.append(f"### git: {repo_key}")
                        lines.append(
                            f"- main_branch: {rc.get('main_branch') or 'unknown'}"
                        )
                        lines.append(
                            f"- indexed_commit: {rc.get('commit') or 'unknown'}"
                        )
                        if rc.get("indexed_at"):
                            lines.append(f"- indexed_at: {rc['indexed_at']}")
                        lines.append("")
                else:
                    lines.append("### git: (none in manifest)")
                    lines.append("")
                lines.append(
                    "Note: last successful index/refresh only — not uncommitted edits."
                )
                report = "\n".join(lines) + "\n"
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
