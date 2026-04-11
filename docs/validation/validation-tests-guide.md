# RAG Validation Test Guide

Automated test suite for measuring and tracking RAG retrieval quality per project.

## Getting Started

Follow these steps to create a validation test suite for your project config.

### Prerequisites

1. **Project config created** — you need a directory `project-configs/<config_name>/` with
   a `config.py` file. See the main README for config setup.
2. **Index built** — run `python src/index_rag.py --config <config_name> --yes --log-to-file --collect-perf-stats`
   at least once so the Qdrant collection has vectors to query.
3. **MCP server works** — verify with `python src/rag_mcp.py --config <config_name> --transport stdio`
   (Ctrl+C to exit after startup).

### Step 1: Explore Your Index

Before writing tests, query your index to see what's actually there:

```bash
# Start the MCP server interactively or use the validation runner in verbose mode
python src/validate_rag.py --config <config_name> --list  # (after creating a minimal YAML)
```

Or use the search tool (if configured as an MCP server) to run a few exploratory queries
and note the `node_type`, `file_path`, `class_name`, and text content of returned chunks.

### Step 2: Create validation_tests.yaml

Create the file `project-configs/<config_name>/validation_tests.yaml` with a few starter tests:

```yaml
# Starter validation suite — adjust queries and criteria to your project
- id: T01
  category: Class Overview Queries
  query: "What is MyMainClass?"
  description: Should find class overview for MyMainClass
  difficulty: Medium
  aspect: Reranker
  criteria:
    node_types: [class_summary, class_overview, class_summary_split]
    file_pattern: "MyMainClass"
    max_position: 3

- id: T02
  category: Precise Identifier Search
  query: "MY_CONSTANT_NAME"
  description: Should find exact constant definition
  difficulty: Easy
  aspect: Sparse
  criteria:
    text_pattern: "MY_CONSTANT_NAME"
    max_position: 2

- id: T03
  category: Natural Language
  query: "How to connect to the database"
  description: Should find database connection code
  difficulty: Hard
  aspect: Dense
  criteria:
    text_pattern: "(?i)(connection|connect|database)"
    max_position: 5
    partial_position: 8
```

### Step 3: Run and Iterate

```bash
# Run all tests
python src/validate_rag.py --config <config_name>

# Verbose mode shows what the index actually returns (useful for tuning criteria)
python src/validate_rag.py --config <config_name> --verbose

# Run a single test to debug
python src/validate_rag.py --config <config_name> --test T01 --verbose
```

Adjust `max_position`, `file_pattern`, `node_types`, and `text_pattern` based on what
`--verbose` shows. Add more tests as you discover important entities in your codebase.

### Step 4: Expand Coverage

Aim for 20-30 tests across these categories:
- **5+ Easy/Sparse** — exact identifier matches (sanity checks)
- **10+ Medium/Hybrid** — class overviews, file-level queries, cross-file searches
- **5+ Hard/Dense** — semantic/natural language queries, paraphrase tests

## Overview

Each project config has its own validation test suite defined in YAML:

```
project-configs/
  <config_name>/
    validation_tests.yaml      # Your project's test suite
```

The runner loads tests from YAML, queries the Qdrant index, and evaluates results
against pass criteria. Scoring: **PASS=2pts, PARTIAL=1pt, FAIL=0pts**.

## Quick Start

```bash
# Run all tests for a config
python src/validate_rag.py --config config_myproject

# List tests without running them
python src/validate_rag.py --config config_another_project --list

# Run specific category or test
python src/validate_rag.py --config config_myproject --category 1
python src/validate_rag.py --config config_myproject --test T01

# Override hybrid alpha, verbose output
python src/validate_rag.py --config config_myproject --alpha 0.7 --verbose

# JSON output for CI/automation
python src/validate_rag.py --config config_myproject --json
```

## CLI Reference

| Flag | Description |
|------|-------------|
| `--config NAME` | **Required.** Config directory name in `project-configs/`. |
| `--alpha FLOAT` | Override `HYBRID_ALPHA` (0.0=BM25 only, 1.0=dense only). |
| `--top-k INT` | Number of results to evaluate (default: 8). |
| `--category N` | Run only category N (by number or name substring). |
| `--test ID` | Run only test with given ID (e.g. `T01`). |
| `--verbose` | Show all retrieved nodes, even for PASS results. |
| `--json` | Output results as JSON to stdout. |
| `--list` | List all test cases and exit (no index query). |

