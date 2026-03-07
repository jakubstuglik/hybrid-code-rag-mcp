# Override config for self-indexing the informica-rag project itself.
# Assumes working directory is the project root.

SOURCE_DIRS = [
    {
        "path": ".",
        "extensions": [".py", ".bat", ".txt", ".md", ".json", ".jsonc", ".yml"],
        "exclude": [
            "source",
            "schemas",
            ".venv",
            ".git",
            ".idea",
            ".ruff_cache",
            "test_sources",
            "backup",
            "index_*",
            "self-index",
            "__pycache__",
            "node_modules",
        ],
    },
]

BASE_PATH = "self-index"
COLLECTION_NAME = "self_rag_index"
MODEL_PATH = "index_rag_self"

QDRANT_USE_DOCKER = True
QDRANT_HOST = "localhost"
QDRANT_PORT = 6973

# Use hybrid mode for better code identifier search
INDEXING_MODE = "hybrid"

# Two-pass hybrid embedding to save VRAM (default: False)
HYBRID_EMBED_SINGLE_PASS = False

# Dense and sparse embedding batch sizes
DENSE_EMBED_BATCH_SIZE = 64
SPARSE_EMBED_BATCH_SIZE = 32  # Smaller due to higher VRAM usage

# ── MCP server settings ──────────────────────────────────────────────
MCP_SERVER_NAME = "self-rag"
MCP_TOOL_NAME = "search_self_rag"
MCP_TOOL_DESCRIPTION = (
    "Search the informica-rag project's own source code, configs, "
    "and documentation for relevant context."
)
MCP_PORT = 8124