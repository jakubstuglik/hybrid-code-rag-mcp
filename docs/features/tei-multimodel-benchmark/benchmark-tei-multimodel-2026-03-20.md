# Multi-Model TEI Benchmark Report

**Date:** 2026-03-20
**Corpus:** Informica 2.0 codebase (11,044 source files — Delphi Pascal, T-SQL, DFM, DPROJ, FR3)
**Vectors per run:** 136,522 (135,307 main branch + 1,215 feature branch overlay)
**Validation suite:** 78 tests across 14 categories (max score: 156 points)
**GPU:** NVIDIA (consumer-grade, VRAM stats below)
**Hybrid search:** `HYBRID_ALPHA = 0.5` (50% dense + 50% BM25 sparse), reranker enabled

---

## 1. Models Tested

| # | Model | Backend | Dimensions | Max Seq Len | dtype | Notes |
|---|-------|---------|-----------|-------------|-------|-------|
| 1 | `jinaai/jina-embeddings-v2-base-code` | PyTorch GPU | 768 | 4096 | float16 | Baseline. Code-specific model. ALiBi attention (O(N^2) VRAM). |
| 2 | `jinaai/jina-embeddings-v2-base-code` | TEI GPU | 768 | 4096 | float16 | Same model, TEI Candle backend. |
| 3 | `Qwen/Qwen3-Embedding-0.6B` | TEI GPU | 1024 | 32768 | float16 | 0.6B params. RoPE attention. Largest context window tested. |
| 4 | `BAAI/bge-m3` | TEI GPU | 1024 | 8192 | float16 | General-purpose multilingual. RoPE. Built-in sparse ignored (BM25 used instead). |
| 5 | `google/embeddinggemma-300m` | TEI GPU | 1152 | 8192 | **float32** | 300M params. Matryoshka dims. Requires float32 (TEI Candle limitation). |
| 6 | `nomic-ai/nomic-embed-text-v2-moe` | TEI GPU | 768 | 8192 | float16 | MoE architecture. Requires `search_query:`/`search_document:` prefixes. TEI enforces 512 max tokens per request (model config `n_positions=2048`). |

All runs share: `EMBED_BATCH_SIZE_DENSE = 32`, `EMBED_BATCH_SIZE_SPARSE = 32`, `EMBED_BATCH_MAX_TOKENS = 16000`, `SPARSE_MODEL_NAME = "Qdrant/bm25"`.

---

## 2. Results Summary

### 2.1 Validation Scores

| Model | Backend | Score | Pct | PASS | PARTIAL | FAIL |
|-------|---------|------:|----:|-----:|--------:|-----:|
| **TEI Jina v2 base code** | TEI GPU | **139**/156 | **89.1%** | 64 | 11 | 3 |
| PyTorch Jina v2 base code | PyTorch GPU | 138/156 | 88.5% | 63 | 12 | 3 |
| BAAI/bge-m3 | TEI GPU | 132/156 | 84.6% | 59 | 14 | 5 |
| Qwen3-Embedding-0.6B | TEI GPU | 130/156 | 83.3% | 57 | 16 | 5 |
| google/embeddinggemma-300m | TEI GPU | 129/156 | 82.7% | 57 | 15 | 6 |
| nomic-embed-text-v2-moe | TEI GPU | 126/156 | 80.8% | 55 | 16 | 7 |

**Winner: Jina v2 base code** on both backends, with TEI marginally ahead (+1 point). The code-specific model outperforms all general-purpose models by 4.5-8.3 percentage points.

### 2.2 Indexing Performance

| Model | Backend | Total Time | Embed Time | Embed % | Speedup vs PyTorch |
|-------|---------|----------:|----------:|--------:|-------------------:|
| **TEI Jina** | TEI GPU | 26.5 min | 19.4 min | 73.4% | **4.5x** |
| TEI BGE-M3 | TEI GPU | 35.6 min | 27.3 min | 76.6% | 3.2x |
| TEI Qwen3 | TEI GPU | 45.4 min | 37.2 min | 81.9% | 2.3x |
| TEI Nomic | TEI GPU | 77.4 min | 68.3 min | 88.2% | 1.3x |
| TEI Gemma-300M | TEI GPU | 80.5 min | 72.9 min | 90.5% | 1.2x |
| PyTorch Jina | PyTorch GPU | 95.3 min | 87.4 min | 91.8% | 1.0x (baseline) |

