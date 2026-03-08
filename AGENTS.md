# AGENTS.md - Developer Guidelines for hybrid-code-rag-mcp

## Project Overview

This is a Python RAG (Retrieval Augmented Generation) project that indexes Delphi Pascal source code, SQL schemas, FastReport .fr3 files, and other languages using Qdrant vector store and LlamaIndex. It also supports self-indexing its own source code for AI-assisted development.

**Main entry point:** `index_rag.py`  
**MCP server:** `rag_mcp.py`

## Self-Index (AI-Assisted Development)

This project indexes its own source code so you (the AI agent) can search it via MCP.
The `opencode.json` config automatically starts the MCP server when OpenCode launches.

### Prerequisites

The self-index requires a Qdrant Docker container running on port 6973:

```bash
# Start the self-index Qdrant container (one-time, stays running)
docker run -d --name informica_rag_self -p 6973:6333 -v "./self-index/index_rag_self:/qdrant/storage" qdrant/qdrant:latest
```

### Initial Setup (first time after cloning)

```bash
.venv\Scripts\activate
python index_rag.py --config self-index
```

This creates the vector index in `self-index/index_rag_self/`.

### Reindexing After Changes

**Run incremental refresh after any major code changes:**

```bash
python index_rag.py --config self-index
```

This is incremental -- it only re-embeds changed/new files. Fast for small changes.

### Using the MCP Tool

The `search_self_rag` MCP tool is automatically available in OpenCode sessions.
The `opencode.json` config starts the `self-rag` MCP server (via `start_self_rag.bat`) which:
1. Ensures the Docker container `hybrid-code-rag-mcp-self-db` is running on port 6973
2. Starts `rag_mcp.py --config self-index --transport stdio`
3. Loads the embedding model at startup (~10-15s), then all queries are fast

Use it to search the codebase for relevant context:

```
use the search_self_rag tool to find how config loading works
```

### When to Reindex (AI Agent Rules)

**You (the AI agent) should run `python index_rag.py --config self-index` when:**

1. **No index exists yet** -- the MCP tool returns errors or the `self-index/index_rag_self/` directory is empty/missing
2. **After major code changes** -- you created, deleted, or substantially modified multiple files
3. **Files changed since last index** -- e.g., after a `git pull` or switching branches

The indexer is incremental -- it only re-embeds changed/new files and removes deleted ones. It is fast for small changes, so err on the side of reindexing when in doubt.

### Troubleshooting

- If the MCP server fails, ensure the index has been built (run `python index_rag.py --config self-index`).
- The embedding model loads at server startup (~10-15s). This happens once per OpenCode session.
- The Qdrant container must be running on port 6973. The `start_self_rag.bat` script handles this automatically.

## Build, Lint, and Test Commands

### Python Environment

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows

# Or with uv
uv venv
uv sync
```

### Installing Dependencies

Always use **uv pip** to install dependencies to the virtual environment:

```bash
# Install from requirements.txt
uv pip install -r requirements.txt

# Install a specific package
uv pip install qdrant-client
```

### Running the Indexer

```bash
# Run the main indexing script (uses base config.py)
python index_rag.py

# Run with a config override
python index_rag.py --config self-index
```

### Testing

This project uses **pytest** with **pytest-cov** for unit testing. Tests live in `tests/`.

```bash
# Run all tests
.venv\Scripts\python -m pytest -v --tb=short

# Run a specific test file
.venv\Scripts\python -m pytest tests/test_log.py -v --tb=short

# Run with coverage report
.venv\Scripts\python -m pytest tests/test_log.py --cov --cov-report=term-missing -v --tb=short

# Run a single test
.venv\Scripts\python -m pytest tests/test_log.py::TestLog::test_log_basic_message -v
```

**Important:** Use `--cov` (no module arg) instead of `--cov=shared.log` to avoid a numpy/coverage
instrumentation conflict caused by `shared/__init__.py` importing heavy dependencies.

**Test file conventions:**
- One test file per module: `tests/test_<module>.py`
- One test class per public function/class: `TestConfigure`, `TestLog`, etc.
- Use `import shared.log as log_module` NOT `from shared import log` (avoids triggering `shared/__init__.py`)
- Target 100% line coverage on the module under test

**Multi-agent test cycle:** Use the `test-cycle` skill (`/skill test-cycle`) for automated
test generation, validation, execution, and iteration after code changes.

### Linting and Formatting

Install development dependencies:

```bash
pip install ruff black mypy
```

Run linting:

```bash
ruff check .              # Lint all files
ruff check index_rag.py --fix  # Fix issues

