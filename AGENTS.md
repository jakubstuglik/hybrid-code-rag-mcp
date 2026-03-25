# AGENTS.md - Developer Guidelines for hybrid-code-rag-mcp

## Project Overview

This is a Python RAG (Retrieval Augmented Generation) project that indexes source code across multiple languages — Delphi Pascal, Java, JavaScript/TypeScript, Python, SQL (T-SQL and ANSI), plus specialized formats like Hibernate mappings (`.hbm.xml`), JasperReports (`.jrxml`), Delphi Forms (`.dfm`), FastReport (`.fr3`), and Delphi project files (`.dproj`) — using Qdrant vector store and LlamaIndex. It also supports self-indexing its own source code for AI-assisted development.

**Main entry point:** `src/index_rag.py`  
**MCP server:** `src/rag_mcp.py`  
**Platform support:** All code MUST work on both **Windows** and **Linux**. Use cross-platform
libraries (e.g. `psutil`, `pathlib`), avoid OS-specific APIs without fallbacks, and test
assumptions about paths, subprocess commands, and system APIs on both platforms.

## Tool Name Corrections

Record corrections made to AGENTS.md when tool names in documentation don't match actual available tools:

| Date | Documentation Said | Actual Tool Name | Notes |
|------|---------------------|------------------|-------|
| 2026-03-11 | `search_self_rag` | `self-rag_search_self_rag` | MCP server prefix required (`self-rag_` + function name) |

## Self-Index — MANDATORY Workflow for AI Agents

This project indexes its own source code into a Qdrant vector store. You have a
`self-rag_search_self_rag` MCP tool available **right now** in this session. It is already
running — zero startup cost to you. **Use it.**

### RULE 0: Correct Tool Naming

When calling MCP tools from OpenCode, the tool name follows the pattern:
`<mcp-server-name>_<tool-function-name>`. The MCP server is registered as `self-rag`
in `opencode.json`, so the correct tool name is `self-rag_search_self_rag`.

**If you encounter a tool name mismatch between AGENTS.md and the actual available tools:**
1. Note the correct name from the error message ("Available tools: ...")
2. Fix AGENTS.md to use the correct name
3. Add a note about this to the "Tool Name Corrections" section below

### Common Pitfalls — Do NOT Repeat

**Windows paths in bash commands:**
- ❌ `.venv\Scripts\activate` — backslashes don't work in bash
- ✅ `.venv/Scripts/activate` — use forward slashes in bash
- ✅ `.\.venv\Scripts\python.exe` — only use backslashes in cmd.exe or PowerShell

**Chaining commands on Windows:**
- ❌ `cd foo && bar` — cd with && doesn't work reliably in bash
- ✅ Use `workdir` parameter in Bash tool instead: `bash(..., workdir="C:/path/to/foo", command="bar")`
- ✅ Or use `cd /d foo && bar` in cmd.exe

**Always verify paths before running:**
- Use glob to confirm file exists before editing or running scripts
- Don't assume directory structure — check with ls/glob first

**Docker GPU selection on Windows/WDDM:**
- ❌ `--gpus "device=1"` alone — Docker Desktop on Windows **ignores** `DeviceIDs` and always exposes all GPUs to the container
- ✅ Also pass `-e CUDA_VISIBLE_DEVICES=1` — the CUDA runtime inside the container then only sees the intended GPU
- This is handled automatically in `_create_tei_container()` in `shared/docker_utils.py`
- To verify: run `nvidia-smi` from **the host** after triggering an embedding request and confirm VRAM is consumed on the correct GPU

**When you make a mistake like this more than once:**
1. Add a note to this "Common Pitfalls" section in AGENTS.md
2. Remember it for future sessions

### RULE 1: Use `self-rag_search_self_rag` FIRST for any exploratory question

Before reaching for grep, glob, or Task(explore), ask yourself: "Am I looking for
something conceptual — how something works, where something is used, what a module does?"
If yes, **call `self-rag_search_self_rag` first.** It returns semantically relevant chunks with
context prefixes, class summaries, and function bodies — not just line matches.

**Use `self-rag_search_self_rag` for:**
- "How does config loading work?"
- "What does `get_embed_model` do?"
- "Where is the OpenVINO embedding branch?"
- "How are Pascal files chunked?"
- "What node_types does the reranker boost?"
- Any question about architecture, design, or how modules interact

**Use grep/glob ONLY for:**
- Exact string matches ("find all files importing `shared.log`")
- File path lookups ("find test files for the manifest module")
- Needle-in-haystack searches for a specific identifier name

**Fallback:** If `self-rag_search_self_rag` doesn't return useful results for your query,
fall back to grep/glob/Task(explore). The index doesn't cover everything perfectly —
use whatever tool gets you the answer. The rule is to **try `self-rag_search_self_rag` first**,
not to avoid other tools entirely.

**Always pass the current branch** using `git branch --show-current`. Omit only when on `master`.

**Example — do this:**
```
self-rag_search_self_rag("how does validate_device_config work", branch="feature/my-branch")
self-rag_search_self_rag("OpenVINO embedding integration", branch="feature/my-branch")
self-rag_search_self_rag("manifest change detection hash mtime", branch="feature/my-branch")
```

**Not this:**
```
grep for "validate_device_config" across all files     ← gives you call sites, not understanding
Task(explore) to "find how config loading works"       ← slower, uses more context, less relevant
```

### RULE 2: Reindex after you modify code

**Run this after you create, delete, or substantially modify files:**

```bash
.venv/bin/python src/index_rag.py --config self-index --yes --log-to-file --collect-perf-stats
```

**Always include `--log-to-file` and `--collect-perf-stats`** on every indexing run
(self-index and project configs). This preserves logs and performance data for
diagnostics. Never run `index_rag.py` without these flags.

The indexer is incremental — it only re-embeds changed/new files. Takes seconds for
small changes. **Do it. Do not skip this.** If you modified 3+ files or created a new
module, reindex before your next `self-rag_search_self_rag` call.

**When to reindex:**
- You created a new file (test file, module, config)
- You substantially modified a function signature or added new functions
- You deleted files
- After `git pull` or branch switch
- When in doubt — just run it, it's fast

**When you can skip reindex:**
- You only changed comments or docstrings in one file
- You only changed values (not structure) in config files

### Prerequisites (one-time setup)

Docker Desktop must be installed and `docker` must be in PATH. The Qdrant container
is auto-managed — you do **not** need to create it manually. Just run:

```bash
.venv/Scripts/activate
python src/index_rag.py --config self-index --yes
```

This will automatically create the `qdrant-self_rag_index` container on port 6973,
mount the volume from `self-index/qdrant/index_rag_self`, and build the initial index.

### How it works (background)

The `opencode.json` config starts the `self-rag` MCP server (via `scripts\start_self_rag.bat`)
automatically when OpenCode launches. It:
1. Calls `ensure_qdrant_running(cfg)` which auto-creates/starts the Docker container
2. Starts `src/rag_mcp.py --config self-index --transport stdio`
3. Loads the embedding model once at startup

