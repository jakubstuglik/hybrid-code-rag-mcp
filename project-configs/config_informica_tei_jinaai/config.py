# TEI benchmark config: jinaai/jina-embeddings-v2-base-code via TEI
# ================================================================
# Same Informica sources as config_informica, but using TEI (Candle)
# backend for dense embeddings instead of PyTorch.
#
# Usage:
#   python src/index_rag.py --config config_informica_tei_jinaai --clear --yes
#   python src/validate_rag.py --config config_informica_tei_jinaai --json
# ================================================================


# ════════════════════════════════════════════════════════════════════
# 1. SOURCE DIRECTORIES  (identical to config_informica)
# ════════════════════════════════════════════════════════════════════
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": "../informica_2_0",
        "main_branch": "develop",
        "branches": ["task/T37523"],
        "sources": [
            {
                "path": "delphi_src",
                "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj"],
                "exclude": [
                    "TURDUS/ENG",
                    "TURDUS/SRM",
                    "TURDUS/UKR",
                ],
            },
            {
                "path": "sql_srcipt/6RedGate",
                "map_to_path": "sql_srcipt/6RedGate",
                "extensions": [".sql"],
            },
        ],
    },
]


# ════════════════════════════════════════════════════════════════════
# 2. STORAGE PATH
# ════════════════════════════════════════════════════════════════════
MODEL_PATH = "index_tei_jinaai_informica"


# ════════════════════════════════════════════════════════════════════
# 3. VECTOR DATABASE (QDRANT) — separate port to avoid collision
# ════════════════════════════════════════════════════════════════════
COLLECTION_NAME = "informica_tei_jinaai"

QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6340


# ════════════════════════════════════════════════════════════════════
# 4. MCP SERVER  (not used during benchmark, but defined for completeness)
# ════════════════════════════════════════════════════════════════════
MCP_SERVER_NAME = "informica-tei-jinaai"
MCP_TOOL_NAME = "search_informica_tei_jinaai"
MCP_TOOL_DESCRIPTION = (
    "Search the Informica 2.0 codebase using TEI + Jina v2 base code embeddings."
)
MCP_HOST = "0.0.0.0"
MCP_PORT = 8124


# ════════════════════════════════════════════════════════════════════
# 5. TEI CONFIGURATION — enable TEI backend
# ════════════════════════════════════════════════════════════════════
USE_TEI = True
TEI_DOCKER_PORT = 8090

# ── GPU mode (default) ──────────────────────────────────────────
# Uses NVIDIA CUDA Docker image.  Auto-detected via nvidia-smi.
# float16 is recommended (faster, lower VRAM, sufficient precision).
# Benchmark: ~117 chunks/sec, full reindex in ~19 min.
TEI_DTYPE = "float16"

# ── CPU mode (uncomment to switch) ──────────────────────────────
# Uses the CPU-only TEI Docker image (no GPU required).  Enables
# running the full pipeline on machines without an NVIDIA GPU.
#
# IMPORTANT: When CPU mode is enabled, ALL embedding runs on CPU:
#   - Dense embeddings:  TEI CPU Docker container (float32 required)
#   - Sparse BM25:       CPU ONNX provider (INDEX_EMBED_DEVICE)
#   - MCP query-time:    CPU for both dense + sparse (MCP_EMBED_DEVICE)
#
# Performance: ~2.4 chunks/sec on CPU vs ~117 on GPU (49x slower).
# Full reindex estimate: ~16 hours.  Best for incremental refreshes
# of small changesets or query-only MCP servers.
#
# TEI_DOCKER_IMAGE = "ghcr.io/huggingface/text-embeddings-inference:cpu-1.9"
# TEI_DTYPE = "float32"           # CPU has no fp16 hardware acceleration
# INDEX_EMBED_DEVICE = "cpu"      # Sparse BM25 encoder on CPU during indexing
# MCP_EMBED_DEVICE = "cpu"        # Sparse BM25 encoder on CPU during MCP queries
