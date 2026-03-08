@echo off
REM start_main_rag.bat
REM Starts the MCP server for informica-rag with stdio transport.
REM Used by informica_2_0/opencode.jsonc as a local MCP command.

"%~dp0.venv\Scripts\python.exe" "%~dp0rag_mcp.py" --transport stdio
