#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Start the quickstart stack without editing compose or .env files.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ORIG_PWD="$PWD"

REPO=""
REF=""
REPO_CONFIG_FLAG=""
GPU=0
GPU_DEVICE_FLAG=""
PROJECT=""
DETACH=0
EXTRA=()

usage() {
    cat <<'USAGE'
Usage: ./start.sh [--repo <path|url>] [--ref <branch-or-tag-or-sha>]
                  [--repo-config <path>]
                  [--gpu] [--gpu-device <id>] [--project <name>] [--detach]
                  [--] [compose args...]

Starts the hybrid-code-rag-mcp quickstart.  --repo may be a local
directory or a git URL.  --ref is only used with a git URL.  --gpu adds
docker-compose.gpu.yml (NVIDIA driver + NVIDIA Container Toolkit required).

--repo-config <path> is an optional Python file with settings for the
indexed tree only (SOURCE_DIRS, MCP tool name and description, server
name).  The same value can go in REPO_CONFIG in .env or the
environment; a start parameter beats both.  The path is on the host and
is mounted read-only into the app container.  Without it, behaviour is
unchanged.  See repo_config.example.py.

--gpu-device <id> implies --gpu and pins TEI to that host GPU (0-based
nvidia-smi index, or a GPU-... UUID).  The same value can go in
GPU_DEVICE in .env or the environment.  When unset, CUDA_VISIBLE_DEVICES
is not set and TEI uses the first GPU.  Single-GPU machines do not need
this flag.

If no compose args are given, runs: docker compose up --build

--project NAME and --detach map to Compose's -p and -d.  They are
the preferred form; `./start.sh --gpu -- -p myshop up --build -d` also
works.  On PowerShell use -Project / -Detach (short -p / -d are reserved).


The same values can be passed without this wrapper:

  REPO_URL=https://github.com/org/repo.git docker compose up --build
  REPO_PATH=/path/to/repo docker compose up --build
  GPU_DEVICE=1 docker compose -f docker-compose.yml -f docker-compose.gpu.yml \
    -f docker-compose.gpu-device.yml up --build
  REPO_CONFIG=/path/to/repo_config.py docker compose -f docker-compose.yml \
    -f docker-compose.repo-config.yml up --build

PowerShell (same options and defaults):

  $env:REPO_URL="https://github.com/org/repo.git"; docker compose up --build
  .\start.ps1 -Repo <path|url> [-Ref X] [-RepoConfig <path>] [-Gpu] [-GpuDevice <id>] [-Project N] [-Detach]
USAGE
}

die() {
    echo "$1" >&2
    exit 1
}

require_value() {
    local flag="$1"
    local value="${2:-}"
    if [[ -z "$value" || "$value" == --* ]]; then
        die "error: $flag requires a value"
    fi
}

# Last assignment of KEY in FILE, if any.  Supports optional matching
# quotes; ignores blank lines and comments.  Strips a trailing CR so a
# Windows-edited .env still parses on Linux.
env_file_get() {
    local file="$1" key="$2" line value found=""
    [[ -f "$file" ]] || return 0
    while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%$'\r'}"
        line="${line#"${line%%[![:space:]]*}"}"
        [[ -n "$line" ]] || continue
        [[ "$line" == \#* ]] && continue
        [[ "$line" == "$key"=* ]] || continue
        value="${line#*=}"
        if [[ ${#value} -ge 2 ]]; then
            local first="${value:0:1}" last="${value: -1}"
            if [[ "$first" == "$last" && ( "$first" == '"' || "$first" == "'" ) ]]; then
                value="${value:1:${#value}-2}"
            fi
        fi
        found="$value"
    done < "$file"
    printf '%s' "$found"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)
            require_value "$1" "${2:-}"
            REPO="$2"
            shift 2
            ;;
        --repo-config)
            require_value "$1" "${2:-}"
            REPO_CONFIG_FLAG="$2"
            shift 2
            ;;
        --ref)
            require_value "$1" "${2:-}"
            REF="$2"
            shift 2
            ;;
        --gpu-device)
            require_value "$1" "${2:-}"
            GPU_DEVICE_FLAG="$2"
            GPU=1
            shift 2
            ;;
        --gpu)
            GPU=1
            shift
            ;;
        --project)
            require_value "$1" "${2:-}"
            PROJECT="$2"
            shift 2
            ;;
        --detach)
            DETACH=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            EXTRA+=("$@")
            break
            ;;
        *)
            EXTRA+=("$1")
            shift
            ;;
    esac
done

