# Iteration 004 — Overfetch Increase, Overview Patterns, and Validator Fixes

**Date:** 2026-03-11
**Author:** AI agent (with human supervision)
**Status:** committed

## Hypothesis

> Increasing `OVERFETCH_MULTIPLIER` from 5 to 10 will surface overview chunks (class_overview,
> class_summary) that currently rank at positions 30-50 in raw hybrid search but should appear
> in the top 10 after reranking. Additionally, adding 10 new overview detection patterns will
> capture query intents like "show me the structure of", "I need to add/modify", "what are
> the main", and "list the methods/classes" — common developer queries that the existing 18
> patterns miss. Finally, fixing validator acceptance criteria for `ddl_group`, `procedure_body`,
> and `class_summary` node types will convert 3 PARTIAL results to PASS.

## Context: Test Suite Expansion

Between iteration 003 and 004, the validation test suite was expanded:

- **38 test source files** (was 23): added FormBasicMain.pas/dfm, ResourceStrings.pas,
  LoginFrm.pas/dfm, and additional SQL/DFM files
- **56 validation tests** (was 44): 12 new tests (T45-T56) covering edge cases,
  cross-concern queries, and new test source files
- **New scoring base: 112 points** (was 88)

The pre-iteration-004 baseline was measured against this expanded suite.

## Changes Made

### 1. Reranker: Overfetch Multiplier (shared/reranker.py, line 49)

- **Changed:** `OVERFETCH_MULTIPLIER` from `5` to `10`
- **Rationale:** T03 ("What is TfrmMainTurdus?") had its `class_overview` chunk ranked at
  position ~35 in raw hybrid search. With 5x overfetch (top_k=10 → fetch 50), it was just
  outside the candidate pool. With 10x (fetch 100), it reliably enters the pool and gets
  promoted to #1 by the +0.65 overview bonus.
- **Trade-off:** 2x more candidates to rerank per overview query. Reranking is pure Python
  (no model inference), so the cost is negligible (~1ms extra).

### 2. Reranker: 10 New Overview Patterns (shared/reranker.py, lines 78-92)

New patterns added to `_OVERVIEW_PATTERNS`:

```python
r"show\s+me\s+(the\s+)?(structure|overview|summary)",
r"I\s+need\s+to\s+(add|modify|change|update|extend)",
r"what\s+are\s+the\s+main",
r"list\s+the\s+(methods|classes|fields|properties)",
r"how\s+is\s+\w+\s+structured",
r"give\s+me\s+(a|an)\s+(overview|summary|breakdown)",
r"what\s+does\s+\w+\s+look\s+like",
r"can\s+you\s+(describe|explain|summarize)",
r"tell\s+me\s+about\s+(the\s+)?(structure|design|architecture)",
r"walk\s+me\s+through",
```

- **Rationale:** Developer queries often use these phrasings when exploring unfamiliar code.
  Without overview detection, these queries get raw hybrid scores without the reranker's
  overview bonuses, causing method-level chunks to dominate over class summaries.
- **Guard rail:** "I need to find" is explicitly NOT an overview pattern (tested).

### 3. Validator Criteria Fixes (validate_rag.py)

Three validators had acceptance criteria that didn't include valid node types:

| Test | Fix | Line |
|------|-----|------|
| T18 | Added `class_summary` to accepted node_types | ~337 |
| T29 | Added `ddl_group` to accepted node_types | ~494 |
| T30 | Added `procedure_body` to accepted node_types | ~508 |

These were validator bugs, not retrieval bugs — the correct chunks were already being
returned but the validator didn't recognize them as valid.

### 4. Test Updates (tests/shared/test_reranker.py)

- **14 new tests** for the 10 new overview patterns (positive matches + mixed queries)
- **1 new negative test** ("I need to find" should NOT trigger overview detection)
- **3 updated assertions** for `OVERFETCH_MULTIPLIER` change (50→100, 500→1000, ==5→==10)
- **Total:** 188 reranker tests (was 174)

### 5. No config changes

All changes are query-time reranker parameters and validator fixes. No reindex needed.

## Baseline (Before — Post-Expansion, Pre-Iteration-004)

| Metric | Value |
|--------|-------|
| Validation pass rate | 97/112 (86.6%) |
| Rating | Good |
| PASS / PARTIAL / FAIL | 44 / 9 / 3 |
| Test count | 56 (expanded from 44) |

