# Configuration for Informica RAG
# Edit these values in one place to affect both indexer and MCP

# ── Source directories ──────────────────────────────────────────────
# Each entry maps a directory path to the file extensions that should
# be indexed from it.  Only extensions that have a matching reader in
# shared/readers/READER_REGISTRY will actually be processed.
#
# To add a new source folder or extension, just edit this list.
SOURCE_DIRS = [
    {
        "path": "source",
        "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj"],
    },
    {
        "path": "schemas",
        "extensions": [".sql"],
    },
]

STORE_TYPE = "qdrant"  # "chroma" or "qdrant"

QDRANT_USE_LOCAL_FILE = False  # Use Docker (recommended)

# MODEL_NAME = "BAAI/bge-m3"  # Big model
# MODEL_PATH = "index_bge_m3"  # Used for storage folder naming
# MODEL_NAME = "BAAI/bge-small-en-v1.5"  # small model
# MODEL_PATH = "index_bge_small_v1.5"  # Used for storage folder naming

# MODEL_NAME = "BAAI/bge-small-en-v1.5"  # small model
# MODEL_PATH = "index_bge_small_20260303"  # Used for storage folder naming

MODEL_NAME = "BAAI/bge-m3"  # small model
MODEL_PATH = "index_bge_m3_20260304"  # Used for storage folder naming
#MODEL_PATH = "index_bge_m3_testing"  # Used for storage folder naming

COLLECTION_NAME = "delphi_rag"

QDRANT_USE_DOCKER = True  # Use Docker server (recommended)
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

EMBED_MODEL_KWARGS = {
    "torch_dtype": "float16"
}  # saves VRAM + faster, empty dict for default

EMBED_BATCH_SIZE = 32  # Max number of chunks per batch (by count)
EMBED_BATCH_MAX_TOKENS = (
    40000  # Max total text tokens per batch (approximate, controls VRAM)
)

INDEX_EMBED_DEVICE = "cuda"  # Device for indexing (cuda/cpu)
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
