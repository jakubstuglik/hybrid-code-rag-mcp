# CPU image for the quickstart indexer + MCP server.
# Dense embeddings run in the sibling TEI container, so this image
# installs the CPU ONNX runtime and a CPU build of PyTorch (a transitive
# dependency) and does not need CUDA.  git is included so REPO_URL can
# be cloned inside the container.
FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv

WORKDIR /app

COPY requirements/requirements.txt /tmp/requirements.txt
# onnxruntime-gpu is for host CUDA setups; the CPU wheel is enough here.
# Install CPU PyTorch first and pin it so the requirements resolve does
# not pull a CUDA wheel and the NVIDIA libraries that come with it.
RUN sed 's/^onnxruntime-gpu==/onnxruntime==/' /tmp/requirements.txt \
        > /tmp/requirements-cpu.txt \
    && uv pip install --system --no-cache --index-url https://download.pytorch.org/whl/cpu torch \
    && python -c "import torch, pathlib; pathlib.Path('/tmp/torch.constraint').write_text(f'torch=={torch.__version__}\n')" \
    && uv pip install --system --no-cache -r /tmp/requirements-cpu.txt -c /tmp/torch.constraint

# git is required only when the user passes REPO_URL (the entrypoint
# clones inside the container).  Disable apt SRV lookups so the install
# works behind proxies that reject SRV records.
RUN printf 'Acquire::EnableSrvRecords "false";\n' > /etc/apt/apt.conf.d/99no-srv \
    && apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY config.py /app/config.py
COPY src /app/src
COPY examples/quickstart /app/examples/quickstart
COPY scripts /app/scripts

ENV PYTHONPATH=/app:/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Strip CR so a Windows checkout with core.autocrlf still runs in Linux.
RUN find /app/examples/quickstart -type f \( -name '*.sh' -o -name '*.py' \) \
        -exec sed -i 's/\r$//' {} + \
    && chmod +x /app/examples/quickstart/entrypoint.sh \
             /app/examples/quickstart/query.py \
             /app/examples/quickstart/wait_for.py \
             /app/examples/quickstart/resolve_repo.py

WORKDIR /app
ENTRYPOINT ["/app/examples/quickstart/entrypoint.sh"]
