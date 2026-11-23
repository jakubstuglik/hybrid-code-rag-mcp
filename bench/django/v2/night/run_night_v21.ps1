<#
Django bench v2.1 - single night entry point (Windows PowerShell 5.1).

    $rb = Join-Path $PSScriptRoot 'run_night_v21.ps1'
    powershell -NoProfile -ExecutionPolicy Bypass -File $rb -Phase night      # preflight, smoke, pilot, gate, official
    powershell -NoProfile -ExecutionPolicy Bypass -File $rb -Phase pilot      # pilot only (60 runs) + gate
    powershell -NoProfile -ExecutionPolicy Bypass -File $rb -Phase official   # official 40 x 6 variants x Reps
    powershell -NoProfile -ExecutionPolicy Bypass -File $rb -Phase stop       # stop every bench service (safe to repeat)
    powershell -NoProfile -ExecutionPolicy Bypass -File $rb -Phase pilot -Variants loom -Reps 3 -Tag v21-pilot-loom   # Loom variant only

Phases: preflight | smoke | pilot | official | night | grade | stop | commit
Exit codes: 0 ok/GO | 10 pilot NOT_DISCRIMINATING | 20 HARNESS_FAIL | 30 preflight/smoke failed | 40 stop time reached
Logs: under $env:TEMP\hcr-night\v21\runbook.log by default (override with HCR_NIGHT_DIR); results in bench\django\logs\<Tag>.
Never touches unrelated host services, Docker Desktop, WSL, or other desktop applications. Never pushes.
Launch it detached (WMI) when driving the benchmark host over SSH, e.g.
    powershell -NoProfile -File (Join-Path $env:TEMP 'hcr-night\wmi.ps1') -File $rb -ArgStr '-Phase night'
#>
param(
  [ValidateSet('preflight','smoke','pilot','official','night','grade','stop','commit')]
  [string]$Phase = 'night',
  [string]$Tag = '',
  [int]$Reps = 1,
  [string]$StopAt = '06:40',
  [string[]]$SkipVariant = @(),
  [string]$Variants = 'none read_only ripgrep hcr claude_context serena'
)
$ErrorActionPreference = 'Continue'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$bench    = Join-Path $repoRoot 'bench\django'
$py       = if ($env:HCR_BENCH_PYTHON) { $env:HCR_BENCH_PYTHON } else { 'python' }
$T        = if ($env:HCR_NIGHT_DIR) { $env:HCR_NIGHT_DIR } else { Join-Path $env:TEMP 'hcr-night\v21' }
$benchRoot = if ($env:HCR_BENCH_ROOT) { $env:HCR_BENCH_ROOT } else { Join-Path $env:USERPROFILE 'hcr-bench' }
$checkout = if ($env:HCR_BENCH_DJANGO) { $env:HCR_BENCH_DJANGO } else { Join-Path $benchRoot 'django' }
$grokHome = if ($env:GROK_HOME) { $env:GROK_HOME } else { Join-Path $benchRoot 'grok-home' }
$sha      = 'f16e25dcb9fe55734ba4ea2b00ac34405b7df74a'
$quick    = Join-Path $repoRoot 'examples\quickstart'
$pilotDir = if ($env:HCR_PILOT_DIR) { $env:HCR_PILOT_DIR } else { Join-Path $env:TEMP 'hcr-pilot' }
New-Item -ItemType Directory -Force -Path $T | Out-Null
$runlog = Join-Path $T 'runbook.log'

