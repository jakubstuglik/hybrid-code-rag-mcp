import os
import sys
from types import ModuleType
from typing import Callable, List, Optional, Tuple

from qdrant_client import AsyncQdrantClient, QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import StorageContext
import config as _base_config

from shared.log import log, log_warn


# ── Sparse encoder cache ─────────────────────────────────────────────
_sparse_encoder_cache: dict = {}
_torch_cuda_libs_loaded = False


def _ensure_torch_cuda_libs() -> None:
    """Add PyTorch's bundled CUDA libraries to DLL search path.

    ONNX Runtime's CUDAExecutionProvider needs cuBLAS and cuDNN DLLs.
    PyTorch ships these in its ``torch/lib`` directory but ONNX Runtime
    can't find them unless they're on the system PATH or registered via
    ``os.add_dll_directory`` (Windows) / ``LD_LIBRARY_PATH`` (Linux).

    This function adds the path once per process.
    """
    global _torch_cuda_libs_loaded
    if _torch_cuda_libs_loaded:
        return

    try:
        import torch

        torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
        if os.path.isdir(torch_lib):
            if sys.platform == "win32":
                os.add_dll_directory(torch_lib)
            # Also prepend to PATH as a fallback for subprocess / older loaders
            os.environ["PATH"] = torch_lib + os.pathsep + os.environ.get("PATH", "")
            _torch_cuda_libs_loaded = True
    except ImportError:
        pass


# Type alias matching LlamaIndex's SparseEncoderCallable
SparseEncoderCallable = Callable[
    [List[str]], Tuple[List[List[int]], List[List[float]]]
]


def get_sparse_encoder(
    cfg: Optional[ModuleType] = None,
    device: Optional[str] = None,
) -> Optional[SparseEncoderCallable]:
    """Get or create a cached fastembed sparse encoder.

    Creates the ``SparseTextEmbedding`` directly (bypassing the LlamaIndex
    wrapper) so we can control the ONNX execution provider based on the
    ``device`` parameter.

    Args:
        cfg: Merged config module. Falls back to base config.
        device: ``"cuda"`` or ``"cpu"``.  Defaults to
                ``cfg.INDEX_EMBED_DEVICE`` (usually ``"cuda"``).

    Returns:
        A SparseEncoderCallable or None if mode is dense-only.
        Signature: ``Callable[[List[str]], Tuple[List[List[int]], List[List[float]]]]``
    """
    if cfg is None:
        cfg = _base_config

    mode = getattr(cfg, "INDEXING_MODE", "dense")
    if mode == "dense":
        return None

    if device is None:
        device = getattr(cfg, "INDEX_EMBED_DEVICE", "cpu")

    model_name = getattr(cfg, "SPARSE_MODEL_NAME", "prithivida/Splade_PP_en_v1")
    cache_key = (model_name, device)
    if cache_key in _sparse_encoder_cache:
        return _sparse_encoder_cache[cache_key]

    from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding

    model: SparseTextEmbedding
    if device == "cuda":
        _ensure_torch_cuda_libs()
        try:
            model = SparseTextEmbedding(
                model_name,
                providers=["CUDAExecutionProvider"],
            )
            log(f"Sparse encoder loaded on GPU (CUDAExecutionProvider)")
        except Exception as exc:
            log_warn(
                f"CUDAExecutionProvider unavailable ({exc}), "
                f"falling back to CPU for sparse encoder"
            )
            model = SparseTextEmbedding(model_name)
    else:
        model = SparseTextEmbedding(model_name)
        log("Sparse encoder loaded on CPU")

    batch_size = 256

    def compute_vectors(
        texts: List[str],
    ) -> Tuple[List[List[int]], List[List[float]]]:
        embeddings = model.embed(texts, batch_size=batch_size)
        indices, values = zip(
            *[
                (embedding.indices.tolist(), embedding.values.tolist())
                for embedding in embeddings
            ]
        )
        return list(indices), list(values)

    _sparse_encoder_cache[cache_key] = compute_vectors
    return compute_vectors


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
    device: Optional[str] = None,
):
    """Get Qdrant vector store based on config.

    When INDEXING_MODE is "hybrid" or "sparse", enables hybrid search with
    fastembed sparse encoder.  The QdrantVectorStore handles collection
    creation with named dense + sparse vectors automatically.

    Args:
        text_key: Optional text key for the vector store.
        cfg: Merged config module (from config_loader). Falls back to base
             config if not provided.
        device: ``"cuda"`` or ``"cpu"`` for the sparse encoder.
                Defaults to ``cfg.INDEX_EMBED_DEVICE``.

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
        sparse_fn = get_sparse_encoder(cfg, device=device)
        if sparse_fn is not None:
            vector_store_kwargs["sparse_doc_fn"] = sparse_fn
            vector_store_kwargs["sparse_query_fn"] = sparse_fn

    if text_key is not None:
        vector_store_kwargs["text_key"] = text_key

    vector_store = QdrantVectorStore(**vector_store_kwargs)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context, qdrant_client, async_client
