# Grading rules for the Django 6.1.3 retrieval benchmark, v2

This document applies only to the v2 pool in this directory
(`questions.jsonl`, `pilot_questions.jsonl`). The v1 rules in
`../grading.md` are a frozen historical record and are not rewritten.

Paths are relative to the clone root (on AO: `C:\Apps\hcr-bench\django`;
Django tag `6.1.3`, commit `f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`).

The unit of grading is one (question, variant, repetition) run. The agent
must finish with a structured answer listing `files`, `symbols`, and
`spans`. Narrative text is ignored except to recover a structured answer
if the JSON block is missing but the same fields are clearly present.

## 1. Line-tolerance N

**N = 10** (inclusive, 1-based).

A predicted span `[p0, p1]` hits a gold span `[g0, g1]` on the same file
when all of the following hold:

- the predicted interval overlaps the gold interval (`p0 <= g1` and `p1 >= g0`);
- the predicted interval is contained in the padded gold interval
  (`p0 >= g0 - N` and `p1 <= g1 + N`);
- if both the predicted span and the gold span name a symbol, the
  identifiers match after ignoring module prefixes
  (`Task._reconstruct` equals `_reconstruct`).

A single line `k` is treated as `[k, k]`. Citing a window that starts more
than N lines before the gold span, or ends more than N lines after it
(for example the whole file around a one-line constant), does not count
as an exact location.

## 2. Accuracy score (0 / 1 / 2)

Each question has `ground_truth.files`, `ground_truth.symbols`, and
`ground_truth.spans`, plus optional `acceptable_alternatives`.

- **2** — the answer includes every required file and every required
  symbol (or a complete `acceptable_alternatives` set), **and** every
  gold span is hit under the ±N rule above.
- **1** — the answer finds the right file and/or the right symbol, but
  omits a line range, or the predicted range is outside ±N, or only one
  side of a cross-file item is correct.
- **0** — the required file is missing (and no acceptable alternative
  set is fully matched), or the structured answer is missing.

An answer without an exact location therefore scores **at most 1**, even
when the file and symbol are right. That is the main change from v1,
where line numbers in the agent's answer were optional for a score of 2.

Extra correct files or symbols do not reduce a 2. A named trap in
`grading_notes` is not a substitute for the required symbol.

File-path and symbol normalisation are the same as v1: POSIX-relative
paths from the clone root; `django/` prefixes and Windows paths are
stripped; symbol matching is case-sensitive and ignores module prefixes.
Paths under `tests/` are not substitutes for library files.

### 2.1 Retrieval-tool gate (applied after blind grading)

The automatic grader in `scripts/grade_run.py` is **blind to variant**.
After it has written scores, `scripts/apply_retrieval_gate.py` joins
them back to the run logs:

- For `ripgrep`, `hcr`, `claude_context`, and `serena`, if
  `tool_calls_retrieval == 0`, accuracy is forced to **0**. The blind
  score is kept as `accuracy_before_gate`.
- For the `none` control, the gate is not applied. Zero retrieval calls
  are expected. If a `none` run issued a retrieval call, the harness
  already marks `protocol_violation`; that run's accuracy is still
  taken from the structured answer unless a later audit overrides it.

Every run log must record `tool_calls_total`, `tool_calls_retrieval`,
`tool_calls_read`, and `tool_calls_other` (same classification as v1).

## 3. Aggregation

For each question and variant, report the three repetition scores and:

- **mean** of the three 0–2 scores (after the retrieval gate)
- **pass@3** — 1 if any repetition scored 2, else 0
- **strict@3** — 1 if all three scored 2, else 0

Per category **E / S / C**, per variant: the mean of that category's
per-question means, with a 95% percentile bootstrap CI (seed `20261114`,
`n_boot=10000`), same protocol as METHOD.md §16.5. `none` is reported
in a separate control section. Do not collapse the table into a single
headline average.

## 3. v2.1 controls (2026-11-15)

- `none` (pure memory, no tools) and `read_only` (`read_file` only) are
  graded with the same 0/1/2 rubric and are not subject to the
  retrieval-tool gate in §2.1.
- A control run whose harness status is `protocol_violation` (`none`
  called any tool, `read_only` called anything but `read_file`) is scored
  **0** after blind grading (`v2/scripts/grade_night.py`).
- Pools: `pilot21_questions.jsonl` (Q3P01–Q3P10) for the v2.1 pilot;
  `questions.jsonl` (revised, see `self_check.md` §v2.1) for the official
  run.
