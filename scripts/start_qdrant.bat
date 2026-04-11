@echo off
setlocal
pushd "%~dp0.."

REM Start Qdrant Docker container for a given config.
REM Uses shared/docker_utils.py to ensure the container is running.
REM Usage: scripts\start_qdrant.bat <config_name>
REM   scripts\start_qdrant.bat config_myproject
REM   scripts\start_qdrant.bat self-index
REM   scripts\start_qdrant.bat test-sources

set "CONFIG_NAME=%~1"
if "%CONFIG_NAME%"=="" (
    echo ERROR: Config name is required.
    echo Usage: scripts\start_qdrant.bat ^<config_name^>
    echo   scripts\start_qdrant.bat config_myproject
    echo   scripts\start_qdrant.bat self-index
    echo   scripts\start_qdrant.bat test-sources
    popd
    endlocal
    exit /b 1
)

.venv\Scripts\python.exe -W ignore -c "import sys; sys.path.insert(0,'.'); sys.path.insert(0,'src'); from config_loader import get_config; from shared.docker_utils import ensure_qdrant_running, get_container_name; c=get_config(config_path='%CONFIG_NAME%'); ok=ensure_qdrant_running(c); exit(0 if ok else 1)"

if errorlevel 1 (
    echo ERROR: Failed to start Qdrant for config '%CONFIG_NAME%'.
    popd
    endlocal
    exit /b 1
)

popd
endlocal