if [[ -n "$REPO" ]]; then
    if [[ "$REPO" == *://* || "$REPO" == git@* ]]; then
        export REPO_URL="$REPO"
        unset REPO_PATH || true
    else
        if [[ "$REPO" = /* ]]; then
            RESOLVED="$REPO"
        else
            RESOLVED="$ORIG_PWD/$REPO"
        fi
        if [[ ! -d "$RESOLVED" ]]; then
            echo "REPO_PATH does not exist or is not a directory: $REPO" >&2
            exit 1
        fi
        # Absolute path so Compose bind-mounts the right tree even when
        # the argument was relative to a different working directory.
        REPO_PATH="$(cd "$RESOLVED" && pwd)"
        export REPO_PATH
        unset REPO_URL || true
    fi
fi
if [[ -n "$REF" ]]; then
    export REPO_REF="$REF"
fi

# Flag wins, then the process environment, then .env next to this script.
# --repo-config is resolved against the caller's working directory;
# a relative path from .env is resolved against this script's directory.
if [[ -n "$REPO_CONFIG_FLAG" ]]; then
    REPO_CONFIG_RAW="$REPO_CONFIG_FLAG"
    REPO_CONFIG_BASE="$ORIG_PWD"
elif [[ -n "${REPO_CONFIG:-}" ]]; then
    REPO_CONFIG_RAW="$REPO_CONFIG"
    REPO_CONFIG_BASE="$ORIG_PWD"
else
    REPO_CONFIG_RAW="$(env_file_get "$SCRIPT_DIR/.env" "REPO_CONFIG")"
    REPO_CONFIG_BASE="$SCRIPT_DIR"
fi
if [[ -n "$REPO_CONFIG_RAW" ]]; then
    if [[ "$REPO_CONFIG_RAW" = /* ]]; then
        RESOLVED_CFG="$REPO_CONFIG_RAW"
    else
        RESOLVED_CFG="$REPO_CONFIG_BASE/$REPO_CONFIG_RAW"
    fi
    if [[ ! -f "$RESOLVED_CFG" ]]; then
        die "error: REPO_CONFIG does not exist or is not a file: $REPO_CONFIG_RAW"
    fi
    # Absolute path so Compose bind-mounts the right file even when
    # the argument was relative to a different working directory.
    REPO_CONFIG="$(cd "$(dirname "$RESOLVED_CFG")" && pwd)/$(basename "$RESOLVED_CFG")"
    export REPO_CONFIG
else
    unset REPO_CONFIG || true
fi


# Map nvidia-smi compute_cap to a TEI CUDA image tag.  TEI_CUDA_TAG, if
# already set in the environment or .env, is left alone (hidden override).
detect_tei_cuda_tag() {
    local idx="0" cap="" smi
    if [[ -n "${GPU_DEVICE:-}" ]]; then
        idx="$GPU_DEVICE"
    fi
    smi="$(command -v nvidia-smi || true)"
    if [[ -z "$smi" ]]; then
        smi="$(command -v nvidia-smi.exe || true)"
    fi
    if [[ -n "$smi" ]]; then
        cap="$("$smi" -i "$idx" --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n1 | tr -d '[:space:]')" || cap=""
    fi
    case "$cap" in
        8.9) TEI_CUDA_TAG="89-latest" ;;
        8.6) TEI_CUDA_TAG="86-1.6.0" ;;
        8.0) TEI_CUDA_TAG="80-latest" ;;
        7.5) TEI_CUDA_TAG="75-latest" ;;
        9.0) TEI_CUDA_TAG="90-latest" ;;
        *)   TEI_CUDA_TAG="latest" ;;
    esac
    if [[ -n "$cap" ]]; then
        echo "TEI CUDA image tag: $TEI_CUDA_TAG (compute cap $cap)"
    else
        echo "TEI CUDA image tag: $TEI_CUDA_TAG (compute cap unknown; generic CUDA tag)"
    fi
}

# Flag wins, then the process environment, then .env next to this script.
if [[ -n "$GPU_DEVICE_FLAG" ]]; then
    GPU_DEVICE="$GPU_DEVICE_FLAG"
elif [[ -z "${GPU_DEVICE:-}" ]]; then
    GPU_DEVICE="$(env_file_get "$SCRIPT_DIR/.env" "GPU_DEVICE")"
fi

# A pin only applies to the GPU stack.  --gpu-device already set GPU=1.
# A GPU_DEVICE in the environment or .env is used when --gpu is also set,
# and is ignored on the CPU path so a leftover pin cannot swap images.
if [[ "$GPU" -eq 1 && -n "${GPU_DEVICE:-}" ]]; then
    export GPU_DEVICE
else
    unset GPU_DEVICE || true
fi

# Hidden override: TEI_CUDA_TAG in the environment or .env wins; otherwise
# pick a tag from the selected GPU's compute cap (GPU_DEVICE, or GPU 0).
if [[ "$GPU" -eq 1 ]]; then
    if [[ -z "${TEI_CUDA_TAG:-}" ]]; then
        TEI_CUDA_TAG="$(env_file_get "$SCRIPT_DIR/.env" "TEI_CUDA_TAG")"
    fi
    if [[ -z "${TEI_CUDA_TAG:-}" ]]; then
        detect_tei_cuda_tag
    else
        echo "TEI CUDA image tag: $TEI_CUDA_TAG (override)"
    fi
    export TEI_CUDA_TAG
fi

cd "$SCRIPT_DIR"

files=(-f docker-compose.yml)
if [[ "$GPU" -eq 1 ]]; then
    files+=(-f docker-compose.gpu.yml)
    if [[ -n "${GPU_DEVICE:-}" ]]; then
        files+=(-f docker-compose.gpu-device.yml)
    fi
fi
if [[ -n "${REPO_CONFIG:-}" ]]; then
    files+=(-f docker-compose.repo-config.yml)
fi
if [[ ${#EXTRA[@]} -eq 0 ]]; then
    EXTRA=(up --build)
fi
if [[ -n "$PROJECT" ]]; then
    EXTRA=(-p "$PROJECT" "${EXTRA[@]}")
fi
if [[ "$DETACH" -eq 1 ]]; then
    has_d=0
    for a in "${EXTRA[@]}"; do
        if [[ "$a" == "-d" ]]; then has_d=1; break; fi
    done
    if [[ "$has_d" -eq 0 ]]; then
        EXTRA+=(-d)
    fi
fi
exec docker compose "${files[@]}" "${EXTRA[@]}"
