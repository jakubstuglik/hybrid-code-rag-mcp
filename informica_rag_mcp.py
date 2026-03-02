# informica_rag_mcp.py
from mcp.server.fastmcp import FastMCP
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

import config

mcp = FastMCP("informica-rag-tool")

# Load your existing index
embed_model = HuggingFaceEmbedding(
    model_name=config.MODEL_NAME,
    device=config.MCP_EMBED_DEVICE,
    model_kwargs=config.EMBED_MODEL_KWARGS,
)
db = chromadb.PersistentClient(path=config.INDEX_PATH)
chroma_collection = db.get_collection(config.COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
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
    mcp.run(transport="http", host="0.0.0.0", port="8123")