## Results (After)

| Metric | Value | Delta |
|--------|-------|-------|
| Validation pass rate | 101/112 (90.2%) | **+4 points (+3.6%)** |
| Rating | Excellent | Upgraded from Good |
| PASS / PARTIAL / FAIL | 48 / 5 / 3 | +4 PASS, -4 PARTIAL, 0 FAIL |

**90% target achieved.**

## Detailed Test-by-Test Changes

### Improvements (+4 points)

| Test | Query | Before | After | Fix | Notes |
|------|-------|--------|-------|-----|-------|
| T03 | "What is TfrmMainTurdus?" | PARTIAL | PASS | OVERFETCH 5→10 | class_overview now in candidate pool, promoted to #1 |
| T18 | "Class hierarchy / parent class" | PARTIAL | PASS | Validator fix | class_summary was already returned, validator now accepts it |
| T29 | "DDL for table X" | PARTIAL | PASS | Validator fix | ddl_group was already returned, validator now accepts it |
| T30 | "Procedure body logic" | PARTIAL | PASS | Validator fix | procedure_body was already returned, validator now accepts it |

### Regressions (0 points)

None. All previous improvements (T04, T07, T08, T09, T27) remain PASS.

### Remaining PARTIAL Tests (5)

| Test | Query | Status | Root Cause | Actionable? |
|------|-------|--------|-----------|-------------|
| T06 | "What does TfrmBaseEditor do?" | PARTIAL | FormBasicMain.pas class_summary (3404 chars) doesn't generate class_overview (threshold: >6000 chars). class_summary scores too low vs method_group after reranking. | Medium — lower MAX_SUMMARY_CHARS threshold or tune per-chunk-size bonus |
| T11 | "PrepareDataSet procedure" | PARTIAL | Production-only — procedure body not in test_sources MainDM.pas | No — test_sources limitation |
| T23 | "All forms using TForm" | PARTIAL | Only 1 TForm file in results (need ≥2). Retrieval diversity issue. | Low ROI — would need cross-file diversity logic |
| T28 | "TActionList components" | PARTIAL | Production-only — TActionList not in test_sources MainTurdus.dfm | No — test_sources limitation |
| T43 | "main data module" | PARTIAL | All words are stop words — no extractable target identifiers. Overview patterns now fire but MainDM chunks don't surface without target matching. | Medium — NL alias mapping (MainDM→"main data module") |

### Remaining FAIL Tests (3)

| Test | Query | Status | Root Cause |
|------|-------|--------|-----------|
| T34 | "ticket prices calculated" | FAIL | Dense/sparse can't connect natural language to FarePrice identifiers |
| T35 | "relief tickets export" | FAIL | Dense/sparse can't find ReliefExport files |
| T41 | "modify ticket export logic" | FAIL | Same as T35 — semantic gap between NL and code identifiers |

All 3 FAILs are **model capacity limitations** — the embedding model cannot bridge the
semantic gap between natural-language descriptions and code identifiers. Options: different
model, NL keyword injection into chunk prefixes, or accept as limitations.

## Analysis

### What Worked

**OVERFETCH_MULTIPLIER 5→10** was the single most impactful change. The reranker's score
adjustments (+0.65 for overview chunks) are powerful, but they can only work on chunks
that are in the candidate pool. With 5x overfetch, overview chunks for less common classes
(like TfrmMainTurdus with its large file) were ranked just outside the pool at positions
30-50. Doubling the pool size to 10x reliably captures these.

The cost is minimal: reranking 100 candidates instead of 50 takes <1ms longer (pure Python
score arithmetic, no model inference). Network cost of fetching 100 vs 50 from Qdrant is
also negligible.

**Validator fixes** were pure bugs — the retrieval pipeline was already returning correct
chunks, but the automated validator didn't accept them. This highlights the importance of
keeping validator acceptance criteria in sync with reader node_type evolution.

### What Didn't Work

**T43 ("main data module")** was investigated thoroughly. The 10 new overview patterns do
fire for this query, but without extractable target identifiers (all words are common English),
the reranker can't boost MainDM-specific chunks. The `_GENERAL_IDENT` pattern from iteration
003 doesn't help because "main", "data", "module" are all lowercase/stop words.

