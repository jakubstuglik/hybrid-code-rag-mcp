# Embedding Model Exploration

**Status:** Code model contest completed (iteration-009). Baseline wins. Docs collection
evaluation deferred pending docs readers implementation.

---

## Current Production Setup (Unchanged)

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
| Validation score | **139/156 (89.1%)** on 78-test suite |

The ALiBi positional encoding causes a quadratic VRAM cost: the bias tensor is ~384 MB at
4096 tokens and ~1.5 GB at 8192. This is why `EMBED_MAX_SEQ_LENGTH` is capped at 4096.

**History note:** BGE-M3 was evaluated previously and rejected for the codebase. The
conclusion was that a model specifically trained on code gives better results for
Delphi/SQL/DFM content than a general-purpose multilingual model. That decision stands.
BGE-M3 is re-examined below only for the docs collection.

---

## Code Model Contest — Results (Iteration 009, 2026-03-17)

Full details: `docs/iterations/iteration-009.md`.

### Final Scores (78-test suite, max 156 pts)

| Model | Params | CoIR NDCG@10 | seq_len used | Truncated | Score | % | vs baseline |
|---|---|---|---|---|---|---|---|
| `jinaai/jina-embeddings-v2-base-code` *(baseline)* | 161M | ~56 | 4096 | — | **139/156** | **89.1%** | — |
| `nomic-ai/CodeRankEmbed` | 137M | 60.1 | 2048 * | 1.0% | **139/156** | **89.1%** | tie |
| `Alibaba-NLP/gte-modernbert-base` | 149M | 79.31 | 8192 | 0.01% | **131/156** | **84.0%** | **-5.1%** |

\* CodeRankEmbed limited to seq_len=2048 due to O(N²) attention fallback on Windows (see below).

**Verdict: baseline wins. No model change.**

### Results by Category

| Category | Baseline (Jina) | CodeRankEmbed | gte-modernbert |
|---|---|---|---|
| 1. Class Overview Queries | 10/11 | 10/11 | 8/11 |
| 2. Precise Identifier Search | 13/13 | 13/13 | 11/13 |
| 3. Cross-File / Dependency | 6/6 | 6/6 | 5/6 |
| 4. DFM Form Queries | 4/6 | 4/6 | 4/6 |
| 5. SQL Schema / Procedure | 6/6 | 6/6 | 6/6 |
| 6. Natural Language Code Understanding | 5/5 | 5/5 | 5/5 |
| 7. Edge Cases / Stress Tests | 4/4 | 4/4 | 4/4 |
| 8. AI Agent Workflow | 4/5 | 4/5 | 4/5 |
| 9. FR3 Report Queries | 4/4 | 4/4 | 4/4 |
| 10. DPROJ Project Queries | 2/3 | 2/3 | 2/3 |
| 11. File Disambiguation | 2/2 | 2/2 | 1/2 |
| 12. Semantic Paraphrase Queries | 4/8 | 4/8 | 3/8 |
| 13. Hard Identifier + Context | 1/3 | 1/3 | 1/3 |
| 14. Polish / Domain Language | 0/2 | 0/2 | 0/2 |

### Key Finding: CodeRankEmbed — O(N²) Attention Wall on Windows

CodeRankEmbed uses the `nomic-bert` architecture which relies on Flash Attention 2 for
O(N) VRAM scaling — but `flash-attn` is Linux-only. On Windows it falls back to standard
`torch.matmul(Q, K^T)` attention, which is O(N²) per sequence.

At seq_len=4096 with the full 11,040-file production corpus:
- Single-sequence attention matrix = `4096² × 12 heads × 2 bytes (fp16)` = 7.5 GiB per sample
- OOM crash on file 5 (`core.base.classes.pas`) which has many large chunks

**Safe ceiling on Windows: seq_len=2048** (attention = ~1.5 GiB per sample).

This means CodeRankEmbed on Windows is capped to half Jina's 4096-token context window.
A tie at a disadvantageous seq_len is not a win — the baseline stays.

### Key Finding: gte-modernbert-base — VRAM-Efficient but Lower Accuracy

ModernBERT uses RoPE + Flash Attention, confirmed O(N) VRAM scaling on Windows:

| Scenario | Peak VRAM | Truncated |
|---|---|---|
| test_sources, seq_len=1024 | 1,376 MiB | 4.9% |
| test_sources, seq_len=8192 | 3,595 MiB | 0.0% |
| **Full corpus, seq_len=8192** | **6,275 MiB** | **0.01% (14/135,235)** |

