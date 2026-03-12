# Configuration for Informica RAG
# ================================================================
# Edit these values in one place to affect both indexer and MCP.
# Override any value by placing a config.py in a subdirectory
# (e.g. self-index/config.py) and running with --config <dir>.
# ================================================================

from pathlib import Path

# ════════════════════════════════════════════════════════════════════
# 1. SOURCE DIRECTORIES
# ════════════════════════════════════════════════════════════════════
# Each entry maps a directory path to the file extensions that should
# be indexed from it.  Only extensions that have a matching reader in
# shared/readers/READER_REGISTRY will actually be processed.
#
# Keys:
#   path          - Directory path relative to project root.
#   map_to_path   - (Optional) Remap path stored in metadata.
#   extensions    - List of file extensions to include.
#   exclude       - (Optional) Folder/path patterns to exclude at any depth.
#                   Single names match any path component (e.g. "__pycache__").
#                   Multi-segment patterns like "TURDUS/ENG" match consecutive
#                   path components.
#
# Example with exclude:
#   {
#       "path": ".",
#       "extensions": [".pas"],
#       "exclude": ["source", "schemas", ".venv", "test_sources"]
#   }
SOURCE_DIRS = [
    {
        "path": "source",
        "map_to_path": "delphi_src",
        "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj"],
        "exclude": [
            "TURDUS/ENG",
            "TURDUS/SRM",
            "TURDUS/UKR",
        ],
    },
    {
        "path": "schemas",
        "map_to_path": "sql_srcipt/6RedGate",
        "extensions": [".sql"],
    },
]

# For testing with test_sources only (uncomment and comment above):
# SOURCE_DIRS = [
#     {"path": "test_sources", "extensions": [".pas", ".dfm", ".sql", ".dproj", ".dpr"]}
# ]


# ════════════════════════════════════════════════════════════════════
# 2. EMBEDDING MODEL
# ════════════════════════════════════════════════════════════════════
# The embedding model converts code chunks into dense vectors.
# trust_remote_code=True is set in shared/embedding.py (MANDATORY for
# Jina's custom JinaBertModel architecture).

# MODEL_NAME = "BAAI/bge-m3"
# MODEL_PATH = "index_bge_m3_20260307_informica_2_0"

MODEL_NAME = "jinaai/jina-embeddings-v2-base-code"
MODEL_PATH = "index_jinaai_20260310_informica_2_0"  # Storage folder name

# Extra kwargs passed to HuggingFaceEmbedding(model_kwargs=...).
# float16 halves VRAM for model weights and activations.
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}


# ════════════════════════════════════════════════════════════════════
# 3. EMBEDDING SEQUENCE LENGTH & DYNAMIC VRAM CAP
# ════════════════════════════════════════════════════════════════════
# The jinaai model uses ALiBi attention which materializes a
# [1, heads, N, N] bias tensor every forward pass — O(N²) in VRAM.
# At the model's native max of 8192, this bias alone is ~1.5 GB in
# float16.  Capping at 4096 reduces it to ~384 MB while still fitting
# virtually all code chunks (MAX_CHUNK_CHARS=24000 ≈ 6000 tokens, so
# only a few very large chunks get truncated).
#
# Set to None to use the model's native max (risky on small GPUs).
EMBED_MAX_SEQ_LENGTH = 4096

# Dynamic VRAM cap: when enabled, the max sequence length is computed
# at indexing time based on actual GPU VRAM (dedicated + shared) using
# a quadratic solver in shared/vram_cap.py.  The computed value is
# clamped to [EMBED_MAX_SEQ_LENGTH, model_native_max].
#
# Only applies to CUDA devices (GPU indexing).  CPU (MCP server)
# always uses the static EMBED_MAX_SEQ_LENGTH.
EMBED_DYNAMIC_VRAM_CAP = False  # Set True to enable dynamic cap

# Safety margin: fraction of total VRAM to reserve (0.0-1.0).
# 0.15 = 15% reserved for OS, display, other processes.
EMBED_VRAM_SAFETY_MARGIN = 0.15

# Override GPU VRAM detection (MiB).  Set to None for auto-detect
# via nvidia-smi.  Useful for testing or when detection fails.
EMBED_VRAM_DEDICATED_MB = None  # None = auto-detect (e.g. 8188 for RTX 4060)
EMBED_VRAM_SHARED_MB = None  # None = auto-detect (e.g. 16384 for 32GB system)


