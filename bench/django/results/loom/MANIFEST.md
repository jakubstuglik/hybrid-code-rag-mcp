# Loom variant – manifest (local branch `bench-loom-variant`, not pushed)

Benchmark: Django 6.1.3 retrieval bench v2.1 (`bench/django/v2`), Django commit
f16e25dcb9fe55734ba4ea2b00ac34405b7df74a, only `django/` indexed.
Written 2026-11-23 (Europe/Warsaw) on JSTUGLIK-AO.

## Agent

| item | value |
|---|---|
| Grok Build CLI | `grok 1.0.91 (74ad9772d2ff) [alpha]` |
| model / effort / turns / timeout | grok-4.7, reasoning effort high, max 20 turns, 180 s |
| session | fresh session per run, isolated `GROK_HOME`, `GROK_MEMORY=0`, `GROK_DISABLE_AUTOUPDATER=1` |
| prompt / schema | `v2/prompts/system_v2.txt` + `v2/prompts/answer.schema.json` – same as hcr / serena / claude_context / ripgrep |
| schedule | `scripts/schedule.py --variants loom --seed 20261114 --mode blocked_rotation` (block `loom`) |

The other variants were not re-run: hcr, serena, claude_context and ripgrep come from
the existing v2.1 tables (Grok 1.0.70 era). The Grok version differs between them and
this variant.

## Loom stack

| item | value |
|---|---|
| Loom | v1.3.0, tag commit 47b479dcdae4c089aef2690428fa4c9a8f54554c (Apache-2.0) |
| image loom | `ghcr.io/clickhouse/loom@sha256:de44a3df7af74392c8fe149c360fa1d9c2f27ac579dd1a82ddaacbb99e373b5c` (tag 1.3.0) |
| image extractor | `ghcr.io/clickhouse/loom-extractor@sha256:64a4ae2c37a3d26b20f39e8a536bde9f35b446466b2be226d83675c1a826dfba` (tag 1.3.0) |
| image ClickHouse | `clickhouse/clickhouse-server@sha256:4f491abc44d9f4a1747c033c35ddd5bc385521305d85ca8251ba0824ff597035` (26.10.4.207) |
| deployment | docker compose project `loom-pilot`, only `127.0.0.1:7777` published, ClickHouse data in named volume `loom-pilot_clickhouse` (bind mount on Windows fails at migration 097: `renameat2() is not supported`) |
| limits | loom mem 4g / 6 CPUs, ClickHouse mem 3g / 4 CPUs, extractor 1.5g |
| MCP | `http://127.0.0.1:7777/mcp?toolset=coding`, Grok server name `loom` |
| embeddings | `local` = bge-small, 384 dims, fastembed/ONNX on CPU, bundled in the image; `/v1/health` fake_embedding=false |
| LLM | fake (`fake-echo-1`), `LOOM_REQUIRE_REAL_PROVIDERS=true`; the only health problem is `fake_llm`. code.search runs without an LLM (HyDE, concept expansion, rerank, summaries off) |
| index | `loom code backfill --embed --concurrency 1 --commit f16e25dc…` (default concurrency 4 was OOM-killed at the 4g limit), then `--edges-second-pass`. ClickHouse counts: 1190 files, 17867 chunks (17867 embedded, coverage 1.0), 19259 symbols, 21502 edges. Repo entry: `path_prefixes: django/`, `exclude: tests/**, docs/**, js_tests/**` |

## Fairness notes

- **Variant A1 (Jakub 23.11 11:55): no read blocks.** The first pilot (commits up to
  078bef4) denied every tool but 7 `loom_code_*`; the model kept reaching for the denied
  `loom_context_pack` / `loom_code_ask` and 4 of 30 runs answered from files only. A1
  opens every read tool, as the vendor's own agent A/B does (`bench/agent_localization_ab.py`
  at 47b479d allows all of `mcp__loom`), and bans only memory writes.
- **Fake LLM.** `code.ask` answers with an echo (`[fake-synthesis: fake-echo-1] ...`)
  plus real `path:line` citations; it is counted (`tool_calls_loom_code_ask`) and
  classed retrieval. The index was built without LLM chunk descriptions
  (`context_description` empty on all 17,867 chunks), which Loom's defaults expect.
