# Iteration 002 — Reranker Tuning: DFM vs Class Overview Separation

**Date:** 2026-03-11
**Author:** AI agent (with human supervision)
**Status:** committed

## Hypothesis

> Increasing `_PRIMARY_OVERVIEW_BONUS` from 0.50 to 0.65, splitting DFM overview types
> into a separate set with a lower bonus (0.10 vs 0.25), and adding a DFM-on-Pascal-class
> penalty (0.15) should improve Class Overview queries because DFM form headers will no
> longer outrank class_summary/class_overview chunks for queries about Pascal classes.

## Changes Made

- **File:** `shared/reranker.py`
  - `_PRIMARY_OVERVIEW_BONUS`: 0.50 -> 0.65 (stronger boost for class_summary/class_overview)
  - New `_DFM_OVERVIEW_TYPES` frozenset containing `dfm_form_header` (separated from `_OVERVIEW_CHUNK_TYPES`)
  - New `_DFM_OVERVIEW_BONUS`: 0.10 (DFM overview types get a lower boost than other secondary types)
  - New `_DFM_ON_CLASS_QUERY_PENALTY`: 0.15 (applied when query targets a T-prefixed Pascal class)
  - `_NON_TARGET_OVERVIEW_PENALTY`: 0.20 -> 0.30 (more aggressive cross-file suppression)
  - `_compute_rerank_score()` updated with 3-tier bonus logic: primary > structural > DFM
  - Pascal class detection added: `targets_pascal_class = any(t.startswith("t") and len(t) > 2 for t in targets)`
  - `dfm_form_header` removed from `_OVERVIEW_CHUNK_TYPES` to prevent double-boosting

- **File:** `tests/shared/test_reranker.py`
  - 10 existing tests updated for new constant values
  - 3 new tests added:
    - `test_dfm_gets_lower_bonus_than_structural_overview`
    - `test_dfm_penalized_when_query_targets_pascal_class`
    - `test_dfm_not_penalized_when_no_pascal_class_target`
  - Total: 125 reranker tests (was 122)

- **No config changes.** All changes are query-time reranker parameters (no reindex needed).

## Baseline (Before — Iteration 001)

| Metric | Value |
|--------|-------|
| Validation pass rate | 65/88 (73.9%) |
| Rating | Acceptable |
| PASS / PARTIAL / FAIL | 26 / 13 / 5 |
| Class Overview category | 9/18 (50%) |

## Results (After)

| Metric | Value | Delta |
|--------|-------|-------|
| Validation pass rate | 68/88 (77.3%) | **+3 points (+3.4%)** |
| Rating | Acceptable | — |
| PASS / PARTIAL / FAIL | 28 / 12 / 4 | +2 PASS, -1 PARTIAL, -1 FAIL |
| Class Overview category | ~13/18 (72%) | **+4 points (+22%)** |

## Detailed Test-by-Test Changes

### Improvements (+5 points)

| Test | Query | Before | After | Notes |
|------|-------|--------|-------|-------|
| T04 | "Describe TfrmSplash" | FAIL | PASS | class_summary now at #1 instead of DFM form header |
| T07 | "Tell me about TSalesReport" | PARTIAL | PASS | class_summary now at #1 |
| T08 | "Overview of TEmar105_OIK" | PARTIAL | PASS | class_summary now at #1 |
| T09 | "What fields does TdmMain have?" | PARTIAL | PASS | class_summary_split at #3 |

### Regressions (-2 points)

| Test | Query | Before | After | Notes |
|------|-------|--------|-------|-------|
| T27 | "SFTP frame components" | PARTIAL | FAIL | DFM penalty too aggressive for form-specific query. "frame components" triggers overview detection, class_summary outranks dfm_form_header. No T-prefix target extracted, so `_DFM_ON_CLASS_QUERY_PENALTY` does not fire -- regression caused by reduced DFM bonus (0.10 vs old 0.25) and increased non-target penalty (0.30 vs 0.20). |

### Unchanged

| Test | Query | Status | Notes |
|------|-------|--------|-------|
| T05 | "What does TfrmBaseEditor do?" | FAIL | defProc from other files at top. BaseEditorForm class_summary doesn't appear in retrieval pool. Reranker can't fix what isn't retrieved. |
| T25 | "MainTurdus form components" | PASS | Still PASS but dfm_form_header dropped to #2 (declUses at #1). Marginal -- could flip to PARTIAL in future. |
| T35 | "How to export relief tickets" | FAIL | Dense embedding limitation. No ReliefExport files surfaced. Not a reranker issue. |
| T42 | "Where are report types defined?" | FAIL | Dense embedding limitation. REPORT_TYPE constants not surfaced. Not a reranker issue. |

