# Code RAG Indexer & MCP Server

A versatile, high-performance RAG (Retrieval Augmented Generation) pipeline and Model Context Protocol (MCP) server designed for searching and analyzing large-scale codebases.

It features intelligent chunking using Tree-sitter AST parsing, hybrid search (Dense + Sparse/BM25) via Qdrant, and a multi-config architecture that supports running separate indices and MCP servers for different projects from a single installation.

## Features

- **Intelligent Chunking**: Tree-sitter AST parsing chunks code by classes, functions, and logical blocks -- not arbitrary line counts.
- **Robust Fallbacks**: Automatic fallback to sophisticated text chunkers for dialects Tree-sitter struggles with (e.g. T-SQL).
- **Hybrid Search**: Dense (semantic) + Sparse (BM25 lexical) vectors catch both exact variable references (`@S1Q1`) and conceptual queries.
- **Incremental Refresh**: Tracks file hashes and modification times to only re-embed what has changed.
- **Git Branch-Aware Indexing**: Index feature branches as lightweight overlays on the main branch. Query with a `branch` parameter to get results that include your branch's changes, with automatic dedup.
- **Multi-Index Architecture**: Each index has its own config file. Run separate indices and MCP servers for different projects, all sharing common system settings.
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
| Other | Extensible via `shared/readers/READER_REGISTRY` |

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
uv pip install -r requirements.txt
```

**Development dependencies** (testing, linting, formatting):
```bash
uv pip install -r requirements_dev.txt
```

### 4. GPU acceleration (optional)

**CUDA (NVIDIA GPU):**
```bash
uv pip uninstall torch
uv pip install -r requirements_cuda.txt
```

The file defaults to **cu126** (CUDA 12.6). Run `nvidia-smi` and check "CUDA Version" in the top-right corner -- that is the maximum toolkit your driver supports. You can always use an older toolkit (e.g. cu121 on a driver reporting 12.6), but not a newer one. Edit `requirements_cuda.txt` to change the version if needed.

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

**OpenVINO (Intel GPU):**
```bash
uv pip install -r requirements_openvino.txt
python -c "import openvino as ov; print(ov.Core().available_devices)"
```

Then enable in your config: `USE_OPENVINO_EMBEDDING = True`, `OPENVINO_EMBED_DEVICE = "GPU"`.

## Configuration

### Architecture

The config system uses a two-layer approach:

| File | Purpose |
|------|---------|
| `config.py` | **Common system defaults** -- embedding model, devices, batch sizes, VRAM cap, indexing mode. Loaded first for every config. |
| `config_informica.py` | **Informica index** -- SOURCE_DIRS, COLLECTION_NAME, Qdrant connection, MCP identity for the Informica 2.0 Delphi/SQL codebase. |
| `self-index/config.py` | **Self-index** -- indexes this project's own source code for AI-assisted development. |
| `test-sources/config.py` | **Test sources** -- curated test files for validation during development. |

`config_loader.py` always loads `config.py` first, then overlays the specified config on top. All scripts require a `--config` parameter to specify which index to work with.

### Creating a new index config

Create a new `.py` file (e.g. `config_myproject.py`) in the project root or a subdirectory:

```python
# config_myproject.py — simple (source_set / legacy format)
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
# config_myproject.py — git_repo format (supports branch overlays)
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

Then use it: `python index_rag.py --config config_myproject --yes`

### Recommended Embedding Models

- **Dense** (`MODEL_NAME`): `jinaai/jina-embeddings-v2-base-code` -- optimized for code, 8192 token context
- **Sparse** (`SPARSE_MODEL_NAME`): `Qdrant/bm25` -- exact lexical matching, zero VRAM

## Vector Store (Qdrant)

The system uses Qdrant as its vector database. Two deployment modes are supported:

### Local mode (`QDRANT_MODE = "local"`)

Docker containers are **auto-managed**: `index_rag.py` and `rag_mcp.py` automatically check for, create, and start the container before connecting. No manual `docker start` needed.

