### Disclaimer
<image-card alt="License" src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" ></image-card>
**This project is in active development.** It is provided as-is with no warranty.
Licensed under the Apache License, Version 2.0. See LICENSE and NOTICE.
The whole codebase, including versions previously released under AGPLv3, is available under Apache-2.0.
I don't guarantee I will be able to incorporate any pull requests, but I will do my best to respond to issues.

# Code RAG Indexer & MCP Server

A versatile, high-performance RAG (Retrieval Augmented Generation) pipeline and Model Context Protocol (MCP) server designed for searching and analyzing large-scale codebases.

It features intelligent chunking using Tree-sitter AST parsing, hybrid search (Dense + Sparse/BM25) via Qdrant, and a multi-config architecture that supports running separate indices and MCP servers for different projects from a single installation.

## Features

- **Intelligent Chunking**: Tree-sitter AST parsing chunks code by classes, functions, and logical blocks -- not arbitrary line counts. Each reader produces context-prefixed chunks with class/module/file metadata.
- **Robust Fallbacks**: Automatic fallback to sophisticated text chunkers for dialects Tree-sitter struggles with (e.g. T-SQL heuristic chunker). SQL dialect is chosen per source path: `tsql` is the default, `postgresql` uses a PostgreSQL chunker.
- **Hybrid Search**: Dense (semantic) + Sparse (BM25 lexical) vectors catch both exact variable references (`@S1Q1`) and conceptual queries ("what is TdmMain?").
- **Multiple Embedding Backends**: PyTorch (CUDA/CPU), OpenVINO (Intel GPU), and TEI (HuggingFace Text Embeddings Inference via Docker). TEI is 4.5x faster and uses 3.3x less VRAM than PyTorch.
- **High-Performance Indexing Pipeline**: Cross-file chunk pooling, concurrent TEI embedding (64 parallel HTTP requests), parse-ahead thread (overlaps file parsing with GPU embedding), HNSW deferral during bulk ingest, and double-buffered Qdrant upserts. Together these achieve **53% faster indexing** and **68% mean GPU utilization** vs the original per-file baseline.
- **Incremental Refresh**: Uses content hashes and git diffs to detect changes, re-embedding only what has changed. Cron-safe guard scripts prevent concurrent runs.
- **Git Branch-Aware Indexing**: Index feature branches as lightweight overlays on the main branch. Query with a `branch` parameter to get results that include your branch's changes, with automatic dedup.
- **Multi-Index Architecture**: Each index has its own config file. Run separate indices and MCP servers for different projects, all sharing common system settings.
- **Post-Retrieval Reranking**: Query intent detection promotes overview chunks for "what is X?" queries while preserving precision for exact lookups.
- **Self-Indexing for AI Development**: The project can index its own source code, providing an MCP tool for AI agents to semantically search the codebase during development.

## Supported File Types & Parsers

| Extension | Parser |
|-----------|--------|
| `.pas` / `.dpr` | Tree-sitter Pascal AST (class summaries, method grouping, context prefixes) |
| `.java` | Tree-sitter Java AST (class/interface/enum/record declarations, method grouping, import grouping, annotation support) |
| `.groovy` | Tree-sitter Groovy AST (class summaries, method/constructor grouping, import grouping, enum support, annotation awareness) |
| `.js` / `.ts` / `.tsx` | Tree-sitter JavaScript/TypeScript AST (ES6 modules, IIFE, prototype-based OOP, TS interfaces/type aliases) |
| `.sql` | T-SQL by default (Tree-sitter SQL, then the T-SQL chunker). Set `sql_dialect` to `"postgresql"` on that source path for PostgreSQL |
| `.c` / `.h` / `.cpp` | Tree-sitter C or C++ (class overview, class summary, one chunk per function) |
| `.ui` | Qt Designer form parser (form header, widgets, visible strings, signal/slot connections) |
| `.dfm` | Custom Delphi Form parser (recursive descent, component grouping) |
| `.hbm.xml` | Hibernate mapping XML parser (entity overview with table/columns/associations, structured metadata) |
| `.jrxml` | JasperReports XML parser (report overview, parameter/field/variable extraction, expression chunks) |
| `.dproj` | Built-in XML parser (project overview, build configs, unit groups) |
| `.fr3` | FastReport XML parser (scripts, memos, bands) |
| `.py` | Tree-sitter Python AST (leaf/container pattern, class context) |
| `.jsp`, `.properties`, `.gradle`, `.yaml`, `.css`, `.scss`, `.md`, `.bat`, `.sh`, `.cfg`, `.ini`, `.conf`, `.json`, `.html`, `.htm` | Text reader (sentence-aware splitting, configurable via `READER_REGISTRY`) |
| Other | Extensible via `src/shared/readers/READER_REGISTRY` |

## Setup

### 1. Install uv (Python package manager)

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and create virtual environment

```bash
git clone https://github.com/jakubstuglik/hybrid-code-rag-mcp.git
cd hybrid-code-rag-mcp
uv venv --python 3.12

# Activate (Windows)
.venv\Scripts\activate

# Or (Linux/Mac)
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements/requirements.txt
```

**Development dependencies** (testing, linting, formatting):
```bash
uv pip install -r requirements/requirements_dev.txt
```

### 4. GPU acceleration (optional)

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

TEI is a high-performance Docker-based embedding server using Candle (Rust). It replaces in-process PyTorch model loading with an HTTP endpoint, achieving 4.5x faster embedding at 3.3x lower VRAM usage.

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

Hardware is auto-detected: NVIDIA GPU uses the CUDA Docker image, no GPU falls back to CPU image. See `project-configs/config_myproject/config.py` for a complete example including a commented-out CPU mode block.

**Note:** TEI and PyTorch produce incompatible vectors. Switching backends requires `--clear` to rebuild the index. The system tracks embedding provenance automatically.

## Configuration

### Architecture

The config system uses a two-layer approach:

| File | Purpose |
|------|---------|
| `config.py` | **Common system defaults** -- embedding model, devices, batch sizes, VRAM cap, indexing mode. Loaded first for every config. |
| `project-configs/<name>/config.py` | **Project index** -- SOURCE_DIRS, COLLECTION_NAME, Qdrant connection, MCP identity for a specific codebase. One subdirectory per project. |
| `self-index/config.py` | **Self-index** -- indexes this project's own source code for AI-assisted development. |

`src/config_loader.py` always loads `config.py` first, then overlays the specified config on top. All scripts require a `--config` parameter to specify which index to work with.

