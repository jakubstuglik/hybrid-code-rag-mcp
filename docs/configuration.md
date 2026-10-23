# Configuration

## Architecture

The config system uses a two-layer approach:

| File | Purpose |
|------|---------|
| `config.py` | **Common system defaults** -- embedding model, devices, batch sizes, VRAM cap, indexing mode. Loaded first for every config. |
| `project-configs/<name>/config.py` | **Project index** -- SOURCE_DIRS, COLLECTION_NAME, Qdrant connection, MCP identity for a specific codebase. One subdirectory per project. |
| `self-index/config.py` | **Self-index** -- indexes this project's own source code for AI-assisted development. |

`src/config_loader.py` always loads `config.py` first, then overlays the specified config on top. All scripts require a `--config` parameter to specify which index to work with.

## Creating a new index config

Create a `config.py` file inside a new subdirectory under `project-configs/` (e.g. `project-configs/my_project/config.py`):

```python
# project-configs/my_project/config.py — simple (source_set / legacy format)
SOURCE_DIRS = [
    {
        "path": "../my-project/src",
        "extensions": [".py", ".js", ".ts"],
    },
]

MODEL_PATH = "index_myproject"
COLLECTION_NAME = "myproject_rag"
QDRANT_MODE = "local"           # "local" (Docker auto-managed) or "remote"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

MCP_SERVER_NAME = "myproject-rag"
MCP_TOOL_NAME = "search_myproject"
MCP_TOOL_DESCRIPTION = "Search the myproject codebase."
MCP_PORT = 8125
```

For **git-backed repositories** with branch and tag overlays:

```python
# project-configs/my_project/config.py — git_repo format (supports overlays)
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": "../my-project",            # Git repo root
        "main_branch": "main",              # Default: "master"
        # Legacy list. Each name is kind "branch" (three-dot diff).
        "branches": ["feature/example"],
        # Optional. A moving tag uses a tree diff against the main tip.
        # "name" is the label stored on points and passed to search.
        "overlays": [
            {"name": "feature/example", "kind": "branch"},
            {"name": "current_release", "kind": "tag", "diff": "against_main_tip"},
        ],
        "sources": [
            {"path": "src", "extensions": [".py", ".js", ".ts"]},
            {"path": "sql", "extensions": [".sql"], "sql_dialect": "postgresql"},
        ],
    },
]
```

`branches` and `overlays` can be used together: `overlays` entries come first, then any `branches` name not already listed. A name that appears in both as a branch is indexed once. Giving one name both kinds, or listing a name twice in `overlays`, is a config error.

Each `overlays` entry is an object with a required `name`. `kind` is optional and defaults to `"branch"`, so configs that only use `branches`, or overlay entries without `kind`, keep working unchanged. A branch overlay accepts only `diff: "merge_base"`, which is also its default. A tag overlay must set `diff: "against_main_tip"`. See [Git overlays](git-overlays.md) for how each kind is indexed.

Then use it: `python src/index_rag.py --config my_project --yes`

Each source under `sources` (and each `source_set` / legacy entry) may set
`exclude`: a list of path patterns. A one-segment pattern such as `build` or
`__pycache__` matches that folder or file name at any depth. A pattern with a
slash such as `docs/backlog` matches that run of consecutive folders at any
depth. Patterns use `fnmatch` rules.

For `git_repo` sources, files ignored by git are also skipped when
`RESPECT_GITIGNORE` is `True` (the default). The indexer asks `git check-ignore`
rather than re-implementing gitignore rules, so nested `.gitignore` files,
`.git/info/exclude`, and the global excludes file all apply. A tracked file
that would match an ignore rule is still indexed.

**Migration:** after upgrading, the **first refresh** on an existing index
deletes Qdrant vectors (and manifest entries) for paths that are now
gitignored. That is intentional for generated trees such as `build/`. To keep
indexing gitignored files as before, set `RESPECT_GITIGNORE = False` in the
project config (only the explicit per-source `exclude` list then applies).

`INDEX_PARSE_WORKERS` (default `1`) is opt-in parallel file parsing in the
indexer. Leave it at `1` for the sequential path; try e.g.
`INDEX_PARSE_WORKERS = 8` on a multi-core machine only when parsing, not
embedding, is the bottleneck. Output order (and therefore point IDs) matches
the sequential path. On a GPU embedding-bound full index of a large C
repository, 8 workers were no faster than 1.

