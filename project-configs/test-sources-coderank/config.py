# Calibration config: test_sources/ with nomic-ai/CodeRankEmbed.
# ================================================================
# Used to tune EMBED_MAX_SEQ_LENGTH before the full Informica build.
# Run with --clear --yes --log-to-file --collect-perf-stats, observe
# VRAM usage in the perf stats, then increase seq length until VRAM
# approaches 7.5 GB (leaving 0.5 GB headroom on an 8 GB card).
#
# Usage:
#   python src/index_rag.py --config test-sources-coderank --clear --yes --log-to-file --collect-perf-stats
#   python src/validate_rag.py --config test-sources-coderank
# ================================================================


# ── Source directories ───────────────────────────────────────────
SOURCE_DIRS = [
    {
        "path": "test_sources",
        "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj", ".sql"],
    },
]

# ── Embedding model ──────────────────────────────────────────────
MODEL_NAME = "nomic-ai/CodeRankEmbed"

# seq_len=4096, batch=32 hit combined peak 20.5 GB (right at ceiling) -> OOM on full corpus.
# seq_len=3072: attention = 3072²×12×2 = 4.3 GiB per sequence, well under 8 GB dedicated.
# Trying this to find the sweet spot between 2048 (safe, 1.0% truncation) and 4096 (OOM).
EMBED_MAX_SEQ_LENGTH = 3072
DENSE_EMBED_BATCH_SIZE = 32
EMBED_BATCH_MAX_TOKENS = 16000
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}
EMBED_DYNAMIC_VRAM_CAP = False

# ── Storage ──────────────────────────────────────────────────────
MODEL_PATH = "index_coderank_test_sources"

# ── Qdrant ───────────────────────────────────────────────────────
# Reuses the coderank container (port 6334) but separate collection.
COLLECTION_NAME = "test_sources_coderank"
QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6334
QDRANT_DOCKER_CONTAINER = "qdrant-informica_coderank"  # reuse existing container
