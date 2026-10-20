# Common system configuration for all RAG indices.
# ================================================================
# This file contains ONLY common/system defaults: embedding model,
# devices, batch sizes, VRAM cap, indexing mode, etc.
#
# Index-specific settings (SOURCE_DIRS, COLLECTION_NAME, Qdrant
# connection, MCP server identity) live in dedicated config files:
#   - project-configs/config_myproject/config.py  (Delphi/SQL codebase)
#   - self-index/config.py  (this project's own source code)
#   - project-configs/test-sources/config.py (curated test files for validation)
#
# Usage:
#   python src/index_rag.py --config config_myproject --yes
#   python src/rag_mcp.py --config config_myproject --transport stdio
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
# Client request timeout in seconds (None = qdrant-client default, 5 s for REST).
# Large wait=true upserts into a multi-million-point collection can take >5 s.
QDRANT_TIMEOUT = 60

# Remote connection options (used when QDRANT_MODE = "remote"):
QDRANT_API_KEY = None  # API key for authenticated Qdrant (e.g. Qdrant Cloud)
QDRANT_HTTPS = False  # Use HTTPS for the REST connection
QDRANT_PREFER_GRPC = False  # Use gRPC instead of HTTP REST (faster for bulk indexing)
QDRANT_GRPC_PORT = 6334  # gRPC port (Qdrant default: 6334)
QDRANT_DELETE_TIMEOUT = (
    60  # Seconds to wait for a delete-by-filter call (large files need more)
)
# How many file_path values to put in one MatchAny delete filter.
# Larger chunks mean fewer round-trips; keep below Qdrant filter limits.
QDRANT_DELETE_CHUNK_SIZE = 500

# For git_repo sources, skip files ignored by git (.gitignore, nested
# .gitignore, .git/info/exclude, global excludes). Tracked files always
# stay (tracked wins). Non-git sources are unchanged. Default True so
# generated dirs like build/ are never indexed; a refresh then deletes
# vectors for paths that become ignored.
RESPECT_GITIGNORE = True