`MANIFEST_SAVE_INTERVAL_S` (default `0`) controls how often the indexer
persists `index_manifest.json` (and overlay manifests) during a run. With `0`
the manifest is rewritten on the main thread after every batch of about 10
processed files, as before, in the indented format; like every manifest save
it goes to a temp file that is renamed into place, so a kill never leaves a
truncated manifest. Each rewrite serialises the whole manifest, so on
an index with tens of thousands of files it costs seconds and stalls the
embedding pipeline. Set e.g. `MANIFEST_SAVE_INTERVAL_S = 60` to save at most
once a minute on a background thread, from a cheap snapshot, as compact JSON
written to a temp file and renamed into place (a crash never leaves a
truncated manifest). The end of a run and a failed run (exception or Ctrl+C)
always save synchronously. After a hard crash a refresh redoes at most the
last interval of work; the manifest never lists points that were not
upserted. Each save logs a `[MANIFEST] ... saved N files (... MB) in X s`
line, and a per-run summary is logged at the end.

Points written to Qdrant before the manifest save that records them are
covered by a journal next to the manifest (`index_manifest.json.pending.jsonl`,
and one per overlay manifest). Each delete or upsert of a file is appended to
it first. If a run is killed in between, or a delete or upsert fails, the next
run deletes the points of every file the journal and the manifest disagree on
and re-indexes it (a `[RECOVER]` warning is logged). Recovery on the main
branch deletes main-branch points only; overlay points of the same paths stay.
If that delete fails (Qdrant down), the indexer stops with exit code 3 and keeps
the journal for the next run. After a run that ends in sync the journal is
removed. It needs no configuration.

`LOG_REFRESH_CHANGES_MAX` (default `0`) caps the change summary printed at
the start of an index run. With `0` every added, modified and deleted path is
listed, as before; a full rebuild of a large tree then prints one line per
file, which takes seconds before the first embedding request. With e.g.
`LOG_REFRESH_CHANGES_MAX = 50` the first 50 paths per action are listed,
followed by a count of the rest; the per-directory totals stay complete.
`--verbose` always lists every path.

`SYMBOLS_PER_SPLIT_PART` (default `False`) and `SYMBOLS_MAX_PER_CHUNK`
(default `0`) shape the `symbols` payload list that the exact symbol lookup
(`SYMBOL_LOOKUP_FIELDS`) and the reranker read. The C/C++ and Rust readers store
every name a chunk defines in `symbols`; when the chunk is too long and is split
into parts, each part inherits the full list by default. For generated
headers with thousands of `#define` lines per group that multiplies the list
by the number of parts: gigabytes of payload on a large C tree, Qdrant
upserts that take minutes, and a symbol lookup that matches every part of the
group. With `SYMBOLS_PER_SPLIT_PART = True` each split part keeps only the
names that appear in its own text (a macro alias such as `sys_read` is kept
where `read` appears; a part with none has no `symbols` key). Every name is
still findable, now pointing at the part that defines it.
`SYMBOLS_MAX_PER_CHUNK = N` keeps at most the first N names of any chunk and
marks a shortened list with `symbols_truncated: true`. Both change stored
payloads: **reindex C/C++ and Rust sources after changing either one**.

`QDRANT_DELETE_CHUNK_SIZE` (default `500`) controls how many `file_path`
values are sent in one delete-by-filter call during refresh. Raise it for
fewer round-trips on huge deletes; lower it if the Qdrant server rejects
large filters. Set it only when tuning refresh delete performance.


## SQL dialect

`.sql` stays one reader. The dialect is a field on the source entry. The indexer does not sniff the file. PostgreSQL and T-SQL can both fail the ANSI grammar, and that error path used to always call the T-SQL chunker.

| `sql_dialect` | Behavior |
|---------------|----------|
| omitted or `"tsql"` | Tree-sitter SQL, then the T-SQL chunker. This is what existing indexes already use. |
| `"postgresql"` | Statement chunker. Dollar quotes, strings, comments, and parentheses hide semicolons. Each `CREATE TABLE`, `FUNCTION`, `PROCEDURE`, `TRIGGER`, `RULE`, `VIEW`, and `COMMENT ON` is its own chunk, with `object_name` and `object_type`. |

The key is valid on a `git_repo` source, a `source_set`, and a legacy entry. Any other value fails when the config loads. Put it only on the path that holds that dialect. Other extensions on other paths are unchanged.

```python
{"path": "Resources/sql", "extensions": [".sql"], "sql_dialect": "postgresql"}
```

