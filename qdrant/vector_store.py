from types import ModuleType
from typing import Optional

from qdrant_client import AsyncQdrantClient, QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import StorageContext
import config as _base_config


# ── Sparse encoder cache ─────────────────────────────────────────────
_sparse_encoder_cache: dict = {}


def get_sparse_encoder(cfg: Optional[ModuleType] = None):
    """Get or create a cached fastembed sparse encoder.

    Returns:
        A SparseEncoderCallable or None if mode is dense-only.
        Signature: Callable[[List[str]], Tuple[List[List[int]], List[List[float]]]]
    """
    if cfg is None:
        cfg = _base_config

    mode = getattr(cfg, "INDEXING_MODE", "dense")
    if mode == "dense":
        return None

    model_name = getattr(cfg, "SPARSE_MODEL_NAME", "prithivida/Splade_PP_en_v1")
    if model_name in _sparse_encoder_cache:
        return _sparse_encoder_cache[model_name]

    from llama_index.vector_stores.qdrant.utils import fastembed_sparse_encoder

    encoder = fastembed_sparse_encoder(model_name=model_name)
    _sparse_encoder_cache[model_name] = encoder
    return encoder


def detect_collection_mode(
    client: QdrantClient,
    collection_name: str,
) -> str:
    """Detect whether an existing collection uses dense, sparse, or hybrid vectors.

    Returns:
        "hybrid" if the collection has both dense named vectors and sparse vectors,
        "sparse" if it has sparse vectors only,
        "dense" if it uses unnamed/single dense vectors,
        "unknown" if the collection doesn't exist or can't be read.
    """
    from qdrant_client.http.exceptions import UnexpectedResponse

    try:
        info = client.get_collection(collection_name=collection_name)
    except (UnexpectedResponse, Exception):
        return "unknown"

    vectors_config = info.config.params.vectors
    sparse_vectors = info.config.params.sparse_vectors or {}

    has_named_dense = isinstance(vectors_config, dict) and len(vectors_config) > 0
    has_sparse = isinstance(sparse_vectors, dict) and len(sparse_vectors) > 0

    if has_named_dense and has_sparse:
        return "hybrid"
    elif has_sparse:
        return "sparse"
    else:
        return "dense"


def get_qdrant_vector_store(
    text_key: Optional[str] = None,
    cfg: Optional[ModuleType] = None,
):
    """Get Qdrant vector store based on config.

    When INDEXING_MODE is "hybrid" or "sparse", enables hybrid search with
    fastembed sparse encoder.  The QdrantVectorStore handles collection
    creation with named dense + sparse vectors automatically.

    Args:
        text_key: Optional text key for the vector store.
        cfg: Merged config module (from config_loader). Falls back to base
             config if not provided.

    Returns:
        Tuple of (storage_context, qdrant_client, async_client).
    """
    if cfg is None:
        cfg = _base_config

    if cfg.QDRANT_USE_DOCKER:
        qdrant_client = QdrantClient(
            host=cfg.QDRANT_HOST,
            port=cfg.QDRANT_PORT,
        )
        async_client = AsyncQdrantClient(
            host=cfg.QDRANT_HOST,
            port=cfg.QDRANT_PORT,
        )
    else:
        index_path = cfg.get_index_path()
        qdrant_client = QdrantClient(path=index_path)
        async_client = AsyncQdrantClient(path=index_path)

    mode = getattr(cfg, "INDEXING_MODE", "dense")
    enable_hybrid = mode in ("hybrid", "sparse")

    vector_store_kwargs = {
        "client": qdrant_client,
        "aclient": async_client,
        "collection_name": cfg.COLLECTION_NAME,
        "enable_hybrid": enable_hybrid,
    }

    if enable_hybrid:
        sparse_fn = get_sparse_encoder(cfg)
        if sparse_fn is not None:
            vector_store_kwargs["sparse_doc_fn"] = sparse_fn
            vector_store_kwargs["sparse_query_fn"] = sparse_fn

    if text_key is not None:
        vector_store_kwargs["text_key"] = text_key

    vector_store = QdrantVectorStore(**vector_store_kwargs)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context, qdrant_client, async_client
