# informica_rag_mcp.py
from mcp.server.fastmcp import FastMCP
from llama_index.core import load_index_from_storage, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

mcp = FastMCP("informica-rag-tool")

# Load your existing index
db = chromadb.PersistentClient(path="./index_storage")
chroma_collection = db.get_collection("delphi_rag")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = load_index_from_storage(storage_context)

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
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port="8123"
    )  # runs on stdio by default (what OpenCode expects for local)