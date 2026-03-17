# Index-specific config for the Informica codebase using nomic-ai/CodeRankEmbed.
# ================================================================
# This is a CHALLENGER config for model comparison against the baseline
# jinaai/jina-embeddings-v2-base-code (config_informica).
#
# DO NOT use as a production config until validate_rag.py comparison is done.
#
# Usage:
#   python src/index_rag.py --config config_informica_coderank --clear --yes
#   python src/validate_rag.py --config config_informica_coderank
#
# Model: nomic-ai/CodeRankEmbed
#   - Apache 2.0, 137M params, 768-dim, 8192 native context
#   - CoIR NDCG@10 = 60.1 (vs baseline ~56)
#   - RoPE positional encoding: O(N) VRAM, no ALiBi quadratic penalty
#   - No trust_remote_code required
#   - May require query-time task prefix (check model card after first download)
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
MODEL_NAME = "nomic-ai/CodeRankEmbed"

# nomic-bert uses standard O(N²) attention on Windows (flash-attn is Linux-only).
# Calibration results on test_sources (8,101 vectors):
#   seq_len=1024: combined_peak=4,595 MiB, truncation=4.8%
#   seq_len=2048: ~1.5% truncation (estimated, 1.0% on full build) — SAFE
#   seq_len=3072: combined_peak=14,953 MiB, truncation=0.4% — SAFE, within 20,700 MiB ceiling
#   seq_len=4096: combined_peak=19,107 MiB on test_sources, OOM on full corpus
# Using seq_len=3072 for best quality/VRAM tradeoff.
EMBED_MAX_SEQ_LENGTH = 3072
DENSE_EMBED_BATCH_SIZE = 32
EMBED_BATCH_MAX_TOKENS = 16000
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}

# Dynamic VRAM cap disabled — static cap used instead.
EMBED_DYNAMIC_VRAM_CAP = False


# ════════════════════════════════════════════════════════════════════
# 3. STORAGE PATH
# ════════════════════════════════════════════════════════════════════
MODEL_PATH = "index_coderank_informica_2_0"


# ════════════════════════════════════════════════════════════════════
# 4. VECTOR DATABASE (QDRANT)
# ════════════════════════════════════════════════════════════════════
# Isolated collection — does NOT share with config_informica's "informica_rag".
COLLECTION_NAME = "informica_coderank"

QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6334  # Different port from baseline (6333) to avoid container conflicts


# ════════════════════════════════════════════════════════════════════
# 5. MCP SERVER
# ════════════════════════════════════════════════════════════════════
MCP_SERVER_NAME = "informica-coderank"
MCP_TOOL_NAME = "search_informica_coderank"
MCP_TOOL_DESCRIPTION = (
    "Search the Informica 2.0 codebase using CodeRankEmbed (challenger model). "
    "Delphi Pascal source, SQL stored procedures, DFM forms, FastReport templates, "
    "and project files. Returns matching code chunks with file paths and line numbers. "
    "Supports branch-aware search: pass a git branch name in the 'branch' parameter to "
    "include feature branch changes alongside the main branch (develop)."
)
MCP_HOST = "0.0.0.0"
MCP_PORT = 8124
