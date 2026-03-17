# Index-specific config for the Informica codebase using Alibaba-NLP/gte-modernbert-base.
# ================================================================
# This is a CHALLENGER config for model comparison against the baseline
# jinaai/jina-embeddings-v2-base-code (config_informica).
#
# DO NOT use as a production config until validate_rag.py comparison is done.
#
# PREREQUISITE: transformers>=4.48.0 must be installed (ModernBERT was added
# in 4.48.0). Current requirements.txt is pinned to 4.48.3 — install first:
#   uv pip install -r requirements/requirements.txt
#
# Usage:
#   python src/index_rag.py --config config_informica_gte --clear --yes
#   python src/validate_rag.py --config config_informica_gte
#
# Model: Alibaba-NLP/gte-modernbert-base
#   - Apache 2.0, 149M params, 768-dim, 8192 native context
#   - CoIR NDCG@10 = 79.31 (far ahead of all <300M models)
#   - ModernBERT architecture: Flash Attention 2 + RoPE, O(N) VRAM
#   - General-purpose model (not code-specialized), but ModernBERT was
#     pretrained on code and GTE fine-tuning included code retrieval tasks
#   - No trust_remote_code required
#   - No task prefix required for retrieval (confirmed from model card)
# ================================================================


# ════════════════════════════════════════════════════════════════════
# 1. SOURCE DIRECTORIES
# ════════════════════════════════════════════════════════════════════
# Identical to config_informica — same source corpus, different model.
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
# 2. EMBEDDING MODEL
# ════════════════════════════════════════════════════════════════════
MODEL_NAME = "Alibaba-NLP/gte-modernbert-base"

# Flash Attention 2 + RoPE — no ALiBi quadratic VRAM penalty, full native context.
EMBED_MAX_SEQ_LENGTH = 8192
DENSE_EMBED_BATCH_SIZE = 32
EMBED_BATCH_MAX_TOKENS = 32000
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}

# Dynamic VRAM cap is not needed (RoPE/Flash Attention is O(N)).
EMBED_DYNAMIC_VRAM_CAP = False


# ════════════════════════════════════════════════════════════════════
# 3. STORAGE PATH
# ════════════════════════════════════════════════════════════════════
MODEL_PATH = "index_gte_informica_2_0"


# ════════════════════════════════════════════════════════════════════
# 4. VECTOR DATABASE (QDRANT)
# ════════════════════════════════════════════════════════════════════
# Isolated collection — does NOT share with config_informica's "informica_rag"
# or config_informica_coderank's "informica_coderank".
COLLECTION_NAME = "informica_gte"

QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6335  # Different port from baseline (6333) and coderank (6334)


# ════════════════════════════════════════════════════════════════════
# 5. MCP SERVER
# ════════════════════════════════════════════════════════════════════
MCP_SERVER_NAME = "informica-gte"
MCP_TOOL_NAME = "search_informica_gte"
MCP_TOOL_DESCRIPTION = (
    "Search the Informica 2.0 codebase using gte-modernbert-base (challenger model). "
    "Delphi Pascal source, SQL stored procedures, DFM forms, FastReport templates, "
    "and project files. Returns matching code chunks with file paths and line numbers. "
    "Supports branch-aware search: pass a git branch name in the 'branch' parameter to "
    "include feature branch changes alongside the main branch (develop)."
)
MCP_HOST = "0.0.0.0"
MCP_PORT = 8125