Despite essentially zero truncation and a 23-point CoIR NDCG@10 advantage over Jina,
gte-modernbert-base scored 84.0% vs baseline 89.1% (-5.1%). The cause: CoIR is a
general retrieval benchmark. Our task is domain-specific (Delphi Pascal, Polish language
domain, proprietary code conventions) — code-specialized Jina training outweighs the
benchmark gap for this corpus.

### Key Finding: Shared Failures Across All Three Models

These 4 tests fail for all models — they are indexing/reranker issues, not model-specific:

| Test | Query | Failure pattern |
|---|---|---|
| T28 | "TActionList in MainForm" | DFM component search not returning .dfm chunks |
| T69 | "authentication dialog for entering user credentials" | Globals.pas comments dominate (score=2.77, BM25 saturation) |
| T71 | "multi-step wizard navigation base class" | Semantic description doesn't match class names |
| T73 | "task scheduler that runs reports on a timetable" | DataSnapSchedule.pas not surfaced |

These are candidates for the next iteration (indexing/reranker improvements, not model changes).

### Dependency Changes (Iteration 009)

| Package | Before | After | Reason |
|---|---|---|---|
| `transformers` | 4.46.3 | 4.48.3 | ModernBERT added in 4.48.0; CodeRankEmbed compat |
| `tokenizers` | 0.20.3 | 0.21.4 | Required by transformers 4.48.x |
| `einops` | not installed | 0.8.2 | Required by CodeRankEmbed (nomic-bert) |

Jina baseline verified working with transformers 4.48.3 + tokenizers 0.21.4.

---

## Models Under Consideration (Commercial Use Only)

CC-BY-NC models (Salesforce SFR-Embedding-Code series) are excluded entirely.

### Code Collection Candidates (Contest Complete)

| Model | Params | Dims | Context | License | CoIR NDCG@10 | Contest outcome |
|---|---|---|---|---|---|---|
| `jinaai/jina-embeddings-v2-base-code` *(production)* | 161M | 768 | 8192 (ALiBi, capped 4096) | Apache 2.0 | ~56 | **Winner (baseline)** |
| `nomic-ai/CodeRankEmbed` | 137M | 768 | 8192 (capped 2048 on Windows) | Apache 2.0 | 60.1 | Eliminated — tie at seq_len disadvantage |
| `Alibaba-NLP/gte-modernbert-base` | 149M | 768 | 8192 | Apache 2.0 | 79.31 | Eliminated — -5.1% despite CoIR lead |

**Eliminated candidates (license/size/access):**
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

Measured and estimated figures:

| Scenario | VRAM Peak | Feasible? | Notes |
|---|---|---|---|
| Current: Jina 161M, batch=32, seq=4096 | ~2.5 GB | Yes (proven) | Baseline |
| CodeRankEmbed, batch=32, seq=2048 (Windows cap) | ~3.0 GB | Yes (proven) | OOMs at seq=4096 on full corpus |
| gte-modernbert-base, batch=32, seq=8192 | **6.275 GB** | Yes (proven) | Full production corpus, 14/135235 truncated |
| BGE-M3, batch=32, seq=4096 | ~4–5 GB | Probably yes | 1024-dim adds overhead |
| BGE-M3, batch=16, seq=2048 | ~2.5–3 GB | Yes | Reduce if OOM |

**CodeRankEmbed on Windows**: Despite using the `nomic-bert` architecture (Flash Attention 2
in theory), `flash-attn` is Linux-only. Windows falls back to O(N²) standard attention.
At seq_len=4096: `4096² × 12 heads × 2 bytes = 7.5 GiB` per sample — OOM on full corpus.
Safe ceiling: **seq_len=2048** (confirmed on 11,040-file production build).

**gte-modernbert-base on Windows**: ModernBERT's Flash Attention works on Windows via the
`transformers` implementation (no `flash-attn` package needed). Confirmed O(N) VRAM
scaling. Full 8192-token context usable with only 6.275 GiB peak on the full corpus.

---

## Two-Collection Architecture

### Code collection: `myproject_rag`
- Source: `../sample_repo` (Delphi Pascal, SQL, DFM, FR3, DPROJ)
- Model: one of the code-specialized models above
- Sparse: `Qdrant/bm25` (unchanged)
- Config: `project-configs/config_myproject/config.py` (already exists)

