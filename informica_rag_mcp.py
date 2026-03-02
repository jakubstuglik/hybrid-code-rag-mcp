# informica_rag_mcp.py
from mcp.server.fastmcp import FastMCP
from llama_index.core import VectorStoreIndex

import config
from shared.embedding import get_embed_model

mcp = FastMCP("informica-rag-tool", host="0.0.0.0", port=8123)

# Load your existing index
embed_model = get_embed_model()

if config.STORE_TYPE == "chroma":
    from chroma.vector_store import get_chroma_vector_store

    storage_context, _, _ = get_chroma_vector_store()
    vector_store = storage_context.vector_store
elif config.STORE_TYPE == "qdrant":
    from qdrant.vector_store import get_qdrant_vector_store

    storage_context, _ = get_qdrant_vector_store()
    vector_store = storage_context.vector_store
else:
    raise ValueError(f"Unsupported STORE_TYPE: {config.STORE_TYPE}")

index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)


@mcp.tool()
async def search_informica(query: str, top_k: int = 8) -> str:
    """Search your Delphi codebase, SQL schemas, FastReport templates, and docs for relevant context."""
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = await retriever.aretrieve(query)

    formatted = []
    for n in nodes:
        meta = n.node.metadata
        formatted.append(
            f"FILE: {meta.get('file_path', 'unknown')}\n"
            f"TYPE: {meta.get('type', meta.get('node_type', 'text'))}\n"
            f"LINES: {meta.get('start_line', '?')}–{meta.get('end_line', '?')}\n"
            f"{n.node.get_content()[:4000]}"  # truncate very long chunks
        )

    context_str = "\n\n---\n\n".join(formatted)
    return f"**Relevant context from Informica project:**\n\n{context_str}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
