# Loom variant – v2.1 pilot (local branch, not pushed)

Run 2026-11-23 10:12–10:27 (Europe/Warsaw), JSTUGLIK-AO, `run_night_v21.ps1 -Phase pilot -Variants loom -Reps 3 -Tag v21-pilot-loom`
(seed 20261114, blocked_rotation, 10 pilot21 questions × 3 repetitions = 30 runs, 180 s, effort high, max 20 turns).
Setup and fairness notes: [MANIFEST.md](MANIFEST.md). Gate: `pilot_gate.py` → NOT_DISCRIMINATING only because a
loom-only log dir has no `none` runs; harness problems: none (0 error/timeout, 0 protocol violations).

## Compared with the v2.1 pilot table (`results/pilot_table.md`, 1 repetition, Grok 1.0.70 era)

scored_gated | E | S | C | all | mean s | runs
---|---|---|---|---|---|---
loom (this run) | 1.78 | 1.67 | 1.56 | 1.67 | 28.0 | 30
ripgrep | 2.00 | 1.50 | 2.00 | 1.80 | 17.6 | 10
hcr | 2.00 | 2.00 | 1.33 | 1.80 | 20.0 | 10
claude_context | 2.00 | 2.00 | 2.00 | 2.00 | 52.2 | 10
serena | 2.00 | 2.00 | 2.00 | 2.00 | 50.0 | 10

Ungated (scored) loom: 1.97 (29 × 2, 1 × 1). All 5 zeros in scored_gated come from the retrieval gate (0 retrieval calls):
Q3P01 r1 answered from memory with no tool call; Q3P06 r2/r3 and Q3P09 r1/r3 tried `loom_context_pack` and
`loom_code_ask` (both denied), then answered from `list_dir` + `read_file` only.

Tool calls (30 runs): 199 in total, 6.6 per run. 44 were denied by the `--deny` rules (loom_context_pack 29,
loom_code_ask 13, loom_search 2). 0 calls failed for any other reason, 0 banned tools ran. Loom retrieval calls:
loom_code_search 19, loom_code_symbol 14, loom_code_grep 7 (1.33 per run). Other calls: search_tool 51,
read_file 49, list_dir 11, todo_write 4.

## scored

variant | E | S | C | all | #2 | #0 | gated | violations | mean s
---|---|---|---|---|---|---|---|---|---
loom | 1.89 (n=9) | 2.00 (n=12) | 2.00 (n=9) | 1.97 (n=30) | 29 | 0 | 0 | 0 | 28.0

question | loom
---|---
Q3P01 | 1/2/2
Q3P02 | 2/2/2
Q3P03 | 2/2/2
Q3P04 | 2/2/2
Q3P05 | 2/2/2
Q3P06 | 2/2/2
Q3P07 | 2/2/2
Q3P08 | 2/2/2
Q3P09 | 2/2/2
Q3P10 | 2/2/2

## scored_gated

variant | E | S | C | all | #2 | #0 | gated | violations | mean s
---|---|---|---|---|---|---|---|---|---
loom | 1.78 (n=9) | 1.67 (n=12) | 1.56 (n=9) | 1.67 (n=30) | 25 | 5 | 5 | 0 | 28.0

question | loom
---|---
Q3P01 | 0/2/2
Q3P02 | 2/2/2
Q3P03 | 2/2/2
Q3P04 | 2/2/2
Q3P05 | 2/2/2
Q3P06 | 2/0/0
Q3P07 | 2/2/2
Q3P08 | 2/2/2
Q3P09 | 0/2/0
Q3P10 | 2/2/2
