# Installation

Full setup reference. For the short version see the [Quick Start](../README.md#quick-start).

## 1. Install uv (Python package manager)

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Clone and create virtual environment

```bash
git clone https://github.com/jakubstuglik/hybrid-code-rag-mcp.git
cd hybrid-code-rag-mcp
uv venv --python 3.12

# Activate (Windows)
.venv\Scripts\activate

# Or (Linux/Mac)
source .venv/bin/activate
```

## 3. Install dependencies

```bash
uv pip install -r requirements/requirements.txt
```

**Development dependencies** (testing, linting, formatting):
```bash
uv pip install -r requirements/requirements_dev.txt
```

## 4. GPU acceleration (optional)

**CUDA (NVIDIA GPU):**
```bash
uv pip uninstall torch
uv pip install -r requirements/requirements_cuda.txt
```

The file defaults to **cu126** (CUDA 12.6). Run `nvidia-smi` and check "CUDA Version" in the top-right corner -- that is the maximum toolkit your driver supports. You can always use an older toolkit (e.g. cu121 on a driver reporting 12.6), but not a newer one. Edit `requirements/requirements_cuda.txt` to change the version if needed.

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

**OpenVINO (Intel GPU):**
```bash
uv pip install -r requirements/requirements_openvino.txt
python -c "import openvino as ov; print(ov.Core().available_devices)"
```

Then enable in your config: `USE_OPENVINO_EMBEDDING = True`, `OPENVINO_EMBED_DEVICE = "GPU"`.

**TEI (HuggingFace Text Embeddings Inference):**

TEI is a high-performance Docker-based embedding server using Candle (Rust). It replaces in-process PyTorch model loading with an HTTP endpoint. In the project's benchmark with `jina-embeddings-v2-base-code` it embedded 4.5x faster than PyTorch at 3.3x lower peak VRAM (see [the benchmark report](features/tei-multimodel-benchmark/benchmark-tei-multimodel-2026-03-20.md)).

```bash
# TEI requires Docker Desktop only -- no Python packages needed.
# The TEI container is auto-managed (created/started) like Qdrant.
```

Enable in your config:
```python
USE_TEI = True
TEI_DOCKER_PORT = 8090
TEI_DTYPE = "float16"    # "float32" for CPU-only mode
```

Hardware is auto-detected: NVIDIA GPU uses the CUDA Docker image, no GPU falls back to CPU image. For CPU-only TEI settings (dtype, batch tokens, pool size) see [TEI on CPU](vram-tuning.md#tei-on-cpu).

**Note:** TEI and PyTorch produce incompatible vectors. Switching backends requires `--clear` to rebuild the index. The system tracks embedding provenance automatically.

**OpenAI-compatible server (e.g. llama.cpp `llama-server --embeddings`):**

Any server that implements `POST /v1/embeddings` can serve the dense vectors. This backend is not auto-started; run the server yourself and point the config at it. Set `USE_TEI = False`, otherwise the TEI container is still started.

```python
EMBED_BACKEND = "openai"
USE_TEI = False
OPENAI_EMBED_URL = "http://localhost:8092"     # default
OPENAI_EMBED_MODEL = None                      # "model" field sent to the server; defaults to MODEL_NAME
OPENAI_EMBED_MAX_TOKENS = 4000                 # longer inputs are truncated with the server's /tokenize + /detokenize
# Optional: spread requests over several servers
# OPENAI_EMBED_ENDPOINTS = [{"url": "http://localhost:8092", "max_tokens": 4000, "slots": 2}, ...]
```

See `src/shared/openai_embedding.py` for the retry and truncation behaviour.

## Vector Store (Qdrant)

The system uses Qdrant as its vector database. Two deployment modes are supported:

### Local mode (`QDRANT_MODE = "local"`)

Docker containers are **auto-managed**: `src/index_rag.py` and `src/rag_mcp.py` automatically check for, create, and start the container before connecting. No manual `docker start` needed.

Container naming is auto-derived as `qdrant-{COLLECTION_NAME}` (e.g. `qdrant-myproject_rag`), overridable via `QDRANT_DOCKER_CONTAINER` in your config.

**Requirements:** Docker Desktop must be installed and `docker` must be in PATH.

**Manual start** (if you prefer):
```bash
# Windows
scripts\start_qdrant.bat my_project

# Linux/Mac
scripts/start_qdrant.sh my_project
```

### Remote mode (`QDRANT_MODE = "remote"`)

For Qdrant Cloud or self-hosted remote servers. Supports API key authentication, HTTPS, and gRPC:

```python
# project-configs/my_project/config.py
QDRANT_MODE = "remote"
QDRANT_HOST = "my-cluster.qdrant.io"
QDRANT_PORT = 6333
QDRANT_API_KEY = "your-api-key"     # Optional: for authenticated clusters
QDRANT_HTTPS = True                 # Optional: use HTTPS
QDRANT_PREFER_GRPC = True           # Optional: use gRPC (faster indexing)
QDRANT_GRPC_PORT = 6334             # Optional: gRPC port (default 6334)
```

No Docker management is performed in remote mode.
