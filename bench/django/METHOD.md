# Django 6.1.3 retrieval benchmark — frozen method

Status: **Stage 1 (method freeze).** This document, the 40 evaluation questions, the answer key, and the 10 pilot questions are frozen before any variant is run. **Do not start the pilot or the 480-run table until an operator approves this method.**

Date of freeze: 2026-11-14 (Europe/Warsaw).
Host for the eventual runs: a Windows 11 laptop, 13th Gen Intel Core i9-13980HX, 32 GB RAM, Docker Desktop 29.8.1, RTX 4060 Laptop (8 GB, GPU 0) and RTX 3060 (12 GB, GPU 1).

The file hashes in [§15](#15-frozen-artefact-hashes) are part of the method. If a question or key file changes, the method has changed and must be re-approved.

## 1. What is being measured

Four retrieval setups, one agent, one prompt, one step budget, three repetitions:

| Variant id | Retrieval allowed during a graded run |
| --- | --- |
| `ripgrep` | `rg` (preferred) or `grep`, plus file reads |
| `hcr` | hybrid-code-rag-mcp search tool plus file reads |
| `claude_context` | `@zilliz/claude-context-mcp` `search_code` plus file reads, fully local |
| `serena` | Serena read-only navigation tools plus file reads |

The agent is **Grok Build CLI** on this machine (`grok` 1.0.70, `f50904eaee6c`, stable; binary `~/.grok/bin/grok.exe` (or `GROK_BIN`)). Confirmed present and logged in with grok.com on 2026-11-14. Default model in `~/.grok/config.toml`: **`grok-4.7`**. Default reasoning effort: **`high`**. Those three pins (CLI version, model, effort) are used for every variant.

Schedule once approved:

- Official table: 40 questions × 4 variants × 3 repetitions = **480 graded runs**, sequential, reusing already-started MCP servers and indexes. Do not rebuild an index between repetitions of the same variant.
- Harness pilot (separate pool, not in the table, not for tuning): 10 questions × 4 variants × 3 = 120 runs, after a still-smaller smoke (see §12).

## 2. Subject repository

- Remote: `https://github.com/django/django`
- Tag: `6.1.3` (annotated tag object `8896844298b244d5bf156c47366f65bb79b2b731`, peeled commit below)
- **Pinned commit:** `f16e25dcb9fe55734ba4ea2b00ac34405b7df74a` (release commit, 2026-11-03)
- Local clone on the benchmark host (2026-11-14, shallow of tag 6.1.3): `<bench-dir>/django` (58.8 MB on disk). `git rev-parse HEAD` is the pinned commit. `HEAD` is detached, which is intended.
- Scope to index / search: the library package `django/` only (909 Python files, 165 634 lines at this commit). The official test suite is the top-level `tests/` directory (1 999 Python files) and is **out of scope**. There are no `tests/` trees inside the `django/` package at this tag.

Do not index `tests/`, `docs/`, `js_tests/`, or `.git`. Do not run against `master` / `main`.

## 3. Question sets

Two disjoint pools, both checked against the pinned tree before this freeze (script: `scripts/verify_keys.py`, 2026-11-14, 0 failures):

| File | Role | Count | Mix |
| --- | --- | --- | --- |
| [questions.jsonl](questions.jsonl) | Official evaluation set. Frozen. The only questions that enter the headline table. | 40 | 13 `exact_lookup` (E01–E13; grep is expected to be strong), 14 `semantic` (S01–S14; “how does X work”, worded so a literal ripgrep of the question should not uniquely hit the key), 13 `cross_file` (C01–C13; setting plus consumers, or a family of subclasses) |
| [answer_key.jsonl](answer_key.jsonl) | Standalone key for the official 40 (id, category, files, symbols, spans, alternatives, notes). Same content as the key fields in `questions.jsonl`. | 40 | — |
| [pilot_questions.jsonl](pilot_questions.jsonl) | **Separate pool.** Used only to test the harness after approval. Not for prompt/tool/index tuning. Not part of the table. IDs P01–P10 do not appear in the official set. | 10 | 4 exact, 3 semantic, 3 cross-file |

Every official and pilot key lists at least one file and one symbol as evidence. Spans are inclusive 1-based line ranges at `f16e25dc`. The file and the symbol exist in that commit (verified).

A sample of official semantic questions was already checked for “ripgrep of the question text uniquely solves it” (see [self_check.md](self_check.md), seed `20261114`). That check is part of the method, not a reason to edit the frozen official set.

## 4. Agent prompt and step budget (identical across variants)

Use [prompts/system.txt](prompts/system.txt) verbatim as `--system-prompt-override`. Do not add variant-specific hints, tool names, or identifier spoilers.

The user message is exactly the `question` field, plus one line that states the absolute checkout path (`<bench-dir>/django`). Do not paste ground truth, grading notes, this method, or the answer key into the agent context. Do not place the `bench/django/` files inside the indexed tree.

Budget, same for every official and pilot run:

- `--max-turns 20`
- Wall-clock cap **180 seconds** from question submit to process exit (or to the structured answer if a process is reused). Raise the cap only if a post-approval smoke shows legitimate slower answers, and raise it for all variants together.
- `--reasoning-effort high`
- `--no-subagents` and `--disallowed-tools Agent` (no subagents)
- `--disable-web-search`
- `GROK_MEMORY=0` (no cross-session memory)
- `--no-plan`
- `--no-auto-update`
- `--json-schema` from [prompts/answer.schema.json](prompts/answer.schema.json) (or omit it for every variant if a smoke shows the flag misbehaves; do not enable it for only some variants)
- `--output-format streaming-json` so tool traces and a final usage object are logged
- Fresh session per (question, variant, repetition): pass a new UUID as `-s`. Do not use `-c` / `-r`.

## 5. Grok Build CLI wiring

Headless invocation (shape; flags confirmed against `grok help` and `~/.grok/docs/user-guide/14-headless-mode.md` on this CLI, **not** executed against the questions):

```
set GROK_HOME=<bench-dir>\grok-home
set GROK_MEMORY=0
set GROK_DISABLE_AUTOUPDATER=1
grok -p "<user message>" ^
  --cwd <bench-dir>\django ^
  --system-prompt-override "<contents of prompts/system.txt>" ^
  --model grok-4.7 ^
  --reasoning-effort high ^
  --max-turns 20 ^
  --output-format streaming-json ^
  --json-schema "<contents of prompts/answer.schema.json>" ^
  --disable-web-search ^
  --no-subagents --no-plan --no-auto-update ^
  --permission-mode bypassPermissions ^
  --disallowed-tools "Agent,web_search,web_fetch,write,search_replace,StrReplace,EditNotebook,Delete" ^
  -s <fresh-uuid>
```

`--system-prompt-override` takes the prompt text; the runner loads `prompts/system.txt`.

**Isolation:** the user’s `~/.grok/config.toml` attaches MCP servers that must not be in a graded session (including the operator's everyday project MCP servers). Every benchmark process must run with `GROK_HOME` set to an isolated directory such as `<bench-dir>/grok-home` (documented override). That home is created only after approval: a minimal `config.toml` (`default = "grok-4.7"`, `default_reasoning_effort = "high"`, no user MCP servers) plus whatever authentication the operator approves (a login in that home, or `XAI_API_KEY`). Do not copy unrelated MCP configs. Do not disable or edit the user’s everyday `~/.grok` MCP servers as a shortcut.

Attach **exactly one** retrieval MCP server (or none, for `ripgrep`) in that isolated home, per variant. `grok mcp add` / `enable` / `disable` only inside `GROK_HOME`.

Token and cost: prefer the `usage` / `modelUsage` / `total_cost_usd` object on the streaming-json `end` event. `grok usage <sessionId>` is the fallback. The CLI documents that cost is stamped for API-key traffic today and that **pool/OAuth paths often omit cost**. This host was logged in with grok.com (OAuth). If `total_cost_usd` is absent, record tokens, set `cost_source=estimated_list_price` or `cost_source=unreported`, and do not invent a billed total.

## 6. Tool restrictions per variant

All variants may use a file-read tool once a path is known. A recursive directory walk used as a substitute for search is forbidden; a single-directory listing of a path already in hand is allowed and counted as `other`.

### 6.1 `ripgrep`

- Allowed retrieval: `rg` (preferred) or `grep`. Built-in Grok `grep` is an equivalent content search and is allowed, but the headline protocol prefers a pinned `rg` on `PATH` invoked through the shell tool (`run_terminal_cmd`).
- `rg` was **not** on `PATH` on the benchmark host at freeze time (`where rg` failed, 2026-11-14). After approval, install an official Windows ripgrep release, put it on the `GROK_HOME` process `PATH`, and record `rg --version` in the run manifest before the first graded run. Prefer a 14.x or 15.x GitHub release and pin that exact version string.
- Forbidden: every MCP server, every language server, `Get-ChildItem -Recurse` / `find` used to scan file contents, and any embedding search.
- Working directory: the clone root. Typical invocation: `rg -n --glob "*.py" --glob "!tests/**" <pattern> django`.

### 6.2 `hcr` (hybrid-code-rag-mcp)

Pin the hybrid-code-rag-mcp tree used to serve the index: this repository, branch `feature/django-bench`, at the commit recorded in the run manifest (the parent of this work is `feature/quickstart-cpu` at `734f0c87082cef70a12d5d5a83c267cace876b6d`). Do not silently move to another SHA mid-run.

Default dense model: `jinaai/jina-embeddings-v2-base-code` through local TEI, BM25 (`Qdrant/bm25`) on CPU. Product default; a different embedder would change the comparison.

Quickstart wiring on the benchmark host (to be started only after approval, and only when free RAM stays ≥ 4 GB):

- Separate Compose project, for example `hcr-django-bench`. Publish **only** the MCP port (pick a free host port, not 8192). Qdrant and TEI stay on the Compose network. **Do not** use or bind host ports 6340, 6341, 6342, 6380, or other in-use reference Qdrants.
- `.\start.ps1 -Repo <bench-dir>\django -RepoConfig <repo>\bench\django\repo_config.py -Project hcr-django-bench` (GPU: add `-Gpu` to use the 4060; CPU is acceptable if VRAM or RAM is tight). `repo_config.py` limits `SOURCE_DIRS` to the `django/` package, `.py` only, and names the tools `search_django` / `get_django_index_state`.
- Build the index once. Record chunk count, wall time, and embedding provenance. Do not `--clear` between graded repetitions.
- During graded runs the agent may call `search_django` (or whatever `MCP_TOOL_NAME` the running server exposes — record it) and may read files. `get_django_index_state` is operator/other, not a retrieval call. Do not reindex mid-run.
- Prefer TEI on the 4060 for index and query. Do not also load Ollama on that GPU at the same time. Do not touch the 3060 (it may already host other workloads; keep ≥ 300 MiB free).

### 6.3 `claude_context` (zilliztech/claude-context, local only, no cloud accounts)

Pins (confirmed on npm, 2026-11-14):

- npm package: **`@zilliz/claude-context-mcp@0.1.16`** (published 2026-11-12; this was also the dist-tag `latest`. A `0.1.17-rc.0` exists; do not use `@latest` on the day of the run). Record `npm view @zilliz/claude-context-mcp@0.1.16 dist.tarball` and the resolved version.
- Upstream: `https://github.com/zilliztech/claude-context`
- Embeddings: Ollama, **`nomic-embed-text`** (768 dimensions). `EMBEDDING_PROVIDER=Ollama`, `EMBEDDING_MODEL=nomic-embed-text`, `OLLAMA_HOST=http://127.0.0.1:11434`, `EMBEDDING_DIMENSION=768`.
- Vector store: **local Milvus standalone** in Docker, `MILVUS_ADDRESS=127.0.0.1:19530`, no `MILVUS_TOKEN`. Official Claude Context local path. Official standalone is documented as needing about 8 GB RAM (16 GB recommended). Give the compose stack a memory limit. **Do not start Milvus while host free RAM is only a few gigabytes** (see §13). If standalone cannot be started without going below 4 GB free RAM, stop and record the failure; `milvus-lite` is an unofficial fallback and is used only if standalone is impossible, and must be said so in the report.
- Leave `OPENAI_API_KEY`, `VOYAGEAI_API_KEY`, `GEMINI_API_KEY`, and any Zilliz cloud token unset. No cloud accounts will be created for this benchmark.

Config in the isolated environment (not the user’s everyday profile unless the operator chooses a dedicated `%USERPROFILE%\.context\.env` that does not add cloud keys):

```
EMBEDDING_PROVIDER=Ollama
EMBEDDING_MODEL=nomic-embed-text
OLLAMA_HOST=http://127.0.0.1:11434
EMBEDDING_DIMENSION=768
MILVUS_ADDRESS=127.0.0.1:19530
CLAUDE_CONTEXT_BACKGROUND_SYNC=false
```

Launch: `npx -y @zilliz/claude-context-mcp@0.1.16`. Index once with `index_codebase`, `splitter=ast`, ignore `tests/**`, `docs/**`, `js_tests/**`, `.git/**`, path = the Django clone (record whether the tool was pointed at the clone root or at `django/`). During graded runs the agent may call `search_code` only (plus file reads). `HYBRID_MODE` stays at its default (`true`) unless a recorded decision changes it.

This is a product-default vs product-default comparison (Jina code embeddings vs `nomic-embed-text`), not a same-embedder ablation.

### 6.4 `serena` (oraios/serena, LSP-based)

Pins (confirmed on PyPI / GitHub, 2026-11-14):

- **`serena-agent==2.1.0`** (GitHub release v2.1.0, 2026-10-19, tag commit `5e4f5cd`). Repository: `https://github.com/oraios/serena`. This was the current PyPI release at freeze time.
- Install: `uv tool install -p 3.13 serena-agent==2.1.0`. `uv` 0.10.7 was already on the host (`~/.local/bin/uv`). Record `serena --version`.
- Language backend: default language-server backend, **not** the JetBrains plugin. Python language server: Serena’s default Pyright integration.

In the Django clone: `serena project create` / `serena project index`, `.serena/project.yml` language `python`, ignore `tests/`, `docs/`, `js_tests/`, `.git/`. Add a `pyrightconfig.json` (or equivalent extra root) so `import django` resolves inside the clone, without installing a different Django into site-packages. Start MCP: `serena start-mcp-server --project <bench-dir>/django --open-web-dashboard false`. Prefer one long-lived server for all Serena runs.

Allowed during graded runs: `find_symbol`, `find_declaration`, `find_referencing_symbols`, `find_implementations`, `get_symbols_overview`, and `search_for_pattern` (regex search is part of the product and is allowed in the default protocol). An LSP-only ablation that disables `search_for_pattern` may be run later; it is not part of the 480-run headline unless the operator changes this method before starting.

Forbidden: `replace_symbol_body`, `insert_before_symbol`, `insert_after_symbol`, `rename_symbol`, `safe_delete_symbol`, and any command that writes files or executes arbitrary mutating code.

## 7. Blind grading

The official accuracy judge is the **deterministic script** [scripts/grade_run.py](scripts/grade_run.py), implementing [grading.md](grading.md) (scores 0 / 1 / 2 from files and symbols). It does not need to know the variant.

Protocol:

1. Each raw run log is stored under `logs/raw/` with `variant` present (needed for tool-call classification and aggregation).
2. Before official scoring, [scripts/anonymize_answers.py](scripts/anonymize_answers.py) writes `logs/anonymized/` objects that contain a random `grade_id`, the question id, predicted files/symbols, and optional narrative — **no variant, no repetition label, no tool-name leakage in the payload the judge sees**. A hidden map `logs/anonymized/map.json` (operator only) joins `grade_id` back to `(variant, repetition, run_id)` after scoring.
3. `grade_run.py` reads only the anonymized payload and the frozen answer key. It must not be given the map or the variant id.
4. After automatic scoring, a **human audits a sample**: at least 40 anonymized official answers (one tenth of 480), drawn with a documented seed (proposed: `20261114`), stratified by category (exact / semantic / cross-file) and by automatic score (0, 1, 2). The auditor still does not see the variant. Disagreements are resolved in writing; the headline table uses the post-audit scores.
5. An LLM is **not** the official judge. If a second-pass LLM review is added later, it must use the same anonymized payloads, the model must be named (proposed: `grok-4.7`, not used for the agent’s retrieval loop in the same session), and every disagreement with the script must go through the same human sample rule. That pass would not replace the script without a method change.

## 8. Metrics

Per (question, variant, repetition), as in [grading.md](grading.md):

- `accuracy` (0 / 1 / 2)
- `tool_calls_total`, `tool_calls_retrieval`, `tool_calls_read`, `tool_calls_other`
- `tokens_input`, `tokens_output`, `tokens_cache_read`, `tokens_cache_write`, `tokens_total` (headless field policy: `input_tokens` is uncached only; `total_tokens = input + cache_read + cache_creation + output`)
- `wall_time_s`
- `cost_usd` and `cost_source` (`cli`, `grok_usage`, `estimated_list_price`, or `unreported`)
- `status`, model, CLI version, timestamps (UTC in the log, Europe/Warsaw in human tables)

Three repetitions: report the three scores and the spread (min / median / max, or mean ± range) for accuracy, tool calls, tokens, time, and cost. Aggregate with mean, pass@3, and strict@3 as in grading.md.

Failed, timed-out, or protocol-violating runs stay in the totals (accuracy 0).

Index-build time, tokens, and disk are setup costs, reported once, not folded into the 480-run means.

## 9. Harness scripts (not run against the tools in Stage 1)

| Script | Purpose |
| --- | --- |
| [scripts/verify_keys.py](scripts/verify_keys.py) | Check that every key’s files, symbols, and spans exist in the pinned tree. **Already run** on the official 40 (0 failures). Run it on the pilot set as part of this freeze. |
| [scripts/grade_run.py](scripts/grade_run.py) | Deterministic 0/1/2 grader. |
| [scripts/anonymize_answers.py](scripts/anonymize_answers.py) | Strip variant labels before grading. |
| [scripts/aggregate.py](scripts/aggregate.py) | Means, pass@3, strict@3, and spread. |
| [scripts/run_one.py](scripts/run_one.py) | Planned single-run runner. **Refuses to launch Grok or MCP servers unless `--approved-by-operator` is passed.** Stage 1 must not pass that flag. |

Raw logs of future runs belong under `logs/raw/` in this directory. Keep them locally; do not commit them. Result tables belong under [results/](results/).

## 10. Install plan (after approval; not started in Stage 1)

1. Install a pinned `rg` on `PATH` (see §6.1).
2. Create `<bench-dir>/grok-home` and authenticate there; do not reuse the user’s MCP list.
3. Confirm free RAM ≥ 4 GB **plus** the footprint of the next service before starting Docker/TEI/Milvus/Ollama/Serena (see §13). Other desktop applications were left running; do not close them to make room (see §16.7).
4. HCR: start project `hcr-django-bench` with [repo_config.py](repo_config.py), index `django/`, record stats. Stop TEI if the next step needs the 4060.
5. Install Ollama for Windows, `ollama pull nomic-embed-text`. Start Milvus standalone only if the memory budget in §13 is met. Index with claude-context 0.1.16. Then stop Ollama/Milvus before HCR graded runs, and vice versa.
6. `uv tool install -p 3.13 serena-agent==2.1.0`, project index, health-check, long-lived MCP server with the dashboard off.

Do not start or restart Docker Desktop or WSL over SSH. Do not prune other people’s images. Do not touch unrelated host services or images that are not part of this benchmark.

## 11. Publication hygiene

The public artefact should include this pin, the question files, the key, grading.md, the aggregation tables under [results/](results/), index-build commands, and software versions. Raw run logs stay on the operator's machine and are not committed. It must not include secrets, cloud endpoints, `auth.json`, API keys, or project names outside this public Django + tool comparison.

## 12. After approval, before the 480

1. Re-confirm the Windows checkout is `f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`.
2. Record `grok --version`, `rg --version`, `serena --version`, the exact `npx @zilliz/claude-context-mcp@0.1.16` resolved version, hybrid-code-rag-mcp SHA, TEI model id, Ollama `nomic-embed-text` digest, Qdrant/Milvus versions, MCP port.
3. A tiny smoke **outside both frozen pools** (for example “Where is the class `Http404` defined?”) — one question per variant, discarded from every table. Do not use official or pilot items for smoke if that can be avoided.
4. Then the **10-question pilot** (`pilot_questions.jsonl` only), 4 × 3, to test logging, tool restriction, grading, and anonymization. Do not change the official 40, the prompt, or the pins because of pilot scores. If the harness is broken, fix the harness and re-pilot.
5. Confirm token usage appears in the logs. Confirm the agent cannot see the answer key.

## 13. Resource estimate (planning figures, not measurements)

Replace estimates with measured numbers before publishing results.

### Wall clock

| Step | Estimate | Notes |
| --- | --- | --- |
| Django clone | already done, ~1 min, 58.8 MB | Shallow tag 6.1.3 at the pinned commit |
| HCR index of `django/` (Jina v2 base code, TEI) | 10–25 min first time | GPU on the 4060 preferred; CPU is slower but acceptable |
| Ollama `nomic-embed-text` pull | 1–3 min | Small embedding model |
| Claude Context index (AST + Ollama + Milvus) | 15–40 min first time | Depends on Ollama throughput on the 4060 |
| Serena / Pyright index | 3–15 min | `tests/` is already out of the package tree |
| One graded run | 20–90 s typical, 180 s cap | ripgrep at the fast end |
| 120 pilot runs (10 × 4 × 3) | about 1.5–3 hours | After approval, not in Stage 1 |
| 480 official runs (40 × 4 × 3), sequential | about 6–12 hours | Overnight is realistic, plus operator time for failures |

### RAM, GPU, disk

Host RAM at Stage 1 start (2026-11-14 12:42:41 Europe/Warsaw): **5.09 GB free** of 32.4 GB (later 5.41 GB before the clone, 5.20 GB after). The 4 GB free floor is currently met, but only just. Largest Working-Set groups then:

- `vmmemWSL` 8 547 MiB (Docker Desktop WSL)
- other desktop applications (IDE, browser, and similar) together several GB
- typical Windows services (`svchost`, `MsMpEng`, PowerShell)

Official Milvus standalone wants ~8 GB RAM (16 GB recommended). **Starting it on top of the present footprint would likely break the 4 GB free floor.** Before any Milvus/TEI/Ollama start, free enough RAM (close or suspend IntelliJ, extra Chrome, Steam, or cap WSL2 memory) so that **free RAM stays ≥ 4 GB with the service running**. Do not start two embedders on the 4060 at once. The 3060 already hosts other workloads (~0.9–1.0 GB); keep ≥ 300 MiB free there; do not pin TEI or Ollama to GPU 1.

Dedicated HCR Qdrant (inside the compose project, unpublished): ~0.5–1 GB RAM. TEI Jina v2 base code: previously measured on this machine (2026-11-14) at about 2.0 GiB container RAM (CPU image) or about 430–440 MiB extra VRAM on the 4060 (CUDA image), not including other desktop use.

Disk: C: had 175.8 GB free at start. Images already on the host include TEI `cpu-latest` / `89-latest` and Qdrant `v1.17.0` (do not delete them). Milvus standalone images, etcd/minio, the nomic model, and two vector stores may add several GB. There is enough disk; still avoid a global prune.

### Grok Build cost and limits

On 2026-11-14 the CLI reported: “You are logged in with grok.com.” Usage on that path comes from the account’s **shared Grok / X subscription pool**, not necessarily from a stamped API invoice. xAI does not publish the absolute size of that pool (only plan multiples of an unpublished Plus allotment, weekly, shared with other Grok products and Cursor). The operator must read the account usage view before starting 120 or 480 runs and stop if the pool will not last.

If the same work were billed at the published **grok-4.7** API list price (docs.x.ai, checked 2026-11-14): **$2 / $0.50 / $6** per 1M tokens for input / cached input / output below a 200K-token prompt; **$4 / $1 / $12** when a prompt reaches 200K (the higher rate applies to the whole request, not only the overflow). Context window 500K. Rate limit quoted for the API: 150 requests/s — not the binding constraint here. `grok-4.7-build-fast` is plan-billed in Grok Build and is **not** the pinned model.

Illustrative envelope for **480 official runs** at list prices (not a measurement):

| Assumption per run | 480-run input + output | List-price envelope (ignoring cache, under 200K) |
| --- | --- | --- |
| 20k in + 2k out | 9.6M + 0.96M | ≈ $25 |
| 50k in + 4k out | 24M + 1.92M | ≈ $60 |
| 100k in + 6k out | 48M + 2.88M | ≈ $113 |

Add ~25% if the 120-run pilot is also billed the same way. Runs that cross 200K input are much more expensive. Cache hits, if stamped, are cheaper. **Do not treat these figures as a quote**; they are a planning ceiling. Prefer `total_cost_usd` from the CLI when it is present.

## 14. Open risks

- Claude Context + local Milvus on a 32 GB Windows host that is already memory-tight is the largest feasibility risk.
- Serena + Pyright against a library-layout Django tree may give weak cross-file navigation if the import root is wrong.
- OAuth cost fields may be missing; token logs must still be complete.
- Fairness: different default embedders (Jina code vs nomic-embed-text).
- Serena `search_for_pattern` overlaps the ripgrep variant; allowed by default, optional ablation later.
- 480 runs may exhaust the unpublished Grok Build pool.

## 15. Frozen artefact hashes

Computed with SHA-256 over the exact byte contents of the LF-normalized files in this directory at the freeze commit (see `SHA256SUMS`). The method cites these hashes:

See also [`SHA256SUMS`](SHA256SUMS).

- `questions.jsonl`: `cacde72bff37b8e5398dafb54caebed271700e1918dc837826de9ec081d18362`
- `answer_key.jsonl`: `560bbea52299695021cfa40d7505a33d1c2771bbb27c02575892eb8aa712e0a5`
- `pilot_questions.jsonl`: `0f8d4a3b7cbb2d15f935c51c91499a903dcaf7fb345d6108a80d9dc657dd9560`
- `grading.md`: `d6b4711613c563bd6c74434da4a1efa838421cbb7964932d3603d0c87eff2aa1`
- `self_check.md`: `27f4275c64af11b43c11b10022ca90b39a1a3b2f65804c140352b207fd8dad30`
- `django-commit.txt`: `2794732de0e848151346ef2e158a6b3ec5a3f185676c424d3d365e1ad121e15c`
- `repo_config.py`: `09993f6ba11091c5a0116e23478f3ee3b72c19dc8b86672aa699111bfd629d2d`
- `prompts/system.txt`: `a61c68c5706dd357b11940a92e85c5cbf1877745e05cb453cc2969fb55f77480`
- `prompts/answer.schema.json`: `ad7d3c046293651fd5c908df700e74c486a0963d2ca7a43aee081e8d760624cd`



## 16. Amendments after a method review (2026-11-14)

This section was added as a **new commit** after the Stage 1 freeze, following a method review. It supersedes the conflicting earlier wording below. **The hashed official artefacts in §15 are unchanged** (`questions.jsonl`, `answer_key.jsonl`, `pilot_questions.jsonl`, `grading.md`, `self_check.md`, `django-commit.txt`, `repo_config.py`, `prompts/system.txt`, `prompts/answer.schema.json`). Their SHA-256 values remain those in [`SHA256SUMS`](SHA256SUMS). Harness changes live in new or updated scripts and in this section.

### 16.1 Authorship (honest)

The official 40 questions and the Stage 1 pilot 10 were **written by the RAG agent working on hybrid-code-rag-mcp** (the same workstream as the author of HCR), as a designed retrieval set, not mined as-is from end users. The exact-lookup (E) items name identifiers on purpose. The semantic (S) items are **paraphrases of library behaviour**, worded so that a literal ripgrep of the question text should not uniquely identify the key (see [self_check.md](self_check.md)); they are not verbatim posts from Django users. Keys were checked against commit `f16e25dc` by `scripts/verify_keys.py`.

The external pool in §16.4 was also prepared by that same RAG workstream after this review, adapted from the cited public threads (natural wording plus a localisation ask). It is **not** independently annotated by a third party.

### 16.2 Fifth variant: `none` (control)

A fifth variant, `none`, is included and **reported separately as the no-retrieval control**. It is not folded into a four-way “winner” table.

**Pick, and why.** During a `none` run the agent has **no retrieval tools**: no `grep` / `rg`, no directory listing, no shell, no MCP server. It may answer from parametric memory with **zero tools**, or it may **`read_file` a path that it itself names**. We chose “read_file only” rather than “zero tools” so a model that already knows a path can open it, while still forbidding search. The same system prompt, step budget, model, and 180 s cap apply. The prompt already says “use only the tools that are available in this session,” so no variant-specific hint is added (the prompt file remains the frozen hash in §15).

`run_one.py` passes `--tools read_file` and extends `--disallowed-tools` to include `grep`, `run_terminal_cmd`, `Bash`, `Shell`, `list_dir`, and related search tools. Any retrieval call in a `none` log is a protocol violation (accuracy 0).

Compared variants remain `ripgrep`, `hcr`, `claude_context`, and `serena`. Official-table arithmetic after this amendment, once approved, is 40 × 5 × 3 = **600** graded runs (the Stage 1 figure of 480 is superseded). The current operator approval is still **pilot only**.

### 16.3 Interleaving and recorded seed

Preferred protocol: shuffle the Cartesian product of (question, variant, repetition) with a **recorded seed**. Default seed: `20261114` (the same integer as the self-check / planned audit seed). `scripts/schedule.py` writes the full order to a JSON file (pilot: `logs/pilot/schedule.json`).

If RAM or GPU exclusivity forces service blocks — in particular HCR (local TEI + Qdrant) versus claude-context (Ollama `nomic-embed-text` + Milvus) cannot reasonably stay up together on this 32 GB host without breaking the **4 GB free-RAM floor**, and swapping stacks per run would dominate the 180 s budget — use **blocked rotation** instead of a pure shuffle, and say so:

- The shuffle is computed first and **preserved inside each service block**.
- Blocks: `light` = `none`, `ripgrep`, `serena` (interleaved); `hcr`; `claude_context`.
- Block order rotates across repetitions: rep 1 `light → hcr → claude_context`; rep 2 `claude_context → hcr → light`; rep 3 `hcr → light → claude_context`.
- If a variant is skipped (for example Milvus blocked by RAM), that block is dropped and the remaining rotation is kept. The skip is recorded in the schedule file.

The 1-repetition pilot will almost certainly have to use `blocked_rotation` for this reason. That is a documented deviation from a full shuffle, not a silent one.

### 16.4 External question pool (prepared only; not used in the pilot)

A third, disjoint pool of **10** questions, IDs **X01–X10**, lives in [`external_questions.jsonl`](external_questions.jsonl) with a standalone key [`external_answer_key.jsonl`](external_answer_key.jsonl). Hashes are in [`EXTERNAL_SHA256SUMS`](EXTERNAL_SHA256SUMS) (its own file; **not** added to the official `SHA256SUMS`).

Each item has natural wording adapted from a public Django Forum thread, Stack Overflow question, or Trac ticket, and includes `sources` with URLs. Keys (file + symbol + 1-based spans) were verified at `f16e25dc`. Some topics overlap the official 40 (CSRF trusted origins, `CONN_MAX_AGE`, `ALLOWED_HOSTS`, trailing slash, `LOGIN_URL`, `make_aware`, hashed static files, `get_user_model`, `safe_join`); two items (`select_related` / `prefetch_related`, and the natural wording of the others) still stand as an externally sourced set, reported **separately** if ever run. **Do not use this pool in the Stage 2 pilot** and do not mix it into the official 40.

### 16.5 Metric name and bootstrap CIs

The accuracy metric is named **retrieval/localization accuracy** (still the deterministic 0 / 1 / 2 score in [grading.md](grading.md); that document is frozen and is not rewritten).

Reporting, implemented in [scripts/aggregate.py](scripts/aggregate.py):

- Per question, per variant: the repetition scores, mean, spread, and a **95% percentile bootstrap CI** over the repetitions.
- Per category **E / S / C** (exact_lookup / semantic / cross_file), per variant: the mean of that category’s per-question means, with a **95% percentile bootstrap CI** obtained by resampling those question means.
- **No single headline average** across all questions is reported as the result.
- Default bootstrap seed: `20261114`; default `n_boot=10000`. A stable per-cell offset is derived from the seed so intervals do not depend on print order.
- With a 1-repetition pilot, the per-question CI is **degenerate** (`n<2`, CI undefined). Category CIs can still be computed by resampling the  questions inside E / S / C (pilot mix: 4 exact, 3 semantic, 3 cross-file).
- `none` is printed in a separate control section.
- Wall time, tokens, and tool-call counts remain process metrics, not the accuracy headline.

### 16.6 claude-context configuration caveat

The `claude_context` pin in §6.3 (Ollama `nomic-embed-text` + **local Milvus standalone**, no cloud keys) is a **no-cost local stand-in**. It is **not** Claude Context’s recommended or default configuration, which typically uses a hosted embedder (OpenAI, Voyage, Gemini, or similar) and Zilliz Cloud. Any table that includes this variant must carry that note next to the table. This remains a product-default-vs-product-default comparison only in the limited sense of “each tool on a local path we can run without a new cloud account”; it is not a comparison against the vendor’s recommended hosted setup.

### 16.7 Host-process and WSL policy (pilot and later runs)

Do **not** close or kill the machine owner's applications to make room for Milvus or TEI. Do **not** edit the user's `~/.wslconfig` or otherwise change the WSL memory limit. If Milvus standalone cannot be started while leaving **≥ 4 GB** host RAM free, **do not start it**; run the other variants and report `claude_context` as **blocked by RAM**. The earlier §10 / §13 suggestion to close or cap processes is superseded by this rule.

### 16.8 Pilot scope after this amendment

Still **pilot only**: `pilot_questions.jsonl` (P01–P10). Variants: `none`, `ripgrep`, `hcr`, `claude_context` (if RAM allows), `serena`. Default **1 repetition** (50 runs if all five variants run; 40 if `claude_context` is skipped). Further repetitions only if time and RAM allow, and not so as to start the official 40 or the external pool. Official 40, the 600-run table, and X01–X10 are **not** started in Stage 2.

Launch still requires `--approved-by-operator`. An isolated `GROK_HOME` directory (`<bench-dir>/grok-home`) is created only after that approval. Raw pilot logs go to `logs/pilot/` (gitignored; keep them locally, do not force-add them to the public repo).

## 17. v2 pool, rubric, and prompt (2026-11-14, after the Stage 2 pilot)

This section is a **new commit**. It does not alter the hashed v1
artefacts in §15 (`questions.jsonl`, `answer_key.jsonl`,
`pilot_questions.jsonl`, `grading.md`, `self_check.md`,
`django-commit.txt`, `repo_config.py`, `prompts/system.txt`,
`prompts/answer.schema.json`). Those files and the Stage 2 pilot logs
under `logs/pilot/` stay as a historical record of the ceiling effect.

### 17.1 Why v2

The Stage 2 pilot (P01–P10 × `none`/`ripgrep`/`serena`/`hcr` × 1, seed
`20261114`) showed a ceiling: **`none` scored 9/10 at 2**. The control
already knew the well-known public APIs, so retrieval tools had little
room to differentiate. `claude_context` was set up (Milvus + local
Ollama `nomic-embed-text`) but indexing was interrupted when the
machine was freed for games, so that variant was not graded in the v1
pilot.

v2 therefore changes three things at once, in [`v2/`](v2/):

1. **A new 40-question official pool** (`v2/questions.jsonl`, keys in
   `v2/answer_key.jsonl`), mixed **10 exact / 15 semantic / 15
   cross-file** (E201–E210, S201–S215, C201–C215). Items target private
   helpers, specific constants, 6.0/6.1 machinery (tasks, CSP, template
   partials, fetch modes; plus the `RemovedInDjango2028Warning` shims in
   this tag), less obvious modules, and multi-hop behaviour described
   without names. A disjoint **pilot 10** (Q2P01–Q2P10) lives in
   `v2/pilot_questions.jsonl`. Hashes are in [`v2/SHA256SUMS`](v2/SHA256SUMS).
   Keys were verified with `scripts/verify_keys.py` against
   `f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`. See
   [`v2/self_check.md`](v2/self_check.md) for the memory spot-check.
2. **A stricter rubric** ([`v2/grading.md`](v2/grading.md)): a score of
   **2** requires the correct file(s) **and** symbol(s) **and** a line
   range within **±N lines, N = 10**, of each verified gold span. An
   answer without an exact location scores at most 1. The grader is
   `v2/scripts/grade_run.py`.
3. **A new system prompt** ([`v2/prompts/system_v2.txt`](v2/prompts/system_v2.txt))
   that requires the provided search/retrieval tool to be used before
   answering, forbids answering from memory, and requires `file:line`
   citations taken from tool results. For retrieval variants, a run
   with `tool_calls_retrieval == 0` is scored **0** after blind grading
   (`v2/scripts/apply_retrieval_gate.py`). The `none` control uses the
   same questions but
   [`v2/prompts/system_v2_none.txt`](v2/prompts/system_v2_none.txt),
   which allows parametric memory (and `read_file` of a path the model
   itself names) and is the reference for “how much the model knows by
   itself.”

### 17.2 Official v2 schedule

40 questions × 5 variants × 3 repetitions = **600** graded runs.
Recorded seed: **20261114**. Mode: **blocked_rotation** (the 4 GB
free-RAM floor and the exclusive HCR vs Milvus/Ollama stacks are
unchanged from §16.3).

```
python scripts/schedule.py --questions v2/questions.jsonl --variants none ripgrep hcr claude_context serena --repetitions 3 --seed 20261114 --mode blocked_rotation --out logs/v2/schedule.json
```

The `none` variant remains a separately reported control, not folded
into a four-way winner table. Metrics and bootstrap CIs follow §16.5,
using scores **after** the retrieval-tool gate.

A realistic wall-clock estimate, from the v1 pilot's per-run times
(typically ~1–2 minutes including tool use and the 180 s cap) plus
index and stack-swap overhead, is **14–20 hours** for the full 600,
plus 30–60 minutes the first time `claude_context` finishes indexing
this checkout. That does not fit in a single night after 23:35. Run
the v2 pilot first (50 runs if all five variants start, ~1.5–3 hours
including a first-time index), then start the official table and pause
at a block boundary.

### 17.3 Tonight (from 23:35 Europe/Warsaw)

The step-by-step command list, including `claude_context` indexing, RAM
and GPU rules, and stop/commit/release, is
[`v2/NIGHT_CHECKLIST.md`](v2/NIGHT_CHECKLIST.md). Do not start before
23:35 (after Brain's 22:00–23:30 window). Launch still requires
`--approved-by-operator`.

## 18. v2.1: pure-memory control, read-only control, harder items (2026-11-15)

The v2 pilot (14/15.11, `logs/v2-pilot/`) again put `none` at the
ceiling (10/10 at 2). Every `none` run named a path from memory and then
used `read_file` to copy the line numbers (Q2P07 probed eight paths). The
pilot also exposed a harness bug: MCP calls arrive as `use_tool` with the
real tool in `rawInput.tool_name`, and `run_one.py` classified them as
`other`, so the retrieval gate zeroed every hcr / claude_context / serena
run.

### 18.1 Controls

- **`none` = pure memory.** No tools at all. Grok gets
  `--tools read_file` (a non-empty allowlist, because an empty `--tools`
  may fail open) and `--disallowed-tools` that also lists `read_file`;
  the denylist wins. Prompt: `v2/prompts/system_v21_none.txt`. Any tool
  call is a `protocol_violation` and is scored 0.
- **`read_only`** (new) = the old `none`: `read_file` of a path the model
  names itself; no grep, directory listing, shell or MCP. Prompt:
  `v2/prompts/system_v21_read_only.txt`. A non-read call is a
  `protocol_violation` (scored 0).
- Both controls are reported separately (`aggregate.py` prints them under
  "Controls") and are not gated by the retrieval-tool rule. Retrieval
  variants keep `v2/prompts/system_v2.txt` and the gate in §17.

`schedule.py` puts `read_only` in the light block; `prep_variant_mcp.py`
attaches no MCP server for it; `run_pilot.py` takes
`--system-prompt-read-only`, `--stop-at HH:MM` and `--only-block`.

### 18.2 Tool-call classification fix

`use_tool` / `CallMcpTool` calls are classified by the inner tool after
stripping the `<server>__` prefix: `search_django` and `search_code` are
retrieval; claude-context `index_codebase` / `get_indexing_status` and
Serena `initial_instructions` are other. Serena 2.x exposes a single
`serena_repl` tool, so its calls are classified by the method in `code`
(`find_symbol`, `search_for_pattern`, `get_symbols_overview`, … =
retrieval; `read_file` = read; `info` = other). Tests:
`scripts/test_run_one.py`. Re-grading the v2 pilot with the fixed
classifier (`v2/scripts/reclassify_runs.py`, `v2/scripts/grade_night.py`)
zeroes exactly five runs: Q2P06/serena, Q2P07/ripgrep, Q2P08/hcr,
Q2P08/claude_context, Q2P09/ripgrep — the same five as the post-hoc
re-classification in `PILOT_SUMMARY.md` §B.

### 18.3 Harder items

New pilot pool `v2/pilot21_questions.jsonl` (Q3P01–Q3P10, 3 E / 4 S /
3 C). In the official 40, eleven guessable items were replaced (E201–E205,
E207, E208, S202, S207, S209, S215); ids and the 10/15/15 mix are
unchanged. Criteria: identifiers whose file is not implied by the name,
private helpers deep in large modules, behaviour described without
identifiers, and Django 6.1-only code. All keys were checked with
`scripts/verify_keys.py` against `f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`
and every new span equals the AST `lineno..end_lineno` of its symbol.
Details: `v2/self_check.md` §v2.1.

### 18.4 Schedule and gate

Pilot: 10 × 6 variants × 1 = 60 runs. Official: 40 × 6 × 1 = 240 runs
(repetitions 2–3 optional, same seed and block rotation). The pilot gate
(`v2/scripts/pilot_gate.py`) requires mean(`none`) ≤ 1.0, best retrieval
mean − mean(`none`) ≥ 0.5, ≤ 10% error/timeout runs, ≤ 1 control
violation, and no retrieval variant with > 30% of runs zeroed by the gate.
The night procedure is `v2/NIGHT_CHECKLIST.md`; the single entry point is
`v2/night/run_night_v21.ps1`. Official and pilot tables:
[results/official_table.md](results/official_table.md),
[results/pilot_table.md](results/pilot_table.md).
