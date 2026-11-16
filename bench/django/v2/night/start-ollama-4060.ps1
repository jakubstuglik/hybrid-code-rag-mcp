# Start portable Ollama (nomic-embed-text for claude_context) pinned to the RTX 4060.
#
# Why: on 14/15.11 Ollama started with only CUDA_VISIBLE_DEVICES=0 still landed
# on the RTX 3060 (Vulkan backend ignores CUDA_VISIBLE_DEVICES; 3060 945 -> 1923 MiB).
# Fix: disable Vulkan, hide Vulkan devices, use PCI bus order and pin CUDA to the
# 4060 by GPU UUID (index-independent), then VERIFY from Ollama's own log and
# from nvidia-smi after a warm-up embed. On any doubt: stop this Ollama only and exit != 0.
#
# Exit codes: 0 ready on 4060 | 2 no 4060 found | 3 did not listen | 4 wrong GPU / Vulkan | 5 warm-up failed
param(
  [string]$LogDir = $(if ($env:HCR_NIGHT_DIR) { $env:HCR_NIGHT_DIR } else { Join-Path $env:TEMP 'hcr-night\v21' }),
  [string]$OllamaDir = $(if ($env:HCR_OLLAMA_DIR) { $env:HCR_OLLAMA_DIR } else { Join-Path $env:USERPROFILE 'hcr-bench\ollama' })
)
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$log = Join-Path $LogDir 'ollama-start.log'
$out = Join-Path $LogDir 'ollama.out'
$err = Join-Path $LogDir 'ollama.err'
$pidf = Join-Path $LogDir 'ollama.pid'
function Log($m) { $l = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') + ' Europe/Warsaw  ' + $m; Add-Content $log $l -Encoding UTF8; Write-Output $l }
function Gpu3060MiB { $r = nvidia-smi --query-gpu=name,memory.used --format=csv,noheader,nounits | Where-Object { $_ -match '3060' }; if ($r) { [int](($r -split ',')[1].Trim()) } else { 0 } }
function Listening { try { $t = New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1', 11434); $ok = $t.Connected; $t.Close(); $ok } catch { $false } }

if (Listening) { Log 'port 11434 already listening - refusing to start a second Ollama'; exit 3 }

$row = nvidia-smi --query-gpu=index,name,uuid,pci.bus_id --format=csv,noheader | Where-Object { $_ -match '4060' } | Select-Object -First 1
if (-not $row) { Log 'no RTX 4060 in nvidia-smi'; exit 2 }
$uuid = (($row -split ',')[2]).Trim()
Log "4060: $row"
$base3060 = Gpu3060MiB
Log "3060 baseline used=${base3060}MiB"

$env:OLLAMA_VULKAN = '0'            # Ollama >= 0.12: Vulkan backend off
$env:GGML_VK_VISIBLE_DEVICES = '-1' # hide all Vulkan devices from ggml
$env:CUDA_DEVICE_ORDER = 'PCI_BUS_ID'
$env:CUDA_VISIBLE_DEVICES = $uuid   # pin by UUID, not by index
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_MODELS = Join-Path $OllamaDir 'models'
$env:OLLAMA_KEEP_ALIVE = '30m'
$exe = Join-Path $OllamaDir 'ollama.exe'
if (-not (Test-Path $exe)) { $exe = (Get-Content 'C:\Temp\hcr-pilot\ollama.exe.path' -EA SilentlyContinue | Select-Object -First 1) }
$p = Start-Process -FilePath $exe -ArgumentList 'serve' -WorkingDirectory $OllamaDir -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
Set-Content $pidf $p.Id
Log "ollama serve pid=$($p.Id) CUDA_VISIBLE_DEVICES=$uuid OLLAMA_VULKAN=0"

$deadline = (Get-Date).AddMinutes(2)
while (-not (Listening) -and (Get-Date) -lt $deadline) { Start-Sleep 2 }
if (-not (Listening)) { Log 'not listening after 2 min'; Stop-Process -Id $p.Id -Force -EA SilentlyContinue; exit 3 }

function Fail($code, $why) { Log "FAIL: $why -> stopping this Ollama (pid $($p.Id)) only"; Stop-Process -Id $p.Id -Force -EA SilentlyContinue; Get-Process ollama* -EA SilentlyContinue | Where-Object { $_.Path -like "$OllamaDir*" } | Stop-Process -Force -EA SilentlyContinue; exit $code }

# Warm-up embed so the runner actually loads on a device.
try {
  $body = '{"model":"nomic-embed-text","input":"warm up"}'
  $r = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/embed' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 120
  Log "warm-up ok dims=$($r.embeddings[0].Count)"
} catch { Fail 5 "warm-up embed failed: $_" }
Start-Sleep 3

$errText = Get-Content $err -Raw -EA SilentlyContinue
$computeLines = ($errText -split "`n") | Where-Object { $_ -match 'inference compute|using device|ggml_vulkan|Vulkan0' }
$computeLines | ForEach-Object { Log "log: $($_.Trim())" }
if ($errText -match '3060') { Fail 4 'Ollama log mentions the RTX 3060' }
if ($errText -match 'ggml_vulkan: Found|library=Vulkan|Vulkan0') { Fail 4 'Vulkan backend active' }
if ($errText -notmatch '4060') { Fail 4 'Ollama log does not show the RTX 4060' }
$now3060 = Gpu3060MiB
Log "3060 used now=${now3060}MiB (baseline ${base3060})"
if (($now3060 - $base3060) -gt 200) { Fail 4 "3060 VRAM rose by $($now3060 - $base3060) MiB" }
Log 'READY on RTX 4060'
exit 0