### Creating a new index config

Create a `config.py` file inside a new subdirectory under `project-configs/` (e.g. `project-configs/my_project/config.py`):

```python
# project-configs/my_project/config.py — simple (source_set / legacy format)
SOURCE_DIRS = [
    {
        "path": "../my-project/src",
        "extensions": [".py", ".js", ".ts"],
    },
]

MODEL_PATH = "index_myproject"
COLLECTION_NAME = "myproject_rag"
QDRANT_MODE = "local"           # "local" (Docker auto-managed) or "remote"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

MCP_SERVER_NAME = "myproject-rag"
MCP_TOOL_NAME = "search_myproject"
MCP_TOOL_DESCRIPTION = "Search the myproject codebase."
MCP_PORT = 8125
```

For **git-backed repositories** with branch-aware indexing:

```python
# project-configs/my_project/config.py — git_repo format (supports branch overlays)
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": "../my-project",            # Git repo root
        "main_branch": "main",              # Default: "master"
        "branches": [],                     # Feature branches to index
        "sources": [
            {"path": "src", "extensions": [".py", ".js", ".ts"]},
            {"path": "sql", "extensions": [".sql"], "sql_dialect": "postgresql"},
        ],
    },
]
```

Then use it: `python src/index_rag.py --config my_project --yes`

### SQL dialect

`.sql` stays one reader. The dialect is a field on the source entry. The indexer does not sniff the file. PostgreSQL and T-SQL can both fail the ANSI grammar, and that error path used to always call the T-SQL chunker.

| `sql_dialect` | Behavior |
|---------------|----------|
| omitted or `"tsql"` | Tree-sitter SQL, then the T-SQL chunker. This is what existing indexes already use. |
| `"postgresql"` | Statement chunker. Dollar quotes, strings, comments, and parentheses hide semicolons. Each `CREATE TABLE`, `FUNCTION`, `PROCEDURE`, `TRIGGER`, `RULE`, `VIEW`, and `COMMENT ON` is its own chunk, with `object_name` and `object_type`. |

The key is valid on a `git_repo` source, a `source_set`, and a legacy entry. Any other value fails when the config loads. Put it only on the path that holds that dialect. Other extensions on other paths are unchanged.

```python
{"path": "Resources/sql", "extensions": [".sql"], "sql_dialect": "postgresql"}
```

A missing `sql_dialect` in the manifest means `tsql`. A refresh of a current project does not re-chunk its SQL files. After you set `postgresql` on a path that was indexed as T-SQL, the next refresh re-embeds only those `.sql` files. You do not need `--clear`. The git fast path does not skip a file whose dialect changed, even when the hash and mtime match.

Overview queries promote `pgsql_create_function`, `pgsql_create_procedure`, `pgsql_create_table`, `pgsql_create_trigger`, `pgsql_create_rule`, and `pgsql_create_view`. Large statements use the same name with a `_split` suffix. `pgsql_statement`, `pgsql_alter`, and `pgsql_create_index` are detail chunks.

### Recommended Embedding Models

- **Dense** (`MODEL_NAME`): `jinaai/jina-embeddings-v2-base-code` -- optimized for code, 8192 token context
- **Sparse** (`SPARSE_MODEL_NAME`): `Qdrant/bm25` -- exact lexical matching, zero VRAM

### Config Reference

All parameters are defined in `config.py` (system defaults) and can be overridden in project configs.

#### Index Identity

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SOURCE_DIRS` | `[]` | Source entries to index (`git_repo`, `source_set`, or legacy). Each entry may set `sql_dialect` to `tsql` (default) or `postgresql`. |
| `COLLECTION_NAME` | `"default_rag"` | Qdrant collection name. Must be unique per index. |
| `MODEL_PATH` | `"default_index"` | Subdirectory under `BASE_PATH` for Qdrant storage and manifests. |

#### Qdrant Connection

| Parameter | Default | Description |
|-----------|---------|-------------|
| `QDRANT_MODE` | `"local"` | `"local"` = auto-managed Docker; `"remote"` = external Qdrant server. |
| `QDRANT_HOST` | `"localhost"` | Qdrant server hostname. |
| `QDRANT_PORT` | `6333` | Qdrant REST port. |
| `QDRANT_API_KEY` | `None` | API key for authenticated clusters (remote mode). |
| `QDRANT_HTTPS` | `False` | Use HTTPS for REST connection (remote mode). |
| `QDRANT_PREFER_GRPC` | `False` | Use gRPC instead of REST (remote mode, faster for bulk indexing). |
| `QDRANT_GRPC_PORT` | `6334` | gRPC port (remote mode). |
| `QDRANT_DELETE_TIMEOUT` | `60` | Seconds to wait for delete-by-filter calls. |
| `QDRANT_DOCKER_CONTAINER` | `None` | Docker container name override. Auto-derived as `qdrant-{COLLECTION_NAME}`. |
| `QDRANT_DOCKER_VOLUME` | `None` | Docker volume path override. Auto-derived from `BASE_PATH`/`MODEL_PATH`. |

#### MCP Server

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MCP_SERVER_NAME` | `"rag-server"` | Server name in MCP registration. |
| `MCP_TOOL_NAME` | `"search_rag"` | Tool function name exposed to MCP clients. |
| `MCP_TOOL_DESCRIPTION` | *(long string)* | Human-readable tool description. |
| `MCP_HOST` | `"0.0.0.0"` | Bind address for HTTP transport. |
| `MCP_PORT` | `8123` | Server port. |

#### Embedding Model

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MODEL_NAME` | `"jinaai/jina-embeddings-v2-base-code"` | HuggingFace model ID for dense embeddings. |
| `EMBED_MODEL_KWARGS` | `{"torch_dtype": "float16"}` | Extra kwargs for `HuggingFaceEmbedding(model_kwargs=...)`. |
| `EMBED_QUERY_PREFIX` | `None` | Prefix for query text (model-specific, e.g. `"search_query: "` for Nomic). |
| `EMBED_TEXT_PREFIX` | `None` | Prefix for document text (model-specific). |

#### Embedding Sequence Length & VRAM Cap

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_MAX_SEQ_LENGTH` | `4096` | Max token sequence length. Caps ALiBi attention O(N^2) VRAM cost. |
| `EMBED_DYNAMIC_VRAM_CAP` | `False` | Compute max sequence length from GPU VRAM at indexing time (CUDA only). |
| `EMBED_VRAM_SAFETY_MARGIN` | `0.15` | Fraction of VRAM to reserve (0.0-1.0). |
| `EMBED_VRAM_DEDICATED_MB` | `None` | Override GPU VRAM detection (MiB). None = auto-detect. |
| `EMBED_VRAM_SHARED_MB` | `None` | Override shared VRAM detection (MiB). None = auto-detect. |

