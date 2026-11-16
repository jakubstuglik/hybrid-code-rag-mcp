#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Resolve the source tree, index it (full rebuild if the source changed),
# then serve MCP.
set -euo pipefail
cd /app

# Fail fast on a bad repo config before waiting for Qdrant or TEI.
if [[ -n "${HCR_REPO_CONFIG:-}" ]]; then
    python examples/quickstart/load_repo_config.py --validate "$HCR_REPO_CONFIG"
fi

python examples/quickstart/wait_for.py "http://qdrant:6333/healthz" "Qdrant"
python examples/quickstart/wait_for.py "http://tei:80/health" "TEI"

# Command substitution (not process substitution) so a non-zero exit
# from resolve_repo.py trips set -e.  An empty or short result is also
# an error under set -u if we indexed blindly.
_resolve_out="$(python examples/quickstart/resolve_repo.py)"
mapfile -t _resolved <<< "$_resolve_out"
if [[ ${#_resolved[@]} -lt 2 ]]; then
    echo "resolve_repo.py did not print a source path and kind" >&2
    exit 1
fi
SOURCE_ROOT="${_resolved[0]}"
SOURCE_KIND="${_resolved[1]}"

# Default bind is ./sample:/data/repo. Treat that as the bundled sample
# unless the user explicitly set REPO_PATH or REPO_URL.
if [[ -z "${REPO_URL:-}" && -z "${REPO_PATH:-}" && "$SOURCE_KIND" == "path" ]]; then
    if [[ -d /app/examples/quickstart/sample ]]; then
        SOURCE_ROOT=/app/examples/quickstart/sample
        SOURCE_KIND=sample
    fi
fi

export HCR_SOURCE_ROOT="$SOURCE_ROOT"
export HCR_SOURCE_KIND="$SOURCE_KIND"
echo "Source tree: $SOURCE_ROOT (kind=$SOURCE_KIND)"

STAMP=/data/index/source_identity.txt
CONFIG_HASH=""
if [[ -n "${HCR_REPO_CONFIG:-}" ]]; then
    CONFIG_HASH="$(python examples/quickstart/load_repo_config.py --hash "$HCR_REPO_CONFIG")"
fi
# The config hash is part of the identity so a scope or tool-name change
# rebuilds the index with --clear, the same as a source change.
IDENTITY="${REPO_URL:-}|${REPO_PATH:-}|${REPO_REF:-}|${SOURCE_ROOT}|${CONFIG_HASH}"
CLEAR_ARGS=()
mkdir -p /data/index
if [[ -f "$STAMP" ]]; then
    if [[ "$(cat "$STAMP")" != "$IDENTITY" ]]; then
        echo "Source or repo config changed since the last index; rebuilding with --clear."
        CLEAR_ARGS=(--clear)
    fi
else
    # First run on a fresh volume: no --clear needed.
    :
fi

echo "Indexing (incremental if the index already matches this source)..."
python src/index_rag.py --config examples/quickstart --yes "${CLEAR_ARGS[@]+"${CLEAR_ARGS[@]}"}"
printf '%s' "$IDENTITY" > "$STAMP"

echo "Starting the MCP server on http://0.0.0.0:8125/mcp"
exec python src/rag_mcp.py --config examples/quickstart --transport streamable-http
