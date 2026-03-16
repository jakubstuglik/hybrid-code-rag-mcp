# Index-specific config for the Informica index.
# ================================================================
# Contains SOURCE_DIRS, Qdrant connection, MCP server identity,
# and storage paths for the Informica 2.0 Delphi/SQL codebase.
#
# Usage:
#   python src/index_rag.py --config config_informica --yes
#   python src/rag_mcp.py --config config_informica --transport stdio
#
# Common/system settings (embedding model, devices, batch sizes,
# VRAM cap, etc.) live in the base config.py and are inherited
# automatically via config_loader.
# ================================================================


# ════════════════════════════════════════════════════════════════════
# 1. SOURCE DIRECTORIES
# ════════════════════════════════════════════════════════════════════
# SOURCE_DIRS supports two entry types, distinguished by the "type" field:
#
# type: "git_repo" — a git repository containing one or more source paths.
#   path          - Path to the git repository root (relative or absolute).
#   main_branch   - Main/default branch name (default: "master").
#   branches      - Feature branches to index as overlays (default: []).
#   diff_full_reindex_threshold - Override global DIFF_FULL_REINDEX_THRESHOLD.
#   sources       - List of source directories within the repo, each with:
#     path        - Path relative to the git repo root.
#     extensions  - File extensions to include.
#     exclude     - (Optional) Folder/path patterns to exclude.
#     map_to_path - (Optional) Override canonical prefix for manifest keys.
#
# type: "source_set" — a standalone directory (not git-backed).
#   Same keys as the legacy flat format: path, extensions, exclude, map_to_path.
#   Chunks from source_sets are branch-agnostic (appear in ALL queries).
#
# Legacy format (no "type" field) is still supported and treated as "source_set".
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
# Subfolder under BASE_PATH (auto-set to {config_dir}/qdrant by
# config_loader) where this index's vectors are stored.
MODEL_PATH = "index_jinaai_informica_2_0"


# ════════════════════════════════════════════════════════════════════
# 3. VECTOR DATABASE (QDRANT)
# ════════════════════════════════════════════════════════════════════
COLLECTION_NAME = "informica_rag"

QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333


# ════════════════════════════════════════════════════════════════════
# 4. MCP SERVER
# ════════════════════════════════════════════════════════════════════
MCP_SERVER_NAME = "informica-rag"
MCP_TOOL_NAME = "search_informica"
MCP_TOOL_DESCRIPTION = (
    "Search the Informica 2.0 codebase — Delphi Pascal source, SQL stored procedures, "
    "DFM forms, FastReport templates, and project files. Returns matching code chunks with "
    "file paths and line numbers. "
    "Supports branch-aware search: pass a git branch name in the 'branch' parameter to "
    "include feature branch changes alongside the main branch (develop). Use "
    "`git branch --show-current` to get the current branch. Omit 'branch' when working "
    "on the main branch."
)
MCP_HOST = "0.0.0.0"
MCP_PORT = 8123
