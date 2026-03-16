# Embedding Model Exploration

**TODO #1** — Evaluate alternative embedding models for the Informica 2.0 codebase and
a separate docs corpus (`../informica-docs`).

---

## Current Setup

| Parameter | Value |
|---|---|
| Dense model | `jinaai/jina-embeddings-v2-base-code` |
| Sparse model | `Qdrant/bm25` (pure lexical) |
| Dimensions | 768 |
| Context window | 8192 tokens (ALiBi), capped at 4096 in config due to VRAM |
| Parameters | 161M |
| License | Apache 2.0 |
| GPU | NVIDIA RTX 4060 (8 GB VRAM) |
| Training data | GitHub code + 150M coding Q&A / docstring pairs |
| Pascal/Delphi support | Not explicit — maps to C-like patterns |

The ALiBi positional encoding causes a quadratic VRAM cost: the bias tensor is ~384 MB at
4096 tokens and ~1.5 GB at 8192. This is why `EMBED_MAX_SEQ_LENGTH` is capped at 4096.

**History note:** BGE-M3 was evaluated previously and rejected for the codebase. The
conclusion was that a model specifically trained on code gives better results for
Delphi/SQL/DFM content than a general-purpose multilingual model. That decision stands.
BGE-M3 is re-examined below only for the docs collection.

---

## Models Under Consideration (Commercial Use Only)

CC-BY-NC models (Salesforce SFR-Embedding-Code series) are excluded entirely.

### Code Collection Candidates

| Model | Params | Dims | Context | VRAM Est. (fp16, batch=32) | License | CoIR NDCG@10 |
|---|---|---|---|---|---|---|
| `jinaai/jina-embeddings-v2-base-code` *(current)* | 161M | 768 | 8192 (ALiBi, capped 4096) | ~2.5 GB | Apache 2.0 | ~55–58 |
| `nomic-ai/CodeRankEmbed-137M` | 137M | 768 | 8192 | ~1.5–2 GB | Apache 2.0 | 60.1 |
| `Alibaba-NLP/gte-modernbert-base` | 149M | 768 | 8192 | ~1.5–2 GB | Apache 2.0 | **79.31** |

**Key notes:**
- `gte-modernbert-base` requires `transformers>=4.48.0` (current pin: `4.46.3`). This is a
  2-minor-version bump. Jina breaks at 5.x — so 4.48 is safe.
- `gte-modernbert-base` is a general-purpose model (not code-specialized), but ModernBERT was
  pretrained on code and GTE fine-tuning included code retrieval tasks. No `trust_remote_code`
  required. Uses standard RoPE attention — no ALiBi O(N²) VRAM penalty.
- `CodeRankEmbed-137M` also uses RoPE — can run at full 8192 context.

**Eliminated candidates:**
- `jinaai/jina-code-embeddings-0.5b` — **CC-BY-NC-4.0. Excluded.** Despite being listed as
  Apache 2.0 in some early announcements, the HuggingFace model card confirmed non-commercial
  only. Also incompatible with `transformers==4.46.3` (requires `>=4.53.0`).
- `jinaai/jina-code-embeddings-1.5b` — **CC-BY-NC-4.0. Excluded.** Same license.
- `nomic-ai/nomic-embed-code` (7B) — Excluded: requires 24 GB+ VRAM, not feasible on RTX 4060.
- Salesforce SFR-Embedding-Code series — CC-BY-NC. Excluded.
- `agentica-org/OASIS-code-embedding-1.5B` — Gated/private (401), license unknown. Excluded.

**Backup plan (ColBERT multi-vector, NOT drop-in):**
- `lightonai/LateOn-Code` — Apache 2.0, 149M, CoIR 74.12. Multi-vector ColBERT format —
  requires Qdrant pipeline changes (MaxSim operator, different storage schema). Do not
  implement unless single-vector models underperform.
- `lightonai/LateOn-Code-edge` — Apache 2.0, 17M, CoIR 66.64. Same ColBERT caveat.

### Docs Collection Candidates

| Model | Params | Dims | Context | VRAM Est. (fp16, batch=32) | License | Notes |
|---|---|---|---|---|---|---|
| `BAAI/bge-m3` | 570M | 1024 | 8192 | ~4–5 GB | MIT | Best multilingual, neural sparse, ColBERT support |
| `nomic-ai/nomic-embed-text-v1.5` | 137M | 768 | 8192 | ~1.5–2 GB | Apache 2.0 | Matryoshka dims; strong NL/docs; needs task prefix |

