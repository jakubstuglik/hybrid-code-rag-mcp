# informica-rag

RAG (Retrieval Augmented Generation) indexer for Delphi Pascal source code, SQL schemas, and FastReport .fr3 files.

## Setup

### 1. Install uv (Python package manager)

uv is a fast Python package manager. Install it using:

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Windows (Winget):**
```powershell
winget install astral-sh.uv
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or install via pip:
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
```uv pip uninstall torch torchvision torchaudio```

```uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121```

Test:
```python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU'); print('Torch version:', torch.__version__)"```

### 4. Create symbolic links to your source files

This project expects two directories:
- `source/` - Delphi Pascal source code (.pas, .dpr, .dfm files)
- `schemas/` - SQL database schema files

Create symbolic links pointing to your actual files:

**Windows (PowerShell - run as Administrator):**
```powershell
# Example paths - adjust to match your system
# The common base path is typically:  C:\[path-to-folder]\informica_2_0\

New-Item -ItemType SymbolicLink -Path "source" -Target "C:\Gitrepos\informica_2_0\delphi_src"
New-Item -ItemType SymbolicLink -Path "schemas" -Target "C:\Gitrepos\informica_2_0\sql_srcipt\6RedGate"
```

**Windows (Command Prompt - run as Administrator):**
```cmd
mklink /D source C:\Gitrepos\informica_2_0\delphi_src
mklink /D schemas C:\Gitrepos\informica_2_0\sql_srcipt\6RedGate
```

**Linux/Mac:**
```bash
ln -s /path/to/informica_2_0/delphi_src source
ln -s /path/to/informica_2_0/sql_srcipt/6RedGate schemas
```

### 5. Run the indexer

```bash
uv run index_delphi.py
```

NVidia monitoring (when using CUDA):
```nvidia-smi -l 2```

If you have low power usage, check Windows power plan, should be high performance, Add python (the one that is actually run, you can check it in windows task manager -> python process -> expand tree -> right click -> show file location) in NVidia control panel -> program settings.
This should kick drawn power to 90 or more Watts. Then it goes much faster.

The indexed data will be stored in `chroma/` or `qdrant/` directories based on your config.py settings.

## Project Structure

```
informica-rag/
├── index_delphi.py          # Main indexing script (supports Chroma/Qdrant)
├── chroma/                  # Chroma vector database storage
├── qdrant/                  # Qdrant vector database storage
├── shared/                  # Common utilities and modules
├── source/                  # Delphi source code (symlink)
├── schemas/                 # SQL schema files (symlink)
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker configuration for Qdrant
├── AGENTS.md                # Developer guidelines
└── README.md                # This file
```
informica-rag/
├── index_delphi.py          # Main indexing script
├── chroma/                  # Chroma vector database (when STORE_TYPE=chroma)
├── qdrant/                  # Qdrant vector database (when STORE_TYPE=qdrant)
└── source/                  # Delphi source code
├── source/  -> <symlink>    # Delphi source code
├── schemas/ -> <symlink>    # SQL schema files
├── requirements.txt         # Python dependencies
├── AGENTS.md               # Developer guidelines for AI agents
└── README.md               # This file
```

## Supported File Types

| Extension | Description | Parser |
|-----------|-------------|--------|
| `.pas` | Delphi Pascal units | Tree-sitter AST + CodeSplitter |
| `.dpr` | Delphi project files | Tree-sitter AST + CodeSplitter |
| `.dfm` | Delphi form files | CodeSplitter |
| `.fr3` | FastReport templates | XML parser + SentenceSplitter |
| `.sql` | SQL schema files | CodeSplitter |

## Switching Vector Stores / Models

Edit `config.py`:
- `STORE_TYPE = "chroma"` or `"qdrant"`
- `MODEL_PATH = "index_bge_m3"` or `"index_bge_small_v1.5"`

**Chroma**: Direct local dirs (`./chroma/${MODEL_PATH}_chroma`).

**Qdrant**:
1. `start_qdrant.bat` (auto-mounts `./qdrant/${MODEL_PATH}_qdrant` so the Docker container loads the aligned index).
2. Or `docker compose up -d` after exporting `MODEL_PATH`.

Switch: edit `config.py`, restart the Qdrant container, and rerun the indexer/MCP server.

## Dockerized Qdrant

Running Qdrant locally requires Docker because the Compose stack mounts the stored index (`./qdrant/${MODEL_PATH}_qdrant`) as a volume. Keep Docker running while the indexer or MCP server operate. `start_qdrant.bat` automates setting the correct path per `MODEL_PATH`.

If your Qdrant instance lives on a different machine, set `QDRANT_USE_DOCKER = False` (or keep it `True` and supply the remote host/port) and configure `QDRANT_HOST`/`QDRANT_PORT` in `config.py`. The indexer and MCP scripts will then connect over the network instead of the local container.

## Command-Line Arguments

The main script supports several options:

```bash
uv run index_delphi.py --help
```

- `--regenerate-manifest`: Regenerate manifest from existing index (one-time bootstrap)
- `--fix-paths`: Convert absolute file paths in vector DB to relative paths
- `--force-full-index`: Force full re-indexing with confirmation (destructive)

## Default Indexing Run

Run `uv run index_delphi.py` with no additional flags to bootstrap and refresh the vector index:

1. The script loads `index_manifest.json` from the directory returned by `config.get_index_path()` and regenerates it from the existing vector store if it is missing (Chroma backends only). If regeneration fails, you are prompted to confirm a full reindex so a manifest can be created.
2. Once the manifest exists, the script records hashes/mtimes and compares them to the current workspace to detect added, modified, or deleted files.
3. The index is updated incrementally using the manifest's `vector_ids` per file, keeping deletions and insertions in sync; the manifest is rewritten afterward for the next run.
4. Future invocations simply rerun this refresh logic, so running the script after every change keeps the index and manifest aligned. Use `--regenerate-manifest` to rebuild the manifest from an existing store or `--force-full-index` to start over when necessary.

## Usage with MCP Server

After indexing, use the MCP server for RAG queries:

```bash
uv run informica_rag_mcp.py
```

## Troubleshooting

- **Chroma lock errors**: Delete `chroma/.../chroma.sqlite3` if locked
- **Memory issues**: Change `INDEX_EMBED_DEVICE` in config.py to "cpu" or reduce batch sizes
- **Encoding issues**: The script handles UTF-8 and Windows-1250 encodings automatically
- **Qdrant migration**: After migrating from Chroma to Qdrant, run `uv run index_delphi.py --fix-paths`
- **Slow indexing**: For large projects, use Qdrant with Docker and set embed device to GPU
- **Docker issues**: If Qdrant container fails, check port 6333 availability: `netstat -ano | findstr 6333`
