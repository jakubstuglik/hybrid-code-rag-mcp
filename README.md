# Code RAG Indexer & MCP Server

A versatile, high-performance RAG (Retrieval Augmented Generation) pipeline and Model Context Protocol (MCP) server explicitly designed for searching and analyzing large-scale codebases. 

While originally built for the `informica_2_0` project (Delphi/SQL), this tool has evolved into a general-purpose semantic code search engine. It features native, intelligent chunking for a variety of programming languages using Tree-sitter AST and hybrid search (Dense + Sparse/BM25) via Qdrant to ensure exact variable names and broad conceptual queries are matched perfectly.

## Features
- **Intelligent Chunking**: Uses Tree-sitter AST to parse and chunk code logically by classes, functions, and blocks rather than arbitrary line counts.
- **Robust Fallbacks**: Automatically falls back to sophisticated overlapping text chunkers for dialects that Tree-sitter struggles with (like T-SQL).
- **Hybrid Search**: Leverages both Dense (Semantic) and Sparse (Lexical BM25) vectors to catch exact variable references (e.g. `@S1Q1`) *and* conceptual questions.
- **Incremental Refresh**: Lightning-fast index updates. It tracks file hashes and modification times to only re-embed what has changed.
- **Path Mapping**: Allows seamless resolution of relative paths across different project boundaries when used as an external MCP server.
- **Multi-Tenant Configs**: Support for config overrides allows you to run completely separate indexes and MCP servers on different ports (e.g. an index for your main project, and a `self-index` for this tool's own codebase).

## Setup

### 1. Install uv (Python package manager)

uv is a fast Python package manager. Install it using:

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Or install via pip (Recommended):**
```bash
pip install uv
```

### 2. Clone and create virtual environment

```bash
git clone https://github.com/jakubstuglik/hybrid-code-rag-mcp.git
cd hybrid-code-rag-mcp

# Create virtual environment
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

#### 3.1 Development dependencies (testing, linting, formatting)

If you plan to run tests, linters, or formatters:

```bash
uv pip install -r requirements_dev.txt
```

#### 3.2 To enable CUDA (NVIDIA GPU acceleration)
If you have an NVIDIA GPU, replacing the CPU-only PyTorch with a CUDA build gives massive embedding speedups:

```bash
uv pip uninstall torch
uv pip install -r requirements_cuda.txt
```

The file defaults to **cu126** (CUDA Toolkit 12.6). If your driver is older, edit `requirements_cuda.txt` and change the `--index-url` line. See the comments inside the file for details on choosing the right version.

**What do cu121, cu124, cu126 mean?**

The `cuXYZ` suffix on PyTorch wheels indicates which CUDA Toolkit version they were compiled against. Your NVIDIA driver determines the maximum toolkit version you can use:

| Suffix | CUDA Toolkit | Minimum Driver (Linux) | Minimum Driver (Windows) |
|--------|-------------|----------------------|------------------------|
| `cu118` | 11.8 | >= 520.61 | >= 522.06 |
| `cu121` | 12.1 | >= 530.30 | >= 531.14 |
| `cu124` | 12.4 | >= 550.54 | >= 551.61 |
| `cu126` | 12.6 | >= 560.28 | >= 560.70 |

Run `nvidia-smi` and check "CUDA Version" in the top-right corner -- that is the **maximum** toolkit your driver supports. You can always use an **older** toolkit (e.g. cu121 on a driver that reports 12.6), but not a newer one. When in doubt, `cu121` is the safest default.

Test CUDA availability:
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

#### 3.3 To enable OpenVINO (Intel GPU acceleration)
If you have an Intel integrated or discrete GPU (Iris Xe, Arc, etc.) and no NVIDIA GPU, OpenVINO provides significant embedding speedups over CPU-only PyTorch (~15x faster in testing).

```bash
uv pip install -r requirements_openvino.txt
```

Verify your Intel GPU is visible to OpenVINO:
```bash
python -c "import openvino as ov; print(ov.Core().available_devices)"
# Should print something like: ['CPU', 'GPU']
```

Then enable it in your `config.py` (or override config):
```python
USE_OPENVINO_EMBEDDING = True
OPENVINO_EMBED_DEVICE = "GPU"   # or "CPU" / "AUTO"

# Clear torch-specific kwargs (not used by OpenVINO)
EMBED_MODEL_KWARGS = {}
```

**Note:** When `USE_OPENVINO_EMBEDDING = True`, the `INDEX_EMBED_DEVICE` and `MCP_EMBED_DEVICE` settings are ignored — OpenVINO manages its own device placement via `OPENVINO_EMBED_DEVICE`.

## Configuration (config.py)

By default, the system reads from `config.py`. Here you define the target source directories, the Qdrant connection info, and the embedding models.

### Defining Source Directories
In `config.py`, configure the `SOURCE_DIRS` list. You can map local relative paths or symbolic links to arbitrary mapped paths in the vector database.

```python
SOURCE_DIRS = [
    {
        "path": "source", # Path relative to this project or a symlink
        "map_to_path": "delphi_src", # How the MCP server presents the path
        "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj"],
    },
    {
        "path": "schemas",
        "map_to_path": "sql_script",
        "extensions": [".sql"],
    },
]
```

### Recommended Embedding Models for Code
* **Dense (`MODEL_NAME`)**: `jinaai/jina-embeddings-v2-base-code` (Highly recommended for coding tasks, supports 8192 tokens)
* **Sparse (`SPARSE_MODEL_NAME`)**: `Qdrant/bm25` (Excellent for exact lexical matching of variables, uses zero VRAM)

### Configuration Overrides
You can create override configs to run multiple indexers. For example, a `self-index` to allow AI agents to navigate this tool's own source code:

```bash
# Create override config
mkdir self-index
# Add self-index/config.py with overrides (e.g. QDRANT_PORT = 6973)