#### Embedding Batch Sizes & Pooling

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DENSE_EMBED_BATCH_SIZE` | `32` | Max chunks per dense embedding batch. |
| `SPARSE_EMBED_BATCH_SIZE` | `32` | Max chunks per sparse embedding batch. |
| `EMBED_BATCH_MAX_TOKENS` | `16000` | Max approximate tokens per batch (chars / 4). |
| `EMBED_POOL_SIZE` | `512` | Max chunks to accumulate from multiple files before pool flush. Set 0 to disable pooling. |
| `EMBED_POOL_MAX_FILES` | `150` | Max files in pool before flush. Bounds crash recovery scope. |
| `EMBED_PIPELINE_DEPTH` | `0` | Opt-in pipelined embedding: pools in the dense stage at once (0 = legacy serial flush; e.g. 6 for TEI on GPU). Host RAM only; see [Tuning GPU memory](#tuning-gpu-memory-vram). |
| `EMBED_PARSE_QUEUE_SIZE` | `400` | Parse-ahead queue length (files), used with any pipeline depth (previously fixed at 2). Host RAM only. |
| `QDRANT_UPSERT_BATCH_SIZE` | `500` | Points per Qdrant upsert call. |

#### Indexing Mode & Search

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INDEXING_MODE` | `"hybrid"` | `"dense"`, `"sparse"`, or `"hybrid"` (recommended). |
| `SPARSE_MODEL_NAME` | `"Qdrant/bm25"` | Sparse model. BM25 always runs on CPU regardless of device settings. |
| `HYBRID_ALPHA` | `0.5` | Query blending: 0.0 = all sparse, 1.0 = all dense. **Do not change** without full validation. |
| `HYBRID_EMBED_SINGLE_PASS` | `True` | True = dense + sparse in one pass. False = two-pass (for constrained VRAM). |

#### Compute Devices

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INDEX_EMBED_DEVICE` | `"auto"` | PyTorch device for indexing. `"auto"` = best free VRAM GPU; `"0"`, `"1"` = specific GPU; `"cpu"`. |
| `MCP_EMBED_DEVICE` | `"cpu"` | PyTorch device for MCP server queries. Same values as above. |

#### OpenVINO (Intel GPU)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `USE_OPENVINO_EMBEDDING` | `False` | Use OpenVINO for embeddings (Intel GPUs). |
| `OPENVINO_EMBED_DEVICE` | `"GPU"` | OpenVINO device: `"GPU"`, `"CPU"`, or `"AUTO"`. |

#### TEI (Text Embeddings Inference)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `USE_TEI` | `True` | Enable TEI Docker backend for dense embeddings (recommended). |
| `TEI_GPU` | `"auto"` | GPU selection: `"auto"` (best free VRAM), `"0"`/`"1"` (specific), `"cpu"`. |
| `TEI_URL` | `None` | TEI server URL. Auto-derived as `http://localhost:{TEI_DOCKER_PORT}`. |
| `TEI_DOCKER_PORT` | `8090` | Host port for TEI Docker container. |
| `TEI_DTYPE` | `"float16"` | Inference dtype. Use `"float32"` for CPU-only mode. |
| `TEI_DOCKER_IMAGE` | `None` | Docker image override. Auto-detected by GPU compute capability. |
| `TEI_MODEL_DIR` | `None` | Model cache mount directory. Auto-derived from `BASE_PATH`. |
| `TEI_MAX_BATCH_TOKENS` | `None` | TEI `--max-batch-tokens`. Auto-derived from `EMBED_BATCH_MAX_TOKENS`. |
| `TEI_TOKENIZATION_WORKERS` | `None` | TEI `--tokenization-workers`. None = platform default. |
| `TEI_CONCURRENT_REQUESTS` | `64` | Concurrent HTTP requests to TEI. Set 1 for synchronous fallback. |

