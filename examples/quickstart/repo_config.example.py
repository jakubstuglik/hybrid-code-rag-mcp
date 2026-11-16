# SPDX-License-Identifier: Apache-2.0
"""Example repo-only config for the Docker Compose quickstart.

Copy this file, edit it, and point the stack at the copy:

    ./start.sh --repo /path/to/your/repo --repo-config ./repo_config.py
    .\\start.ps1 -Repo C:\\path\\to\\your\\repo -RepoConfig .\\repo_config.py

Or set REPO_CONFIG in a `.env` file next to docker-compose.yml (a start
parameter beats `.env`).

Paths are relative to the repository root — the tree selected with
`--repo` / `-Repo`, `REPO_PATH` or `REPO_URL`.  Only SOURCE_DIRS and the
MCP identity keys below are accepted.  Infrastructure (Qdrant, TEI,
batch sizes, dtype, ports, BASE_PATH, collection name) stays on the
CPU or GPU Compose profile; if this file sets one of those keys,
startup exits with an error.

Changing this file, or the source tree, rebuilds the index with `--clear`.
"""

# Limit the index to src/ and docs/.  Each entry uses the same shape as
# SOURCE_DIRS in a normal project config (see docs/configuration.md):
#   path        — subdirectory of the repo root (use "." for the root)
#   extensions  — file suffixes to include
#   exclude     — optional fnmatch patterns.  A single segment such as
#                 "tests" or "__pycache__" matches that name at any depth.
SOURCE_DIRS = [
    {
        "path": "src",
        "extensions": [".py"],
        "exclude": ["tests", "test_*.py"],
    },
    {
        "path": "docs",
        "extensions": [".md"],
    },
]

MCP_SERVER_NAME = "myshop-rag"
MCP_TOOL_NAME = "search_myshop"
MCP_TOOL_DESCRIPTION = (
    "Hybrid semantic + keyword search over the myshop src/ and docs/ trees.\n\n"
    "USE WHEN: looking up symbols or behaviour in this codebase.\n\n"
    "HOW TO QUERY: prefer identifiers or short English concepts.\n\n"
    "RETURNS per hit: FILE, DISK_PATH, TYPE, LINES, chunk text."
)
