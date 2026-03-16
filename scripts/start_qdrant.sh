#!/usr/bin/env bash
# scripts/start_qdrant.sh
# Start Qdrant Docker container for a given config.
# Uses shared/docker_utils.py to ensure the container is running.
# Usage: scripts/start_qdrant.sh <config_name>
#   scripts/start_qdrant.sh config_informica
#   scripts/start_qdrant.sh self-index
#   scripts/start_qdrant.sh test-sources

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

CONFIG_NAME="${1:-}"
if [[ -z "$CONFIG_NAME" ]]; then
    echo "ERROR: Config name is required."
    echo "Usage: scripts/start_qdrant.sh <config_name>"
    echo "  scripts/start_qdrant.sh config_informica"
    echo "  scripts/start_qdrant.sh self-index"
    echo "  scripts/start_qdrant.sh test-sources"
    exit 1
fi

.venv/bin/python -W ignore -c \
    "import sys; sys.path.insert(0,'.'); sys.path.insert(0,'src'); \
     from config_loader import get_config; \
     from shared.docker_utils import ensure_qdrant_running; \
     c=get_config(config_path='$CONFIG_NAME'); ok=ensure_qdrant_running(c); exit(0 if ok else 1)"