Non-embedding overhead (parsing, BM25 sparse, Qdrant upsert, SQLite manifest) was ~7-9 minutes across all runs, confirming embedding is the dominant cost.

### 2.3 GPU Resource Usage

| Model | Backend | Avg GPU Util | Avg/Peak Temp | Avg/Peak VRAM Ded | Avg/Peak VRAM Shared |
|-------|---------|------------:|-------------:|------------------:|---------------------:|
| TEI Jina | TEI GPU | 28.3% | 53.5/69 C | 1,814/2,440 MiB | 239/327 MiB |
| TEI BGE-M3 | TEI GPU | 33.7% | 56.9/73 C | 2,855/3,324 MiB | 246/249 MiB |
| TEI Qwen3 | TEI GPU | 40.1% | 59.1/73 C | 2,879/3,616 MiB | 268/362 MiB |
| TEI Nomic | TEI GPU | 26.4% | 49.9/55 C | 2,695/2,791 MiB | 260/262 MiB |
| TEI Gemma-300M | TEI GPU | 52.8% | 57.9/67 C | 3,240/5,384 MiB | 259/262 MiB |
| PyTorch Jina | PyTorch GPU | 73.3% | 57.3/71 C | 4,975/7,858 MiB | 2,823/6,638 MiB |

**Key observation:** PyTorch Jina used 7.9 GB dedicated + 6.6 GB shared VRAM (peak), while TEI Jina used only 2.4 GB dedicated + 0.3 GB shared. TEI's Candle/Rust backend is dramatically more VRAM-efficient.

---

## 3. Per-Category Score Breakdown

| Category | Max | PT Jina | TEI Jina | TEI Qwen3 | TEI BGE-M3 | TEI Gemma | TEI Nomic |
|----------|----:|--------:|---------:|----------:|-----------:|----------:|----------:|
| AI Agent Workflow | 10 | 9 | 9 | 9 | 8 | 9 | 9 |
| Class Overview Queries | 22 | 17 | 17 | 18 | **21** | 19 | 19 |
| Cross-File / Dependency | 12 | **12** | **12** | 10 | **12** | 11 | **12** |
| DFM Form Queries | 12 | **11** | **11** | 9 | 7 | 8 | 7 |
| DPROJ Project Queries | 6 | 5 | 5 | 5 | 5 | 5 | 5 |
| Edge Cases / Stress Tests | 8 | **8** | **8** | **8** | **8** | **8** | **8** |
| FR3 Report Queries | 8 | **8** | **8** | **8** | **8** | **8** | 7 |
| File Disambiguation | 4 | **4** | **4** | **4** | **4** | **4** | **4** |
| Hard Identifier + Context | 6 | 2 | 2 | 3 | 3 | 2 | 3 |
| Natural Language Code Understanding | 10 | **10** | **10** | **10** | **10** | **10** | 9 |
| Polish / Domain Language | 4 | 2 | 2 | 2 | 3 | 2 | 2 |
| Precise Identifier Search | 26 | **26** | **26** | 24 | 25 | 24 | 25 |
| SQL Schema / Procedure | 12 | 11 | **12** | 11 | 11 | 11 | 11 |
| **Semantic Paraphrase Queries** | **16** | **13** | **13** | 9 | 7 | 8 | 5 |

### Category Analysis

