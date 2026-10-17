# Contributing

Thanks for your interest. Bug reports, reader improvements and new language readers are all welcome. Please open an issue before a large change so we can agree on the approach. I can't promise to merge every pull request, but I will respond.

## Development setup

```bash
git clone https://github.com/jakubstuglik/hybrid-code-rag-mcp.git
cd hybrid-code-rag-mcp
uv venv --python 3.12
source .venv/bin/activate            # Windows: .venv\Scripts\activate
uv pip install -r requirements/requirements.txt
uv pip install -r requirements/requirements_dev.txt
```

Unit tests need neither a GPU nor Docker nor network access. Indexing and the MCP server need Docker (Qdrant and TEI); see [docs/installation.md](docs/installation.md).

## Running tests and linters

Run everything from the repository root (`conftest.py` puts the root and `src/` on `sys.path`).

```bash
python -m pytest                                  # src_test/ (testpaths in pytest.ini)
python -m pytest -q tests                         # git overlay tests (throwaway repos in the temp dir)
python -m pytest src_test/shared/readers -q       # reader tests only
python -m pytest src_test/test_config_loader.py   # one module
python -m pytest src_test/ --cov --cov-report=term-missing

ruff check src/shared/readers/kotlin_reader.py    # lint the files you changed
black src/shared/readers/kotlin_reader.py         # format the files you changed
```

The codebase is not yet lint-clean as a whole (`ruff check .` reports existing findings), so please keep the files you touch clean rather than reformatting unrelated code.

If you change chunking, also rebuild an index of a codebase you know and run its retrieval validation suite (`python src/validate_rag.py --config <name>`, see [docs/validation/validation-tests-guide.md](docs/validation/validation-tests-guide.md)) before and after the change. Retrieval quality is the real acceptance test for reader changes.

## Project layout

```
hybrid-code-rag-mcp/
  config.py                    # System-wide defaults (embedding, devices, batching)
  project-configs/             # Your per-project index configs (git-ignored)
  self-index/                  # Config that indexes this repository itself
  src/
    index_rag.py               # Indexing entry point
    rag_mcp.py                 # MCP server entry point
    validate_rag.py            # Retrieval validation runner
    config_loader.py           # Two-layer config loading and validation
    refresh_guard.py           # Cron-safe indexing wrapper
    git_pull_guard.py          # Cron-safe git pull wrapper
    git_pull_all.py            # Simple git pull for all repos
    shared/
      readers/                 # One module per file type + READER_REGISTRY
      embedding.py             # Dense embedding backends (TEI, PyTorch, OpenVINO, OpenAI-compatible)
      reranker.py              # Post-retrieval, intent-aware reranking (generic core)
      rerank_profile.py        # RerankProfile: per-language rules attached to readers
      branch_dedup.py          # Overlay filters, dedup and tombstones
      chunk_pool.py            # Cross-file chunk pooling
      docker_utils.py          # Qdrant and TEI container management
      manifest.py, index_state.py, overlay.py, git_ops.py
      validation/              # Validation framework
    qdrant/vector_store.py     # Qdrant vector store and BM25 sparse encoder
  src_test/                    # Main pytest suite (mirrors src/)
  tests/                       # Git overlay tests
  scripts/                     # Launchers (.bat and .sh)
  docs/                        # User docs, design notes and benchmarks
  requirements/                # base, dev, CUDA, OpenVINO
```

## How to add a reader for a new language

The Kotlin reader (`src/shared/readers/kotlin_reader.py`, added in commit `673a7c7`) is the best template: it reuses the Java chunk conventions, so the reranker needed almost no changes. The Groovy reader follows the same pattern. For a brace-style language with classes and methods, the quickest start is now `StructuredReaderBase` in `src/shared/readers/_structured.py`: it provides the prefix builder, splitting, trivial-method grouping, class summaries/overviews and comment merging, and the C#, Go, PHP and Python readers are short examples built on it ([docs](docs/csharp-go-php-python-chunking.md)). A new reader touches these files:

| File | Change |
|---|---|
| `src/shared/readers/<lang>_reader.py` | New reader class |
| `src/shared/readers/__init__.py` | Import, `READER_REGISTRY` entries, `__all__` |
| `src_test/shared/readers/test_<lang>_reader.py` | Reader tests |
| `src_test/shared/readers/test_readers_init.py` | Add the extensions to `EXPECTED_EXTENSIONS` |
| End of `<lang>_reader.py` | Optional: `RERANK_PROFILE` (file-stem pattern, node types, test paths, declared names); the core `src/shared/reranker.py` needs no change |
| `README.md` | Row in the supported-languages table |

### 1. Get a parser

