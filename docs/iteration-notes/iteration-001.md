# Iteration 001 — Baseline Measurement

**Date:** 2026-03-10
**Author:** AI agent (with human supervision)
**Status:** committed

## Purpose

This is the initial baseline iteration — no changes are being made.  It documents the
state of the system after the chunking strategy overhaul (commit `5c3bc8f`) and the
embedding model fix + OOM prevention work.  All future iterations measure improvement
against these numbers.

## System State

### Configuration

| Parameter | Value |
|-----------|-------|
| `MODEL_NAME` | `jinaai/jina-embeddings-v2-base-code` |
| `INDEXING_MODE` | `hybrid` |
| `SPARSE_MODEL_NAME` | `Qdrant/bm25` |
| `HYBRID_ALPHA` | `0.5` |
| `EMBED_MAX_SEQ_LENGTH` | `4096` |
| `EMBED_MODEL_KWARGS` | `{"torch_dtype": "float16"}` |
| `DENSE_EMBED_BATCH_SIZE` | `32` |
| `SPARSE_EMBED_BATCH_SIZE` | `32` |
| `EMBED_BATCH_MAX_TOKENS` | `16000` |
| `HYBRID_EMBED_SINGLE_PASS` | `False` (two-pass) |
| `INDEX_EMBED_DEVICE` | `cuda` |
| `EMBED_DYNAMIC_VRAM_CAP` | `False` (static cap) |

### Hardware

| Resource | Value |
|----------|-------|
| GPU | NVIDIA GeForce RTX 4060 |
| Dedicated VRAM | 8188 MiB |
| Shared GPU memory | ~16 GB (from 32 GB system RAM) |
| System RAM | 32 GB |
| OS | Windows |

### Codebase

| Metric | Value |
|--------|-------|
| Total source files | ~12,400 |
| Total chunks produced | ~140,354 |
| Languages | Delphi Pascal, T-SQL, DFM, FR3, DPROJ |

## Quality Baseline (Manual 14-Query Suite)

These are the results from the **manual** evaluation harness (`query_test_index.py`),
run after the chunking strategy overhaul (Round 10 — Final).

| Q# | Query | Result | Top chunk |
|----|-------|--------|-----------|
| 1 | What is TdmMain? | PASS | class_summary_split from MainDM.pas at #2 |
| 2 | Classes in emar105? | PASS | class_summary at #1 |
| 3 | What is TfrmMainTurdus? | PASS | class_overview at #2 |
| 4 | Splash form | PASS | dfm_form_header at #1 |
| 5 | REPORT_TYPE_PUNCTUALITY_RIDES | PASS | Exact match at #1 |
| 6 | PrepareDataSet | PASS | Implementation at #1 |
| 7 | OpenConnection | PASS | Implementation at #1, class_overview at #3 |
| 8 | SLS_ReliefExport_Bilety_Get | PASS | procedure_header at #2 |
| 9 | TCK_FarePrice_GetPriceForXDesignation | PASS | function_header at #1 |
| 10 | GetCardSerialNumber | PASS | method_group at #3 |
| 11 | uses clause MainDM | PASS | declUses at #1 |
| 12 | TClientDataSet cdsStoredProc | PASS | DFM group at #1 |
| 13 | MainTurdus form components | PASS | dfm_form_header at #1 |
| 14 | SFTP frame components | PASS | dfm_form_header at #1 |

**Result: 14/14 PASS (100%)** with `HYBRID_ALPHA = 0.5`.

### Automated Validation Suite (44 Tests)

First run of `validate_rag.py` against the production index (2026-03-10):

**Overall: 26 PASS, 13 PARTIAL, 5 FAIL — 73.9% (65/88 points) — Rating: Acceptable**

| Category | PASS | PARTIAL | FAIL | Score |
|----------|------|---------|------|-------|
| 1. Class Overview Queries | 3 | 3 | 3 | 9/18 |
| 2. Precise Identifier Search | 8 | 2 | 0 | 18/20 |
| 3. Cross-File / Dependency | 4 | 1 | 0 | 9/10 |
| 4. DFM Form Queries | 2 | 2 | 0 | 6/8 |
| 5. SQL Schema / Procedure | 2 | 2 | 0 | 6/8 |
| 6. Natural Language Code Understanding | 2 | 1 | 1 | 5/8 |
| 7. Edge Cases / Stress Tests | 3 | 1 | 0 | 7/8 |
| 8. AI Agent Workflow | 2 | 1 | 1 | 5/8 |