#### Git Branch-Aware Indexing

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DIFF_FULL_REINDEX_THRESHOLD` | `0.5` | If ratio of changed files exceeds this, fallback to full hash scan instead of git diff. |

## Tuning GPU memory (VRAM)

This section explains how each indexing parameter affects GPU memory, so you can size a configuration for your own card. The defaults in `config.py` fill almost all of a 12 GB GPU with the PyTorch backend (for example, a ~300M-parameter model in bfloat16 can reserve about 11.5 of 12 GB, as shown by `nvidia-smi`). With the same settings, an 8 GB card will usually run out of memory. An example configuration for 8 GB comes at the end of this section, but treat it as a starting point and measure on your own data.

### How memory is used

**PyTorch backend (`USE_TEI = False`).** All dense-embedding memory lives in the indexer process:

- **Model weights.** Parameters x bytes per value. This is a fixed cost; only the dtype or a different model changes it.
- **Activations of one forward pass.** This is the variable part and the usual cause of OOM. It grows linearly with *chunks in the pass x padded sequence length*. The attention part grows with the square of the sequence length, unless the model uses a memory-efficient attention kernel. It is freed after the pass.
- **PyTorch caching allocator.** Freed blocks stay *reserved* for reuse. `nvidia-smi` therefore shows the high-water mark plus fragmentation, not what the run currently has *allocated*. To measure the real peak, use `torch.cuda.max_memory_allocated()`.
- **Other processes on the same GPU.** The display, a browser, or a TEI container all take their share.

**How one forward pass is formed (PyTorch):**

1. Chunks are pooled across files and sorted longest-first.
2. The indexer cuts a *batch* that stops at `DENSE_EMBED_BATCH_SIZE` chunks or `EMBED_BATCH_MAX_TOKENS` approximate tokens (chars / 4), whichever comes first. A single chunk larger than the budget still forms its own batch.
3. llama_index `HuggingFaceEmbedding` splits the batch into forward passes of `embed_batch_size` chunks. That is the llama_index default of **10**; this project does not override it.
4. Each pass is padded to its longest chunk, capped at `EMBED_MAX_SEQ_LENGTH`.
5. Only one pass runs on the GPU at a time, because the PyTorch dense stage has a single worker.

```
chunks per pass  ~ min(10, DENSE_EMBED_BATCH_SIZE, chunks that fit in EMBED_BATCH_MAX_TOKENS)
padded length    = min(longest chunk in the pass, EMBED_MAX_SEQ_LENGTH)
peak activations ~ chunks per pass x padded length  (attention part: x padded length again)
peak VRAM        ~ weights + peak activations + allocator reserve/fragmentation + other processes
```

Because chunks are sorted longest-first, the first passes are the ones with the longest padding. An OOM therefore usually shows up early in a run, or on the first pool that contains very long chunks.

**TEI backend (`USE_TEI = True`).** The dense model runs inside the TEI Docker container. Its VRAM is roughly the weights plus buffers for one batch of up to `--max-batch-tokens` tokens. The indexer process uses no VRAM for dense embedding.

### Parameters, one by one

#### `EMBED_MAX_SEQ_LENGTH` (default `4096`). PyTorch and OpenVINO
- **Controls:** the maximum number of tokens the model sees per chunk. The tokenizer truncates anything longer.
- **Mechanism:** sets the upper bound of the padded length of each pass. Activations scale linearly with it, and the attention part scales quadratically (N^2), so at long lengths this dominates.
- **Direction:** lower means less VRAM. Halving it at least halves the activation peak of the longest passes.
- **Trade-offs:**
  - The dense vector ignores text beyond the cap. BM25 still indexes the full chunk.
  - Vectors of truncated chunks change, so rebuild with `--clear` and re-run RAG validation.
  - Slightly faster.
- **Note:** chunks are limited by characters, not tokens, so some chunks exceed 4096 tokens. The cap is what bounds them.

#### `EMBED_BATCH_MAX_TOKENS` (default `16000`). PyTorch, and TEI via `TEI_MAX_BATCH_TOKENS`
- **Controls:** the approximate token budget of one batch, counted as characters / 4.
- **Mechanism:** limits how many long chunks share a batch, and therefore a pass. With 4096-token chunks, a 16000 budget allows about 3-4 per batch. With short chunks the 10-chunk pass limit is reached first, and this budget has no effect.
- **Direction:** lower means less VRAM for passes of long chunks. Roughly linear.
- **Trade-offs:**
  - The vectors don't change; there is only floating-point noise, and no `--clear` is needed.
  - Smaller passes give lower GPU utilisation, so it is slower.
  - chars / 4 is an estimate. Code often has more real tokens than that, so the true size of a pass can exceed the budget. Keep headroom.

#### `DENSE_EMBED_BATCH_SIZE` (default `32`). PyTorch
- **Controls:** the maximum number of chunks per batch.
- **Mechanism:** only lowers VRAM when set **below 10**, because llama_index already limits each pass to 10 chunks. Between 10 and 32 it changes how often the token budget and the VRAM check are evaluated, not the size of a pass.
- **Direction:** lower means less VRAM only below 10. It mainly matters for many medium-length chunks.
- **Trade-offs:** slower at small values. Vectors are unchanged and no `--clear` is needed.
- **TEI:** not used on the TEI concurrent path, because TEI forms its own batches.

#### `embed_batch_size` (llama_index, fixed at `10`). PyTorch
- **Controls:** chunks per `SentenceTransformer.encode` pass.
- **Mechanism:** the hard upper limit on chunks per pass.
- **Configuration:** not configurable in this project today. It is listed because it explains why `DENSE_EMBED_BATCH_SIZE` above 10 does not increase VRAM.
- **Raising it (or calling `encode()` on a whole batch):** increases VRAM linearly. During development, doing this together with two concurrent dense pools caused OOM on a 12 GB GPU.

#### `EMBED_MODEL_KWARGS["torch_dtype"]` (default `"float16"`). PyTorch
- **Controls:** the precision of weights and activations.
- **Mechanism:** float16 and bfloat16 use 2 bytes per value instead of 4 for float32. That halves the weights and the activations.
- **Direction:** float16/bfloat16 use about half the VRAM of float32.
- **Trade-offs:**
  - Use bfloat16 for models trained in bf16 (for example Gemma-based embedders). It needs an Ampere or newer GPU.
  - Vectors differ between dtypes, so rebuild with `--clear`.
  - float32 is meant for CPU only.

#### `EMBED_DYNAMIC_VRAM_CAP` (default `False`), with `EMBED_VRAM_SAFETY_MARGIN`, `EMBED_VRAM_DEDICATED_MB` and `EMBED_VRAM_SHARED_MB`. PyTorch on CUDA
- **Controls:** computes the sequence cap from the detected VRAM, using the quadratic model in `shared/vram_cap.py` (which assumes the Jina ALiBi attention).
- **Mechanism:** the result is clamped to `[EMBED_MAX_SEQ_LENGTH, model max]`, so it can only **raise** the cap.
- **Direction:** enabling it can increase VRAM, never decrease it. Leave it off on small cards.

#### `INDEX_EMBED_DEVICE` (default `"auto"`) and `MCP_EMBED_DEVICE` (default `"cpu"`)
- **Controls:** which device holds the model during indexing and during MCP queries.
  - `"auto"` picks the GPU with the most free VRAM.
  - `"0"`, `"1"` and so on select a specific GPU.
  - `"cpu"` uses no VRAM.
- **Trade-offs:**
  - Prefer a GPU that isn't driving the display and isn't shared with TEI.
  - CPU always fits but is much slower.
  - Keep `MCP_EMBED_DEVICE = "cpu"` so a long-running server holds no VRAM.

#### `TEI_MAX_BATCH_TOKENS` (default `None`, which means use `EMBED_BATCH_MAX_TOKENS`). TEI
- **Controls:** TEI's `--max-batch-tokens`, the largest GPU batch TEI will form.
- **Mechanism:** sets the size of TEI's activation buffers. Roughly linear.
- **Direction:** lower means less VRAM in the container.
- **Trade-offs:**
  - Slower. Vectors are unchanged.
  - It is applied when the container is **created**, so remove the container to apply a new value.

#### `TEI_DTYPE` (default `"float16"`) and `TEI_GPU` (default `"auto"`). TEI
- **Controls:** precision and GPU choice of the TEI container, with the same reasoning as `torch_dtype` and the device settings above.
- **Advice:** keep float16 on a GPU, and don't share the GPU with a PyTorch indexer.

#### `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (environment variable, unset by default). PyTorch
- **Controls:** a standard PyTorch allocator mode that reduces fragmentation.
- **Mechanism:** less memory sits reserved but unusable, so a pass that would fail because of fragmentation can fit.
- **Effect:** does not lower allocated memory. Measure it on your own setup.

