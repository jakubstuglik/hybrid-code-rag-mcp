# Copyright (c) 2025-2026 hybrid-code-rag-mcp contributors
# SPDX-License-Identifier: MIT
"""Index state report for MCP agents.

**Hot path must stay trivial:** read one JSON file (the index manifest).
No repo walks, no embedding, no QdrantClient, no git subprocesses on the
default path. Live freshness is optional and fail-fast when enabled.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def get_manifest_dir(cfg: Any) -> Path:
    """Return the index directory that holds manifests and logs."""
    if hasattr(cfg, "get_index_path"):
        return Path(cfg.get_index_path()).resolve()
    base = getattr(cfg, "BASE_PATH", ".")
    model = getattr(cfg, "MODEL_PATH", "index")
    return (Path(base) / model).resolve()


def get_main_manifest_path(cfg: Any) -> Path:
    """Path to the main ``index_manifest.json``."""
    return get_manifest_dir(cfg) / "index_manifest.json"


def load_main_manifest(cfg: Any) -> Optional[dict]:
    """Load the main index manifest, or None if missing/invalid."""
    path = get_main_manifest_path(cfg)
    if not path.is_file():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def utc_iso_now() -> str:
    """UTC ISO timestamp for indexer bookkeeping."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _mtime_to_iso(mtime: float | None) -> str:
    if mtime is None:
        return "unknown"
    try:
        return (
            datetime.fromtimestamp(float(mtime), tz=timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
    except (OSError, OverflowError, ValueError):
        return "unknown"


def _short_sha(commit: str | None, n: int = 12) -> str:
    if not commit:
        return "unknown"
    return commit[:n] if len(commit) > n else commit


def fingerprint_files(files: dict) -> str:
    """Stable short fingerprint of path→content-hash pairs in the manifest."""
    if not files:
        return "empty"
    lines = []
    for key in sorted(files.keys()):
        entry = files[key]
        h = str(entry.get("hash") or "") if isinstance(entry, dict) else ""
        lines.append(f"{key}:{h}")
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:12]


def build_source_snapshots(manifest: dict, cfg: Any) -> dict:
    """Build ``source_snapshots`` from manifest files only (no disk walk of sources).

    Used by the indexer after refresh — not by the MCP hot path.
    """
    files = manifest.get("files") or {}
    if not isinstance(files, dict):
        files = {}
    now = utc_iso_now()
    snapshots: dict[str, Any] = {}

    repo_commits = manifest.get("repo_commits") or {}
    if isinstance(repo_commits, dict):
        for repo_key, rc in repo_commits.items():
            if not isinstance(rc, dict):
                continue
            # Count files cheaply from the in-memory files map only
            if len(repo_commits) == 1:
                matched = files
            else:
                matched = {
                    fk: fv
                    for fk, fv in files.items()
                    if str(fk).replace("\\", "/").startswith(repo_key + "/")
                    or str(fk).replace("\\", "/") == repo_key
                }
            mtimes = []
            for entry in matched.values():
                if isinstance(entry, dict) and entry.get("mtime") is not None:
                    try:
                        mtimes.append(float(entry["mtime"]))
                    except (TypeError, ValueError):
                        pass
            snapshots[repo_key] = {
                "type": "git_repo",
                "main_branch": rc.get("main_branch"),
                "commit": rc.get("commit"),
                "file_count": len(matched),
                "latest_mtime": max(mtimes) if mtimes else None,
                "fingerprint": _short_sha(rc.get("commit")),
                "indexed_at": rc.get("indexed_at") or now,
            }

    # Non-git: only if source_snapshots already empty and SOURCE_DIRS has non-git
    # entries — still NO filesystem walk of the source tree, only manifest keys.
    try:
        from config_loader import resolve_source_entries
        from shared.manifest import make_repo_key

        for entry in resolve_source_entries(cfg) or []:
            if entry.get("_entry_type") == "git_repo":
                continue
            path = entry.get("path") or ""
            key = make_repo_key(path) if path else "source"
            if key in snapshots:
                continue
            prefix = path.replace("\\", "/").rstrip("/")
            if prefix and prefix != ".":
                matched = {
                    fk: fv
                    for fk, fv in files.items()
                    if str(fk).replace("\\", "/") == prefix
                    or str(fk).replace("\\", "/").startswith(prefix + "/")
                }
            else:
                matched = dict(files)
            mtimes = []
            for e in matched.values():
                if isinstance(e, dict) and e.get("mtime") is not None:
                    try:
                        mtimes.append(float(e["mtime"]))
                    except (TypeError, ValueError):
                        pass
            snapshots[key] = {
                "type": "directory",
                "path": path,
                "file_count": len(matched),
                "latest_mtime": max(mtimes) if mtimes else None,
                "fingerprint": fingerprint_files(matched),
                "indexed_at": now,
            }
    except Exception:
        pass

    return snapshots


def list_branch_overlays(cfg: Any) -> list[dict]:
    """Load branch overlay manifests from the index dir only (few small JSON files)."""
    index_dir = get_manifest_dir(cfg)
    results: list[dict] = []
    if not index_dir.is_dir():
        return results
    for path in sorted(index_dir.glob("index_manifest_branch_*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        files = data.get("files") or {}
        results.append(
            {
                "branch": data.get("branch")
                or path.stem.replace("index_manifest_branch_", ""),
                "last_branch_commit": data.get("last_branch_commit"),
                "merge_base": data.get("merge_base"),
                "file_count": len(files) if isinstance(files, dict) else 0,
                "indexed_at": data.get("indexed_at"),
                "path": str(path),
            }
        )
    return results


def build_index_state_report(
    cfg: Any,
    client: Any | None = None,  # kept for API compat; ignored
    *,
    check_live_git: bool = False,
) -> str:
    """Compact markdown of what the index is serving.

    Default path (``check_live_git=False``):
      1. Read ``index_manifest.json`` once
      2. Optionally list a handful of branch-manifest JSON files in the same dir
      3. Done — no source-tree scan, no git, no Qdrant, no network

    That is intentional: agents need indexed commit + timestamps, which are
    already stored at index time. Live freshness is optional.
    """
    del client  # unused; do not open Qdrant here

    server = getattr(cfg, "MCP_SERVER_NAME", "rag-server")
    collection = getattr(cfg, "COLLECTION_NAME", "unknown")
    host = getattr(cfg, "QDRANT_HOST", "localhost")
    port = getattr(cfg, "QDRANT_PORT", "?")

    lines: list[str] = [
        f"# Index state — {server}",
        "",
        f"- collection: {collection} @ {host}:{port}",
    ]

    manifest_path = get_main_manifest_path(cfg)
    manifest = load_main_manifest(cfg)

    if manifest is None:
        lines.append(
            f"- last_index_completed_at: unknown (no manifest at {manifest_path})"
        )
        lines.append("- indexed_files: 0")
        lines.append("")
        lines.append(
            "No index manifest found. Run the indexer for this config before searching."
        )
        return "\n".join(lines) + "\n"

    files = manifest.get("files") or {}
    if not isinstance(files, dict):
        files = {}
    file_count = len(files)

    index_run = manifest.get("index_run") if isinstance(manifest.get("index_run"), dict) else {}
    completed = index_run.get("completed_at") if index_run else None
    backend = index_run.get("embed_backend") if index_run else None
    if not completed:
        try:
            completed = _mtime_to_iso(manifest_path.stat().st_mtime) + " (manifest mtime)"
        except OSError:
            completed = "unknown"

    lines.append(f"- last_index_completed_at: {completed}")
    lines.append(f"- indexed_files: {file_count}")
    if backend:
        lines.append(f"- embed_backend: {backend}")
    # points_count is NOT required for "what commit is indexed" — skip Qdrant
    lines.append("")

    lines.append("## Sources")
    repo_commits = manifest.get("repo_commits") or {}
    if not isinstance(repo_commits, dict):
        repo_commits = {}

    # Overlays: only small JSON files next to the main manifest
    overlays = list_branch_overlays(cfg)
    if overlays:
        bits = [
            f"{ov.get('branch')}@{_short_sha(ov.get('last_branch_commit'), 7)} "
            f"({ov.get('file_count') or 0} files)"
            for ov in overlays
        ]
        overlays_line = ", ".join(bits)
    else:
        overlays_line = "none"

    if repo_commits:
        first = True
        for repo_key, rc in sorted(repo_commits.items()):
            if not isinstance(rc, dict):
                continue
            lines.append(f"### git: {repo_key}")
            lines.append(f"- main_branch: {rc.get('main_branch') or 'unknown'}")
            commit = rc.get("commit")
            lines.append(f"- indexed_commit: {commit or 'unknown'}")
            if rc.get("indexed_at"):
                lines.append(f"- indexed_at: {rc['indexed_at']}")
            if check_live_git and commit:
                # Fail-fast optional path only when explicitly requested
                live, match = _git_freshness_fast(
                    ".", rc.get("main_branch") or "master", commit
                )
                lines.append(f"- live_commit: {live} | matches_indexed: {match}")
            if first:
                lines.append(f"- overlays: {overlays_line}")
                first = False
            lines.append("")
    else:
        lines.append("### git: (none in manifest)")
        lines.append("- no repo_commits yet")
        lines.append(f"- overlays: {overlays_line}")
        lines.append("")

    # Directory snapshots already stored at index time (no live mtime scan)
    snapshots = manifest.get("source_snapshots") or {}
    if isinstance(snapshots, dict):
        for key, snap in sorted(snapshots.items()):
            if not isinstance(snap, dict) or snap.get("type") == "git_repo":
                continue
            n = snap.get("file_count", 0)
            fp = snap.get("fingerprint") or "unknown"
            latest = _mtime_to_iso(snap.get("latest_mtime"))
            lines.append(f"### dir: {key}")
            lines.append(f"- files: {n} | latest_mtime: {latest} | fingerprint: {fp}")
            lines.append("")

    lines.append(
        "Note: reflects last successful index/refresh only — not uncommitted edits."
    )
    return "\n".join(lines).rstrip() + "\n"


def _git_freshness_fast(
    repo_path: str, main_branch: str, indexed_commit: str
) -> tuple[str, str]:
    """Optional live check; 1s timeout, never used on default MCP path."""
    try:
        from shared.git_ops import GitError, _run_git

        repo = str(Path(repo_path).resolve())
        live = _run_git(
            ["rev-parse", "--verify", main_branch], repo, timeout=1
        ).stdout.strip()
        return (live, "yes" if live == indexed_commit else "no")
    except Exception as exc:
        return (f"unavailable ({exc})", "unknown")