## Analysis

### What Worked

The 3-tier bonus system (primary > structural > DFM) effectively separates class overview
chunks from DFM form headers. For queries with clear T-prefixed targets (T04, T07, T08, T09),
the class_summary/class_overview chunks now consistently outrank DFM form headers. This was
the primary goal and it succeeded.

### What Didn't Work

The T27 regression reveals a design gap: **queries that target DFM content but don't
mention a T-prefixed class** get hurt by the reduced DFM bonus. "SFTP frame components"
has no T-prefix target, so `_DFM_ON_CLASS_QUERY_PENALTY` doesn't fire, but the lower
base DFM bonus (0.10 vs old 0.25) still suppresses the DFM form header relative to
class_summary chunks from matching files.

### Root Cause of T27 Regression

1. "frame components" matches the `\bframe\s+components\b` overview pattern
2. Overview mode activates, boosting class_summary by +0.65
3. DFM form header only gets +0.10 (was +0.25 when it was in `_OVERVIEW_CHUNK_TYPES`)
4. The 0.55 gap (0.65 - 0.10) is too large for the DFM chunk's raw score advantage to overcome
5. No T-prefix target detected, so the class penalty doesn't fire -- but the damage is already
   done by the lower base bonus

### Remaining Failures (Not Addressable by Reranker)

- **T05**: BaseEditorForm file is likely not producing class_summary chunks that match the
  query, or the chunks score too low in raw retrieval to appear even with 5x overfetch.
  Needs investigation at the reader/chunking level.
- **T35, T42**: Dense embedding limitations for natural-language queries about concepts
  (not identifiers). These queries need either: (a) a better dense model, or (b) enhanced
  chunk metadata/context that makes BM25 match on relevant keywords.

## Decision

**Committed.** Net positive: +3 points (68 vs 65), +3.4% improvement. The T27 regression
(-1 point) is outweighed by the 4 improvements (+5 points). The regression has a clear
root cause and can be addressed in iteration-003.

## Current Parameter Values (After This Iteration)

### Reranker Parameters (`shared/reranker.py`)

| Parameter | Value | Changed? |
|-----------|-------|----------|
| `OVERFETCH_MULTIPLIER` | 5 | No |
| `_PRIMARY_OVERVIEW_BONUS` | 0.65 | **Yes** (was 0.50) |
| `_OVERVIEW_BONUS` | 0.25 | No |
| `_DFM_OVERVIEW_BONUS` | 0.10 | **New** |
| `_DFM_ON_CLASS_QUERY_PENALTY` | 0.15 | **New** |
| `_TARGET_MATCH_BONUS` | 0.15 | No |
| `_NON_TARGET_OVERVIEW_PENALTY` | 0.30 | **Yes** (was 0.20) |
| `_CROSS_FILE_COMMENT_PENALTY` | 0.30 | No |
| `_DETAIL_PENALTY` | 0.05 | No |

### All Other Parameters (Unchanged)

| Parameter | Value |
|-----------|-------|
| `HYBRID_ALPHA` | 0.5 |
| `MODEL_NAME` | `jinaai/jina-embeddings-v2-base-code` |
| `EMBED_MAX_SEQ_LENGTH` | 4096 |
| `DENSE_EMBED_BATCH_SIZE` | 32 |
| `SPARSE_EMBED_BATCH_SIZE` | 32 |
| `EMBED_BATCH_MAX_TOKENS` | 16000 |

## Unit Tests

| Suite | Tests | Status |
|-------|-------|--------|
| All tests | 875 | Passing |
| Reranker tests | 125 | Passing (3 new) |

## Next Steps

1. **Iteration 003: Fix T27 regression** — Add a "form/DFM-specific query" detector that
   detects queries about forms, frames, DFM components. When the query targets DFM content
   (not a Pascal class), reverse the DFM penalty and boost DFM chunks instead. Possible
   approach: detect keywords like "form", "frame", "components", "dfm" combined with the
   absence of a T-prefixed target.

2. **Investigate T05** — Why doesn't BaseEditorForm's class_summary appear in the retrieval
   pool even with 5x overfetch? May need reader-level investigation.

3. **Consider T35/T42** — These are dense embedding limitations. Options:
   - Add natural-language keywords to chunk context prefixes (e.g., "relief export", "report types")
   - Accept as model limitations and document in the test criteria
   - Consider a cross-encoder reranker for semantic queries (major architectural change)
