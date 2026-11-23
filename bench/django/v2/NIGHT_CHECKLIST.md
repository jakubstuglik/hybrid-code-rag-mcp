# v2.1 night checklist (Django bench)

One entry point does everything:
`bench/django/v2/night/run_night_v21.ps1` in this repository.
The night agent runs it, reads the verdict, and only steps in when it
returns a non-zero code. Work only in the clone of this repository on
`feature/django-bench`. **Never push.**

## Hard rules

- Start no earlier than the agreed slot (tonight: 22:00 Europe/Warsaw, or
  later if the machine owner is still using the host; give up at 01:00).
  The host is needed back at **07:30**: the runbook stops starting runs at
  `-StopAt 06:40`; all services must be down and the resource ledger
  RELEASED by **07:00**.
- Do not touch unrelated host services, Docker Desktop, WSL, or other
  desktop applications. No global Docker prune. If pulls must not use a
  logged-in registry, point `DOCKER_CONFIG` at an anonymous Docker config
  (the start scripts do this when that variable is set).
- Host free RAM floor **≥ 4 GB**. TEI and Ollama on the **RTX 4060 only**;
  the RTX 3060 must not gain more than ~200 MiB.
- Ledger: record STARTED and RELEASED lines in the operator's resource ledger.

## What changed in v2.1 (why `none` should drop)

1. `none` is now **pure memory**: no tools at all (read_file denied too;
   `--disallowed-tools` wins over `--tools`). In the v2 pilot every `none`
   run used `read_file` on a path it guessed from memory and read the line
   numbers off the file (Q2P07 probed 8 paths); with no file access it has
   to recall a line range within ±10 lines, which it cannot do reliably.
2. New control **`read_only`** (`read_file` only, no search) = the old
   `none`. Reported separately as a control; not a gate.
3. Harder questions: new pilot pool `pilot21_questions.jsonl` (Q3P01–Q3P10)
   and 11 replaced items in `questions.jsonl` (E201–E205, E207, E208, S202,
   S207, S209, S215): private helpers in files whose names do not give the
   location away, behaviour described without identifiers, and Django
   6.1-only code (mailers, UUID7, timing-attack helper). See
   `self_check.md` §v2.1.
4. Harness fix: MCP calls (`use_tool` → `<server>__<tool>`) are now
   classified by the inner tool; Serena `serena_repl` by the REPL method.
   The v2 pilot gate zeroed all hcr/claude_context/serena runs because of
   this; re-graded results are in `logs/v2-pilot/pilot_regrade_v21_table.md`.

## Commands (PowerShell on the benchmark host, or detached over SSH via WMI)

```
$rb = Join-Path <repo-dir> 'bench\django\v2\night\run_night_v21.ps1'
# 0. pull nothing, push nothing. Optional dry checks first:
powershell -NoProfile -ExecutionPolicy Bypass -File $rb -Phase preflight
# 1. whole night: preflight -> smoke -> pilot (60 runs) -> gate -> official 40 x 6 x 1
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $env:TEMP 'hcr-night\wmi.ps1') -File $rb -ArgStr '-Phase night -StopAt 06:40'
# follow progress
Get-Content (Join-Path $env:TEMP 'hcr-night\v21\runbook.log') -Tail 30
# after it exits (or at 06:40 at the latest)
powershell -NoProfile -ExecutionPolicy Bypass -File $rb -Phase stop
powershell -NoProfile -ExecutionPolicy Bypass -File $rb -Phase commit
```

The last line of `runbook.log` is `##### run_night_v21 Phase=... exit=N`.

| exit | meaning | what the night agent does |
|---|---|---|
| 0 | pilot GO and official finished (or `-Phase pilot` GO) | if before ~03:30, add repetitions: `-Phase official -Reps 3` (existing rep-1 runs are skipped; block order rotates) |
| 10 | pilot NOT_DISCRIMINATING (`none` > 1.0 or best retrieval − `none` < 0.5) | fix and re-run inside the slot (see below) |
| 20 | HARNESS_FAIL (>10% error/timeout, >1 control violation, or a retrieval variant with >30% gate zeros) | read `$env:TEMP\hcr-night\v21\*.out` and the raw logs, fix, re-run |
| 30 | preflight or smoke failed | see "Smoke failure" below |
| 40 | stop time reached | stop, grade what exists, commit, release |

Verdict and tables: `bench\django\logs\v21-pilot\pilot_verdict.json`,
`pilot_table.md`; official: `bench\django\logs\v21\official_table.md`.

## Rule: fix and re-run while time remains

If the pilot is not discriminating or the harness fails and it is still
before ~04:30, **do not stop**. Diagnose, fix, commit the fix locally, and
re-run with a fresh tag so earlier logs stay intact, e.g.
`-Phase pilot -Tag v21-pilot-b`, then `-Phase official` once the gate says
GO. Typical fixes:

- `none` still high: look at which questions it gets 2 on in
  `pilot_table.md`; replace those items (verify with `scripts\verify_keys.py`,
  update `v2\SHA256SUMS`) or tighten the ±N rule only after recording why.
