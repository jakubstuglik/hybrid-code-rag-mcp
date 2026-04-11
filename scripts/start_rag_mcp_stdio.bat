@echo off
setlocal
pushd "%~dp0.."

REM Start MCP server with stdio transport for a given config.
REM Usage: scripts\start_rag_mcp_stdio.bat <config_name>
REM   scripts\start_rag_mcp_stdio.bat config_myproject
REM   scripts\start_rag_mcp_stdio.bat self-index

set "CONFIG_NAME=%~1"
if "%CONFIG_NAME%"=="" (
    echo ERROR: Config name is required.
    echo Usage: scripts\start_rag_mcp_stdio.bat ^<config_name^>
    echo   scripts\start_rag_mcp_stdio.bat config_myproject
    echo   scripts\start_rag_mcp_stdio.bat self-index
    popd
    endlocal
    exit /b 1
)

set "PYTHONPATH=%CD%;%CD%\src"
.venv\Scripts\python.exe src\rag_mcp.py --config %CONFIG_NAME% --transport stdio

popd
endlocal
