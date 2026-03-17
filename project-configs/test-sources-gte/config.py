# Calibration config: test_sources/ with Alibaba-NLP/gte-modernbert-base.
# ================================================================
# Used to tune EMBED_MAX_SEQ_LENGTH before the full Informica build.
# Run with --clear --yes --log-to-file --collect-perf-stats, observe
# VRAM usage in the perf stats, then increase seq length until VRAM
# approaches 7.5 GB (leaving 0.5 GB headroom on an 8 GB card).
#
# Usage:
#   python src/index_rag.py --config test-sources-gte --clear --yes --log-to-file --collect-perf-stats
#   python src/validate_rag.py --config test-sources-gte
# ================================================================


# ── Source directories ───────────────────────────────────────────
SOURCE_DIRS = [
    {
        "path": "test_sources",
        "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj", ".sql"],
    },
]

# ── Embedding model ──────────────────────────────────────────────
MODEL_NAME = "Alibaba-NLP/gte-modernbert-base"

# START conservative. Read the perf stats log after the run, check peak VRAM,
# then increase and re-run. Target: max peak VRAM < 7.5 GB.
EMBED_MAX_SEQ_LENGTH = 8192
DENSE_EMBED_BATCH_SIZE = 32
EMBED_BATCH_MAX_TOKENS = 16000
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}
EMBED_DYNAMIC_VRAM_CAP = False

# ── Storage ──────────────────────────────────────────────────────
MODEL_PATH = "index_gte_test_sources"

# ── Qdrant ───────────────────────────────────────────────────────
# Reuses the gte container (port 6335) but separate collection.
COLLECTION_NAME = "test_sources_gte"
QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6335
