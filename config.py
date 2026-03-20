# Common system configuration for all RAG indices.
# ================================================================
# This file contains ONLY common/system defaults: embedding model,
# devices, batch sizes, VRAM cap, indexing mode, etc.
#
# Index-specific settings (SOURCE_DIRS, COLLECTION_NAME, Qdrant
# connection, MCP server identity) live in dedicated config files:
#   - project-configs/config_informica/config.py  (Informica 2.0 Delphi/SQL codebase)
#   - self-index/config.py  (this project's own source code)
#   - project-configs/test-sources/config.py (curated test files for validation)
#
# Usage:
#   python src/index_rag.py --config config_informica --yes
#   python src/rag_mcp.py --config config_informica --transport stdio
#
# src/config_loader.py always loads this file first, then overlays
# the index-specific config on top.
# ================================================================

from pathlib import Path

# ════════════════════════════════════════════════════════════════════
# 1. INDEX-SPECIFIC DEFAULTS
# ════════════════════════════════════════════════════════════════════
# These are fallback defaults used when no --config override is given.
# In normal usage, these are always overridden by the index-specific
# config file.  They exist here so the system doesn't crash if someone
# runs index_rag.py without --config (they'll get a sensible error or
# a no-op rather than a NameError).
SOURCE_DIRS = []  # Override in index-specific config
COLLECTION_NAME = "default_rag"  # Override in index-specific config
MODEL_PATH = "default_index"  # Override in index-specific config
# ── Qdrant connection mode ───────────────────────────────────────
# "local"  - Local Docker container, auto-managed by shared/docker_utils.py.
#            Qdrant runs on localhost, storage is volume-mounted from disk.
#            Container is auto-started/created when the indexer or MCP server
#            starts.  QDRANT_HOST is always "localhost" in this mode.
# "remote" - Remote Qdrant server/cluster (self-hosted or Qdrant Cloud).
#            No Docker management.  Set QDRANT_HOST, QDRANT_PORT, and
#            optionally QDRANT_API_KEY / QDRANT_HTTPS for authenticated
#            connections.  Both the indexer and MCP server can point at the
#            same remote instance from different machines.
QDRANT_MODE = "local"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Remote connection options (used when QDRANT_MODE = "remote"):
QDRANT_API_KEY = None  # API key for authenticated Qdrant (e.g. Qdrant Cloud)
QDRANT_HTTPS = False  # Use HTTPS for the REST connection
QDRANT_PREFER_GRPC = False  # Use gRPC instead of HTTP REST (faster for bulk indexing)
QDRANT_GRPC_PORT = 6334  # gRPC port (Qdrant default: 6334)

# Local Docker options (used when QDRANT_MODE = "local"):
# Container name: auto-derived as "qdrant-{COLLECTION_NAME}" when None.
QDRANT_DOCKER_CONTAINER = None
# Volume path: auto-derived as "{BASE_PATH}/{MODEL_PATH}" when None.
QDRANT_DOCKER_VOLUME = None
MCP_SERVER_NAME = "rag-server"
MCP_TOOL_NAME = "search_rag"
MCP_TOOL_DESCRIPTION = (
    "Search the indexed codebase for relevant code, classes, functions, SQL procedures, "
    "forms, and documentation. Returns matching code chunks with file paths and line numbers. "
    "Supports branch-aware search: pass a git branch name in the 'branch' parameter to "
    "include feature branch changes alongside main branch results."
)
MCP_HOST = "0.0.0.0"
MCP_PORT = 8123


# ════════════════════════════════════════════════════════════════════
# 2. EMBEDDING MODEL
# ════════════════════════════════════════════════════════════════════
# The embedding model converts code chunks into dense vectors.
# trust_remote_code=True is set in shared/embedding.py (MANDATORY for
# Jina's custom JinaBertModel architecture).
MODEL_NAME = "jinaai/jina-embeddings-v2-base-code"

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
# Default True — with TEI backend, dense goes through Docker (no local VRAM),
# so there is no VRAM contention reason to separate passes.
HYBRID_EMBED_SINGLE_PASS = True


