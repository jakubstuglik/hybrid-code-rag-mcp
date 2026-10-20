# Indexing

## Build or refresh an index

```bash
# Incremental refresh (only re-embeds changed files)
python src/index_rag.py --config my_project --yes

# Full rebuild (clear + reindex)
python src/index_rag.py --config my_project --clear --yes

# Self-index (this project's own code)
python src/index_rag.py --config self-index --yes

# Any other config, by name or by path to its config.py
python src/index_rag.py --config project-configs/my_project/config.py --yes
```

## CLI parameters

```
--config CONFIG        Config name or path (required for meaningful operation)
--yes                  Skip all confirmations
--clear                Clear the collection and manifest before indexing (requires --yes)
--verbose              Print verbose refresh diagnostics and chunk counts
--regenerate-manifest  Rebuild manifest by scanning existing vector store
--log-to-file          Also log to a timestamped file in the index directory
--collect-perf-stats   Collect GPU stats via nvidia-smi during indexing (CUDA only)
--dry-run              Compute file actions without embedding (diagnostic mode)
--calculate-histogram  Generate chunk histograms without embedding or Qdrant
```

## Indexing Pipeline

The indexer uses a multi-layered optimization pipeline to maximize GPU utilization:

1. **Cross-file chunk pooling** -- chunks from multiple files are accumulated into a pool (up to `EMBED_POOL_SIZE` chunks or `EMBED_POOL_MAX_FILES` files), then sorted by length for homogeneous batching. This eliminates padding waste and GPU starvation from small per-file batches.

2. **Concurrent TEI embedding** -- pool chunks are split into mini-batches of 8 and submitted to TEI via 16 concurrent HTTP requests by default (`TEI_CONCURRENT_REQUESTS`; multiplied by `EMBED_PIPELINE_DEPTH` when pipelining). TEI's internal Rust scheduler receives all requests near-simultaneously and forms optimal GPU work units.

3. **Parse-ahead thread** -- a background thread reads and parses the next files (tree-sitter, node building, ID generation) while the main thread embeds the current pool. Since tree-sitter is a C extension that releases the GIL, true parallelism is achieved.

4. **HNSW deferral** -- during bulk ingest, HNSW graph building is deferred (`indexing_threshold=200000`) to eliminate SSD I/O contention from Qdrant's background optimizer. Restored to default after all upserts complete.

5. **Double-buffered Qdrant upserts** -- previous pool's Qdrant upsert runs on a background thread while the next pool is being embedded. Cross-file batch upserts (`QDRANT_UPSERT_BATCH_SIZE`, 500 points per call) replace per-file upserts.

