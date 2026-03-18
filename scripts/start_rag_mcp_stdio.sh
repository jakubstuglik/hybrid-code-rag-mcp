#!/usr/bin/env bash
# scripts/start_rag_mcp_stdio.sh
# Start MCP server with stdio transport for a given config.
# Usage: scripts/start_rag_mcp_stdio.sh <config_name>
#   scripts/start_rag_mcp_stdio.sh config_informica
#   scripts/start_rag_mcp_stdio.sh self-index

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

CONFIG_NAME="${1:-}"
if [[ -z "$CONFIG_NAME" ]]; then
    echo "ERROR: Config name is required."
    echo "Usage: scripts/start_rag_mcp_stdio.sh <config_name>"
    echo "  scripts/start_rag_mcp_stdio.sh config_informica"
    echo "  scripts/start_rag_mcp_stdio.sh self-index"
    exit 1
fi

export PYTHONPATH="$PWD:$PWD/src"
exec .venv/bin/python src/rag_mcp.py --config "$CONFIG_NAME" --transport stdio
