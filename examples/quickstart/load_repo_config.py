#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Load an optional repo-only config for the Docker Compose quickstart.

The file may set SOURCE_DIRS, MCP identity keys and MCP_INDEX_STATE_*.
Paths in SOURCE_DIRS are relative to the repository root
(HCR_SOURCE_ROOT).  Infrastructure keys (Qdrant, TEI, batch sizes,
dtype, ports, BASE_PATH, devices, COLLECTION_NAME) are rejected with a
clear error.

Used by examples/quickstart/config.py and by the Compose entrypoint.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Mapping, MutableMapping

# Keys the repo file is allowed to set.  MCP_INDEX_STATE_* is also
# accepted via the prefix rule below.
ALLOWED_KEYS = frozenset(
    {
        "SOURCE_DIRS",
        "MCP_SERVER_NAME",
        "MCP_TOOL_NAME",
        "MCP_TOOL_DESCRIPTION",
        "MCP_INDEX_STATE_TOOL_NAME",
        "MCP_INDEX_STATE_TOOL_DESCRIPTION",
    }
)
ALLOWED_PREFIXES = ("MCP_INDEX_STATE_",)

# Names that are clearly infrastructure / profile settings.  Listed so
# the error can say why they are refused, not only that they are unknown.
INFRASTRUCTURE_KEYS = frozenset(
    {
        "BASE_PATH",
        "MODEL_PATH",
        "COLLECTION_NAME",
        "QDRANT_MODE",
        "QDRANT_HOST",
        "QDRANT_PORT",
        "QDRANT_GRPC_PORT",
        "QDRANT_API_KEY",
        "QDRANT_HTTPS",
        "INDEX_EMBED_DEVICE",
        "MCP_EMBED_DEVICE",
        "USE_TEI",
        "TEI_MANAGE_DOCKER",
        "TEI_URL",
        "TEI_GPU",
        "TEI_DTYPE",
        "TEI_CONCURRENT_REQUESTS",
        "TEI_REQUEST_TIMEOUT",
        "TEI_MAX_BATCH_TOKENS",
        "TEI_TOKENIZATION_WORKERS",
        "DENSE_EMBED_BATCH_SIZE",
        "EMBED_BATCH_MAX_TOKENS",
        "EMBED_POOL_SIZE",
        "EMBED_POOL_MAX_FILES",
        "EMBED_PIPELINE_DEPTH",
        "MCP_PORT",
        "MCP_HOST",
        "MCP_TRANSPORT",
    }
)

_CONFIG_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")


class RepoConfigError(Exception):
    """User-facing error while reading a repo config file."""


