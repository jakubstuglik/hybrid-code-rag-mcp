# Index-specific config for test-sources quick validation.
# ================================================================
# Points at the curated test_sources/ directory (38 files) for fast
# iteration during chunking strategy development.
#
# Usage:
#   python src/index_rag.py --config test-sources --clear --yes
#   python src/validate_rag.py --config test-sources
#
# Common/system settings are inherited from the base config.py.
# ================================================================


# ── Source directories ───────────────────────────────────────────
SOURCE_DIRS = [
    {
        "path": "test_sources",
        "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj", ".sql"],
    },
]

# ── Storage path ─────────────────────────────────────────────────
# Uses the same MODEL_PATH as my_project (same embedding model),
# but a SEPARATE COLLECTION to avoid --clear destroying production data.
MODEL_PATH = "index_jinaai_test_sources"

# ── Qdrant connection ────────────────────────────────────────────
# Reuses the main Qdrant container on port 6333, but with its own
# collection name so --clear is safe.
COLLECTION_NAME = "test_sources_rag"
QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