# Local Docker options (used when QDRANT_MODE = "local"):
# Container name: auto-derived as "qdrant-{COLLECTION_NAME}" when None.
QDRANT_DOCKER_CONTAINER = None
# Volume path: auto-derived as "{BASE_PATH}/{MODEL_PATH}" when None.
QDRANT_DOCKER_VOLUME = None
MCP_SERVER_NAME = "rag-server"
MCP_TOOL_NAME = "search_rag"
MCP_TOOL_DESCRIPTION = (
    "Hybrid semantic + keyword search over this index's codebase "
    "(dense embeddings + BM25).\n\n"
    "USE WHEN: locating classes, functions, methods, SQL objects, configs, or docs "
    "by meaning or name; answering what/where/how questions about the indexed code; "
    "needing file path + line range + chunk text before opening files.\n\n"
    "HOW TO QUERY: prefer concrete identifiers when known; short conceptual phrases "
    "for architecture; top_k 5–8 for exact lookups, 12–20 for broad/overview queries. "
    "Always pass branch= when your working tree is NOT the configured main branch "
    "(use `git branch --show-current`); omit branch only on main.\n\n"
    "RETURNS per hit: FILE, optional BRANCH, DISK_PATH, TYPE (node_type), LINES, "
    "then chunk text (≤4000 chars).\n\n"
    "LIMITATIONS: results reflect the last successful index run, not uncommitted edits. "
    "Call get_index_state to see indexed commit / freshness. Large chunks may be "
    "truncated for embedding; BM25 still matches keywords."
)
MCP_INDEX_STATE_TOOL_NAME = "get_index_state"
MCP_INDEX_STATE_TOOL_DESCRIPTION = (
    "Report what repository/source state this RAG index is serving: last index "
    "completion time, indexed git commit(s), branch and tag overlays, non-git "
    "source fingerprints, collection point count / embed backend, and whether "
    "live main-branch HEAD still matches the indexed commit. "
    "Call before relying on search when you need to know if the index matches "
    "your current branch/commit. No parameters."
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
# PyTorch backend (TEI uses TEI_DTYPE instead).
#
# VRAM impact: "float16" / "bfloat16" store weights AND activations in
# 2 bytes instead of 4, i.e. roughly half the VRAM of float32.
#   - "float16":  default; fine for Jina v2.
#   - "bfloat16": use for models trained in bf16 (e.g. Gemma-based
#                 embedders); needs an Ampere+ GPU (RTX 30xx/40xx).
#   - omit / "float32": CPU indexing, or to rule out fp16 overflow issues.
# Changing dtype changes the vectors slightly -> reindex with --clear.
# See README "Tuning GPU memory (VRAM)".
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
#
# VRAM impact (PyTorch backend): the largest single lever.  Activation
# memory of one forward pass grows ~linearly with sequence length, and
# the attention part ~quadratically (N^2) unless the model uses a
# memory-efficient attention kernel.  Every token above the cap is
# dropped from the dense vector (BM25 still sees the full chunk), so
# lowering it trades retrieval quality on very long chunks for VRAM.
# Example starting points (NOT measured; see README "Tuning GPU memory"):
#   12 GB GPU: 4096    8 GB GPU: 2048    CPU: 4096 (RAM is not the limit,
#   but long sequences are slow on CPU).
# Changing it changes vectors of truncated chunks -> reindex with --clear.
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
EMBED_VRAM_DEDICATED_MB = None  # None = auto-detect (e.g. ~8188 on an 8 GB card)
EMBED_VRAM_SHARED_MB = None  # None = auto-detect (e.g. 16384 for 32GB system)


# ════════════════════════════════════════════════════════════════════
# 4. EMBEDDING BATCH SIZES
# ════════════════════════════════════════════════════════════════════
# Control GPU memory usage during embedding.  Batches are flushed when
# either the count limit or the token limit is reached, whichever
# comes first.  Documents are sorted longest-first for optimal GPU
# utilization.  A single chunk larger than the token budget still forms
# its own batch (it is truncated to EMBED_MAX_SEQ_LENGTH by the model).
#
# How these map to VRAM depends on the backend:
#
#   PyTorch (USE_TEI=False): _embed_batched() builds a batch of at most
#     DENSE_EMBED_BATCH_SIZE chunks / EMBED_BATCH_MAX_TOKENS tokens and
#     hands it to llama_index HuggingFaceEmbedding, which splits it again
#     into forward passes of embed_batch_size chunks (llama_index default
#     10; not set by this project).  Each forward pass is padded to its
#     longest chunk (<= EMBED_MAX_SEQ_LENGTH).  Peak activation VRAM is
#     therefore driven by
#         min(10, DENSE_EMBED_BATCH_SIZE) x min(longest chunk, MAX_SEQ)
#     further bounded by EMBED_BATCH_MAX_TOKENS.  Only ONE batch is on the
#     GPU at a time (one dense worker, see EMBED_PIPELINE_DEPTH).
#
#   TEI (USE_TEI=True): DENSE_EMBED_BATCH_SIZE is not used for the
#     concurrent path; TEI forms its own GPU batches, bounded by
#     --max-batch-tokens (TEI_MAX_BATCH_TOKENS, default = this
#     EMBED_BATCH_MAX_TOKENS).  The VRAM lives in the TEI container.
#
# "tokens" here are approximate (chars / 4).  Code often tokenizes to
# more tokens than chars/4, so the real token count can exceed the budget;
# keep headroom.
#
# NOTE: since llama_index caps a pass at 10 chunks, DENSE_EMBED_BATCH_SIZE
# only lowers VRAM when set below 10.  EMBED_BATCH_MAX_TOKENS bounds passes
# of long chunks (linear).  Neither changes vectors (no --clear needed).
# Example starting points (PyTorch, NOT measured; see README):
#                           12 GB     8 GB      CPU
#   DENSE_EMBED_BATCH_SIZE  32        16        32
#   EMBED_BATCH_MAX_TOKENS  16000     8000      16000
# The 12 GB values are the defaults; with a ~300M-parameter model in
# bfloat16 they leave little headroom on a 12 GB card (example).  If you hit "CUDA out of memory", halve
# EMBED_BATCH_MAX_TOKENS first, then lower EMBED_MAX_SEQ_LENGTH.
# SPARSE_EMBED_BATCH_SIZE only affects the sparse model (Qdrant/bm25 runs
# on CPU) - no VRAM impact with BM25.
DENSE_EMBED_BATCH_SIZE = 32  # Max chunks per dense embedding batch
SPARSE_EMBED_BATCH_SIZE = 32  # Max chunks per sparse embedding batch
EMBED_BATCH_MAX_TOKENS = 16000  # Max approximate tokens per batch (chars / 4)

# Cross-file chunk pooling: accumulate chunks from multiple files
# before embedding, so _embed_batched() can sort by length across
# files for better GPU utilization and reduced padding waste.
#
# Pool flushes when EITHER threshold is reached:
#   - EMBED_POOL_SIZE chunks accumulated
#   - EMBED_POOL_MAX_FILES files in the pool
# Set EMBED_POOL_SIZE = 0 to disable pooling (per-file embedding).
#
# Phase 2 double-buffer: upsert of pool N runs on a background thread
# while pool N+1 is being embedded.  EMBED_POOL_MAX_FILES=150 ensures
# even small-file regions accumulate enough chunks that embedding time
# exceeds upsert time, so the GPU never stalls waiting for upsert I/O.
# VRAM impact: none directly (pools are host RAM).  Larger pools give
# better length sorting (less padding per batch).
# TEI: keep EMBED_POOL_SIZE clearly below TEI's --max-concurrent-requests
# (default 512).  A pool may overshoot EMBED_POOL_SIZE (the last file is
# added whole), and a pool larger than TEI's limit is answered with
# HTTP 429 "Model is overloaded", which aborts the run (with any
# EMBED_PIPELINE_DEPTH, including 0).  This shows up mostly with slow (CPU)
# TEI, where requests stay queued.  256 is a safe value; see README
# "TEI on CPU".
EMBED_POOL_SIZE = 512  # Max chunks to accumulate before flush
EMBED_POOL_MAX_FILES = 150  # Max files in pool before flush

# Pipelined embedding (keeps the GPU busy across pool boundaries).
# OPT-IN: default 0 = legacy serial flush (same behaviour as before this
# option existed).  Recommended for TEI on a GPU: e.g. 6.  Little or no
# gain on CPU (see below).  N > 0 = up to N pools in the dense stage at once:
# dense embedding runs on worker thread(s) (N concurrent pools for TEI, 1 for
# other backends) while a post-worker does sanitize + sparse + build + upsert
# as each pool's dense finishes (out of order), and the main thread keeps
# parsing/pooling the next files. With a GPU backend this removes the GPU
# idle time between pools (on an example index, wall time dropped by ~40%
# with TEI).
#
# VRAM impact:
#   PyTorch / OpenVINO: none - there is exactly one dense worker, so only
#     one batch is on the GPU at a time regardless of depth.  Depth only
#     controls how many pools wait in host RAM.  (An experiment running two
#     concurrent dense pools + one large encode() per batch on PyTorch ran
#     out of memory on a 12 GB GPU and was reverted - do not add
#     concurrency to the PyTorch dense stage without measuring peak VRAM.)
#   TEI: none in this process; the extra requests just queue inside TEI,
#     whose GPU batches stay bounded by --max-batch-tokens.
# Host RAM: up to N pools (EMBED_POOL_SIZE chunks each, texts + vectors)
# in flight.  Use 0 to get the legacy serial code path.
# TEI on CPU: depth gives little - dense embedding dominates wall time and
# keeps the CPU busy even with depth 0, so there are no idle gaps to fill.
# Keep 0 there; any depth is safe as long as EMBED_POOL_SIZE is small.
EMBED_PIPELINE_DEPTH = 0
# Parse-ahead queue length (files).  Used by the parse-ahead thread with
# ANY EMBED_PIPELINE_DEPTH, including 0 (previously hard-coded to 2).  The
# parser may run up to this many files ahead of embedding (host RAM).
# Set 2 for the exact previous behaviour.  With the pipeline it must be
# large: with a short queue the parser stalls whenever the main thread waits for a pipeline slot, and the
# next pool is not ready when a slot frees up (GPU idles).
# VRAM impact: none (parsed files are held in host RAM only).
EMBED_PARSE_QUEUE_SIZE = 400

# Parallel file parsing/chunking in the indexer parse-ahead path.
# 1 = sequential (default, same as before). Set e.g. 4 or 8 to use a
# thread pool. Opt-in only: it helps only when parsing, not embedding,
# is the bottleneck (no speedup measured on GPU embedding-bound runs).
INDEX_PARSE_WORKERS = 1
# Points per Qdrant upsert call.
QDRANT_UPSERT_BATCH_SIZE = 500
# Upper bound on the estimated JSON size of one upsert request.  Qdrant rejects
# bodies above service.max_request_size_mb (32 MB default), and closes the
# socket mid-upload (seen as WinError 10053/10054); 16 MB leaves headroom.
# A rejected batch is also split in half and retried automatically.
QDRANT_UPSERT_MAX_BYTES = 16 * 1024 * 1024


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

# Hybrid fusion depth: candidates fetched per leg (dense and sparse) before
# Relative Score Fusion.  The fused list is still cut to the reranker input
# size, so this only lets chunks that rank moderately in both legs reach the
# reranker.  None = legs fetch exactly the reranker input size.
# Default 100: validated on large C and C++ repositories; it costs a few ms per
# query.  Set None to restore the reranker-input-sized legs.
HYBRID_PREFETCH_K = 100

# Exact symbol lookup: when a query names a code identifier (snake_case,
# camelCase, Owner::member, "struct foo", "foo()"), up to this many chunks whose
# SYMBOL_LOOKUP_FIELDS payload equals that name are added to the reranker pool.
# 0 = off.  Works without a payload index; new collections get a keyword index.
SYMBOL_LOOKUP_K = 4
# Payload fields holding declared names: "object_name" (every reader) and
# "symbols" (all names of a grouped chunk, newer readers).
SYMBOL_LOOKUP_FIELDS = ["object_name", "symbols"]
# Score given to added candidates before reranking: "bar" = score of the last
# candidate that would be returned (they need a rerank bonus to move up),
# "top" = best score in the pool.
SYMBOL_LOOKUP_SCORE = "top"

# Pool-level rerank options (see docs/reranker.md).  The defaults below are the
# validated combination; the core mention penalty stays off and per-language
# values live in the reader rerank profiles.
# Demote chunks that only mention an identifier the query names while another
# candidate declares it: core value for every language, or the per-language
# value of the reader's rerank profile.
RERANK_CORE_MENTION_PENALTY = 0.0
RERANK_PROFILE_MENTION = True
# Per-language "query asks for an enumeration / flags" boosts.
RERANK_TYPE_INTENT = True
# Queries about several places ("A and B", "both", "across"): at most this many
# results per file keep their rank (0 = off).
RERANK_FILE_CAP = 2
# Path globs (fnmatch on the indexed file_path, "/" separators) of code that is
# rarely the answer, e.g. ["*/third_party/*", "*/examples/*"].  Matching chunks
# lose DEPRIORITIZED_PATH_PENALTY unless the query names a word of the glob.
DEPRIORITIZED_PATHS = ["*/tools/*", "*/tests/*", "*/test/*", "*/testing/*"]
DEPRIORITIZED_PATH_PENALTY = 0.10
# Extra demotion for a prototype / declaration-only chunk when a candidate with
# a body declares the identifier the query names (0 = off).
RERANK_PROTOTYPE_YIELD = 0.3
# Behaviour queries ("handle a page fault"): type summaries (struct / class
# bodies) yield to function bodies by the profile's summary_yield times this
# scale; only profiles that set summary_yield (C/C++) are affected (0 = off).
RERANK_BODY_PREFERENCE = 1.0

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
#   Dense embeddings go through the TEI Docker container (GPU selection
#   is controlled by TEI_GPU below, not by INDEX_EMBED_DEVICE).
#   Sparse BM25 STILL uses INDEX_EMBED_DEVICE / MCP_EMBED_DEVICE for
#   its ONNX execution provider (CUDAExecutionProvider vs CPU).
#   For full CPU mode with TEI, set BOTH to "cpu".
#
# Accepted values for INDEX_EMBED_DEVICE / MCP_EMBED_DEVICE:
#   "auto"      — use GPU with most free VRAM (recommended default when
#                 USE_TEI=False); equivalent to legacy "cuda" on single-GPU
#   "cuda"      — same as "auto" (backward-compatible alias)
#   "0","1",... — specific GPU by index (e.g. "1" for second GPU)
#   "cpu"       — CPU only
INDEX_EMBED_DEVICE = "auto"  # Device for indexing (auto/cuda/0/1.../cpu)
MCP_EMBED_DEVICE = "cpu"  # Device for MCP server queries (auto/cuda/0/1.../cpu)


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
# Hardware auto-detection (controlled by TEI_GPU below):
#   TEI_GPU="auto" → GPU with most free VRAM → CUDA Docker image
#   TEI_GPU="cpu"  → no GPU → CPU Docker image
#   TEI_GPU="N"    → specific GPU index N → CUDA Docker image for that GPU
#
# Phase 2 (not yet implemented): Intel XPU via custom Dockerfile.
# See docs/features/tei-batch-saturation/tei-intel-xpu.md for details.
USE_TEI = True  # TEI is the recommended backend (4.5x faster, 3.3x less VRAM)

# Which GPU the TEI Docker container should use.
#
# Accepted values:
#   "auto"      — pick the GPU with the most free VRAM at container start
#                 time.  Recommended default.  On a single-GPU system this
#                 is equivalent to "0".  On a multi-GPU system it picks the
#                 one with the most headroom (e.g. the dedicated desktop GPU
#                 rather than the laptop integrated GPU).
#   "0","1",... — specific GPU by physical index (as shown by nvidia-smi -L).
#   "cpu"       — no GPU passthrough; forces CPU Docker image regardless of
#                 TEI_DOCKER_IMAGE.  Also set TEI_DTYPE="float32" for CPU.
#
# Note: TEI runs on ONE GPU only (no multi-GPU model parallelism).
# The physical index is mapped to container device 0 by Docker.
TEI_GPU = "auto"

# TEI server URL.  When None, auto-derived as http://127.0.0.1:{TEI_DOCKER_PORT}
# (IPv4 loopback: "localhost" may resolve to ::1, which Docker Desktop on
# Windows serves through a relay that resets connections under load).
# Set explicitly if TEI runs on a remote machine or non-default port.
TEI_URL = None

# Host port for the TEI Docker container.
TEI_DOCKER_PORT = 8090

# Concurrent HTTP requests to TEI per embedding call (1 = synchronous).
# With EMBED_PIPELINE_DEPTH > 0 the total in flight is depth x this value.
TEI_CONCURRENT_REQUESTS = 16

# Data type for TEI inference.  TEI only supports "float16" or "float32".
# float16 is recommended (faster, lower VRAM, sufficient precision).
TEI_DTYPE = "float16"

# Docker image override.  When None, auto-detected based on hardware:
#   NVIDIA GPU → ghcr.io/huggingface/text-embeddings-inference:{CC}-1.9
#   CPU only   → ghcr.io/huggingface/text-embeddings-inference:cpu-1.9
# where {CC} is the CUDA compute capability (e.g. "89" for Ada / RTX 40xx).
TEI_DOCKER_IMAGE = None

# Local model cache directory to mount into the TEI container.
# When None, auto-derived as {BASE_PATH}/tei_model_cache.
# TEI downloads the model on first start; this mount persists it.
TEI_MODEL_DIR = None

# TEI server-side batch token budget.  Controls TEI's internal
# --max-batch-tokens parameter, which limits total tokens per inference
# batch.  When None, auto-derived from EMBED_BATCH_MAX_TOKENS (our
# client-side token budget) to prevent TEI from splitting batches
# that we already sized to fit.
#
# VRAM impact (TEI): the main activation-memory knob for TEI; TEI's VRAM
# is roughly model weights + buffers for one batch of this many tokens.
# It is passed when the container is CREATED - after changing it, remove
# the TEI container so it is recreated.  For a small (~150M) model in
# float16, 16000 fits an 8 GB GPU (example).  Lower it (e.g. 8000) if TEI
# fails to start or OOMs on a smaller GPU or with a larger model.
# TEI on CPU (float32): the same budget is allocated in host RAM; a large
# value can get the container OOM-killed during warm-up.  Start with ~4096
# on CPU and raise it only if the container has RAM to spare.
TEI_MAX_BATCH_TOKENS = None

# Number of tokenization workers inside the TEI container.
# Controls TEI's --tokenization-workers parameter.
# When None, TEI uses its platform default.  Set to 2-4 for
# parallelized tokenization on multi-core machines.
TEI_TOKENIZATION_WORKERS = None


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

# PyTorch path only: extra SentenceTransformer config kwargs and
# Matryoshka output dimension (None = native).
EMBED_CONFIG_KWARGS = None  # e.g. {"vision_config": None, "audio_config": None}
EMBED_TRUNCATE_DIM = None  # e.g. 512 for MRL models


# ════════════════════════════════════════════════════════════════════
# 7. GIT OVERLAYS (BRANCHES AND MOVING TAGS)
# ════════════════════════════════════════════════════════════════════
# Index selected git refs as overlays on a main branch. Only files that
# differ are stored under the overlay's name. Unchanged files are served
# from the main-branch vectors. The overlay name is a label: it is the
# payload value and the search argument. It is not parsed as a ref type.
#
#   branches: ["feature/foo"]
#       Legacy form. Each name is kind "branch": three-dot diff from the
#       merge-base (commits on that branch since it left main).
#
#   overlays: [
#       {"name": "feature/foo", "kind": "branch"},
#       {"name": "current_release", "kind": "tag", "diff": "against_main_tip"},
#   ]
#       "kind" is optional and defaults to "branch", so existing configs
#       need no change. kind "branch" is the same three-dot diff as the
#       legacy list ("diff" may be omitted or set to "merge_base").
#       kind "tag" requires diff "against_main_tip": it peels the tag
#       (annotated or lightweight) to a commit and diffs that tree against
#       the main tip. Intended for a moving tag (e.g. current_release)
#       that is re-pointed as releases happen, so the overlay holds only
#       the release's differences from main. Moving the tag and
#       re-running the indexer refreshes the set. Paths that no longer
#       differ from main are deleted from the overlay.
#
# A name in `branches` and the same name as a branch overlay are one
# overlay. The same name as both a branch and a tag is a config error.
# Tag names are not fetched as branches. git_pull_guard.py force-updates
# each configured tag from origin (only those refs); if that fetch fails it
# warns and the local tag is used.
#
# Each overlay has a manifest index_manifest_branch_<sanitized>.json (tags
# too) with kind, files, tombstones, indexed_at and overlay_signature, plus
# merge_base/last_branch_commit (branch) or last_resolved_commit (tag).
# overlay_signature hashes kind, overlay commit, base (merge-base or main
# tip) and the repo group settings. When it is unchanged (and Qdrant still
# has points for an overlay that lists files), the run logs "[TAG] <name> overlay is up to date
# (refs unchanged)" (or [BRANCH]) and reads no files. Old manifests get one
# full compare that adds the signature. Removing an overlay from config
# deletes its points, manifest and chunk_histogram_branch_<sanitized>.json.
#
# To use this feature, SOURCE_DIRS entries must use type="git_repo":
#
#   SOURCE_DIRS = [
#       {
#           "type": "git_repo",
#           "path": "../my-repo",           # Git repo root
#           "main_branch": "develop",       # Main/default branch
#           "branches": ["feature/foo"],    # Still accepted: kind branch
#           "overlays": [
#               {"name": "current_release", "kind": "tag",
#                "diff": "against_main_tip"},
#           ],
#           "sources": [                    # Source dirs within the repo
#               {"path": "src", "extensions": [".py"]},
#               # sql_dialect: "tsql" (default) or "postgresql".
#               # Omitted means tsql, so current indexes keep their chunks.
#               # A change reindexes only the .sql files on that path.
#               {"path": "sql", "extensions": [".sql"], "sql_dialect": "tsql"},
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
# The indexer reads overlay blobs with git show. It does not check out
# the branch or the tag, and it does not create a worktree. The working
# copy for main-branch indexing must still be on main_branch.
#
# MCP query-time behavior (one argument, no separate tag parameter):
#   - No branch param: returns main-branch + non-git chunks
#   - branch="feature/foo" or branch="current_release": main plus that
#     overlay. The overlay wins on the same path. Tombstones hide files
#     the overlay deletes. If that name has never been indexed, the
#     filter matches nothing extra and the caller gets main.

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