- **Prompt unchanged** (METHOD §4): `system_v2.txt`, no skill. Loom's own MCP
  `initialize` instructions ("First step of each task: call `loom_context_pack`...") do
  reach the model: Grok 1.0.91 logs them at the handshake and the model quoted them
  verbatim in a no-tool check (23.11, `bench-logs-loom/smoke-harness/mcp-instr-*`).
  Every MCP variant gets its server's instructions the same way.
- **Run hygiene.** Before each loom group the runbook truncates `loom.code_answers`
  (code.ask answer cache) and `loom.llm_response_cache`, deletes memory rows outside the
  code namespace, and audits the memory tables (must be 0); after the group it audits
  again. Log: `$T\loom-hygiene.tsv` and runbook lines `loom hygiene pre|post`.
- **Default code scope.** `LOOM_CODE_ORG=dev`, `LOOM_CODE_NAMESPACE=code-django-bench`:
  calls without `namespace` read the bench index. Without it every `loom_code_*` call
  fails with VALIDATION_FAILED. hcr also serves one fixed index, so the agent does not
  have to know an index name in either variant.
- **SCIP (compiler tier) off.** Symbols and edges come from tree-sitter only
  (`tier: treesitter`); Loom's compiler-grade Python tier (scip-python) was not run.
- **No live GitHub data.** The repo entry is a local bare mirror; PR history, reviews
  and tracker data are empty, so pr_check / bisect / tracker return empty verdicts.
- **Provider name.** The repo entry is named `django/django` (GitHub-style), but no
  GitHub API is used.

## Tool policy (`scripts/run_one.py`, A1)

| class | tools |
|---|---|
| retrieval | loom_code_search, loom_code_grep, loom_code_symbol, loom_code_callers, loom_code_context_pack, loom_code_ask, loom_code_impact; loom_op with a read `code.*` op |
| read | loom_code_outline, loom_code_enclosing, loom_op code.outline / code.enclosing (plus built-in read_file) |
| other | loom_context_pack, loom_search, loom_activate, loom_memory_get, loom_code_bisect_candidates, loom_code_pr_check, loom_tracker_duplicate_check, loom_op help / index status / non-code read ops |
| denied | loom_memory_set, loom_memory_update, loom_memory_delete, loom_working_memory_set |

Denied tools get one `--deny MCPTool(loom__<tool>)` rule each; a denied attempt is
recorded in `tool_calls_denied` (not a violation), one that ran is a
`protocol_violation`. `loom_op` naming a write op (`LOOM_WRITE_OPS`, 163 ops with
`read_only=False` in Loom's registry at 47b479d) is a violation whether or not it ran.
Per-run counters: `tool_calls_loom`, `tool_calls_loom_context_pack`,
`tool_calls_loom_code_ask` (direct or via loom_op), `tool_calls_loom_op_write`.

## Checksums (`v2/SHA256SUMS`, recomputed on this branch)

Hashes are taken over LF-normalised content, i.e. the committed blobs. `*.json` is
`text=auto` and has CRLF in the Windows checkout, so a plain Get-FileHash of
`prompts/answer.schema.json` differs while its content is unchanged.

Changed entries:

- grading.md, self_check.md, README.md, NIGHT_CHECKLIST.md (part), night/run_night_v21.ps1
  (part), night/start-ollama-4060.ps1: these were edited in commit **98185bd**
  (2026-11-16, "docs: remove machine-specific details") after SHA256SUMS was written.
  The question pools, answer keys, prompts, schema and grade_run.py are unchanged.
- scripts/apply_retrieval_gate.py, scripts/grade_night.py, scripts/pilot_gate.py,
  night/run_night_v21.ps1, NIGHT_CHECKLIST.md: the loom variant (this branch).

The frozen v1 `bench/django/SHA256SUMS` was left as is. Its grading.md and self_check.md
entries also differ because of 98185bd, and prompts/answer.schema.json only by CRLF.