# ════════════════════════════════════════════════════════════════════
# 6. COMPUTE DEVICES
# ════════════════════════════════════════════════════════════════════
# These control the PyTorch/ONNX device for embedding.
#
# When USE_TEI=False (PyTorch mode):
#   INDEX_EMBED_DEVICE controls both dense and sparse during indexing.
#   MCP_EMBED_DEVICE controls both dense and sparse during MCP queries.
#
# When USE_TEI=True (TEI mode):
#   Dense embeddings go through the TEI Docker container (device is
#   managed by TEI itself — GPU or CPU depending on Docker image).
#   Sparse BM25 STILL uses INDEX_EMBED_DEVICE / MCP_EMBED_DEVICE for
#   its ONNX execution provider (CUDAExecutionProvider vs CPU).
#   For full CPU mode with TEI, set BOTH to "cpu".
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
#   uv pip install -r requirements/requirements_openvino.txt
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
# 6b. TEI (TEXT EMBEDDINGS INFERENCE)
# ════════════════════════════════════════════════════════════════════
# HuggingFace Text Embeddings Inference (TEI) is a high-performance
# Docker-based embedding server using Candle (Rust) inference.
# When enabled, dense embeddings are served by an HTTP endpoint
# instead of loading the model into the Python process.  Sparse
# embeddings (BM25) remain local regardless.
#
# TEI and PyTorch produce INCOMPATIBLE vectors (different inference
# engines).  The indexer tracks provenance ("tei" vs "pytorch") in
# Qdrant collection metadata.  Mixing backends for the same
# collection requires a full reindex (--clear).
#
# Prerequisites:
#   Docker Desktop must be running.  The TEI container is auto-managed
#   (created/started) just like Qdrant containers.
#
# Hardware auto-detection:
#   nvidia-smi succeeds → NVIDIA CUDA Docker image
#   No NVIDIA GPU       → CPU Docker image
#
# Phase 2 (not yet implemented): Intel XPU via custom Dockerfile.
# See docs/tei-intel-xpu.md for details.
USE_TEI = True  # TEI is the recommended backend (4.5x faster, 3.3x less VRAM)

# TEI server URL.  When None, auto-derived as http://localhost:{TEI_DOCKER_PORT}.
# Set explicitly if TEI runs on a remote machine or non-default port.
TEI_URL = None

# Host port for the TEI Docker container.
TEI_DOCKER_PORT = 8090

# Data type for TEI inference.  TEI only supports "float16" or "float32".
# float16 is recommended (faster, lower VRAM, sufficient precision).
TEI_DTYPE = "float16"

# Docker image override.  When None, auto-detected based on hardware:
#   NVIDIA GPU → ghcr.io/huggingface/text-embeddings-inference:{CC}-1.9
#   CPU only   → ghcr.io/huggingface/text-embeddings-inference:cpu-1.9
# where {CC} is the CUDA compute capability (e.g. "89" for RTX 4060).
TEI_DOCKER_IMAGE = None

# Local model cache directory to mount into the TEI container.
# When None, auto-derived as {BASE_PATH}/tei_model_cache.
# TEI downloads the model on first start; this mount persists it.
TEI_MODEL_DIR = None

# ── Embedding text prefixes ─────────────────────────────────────
# Some models require specific prefixes prepended to text before embedding.
# For example, Nomic Embed V2 requires "search_query: " for queries and
# "search_document: " for documents.  Leave as None or "" for models
# that don't use prefixes (Jina, BGE-M3, Qwen3, Gemma, etc.).
#
# These prefixes are applied transparently inside TEIEmbedding and
# HuggingFaceEmbedding wrappers — callers (indexer, MCP, validate_rag)
# don't need to know about them.
EMBED_QUERY_PREFIX = None  # e.g. "search_query: " for Nomic
EMBED_TEXT_PREFIX = None  # e.g. "search_document: " for Nomic


# ════════════════════════════════════════════════════════════════════
# 7. GIT BRANCH-AWARE INDEXING
# ════════════════════════════════════════════════════════════════════
# Enables indexing multiple git branches as overlays on a main branch
# index.  Only files that differ between a feature branch and the main
# branch are indexed under the feature branch label — unchanged files
# are served from the main branch vectors.
#
# To use this feature, SOURCE_DIRS entries must use type="git_repo":
#
#   SOURCE_DIRS = [
#       {
#           "type": "git_repo",
#           "path": "../my-repo",           # Git repo root
#           "main_branch": "develop",       # Main/default branch
#           "branches": ["feature/foo"],    # Feature branches to index
#           "sources": [                    # Source dirs within the repo
#               {"path": "src", "extensions": [".py"]},
#           ],
#       },
#       {
#           "type": "source_set",           # Or omit "type" for legacy format
#           "path": "./docs",
#           "extensions": [".md"],
#       },
#   ]
#
# source_set entries (or legacy flat format without "type") are
# branch-agnostic — their chunks appear in ALL queries regardless
# of the branch parameter.
#
# MCP query-time behavior:
#   - No branch param: returns main-branch + non-git chunks
#   - branch="feature/foo": returns main + feature + non-git chunks,
#     with post-retrieval dedup preferring feature-branch versions.
#
# DIFF_FULL_REINDEX_THRESHOLD: if the ratio of changed files to total
# indexed files in a repo group exceeds this value, the indexer falls
# back to a full reindex instead of a differential update.
# This global default can be overridden per git_repo entry via the
# "diff_full_reindex_threshold" key.
DIFF_FULL_REINDEX_THRESHOLD = 0.5


# ════════════════════════════════════════════════════════════════════
# 8. HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════
# BASE_PATH is auto-set by config_loader to {config_dir}/qdrant.
# MODEL_PATH is set by each index-specific config file.
# These functions combine them to get the full storage path.


def get_index_path() -> str:
    """Get the full index path based on BASE_PATH and MODEL_PATH."""
    return f"{BASE_PATH}/{MODEL_PATH}"


def get_qdrant_path() -> str:
    """Get the Qdrant index path (for migration purposes)."""
    return f"{BASE_PATH}/{MODEL_PATH}"
