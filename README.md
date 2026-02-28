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
python index_delphi_chroma.py
```

The indexed data will be stored in `index_storage/` directory.

## Project Structure

```
informica-rag/
├── index_delphi_chroma.py   # Main indexing script
├── index_storage/           # Chroma vector database (created on first run)
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

## Usage with MCP Server

After indexing, you can use the MCP server for RAG queries. See `delphi_rag_mcp.py` (if present).

## Troubleshooting

- **Chroma lock errors**: Delete `index_storage/chroma.sqlite3` if locked
- **Memory issues**: Use CPU mode in the script or reduce batch sizes
- **Encoding issues**: The script automatically handles UTF-8 and Windows-1250 encodings
