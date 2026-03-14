@echo off
setlocal
pushd "%~dp0"

REM Start MCP server with stdio transport for a given config.
REM Usage: start_rag_mcp_stdio.bat <config_name>
REM   start_rag_mcp_stdio.bat config_informica
REM   start_rag_mcp_stdio.bat self-index

set "CONFIG_NAME=%~1"
if "%CONFIG_NAME%"=="" (
    echo ERROR: Config name is required.
    echo Usage: start_rag_mcp_stdio.bat ^<config_name^>
    echo   start_rag_mcp_stdio.bat config_informica
    echo   start_rag_mcp_stdio.bat self-index
    popd
    endlocal
    exit /b 1
)

"%~dp0.venv\Scripts\python.exe" "%~dp0rag_mcp.py" --config %CONFIG_NAME% --transport stdio

popd
endlocal