function Log($m) { $l = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') + ' Europe/Warsaw  ' + $m; Add-Content $runlog $l -Encoding UTF8; Write-Host $l }
function FreeGB { [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2) }
function GpuCsv { (nvidia-smi --query-gpu=index,name,memory.used,memory.free --format=csv,noheader) -join ' | ' }
function PortUp([int]$port) { try { $t = New-Object Net.Sockets.TcpClient; $a = $t.BeginConnect('127.0.0.1', $port, $null, $null); $ok = $a.AsyncWaitHandle.WaitOne(1500, $false) -and $t.Connected; $t.Close(); $ok } catch { $false } }
function WaitPort([int]$port, [int]$sec) { $d = (Get-Date).AddSeconds($sec); while ((Get-Date) -lt $d) { if (PortUp $port) { return $true }; Start-Sleep 3 }; return $false }
function PastStop {
  $h, $m = $StopAt.Split(':') | ForEach-Object { [int]$_ }
  $now = Get-Date
  if ($now.Hour -ge 12 -and $h -lt 12) { return $false }
  return $now -ge (Get-Date -Hour $h -Minute $m -Second 0)
}
function KillByCmd([string]$like, [string]$what) {
  Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like $like } | ForEach-Object {
    Log "stop $what pid=$($_.ProcessId) $($_.Name)"; & taskkill /F /T /PID $_.ProcessId 2>&1 | Out-Null }
}
function Bench-Env {
  $env:GROK_HOME = $grokHome; $env:GROK_MEMORY = '0'; $env:GROK_DISABLE_AUTOUPDATER = '1'
  # Use the operator PATH as-is (python, node, and grok should already be on it).
}

