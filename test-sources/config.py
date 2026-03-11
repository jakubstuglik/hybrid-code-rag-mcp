# Override config for test-sources quick validation.
# Points at the curated test_sources/ directory (38 files) for fast iteration.
# Usage: python index_rag.py --config test-sources --clear --yes

SOURCE_DIRS = [
    {
        "path": "test_sources",
        "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj", ".sql"],
    },
]

# Reuse the main Qdrant container on port 6333
COLLECTION_NAME = "informica_rag"

# Use CUDA for indexing (same as production)
INDEX_EMBED_DEVICE = "cuda"
MCP_EMBED_DEVICE = "cpu"

# Same model kwargs as production
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}
