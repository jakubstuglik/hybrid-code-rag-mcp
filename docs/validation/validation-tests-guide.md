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

### External suite path

A suite can live outside this repository, next to the codebase it measures.
`--config` still names the index. `--tests` names the YAML file:

```bash
python src/validate_rag.py --config <config_name> --tests D:\path\to\validation_tests.yaml --list
python src/validate_rag.py --config <config_name> --tests D:\path\to\validation_tests.yaml
```

The file must be the same YAML list documented above. Nothing in the suite is
read from `project-configs/` when `--tests` is set. Keep product-specific cases
in the product repository, not in this one.

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
| `--alpha FLOAT` | Override `HYBRID_ALPHA` (0.0=BM25 only, 1.0=dense only). In fixed mode this is the alpha for every query. In adaptive mode it replaces `HYBRID_ALPHA` as the base for mixed and natural-language queries when `HYBRID_ALPHA_MIXED` / `HYBRID_ALPHA_NL` are unset; `HYBRID_ALPHA_IDENT` is unchanged. |
| `--top-k INT` | Number of results to evaluate (default: 8). |
| `--category N` | Run only category N (by number or name substring). |
| `--test ID` | Run only test with given ID (e.g. `T01`). |
| `--verbose` | Show all retrieved nodes, even for PASS results. |
| `--json` | Output results as JSON to stdout. |
| `--list` | List all test cases and exit (no index query). |
| `--tests PATH` | Load this YAML suite instead of the config default. Wins over `VALIDATION_TESTS_FILE`. |
| `--diag-rank N` | Extra search of N results per test. JSON gains `diag_rank` (1-based full criteria match, or null) and `diag_top3_files`. The scored search is unchanged: a larger fetch can change fusion and rerank pools, so this is a separate call. |
| `--set KEY=VALUE` | Override a config value for this run (repeatable), e.g. `--set HYBRID_PREFETCH_K=50` or `--set "DEPRIORITIZED_PATHS=[]"`. `VALUE` is parsed as a Python literal; anything else is taken as a string. Useful for A/B runs without editing the config. |
| `--lang pl\|en\|both` | Score Polish, English, or both passes against one index. Omitted: a legacy `query` is used as-is; a bilingual test uses `query_en` when present, otherwise `query_pl`. |
| `--strict-lang` | Exit 1 if any test lacks `query_pl` or `query_en`, or if an id is duplicated. With `--list`, lint the suite without opening an index. |

The suite path, when `--tests` is omitted, is `VALIDATION_TESTS_FILE` on the config (absolute path) if that key is set, otherwise `project-configs/<config>/validation_tests.yaml`.

## YAML Schema