# ---------- service blocks ----------
function Start-Light {
  if (-not (PortUp 9121)) {
    Log 'start serena ($(Join-Path $pilotDir 'start-serena-mcp.ps1'))'
    Start-Process powershell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File $(Join-Path $pilotDir 'start-serena-mcp.ps1')' -WindowStyle Hidden | Out-Null
  }
  $ok = WaitPort 9121 240
  Log "serena port 9121 up=$ok free=$(FreeGB)"
  return $ok
}
function Stop-Light { KillByCmd '*serena*start-mcp-server*' 'serena'; KillByCmd '*start-serena-mcp.ps1*' 'serena launcher' }
function Start-Hcr {
  Log "start HCR on 4060 ($(Join-Path $pilotDir 'start-hcr-gpu.ps1')) free=$(FreeGB)"
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pilotDir 'start-hcr-gpu.ps1') | Out-Null
  $rc = $LASTEXITCODE
  $ok = ($rc -eq 0) -and (PortUp 19130)
  if (-not $ok) {
    # start.ps1 sets EAP=Stop; under PS 5.1 a docker stderr line redirected by the wrapper becomes a terminating error,
    # so start-hcr-gpu.ps1 dies with rc=1 after compose has already started the stack. Accept the stack if it is really up.
    $d = (Get-Date).AddMinutes(10); $ready = $false
    while ((Get-Date) -lt $d) { $lg = (docker logs --since 15m hcr-django-bench-app-1 2>&1 | Out-String); if (($lg -match '\[MCP\] Index ready') -and (PortUp 19130)) { $ready = $true; break }; Start-Sleep 10 }
    if ($ready) { Log "WARN start-hcr-gpu rc=$rc but app says Index ready and MCP 19130 is up -> using the stack"; $ok = $true }
  }
  Log "HCR start rc=$rc mcp19130=$(PortUp 19130) gpu: $(GpuCsv)"
  return $ok
}
function Stop-Hcr { Log 'stop HCR stack'; KillByCmd '*hcr-gpu-watchdog*' 'hcr watchdog'; Push-Location $quick; docker compose -p hcr-django-bench stop 2>&1 | ForEach-Object { Log "  $_" }; Pop-Location }
function Start-CC {
  Log "start Milvus ($(Join-Path $pilotDir 'start-milvus.ps1')) free=$(FreeGB)"
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pilotDir 'start-milvus.ps1') | Out-Null
  if ($LASTEXITCODE -ne 0) { Log "Milvus start rc=$LASTEXITCODE -> claude_context BLOCKED"; return $false }
  # Not piped: ollama serve inherits the starter's stdout handle, so a pipeline here never sees EOF (hung 15.11 21:34).
  $sp = Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$bench\v2\night\start-ollama-4060.ps1`" -LogDir `"$T`"" -WindowStyle Hidden -PassThru
  $null = $sp.Handle
  if (-not $sp.WaitForExit(6 * 60 * 1000)) { Log "Ollama starter > 6 min -> claude_context BLOCKED"; & taskkill /F /T /PID $sp.Id | Out-Null; Stop-CC; return $false }
  $orc = $sp.ExitCode
  Get-Content (Join-Path $T 'ollama-start.log') -Tail 6 -EA SilentlyContinue | ForEach-Object { Log "  $_" }
  if ($orc -ne 0) { Log "Ollama 4060 start rc=$orc -> claude_context BLOCKED"; Stop-CC; return $false }
  # Index check: reuses the existing Milvus collection (force=False); only indexes if missing.
  Log "claude-context index check ($(Join-Path (Split-Path $T) 'idx.py'), force=False)"
  $p = Start-Process $py -ArgumentList '-u',(Join-Path (Split-Path $T) 'idx.py') -RedirectStandardOutput "$T\idx.out" -RedirectStandardError "$T\idx.err" -WindowStyle Hidden -PassThru
  if (-not $p.WaitForExit(45 * 60 * 1000)) { Log 'index check > 45 min, killing it -> claude_context BLOCKED'; & taskkill /F /T /PID $p.Id | Out-Null; KillByCmd '*claude-context-mcp*' 'claude-context'; Stop-CC; return $false }
  $done = Select-String -Path "$T\idx.out" -Pattern 'INDEX_DONE' -Quiet
  KillByCmd '*claude-context-mcp*' 'claude-context indexer'
  Log "index check exit=$($p.ExitCode) INDEX_DONE=$done free=$(FreeGB) gpu: $(GpuCsv)"
  if (-not $done) { Stop-CC; return $false }
  return $true
}
function Stop-CC {
  Log 'stop Ollama + Milvus + claude-context'
  $pidf = Join-Path $T 'ollama.pid'
  if (Test-Path $pidf) { & taskkill /F /T /PID (Get-Content $pidf) 2>&1 | Out-Null }
  Get-Process ollama* -EA SilentlyContinue | Where-Object { $_.Path -like (Join-Path $benchRoot 'ollama*') } | Stop-Process -Force -EA SilentlyContinue
  KillByCmd '*claude-context-mcp*' 'claude-context'
  docker compose -p hcr-bench-milvus -f (Join-Path $benchRoot 'milvus\docker-compose.yml') stop 2>&1 | ForEach-Object { Log "  $_" }
}
# Loom (ClickHouse Loom 1.3.0): docker compose project loom-pilot in $loomDir, MCP on 127.0.0.1:7777 only.
# The index lives in the stack's own storage, so Start-Loom only starts the existing stack and checks it.
$loomDir = if ($env:LOOM_PILOT_DIR) { $env:LOOM_PILOT_DIR } else { 'C:\Apps\loom-pilot\loom' }
function LoomReady {
  try { $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 'http://127.0.0.1:7777/v1/health/ready'; if ($r.StatusCode -ne 200) { return $false } } catch { return $false }
  try { $c = Invoke-RestMethod -TimeoutSec 20 -Method Post -ContentType 'application/json' -Body '{}' 'http://127.0.0.1:7777/v1/code.repos' } catch { return $false }
  $row = $c.repos | Where-Object { $_.namespace -eq 'code-django-bench' } | Select-Object -First 1
  return ($row -and $row.searchable -and $row.git_head -eq $sha)
}
function Start-Loom {
  if (-not (LoomReady)) {
    if (-not (Test-Path (Join-Path $loomDir 'compose.yaml'))) { Log "loom: $loomDir has no compose.yaml -> loom BLOCKED"; return $false }
    Log "start Loom (docker compose -p loom-pilot up -d in $loomDir) free=$(FreeGB)"
    Push-Location $loomDir; docker compose -p loom-pilot up -d --no-build --pull never clickhouse extractor loom 2>&1 | ForEach-Object { Log "  $_" }; Pop-Location
    $d = (Get-Date).AddMinutes(5); while ((Get-Date) -lt $d -and -not (LoomReady)) { Start-Sleep 5 }
  }
  $ok = LoomReady
  Log "Loom 7777 ready+code-django-bench@$($sha.Substring(0,8))=$ok free=$(FreeGB)"
  return $ok
}
# A1 hygiene (Jakub 23.11): before every loom group, empty the code.ask answer cache and the
# LLM response cache, drop memory rows outside the code namespace (probe leftovers), then
# audit that the memory planes hold nothing; after the group, audit again (a memory row
# then means a write got through). Counts go to the runbook log and $T\loom-hygiene.tsv.
$loomMemTables = @('memory','memory_embeddings','memory_versions','memory_chunks','memory_records',
  'working_memory','conversations','session_briefs','agent_runs')