---

## VRAM Feasibility on RTX 4060 (8 GB)

The key constraint. Current Jina with batch=32, seq=4096, fp16 uses roughly 2.5 GB for
model weights + activations. BM25 uses zero VRAM (CPU).

| Scenario | VRAM Est. | Feasible? | Notes |
|---|---|---|---|
| Current: Jina 161M, batch=32, seq=4096 | ~2.5 GB | Yes (proven) | Baseline |
| CodeRankEmbed-137M, batch=32, seq=8192 | ~2 GB | Yes | RoPE, O(N) scaling, full native context |
| gte-modernbert-base 149M, batch=32, seq=8192 | ~2 GB | Yes | Flash Attention 2 + RoPE, O(N) scaling |
| BGE-M3, batch=32, seq=4096 | ~4–5 GB | Probably yes | 1024-dim adds overhead |
| BGE-M3, batch=16, seq=2048 | ~2.5–3 GB | Yes | Reduce if OOM |

**Critical insight about CodeRankEmbed-137M and gte-modernbert-base:** Unlike Jina's ALiBi,
both models use RoPE-based positional encoding — O(N) VRAM scaling with sequence length, not
O(N²). They can run at their native 8192 token context without the quadratic VRAM penalty
that forced Jina's cap to 4096. Better coverage of long code chunks.

`gte-modernbert-base` additionally uses Flash Attention 2 (ModernBERT architecture), which
further reduces memory usage compared to standard attention at long contexts.

---

## Two-Collection Architecture

### Code collection: `informica_rag`
- Source: `../informica_2_0` (Delphi Pascal, SQL, DFM, FR3, DPROJ)
- Model: one of the code-specialized models above
- Sparse: `Qdrant/bm25` (unchanged)
- Config: `project-configs/config_informica/config.py` (already exists)

### Docs collection: `informica_docs_rag`  *(new)*
- Source: `../informica-docs` (PDF, DOCX, XLS, TXT — natural language heavy)
- Model: `BAAI/bge-m3` or `nomic-embed-text-v1.5`
- Sparse: BGE-M3's own neural sparse (if using BGE-M3) or `Qdrant/bm25` (if nomic)
- Config: `project-configs/config_informica_docs/config.py` *(new)*
- MCP: Separate MCP server instance or extend the existing one with a second tool

This is the correct separation. Code-specialized models for code, general-NL model for
docs. No quality compromise on either side.

**Docs reader work needed:** PDF, DOCX, XLS files are not currently handled by any reader.
Before the docs collection can be indexed, readers for these formats must be added. This is
a non-trivial prerequisite (see "Prerequisite Work" section below).

---

## Do Code Changes Need to Break Master?

**No. No code changes to `shared/embedding.py` are needed to test any of the three
shortlisted models.** Here is why:

### CodeRankEmbed-137M — pure config change

`get_embed_model()` calls `HuggingFaceEmbedding(model_name=cfg.MODEL_NAME, ...)`. Changing
`MODEL_NAME` is sufficient. The model loads via standard HuggingFace transformers, no
custom architecture (no `trust_remote_code` required, though leaving it True is harmless).

Config diff for a test:
```python
MODEL_NAME = "nomic-ai/CodeRankEmbed-137M"
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}  # unchanged
EMBED_MAX_SEQ_LENGTH = 8192  # can use full native max (no ALiBi penalty)
DENSE_EMBED_BATCH_SIZE = 32  # start here, reduce if OOM
EMBED_BATCH_MAX_TOKENS = 32000  # can increase at full seq length
```

Also requires adding an entry to `MODEL_REGISTRY` in `shared/vram_cap.py` — a
2-line addition that does not affect any existing model's behavior.

### gte-modernbert-base — requires transformers bump

`get_embed_model()` handles this with a plain `MODEL_NAME` change. No `trust_remote_code`
required. The only prerequisite is bumping `transformers==4.46.3` → `>=4.48.0` in
`requirements.txt` (ModernBERT architecture was added in transformers 4.48.0).

The bump is safe: Jina breaks at 5.x, not 4.x. `transformers==4.48.x` is fully compatible
with `jinaai/jina-embeddings-v2-base-code`.

Config diff for a test:
```python
MODEL_NAME = "Alibaba-NLP/gte-modernbert-base"
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}  # unchanged
EMBED_MAX_SEQ_LENGTH = 8192  # Flash Attention 2 + RoPE, no VRAM penalty
DENSE_EMBED_BATCH_SIZE = 32
EMBED_BATCH_MAX_TOKENS = 32000
```

