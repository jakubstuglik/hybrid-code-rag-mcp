@echo off
setlocal enabledelayedexpansion
REM scripts\start_self_rag.bat
REM Starts the MCP server for self-indexing over stdio transport.
REM Docker auto-start is handled by rag_mcp.py (via shared/docker_utils.py).
REM Used by opencode.json as a local MCP command.
REM All diagnostic output goes to stderr (stdout is the JSON-RPC channel).

REM -- Start MCP server (stdio) --
call "%~dp0start_rag_mcp_stdio.bat" self-index
