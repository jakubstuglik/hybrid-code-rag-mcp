# informica-rag

RAG (Retrieval Augmented Generation) indexer for Delphi Pascal source code, SQL schemas, and FastReport .fr3 files.

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
git clone https://github.com/yourusername/informica-rag.git
cd informica-rag

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

#### 3.1 To enable CUDA (device="cuda" instead of cpu in HuggingFaceEmbedding)
```bash
uv pip uninstall torch torchvision torchaudio
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Test:
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU'); print('Torch version:', torch.__version__)"
```

### 4. Create symbolic links to your source files

This project expects two directories:
- `source/` - Delphi Pascal source code (.pas, .dpr, .dfm files)
- `schemas/` - SQL database schema files

Create symbolic links pointing to your actual files. **Note: These specific paths are used for the Informica 2.0 RAG indexing.**

**Windows (PowerShell - run as Administrator):**
```powershell
# Example paths for Informica 2.0
New-Item -ItemType SymbolicLink -Path "source" -Target "C:\Gitrepos\informica_2_0\delphi_src"
New-Item -ItemType SymbolicLink -Path "schemas" -Target "C:\Gitrepos\informica_2_0\sql_srcipt\6RedGate"
```

**Windows (Command Prompt - run as Administrator):**
```cmd
mklink /D source C:\Gitrepos\informica_2_0\delphi_src
mklink /D schemas C:\Gitrepos\informica_2_0\sql_srcipt\6RedGate
```

## Indexing

**Default Behavior (`uv run index_delphi.py`): Incremental refresh**
1. Loads `index_manifest.json` from store path (tracks file paths, mtimes, hashes, vector_ids).
2. Scans `source/` & `schemas/` for changes (add/modify/delete via hash/mtime).
3. Deletes old vectors, embeds/inserts new nodes using custom parsers (Tree-sitter/XML).
4. Updates & saves manifest for next run.

If no manifest: Auto-regenerates from store or prompts full index.

**CLI Parameters:**
```bash
uv run index_delphi.py --help
```
- `--regenerate-manifest`: Rebuild manifest by scanning existing vector store.
- `--fix-paths`: Convert absolute `file_path` metadata to relative paths (e.g., `source/foo.pas`).
- `--force-full-index`: **DESTRUCTIVE** - Deletes index/manifest, full re-index (type 'YES').
- `--verbose`: Detailed logs of changes, node counts, parse fallbacks.

**NVidia monitoring (CUDA):**
```bash
nvidia-smi -l 2
```
Low power? Set Windows to High Performance; add `python.exe` to NVIDIA Control Panel.

Indexed data stored in `./{STORE_TYPE}/{MODEL_PATH}_{STORE_TYPE}`.

## Configuration (config.py)

Edit `config.py` to customize settings. All parameters:

| Parameter | Description | Example/Default |
|-----------|-------------|-----------------|
| `STORE_TYPE` | Vector store backend | `"qdrant"` or `"chroma"` |
| `QDRANT_USE_LOCAL_FILE` | Use local Qdrant file storage (False = Docker) | `False` |
| `MODEL_NAME` | HuggingFace embedding model name | `"BAAI/bge-small-en-v1.5"` |
| `MODEL_PATH` | **Critical:** Storage folder name & Docker volume alignment | `"index_bge_small_testing_20260303"` |
| `COLLECTION_NAME` | Vector collection name | `"delphi_rag"` |
| `QDRANT_USE_DOCKER` | Connect to Dockerized Qdrant | `True` |
| `QDRANT_HOST` | Qdrant host (Docker: localhost) | `"localhost"` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `EMBED_MODEL_KWARGS` | Embedding model options (e.g., dtype) | `{"torch_dtype": "float16"}` |
| `INDEX_EMBED_DEVICE` | Device for indexing embeddings | `"cpu"` or `"cuda"` |
| `MCP_EMBED_DEVICE` | Device for MCP server embeddings | `"cpu"` or `"cuda"` |

Utility functions like `get_index_path()` derive paths from `STORE_TYPE` + `MODEL_PATH`.

## Vector Store (Qdrant)

**IMPORTANT:** Always use `start_qdrant.bat` to start Qdrant. This script reads `MODEL_PATH` and `QDRANT_PORT` from `config.py` to mount the correct persistent volume.

```bash
start_qdrant.bat
```

## Usage with MCP Server

After indexing, start the MCP server:

```bash
uv run informica_rag_mcp.py
```

- `--lazy-init`: Defer model/index load until first query.

## Project Structure

```
informica-rag/
├── index_delphi.py          # Main incremental indexer
├── informica_rag_mcp.py     # MCP server for RAG queries
├── start_qdrant.bat         # Starts Qdrant Docker (reads config.py)
├── config.py                # All configuration parameters
├── shared/                  # Readers, embedding, indexing utilities
├── source/                  # Symlink: Delphi source (.pas/.dpr/.dfm/.fr3/.dproj)
├── schemas/                 # Symlink: SQL schemas (.sql)
├── chroma/                  # Vital Chroma code for indexing/MCP serving
│   └── vector_store.py      # ChromaVectorStore connector
├── qdrant/                  # Vital Qdrant code/utilities for indexing/MCP
│   ├── vector_store.py      # QdrantVectorStore connector
│   ├── fix_paths.py         # Normalize absolute paths to relative
│   ├── migrate.py           # Migrate from Chroma to Qdrant
│   ├── verify_payload.py    # Validate payloads
│   └── ...                  # dump/repair/migration tools
├── requirements.txt
├── docker-compose.yml
├── AGENTS.md
├── TODO.md
└── README.md
```

## Supported File Types

| Extension | Parser |
|-----------|--------|
| `.pas`/`.dpr` | Tree-sitter Pascal AST |
| `.dfm` | Custom object parser |
| `.dproj` | XML parser |
| `.fr3` | XML (scripts/memos/bands) |
| `.sql` | Tree-sitter SQL AST |
