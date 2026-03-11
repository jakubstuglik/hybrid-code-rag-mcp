# Iteration 003 — DFM Query Detection & General Identifier Extraction

**Date:** 2026-03-11
**Author:** AI agent (with human supervision)
**Status:** committed

## Hypothesis

> Adding a DFM query detector (`is_dfm_query()`) that recognizes queries about forms,
> frames, and DFM components, combined with bonus-swapping logic that promotes DFM chunks
> over class_summary chunks for DFM-targeted queries, should fix the T27 regression from
> iteration-002. Additionally, a general identifier extraction pattern (`_GENERAL_IDENT`)
> that captures any capitalized word (3+ chars) will improve target matching for queries
> like "SFTP frame components" where the target identifier isn't T-prefixed or in a
> hardcoded allowlist.

## Changes Made

- **File:** `shared/reranker.py`
  - New `_DFM_QUERY_PATTERNS` list: 10 regex patterns detecting DFM-related queries
    (`form components`, `frame components`, `form layout`, `dfm`, `.dfm`,
    `form header`, `form properties`, `form design`, `visual components`, `UI components`)
  - New `is_dfm_query()` function: returns True when query matches any DFM pattern
  - New `_GENERAL_IDENT` pattern: `r"\b([A-Z][A-Za-z0-9_]{2,})\b"` — captures any
    capitalized word with 3+ characters as a potential target identifier
  - New `_TARGET_STOP_WORDS` frozenset: ~40 common English words filtered from general
    identifier extraction (What, How, Where, Tell, Describe, Class, etc.)
  - `BaseEditorForm` added to `_FILE_STEM_NO_EXT` allowlist
  - `extract_target_identifiers()` updated: after existing pattern checks, applies
    `_GENERAL_IDENT` to capture identifiers like "SFTP" that aren't T-prefixed
  - `_compute_rerank_score()` signature updated: added `is_dfm: bool` parameter
  - Bonus-swapping logic: when `is_dfm=True`, DFM chunks get `_PRIMARY_OVERVIEW_BONUS`
    (0.65) and class_summary types get `_DFM_OVERVIEW_BONUS` (0.10) — reversed from
    default behavior. `_DFM_ON_CLASS_QUERY_PENALTY` only applies when `is_dfm=False`.
  - `rerank_results()` updated: computes `dfm_mode = is_dfm_query(query)` and passes
    it to `_compute_rerank_score()`

- **File:** `tests/shared/test_reranker.py`
  - Fixed all 27 existing `_compute_rerank_score` calls — added `is_dfm=False` parameter
  - Updated `test_no_targets_in_generic_query` — changed query from "how do I install
    Python?" to "how do I install this?" (Python is now correctly captured by `_GENERAL_IDENT`)
  - New `TestIsDfmQuery` class (20 tests): 10 positive patterns, 3 case-insensitivity,
    7 negative cases
  - New `TestComputeRerankScoreDfmMode` class (10 tests): bonus swapping, penalty
    suppression, DFM vs class comparisons
  - New `TestGeneralIdentifierExtraction` class (15 tests): SFTP extraction, stop word
    filtering, deduplication, BaseEditorForm allowlist
  - 2 new integration tests in `TestRerankResults`: `test_dfm_query_promotes_dfm_form_header`,
    `test_dfm_query_with_overfetch_promotes_dfm`
  - Total: 174 reranker tests (was 125)

- **No config changes.** All changes are query-time reranker parameters (no reindex needed).

## Baseline (Before — Iteration 002)

| Metric | Value |
|--------|-------|
| Validation pass rate | 68/88 (77.3%) |
| Rating | Acceptable |
| PASS / PARTIAL / FAIL | 28 / 12 / 4 |
| DFM Form Queries category | 5/8 (62.5%) |

## Results (After)

| Metric | Value | Delta |
|--------|-------|-------|
| Validation pass rate | 70/88 (79.5%) | **+2 points (+2.2%)** |
| Rating | Acceptable | — |
| PASS / PARTIAL / FAIL | 29 / 12 / 3 | +1 PASS, 0 PARTIAL, -1 FAIL |
| DFM Form Queries category | 6/8 (75%) | **+1 point (+12.5%)** |

## Detailed Test-by-Test Changes

### Improvements (+2 points)

| Test | Query | Before | After | Notes |
|------|-------|--------|-------|-------|
| T27 | "SFTP frame components" | FAIL | PASS | `dfm_form_header` from `WithFrame_SFTP.dfm` at #1. DFM query detection activates bonus-swapping; `_GENERAL_IDENT` extracts "SFTP" as target identifier. |

### Regressions (0 points)

None. All iteration-002 improvements (T04, T07, T08, T09) remain PASS.

### Unchanged

| Test | Query | Status | Notes |
|------|-------|--------|-------|
| T05 | "What does TfrmBaseEditor do?" | FAIL | `BaseEditorForm.dfm` form header appears at #3, but .pas class_summary doesn't surface. Dense embedding for "TfrmBaseEditor" doesn't match `BaseEditorForm.pas` well enough. Not a reranker issue — retrieval gap. |
| T25 | "MainTurdus form components" | PASS | `dfm_form_header` at #1, stable. DFM query detection correctly activates here too. |
| T35 | "How to export relief tickets" | FAIL | Dense embedding limitation. No ReliefExport files surfaced. Not a reranker issue. |
| T42 | "Where are report types defined?" | FAIL | Dense embedding limitation. REPORT_TYPE constants not surfaced. Not a reranker issue. |