function LoomCH($q) {
  $c = docker ps -q --filter label=com.docker.compose.project=loom-pilot --filter label=com.docker.compose.service=clickhouse
  if (-not $c) { return 'NO_CLICKHOUSE' }
  return ((docker exec $c clickhouse-client -q $q 2>&1) -join ' ')
}
function Loom-Hygiene([string]$when, [string]$label) {
  if ($when -eq 'pre') {
    LoomCH 'TRUNCATE TABLE loom.code_answers' | Out-Null
    LoomCH 'TRUNCATE TABLE loom.llm_response_cache' | Out-Null
    foreach ($tb in $loomMemTables) {
      LoomCH "DELETE FROM loom.$tb WHERE namespace != 'code-django-bench' SETTINGS mutations_sync = 2" | Out-Null
    }
  }
  $parts = @(); $mem = 0
  foreach ($tb in $loomMemTables + @('code_answers','llm_response_cache')) {
    $n = LoomCH "SELECT count() FROM loom.$tb WHERE namespace != 'code-django-bench'"
    if ($tb -in 'code_answers','llm_response_cache') { $n = LoomCH "SELECT count() FROM loom.$tb" }
    $parts += "$tb=$n"
    if ($tb -in $loomMemTables -and $tb -ne 'agent_runs' -and "$n" -ne '0') { $mem++ }
  }
  $verdict = if ($mem) { 'MEMORY_NOT_EMPTY' } else { 'memory_empty' }
  Log "loom hygiene $when $label ${verdict}: $($parts -join ' ')"
  Add-Content (Join-Path $T 'loom-hygiene.tsv') ("{0}`t{1}`t{2}`t{3}`t{4}" -f (Get-Date -Format s), $when, $label, $verdict, ($parts -join ' ')) -Encoding UTF8
  return (-not $mem)
}
function Stop-Loom {
  if (-not (Test-Path (Join-Path $loomDir 'compose.yaml'))) { return }
  Log 'stop Loom stack (compose stop, data kept)'; Push-Location $loomDir; docker compose -p loom-pilot stop 2>&1 | ForEach-Object { Log "  $_" }; Pop-Location
}
function Stop-All {
  KillByCmd "*grok*--cwd*hcr-bench\django*" 'bench grok'
  KillByCmd '*run_pilot.py*' 'run_pilot'
  Stop-Light; Stop-Hcr; Stop-CC; Stop-Loom
  Log "all bench services stopped. free=$(FreeGB) gpu: $(GpuCsv)"
  Log ("containers: " + ((docker ps --format '{{.Names}}') -join ', '))
}
function Start-Block($b) { switch ($b) { 'light' { Start-Light } 'hcr' { Start-Hcr } 'claude_context' { Start-CC } 'loom' { Start-Loom } default { $true } } }
function Stop-Block($b)  { switch ($b) { 'light' { Stop-Light } 'hcr' { Stop-Hcr } 'claude_context' { Stop-CC } 'loom' { Stop-Loom } } }
$blockOf = @{ none = 'light'; read_only = 'light'; ripgrep = 'light'; serena = 'light'; hcr = 'hcr'; claude_context = 'claude_context'; loom = 'loom' }

