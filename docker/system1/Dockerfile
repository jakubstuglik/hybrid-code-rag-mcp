# Decision server. The model id, GPU, and fast/eager mode come from
# `docker run` arguments built from config, not from this file.
FROM python:3.12-slim-bookworm

RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cu124 \
    && pip install --no-cache-dir "basal @ https://github.com/rkinas/basal/archive/refs/tags/v1.0.1.tar.gz"

ENTRYPOINT ["basal-serve"]
