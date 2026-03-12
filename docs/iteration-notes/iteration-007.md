# Iteration 007 — FR3 & DPROJ Reader Rewrite

**Date:** 2026-03-12
**Author:** AI agent (with human supervision)
**Status:** completed — 92.1% production score (Excellent), no regressions

## Hypothesis

> The FR3 (FastReport) and DPROJ (Delphi project) readers are completely broken — they
> produce almost no useful chunks due to fundamental XML parsing bugs. Rewriting both
> readers with correct element names and namespace handling should make FR3/DPROJ content
> searchable, improving the validation score by adding meaningful coverage for ~340 files
> (265 FR3 + 75 DPROJ) that were previously producing garbage chunks.

## Root Cause Analysis

### FR3 Reader — Wrong XPath Element Names

The old FR3 reader searched for `Page`, `Band`, `Memo` elements but actual FastReport XML uses:
- **`TfrxReportPage`** (not `Page`)
- **`TfrxPageHeader`**, **`TfrxMasterData`**, **`TfrxPageFooter`**, **`TfrxReportTitle`**,
  **`TfrxReportSummary`**, **`TfrxGroupHeader`** (not `Band`)
- **`TfrxMemoView`** with `Text` as an **XML attribute** (not child element)

Result: The reader found zero meaningful elements and fell back to full-file chunks.

### DPROJ Reader — XML Namespace Not Handled

The old DPROJ reader used bare XPath like `.//PropertyGroup` but the DPROJ file uses
MSBuild namespace `http://schemas.microsoft.com/developer/msbuild/2003`. All element
queries returned empty. Additionally, the file has a UTF-8 BOM that must be handled with
`utf-8-sig` encoding.

Result: The reader found zero property groups or item groups and produced only file-level chunks.

## Changes Made

### 1. FR3 Reader — Complete Rewrite

**File:** `shared/readers/fr3_reader.py` (~462 lines, was ~142 lines)

- Correct FastReport element names (`TfrxReportPage`, `TfrxMemoView`, etc.)
- Band-level chunking with `fr3_band_content` node type grouping all TfrxMemoView Text
  attributes within a band
- Report overview chunk (`fr3_report_overview`) with band summary, page count, and script info
- Pascal script extraction from base64-encoded `TfrxReport.Script.Text` attribute
- Variables extraction from `TfrxReport.Variables.Text` attribute
- Context prefix: `// Report: <ReportName> (<filename>)`
- Small band grouping to prevent too-tiny chunks (follows DFM reader grouping pattern)
- Node types: `fr3_report_overview`, `fr3_band_content`, `fr3_pascal_script`, `fr3_variables`

### 2. DPROJ Reader — Complete Rewrite

**File:** `shared/readers/dproj_reader.py` (~529 lines, was ~189 lines)

- Proper MSBuild namespace handling via `_ns()` helper
- UTF-8 BOM support with `utf-8-sig` encoding
- Project overview chunk (`dproj_project_overview`) with project GUID, main source,
  framework type, compiler defines, version info
- Build configuration chunks (`dproj_build_config`) for Release/Debug configs with
  distinct compiler and linker settings
- Unit group chunks (`dproj_unit_group`) grouping DCCReferences by directory
- `_build_cfg_name_map()` for resolving Cfg_N references to human-readable config names
- Correct handling of dual `'$(Base)'!=''` PropertyGroups (skip empty first one)
- Context prefix: `// Project: <ProjectName> (<filename>)`
- Node types: `dproj_project_overview`, `dproj_build_config`, `dproj_unit_group`

### 3. Reranker Updates

**File:** `shared/reranker.py`

- Added FR3 query detection: `is_fr3_query()` with patterns for report, .fr3, FastReport,
  TfrxMemoView, band, etc.
- Added DPROJ query detection: `is_dproj_query()` with patterns for .dproj, project file,
  build config, DCCReference, compiler, linker, etc.
- Domain-specific overview bonuses: FR3/DPROJ overview types get primary bonus (+0.65) only
  when query targets that domain; otherwise mild +0.10 bonus
- Updated `_compute_rerank_score()` with `is_fr3`/`is_dproj` parameters
- FR3 overview types: `fr3_report_overview`
- DPROJ overview types: `dproj_project_overview`
- Detail types updated: `fr3_variables`, `dproj_unit_group`