#### Parameters with no VRAM effect (host RAM only)
- **`EMBED_PIPELINE_DEPTH`** (default `0`, pipeline off; opt in with e.g. `6` for TEI on GPU)
  - PyTorch/OpenVINO: there is exactly one dense worker, so depth only sets how many pools wait in host RAM.
  - TEI: extra pools only add queued HTTP requests, and TEI still batches within `--max-batch-tokens`.
  - Higher values use more host RAM; `0` uses the legacy serial path. On a GPU, enabling it removes idle gaps between pools.
- **`EMBED_PARSE_QUEUE_SIZE`** (default `400`): parsed files waiting in a Python queue. Applies with any depth, including `0`.
- **`EMBED_POOL_SIZE`** and **`EMBED_POOL_MAX_FILES`**: chunks collected in RAM before batching. Larger pools sort better and mean less padding per pass, which helps indirectly.
- **`QDRANT_UPSERT_BATCH_SIZE`**: points per upsert call.
- **`TEI_CONCURRENT_REQUESTS`**: client-side HTTP concurrency.
- **`SPARSE_EMBED_BATCH_SIZE`** and **`HYBRID_EMBED_SINGLE_PASS`**: the default sparse model `Qdrant/bm25` runs on CPU.

### Summary table

| Parameter | Backend | Default | VRAM scaling | Lower = less VRAM? | Needs `--clear`? |
|-----------|---------|---------|--------------|--------------------|------------------|
| `EMBED_MAX_SEQ_LENGTH` | PyTorch | `4096` | linear to quadratic per pass | yes, strongest | yes |
| `EMBED_BATCH_MAX_TOKENS` | PyTorch, TEI | `16000` | linear, for long-chunk passes | yes | no |
| `DENSE_EMBED_BATCH_SIZE` | PyTorch | `32` | linear only below 10 | only below 10 | no |
| `embed_batch_size` (llama_index) | PyTorch | `10` (fixed) | linear | yes (not configurable) | no |
| `torch_dtype` | PyTorch | `float16` | x2 for float32 | use fp16/bf16 | yes |
| `EMBED_DYNAMIC_VRAM_CAP` | PyTorch | `False` | can only raise the cap | keep off | yes, if the cap changes |
| `INDEX_EMBED_DEVICE` | PyTorch | `"auto"` | which GPU / CPU | `"cpu"` = none | no |
| `TEI_MAX_BATCH_TOKENS` | TEI | = token budget | linear | yes (recreate container) | no |
| `TEI_DTYPE` | TEI | `float16` | x2 for float32 | use fp16 | yes |
| `expandable_segments` | PyTorch | unset | lowers fragmentation | n/a | no |
| pipeline depth, parse queue, pool, upsert, TEI concurrency, sparse batch | all | various | none (host RAM) | no | no |

### Example configuration for an 8 GB card (starting point, not measured)

This is an **example**, not a measured or guaranteed preset. It applies the levers above in order of effectiveness to a PyTorch run on an 8 GB GPU. Check peak VRAM on your own codebase (`nvidia-smi -l 1`, or `torch.cuda.max_memory_allocated()`) and adjust.

```python
# project-configs/<name>/config.py
USE_TEI = False
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}   # "bfloat16" for Gemma-based models
EMBED_MAX_SEQ_LENGTH = 2048     # strongest lever; longer chunks truncated for the dense vector -> --clear
EMBED_BATCH_MAX_TOKENS = 8000   # halves long-chunk passes; vectors unchanged
DENSE_EMBED_BATCH_SIZE = 16     # no VRAM effect above 10; set < 10 only if still OOM
EMBED_DYNAMIC_VRAM_CAP = False
INDEX_EMBED_DEVICE = "0"        # preferably a GPU without the display
# EMBED_PIPELINE_DEPTH: 0 by default; enabling it (e.g. 6) costs host RAM only, not VRAM
# Shell, before indexing:  set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

With TEI on 8 GB, the defaults (`TEI_MAX_BATCH_TOKENS` = 16000, float16) are usually enough for small (~150M-parameter) models, for example Jina v2 base code. For larger models, lower `TEI_MAX_BATCH_TOKENS` to 8000.

### TEI on CPU

VRAM does not matter when TEI runs on CPU, but a few parameters decide whether a CPU run works at all and how fast it is:

- **`EMBED_POOL_SIZE`: keep it clearly below TEI's `--max-concurrent-requests` (default 512).** A pool can overshoot `EMBED_POOL_SIZE`, because the last file is added whole. When one pool sends more inputs than TEI accepts, TEI answers `HTTP 429 Model is overloaded` and the run aborts. This applies to any `EMBED_PIPELINE_DEPTH`, including 0 (legacy). It shows up mostly on CPU, where requests stay queued for a long time. 256 is a safe value.
- **`TEI_MAX_BATCH_TOKENS`: start low (about 4096).** On CPU the batch buffers live in host RAM (or in the Docker VM's RAM), and float32 doubles them. A large budget can get the container OOM-killed during warm-up. Raise it only if the container has RAM to spare.
- **`EMBED_PIPELINE_DEPTH`: keep the default `0`.** Dense embedding dominates wall time and keeps all cores busy even with the legacy serial path, so there are almost no idle gaps for the pipeline to fill. Enabling it is safe once the pool size is small, but gains little.
- **`TEI_DTYPE`: must be `"float32"`** on CPU.

```python
# project-configs/<name>/config.py, TEI on CPU (example)
TEI_GPU = "cpu"
TEI_DTYPE = "float32"
TEI_MAX_BATCH_TOKENS = 4096
EMBED_POOL_SIZE = 256
EMBED_PIPELINE_DEPTH = 0   # default; pipelining gains little on CPU
```

### OOM troubleshooting

1. **Confirm it is VRAM.** Look for `CUDA out of memory` / `torch.OutOfMemoryError` in the index log. Watch `nvidia-smi -l 1` during the run and check what else holds memory on that GPU.
2. **Free the GPU.** Close other CUDA processes. Don't run a TEI container and a PyTorch indexer on the same GPU. Use `INDEX_EMBED_DEVICE` to choose the card without the display.
3. **Halve `EMBED_BATCH_MAX_TOKENS`** (16000 -> 8000 -> 4000). It doesn't change vectors, and it is the first thing to try.
4. **Lower `DENSE_EMBED_BATCH_SIZE` below 10** (8 -> 4) if most chunks are medium-length. Values from 10 to 32 make no difference to VRAM.
5. **Lower `EMBED_MAX_SEQ_LENGTH`** (4096 -> 2048). This truncates long chunks for the dense vector, so rebuild with `--clear` and re-run RAG validation.
6. **Set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`** before starting the indexer if the error says a lot of memory is "reserved but unallocated" (fragmentation).
7. **Check dtype.** Make sure `EMBED_MODEL_KWARGS` sets float16/bfloat16; float32 doubles memory.
8. **Switch backend.** TEI usually needs less VRAM for the same model. CPU (`INDEX_EMBED_DEVICE = "cpu"`) always works but is much slower.
9. **Don't add parallelism to the PyTorch dense stage** (several concurrent pools, or larger `encode()` calls) without measuring peak VRAM. That combination can easily exceed 12 GB.