# ---------- phases ----------
function Preflight {
  Log "=== preflight free=$(FreeGB) gpu: $(GpuCsv)"
  $head = (& git -C $checkout rev-parse HEAD).Trim()
  Log "django HEAD=$head"
  if ($head -ne $sha) { Log 'FAIL: wrong Django commit'; return $false }
  Log ("bench repo: " + ((& git -C $repoRoot log --oneline -1) -join ''))
  Log ("bench branch: " + ((& git -C $repoRoot rev-parse --abbrev-ref HEAD) -join ''))
  $vm = [math]::Round(((Get-Process vmmemWSL -EA SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum) / 1MB, 0)
  Log "vmmemWSL=${vm}MB containers: $((docker ps --format '{{.Names}}') -join ', ')"
  foreach ($port in 9121, 19130, 19530, 11434, 7777) { if (PortUp $port) { Log "WARN port $port already in use (leftover bench service?)" } }
  if ((FreeGB) -lt 8) { Log 'FAIL: < 8 GB free RAM; the machine may still be in use'; return $false }
  Bench-Env
  & $py "$bench\scripts\test_run_one.py" 2>&1 | Select-Object -Last 3 | ForEach-Object { Log "  test_run_one: $_" }
  & $py "$bench\v2\scripts\test_grade_run.py" 2>&1 | Select-Object -Last 1 | ForEach-Object { Log "  test_grade_run: $_" }
  foreach ($q in 'v2\pilot21_questions.jsonl', 'v2\questions.jsonl') {
    $r = & $py "$bench\scripts\verify_keys.py" --repo $checkout --questions "$bench\$q" | Select-Object -Last 1
    Log "verify_keys $q -> $r"; if ($r -notmatch 'failures=0') { return $false }
  }
  return $true
}

function Smoke {
  # One pilot question for both controls: proves `none` really has zero tools and read_only still reads.
  Log '=== smoke (Q3P01 none + read_only)'
  Bench-Env
  $sd = Join-Path $T 'smoke'; New-Item -ItemType Directory -Force $sd | Out-Null
  & $py "$bench\scripts\prep_variant_mcp.py" --variant none --grok-home $grokHome --cwd $checkout | Out-Null
  $ok = $true
  foreach ($v in 'none', 'read_only') {
    $prompt = if ($v -eq 'none') { "$bench\v2\prompts\system_v21_none.txt" } else { "$bench\v2\prompts\system_v21_read_only.txt" }
    & $py "$bench\scripts\run_one.py" --questions "$bench\v2\pilot21_questions.jsonl" --id Q3P01 --variant $v --checkout $checkout --grok-home $grokHome --system-prompt $prompt --schema "$bench\v2\prompts\answer.schema.json" --out "$sd\Q3P01__$v.json" --raw-out "$sd\Q3P01__$v.raw.json" --approved-by-operator 2>&1 | Select-Object -Last 1 | ForEach-Object { Log "  $v -> $_" }
    $rec = Get-Content "$sd\Q3P01__$v.json" -Raw -EA SilentlyContinue | ConvertFrom-Json
    if (-not $rec) { Log "  FAIL ${v}: no record"; $ok = $false; continue }
    Log "  $v status=$($rec.status) tools=$($rec.tool_calls_total) files=$($rec.files_predicted -join ',')"
    if ($rec.status -notin 'ok', 'max_turns') { $ok = $false }
    if ($v -ne 'none' -and -not $rec.files_predicted -and $rec.tool_calls_total -eq 0) { $ok = $false }
    if ($v -eq 'none' -and $rec.tool_calls_total -ne 0) { $ok = $false }
  }
  if (-not $ok) { Log "SMOKE FAIL - see $sd (raw stderr shows whether grok refused an empty tool set)" }
  return $ok
}

function Run-Pool($tag, $questions, $key, $prefix, [int]$reps) {
  Bench-Env
  $logDir = Join-Path $bench "logs\$tag"
  New-Item -ItemType Directory -Force $logDir | Out-Null
  $sched = Join-Path $logDir "schedule-r$reps.json"
  # @(...): with one variant the pipeline yields a scalar string, and splatting a string (@vars)
  # passes its characters as separate arguments (23.11: -Variants loom became l o o m).
  $vars = @($Variants.Split(' ') | Where-Object { $_ -and ($SkipVariant -notcontains $_) })
  & $py "$bench\scripts\schedule.py" --questions "$bench\$questions" --variants @vars --repetitions $reps --seed 20261114 --mode blocked_rotation --out $sched | ForEach-Object { Log "  $_" }
  $groups = & $py "$bench\v2\scripts\schedule_groups.py" --schedule $sched --out-dir (Join-Path $logDir "groups-r$reps")
  Log "=== $tag start: $($groups.Count) groups, free=$(FreeGB)"
  $current = $null; $blocked = @{}; $stopped = $false
  foreach ($g in $groups) {
    $rep, $block, $n, $path = $g.Split(' ', 4)
    if (PastStop) { Log "stop time $StopAt reached before r$rep/$block"; $stopped = $true; break }
    if ($blocked[$block]) { Log "skip r$rep/$block (blocked earlier)"; continue }
    if ($current -and $current -ne $block) { Stop-Block $current; $current = $null }
    $waitUntil = (Get-Date).AddMinutes(10)
    while ((FreeGB) -lt 4.2 -and (Get-Date) -lt $waitUntil) { Log "RAM $(FreeGB) GB < 4.2, waiting"; Start-Sleep 30 }
    if ((FreeGB) -lt 4.0) { Log "RAM floor: skip r$rep/$block"; continue }
    if (-not $current) {
      if (-not (Start-Block $block)) {
        if ($block -eq 'light') {
          Log 'serena did not start: running the light block without serena'
          $path2 = $path -replace '\.json$', '-noserena.json'
          & $py -c "import json,sys;d=json.load(open(sys.argv[1],encoding='utf-8'));d['items']=[i for i in d['items'] if i['variant']!='serena'];d['n_runs']=len(d['items']);open(sys.argv[2],'w',encoding='utf-8').write(json.dumps(d,indent=2))" $path $path2
          $path = $path2
        } else { $blocked[$block] = $true; Log "BLOCKED $block (recorded; other blocks continue)"; continue }
      }
      $current = $block
    }
    if ($block -eq 'loom' -and -not (Loom-Hygiene 'pre' "$tag-r$rep")) { Log "loom: memory not empty after cleanup -> skip r$rep/loom"; continue }
    Log "run r$rep/$block n=$n free=$(FreeGB)"
    $out = Join-Path $T "$tag-r$rep-$block.out"
    & $py "$bench\scripts\run_pilot.py" --questions "$bench\$questions" --schedule $path --log-dir $logDir `
      --system-prompt "$bench\v2\prompts\system_v2.txt" --system-prompt-none "$bench\v2\prompts\system_v21_none.txt" `
      --system-prompt-read-only "$bench\v2\prompts\system_v21_read_only.txt" --schema "$bench\v2\prompts\answer.schema.json" `
      --checkout $checkout --timeout-s 180 --grok-home $grokHome --stop-at $StopAt --approved-by-operator *>> $out
    Log "done r$rep/$block exit=$LASTEXITCODE free=$(FreeGB) $(Select-String -Path $out -Pattern 'finished failures|stop-at' | Select-Object -Last 1)"
    if ($block -eq 'loom') { Loom-Hygiene 'post' "$tag-r$rep" | Out-Null }
  }
  if ($current) { Stop-Block $current }
  Grade $tag $key $prefix
  if ($stopped) { return 40 }
  return 0
}

function Grade($tag, $key, $prefix) {
  $logDir = Join-Path $bench "logs\$tag"
  & $py "$bench\v2\scripts\grade_night.py" --log-dir $logDir --key "$bench\$key" --prefix $prefix *> (Join-Path $T "$tag-grade.out")
  Log "graded $tag exit=$LASTEXITCODE -> $logDir\${prefix}_table.md"
}

function Gate($tag, $prefix) {
  $logDir = Join-Path $bench "logs\$tag"
  & $py "$bench\v2\scripts\pilot_gate.py" --log-dir $logDir --prefix $prefix --out "$logDir\${prefix}_verdict.json" | ForEach-Object { Log "  $_" }
  $rc = $LASTEXITCODE
  Log "pilot gate exit=$rc (0 GO, 10 NOT_DISCRIMINATING, 20 HARNESS_FAIL)"
  return $rc
}

$pilotTag = if ($Tag) { $Tag } else { 'v21-pilot' }
$offTag   = if ($Tag) { $Tag } else { 'v21' }
Log "##### run_night_v21 Phase=$Phase Tag=$Tag Reps=$Reps StopAt=$StopAt Skip=$($SkipVariant -join ',')"
$code = 0
try {
  switch ($Phase) {
    'preflight' { if (-not (Preflight)) { $code = 30 } }
    'smoke'     { if (-not (Smoke)) { $code = 30 } }
    'stop'      { Stop-All }
    'grade'     { Grade $pilotTag 'v2\pilot21_answer_key.jsonl' 'pilot'; $code = Gate $pilotTag 'pilot' }
    'pilot'     { $r = Run-Pool $pilotTag 'v2\pilot21_questions.jsonl' 'v2\pilot21_answer_key.jsonl' 'pilot' $Reps; $code = Gate $pilotTag 'pilot'; if ($r -eq 40) { $code = 40 } }
    'official'  { $code = Run-Pool $offTag 'v2\questions.jsonl' 'v2\answer_key.jsonl' 'official' $Reps }
    'night' {
      if (-not (Preflight)) { $code = 30; break }
      if (-not (Smoke)) { $code = 30; break }
      $r = Run-Pool $pilotTag 'v2\pilot21_questions.jsonl' 'v2\pilot21_answer_key.jsonl' 'pilot' 1
      $code = Gate $pilotTag 'pilot'
      if ($r -eq 40) { $code = 40; break }
      if ($code -eq 0) { $code = Run-Pool $offTag 'v2\questions.jsonl' 'v2\answer_key.jsonl' 'official' $Reps }
    }
    'commit' {
      Push-Location $repoRoot
      $results = 'bench/django/results'
      New-Item -ItemType Directory -Path $results -Force | Out-Null
      if (Test-Path 'bench/django/logs/v21/official_table.md') {
        Copy-Item 'bench/django/logs/v21/official_table.md' (Join-Path $results 'official_table.md') -Force
      }
      if (Test-Path 'bench/django/logs/v21-pilot/pilot_table.md') {
        Copy-Item 'bench/django/logs/v21-pilot/pilot_table.md' (Join-Path $results 'pilot_table.md') -Force
      }
      & git add -- $results
      & git commit -m "bench(django): v2.1 graded tables ($(Get-Date -Format 'yyyy-MM-dd'))" 2>&1 | ForEach-Object { Log "  $_" }
      Pop-Location
    }
  }
} finally {
  if ($Phase -in 'pilot', 'official', 'night') { Stop-All }
  Log "##### run_night_v21 Phase=$Phase exit=$code"
}
exit $code