## YAML Schema

Each test case is a YAML mapping in a list. The file must be named
`validation_tests.yaml` and placed in the project config directory.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier, e.g. `"T01"`, `"T02"` |
| `category` | string | Category name for grouping, e.g. `"Class Overview Queries"` |
| `query` | string | The query text sent to the RAG retriever |
| `description` | string | Human-readable description of what we expect |
| `criteria` | mapping | Pass/fail evaluation criteria (see below) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `difficulty` | string | `"Medium"` | `Easy`, `Medium`, or `Hard` (reporting only) |
| `aspect` | string | `"Hybrid"` | Which subsystem is tested: `Dense`, `Sparse`, `Hybrid`, `Reranker` |

### Criteria Fields

All criteria fields are optional. Omitted fields are not checked. A retrieved
node must satisfy **ALL** specified fields to count as a full match.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `node_types` | list[string] | any | Acceptable `node_type` metadata values |
| `file_pattern` | string (regex) | any | Regex matched against `file_path` metadata |
| `text_pattern` | string (regex) | any | Regex matched against chunk text content |
| `max_position` | int | 3 | Position threshold for PASS (1-indexed, inclusive) |
| `partial_position` | int | 5 | Position threshold for PARTIAL |
| `class_name_pattern` | string (regex) | any | Regex matched against `class_name` metadata |
| `multi_file` | bool | false | PASS requires matches from >= 2 distinct files |

### Evaluation Logic

For each test, the runner retrieves `top_k` results and evaluates:

1. **PASS**: A node matching ALL criteria appears at position <= `max_position`
2. **PARTIAL**: A full match appears at position <= `partial_position` but > `max_position`,
   OR a partial match (file only, type only, or text only) appears at position <= `partial_position`
3. **FAIL**: No matching node found in any position

For `multi_file: true` tests, PASS additionally requires matches from >= 2 different files.

## Examples

### Simple identifier search (Sparse)

```yaml
- id: T10
  category: Precise Identifier Search
  query: REPORT_TYPE_PUNCTUALITY_RIDES
  description: Should find constant definition in .pas file
  difficulty: Easy
  aspect: Sparse
  criteria:
    file_pattern: "\\.pas"
    text_pattern: "REPORT_TYPE_PUNCTUALITY_RIDES"
    max_position: 2
```

### Class overview with reranker (Reranker)

```yaml
- id: T01
  category: Class Overview Queries
  query: What is TdmMain?
  description: Should find class summary/overview for TdmMain in MainDM.pas
  difficulty: Medium
  aspect: Reranker
  criteria:
    node_types: [class_summary, class_summary_split, class_overview]
    file_pattern: "MainDM\\.pas"
```

### Natural language / semantic query (Dense)

```yaml
- id: T33
  category: Natural Language
  query: How to connect to the database
  description: Should find database connection code
  difficulty: Hard
  aspect: Dense
  criteria:
    file_pattern: "MainDM\\.pas"
    text_pattern: "(?i)(Connection|Connect|database)"
    max_position: 5
    partial_position: 8
```

### Cross-file multi-match (Hybrid)

```yaml
- id: T23
  category: Cross-File
  query: classes that inherit from TForm
  description: Should find TForm references from multiple files
  difficulty: Medium
  aspect: Hybrid
  criteria:
    text_pattern: "TForm"
    multi_file: true
    max_position: 5
    partial_position: 8
```

### HBM entity mapping (Hybrid)

```yaml
- id: T11
  category: Hibernate Mapping
  query: Ticket hibernate mapping
  description: Should find HBM entity overview for Ticket entity
  difficulty: Medium
  aspect: Hybrid
  criteria:
    file_pattern: "(?i)Ticket.*\\.hbm\\.xml"
    node_types: [hbm_entity_overview, hbm_entity_overview_split]
    max_position: 5
    partial_position: 8
```

## Available node_type Values

Use these in the `node_types` criteria field. Values depend on which reader
processed the file.

