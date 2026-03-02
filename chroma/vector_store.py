import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import config


def get_chroma_vector_store():
    """Get Chroma vector store based on config."""
    index_path = config.get_index_path()
    db = chromadb.PersistentClient(path=index_path)
    collection = db.get_or_create_collection(config.COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context, db, collection