Check whether [`tree-sitter-language-pack`](https://pypi.org/project/tree-sitter-language-pack/) (already a dependency) has a grammar for the language:

```python
from tree_sitter_language_pack import get_parser
parser = get_parser("kotlin")
tree = parser.parse(source_bytes)
print(tree.root_node)              # inspect node types before writing the reader
```

If there is no usable grammar, a hand-written parser is fine; see `dfm_reader.py` (depth-tracking parser) or the XML readers (`ui_reader.py`, `hbm_reader.py`) that use `xml.etree.ElementTree`. Grammars have gaps: the Kotlin reader descends into `ERROR` nodes inside class bodies and pre-processes one construct the grammar mis-parses (`_join_where_clauses`). Write tests for such cases.

### 2. Implement the reader

Subclass `BaseFileReader` from `_base.py` and implement `load_data(file, extra_info=None) -> List[Document]`. The default `load_nodes()` turns each `Document` into a `TextNode`.

```python
from pathlib import Path
from typing import List, Optional

from llama_index.core import Document
from tree_sitter_language_pack import get_parser

from shared.readers._base import BaseFileReader, get_file_datetime, read_file_with_encoding_and_bytes

_parser = get_parser("mylang")


class MyLangFileReader(BaseFileReader):
    def load_data(self, file: Path, extra_info: Optional[dict] = None) -> List[Document]:
        content, content_bytes = read_file_with_encoding_and_bytes(file)
        if not content.strip():
            return []
        file_datetime = get_file_datetime(file)
        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            # Never drop a file: fall back to one full_file chunk
            return [Document(text=content, metadata={
                "file_path": str(file), "node_type": "full_file",
                "parse_error": str(e), **file_datetime})]
        ...
```

Conventions the rest of the pipeline relies on:

- **Context prefix on every chunk.** Start each chunk with the same header lines as Java and Kotlin, so BM25 and the embedding both see where the code lives:

  ```
  // File: OrderService.kt
  // Package: com.example.orders
  // Class: Outer > Inner > class Inner(...)
  ```

  Omit `// Package:` or `// Class:` when they do not apply. Nested types use the `Outer > Inner` chain. When a long chunk is split, repeat the prefix on every part.
- **Metadata on every `Document`**: `file_path`, `node_type`, `start_line`, `end_line` (1-based), `start_byte`, `end_byte`, plus the `get_file_datetime()` fields. Add `class_name`, `package_name` and `unit_name` (file stem) where they apply. The MCP server prints `TYPE` and `LINES` from these fields.
- **Node types.** Reuse existing names whenever the concept matches: `class_summary` (header plus member signatures, no bodies), `class_overview` (compact overview for large types), `method_declaration`, `constructor_declaration`, `field_declaration`, `enum_constant`, `import_group`, `block_comment`, `method_group` (grouped trivial methods), `full_file`. Oversized chunks get the `_split` suffix with `split_part` / `split_total`. The reranker already knows these names, so "what is X?" queries promote your summaries without any reranker change.
- **Chunk sizes.** Follow the Kotlin/Java constants (`MIN_CHUNK_SIZE`, `MAX_CHUNK_CHARS`, `MAX_SUMMARY_CHARS`, trivial-method grouping) unless you have measurements that say otherwise.

### 3. Register it

```python
# src/shared/readers/__init__.py
from shared.readers.mylang_reader import MyLangFileReader

READER_REGISTRY = {
    ...
    ".ml": MyLangFileReader(),
}
```

Compound extensions such as `.hbm.xml` are checked before the last suffix, so a specialised reader can take over part of a generic extension. Add the class name to `__all__`. Nothing else needs to change for indexing: a project picks the reader up as soon as the extension is listed in its `SOURCE_DIRS` `extensions`.

### 4. Rerank profile (optional)

The reranker core (`src/shared/reranker.py`) is language-neutral. Everything it needs to know about your reader goes into a `RerankProfile` (`src/shared/rerank_profile.py`) attached to the reader class:

```python
# end of src/shared/readers/mylang_reader.py
from shared.rerank_profile import java_style_profile

RERANK_PROFILE = java_style_profile(
    "mylang",
    r"\b([A-Za-z][A-Za-z0-9_]*)\.ml\b",
    test_paths=[r"(?:^|/)test_[^/]*\.ml$", r"_test\.ml$"],
    declaration_names=[r"^let\s+([A-Za-z_][A-Za-z0-9_]*)\b"],
)
MyLangFileReader.rerank_profile = RERANK_PROFILE
```

A profile can declare: file-stem/identifier `target_patterns` (so "what is `OrderService.ml`?" targets that file), `overview_types` / `artifact_overview_types` / `detail_types` / `import_types` for your node types, extra `overview_query_patterns`, and `domains` (query intents such as "report structure" that make one of your chunk types the primary answer). For the query-intent rules it can also declare `test_path_patterns` (test files, demoted unless the query is about tests), `declaration_name_patterns` (names a chunk declares that the generic `def`/`function`/`name(` rules miss, so a query naming `load_items` or `Store::flush` finds the definition), `binding_path_patterns` / `binding_text_patterns` (glue layers such as JNI or C API wrappers) and `is_declaration_chunk` (declaration-only chunks such as headers). `java_style_profile()` covers readers that emit the Java chunk conventions. The generic types (`class_overview`, `class_summary`, `method_group`, comments, `import_group`) need no declaration. All fields and score values are described in [docs/reranker.md](docs/reranker.md).

A profile is only active for projects that index your extension (or list it in `RERANK_PROFILES`), so it cannot change ranking for other languages. Changing a profile is a query-time change: no reindex, but re-run the validation suites of the projects that use the reader.

### 5. Tests

Look at `src_test/shared/readers/test_kotlin_reader.py`. Cover at least:

- registry wiring (`get_reader(Path("x.ml"))` returns your reader);
- the exact context-prefix format, and that it matches the Java prefix for the same names;
- each construct you chunk (classes, nested classes, functions, enums, comments, imports);
- splitting of oversized chunks and trivial-method grouping;
- empty files, syntax errors and grammar gaps (fallback, no exception).

### 6. Document it

Add a row to the table in `README.md` (extensions and how they are parsed), and for a non-trivial grammar a short `docs/<lang>-chunking.md` like [docs/kotlin-chunking.md](docs/kotlin-chunking.md). To index the new file type in an existing project, add the extension to its config and run the indexer (use `--clear` if in doubt). Changing an existing reader's output requires a `--clear` rebuild of affected indexes, so mention it in the PR.

## Pull requests

- Keep changes focused, with tests.
- Run `python -m pytest`, `python -m pytest -q tests` and `ruff check` on the files you changed before opening the PR.
- Do not commit project configs, indexes, logs or model caches (they are git-ignored).
- Describe the retrieval impact if you changed chunking or ranking.