# Run with override
python index_rag.py --config self-index
python rag_mcp.py --config self-index
```

## Vector Store (Qdrant)

The system relies on Qdrant as the vector database.

**IMPORTANT:** Always use the provided startup scripts to launch the Qdrant Docker container. These scripts automatically read the correct host ports and volume bindings from your `config.py` (or override config).

```bash
# Start main Qdrant instance
start_qdrant.bat

# Start a secondary/override instance (e.g. self-index)
start_self_rag.bat 
```

## Indexing Code

**Default Behavior (`uv run index_rag.py`): Incremental refresh**
1. Loads `index_manifest.json` from the configured volume.
2. Scans `SOURCE_DIRS` for file additions, modifications, and deletions.
3. Automatically deletes old vectors, chunks new code using AST/Text splitters, and generates hybrid embeddings.
4. Updates the manifest.

**CLI Parameters:**
```bash
uv run index_rag.py --help
```
- `--config CONFIG`: Config name (e.g., 'self-index') or path to config file override.
- `--regenerate-manifest`: Rebuild manifest by scanning existing vector store (one-time bootstrap).
- `--verbose`: Print verbose refresh diagnostics and chunk counts.
- `--clear`: Clear the vector collection and manifest before indexing (requires `--yes`).
- `--yes`: Skip all confirmations.
- `--log-to-file`: Also log output to a timestamped file in the index directory (useful for long background runs).
- `--collect-perf-stats`: Collect GPU stats via nvidia-smi during indexing (CUDA only).

## Usage with MCP Server

Once indexed, you can launch the MCP server. This allows AI assistants (like OpenCode, Claude Desktop, etc.) to query the codebase dynamically.

### Ready-to-use Batch Scripts
For convenience, the project includes pre-configured `.bat` scripts to start the MCP servers easily:
- `start_main_rag_mcp_stdio.bat`: Starts the main RAG server via stdio (Standard Input/Output) - Required by OpenCode and Claude Desktop tools.
- `start_main_rag_mcp_http.bat`: Starts the main RAG server via HTTP/SSE (useful for debugging or remote clients).
- `start_self_rag.bat`: Starts the `self-index` Qdrant instance and stdio server so AI agents can query this tool's own codebase.

### Manual Launch
```bash
# HTTP Transport
uv run rag_mcp.py --transport http

# Stdio Transport (For direct tool integration)
uv run rag_mcp.py --transport stdio
```

### OpenCode Integration
To use this as a tool inside another OpenCode project, update the target project's `opencode.jsonc`. Because OpenCode resolves command paths relative to the current working directory, use this reliable PowerShell wrapper to execute the MCP script regardless of which subfolder OpenCode is launched from:

```json
{
  "mcp": {
    "code-rag": {
      "type": "local",
      "enabled": true,
      "command": [
        "powershell",
        "-Command",
        "cmd.exe /c 'for /f \"delims=\" %a in (''git rev-parse --show-toplevel'') do call \"%a\\..\\hybrid-code-rag-mcp\\start_main_rag_mcp_stdio.bat\"'"
      ]
    }
  }
}
```

## Supported File Types & Parsers

| Extension | Parser Mechanism |
|-----------|------------------|
| `.pas`/`.dpr` | Tree-sitter Pascal AST |
| `.sql` | Tree-sitter SQL AST (Falls back to `TokenTextSplitter` for T-SQL dialects) |
| `.dfm` | Custom Delphi Object parser |
| `.dproj` | Built-in XML parser |
| `.fr3` | FastReport XML parser (extracts scripts/memos/bands) |
| `.py`/`.js`/etc | Easily extensible via `shared/readers/READER_REGISTRY` |

