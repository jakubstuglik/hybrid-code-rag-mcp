@echo off
setlocal
pushd "%~dp0"

REM Dynamic Qdrant Docker start based on config_loader configuration
REM Extract MODEL_PATH, BASE_PATH, QDRANT_PORT from config.py via config_loader cleanly using for /f
for /f "tokens=1,* delims==" %%A in ('.venv\Scripts\python.exe -W ignore -c "from config_loader import get_config; c=get_config('config'); print(f'MODEL_PATH={c.MODEL_PATH}\nBASE_PATH={str(c.BASE_PATH).replace(chr(92), chr(47))}\nQDRANT_PORT={c.QDRANT_PORT}')"') do set "%%A=%%B"

echo Using BASE_PATH: %BASE_PATH%
echo Using MODEL_PATH: %MODEL_PATH%
echo Using QDRANT_PORT: %QDRANT_PORT%

echo Qdrant storage: %BASE_PATH%/%MODEL_PATH%

docker compose down
docker compose up -d

echo Qdrant ready on localhost:%QDRANT_PORT%. Check: docker logs code_rag_qdrant

popd
endlocal