# Grading rules for the Django 6.1.3 retrieval benchmark

This document defines a deterministic score for each question and how tool-call, token, and wall-time metrics are taken from agent logs. Paths in `questions.jsonl` and `pilot_questions.jsonl` are relative to the clone root (on AO: `C:\Apps\hcr-bench\django`; Django tag `6.1.3`, commit `f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`).

The unit of grading is one (question, variant, repetition) run. The agent must finish with a structured answer (see the prompt in `METHOD.md` and `prompts/system.txt`) listing files and symbols. Narrative text is ignored except to recover a structured answer if the JSON block is missing but the same fields are clearly present.

## 1. Accuracy score (0 / 1 / 2)

Each question in `questions.jsonl` has:

- `ground_truth.files` — required file paths
- `ground_truth.symbols` — required symbol names (classes, functions, methods, or settings)
- `ground_truth.spans` — verified line ranges at the pinned SHA (inclusive, 1-based). Spans are the authority for “did they land in the right place?” but are not required in the agent’s answer.
- `acceptable_alternatives` — additional file/symbol sets that also count
- `grading_notes` — per-question exceptions, traps, and what is *not* enough

Line numbers in the agent’s answer are optional. If present, they must overlap a verified span for that symbol; a wildly wrong line range in the correct file does not by itself reduce a 2 to a 1, because several tools return chunk ranges rather than definition lines. A line range that points at a *different* symbol in the same file is treated as a wrong symbol.

### 1.1 Exact-lookup questions (`category: exact_lookup`)

These name a specific identifier.

- **2** — the answer includes the ground-truth file and the ground-truth symbol (or an `acceptable_alternatives` pair that the notes treat as a full substitute). Extra correct context (imports, callers, parents) is allowed.
- **1** — the answer includes the correct file but not the required symbol (for example, naming only `default_token_generator` when the required symbol is `PasswordResetTokenGenerator`, or naming only the parent class in the same file).
- **0** — the required file is missing, or the only symbols cited are explicit traps in `grading_notes` (wrong sibling class, setting default without the class, test helper, unrelated `resolve` method, and so on).

### 1.2 Semantic questions (`category: semantic`)

These describe behaviour and do not name the target identifier.

- **2** — the answer includes the primary implementation file and the primary symbol (or the pair of symbols) required by `grading_notes` for a full score. Example: for S01, `Storage.get_alternative_name` in `django/core/files/storage/base.py` is sufficient; for S13, both `connect` (where `close_at` is set) and `close_if_unusable_or_obsolete` are required unless the notes say otherwise.
- **1** — the answer finds a correct file or a documented caller/consumer but misses the implementing symbol, or finds only one side of a two-sided behaviour (for example, the `CONN_MAX_AGE` default in `django/db/utils.py` without the close-on-expiry logic).
- **0** — a different mechanism is named (the traps in `grading_notes`), or the files are unrelated.

### 1.3 Cross-file questions (`category: cross_file`)

These ask for a definition site plus consumers, or for a family of subclasses.

- **2** — the answer meets the completeness rule in that question’s `grading_notes` (usually: the setting or base class *and* a stated minimum set of consumers or subclasses, with module paths when several classes share a name such as `SessionStore` or `DatabaseWrapper`).
- **1** — only one side of the chain is correct (setting without consumers, base class without enough subclasses, public `resolve()` without `URLResolver.resolve`).
- **0** — the chain is wrong, or a namesake in another package is cited (for example `Template.resolve`).

Listing extra correct files beyond the minimum does not change a 2. Listing incorrect extras does not by itself reduce a 2, unless the required items are missing or the notes say a named trap must not be the only hit.

### 1.4 How to match files and symbols

- File paths are compared after normalising to POSIX relative paths from the clone root. A leading `django/` path, a Windows path to the same clone, or an absolute path ending in the same relative suffix all match. Paths under `tests/` are not substitutes for library files.
- Symbol matching is case-sensitive and ignores module prefixes and parent qualifiers: `TimestampSigner`, `signing.TimestampSigner`, and `django.core.signing.TimestampSigner` are the same symbol. `get_cookie_signer` and `signing.get_cookie_signer` match. A typo or a different identifier does not.
- Settings are symbols. `LOGIN_URL` in `django/conf/global_settings.py` is a valid symbol hit for C01.
- If the structured answer is missing or unparseable, the run scores 0 for accuracy. Do not guess from tool traces.

### 1.5 Aggregation

For each question and variant, report the three repetition scores and:

- **mean** of the three 0–2 scores
- **pass@3** — 1 if any repetition scored 2, else 0
- **strict@3** — 1 if all three scored 2, else 0

For a variant, report the sum and the mean of the 40 question means (range 0–80 and 0–2), plus the number of questions with pass@3 and strict@3. Do not convert 0–2 into a percentage without also showing the raw 0–2 mean.