mypy index_rag.py  # Type checking
```

Format code:

```bash
black index_rag.py
```

## Code Style Guidelines

### General Principles

- Follow PEP 8 style guide for Python
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive names for variables, functions, and classes
- **Logging verbosity must never change main algorithm behavior** -- verbose vs non-verbose should only differ in output, never in logic
- **Adhere to DRY (Don't Repeat Yourself)** -- factor out common logic, don't duplicate code paths that only differ in logging

### Imports

```python
# Standard library first
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

# Third-party libraries (alphabetical)
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Document,
)

# Local application imports
from tree_sitter import Parser, Node
```

### Type Hints

- Use type hints for all function parameters and return types
- Use `List`, `Dict`, `Optional` from `typing` module (or modern `list[]` syntax for Python 3.9+)

```python
def process_documents(docs: List[Document]) -> List[TextNode]:
    """Process documents and return text nodes."""
    nodes: List[TextNode] = []
    for doc in docs:
        # ...
    return nodes
```

### Naming Conventions

- **Variables/functions:** snake_case (`file_path`, `get_documents()`)
- **Classes:** PascalCase (`DelphiTreeSitterParser`, `FastReportFR3Parser`)
- **Constants:** UPPER_SNAKE_CASE (`MAX_CHUNK_SIZE`, `DEFAULT_EMBED_MODEL`)
- **Private methods/attributes:** prefix with underscore (`_parse_nodes()`, `_internal_cache`)

### Logging

All output goes through `shared/log.py`. **Never use `print()` directly.**

```python
from shared.log import log, log_raw, log_error, log_warn

log("Starting indexing...")          # [2026-03-06 14:23:05] Starting indexing...
log_raw("=" * 70)                    # ======...  (no timestamp, for tables/separators)
log_error("File not found: x.pas")   # [2026-03-06 14:23:05] [ERROR] File not found: x.pas
log_warn("Skipping empty file")      # [2026-03-06 14:23:05] [WARN] Skipping empty file
```

Guidelines:
- **Operational messages** use `log()` (timestamped) -- progress, status changes, completion
- **Tables and summaries** use `log_raw()` (no timestamp) -- formatting, separators, blank lines
- **Errors** use `log_error()`, **warnings** use `log_warn()`
- **MCP server** calls `configure(stream=sys.stderr)` at startup (required for stdio JSON-RPC transport)
- All output is flushed immediately (important for long indexing runs)
- The only file that legitimately uses `print()` is `shared/log.py` itself

### Error Handling

- Use try/except blocks with specific exception types when possible
- Include informative error messages
- Use `log_warn()` or `log_error()` from `shared.log` for error output

```python
from shared.log import log_warn

try:
    tree = parser_global.parse(bytes(content, "utf8"))
except Exception as e:
    log_warn(f"Tree-sitter parse failed for {file_path}: {e}")
    continue
```

### Docstrings

Use Google-style or NumPy-style docstrings:

```python
class DelphiTreeSitterParser(NodeParser):
    """Semantic chunking for Delphi Pascal using Tree-sitter AST."""

    def _parse_nodes(self, documents: List[Document], **kwargs) -> List[TextNode]:
        """Parse documents into TextNode objects.
        
        Args:
            documents: List of documents to parse.
            **kwargs: Additional keyword arguments.
            
        Returns:
            List of TextNode objects.
        """
        nodes = []
        # ...
        return nodes
```

### Class Structure

- Keep classes focused with single responsibility
- Use inheritance from base classes when applicable
- Use composition over inheritance when appropriate

### Comments

- Use inline comments sparingly
- Use section headers for major code blocks:

```python
# ────────────────────────────────────────────────
# Tree-sitter (using tree-sitter-language-pack)
# ────────────────────────────────────────────────
```

### File Organization

1. Imports (stdlib, third-party, local)
2. Constants/configuration
3. Classes
4. Functions
5. Main execution block (if __name__ == "__main__":)

### Dependencies

Key dependencies (from virtual environment):
- `llama-index` - Core RAG framework
- `qdrant-client` - Qdrant vector database
- `tree-sitter` + `tree-sitter-language-pack` - AST parsing (Pascal, SQL, Python)
- `llama-index-embeddings-huggingface` - Embedding model
- `xml.etree.ElementTree` - Built-in XML parsing
- `mcp` - Model Context Protocol server

### Development Workflow

1. Activate the virtual environment: `.venv\Scripts\activate`
2. Make changes to code files
3. Test syntax: `python -m py_compile index_rag.py`
4. Run the script: `python index_rag.py`
5. **Reindex self-index:** `python index_rag.py --config self-index`

### Common Issues

- **Memory issues:** Reduce embedding batch size or use CPU mode
- **Tree-sitter parse errors:** Check file encoding (UTF-8)

### VS Code Settings (Recommended)

If using VS Code, add to `.vscode/settings.json`:

```json
{
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.analysis.typeCheckingMode": "basic"
}
```