### Docs collection: `myproject_docs_rag`  *(new)*
- Source: `../sample-docs` (PDF, DOCX, XLS, TXT — natural language heavy)
- Model: `BAAI/bge-m3` or `nomic-embed-text-v1.5`
- Sparse: BGE-M3's own neural sparse (if using BGE-M3) or `Qdrant/bm25` (if nomic)
- Config: `project-configs/config_myproject_docs/config.py` *(new)*
- MCP: Separate MCP server instance or extend the existing one with a second tool

This is the correct separation. Code-specialized models for code, general-NL model for
docs. No quality compromise on either side.

**Docs reader work needed:** PDF, DOCX, XLS files are not currently handled by any reader.
Before the docs collection can be indexed, readers for these formats must be added. This is
a non-trivial prerequisite (see "Prerequisite Work" section below).

---

## Prerequisite Work: Docs Readers

Before `config_myproject_docs` can be used, readers for document formats must be added:

| Format | Reader approach | Complexity |
|---|---|---|
| `.txt` | Already handled (generic text splitter fallback) | None |
| `.pdf` | `pypdf` or `pdfminer.six` — extract text, chunk by section headers | Medium |
| `.docx` | `python-docx` — extract paragraphs/headings, chunk by heading level | Medium |
| `.xls` / `.xlsx` | `openpyxl` — extract sheet names + cell text, chunk by sheet/table | Medium–High |

PDF/DOCX are the most valuable; XLS is trickier (tabular data doesn't chunk well as text).
These readers can be added as `shared/readers/pdf_reader.py`, `docx_reader.py`, etc.,
following the same `BaseFileReader` interface as the existing readers.

---

## Next Steps

### Immediate (iteration 010 candidates)

The 4 shared failures across all models are the highest-leverage targets:

| Test | Failure | Likely fix |
|---|---|---|
| T28 | TActionList DFM component search | Investigate DFM reader chunk coverage for non-root components |
| T69 | BM25 saturation (score=2.77) on Globals.pas comments | Reranker penalty for comment node_types on non-target files |
| T71 | Semantic description vs class names mismatch | Improve class_overview natural-language summaries |
| T73 | DataSnapSchedule.pas not surfaced | Check why this file doesn't appear; check chunk coverage |

### Deferred: Docs Collection

1. Implement `shared/readers/pdf_reader.py` and `shared/readers/docx_reader.py`
2. Create `project-configs/config_myproject_docs/config.py` using BGE-M3 dense + BM25 sparse
3. Build and validate docs index with `validate_rag.py` (docs-specific test cases)
4. Wire up as second MCP server or extend `rag_mcp.py` for dual-collection mode

---

## Single MCP Server for Both Collections (Design)

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

1. **Two embed models loaded at startup** — one for code (Jina 768-dim), one for docs
   (BGE-M3 1024-dim). These are independent model instances; they do not share weights.
2. **Two Qdrant vector stores** — `myproject_rag` (code) and `myproject_docs_rag` (docs).
3. **Two `VectorStoreIndex` objects** — one built with each embed model + vector store pair.
4. **Two tools on the same `FastMCP` instance** — `search_code` and `search_docs`.
5. **`--config` replaced by `--config-code` + `--config-docs`** — or a multi-config YAML.

### VRAM implications (MCP server uses CPU)

The MCP server uses `MCP_EMBED_DEVICE = "cpu"` by default — VRAM is not a concern at
query time. Both models loaded on CPU:

| Model | RAM (fp16, CPU inference) |
|---|---|
| `jina-v2-base-code` (161M, 768-dim) | ~1.5 GB RAM |
| `bge-m3` (570M, 1024-dim) | ~2.5 GB RAM |
| **Total** | **~4 GB RAM** |

### Graceful fallback: two separate MCP server instances

The alternative is two separate `rag_mcp.py` processes, each registered as a separate
MCP server in `opencode.json`. Zero code changes, fully supported today.

| Approach | Code changes | Startup | OpenCode config |
|---|---|---|---|
| Single server, two tools | Moderate (`rag_mcp.py` refactor) | ~30 s | One MCP entry |
| Two separate servers | None | ~15 s each | Two MCP entries |

**Recommendation:** Start with two separate servers (zero code risk). Consolidate later
if managing two entries in `opencode.json` becomes inconvenient.

---

- **TODO #2** — BGE-M3 neural sparse (vs BM25) becomes available once BGE-M3 is in use
  for the docs collection
- **TODO #5** — Model tracking becomes critical once multiple collections with different
  models coexist; the sidecar `collection_meta.json` design was built with this scenario in mind
