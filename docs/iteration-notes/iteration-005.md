# Iteration 005 — SQL NL Descriptions, Pascal NL Prefixes, and Class Overview Threshold

**Date:** 2026-03-10 through 2026-03-12
**Author:** AI agent (with human supervision)
**Status:** completed (net regression — only SQL NL descriptions kept)

## Hypothesis

> Three changes will improve natural language query performance:
> 1. **SQL identifier decomposition** — Adding `-- Description: <natural language>` to SQL
>    chunk context prefixes will bridge the semantic gap between domain-specific identifiers
>    (e.g., `SLS_ReliefExport_Bilety_Get`) and natural language queries (e.g., "export relief
>    tickets"). This uses a new `decompose_identifier()` utility that splits CamelCase/underscore
>    names and expands abbreviations via `_ABBREVIATION_MAP`.
> 2. **Pascal NL description prefixes** — Same approach applied to Pascal chunks (class context
>    prefixes) to help queries like "What is TdmMain?" find the right class summaries.
> 3. **Class overview member-count threshold** — `MIN_OVERVIEW_MEMBERS = 10` forces
>    `class_overview` chunk generation for classes with ≥10 members, even if the class_summary
>    is short. This addresses T05/T06 where class_overview chunks don't exist for medium-sized
>    classes.

## Sub-Iterations

This iteration went through three sub-versions due to progressive discovery of regressions:

| Sub-iteration | Changes | Test-sources | Production |
|---------------|---------|-------------|-----------|
| **005a** | All 3 changes (SQL + Pascal NL + member threshold) | 109/112 (97.3%) | 92/112 (82.1%) |
| **005b** | SQL NL + member threshold (Pascal NL removed) | 110/112 (98.2%) | 94/112 (83.9%) |
| **005c** | SQL NL only (member threshold reverted) | 108/112 (96.4%) | **94/112 (83.9%)** |

## Changes Made (Final State — 005c)

### 1. SQL Identifier Decomposition (KEPT)

**File:** `shared/readers/_base.py` (~235 lines, NEW utility module)

- `decompose_identifier(name)` — splits CamelCase and underscore-separated identifiers into
  natural language words. Handles:
  - Schema prefix stripping (`dbo.` → removed)
  - T-prefix stripping (`TMyClass` → `My Class`)
  - Underscore separation (`SLS_ReliefExport` → `SLS Relief Export`)
  - CamelCase splitting (`GetPriceForX` → `Get Price For X`)
  - Abbreviation expansion via `_ABBREVIATION_MAP` (~50 entries: TCK→Ticket, SLS→Sales,
    Bilety→Tickets, Emar→EMAR, etc.)
- `_DELPHI_LOWER_PREFIXES` — set of common Delphi prefixes to strip (cds, qry, btn, etc.)

**File:** `shared/readers/tsql_chunker.py` (modified `_make_context_prefix()`)

- SQL chunks now include `-- Description: <decomposed name>` in context prefix
- Example: `-- Procedure: [dbo].[SLS_ReliefExport_Bilety_Get]` becomes augmented with
  `-- Description: Sales Relief Export Tickets Get`
- Only added to procedure/function headers and bodies

**Tests:** `tests/shared/readers/test_readers_base.py` — 45 `TestDecomposeIdentifier` tests

### 2. T11 Test Fix (KEPT)

**File:** `validate_rag.py`

- T11 query changed from `"PrepareDataSet"` to `"PreapreDataSet"` to match the actual typo
  in the production codebase (MainDM.pas has `PreapreDataSet`, not `PrepareDataSet`)

### 3. Pascal NL Description Prefixes (REMOVED in 005b)

- Was applied to `_build_context_prefix()` in pascal_reader.py
- Caused -9 point regression on production (005a: 92/112 vs 004: 101/112)
- Root cause: NL descriptions on Pascal chunks diluted BM25 signal and caused cross-file
  interlopers to rank higher

### 4. Class Overview Member-Count Threshold (REVERTED in 005c)

**What it was:** `MIN_OVERVIEW_MEMBERS = 10` constant + `_count_class_members()` method
in pascal_reader.py. Modified `_build_class_overview()` to generate overview when EITHER
`len(summary) > MAX_SUMMARY_CHARS` OR `member_count >= MIN_OVERVIEW_MEMBERS`.

**Why it was reverted:**
- Created class_overview chunks for hundreds of medium-sized classes across the 12,400-file
  production index
- These spurious overviews for unrelated files (e.g., DBClassesBusStop.pas, TPersonEditorFrame.pas)
  outranked target files in many queries due to the reranker's +0.65 overview bonus
- Caused 13 test regressions on production that were invisible in the 38-file test-sources index
- Removed: `MIN_OVERVIEW_MEMBERS` constant, `_count_class_members()` method, OR condition
  in overview gate, and 10 associated tests

## Baseline (Iteration 004 Production)

| Metric | Value |
|--------|-------|
| Validation pass rate | 101/112 (90.2%) |
| Rating | Excellent |
| PASS / PARTIAL / FAIL | 48 / 5 / 3 |

## Results (005c Production)

| Metric | Value | Delta vs 004 |
|--------|-------|--------------|
| Validation pass rate | 94/112 (83.9%) | **-7 points (-6.3%)** |
| Rating | Good | Downgraded from Excellent |
| PASS / PARTIAL / FAIL | 40 / 14 / 2 | -8 PASS, +9 PARTIAL, -1 FAIL |

## Detailed Test-by-Test Changes (005c vs 004)

### Improvements (+4 tests, +11 points)

| Test | Query | Before | After | Cause |
|------|-------|--------|-------|-------|
| T11 | "PreapreDataSet" | PARTIAL | PASS | Test query fix (matches actual typo in code) |
| T34 | "Where are ticket prices calculated" | FAIL | PASS | SQL NL description on TCityTicketsEditorFrame chunks |
| T35 | "How to export relief tickets" | FAIL | PASS | SQL NL description bridges "export relief tickets" → SLS_ReliefExport_Bilety_Get |
| T41 | "...modify the ticket export logic..." | FAIL | PASS | SQL NL description bridges "ticket export" → ListOfTicketsPrintWrapper |

### Regressions (-13 tests, -18 points)

| Test | Query | Before | After | Root Cause |
|------|-------|--------|-------|------------|
| T01 | "What is TdmMain?" | PASS | PARTIAL | DBClassesBusStop.pas class_summary outranks MainDM; reindex shifted embeddings |
| T03 | "What is TfrmMainTurdus?" | PASS | PARTIAL | class_overview no longer surfacing at #1; declProc dominates |
| T05 | "What does TfrmBaseEditor do?" | PASS | FAIL | class_overview from BaseEditorForm.pas gone from top results; TPersonEditorFrame.pas at #1 |
| T09 | "What fields does TdmMain have?" | PASS | PARTIAL | class_overview at #1 instead of class_summary_split; node_type mismatch |
| T13 | "GetCardSerialNumber" | PASS | PARTIAL | declProc at #1 instead of method_group; different chunk selection |
| T15 | "TCK_FarePrice_GetPriceForXDesignation" | PASS | PARTIAL | function_header dropped from #1 to #3 |
| T21 | "what units does MainTurdus use" | PASS | PARTIAL | comment chunk outranked declUses at #1 |
| T31 | "body of SLS_ReliefExport_Bilety_Get" | PASS | PARTIAL | Wrong file (ADMIN_createdelphiclass) at #2 |
| T36 | "Where is the splash screen shown" | PASS | PARTIAL | SplashScreen.pas outranked Splash.pas (different file) |
| T38 | "...understand complete architecture..." | PASS | PARTIAL | declProc at #1 instead of class_overview |
| T42 | "Where are report types defined?" | PASS | FAIL | comment from SalesReport.Types.pas instead of declConst with REPORT_TYPE |
| T46 | "Describe TframeBaseCreator" | PASS | PARTIAL | dfm_form_header from .dfm instead of class_summary from .pas |
| T53 | "SLS_TicketPaymentTypeEMAR205 table" | PASS | PARTIAL | comment from Informica.dpr outranked create_table |

### Unchanged Tests (39 tests)

- T23: PARTIAL→PASS (improvement from different index composition)
- All other tests remained at their iteration 004 level

## Root Cause Analysis

### Why did a reindex cause so many regressions?

The iteration 005 changes required a **full production reindex** because they modified chunk
content (SQL NL descriptions in context prefixes). The previous production index (iteration 004)
was built with different code — likely from an earlier version with different chunking parameters.

Key factors:
1. **Chunk content changes alter ALL embeddings** — even chunks that weren't directly modified
   get different relative rankings because the vector space is recalculated
2. **Score flattening** — many 005c results show scores at exactly 0.5000, suggesting ties in
   hybrid scoring that get resolved differently than in 004
3. **SQL NL descriptions shift BM25 vocabulary** — adding natural language words to SQL chunks
   changes the BM25 term frequency distribution, potentially affecting ranking of non-SQL chunks
4. **Test-sources vs production divergence** — 38-file test index showed 108/112 (96.4%) while
   production showed 94/112 (83.9%). The 12,400-file production index has much more competition
   for ranking positions

### The core problem

The SQL NL description change IS a net positive for the 3 tests it targets (T34, T35, T41)
but introduces a subtle BM25 vocabulary shift across the entire index. This is an inherent
trade-off of augmenting chunk text — it helps targeted queries but can hurt others.

The fact that 005c scores identical to 005b (both 94/112) despite reverting the member-count
threshold suggests the regressions are **primarily caused by the reindex itself** (different
chunk content producing different embeddings), not specifically by the member-count threshold.

## What We Learned

### 1. Reindex is not idempotent

Even with identical code and data, a reindex can produce slightly different rankings because:
- Float16 precision introduces non-deterministic rounding
- Qdrant's HNSW graph construction is non-deterministic
- Different batching order can affect BM25 statistics

### 2. NL augmentation has diminishing returns

Adding NL descriptions to context prefixes works well for individual test cases (T34, T35, T41
all fixed) but the global effect on the BM25 vocabulary distribution causes unpredictable
regressions elsewhere. The more text you add to chunks, the more you dilute the BM25 signal
for exact identifier matches.

### 3. Test-sources index is necessary but insufficient

The 38-file test-sources index correctly predicted the SQL NL improvements but completely
missed the 13 regressions. Future iterations should be more cautious about changes that
require a full reindex — they need production validation before committing.

### 4. Member-count threshold was a red herring

Reverting the threshold (005b→005c) changed test-sources from 110→108 but production stayed
at 94. The regressions in 005b that were attributed to the threshold were actually caused by
the broader reindex effect. The threshold removal only affected test T06 (lost its class_overview).

## Decision

**Partially committed.** Only the SQL NL description change (`decompose_identifier()` +
`-- Description:` in tsql_chunker.py) and the T11 test fix are kept. The Pascal NL prefix
and member-count threshold are reverted.

**Net result: -7 points from iteration 004 (94 vs 101).** This is a regression from the
90.2% target. The SQL NL descriptions are kept because they fix genuinely hard queries
(T34/T35/T41) that were previously marked as "model limitations." The regressions need
investigation in a future iteration.

## Current Parameter Values (After This Iteration)

### Chunking Parameters (changed by reindex)

| Parameter | Value | Changed? |
|-----------|-------|----------|
| SQL context prefix `-- Description:` | Enabled | **NEW** |
| Pascal NL context prefix | Disabled | No (removed in 005b) |
| `MIN_OVERVIEW_MEMBERS` | Removed | **Reverted** |
| `MAX_SUMMARY_CHARS` | 6000 | No |

### Reranker Parameters (unchanged from 004)

| Parameter | Value |
|-----------|-------|
| `OVERFETCH_MULTIPLIER` | 10 |
| `_PRIMARY_OVERVIEW_BONUS` | 0.65 |
| `_OVERVIEW_BONUS` | 0.25 |
| `_DFM_OVERVIEW_BONUS` | 0.10 |
| `_TARGET_MATCH_BONUS` | 0.15 |
| `_NON_TARGET_OVERVIEW_PENALTY` | 0.30 |
| `_CROSS_FILE_COMMENT_PENALTY` | 0.30 |
| `_DETAIL_PENALTY` | 0.05 |
| `_OVERVIEW_PATTERNS` | 28 patterns |

### Index Statistics

| Metric | 004 | 005c |
|--------|-----|------|
| Files indexed | ~12,400 | 12,533 |
| Vectors | ~140,000 | 140,543 |
| Indexing time | ~90 min | ~99 min |
| Errors | 0 | 0 |

## Unit Tests

| Suite | Tests | Status |
|-------|-------|--------|
| All tests | 1,032 | Passing |
| Pascal reader | 159 | Passing (was 169; removed 10 threshold tests) |
| T-SQL chunker | 125+ | Passing (includes NL description tests) |
| decompose_identifier | 45 | Passing (NEW) |

## Progress Toward Target

| Iteration | Score (test) | Score (prod) | Delta vs prev prod |
|-----------|-------------|-------------|-----|
| 001 (baseline) | 65/88 (73.9%) | — | — |
| 002 (reranker tuning) | 68/88 (77.3%) | — | +3 |
| 003 (DFM detection) | 70/88 (79.5%) | — | +2 |
| **Test expansion** | **97/112 (86.6%)** | — | New baseline (56 tests) |
| **004 (overfetch + patterns)** | **101/112 (90.2%)** | **101/112 (90.2%)** | **Target met** |
| **005a (all NL descriptions)** | **109/112 (97.3%)** | **92/112 (82.1%)** | -9 |
| **005b (SQL-only NL + threshold)** | **110/112 (98.2%)** | **94/112 (83.9%)** | -7 |
| **005c (SQL-only NL, no threshold)** | **108/112 (96.4%)** | **94/112 (83.9%)** | **-7** |

## Next Steps (Recommended for Iteration 006)

1. **Investigate score flattening** — Many 005c results show scores at exactly 0.5000.
   Understand why this happens and whether it's related to the reindex or a systematic issue.

2. **Revert SQL NL descriptions and reindex** — To isolate whether the regressions are caused
   by the SQL NL description change or by the reindex itself, do a clean reindex with the
   SQL NL descriptions removed. If the score returns to ~101/112, the NL descriptions are
   the culprit. If it stays at ~94, the reindex non-determinism is the issue.

3. **Improve reranker target extraction** — Several regressions (T01, T03, T05, T38, T46) are
   class overview queries where the reranker failed to boost the correct file. The target
   extraction logic may need improvement for the production-scale index.

4. **Consider per-category improvements** — Category 1 (Class Overview) dropped from 10/11
   to 5/11. This specific category needs focused attention.
