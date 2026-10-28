# MCP server

## Starting the MCP server

All scripts require a config name. Two transports are available:

**Stdio** (for OpenCode, Claude Desktop, and other MCP clients):
```bash
# Windows
scripts\start_rag_mcp_stdio.bat my_project
scripts\start_rag_mcp_stdio.bat self-index

# Linux/Mac
scripts/start_rag_mcp_stdio.sh my_project
scripts/start_rag_mcp_stdio.sh self-index
```

**HTTP** (for debugging, remote clients, or browser-based tools):
```bash
# Windows
scripts\start_rag_mcp_http.bat my_project
scripts\start_rag_mcp_http.bat self-index

# Linux/Mac
scripts/start_rag_mcp_http.sh my_project
scripts/start_rag_mcp_http.sh self-index
```

**Manual launch** (without scripts):
```bash
python src/rag_mcp.py --config my_project --transport stdio
python src/rag_mcp.py --config my_project --transport streamable-http
python src/rag_mcp.py --config self-index --transport stdio
```

## OpenCode integration

To use this as an MCP tool inside another project, add to that project's `opencode.jsonc`:

```jsonc
{
  "mcp": {
    "my-project-rag": {
      "type": "local",
      "enabled": true,
      "command": [
        "powershell", "-Command",
        "cmd.exe /c 'for /f \"delims=\" %a in (''git rev-parse --show-toplevel'') do call \"%a\\..\\hybrid-code-rag-mcp\\scripts\\start_rag_mcp_stdio.bat\" my_project'"
      ]
    }
  }
}
```

The PowerShell wrapper resolves paths relative to the git root, so it works regardless of which subfolder OpenCode is launched from.

**Linux/Mac equivalent:**
```json
{
  "mcp": {
    "my-project-rag": {
      "type": "local",
      "enabled": true,
      "command": ["bash", "-c", "$(git rev-parse --show-toplevel)/../hybrid-code-rag-mcp/scripts/start_rag_mcp_stdio.sh my_project"]
    }
  }
}
```

For the self-index, this repository's own `opencode.json` uses the cross-platform Python launcher (paths are relative to the repo root):
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "self-rag": {
      "type": "local",
      "command": ["python", "scripts/start_self_rag.py"],
      "enabled": true,
      "timeout": 120000
    }
  }
}
```

`scripts/start_self_rag.py` switches to the repo root, prefers `.venv`'s Python and runs `src/rag_mcp.py --config self-index --transport stdio`. `scripts\start_self_rag.bat` and `scripts/start_self_rag.sh` do the same through the stdio script. Docker auto-start is handled by `src/rag_mcp.py`.

For a remote (HTTP) server, OpenCode uses `"type": "remote"` with a `url`, for example `{"type": "remote", "url": "http://localhost:8125/mcp", "oauth": false}`. See the [OpenCode MCP docs](https://opencode.ai/docs/mcp-servers/).

## Grok Build integration

Grok Build reads MCP servers from `[mcp_servers.<name>]` tables in `~/.grok/config.toml` and in project `.grok/config.toml` files (it walks from the current directory up to the git root). See the [Grok Build MCP docs](https://docs.x.ai/build/features/mcp-servers).

```bash
# stdio: everything after -- is the server command
grok mcp add my-project-rag -- /path/to/hybrid-code-rag-mcp/scripts/start_rag_mcp_stdio.sh my_project
# HTTP (start the server with scripts/start_rag_mcp_http.* first)
grok mcp add --transport http my-project-rag http://localhost:8125/mcp
# add --scope project to write ./.grok/config.toml instead of ~/.grok/config.toml
```

This repository ships a project-scoped config for the self-index in `.grok/config.toml`:

```toml
[mcp_servers.self-rag]
command = "python"
args = ["scripts/start_self_rag.py"]
enabled = true
# Cold start may start Qdrant/TEI containers + load BM25 encoder
startup_timeout_sec = 180
```

`startup_timeout_sec` defaults to 30 seconds; the first start can take longer because the Qdrant and TEI containers may have to be created. `grok mcp doctor <name>` diagnoses a server that does not connect, and stderr of stdio servers is captured under `~/.grok/logs/mcp/`.

## Centralized serving

One indexer can write to a shared Qdrant while one or more MCP servers on
other machines serve it over HTTP. The MCP server needs **no manifest
file**: everything it needs is stored in the collection.

```
indexer host                         serving host(s)
  index_rag.py ──writes──► Qdrant ◄──reads── rag_mcp.py (HTTP) ◄── clients
  (manifests stay here)               ▲
                                      └── embedding endpoint (EMBEDDING_MODE="remote")