Each test case is a YAML mapping in a list. The file must be named
`validation_tests.yaml` and placed in the project config directory.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier, e.g. `"T01"`, `"T02"` |
| `category` | string | Category name for grouping, e.g. `"Class Overview Queries"` |
| `query` | string | Language-neutral query text. Required when `query_pl` / `query_en` are omitted. Do not combine it with those keys. |
| `description` | string | Human-readable description of what we expect |
| `criteria` | mapping | Pass/fail evaluation criteria (see below). Shared by every language. |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `difficulty` | string | `"Medium"` | `Easy`, `Medium`, or `Hard` (reporting only) |
| `aspect` | string | `"Hybrid"` | Which subsystem is tested: `Dense`, `Sparse`, `Hybrid`, `Reranker` |
| `query_class` | string | unset | `semantic`, `exact`, or `mixed` (any case). When at least one test sets it, the console summary and JSON (`by_query_class`) add per-class score %, PASS/PARTIAL/FAIL counts and n. Any other value warns and is unclassified. Suites that omit the field keep the previous report shape. |
| `query_pl` | string | unset | Polish wording of the same question. See [Bilingual suites](#bilingual-suites-query_pl--query_en). |
| `query_en` | string | unset | English wording of the same question. See [Bilingual suites](#bilingual-suites-query_pl--query_en). |

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

A `node_type` match **on its own** earns no PARTIAL when the test sets a
`file_pattern`: any chunk of an allowed type (any function, any struct) would
qualify, so it says nothing about the answer. File-only and text-only matches
still count. Scores of suites that relied on type-only partial credit drop
after this change; that is the honest number, not a retrieval regression.

### Reported metrics

Besides PASS / PARTIAL / FAIL and the score, each run reports:

- **Doc hints**: how many non-PASS tests have a documentation chunk (Markdown,
  reStructuredText, plain text or a comment chunk of another file) in the
  top-k whose text names the expected file or symbol. Such a result points the
  caller to the answer although the expected code chunk was missed. It is
  reported separately and never changes the score. In `--json` output:
  `doc_hint_count` and, per test, `doc_hint_position`.
- **Latency**: wall time per query (`query_ms` per test; `latency_ms` with
  `p50`, `p95`, `mean` in the JSON summary). It includes embedding the query,
  both hybrid legs, the optional symbol lookup and the reranker.

## Bilingual suites (query_pl / query_en)

A suite can give every test a Polish query and an English query that share
one expected result. Category, description, criteria, difficulty, aspect and
`query_class` are stored once, so the two languages cannot drift apart.

### Schema

Each test has **either** the legacy `query` **or** at least one of `query_pl`
and `query_en`.

- `query_pl` and `query_en` are non-empty strings. An empty value, a
  whitespace-only value, or a non-string is a load error.
- Putting `query` in the same test as `query_pl` or `query_en` is an error
  (`ambiguous: use query_pl/query_en or query, not both`).
- A test with neither `query` nor a language query is still a missing-`query`
  error.
- Everything else on the test is shared. Do not copy criteria per language.

### Which text is sent

| How you load | Legacy `query` only | Bilingual test |
|---|---|---|
| `--lang` omitted | `query`, unchanged | `query_en` if present, otherwise `query_pl` |
| `--lang pl` or `--lang en` | `query`, unchanged | That language. If it is missing, the other language is used, one warning names the test, and the recorded language is the one actually used |
| `--strict-lang` | Load fails | Load fails unless **both** `query_pl` and `query_en` are set |

A legacy `query` is language-neutral. It is sent unchanged for every
language, including both passes of `--lang both`. Existing suites therefore
score exactly as before, and JSON from a run that does not pass `--lang`
has no new keys.

`--strict-lang` fails if any test lacks `query_pl` or `query_en` (a
`query`-only test lacks both). The error lists every offending id. Duplicate
ids fail in this mode as well. It works with `--list`, so it can lint a
suite without an index:

```bash
python src/validate_rag.py --config config_myproject --tests suite.yaml --strict-lang --list
python src/validate_rag.py --config config_myproject --tests suite.yaml --lang en
python src/validate_rag.py --config config_myproject --tests suite.yaml --lang both --json
```

`--list` shows `[pl,en]` (or whichever language the test has) on bilingual
rows. `--lang both --list` prints both query texts. `--lang pl` or `--lang en`
prints the language in the result header. JSON from those runs adds a
top-level `"lang"` and a per-test `"lang"` (the language actually used, or
null for a legacy query).

`--lang both` opens the index once, runs the selected tests (honouring
`--test` and `--category`) in Polish, then in English, with the same
`top_k` and the same `--diag-rank` on each pass. The text report is a
side-by-side summary: overall score and PASS/PARTIAL/FAIL, the delta in
percentage points (English minus Polish), the same split for each
`query_class` (with n) and each category, then the tests whose result or
match position differs. `--verbose` also prints the full per-language
detail. `--json` returns `pl` and `en` (each the normal single-language
object), `delta` (`score_pct`, `by_query_class`, `by_category`),
`changed_tests`, and `fallback_tests`. A legacy-only suite is allowed;
both passes are identical and stderr notes that the suite has no
language-specific queries.

### Authoring rule

Both languages ask the same question with the same specificity. An
identifier-only query is identical in both languages. Expected results are
shared, so never tune one language separately: if Polish fails and English
passes, fix the index or the shared criteria, not one wording.

```yaml
- id: U01
  category: Uploads
  description: Retry logic for failed uploads lives on UploadQueue
  difficulty: Medium
  aspect: Hybrid
  query_class: semantic
  query_pl: "Gdzie jest logika ponawiania nieudanych wysyłek?"
  query_en: "Where is the retry logic for failed uploads?"
  criteria:
    file_pattern: "upload_queue\\.py$"
    text_pattern: "retry"
    max_position: 3

- id: U02
  category: Uploads
  description: Identifier is the same in both languages
  difficulty: Easy
  aspect: Sparse
  query_class: exact
  query_pl: "UploadQueue"
  query_en: "UploadQueue"
  criteria:
    text_pattern: "UploadQueue"
    max_position: 2
```

## Examples

### Simple identifier search (Sparse)

```yaml
- id: T10
  category: Precise Identifier Search
  query: REPORT_TYPE_MONTHLY_TOTALS
  description: Should find constant definition in .pas file
  difficulty: Easy
  aspect: Sparse
  criteria:
    file_pattern: "\\.pas"
    text_pattern: "REPORT_TYPE_MONTHLY_TOTALS"
    max_position: 2
```

### Class overview with reranker (Reranker)

```yaml
- id: T01
  category: Class Overview Queries
  query: What is TdmOrders?
  description: Should find class summary/overview for TdmOrders in OrdersDM.pas
  difficulty: Medium
  aspect: Reranker
  criteria:
    node_types: [class_summary, class_summary_split, class_overview]
    file_pattern: "OrdersDM\\.pas"
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
    file_pattern: "OrdersDM\\.pas"
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

The SQL reader and T-SQL chunker types above apply when `sql_dialect` is omitted or `tsql`.

### PostgreSQL Chunker (`sql_dialect: postgresql`)
`pgsql_create_table`, `pgsql_create_function`, `pgsql_create_procedure`,
`pgsql_create_trigger`, `pgsql_create_rule`, `pgsql_create_index`,
`pgsql_create_view`, `pgsql_create_sequence`, `pgsql_create_schema`,
`pgsql_comment`, `pgsql_alter`, `pgsql_statement`, `full_file`, plus `_split`.

Overview queries promote `pgsql_create_function`, `pgsql_create_procedure`,
`pgsql_create_table`, `pgsql_create_trigger`, `pgsql_create_rule`, and
`pgsql_create_view`. `pgsql_statement`, `pgsql_alter`, and `pgsql_create_index`
are detail chunks.

### C/C++ Reader
`class_overview`, `class_summary`, `cpp_function`, `method_group`,
`include_group`, `declaration_group`, `enum_declaration`, `macro_group`,
`macro_definition`, `full_file`, plus `_split`

### Qt .ui Reader
`ui_form_header`, `ui_object`, `ui_object_group`, `ui_connections`, `full_file`

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
