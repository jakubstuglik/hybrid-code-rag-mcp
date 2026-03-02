@echo off
REM Dynamic Qdrant Docker start based on config.py MODEL_PATH

REM Extract MODEL_PATH from config.py
for /f "delims=" %%i in ('python -c "from config import MODEL_PATH; print(MODEL_PATH)"') do set MODEL_PATH=%%i

echo Using MODEL_PATH: %MODEL_PATH%
echo Qdrant storage: ./qdrant/%MODEL_PATH%_qdrant

docker compose down
docker compose up -d

echo Qdrant ready on localhost:6333. Check: docker logs informica_qdrant