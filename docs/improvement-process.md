# Indexing Improvement Process

A structured methodology for iteratively improving the hybrid-code-rag-mcp index — the
RAG system that serves AI agents working on a Delphi Pascal / T-SQL / DFM codebase.

---

## 1. Core Rules

These rules are immutable unless the user explicitly approves a change. They are ordered
by priority. When two rules conflict, the higher-priority rule wins.

### Priority 1 — Index Quality

The goal is making the best possible index for a RAG MCP server that serves AI agents
accelerating programming tasks (small and large) on the indexed codebase.

- **Quality is measured by the RAG validation test suite** (`docs/rag-validation-tests.md`) — a
  comprehensive set of queries with expected results. Every improvement must be validated
  against this suite. If the suite does not exist yet, it must be created before beginning
  the first improvement cycle.
- **The index must be comprehensive.** No parts of the codebase may be excluded. Every file
  that exists in the configured `SOURCE_DIRS` must have its content indexed.
- **Noise dilutes quality.** Including too many loosely related snippets buries the relevant
  ones. The sweet spot is: every meaningful code construct is findable, but generic boilerplate
  does not dominate results. Chunk design (context prefixes, grouping, deduplication) is the
  primary lever here.
- **Two query archetypes must both work well:**
  1. **Overview / understanding** — "What does TdmMain do?", "What classes are in emar105?"
  2. **Precise code location** — "Where is PrepareDataSet?", "REPORT_TYPE_PUNCTUALITY_RIDES"

### Priority 2 — Hardware Constraints

The system runs on a workstation with an NVIDIA GeForce RTX 4060:

| Resource | Capacity | Notes |
|----------|----------|-------|
| Dedicated VRAM | 8 GB (8188 MiB) | Fast GDDR6, exclusive to GPU |
| Shared GPU memory | Up to 16 GB | Carved from 32 GB system RAM, ~10x slower than dedicated |
| System RAM | 32 GB total | Shared with OS and other processes |
| OS | Windows | nvidia-smi + Windows performance counters for monitoring |

**Hard constraints:**

- **CUDA indexing is mandatory.** CPU embedding is too slow for 12,400+ files.
- **Must NOT produce CUDA OOM errors.** An OOM crash wastes the entire run.
- **The jinaai model uses ALiBi attention** with an O(N^2) VRAM cost for the bias tensor.
  At the model's native max of 8192 tokens the bias alone is ~1.5 GB in float16.
  `EMBED_MAX_SEQ_LENGTH = 4096` caps this at ~384 MB. This is a fundamental architectural
  constraint — it cannot be fixed without changing the model.
- **Minimize shared VRAM spilling.** Dedicated VRAM is ~10x faster than shared. When the
  working set exceeds 8 GB, the driver spills to shared memory and throughput collapses.
  Target: average shared VRAM < 1 GB during indexing.

### Priority 3 — Performance

Indexing speed matters but is secondary to quality. The production codebase is ~12,400 files
producing ~140K chunks; a full reindex currently takes approximately 2 hours.

- **Higher average GPU utilization generally means better throughput** (the GPU is not starved
  waiting for CPU-side batch preparation).
- Use `gpu_stats.csv` and indexing logs to measure performance quantitatively.
- **Target: reduce production indexing time below 1 hour** (stretch goal).
- The indexer is incremental (only re-embeds changed files), so day-to-day reindexing is fast.
  Full reindex time matters for model changes, chunking strategy changes, and CI.

### Priority 4 — Model Selection

- **Stick with jinaai/jina-embeddings-v2-base-code (dense) + Qdrant/bm25 (sparse)** unless a
  clearly better option is found and validated.
- If trying a different model, the stable process on the current model must be preserved.
  Work on a branch. No breaking changes to main.
- **Any model change requires a full reindex + full validation test suite run.** There are no
  shortcuts — embedding spaces are not comparable across models.

### Priority 5 — Query Parameters

- **`HYBRID_ALPHA = 0.5` is confirmed optimal.** Alpha=0.7 was tested and caused regressions:
  overview queries lost their results because dense scores dominated, and dense embeddings for
  large overview chunks are inherently weak.