### 4. Validation Test Cases

**File:** `validate_rag.py` — Added T57-T63 (7 new test cases)
**File:** `docs/rag-validation-tests.md` — Added Category 9 (FR3) and Category 10 (DPROJ)

| Test | Query | Category | Aspect |
|------|-------|----------|--------|
| T57 | "SettlementWithCarriersByRides report layout" | FR3 Report Queries | Dense + Reranker |
| T58 | "TfrxMemoView SettlementWithCarriers" | FR3 Report Queries | Sparse |
| T59 | "ListOfPrintOut report bands" | FR3 Report Queries | Dense + Reranker |
| T60 | "DrillDown ListOfPrintOut" | FR3 Report Queries | Sparse |
| T61 | "Informica.dproj project overview" | DPROJ Project Queries | Dense + Reranker |
| T62 | "DCCReference Informica" | DPROJ Project Queries | Sparse |
| T63 | "Debug build config Informica.dproj" | DPROJ Project Queries | Dense |

### 5. Bug Fix

**File:** `index_rag.py` line 756 — Replaced `→` (U+2192) with `->` ASCII equivalent
to fix `UnicodeEncodeError` on Windows cp1250 console during reindex.

### 6. Documentation Updates

**File:** `AGENTS.md`
- Updated node_type reference table (54 → 62 types, added FR3/DPROJ rows)
- Updated test counts (873 → 1136)
- Removed FR3/DPROJ from "Remaining Work" section

## Baseline (Before)

Captured against production index with 140,543 vectors (broken FR3/DPROJ chunks).

| Metric | Value |
|--------|-------|
| Validation score | 107/126 (84.9%) |
| PASS count | 48 |
| PARTIAL count | 11 |
| FAIL count | 4 |
| Rating | Good |
| T01-T56 score | 103/112 (92.0%) |
| T57-T63 score | 4/14 (28.6%) — 0 PASS, 4 PARTIAL, 3 FAIL |
| Total vectors | 140,543 |
| FR3/DPROJ vectors | 738 (broken) |

## Results (After)

Selective purge of FR3/DPROJ vectors + incremental reindex of 340 files.

| Metric | Value | Delta |
|--------|-------|-------|
| Validation score | 116/126 (92.1%) | **+9** |
| PASS count | 54 | +6 |
| PARTIAL count | 8 | -3 |
| FAIL count | 1 | -3 |
| Rating | **Excellent** | Upgrade |
| T01-T56 score | 103/112 (92.0%) | 0 (no regression) |
| T57-T63 score | 13/14 (92.9%) — 6 PASS, 1 PARTIAL, 0 FAIL | **+9** |
| Total vectors | 142,359 | +1,816 |
| FR3/DPROJ vectors | 2,554 (meaningful) | +1,816 net |
| Manifest files | 12,533 | +340 |
| Reindex time | ~8 minutes | Incremental |
| Truncated chunks | 10/2,554 (0.4%) | Below 1% target |

## Detailed Test Results — New Tests (T57-T63)

| Test | Query | Before | After | Top Match | Score |
|------|-------|--------|-------|-----------|-------|
| T57 | SettlementWithCarriersByRides report layout | FAIL | **PASS** | fr3_report_overview | 0.966 |
| T58 | TfrxMemoView SettlementWithCarriers | FAIL | **PASS** | fr3_band_content | 0.500 |
| T59 | ListOfPrintOut report bands | PARTIAL | **PASS** | fr3_report_overview | 0.500 |
| T60 | DrillDown ListOfPrintOut | PARTIAL | **PASS** | fr3_band_content | 0.500 |
| T61 | Informica.dproj project overview | FAIL | **PASS** | dproj_project_overview | 0.717 |
| T62 | DCCReference Informica | PARTIAL | **PASS** | dproj_unit_group | 0.500 |
| T63 | Debug build config Informica.dproj | PARTIAL | PARTIAL | dproj_build_config | 0.500 |

### T63 Analysis (Remaining PARTIAL)