## 2. Tool-call counts

Count every tool invocation the agent actually issues after the run starts, including failed calls and retries. Do not count server-side work that the agent did not request (background index sync, language-server boot).

Record, for each run:

| Field | Meaning |
| --- | --- |
| `tool_calls_total` | All tool invocations |
| `tool_calls_retrieval` | Calls whose purpose is to find candidate code (see below) |
| `tool_calls_read` | File reads, outline/peek, and snippet fetches of an already known path |
| `tool_calls_other` | Directory listings, `get_index_state` / `get_indexing_status`, LSP diagnostics, shell besides `rg`/`grep`, accidental edits, etc. |

Retrieval tools by variant:

- **ripgrep** — `rg`, `grep`, `ag`, `ack`, `findstr`, and any shell command whose primary purpose is a content or filename search. A shell `rg` plus a later `sed -n` on a known file counts as one retrieval call and one read.
- **hybrid-code-rag-mcp** — `search_rag` (and any alias configured as the search tool). `get_index_state` is `other`.
- **claude-context** — `search_code`. `index_codebase`, `clear_index`, and `get_indexing_status` are `other` (they should not run during a graded run).
- **Serena** — `find_symbol`, `find_declaration`, `find_referencing_symbols`, `find_implementations`, `search_for_pattern`, `get_symbols_overview`. `get_diagnostics_*` is `other`. Edit tools should not run; if they do, count them as `other` and flag the run.

A tool that both searches and returns snippets in one response still counts as one retrieval call, not as a read. If the agent then opens a file to confirm a symbol, that follow-up is a read.

If the agent is given a generic `bash` / `shell` tool, classify each invocation from its command line. An empty or unparseable command counts as `other`.

## 3. Token counts

Prefer the Grok Build CLI’s own usage record for the run (input / output / cache-read / cache-write if the CLI exposes cache figures). If the CLI writes a JSON or JSONL event log, take the final billed totals for that run, not a mid-run snapshot.

If the CLI does not expose usage:

1. First fallback: the model provider’s usage object in the same log (`prompt_tokens`, `completion_tokens`, and cache fields when present).
2. Second fallback: recount from recorded messages with the same tokenizer the CLI documents. State the tokenizer and that this is an estimate.

Always report, per run:

- `tokens_input` — prompt/input tokens, including tool results sent back to the model
- `tokens_output` — completion/output tokens, including tool-call argument tokens if the provider bills them as output
- `tokens_cache_read` / `tokens_cache_write` — 0 if unknown
- `tokens_total` — input + output + cache-write (do not add cache-read twice if the provider already includes it in input; follow the CLI’s published rule and record which rule was used)

Do not count tokens used to build indexes, start MCP servers, or warm a language server. Those are setup costs and are reported once in the harness notes, separately from the 480 graded runs.

If a run fails or is retried, keep the failed attempt’s tokens in an `attempts[]` list and report both `tokens_total_including_retries` and `tokens_total_final_attempt`. The headline number is `tokens_total_including_retries`.

## 4. Wall time

`wall_time_s` is the elapsed time from the moment the agent process is launched for that (question, variant, repetition) until the process exits (or the harness records a completed final answer, if the process is reused).

- Do not include index builds, container start, or MCP server start.
- If one long-lived agent or MCP server is reused, start the clock when the question is submitted and stop when the structured answer is received.
- Timeouts, crashes, and hangs: record `wall_time_s` up to the timeout, set `status` to `timeout` / `error`, and score accuracy 0. Do not drop the run from the token or tool-call totals.
- Use a monotonic clock. Persist UTC timestamps in the raw log as well, then convert to Europe/Warsaw when presenting human-readable times.

## 5. Run status and invalid runs

A run is **valid** if the agent returned a parseable structured answer (or clearly equivalent fields) without using a tool that the variant forbids (see `METHOD.md`).

- Forbidden-tool use: accuracy 0, keep other metrics, set `status=protocol_violation`.
- If the operator has to restart a crashed MCP server mid-run, mark `status=error` and repeat that repetition once. Keep both attempts in the raw log. The headline score uses the first valid attempt, or 0 if both fail.

## 6. Raw log fields

Each run’s log (JSONL, one object per run or a folder of per-run files) must contain at least:

```
run_id, question_id, variant, repetition (1..3),
status, accuracy, files_predicted, symbols_predicted,
tool_calls_total, tool_calls_retrieval, tool_calls_read, tool_calls_other,
tokens_input, tokens_output, tokens_cache_read, tokens_cache_write, tokens_total,
wall_time_s, started_at, ended_at, model, cli_version
```

plus the verbatim tool trace needed to audit the counts. Do not delete traces after scoring.