# ════════════════════════════════════════════════════════════════════
# 4. EMBEDDING BATCH SIZES
# ════════════════════════════════════════════════════════════════════
# Control GPU memory usage during embedding.  Batches are flushed when
# either the count limit or the token limit is reached, whichever
# comes first.  Documents are sorted longest-first for optimal GPU
# utilization.
#
# These values are tuned for GeForce RTX 4060 (8 GB dedicated VRAM)
# with trust_remote_code=True (correct JinaBert model loading uses
# significantly more VRAM than the broken generic BertModel).
DENSE_EMBED_BATCH_SIZE = 32  # Max chunks per dense embedding batch
SPARSE_EMBED_BATCH_SIZE = 32  # Max chunks per sparse embedding batch
EMBED_BATCH_MAX_TOKENS = 16000  # Max approximate tokens per batch (chars / 4)


# ════════════════════════════════════════════════════════════════════
# 5. INDEXING MODE & SPARSE MODEL
# ════════════════════════════════════════════════════════════════════
# "dense"  - dense vectors only (backward compatible)
# "sparse" - sparse vectors only (lexical/keyword matching)
# "hybrid" - both dense + sparse vectors (best for code search)
INDEXING_MODE = "hybrid"

# Sparse embedding model (only used when INDEXING_MODE != "dense").
# SPARSE_MODEL_NAME = "prithivida/Splade_PP_en_v1"
SPARSE_MODEL_NAME = "Qdrant/bm25"

# Hybrid search alpha: blending weight at query time.
# 0.0 = all sparse (BM25), 1.0 = all dense.
# 0.5 was confirmed optimal (alpha=0.7 caused regressions — overview
# queries lost results because dense scores dominated).
# DO NOT CHANGE without re-running the full validation suite.
HYBRID_ALPHA = 0.5

# Two-pass hybrid embedding to save VRAM:
# False = dense first (save to SQLite), unload, then sparse + combine.
# True  = dense and sparse in one pass (requires more VRAM).
HYBRID_EMBED_SINGLE_PASS = False


# ════════════════════════════════════════════════════════════════════
# 6. COMPUTE DEVICES
# ════════════════════════════════════════════════════════════════════
INDEX_EMBED_DEVICE = "cuda"  # Device for indexing (cuda/cpu)
MCP_EMBED_DEVICE = "cpu"  # Device for MCP server queries (cuda/cpu)


# ════════════════════════════════════════════════════════════════════
# 6a. OPENVINO (INTEL GPU ACCELERATION)
# ════════════════════════════════════════════════════════════════════
# OpenVINO enables embedding on Intel integrated/discrete GPUs (e.g.
# Iris Xe, Arc) without requiring NVIDIA CUDA.  When enabled, the
# indexer and MCP server use OpenVINOEmbedding instead of
# HuggingFaceEmbedding, bypassing INDEX_EMBED_DEVICE / MCP_EMBED_DEVICE.
#
# Prerequisites:
#   uv pip install -r requirements_openvino.txt
#
# Verify Intel GPU is visible:
#   python -c "import openvino as ov; print(ov.Core().available_devices)"
#   # Should include 'GPU' for Intel graphics
#
# Performance note: OpenVINO GPU was ~15x faster than CPU-only PyTorch
# for indexing the self-index (62 files in ~4 min vs estimated 60+ min).
USE_OPENVINO_EMBEDDING = False  # Set True to use OpenVINO for embeddings

# OpenVINO device target.  Common values:
#   "GPU"   - Intel integrated/discrete GPU (recommended if available)
#   "CPU"   - OpenVINO CPU backend (still faster than PyTorch CPU)
#   "AUTO"  - Let OpenVINO pick the best available device
OPENVINO_EMBED_DEVICE = "GPU"


# ════════════════════════════════════════════════════════════════════
# 7. VECTOR DATABASE (QDRANT)
# ════════════════════════════════════════════════════════════════════
# Qdrant runs in Docker.  start_qdrant.bat reads these values via
# config_loader.py and sets them as env vars for docker-compose.yml.
# There is no .env file — all config lives here.
COLLECTION_NAME = "informica_rag"

QDRANT_USE_DOCKER = True  # Use Docker server (recommended)
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# BASE_PATH is auto-set by config_loader to {config_dir}/qdrant


# ════════════════════════════════════════════════════════════════════
# 8. MCP SERVER
# ════════════════════════════════════════════════════════════════════
MCP_SERVER_NAME = "informica-rag"
MCP_TOOL_NAME = "search_informica"
MCP_TOOL_DESCRIPTION = (
    "Search your Delphi codebase, SQL schemas, FastReport templates, "
    "and docs for relevant context."
)
MCP_HOST = "0.0.0.0"
MCP_PORT = 8123


# ════════════════════════════════════════════════════════════════════
# 9. HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════


def get_index_path() -> str:
    """Get the full index path based on BASE_PATH and MODEL_PATH."""
    return f"{BASE_PATH}/{MODEL_PATH}"


def get_qdrant_path() -> str:
    """Get the Qdrant index path (for migration purposes)."""
    return f"{BASE_PATH}/{MODEL_PATH}"