A missing `sql_dialect` in the manifest means `tsql`. A refresh of a current project does not re-chunk its SQL files. After you set `postgresql` on a path that was indexed as T-SQL, the next refresh re-embeds only those `.sql` files. You do not need `--clear`. The git fast path does not skip a file whose dialect changed, even when the hash and mtime match.

Overview queries promote `pgsql_create_function`, `pgsql_create_procedure`, `pgsql_create_table`, `pgsql_create_trigger`, `pgsql_create_rule`, and `pgsql_create_view`. Large statements use the same name with a `_split` suffix. `pgsql_statement`, `pgsql_alter`, and `pgsql_create_index` are detail chunks.

## Recommended Embedding Models

- **Dense** (`MODEL_NAME`): `jinaai/jina-embeddings-v2-base-code` -- optimized for code, 8192 token context
- **Sparse** (`SPARSE_MODEL_NAME`): `Qdrant/bm25` -- exact lexical matching, zero VRAM

## Config Reference

All parameters are defined in `config.py` (system defaults) and can be overridden in project configs.

### Index Identity

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SOURCE_DIRS` | `[]` | Source entries to index (`git_repo`, `source_set`, or legacy). Each entry may set `sql_dialect` to `tsql` (default) or `postgresql`. |
| `COLLECTION_NAME` | `"default_rag"` | Qdrant collection name. Must be unique per index. |
| `MODEL_PATH` | `"default_index"` | Subdirectory under `BASE_PATH` for Qdrant storage and manifests. |

### Qdrant Connection

| Parameter | Default | Description |
|-----------|---------|-------------|
| `QDRANT_MODE` | `"local"` | `"local"` = auto-managed Docker; `"remote"` = external Qdrant server. |
| `QDRANT_HOST` | `"localhost"` | Qdrant server hostname. |
| `QDRANT_TIMEOUT` | `60` | Client request timeout in seconds (qdrant-client defaults to 5 s, too short for large upserts into big collections). |
| `QDRANT_PORT` | `6333` | Qdrant REST port. |
| `QDRANT_API_KEY` | `None` | API key for authenticated clusters (remote mode). |
| `QDRANT_HTTPS` | `False` | Use HTTPS for REST connection (remote mode). |
| `QDRANT_PREFER_GRPC` | `False` | Use gRPC instead of REST (remote mode, faster for bulk indexing). |
| `QDRANT_GRPC_PORT` | `6334` | gRPC port (remote mode). |
| `QDRANT_DELETE_TIMEOUT` | `60` | Seconds to wait for delete-by-filter calls. |
| `QDRANT_DELETE_CHUNK_SIZE` | `500` | Max `file_path` values per refresh delete filter (`MatchAny`). Tune only for large delete batches. |
| `RESPECT_GITIGNORE` | `True` | Skip gitignored files for `git_repo` sources (tracked files stay). First refresh after upgrade removes those vectors from existing indexes; set `False` to keep old behaviour. |
| `QDRANT_DOCKER_CONTAINER` | `None` | Docker container name override. Auto-derived as `qdrant-{COLLECTION_NAME}`. |
| `QDRANT_DOCKER_VOLUME` | `None` | Docker volume path override. Auto-derived from `BASE_PATH`/`MODEL_PATH`. |
| `QDRANT_DOCKER_IMAGE` | `None` | Image for Qdrant containers this tool **creates**. `None` = the pinned default `docker.io/qdrant/qdrant:v1.17.0` (the version the release is tested with). Existing containers keep their image. |
| `QDRANT_FILE_PATH_INDEX` | `True` | Keyword payload index on `file_path` (refresh deletes filter on it). Created with new collections and added to existing ones at the end of an indexer run; never changes results. |
| `INDEX_STATE_PUBLISH` | `True` | Indexer publishes the index state and overlay tombstones into Qdrant after every run and overlay update (see [Centralized serving](mcp-server.md#centralized-serving)). |
| `INDEX_STATE_TOMBSTONES_PER_POINT` | `1000` | Deleted-file keys per reserved tombstone point. |
| `INDEX_STATE_CACHE_S` | `10` | MCP server: seconds the state read from Qdrant is reused (`0` = read on every call). |

Qdrant containers created by the indexer or the MCP server always start with
`QDRANT__TELEMETRY_DISABLED=true`, so Qdrant sends no usage telemetry. A
container created by an older version keeps its old environment; recreate it
on the same storage path (data is kept) to turn telemetry off, and set the
variable yourself for a Qdrant you run outside this tool.

### MCP Server

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MCP_SERVER_NAME` | `"rag-server"` | Server name in MCP registration. |
| `MCP_TOOL_NAME` | `"search_rag"` | Tool function name exposed to MCP clients. |
| `MCP_TOOL_DESCRIPTION` | *(long string)* | Human-readable tool description. |
| `MCP_HOST` | `"0.0.0.0"` | Bind address for HTTP transport. |
| `MCP_INDEX_STATE_TOOL_NAME` | `"get_index_state"` | Name of the second tool, which reports the indexed commit, overlays and freshness. |
| `MCP_PORT` | `8123` | Server port. |