def _is_allowed_key(name: str) -> bool:
    if name in ALLOWED_KEYS:
        return True
    return any(name.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def config_hash(path: str | Path) -> str:
    """Return the SHA-256 hex digest of the file contents."""
    data = Path(path).read_bytes()
    return hashlib.sha256(data).hexdigest()


def load_namespace(path: str | Path) -> dict[str, Any]:
    """Execute a repo config file and return its uppercase bindings."""
    config_path = Path(path)
    if not config_path.is_file():
        raise RepoConfigError(
            f"error: repo config file does not exist or is not a file: {path}"
        )
    try:
        source = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RepoConfigError(
            f"error: cannot read repo config {config_path}: {exc}"
        ) from exc
    try:
        code = compile(source, str(config_path), "exec")
        namespace: dict[str, Any] = {}
        exec(code, namespace)  # noqa: S102 — user-supplied local config
    except SyntaxError as exc:
        where = f"{exc.filename}:{exc.lineno}" if exc.filename else str(config_path)
        detail = exc.msg or "invalid syntax"
        raise RepoConfigError(
            f"error: syntax error in repo config {where}: {detail}"
        ) from None
    except RepoConfigError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface any import-time failure
        raise RepoConfigError(
            f"error: failed to load repo config {config_path}: {exc}"
        ) from None

    bindings = {
        key: value
        for key, value in namespace.items()
        if _CONFIG_NAME.match(key)
    }
    return bindings


def select_overrides(bindings: Mapping[str, Any], *, path: str | Path) -> dict[str, Any]:
    """Return allowed keys, or raise if the file sets anything else."""
    unknown: list[str] = []
    infrastructure: list[str] = []
    for key in bindings:
        if _is_allowed_key(key):
            continue
        if key in INFRASTRUCTURE_KEYS:
            infrastructure.append(key)
        else:
            unknown.append(key)
    if infrastructure or unknown:
        lines = [f"error: repo config {path} sets keys that are not allowed:"]
        if infrastructure:
            lines.append(
                "  infrastructure keys (these stay on the CPU/GPU Compose "
                "profile): " + ", ".join(sorted(infrastructure))
            )
        if unknown:
            allowed = ", ".join(sorted(ALLOWED_KEYS))
            lines.append("  unknown keys: " + ", ".join(sorted(unknown)))
            lines.append(
                "  allowed keys: "
                + allowed
                + ", and any MCP_INDEX_STATE_* setting"
            )
        raise RepoConfigError("\n".join(lines))
    return {key: bindings[key] for key in bindings if _is_allowed_key(key)}


def _resolve_under_root(raw: str, root: Path, *, location: str) -> str:
    root = root.resolve()
    candidate = Path(raw)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RepoConfigError(
            f"error: {location} path {raw!r} is outside the repository root {root}"
        ) from exc
    return str(resolved)


def resolve_source_dirs(source_dirs: Any, root: str | Path) -> list[dict[str, Any]]:
    """Rewrite SOURCE_DIRS paths so they are under the repository root.

    Top-level ``path`` values are relative to *root*.  Nested ``sources``
    paths on a ``git_repo`` entry stay relative to that repo path, as in a
    normal project config.
    """
    if not isinstance(source_dirs, list) or not source_dirs:
        raise RepoConfigError(
            "error: SOURCE_DIRS must be a non-empty list of source entries"
        )
    root_path = Path(root)
    resolved: list[dict[str, Any]] = []
    for idx, entry in enumerate(source_dirs):
        if not isinstance(entry, dict):
            raise RepoConfigError(
                f"error: SOURCE_DIRS[{idx}] must be a dict, got {type(entry).__name__}"
            )
        copy = dict(entry)
        raw = copy.get("path")
        if not isinstance(raw, str) or not raw.strip():
            raise RepoConfigError(
                f"error: SOURCE_DIRS[{idx}] is missing a 'path' string"
            )
        copy["path"] = _resolve_under_root(
            raw, root_path, location=f"SOURCE_DIRS[{idx}]"
        )
        resolved.append(copy)
    return resolved


def validate(path: str | Path) -> dict[str, Any]:
    """Load the file and check keys.  Paths are not resolved yet."""
    return select_overrides(load_namespace(path), path=path)


def apply_to_globals(
    target: MutableMapping[str, Any],
    path: str | Path,
    source_root: str | Path,
) -> dict[str, Any]:
    """Overlay allowed settings onto a config module's globals."""
    overrides = validate(path)
    if "SOURCE_DIRS" in overrides:
        overrides["SOURCE_DIRS"] = resolve_source_dirs(
            overrides["SOURCE_DIRS"], source_root
        )
    target.update(overrides)
    return overrides


def _print_error_and_exit(exc: RepoConfigError) -> int:
    print(str(exc), file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or hash a quickstart repo config file."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--validate",
        metavar="PATH",
        help="Load PATH and exit 0 if the file is a valid repo config.",
    )
    group.add_argument(
        "--hash",
        metavar="PATH",
        help="Print the SHA-256 digest of PATH to stdout.",
    )
    args = parser.parse_args(argv)
    try:
        if args.hash:
            hash_path = Path(args.hash)
            if not hash_path.is_file():
                raise RepoConfigError(
                    f"error: repo config file does not exist or is not a file: {args.hash}"
                )
            print(config_hash(hash_path), end="")
            return 0
        validate(args.validate)
        return 0
    except RepoConfigError as exc:
        return _print_error_and_exit(exc)


if __name__ == "__main__":
    sys.exit(main())
