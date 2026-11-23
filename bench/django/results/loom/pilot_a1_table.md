# Loom variant A1 – v2.1 pilot (local branch, not pushed)

Run 2026-11-23 12:05–12:18 (Europe/Warsaw), JSTUGLIK-AO, commit a3578dc,
`run_night_v21.ps1 -Phase pilot -Variants loom -Reps 3 -Tag v21-pilot-loom-a1`
(seed 20261114, blocked_rotation, 10 pilot21 questions × 3 = 30 runs, 180 s, effort high, max 20 turns).
A1: every Loom read tool open, only memory writes denied; prompt `system_v2.txt` unchanged, no skill.
Setup: [MANIFEST.md](MANIFEST.md). The blocked-tools pilot of the morning is [pilot_table.md](pilot_table.md).

- Status: 30 ok. Mean 24.2 s (median 22.9). 0 protocol violations, 0 denied, 0 failed calls.
- Tool calls: 172 (5.73/run); retrieval 1.57/run; loom_context_pack 27 (first Loom call in all 27 runs
  that used a tool), loom_code_ask 8 (in 8 runs), loom_code_search 23, symbol 10, grep 6, outline 3, loom_search 1.
- Gated: 3 runs (Q3P01 r3, Q3P08 r2, Q3P10 r1) made no tool call at all (answer from memory, ~6 s).
- Hygiene: memory tables 0 before and after each of the 3 groups.
- `pilot_gate.py`: NOT_DISCRIMINATING only because a loom-only log dir has no `none` runs; harness problems none.
- Logs: `C:\Apps\hcr-promo-files\bench-logs-loom\logs-v21-pilot-loom-a1` (+ .zip).

## scored

variant | E | S | C | all | #2 | #0 | gated | violations | mean s
---|---|---|---|---|---|---|---|---|---
loom | 1.89 (n=9) | 2.00 (n=12) | 1.67 (n=9) | 1.87 (n=30) | 27 | 1 | 0 | 0 | 24.2

question | loom
---|---
Q3P01 | 2/2/1
Q3P02 | 2/2/2
Q3P03 | 2/2/2
Q3P04 | 2/2/2
Q3P05 | 2/2/2
Q3P06 | 2/2/2
Q3P07 | 2/2/2
Q3P08 | 2/0/2
Q3P09 | 2/2/2
Q3P10 | 1/2/2

## scored_gated

variant | E | S | C | all | #2 | #0 | gated | violations | mean s
---|---|---|---|---|---|---|---|---|---
loom | 1.78 (n=9) | 2.00 (n=12) | 1.56 (n=9) | 1.80 (n=30) | 27 | 3 | 3 | 0 | 24.2

question | loom
---|---
Q3P01 | 2/2/0
Q3P02 | 2/2/2
Q3P03 | 2/2/2
Q3P04 | 2/2/2
Q3P05 | 2/2/2
Q3P06 | 2/2/2
Q3P07 | 2/2/2
Q3P08 | 2/0/2
Q3P09 | 2/2/2
Q3P10 | 0/2/2
