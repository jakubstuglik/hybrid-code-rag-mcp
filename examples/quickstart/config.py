# SPDX-License-Identifier: Apache-2.0
"""Project config for the Docker Compose quickstart.

Used by the `app` service in examples/quickstart/docker-compose.yml.
Qdrant and TEI are started by Compose, not by this process, so Docker
container management is turned off and the hostnames are the Compose
service names.

The tree to index is selected at start time, without editing this file:
the entrypoint sets HCR_SOURCE_ROOT from REPO_PATH, REPO_URL or the
bundled sample.  An optional repo-only file (HCR_REPO_CONFIG, mounted
from REPO_CONFIG / --repo-config / -RepoConfig) may narrow SOURCE_DIRS
and set MCP identity keys; infrastructure (including the collection) stays on the CPU or GPU
profile.  Batch and dtype settings come from the Compose CPU or GPU
profile (environment variables), with conservative CPU defaults.
"""

import os
from pathlib import Path

# Extensions the indexer knows how to parse (see README and QUICKSTART.md).
# A source path may contain a mix of these; unknown files are simply skipped.
# A repo config file may replace this list for the mounted tree.
_SOURCE_EXTENSIONS = [
    ".py", ".pyi",
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".mts", ".cts", ".tsx",
    ".java", ".kt", ".kts", ".groovy",
    ".cs", ".go", ".rs", ".php",
    ".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx", ".ino",
    ".pas", ".dpr", ".dfm", ".dproj",
    ".sql",
    ".ui", ".hbm.xml", ".jrxml", ".fr3",
    ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".bat",
    ".md", ".txt", ".json", ".jsonc", ".yml", ".yaml", ".toml",
    ".xml", ".xsd", ".wsdl", ".html", ".htm", ".jsp", ".css", ".scss",
    ".properties", ".gradle", ".http", ".ini", ".cfg",
]


def _env_str(name: str, default: str) -> str:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip()


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return int(raw)


# Set by examples/quickstart/entrypoint.sh after it resolves REPO_PATH,
# REPO_URL / REPO_REF, or the bundled sample.
_SOURCE_ROOT = _env_str("HCR_SOURCE_ROOT", "examples/quickstart/sample")

SOURCE_DIRS = [
    {
        "path": _SOURCE_ROOT,
        "extensions": list(_SOURCE_EXTENSIONS),
    },
]

# Persist manifests and any local cache on the `quickstart_index` volume.
BASE_PATH = "/data/index"
MODEL_PATH = "index_quickstart"

COLLECTION_NAME = "quickstart_rag"
QDRANT_MODE = "remote"
QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333

INDEX_EMBED_DEVICE = "cpu"
MCP_EMBED_DEVICE = "cpu"

# Dense model is the project default: jinaai/jina-embeddings-v2-base-code
# (161M parameters, 768 dimensions), served by the Compose TEI service.
USE_TEI = True
TEI_MANAGE_DOCKER = False
TEI_URL = "http://tei:80"
TEI_GPU = _env_str("TEI_GPU", "cpu")
TEI_DTYPE = _env_str("TEI_DTYPE", "float32")

# CPU-profile defaults fit about 8 GB of host RAM (float32, tiny batches,
# few concurrent TEI requests).  The GPU Compose override raises these
# via the environment (float16, larger batches, still aimed at 8 GB VRAM).
TEI_CONCURRENT_REQUESTS = _env_int("TEI_CONCURRENT_REQUESTS", 1)
TEI_REQUEST_TIMEOUT = 3600
DENSE_EMBED_BATCH_SIZE = _env_int("DENSE_EMBED_BATCH_SIZE", 1)
TEI_MAX_BATCH_TOKENS = _env_int("TEI_MAX_BATCH_TOKENS", 2048)
EMBED_BATCH_MAX_TOKENS = _env_int("EMBED_BATCH_MAX_TOKENS", 2048)
EMBED_POOL_SIZE = _env_int("EMBED_POOL_SIZE", 32)
EMBED_POOL_MAX_FILES = _env_int("EMBED_POOL_MAX_FILES", 8)
EMBED_PIPELINE_DEPTH = _env_int("EMBED_PIPELINE_DEPTH", 0)
TEI_TOKENIZATION_WORKERS = _env_int("TEI_TOKENIZATION_WORKERS", 2)

_source_name = Path(_SOURCE_ROOT).name or _SOURCE_ROOT
_is_sample = _env_str("HCR_SOURCE_KIND", "sample") == "sample"

MCP_SERVER_NAME = "quickstart-rag"
MCP_TOOL_NAME = "search_quickstart"
if _is_sample:
    MCP_TOOL_DESCRIPTION = (
        "Hybrid semantic + keyword search over the bundled ForgeCart sample "
        "project (a tiny shopping-cart library: cart, pricing, inventory, "
        "shipping retries, sessions and payments).\n\n"
        "USE WHEN: looking up how discounts, stock reservation, shipment "
        "retries, expired sessions or payments work in the sample.\n\n"
        "HOW TO QUERY: prefer symbols (calculate_discount, retry_shipment) "
        "or short English concepts (\"expired session\", \"idempotent refund\"). "
        "top_k 5–8 is enough on this small tree.\n\n"
        "RETURNS per hit: FILE, DISK_PATH, TYPE, LINES, chunk text."
    )
    MCP_INDEX_STATE_TOOL_DESCRIPTION = (
        "Report the state of the quickstart sample index: last index time, "
        "collection stats and embedder backend. No parameters."
    )
else:
    MCP_TOOL_DESCRIPTION = (
        f"Hybrid semantic + keyword search over the tree at {_source_name}.\n\n"
        "USE WHEN: looking up symbols or behaviour in this codebase.\n\n"
        "HOW TO QUERY: prefer identifiers or short English concepts. "
        "Paste quoted strings and names verbatim.\n\n"
        "RETURNS per hit: FILE, DISK_PATH, TYPE, LINES, chunk text."
    )
    MCP_INDEX_STATE_TOOL_DESCRIPTION = (
        f"Report the state of the index for {_source_name}: last index time, "
        "collection stats and embedder backend. No parameters."
    )
MCP_INDEX_STATE_TOOL_NAME = "get_quickstart_index_state"
MCP_PORT = 8125
MCP_HOST = "0.0.0.0"

# Optional repo-only overlay (SOURCE_DIRS and MCP identity keys).
# Loaded from HCR_REPO_CONFIG, which the repo-config Compose overlay sets
# to /config/repo_config.py when the user passed --repo-config / REPO_CONFIG.
def _apply_optional_repo_config() -> None:
    repo_config = _env_str("HCR_REPO_CONFIG", "")
    if not repo_config:
        return
    import importlib.util
    import sys

    loader_path = Path(__file__).resolve().with_name("load_repo_config.py")
    spec = importlib.util.spec_from_file_location(
        "quickstart_load_repo_config", loader_path
    )
    if spec is None or spec.loader is None:
        print(f"error: cannot load {loader_path}", file=sys.stderr)
        raise SystemExit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.apply_to_globals(globals(), repo_config, _SOURCE_ROOT)
    except module.RepoConfigError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from None


_apply_optional_repo_config()
