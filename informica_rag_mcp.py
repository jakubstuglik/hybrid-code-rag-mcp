# informica_rag_mcp.py
from mcp.server.fastmcp import FastMCP
from llama_index.core import VectorStoreIndex
import argparse
import asyncio
import os
import time
from pathlib import Path

import config
from shared.embedding import get_embed_model

mcp = FastMCP(
    "informica-rag-tool",
    host="0.0.0.0",
    port=8123,
    json_response=True,
)

_index = None
_index_lock = asyncio.Lock()


def _build_index() -> VectorStoreIndex:
    start = time.perf_counter()
    embed_model = get_embed_model(device=config.MCP_EMBED_DEVICE)

    if config.STORE_TYPE == "chroma":
        from chroma.vector_store import get_chroma_vector_store

        storage_context, _, _ = get_chroma_vector_store()
        vector_store = storage_context.vector_store
    elif config.STORE_TYPE == "qdrant":
        from qdrant.vector_store import get_qdrant_vector_store

        storage_context, _, _ = get_qdrant_vector_store(text_key="text")
        vector_store = storage_context.vector_store
    else:
        raise ValueError(f"Unsupported STORE_TYPE: {config.STORE_TYPE}")

    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
    elapsed = time.perf_counter() - start
    print(
        f"[MCP] Index ready in {elapsed:.2f}s (store={config.STORE_TYPE})", flush=True
    )
    return index


async def get_index() -> VectorStoreIndex:
    global _index
    if _index is None:
        async with _index_lock:
            if _index is None:
                print("[MCP] Building index on first request...", flush=True)
                _index = _build_index()
    return _index


def _safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def _load_snippet_from_file(meta, max_chars: int = 4000) -> str:
    file_path = meta.get("file_path") if isinstance(meta, dict) else None
    if not file_path:
        return ""

    path = Path(file_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / file_path

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

    start_line = _safe_int(meta.get("start_line")) if isinstance(meta, dict) else None
    end_line = _safe_int(meta.get("end_line")) if isinstance(meta, dict) else None
    if start_line and end_line and start_line <= end_line:
        lines = text.splitlines()
        snippet = "\n".join(lines[start_line - 1 : end_line])
    else:
        snippet = text

    return snippet[:max_chars]


@mcp.tool()
async def search_informica(query: str, top_k: int = 8) -> str:
    """Search your Delphi codebase, SQL schemas, FastReport templates, and docs for relevant context."""
    start = time.perf_counter()
    print(
        f"[MCP] search_informica start (top_k={top_k}, query_len={len(query)})",
        flush=True,
    )

    index = await get_index()
    print(
        f"[MCP] index available after {time.perf_counter() - start:.2f}s",
        flush=True,
    )

    retriever = index.as_retriever(similarity_top_k=top_k)
    print("[MCP] retriever ready", flush=True)

    timeout_raw = os.getenv("MCP_QUERY_TIMEOUT_SECONDS", "")
    timeout = float(timeout_raw) if timeout_raw else None
    if timeout:
        nodes = await asyncio.wait_for(retriever.aretrieve(query), timeout=timeout)
    else:
        nodes = await retriever.aretrieve(query)

    print(
        f"[MCP] retrieved {len(nodes)} nodes in {time.perf_counter() - start:.2f}s",
        flush=True,
    )

    formatted = []
    for n in nodes:
        meta = n.node.metadata
        content = n.node.get_content() or ""
        file_path = meta.get("file_path") if isinstance(meta, dict) else None
        if not content or (file_path and content.strip() == file_path):
            content = _load_snippet_from_file(meta)

        formatted.append(
            f"FILE: {meta.get('file_path', 'unknown')}\n"
            f"TYPE: {meta.get('type', meta.get('node_type', 'text'))}\n"
            f"LINES: {meta.get('start_line', '?')}–{meta.get('end_line', '?')}\n"
            f"{content[:4000]}"  # truncate very long chunks
        )

    context_str = "\n\n---\n\n".join(formatted)
    total = time.perf_counter() - start
    print(f"[MCP] search_informica done in {total:.2f}s", flush=True)
    return f"**Relevant context from Informica project:**\n\n{context_str}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lazy-init",
        action="store_true",
        help="Defer loading the embed model/index until first request.",
    )
    args = parser.parse_args()

    if not args.lazy_init:
        _index = _build_index()

    mcp.run(transport="streamable-http")
