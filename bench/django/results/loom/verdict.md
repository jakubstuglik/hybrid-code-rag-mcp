# Loom vs hcr: verdict material (Django 6.1.3 bench v2.1)

Written 2026-11-25 (Europe/Warsaw) from existing logs only; no run was repeated for this file.
Local branch `bench-loom-variant`, not pushed. Comparison tables: [comparison_gated.md](comparison_gated.md).

## 1. Gate: which baseline numbers are gated

The retrieval-tool gate (METHOD.md §17.1 item 3, `v2/scripts/apply_retrieval_gate.py`): for a
retrieval variant, a run with `tool_calls_retrieval == 0` scores 0 after blind grading; the blind
score stays in `accuracy_before_gate`. METHOD.md §17.2 says the headline uses scores **after**
the gate. Loom was added to `RETRIEVAL_VARIANTS` on this branch, so it is gated the same way.

The baseline numbers quoted so far (ripgrep 1.93, serena 1.90, hcr 1.82, claude_context 1.70) are
**gated**, and they are **one repetition (k = 1, n = 40)**, not 40 x 3:

- `results/official_table.md` (README: "40 questions x 6 variants, k = 1"), section `scored_gated`.
  Ungated (`scored`) in the same file: ripgrep 1.95, serena 1.95, hcr 1.88, claude_context 1.77.
