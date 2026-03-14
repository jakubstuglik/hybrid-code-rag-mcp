@echo off
setlocal
pushd "%~dp0"

REM Start Qdrant Docker container for a given config.
REM Reads MODEL_PATH, BASE_PATH, QDRANT_PORT from the config via config_loader.
REM Usage: start_qdrant.bat <config_name>
REM   start_qdrant.bat config_informica
REM   start_qdrant.bat self-index
REM   start_qdrant.bat test-sources

set "CONFIG_NAME=%~1"
if "%CONFIG_NAME%"=="" (
    echo ERROR: Config name is required.
    echo Usage: start_qdrant.bat ^<config_name^>
    echo   start_qdrant.bat config_informica
    echo   start_qdrant.bat self-index
    echo   start_qdrant.bat test-sources
    popd
    endlocal
    exit /b 1
)

REM Extract MODEL_PATH, BASE_PATH, QDRANT_PORT from config via config_loader
for /f "tokens=1,* delims==" %%A in ('.venv\Scripts\python.exe -W ignore -c "from config_loader import get_config; c=get_config(config_path='%CONFIG_NAME%'); print(f'MODEL_PATH={c.MODEL_PATH}\nBASE_PATH={str(c.BASE_PATH).replace(chr(92), chr(47))}\nQDRANT_PORT={c.QDRANT_PORT}')"') do set "%%A=%%B"

echo Config: %CONFIG_NAME%
echo Using BASE_PATH: %BASE_PATH%
echo Using MODEL_PATH: %MODEL_PATH%
echo Using QDRANT_PORT: %QDRANT_PORT%

echo Qdrant storage: %BASE_PATH%/%MODEL_PATH%

docker compose down
docker compose up -d

echo Qdrant ready on localhost:%QDRANT_PORT%. Check: docker logs code_rag_qdrant

popd
endlocal