### Embedding Model

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MODEL_NAME` | `"jinaai/jina-embeddings-v2-base-code"` | HuggingFace model ID for dense embeddings. |
| `EMBED_MODEL_KWARGS` | `{"torch_dtype": "float16"}` | Extra kwargs for `HuggingFaceEmbedding(model_kwargs=...)`. |
| `EMBED_QUERY_PREFIX` | `None` | Prefix for query text (model-specific, e.g. `"search_query: "` for Nomic). |
| `EMBED_TEXT_PREFIX` | `None` | Prefix for document text (model-specific). |
| `EMBED_CONFIG_KWARGS` | `None` | PyTorch only: extra SentenceTransformer config kwargs. |
| `EMBED_TRUNCATE_DIM` | `None` | PyTorch only: Matryoshka output dimension (None = native). |
| `EMBED_BACKEND` | *(unset)* | Set to `"openai"` to use an OpenAI-compatible `/v1/embeddings` server (e.g. `llama-server`). See [Installation](installation.md). |
| `EMBEDDING_MODE` | `"local"` | `"local"`: embeddings come from this machine exactly as before (PyTorch, OpenVINO, managed TEI container, `EMBED_BACKEND`). `"remote"`: any OpenAI-compatible `POST {EMBEDDING_URL}/v1/embeddings` endpoint; **all** TEI settings (`USE_TEI`, `TEI_URL`, `TEI_*`), Docker checks and local weight downloads are ignored by the indexer and the MCP server. Unset = `"local"`. |
| `EMBEDDING_URL` | `None` | Base URL of the remote endpoint (required in remote mode). `GET /v1/models` (or TEI `/info`) is queried when available to log the served model; it is not required. |
| `EMBEDDING_QUANT` | `None` | Human-readable quantization/precision of the served weights (`"fp16"`, `"fp32"`, `"q8_0"`, ...). Stored as provenance; if the collection and the server both name one and they differ, the server refuses to start. |
| `EMBEDDING_API_MODEL` | `None` | `model` field sent with requests (default `MODEL_NAME`, or `OPENAI_EMBED_MODEL`). |
| `EMBEDDING_API_KEY` / `EMBEDDING_API_KEY_ENV` | `None` / `"HCR_EMBEDDING_API_KEY"` | Bearer token for the endpoint; prefer the environment variable so keys stay out of config files. |
| `EMBEDDING_TIMEOUT` | `600` | Remote request timeout in seconds. |
| `EMBEDDING_REQUEST_RETRIES` | `4` | Retries of transient errors (dropped/refused connections, HTTP 429/502/503/504) with exponential backoff, for remote mode and `EMBED_BACKEND = "openai"`. |
| `EMBEDDING_FINGERPRINT_MIN_COSINE` | `0.98` | Minimum cosine between the stored and the live embedding of each provenance fingerprint text (see [Embedding provenance](mcp-server.md#embedding-provenance)). |

### Embedding Sequence Length & VRAM Cap

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_MAX_SEQ_LENGTH` | `4096` | Max token sequence length. Caps ALiBi attention O(N^2) VRAM cost. |
| `EMBED_DYNAMIC_VRAM_CAP` | `False` | Compute max sequence length from GPU VRAM at indexing time (CUDA only). |
| `EMBED_VRAM_SAFETY_MARGIN` | `0.15` | Fraction of VRAM to reserve (0.0-1.0). |
| `EMBED_VRAM_DEDICATED_MB` | `None` | Override GPU VRAM detection (MiB). None = auto-detect. |
| `EMBED_VRAM_SHARED_MB` | `None` | Override shared VRAM detection (MiB). None = auto-detect. |

