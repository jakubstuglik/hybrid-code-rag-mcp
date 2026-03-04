@echo off
REM Run indexer with GPU monitoring in parallel

echo Starting GPU monitor...
start "GPU Monitor" cmd /c "nvidia-smi -l 1 --query-gpu=timestamp,power.draw,temperature.gpu,utilization.gpu,memory.used --format=csv,noheader > gpu_log.txt"

echo Starting indexer...
python index_delphi.py --clear --yes --verbose 2>&1 | tee index_timing.log

echo.
echo Indexing complete. GPU log saved to gpu_log.txt
pause
