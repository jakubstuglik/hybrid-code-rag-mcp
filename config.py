# Configuration for Informica RAG
# Edit these values in one place to affect both indexer and MCP

# ── Source directories ──────────────────────────────────────────────
# Each entry maps a directory path to the file extensions that should
# be indexed from it.  Only extensions that have a matching reader in
# shared/readers/READER_REGISTRY will actually be processed.
#
# To add a new source folder or extension, just edit this list.
#
# Optional "exclude" list: folder names to exclude (can be nested at any level).
# Example:
#   {
#       "path": ".",
#       "extensions": [".pas"],
#       "exclude": ["source", "schemas", ".venv", "test_sources", "backup", "index_*"]
#   }
# SOURCE_DIRS = [
#     {
#         "path": "source",
#         "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj"],
#     },
#     {
#         "path": "schemas",
#         "extensions": [".sql"],
#     },
# ]
SOURCE_DIRS = [
    {
        "path": "test_sources",
        "extensions": [".pas", ".dfm", ".sql", ".dproj"]
    }
]

# MODEL_NAME = "BAAI/bge-m3"  # Big model
# MODEL_PATH = "index_bge_m3"  # Used for storage folder naming
# MODEL_NAME = "BAAI/bge-small-en-v1.5"  # small model
# MODEL_PATH = "index_bge_small_v1.5"  # Used for storage folder naming

# Base path for storing Qdrant database
BASE_PATH = "./qdrant"

MODEL_NAME = "BAAI/bge-m3"  # small model
MODEL_PATH = "index_bge_m3_20260306_test_sources"  # Used for storage folder naming

COLLECTION_NAME = "informica_rag"

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

# ── Indexing mode ────────────────────────────────────────────────────
# "dense"  - dense vectors only (default, backward compatible)
# "sparse" - sparse vectors only (lexical/keyword matching)
# "hybrid" - both dense + sparse vectors (best for code search)
INDEXING_MODE = "hybrid"

# Sparse embedding model used by fastembed (only used when mode != "dense")
SPARSE_MODEL_NAME = "prithivida/Splade_PP_en_v1"

# Hybrid search alpha: 0.0 = all sparse, 1.0 = all dense (only used at query time)
HYBRID_ALPHA = 0.5

INDEX_EMBED_DEVICE = "cuda"  # Device for indexing (cuda/cpu)
MCP_EMBED_DEVICE = "cpu"  # Device for MCP server (cuda/cpu)

# ── MCP server settings ──────────────────────────────────────────────
MCP_SERVER_NAME = "informica-rag"
MCP_TOOL_NAME = "search_informica"
MCP_TOOL_DESCRIPTION = (
    "Search your Delphi codebase, SQL schemas, FastReport templates, "
    "and docs for relevant context."
)
MCP_HOST = "0.0.0.0"
MCP_PORT = 8123


def get_index_path() -> str:
    """Get the full index path based on BASE_PATH and MODEL_PATH."""
    return f"{BASE_PATH}/{MODEL_PATH}"


def get_qdrant_path() -> str:
    """Get the Qdrant index path (for migration purposes)."""
    return f"{BASE_PATH}/{MODEL_PATH}"
