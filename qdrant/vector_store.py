from typing import Optional

from qdrant_client import AsyncQdrantClient, QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import StorageContext
import config


def get_qdrant_vector_store(text_key: Optional[str] = None):
    """Get Qdrant vector store based on config."""
    if config.QDRANT_USE_DOCKER:
        qdrant_client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
        )
        async_client = AsyncQdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
        )
    else:
        index_path = config.get_index_path()
        qdrant_client = QdrantClient(path=index_path)
        async_client = AsyncQdrantClient(path=index_path)

    vector_store_kwargs = {
        "client": qdrant_client,
        "aclient": async_client,
        "collection_name": config.COLLECTION_NAME,
    }
    if text_key is not None:
        vector_store_kwargs["text_key"] = text_key
    vector_store = QdrantVectorStore(**vector_store_kwargs)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context, qdrant_client, async_client
