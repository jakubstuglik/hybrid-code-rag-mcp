@echo off
setlocal enabledelayedexpansion
REM start_self_rag.bat
REM Ensures the self-index Qdrant Docker container is running, then starts
REM the MCP server for self-indexing over stdio transport.
REM Used by opencode.json as a local MCP command.
REM All diagnostic output goes to stderr (stdout is the JSON-RPC channel).

REM -- Ensure Qdrant container is running --
docker inspect informica_rag_self >nul 2>&1
if errorlevel 1 (
    echo [self-rag] Container does not exist, creating... 1>&2
    docker run -d --name informica_rag_self -p 6973:6333 -v "%~dp0self-index\qdrant\index_rag_self:/qdrant/storage" qdrant/qdrant:latest 1>&2 2>&1
) else (
    echo [self-rag] Container exists, starting... 1>&2
    docker start informica_rag_self 1>&2 2>&1
)

REM -- Wait for Qdrant to be healthy (up to ~30 seconds) --
echo [self-rag] Waiting for Qdrant on port 6973... 1>&2
set RETRIES=0
:healthcheck
if !RETRIES! geq 30 (
    echo [self-rag] ERROR: Qdrant not ready after 30 attempts 1>&2
    exit /b 1
)
curl -sf http://localhost:6973/healthz >nul 2>&1
if errorlevel 1 (
    set /a RETRIES+=1
    ping -n 2 127.0.0.1 >nul 2>&1
    goto healthcheck
)
echo [self-rag] Qdrant is ready after !RETRIES! retries 1>&2

REM -- Start MCP server (stdio) --
"%~dp0.venv\Scripts\python.exe" "%~dp0rag_mcp.py" --config self-index --transport stdio
