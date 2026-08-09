# Index-specific config for self-indexing the hybrid-code-rag-mcp project itself.
# ================================================================
# Contains SOURCE_DIRS, Qdrant connection, MCP server identity,
# and storage paths for indexing this project's own source code.
#
# Usage:
#   python src/index_rag.py --config self-index --yes
#   python src/rag_mcp.py --config self-index --transport stdio
#
# Common/system settings (embedding model, batch sizes, VRAM cap,
# etc.) are inherited from the base config.py.
# ================================================================


# ── Source directories ───────────────────────────────────────────
# git_repo type gives branch-awareness: the working directory is
# verified to be on main_branch before indexing, and feature
# branches can be indexed as overlays via the "branches" list.
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": ".",  # this project IS the git repo
        "main_branch": "master",
        "branches": [],
        "sources": [
            {
                "path": ".",  # index from repo root
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
                    # Do NOT use "index_*" — it also matches src/index_rag.py
                    # and shared/index_state.py via path-component fnmatch.
                    "self-index",
                    "project-configs",
                    "__pycache__",
                    "node_modules",
                    ".pytest_cache",
                ],
            },
            {
                # Index only config.py files from project-configs (the main
                # source entry above excludes the whole directory).
                "path": "project-configs",
                "extensions": [".py"],
            },
        ],
    },
]

# ── Storage path ─────────────────────────────────────────────────
# BASE_PATH is auto-set by config_loader to {config_dir}/qdrant
MODEL_PATH = "index_rag_self"

# ── Qdrant connection ────────────────────────────────────────────
COLLECTION_NAME = "self_rag_index"
QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6973

# ── Compute devices ─────────────────────────────────────────────
# This host has AMD Radeon only (no NVIDIA / no ROCm TEI path).
# Force CPU for sparse BM25 and any local PyTorch fallbacks.
INDEX_EMBED_DEVICE = "cpu"
MCP_EMBED_DEVICE = "cpu"

# ── TEI (Text Embeddings Inference) — CPU host (no NVIDIA) ─────
# Keep TEI (not PyTorch). CPU path needs ORT-friendly float32 and
# tiny sequential requests: Jina ALiBi is O(N²); one long batch on
# float16/Candle took ~5 min with zero client progress logs.
USE_TEI = True
TEI_DOCKER_PORT = 8090
TEI_GPU = "cpu"
TEI_DTYPE = "float32"
TEI_DOCKER_IMAGE = "ghcr.io/huggingface/text-embeddings-inference:cpu-latest"

# Sequential embeds only. Default 64 concurrent requests stampede the
# CPU TEI queue (max_batch_requests≈4) and hit client timeouts.
TEI_CONCURRENT_REQUESTS = 1
# Long sequences on CPU can take minutes each; do not timeout mid-batch.
TEI_REQUEST_TIMEOUT = 3600

# One chunk per HTTP call — avoids packing several long docs into one
# ORT/Candle batch (that was the multi-minute "silent" hang).
DENSE_EMBED_BATCH_SIZE = 1
# Cap TEI server-side batch tokens (applied when container is created).
TEI_MAX_BATCH_TOKENS = 2048
EMBED_BATCH_MAX_TOKENS = 2048

# Frequent flushes so FLUSH lines prove progress and limit lost work.
EMBED_POOL_SIZE = 32
EMBED_POOL_MAX_FILES = 8

# ── MCP server identity ─────────────────────────────────────────
MCP_SERVER_NAME = "self-rag"
MCP_TOOL_NAME = "search_self_rag"
MCP_TOOL_DESCRIPTION = (
    "Hybrid semantic + keyword search over the hybrid-code-rag-mcp project's own "
    "source (Python indexer/MCP, readers, tests, docs, configs).\n\n"
    "USE WHEN: exploring how indexing, TEI, chunking, reranker, or MCP work; "
    "finding classes/functions/modules by name or concept; answering what/where/how "
    "about this repo before opening files.\n\n"
    "HOW TO QUERY: prefer symbols (e.g. embed_dense_batch, ChunkPool) or short "
    "concepts (\"TEI provenance\", \"branch overlay dedup\"). top_k 5–8 for exact "
    "lookups, 12–20 for overviews. Main branch is master — pass branch= only when "
    "not on master (`git branch --show-current`).\n\n"
    "RETURNS per hit: FILE, optional BRANCH, DISK_PATH, TYPE, LINES, chunk text.\n\n"
    "LIMITATIONS: reflects last successful self-index run. Call "
    "get_self_rag_index_state for indexed commit / freshness."
)
MCP_INDEX_STATE_TOOL_NAME = "get_self_rag_index_state"
MCP_INDEX_STATE_TOOL_DESCRIPTION = (
    "Report what state the self-rag index is serving for hybrid-code-rag-mcp: "
    "last index time, indexed master commit, overlays if any, collection stats, "
    "and whether live master HEAD matches the indexed commit. "
    "No parameters. Use before search when you need index freshness."
)
MCP_PORT = 8124
