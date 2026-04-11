#!/usr/bin/env bash
# scripts/start_rag_mcp_http.sh
# Start MCP server with HTTP transport for a given config.
# Usage: scripts/start_rag_mcp_http.sh <config_name>
#   scripts/start_rag_mcp_http.sh config_myproject
#   scripts/start_rag_mcp_http.sh self-index

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

CONFIG_NAME="${1:-}"
if [[ -z "$CONFIG_NAME" ]]; then
    echo "ERROR: Config name is required."
    echo "Usage: scripts/start_rag_mcp_http.sh <config_name>"
    echo "  scripts/start_rag_mcp_http.sh config_myproject"
    echo "  scripts/start_rag_mcp_http.sh self-index"
    exit 1
fi

# Extract MCP_PORT from config for the info message
export PYTHONPATH="$PWD:$PWD/src"
MCP_PORT=$(.venv/bin/python -W ignore -c \
    "from config_loader import get_config; c=get_config(config_path='$CONFIG_NAME'); print(c.MCP_PORT)")

echo "Starting MCP server (HTTP transport) for $CONFIG_NAME..."
echo
echo "Server will be available at: http://localhost:${MCP_PORT}/mcp"
echo

exec .venv/bin/python src/rag_mcp.py --config "$CONFIG_NAME" --transport streamable-http