Container naming is auto-derived as `qdrant-{COLLECTION_NAME}` (e.g. `qdrant-informica_rag`), overridable via `QDRANT_DOCKER_CONTAINER` in your config.

**Requirements:** Docker Desktop must be installed and `docker` must be in PATH.

**Manual start** (if you prefer):
```bash
start_qdrant.bat config_informica
```

### Remote mode (`QDRANT_MODE = "remote"`)

For Qdrant Cloud or self-hosted remote servers. Supports API key authentication, HTTPS, and gRPC:

```python
# config_myproject.py
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
python index_rag.py --config config_informica --yes

# Full rebuild (clear + reindex)
python index_rag.py --config config_informica --clear --yes

# Self-index (this project's own code)
python index_rag.py --config self-index --yes

# Test sources (for development/validation)
python index_rag.py --config test-sources --clear --yes
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
```

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
start_rag_mcp_stdio.bat config_informica
start_rag_mcp_stdio.bat self-index
```

**HTTP** (for debugging, remote clients, or browser-based tools):
```bash
start_rag_mcp_http.bat config_informica
start_rag_mcp_http.bat self-index
```

**Manual launch** (without batch scripts):
```bash
python rag_mcp.py --config config_informica --transport stdio
python rag_mcp.py --config config_informica --transport streamable-http
python rag_mcp.py --config self-index --transport stdio
```

### OpenCode integration

To use this as an MCP tool inside another project, add to that project's `opencode.jsonc`:

```jsonc
{
  "mcp": {
    "informica-rag": {
      "type": "local",
      "enabled": true,
      "command": [
        "powershell", "-Command",
        "cmd.exe /c 'for /f \"delims=\" %a in (''git rev-parse --show-toplevel'') do call \"%a\\..\\hybrid-code-rag-mcp\\start_rag_mcp_stdio.bat\" config_informica'"
      ]
    }
  }
}
```

The PowerShell wrapper resolves paths relative to the git root, so it works regardless of which subfolder OpenCode is launched from.

For the self-index (used inside this project's own `opencode.json`):
```json
{
  "mcp": {
    "self-rag": {
      "type": "local",
      "command": ["cmd", "/c", "start_self_rag.bat"],
      "enabled": true,
      "timeout": 120000
    }
  }
}
```

`start_self_rag.bat` delegates to `start_rag_mcp_stdio.bat self-index`. Docker auto-start is handled by `rag_mcp.py`.

## Batch Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `start_qdrant.bat` | Start Qdrant Docker container for a config (manual) | `start_qdrant.bat config_informica` |
| `start_rag_mcp_stdio.bat` | Start MCP server (stdio transport) | `start_rag_mcp_stdio.bat config_informica` |
| `start_rag_mcp_http.bat` | Start MCP server (HTTP transport) | `start_rag_mcp_http.bat self-index` |
| `start_self_rag.bat` | Start self-index MCP server (stdio) | `start_self_rag.bat` |

All scripts except `start_self_rag.bat` require a config name as the first argument.

**Note:** In local mode, `index_rag.py` and `rag_mcp.py` auto-start Docker containers, so `start_qdrant.bat` is only needed for manual/diagnostic use.

## Testing

```bash
# Run all tests
.venv\Scripts\python -m pytest -v --tb=short

# Run a specific test file
.venv\Scripts\python -m pytest tests/test_config_loader.py -v --tb=short

# Run with coverage
.venv\Scripts\python -m pytest tests/ --cov --cov-report=term-missing -v --tb=short
```

## RAG Validation

A 65-test automated validation suite verifies search quality across 11 categories:

```bash
# Run all validation tests
python validate_rag.py --config config_informica

# Run a specific category
python validate_rag.py --config config_informica --category "Class & Unit Overview"

# Verbose output with chunk details
python validate_rag.py --config config_informica --verbose
```

## Linting & Formatting

```bash
ruff check .                       # Lint all files
ruff check index_rag.py --fix      # Auto-fix issues
black index_rag.py                 # Format code
mypy index_rag.py                  # Type checking
```