6. **Pipelined embedding (opt-in)** -- with `EMBED_PIPELINE_DEPTH > 0`, dense embedding of several pools overlaps with sparse embedding, node building, Qdrant upserts and parsing of the next files, so the GPU does not idle between pools. Off by default (`0`); e.g. `6` is a good value for TEI on a GPU. See [Upgrading / migration notes](#upgrading--migration-notes-indexing-pipeline).

Set `EMBED_POOL_SIZE = 0` to disable pooling and revert to per-file embedding.

## Performance

What to expect from the pipeline optimizations, measured as a full rebuild of a mid-sized codebase (on the order of ten thousand files and a hundred thousand or more vectors) with a small (~150M-parameter) code embedding model served by TEI in float16 on a 12 GB consumer GPU. Treat the figures as orders of magnitude; your results depend on the codebase, the model and the GPU.

| Metric | Original per-file baseline | All optimizations |
|--------|----------------------------|-------------------|
| **Total indexing time** | 1x | **about 0.5x** (roughly half) |
| GPU mean utilization | under half | about two thirds |
| GPU median utilization | about a third | close to 90% |
| Chunks/sec (wall clock) | 1x | **about 2x** |
| Retrieval quality (validation score) | reference | unchanged within run-to-run noise |

See `docs/features/tei-batch-saturation/implementation-report.md` for the full phase-by-phase breakdown.

## Upgrading / migration notes (indexing pipeline)

Existing project configs keep working unchanged and, by default, keep the previous sequential indexing behaviour. A project `config.py` only overrides the names it defines; everything else comes from the root `config.py`, so older configs pick up the defaults below automatically.

**New parameters and defaults**
- `EMBED_PIPELINE_DEPTH = 0`: pipelined embedding is **opt-in**. `0` runs the previous sequential (serial flush) code path. With `N > 0`, dense embedding of up to `N` pools overlaps with sparse embedding, node building, Qdrant upserts and parsing of the next files. With TEI, up to `N` pools are embedded concurrently; in-process backends (PyTorch/OpenVINO) still use a single dense worker. Enable it where the GPU idles between pools, typically TEI on a GPU:
  ```python
  EMBED_PIPELINE_DEPTH = 6
  ```
- `EMBED_PARSE_QUEUE_SIZE = 400`: number of parsed files the parse-ahead thread may buffer ahead of embedding (previously fixed at 2). It is used with **any** pipeline depth, including `0`, so older configs get the larger queue too. It only lets the parser run further ahead and costs host RAM; it does not change results. With the pipeline enabled it should stay large, otherwise the next pool is not ready when a slot frees up. Set `2` for the exact previous behaviour.
- `QDRANT_UPSERT_BATCH_SIZE = 500`: points per Qdrant upsert call, now configurable (same value as before).

**Exact previous behaviour**
```python
EMBED_PIPELINE_DEPTH = 0   # default
EMBED_PARSE_QUEUE_SIZE = 2
```

**TEI on CPU**
On CPU almost all the time goes to dense embedding, so pipelining gives little or no speed-up. Recommended:
```python
EMBED_PIPELINE_DEPTH = 0      # keep the default
EMBED_POOL_SIZE = 256         # keep well below TEI --max-concurrent-requests (default 512)
TEI_DTYPE = "float32"
TEI_MAX_BATCH_TOKENS = 4096   # TEI --max-batch-tokens; limits host RAM of the container
```
HTTP 429 ("Model is overloaded") from TEI means more requests are in flight than TEI accepts. A pool can overshoot `EMBED_POOL_SIZE`, because the last file is added whole. Lower `EMBED_POOL_SIZE` and/or `TEI_CONCURRENT_REQUESTS`, or raise `--max-concurrent-requests` on the container. This can happen with the sequential path (`EMBED_PIPELINE_DEPTH = 0`) as well, not only with the pipeline.

**Memory**
VRAM per forward pass is unchanged by these parameters (one PyTorch dense worker; TEI batches stay bounded by `--max-batch-tokens`). Host RAM grows with `EMBED_PIPELINE_DEPTH` (pools in flight) and `EMBED_PARSE_QUEUE_SIZE` (parsed files buffered); lower them on machines with little RAM.

**Reindexing**
Not needed. The pipelined and sequential paths produce identical points and vectors, and existing collections and manifests stay compatible. `--clear` now also removes overlay manifests (branch and tag), so overlays are fully rebuilt after a clear.

### Upgrading: new readers, JS/TS doc comments and the reranker

| Change | Reindex? |
|---|---|
| New readers for C# (`.cs`), Go (`.go`), PHP (`.php`) and the new C/C++, JS/TS, Python and script extensions | Only to start indexing them: add the extensions to `SOURCE_DIRS` and run the indexer |
| Python reader rewrite (class summaries, methods, fields, import groups) | `--clear` for indexes that contain `.py` / `.pyi` files |
| JS/TS: a JSDoc / `//` block directly above a declaration is now part of that declaration's chunk instead of a separate `comment` chunk | `--clear` for indexes that contain JS/TS files (otherwise only changed files get the new chunks) |
| Reranker: generic core + per-language profiles, query-intent rules ([reranker.md](reranker.md)) | No: query-time only. Re-run your validation suites |

### Upgrading: retrieval defaults, C/C++ reader and indexer robustness

| Change | Reindex? |
|---|---|
| Deeper hybrid fusion (`HYBRID_PREFETCH_K = 100`), exact symbol lookup (`SYMBOL_LOOKUP_K = 4`) and pool-level rerank rules (mention penalty, enum/flag intent, per-file cap, `tests/` and `tools/` demotion, prototype yield) are **on by default** ([reranker.md](reranker.md#pool-level-rules)) | No: query-time only. The symbol lookup reads `object_name` on every index and `symbols` on C/C++ indexes built with the new reader. To get the previous ranking, set `HYBRID_PREFETCH_K = None`, `SYMBOL_LOOKUP_K = 0`, `RERANK_PROFILE_MENTION = False`, `RERANK_TYPE_INTENT = False`, `RERANK_FILE_CAP = 0`, `DEPRIORITIZED_PATHS = []`, `RERANK_PROTOTYPE_YIELD = 0.0` |
| C/C++ reader: leading comments and kernel-doc / Doxygen blocks join the function, struct, enum or macro below them; functions defined through a macro (`NAME(args) { ... }`) become `cpp_function` chunks; file-scope initialized tables become `variable_definition` chunks (large ones are cut, not split); annotation macros between `)` and `{` no longer break parsing; `.h` files fall back to the C grammar when that parses better; large parse-error regions are recovered; groups record every defined name in `symbols` | `--clear` for indexes that contain C/C++ files (otherwise only changed files get the new chunks) |
| Keyword payload indexes on `object_name` and `symbols` for the symbol lookup | Created for new collections only; existing collections work without them |
| Qdrant upserts are capped by request size (`QDRANT_UPSERT_MAX_BYTES`, 16 MiB) and a rejected or timed-out batch is halved and retried; client timeout `QDRANT_TIMEOUT = 60` s | No. Upserts are idempotent (same point ids), so the index content is identical |
| TEI: default URL `http://127.0.0.1:{TEI_DOCKER_PORT}` instead of `localhost`, `TEI_CONCURRENT_REQUESTS = 16` (was 64), transient errors retried with backoff | No |
| Qdrant containers created by the tool start with telemetry disabled | No; recreate an older container on the same storage to apply it |
| Validation: no partial credit for a `node_type` match alone when the test sets a `file_pattern`; doc-hint metric, per-query latency and `--set KEY=VALUE` overrides ([validation guide](validation/validation-tests-guide.md#evaluation-logic)) | No. Scores of suites that depended on type-only partial credit go down |

### Upgrading: C/C++ reader and ranking fixes (0.11.0)

| Change | Reindex? |
|---|---|
| C/C++ reader: a function body the grammar could not close no longer swallows the rest of the file (cut at the next column-0 `}`, rest parsed again); one-argument macro functions (`SYSCALL_DEFINE0(getpid)`, `DEFINE_IDTENTRY(exc_x)`) are named; `sys_<name>` aliases in `symbols` for `SYSCALL_DEFINEn`; attribute macros before the name no longer break the header; functions returning function pointers are named | `--clear` for indexes that contain C/C++ files (otherwise only changed files get the new chunks) |
| C/C++ ranking: type summaries yield to function bodies in behaviour queries (`RERANK_BODY_PREFERENCE`); `__name` identifiers in queries feed the declared-name rules and the symbol lookup | No: query-time only. `RERANK_BODY_PREFERENCE = 0` restores the previous ranking |

### Upgrading: gitignore, batched deletes and parse workers (0.12.0)

| Change | Reindex? |
|---|---|
| `RESPECT_GITIGNORE = True` (default): `git_repo` sources skip files ignored by git; tracked files stay | **No full `--clear`.** The **first refresh** after upgrading deletes vectors for paths that are now gitignored. Set `RESPECT_GITIGNORE = False` to keep indexing them |
| `QDRANT_DELETE_CHUNK_SIZE = 500`: refresh batches delete-by-filter calls | No. Same deletes, fewer round-trips |
| `INDEX_PARSE_WORKERS = 1` (default): sequential parse-ahead; set e.g. `8` for a thread pool | No. Same chunks and point IDs when ordered |

### Upgrading: version numbers (0.10.0)

Read the [changelog](../CHANGELOG.md) before upgrading: every release says
whether a reindex or a config change is needed. From 0.10.0 the indexer writes
`indexer_version` and `first_indexer_version` to `index_manifest.json`.
Manifests without these fields load and refresh normally and get them on the
next run; no reindex is needed. Entries of repositories removed from
`SOURCE_DIRS` are dropped from `repo_commits` on the next run.

### Project-specific identifier abbreviations (SQL descriptions)

The T-SQL and PostgreSQL chunkers add a `-- Description:` line that spells out
identifier parts (`RPT_DailyExport_Get` -> "Report Daily Export Get"). Only
generic abbreviations are built in. To expand your own module prefixes or
non-English words, put them in a JSON object and set `HCR_ABBREVIATIONS_FILE`
to its path before indexing, e.g. `{"ACC": "Account", "Artikel": "Article"}`.
Upper-case keys match any casing; other keys match exactly. Re-index the SQL
files (`--clear`) after changing the file.

## Cron & Automation

Two wrapper scripts provide cron-safe operation with concurrency guards:

### refresh_guard.py

Prevents concurrent `index_rag.py` runs. Intended for hourly cron invocation.

- Skips this run if a prior one is still active (skip counter persists across invocations)
- Kills the stale process after 3 consecutive skips
- State stored in `refresh_guard_state.json` next to the Qdrant index

```bash
python src/refresh_guard.py --config my_project --yes
```

### git_pull_guard.py

Pulls all `git_repo` sources before indexing. Run before `refresh_guard.py` in cron.

- Runs `git fetch --all --prune` on every `git_repo` entry in the config
- Creates tracking branches for configured branches not yet present locally
- Force-updates each configured tag overlay from `origin` (`git fetch origin +refs/tags/<name>:refs/tags/<name>`); if that fails it logs a warning and the local tag is used
- Pulls the current branch (if tracked); skips detached HEAD
- Parallel pull (up to 4 workers) across all repos
- Same skip/kill guard as `refresh_guard.py`

```bash
python src/git_pull_guard.py --config my_project
```

### git_pull_all.py

Simple, no-frills `git pull` for all `git_repo` entries. No concurrency guard. It does not move tag overlays; use `git_pull_guard.py` for that.

```bash
python src/git_pull_all.py --config my_project
```

### Recommended crontab

```bash
0 * * * * cd /home/user/hybrid-code-rag-mcp && \
    .venv/bin/python src/git_pull_guard.py --config my_project >> /home/user/git_pull.log 2>&1 && \
    .venv/bin/python src/refresh_guard.py --config my_project --yes --log-to-file --collect-perf-stats >> /home/user/index_refresh.log 2>&1
```

## RAG Validation

Per-config YAML validation suites verify search quality. Test cases are defined in `project-configs/<config_name>/validation_tests.yaml`:

```bash
# Run all validation tests
python src/validate_rag.py --config my_project

# Run a specific category
python src/validate_rag.py --config my_project --category "Class & Unit Overview"

# Run a single test by ID
python src/validate_rag.py --config my_project --test T05

# List all tests without running
python src/validate_rag.py --config my_project --list

# Verbose output with chunk details
python src/validate_rag.py --config my_project --verbose

# JSON output for CI
python src/validate_rag.py --config my_project --json
```

See `docs/validation/validation-tests-guide.md` for the YAML test authoring guide.