### Pascal Reader (27 types)
`defProc`, `declProc`, `declSection`, `declVar`, `declConst`, `declUses`,
`comment`, `declType`, `declClass`, `class_summary`, `class_overview`,
`method_group`, `full_file`, plus `_split` variants

### Java Reader (20+ types)
`class_declaration`, `interface_declaration`, `enum_declaration`,
`record_declaration`, `method_declaration`, `constructor_declaration`,
`field_declaration`, `constant_declaration`, `enum_constant`,
`class_overview`, `import_group`, `method_group`, `block_comment`,
`full_file`, plus `_split` variants

### JavaScript/TypeScript Reader (20+ types)
`class_declaration`, `function_declaration`, `variable_declaration`,
`interface_declaration`, `type_alias_declaration`, `enum_declaration`,
`class_overview`, `import_group`, `function_group`, `block_comment`,
`iife`, `namespace_object`, `prototype_method`, `full_file`, plus `_split` variants

### DFM Reader (4 types)
`dfm_form_header`, `dfm_object`, `dfm_object_group`, `full_file`

### SQL Reader (12 types)
`create_function`, `create_procedure`, `create_trigger`, `create_view`,
`create_table`, `alter_table`, `drop_table`, `select`, `statement`,
`set_statement`, `create_index`, `full_file`

### T-SQL Chunker (19 types)
`sql_batch`, `procedure_full`, `function_full`, `procedure_header`,
`function_header`, `procedure_body`, `function_body`, various `_group` variants

### Python Reader (16 types)
`function_definition`, `decorated_definition`, `import_statement`,
`class_definition`, `full_file`, plus `_split` variants

### HBM Reader (2 types)
`hbm_entity_overview`, `hbm_entity_overview_split`

### JRXML Reader (3 types)
`jrxml_report_overview`, `jrxml_expressions`, `jrxml_report_overview_split`

### FR3 Reader (4 types)
`fr3_report_overview`, `fr3_band_content`, `fr3_pascal_script`, `fr3_variables`

### DPROJ Reader (3 types)
`dproj_project_overview`, `dproj_build_config`, `dproj_unit_group`

### Text Reader
`full_file` (all extensions handled by TextFileReader)

## Writing Good Tests

### Difficulty Guidelines

- **Easy**: Exact identifier match, should be top-1 or top-2. Tests sparse/BM25.
- **Medium**: Requires right node type + file. Tests hybrid retrieval + reranker.
- **Hard**: Semantic/paraphrase queries, typo tolerance, cross-file. Tests dense embeddings.

### Aspect Guidelines

- **Sparse**: Query contains exact tokens from the source. BM25 should handle it.
- **Dense**: Query uses different words than the source. Semantic embeddings needed.
- **Hybrid**: Both sparse and dense contribute. Alpha balance matters.
- **Reranker**: Post-retrieval reranker score adjustments are critical for PASS.

### Tips

1. Start with 20-30 tests covering your project's most important entities.
2. Include at least 5 "Easy/Sparse" tests as sanity checks.
3. Include at least 5 "Hard/Dense" tests to stress-test semantic understanding.
4. Use `--verbose` to see what the index actually returns — adjust criteria accordingly.
5. Run after every reindex to catch regressions.
6. Track scores over time (use `--json` and save to `validation_results.json`).

## Architecture

```
src/
  validate_rag.py                   # CLI entry point (thin — loads YAML, delegates)
  shared/
    validation/
      __init__.py                   # Exports: PassCriteria, TestCase, TestResult
      models.py                     # Dataclasses (no external dependencies)
      loader.py                     # YAML loading + TestCase construction
      runner.py                     # setup(), run_query(), evaluate_test()
      output.py                     # print_results(), output_json()

project-configs/
  <config_name>/
    validation_tests.yaml           # Per-config test definitions
    validation_results.json         # Optional: saved JSON results
```

The `validate_rag.py` CLI loads test cases via `loader.load_test_cases(config_name)`,
sets up the retrieval pipeline via `runner.setup()`, runs each query via
`runner.run_query()`, evaluates via `runner.evaluate_test()`, and formats output
via `output.print_results()` or `output.output_json()`.