The `self-rag_search_self_rag` tool is then available for the entire session with no per-call
overhead. There is no reason to avoid using it.

### Troubleshooting

- If `self-rag_search_self_rag` returns errors, the index may not be built yet. Run `python src/index_rag.py --config self-index --yes`.
- Docker must be running and `docker` must be in PATH. The container is auto-managed.
- Container name: `qdrant-self_rag_index` (port 6973). Check with `docker ps`.

## Build, Lint, and Test Commands

### Python Environment

```bash
# Activate virtual environment
.venv/Scripts/activate  # Windows

# Or with uv
uv venv
uv sync
```

### Installing Dependencies

Always use **uv pip** to install dependencies to the virtual environment:

```bash
# Install from requirements.txt
uv pip install -r requirements/requirements.txt

# Install a specific package
uv pip install qdrant-client
```

### Running the Indexer

```bash
# Run the main indexing script (uses base config.py)
python src/index_rag.py

# Run with a config override
python src/index_rag.py --config self-index
```

### Cron Guard Scripts

Two wrapper scripts provide cron-safe operation with concurrency guards:

**`src/refresh_guard.py`** — prevents concurrent `index_rag.py` runs:
- Skips this run if a prior one is still active (skip counter survives across cron invocations)
- Kills the stale process after 3 consecutive skips
- State stored in `refresh_guard_state.json` next to the Qdrant index

```bash
python src/refresh_guard.py --config config_informica_tei_jinaai [--yes]
```

**`src/git_pull_guard.py`** — pulls all `git_repo` sources before indexing:
- Runs `git fetch --all --prune` on every `git_repo` entry in the config
- Stashes uncommitted changes, pulls the current branch, restores stash
- Only pulls if on `main_branch` or a configured feature branch; skips detached HEAD
- Parallel pull (up to 4 workers) across all repos
- Same skip/kill guard as `refresh_guard.py`

```bash
python src/git_pull_guard.py --config config_informica_tei_jinaai
```

**Recommended crontab order** (every hour):
```bash
0 * * * * cd /home/rag/hybrid-code-rag-mcp && \
    .venv/bin/python src/git_pull_guard.py --config config_informica_tei_jinaai >> /home/rag/git_pull.log 2>&1 && \
    .venv/bin/python src/refresh_guard.py --config config_informica_tei_jinaai --yes >> /home/rag/index_refresh.log 2>&1
```

### Testing

This project uses **pytest** with **pytest-cov** for unit testing. Tests live in `src_test/`.

```bash
# Run all tests
.venv\Scripts\python -m pytest -v --tb=short

# Run a specific test file
.venv\Scripts\python -m pytest src_test/test_log.py -v --tb=short

# Run with coverage report
.venv\Scripts\python -m pytest src_test/test_log.py --cov --cov-report=term-missing -v --tb=short

# Run a single test
.venv\Scripts\python -m pytest src_test/test_log.py::TestLog::test_log_basic_message -v
```

**Important:** Use `--cov` (no module arg) instead of `--cov=shared.log` to avoid a numpy/coverage
instrumentation conflict caused by `shared/__init__.py` importing heavy dependencies.

**Test file conventions:**
- One test file per module: `src_test/test_<module>.py`
- One test class per public function/class: `TestConfigure`, `TestLog`, etc.
- Use `import shared.log as log_module` NOT `from shared import log` (avoids triggering `shared/__init__.py`)
- Target 100% line coverage on the module under test

**Multi-agent test cycle:** Use the `test-cycle` skill (`/skill test-cycle`) for automated
test generation, validation, execution, and iteration after code changes.

### Linting and Formatting

Install development dependencies (includes pytest, ruff, black, mypy):

```bash
uv pip install -r requirements/requirements_dev.txt
```

Run linting:

```bash
ruff check .              # Lint all files
ruff check src/index_rag.py --fix  # Fix issues

mypy src/index_rag.py  # Type checking
```

Format code:

```bash
black src/index_rag.py
```

## Code Style Guidelines

### General Principles

