# AGENTS.md - Developer Guidelines for informica-rag

## Project Overview

This is a Python RAG (Retrieval Augmented Generation) project that indexes Delphi Pascal source code, SQL schemas, and FastReport .fr3 files using Chroma or Qdrant vector store and LlamaIndex.

**Main entry point:** `index_delphi.py`

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
# Run the main indexing script (uses config.py STORE_TYPE setting)
python index_delphi.py
```

### Testing

This project has **no formal test suite**. To run a quick validation:

```bash
# Check syntax and imports
python -m py_compile index_delphi.py

# Run with Python interpreter
python -c "import index_delphi"
```

To add tests in the future, use pytest:

```bash
pytest                          # Run all tests
pytest tests/                   # Run specific test directory
pytest tests/test_file.py       # Run single test file
pytest tests/test_file.py::test_function_name  # Run single test
```

### Linting and Formatting

Install development dependencies:

```bash
pip install ruff black mypy
```

Run linting:

```bash
ruff check .              # Lint all files
ruff check index_delphi.py --fix  # Fix issues

mypy index_delphi.py  # Type checking
```

Format code:

```bash
black index_delphi.py
```

## Code Style Guidelines

### General Principles

- Follow PEP 8 style guide for Python
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive names for variables, functions, and classes

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
from llama_index.vector_stores.chroma import ChromaVectorStore

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

### Error Handling

- Use try/except blocks with specific exception types when possible
- Include informative error messages
- Log errors appropriately (print for simple scripts)

```python
try:
    tree = parser_global.parse(bytes(content, "utf8"))
except Exception as e:
    print(f"Tree-sitter parse failed for {file_path}: {e}")
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
- `chromadb` - Chroma vector database
- `qdrant-client` - Qdrant vector database (alternative)
- `tree-sitter` + `tree-sitter-language-pack` - Pascal AST parsing
- `huggingface-huggingface-embedding` - Embedding model
- `xml.etree.ElementTree` - Built-in XML parsing

### Development Workflow

1. Activate the virtual environment: `.venv\Scripts\activate`
2. Make changes to code files
3. Test syntax: `python -m py_compile index_delphi.py`
4. Run the script: `python index_delphi.py`
5. Verify output in `chroma/` or `qdrant/` directory

### Switching Vector Store

Edit `config.py` to change vector store:
- `STORE_TYPE = "chroma"` - Use Chroma
- `STORE_TYPE = "qdrant"` - Use Qdrant

Path configuration is handled automatically via `MODEL_PATH` in config.py.

### Common Issues

- **Chroma lock errors:** Delete `chroma/index_*_chroma/chroma.sqlite3` if locked
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