**T06** was investigated in depth. The root cause chain:
1. FormBasicMain.pas has 53 chunks, 1 `class_summary` (3404 chars), 0 `class_overview`
2. `class_overview` is only generated when `class_summary` exceeds `MAX_SUMMARY_CHARS` (6000)
3. The `class_summary` IS in the reranked results at position #4
4. But method_group chunks at positions #1-3 outscore it despite the +0.65 overview bonus
5. This means the class_summary's raw hybrid score is very low relative to method_group chunks

### Design Decisions

1. **10x overfetch rather than higher**: 10x is a reasonable upper bound. Going to 20x
   would fetch 200 candidates for a top-10 query, which starts to feel excessive. The
   remaining PARTIALs and FAILs are not overfetch issues.

2. **Pattern breadth**: The 10 new patterns cover common developer phrasings. The "I need
   to add/modify" pattern specifically targets the intent-to-modify use case, which is
   inherently an overview query (developer needs to understand structure before modifying).
   "I need to find" was explicitly excluded as a negative case.

## Decision

**Committed.** Net positive: +4 points (101 vs 97), +3.6% improvement. Zero regressions.
**90% target (≥101/112) achieved.** Cumulative improvement from iteration 001 baseline:
+36 points (101 vs 65) across expanded test suite.

## Current Parameter Values (After This Iteration)

### Reranker Parameters (shared/reranker.py)

| Parameter | Value | Changed? |
|-----------|-------|----------|
| `OVERFETCH_MULTIPLIER` | 10 | **5→10** |
| `_PRIMARY_OVERVIEW_BONUS` | 0.65 | No |
| `_OVERVIEW_BONUS` | 0.25 | No |
| `_DFM_OVERVIEW_BONUS` | 0.10 | No |
| `_DFM_ON_CLASS_QUERY_PENALTY` | 0.15 | No |
| `_TARGET_MATCH_BONUS` | 0.15 | No |
| `_NON_TARGET_OVERVIEW_PENALTY` | 0.30 | No |
| `_CROSS_FILE_COMMENT_PENALTY` | 0.30 | No |
| `_DETAIL_PENALTY` | 0.05 | No |
| `_OVERVIEW_PATTERNS` | 28 patterns | **+10 new** (was 18) |
| `is_dfm_query()` | 10 patterns | No |
| `_GENERAL_IDENT` | `[A-Z][A-Za-z0-9_]{2,}` | No |
| `_TARGET_STOP_WORDS` | ~40 words | No |

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
| All tests | 978 | Passing |
| Reranker tests | 188 | Passing (14 new + 3 updated) |

## Progress Toward Target

| Iteration | Score | Delta | Cumulative |
|-----------|-------|-------|------------|
| 001 (baseline) | 65/88 (73.9%) | — | — |
| 002 (reranker tuning) | 68/88 (77.3%) | +3 | +3 |
| 003 (DFM detection) | 70/88 (79.5%) | +2 | +5 |
| **Test expansion** | **97/112 (86.6%)** | — | New baseline (56 tests) |
| **004 (overfetch + patterns + validators)** | **101/112 (90.2%)** | **+4** | **Target met** |

## Next Steps

1. **Production validation** — Reindex production (12,400 files) and run validation suite
   against the full index. Changes are reranker-only (no reindex strictly needed), but
   confirming scores on the production index is important per improvement process Step 5.

2. **T06 investigation** — Lower `MAX_SUMMARY_CHARS` threshold from 6000 to ~3000 so
   FormBasicMain.pas generates a `class_overview`. Alternatively, add a chunk-size-aware
   bonus in the reranker (smaller class_summary chunks get a proportionally higher boost).

3. **T43 natural language aliases** — Add an alias mapping system (e.g., "main data module"
   → MainDM, "base editor" → BaseEditorForm) for queries where no identifiers are extractable.

4. **T34/T35/T41 semantic gap** — These remain model-level limitations. Options:
   - Inject NL keywords into chunk context prefixes during indexing
   - Evaluate cross-encoder reranker (major architecture change)
   - Accept as model limitations and document for users

5. **Test source rotation** — Per rotation policy, next rotation due at iteration 006-008.
   Current permanent files: MainDM, MainTurdus, emar105, BaseEditorForm, ResourceStrings,
   FormBasicMain, LoginFrm.
