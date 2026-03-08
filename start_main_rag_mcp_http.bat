@echo off
REM Start MCP server for informica_2_0 with HTTP transport
REM Usage: run_mcp.bat

echo Starting MCP server (HTTP transport) for informica_2_0...
echo.
echo Server will be available at: http://localhost:8123/mcp
echo Tool name: search_informica
echo.

.venv\Scripts\python rag_mcp.py --transport streamable-http

pause
