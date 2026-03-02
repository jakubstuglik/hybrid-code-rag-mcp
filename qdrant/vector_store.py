from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import StorageContext
import config


def get_qdrant_vector_store():
    """Get Qdrant vector store based on config."""
    if config.QDRANT_USE_DOCKER:
        qdrant_client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
        )
    else:
        index_path = config.get_index_path()
        qdrant_client = QdrantClient(path=index_path)

    vector_store = QdrantVectorStore(
        client=qdrant_client, collection_name=config.COLLECTION_NAME
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context, qdrant_client