- Follow PEP 8 style guide for Python
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive names for variables, functions, and classes
- **Logging verbosity must never change main algorithm behavior** -- verbose vs non-verbose should only differ in output, never in logic
- **Adhere to DRY (Don't Repeat Yourself)** -- factor out common logic, don't duplicate code paths that only differ in logging

### AI Agent: Honesty About Fundamental Limitations

**CRITICAL RULE:** When the user wants a specific outcome (e.g., "all chunks must be meaningfully searchable") but you know that outcome is **impossible with the current model/architecture**, say so immediately and clearly. Do NOT propose workarounds that only mask the symptom without explaining that the root cause is a fundamental limitation.

Specifically:
- If a model cannot produce meaningful embeddings for certain inputs (e.g., jinaai/jina-embeddings-v2-base-code produces near-zero activations for highly repetitive code), **state this upfront** as a model limitation. Do not lead the user through precision changes (float16 vs float32) or other parameter tweaks that cannot fix a model capacity problem.
- Float16 vs float32 upcasting: if model weights are stored as float16, loading them in float32 only prevents arithmetic underflow in intermediate values -- it does NOT improve the model's ability to understand or differentiate the input. The embeddings for degenerate inputs will be noise either way.
- Always distinguish between **fixing errors/crashes** (safety nets like sanitize + skip are valid) and **improving search quality** (requires a different model, different chunking strategy, or accepting that some inputs are outside the model's capability).
- If hybrid mode (dense + sparse) provides a viable fallback (e.g., BM25 keyword matching works for chunks where dense embeddings fail), explain this tradeoff clearly so the user can make an informed decision.

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
- `tree-sitter` + `tree-sitter-language-pack` - AST parsing (Pascal, SQL, Python, Java, JavaScript, TypeScript)
- `llama-index-embeddings-huggingface` - Embedding model
- `xml.etree.ElementTree` - Built-in XML parsing (HBM, JRXML, DPROJ, FR3)
- `mcp` - Model Context Protocol server

### Development Workflow

1. Activate the virtual environment: `.venv/Scripts/activate`
2. Make changes to code files
3. Test syntax: `python -m py_compile src/index_rag.py`
4. Run the script: `python src/index_rag.py`
5. **Reindex self-index:** `python src/index_rag.py --config self-index`

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

---

## Completed: Chunking Strategy Overhaul

All readers have been redesigned and validated through 10 rounds of test-index evaluation,
achieving **14/14 PASS** on a comprehensive query suite. The embedding model bug was fixed
(trust_remote_code=True), and a post-retrieval reranker handles overview query promotion.

### Design Goal (Achieved)

Chunks serve **two AI agent use cases simultaneously**:

1. **Big picture / understanding** — "What does TdmMain do? What classes are in emar105?"
2. **Precise code location** — "Where is PrepareDataSet? Where is REPORT_TYPE_PUNCTUALITY_RIDES?"

### What Was Done

#### 1. Pascal Reader (`shared/readers/pascal_reader.py`, ~1005 lines)

Fully redesigned from 235 lines. All original drawbacks (P1-P5) are fixed:

- **Context prefix on all chunks** — every chunk starts with `// Unit: <filename>` and
  class-member chunks add `// Class: TClassName = class(TParent)`. Fixes P1.
- **Class summary chunks** — `class_summary` node_type emits the class header + all
  interface declarations as one chunk. Enables "What is TdmMain?" queries.
- **Class overview with natural-language summary** — `class_overview` node_type includes a
  generated sentence like "TdmMain is a Delphi class inheriting from TDataModule with
  150 published members, 60 private members, and 30 public members."
- **Trivial method grouping** — consecutive trivial methods (≤5 lines each, ≥3 consecutive)
  are merged into `method_group` chunks. Collapses 500 getter/setter chunks into ~20. Fixes P2/P3.
- **Uses clause captured** — `declUses` node_type for both interface and implementation uses. Fixes P5.
- **Commented-out code detection** — `_is_commented_out_code()` identifies comment blocks that
  are actually disabled code vs documentation. Suppressed inside classes (still in class_summary).
- **Tiny declSection suppression** — small visibility sections inside classes with a class_summary
  are not emitted as standalone chunks (content is in the class_summary already).
- **Class name resolution** — method implementations are matched to their owning class via
  `genericDot > identifier` pattern in the Tree-sitter AST.
- **Metadata**: `class_name`, `unit_name`, `node_type`, `line_number`, `byte_start`, `byte_end`,
  `file_datetime`, `file_path` on every chunk.
- **164 tests** in `src_test/shared/readers/test_pascal_reader.py`.

#### 2. T-SQL Chunker (`shared/readers/tsql_chunker.py`, 972 lines — NEW)

Entirely new module replacing the broken tree-sitter SQL fallback:

- **Line-based heuristic parser** for T-SQL (Microsoft SQL Server) syntax.
- **GO batch splitting** — splits on `^GO$` batch separators.
- **Object detection** — recognizes CREATE PROCEDURE/FUNCTION/TRIGGER/VIEW/TABLE, ALTER, DROP.
- **Header + body splitting** — procedure signature with parameters becomes `procedure_header`,
  body sections become `procedure_body` chunks.
- **Dynamic SQL grouping** — consecutive `SET @Sql = @Sql + ...` lines kept together.
- **Context prefix** — every chunk starts with `-- Procedure: [dbo].[ProcName]` and parameters.
- **Metadata**: `object_name`, `object_type`, `parameters` on all chunks.
- **125 tests** in `src_test/shared/readers/test_tsql_chunker.py`.

#### 3. SQL Reader (`shared/readers/sql_reader.py`, ~175 lines)

Updated `_fallback_split()` to call `chunk_tsql()` from the new T-SQL chunker instead of
arbitrary `TokenTextSplitter` splitting. Tree-sitter AST path still works for ANSI SQL.
Added `object_name`/`object_type` metadata.

#### 4. DFM Reader (`shared/readers/dfm_reader.py`, ~460 lines)

Fully rewritten from 142 lines:

- **Recursive descent parser** — proper nesting-aware `object`/`end` tracking. Fixes D1.
- **Form header chunk** — `dfm_form_header` with root object properties (no children).
- **Small sibling grouping** — consecutive small same-type components merged into
  `dfm_object_group` chunks. Fixes D2.
- **Context prefix** — `// Form: TfrmMain (MainTurdus.dfm)` on all chunks.
- **Collection syntax support** — `<item>` / `</item>` and `item` / `end` blocks don't
  prematurely close parent objects.
- **Metadata**: `class_name` (form type), `unit_name` (file stem), form info.
- **58 tests** in `src_test/shared/readers/test_dfm_reader.py`.

#### 5. Python Reader (`shared/readers/python_reader.py`, ~360 lines)

Fully rewritten from 108 lines. All drawbacks (Y1-Y3) fixed:

- **Leaf/container pattern** — same as Pascal reader. Classes with methods recurse;
  standalone functions are leaf nodes. Fixes Y1 duplication.
- **MAX_CHUNK_CHARS + TokenTextSplitter** — oversized chunks split with `_split` suffix. Fixes Y2.
- **MIN_CHUNK_SIZE enforced** — tiny assignments not emitted standalone. Fixes Y3.
- **Context prefix** — `# Module: <filename>` and `# Class: ClassName` on class members.
- **Metadata**: `module_name`, `unit_name`, `class_name` on all chunks.
- **91 tests** in `src_test/shared/readers/test_python_reader.py`.

#### 6. Java Reader (`shared/readers/java_reader.py`, ~996 lines — NEW)

Tree-sitter AST-based Java reader with full support for classes, interfaces, enums, and records:

- **Leaf/container pattern** — same as Pascal/Python readers. Classes with methods recurse;
  standalone functions are leaf nodes. Eliminates content duplication.
- **Class overview with natural-language summary** — `class_overview` node_type includes a
  generated sentence like "PaymentService is a Java class with 12 methods and 5 fields."
- **Import grouping** — consecutive import statements merged into `import_group` chunks
  instead of one chunk per import line.
- **Annotation preservation** — annotations (`@Override`, `@Transactional`, etc.) are kept
  with their associated declarations.
- **Enum body handling** — methods and fields inside `enum_body_declarations` are correctly
  extracted (not confused with enum constants).
- **Context prefix** — `// File: <filename>` and `// Class: ClassName` on class members.
- **Trivial method grouping** — consecutive trivial methods (≤5 lines) merged into
  `method_group` chunks, same threshold as Pascal reader.
- **Metadata**: `class_name`, `unit_name`, `node_type`, `line_number`, `file_path` on every chunk.
- **87 tests** in `src_test/shared/readers/test_java_reader.py`.

#### 7. JavaScript/TypeScript Reader (`shared/readers/js_reader.py`, ~750 lines — NEW)

Tree-sitter AST-based reader supporting both JavaScript and TypeScript:

- **Dual grammar support** — uses `javascript` grammar for `.js` files and `typescript`
  grammar for `.ts`/`.tsx` files. Language auto-detected from file extension.
- **JavaScript patterns**: IIFE (`(function() {...})();`), namespace-object
  (`var Foo = { method: function() {...} }`), prototype-based OOP
  (`Foo.prototype.bar = function() {...}`), revealing module pattern.
- **TypeScript patterns**: `interface_declaration`, `type_alias_declaration`,
  `enum_declaration`, ES6 `export_statement` unwrapping.
- **Export unwrapping** — `export_statement` nodes that wrap a declaration are unwrapped
  to extract the inner declaration (class, function, interface, etc.).
- **Trivial function grouping** — consecutive small functions merged into `function_group`
  chunks.
- **Context prefix** — `// File: <filename>` and `// Class: ClassName` on class members.
- **Metadata**: `class_name`, `unit_name`, `node_type`, `line_number`, `file_path` on every chunk.
- **90 tests** in `src_test/shared/readers/test_js_reader.py`.

#### 8. Hibernate Mapping Reader (`shared/readers/hbm_reader.py`, ~477 lines — NEW)

XML parser for Hibernate `.hbm.xml` mapping files:

- **Entity overview chunk** — `hbm_entity_overview` node_type produces a structured
  natural-language overview: class name, table, discriminator, ID strategy, all properties,
  many-to-one/one-to-many/set associations.
- **Column/property extraction** — all `<property>`, `<many-to-one>`, `<one-to-many>`,
  `<set>`, `<bag>`, `<list>`, `<map>`, `<component>` elements are parsed.
- **Composite ID support** — `<composite-id>` with `<key-property>` and `<key-many-to-one>`
  elements are correctly handled.
- **Inheritance mapping** — `<discriminator>` and `<subclass>` elements are detected.
- **Context prefix** — `<!-- Hibernate Mapping: com.package.ClassName (filename.hbm.xml) -->`
- **Metadata**: `class_name`, `unit_name`, `node_type`, `table_name` on every chunk.
- **76 tests** in `src_test/shared/readers/test_hbm_reader.py`.

#### 9. JasperReports Reader (`shared/readers/jrxml_reader.py`, ~325 lines — NEW)

XML parser for JasperReports `.jrxml` report definition files:

- **Report overview chunk** — `jrxml_report_overview` node_type with report name, page size,
  parameters, fields, variables, groups, and data source info.
- **Expression chunks** — `jrxml_expressions` for reports with many expressions that exceed
  the overview chunk size limit.
- **Parameter/field/variable extraction** — all `<parameter>`, `<field>`, and `<variable>`
  elements with their types and expressions.
- **Context prefix** — `<!-- JasperReport: ReportName (filename.jrxml) -->`
- **Metadata**: `unit_name`, `node_type`, `report_name` on every chunk.
- **63 tests** in `src_test/shared/readers/test_jrxml_reader.py`.

#### 10. Post-Retrieval Reranker (`shared/reranker.py`, ~395 lines — NEW)

New module that fixes BM25 saturation and dense embedding dilution for overview queries:

- **Query intent detection** — `is_overview_query()` with 18 regex patterns (what is, describe,
  explain, what classes, how does X work, form components, etc.).
- **Over-fetch strategy** — `OVERFETCH_MULTIPLIER = 5` fetches 5x candidates for overview queries,
  then trims after reranking. This surfaces overview chunks that raw hybrid search placed at
  position 30-40.
- **Target identifier extraction** — Pascal class names (T-prefixed), .pas file stems, known
  file stems (emar105, MainDM, etc.), SQL procedure names.
- **Score adjustments** (overview queries only):
  - `+0.50` for primary overview types (class_overview, class_summary, class_summary_split)
  - `+0.25` for other overview types (dfm_form_header, procedure_header, function_header, etc.)
  - `+0.15` for chunks matching the target file/class
  - `-0.20` for overview chunks from non-target files (cross-file interlopers)
  - `-0.30` for comment chunks from non-target files
  - `-0.05` for detail types (defProc, method_group, declSection, etc.)
- Non-overview queries pass through unchanged.
- Integrated into `src/rag_mcp.py` and `query_test_index.py`.
- **265 tests** in `src_test/shared/test_reranker.py`, 100% line coverage.

#### 11. Embedding Model Fix

- **Root cause**: `trust_remote_code=False` (LlamaIndex default) caused Jina's custom
  `JinaBertModel` to load as generic `BertModel` with random weights. All embeddings were noise.
- **Fix**: Added `trust_remote_code=True` to `get_embed_model()` in `shared/embedding.py`.
- **Dependency fix**: Downgraded `transformers` 5.2.0 → 4.46.3, `huggingface-hub` 1.5.0 → 0.36.2,
  `tokenizers` 0.22.2 → 0.20.3 for Jina compatibility.
- **Batch sizes reduced**: DENSE 128→32, SPARSE 64→32, MAX_TOKENS 40000→16000 (working model
  uses more VRAM).

#### 12. Cross-Cutting

- **[X1] Context prefix** — implemented on all readers (Pascal, SQL, DFM, Python, Java, JS/TS, HBM, JRXML).
- **[X2] Metadata fields** — `class_name`, `unit_name`, `object_name` on all readers.
  Used by reranker for target matching.
- **[X3] Deduplication** — Python reader leaf/container pattern eliminates duplication.
  Pascal reader class_summary subsumes tiny declSections. Java/JS readers use the same
  leaf/container approach.

### Evaluation Results (Round 10 — Final)

| Q# | Query | Result | Top chunk |
|----|-------|--------|-----------|
| 1 | What is TdmMain? | PASS | class_summary_split from MainDM.pas at #2 |
| 2 | Classes in emar105? | PASS | class_summary at #1 |
| 3 | What is TfrmMainTurdus? | PASS | class_overview at #2 |
| 4 | Splash form | PASS | dfm_form_header at #1 |
| 5 | REPORT_TYPE_PUNCTUALITY_RIDES | PASS | Exact match at #1 |
| 6 | PrepareDataSet | PASS | Implementation at #1 |
| 7 | OpenConnection | PASS | Implementation at #1, class_overview at #3 |
| 8 | SLS_ReliefExport_Bilety_Get | PASS | procedure_header at #2 |
| 9 | TCK_FarePrice_GetPriceForXDesignation | PASS | function_header at #1 |
| 10 | GetCardSerialNumber | PASS | method_group at #3 |
| 11 | uses clause MainDM | PASS | declUses at #1 |
| 12 | TClientDataSet cdsStoredProc | PASS | DFM group at #1 |
| 13 | MainTurdus form components | PASS | dfm_form_header at #1 |
| 14 | SFTP frame components | PASS | dfm_form_header at #1 |

**14 PASS, 0 PARTIAL, 0 FAIL** with `HYBRID_ALPHA = 0.5`.

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| `shared/reranker.py` | 337 | 100% line coverage |
| `shared/readers/pascal_reader.py` | 164 | Integration + unit |
| `shared/readers/tsql_chunker.py` | 125 | Unit |
| `shared/readers/python_reader.py` | 91 | Integration + unit |
| `shared/readers/java_reader.py` | 87 | Integration + unit |
| `shared/readers/js_reader.py` | 90 | Integration + unit |
| `shared/readers/hbm_reader.py` | 76 | Integration + unit |
| `shared/readers/jrxml_reader.py` | 63 | Integration + unit |
| `shared/vram_cap.py` | 85 | 98% line coverage |
| `config_loader.py` | 78 | Unit + integration |
| `shared/readers/fr3_reader.py` | 74 | Integration + unit |
| `shared/docker_utils.py` | 65 | Unit (mocked subprocess) |
| `shared/readers/dfm_reader.py` | 58 | Integration + unit |
| `shared/readers/dproj_reader.py` | 49 | Integration + unit |
| `shared/qdrant_client.py` | 45 | 100% line coverage |
| Other test files | 329 | Various |
| `shared/validation/` (models, loader, runner, output) | 103 | Unit |
| **Total** | **2219** | All passing |

### Remaining Work

- **Chunk quality metrics** — not yet implemented (diagnostic tooling, P3).
- **TEI Intel XPU support** — Phase 2 (see `docs/features/tei-batch-saturation/tei-intel-xpu.md`).

---

## Completed: TEI (Text Embeddings Inference) Integration

HuggingFace Text Embeddings Inference (TEI) was integrated as an alternative embedding
backend.  TEI uses Candle (Rust) inference inside a Docker container, replacing the
Python-process PyTorch model loading.  Dense embeddings are served via HTTP; sparse
BM25 remains local regardless.

### Why TEI

| Metric | PyTorch GPU | TEI GPU |
|--------|------------|---------|
| Embedding speed | 87.4 min | **19.4 min** (4.5x faster) |
| Peak VRAM | 7.9 GB | **2.4 GB** (3.3x less) |
| Validation score | 88.5% | **89.1%** |

TEI produces slightly different vectors than PyTorch (Candle vs PyTorch inference engines).
The vectors are **incompatible** — mixing them in the same collection degrades search quality.

### Architecture

- **`shared/embedding.py`** — `TEIEmbedding(BaseEmbedding)` class (line ~22). LlamaIndex-
  compatible wrapper that calls the TEI HTTP endpoint.  `get_embed_model()` routes to
  TEIEmbedding when `USE_TEI=True`, otherwise HuggingFaceEmbedding (PyTorch).
- **`shared/docker_utils.py`** — `ensure_tei_running(cfg)` auto-manages the TEI Docker
  container (create/start/health-check), analogous to `ensure_qdrant_running()`.
  `_detect_tei_image()` auto-selects NVIDIA CUDA or CPU Docker image.
- **Provenance tracking** — `shared/embedding.py` stores `embedding_provenance` in Qdrant
  collection metadata (`"tei"` or `"pytorch"`).  On query, `check_provenance_for_query()`
  warns if the MCP server's backend doesn't match what was used to build the index.
  On indexing, a mismatch triggers a hard error requiring `--clear`.

### Config Parameters (section 6b in `config.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `USE_TEI` | `False` | Enable TEI backend for dense embeddings |
| `TEI_URL` | `None` | TEI server URL (auto-derived from port when None) |
| `TEI_DOCKER_PORT` | `8090` | Host port for TEI Docker container |
| `TEI_DTYPE` | `"float16"` | TEI inference dtype (float16 or float32) |
| `TEI_GPU` | `"auto"` | GPU selection: `"auto"` (best free VRAM), `"0"`/`"1"` (specific index), `"cpu"` |
| `TEI_DOCKER_IMAGE` | `None` | Docker image override (auto-detected from selected GPU's CC when None) |
| `TEI_MODEL_DIR` | `None` | Model cache mount dir (auto-derived when None) |
| `EMBED_QUERY_PREFIX` | `None` | Prefix for query text (model-specific, e.g. Nomic) |
| `EMBED_TEXT_PREFIX` | `None` | Prefix for document text |

### PyTorch Device Selection (section 6 in `config.py`)

| Parameter | Default | Accepted Values |
|-----------|---------|-----------------|
| `INDEX_EMBED_DEVICE` | `"auto"` | `"auto"`, `"cuda"` (alias for auto), `"0"`, `"1"`, `"cuda:N"`, `"cpu"` |
| `MCP_EMBED_DEVICE` | `"cpu"` | same as above |

`"auto"` / `"cuda"` pick the GPU with the most free VRAM via nvidia-smi at startup.
On single-GPU systems this is equivalent to `"cuda:0"`.  On multi-GPU systems it
avoids landing on the wrong device.  Bare integer strings like `"1"` map to `"cuda:1"`.

### TEI GPU vs CPU

- **GPU** (default, `TEI_GPU="auto"`): picks the GPU with the most free VRAM, selects
  the matching CUDA Docker image by compute capability.  `TEI_DTYPE="float16"`.
  ~117 chunks/sec.  On multi-GPU systems, `"auto"` avoids the wrong GPU automatically.
- **Specific GPU** (`TEI_GPU="1"`): pins TEI to GPU index 1; useful when you want to
  reserve GPU 0 for other work.
- **CPU** (`TEI_GPU="cpu"`): no GPU passthrough, uses CPU Docker image.
  `TEI_DTYPE="float32"` (required — no fp16 HW acceleration on CPU).
  ~2.4 chunks/sec (49x slower).  Also set `INDEX_EMBED_DEVICE="cpu"` and
  `MCP_EMBED_DEVICE="cpu"` so sparse BM25 also runs on CPU.

TEI runs on ONE GPU only — no multi-GPU model parallelism.  `TEI_GPU="auto"` is the
recommended default: it queries nvidia-smi free VRAM at container start time and
passes `--gpus "device=N"` to Docker, so TEI sees only the chosen GPU as device 0.

TEI GPU and TEI CPU produce compatible vectors (same `"tei"` provenance family).

### Docker Container Management

TEI containers are auto-managed alongside Qdrant containers:
- Container name: `tei-{model_name}` (e.g. `tei-jinaai-jina-embeddings-v2-base-code`)
- GPU containers use `--gpus "device=N"` (specific GPU); CPU containers skip the flag
- Health check: `GET /health` endpoint with 120s timeout
- Model cache: mounted from `{BASE_PATH}/tei_model_cache` (persistent across restarts)

### Project Config: `config_informica_tei_jinaai`

The production TEI config lives in `project-configs/config_informica_tei_jinaai/config.py`.
Uses the same Informica sources as `config_informica` but with TEI backend on Qdrant
port 6340 and TEI port 8090.  Contains a commented-out CPU config block that enables
full CPU mode (TEI CPU + BM25 CPU + MCP CPU) when uncommented.

### Multi-Model Benchmark Results (2026-03-20)

Full benchmark report: `docs/features/tei-multimodel-benchmark/benchmark-tei-multimodel-2026-03-20.md`

| Model | Backend | Score | Embed Time | Peak VRAM |
|-------|---------|------:|----------:|----------:|
| **Jina v2 base code** | **TEI GPU** | **89.1%** | **19.4 min** | **2.4 GB** |
| Jina v2 base code | PyTorch GPU | 88.5% | 87.4 min | 7.9 GB |
| BAAI/bge-m3 | TEI GPU | 84.6% | 27.3 min | 3.3 GB |
| Qwen3-0.6B | TEI GPU | 83.3% | 37.2 min | 3.6 GB |
| embeddinggemma-300m | TEI GPU | 82.7% | 72.9 min | 5.4 GB |
| nomic-embed-v2-moe | TEI GPU | 80.8% | 68.3 min | 2.8 GB |

Jina v2 base code via TEI remains the recommended model.  Non-Jina benchmark configs
were cleaned up after testing.

---

## Completed: Cross-File Chunk Pooling (TEI Batch Saturation)

The indexing loop was refactored to pool chunks from multiple files before embedding,
eliminating per-file GPU starvation and TEI padding waste.  Phases 1 and 2 of TODO #11.

Phase 2 added double-buffered upsert: Qdrant upsert I/O of pool N runs on a background
thread while pool N+1 is being embedded, eliminating GPU idle time between flushes.

Chunk histograms are branch-aware: `chunk_histogram.json` for main branch,
`chunk_histogram_branch_<name>.json` for overlays.  The `--calculate-histogram` flag
generates histograms without embedding or Qdrant.

**Design document:** `docs/features/tei-batch-saturation/design.md`
**Implementation report:** `docs/features/tei-batch-saturation/implementation-report.md`
**Branch:** `feature/tei-batch-saturation`

### Results

| Metric | Before (per-file) | Phase 1 (pooling) | Phase 2 (double-buffer) |
|--------|-------------------|-------------------|------------------------|
| Total indexing time | 26.3 min | 20.4 min | ~16 min (estimated) |
| Avg GPU utilization | 28.3% | 38.5% | ~55% (estimated) |
| Median GPU utilization | 23% | 39% | ~55% (estimated) |
| Validation score | 89.1% | 89.1% | unchanged |

### Architecture

- **`shared/chunk_pool.py`** — `ChunkPool` class accumulates `FileEntry` objects (nodes,
  IDs, metadata) from multiple files. `collect()` gathers all texts; `distribute_results()`
  maps embeddings back to per-file groups after cross-file batch embedding.
  `ChunkHistogram` collects char/token length distributions, saved to `chunk_histogram.json`
  (main branch) or `chunk_histogram_branch_<name>.json` (overlays).

- **`_flush_pool()` in `index_rag.py`** — Phase 2 double-buffered orchestration:
  1. `_drain_pending_upsert()` — wait for previous pool's background upsert to finish
  2. Dense embedding (main thread, GPU-bound critical path)
  3. Sparse BM25 embedding (main thread, CPU-bound)
  4. Build per-file upsert work items (main thread, CPU)
  5. Submit upsert to background thread via `ThreadPoolExecutor`
  6. Main thread returns immediately to fill next pool

  Pool flushes when `EMBED_POOL_SIZE` (512) chunks or `EMBED_POOL_MAX_FILES` (150) files
  are accumulated, or at end of input.

- **`_do_background_upsert()` in `index_rag.py`** — runs on background thread. Upserts
  per-file to Qdrant, updates manifest entries, returns counter deltas.  All log messages
  prefixed with `[upsert-worker]` for interleaved log disambiguation.

- **`_drain_pending_upsert()`** — blocks until background upsert completes, applies
  counter deltas (vectors_added, files_added, etc.) to main-thread state, handles
  periodic manifest saves. Called at start of each flush and after the final flush.

- **Thread safety** — at most one upsert in flight (double-buffer, not unbounded queue).
  `_drain_pending_upsert()` ensures no concurrent writes to manifest or counters.
  Qdrant client is thread-safe for upsert operations.

- **Two-pass compatibility** — when `HYBRID_EMBED_SINGLE_PASS=False`, the pool is bypassed
  and embedding reverts to per-file mode (no background upsert).

### DRY Helpers Added to `index_rag.py`

| Helper | Purpose |
|--------|---------|
| `_make_manifest_entry(file_info, ids, **extra)` | Builds manifest entry dict (replaced 4 sites) |
| `_sparse_dicts_to_vectors(sparse_dicts)` | Converts sparse dicts to SparseVector objects (replaced 3 sites) |
| `_build_qdrant_points(...)` | Builds PointStruct objects (replaced 2 sites) |
| `_upsert_and_record(...)` | Upserts in batches of 500 + manifest record (two-pass path) |
| `build_branch_resolver(cfg, fixed_label)` | Unified branch resolver factory (replaced 2 sites) |
| `_do_background_upsert(work_items)` | Phase 2: background thread upsert with counter deltas |
| `_drain_pending_upsert()` | Phase 2: wait for background upsert + apply counters |

### Config Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_POOL_SIZE` | 512 | Max chunks before pool flush. Set 0 to disable pooling. |
| `EMBED_POOL_MAX_FILES` | 150 | Max files before pool flush. Raised from 50→150 in Phase 2 to eliminate GPU stalls in small-file regions. |
| `TEI_MAX_BATCH_TOKENS` | None | TEI `--max-batch-tokens` (auto-derived when None). |
| `TEI_TOKENIZATION_WORKERS` | None | TEI `--tokenization-workers` (auto-detected when None). |

### Test Coverage Update

| Module | Tests | Coverage |
|--------|-------|----------|
| `shared/chunk_pool.py` | 70 | Unit |
| `shared/embedding.py` (TruncationStats) | 24 | Unit |
| `qdrant/vector_store.py` | 16 | Unit (BM25 CPU) |
| `shared/docker_utils.py` | 65 | Unit (22 fixed + 2 new) |
| `shared/validation/` (models, loader, runner, output) | 103 | Unit |
| **Total project** | **2219** | All passing |

---

## Technical Reference: Key Gotchas and Architecture

This section documents critical discoveries made during development that future sessions
must know to avoid repeating mistakes.

### Embedding Model: trust_remote_code=True is MANDATORY

The Jina embedding model (`jinaai/jina-embeddings-v2-base-code`) uses a custom
`JinaBertModel` architecture. Without `trust_remote_code=True`, LlamaIndex/HuggingFace
loads it as a generic `BertModel` with randomly initialized weights. This produces
noise embeddings that appear to work (no errors) but give garbage search results.

**The fix is in `shared/embedding.py` line ~99.** Never remove `trust_remote_code=True`.

### Dependency Versions: transformers Must Be 4.x

The Jina model is incompatible with `transformers >= 5.0`. Pinned versions:
- `transformers==4.46.3`
- `huggingface-hub==0.36.2`
- `tokenizers==0.20.3`

If you upgrade any of these, test that the embedding model still loads correctly
(check for `JinaBertModel` in the loaded architecture, not `BertModel`).

### Float16 and -0.0: sanitize_dense_vector()

When using `torch_dtype: float16`, the model can produce `-0.0` values in embedding
vectors. Qdrant rejects these during upsert (243 errors in initial testing). The
`sanitize_dense_vector()` function in `shared/embedding.py` converts `-0.0` to `0.0`.
The `is_zero_vector()` function detects degenerate all-zero embeddings so they can be
skipped (logged as warnings). These safety nets are in `src/index_rag.py`.

### Working Directory Must Be on main_branch Before Indexing

Main-branch indexing reads source files directly from disk (the working copy).
If `../informica_2_0` (or any `git_repo` source) is checked out on a feature branch,
those feature-branch files are indexed with `branch="develop"` — silently contaminating
the main-branch vectors.

**The indexer now hard-fails on this** (`_check_git_repo_working_dirs()` in `src/index_rag.py`).
It fires before any embedding work, prints a clear error per affected repo, and calls
`sys.exit(1)`. There is no prompt — the user must fix the checkout and re-run.

**If contamination already occurred**, an incremental refresh (no `--clear` needed) will
fix it: the hash-based change detection flags files that differ between the wrong branch
and the correct branch as `modify`, and re-embeds them with the correct content.
Files that only existed on the wrong branch are flagged as `delete` and removed.

Note: The Phase 2 git-diff fast-path (`determine_actions` using `git diff` instead of
file hashes) was explicitly deferred — the indexer uses pure SHA-256 hash comparison.
This is why `--clear` is not needed for contamination recovery: changed files are
detected by hash mismatch regardless of what `main_branch_commit` says.

### HYBRID_ALPHA = 0.5 — Do NOT Change

Alpha=0.5 was confirmed optimal through testing. Alpha=0.7 was tested and caused
**regressions** — overview queries lost their results because dense embedding scores
dominated, and dense embeddings for large overview chunks are inherently weak.
The 50/50 balance lets BM25 keyword matching compensate for dense embedding limitations.

### Docker Setup: QDRANT_MODE and Auto-Start

Docker containers are auto-managed via `shared/docker_utils.py`:

- **`QDRANT_MODE = "local"`** — `src/index_rag.py` and `src/rag_mcp.py` call
  `ensure_qdrant_running(cfg)` at startup, which checks for/creates/starts the Docker
  container automatically. Container names are derived as `qdrant-{COLLECTION_NAME}`
  (overridable via `QDRANT_DOCKER_CONTAINER`).
- **TEI containers** — when `USE_TEI=True`, `ensure_tei_running(cfg)` similarly
  auto-manages the TEI Docker container (`tei-{COLLECTION_NAME}`).
- **`QDRANT_MODE = "remote"`** — No Docker management. Caller must ensure the remote
  Qdrant server is reachable. Supports `QDRANT_API_KEY`, `QDRANT_HTTPS`, `QDRANT_PREFER_GRPC`.

Client construction is centralized in `shared/qdrant_client.py` — a single
`get_qdrant_client(cfg)` call replaces all ad-hoc `QdrantClient()` constructions.

`scripts\start_qdrant.bat <config_name>` still exists for manual/diagnostic use. It calls
`ensure_qdrant_running()` via Python.

**Important:** If upgrading from a pre-`QDRANT_MODE` codebase, any config file containing
`QDRANT_USE_DOCKER` will trigger a hard `RuntimeError` with a migration message. Replace
`QDRANT_USE_DOCKER = True` with `QDRANT_MODE = "local"` in your configs.

### TEI Provenance: Don't Mix Backends

TEI and PyTorch produce **incompatible** dense vectors (different inference engines).
The indexer writes `embedding_provenance` (`"tei"` or `"pytorch"`) into Qdrant collection
metadata.  On indexing, a backend mismatch triggers a hard error requiring `--clear`.
On query (MCP), a mismatch logs a warning but doesn't block.

TEI GPU and TEI CPU vectors are compatible (both are `"tei"` provenance).

### Sparse BM25 Device: Hard-Wired to CPU

BM25 (`Qdrant/bm25`) is a vocabulary lookup with zero GPU benefit.  As of the
`feature/tei-batch-saturation` branch, `get_sparse_encoder()` in `qdrant/vector_store.py`
**always loads BM25 on CPU** regardless of `INDEX_EMBED_DEVICE`.  Only neural sparse
models (SPLADE, etc.) respect the device setting.

`INDEX_EMBED_DEVICE` and `MCP_EMBED_DEVICE` still control the device for:
- **Dense embeddings** (when `USE_TEI=False`, i.e. PyTorch backend)
- **Neural sparse models** (SPLADE) if ever used instead of BM25

When `USE_TEI=True`, dense embeddings go through the TEI Docker container, BM25 runs
on CPU, and `INDEX_EMBED_DEVICE` is effectively unused unless you switch to SPLADE.

### Pascal Tree-sitter AST Structure

Key structural insight for the Pascal reader:
- **Class name lives on `declType`, NOT `declClass`**:
  `declType > [identifier("TMyClass"), kEq, declClass, ";"]`
- `declClass > [kClass, "(", typeref, ")", ...declSection..., kEnd]`
- `declSection` = visibility blocks (published, private, public, protected)
- Method implementations: `defProc > declProc > genericDot > identifier("TMyClass")`
- The Tree-sitter grammar is `tree-sitter-language-pack` (Pascal dialect: `objectpascal`)

### All node_type Values Across Readers (95+ total)

These are the `node_type` metadata values stored in Qdrant chunks. The reranker uses
these for score adjustments.

| Reader | node_type values |
|--------|-----------------|
| **pascal_reader** (27) | `defProc`, `declProc`, `declSection`, `declVar`, `declConst`, `declUses`, `comment`, `declType`, `declClass`, `class_summary`, `class_overview`, `method_group`, `full_file`, plus 14 `_split` variants |
| **java_reader** (20+) | `class_declaration`, `interface_declaration`, `enum_declaration`, `record_declaration`, `method_declaration`, `constructor_declaration`, `field_declaration`, `constant_declaration`, `enum_constant`, `class_overview`, `import_group`, `method_group`, `block_comment`, `full_file`, plus `_split` variants |
| **js_reader** (20+) | `class_declaration`, `function_declaration`, `variable_declaration`, `interface_declaration`, `type_alias_declaration`, `enum_declaration`, `class_overview`, `import_group`, `function_group`, `block_comment`, `iife`, `namespace_object`, `prototype_method`, `full_file`, plus `_split` variants |
| **dfm_reader** (4) | `dfm_form_header`, `dfm_object`, `dfm_object_group`, `full_file` |
| **sql_reader** (12) | `create_function`, `create_procedure`, `create_trigger`, `create_view`, `create_table`, `alter_table`, `drop_table`, `select`, `statement`, `set_statement`, `create_index`, `full_file` |
| **tsql_chunker** (19) | `sql_batch`, `procedure_full`, `function_full`, `procedure_header`, `function_header`, `procedure_body`, `function_body`, various `_group` variants |
| **python_reader** (16) | `function_definition`, `decorated_definition`, `import_statement`, `class_definition`, `full_file`, plus `_split` variants |
| **hbm_reader** (2) | `hbm_entity_overview`, `hbm_entity_overview_split` |
| **jrxml_reader** (3) | `jrxml_report_overview`, `jrxml_expressions`, `jrxml_report_overview_split` |
| **fr3_reader** (4) | `fr3_report_overview`, `fr3_band_content`, `fr3_pascal_script`, `fr3_variables` |
| **dproj_reader** (3) | `dproj_project_overview`, `dproj_build_config`, `dproj_unit_group` |

**Reranker categories for FR3/DPROJ:**
- **Overview types** (primary bonus in domain-specific mode): `fr3_report_overview`, `dproj_project_overview`
- **Detail types** (mild penalty in overview queries): `fr3_variables`, `dproj_unit_group`
- **Uncategorized** (no bonus/penalty): `fr3_band_content`, `fr3_pascal_script`, `dproj_build_config`

**Reranker categories for Java/JS/TS/HBM/JRXML:**
- **Primary overview types** (+0.50): `class_overview`, `class_summary`, `class_summary_split`
- **Secondary overview types** (+0.25): `hbm_entity_overview`, `jrxml_report_overview`, `interface_declaration`, `type_alias_declaration`
- **Import penalty** (-0.25): `import_group`, `import_statement`
- **Block comment penalty**: `block_comment` from non-target files
- **Detail types** (-0.05): `method_declaration`, `constructor_declaration`, `field_declaration`, `constant_declaration`, `enum_constant`, `method_group`, `function_group`, `function_declaration`, `variable_declaration`

### Evaluation Harness: query_test_index.py

`query_test_index.py` is the evaluation tool that produced the 14/14 PASS results.
It connects to the Qdrant index, runs 14 predefined queries, and prints results with
scores, node types, and metadata. Supports `--alpha` CLI argument to test different
hybrid alpha values. Uses the reranker module.

Usage:
```bash
python query_test_index.py              # Default alpha from config
python query_test_index.py --alpha 0.5  # Override alpha
```

### test_sources/ Directory

Contains 23 curated test files (11 .pas, 1 .dpr, 6 .sql, 4 .dfm, 1 .dproj) used for
evaluation during the chunking strategy overhaul. These produce 7,734 vectors. The files
exercise all major code patterns (large classes, many methods, T-SQL procedures, DFM forms).
Use `SOURCE_DIRS = [{"path": "test_sources", ...}]` in `config.py` for test indexing.

### Dynamic VRAM Cap: shared/vram_cap.py

Computes the maximum safe sequence length for the embedding model based on GPU VRAM.
The jinaai model's ALiBi attention has O(N²) VRAM cost — the quadratic solver in
`compute_max_seq_length()` finds the largest N that fits within the VRAM budget.

- Integrated into `shared/embedding.py` — when `EMBED_DYNAMIC_VRAM_CAP = True` in config
  and the device is CUDA, `get_embed_model()` calls `resolve_embed_max_seq_length()`.
- For CPU devices (MCP server), the static `EMBED_MAX_SEQ_LENGTH` is always used.
- `MODEL_REGISTRY` contains architecture params for jinaai and bge-m3 models.
- Auto-detects GPU VRAM via nvidia-smi and shared VRAM from system RAM.
- Config overrides: `EMBED_VRAM_DEDICATED_MB`, `EMBED_VRAM_SHARED_MB`, `EMBED_VRAM_SAFETY_MARGIN`.
- 85 unit tests in `src_test/shared/test_vram_cap.py`.

---

## RAG Validation & Improvement Process

### Per-Config YAML Validation Tests

Each project config has its own validation test suite defined in YAML:

```
project-configs/<config_name>/validation_tests.yaml
```

Test cases are pure YAML — no Python code in test definitions. Each test specifies
a query, expected criteria (node_types, file_pattern, text_pattern, class_name_pattern,
max_position, partial_position, multi_file), difficulty, and aspect.

**Existing test suites:**

| Config | Tests | Categories | Description |
|--------|------:|:----------:|-------------|
| `config_informica_tei_jinaai` | 78 | 14 | Delphi/SQL/DFM codebase (original) |
| `config_informica` | 78 | 14 | Same tests, PyTorch backend |
| `config_epodroznik` | 30 | 10 | Java/HBM/JRXML webapp |

**YAML schema:** See `docs/validation/validation-tests-guide.md` for the full authoring guide.
**Original test spec:** See `docs/validation/rag-validation-tests.md` for the informica test
rationale, design notes, and evaluation methodology.

### Validation Framework Architecture

The monolithic `validate_rag.py` (formerly 1927 lines) was refactored into a modular
`shared/validation/` package:

| Module | Lines | Purpose |
|--------|------:|---------|
| `shared/validation/models.py` | 87 | `PassCriteria`, `TestCase`, `TestResult` dataclasses |
| `shared/validation/loader.py` | 129 | YAML loading via `load_test_cases(config_name)` |
| `shared/validation/runner.py` | 388 | `setup()`, `run_query()`, `evaluate_test()` + helpers |
| `shared/validation/output.py` | 289 | `print_results()`, `output_json()`, `get_categories()` |
| `validate_rag.py` | 202 | Thin CLI entry point (`--config` required) |

**103 unit tests** in `src_test/shared/validation/` (models, loader, runner, output).

### Automated Test Runner: validate_rag.py

`--config` is **required** — there is no default config.

```bash
# Run all tests for a config
python src/validate_rag.py --config config_informica_tei_jinaai

# List tests without running
python src/validate_rag.py --config config_epodroznik --list

# Run a specific category (by number or name substring)
python src/validate_rag.py --config config_informica_tei_jinaai --category "Class Overview"

# Run a single test by ID
python src/validate_rag.py --config config_epodroznik --test T05

# JSON output for CI
python src/validate_rag.py --config config_informica_tei_jinaai --json

# Verbose (show chunk details for PASS results too)
python src/validate_rag.py --config config_informica_tei_jinaai --verbose

# Override alpha
python src/validate_rag.py --config config_informica_tei_jinaai --alpha 0.5
```

Scoring: PASS=2pts, PARTIAL=1pt, FAIL=0pts.
Rating thresholds: Outstanding (>=95%), Excellent (>=90%), Good (>=80%),
Acceptable (>=70%), Needs Improvement (>=60%), Poor (<60%).

### Improvement Process: docs/improvement-process.md

Structured 7-step methodology for iteratively improving index quality and performance:

1. **Baseline Measurement** — run validation suite, record metrics
2. **Hypothesis** — propose a specific change with expected improvement
3. **Implement** — make the change
4. **Quick Validation** — test against test_sources index
5. **Production Validation** — full reindex + validation suite
6. **Decision** — commit or revert based on results
7. **Update Notes** — record results in iteration notes

**Iteration notes** live in `docs/iterations/iteration-NNN.md`.  Each iteration
documents the hypothesis, changes, before/after metrics, and conclusion.

### When to Run Validation Tests

Run `validate_rag.py` (or a subset) when:

1. **Before starting an improvement iteration** — establish baseline
2. **After any chunking strategy change** — reader modifications, grouping rules, context prefixes
3. **After reranker parameter changes** — score adjustments, overfetch multiplier
4. **After config changes** — alpha, batch sizes, sequence length cap
5. **After model changes** — different embedding model (requires full reindex first)

The test runner connects to the production Qdrant index on `QDRANT_HOST:QDRANT_PORT`
and uses the CPU embedding device by default.