T63 asks for "Debug build config Informica.dproj". The top result is a `dproj_build_config`
chunk but from `UpgradeLayouts.dproj` instead of `Informica.dproj`. The Informica build config
is present in the index but ranks lower. This is a BM25 keyword saturation issue — both files
contain similar "Debug" build config content, and UpgradeLayouts.dproj scored slightly higher
on BM25 matching.

## Existing Tests — No Regression

All T01-T56 results are **identical** to the iteration 006 baseline. The only FAIL remains
T05 (TfrmBaseEditor cross-file interloper), which is a pre-existing hard problem.

### Notable Side Effect

T16 (`ADMIN_ReportDef_AnalysisRoute`) now shows `fr3_report_overview` from
`AnalysisRoute.fr3` at position #1 (score 0.500). This is actually a useful result — the
FR3 report layout is directly related to the SQL procedure. The test still PASS because
`procedure_header` is at position #2.

## Test Suite

| Module | Tests | Status |
|--------|-------|--------|
| `tests/shared/readers/test_fr3_reader.py` | 74 | All passing (new) |
| `tests/shared/readers/test_dproj_reader.py` | 49 | All passing (new) |
| `tests/shared/test_reranker.py` | 263 | All passing (updated) |
| All other tests | 844 | All passing (unchanged) |
| **Total** | **1230** | **0 failures** |

## Files Changed

| File | Lines | Type |
|------|-------|------|
| `shared/readers/fr3_reader.py` | ~462 (rewrite) | Reader |
| `shared/readers/dproj_reader.py` | ~529 (rewrite) | Reader |
| `shared/reranker.py` | ~40 lines changed | Reranker |
| `tests/shared/readers/test_fr3_reader.py` | ~1200 (new) | Tests |
| `tests/shared/readers/test_dproj_reader.py` | ~850 (new) | Tests |
| `tests/shared/test_reranker.py` | ~200 lines changed | Tests |
| `validate_rag.py` | ~80 lines added | Validation |
| `docs/rag-validation-tests.md` | ~60 lines added | Documentation |
| `AGENTS.md` | ~30 lines changed | Documentation |
| `index_rag.py` | 1 line changed | Bug fix |

## Conclusion

Iteration 007 successfully fixed the completely broken FR3 and DPROJ readers, adding
meaningful search coverage for ~340 files (265 FR3 + 75 DPROJ) that were previously
producing garbage chunks. The production score improved from 84.9% to 92.1% (+9 points),
maintaining the "Excellent" rating with zero regressions on existing tests.

Key achievements:
1. **FR3 reader rewrite** — correct FastReport XML element names, band-level chunking,
   report overview with summary, Pascal script extraction
2. **DPROJ reader rewrite** — MSBuild namespace handling, BOM support, build config parsing,
   unit group chunking by directory
3. **Reranker domain detection** — FR3/DPROJ-specific query patterns and score adjustments
4. **2,554 new meaningful vectors** replacing 738 broken ones (3.5x more useful chunks)
5. **1,230 tests passing** with 74+49 new reader tests and 140 new reranker tests

## Iteration History

| Iteration | Score (prod) | Delta | Tests |
|-----------|-------------|-------|-------|
| 001 (baseline) | 65/88 (73.9%) | — | 44 |
| 002 (reranker tuning) | 68/88 (77.3%) | +3 | 44 |
| 003 (DFM detection) | 70/88 (79.5%) | +2 | 44 |
| 004 (overfetch + patterns) | 101/112 (90.2%) | +4 | 56 |
| 005c (SQL NL desc) | 94/112 (83.9%) | -7 | 56 |
| 006 (validator + reranker) | 103/112 (92.0%) | +9 | 56 |
| **007 (FR3/DPROJ rewrite)** | **116/126 (92.1%)** | **+9** | **63** |

## Next Steps

1. **Investigate T63** — DPROJ build config targeting could be improved with stronger
   file stem matching in the reranker
2. **Remaining T01-T56 non-PASS tests** (T01, T03, T05, T06, T28, T31, T43, T53) —
   these are pre-existing hard problems, mostly cross-file interloper issues
3. **Consider adding more FR3/DPROJ test queries** to expand coverage
4. **Performance optimization** — the full reindex target of <1 hour is still a stretch goal
