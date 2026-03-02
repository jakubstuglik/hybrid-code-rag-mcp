# Configuration for Informica RAG
# Edit these values in one place to affect both indexer and MCP

STORE_TYPE = "qdrant"  # "chroma" or "qdrant"

QDRANT_USE_LOCAL_FILE = False  # Use Docker (recommended)

MODEL_NAME = "BAAI/bge-m3"  # Big model
#MODEL_NAME = "BAAI/bge-small-en-v1.5" # small model
MODEL_PATH = "index_bge_m3"  # Used for storage folder naming
#MODEL_PATH = "index_bge_small_v1.5"  # Used for storage folder naming

COLLECTION_NAME = "delphi_rag"

QDRANT_USE_DOCKER = True  # Use Docker server (recommended)
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

EMBED_MODEL_KWARGS = {
    "torch_dtype": "float16"
}  # saves VRAM + faster, empty dict for default

INDEX_EMBED_DEVICE = "cpu"  # Device for indexing (cuda/cpu)
MCP_EMBED_DEVICE = "cpu"  # Device for MCP server (cuda/cpu)


def get_index_path() -> str:
    """Get the full index path based on STORE_TYPE and MODEL_PATH."""
    suffix = "_" + STORE_TYPE
    return f"./{STORE_TYPE}/{MODEL_PATH}{suffix}"


def get_chroma_path() -> str:
    """Get the Chroma index path (for migration purposes)."""
    return f"./chroma/{MODEL_PATH}_chroma"


def get_qdrant_path() -> str:
    """Get the Qdrant index path (for migration purposes)."""
    return f"./qdrant/{MODEL_PATH}_qdrant"


def get_current_store_path() -> str:
    """Get path for current store type (used for --fix-paths, --regenerate-manifest)."""
    return get_index_path()
