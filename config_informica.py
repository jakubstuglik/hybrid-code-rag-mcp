# Index-specific config for the Informica index.
# ================================================================
# Contains SOURCE_DIRS, Qdrant connection, MCP server identity,
# and storage paths for the Informica 2.0 Delphi/SQL codebase.
#
# Usage:
#   python index_rag.py --config config_informica --yes
#   python rag_mcp.py --config config_informica --transport stdio
#
# Common/system settings (embedding model, devices, batch sizes,
# VRAM cap, etc.) live in the base config.py and are inherited
# automatically via config_loader.
# ================================================================


# ════════════════════════════════════════════════════════════════════
# 1. SOURCE DIRECTORIES
# ════════════════════════════════════════════════════════════════════
# Each entry maps a directory path to the file extensions that should
# be indexed from it.  Only extensions that have a matching reader in
# shared/readers/READER_REGISTRY will actually be processed.
#
# Keys:
#   path          - Directory path (relative to project root or absolute).
#                   The canonical prefix for manifest keys / Qdrant payloads
#                   is derived from the LAST SEGMENT of this path (e.g.
#                   "../informica_2_0/delphi_src" -> "delphi_src").
#   map_to_path   - (Optional) Override the canonical prefix explicitly.
#                   Use when the last segment of path doesn't match the
#                   desired key prefix (e.g. path ends in "6RedGate" but
#                   keys should be "sql_srcipt/6RedGate/...").
#   extensions    - List of file extensions to include.
#   exclude       - (Optional) Folder/path patterns to exclude at any depth.
#                   Single names match any path component (e.g. "__pycache__").
#                   Multi-segment patterns like "TURDUS/ENG" match consecutive
#                   path components.
SOURCE_DIRS = [
    {
        "path": "../informica_2_0/delphi_src",
        "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj"],
        "exclude": [
            "TURDUS/ENG",
            "TURDUS/SRM",
            "TURDUS/UKR",
        ],
    },
    {
        "path": "../informica_2_0/sql_srcipt/6RedGate",
        "map_to_path": "sql_srcipt/6RedGate",
        "extensions": [".sql"],
    },
]


# ════════════════════════════════════════════════════════════════════
# 2. STORAGE PATH
# ════════════════════════════════════════════════════════════════════
# Subfolder under BASE_PATH (auto-set to {config_dir}/qdrant by
# config_loader) where this index's vectors are stored.
MODEL_PATH = "index_jinaai_20260310_informica_2_0"


# ════════════════════════════════════════════════════════════════════
# 3. VECTOR DATABASE (QDRANT)
# ════════════════════════════════════════════════════════════════════
COLLECTION_NAME = "informica_rag"

QDRANT_USE_DOCKER = True
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333


# ════════════════════════════════════════════════════════════════════
# 4. MCP SERVER
# ════════════════════════════════════════════════════════════════════
MCP_SERVER_NAME = "informica-rag"
MCP_TOOL_NAME = "search_informica"
MCP_TOOL_DESCRIPTION = (
    "Search your Delphi codebase, SQL schemas, FastReport templates, "
    "and docs for relevant context."
)
MCP_HOST = "0.0.0.0"
MCP_PORT = 8123