## Upgrading / migration notes (indexing pipeline)

Existing project configs keep working unchanged and, by default, keep the previous sequential indexing behaviour. A project `config.py` only overrides the names it defines; everything else comes from the root `config.py`, so older configs pick up the defaults below automatically.

**New parameters and defaults**
- `EMBED_PIPELINE_DEPTH = 0`: pipelined embedding is **opt-in**. `0` runs the previous sequential (serial flush) code path. With `N > 0`, dense embedding of up to `N` pools overlaps with sparse embedding, node building, Qdrant upserts and parsing of the next files. With TEI, up to `N` pools are embedded concurrently; in-process backends (PyTorch/OpenVINO) still use a single dense worker. Enable it where the GPU idles between pools, typically TEI on a GPU:
  ```python
  EMBED_PIPELINE_DEPTH = 6
  ```
- `EMBED_PARSE_QUEUE_SIZE = 400`: number of parsed files the parse-ahead thread may buffer ahead of embedding (previously fixed at 2). It is used with **any** pipeline depth, including `0`, so older configs get the larger queue too. It only lets the parser run further ahead and costs host RAM; it does not change results. With the pipeline enabled it should stay large, otherwise the next pool is not ready when a slot frees up. Set `2` for the exact previous behaviour.
- `QDRANT_UPSERT_BATCH_SIZE = 500`: points per Qdrant upsert call, now configurable (same value as before).

**Exact previous behaviour**
```python
EMBED_PIPELINE_DEPTH = 0   # default
EMBED_PARSE_QUEUE_SIZE = 2
```

**TEI on CPU**
On CPU almost all the time goes to dense embedding, so pipelining gives little or no speed-up. Recommended:
```python
EMBED_PIPELINE_DEPTH = 0      # keep the default
EMBED_POOL_SIZE = 256         # keep well below TEI --max-concurrent-requests (default 512)
TEI_DTYPE = "float32"
TEI_MAX_BATCH_TOKENS = 4096   # TEI --max-batch-tokens; limits host RAM of the container
```
HTTP 429 ("Model is overloaded") from TEI means more requests are in flight than TEI accepts. A pool can overshoot `EMBED_POOL_SIZE`, because the last file is added whole. Lower `EMBED_POOL_SIZE` and/or `TEI_CONCURRENT_REQUESTS`, or raise `--max-concurrent-requests` on the container. This can happen with the sequential path (`EMBED_PIPELINE_DEPTH = 0`) as well, not only with the pipeline.

**Memory**
VRAM per forward pass is unchanged by these parameters (one PyTorch dense worker; TEI batches stay bounded by `--max-batch-tokens`). Host RAM grows with `EMBED_PIPELINE_DEPTH` (pools in flight) and `EMBED_PARSE_QUEUE_SIZE` (parsed files buffered); lower them on machines with little RAM.

**Reindexing**
Not needed. The pipelined and sequential paths produce identical points and vectors, and existing collections and manifests stay compatible. `--clear` now also removes branch-overlay manifests, so branch overlays are fully rebuilt after a clear.

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

## Indexing

### Build or refresh an index

```bash
# Incremental refresh (only re-embeds changed files)
python src/index_rag.py --config my_project --yes

# Full rebuild (clear + reindex)
python src/index_rag.py --config my_project --clear --yes

# Self-index (this project's own code)
python src/index_rag.py --config self-index --yes

# Test sources (for development/validation)
python src/index_rag.py --config test-sources --clear --yes
```

### CLI parameters

```
--config CONFIG        Config name or path (required for meaningful operation)
--yes                  Skip all confirmations
--clear                Clear the collection and manifest before indexing (requires --yes)
--verbose              Print verbose refresh diagnostics and chunk counts
--regenerate-manifest  Rebuild manifest by scanning existing vector store
--log-to-file          Also log to a timestamped file in the index directory
--collect-perf-stats   Collect GPU stats via nvidia-smi during indexing (CUDA only)
--dry-run              Compute file actions without embedding (diagnostic mode)
--calculate-histogram  Generate chunk histograms without embedding or Qdrant
```

### Indexing Pipeline

The indexer uses a multi-layered optimization pipeline to maximize GPU utilization:

1. **Cross-file chunk pooling** -- chunks from multiple files are accumulated into a pool (up to `EMBED_POOL_SIZE` chunks or `EMBED_POOL_MAX_FILES` files), then sorted by length for homogeneous batching. This eliminates padding waste and GPU starvation from small per-file batches.

2. **Concurrent TEI embedding** -- pool chunks are split into mini-batches of 8 and submitted to TEI via 64 concurrent HTTP requests (`TEI_CONCURRENT_REQUESTS`). TEI's internal Rust scheduler receives all requests near-simultaneously and forms optimal GPU work units.

3. **Parse-ahead thread** -- a background thread reads and parses the next files (tree-sitter, node building, ID generation) while the main thread embeds the current pool. Since tree-sitter is a C extension that releases the GIL, true parallelism is achieved.

4. **HNSW deferral** -- during bulk ingest, HNSW graph building is deferred (`indexing_threshold=200000`) to eliminate SSD I/O contention from Qdrant's background optimizer. Restored to default after all upserts complete.

5. **Double-buffered Qdrant upserts** -- previous pool's Qdrant upsert runs on a background thread while the next pool is being embedded. Cross-file batch upserts (`QDRANT_UPSERT_BATCH_SIZE`, 500 points per call) replace per-file upserts.

