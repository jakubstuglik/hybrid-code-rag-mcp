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
| `QDRANT_DOCKER_CONTAINER` | `None` | Docker container name override. Auto-derived as `qdrant-{COLLECTION_NAME}`. |
| `QDRANT_DOCKER_VOLUME` | `None` | Docker volume path override. Auto-derived from `BASE_PATH`/`MODEL_PATH`. |

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
| `EMBED_PARSE_QUEUE_SIZE` | `400` | Parse-ahead queue length (files), used with any pipeline depth (previously fixed at 2). Host RAM only. |
| `QDRANT_UPSERT_BATCH_SIZE` | `500` | Points per Qdrant upsert call. |
| `QDRANT_UPSERT_MAX_BYTES` | `16 MiB` | Cap on the estimated JSON size of one upsert request (Qdrant rejects bodies above `max_request_size_mb`, 32 MB by default, and drops the connection mid-upload). A rejected batch is halved and retried. |

### Indexing Mode & Search

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INDEXING_MODE` | `"hybrid"` | `"dense"`, `"sparse"`, or `"hybrid"` (recommended). |
| `SPARSE_MODEL_NAME` | `"Qdrant/bm25"` | Sparse model. BM25 always runs on CPU regardless of device settings. |
| `HYBRID_ALPHA` | `0.5` | Query blending: 0.0 = all sparse, 1.0 = all dense. **Do not change** without full validation. |
| `HYBRID_PREFETCH_K` | `None` | Candidates fetched per hybrid leg (dense, sparse) before fusion. The fused list is still cut to the reranker input size. `None` = same as the reranker input. |
| `SYMBOL_LOOKUP_K` | `0` | Exact symbol lookup: when a query names a code identifier, up to this many chunks whose `SYMBOL_LOOKUP_FIELDS` payload (default `object_name`, `symbols`) equals it join the reranker pool. `0` = off. New collections get keyword payload indexes on these fields. |
| `SYMBOL_LOOKUP_SCORE` | `"bar"` | Pre-rerank score of looked-up chunks: `"bar"` = score of the last returned candidate, `"top"` = best pool score. |
| `RERANK_CORE_MENTION_PENALTY` / `RERANK_PROFILE_MENTION` | `0.0` / `False` | Demote chunks that only mention an identifier the query names when another candidate declares it (core value, or per-language profile value). |
| `RERANK_TYPE_INTENT` | `False` | Per-language boosts when a query asks for an enumeration, flags or constants. |
| `RERANK_FILE_CAP` | `0` | For queries about several places ("A and B", "both", "across"), at most this many results per file keep their rank. |
| `DEPRIORITIZED_PATHS` / `DEPRIORITIZED_PATH_PENALTY` | `[]` / `0.10` | Path globs of code that is rarely the answer (vendored copies, tooling, samples). Not applied when the query names a word of the glob. |
| `RERANK_PROTOTYPE_YIELD` | `0.0` | Extra demotion for a declaration-only chunk when a candidate with a body declares the named identifier. |
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
| `TEI_URL` | `None` | TEI server URL. Auto-derived as `http://localhost:{TEI_DOCKER_PORT}`. |
| `TEI_DOCKER_PORT` | `8090` | Host port for TEI Docker container. |
| `TEI_DTYPE` | `"float16"` | Inference dtype. Use `"float32"` for CPU-only mode. |
| `TEI_DOCKER_IMAGE` | `None` | Docker image override. Auto-detected by GPU compute capability. |
| `TEI_MODEL_DIR` | `None` | Model cache mount directory. Auto-derived from `BASE_PATH`. |
| `TEI_MAX_BATCH_TOKENS` | `None` | TEI `--max-batch-tokens`. Auto-derived from `EMBED_BATCH_MAX_TOKENS`. |
| `TEI_TOKENIZATION_WORKERS` | `None` | TEI `--tokenization-workers`. None = platform default. |
| `TEI_CONCURRENT_REQUESTS` | `64` | Concurrent HTTP requests to TEI. Set 1 for synchronous fallback. |

### Git Branch-Aware Indexing

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DIFF_FULL_REINDEX_THRESHOLD` | `0.5` | If ratio of changed files exceeds this, fallback to full hash scan instead of git diff. |