- A retrieval variant zeroed by the gate: inspect `tool_calls` in its run
  JSON; extend `classify_mcp_call` in `scripts\run_one.py`, add a test in
  `scripts\test_run_one.py`, re-grade with `v2\scripts\reclassify_runs.py`
  + `-Phase grade` (no re-run needed for a pure classifier bug).
- Errors/timeouts in one block: check that block's stack (ports 9121
  serena, 19130 HCR, 19530 Milvus, 11434 Ollama) and re-run only it by
  re-invoking the same phase/tag (finished runs are skipped).

If a hcr src/ change were ever needed, report it; it is not expected.

## Smoke failure (exit 30)

The smoke step runs Q3P01 for `none` and `read_only` only. If `none`
fails because Grok refuses a session with every built-in tool denied
(see `$env:TEMP\hcr-night\v21\smoke\Q3P01__none.raw.json` stderr), do
**not** silently fall back to read_file. Options, in order: (a) keep
`--tools read_file` and add `--deny read_file` as a permission rule in
`run_one.py` for `none`; a refused call still counts as a protocol
violation, so check the smoke record shows 0 calls; (b) run tonight with
`-SkipVariant none` (read_only remains the control) and report it.

## Services (started and stopped by the runbook)

| block | start | stop |
|---|---|---|
| light (`none`, `read_only`, `ripgrep`, `serena`) | `<work-dir>/start-serena-mcp.ps1` (port 9121) | kill `serena start-mcp-server` |
| hcr | `<work-dir>/start-hcr-gpu.ps1` (GPU 0 = 4060, needs ≥ 6 GB free, MCP 19130; index reused) | `docker compose -p hcr-django-bench stop` |
| claude_context | `<work-dir>/start-milvus.ps1` (needs ≥ 12 GB free) + `v2/night/start-ollama-4060.ps1` + `<work-dir>/idx.py` (force=False; index from 15.11 reused) | Ollama pid, `docker compose -p hcr-bench-milvus stop`, claude-context node |

`start-ollama-4060.ps1` sets `OLLAMA_VULKAN=0`, `GGML_VK_VISIBLE_DEVICES=-1`,
`CUDA_DEVICE_ORDER=PCI_BUS_ID` and pins `CUDA_VISIBLE_DEVICES` to the 4060's
GPU UUID, then verifies from Ollama's log and nvidia-smi after a warm-up
embed. If it lands anywhere but the 4060 it stops that Ollama and the
runbook marks `claude_context` BLOCKED (other blocks continue).

## Duration estimates (from the v2 pilot, 14/15.11)

v2 pilot: 50 runs 23:42–00:21 (light 30 runs 11 min, hcr 10 runs 3 min,
claude_context 10 runs 5 min; mean per run: none 19 s, ripgrep 11 s,
hcr 16 s, claude_context 28 s, serena 36 s).

| step | runs | estimate |
|---|---|---|
| preflight + smoke | 2 | 3–5 min |
| v2.1 pilot (10 q × 6 variants) | 60 | 35–60 min incl. stack swaps |
| official 40 × 6 × 1 | 240 | 2–3.5 h |
| extra official reps 2–3 (optional) | +480 | 4–7 h, only partly fits |

Starting at 22:00, pilot + official rep 1 should be done by about 01:30–03:00,
leaving time for one fix-and-re-run cycle or additional repetitions until 06:40.

## Stop, commit, release

`-Phase stop` (idempotent), then `-Phase commit` (adds `logs\v21-pilot`
and `logs\v21`, commits locally, no push). Record free RAM, running
containers and both GPUs in the RELEASE line. Report to the user in the
morning with `official_table.md` (or the pilot table if the official run
did not start) and the verdict JSON.

## Loom variant (local branch, 23.11.2026)

- Stack: ClickHouse Loom 1.3.0, docker compose project `loom-pilot` in
  `C:\Apps\loom-pilot\loom`, MCP `http://127.0.0.1:7777/mcp?toolset=coding`
  (Grok server name `loom`, tools `loom__loom_code_*`). The index of `django/`
  at f16e25dc is already in the stack's storage; `Start-Loom` only starts the
  stack and checks `/v1/health/ready` plus `code.repos` (searchable, git_head).
- Run: `-Phase pilot -Variants loom -Reps 3 -Tag v21-pilot-loom` (own log dir;
  never reuse `v21-pilot`). Same system prompt and schema as hcr/serena.
- A1 (23.11): every Loom read tool is open; only loom_memory_set / _update /
  _delete and loom_working_memory_set are denied (`--deny MCPTool(loom__<tool>)`);
  a denied tool that ran, or `loom_op` with a write op, is a protocol violation
  (`run_one.LOOM_BANNED`, `LOOM_WRITE_OPS`). Before each loom group: truncate
  `loom.code_answers` + `loom.llm_response_cache`, clear memory rows, audit = 0;
  audit again after (`loom hygiene pre|post` in the runbook log).
- `pilot_gate.py` on a loom-only log dir has no `none` runs, so it reports
  NOT_DISCRIMINATING by design; compare against the v2.1 pilot table instead.
