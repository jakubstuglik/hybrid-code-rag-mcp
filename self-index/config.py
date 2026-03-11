# Override config for self-indexing the informica-rag project itself.
# Assumes working directory is the project root.

from pathlib import Path

SOURCE_DIRS = [
    {
        "path": "",  # empty string matches all files in root
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

# BASE_PATH is auto-set by config_loader to {config_dir}/qdrant
COLLECTION_NAME = "self_rag_index"
MODEL_PATH = "index_rag_self"

QDRANT_USE_DOCKER = True
QDRANT_HOST = "localhost"
QDRANT_PORT = 6973

# Use hybrid mode for better code identifier search
INDEXING_MODE = "hybrid"

# Two-pass hybrid embedding to save VRAM (default: False)
HYBRID_EMBED_SINGLE_PASS = False

# Use OpenVINO for Intel GPU acceleration (requires requirements_openvino.txt)
USE_OPENVINO_EMBEDDING = False

# OpenVINO device: "GPU" for Intel GPU, "CPU" for CPU-only
OPENVINO_EMBED_DEVICE = "GPU"

INDEX_EMBED_DEVICE = "cuda"  # Not used when USE_OPENVINO_EMBEDDING=True
MCP_EMBED_DEVICE = "cuda"  # Not used when USE_OPENVINO_EMBEDDING=True

# Override to avoid CUDA issues with float16 on CPU-only systems
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}

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
