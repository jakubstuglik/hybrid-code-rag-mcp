@echo off
REM Dynamic Qdrant Docker start based on config.py MODEL_PATH/QDRANT_PORT

REM Extract MODEL_PATH from config.py
for /f "delims=" %%i in ('python -c "from config import MODEL_PATH; print(MODEL_PATH)"') do set MODEL_PATH=%%i

REM Extract QDRANT_PORT from config.py
for /f "delims=" %%i in ('python -c "from config import QDRANT_PORT; print(QDRANT_PORT)"') do set QDRANT_PORT=%%i

echo Using MODEL_PATH: %MODEL_PATH%
echo Using QDRANT_PORT: %QDRANT_PORT%
echo Qdrant storage: ./qdrant/%MODEL_PATH%_qdrant

docker compose down
docker compose up -d

echo Qdrant ready on localhost:%QDRANT_PORT%. Check: docker logs informica_qdrant