Also requires adding a `MODEL_REGISTRY` entry in `shared/vram_cap.py`.

### BGE-M3 (for docs collection) — one small code addition needed

BGE-M3 does NOT need `trust_remote_code`. Its standard HuggingFace path works. However,
two things differ from the current setup:

1. **Neural sparse output:** BGE-M3 produces both dense and sparse vectors from a single
   model pass. The current `get_sparse_encoder()` in `qdrant/vector_store.py` uses
   `fastembed.sparse.SparseTextEmbedding` (separate BM25 model). To use BGE-M3's native
   sparse, a new code path is needed. **Alternatively:** just use BGE-M3 for dense only
   and keep `Qdrant/bm25` for sparse — this is fully supported today with zero code
   changes, and gives most of the benefit.

2. **1024-dim vectors:** The Qdrant collection schema stores vector dimension at creation
   time. A BGE-M3 docs collection would have 1024-dim vectors vs 768-dim for code. This is
   fine — they are separate collections. No code change needed; the vector store code reads
   dimension from the model at collection creation.

**Recommended starting point for docs collection:** Use BGE-M3 dense + BM25 sparse. No
code changes required. BGE-M3 neural sparse can be explored later (TODO #2 territory).

### Summary

| Model | Code changes to master? | What's needed |
|---|---|---|
| `CodeRankEmbed-137M` | No | New project config + MODEL_REGISTRY entry |
| `gte-modernbert-base` | transformers bump only | New project config + MODEL_REGISTRY entry + transformers>=4.48.0 |
| `jina-code-embeddings-0.5b` | N/A — **excluded (CC-BY-NC)** | — |
| `jina-code-embeddings-1.5b` | N/A — **excluded (CC-BY-NC)** | — |
| `BGE-M3` (docs, dense+BM25) | No | New project config + MODEL_REGISTRY entry + docs readers |
| `BGE-M3` (docs, native sparse) | Yes — new sparse code path | Not recommended for first iteration |

**Git branches are not needed.** All testing can happen via separate named configs
(`config_informica_coderank`, `config_informica_docs`) pointing to isolated Qdrant
collections with different `COLLECTION_NAME` and `MODEL_PATH` values. Master stays on
the current Jina model and its existing collection untouched.

---

## Proposed Test Configs

### 1. `config_informica_coderank` — CodeRankEmbed-137M on codebase

```
COLLECTION_NAME = "informica_coderank"
MODEL_PATH = "index_coderank_informica_2_0"
MODEL_NAME = "nomic-ai/CodeRankEmbed-137M"
EMBED_MAX_SEQ_LENGTH = 8192
DENSE_EMBED_BATCH_SIZE = 32
EMBED_BATCH_MAX_TOKENS = 32000
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}
SPARSE_MODEL_NAME = "Qdrant/bm25"
# SOURCE_DIRS — same as config_informica
```

### 2. `config_informica_gte` — gte-modernbert-base on codebase

```
COLLECTION_NAME = "informica_gte"
MODEL_PATH = "index_gte_informica_2_0"
MODEL_NAME = "Alibaba-NLP/gte-modernbert-base"
EMBED_MAX_SEQ_LENGTH = 8192
DENSE_EMBED_BATCH_SIZE = 32
EMBED_BATCH_MAX_TOKENS = 32000
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}
SPARSE_MODEL_NAME = "Qdrant/bm25"
# SOURCE_DIRS — same as config_informica
```

**Note:** `config_informica_gte` requires `transformers>=4.48.0`. The bump from 4.46.3
is backward-compatible with Jina (which breaks only at 5.x).

### 3. `config_informica_docs` — BGE-M3 on docs corpus *(after docs readers are ready)*

```
COLLECTION_NAME = "informica_docs"
MODEL_PATH = "index_bge_informica_docs"
MODEL_NAME = "BAAI/bge-m3"
EMBED_MAX_SEQ_LENGTH = 4096   # safe starting point; no ALiBi penalty
DENSE_EMBED_BATCH_SIZE = 16   # 570M model — conservative
EMBED_BATCH_MAX_TOKENS = 16000
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}
SPARSE_MODEL_NAME = "Qdrant/bm25"
SOURCE_DIRS = [{"type": "source_set", "path": "../informica-docs", "extensions": [...]}]
```

---

## What MODEL_REGISTRY Changes Are Needed

`shared/vram_cap.py` `MODEL_REGISTRY` needs new entries for the dynamic VRAM cap to work
correctly with each model. If `EMBED_DYNAMIC_VRAM_CAP = False` (current default), these
entries are only used for logging — but they should still be added for accuracy.

```python
"nomic-ai/CodeRankEmbed-137M": {
    "native_max": 8192,
    "num_heads": 12,
    "hidden_dim": 768,
    "num_layers": 12,
    "params_millions": 137.0,
},
"Alibaba-NLP/gte-modernbert-base": {
    "native_max": 8192,
    "num_heads": 12,
    "hidden_dim": 768,
    "num_layers": 22,   # ModernBERT-base: 22 layers
    "params_millions": 149.0,
},
```

The jina-code-embeddings-0.5b and 1.5b entries are not needed — both models are excluded.
BGE-M3 is already in `MODEL_REGISTRY` (added in a previous session).

---

## Prerequisite Work: Docs Readers

Before `config_informica_docs` can be used, readers for document formats must be added:

| Format | Reader approach | Complexity |
|---|---|---|
| `.txt` | Already handled (generic text splitter fallback) | None |
| `.pdf` | `pypdf` or `pdfminer.six` — extract text, chunk by section headers | Medium |
| `.docx` | `python-docx` — extract paragraphs/headings, chunk by heading level | Medium |
| `.xls` / `.xlsx` | `openpyxl` — extract sheet names + cell text, chunk by sheet/table | Medium–High |

PDF/DOCX are the most valuable; XLS is trickier (tabular data doesn't chunk well as text).
These readers can be added as `shared/readers/pdf_reader.py`, `docx_reader.py`, etc.,
following the same `BaseFileReader` interface as the existing readers.

This is a separate implementation task, not a blocker for the code model testing.

---

## Evaluation Plan

1. **Bump `transformers` pin** to `>=4.48.0` in `requirements.txt` (needed for `gte-modernbert-base`)
2. **Add MODEL_REGISTRY entries** for `CodeRankEmbed-137M` and `gte-modernbert-base` in `shared/vram_cap.py`
3. **Create `config_informica_coderank`** and **`config_informica_gte`** config files
4. **Run full index** on `informica_2_0` with each model (`--clear --yes`)
5. **Run `validate_rag.py`** against all three collections — record scores vs baseline (103/112 = 92.0%)
6. **Compare** jina-v2-base-code vs CodeRankEmbed-137M vs gte-modernbert-base on the 65-query suite
7. If a challenger wins: promote it to `config_informica`, retire the test config
8. Docs collection: tackle after docs readers are implemented

---

## Open Questions

1. **CodeRankEmbed-137M query prefix:** Nomic models often require a task prefix for
   queries (e.g., `"search_query: "`). CodeRankEmbed-137M's model card should be checked
   after downloading — if a prefix is required at query time, `rag_mcp.py`'s embed call
   needs a 1-line addition. Indexing does NOT use a prefix (documents are embedded as-is).

2. **gte-modernbert-base query prefix:** GTE models sometimes use `"Represent this sentence: "`
   or no prefix at all. The model card confirms: no task prefix needed for retrieval with
   `gte-modernbert-base`. Standard passage embedding works out of the box.

3. **Docs corpus size:** `../informica-docs` size is unknown. If it contains thousands of
   large PDFs, indexing time and Qdrant storage will be significant. Worth doing a file count
   before committing to the docs collection approach.

## Single MCP Server for Both Collections

The user requirement: one MCP server process serves both the code collection and the docs
collection — two tools, `search_code` and `search_docs`, registered on a single FastMCP
instance.

### What `rag_mcp.py` does today

The current server is entirely single-config:

- `config_loader.get_config(config_path=args.config)` loads one config at startup
- `get_embed_model(device=config.MCP_EMBED_DEVICE, cfg=config)` loads one model
- `get_qdrant_vector_store(cfg=config)` connects to one Qdrant collection
- One `VectorStoreIndex`, one `_index` variable, one `_build_index()` function
- One tool registered under `config.MCP_TOOL_NAME`

### What dual-collection requires

To serve both collections from one process:

1. **Two embed models loaded at startup** — one for code (`jina-v2-base-code` or
   `CodeRankEmbed-137M`, 768-dim), one for docs (`bge-m3`, 1024-dim). These are independent
   model instances; they do not share weights.

2. **Two Qdrant vector stores** — `informica_rag` (code) and `informica_docs_rag` (docs),
   potentially on different ports or the same Qdrant instance with different collection names.

3. **Two `VectorStoreIndex` objects** — one built with each embed model + vector store pair.

4. **Two tools registered on the same `FastMCP` instance** — `search_code` and
   `search_docs`. FastMCP supports registering multiple tools on one server; the existing
   `mcp.tool()(_search_tool)` call can be repeated with a second function.

5. **`--config` replaced by `--config-code` + `--config-docs`** (or a multi-config YAML)
   — the server needs to know both configs at startup.

### VRAM implications

Loading two models simultaneously on RTX 4060 (8 GB):

| Model | VRAM (fp16, inference) |
|---|---|
| `jina-v2-base-code` (161M, 768-dim) | ~1.5 GB |
| `CodeRankEmbed-137M` (137M, 768-dim) | ~1.2 GB |
| `bge-m3` (570M, 1024-dim) | ~2.5 GB |
| **Total (current Jina + BGE-M3)** | **~4 GB** |
| **Total (CodeRankEmbed + BGE-M3)** | **~3.7 GB** |

Both scenarios fit within 8 GB with comfortable headroom. The MCP server uses CPU by
default (`MCP_EMBED_DEVICE = "cpu"`), so VRAM is not a concern at query time — it only
matters during indexing. The MCP server loads the model for inference, which uses less
memory than the training/indexing batch configuration.

### Code change scope

This is a **moderate, non-breaking change** to `rag_mcp.py`. The core logic of
`_build_index()` and `_search_tool()` is reused — it just needs to be instantiated twice.

Rough design:

```python
# At startup: load both configs
config_code = config_loader.get_config(config_path=args.config_code)
config_docs = config_loader.get_config(config_path=args.config_docs)

# Build two indexes independently
_indexes = {}  # "code" -> VectorStoreIndex, "docs" -> VectorStoreIndex

def _build_index_for(cfg) -> VectorStoreIndex:
    embed_model = get_embed_model(device=cfg.MCP_EMBED_DEVICE, cfg=cfg)
    storage_context, _, _ = get_qdrant_vector_store(cfg=cfg, ...)
    return VectorStoreIndex.from_vector_store(storage_context.vector_store,
                                              embed_model=embed_model)

# Register two tools on one FastMCP instance
async def search_code(query: str, top_k: int = 8, branch: str = "") -> str:
    return await _do_search(_indexes["code"], config_code, query, top_k, branch)

async def search_docs(query: str, top_k: int = 8) -> str:
    return await _do_search(_indexes["docs"], config_docs, query, top_k, branch="")

mcp.tool()(search_code)
mcp.tool()(search_docs)
```

The shared `_do_search()` helper extracts the common logic from the current `_search_tool`.
The function names (`search_code`, `search_docs`) become the tool names in the MCP protocol.

### Config-driven vs hard-coded tool names

The current server reads `MCP_TOOL_NAME` from config to set the tool name dynamically.
For dual-collection, the tool names could be driven by a new config field
(`MCP_TOOL_NAME_CODE`, `MCP_TOOL_NAME_DOCS`) or simply hard-coded as `search_code` /
`search_docs` — since a dual-collection server is a different run mode, hard-coding is
acceptable and simpler.

### Startup time

Both models are loaded sequentially at startup. With `trust_remote_code=True` and local
weights already cached, each model takes ~5–15 s to load on CPU (MCP default). Total
startup time ~15–30 s — acceptable for a long-lived MCP server process.

### Graceful fallback: two separate MCP server instances

The alternative is to run two separate `rag_mcp.py` processes — one for code, one for docs
— each registered as a separate MCP server in `opencode.json`. This requires **zero code
changes** and is fully supported today.

| Approach | Code changes | VRAM at query | Startup | OpenCode config |
|---|---|---|---|---|
| Single server, two tools | Moderate (rag_mcp.py refactor) | CPU (same as now) | ~30 s | One MCP entry |
| Two separate servers | None | CPU (same as now) | ~15 s each | Two MCP entries |

**Recommendation:** Start with two separate servers (zero code risk). Consolidate to a
single server later if managing two config entries in `opencode.json` becomes annoying.
The two-server path also makes it easier to restart/reload just the docs server without
touching the code server.

---


- **TODO #2** — BGE-M3 neural sparse (vs BM25) is a hybrid querying experiment that becomes
  available once BGE-M3 is in use for the docs collection
- **TODO #5** — Model tracking becomes critical once multiple collections with different
  models coexist; the sidecar `collection_meta.json` design was built with this scenario in mind
