# SPDX-License-Identifier: Apache-2.0
# Start the quickstart stack without editing compose or .env files.
# Same options and defaults as start.sh:
#   .\start.ps1 -Repo <path|url> [-Ref X] [-RepoConfig <path>] [-Gpu] [-GpuDevice <id>] [-- compose args...]
[CmdletBinding(PositionalBinding = $false)]
param(
    [string] $Repo = "",
    [string] $Ref = "",
    [string] $RepoConfig = "",
    [switch] $Gpu,
    [string] $GpuDevice = "",
    [string] $Project = "",
    [switch] $Detach,
    [switch] $Help,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ComposeArgs
)

$ErrorActionPreference = "Stop"
$callerCwd = (Get-Location).Path

# [CmdletBinding] keeps `.\start.ps1 up --build` from binding "up" as
# -Repo, but it also claims the short prefixes -p / -d / -v.  Those
# flags only reach Compose when they follow --.
if ($PSBoundParameters.ContainsKey('PipelineVariable')) {
    throw "PowerShell interpreted -p as -PipelineVariable. Put compose arguments after --, e.g. .\start.ps1 -Gpu -- -p myproj up --build -d"
}

function Show-Usage {
    @'
Usage: .\start.ps1 [-Repo <path|url>] [-Ref <branch-or-tag-or-sha>]
                   [-RepoConfig <path>]
                   [-Gpu] [-GpuDevice <id>] [-Project <name>] [-Detach]
                   [-- compose args...]

Starts the hybrid-code-rag-mcp quickstart.  -Repo may be a local
directory or a git URL.  -Ref is only used with a git URL.  -Gpu adds
docker-compose.gpu.yml (NVIDIA driver + NVIDIA Container Toolkit required).

-RepoConfig <path> is an optional Python file with settings for the
indexed tree only (SOURCE_DIRS, MCP tool name and description, server
name).  The same value can go in REPO_CONFIG in .env or the
environment; a start parameter beats both.  The path is on the host and
is mounted read-only into the app container.  Without it, behaviour is
unchanged.  See repo_config.example.py.

-GpuDevice <id> implies -Gpu and pins TEI to that host GPU (0-based
nvidia-smi index, or a GPU-... UUID).  The same value can go in
GPU_DEVICE in .env or the environment.  When unset, CUDA_VISIBLE_DEVICES
is not set and TEI uses the first GPU.  Single-GPU machines do not need
this parameter.

If no compose args are given, runs: docker compose up --build

Prefer -Project and -Detach instead of Compose's -p / -d.  Those short
flags are PowerShell common-parameter prefixes and are swallowed unless
they follow --.  Also, powershell.exe -File does not honour --; call
the script from a PowerShell prompt, or use -Project / -Detach:

  .\start.ps1 -Repo C:\path\to\repo -Project myshop -Detach
  .\start.ps1 -Repo C:\path\to\repo -- -p myshop up --build -d

The same values can be passed without this wrapper:

  $env:REPO_URL="https://github.com/org/repo.git"; docker compose up --build
  $env:REPO_PATH="C:\path\to\repo"; docker compose up --build
  $env:GPU_DEVICE="1"; docker compose -f docker-compose.yml -f docker-compose.gpu.yml `
    -f docker-compose.gpu-device.yml up --build
  $env:REPO_CONFIG="C:\path\to\repo_config.py"; docker compose -f docker-compose.yml `
    -f docker-compose.repo-config.yml up --build

Bash (same options and defaults):

  ./start.sh --repo <path|url> [--ref X] [--repo-config <path>] [--gpu] [--gpu-device <id>] [--project N] [--detach]
'@
}

if ($Help) {
    Show-Usage
    exit 0
}

function Get-EnvFileValue {
    param(
        [string] $Path,
        [string] $Key
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return ""
    }
    $found = ""
    foreach ($raw in Get-Content -LiteralPath $Path) {
        $line = $raw.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) {
            continue
        }
        $prefix = "$Key="
        if (-not $line.StartsWith($prefix)) {
            continue
        }
        $value = $line.Substring($prefix.Length)
        if ($value.Length -ge 2) {
            $first = $value[0]
            $last = $value[$value.Length - 1]
            if (($first -eq '"' -or $first -eq "'") -and $last -eq $first) {
                $value = $value.Substring(1, $value.Length - 2)
            }
        }
        $found = $value
    }
    return $found
}

function Get-TeiCudaTag {
    param([string] $GpuDevice)
    $idx = "0"
    if ($GpuDevice) { $idx = $GpuDevice }
    $cap = ""
    $smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if (-not $smi) { $smi = Get-Command nvidia-smi.exe -ErrorAction SilentlyContinue }
    if ($smi) {
        try {
            $raw = & $smi.Source -i $idx --query-gpu=compute_cap --format=csv,noheader 2>$null
            if ($raw) { $cap = ([string]$raw).Trim() }
        } catch { $cap = "" }
    }
    switch ($cap) {
        '8.9' { $tag = '89-latest' }
        '8.6' { $tag = '86-1.6.0' }
        '8.0' { $tag = '80-latest' }
        '7.5' { $tag = '75-latest' }
        '9.0' { $tag = '90-latest' }
        default { $tag = 'latest' }
    }
    # Return a single object so the tag is not mixed with host messages.
    [pscustomobject]@{ Tag = $tag; Cap = $cap }
}