```

Serving config: the same `COLLECTION_NAME`, `MODEL_NAME`, prefixes and
`EMBEDDING_QUANT` as the indexer, `QDRANT_MODE = "remote"` with
`QDRANT_HOST` / `QDRANT_PORT`, and either a local embedding backend or
`EMBEDDING_MODE = "remote"` with `EMBEDDING_URL`. `SOURCE_DIRS` may be empty:
the main branch label used by the branch filter is then taken from the
published state (`repo_commits.*.main_branch`), else `master`.

```python
# serving-only config (no manifest, no source checkout)
SOURCE_DIRS = []
COLLECTION_NAME = "my_project"
QDRANT_MODE = "remote"
QDRANT_HOST = "qdrant.internal"
QDRANT_PORT = 6333
EMBEDDING_MODE = "remote"
EMBEDDING_URL = "http://embeddings.internal:8080"   # TEI, llama.cpp server, vLLM, ...
MODEL_NAME = "jinaai/jina-embeddings-v2-base-code"
EMBEDDING_QUANT = "fp16"
MCP_HOST = "0.0.0.0"
MCP_PORT = 8123
```

### What the indexer publishes

At the end of every successful run, and after every overlay update, the
indexer writes (unless `INDEX_STATE_PUBLISH = False`):

| Item | Where | Content |
|------|-------|---------|
| Index state | collection metadata key `hcr_index_state` (Qdrant >= 1.16, PATCH semantics, other keys kept) | indexed file count, `index_run`, indexer versions, `repo_commits`, directory snapshots, one summary per overlay (kind, merge base, last commit, signature, file and tombstone counts, tombstone digest, keys per tombstone point) |
| Overlay tombstones | reserved points, `INDEX_STATE_TOMBSTONES_PER_POINT` keys each; ids from the overlay label, tombstone digest, that per-point value and the part number (`tombstone_per_point` on the overlay entry; older documents omit it and use the previous ids) | file keys deleted on the overlay |
| Provenance | sentinel point (full record incl. fingerprint vectors) and metadata key `hcr_provenance` (without vectors) | see below |

Servers without collection metadata support (older than 1.16) get the state
document in a reserved point instead. Reading order: metadata, reserved
point, then the local manifest (collections published by older releases).
Per-file manifest data (hashes, point ids) is never published; the manifest
stays on the indexer host.

All reserved points carry `branch = "__hcr_reserved__"` and zero vectors, so
the branch filter of `search_rag` never returns them.

**Size limits.** Collection metadata is replicated through cluster consensus
and should stay small: the state document holds only summaries and never
tombstone keys. Measured on real indexes of 1k–64k files it is 0.5–1.8 KB
(about 1 KB plus about 0.3 KB per overlay), independent of the file count.
Tombstones go into reserved points of `INDEX_STATE_TOMBSTONES_PER_POINT`
(1000) keys each; with typical repository paths that is about 50–80 KB per
point, well below Qdrant's request limits. An overlay with N deleted files
needs `ceil(N / 1000)` points. Parts are written when the tombstone digest,
the part count or `INDEX_STATE_TOMBSTONES_PER_POINT` changes, or when a part
is missing. The id includes the label, the digest and that per-point value,
so a series split differently never reuses a live series' ids: the new set
is written next to the old one, the state document switches to it in one
write, and only then are the old parts deleted. A document from a release
that did not store `tombstone_per_point` keeps its previous ids until that
publish. A server that cannot read a complete set keeps using the last
complete set it read (or, if it never had one, the local manifest). Reserved
points count towards `points_count`.

Publishing costs one metadata PATCH plus the changed tombstone points:
measured 45–90 ms per publish against a local Qdrant, about 0.1–0.2% of a
small refresh and negligible for large ones.

`get_index_state` shows `state_source: qdrant collection metadata` (or
`qdrant reserved point`) when it reads the published state, the overlays
with `N deleted` tombstone counts, and an "Embedding provenance" section.
The state is cached for `INDEX_STATE_CACHE_S` seconds.

### Embedding provenance

Stored per collection: model name, `EMBEDDING_QUANT`, dimension, distance,
query and document prefixes, truncate dimension, sparse model, backend
family, the model name the endpoint reports, indexer version, and a
fingerprint: the query embeddings of three fixed texts.

At startup the MCP server (also a serving-only instance) logs the stored
provenance, embeds the fingerprint texts through its own query path and
checks: real dimension (vs stored and vs the collection), model name,
quantization (an error when both sides name one and they differ, a warning
when only one does), prefixes, truncate dimension, sparse model, and the
fingerprint cosine. Any mismatch is a **fatal startup error** with a list of
the differences. The indexer runs the same check before it writes.

The cosine threshold `EMBEDDING_FINGERPRINT_MIN_COSINE` (default 0.98)
separates "same model on other hardware or precision" from "other model or
weights". Measured: the same model served by TEI in fp16 on a GPU and run by
PyTorch in fp32 on a CPU gives a minimum cosine of 0.999999 over the
fingerprint texts; random vectors give about 0.0, and even different texts
through the same model stay below 0.8. Raise the threshold to also catch
close quantization variants (or set `EMBEDDING_QUANT` on both sides); lower
it only if a known-good setup is rejected.

Collections indexed by older releases have no full provenance: the server
starts with a warning (only the dimension is checked) and the next indexer
run backfills it. The old backend-family check no longer reports TEI vs an
OpenAI-compatible server (TEI also serves `/v1/embeddings`) as a mismatch;
PyTorch vs a server backend is still reported.

### Concurrency

The HTTP server handles each request as its own asyncio task. Blocking work
on the query path runs in worker threads so concurrent clients are not
serialized on the event loop: the query-embedding HTTP call, BM25 query
encoding (computed in a thread and handed to the vector store through a
per-request context variable, so the result is identical), reranking, the
Qdrant state reads and, with `--lazy-init`, the first index build. Shared
state is read-only or lock-protected (state cache, endpoint load
balancer). `tools/mcp_load_test.py` measures throughput and latency with N
concurrent clients.

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/start_qdrant.*` | Start Qdrant Docker container for a config (manual) | `scripts\start_qdrant.bat my_project` |
| `scripts/start_rag_mcp_stdio.*` | Start MCP server (stdio transport) | `scripts\start_rag_mcp_stdio.bat my_project` |
| `scripts/start_rag_mcp_http.*` | Start MCP server (HTTP transport) | `scripts\start_rag_mcp_http.bat self-index` |
| `scripts/start_self_rag.*` | Start self-index MCP server (stdio) | `scripts\start_self_rag.bat` |
| `scripts/start_self_rag.py` | Cross-platform Python launcher for self-index MCP | `python scripts/start_self_rag.py` |
| `src/refresh_guard.py` | Cron-safe indexing with skip/kill guard | `python src/refresh_guard.py --config my_project --yes` |
| `src/git_pull_guard.py` | Cron-safe git pull + indexing guard | `python src/git_pull_guard.py --config my_project` |
| `src/git_pull_all.py` | Simple git pull for all repos in a config | `python src/git_pull_all.py --config my_project` |

All shell scripts have `.bat` (Windows) and `.sh` (Linux/Mac) variants. Scripts except `start_self_rag` require a config name as the first argument.

**Note:** In local mode, `src/index_rag.py` and `src/rag_mcp.py` auto-start Docker containers, so `start_qdrant` is only needed for manual/diagnostic use.
