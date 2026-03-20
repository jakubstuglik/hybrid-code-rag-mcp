# Code RAG Indexer & MCP Server

A versatile, high-performance RAG (Retrieval Augmented Generation) pipeline and Model Context Protocol (MCP) server designed for searching and analyzing large-scale codebases.

It features intelligent chunking using Tree-sitter AST parsing, hybrid search (Dense + Sparse/BM25) via Qdrant, and a multi-config architecture that supports running separate indices and MCP servers for different projects from a single installation.

## Features

- **Intelligent Chunking**: Tree-sitter AST parsing chunks code by classes, functions, and logical blocks -- not arbitrary line counts.
- **Robust Fallbacks**: Automatic fallback to sophisticated text chunkers for dialects Tree-sitter struggles with (e.g. T-SQL).
- **Hybrid Search**: Dense (semantic) + Sparse (BM25 lexical) vectors catch both exact variable references (`@S1Q1`) and conceptual queries.
- **Multiple Embedding Backends**: PyTorch (CUDA/CPU), OpenVINO (Intel GPU), and TEI (HuggingFace Text Embeddings Inference via Docker). TEI is 4.5x faster and uses 3.3x less VRAM than PyTorch.
- **Incremental Refresh**: Uses content hashes and git diffs to detect changes, re-embedding only what has changed.
- **Git Branch-Aware Indexing**: Index feature branches as lightweight overlays on the main branch. Query with a `branch` parameter to get results that include your branch's changes, with automatic dedup.
- **Multi-Index Architecture**: Each index has its own config file. Run separate indices and MCP servers for different projects, all sharing common system settings.
- **Cross-File Chunk Pooling**: Accumulates chunks from multiple files before embedding, enabling length-sorted batching across files. Reduces TEI padding waste and GPU idle time, achieving 22% faster indexing and 36% higher GPU utilization.
- **Post-Retrieval Reranking**: Query intent detection promotes overview chunks for "what is X?" queries while preserving precision for exact lookups.

## Supported File Types & Parsers

| Extension | Parser |
|-----------|--------|
| `.pas` / `.dpr` | Tree-sitter Pascal AST (class summaries, method grouping, context prefixes) |
| `.sql` | Tree-sitter SQL AST + T-SQL heuristic chunker fallback |
| `.dfm` | Custom Delphi Form parser (recursive descent, component grouping) |
| `.dproj` | Built-in XML parser (project overview, build configs, unit groups) |
| `.fr3` | FastReport XML parser (scripts, memos, bands) |
| `.py` | Tree-sitter Python AST (leaf/container pattern, class context) |
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

Hardware is auto-detected: NVIDIA GPU uses the CUDA Docker image, no GPU falls back to CPU image. See `project-configs/config_informica_tei_jinaai/config.py` for a complete example including a commented-out CPU mode block.

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
            {"path": "sql", "extensions": [".sql"]},
        ],
    },
]
```

Then use it: `python src/index_rag.py --config my_project --yes`

### Recommended Embedding Models

- **Dense** (`MODEL_NAME`): `jinaai/jina-embeddings-v2-base-code` -- optimized for code, 8192 token context
- **Sparse** (`SPARSE_MODEL_NAME`): `Qdrant/bm25` -- exact lexical matching, zero VRAM

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
--config CONFIG     Config name or path (required for meaningful operation)
--yes               Skip all confirmations
--clear             Clear the collection and manifest before indexing (requires --yes)
--verbose           Print verbose refresh diagnostics and chunk counts
--regenerate-manifest  Rebuild manifest by scanning existing vector store
--log-to-file       Also log to a timestamped file in the index directory
--collect-perf-stats   Collect GPU stats via nvidia-smi during indexing (CUDA only)
--dry-run           Compute file actions without embedding (diagnostic mode)
--calculate-histogram  Generate chunk histograms without embedding or Qdrant
```

### Cross-File Chunk Pooling

By default, chunks from multiple files are accumulated into a pool before embedding. The embedding engine sorts all pooled chunks by length, forming batches of similar-sized texts. This reduces padding waste (especially for TEI) and keeps the GPU busy with full batches instead of undersized per-file batches.