if ($Repo) {
    if ($Repo -match "://" -or $Repo.StartsWith("git@")) {
        $env:REPO_URL = $Repo
        Remove-Item Env:REPO_PATH -ErrorAction SilentlyContinue
    }
    else {
        $resolved = $Repo
        if (-not [System.IO.Path]::IsPathRooted($Repo)) {
            $resolved = Join-Path $callerCwd $Repo
        }
        if (-not (Test-Path -LiteralPath $resolved -PathType Container)) {
            throw "REPO_PATH does not exist or is not a directory: $Repo"
        }
        $env:REPO_PATH = (Resolve-Path -LiteralPath $resolved).Path
        Remove-Item Env:REPO_URL -ErrorAction SilentlyContinue
    }
}
if ($Ref) {
    $env:REPO_REF = $Ref
}

# Flag wins, then the process environment, then .env next to this script.
# -RepoConfig is resolved against the caller's working directory;
# a relative path from .env is resolved against this script's directory.
if ($RepoConfig) {
    $repoConfigRaw = $RepoConfig
    $repoConfigBase = $callerCwd
}
elseif ($env:REPO_CONFIG) {
    $repoConfigRaw = $env:REPO_CONFIG
    $repoConfigBase = $callerCwd
}
else {
    $repoConfigRaw = Get-EnvFileValue -Path (Join-Path $PSScriptRoot ".env") -Key "REPO_CONFIG"
    $repoConfigBase = $PSScriptRoot
}
if ($repoConfigRaw) {
    $resolvedCfg = $repoConfigRaw
    if (-not [System.IO.Path]::IsPathRooted($repoConfigRaw)) {
        $resolvedCfg = Join-Path $repoConfigBase $repoConfigRaw
    }
    if (-not (Test-Path -LiteralPath $resolvedCfg -PathType Leaf)) {
        throw "REPO_CONFIG does not exist or is not a file: $repoConfigRaw"
    }
    $env:REPO_CONFIG = (Resolve-Path -LiteralPath $resolvedCfg).Path
}
else {
    Remove-Item Env:REPO_CONFIG -ErrorAction SilentlyContinue
}

# Flag wins, then the process environment, then .env next to this script.
if ($GpuDevice) {
    $env:GPU_DEVICE = $GpuDevice
    $Gpu = $true
}
elseif (-not $env:GPU_DEVICE) {
    $fromFile = Get-EnvFileValue -Path (Join-Path $PSScriptRoot ".env") -Key "GPU_DEVICE"
    if ($fromFile) {
        $env:GPU_DEVICE = $fromFile
    }
}

# A pin only applies to the GPU stack.  -GpuDevice already set $Gpu.
# A GPU_DEVICE in the environment or .env is used when -Gpu is also set,
# and is ignored on the CPU path so a leftover pin cannot swap images.
if (-not $Gpu) {
    Remove-Item Env:GPU_DEVICE -ErrorAction SilentlyContinue
}

# Hidden override: TEI_CUDA_TAG in the environment or .env wins; otherwise
# pick a tag from the selected GPU's compute cap (GPU_DEVICE, or GPU 0).
if ($Gpu) {
    if (-not $env:TEI_CUDA_TAG) {
        $fromFile = Get-EnvFileValue -Path (Join-Path $PSScriptRoot ".env") -Key "TEI_CUDA_TAG"
        if ($fromFile) { $env:TEI_CUDA_TAG = $fromFile }
    }
    if ($env:TEI_CUDA_TAG) {
        Write-Output "TEI CUDA image tag: $($env:TEI_CUDA_TAG) (override)"
    } else {
        $detected = Get-TeiCudaTag -GpuDevice $env:GPU_DEVICE
        $env:TEI_CUDA_TAG = $detected.Tag
        if ($detected.Cap) {
            Write-Output "TEI CUDA image tag: $($detected.Tag) (compute cap $($detected.Cap))"
        } else {
            Write-Output "TEI CUDA image tag: $($detected.Tag) (compute cap unknown; generic CUDA tag)"
        }
    }
}

Set-Location -LiteralPath $PSScriptRoot

$files = @("-f", "docker-compose.yml")
if ($Gpu) {
    $files += @("-f", "docker-compose.gpu.yml")
    if ($env:GPU_DEVICE) {
        $files += @("-f", "docker-compose.gpu-device.yml")
    }
}
if ($env:REPO_CONFIG) {
    $files += @("-f", "docker-compose.repo-config.yml")
}
if (-not $ComposeArgs -or $ComposeArgs.Count -eq 0) {
    $ComposeArgs = @("up", "--build")
}
if ($Project) {
    $ComposeArgs = @("-p", $Project) + @($ComposeArgs)
}
if ($Detach -and ($ComposeArgs -notcontains "-d")) {
    $ComposeArgs = @($ComposeArgs) + @("-d")
}

& docker compose @files @ComposeArgs
exit $LASTEXITCODE