- **Semantic Paraphrase Queries** is the biggest differentiator. Jina scores 13/16 while Nomic scores only 5/16. These tests use natural language descriptions (e.g., "authentication dialog for entering user credentials") to find code — a task where code-trained embeddings excel.
- **Class Overview Queries** is where BGE-M3 leads (21/22 vs Jina's 17/22). BGE-M3's multilingual training may help with class summary chunks.
- **DFM Form Queries** strongly favor Jina (11/12 vs BGE-M3/Nomic at 7/12). DFM files are Delphi-specific — code-trained models understand them better.
- **Precise Identifier Search** — all models do well (24-26/26) because BM25 handles exact keyword matches regardless of dense embedding quality.
- **Edge Cases / Stress Tests** and **File Disambiguation** — perfect scores across all models. The chunking strategy and reranker handle these well regardless of model.

---

## 4. Failure Analysis

### 4.1 All Failed Tests

| Test | Query | PT Jina | TEI Jina | Qwen3 | BGE-M3 | Gemma | Nomic |
|------|-------|:-------:|:--------:|:-----:|:------:|:-----:|:-----:|
| T05 | What does TfrmBaseEditor do? | **F** | **F** | **F** | P | P | P |
| T26 | Splash form layout | P | P | **F** | P | **F** | P |
| T27 | SFTP frame components | P | P | P | **F** | P | **F** |
| T28 | TActionList in MainTurdus | A | A | A | **F** | **F** | **F** |
| T66 | background worker that populates a list view with historical data | P | P | P | A | P | **F** |
| T68 | GPS coordinates input widget for editing location points | P | P | P | A | A | **F** |
| T69 | authentication dialog for entering user credentials | **F** | **F** | **F** | **F** | **F** | **F** |
| T71 | multi-step wizard navigation base class for content creation | P | P | **F** | **F** | **F** | **F** |
| T73 | task scheduler that runs reports on a timetable and exports results | P | P | **F** | **F** | **F** | **F** |
| T76 | SLS_ReliefExport_Bilety_Get input parameters | **F** | **F** | A | A | **F** | A |

P = PASS, A = PARTIAL, **F** = FAIL

### 4.2 Universal Failures (all 6 models FAIL)

- **T69** — "authentication dialog for entering user credentials": No model can map this natural language description to the actual Delphi login form. The semantic gap between "authentication dialog" and the actual class/form name is too large for any tested model.

### 4.3 Hard Tests (FAIL or PARTIAL on 4+ models)

- **T28** — "TActionList in MainTurdus": Jina variants get PARTIAL, all others FAIL. The identifier exists but is buried in a large DFM form — dense embeddings dilute it.
- **T71** — "multi-step wizard navigation base class": Only Jina PASSes. The paraphrase→code mapping requires strong code understanding.
- **T73** — "task scheduler that runs reports on a timetable and exports results": Only Jina PASSes. Same pattern as T71.
- **T76** — "SLS_ReliefExport_Bilety_Get input parameters": Jina FAILs but Qwen3/BGE-M3/Nomic get PARTIAL. The procedure header chunk exists but different models rank it differently.

### 4.4 Model-Specific Weaknesses

| Model | Unique/Rare FAILs | Pattern |
|-------|-------------------|---------|
| **Jina** (both) | T05 (TfrmBaseEditor), T76 (SQL parameters) | Weak on a specific class overview and SQL parameter lookup |
| **Qwen3** | T26 (splash form) | Occasional DFM weakness |
| **BGE-M3** | T27 (SFTP frame) | DFM form queries generally weak (7/12) |
| **Gemma** | T26 (splash form) | Plus shared failures on T28, T71, T73 |
| **Nomic** | T27, T66, T68 | Worst on semantic paraphrase (5/16), plus unique DFM/form failures |

---

## 5. Key Findings

### 5.1 TEI vs PyTorch (Same Model Comparison)

Using the identical Jina v2 base code model:

| Metric | PyTorch GPU | TEI GPU | Improvement |
|--------|------------|---------|-------------|
| Validation score | 88.5% | 89.1% | +0.6% (within noise) |
| Embedding time | 87.4 min | 19.4 min | **4.5x faster** |
| Peak VRAM (dedicated) | 7,858 MiB | 2,440 MiB | **3.2x less** |
| Peak VRAM (shared) | 6,638 MiB | 327 MiB | **20x less** |

**Conclusion:** TEI is strictly superior for this model — same quality, 4.5x faster, dramatically less VRAM. The Candle/Rust backend is highly optimized compared to Python/PyTorch.

### 5.2 Model Quality Ranking

1. **Jina v2 base code (89.1%)** — Best overall. Code-specific training pays off, especially on semantic paraphrase queries (13/16) and DFM forms (11/12).
2. **BGE-M3 (84.6%)** — Best class overviews (21/22) but worst DFM forms (7/12). Strong multilingual capability may help with Polish domain terms (3/4 vs Jina's 2/4).
3. **Qwen3-Embedding-0.6B (83.3%)** — Solid mid-range. Largest context (32K) but didn't translate to better scores. 0.6B params didn't outperform smaller specialized models.
4. **embeddinggemma-300M (82.7%)** — Handicapped by float32 requirement (2x VRAM, slower). Matryoshka capability unused. Max 2048 seq effective limit.
5. **nomic-embed-text-v2-moe (80.8%)** — Worst overall. MoE architecture may be suboptimal for code. TEI's 512-token-per-request limit is a significant handicap. Worst on semantic paraphrase (5/16).

### 5.3 Speed vs Quality Tradeoff

| Model | Score | Embed Time | Score/Minute |
|-------|------:|----------:|-----------:|
| TEI Jina | 89.1% | 19.4 min | 4.59%/min |
| TEI BGE-M3 | 84.6% | 27.3 min | 3.10%/min |
| TEI Qwen3 | 83.3% | 37.2 min | 2.24%/min |
| TEI Nomic | 80.8% | 68.3 min | 1.18%/min |
| TEI Gemma | 82.7% | 72.9 min | 1.13%/min |
| PyTorch Jina | 88.5% | 87.4 min | 1.01%/min |

TEI Jina dominates on efficiency — highest score AND fastest embedding time.

### 5.4 What BM25 Hybrid Search Provides

The 50/50 hybrid alpha is critical. All models achieve near-perfect scores (24-26/26) on **Precise Identifier Search** because BM25 keyword matching handles exact identifiers regardless of dense embedding quality. Without BM25, weaker models would score much lower on identifier lookups.

The reranker's overview query detection and score adjustments further normalize performance across models for structured queries (class overviews, form headers).

---

## 6. Recommendations

1. **Use TEI Jina v2 base code for production.** Highest quality (89.1%), fastest indexing (19.4 min), lowest VRAM (2.4 GB peak). No reason to use PyTorch backend.

2. **Keep HYBRID_ALPHA = 0.5.** The 50/50 dense+sparse balance compensates for dense embedding limitations on exact identifiers and large overview chunks.

3. **Do not switch to a general-purpose model** unless the corpus changes significantly (e.g., adding non-code documents). The 4.5-8.3% quality gap is substantial.

4. **BGE-M3 is the best alternative** if Jina becomes unavailable or a multilingual corpus is needed. It leads on class overviews and Polish language terms but loses on DFM forms and semantic paraphrase.

5. **Nomic and Gemma are not recommended** for code RAG. Nomic's TEI token limit (512) severely constrains it, and Gemma's float32 requirement doubles VRAM usage with no quality benefit.

6. **Future testing candidates:**
   - `jinaai/jina-embeddings-v4` — multimodal, but TEI support is partial as of March 2026
   - `int8` quantization of Jina v2 — could further reduce VRAM while maintaining quality
   - `BAAI/bge-m3` with built-in sparse vectors (replacing BM25) — worth testing if dense+native-sparse outperforms dense+BM25

---

## 7. Appendix: Configuration Reference

All benchmark configs are in `project-configs/config_informica_tei_*/config.py`. Validation results in `project-configs/config_informica*/validation_results.json`. Indexing logs and GPU stats CSVs in the respective `qdrant/` subdirectories.

| Config | Qdrant Port | TEI Port | Collection Name |
|--------|------------|---------|----------------|
| `config_informica` (PyTorch baseline) | 6333 | — | `informica_rag` |
| `config_informica_tei_jinaai` | 6340 | 8090 | `informica_tei_jinaai` |
| `config_informica_tei_qwen3` | 6335 | 8091 | `informica_tei_qwen3` |
| `config_informica_tei_bge_m3` | 6336 | 8092 | `informica_tei_bge_m3` |
| `config_informica_tei_gemma` | 6337 | 8093 | `informica_tei_gemma` |
| `config_informica_tei_nomic` | 6338 | 8094 | `informica_tei_nomic` |