- Fine-tune query-time parameters (reranker bonuses/penalties, overfetch multiplier) based on
  validation test results.
- The reranker module (`shared/reranker.py`) adjusts scores for overview queries — its
  parameters are tunable without reindexing.

---

## 2. Improvement Cycle Methodology

Every improvement follows a seven-step cycle. No step may be skipped.

```
 Step 1          Step 2          Step 3          Step 4
Baseline  --->  Hypothesis --->  Implement --->  Quick
Measurement                                     Validation
    ^                                               |
    |           Step 7          Step 6          Step 5
    +------  Update Notes  <--- Decision  <--- Production
                                                Validation
```

### Step 1: Baseline Measurement

Before changing anything, record the current state.

1. Run the validation test suite against the current production index:
   ```bash
   python query_test_index.py --alpha 0.5
   ```
2. Record:
   - PASS / PARTIAL / FAIL count for each test category
   - Overall pass rate (e.g., 14/14 = 100%)
   - Any specific queries that are borderline
3. If measuring performance, record from the most recent indexing run:
   - Total indexing wall time
   - Average GPU utilization (from `gpu_stats.csv`)
   - Peak and average dedicated VRAM usage
   - Peak and average shared VRAM usage
   - Number of chunks truncated at `EMBED_MAX_SEQ_LENGTH`
   - Number of zero-vector / degenerate embedding warnings

### Step 2: Hypothesis

1. **Identify the weakest area.** Look at:
   - Lowest-scoring test categories (overview queries? exact match? SQL?)
   - Worst performance metrics (GPU idle? high shared VRAM? many truncations?)
   - Known TODO items or user-reported search quality issues
2. **Form a hypothesis.** Write it as:
   > "Changing [X] from [current] to [proposed] should improve [metric] because [reason]."
3. **Estimate impact** — will this affect quality, performance, or both?
4. **Estimate risk** — could this regress other test categories?

Document the hypothesis in the iteration notes before writing any code.

### Step 3: Implementation

1. Make the code change on a branch (or on main for small, safe changes).
2. Run the unit test suite to catch regressions:
   ```bash
   .venv\Scripts\python -m pytest -v --tb=short
   ```
3. All 873+ tests must pass before proceeding. Fix any failures.

### Step 4: Quick Validation (test_sources)

Use the curated `test_sources/` directory (38 files, ~10K+ chunks) for fast iteration.

1. Reindex test_sources:
   ```bash
   python index_rag.py --config test-sources --clear --yes
   ```
   This takes ~2-3 minutes — fast enough for tight iteration loops.
2. Run the validation test suite against the test_sources index.
3. Compare against the baseline recorded in Step 1.
4. **If results are worse or unchanged:** revert and return to Step 2 with a new hypothesis.
5. **If results are improved:** proceed to Step 5.

This step exists to prevent wasting 2 hours on a production reindex for a change that
does not help. Always validate on test_sources first.

### Step 5: Production Validation

1. Reindex the full production codebase:
   ```bash
   python index_rag.py --collect-perf-stats --log-to-file
   ```
   Enable GPU stats collection and log-to-file for post-run analysis.
