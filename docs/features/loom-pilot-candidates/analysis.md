# Candidates from the ClickHouse Loom comparative pilot

**TODO #13** — Ideas worth considering, not a commitment to implement them.

## Source and status

On 2026-11-25 a comparative pilot measured [ClickHouse Loom](https://github.com/ClickHouse/loom)
v1.3.0 against hybrid-code-rag-mcp on the frozen Django 6.1.3 benchmark
(40 questions × 3 repetitions). Headline verdict: Loom is **not worth adopting**
as a replacement for, or an add-on to, hcr for this kind of code-localisation
task. Some of Loom's tools are still worth considering as development paths for hcr.

This document records those candidates. Each item is **pending decision**.
Nothing here is scheduled or promised.

Evidence comes from the notes on branch `bench-loom-variant`
(`bench/django/results/loom/verdict.md`, `analysis_a2_qwen.md`).
The official 40×3 tables cover two Loom configurations: A1 (no real LLM) and A2
(a local Qwen3-8B model for chunk descriptions and `code_ask`). Tool-use counts
below are over both official runs (240 runs total) unless stated otherwise.
Loom's SCIP tier was off in this pilot (tree-sitter only), so callers/impact
were not exercised.

Caveat: the hcr / ripgrep / serena / claude_context baselines ran on an older
Grok CLI build than Loom. After the retrieval-tool gate, the accuracy gap is
within noise (Loom A2 vs hcr: gated −0.05, 95% CI −0.18 .. +0.08; ungated tie
at 1.88).

## Candidates

### A. Exact symbol lookup (`code_symbol`)

**What it does in Loom:** `code_symbol` takes a symbol name and returns its
definition and body (optional neighbours).

**Pilot evidence:** 140 calls over 240 official runs (A2: 66, A1: 74). Used
about as often as indexed grep. On question C206, `code_symbol` returned
`PartialNode` and `PartialTemplate` by name; the later miss was a turn-budget
and wording issue, not a retrieval miss.

**What it would give hcr:** hcr today exposes `search_rag` and
`get_index_state`. Symbol lookup already happens *inside* hybrid search
(`SYMBOL_LOOKUP_K`), but the agent cannot ask for one named symbol and get
its definition plus body in a single call. A dedicated tool (for example
`get_symbol`) would cut follow-up file reads.

Related, not the same: [TODO #4](../mcp-additional-tools/analysis.md) proposes
extra search tools filtered by `node_type` (`search_method_decl`,
`search_method_def`, and similar). That is typed search, not exact name →
definition + body.

**Effort / risk (estimate):** Medium. The indexer already stores symbol-bearing
chunks; a new MCP tool and a precise name index (plus tests for overloads and
the same name in many files) are the main work. Risk: agents may over-use the
exact tool and skip hybrid search when the name is wrong or ambiguous.

**Status:** pending decision

### B. Indexed grep with a path filter (`code_grep`)

**What it does in Loom:** `code_grep` is an indexed regex/grep with
`path_prefix` / `path_globs` to narrow the scope.

**Pilot evidence:** 142 calls over 240 official runs (A2: 64, A1: 78) — used
as often as a first-class peer of semantic search (`code_search` 207 calls).

**What it would give hcr:** Agents already combine `search_rag` with raw file
reads. A first-class, path-scoped grep over the indexed tree would let them
pin a pattern to a directory without leaving the MCP tools or grepping a
full working copy.

**Effort / risk (estimate):** Low to medium if built on the files already
walked by the indexer (or on a maintained text index). Risk: overlap with
BM25 and with the agent simply using ripgrep; the tool description needs to
make it obvious when a literal or regex pattern is the right choice.

**Status:** pending decision

### C. Abstain / retrieval confidence + `as_of` on every result

**What it does in Loom:** Search answers include `abstain`,
`abstain_code: not_covered`, `retrieval_confidence`, hints such as "path
outside indexed prefixes — read the file directly", and `as_of` (branch,
commit, fresh/stale) on every result.

**Pilot evidence:** Qualitatively visible in traces (section 4 of the
verdict). Not a scored metric. hcr already exposes the indexed commit and
freshness through `get_index_state`, but not per-hit coverage or confidence,
and not an explicit "this path is outside the index" signal on search hits.

**What it would give hcr:** Fewer confident answers over stale or unindexed
paths; agents can fall back to reading the file. A commit / `as_of` stamp on
each result makes it obvious when the index lags the working tree.

**Effort / risk (estimate):** Low for surfacing existing manifest and commit
data on every search response. Medium for a reliable abstain/coverage signal
(defining "not covered", calibrating confidence). Risk: a noisy confidence
score that agents treat as ground truth.

**Status:** pending decision

### D. Compiler call graph (SCIP) with callers / impact

**What it does in Loom:** A SCIP-based graph (scip-python, scip-typescript,
scip-clang, scip-go; edges such as calls, overrides, inherits) and tools for
callers, callees, and change impact.

**Pilot evidence:** **Not measured.** Loom's SCIP tier was off in this
benchmark (tree-sitter only). This item is recorded because it is a Loom
capability hcr does not have, not because the Django bench showed a gain.

**Already under research in this project:** This is an existing research
topic, not a scheduled work item. The related in-repo plan is
[TODO #11](../structural-metadata-graph/analysis.md): structured metadata in
Qdrant payloads from AST readers already run at index time, with a graph
database only if multi-hop traversal is proven necessary. TODO #11 is
AST-based and cheaper; SCIP is compiler-accurate and covers a language
subset (there is no official SCIP indexer for Delphi/Pascal; Loom does not
provide one either). Whether to go beyond AST to SCIP is a separate decision
and should not be started in parallel with Phase 1 of TODO #11 without an
explicit choice about how the two relate.

**What it would give hcr:** More reliable "who calls this?" / impact answers
than hybrid search and AST-only `calls` lists can guarantee, especially
across files and after overloads or inheritance.

**Effort / risk (estimate):** High. Extra indexers, language-coverage gaps
(Pascal/Delphi would still need another edge source), operational cost, and
overlap with TODO #11.

**Status:** pending decision (research topic already open)

### E. Optional, low priority: `code_ask` and index-time chunk descriptions

**What they do in Loom:** `code_ask` synthesises an answer with `path:line`
citations and a full/partial coverage flag. At index time, an LLM one-liner
can be prepended to each chunk before embedding.

**Pilot evidence:** 54 `code_ask` calls in the official A2 run, all real
syntheses (45 full, 9 partial, mean 454 characters). Runs with `code_ask`
were about 9 s slower (34.7 s vs 25.5 s) and no more accurate (1.94 vs 1.96
ungated on those splits). A2 vs A1 overall: +0.02 gated / +0.04 ungated,
within noise. Descriptions for 11 334 chunks took about 29 minutes on a
local 8B model. Both features require an LLM; without one, `code_ask` only
echoes citations.

**What it would give hcr:** An optional synthesis tool and optional
index-time context. On this benchmark they did not improve localisation
accuracy, so they are low priority.

**Effort / risk (estimate):** Medium-high (LLM dependency at query and/or
index time, latency, cost, quality of a local small model vs a hosted one).
Risk: a slower default path for no measured gain.

**Status:** pending decision — low priority

## Recorded but not measured

These Loom capabilities were out of scope of the localisation benchmark.
They are written down so they are not forgotten; this pilot has no evidence
for or against them.

- **Shared agent memory** (namespaces, role tokens, extraction, entity
  tagging, session briefs). Several of its legs require an LLM.
- **PR / tracker tools** (review and issue workflows around the code index).

## What the pilot does not recommend

Adopting Loom itself as a second stack (ClickHouse + extractor + Docker,
plus an LLM for the LLM features) is not recommended for this class of
task: slightly slower and slightly more expensive than hcr, no accuracy
gain after the retrieval-tool gate, and no Delphi/Pascal AST (`.pas` is
indexed as plain text; no SCIP indexer for Pascal). Java is fully supported
in Loom's tree-sitter lane. `.sql` files are supported with Oracle dialect
detection, but `.pks` / `.pkb` package files were not in the extension
tables reviewed in Loom v1.3.0.
