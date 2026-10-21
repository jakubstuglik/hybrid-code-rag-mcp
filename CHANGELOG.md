# Changelog

All notable user-facing changes to this project are listed here, newest first.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/) in its 0.x form.
Each release is tagged `vX.Y.Z` in git. The running version is printed by
`python src/index_rag.py --version`, logged when the indexer or the MCP server
starts, recorded in `index_manifest.json` and shown by `get_index_state`.

## Versioning rules

- **PATCH** (0.9.**1**): fixes that change neither search results nor config.
- **MINOR** (0.**10**.0): new features, new settings, changed defaults or
  behaviour that work on an existing index.
- **Reindex required or config incompatible:** a MINOR bump while the project
  is below 1.0, flagged with **Reindex required** or **Config change required**
  in the upgrade notes. From 1.0 on, such changes bump MAJOR.

"Reindex" means a full rebuild with
`python src/index_rag.py --config <name> --clear --yes`. Query-time changes take
effect after restarting the MCP server. Detailed upgrade tables live in
[docs/indexing.md](docs/indexing.md#upgrading--migration-notes-indexing-pipeline).

## [Unreleased]

### Added
- `MANIFEST_SAVE_INTERVAL_S` (default `0`): throttle for manifest saves
  during indexing. `0` keeps the previous behaviour (save after every batch
  of processed files, on the main thread). A positive value saves at most
  every N seconds on a single background thread from a shallow snapshot, as
  compact JSON written to a temp file and renamed into place; the end of a
  run and a failed run (exception or Ctrl+C) always save synchronously.
  Applies to main-branch, refresh and branch/tag overlay runs. On large
  indexes the per-batch full rewrite dominated the indexer's main thread and
  left the GPU idle.
- Every manifest save logs its size and duration (`[MANIFEST] ...`), and each
  indexing run logs a save summary.

### Upgrade notes
- No reindex and no config change needed. Existing manifests load
  unchanged; compact manifests written with a positive interval load in
  older versions too.

## [0.12.0] - 2026-10-20

### Added
- `INDEX_PARSE_WORKERS` (default `1`): opt-in parallel parsing/chunking in
  the indexer. `1` keeps the sequential parse-ahead path; set e.g. `4` or `8`
  to use a thread pool. Results stay in file order, so chunks and point IDs
  match the sequential path. On embedding-bound runs it gave no speedup: a
  full index of a ~64k-file C repository took about the same wall time with
  8 workers as with 1 (8 workers were ~5% slower), because the GPU embedding
  stage, not parsing, sets the pace. Leave it at `1` unless parsing is your
  bottleneck.
- `RESPECT_GITIGNORE` (default `True`): for `git_repo` sources the indexer
  skips files ignored by git (`.gitignore`, nested ignore files,
  `.git/info/exclude`, and the global excludes file) by asking
  `git check-ignore`. Tracked files always stay. Non-git sources are
  unchanged.
- `QDRANT_DELETE_CHUNK_SIZE` (default `500`): refresh deletes batch
  `file_path` values into one `MatchAny` filter call per chunk instead of
  one delete per file.
- Tests for the gitignore filter, batched deletes and `INDEX_PARSE_WORKERS`
  (fake Qdrant and embedding; no GPU or running services needed).

### Changed
- **Migration (`RESPECT_GITIGNORE`):** the first refresh after upgrading
  removes vectors for gitignored paths from existing indexes (they are no
  longer in the scanned file set, so refresh treats them as deletes). Set
  `RESPECT_GITIGNORE = False` in the project config to keep the previous
  behaviour (only the explicit per-source `exclude` list applies).

### Fixed
- Refresh no longer drops a manifest entry when the Qdrant delete for that
  file (or delete chunk) fails, so the manifest stays aligned with the
  collection.

### Upgrade notes
- **No reindex required.** With the new default `RESPECT_GITIGNORE = True`,
  the first refresh after upgrading deletes vectors (and manifest entries)
  for paths of `git_repo` sources that git ignores; tracked files stay. Set
  `RESPECT_GITIGNORE = False` in the project config to keep indexing them.
  `QDRANT_DELETE_CHUNK_SIZE` and `INDEX_PARSE_WORKERS` need no action.

## [0.11.0] - 2026-10-19

### Added
- C/C++ rerank profile: for behaviour queries ("handle a page fault for a
  VMA", "how is a socket buffer freed") struct / class summaries yield to
  function bodies when a body of the same language is in the candidate pool
  (`summary_yield` 0.15, scaled by the new `RERANK_BODY_PREFERENCE`, default
  `1.0`, `0` = off). Not applied when the query asks about a structure, type,
  field, macro, flag or declaration, or names an identifier the summary
  declares or mentions (a field such as `max_open_files`). Other languages
  are not affected.
- Rerank profiles can add identifier shapes for queries
  (`query_identifier_patterns`). The C/C++ profile recognises reserved names
  with a leading double underscore (`__alloc_pages_slowpath`, `__schedule`),
  so the declared-name rules and the exact symbol lookup see them. Dunder
  names such as `__init__` are not matched, and projects without C/C++
  sources are unchanged.

### Changed
- Docs: `DEPRIORITIZED_PATHS` set per project for source trees that are
  rarely the answer, for example `*/arch/<arch>/*` for every architecture in
  a Linux kernel checkout, so generic code ranks before architecture-specific
  copies. A query that names the architecture (`x86`, `arm64`) is exempt.

### Fixed
- C/C++ reader: a function whose body the grammar could not close (for
  example an unknown macro inside a `switch`) swallowed every following
  definition of the file into split parts named after the first function.
  The body is now cut at the next `}` in column 0 and the rest of the file is
  parsed again, so each following function gets its own chunk and name.
- C/C++ reader: functions defined through a one-argument macro
  (`SYSCALL_DEFINE0(getpid)`, `DEFINE_IDTENTRY(exc_name)`) are named after the
  argument instead of having no name; `SYSCALL_DEFINEn` / `COMPAT_SYSCALL_DEFINEn`
  functions also list `sys_<name>` / `compat_sys_<name>` in `symbols`.
- C/C++ reader: attribute-like macros between the return type and the name
  (`asmlinkage __visible void __softirq_entry f(void)`, `static void noinline
  __cold f(void)`) no longer cut the header off the body or lose the name
  (used only when the plain parse has errors), and functions returning a
  function pointer are named.

### Upgrade notes
- **Reindex required for C/C++ projects** to get the reader fixes:
  `python src/index_rag.py --config <name> --clear --yes`. Without a reindex
  only changed files get the new chunks. Projects without C/C++ files need no
  reindex. The ranking changes are query-time only; set
  `RERANK_BODY_PREFERENCE = 0` to restore the previous C/C++ ranking.

## [0.10.0] - 2026-10-18

### Added
- Version numbers: a single version source (`src/shared/version.py`), a
  `--version` flag for the indexer and the MCP server, and the version in the
  start-up log of both.
- `index_manifest.json` records `indexer_version` (updated on every run) and
  `first_indexer_version` (kept from the first versioned run; after `--clear`
  it is the version that built the index). `get_index_state` shows the index
  version next to the running server version.

### Fixed
- A repository removed from `SOURCE_DIRS` kept its entry in the manifest
  `repo_commits` and kept showing up in `get_index_state`. Entries of
  repositories that are no longer configured are now dropped on the next run.

### Upgrade notes
- No reindex. Manifests without the version fields load and refresh normally;
  the next indexer run adds them.

## [0.9.1] - 2026-10-18

### Changed
- The exact symbol lookup reuses the query embedding and runs concurrently
  with the hybrid search, which removes most of its added latency. Results are
  unchanged.

### Upgrade notes
- No reindex, no config change.

## [0.9.0] - 2026-10-18

### Added
- **Exact symbol lookup.** When a query names a code identifier (`snake_case`,
  `camelCase`, `Owner::member`, `struct foo`, `foo()`), chunks that declare that
  name are added to the reranker candidates. Settings: `SYMBOL_LOOKUP_K = 4`
  (0 = off), `SYMBOL_LOOKUP_FIELDS = ["object_name", "symbols"]`,
  `SYMBOL_LOOKUP_SCORE = "top"`.
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
- **Reindex required** for indexes that contain C/C++ files, to get the new
  C/C++ chunks (otherwise only changed files get them).
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

## [0.8.0] - 2026-10-17

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
- **Reindex required** for indexes that contain Python, JS/TS or Kotlin
  files, to get the new chunks.
- Reranker changes are query-time only: no reindex; re-run your validation
  suites.
- Existing branch overlays need no change and no rebuild; old overlay manifests
  get one full compare on the next run.

## [0.7.0] - 2026-10-14

### Added
- **Kotlin** reader (`.kt`, `.kts`) with the same chunk headers as Java
  ([docs/kotlin-chunking.md](docs/kotlin-chunking.md)).

### Changed
- Nested Java and Kotlin classes show the outer-class chain
  (`Outer > Inner`) in the `// Class:` header.

### Upgrade notes
- **Reindex required** for indexes that contain Java files, to get the new
  nested-class headers.

## [0.6.0] - 2026-10-11

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

## [0.5.0] - 2026-10-08

### Added
- **C/C++** reader (`.c`, `.cpp`, `.h`) with class summaries and one chunk per
  function, and a Qt `.ui` form reader.
- Per-path `sql_dialect`: `tsql` (default) or `postgresql`.
- Validation suites can be loaded from an external YAML file (`--tests`).

### Upgrade notes
- No reindex: omitting `sql_dialect` keeps T-SQL chunking. Changing the dialect
  reindexes only the `.sql` files on that path.

## [0.4.1] - 2026-10-01

### Changed
- The project is relicensed under the **Apache License 2.0**, including
  versions previously released under AGPLv3. The unused AGPL `pymupdf`
  dependency was removed.

### Upgrade notes
- No code changes affecting indexing or search.

## [0.4.0] - 2026-08-09

### Added
- `get_index_state` MCP tool: last index time, indexed commits, overlays, point
  count and whether `HEAD` still matches the index (reads manifests only).
- Portable launcher for the self-index MCP server.

## [0.3.0] - 2026-06-06

### Added
- **Groovy** reader (`.groovy`).

## [0.2.1] - 2026-04-12

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

## [0.2.0] - 2026-03-26

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

### Upgrade notes
- **Reindex required** for indexes built with 0.1.0 (new chunking).
- **Config change required:** replace `QDRANT_USE_DOCKER` with `QDRANT_MODE`,
  move project configs to `project-configs/` and use the `type: "git_repo"` /
  `source_set` entry format in `SOURCE_DIRS`.

## [0.1.0] - 2026-03-08

### Added
- First version (development since 2026-02-28): local RAG indexer and MCP server (stdio and HTTP) for
  Delphi/Pascal, DFM forms, SQL (including T-SQL procedures) and FastReport.
- Qdrant backend with hybrid dense + sparse (BM25-style) search, incremental
  refresh driven by a manifest, path mapping and path excludes.

[Unreleased]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.12.0...HEAD
[0.12.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.9.1...v0.10.0
[0.9.1]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/jakubstuglik/hybrid-code-rag-mcp/releases/tag/v0.1.0