#### Failed Tests (5)

| Test | Query | Issue |
|------|-------|-------|
| T01 | "What is TdmMain?" | DFM form headers dominate — class_summary/overview not in top results |
| T04 | "Describe TfrmSplash" | DFM form headers dominate over class overview chunks |
| T05 | "What does TfrmBaseEditor do?" | Same DFM dominance pattern |
| T35 | "How to export relief tickets" | No ReliefExport/Bilety files in top results |
| T42 | "Where are report types defined?" | REPORT_TYPE/C_REPORT_ constants not surfaced |

#### Key Observations

1. **Class Overview queries are the weakest category** (9/18 = 50%). The reranker's
   overview boost is not strong enough to overcome DFM form header dominance when both
   .pas and .dfm files match the same class name.
2. **Precise Identifier Search is the strongest** (18/20 = 90%). BM25 keyword matching
   works well for exact identifiers.
3. **DFM form headers frequently appear above class summaries** for overview queries.
   This is the primary regression vs the manual 14-query suite, which had different
   query wording that happened to favor .pas chunks.
4. **SQL queries show decent but not perfect results** — procedure_header chunks work
   well but procedure_body sometimes beats procedure_header in ranking.

## Performance Baseline (Production Indexing Run)

From the full production indexing run on 2026-03-10 (with `EMBED_MAX_SEQ_LENGTH=4096`):

| Metric | Value | Notes |
|--------|-------|-------|
| Total indexing time | 1h 59m | Full reindex (~12,400 files) |
| Dense embedding time | 5,433s | 92.3% of total time |
| Total chunks embedded | 140,354 | — |
| Embedding errors | 0 | — |
| Peak dedicated VRAM | 7,866 MiB | 96.1% of 8,188 MiB |
| Peak shared VRAM | 6,892 MiB | Significant spilling |
| Average shared VRAM | 2,833 MiB | Well above 1 GB target |
| GPU utilization at 100% | 66% of samples | — |
| GPU utilization at 1-25% | 21.2% of samples | Starvation between batches |
| Truncated chunks | Not measured | Need to run with truncation tracking |

## Assessment Against Success Criteria

### Quality

| Criterion | Target | Current | Status |
|-----------|--------|---------|--------|
| Validation pass rate (44-test) | >= 90% | 73.9% (65/88) | BELOW TARGET |
| Manual suite pass rate | >= 90% | 14/14 (100%) | EXCEEDS |
| Zero excluded files | Yes | Yes | PASS |
| Overview queries top-3 | >= 90% | 50% (category 1) | BELOW TARGET |
| Exact identifier top-1 | >= 95% | 90% (category 2) | BELOW TARGET |

### Performance

| Criterion | Target | Current | Status |
|-----------|--------|---------|--------|
| Indexing time | < 1.5 hours | 1h 59m | BELOW TARGET |
| Avg GPU utilization | > 70% | ~66% at 100% | BELOW TARGET |
| Avg shared VRAM | < 1 GB | 2,833 MiB | BELOW TARGET |
| Peak dedicated VRAM | < 7,500 MiB | 7,866 MiB | BELOW TARGET |
| CUDA OOM errors | 0 | 0 | PASS |

### Summary

**Quality needs work** — the 44-test automated suite reveals weaknesses that the
manual 14-query suite did not catch.  The primary issue is **DFM form headers
dominating class overview queries** (T01, T04, T05).  The reranker needs stronger
boosting for class_summary/class_overview chunks, or DFM form headers need
penalization for overview queries about .pas classes.

**Performance needs improvement** — shared VRAM spilling is 2.8x the target, indexing
time is 32% over target, and GPU utilization has significant gaps.

## Unit Tests

| Test Suite | Tests | Status |
|------------|-------|--------|
| All existing tests | 788+ | Passing |
| `test_vram_cap.py` | 85 | Passing (new) |
| Total | 873+ | Passing |

## Next Steps

1. **Priority: Fix class overview query weakness** — tune reranker to boost class_summary/
   class_overview over dfm_form_header for overview queries about classes
2. Investigate dynamic VRAM cap (`EMBED_DYNAMIC_VRAM_CAP=True`) for throughput improvement
3. Profile GPU utilization gaps — is the bottleneck CPU tokenization or batch preparation?
4. Consider pipelined double-buffered batching to overlap CPU and GPU work
5. Address the 5 FAIL cases — may need test criteria adjustments or reranker tuning
