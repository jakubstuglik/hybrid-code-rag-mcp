#!/usr/bin/env bash
# scripts/start_self_rag.sh
# Starts the MCP server for self-indexing over stdio transport.
# Docker auto-start is handled by rag_mcp.py (via shared/docker_utils.py).
# Used by opencode.json as a local MCP command.
# All diagnostic output goes to stderr (stdout is the JSON-RPC channel).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/start_rag_mcp_stdio.sh" self-index
