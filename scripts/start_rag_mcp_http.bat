@echo off
setlocal
pushd "%~dp0.."

REM Start MCP server with HTTP transport for a given config.
REM Usage: scripts\start_rag_mcp_http.bat <config_name>
REM   scripts\start_rag_mcp_http.bat config_myproject
REM   scripts\start_rag_mcp_http.bat self-index

set "CONFIG_NAME=%~1"
if "%CONFIG_NAME%"=="" (
    echo ERROR: Config name is required.
    echo Usage: scripts\start_rag_mcp_http.bat ^<config_name^>
    echo   scripts\start_rag_mcp_http.bat config_myproject
    echo   scripts\start_rag_mcp_http.bat self-index
    popd
    endlocal
    exit /b 1
)

REM Extract MCP_PORT from config for the info message
set "PYTHONPATH=%CD%;%CD%\src"
for /f "tokens=1,* delims==" %%A in ('.venv\Scripts\python.exe -W ignore -c "from config_loader import get_config; c=get_config(config_path=''%CONFIG_NAME%''); print(f''MCP_PORT={c.MCP_PORT}'')"') do set "%%A=%%B"

echo Starting MCP server (HTTP transport) for %CONFIG_NAME%...
echo.
echo Server will be available at: http://localhost:%MCP_PORT%/mcp
echo.

.venv\Scripts\python.exe src\rag_mcp.py --config %CONFIG_NAME% --transport streamable-http

popd
endlocal
pause
