# Changelog

All notable user-facing changes to this project are listed here, newest first.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
The project has no version numbers yet, so entries are grouped by the date the
change reached `master`.

Every section says whether an existing index has to be rebuilt. "Reindex" means
a full rebuild with `python src/index_rag.py --config <name> --clear --yes`;
query-time changes take effect after restarting the MCP server. Detailed upgrade
tables live in [docs/indexing.md](docs/indexing.md#upgrading--migration-notes-indexing-pipeline).

## 2026-10-18

### Added
- **Exact symbol lookup.** When a query names a code identifier (`snake_case`,
  `camelCase`, `Owner::member`, `struct foo`, `foo()`), chunks that declare that
  name are added to the reranker candidates. Settings: `SYMBOL_LOOKUP_K = 4`
  (0 = off), `SYMBOL_LOOKUP_FIELDS = ["object_name", "symbols"]`,
  `SYMBOL_LOOKUP_SCORE = "top"`. The lookup reuses the query embedding and runs
  concurrently with the hybrid search, so it adds almost no latency.
- **Deeper hybrid fusion.** `HYBRID_PREFETCH_K = 100`: the dense and sparse
  legs each fetch 100 candidates before fusion, so chunks that rank moderately
  in both legs can still reach the reranker.
- **Pool-level rerank rules** ([docs/reranker.md](docs/reranker.md#pool-level-rules)),
  on by default: mention penalty from the language profile
  (`RERANK_PROFILE_MENTION = True`), enum/flag intent (`RERANK_TYPE_INTENT = True`),
  at most 2 results per file for "A and B" queries (`RERANK_FILE_CAP = 2`),
  demotion of `tests/` and `tools/` paths (`DEPRIORITIZED_PATHS`,
  `DEPRIORITIZED_PATH_PENALTY = 0.10`) and prototypes yielding to definitions
  (`RERANK_PROTOTYPE_YIELD = 0.3`).
- C/C++ reader: leading comments and kernel-doc/Doxygen blocks join the
  declaration below them; functions defined through macros become function
  chunks; file-scope initialized tables become their own chunks (large ones are
  cut, not split); annotation macros no longer break parsing; `.h` files fall
  back to the C grammar when it parses better; large parse-error regions are
  recovered; grouped chunks record every defined name in a `symbols` payload.
- `QDRANT_TIMEOUT = 60` (seconds): Qdrant client timeout.
- `QDRANT_UPSERT_MAX_BYTES` (16 MiB): upsert requests are capped by size; a
  rejected or timed-out batch is halved and retried.
- Validation: `--set KEY=VALUE` overrides, a doc-hint metric and per-query
  latency in the JSON output.

### Changed
- TEI defaults: URL `http://127.0.0.1:{TEI_DOCKER_PORT}` instead of `localhost`,
  `TEI_CONCURRENT_REQUESTS = 16` (was 64); transient TEI errors are retried
  with backoff.
- Qdrant containers created by the tool start with telemetry disabled.
- Validation no longer gives partial credit for a `node_type` match alone when
  a test sets a `file_pattern`. Suites that relied on it score lower.

### Upgrade notes
- Retrieval and rerank changes are query-time only: **no reindex**. The symbol
  lookup works on any index via `object_name`; `symbols` is only filled by the
  new C/C++ reader. Keyword payload indexes for both fields are created for new
  collections only; existing collections work without them.
- **Reindex indexes that contain C/C++ files** to get the new C/C++ chunks
  (otherwise only changed files get them).
- Restore the previous ranking with:
  ```python
  HYBRID_PREFETCH_K = None
  SYMBOL_LOOKUP_K = 0
  RERANK_PROFILE_MENTION = False
  RERANK_TYPE_INTENT = False
  RERANK_FILE_CAP = 0
  DEPRIORITIZED_PATHS = []
  RERANK_PROTOTYPE_YIELD = 0.0
  ```
- To apply the telemetry setting, recreate an older Qdrant container on the
  same storage.

## 2026-10-17

### Added
- Readers for **C#** (`.cs`), **Go** (`.go`) and **PHP** (`.php`; Blade and
  `.phtml` templates are indexed as text). More C++, JS/TS, Python and script
  extensions are routed to their readers; `.tsx` uses the TSX grammar.
- **Reranker profiles:** a generic, language-neutral core plus per-reader
  profiles, and query-intent rules for identifiers, tests, bindings and
  declarations ([docs/reranker.md](docs/reranker.md)).
- **Tag overlays:** a moving git tag (for example `current_release`) can be
  indexed as an overlay holding only the files that differ from the main tip.
  Configure it under `overlays` with `kind: "tag"` and
  `diff: "against_main_tip"`; search it with `branch="<tag name>"`
  ([docs/git-overlays.md](docs/git-overlays.md)). `git_pull_guard.py`
  force-updates configured tags from `origin`.
- Unchanged overlays are skipped without reading files; log lines are prefixed
  `[BRANCH]` or `[TAG]`.

### Changed
- Python reader rewritten on the Java/Kotlin conventions (class summaries,
  methods, fields, import groups).
- JS/TS: a JSDoc or `//` block directly above a declaration is now part of that
  declaration's chunk instead of a separate comment chunk.
- Per-line `//` comments are merged into one comment block (C#, Go, PHP).
- Overlay `kind` defaults to `"branch"`; the legacy `branches` list keeps
  working unchanged.

### Fixed
- Kotlin: functions and classes whose `where` clause starts on a new line kept
  losing the clause, their body and their class context.
- `git_pull_guard.py` reported failed fetches and fast-forwards as successful.

### Upgrade notes
- New readers: add the extensions to `SOURCE_DIRS` and run the indexer.
- **Reindex** indexes that contain Python, JS/TS or Kotlin files to get the new
  chunks.
- Reranker changes are query-time only: no reindex; re-run your validation
  suites.
- Existing branch overlays need no change and no rebuild; old overlay manifests
  get one full compare on the next run.

## 2026-10-14

### Added
- **Kotlin** reader (`.kt`, `.kts`) with the same chunk headers as Java
  ([docs/kotlin-chunking.md](docs/kotlin-chunking.md)).

### Changed
- Nested Java and Kotlin classes show the outer-class chain
  (`Outer > Inner`) in the `// Class:` header.

### Upgrade notes
- **Reindex** indexes that contain Java files to get the new nested-class
  headers.

## 2026-10-11

### Added
- **OpenAI-compatible embedding backend** for any `/v1/embeddings` server such
  as llama.cpp `llama-server`: `EMBED_BACKEND = "openai"` with `USE_TEI = False`,
  `OPENAI_EMBED_URL` (default `http://localhost:8092`), `OPENAI_EMBED_MODEL`
  (defaults to `MODEL_NAME`), `OPENAI_EMBED_MAX_TOKENS = 4000` (longer inputs are
  truncated server-side) and optional `OPENAI_EMBED_ENDPOINTS` to spread requests
  over several servers ([docs/installation.md](docs/installation.md)).
- PyTorch backend: query/text prefixes, `EMBED_CONFIG_KWARGS` and
  `EMBED_TRUNCATE_DIM` (Matryoshka dimension), enough for EmbeddingGemma-style
  models.
- **Pipelined embedding** (opt-in): `EMBED_PIPELINE_DEPTH = 0` by default; e.g.
  `6` overlaps dense embedding with sparse embedding, upserts and parsing, which
  helps TEI on a GPU (little gain on CPU).
- `EMBED_PARSE_QUEUE_SIZE = 400` (was fixed at 2) and a configurable
  `QDRANT_UPSERT_BATCH_SIZE = 500`.
- VRAM tuning guide ([docs/vram-tuning.md](docs/vram-tuning.md)).

### Changed
- `--clear` also deletes overlay manifests, so overlays are rebuilt after a
  clear.

### Upgrade notes
- No reindex: the pipelined and sequential paths produce identical points.
  Switching to a different embedding model always requires a reindex.
- Exact previous behaviour: `EMBED_PIPELINE_DEPTH = 0`,
  `EMBED_PARSE_QUEUE_SIZE = 2`.

## 2026-10-08

### Added
- **C/C++** reader (`.c`, `.cpp`, `.h`) with class summaries and one chunk per
  function, and a Qt `.ui` form reader.
- Per-path `sql_dialect`: `tsql` (default) or `postgresql`.
- Validation suites can be loaded from an external YAML file (`--tests`).

### Upgrade notes
- No reindex: omitting `sql_dialect` keeps T-SQL chunking. Changing the dialect
  reindexes only the `.sql` files on that path.

## 2026-10-01

### Changed
- The project is relicensed under the **Apache License 2.0**, including
  versions previously released under AGPLv3. The unused AGPL `pymupdf`
  dependency was removed.

## 2026-08-09

### Added
- `get_index_state` MCP tool: last index time, indexed commits, overlays, point
  count and whether `HEAD` still matches the index (reads manifests only).
- Portable launcher for the self-index MCP server.

## 2026-06-06

### Added
- **Groovy** reader (`.groovy`).

## 2026-04

### Fixed
- TEI container creation on CUDA 12.4 and older drivers.
- `git_pull_guard.py` fast-forwards all configured branches, not only the one
  checked out.
- Default TEI embedding timeout raised to 600 s.
- Renamed and copied files in branch overlays no longer cause repeated
  warnings.
- The git-diff fast path of incremental refresh missed uncommitted edits in
  the working copy.

### Changed
- Dependencies are pinned.

## 2026-03

### Added
- **Git branch overlays:** index feature branches as small overlays on top of
  the main branch and search them with the MCP `branch` argument; repo groups
  with configured branches (`type: "git_repo"` in `SOURCE_DIRS`).
- **TEI** (Text Embeddings Inference) as the default embedding backend
  (`USE_TEI = True`), also on CPU; multi-GPU support (best GPU picked by free
  VRAM).
- Faster indexing: cross-file chunk pooling, concurrent TEI requests, a
  parse-ahead thread and deferred HNSW building during bulk ingest.
- Git-diff fast path for incremental refresh and `--dry-run` mode.
- Readers for **Java**, **JavaScript/TypeScript**, Hibernate `.hbm.xml` and
  JasperReports `.jrxml`.
- Cron helpers: `refresh_guard.py`, `git_pull_guard.py`, `git_pull_all.py`.
- Retrieval validation framework with per-config YAML suites.
- `QDRANT_DELETE_TIMEOUT`.

### Changed
- `QDRANT_MODE = "local"` / `"remote"` replaces `QDRANT_USE_DOCKER`.
- Project layout: sources in `src/`, configs in `project-configs/`,
  requirements in `requirements/`.
- Chunking strategy overhauled; manifests are portable across operating
  systems (CRLF-insensitive hashes, platform-independent keys).

## 2026-02-28 – 2026-03-08

### Added
- Initial release: local RAG indexer and MCP server (stdio and HTTP) for
  Delphi/Pascal, DFM forms, SQL (including T-SQL procedures) and FastReport.
- Qdrant backend with hybrid dense + sparse (BM25-style) search, incremental
  refresh driven by a manifest, path mapping and path excludes.