### Embedding Batch Sizes & Pooling

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DENSE_EMBED_BATCH_SIZE` | `32` | Max chunks per dense embedding batch. |
| `SPARSE_EMBED_BATCH_SIZE` | `32` | Max chunks per sparse embedding batch. |
| `EMBED_BATCH_MAX_TOKENS` | `16000` | Max approximate tokens per batch (chars / 4). |
| `EMBED_POOL_SIZE` | `512` | Max chunks to accumulate from multiple files before pool flush. Set 0 to disable pooling. |
| `EMBED_POOL_MAX_FILES` | `150` | Max files in pool before flush. Bounds crash recovery scope. |
| `EMBED_PIPELINE_DEPTH` | `0` | Opt-in pipelined embedding: pools in the dense stage at once (0 = legacy serial flush; e.g. 6 for TEI on GPU). Host RAM only; see [Tuning GPU memory](vram-tuning.md). |
| `INDEX_PARSE_WORKERS` | `1` | Parallel parse/chunk workers in the indexer. `1` = sequential (default). Opt-in (e.g. `4` or `8`) when parsing is the bottleneck; no speedup on embedding-bound runs. Ordered output. |
| `MANIFEST_SAVE_INTERVAL_S` | `0` | Manifest save throttle in seconds. `0` = save after every batch of processed files on the main thread (default). e.g. `60` = at most once a minute on a background thread, compact JSON, atomic write; always saved at the end and on failure. Use on large indexes. |
| `LOG_REFRESH_CHANGES_MAX` | `0` | Paths listed per action in the start-of-run change summary. `0` = all (default); e.g. `50` = first 50 per action plus a count. `--verbose` lists all. |
| `EMBED_PARSE_QUEUE_SIZE` | `400` | Parse-ahead queue length (files), used with any pipeline depth (previously fixed at 2). Host RAM only. |
| `QDRANT_UPSERT_BATCH_SIZE` | `500` | Points per Qdrant upsert call. |
| `QDRANT_UPSERT_MAX_BYTES` | `16 MiB` | Cap on the estimated JSON size of one upsert request (Qdrant rejects bodies above `max_request_size_mb`, 32 MB by default, and drops the connection mid-upload). A rejected batch is halved and retried. |

### Indexing Mode & Search

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INDEXING_MODE` | `"hybrid"` | `"dense"`, `"sparse"`, or `"hybrid"` (recommended). |
| `SPARSE_MODEL_NAME` | `"Qdrant/bm25"` | Sparse model. BM25 always runs on CPU regardless of device settings. |
| `HYBRID_ALPHA` | `0.5` | Query blending: 0.0 = all sparse, 1.0 = all dense. With `HYBRID_FUSION = "rrf"` it weighs the dense rank term against the sparse one (0.5 = classic RRF). **Do not change** without full validation. |
| `HYBRID_FUSION` | `"minmax"` | How the dense and sparse legs are combined: `"minmax"` = Relative Score Fusion (each leg min-max scaled, blended by alpha; the behaviour of earlier versions), `"rrf"` = weighted Reciprocal Rank Fusion on the legs' ranks. Any other value is a configuration error. See [Hybrid fusion](../README.md#hybrid-fusion). |
| `HYBRID_RRF_K` | `60` | RRF constant k (only with `"rrf"`; number >= 0). Larger = flatter rank curve, smaller = more weight on the top ranks. |
| `HYBRID_PREFETCH_K` | `100` | Candidates fetched per hybrid leg (dense, sparse) before fusion. The fused list is still cut to the reranker input size. `None` = same as the reranker input (the behaviour before this option). |
| `SYMBOL_LOOKUP_K` | `4` | Exact symbol lookup: when a query names a code identifier, up to this many chunks whose `SYMBOL_LOOKUP_FIELDS` payload (default `object_name`, `symbols`) equals it join the reranker pool. `0` = off. New collections get keyword payload indexes on these fields. |
| `SYMBOL_LOOKUP_SCORE` | `"top"` | Pre-rerank score of looked-up chunks: `"bar"` = score of the last returned candidate, `"top"` = best pool score. |
| `SYMBOLS_PER_SPLIT_PART` | `False` | Split parts of a long chunk keep only the `symbols` names that appear in their own text (C/C++ and Rust readers). `False` = every part inherits the full list (default). Reindex after changing. |
| `SYMBOLS_MAX_PER_CHUNK` | `0` | Max entries in a chunk's `symbols` list; longer lists keep the first N and get `symbols_truncated: true`. `0` = no limit (default). Reindex after changing. |
| `RERANK_CORE_MENTION_PENALTY` / `RERANK_PROFILE_MENTION` | `0.0` / `True` | Demote chunks that only mention an identifier the query names when another candidate declares it (core value, or per-language profile value). |
| `RERANK_TYPE_INTENT` | `True` | Per-language boosts when a query asks for an enumeration, flags or constants. |
| `RERANK_FILE_CAP` | `2` | For queries about several places ("A and B", "both", "across"), at most this many results per file keep their rank. |
| `DEPRIORITIZED_PATHS` / `DEPRIORITIZED_PATH_PENALTY` | `["*/tools/*", "*/tests/*", "*/test/*", "*/testing/*"]` / `0.10` | Path globs of code that is rarely the answer (tooling, tests; add vendored copies or samples per project, e.g. `*/arch/<arch>/*` for each architecture of a kernel checkout). Not applied when the query names a word of the glob. `[]` = off. |
| `RERANK_PROTOTYPE_YIELD` | `0.3` | Extra demotion for a declaration-only chunk when a candidate with a body declares the named identifier. |
| `RERANK_BODY_PREFERENCE` | `1.0` | Scale of the profiles' `summary_yield`: in behaviour queries a struct / class summary yields to a function body of the same language (C/C++ only, 0.15). `0` = off. |
| `HYBRID_EMBED_SINGLE_PASS` | `True` | True = dense + sparse in one pass. False = two-pass (for constrained VRAM). |
| `RERANK_PROFILES` | *(auto)* | Query-time rerank profiles to activate, e.g. `["java", "hibernate_mapping", "sql"]`, or `"all"`. By default the profiles of the readers registered for the extensions in `SOURCE_DIRS` are used, so only indexed languages influence ranking. Names: `delphi`, `delphi_forms`, `delphi_project`, `fastreport`, `sql`, `python`, `java`, `groovy`, `kotlin`, `javascript`, `csharp`, `go`, `php`, `cpp`, `qt_forms`, `hibernate_mapping`, `jasperreports`. No reindex needed. See [reranker.md](reranker.md). |

