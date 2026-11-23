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

- **code.ask disabled.** It needs an LLM, and the pilot runs on a fake one, so it is
  denied together with the other LLM / memory / escape-hatch tools. Loom's strongest
  "grounded answer" feature is therefore not measured here.
- **Default code scope.** `LOOM_CODE_ORG=dev`, `LOOM_CODE_NAMESPACE=code-django-bench`:
  calls without `namespace` read the bench index. Without it every `loom_code_*` call
  fails with VALIDATION_FAILED. hcr also serves one fixed index, so the agent does not
  have to know an index name in either variant.
- **SCIP (compiler tier) off.** Symbols and edges come from tree-sitter only
  (`tier: treesitter`); Loom's compiler-grade Python tier (scip-python) was not run.
- **No live GitHub data.** The repo entry is a local bare mirror; PR history, reviews
  and tracker data are empty, and the tools built on them are denied.
- **Provider name.** The repo entry is named `django/django` (GitHub-style), but no
  GitHub API is used.

## Tool policy (`scripts/run_one.py`)

| class | tools |
|---|---|
| retrieval | loom_code_search, loom_code_grep, loom_code_symbol, loom_code_callers, loom_code_context_pack |
| read | loom_code_outline, loom_code_enclosing (plus built-in read_file) |
| denied | loom_code_ask, loom_op, loom_search, loom_activate, loom_context_pack, loom_memory_get/set/update/delete (+ `loom_memory_*`), loom_working_memory_set (+ `loom_working_memory_*`), loom_code_pr_check, loom_code_impact, loom_code_bisect_candidates, loom_tracker_duplicate_check |

Denied tools get one `--deny MCPTool(loom__<tool>)` rule each (deny wins over
bypassPermissions). A denied call that still shows up in the stream is recorded as
`protocol_violation`. Built-in tools are the same as for hcr/serena/claude_context.
`loom_context_pack` (memories/decisions) and `loom_code_context_pack` (code briefing)
are different tools: the first is denied, the second is allowed.

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
