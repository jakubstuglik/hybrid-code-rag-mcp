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
                    "index_*",
                    "self-index",
                    "project-configs",
                    "__pycache__",
                    "node_modules",
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

# ── Compute devices (overrides) ─────────────────────────────────
# Self-index MCP server runs on CUDA (small index, fast queries)
MCP_EMBED_DEVICE = "cuda"

# ── TEI (Text Embeddings Inference) ─────────────────────────────
# Self-index uses TEI for dense embeddings (same as production).
# Port 8091 to avoid collision with informica TEI on 8090.
USE_TEI = True
TEI_DOCKER_PORT = 8091

# Larger batch size for self-index (small index, fits easily)
DENSE_EMBED_BATCH_SIZE = 64

# ── MCP server identity ─────────────────────────────────────────
MCP_SERVER_NAME = "self-rag"
MCP_TOOL_NAME = "search_self_rag"
MCP_TOOL_DESCRIPTION = (
    "Search the hybrid-code-rag-mcp project's own source code, configs, and documentation "
    "for relevant context. Returns matching code chunks with file paths and line numbers. "
    "Supports branch-aware search: pass a git branch name in the 'branch' parameter to "
    "include feature branch changes alongside the main branch."
)
MCP_PORT = 8124