6. **Pipelined embedding (opt-in)** -- with `EMBED_PIPELINE_DEPTH > 0`, dense embedding of several pools overlaps with sparse embedding, node building, Qdrant upserts and parsing of the next files, so the GPU does not idle between pools. Off by default (`0`); e.g. `6` is a good value for TEI on a GPU. See [Upgrading / migration notes](#upgrading--migration-notes-indexing-pipeline).

Set `EMBED_POOL_SIZE = 0` to disable pooling and revert to per-file embedding.

### Performance

Benchmark on a production Delphi/SQL codebase (~11,000 files, ~136,000 vectors) with TEI GPU (Jina v2 base code, float16) on RTX 3060 eGPU:

| Metric | Original Baseline | Current (all optimizations) | Improvement |
|--------|------------------:|----------------------------:|------------:|
| **Total indexing time** | 25.0 min | **11.7 min** | **-53.2%** |
| GPU mean utilization | 43% | **68.1%** | +58% |
| GPU median utilization | ~35% | **89.0%** | +154% |
| Chunks/sec (wall clock) | ~91 | **192.9** | +112% |
| Validation score | 89.1% | 87.8% | -1.3pp (noise) |

See `docs/features/tei-batch-saturation/implementation-report.md` for the full phase-by-phase breakdown.

### Git Branch-Aware Indexing

When `SOURCE_DIRS` uses the `type: "git_repo"` format, the indexer supports branch-aware indexing. Only files that differ between a feature branch and the main branch are indexed as overlays -- unchanged files are served from the main-branch vectors.

**Config example:**

```python
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": "../my-repo",
        "main_branch": "develop",
        "branches": ["feature/my-feature"],
        "sources": [
            {"path": "src", "extensions": [".py", ".js"]},
            {"path": "sql", "extensions": [".sql"], "sql_dialect": "tsql"},
        ],
    },
    # Non-git entries are branch-agnostic (appear in ALL queries)
    {
        "type": "source_set",
        "path": "./docs",
        "extensions": [".md"],
    },
]
```

**How it works:**

1. **Main branch indexing** runs first (full incremental refresh as usual). Every vector gets a `branch` payload field set to the `main_branch` name.
2. **Branch overlay indexing** runs for each branch in `branches`. Uses `git diff` to find changed files, reads them via `git show` (no checkout needed), embeds, and upserts with the feature branch name as the `branch` payload.
3. **Backfill migration** automatically adds `branch` metadata to any existing vectors that lack it (one-time, runs on every indexing pass until all vectors have the field).

**Incremental main-branch comparison (Cases A/B/C):**

For `git_repo` entries, change detection uses git metadata in addition to file hashes:

- **Case A** (commit unchanged): The stored commit equals the current HEAD. Files with matching `mtime` are skipped without reading disk -- only new/modified files (different mtime) go through hash comparison.
- **Case B** (commit advanced): A `git diff` between the stored and current commit identifies exactly which files changed. Only those files (plus any with differing mtime outside the diff) are re-embedded. If the diff covers more than `DIFF_FULL_REINDEX_THRESHOLD` (default 50%) of indexed files, a full hash scan runs instead.
- **Case C** (no stored commit or git unavailable): Full hash scan against all files on disk. This is the baseline behavior used for `source_set` entries and as a fallback when git operations fail.

A `.sql` file whose `sql_dialect` differs from the manifest is re-chunked on every case, including when the hash and mtime match. A missing manifest value means `tsql`.

`source_set` entries always use Case C (hash comparison only).

**Querying with branches:**

The MCP search tool accepts an optional `branch` parameter:
- **No branch**: returns main-branch + non-git chunks (default behavior).
- **`branch="feature/foo"`**: returns main + feature + non-git chunks, with post-retrieval dedup preferring feature-branch versions. Files deleted on the feature branch are filtered via tombstones.

**Branch cleanup:** removing a branch from the `branches` list in config and re-running the indexer will automatically delete that branch's overlay vectors from Qdrant and remove its manifest file.

## Cron & Automation

Two wrapper scripts provide cron-safe operation with concurrency guards:

### refresh_guard.py

Prevents concurrent `index_rag.py` runs. Intended for hourly cron invocation.

- Skips this run if a prior one is still active (skip counter persists across invocations)
- Kills the stale process after 3 consecutive skips
- State stored in `refresh_guard_state.json` next to the Qdrant index

```bash
python src/refresh_guard.py --config my_project --yes
```

### git_pull_guard.py

Pulls all `git_repo` sources before indexing. Run before `refresh_guard.py` in cron.

- Runs `git fetch --all --prune` on every `git_repo` entry in the config
- Creates tracking branches for configured branches not yet present locally
- Pulls the current branch (if tracked); skips detached HEAD
- Parallel pull (up to 4 workers) across all repos
- Same skip/kill guard as `refresh_guard.py`

```bash
python src/git_pull_guard.py --config my_project
```

### git_pull_all.py

Simple, no-frills `git pull` for all `git_repo` entries. No concurrency guard.

```bash
python src/git_pull_all.py --config my_project
```

### Recommended crontab

```bash
0 * * * * cd /home/user/hybrid-code-rag-mcp && \
    .venv/bin/python src/git_pull_guard.py --config my_project >> /home/user/git_pull.log 2>&1 && \
    .venv/bin/python src/refresh_guard.py --config my_project --yes --log-to-file --collect-perf-stats >> /home/user/index_refresh.log 2>&1
```

## MCP Server

### Starting the MCP server

All scripts require a config name. Two transports are available:

**Stdio** (for OpenCode, Claude Desktop, and other MCP clients):
```bash
# Windows
scripts\start_rag_mcp_stdio.bat my_project
scripts\start_rag_mcp_stdio.bat self-index

# Linux/Mac
scripts/start_rag_mcp_stdio.sh my_project
scripts/start_rag_mcp_stdio.sh self-index
```

**HTTP** (for debugging, remote clients, or browser-based tools):
```bash
# Windows
scripts\start_rag_mcp_http.bat my_project
scripts\start_rag_mcp_http.bat self-index

# Linux/Mac
scripts/start_rag_mcp_http.sh my_project
scripts/start_rag_mcp_http.sh self-index
```

**Manual launch** (without scripts):
```bash
python src/rag_mcp.py --config my_project --transport stdio
python src/rag_mcp.py --config my_project --transport streamable-http
python src/rag_mcp.py --config self-index --transport stdio
```

### OpenCode integration

To use this as an MCP tool inside another project, add to that project's `opencode.jsonc`:

```jsonc
{
  "mcp": {
    "my-project-rag": {
      "type": "local",
      "enabled": true,
      "command": [
        "powershell", "-Command",
        "cmd.exe /c 'for /f \"delims=\" %a in (''git rev-parse --show-toplevel'') do call \"%a\\..\\hybrid-code-rag-mcp\\scripts\\start_rag_mcp_stdio.bat\" my_project'"
      ]
    }
  }
}
```

The PowerShell wrapper resolves paths relative to the git root, so it works regardless of which subfolder OpenCode is launched from.

**Linux/Mac equivalent:**
```json
{
  "mcp": {
    "my-project-rag": {
      "type": "local",
      "enabled": true,
      "command": ["bash", "-c", "$(git rev-parse --show-toplevel)/../hybrid-code-rag-mcp/scripts/start_rag_mcp_stdio.sh my_project"]
    }
  }
}
```

For the self-index (used inside this project's own `opencode.json`):
```json
{
  "mcp": {
    "self-rag": {
      "type": "local",
      "command": ["cmd", "/c", "scripts\\start_self_rag.bat"],
      "enabled": true,
      "timeout": 120000
    }
  }
}
```

`scripts\start_self_rag.bat` (or `scripts/start_self_rag.sh` on Linux/Mac) delegates to the stdio script with the `self-index` config. Docker auto-start is handled by `src/rag_mcp.py`.

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/start_qdrant.*` | Start Qdrant Docker container for a config (manual) | `scripts\start_qdrant.bat my_project` |
| `scripts/start_rag_mcp_stdio.*` | Start MCP server (stdio transport) | `scripts\start_rag_mcp_stdio.bat my_project` |
| `scripts/start_rag_mcp_http.*` | Start MCP server (HTTP transport) | `scripts\start_rag_mcp_http.bat self-index` |
| `scripts/start_self_rag.*` | Start self-index MCP server (stdio) | `scripts\start_self_rag.bat` |
| `scripts/start_self_rag.py` | Cross-platform Python launcher for self-index MCP | `python scripts/start_self_rag.py` |
| `src/refresh_guard.py` | Cron-safe indexing with skip/kill guard | `python src/refresh_guard.py --config my_project --yes` |
| `src/git_pull_guard.py` | Cron-safe git pull + indexing guard | `python src/git_pull_guard.py --config my_project` |
| `src/git_pull_all.py` | Simple git pull for all repos in a config | `python src/git_pull_all.py --config my_project` |

All shell scripts have `.bat` (Windows) and `.sh` (Linux/Mac) variants. Scripts except `start_self_rag` require a config name as the first argument.

**Note:** In local mode, `src/index_rag.py` and `src/rag_mcp.py` auto-start Docker containers, so `start_qdrant` is only needed for manual/diagnostic use.

## Testing

```bash
# Run all tests (2,242 tests)
.venv\Scripts\python -m pytest -v --tb=short

# Run a specific test file
.venv\Scripts\python -m pytest src_test/test_config_loader.py -v --tb=short

# Run with coverage
.venv\Scripts\python -m pytest src_test/ --cov --cov-report=term-missing -v --tb=short
```

## RAG Validation

Per-config YAML validation suites verify search quality. Test cases are defined in `project-configs/<config_name>/validation_tests.yaml`:

```bash
# Run all validation tests
python src/validate_rag.py --config my_project

# Run a specific category
python src/validate_rag.py --config my_project --category "Class & Unit Overview"

# Run a single test by ID
python src/validate_rag.py --config my_project --test T05

# List all tests without running
python src/validate_rag.py --config my_project --list

# Verbose output with chunk details
python src/validate_rag.py --config my_project --verbose

# JSON output for CI
python src/validate_rag.py --config my_project --json
```

See `docs/validation/validation-tests-guide.md` for the YAML test authoring guide.

## Linting & Formatting

```bash
ruff check .                           # Lint all files
ruff check src/index_rag.py --fix      # Auto-fix issues
black src/index_rag.py                 # Format code
mypy src/index_rag.py                  # Type checking
```

## Project Structure

```
hybrid-code-rag-mcp/
  config.py                            # System-wide defaults (embedding, devices, batching)
  project-configs/                     # Per-project index configs
    config_myproject/                    # Example: Delphi/SQL codebase with TEI
    config_another_project/            # Example: Java/HBM/JRXML webapp
  self-index/                          # Self-index config (this project's own code)
  src/
    index_rag.py                       # Main indexing entry point
    rag_mcp.py                         # MCP server entry point
    validate_rag.py                    # RAG validation test runner
    config_loader.py                   # Two-layer config loading
    refresh_guard.py                   # Cron-safe indexing wrapper
    git_pull_guard.py                  # Cron-safe git pull wrapper
    git_pull_all.py                    # Simple git pull for all repos
    shared/
      embedding.py                     # Dense embedding (PyTorch, TEI, OpenVINO)
      chunk_pool.py                    # Cross-file chunk pooling + histogram
      reranker.py                      # Post-retrieval reranking
      docker_utils.py                  # Qdrant + TEI Docker container management
      qdrant_client.py                 # Centralized QdrantClient construction
      vram_cap.py                      # Dynamic VRAM-based sequence length cap
      log.py                           # Unified logging (ms-precision timestamps)
      gpu_stats.py                     # GPU stats collector (nvidia-smi)
      sql_dialect.py                   # tsql / postgresql names and manifest compare
      readers/                         # File-type-specific chunking readers
        pascal_reader.py               # Delphi Pascal (tree-sitter)
        java_reader.py                 # Java (tree-sitter)
        groovy_reader.py               # Groovy (tree-sitter)
        js_reader.py                   # JavaScript/TypeScript (tree-sitter)
        python_reader.py               # Python (tree-sitter)
        sql_reader.py                  # SQL (T-SQL by default, PostgreSQL by sql_dialect)
        tsql_chunker.py                # T-SQL heuristic chunker
        pgsql_chunker.py               # PostgreSQL statement chunker
        cpp_reader.py                  # C and C++ (tree-sitter)
        ui_reader.py                   # Qt Designer forms
        dfm_reader.py                  # Delphi Forms
        hbm_reader.py                  # Hibernate mappings
        jrxml_reader.py                # JasperReports
        dproj_reader.py                # Delphi project files
        fr3_reader.py                  # FastReport
      validation/                      # Validation framework modules
    qdrant/
      vector_store.py                  # Qdrant vector store + BM25 sparse encoder
  src_test/                            # 2,242 tests (pytest)
  scripts/                             # Shell launcher scripts (Windows + Linux)
  docs/                                # Feature design docs, benchmark reports
  requirements/                        # Dependency files (base, CUDA, OpenVINO, dev)
```