- Repetitions 2 and 3 of the baselines exist separately: `logs/extra1/official_table.md`
  (n = 80 per variant; also `C:\Apps\hcr-promo-files\bench-logs-v0.24.0\logs\extra1\`).
- Repetition 1 per-run data: `C:\Apps\hcr-promo-files\bench-logs-v0.24.0\logs\v21\official_aggjoin_scored_gated.jsonl`.

So the earlier comparison (Loom 40 x 3 vs baselines k = 1) mixed n = 120 with n = 40. The table
below puts every variant on 40 x 3, gated and ungated, from the per-run `*_aggjoin_scored_gated.jsonl`
files (fields `accuracy`, `accuracy_before_gate`, `category`, `wall_time_s`, `repetition`).

| variant (40 x 3) | gated all | gated E / S / C | ungated all | ungated E / S / C | zeroed by gate | mean s | median s |
|---|---|---|---|---|---|---|---|
| serena | **1.92** | 2.00 / 1.96 / 1.82 | 1.96 | 2.00 / 2.00 / 1.89 | 4 | 46.8 | 42.7 |
| ripgrep | **1.86** | 1.93 / 1.87 / 1.80 | 1.91 | 1.97 / 1.93 / 1.84 | 6 | 20.2 | 15.9 |
| hcr | **1.84** | 1.93 / 1.87 / 1.76 | 1.88 | 1.97 / 1.91 / 1.78 | 5 | 22.6 | 16.6 |
| loom A2 (Qwen3-8B) | **1.79** | 1.93 / 1.82 / 1.67 | 1.88 | 1.97 / 1.91 / 1.78 | 10 | 28.1 | 25.8 |
| loom A1 (fake LLM) | **1.77** | 1.87 / 1.76 / 1.71 | 1.84 | 1.93 / 1.87 / 1.76 | 9 | 28.3 | 25.7 |
| claude_context | **1.68** | 1.60 / 1.82 / 1.60 | 1.77 | 1.67 / 1.91 / 1.69 | 10 | 44.0 | 34.8 |
| read_only (control, not gated) | 1.83 | 1.60 / 2.00 / 1.82 | 1.83 | | 0 | 39.1 | 24.0 |
| none (control, not gated) | 0.91 | 1.00 / 0.87 / 0.89 | 0.91 | | 0 | 37.7 | 28.0 |

Sources: baselines r1 = `bench-logs-v0.24.0\logs\v21\official_aggjoin_scored_gated.jsonl`,
r2-r3 = `bench-logs-v0.24.0\logs\extra1\official_aggjoin_scored_gated.jsonl` (repetition 1/2 there = r2/r3);
Loom A1 = `bench-logs-loom\logs-v21-official-loom-a1\official_aggjoin_scored_gated.jsonl`;
Loom A2 = `bench-logs-loom\logs-v21-official-loom-a2-qwen\official_aggjoin_scored_gated.jsonl`
(all under `C:\Apps\hcr-promo-files\`). Aggregated values match each source's `official_table.md`.

Paired bootstrap over the 40 question means (10 000 resamples, seed 20261114), Loom A2 minus hcr:
gated -0.05 (95% CI -0.18 .. +0.08), ungated 0.00 (-0.09 .. +0.09). Loom A1 minus hcr: gated -0.075
(-0.23 .. +0.07), ungated -0.03 (-0.10 .. +0.03). A2 minus A1: gated +0.025 (-0.11 .. +0.15).
Only serena is ahead of Loom A2 with a CI that excludes 0 (gated -0.125, -0.23 .. -0.02).
Repetition spread is large: Loom A2 gated r1/r2/r3 = 1.90 / 1.68 / 1.80, hcr 1.82 / 1.85 / 1.85.

Cost over 120 runs (Grok CLI `total_cost_usd`): ripgrep 1.82, hcr 3.98, Loom A2 4.26, Loom A1 4.56,
claude_context 6.54, serena 6.64 USD. Mean tool calls per run: hcr 4.8, ripgrep 5.9, Loom A2 6.7,
Loom A1 7.4, serena 9.1, claude_context 9.3.

Comparability caveats (from MANIFEST.md): baselines ran 15-16.11 with Grok Build 1.0.70-era,
Loom 23-24.11 with 1.0.91; same model (grok-4.7), prompt, schema, 20 turns, 180 s. Loom indexes
`django/` only (tests/docs excluded); Loom's SCIP tier was off (tree-sitter only).

## 2. Qualitative analysis

### 2.1 Runs without any tool call

All Loom runs zeroed by the gate had **zero tool calls of any kind** (not a misclassified tool):
the agent answered from memory in one turn, 4.5-9.2 s, `num_turns = 1`. The tool list in those runs is
the same as in runs that used Loom (`search_tool` / `use_tool` present), stderr has no MCP error,
and the neighbouring runs of the same block called Loom normally. This is agent behaviour, not a
Loom failure.

- A1 (9): C202 r3, C213 r3, E201 r1, E201 r2, S201 r1, S204 r1-r3, S210 r1. Blind scores 1 x 7, 2 x 1 (S204 r1), 0 x 1 (S210 r1).
- A2 (10): C202 r2, C203 r2, C206 r2, C211 r2, C213 r3, E201 r2, S204 r1, S206 r1, S208 r2, S212 r3. Blind scores 1 x 10.
- Baselines do the same: zero-tool runs ripgrep 6, hcr 5, claude_context 10, serena 3 of 120
  (serena S208 r3 had 4 non-retrieval calls). Loom: 19 of 240 (7.9%) vs hcr 4.2%.

Without the gate Loom A2 ties hcr (1.88 = 1.88); the whole gated gap (-0.05) comes from these
memory answers. Whether Loom makes the agent skip tools more often (e.g. through its long MCP
instructions or the newer CLI) cannot be decided from these logs: same CLI for A1/A2, different CLI
for the baselines, and the counts are small.

### 2.2 C206 (partials: `partialdef_func`, `PartialNode`, `PartialTemplate`)

Key (`v2/questions.jsonl`): files `django/template/defaulttags.py`, `django/template/base.py`;
a 2 needs all three symbols; `PartialDefNode` is not a substitute.

Gated scores r1/r2/r3: ripgrep 2/1/1, serena 2/0/2, hcr 0/0/0, claude_context 0/0/0, read_only 0/0/0,
none 0/0/1, **Loom A1 0/0/0, Loom A2 2/0/0** (A2 ungated 2/1/0; r2 was a 9 s memory answer).
So "zero in every repetition" holds for A1 and for hcr, not for A2.

What happened (traces in `raw/C206__*.raw.json`):

- Loom found the answer early every time. A1 r1: `loom_code_ask` (call 3) and `loom_code_search` (4)
  return `partialdef_func` + `PartialTemplate`; `loom_code_symbol` gives `PartialNode` and
  `PartialTemplate` by call 11; `read_file` of all three spans by call 15. A2 r1/r3: same within 5-8 calls.
- Then the agent keeps looking for something matching the wording "inclusion tag" / "compiled fragment"
  (`library.py` inclusion_tag, `loader_tags.py`, docs `builtins.txt`, tests) until 20 turns run out
  (`max_turns`, no structured answer, 0). A2 r1 stopped in time (15 turns, 121 s) and scored 2.
- hcr does the same: `search_django` returns all three symbols in calls 2-3 of every run, reads of the
  spans follow, then 20+ doc reads and `max_turns` in all three repetitions.
- ripgrep/serena are the only variants that answer within the budget more often.

Conclusion: C206 is a question-wording trap plus the 20-turn budget, not a retrieval miss in Loom or hcr.

### 2.3 Other per-question differences vs hcr (gated, r1/r2/r3)

- Loom (both A1 and A2) below hcr: C202, C213, E201, S204. Every lost run there is a zero-tool memory answer.
- Loom (both) above hcr: C204, C208, E205, S202. hcr's misses there are mostly zero-tool runs too
  (C204 r1, E205 r2, S202 r1; C208 r3 = 1).
- C207 (hard for every variant): Loom A2 2/1/2 is the best row (hcr 1/2/1, ripgrep 1/1/1, serena 0/0/2).
- No question shows Loom's retrieval failing where hcr's works. Full per-question grid: comparison_gated.md.

### 2.4 code_ask with a real LLM (A2)

54 `loom_code_ask` calls, all real syntheses (45 full, 9 partial, mean 454 characters; A1: 43 fake echoes).
Runs with code_ask: accuracy 1.94, 34.7 s; without: 1.96, 25.5 s (A1: 1.81 / 36.3 s vs 1.97 / 26.2 s).
The agent re-checks the answer with `code_symbol` / `read_file`, so synthesis adds about 9 s per run
and no measurable accuracy on this benchmark.

## 3. Verdict draft

**Not worth it (nie grane) as a replacement for or addition to hcr on this kind of task; worth mining
for features.**

- Accuracy: Loom A2 = hcr ungated (1.88 vs 1.88), slightly below gated (1.79 vs 1.84, CI includes 0).
  The real LLM (A2 vs A1) adds +0.02..+0.04, within noise. The benchmark is near its ceiling (~1.9),
  so it cannot show a larger gain.
- Speed and cost: Loom is slower (median 25.8 s vs 16.6 s) and slightly dearer (4.26 vs 3.98 USD / 120 runs),
  with more tool calls per run (6.7 vs 4.8).
- Operations: Docker + ClickHouse + extractor, about 5.7 GiB RAM peak while indexing, 20 min index plus
  29 min of Qwen descriptions on the RTX 4060 (11 334 of 17 867 chunks), and a GPU LLM for the LLM features.
  hcr needs Qdrant and an embedding service, but no ClickHouse stack and no LLM.
- Languages: Delphi has no parser in Loom (see section 5).
- What was not measured: Loom's memory layer, SCIP graph, callers/impact, PR/tracker tools.
  This benchmark tests code localisation only.

## 4. What Loom has that hcr lacks (candidates to port)

Seen in use in the logs (calls over 240 runs: code_search 207, context_pack 221, code_symbol 140,
code_grep 142, code_ask 97):

1. **Exact symbol tool** (`loom_code_symbol`: name -> definition + body, optional neighbours). hcr has
   only `search_rag` + `get_index_state`; symbol lookup happens inside search. A `get_symbol` tool would
   save read_file calls.
2. **Indexed grep with path scope** (`loom_code_grep`, `path_prefix` / `path_globs`, regex): the agent
   used it as often as semantic search.
3. **Abstain / coverage signals** in the search answer (`abstain`, `abstain_code: not_covered`,
   `retrieval_confidence`, "path outside indexed prefixes - read the file directly") and `as_of`
   (branch, commit, fresh/stale) on every result.
4. **Compiler call graph (SCIP) with callers / callees / impact** - already a RAG research topic;
   not exercised here.
5. **code_ask** (synthesis with `path:line` citations, coverage full/partial) as an optional tool;
   on this benchmark it did not raise accuracy, so low priority.
6. **Per-chunk contextual descriptions** (LLM one-liner prepended before embedding): an optional
   index-time step for hcr with a local model; effect here not separable from code_ask.

## 5. Company projects (Delphi, Java, Oracle)

From Loom v1.3.0 source (`server/code/domain/extract/`):

- **Delphi:** `.pas` is in `lang_text.py` `_CODE_TEXT_EXTENSIONS` = indexed line-wise as text, no
  symbols, no edges. `.dpr`, `.dfm`, `.dpk`, `.inc` are not in any extension table found. No SCIP
  indexer for Pascal. For informica_2_0 Loom gives at most text search. hcr has a Delphi/Pascal AST.
- **Java:** full tree-sitter lane (`lang_detect.py` `.java -> java`, `lang_java.py`, `tree-sitter-java`);
  no SCIP tier for Java (SCIP: clang, go, python, typescript).
- **Oracle SQL:** `.sql` files get the SQL lane with dialect detection that recognises Oracle
  (`lang_sql_dialect.py`: VARCHAR2, `/` terminator, PACKAGE/TRIGGER, DUAL, NVL ...). PL/SQL package
  files `.pks`, `.pkb`, `.pls` are not in any extension table found, so they would need renaming or a patch.

So Loom fits Java + `.sql` repos; for Delphi-heavy projects it is not usable as the main index.

## 6. Which Loom features need an LLM, and what local Qwen3-8B gives

Need an LLM (`docs/reference/configuration.md`): `code.ask` synthesis and its pre-synthesis legs
(identifier proposal, HyDE, concept legs); per-chunk context descriptions
(`LOOM_CODE_CONTEXT_DESCRIPTION_ENABLED`); code.search model legs (HyDE, rerank); file/module summaries;
bisect rerank; and the memory side: extraction, entity tagging, conflict resolver, profile, session
briefs, titles, reflection.
Without an LLM (A1): code.search / grep / symbol / outline work; code.ask returns an echo plus real citations.

With Qwen3-8B Q4_K_M on the RTX 4060 (A2): every code_ask call returned a real answer (45 full / 9 partial),
descriptions took 29 min for 11 334 chunks, and accuracy rose by +0.02 gated / +0.04 ungated vs A1
(within noise). What a larger model would add cannot be measured from these logs (no run with a
hosted model). Loss on a local 8B: GPU time while indexing, about 9 s more per run when code_ask is
used; on this benchmark no accuracy loss was visible.