## Analysis

### What Worked

The `is_dfm_query()` detector correctly identifies queries about forms, frames, and DFM
components. The bonus-swapping mechanism elegantly reverses the priority: for DFM queries,
DFM chunks get the primary boost (0.65) while class_summary chunks get the reduced boost
(0.10). This is the exact inverse of the default behavior, which means DFM queries and
class queries each get optimal treatment without compromising the other.

The `_GENERAL_IDENT` pattern successfully extracted "SFTP" from "SFTP frame components",
allowing target matching against `WithFrame_SFTP.dfm`. This is more robust than adding
every possible identifier to a hardcoded allowlist.

### What Didn't Work

T05 remains FAIL despite adding `BaseEditorForm` to `_FILE_STEM_NO_EXT`. The issue is not
target extraction — it's that the dense embedding for "TfrmBaseEditor" doesn't semantically
match chunks from `BaseEditorForm.pas`. The class_summary chunk exists in the index but
scores too low in raw retrieval to appear even with 5x overfetch. This is a fundamental
retrieval gap, not a reranker issue.

### Design Decisions

1. **Bonus swapping vs. separate parameters**: Rather than introducing new DFM-specific
   bonus values, we reuse `_PRIMARY_OVERVIEW_BONUS` and `_DFM_OVERVIEW_BONUS` but swap
   which chunk types they apply to. This keeps the parameter space small and makes the
   behavior symmetric and predictable.

2. **General identifier extraction**: The `_GENERAL_IDENT` pattern (`[A-Z][A-Za-z0-9_]{2,}`)
   is intentionally broad. The `_TARGET_STOP_WORDS` frozenset filters out ~40 common English
   words that would otherwise be false-positive identifiers. This is more maintainable than
   growing a hardcoded allowlist.

3. **DFM penalty suppression**: When `is_dfm=True`, the `_DFM_ON_CLASS_QUERY_PENALTY` is
   not applied. This prevents DFM chunks from being penalized when the query explicitly
   targets DFM content.

## Decision

**Committed.** Net positive: +2 points (70 vs 68), +2.2% improvement. Zero regressions.
The T27 regression from iteration-002 is fully fixed. Cumulative improvement from baseline:
+5 points (70 vs 65), +5.6%.

## Current Parameter Values (After This Iteration)

### Reranker Parameters (`shared/reranker.py`)

| Parameter | Value | Changed? |
|-----------|-------|----------|
| `OVERFETCH_MULTIPLIER` | 5 | No |
| `_PRIMARY_OVERVIEW_BONUS` | 0.65 | No |
| `_OVERVIEW_BONUS` | 0.25 | No |
| `_DFM_OVERVIEW_BONUS` | 0.10 | No |
| `_DFM_ON_CLASS_QUERY_PENALTY` | 0.15 | No |
| `_TARGET_MATCH_BONUS` | 0.15 | No |
| `_NON_TARGET_OVERVIEW_PENALTY` | 0.30 | No |
| `_CROSS_FILE_COMMENT_PENALTY` | 0.30 | No |
| `_DETAIL_PENALTY` | 0.05 | No |
| `is_dfm_query()` | 10 patterns | **New** |
| `_GENERAL_IDENT` | `[A-Z][A-Za-z0-9_]{2,}` | **New** |
| `_TARGET_STOP_WORDS` | ~40 words | **New** |

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
| All tests | 924 | Passing |
| Reranker tests | 174 | Passing (49 new) |

## Progress Toward Target

| Iteration | Score | Delta | Cumulative |
|-----------|-------|-------|------------|
| 001 (baseline) | 65/88 (73.9%) | — | — |
| 002 (reranker tuning) | 68/88 (77.3%) | +3 | +3 |
| 003 (DFM detection) | 70/88 (79.5%) | +2 | +5 |
| Target | 79/88 (90%) | — | +14 needed |

9 more points needed to reach 90% target. Remaining 3 FAILs (T05, T35, T42) account for
6 points; converting the 12 PARTIALs to PASS would add 12 points. The most impactful
next steps target PARTIAL->PASS conversions.

## Next Steps

1. **Investigate T05** — "What does TfrmBaseEditor do?" The class_summary from
   `BaseEditorForm.pas` doesn't appear in the retrieval pool. May need: (a) a synonym
   or alias in the context prefix ("TfrmBaseEditor" -> "BaseEditorForm"), (b) reader-level
   changes to add the form class name to the unit context prefix, or (c) accepting this
   as a limitation of the model's ability to match `TfrmBaseEditor` to `BaseEditorForm`.

2. **Convert PARTIALs to PASS** — 12 PARTIAL results represent +12 potential points.
   Analyzing which are closest to flipping (e.g., T13, T18, T21, T28, T30, T31) may
   yield higher ROI than chasing the remaining FAILs.

3. **T35/T42** — Dense embedding limitations. Options remain:
   - Add natural-language keywords to chunk context prefixes
   - Accept as model limitations
   - Consider a cross-encoder reranker (major architectural change)
