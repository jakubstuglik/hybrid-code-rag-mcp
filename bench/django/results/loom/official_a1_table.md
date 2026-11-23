# Loom variant A1 – v2.1 official 40 × 3 (local branch, not pushed)

Run 2026-11-23 12:20–13:18 (Europe/Warsaw), JSTUGLIK-AO, commit a3578dc,
`run_night_v21.ps1 -Phase official -Variants loom -Reps 3 -Tag v21-official-loom-a1`
(seed 20261114, blocked_rotation, 40 questions × 3 = 120 runs, 180 s, effort high, max 20 turns).
A1: every Loom read tool open, only memory writes denied; prompt `system_v2.txt` unchanged, no skill.
Setup: [MANIFEST.md](MANIFEST.md).

- Status: 117 ok, 3 max_turns. Mean 28.3 s (median 25.7, max 135.2). 0 protocol violations, 0 denied, 3 failed calls.
- Tool calls: 888 (7.40/run); retrieval 2.62/run; loom_context_pack 111 (the first Loom call in all 111
  runs that used a tool), loom_code_ask 43 (in 43 runs; fake LLM: echo answer + real citations),
  loom_code_search 119, grep 78, symbol 74, outline 1, loom_search 6; loom_op 0.
- Gated: 9 runs made no tool call at all (C202 r3, C213 r3, E201 r1/r2, S201 r1, S204 r1/r2/r3, S210 r1).
- Hygiene: memory tables 0 before and after each of the 3 groups.
- Comparison: `../official_table.md` (ripgrep / hcr / claude_context / serena, n=40 each, i.e. 1 repetition).
- Logs: `C:\Apps\hcr-promo-files\bench-logs-loom\logs-v21-official-loom-a1` (+ .zip).

## scored

variant | E | S | C | all | #2 | #0 | gated | violations | mean s
---|---|---|---|---|---|---|---|---|---
loom | 1.93 (n=30) | 1.87 (n=45) | 1.76 (n=45) | 1.84 (n=120) | 105 | 4 | 0 | 0 | 28.3

question | loom
---|---
C201 | 2/2/2
C202 | 2/2/1
C203 | 2/2/2
C204 | 2/2/2
C205 | 2/2/2
C206 | 0/0/0
C207 | 1/2/1
C208 | 2/2/2
C209 | 2/2/2
C210 | 2/2/1
C211 | 2/2/2
C212 | 2/2/2
C213 | 2/2/1
C214 | 2/2/2
C215 | 2/2/2
E201 | 1/1/2
E202 | 2/2/2
E203 | 2/2/2
E204 | 2/2/2
E205 | 2/2/2
E206 | 2/2/2
E207 | 2/2/2
E208 | 2/2/2
E209 | 2/2/2
E210 | 2/2/2
S201 | 1/2/2
S202 | 2/2/2
S203 | 2/2/2
S204 | 2/1/1
S205 | 2/2/2
S206 | 2/2/2
S207 | 2/2/2
S208 | 2/2/2
S209 | 2/2/2
S210 | 0/2/2
S211 | 2/2/2
S212 | 2/2/2
S213 | 2/2/2
S214 | 2/2/2
S215 | 2/1/2

## scored_gated

variant | E | S | C | all | #2 | #0 | gated | violations | mean s
---|---|---|---|---|---|---|---|---|---
loom | 1.87 (n=30) | 1.76 (n=45) | 1.71 (n=45) | 1.77 (n=120) | 104 | 12 | 9 | 0 | 28.3

question | loom
---|---
C201 | 2/2/2
C202 | 2/2/0
C203 | 2/2/2
C204 | 2/2/2
C205 | 2/2/2
C206 | 0/0/0
C207 | 1/2/1
C208 | 2/2/2
C209 | 2/2/2
C210 | 2/2/1
C211 | 2/2/2
C212 | 2/2/2
C213 | 2/2/0
C214 | 2/2/2
C215 | 2/2/2
E201 | 0/0/2
E202 | 2/2/2
E203 | 2/2/2
E204 | 2/2/2
E205 | 2/2/2
E206 | 2/2/2
E207 | 2/2/2
E208 | 2/2/2
E209 | 2/2/2
E210 | 2/2/2
S201 | 0/2/2
S202 | 2/2/2
S203 | 2/2/2
S204 | 0/0/0
S205 | 2/2/2
S206 | 2/2/2
S207 | 2/2/2
S208 | 2/2/2
S209 | 2/2/2
S210 | 0/2/2
S211 | 2/2/2
S212 | 2/2/2
S213 | 2/2/2
S214 | 2/2/2
S215 | 2/1/2