2. Run the validation test suite against the production index.
3. **Run ad-hoc production queries.** Each iteration must include **at least 3 freshly
   written queries** targeting random files from the full production set that are **NOT in
   test_sources/**. This prevents overfitting to the curated test set. Document the ad-hoc
   queries and their results in the iteration notes.
   - Pick files by browsing `source/` or `schemas/` randomly (e.g., `dir source\*.pas /b | sort /R`
     and grab the first few).
   - Write queries that exercise the same archetypes as the formal tests: overview, exact
     identifier, cross-file, natural language.
   - Score them informally (PASS/PARTIAL/FAIL) with a brief explanation.
   - If an ad-hoc query reveals a systematic failure, consider adding it to the formal test
     suite in the next iteration.
4. Compare against the baseline from Step 1:
   - Quality: pass rate, any new failures or regressions?
   - Performance: wall time, GPU utilization, VRAM usage.
5. **Pay special attention to queries that worked before.** Regressions are worse than
   missing improvements.

### Step 6: Decision

| Outcome | Action |
|---------|--------|
| Quality improved, no regressions | Commit, push, update notes |
| Quality unchanged, performance improved | Commit, push, update notes |
| Quality improved in one area but regressed in another | Analyze tradeoff. If net positive, commit with documented caveats. If net negative, revert. |
| Quality degraded | **Revert.** Document the dead end in iteration notes. |
| CUDA OOM or crash | **Revert immediately.** Diagnose VRAM cause before retrying. |

### Step 7: Update Notes

1. Create (or update) an iteration notes file: `docs/iteration-notes/iteration-NNN.md`
2. Record:
   - Date
   - Hypothesis (from Step 2)
   - What was changed (files, parameters, config values)
   - Baseline scores vs. new scores (table format)
   - Performance metrics before/after
   - Conclusion: did it work? Why or why not?
   - Any secondary observations
3. **The latest notes file should be self-contained** — sufficient to restart work without
   reading all previous iteration files. Include current parameter values, known issues,
   and next steps.

---

## 3. Tunable Parameters (Knobs)

This is the complete inventory of parameters and code areas that can be modified to
improve quality or performance. Organized by subsystem.

### 3.1 Chunking (Readers)

These parameters control how source code is split into chunks before embedding. Changes
here require reindexing.

#### Pascal Reader (`shared/readers/pascal_reader.py`)

| Parameter | Current Value | Description |
|-----------|---------------|-------------|
| `MAX_CHUNK_CHARS` | 24000 | Max chars per chunk before split (~6000 tokens). Chunks exceeding this are split with TokenTextSplitter and get `_split` suffix on node_type. |
| `MIN_CHUNK_SIZE` | 20 | Minimum chars for a chunk to be emitted. Smaller chunks are discarded. |
| `MAX_SUMMARY_CHARS` | 6000 | Max chars for class_summary before it gets split. When exceeded, a separate class_overview chunk is also generated. |
| `TRIVIAL_METHOD_LINES` | 6 | Method bodies with <= this many lines are considered "trivial" and eligible for grouping. |
| `MAX_GROUP_CHARS` | 8000 | Max chars for a grouped trivial-method chunk (method_group). |
| Context prefix format | `// Unit: <filename>` + `// Class: TClassName = class(TParent)` | Prefixed to every chunk. Critical for embedding quality — gives the model context about what file/class this code belongs to. |
| Class overview generation | Natural-language summary + member list | The `_build_class_overview()` method produces a concise overview with a sentence like "TdmMain is a Delphi class inheriting from TDataModule with 150 published members." |

#### T-SQL Chunker (`shared/readers/tsql_chunker.py`)

| Parameter | Current Value | Description |
|-----------|---------------|-------------|
| `MIN_CHUNK_CHARS` | 100 | Minimum chars for a chunk. |
| `MAX_CHUNK_CHARS` | 12000 | Max chars before force-split. |
| `FORCE_SPLIT_CHARS` | (> MAX_CHUNK_CHARS) | Absolute ceiling for force-splitting oversized chunks. |
| DDL grouping threshold | `MAX_CHUNK_CHARS // 3` | Small DDL batches (CREATE INDEX, ALTER TABLE) below this size are grouped together. |
| Header/body splitting | Procedure signature -> `procedure_header`, body sections -> `procedure_body` | Controls how stored procedures are decomposed. |

#### DFM Reader (`shared/readers/dfm_reader.py`)

| Parameter | Current Value | Description |
|-----------|---------------|-------------|
| `MIN_CHUNK_SIZE` | 20 | Minimum chars for a chunk. |
| Small sibling grouping | Consecutive small same-type components merged into `dfm_object_group` | Controls how many small components are grouped together. |
| Context prefix format | `// Form: TfrmMain (MainTurdus.dfm)` | Prefixed to every chunk. |

#### Python Reader (`shared/readers/python_reader.py`)

| Parameter | Current Value | Description |
|-----------|---------------|-------------|
| `MAX_CHUNK_CHARS` | 24000 | Max chars per chunk before split. |
| `MIN_CHUNK_SIZE` | 20 | Minimum chars for a chunk. |
| Leaf/container pattern | Classes with methods recurse; standalone functions are leaf nodes | Controls deduplication — class body is not emitted if its methods are emitted individually. |

#### SQL Reader (`shared/readers/sql_reader.py`)

| Parameter | Current Value | Description |
|-----------|---------------|-------------|
| `MIN_CHUNK_SIZE` | 50 | Minimum chars for a chunk (higher than other readers due to SQL noise). |
| Fallback strategy | Calls `chunk_tsql()` from tsql_chunker instead of TokenTextSplitter | The T-SQL chunker is used when tree-sitter AST parsing produces suboptimal results. |

### 3.2 Embedding

These parameters control how chunks are converted to vectors. Changes here require
reindexing (except query-time model loading settings).

| Parameter | Location | Current Value | Description |
|-----------|----------|---------------|-------------|
| `MODEL_NAME` | `config.py:43` | `jinaai/jina-embeddings-v2-base-code` | Dense embedding model. 768-dim, ALiBi attention, code-optimized. |
| `SPARSE_MODEL_NAME` | `config.py:85` | `Qdrant/bm25` | Sparse model. Pure lexical matching, zero VRAM. |
| `EMBED_MAX_SEQ_LENGTH` | `config.py:63` | 4096 | Max tokens per chunk. Trades truncation vs VRAM. At 4096, the ALiBi bias tensor is ~384 MB. At 8192 it's ~1.5 GB. |
| `DENSE_EMBED_BATCH_SIZE` | `config.py:69` | 32 | Max chunks per dense embedding batch (by count). |
| `SPARSE_EMBED_BATCH_SIZE` | `config.py:70-72` | 32 | Max chunks per sparse embedding batch. |
| `EMBED_BATCH_MAX_TOKENS` | `config.py:73-75` | 16000 | Max approximate tokens per batch (chars / 4). This is the effective VRAM governor. |
| `EMBED_MODEL_KWARGS` | `config.py:52-54` | `{"torch_dtype": "float16"}` | Model loading kwargs. float16 saves VRAM and is correct for this model. |
| `HYBRID_EMBED_SINGLE_PASS` | `config.py:93` | `False` | Two-pass embedding: dense first (save to SQLite), unload, then sparse. Saves VRAM. |
| `INDEX_EMBED_DEVICE` | `config.py:95` | `cuda` | Device for indexing. |
| `MCP_EMBED_DEVICE` | `config.py:96` | `cpu` | Device for MCP server query-time embedding. |
| `trust_remote_code` | `shared/embedding.py` | `True` | **MANDATORY.** Without it, Jina's custom JinaBertModel loads as generic BertModel with garbage weights. |
| Document sort strategy | `shared/embedding.py` | Longest-first | Batches are sorted by document length for optimal GPU utilization (minimizes padding waste). |
| VRAM check threshold | `shared/embedding.py` | 90% | `cuda_vram_check()` clears cache when dedicated VRAM exceeds this fraction. |

### 3.3 Query / Retrieval

These parameters are tunable without reindexing. Changes take effect immediately on the
next MCP query.

| Parameter | Location | Current Value | Description |
|-----------|----------|---------------|-------------|
| `HYBRID_ALPHA` | `config.py:88` | 0.5 | Dense/sparse weight. 0.0 = all sparse, 1.0 = all dense. **Do not change without full validation.** |
| `OVERFETCH_MULTIPLIER` | `shared/reranker.py:42` | 5 | For overview queries, fetch 5x candidates then rerank and trim. |
| `_PRIMARY_OVERVIEW_BONUS` | `shared/reranker.py:226` | +0.50 | Score boost for class_overview, class_summary, class_summary_split. |
| `_OVERVIEW_BONUS` | `shared/reranker.py:220` | +0.25 | Score boost for dfm_form_header, procedure_header, function_header, etc. |
| `_TARGET_MATCH_BONUS` | `shared/reranker.py:238` | +0.15 | Score boost for chunks matching the target file/class identifier. |
| `_NON_TARGET_OVERVIEW_PENALTY` | `shared/reranker.py:244` | -0.20 | Penalty for overview chunks from non-target files (cross-file interlopers). |
| `_CROSS_FILE_COMMENT_PENALTY` | `shared/reranker.py:241` | -0.30 | Penalty for comment chunks from non-target files. |
| `_DETAIL_PENALTY` | `shared/reranker.py:247` | -0.05 | Mild penalty for detail chunk types (defProc, method_group, etc.). |
| Overview query patterns | `shared/reranker.py:50` | 18 regex patterns | Controls which queries trigger the overview reranking pipeline. |
| Target identifier extraction | `shared/reranker.py:141-152` | Pascal T-prefix, file stems, SQL proc names | Controls how the reranker identifies which file/class the user is asking about. |

### 3.4 Model Selection

Changing models is a major operation. Document it as a separate iteration.

| Option | Status | Notes |
|--------|--------|-------|
| `jinaai/jina-embeddings-v2-base-code` | **Current (stable)** | 768-dim, ALiBi, code-optimized. Requires trust_remote_code=True, transformers 4.x. |
| `BAAI/bge-m3` | Previously tested | 1024-dim. Was used before jina. Larger vectors, different embedding space. |
| Different sparse model (SPLADE, etc.) | Not tested | BM25 is zero-VRAM and works well. SPLADE uses GPU VRAM and was tested at 22% utilization — CPU-bound via ONNX Runtime. |
| `float16` vs `float32` | float16 is correct | float32 only prevents arithmetic underflow in intermediates. Does not improve model capacity. The embeddings for degenerate inputs are noise either way. |

---

## 4. Measurement Tools

### 4.1 RAG Validation Test Suite

**File:** `docs/rag-validation-tests.md` (to be created if not present)

The definitive quality measurement. A set of queries organized by category with expected
results (which chunk types, which files, which positions). Each query has a PASS/PARTIAL/FAIL
criterion.

**Categories should include:**

| Category | Example Query | What It Tests |
|----------|---------------|---------------|
| Class overview | "What is TdmMain?" | class_summary / class_overview chunks surface |
| File overview | "Classes in emar105?" | File-level class_summary chunks |
| Form overview | "Splash form components" | dfm_form_header chunks |
| Exact identifier | "PrepareDataSet" | Precise method/variable location |
| Constant lookup | "REPORT_TYPE_PUNCTUALITY_RIDES" | declConst / declVar chunks |
| SQL procedure | "SLS_ReliefExport_Bilety_Get" | procedure_header / procedure_body |
| Uses clause | "uses clause MainDM" | declUses chunks |
| DFM component | "TClientDataSet cdsStoredProc" | DFM object/group chunks |
| Cross-file | "OpenConnection" | Results from multiple files ranked correctly |

### 4.2 Query Test Index (`query_test_index.py`)

The existing manual evaluation harness. Connects to the Qdrant index, runs predefined
queries, and prints results with scores, node_types, and metadata.

```bash
# Run with default alpha
python query_test_index.py

# Override alpha for A/B testing
python query_test_index.py --alpha 0.5
python query_test_index.py --alpha 0.7
```

### 4.3 GPU Stats Collector (`shared/gpu_stats.py`)

Background thread that samples GPU metrics every N seconds into a CSV file.

**Columns:** `timestamp, gpu_util_%, mem_util_%, dedicated_used_mib, dedicated_total_mib, shared_used_mib, temp_c`

```bash
# Enable during indexing
python index_rag.py --collect-perf-stats

# Output: gpu_stats.csv in the index directory
```

**Key metrics to extract from the CSV:**

| Metric | How to Compute | Target |
|--------|----------------|--------|
| Average GPU utilization | Mean of `gpu_util_%` | > 80% |
| Peak dedicated VRAM | Max of `dedicated_used_mib` | < 8000 MiB |
| Average shared VRAM | Mean of `shared_used_mib` | < 1000 MiB (< 1 GB) |
| Time at 0% GPU util (idle) | Count of rows where `gpu_util_%` = 0 / total rows | < 5% |
| Time at >= 90% GPU util (saturated) | Count of rows where `gpu_util_%` >= 90 / total rows | > 50% |

### 4.4 Indexing Log

When `--log-to-file` is passed, the indexer writes a timestamped log file in the index
directory. Key data points to extract:

- Total wall time
- Files scanned / files changed / files deleted
- Chunks generated (by reader, by node_type)
- Truncation count (chunks exceeding `EMBED_MAX_SEQ_LENGTH`)
- Zero-vector / degenerate embedding warnings
- Qdrant upsert timing and error count

### 4.5 Diagnostic Analyzer (`diag_analyze.py`)

Post-run analysis script that parses GPU logs and indexing logs to produce summary
statistics. Use this to compare runs.

### 4.6 Unit Tests

788+ tests across all modules. Run before every production validation:

```bash
.venv\Scripts\python -m pytest -v --tb=short
```

**Note:** The test count grows as new readers and validation tests are added. As of the
test expansion (T45-T56), there are 873+ tests. Check the actual count with pytest output.

---

## 5. Known Constraints and Dead Ends

Things already tried that did not work, or fundamental limitations that cannot be fixed
with parameter tuning. **Do not re-attempt these without a fundamentally different approach.**

### 5.1 Fundamental Limitations

| Constraint | Details |
|------------|---------|
| **ALiBi O(N^2) bias tensor** | The jinaai model materializes a `[1, heads, N, N]` bias tensor every forward pass. At N=4096, this is ~384 MB in float16. At N=8192, it's ~1.5 GB. This is intrinsic to the JinaBertModel architecture and cannot be patched. The only fix is a different model. |
| **trust_remote_code=True** | Mandatory for jinaai/jina-embeddings-v2-base-code. Without it, HuggingFace loads the model as generic BertModel with randomly initialized weights. Embeddings look normal (no errors) but are pure noise. **Never remove this setting.** |
| **transformers must be 4.x** | The Jina model's custom modeling code is incompatible with transformers >= 5.0. Pinned: transformers==4.46.3, huggingface-hub==0.36.2, tokenizers==0.20.3. Upgrading these will silently break the model. |
| **Float16 is correct, float32 does not help** | If model weights are stored as float16, loading in float32 only prevents arithmetic underflow in intermediate values. It does NOT improve the model's ability to understand or differentiate inputs. The embeddings for degenerate inputs (highly repetitive code) will be noise in either precision. |
| **Qdrant uses Relative Score Fusion** | The fusion method for hybrid search is fixed by Qdrant (RSF). Cannot use RRF, custom weighted fusion, or cascading rerank at the Qdrant level. Post-retrieval reranking in Python is the workaround. |

### 5.2 Dead Ends (Tested and Failed)

| Attempt | Result | Why It Failed |
|---------|--------|---------------|
| `HYBRID_ALPHA = 0.7` | **Regression** | Overview queries lost their results. Dense embeddings for large overview chunks are inherently weak (too many tokens, diluted semantics). The 50/50 balance lets BM25 keyword matching compensate. |
| Aggressive per-batch CUDA cache clearing | **Performance collapse** | Clearing the CUDA cache after every batch forces reallocation. Throughput dropped dramatically. The current approach: clear only when VRAM exceeds 90% threshold. |
| SPLADE sparse model (Splade_PP_en_v1) | **22% GPU util, 51% idle** | ONNX Runtime is CPU-bound on tokenization. GPU sits idle between batches. BM25 (Qdrant/bm25) uses zero VRAM and is fast. |
| Sparse batch_size=96 (with SPLADE) | **VRAM thrashing** | Hit the 8 GB VRAM cliff and started spilling to shared memory. batch_size=64 was the maximum. Moot since we switched to BM25. |
| Dense batch_size=128 (with jina) | **CUDA OOM** | The correctly-loaded JinaBertModel uses significantly more VRAM than the broken generic BertModel. Reduced to 32. |

### 5.3 Open Questions (Worth Investigating)

| Question | Potential Approach | Risk |
|----------|-------------------|------|
| Can pipelined double-buffered batching improve GPU saturation? | Overlap CPU tokenization with GPU inference using ThreadPoolExecutor | Medium — PyTorch releases GIL during GPU kernels, but testing needed |
| Would a dynamic VRAM cap improve throughput? | Monitor VRAM in real time and adjust batch size dynamically | Low — pure performance improvement, no quality impact |
| Are FR3/DPROJ readers producing useful chunks? | Audit chunk content and add to validation suite | Low |
| Can we embed project library docs alongside source code? | Add library docs to SOURCE_DIRS with appropriate readers | Medium — may dilute search if not carefully scoped |

---

## 6. Success Criteria

### Quality (Primary)

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Validation test pass rate | >= 85% | >= 90% | 100% |
| Zero excluded files | Yes (hard requirement) | — | — |
| Overview queries (top-3 has relevant chunk) | >= 80% | >= 90% | 100% |
| Exact identifier queries (top-1 is correct) | >= 90% | >= 95% | 100% |
| No false positives in top-3 | >= 80% | >= 90% | >= 95% |

### Performance (Secondary)

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Production indexing time | < 2.5 hours | < 1.5 hours | < 1 hour |
| Average GPU utilization | > 50% | > 70% | > 85% |
| Average shared VRAM | < 4 GB | < 1 GB | < 200 MB |
| Peak dedicated VRAM | < 8188 MiB | < 7500 MiB | < 6500 MiB |
| CUDA OOM errors | 0 (hard requirement) | — | — |
| Zero-vector warnings | < 0.1% of chunks | < 0.01% | 0 |
| Truncated chunks | < 5% of total | < 1% | 0 |

### Stability (Tertiary)

| Metric | Requirement |
|--------|-------------|
| All unit tests passing | Yes (hard requirement, 873+ tests) |
| Incremental reindex works | Yes (no stale vectors, no missing files) |
| MCP server starts cleanly | Yes (model loads, queries return results) |
| Indexer handles UTF-8 encoding errors | Yes (log warning, skip file, continue) |
| Indexer handles empty/corrupt files | Yes (log warning, skip, continue) |

---

## 7. File Inventory

Quick reference for where things live.

### Core Pipeline

| File | Purpose |
|------|---------|
| `config.py` | All configuration parameters (single source of truth) |
| `config_loader.py` | Config loading with override support |
| `index_rag.py` | Main indexing entry point |
| `rag_mcp.py` | MCP server entry point |
| `query_test_index.py` | Evaluation harness |

### Readers (Chunking)

| File | Language | Key Node Types |
|------|----------|----------------|
| `shared/readers/pascal_reader.py` | Delphi Pascal (.pas, .dpr) | defProc, declProc, class_summary, class_overview, method_group, declUses, declSection, declVar, declConst, comment, declType, declClass |
| `shared/readers/sql_reader.py` | SQL (.sql, tree-sitter path) | create_function, create_procedure, create_trigger, create_view, create_table |
| `shared/readers/tsql_chunker.py` | T-SQL (.sql, fallback path) | procedure_header, procedure_body, function_header, function_body, sql_batch |
| `shared/readers/dfm_reader.py` | DFM forms (.dfm) | dfm_form_header, dfm_object, dfm_object_group |
| `shared/readers/python_reader.py` | Python (.py) | function_definition, class_definition, import_statement, decorated_definition |

### Embedding & Search

| File | Purpose |
|------|---------|
| `shared/embedding.py` | Model loading, batch embedding, VRAM management, sanitization |
| `shared/reranker.py` | Post-retrieval score adjustment for overview queries |
| `qdrant/vector_store.py` | Qdrant connection, collection management, hybrid mode detection |

### Monitoring & Diagnostics

| File | Purpose |
|------|---------|
| `shared/gpu_stats.py` | Background GPU stats CSV collector |
| `diag_analyze.py` | Post-run log analysis |
| `shared/log.py` | Centralized logging (all output goes through here) |

### Tests

| Directory | Count | Coverage |
|-----------|-------|----------|
| `tests/shared/readers/test_pascal_reader.py` | 164 | Integration + unit |
| `tests/shared/readers/test_tsql_chunker.py` | 125 | Unit |
| `tests/shared/test_reranker.py` | 123 | 100% line coverage |
| `tests/shared/readers/test_python_reader.py` | 91 | Integration + unit |
| `tests/shared/readers/test_dfm_reader.py` | 58 | Integration + unit |
| Other test files | 227+ | Various |

---

## 8. Iteration Notes Template

Use this template for `docs/iteration-notes/iteration-NNN.md`:

```markdown
# Iteration NNN — [Short Title]

**Date:** YYYY-MM-DD
**Author:** [human / AI agent]
**Status:** [committed / reverted / in progress]

## Hypothesis

> Changing [X] from [current] to [proposed] should improve [metric] because [reason].

## Changes Made

- File: `path/to/file.py` — description of change
- Config: `PARAM_NAME` changed from X to Y

## Baseline (Before)

| Metric | Value |
|--------|-------|
| Validation pass rate | NN/NN |
| Indexing time | Xh Ym |
| Avg GPU util | NN% |
| Avg shared VRAM | NNN MiB |

## Results (After)

| Metric | Value | Delta |
|--------|-------|-------|
| Validation pass rate | NN/NN | +N / -N |
| Indexing time | Xh Ym | -Nm / +Nm |
| Avg GPU util | NN% | +N% / -N% |
| Avg shared VRAM | NNN MiB | -NNN / +NNN |

## Detailed Test Results

| Query | Before | After | Notes |
|-------|--------|-------|-------|
| What is TdmMain? | PASS | PASS | — |
| ... | ... | ... | ... |

## Conclusion

[Did it work? Why or why not? Any secondary observations?]

## Current Parameter Values (After This Iteration)

[List all parameters that were changed, with their new values. This section makes
the latest iteration file self-contained.]

## Next Steps

[What should the next iteration investigate?]
```

---

## 9. Quick Reference: Common Operations

### Full Reindex with Monitoring

```bash
.venv\Scripts\activate
python index_rag.py --clear --yes --collect-perf-stats --log-to-file
```

### Incremental Reindex (After Code Changes)

```bash
python index_rag.py --collect-perf-stats
```

### Test-Sources Quick Validation

```bash
# Edit config.py to use test_sources SOURCE_DIRS (or use --config test-sources)
python index_rag.py --config test-sources --clear --yes
python query_test_index.py --alpha 0.5
```

### Run All Unit Tests

```bash
.venv\Scripts\python -m pytest -v --tb=short
```

### Run Tests for a Specific Reader

```bash
.venv\Scripts\python -m pytest tests/shared/readers/test_pascal_reader.py -v --tb=short
```

### Check GPU Status

```bash
nvidia-smi
```

### Self-Index (This Project)

```bash
python index_rag.py --config self-index
```

---

## 10. Test Sources Rotation Policy

The `test_sources/` directory is the fast-iteration index used in Step 4. To prevent the
validation suite from overfitting to a fixed set of files, the directory is periodically
refreshed with new files from production.

### Permanent Files (Never Remove)

These files exercise the hardest edge cases and are referenced by many validation tests.
Removing them would invalidate too many tests and lose regression coverage:

| File | Why Permanent |
|------|---------------|
| `MainDM.pas` | Largest class (TdmMain), 150+ published members, class_summary stress test |
| `MainTurdus.pas` | Large form class (TfrmMainTurdus), 500+ components in DFM |
| `emar105.pas` | Multi-class unit, class overview queries |
| `BaseEditorForm.pas` | Abstract base class, inheritance queries, T05 test target |
| `ResourceStrings.pas` | Constants-only unit, declConst queries |
| `FormBasicMain.dfm` | Complex DFM, form component queries |
| `LoginFrm.dfm` | Large DFM (252KB), component count stress test |

### Rotatable Files

All other files in `test_sources/` are candidates for rotation. When rotating:

1. **Frequency:** Every 3-5 iterations, or when the validation score plateaus and overfitting
   is suspected.
2. **How many:** Replace 3-5 files per rotation (keep the total around 35-40 files).
3. **Selection criteria for new files:**
   - Pick files the AI agent has never seen in test_sources before.
   - Include at least one file from each language (Pascal, SQL, DFM).
   - Prefer files that exercise patterns not well covered by existing test_sources
     (e.g., very short units, units with unusual structure, deeply nested DFMs).
4. **When removing a file:** Check that no PASS-level validation test depends solely on that
   file. If it does, either keep the file or update the test to target a different file.
5. **Document the rotation** in the iteration notes (which files were added/removed and why).

### Adding New Validation Tests for New Files

When adding new files to test_sources, also add at least one validation test per new file
to `validate_rag.py` and `docs/rag-validation-tests.md`. This ensures the new files
actually contribute to quality measurement rather than just inflating the index size.
