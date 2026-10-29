# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0
"""Index state report for MCP agents.

**Hot path must stay trivial:** render a small state document. A
serving-only MCP server reads it from Qdrant (``shared.index_meta``); on the
indexer host, or for collections published before index state existed, it
is built from the local manifest files. No repo walks, no embedding, no git
subprocesses on the default path. Live freshness is optional and fail-fast
when enabled.
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
    from shared.manifest_saver import read_json_file

    path = get_main_manifest_path(cfg)
    if not path.is_file():
        return None
    try:
        data = read_json_file(path)
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
    """Load overlay manifests (branch and tag) from the index dir only (few small JSON files)."""
    from shared.manifest_saver import read_json_file
    from shared.overlay import overlay_kind_from_manifest

    index_dir = get_manifest_dir(cfg)
    results: list[dict] = []
    if not index_dir.is_dir():
        return results
    for path in sorted(index_dir.glob("index_manifest_branch_*.json")):
        try:
            data = read_json_file(path)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        files = data.get("files") or {}
        kind = overlay_kind_from_manifest(data)
        results.append(
            {
                "branch": data.get("branch")
                or path.stem.replace("index_manifest_branch_", ""),
                "kind": kind,
                # Tag manifests keep the peeled tag commit; branch manifests the head.
                "commit": data.get("last_resolved_commit")
                if kind == "tag"
                else data.get("last_branch_commit"),
                "last_branch_commit": data.get("last_branch_commit"),
                "merge_base": data.get("merge_base"),
                "file_count": len(files) if isinstance(files, dict) else 0,
                "indexed_at": data.get("indexed_at"),
                "path": str(path),
            }
        )
    return results


def _overlay_summary(label: str, data: dict) -> dict:
    """Compact overlay entry of the state document (no files, no tombstones).

    ``tombstone_parts``, ``tombstones_sha256`` and ``tombstone_per_point``
    are not copied from the manifest. ``publish_index_state`` fills them
    on the stored document. The report projection keeps ``tombstone_count``.
    """
    from shared.overlay import overlay_kind_from_manifest

    files = data.get("files") or {}
    return {
        "branch": data.get("branch") or label,
        "kind": overlay_kind_from_manifest(data),
        "merge_base": data.get("merge_base"),
        "last_branch_commit": data.get("last_branch_commit"),
        "last_resolved_commit": data.get("last_resolved_commit"),
        "overlay_signature": data.get("overlay_signature"),
        "indexed_at": data.get("indexed_at"),
        "file_count": len(files) if isinstance(files, dict) else 0,
        "tombstone_count": len(data.get("tombstones") or []),
    }


def load_overlay_manifests(cfg: Any) -> dict[str, dict]:
    """``{overlay label: overlay manifest}`` from the index dir (indexer side)."""
    from shared.manifest_saver import read_json_file

    index_dir = get_manifest_dir(cfg)
    out: dict[str, dict] = {}
    if not index_dir.is_dir():
        return out
    for path in sorted(index_dir.glob("index_manifest_branch_*.json")):
        try:
            data = read_json_file(path)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        label = data.get("branch") or path.stem.replace("index_manifest_branch_", "")
        out[label] = data
    return out


def build_state_document(
    manifest: dict, overlays: dict[str, dict], collection: str | None = None
) -> dict:
    """Index state document from the main manifest and the overlay manifests.

    This is what the indexer publishes into Qdrant (``shared.index_meta``)
    and what ``build_index_state_report`` renders. It never contains the
    per-file entries, only their count.
    """
    files = manifest.get("files") or {}
    doc: dict[str, Any] = {
        "collection": collection,
        "published_at": utc_iso_now(),
        "indexed_files": len(files) if isinstance(files, dict) else 0,
        "index_run": manifest.get("index_run") if isinstance(manifest.get("index_run"), dict) else {},
        "indexer_version": manifest.get("indexer_version"),
        "first_indexer_version": manifest.get("first_indexer_version"),
        "repo_commits": manifest.get("repo_commits")
        if isinstance(manifest.get("repo_commits"), dict)
        else {},
        "source_snapshots": manifest.get("source_snapshots")
        if isinstance(manifest.get("source_snapshots"), dict)
        else {},
        "overlays": {label: _overlay_summary(label, data) for label, data in overlays.items()},
    }
    return doc


def load_local_state(cfg: Any) -> Optional[dict]:
    """State document built from the local manifest files, None without manifest."""
    manifest = load_main_manifest(cfg)
    if manifest is None:
        return None
    return build_state_document(
        manifest, load_overlay_manifests(cfg), getattr(cfg, "COLLECTION_NAME", None)
    )


def _overlays_from_state(doc: dict) -> list[dict]:
    out = []
    for label, ov in sorted((doc.get("overlays") or {}).items()):
        if not isinstance(ov, dict):
            continue
        kind = ov.get("kind") or "branch"
        out.append(
            {
                "branch": ov.get("branch") or label,
                "kind": kind,
                "commit": ov.get("last_resolved_commit")
                if kind == "tag"
                else ov.get("last_branch_commit"),
                "file_count": ov.get("file_count") or 0,
                # tombstone_parts, tombstones_sha256 and tombstone_per_point
                # stay on the stored document; the report uses the count.
                "tombstone_count": ov.get("tombstone_count") or 0,
            }
        )
    return out


def build_index_state_report(
    cfg: Any,
    client: Any | None = None,  # kept for API compat; ignored
    *,
    check_live_git: bool = False,
    state: Optional[dict] = None,
    state_source: Optional[str] = None,
    provenance_lines: Optional[list[str]] = None,
) -> str:
    """Compact markdown of what the index is serving.

    With *state* (a state document read from Qdrant, see
    ``shared.index_meta``) no file is read: this is the path of a
    serving-only MCP server. Without it the local manifest files are used
    (indexer host, or collections published before index state existed):
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
    completed_fallback = None
    if state is None:
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
        state = build_state_document(manifest, {}, collection)
        overlays = list_branch_overlays(cfg)
        try:
            completed_fallback = (
                _mtime_to_iso(manifest_path.stat().st_mtime) + " (manifest mtime)"
            )
        except OSError:
            completed_fallback = "unknown"
    else:
        overlays = _overlays_from_state(state)

    if state_source:
        lines.append(f"- state_source: {state_source}")
    file_count = int(state.get("indexed_files") or 0)
    index_run = state.get("index_run") if isinstance(state.get("index_run"), dict) else {}
    completed = index_run.get("completed_at") if index_run else None
    backend = index_run.get("embed_backend") if index_run else None
    if not completed:
        completed = completed_fallback or "unknown"

    lines.append(f"- last_index_completed_at: {completed}")
    lines.append(f"- indexed_files: {file_count}")
    if backend:
        lines.append(f"- embed_backend: {backend}")
    from shared.version import manifest_version_line

    lines.append(manifest_version_line(state))
    # points_count is NOT required for "what commit is indexed" — skip Qdrant
    lines.append("")

    if provenance_lines:
        lines.append("## Embedding provenance")
        lines.extend(f"- {line}" for line in provenance_lines)
        lines.append("")

    lines.append("## Sources")
    repo_commits = state.get("repo_commits") or {}
    if not isinstance(repo_commits, dict):
        repo_commits = {}

    if overlays:
        bits = [
            f"{ov.get('branch')}@{_short_sha(ov.get('commit'), 7)} "
            f"({'tag, ' if ov.get('kind') == 'tag' else ''}{ov.get('file_count') or 0} files"
            + (
                f", {ov['tombstone_count']} deleted"
                if ov.get("tombstone_count") and state_source
                else ""
            )
            + ")"
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
    snapshots = state.get("source_snapshots") or {}
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