### Compute Devices

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INDEX_EMBED_DEVICE` | `"auto"` | PyTorch device for indexing. `"auto"` = best free VRAM GPU; `"0"`, `"1"` = specific GPU; `"cpu"`. |
| `MCP_EMBED_DEVICE` | `"cpu"` | PyTorch device for MCP server queries. Same values as above. |

### OpenVINO (Intel GPU)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `USE_OPENVINO_EMBEDDING` | `False` | Use OpenVINO for embeddings (Intel GPUs). |
| `OPENVINO_EMBED_DEVICE` | `"GPU"` | OpenVINO device: `"GPU"`, `"CPU"`, or `"AUTO"`. |

### TEI (Text Embeddings Inference)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `USE_TEI` | `True` | Enable TEI Docker backend for dense embeddings (recommended). |
| `TEI_GPU` | `"auto"` | GPU selection: `"auto"` (best free VRAM), `"0"`/`"1"` (specific), `"cpu"`. |
| `TEI_URL` | `None` | TEI server URL. Auto-derived as `http://127.0.0.1:{TEI_DOCKER_PORT}` (IPv4 loopback; `localhost` can resolve to `::1`, which Docker Desktop on Windows relays and which reset connections under indexing load). |
| `TEI_DOCKER_PORT` | `8090` | Host port for TEI Docker container. |
| `TEI_DTYPE` | `"float16"` | Inference dtype. Use `"float32"` for CPU-only mode. |
| `TEI_DOCKER_IMAGE` | `None` | Docker image override. Auto-detected by GPU compute capability. |
| `TEI_MODEL_DIR` | `None` | Model cache mount directory. Auto-derived from `BASE_PATH`. |
| `TEI_MAX_BATCH_TOKENS` | `None` | TEI `--max-batch-tokens`. Auto-derived from `EMBED_BATCH_MAX_TOKENS`. |
| `TEI_TOKENIZATION_WORKERS` | `None` | TEI `--tokenization-workers`. None = platform default. |
| `TEI_CONCURRENT_REQUESTS` | `16` | Concurrent HTTP requests to TEI (previously 64). Set 1 for synchronous fallback. With `EMBED_PIPELINE_DEPTH` > 0 the total in flight is depth × this value. |

Dropped connections and busy-server answers from TEI (HTTP 429, 502, 503,
504) are retried up to 4 times with exponential backoff (1, 2, 4, 8 s)
instead of aborting the indexing run. Other errors fail immediately.

### Git Branch-Aware Indexing

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DIFF_FULL_REINDEX_THRESHOLD` | `0.5` | If ratio of changed files exceeds this, fallback to full hash scan instead of git diff. |