**Config parameters** (in `config.py`):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_POOL_SIZE` | 512 | Max chunks to accumulate before flushing for cross-file batch embedding |
| `EMBED_POOL_MAX_FILES` | 150 | Max files in pool before flush (bounds crash recovery scope) |

Set `EMBED_POOL_SIZE = 0` to disable pooling and revert to per-file embedding.

**Benchmark (TEI GPU, Jina v2 base code, RTX 4060):** 22% faster total indexing time (26.3 min -> 20.8 min), 36% higher average GPU utilization (28.3% -> 38.5%), zero quality regression. See `docs/features/tei-batch-saturation/implementation-report.md` for full results.

### Git Branch-Aware Indexing

When `SOURCE_DIRS` uses the `type: "git_repo"` format, the indexer supports branch-aware indexing. Only files that differ between a feature branch and the main branch are indexed as overlays — unchanged files are served from the main-branch vectors.

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
            {"path": "sql", "extensions": [".sql"]},
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

- **Case A** (commit unchanged): The stored commit equals the current HEAD. Files with matching `mtime` are skipped without reading disk — only new/modified files (different mtime) go through hash comparison.
- **Case B** (commit advanced): A `git diff` between the stored and current commit identifies exactly which files changed. Only those files (plus any with differing mtime outside the diff) are re-embedded. If the diff covers more than `DIFF_FULL_REINDEX_THRESHOLD` (default 50%) of indexed files, a full hash scan runs instead.
- **Case C** (no stored commit or git unavailable): Full hash scan against all files on disk. This is the baseline behavior used for `source_set` entries and as a fallback when git operations fail.

`source_set` entries always use Case C (hash comparison only).

**Querying with branches:**

The MCP search tool accepts an optional `branch` parameter:
- **No branch**: returns main-branch + non-git chunks (default behavior).
- **`branch="feature/foo"`**: returns main + feature + non-git chunks, with post-retrieval dedup preferring feature-branch versions. Files deleted on the feature branch are filtered via tombstones.

**Branch cleanup:** removing a branch from the `branches` list in config and re-running the indexer will automatically delete that branch's overlay vectors from Qdrant and remove its manifest file.

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
| `scripts\start_qdrant.bat` / `scripts/start_qdrant.sh` | Start Qdrant Docker container for a config (manual) | `scripts\start_qdrant.bat my_project` |
| `scripts\start_rag_mcp_stdio.bat` / `scripts/start_rag_mcp_stdio.sh` | Start MCP server (stdio transport) | `scripts\start_rag_mcp_stdio.bat my_project` |
| `scripts\start_rag_mcp_http.bat` / `scripts/start_rag_mcp_http.sh` | Start MCP server (HTTP transport) | `scripts\start_rag_mcp_http.bat self-index` |
| `scripts\start_self_rag.bat` / `scripts/start_self_rag.sh` | Start self-index MCP server (stdio) | `scripts\start_self_rag.bat` |

All scripts except `start_self_rag` require a config name as the first argument. The `.bat` scripts are for Windows and the `.sh` scripts are for Linux/Mac.

**Note:** In local mode, `src/index_rag.py` and `src/rag_mcp.py` auto-start Docker containers, so `start_qdrant` is only needed for manual/diagnostic use.

## Testing

```bash
# Run all tests
.venv\Scripts\python -m pytest -v --tb=short

# Run a specific test file
.venv\Scripts\python -m pytest src_test/test_config_loader.py -v --tb=short

# Run with coverage
.venv\Scripts\python -m pytest src_test/ --cov --cov-report=term-missing -v --tb=short
```

## RAG Validation

A 78-test automated validation suite verifies search quality across 14 categories:

```bash
# Run all validation tests
python src/validate_rag.py --config my_project

# Run a specific category
python src/validate_rag.py --config my_project --category "Class & Unit Overview"

# Verbose output with chunk details
python src/validate_rag.py --config my_project --verbose
```

## Linting & Formatting

```bash
ruff check .                           # Lint all files
ruff check src/index_rag.py --fix      # Auto-fix issues
black src/index_rag.py                 # Format code
mypy src/index_rag.py                  # Type checking
```
