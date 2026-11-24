# Loom A2 (local Qwen3-8B descriptions + synthesis) - analysis

Written 2026-11-24 (Europe/Warsaw) on JSTUGLIK-AO. Source: `bench/django/logs/v21-official-loom-a2-qwen` (120 runs, 40 questions x 3), script `analyze.py` (code_ask and tool usage). A1 reference: `logs-v21-official-loom-a1`.

## Scores (official table, 120 runs each)

| metric | A2 qwen ungated | A2 qwen gated | A1 ungated | A1 gated |
|---|---|---|---|---|
| all | 1.88 | 1.79 | 1.84 | 1.77 |
| E | 1.97 | 1.93 | 1.93 | 1.87 |
| S | 1.91 | 1.82 | 1.87 | 1.76 |
| C | 1.78 | 1.67 | 1.76 | 1.71 |
| #0 | 1 | 11 | 4 | 12 |
| gated runs | 0 | 10 | 0 | 9 |
| mean s | 28.1 | 28.1 | 28.3 | 28.3 |

Pilot (30 runs): A2 1.93 (gated 1.93, 1 gated run), mean 29.2 s; A1 pilot 1.87 ungated / 1.80 gated, mean 24.2 s.

## Description generation (A2)
11196 chunks in 1 732 843 ms (28 min 53 s; log `describe-sample.log`, 2026-11-24 16:52 start - 17:21 end Europe/Warsaw) + 138 chunks in 25 936 ms (`describe-fill.log`) = 11 334 chunks.

## A2 qwen analyze.py
```json
{
 "n": 120,
 "status": {
  "ok": 119,
  "max_turns": 1
 },
 "mean_s": 28.1,
 "median_s": 25.8,
 "tool_calls_total": 801,
 "retrieval": 272,
 "read": 220,
 "other": 309,
 "failed": 1,
 "denied": 0,
 "loom": 388,
 "context_pack": 110,
 "code_ask_calls": 54,
 "runs_with_code_ask": 54,
 "op_write": 0,
 "ask_outputs_found": 54,
 "ask_source": {
  "synthesized": 54
 },
 "ask_fake": 0,
 "ask_real_answer": 54,
 "ask_coverage": {
  "full": 45,
  "partial": 9
 },
 "ask_answer_len_mean": 454.0,
 "tokens_mean": 91300,
 "cost_usd": 4.26,
 "loom_tools": {
  "loom_context_pack": 110,
  "loom_code_search": 88,
  "loom_code_symbol": 66,
  "loom_code_grep": 64,
  "loom_code_ask": 54,
  "loom_search": 6
 }
}
```

## A1 analyze.py
```json
{
 "n": 120,
 "status": {
  "ok": 117,
  "max_turns": 3
 },
 "mean_s": 28.3,
 "median_s": 25.7,
 "tool_calls_total": 888,
 "retrieval": 314,
 "read": 240,
 "other": 334,
 "failed": 3,
 "denied": 0,
 "loom": 432,
 "context_pack": 111,
 "code_ask_calls": 43,
 "runs_with_code_ask": 43,
 "op_write": 0,
 "ask_outputs_found": 43,
 "ask_source": {
  "synthesized": 43
 },
 "ask_fake": 43,
 "ask_real_answer": 0,
 "ask_coverage": {
  "partial": 43
 },
 "ask_answer_len_mean": 230.0,
 "tokens_mean": 103042,
 "cost_usd": 4.56,
 "loom_tools": {
  "loom_code_search": 119,
  "loom_context_pack": 111,
  "loom_code_grep": 78,
  "loom_code_symbol": 74,
  "loom_code_ask": 43,
  "loom_search": 6,
  "loom_code_outline": 1
 }
}
```
