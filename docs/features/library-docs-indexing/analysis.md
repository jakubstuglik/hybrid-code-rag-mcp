# Library Docs Indexing

**TODO #3** — Index project library documentation at specific pinned versions, and/or leverage existing MCP servers to supplement the codebase index.

---

## Problem Statement

The current index covers project source code (Delphi Pascal, SQL, DFM, Python). AI agents querying the index cannot answer questions about the *libraries* the project depends on — e.g.:

- "What is the signature of `VectorStoreIndex.from_documents()` in LlamaIndex 0.10.x?"
- "How do I use `QdrantClient.upsert()` with named vectors?"
- "What parameters does `HuggingFaceEmbedding` accept?"

Without this, agents must rely on general training knowledge, which may be stale or version-mismatched.

---

## Libraries in Scope (Current Project)

Key dependencies (from `requirements/requirements.txt`):

| Library | Relevance | Docs Available |
|---|---|---|
| `llama-index` | Core RAG framework — VectorStoreIndex, NodeParser, etc. | Yes (llamaindex.ai/docs) |
| `qdrant-client` | Vector DB client — QdrantClient, models, search API | Yes (qdrant.tech/documentation) |
| `llama-index-embeddings-huggingface` | Embedding model loading | Yes (part of llama-index docs) |
| `tree-sitter` + `tree-sitter-language-pack` | AST parsing | Limited (README + source) |
| `mcp` | Model Context Protocol server | Yes (modelcontextprotocol.io) |
| `fastapi` / `uvicorn` | HTTP MCP transport | Yes |

---

## Options

### Option A — Scrape and Index Docs

Fetch HTML/Markdown documentation for each library at the pinned version, chunk it, and embed it into a separate Qdrant collection (or a separate namespace in the existing collection with a `source: docs` filter).

**Process:**
1. Identify doc URLs for the pinned version (e.g., LlamaIndex has versioned docs at `docs.llamaindex.ai/en/v0.10.x/`)
2. Crawl the docs with a tool like `wget --mirror` or `scrapy`
3. Convert HTML → Markdown (e.g., `markdownify`)
4. Chunk with the existing Python reader or a generic text splitter
5. Embed and store in Qdrant

**Pros:**
- Full control over what's indexed
- Works offline after initial scrape
- Can be re-indexed when pinned versions change

**Cons:**
- High maintenance burden: re-scrape on version bumps
- Doc sites often have anti-scraping measures
- Versioned doc URLs may not exist for all libraries
- Large volume: LlamaIndex docs alone are hundreds of pages

---

### Option B — Index from Source (Git Clone at Tag)

Clone each library repo at the exact pinned version tag and run it through the existing indexer (Python reader + SQL reader as applicable).

**Process:**
1. `git clone --branch v0.10.65 https://github.com/run-llama/llama_index.git`
2. Add the cloned path as a `SOURCE_DIRS` entry with `type: git_repo`
3. Run `index_rag.py` — the Python reader will chunk all `.py` files with class/function summaries

**Pros:**
- No scraping needed — works directly with the existing pipeline
- Source code is authoritative for function signatures and parameter names
- Docstrings are indexed as part of function/class chunks (context prefix includes them)
- The incremental manifest system handles re-indexing on version bumps

**Cons:**
- Source code is not the same as documentation — no tutorials, usage examples, or concept explanations
- Large repos (LlamaIndex has 500k+ lines) may produce tens of thousands of chunks
- Clutters the index with library internals that are not relevant to the project

**Mitigation:** Use `INCLUDE_PATTERNS` / `EXCLUDE_PATTERNS` in the source dir config to limit indexing to public API surface (e.g., only `llama_index/core/*.py`, not `tests/` or `benchmarks/`).

---

### Option C — MCP Servers for Libraries

Instead of indexing docs locally, connect to community or official MCP servers that expose library documentation as tools.

**Known / discoverable MCP servers:**

| Library | MCP Server Availability |
|---|---|
| General web search | `fetch` MCP server (official) — fetches any URL as Markdown |
| Python packages | `pypi-mcp` — queries PyPI package metadata |
| GitHub repos | `github` MCP server (official) — search code, issues, PRs |
| LlamaIndex | No dedicated MCP server found (as of research date) |
| Qdrant | Qdrant has an official MCP server (`qdrant-mcp`) but it's for querying Qdrant, not its docs |

**Process:**
1. Add the relevant MCP servers to `opencode.json`
2. The AI agent can call `fetch` to retrieve a specific doc page on demand
3. No pre-indexing required — docs are fetched live

**Pros:**
- Zero maintenance — always returns current docs
- No VRAM cost — no embedding at query time
- Works for any library with a public doc site

**Cons:**
- Requires internet access at query time
- Not suitable for offline or air-gapped environments
- The `fetch` MCP server returns raw page content — quality depends on how well the doc site renders to Markdown
- Not searchable in bulk — the agent must know which page to fetch

---

### Option D — Hybrid (Source Index + Fetch on Demand)

Index library source at pinned version (Option B, limited to public API files) for fast offline search of signatures, and use the `fetch` MCP server for on-demand doc page retrieval when richer context is needed.

This is the recommended approach.

---

## Recommendation

**Phase 1 (low effort):** Add the `fetch` MCP server to `opencode.json`. This immediately allows agents to retrieve any library doc page on demand with zero maintenance cost.

**Phase 2 (medium effort):** For the 2–3 most-queried libraries (likely `llama-index` and `qdrant-client`), clone at pinned version, configure `SOURCE_DIRS` with narrow `INCLUDE_PATTERNS`, and index the public API surface only. This provides fast offline search of signatures.

**Not recommended:** Full doc scraping (Option A) — high maintenance, fragile, and the effort is not proportional to the gain given that Option B + C covers most use cases.

---

## Implementation Notes

- A new `source_type: "library_source"` could be added to config to distinguish library code chunks from project code in search results (via metadata filtering)
- The `EXCLUDE_PATTERNS` config key can exclude `tests/`, `docs/`, `benchmarks/`, `examples/` from library source indexing to keep chunk count manageable
- Version tracking: store the library version tag in the source dir config so the manifest system can detect when the tag changes
- The `fetch` MCP server is available at `https://github.com/modelcontextprotocol/servers/tree/main/src/fetch` — add to `opencode.json` as an `npx` command

---

## Related TODOs
- **TODO #5** — Model tracking becomes more important when multiple collections (project code + library docs) exist, each potentially embedded with different models
