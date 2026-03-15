# Iteration 008 — Proportional Target Matching for File Disambiguation

**Date:** 2026-03-15
**Author:** AI agent (with human supervision)
**Status:** completed — 93.1% production score (121/130), +1 point, zero regressions

## Hypothesis

> When multiple files share the same name (e.g., 5 different `ReportHelpers.pas` files),
> path-qualified queries like `"Common/LPC/ReportHelpers.pas"` fail to surface the correct
> file because the reranker's `_chunk_matches_target()` was boolean — any file matching
> ANY target identifier got the same bonus. By changing it to return a proportional score
> (fraction of matched targets), chunks matching all path components get a full bonus while
> partial matches get proportionally less (and more penalty).

## Root Cause Analysis

Three compounding factors caused `Common/LPC/ReportHelpers.pas` (the main 25-chunk file)
to be buried by 4 smaller `ReportHelpers.pas` files:

1. **Dense embedding dilution**: The `Common/LPC/ReportHelpers.pas` uses clause is 13,211
   chars / 197 lines — a massive wall of unit names. The Jina model produces a single
   768-dim vector. Smaller variants (BusStopOnline: 105 chars, ForisAP: 75 chars) have
   much higher signal-to-noise ratio.

2. **Boolean target matching**: `_chunk_matches_target()` returned `True` for ANY target
   match. With query targets `['common', 'lpc', 'reporthelpers']`, all 5 ReportHelpers
   files matched on `'reporthelpers'` alone — indistinguishable to the reranker.

3. **Path components not extracted**: `extract_target_identifiers()` had no regex for
   slash-separated paths like `Common/LPC/ReportHelpers.pas`.

## Changes Made

### 1. Path-Component Extraction in `extract_target_identifiers()`

**File:** `shared/reranker.py` (line ~397)

Added regex `((?:[A-Za-z][A-Za-z0-9_]*/)+[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9]+)?)` to
detect slash-separated paths in queries. Each component is extracted as a separate target:
- `"Common/LPC/ReportHelpers.pas"` → targets `['common', 'lpc', 'reporthelpers']`

### 2. Proportional `_chunk_matches_target()` (bool → float)

**File:** `shared/reranker.py` (line ~452)

Changed return type from `bool` to `float` (0.0 to 1.0) — the fraction of targets matched:
- `Common/LPC/ReportHelpers.pas` matching 3/3 → `1.0` (full bonus)
- `BusStopOnline/ReportHelpers.pas` matching 1/3 → `0.33` (1/3 bonus + 2/3 penalty)

### 3. Proportional Bonus/Penalty Scaling in `_compute_rerank_score()`

**File:** `shared/reranker.py` (line ~576)

- `_TARGET_MATCH_BONUS` is now multiplied by `match_score`: full bonus only for full match
- `_NON_TARGET_OVERVIEW_PENALTY` is now multiplied by `(1.0 - match_score)`: partial matches
  get proportional penalty, not all-or-nothing
- Comment penalty (`_CROSS_FILE_COMMENT_PENALTY`) only applies to `match_score == 0.0` (no
  match at all), not to partial matches

### 4. Validation Test Cases T64-T65

**File:** `validate_rag.py` (line ~1008)

New "File Disambiguation" category with 2 tests:

| Test | Query | Aspect |
|------|-------|--------|
| T64 | `"What units does Common/LPC/ReportHelpers.pas use?"` | Path-qualified: must find declUses from Common/LPC/ variant |
| T65 | `"ReportHelpers.pas class overview"` | Unqualified: largest file should rank above smaller variants |

### 5. Unit Test Updates

**File:** `tests/shared/test_reranker.py`

- Updated 13 existing `TestChunkMatchesTarget` tests from `is True`/`is False` assertions
  to `== 1.0`/`== 0.0` (float return type)
- Added 2 new tests:
  - `test_multiple_targets_all_match` — all targets found → 1.0
  - `test_multiple_targets_partial_path_match` — 1/3 targets found → 0.33

Total: 265 tests, all passing.

## Baseline (Before Fix)

| Metric | Value |
|--------|-------|
| Validation score | 120/130 (92.3%) |
| PASS / PARTIAL / FAIL | 56 / 8 / 1 |
| Rating | Excellent |
| T64 | PARTIAL (Common/LPC not in top 3) |
| T65 | PASS |

## Results (After Fix)

| Metric | Value | Delta |
|--------|-------|-------|
| Validation score | 121/130 (93.1%) | **+1** |
| PASS / PARTIAL / FAIL | 57 / 7 / 1 | +1 PASS, -1 PARTIAL |
| Rating | Excellent | Maintained |
| T64 | **PASS** | Improved |
| T65 | PASS | Maintained |

### Zero Regressions

All 63 pre-existing tests maintained their exact results from the iteration 007 baseline.

## Why Only +1 Point?

The fix is narrowly targeted at path-qualified disambiguation queries — a specific failure
mode. T65 (unqualified `"ReportHelpers.pas class overview"`) already passed because the
Common/LPC variant has the most chunks (25 vs 1-5 for others), giving it natural ranking
advantage through volume. T64 was the only test that specifically failed due to the boolean
target matching limitation.

The real value of this fix is **forward-looking**: as more same-name files are encountered
in production queries, the proportional matching will correctly disambiguate them without
needing new reranker rules per file.

## Files Changed

| File | Lines Changed | Type |
|------|--------------|------|
| `shared/reranker.py` | +55 -30 | Core fix |
| `tests/shared/test_reranker.py` | +50 -20 | Test updates |
| `validate_rag.py` | +30 -4 | New test cases |

## Iteration History

| Iteration | Score (prod) | Delta | Tests |
|-----------|-------------|-------|-------|
| 001 (baseline) | 65/88 (73.9%) | — | 44 |
| 002 (reranker tuning) | 68/88 (77.3%) | +3 | 44 |
| 003 (DFM detection) | 70/88 (79.5%) | +2 | 44 |
| 004 (overfetch + patterns) | 101/112 (90.2%) | +4 | 56 |
| 005c (SQL NL desc) | 94/112 (83.9%) | -7 | 56 |
| 006 (validator + reranker) | 103/112 (92.0%) | +9 | 56 |
| 007 (FR3/DPROJ rewrite) | 116/126 (92.1%) | +9 | 63 |
| **008 (file disambiguation)** | **121/130 (93.1%)** | **+1** | **65** |

## Next Steps

1. **More disambiguation test cases** — add queries for other same-name files to validate
   the proportional matching works broadly
2. **Remaining non-PASS tests** (T01, T03, T05, T06, T28, T31, T43, T53) — cross-file
   interloper problems that may benefit from the proportional approach if reformulated
   with path qualifiers
