"""
Main entry point for RAG indexer.
"""

import os
import sys

# Ensure the project root (for `import config`) and src/ (for `import shared`,
# `import config_loader`, etc.) are on sys.path when this script is invoked
# directly as `python src/index_rag.py` from the project root.
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
for _p in (_root, _here):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gc
import json
import shutil
import subprocess
import uuid
import time
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, Future

os.environ["TORCHVISION_DISABLE_META_REGISTRATIONS"] = "1"

import argparse

import config_loader
from config_loader import resolve_source_entries
from shared.log import log, log_raw, log_error, log_warn
from shared.embedding import (
    get_embed_model,
    get_embed_backend_family,
    check_provenance_for_indexing,
    check_provenance_for_query,
    set_collection_provenance,
    embed_dense_batch,
    embed_sparse_batch,
    cuda_clear_cache,
    sanitize_dense_vectors,
    is_zero_vector,
    check_truncation,
    TruncationStats,
    validate_device_config,
)
from shared.indexing import load_all_sources
from shared.manifest import (
    compute_file_hash,
    is_excluded,
    normalize_file_key,
    resolve_key_to_disk_path,
    validate_source_dirs,
)
from shared.qdrant_client import get_qdrant_client, get_qdrant_url
from shared.docker_utils import ensure_qdrant_running, ensure_tei_running
from shared.hybrid_embed import (
    get_sqlite_path,
    init_sqlite_db,
    save_dense_vectors_sqlite,
    read_dense_vectors_sqlite,
    cleanup_sqlite,
)
from shared.chunk_pool import ChunkPool, ChunkHistogram
from typing import Callable, Any

# Sentinel for build_branch_resolver() default arg (distinguish "not passed" from None)
_SENTINEL: Any = object()


class TimingTracker:
    """Track timing for different phases of indexing."""

    def __init__(self, verbose: bool = False):
        self.timings = {}
        self.counts = {}
        self.verbose = verbose

    @contextmanager
    def measure(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            if name not in self.timings:
                self.timings[name] = 0
                self.counts[name] = 0
            self.timings[name] += elapsed
            self.counts[name] += 1

    def print_item(self, name: str, elapsed: float, count: int = 1):
        """Print timing for a single operation."""
        if self.verbose:
            log(f"        {name}: {elapsed:.3f}s ({count} items)")

    def print_summary(self):
        log_raw()
        log_raw("=" * 70)
        log_raw("TIMING SUMMARY")
        log_raw("=" * 70)
        total = sum(self.timings.values())
        for name, elapsed in sorted(self.timings.items(), key=lambda x: -x[1]):
            count = self.counts[name]
            pct = 100 * elapsed / total if total > 0 else 0
            log_raw(f"  {name:30s}: {elapsed:8.2f}s ({count:5d} items) {pct:5.1f}%")
        log_raw("-" * 70)
        log_raw(f"  {'TOTAL':30s}: {total:8.2f}s")
        log_raw("=" * 70)
        log_raw()


def get_manifest_path():
    """Get manifest path based on store type."""
    index_path = Path(config.get_index_path()).resolve()
    return index_path / "index_manifest.json"


def load_manifest():
    """Load manifest based on store type."""
    manifest_path = get_manifest_path()
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            # Normalize old format if necessary
            if "files" in manifest and isinstance(manifest["files"], list):
                # Convert old list format to new dict format
                old_files = manifest["files"]
                new_files = {}
                for f in old_files:
                    path = f.get("file_path", "")
                    if path:
                        normalized = normalize_manifest_key(path)
                        new_files[normalized] = {
                            "file_path": normalized,
                            "mtime": f.get("mtime", 0),
                            "hash": f.get("hash", ""),
                            "vector_ids": [],  # Initialize empty
                        }
                manifest["files"] = new_files
            elif "files" in manifest and isinstance(manifest["files"], dict):
                # Convert filename-keyed manifests to path-keyed manifests
                new_files = {}
                for key, value in manifest["files"].items():
                    path = value.get("file_path", key)
                    normalized = normalize_manifest_key(path)
                    new_files[normalized] = {
                        "file_path": normalized,
                        "mtime": value.get("mtime", 0),
                        "hash": value.get("hash", ""),
                        "vector_ids": value.get("vector_ids", []),
                    }
                manifest["files"] = new_files
            return manifest
    return None


def save_manifest(manifest):
    """Save manifest based on store type."""
    if manifest is None:
        return
    manifest_path = get_manifest_path()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def regenerate_manifest():
    """Regenerate manifest from Qdrant collection."""
    regenerate_manifest_qdrant()


def resolve_manifest_path(file_path: str) -> Path | None:
    """Resolve a stored file_path (canonical key) to an actual file on disk.

    Uses ``resolve_key_to_disk_path()`` to map canonical keys back to their
    real disk location, then falls back to legacy heuristics for keys that
    pre-date the canonical prefix system.
    """
    normalized = file_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]

    # Primary: use the new canonical-key-to-disk resolver
    disk_path = resolve_key_to_disk_path(normalized, cfg=config)
    candidate = Path(disk_path)
    if not candidate.is_absolute():
        candidate = Path(__file__).resolve().parent / disk_path
    if candidate.exists():
        return candidate

    # Fallback: try the normalized key directly (may already be a disk path)
    candidate = Path(normalized)
    if candidate.exists():
        return candidate

    # Fallback: try under each configured source root (legacy keys)
    for source_dir in resolve_source_entries(config):
        candidate = Path(source_dir["path"]) / normalized
        if candidate.exists():
            return candidate

    return None


def normalize_manifest_key(file_path: str) -> str:
    """Normalize a manifest key to the canonical format.

    Resolves the file on disk to determine which SOURCE_DIR it belongs to,
    then delegates to ``normalize_file_key()`` for consistent key generation.
    Falls back to simple ``./`` prefix stripping when the file cannot be resolved.
    """
    cleaned = file_path.replace("\\", "/")
    # Strip leading "./" properly (prefix, not character set)
    if cleaned.startswith("./"):
        cleaned = cleaned[2:]

    resolved = resolve_manifest_path(cleaned)
    if not resolved:
        return cleaned

    resolved_abs = resolved.resolve()
    for source_dir in resolve_source_entries(config):
        root_abs = Path(source_dir["path"]).resolve()
        try:
            rel = resolved_abs.relative_to(root_abs).as_posix()
            return normalize_file_key(source_dir["path"], rel, source_dir=source_dir)
        except ValueError:
            continue

    return cleaned


def regenerate_manifest_qdrant():
    """Rebuild the manifest by scanning the Qdrant collection."""
    from qdrant_client.http.exceptions import UnexpectedResponse

    log("[REGENERATE MANIFEST] Scanning Qdrant collection...")
    # Only need a QdrantClient for scrolling — don't use get_qdrant_vector_store()
    # which would load the sparse encoder on CUDA as a side effect.
    client = get_qdrant_client(config)
    manifest = {"files": {}}
    offset = 0
    limit = 1000

    while True:
        try:
            response = client.scroll(
                collection_name=config.COLLECTION_NAME,
                offset=offset,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
        except UnexpectedResponse as exc:
            if "doesn't exist" in str(exc) or "Not found" in str(exc):
                log(f"Collection '{config.COLLECTION_NAME}' not found.")
                save_manifest(manifest)
                return
            raise
        points, next_offset = response
        points = points or []
        if not points:
            break
        offset = next_offset
        if offset is None:
            break

        for point in points:
            payload = point.payload or {}
            # file_path in Qdrant payload is already the canonical key
            canonical_key = payload.get("file_path")
            if not canonical_key:
                continue
            # Normalize for safety (strip backslashes, leading ./)
            normalized = canonical_key.replace("\\", "/")
            if normalized.startswith("./"):
                normalized = normalized[2:]
            entry = manifest["files"].setdefault(
                normalized,
                {
                    "file_path": normalized,
                    "mtime": 0,
                    "hash": "",
                    "vector_ids": [],
                },
            )
            if not entry.get("file_path"):
                entry["file_path"] = normalized
            entry["vector_ids"].append(str(point.id))

    # Deduplicate vector ids and attach file stats
    for entry in manifest["files"].values():
        entry["vector_ids"] = list(dict.fromkeys(entry["vector_ids"]))
        resolved = resolve_manifest_path(entry["file_path"])
        if resolved:
            entry["mtime"] = int(resolved.stat().st_mtime)
            entry["hash"] = compute_file_hash(resolved)
        else:
            entry["mtime"] = entry.get("mtime", 0)
            entry["hash"] = entry.get("hash", "")

    save_manifest(manifest)
    log("Manifest rebuilt from Qdrant collection")


def make_qdrant_point_id(file_key: str, index: int) -> str:
    """Create a deterministic UUID for a Qdrant point."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{file_key}:{index}"))


def make_branch_point_id(branch: str, file_key: str, index: int) -> str:
    """Create a deterministic UUID for a branch-overlay Qdrant point.

    Branch-namespaced IDs never collide with main-branch IDs because
    the ``{branch}::`` prefix is absent in ``make_qdrant_point_id``.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{branch}::{file_key}:{index}"))


def get_current_file_states():
    """Get current state of all source files, driven by resolved SOURCE_DIRS."""
    states = {}

    for source_dir in resolve_source_entries(config):
        dir_path = Path(source_dir["path"])
        if not dir_path.exists():
            continue
        exclude_patterns = source_dir.get("exclude", [])
        for ext in source_dir["extensions"]:
            for f in dir_path.rglob(f"*{ext}"):
                if is_excluded(f, exclude_patterns):
                    continue
                try:
                    if not f.is_file():
                        continue
                    mtime = f.stat().st_mtime
                    hash_val = compute_file_hash(f)
                    relative_path = f.relative_to(dir_path).as_posix()
                    path_key = normalize_file_key(
                        source_dir["path"], relative_path, source_dir=source_dir
                    )
                    states[path_key] = {
                        "file_path": path_key,
                        "full_path": str(f),
                        "mtime": mtime,
                        "hash": hash_val,
                    }
                except Exception:
                    continue

    return states


def load_nodes_for_file(file_info):
    """Load and process nodes for a specific file using the reader registry."""
    from shared.readers import load_nodes_for_file as _registry_load

    return _registry_load(file_info)


def confirm_full_index(message: str) -> bool:
    """Ask user to confirm full indexing with warning."""
    log_warn(message)
    log_raw("This will take a VERY LONG TIME and may be resource-intensive.")
    response = input("Type 'YES' to confirm: ")
    return response.strip() == "YES"


def _check_git_repo_working_dirs() -> None:
    """Abort if any git_repo source has its working directory on the wrong branch.

    Main-branch indexing reads files directly from disk (the working copy).
    If the repository is checked out on a branch other than ``main_branch``,
    the files on disk belong to the wrong branch and will be indexed under the
    main-branch label — silently contaminating the index.

    This is a hard error, not a warning.  The user must fix the checkout before
    running the indexer to prevent silent index contamination.
    """
    from config_loader import get_repo_groups
    from shared.git_ops import get_current_branch, GitError

    repo_groups = get_repo_groups(config)
    if not repo_groups:
        return

    mismatches = []
    for group in repo_groups:
        repo_path = group["repo_path"]
        main_branch = group["main_branch"]
        try:
            current = get_current_branch(repo_path)
        except GitError as exc:
            log_warn(f"Could not determine current branch for {repo_path}: {exc}")
            continue

        if current != main_branch:
            mismatches.append((repo_path, main_branch, current))

    if not mismatches:
        return

    for repo_path, main_branch, current in mismatches:
        log_error(
            f"Working directory '{repo_path}' is on branch '{current}', "
            f"but main_branch is '{main_branch}'. "
            f"Main-branch indexing reads files from disk — "
            f"'{current}' content would be indexed as '{main_branch}'."
        )
        log_error(f"  Fix: cd '{repo_path}' && git checkout {main_branch}")
    log_error("Re-run the indexer after fixing all affected repos.")
    sys.exit(1)


def run_indexing(mode="full"):
    """Run the indexing process: full rebuild or incremental refresh."""
    # Validate device config before doing any heavy work (model load, Qdrant connect).
    # This gives a clear message instead of a cryptic stack trace.
    check = validate_device_config(config)
    if check.errors:
        for err in check.errors:
            log_error(err)
        log_error("Fix the device configuration and re-run.")
        sys.exit(1)
    if check.warnings:
        for warn_msg in check.warnings:
            log_warn(warn_msg)
        if not args.yes:
            confirm = input("Continue anyway? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                log("Aborted.")
                sys.exit(0)

    # Validate SOURCE_DIRS canonical prefix uniqueness
    prefix_errors = validate_source_dirs(cfg=config)
    if prefix_errors:
        for err in prefix_errors:
            log_error(err)
        log_error("Fix SOURCE_DIRS canonical prefix collisions and re-run.")
        sys.exit(1)

    # Warn if any git_repo working directory is not on its configured main_branch.
    # Main-branch indexing reads files from disk, so a mismatched checkout silently
    # indexes the wrong branch content under the main_branch label.
    _check_git_repo_working_dirs()

    if mode == "full":
        run_full_indexing()
    else:
        run_refresh_indexing()

    # ── Branch support (after main indexing) ────────────────────────
    from config_loader import get_repo_groups

    repo_groups = get_repo_groups(config)
    has_git_repos = len(repo_groups) > 0
    has_branches = any(g.get("branches") for g in repo_groups)

    if has_git_repos:
        # Ensure branch payload index + backfill existing vectors.
        # This runs even without feature branches configured, because
        # the MCP query filter always requires branch == main_branch
        # on git-backed vectors.
        ensure_branch_payload_index()
        backfill_branch_payload()

    if has_branches:
        run_branch_overlay_indexing()
    elif has_git_repos:
        # No branches configured, but we still need to clean up
        # branch overlays that were previously indexed and have since
        # been removed from the config.
        _cleanup_stale_branches(configured_branches=set())


def run_full_indexing():
    """Run full indexing by routing through the refresh path.

    After ``--clear`` the manifest is empty, so ``determine_actions()`` puts
    every discovered file into the ``add`` list.  This reuses the two-pass
    hybrid embedding logic in ``perform_refresh_qdrant()`` rather than
    duplicating a separate (and VRAM-unsafe) code path.
    """
    log("[MODE] Full indexing (via refresh path — all files as ADD)...")

    # Empty manifest = every file is new
    manifest = {"files": {}}
    current_states = get_current_file_states()
    actions = determine_actions(manifest["files"], current_states, manifest=manifest)

    log(f"Found {len(actions['add'])} files to index (full rebuild after --clear)")
    log_refresh_changes(
        actions,
        current_states,
        manifest["files"],
        branch_resolver=build_branch_resolver(),
    )

    perform_refresh_qdrant(actions, manifest)

    # Store repo commits after full indexing
    _update_repo_commits(manifest)
    save_manifest(manifest)


def run_refresh_indexing():
    """Run incremental refresh process.

    Uses git-diff acceleration for git-backed SOURCE_DIRS entries:
    if the stored main branch commit matches the current HEAD, only
    uncommitted changes are checked (via hash).  If commits differ,
    git diff narrows the set of files to re-hash.
    """
    log("[MODE] Refreshing index incrementally...")

    manifest = load_manifest()
    if not manifest or "files" not in manifest:
        log("No valid manifest found for refresh - switching to full indexing")
        return run_full_indexing()  # routes through refresh path (all files as ADD)

    # Get current file states
    current_states = get_current_file_states()

    # Determine actions (enhanced with git-diff acceleration)
    actions = determine_actions(manifest["files"], current_states, manifest=manifest)

    if not actions["add"] and not actions["modify"] and not actions["delete"]:
        log("No changes detected - index is up to date")
        if VERBOSE:
            log_verbose_refresh(actions, current_states, manifest["files"])
        # Still update repo commits even when nothing changed (first run
        # with git-aware config on an existing manifest may not have commits yet)
        _update_repo_commits(manifest)
        save_manifest(manifest)
        return

    log(
        f"Found {len(actions['add'])} new, "
        f"{len(actions['modify'])} modified, "
        f"{len(actions['delete'])} deleted"
    )
    log_refresh_changes(
        actions,
        current_states,
        manifest["files"],
        branch_resolver=build_branch_resolver(),
    )
    if VERBOSE:
        log_verbose_refresh(actions, current_states, manifest["files"])

    # Perform updates
    perform_refresh_qdrant(actions, manifest)

    # Update stored repo commit hashes after successful indexing
    _update_repo_commits(manifest)
    save_manifest(manifest)


def _git_prefix_paths(group: dict) -> list[str] | None:
    """Return the git path prefixes for a repo group, or None (no filter).

    A prefix of ``"."`` or ``""`` means the whole repo — return None so
    ``git diff`` is not given a path filter (which would restrict to
    literally files named ``"."``, not all files).
    """
    prefixes = group.get("git_prefixes", [])
    if not prefixes:
        return None
    # Filter out root placeholders
    cleaned = [p for p in prefixes if p and p != "."]
    return cleaned if cleaned else None


def _build_repo_group_file_map(resolved_entries: list) -> dict[str, list[dict]]:
    """Build a map: absolute-posix repo_path → list of resolved source entries.

    Used by the git-diff fast path to associate manifest file keys with
    their parent repo group.
    """
    result: dict[str, list[dict]] = {}
    for entry in resolved_entries:
        if entry["_entry_type"] != "git_repo":
            continue
        repo_key = Path(entry["_repo_path"]).resolve().as_posix()
        result.setdefault(repo_key, []).append(entry)
    return result


def _file_key_to_git_path(file_key: str, entry: dict) -> str | None:
    """Convert a manifest file key back to a git-relative path.

    Canonical file keys use the last segment of ``path`` (or
    ``map_to_path``) as prefix.  Git paths are relative to the repo root
    and use the ``_git_prefix`` from the resolved entry.

    Returns None if the file key does not belong to this entry.
    """
    from shared.manifest import _get_canonical_prefix

    canon_prefix = _get_canonical_prefix(entry)
    git_prefix = entry.get("_git_prefix", "") or ""
    # Normalise root placeholders
    if git_prefix == ".":
        git_prefix = ""

    if canon_prefix:
        if not file_key.startswith(canon_prefix + "/"):
            return None
        relative = file_key[len(canon_prefix) + 1 :]
    else:
        relative = file_key

    if git_prefix:
        return f"{git_prefix}/{relative}"
    return relative


def _git_path_to_file_key(git_path: str, entries: list[dict]) -> str | None:
    """Convert a git-relative path to its manifest file key.

    Tries each resolved entry for the repo group until one matches.
    Returns None if no entry covers the path (e.g. extension not indexed).
    """
    from shared.manifest import _get_canonical_prefix

    git_norm = git_path.replace("\\", "/")

    for entry in entries:
        git_prefix = entry.get("_git_prefix", "") or ""
        if git_prefix == ".":
            git_prefix = ""

        # Check if this git path falls under this entry's prefix
        if git_prefix:
            if not (git_norm.startswith(git_prefix + "/") or git_norm == git_prefix):
                continue
            relative = git_norm[len(git_prefix) + 1 :] if git_prefix else git_norm
        else:
            relative = git_norm

        # Check extension
        ext = "." + relative.rsplit(".", 1)[-1].lower() if "." in relative else ""
        exts_lower = [e.lower() for e in entry.get("extensions", [])]
        if ext not in exts_lower:
            continue

        canon_prefix = _get_canonical_prefix(entry)
        if canon_prefix:
            return f"{canon_prefix}/{relative}"
        return relative

    return None


def determine_actions(
    old_files: dict,
    current_states: dict,
    manifest: dict | None = None,
) -> dict:
    """Determine which files to add, modify, or delete.

    For ``git_repo`` SOURCE_DIRS entries the function uses a two-tier
    fast path when ``manifest`` is supplied:

    **Tier 1 — commits match (Case A):**
    If the stored ``repo_commits`` commit equals the current HEAD the
    committed portion of the repo has not changed.  Only files whose
    ``mtime`` differs from the manifest are re-hashed (uncommitted
    working-copy changes).  All other committed files are assumed
    unchanged without reading them from disk.

    **Tier 2 — commits differ (Case B):**
    ``git diff <stored_commit>..<current_HEAD>`` narrows the candidate
    set to files that changed between the two commits.  Only those
    files (plus any with mtime drift) are considered for re-embedding.
    If the ratio of changed files to total manifest files exceeds
    ``DIFF_FULL_REINDEX_THRESHOLD`` the entire repo group falls back to
    full hash comparison.

    **Case C — no stored commit / source_set / legacy:**
    Full hash comparison, identical to the original behaviour.

    Regardless of tier, new on-disk files (not in the manifest) are
    always added, and manifest entries with no on-disk counterpart are
    always deleted.

    Args:
        old_files: Manifest ``files`` dict (path_key → entry).
        current_states: Output of ``get_current_file_states()``.
        manifest: Full manifest dict (for ``repo_commits``).  When
            ``None`` the function behaves as before (Case C for all
            files).

    Returns:
        Dict with keys ``"add"``, ``"modify"``, ``"delete"``, each a
        list of path keys.
    """
    from config_loader import get_repo_groups, resolve_source_entries
    from shared.git_ops import (
        GitError,
        diff_commits,
        get_branch_head,
        validate_git_repo,
    )
    from shared.manifest import _get_canonical_prefix

    actions: dict[str, list] = {"add": [], "modify": [], "delete": []}

    # ── Build per-repo-group skips using git-diff fast path ──────────
    # skip_hash_check: set of path_keys whose hashes we can skip entirely
    #                  (commits match AND mtime unchanged)
    skip_hash_check: set[str] = set()

    if manifest is not None:
        repo_commits = manifest.get("repo_commits", {})
        repo_groups = get_repo_groups(config)
        resolved = resolve_source_entries(config)
        repo_entry_map = _build_repo_group_file_map(resolved)
        threshold = getattr(config, "DIFF_FULL_REINDEX_THRESHOLD", 0.5)

        for group in repo_groups:
            repo_path = group["repo_path"]
            main_branch = group["main_branch"]
            repo_key = Path(repo_path).resolve().as_posix()
            entries_for_repo = repo_entry_map.get(repo_key, [])

            stored_entry = repo_commits.get(repo_key)
            if not stored_entry:
                # Case C: no stored commit → full hash scan
                continue

            stored_commit = stored_entry.get("commit", "")
            if not stored_commit:
                continue

            # Get current HEAD
            try:
                if not validate_git_repo(repo_path):
                    continue
                current_commit = get_branch_head(repo_path, main_branch)
            except GitError as exc:
                log_warn(f"[FAST-PATH] Cannot get HEAD for {repo_path}: {exc}")
                continue

            if current_commit == stored_commit:
                # ── Case A: commits match ─────────────────────────────
                # Committed files haven't changed.  Only check files
                # whose mtime differs from what is stored (uncommitted
                # working-copy changes).
                for path_key, old_entry in old_files.items():
                    # Only applies to files in this repo group
                    if path_key not in current_states:
                        continue  # will be caught in delete pass
                    current = current_states[path_key]

                    # Verify this key belongs to this repo group
                    belongs = any(
                        _file_key_to_git_path(path_key, e) is not None
                        for e in entries_for_repo
                    )
                    if not belongs:
                        continue

                    stored_mtime = old_entry.get("mtime", 0)
                    current_mtime = current.get("mtime", 0)
                    if int(stored_mtime) == int(current_mtime):
                        # mtime unchanged → assume content unchanged
                        skip_hash_check.add(path_key)
                    # else: mtime changed → hash will be compared in main loop

            else:
                # ── Case B: commits differ ────────────────────────────
                git_paths = _git_prefix_paths(group)
                try:
                    changes = diff_commits(
                        repo_path,
                        stored_commit,
                        current_commit,
                        paths=git_paths,
                    )
                except GitError as exc:
                    log_warn(
                        f"[FAST-PATH] git diff failed for {repo_path} "
                        f"({stored_commit[:8]}..{current_commit[:8]}): {exc}. "
                        f"Falling back to full hash scan."
                    )
                    continue  # Case C fallback: full hash scan for this group

                # Collect all manifest keys for this repo group
                repo_manifest_keys = {
                    k
                    for k in old_files
                    if any(
                        _file_key_to_git_path(k, e) is not None
                        for e in entries_for_repo
                    )
                }

                total_in_manifest = len(repo_manifest_keys)
                changed_file_keys = set()
                for status, git_path in changes:
                    fk = _git_path_to_file_key(git_path, entries_for_repo)
                    if fk:
                        changed_file_keys.add(fk)

                if total_in_manifest > 0:
                    ratio = len(changed_file_keys) / total_in_manifest
                    if ratio > threshold:
                        log(
                            f"[FAST-PATH] {repo_path}: diff too large "
                            f"({len(changed_file_keys)}/{total_in_manifest} = "
                            f"{ratio:.0%}), falling back to full hash scan"
                        )
                        continue  # Case C fallback

                # Mark all repo-group files not in the changed set as skip
                # Skip hash check for files that git says haven't changed
                for path_key in repo_manifest_keys:
                    if path_key in current_states and path_key not in changed_file_keys:
                        skip_hash_check.add(path_key)

    # ── Main comparison loop ─────────────────────────────────────────
    for path_key, current in current_states.items():
        if path_key not in old_files:
            actions["add"].append(path_key)
        elif path_key in skip_hash_check:
            pass  # fast path: assume unchanged
        else:
            old_entry = old_files[path_key]
            # Compare by content hash only — mtime differs across machines
            # (git clone, copy, different OS) even when content is identical.
            if current["hash"] != old_entry.get("hash", ""):
                actions["modify"].append(path_key)

    # Find deletes
    for path_key in old_files:
        if path_key not in current_states:
            actions["delete"].append(path_key)

    return actions


def _update_repo_commits(manifest: dict) -> None:
    """Update manifest with current git commit hashes for each repo group.

    Stores the current HEAD commit for each git-backed repo group so that
    subsequent runs can use ``git diff`` for fast change detection.  Non-git
    SOURCE_DIRS entries are ignored.

    The ``repo_commits`` dict in the manifest is keyed by the resolved
    (absolute, posix) repo path and stores:
      - ``main_branch``: branch name
      - ``commit``: HEAD commit hash at this point in time
    """
    from config_loader import get_repo_groups
    from shared.git_ops import get_branch_head, validate_git_repo, GitError

    repo_groups = get_repo_groups(config)
    if not repo_groups:
        return

    repo_commits = manifest.get("repo_commits", {})

    for group in repo_groups:
        repo_path = group["repo_path"]
        main_branch = group["main_branch"]
        repo_key = Path(repo_path).resolve().as_posix()

        try:
            if not validate_git_repo(repo_path):
                log_warn(f"Not a git repo: {repo_path}, skipping commit tracking")
                continue
            commit = get_branch_head(repo_path, main_branch)
            repo_commits[repo_key] = {
                "main_branch": main_branch,
                "commit": commit,
            }
        except GitError as exc:
            log_warn(f"Cannot get HEAD for {main_branch} in {repo_path}: {exc}")

    manifest["repo_commits"] = repo_commits


# ── Branch overlay indexing ──────────────────────────────────────


def _get_branch_manifest_path(branch: str) -> Path:
    """Return path to a branch-specific manifest file."""
    from shared.git_ops import sanitize_branch_name

    index_path = Path(config.get_index_path()).resolve()
    safe = sanitize_branch_name(branch)
    return index_path / f"index_manifest_branch_{safe}.json"


def _load_branch_manifest(branch: str) -> dict:
    """Load a branch manifest, returning empty structure if absent."""
    path = _get_branch_manifest_path(branch)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "branch": branch,
        "files": {},
        "tombstones": [],
        "merge_base": None,
        "last_branch_commit": None,
    }


def _save_branch_manifest(branch: str, manifest: dict) -> None:
    """Persist a branch manifest to disk."""
    path = _get_branch_manifest_path(branch)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def ensure_branch_payload_index() -> None:
    """Create a Qdrant payload index on the ``branch`` field if missing.

    This is idempotent — Qdrant silently accepts re-creation of an
    existing index.  Called once before branch overlay indexing and
    once before the backfill migration.
    """
    from qdrant_client import models

    client = get_qdrant_client(config)
    try:
        client.create_payload_index(
            collection_name=config.COLLECTION_NAME,
            field_name="branch",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        log("Qdrant payload index on 'branch' field ensured")
    except Exception as exc:
        # Index may already exist — that's fine
        if "already exists" not in str(exc).lower():
            log_warn(f"Could not create branch payload index: {exc}")


def backfill_branch_payload() -> int:
    """Add ``branch`` payload to existing vectors that lack it.

    Existing vectors indexed before the branch feature have no ``branch``
    field.  Without backfill, the Qdrant filter ``branch == "develop"``
    would miss them entirely.  This function scrolls through all points
    where ``branch IS NULL``, resolves the correct branch label from the
    file_path metadata and the config prefix map, and applies
    ``set_payload`` in batches.

    Non-git ``source_set`` chunks (whose file_path doesn't match any
    git_repo prefix) are left without a ``branch`` field — this is by
    design so they pass through the ``IsNullCondition`` filter.

    Returns:
        Number of points updated.
    """
    from qdrant_client import models

    _resolve_branch_for_file = build_branch_resolver()

    client = get_qdrant_client(config)
    collection = config.COLLECTION_NAME
    batch_size = 500
    total_updated = 0
    total_skipped = 0  # non-git (source_set) points left as-is
    offset = None
    first_pass = True

    log("Backfilling 'branch' payload on existing vectors...")

    # Scroll through all points where branch is absent or null.
    # Pre-existing vectors have no ``branch`` key at all (IS EMPTY),
    # while future edge cases might have an explicit null (IS NULL).
    # We match both to be safe.
    null_filter = models.Filter(
        should=[
            models.IsNullCondition(
                is_null=models.PayloadField(key="branch"),
            ),
            models.IsEmptyCondition(
                is_empty=models.PayloadField(key="branch"),
            ),
        ],
    )

    while True:
        scroll_kwargs = {
            "collection_name": collection,
            "scroll_filter": null_filter,
            "limit": batch_size,
            "with_payload": ["file_path"],
            "with_vectors": False,
        }
        if offset is not None:
            scroll_kwargs["offset"] = offset

        points, next_offset = client.scroll(**scroll_kwargs)
        points = points or []

        if not points:
            break

        # Group points by target branch label
        by_branch: dict[str, list[str]] = {}  # branch_label → [point_id, ...]

        for point in points:
            payload = point.payload or {}
            file_path = payload.get("file_path", "")
            branch_label = _resolve_branch_for_file(file_path)

            if branch_label is None:
                # Non-git chunk — leave without branch field
                total_skipped += 1
                continue

            if branch_label not in by_branch:
                by_branch[branch_label] = []
            by_branch[branch_label].append(point.id)

        # Apply set_payload for each branch label
        for branch_label, point_ids in by_branch.items():
            client.set_payload(
                collection_name=collection,
                payload={"branch": branch_label},
                points=point_ids,
            )
            total_updated += len(point_ids)

        if first_pass:
            log(
                f"  First batch: {len(points)} points scrolled, "
                f"{sum(len(v) for v in by_branch.values())} updated"
            )
            first_pass = False

        offset = next_offset
        if offset is None:
            break

    if total_updated > 0:
        log(f"Backfill complete: {total_updated} points updated with 'branch' payload")
    else:
        log("Backfill: no points needed updating (all already have 'branch' field)")

    if total_skipped > 0:
        log(f"  {total_skipped} non-git points left without 'branch' (by design)")

    return total_updated


def _collect_branch_extensions(group: dict) -> set:
    """Collect all configured file extensions for a repo group."""
    exts = set()
    for entry in group["resolved_entries"]:
        for ext in entry.get("extensions", []):
            exts.add(ext.lower())
    return exts


def _map_git_path_to_file_key(git_path: str, group: dict) -> tuple[str, dict] | None:
    """Map a git-relative file path to its canonical file_key and source entry.

    Returns (file_key, resolved_entry) or None if the path doesn't match
    any configured source within the repo group.
    """
    from shared.manifest import normalize_file_key

    git_normalized = git_path.replace("\\", "/")

    for entry in group["resolved_entries"]:
        git_prefix = entry["_git_prefix"]
        if not git_prefix or git_prefix == ".":
            # Root source — all paths match
            relative_posix = git_normalized
        else:
            prefix = git_prefix.replace("\\", "/").rstrip("/") + "/"
            if not git_normalized.startswith(prefix):
                continue
            relative_posix = git_normalized[len(prefix) :]

        # Check extension matches
        ext = "." + git_normalized.rsplit(".", 1)[-1] if "." in git_normalized else ""
        configured_exts = {e.lower() for e in entry.get("extensions", [])}
        if ext.lower() not in configured_exts:
            continue

        # Check exclude patterns
        from shared.manifest import is_excluded
        from pathlib import Path as _Path

        full_disk_path = _Path(entry["path"]) / relative_posix
        exclude_patterns = entry.get("exclude", [])
        if is_excluded(full_disk_path, exclude_patterns):
            continue

        file_key = normalize_file_key(entry["path"], relative_posix, source_dir=entry)
        return file_key, entry

    return None


def run_branch_overlay_indexing() -> None:
    """Index feature branch overlays for all configured branches.

    For each repo group with ``branches``, this function:
      1. Diffs the feature branch against main to find changed files.
      2. Reads changed files from git (no checkout required).
      3. Runs them through the reader pipeline.
      4. Embeds and upserts to Qdrant with branch-namespaced point IDs
         and ``branch`` payload = feature branch name.
      5. Stores tombstones for deleted files in the branch manifest.
      6. Cleans up branches removed from config.
    """
    from config_loader import get_repo_groups
    from shared.git_ops import (
        GitError,
        branch_exists,
        diff_branches,
        get_branch_head,
        get_merge_base,
        read_files_to_temp_dir,
        sanitize_branch_name,
    )

    repo_groups = get_repo_groups(config)
    if not repo_groups:
        return

    # Collect all (repo, branch) pairs that should exist
    configured_branches: set[tuple[str, str]] = set()

    for group in repo_groups:
        repo_path = group["repo_path"]
        main_branch = group["main_branch"]
        branches = group.get("branches", [])

        if not branches:
            continue

        for feature_branch in branches:
            configured_branches.add((repo_path, feature_branch))

            log(
                f"[BRANCH] Processing overlay: {feature_branch} "
                f"(repo={repo_path}, main={main_branch})"
            )

            # ── Validate branch existence ──
            try:
                if not branch_exists(repo_path, feature_branch):
                    log_warn(
                        f"Branch '{feature_branch}' not found in {repo_path}, skipping"
                    )
                    continue
            except GitError as exc:
                log_warn(f"Cannot check branch '{feature_branch}': {exc}")
                continue

            # ── Get merge base and diff ──
            try:
                merge_base = get_merge_base(repo_path, main_branch, feature_branch)
                git_prefixes = group.get("git_prefixes", [])
                changes = diff_branches(
                    repo_path,
                    main_branch,
                    feature_branch,
                    paths=git_prefixes if git_prefixes else None,
                )
            except GitError as exc:
                log_warn(f"Cannot diff {feature_branch} vs {main_branch}: {exc}")
                continue

            if not changes:
                log(f"[BRANCH] No changes on {feature_branch}, skipping")
                continue

            # ── Separate A/M from D (deleted) ──
            add_modify_git_paths = []
            deleted_git_paths = []
            for status, git_path in changes:
                if status == "D":
                    deleted_git_paths.append(git_path)
                else:
                    add_modify_git_paths.append(git_path)

            # ── Filter to configured extensions ──
            valid_exts = _collect_branch_extensions(group)
            add_modify_git_paths = [
                p
                for p in add_modify_git_paths
                if "." in p and ("." + p.rsplit(".", 1)[-1]).lower() in valid_exts
            ]

            # ── Check diff threshold ──
            threshold = group.get("diff_threshold", 0.5)
            # Rough estimate: count total files in git prefixes
            # If change ratio exceeds threshold, warn (but don't block)
            total_changes = len(add_modify_git_paths) + len(deleted_git_paths)
            if total_changes > 5000:
                log_warn(
                    f"[BRANCH] {feature_branch} has {total_changes} changed files "
                    f"— this is a very large overlay"
                )

            log(
                f"[BRANCH] {feature_branch}: {len(add_modify_git_paths)} files to index, "
                f"{len(deleted_git_paths)} deleted"
            )

            # ── Load branch manifest ──
            branch_manifest = _load_branch_manifest(feature_branch)

            # ── Map git paths to file keys ──
            files_to_index: dict[str, dict] = {}  # file_key -> file_info
            for git_path in add_modify_git_paths:
                mapping = _map_git_path_to_file_key(git_path, group)
                if mapping is None:
                    continue
                file_key, entry = mapping
                files_to_index[file_key] = {
                    "git_path": git_path,
                    "file_key": file_key,
                    "entry": entry,
                }

            # Map deleted paths to file keys for tombstones
            tombstone_keys = set()
            for git_path in deleted_git_paths:
                mapping = _map_git_path_to_file_key(git_path, group)
                if mapping is not None:
                    tombstone_keys.add(mapping[0])

            if not files_to_index and not tombstone_keys:
                log(f"[BRANCH] No indexable changes on {feature_branch}")
                # Still update manifest merge_base
                branch_manifest["merge_base"] = merge_base
                _save_branch_manifest(feature_branch, branch_manifest)
                continue

            # ── Read files from git to temp dir ──
            git_paths_to_read = [info["git_path"] for info in files_to_index.values()]
            temp_dir = None
            try:
                if git_paths_to_read:
                    temp_dir = read_files_to_temp_dir(
                        repo_path, feature_branch, git_paths_to_read
                    )

                # ── Build file states (like get_current_file_states but for branch) ──
                branch_states: dict[str, dict] = {}
                for file_key, info in files_to_index.items():
                    git_path = info["git_path"]
                    entry = info["entry"]

                    if temp_dir:
                        full_path = Path(temp_dir) / git_path.replace("\\", "/")
                    else:
                        continue

                    if not full_path.exists():
                        log_warn(f"[BRANCH] Temp file missing: {full_path}")
                        continue

                    try:
                        hash_val = compute_file_hash(full_path)
                    except Exception:
                        log_warn(f"[BRANCH] Cannot hash: {full_path}")
                        continue

                    branch_states[file_key] = {
                        "file_path": file_key,
                        "full_path": str(full_path),
                        "mtime": 0,  # git doesn't preserve mtime
                        "hash": hash_val,
                    }

                # ── Determine actions vs branch manifest ──
                old_files = branch_manifest.get("files", {})
                actions = determine_actions(old_files, branch_states)

                # Also handle: files that were in the previous branch manifest
                # but are no longer changed on the branch (reverted/merged to main).
                # These should be deleted from the branch overlay.
                for old_key in list(old_files.keys()):
                    if (
                        old_key not in branch_states
                        and old_key not in actions["delete"]
                    ):
                        actions["delete"].append(old_key)

                total_work = (
                    len(actions["add"])
                    + len(actions["modify"])
                    + len(actions["delete"])
                )
                if total_work == 0 and not tombstone_keys:
                    # Hash-diff says nothing changed — but verify that the vectors
                    # actually exist in Qdrant.  If the collection was cleared while
                    # the branch manifest survived, Qdrant has 0 branch vectors but
                    # the manifest still reports files as "up to date".  Detect this
                    # by counting vectors tagged with this branch; if 0, force a full
                    # re-index of all files recorded in the manifest.
                    manifest_file_count = len(branch_manifest.get("files", {}))
                    if manifest_file_count > 0:
                        try:
                            from qdrant_client import models as _chk_models

                            chk_client = get_qdrant_client(config)
                            chk_result = chk_client.count(
                                collection_name=config.COLLECTION_NAME,
                                count_filter=_chk_models.Filter(
                                    must=[
                                        _chk_models.FieldCondition(
                                            key="branch",
                                            match=_chk_models.MatchValue(
                                                value=feature_branch
                                            ),
                                        )
                                    ]
                                ),
                                exact=False,
                            )
                            qdrant_branch_count = chk_result.count
                        except Exception as _exc:
                            log_warn(
                                f"[BRANCH] Could not count Qdrant vectors for "
                                f"{feature_branch}: {_exc}. Assuming up to date."
                            )
                            qdrant_branch_count = manifest_file_count  # skip re-index

                        if qdrant_branch_count == 0:
                            log_warn(
                                f"[BRANCH] {feature_branch}: manifest claims "
                                f"{manifest_file_count} files up to date but Qdrant "
                                f"has 0 branch vectors — collection was likely cleared. "
                                f"Forcing full re-index of branch overlay."
                            )
                            # Treat all manifest files as adds so they get re-embedded
                            actions["add"] = list(branch_manifest["files"].keys())
                            branch_manifest["files"] = {}
                            total_work = len(actions["add"])
                        # else: vectors exist — genuinely up to date

                if total_work == 0 and not tombstone_keys:
                    log(f"[BRANCH] {feature_branch} overlay is up to date")
                    branch_manifest["merge_base"] = merge_base
                    # Store branch HEAD for future incremental branch updates (TODO #5b)
                    try:
                        branch_manifest["last_branch_commit"] = get_branch_head(
                            repo_path, feature_branch
                        )
                    except GitError:
                        pass
                    _save_branch_manifest(feature_branch, branch_manifest)
                    continue

                log(
                    f"[BRANCH] {feature_branch}: "
                    f"{len(actions['add'])} add, "
                    f"{len(actions['modify'])} modify, "
                    f"{len(actions['delete'])} delete"
                )
                log_refresh_changes(
                    actions,
                    branch_states,
                    branch_manifest.get("files", {}),
                    branch_label=feature_branch,
                )

                # ── Delete stale branch vectors ──
                if actions["delete"]:
                    from qdrant_client import models as _models

                    client = get_qdrant_client(config)
                    for del_key in actions["delete"]:
                        old_entry = old_files.get(del_key, {})
                        old_ids = old_entry.get("vector_ids", [])
                        if old_ids:
                            try:
                                client.delete(
                                    collection_name=config.COLLECTION_NAME,
                                    points_selector=_models.PointIdsList(
                                        points=old_ids,
                                    ),
                                )
                                log(
                                    f"[BRANCH] Deleted {len(old_ids)} vectors "
                                    f"for {del_key} on {feature_branch}"
                                )
                            except Exception as exc:
                                log_warn(
                                    f"[BRANCH] Failed to delete vectors for "
                                    f"{del_key}: {exc}"
                                )
                        # Remove from branch manifest
                        old_files.pop(del_key, None)

                # ── Embed and upsert changed files ──
                if actions["add"] or actions["modify"]:
                    from functools import partial

                    perform_refresh_qdrant(
                        actions=actions,
                        manifest=branch_manifest,
                        branch_label=feature_branch,
                        file_states=branch_states,
                        point_id_fn=partial(make_branch_point_id, feature_branch),
                        save_fn=lambda m: _save_branch_manifest(feature_branch, m),
                    )

                # ── Update tombstones ──
                branch_manifest["tombstones"] = sorted(tombstone_keys)
                branch_manifest["merge_base"] = merge_base

                # Store branch HEAD for future incremental branch updates (TODO #5b)
                try:
                    branch_manifest["last_branch_commit"] = get_branch_head(
                        repo_path, feature_branch
                    )
                except GitError:
                    pass

                _save_branch_manifest(feature_branch, branch_manifest)
                log(f"[BRANCH] {feature_branch} overlay indexing complete")

            finally:
                # Clean up temp directory
                if temp_dir and Path(temp_dir).exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)

    # ── Clean up branches removed from config ──
    _cleanup_stale_branches(configured_branches)


def _cleanup_stale_branches(configured_branches: set[tuple[str, str]]) -> None:
    """Remove branch overlays from Qdrant and disk for branches no longer in config.

    Scans for branch manifest files on disk. If a branch is not in the
    configured set, deletes its Qdrant vectors and manifest file.
    """
    from qdrant_client import models
    from shared.git_ops import sanitize_branch_name

    index_path = Path(config.get_index_path()).resolve()

    # Find all branch manifest files
    for manifest_file in index_path.glob("index_manifest_branch_*.json"):
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                branch_data = json.load(f)
        except Exception:
            continue

        branch_name = branch_data.get("branch", "")
        if not branch_name:
            continue

        # Check if this branch is still configured in ANY repo group
        is_configured = any(branch_name == fb for _, fb in configured_branches)

        if is_configured:
            continue

        log(f"[BRANCH] Cleaning up removed branch: {branch_name}")

        # Delete all vectors for this branch from Qdrant
        all_ids = []
        for file_entry in branch_data.get("files", {}).values():
            all_ids.extend(file_entry.get("vector_ids", []))

        if all_ids:
            client = get_qdrant_client(config)
            try:
                # Delete in batches
                batch_size = 1000
                for batch_idx in range(0, len(all_ids), batch_size):
                    batch = all_ids[batch_idx : batch_idx + batch_size]
                    client.delete(
                        collection_name=config.COLLECTION_NAME,
                        points_selector=models.PointIdsList(points=batch),
                    )
                log(f"[BRANCH] Deleted {len(all_ids)} vectors for {branch_name}")
            except Exception as exc:
                log_warn(f"[BRANCH] Failed to delete vectors for {branch_name}: {exc}")

        # Delete the manifest file
        try:
            manifest_file.unlink()
            log(f"[BRANCH] Deleted manifest for {branch_name}")
        except Exception as exc:
            log_warn(f"[BRANCH] Failed to delete manifest: {exc}")


def build_branch_resolver(
    cfg=None, fixed_label=_SENTINEL
) -> Callable[[str], str | None]:
    """Return a callable ``(file_path) -> str | None`` that resolves the
    branch label for a given file path.

    When *fixed_label* is provided (including ``None``), every call returns
    that value verbatim — used for branch-overlay runs where all points share
    the same branch tag.

    When *fixed_label* is omitted (default sentinel), the resolver builds a
    prefix → branch map from the config's resolved source entries:
    git_repo entries resolve to their ``main_branch`` value (e.g. ``"develop"``),
    plain source_set entries resolve to ``None`` (no branch label).

    Args:
        cfg: Config module.  Defaults to the global ``config``.
        fixed_label: If provided, all files resolve to this label.
            Pass ``_SENTINEL`` (default) for prefix-map resolution.

    Returns:
        Callable ``(file_path) -> str | None``.
    """
    if cfg is None:
        cfg = config

    # Fast path: fixed label for all files (branch overlay)
    if fixed_label is not _SENTINEL:
        _fixed = fixed_label  # capture for closure type clarity

        def _fixed_resolver(_file_path: str) -> str | None:
            return _fixed

        return _fixed_resolver

    # Build prefix → branch label map from config's source entries
    from shared.manifest import _get_canonical_prefix

    resolved = resolve_source_entries(cfg)
    prefix_map: dict[str, str | None] = {}
    for entry in resolved:
        prefix = _get_canonical_prefix(entry)
        if entry["_entry_type"] == "git_repo":
            prefix_map[prefix] = entry["_main_branch"]
        else:
            prefix_map[prefix] = None

    def _resolve(file_path: str) -> str | None:
        normalized = file_path.replace("\\", "/")
        for pfx, label in prefix_map.items():
            if not pfx or pfx == ".":
                return label
            if normalized.startswith(pfx + "/") or normalized.startswith(pfx + "\\"):
                return label
        return None

    return _resolve


def log_refresh_changes(
    actions, current_states, manifest_files, branch_label=None, branch_resolver=None
) -> None:
    """Log changes detected, grouped by SOURCE_DIRS directories.

    Args:
        actions: Dict with 'add', 'modify', 'delete' lists of path keys.
        current_states: Mapping of path key → file state info.
        manifest_files: Mapping of path key → manifest entry.
        branch_label: Fixed branch label appended to every filename
            (e.g. ``"task/T37523"`` for branch overlay runs).
        branch_resolver: Callable ``(file_path) -> str | None`` that
            resolves a per-file branch label.  Used for main-branch runs
            where different files may belong to different repo groups with
            different main-branch names.  Takes precedence over
            ``branch_label`` when both are supplied.
    """
    resolved = resolve_source_entries(config)

    # Build prefix list dynamically from resolved entries
    dir_prefixes = [sd["path"].replace("\\", "/").rstrip("/") + "/" for sd in resolved]
    dir_labels = [sd["path"] for sd in resolved]

    def classify(path_value: str) -> str:
        normalized = path_value.replace("\\", "/")
        for prefix, label in zip(dir_prefixes, dir_labels):
            # Empty path or "." matches everything (all files are under current dir)
            if not prefix or prefix == "./":
                return label if label else "root"
            if normalized.startswith(prefix):
                return label
        return "other"

    def collect_details(filenames, source_map):
        grouped: dict[str, list] = {label: [] for label in dir_labels}
        grouped["other"] = []
        for path_key in filenames:
            file_info = source_map.get(path_key, {})
            path_value = file_info.get("file_path", path_key)
            grouped[classify(path_value)].append(path_value)
        return grouped

    add_grouped = collect_details(actions["add"], current_states)
    modify_grouped = collect_details(actions["modify"], current_states)
    delete_grouped = collect_details(actions["delete"], manifest_files)

    def _item_suffix(file_path: str) -> str:
        if branch_resolver is not None:
            label = branch_resolver(file_path)
            return f" [{label}]" if label else ""
        return f" [{branch_label}]" if branch_label else ""

    def _log_group(action_label, grouped):
        log_raw(f"\n  [{action_label.upper()}]")
        # Replace empty string labels with "root" for display
        display_labels = [label if label else "root" for label in dir_labels]
        for key in display_labels + ["other"]:
            # Map back to actual key (empty string -> "")
            actual_key = key if key != "root" else ""
            items = grouped.get(actual_key, [])
            if not items:
                continue
            log_raw(f"    {key}: {len(items)}")
            for item in items:
                log_raw(f"      - {item}{_item_suffix(item)}")

    if actions["add"]:
        _log_group("add", add_grouped)
    if actions["modify"]:
        _log_group("modify", modify_grouped)
    if actions["delete"]:
        _log_group("delete", delete_grouped)


def log_verbose_refresh(actions, current_states, manifest_files) -> None:
    """Verbose diagnostics for refresh operations."""
    log("[VERBOSE]")
    log_raw(f"  Manifest entries: {len(manifest_files):,}")
    log_raw(f"  Current files:    {len(current_states):,}")

    def extension_counts(items):
        counts = {}
        for item in items:
            suffix = Path(item).suffix.lower() or "(none)"
            counts[suffix] = counts.get(suffix, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    for label, items in (
        ("add", actions["add"]),
        ("modify", actions["modify"]),
        ("delete", actions["delete"]),
    ):
        if not items:
            continue
        counts = extension_counts(items)
        top = ", ".join([f"{k}:{v}" for k, v in list(counts.items())[:6]])
        log_raw(f"  {label} extensions: {top}")

    def print_diff_samples(label, items, limit=5):
        if not items:
            return
        log_raw(f"  {label} samples:")
        for item in items[:limit]:
            current = current_states.get(item)
            previous = manifest_files.get(item)
            cur_mtime = int(current["mtime"]) if current else None
            cur_hash = current.get("hash") if current else None
            prev_mtime = int(previous.get("mtime", 0)) if previous else None
            prev_hash = previous.get("hash") if previous else None
            log_raw(
                f"    {item} | mtime {prev_mtime} -> {cur_mtime} | hash {prev_hash} -> {cur_hash}"
            )

    print_diff_samples("add", actions["add"])
    print_diff_samples("modify", actions["modify"])
    print_diff_samples("delete", actions["delete"])


# ────────────────────────────────────────────────
# Shared helpers for point construction and upsert
# (used by both single-pass pool flush and two-pass second pass)
# ────────────────────────────────────────────────


def _make_manifest_entry(file_info: dict, ids: list[str], **extra) -> dict:
    """Build a manifest entry dict for a processed file.

    Args:
        file_info: File state dict with 'file_path', 'mtime', 'hash'.
        ids: List of Qdrant point IDs for this file.
        **extra: Additional fields (e.g. empty=True, no_content=True).

    Returns:
        Manifest entry dict.
    """
    entry = {
        "file_path": file_info["file_path"],
        "mtime": file_info["mtime"],
        "hash": file_info["hash"],
        "vector_ids": ids,
    }
    entry.update(extra)
    return entry


def _sparse_dicts_to_vectors(
    sparse_dicts: list[dict],
) -> list:
    """Convert sparse embedding dicts to Qdrant SparseVector objects.

    Args:
        sparse_dicts: List of dicts with 'indices' and 'values' keys.

    Returns:
        List of qdrant_client.models.SparseVector.
    """
    from qdrant_client import models

    return [
        models.SparseVector(indices=d["indices"], values=d["values"])
        for d in sparse_dicts
    ]


def _build_qdrant_points(
    *,
    nodes_or_payloads,
    dense_vecs: list,
    ids: list[str],
    sparse_vectors: list | None,
    is_hybrid: bool,
    resolve_branch: Callable[[str], str | None],
    file_key: str,
    verbose: bool = False,
) -> tuple[list, int]:
    """Build Qdrant PointStruct objects from nodes/payloads and embeddings.

    Handles zero-vector skipping, payload construction with branch labels,
    and hybrid vs dense-only vector formatting.

    Args:
        nodes_or_payloads: Either a list of TextNode objects (single-pass) or
            a list of pre-built payload dicts (two-pass).  TextNodes have
            ``.get_content()`` and ``.metadata``; dicts have ``"text"`` key.
        dense_vecs: Dense embedding vectors (one per node/payload).
        ids: Qdrant point IDs (one per node/payload).
        sparse_vectors: SparseVector objects (one per node/payload), or None.
        is_hybrid: Whether to build hybrid vectors (dense + sparse).
        resolve_branch: Branch resolver callable.
        file_key: File key for logging and branch resolution.
        verbose: Whether to log zero-vector warnings.

    Returns:
        Tuple of (points, zero_vector_count).
    """
    from qdrant_client import models

    points = []
    zero_count = 0

    for i, (item, dense_vec, vid) in enumerate(zip(nodes_or_payloads, dense_vecs, ids)):
        if is_zero_vector(dense_vec):
            zero_count += 1
            if verbose:
                # Support both TextNode objects and pre-built payload dicts
                if hasattr(item, "get_content"):
                    text_preview = (item.get_content() or "")[:200]
                else:
                    text_preview = (item.get("text", "") or "")[:200]
                log_warn(
                    f"Skipping zero-vector node {vid} in {file_key}: {text_preview!r}"
                )
            continue

        # Build payload: TextNode (single-pass) vs dict (two-pass)
        if hasattr(item, "get_content"):
            text_value = item.get_content() or ""
            payload = {**item.metadata, "text": text_value}
        else:
            payload = dict(item)  # copy the pre-built payload

        file_branch = resolve_branch(file_key)
        if file_branch is not None:
            payload["branch"] = file_branch

        if is_hybrid and sparse_vectors is not None:
            vector = {
                "text-dense": dense_vec,
                "text-sparse-new": sparse_vectors[i],
            }
        else:
            vector = dense_vec

        point = models.PointStruct(id=vid, vector=vector, payload=payload)
        points.append(point)

    return points, zero_count


def _upsert_and_record(
    *,
    client,
    collection_name: str,
    points: list,
    file_key: str,
    ids: list[str],
    file_info: dict,
    action_type: str,
    manifest: dict,
    timing_tracker,
    verbose_label: str = "",
) -> tuple[bool, int]:
    """Upsert points to Qdrant and record in manifest.

    Args:
        client: Qdrant client.
        collection_name: Qdrant collection name.
        points: List of PointStruct objects to upsert.
        file_key: File key for logging and manifest.
        ids: All point IDs for this file (for manifest, may include skipped zeros).
        file_info: File state dict for manifest entry.
        action_type: 'add' or 'modify'.
        manifest: Manifest dict to update.
        timing_tracker: TimingTracker instance.
        verbose_label: Extra label for log messages (e.g. "hybrid ").

    Returns:
        Tuple of (success: bool, vectors_added: int).
    """
    upsert_batch_size = 500
    with timing_tracker.measure("upsert"):
        try:
            total_batches = (len(points) + upsert_batch_size - 1) // upsert_batch_size
            for batch_idx in range(total_batches):
                start_idx = batch_idx * upsert_batch_size
                end_idx = min(start_idx + upsert_batch_size, len(points))
                batch = points[start_idx:end_idx]
                client.upsert(collection_name=collection_name, points=batch)
            log(f"  Added {len(points)} {verbose_label}vectors for {file_key}")
            manifest["files"][file_key] = _make_manifest_entry(file_info, ids)
            return True, len(points)
        except Exception as e:
            log_error(f"Adding {file_key}: {e}")
            return False, 0


def perform_refresh_qdrant(
    actions,
    manifest,
    branch_label=None,
    file_states=None,
    point_id_fn=None,
    save_fn=None,
):
    """Perform refresh operations on Qdrant DB.

    This is the **single embedding pipeline** used by both main-branch and
    branch-overlay indexing.  Branch overlays call it with explicit
    ``branch_label``, ``file_states``, ``point_id_fn``, and ``save_fn``
    so that branch-namespaced IDs and branch manifests are used — but the
    actual embedding logic (single-pass or two-pass, dense + sparse,
    sanitisation, truncation checks, etc.) is identical.

    Args:
        actions: Dict with 'add', 'modify', 'delete' lists of file keys.
        manifest: Manifest dict with 'files' entry.
        branch_label: If provided, sets the ``branch`` payload field on all
            upserted points.  ``None`` means auto-detect from config: git-backed
            files get their main_branch name, non-git files get no branch field.
        file_states: Pre-built file states dict (file_key → info).  When
            ``None``, calls ``get_current_file_states()`` (main-branch path).
        point_id_fn: Callable ``(file_key, index) -> str`` for point ID
            generation.  Defaults to ``make_qdrant_point_id``.
        save_fn: Callable ``(manifest) -> None`` for periodic manifest saves.
            Defaults to the module-level ``save_manifest``.
    """
    from qdrant_client import models
    from qdrant_client.http.exceptions import UnexpectedResponse
    from qdrant.vector_store import get_sparse_encoder, detect_collection_mode

    client = get_qdrant_client(config)

    # Probe Qdrant connectivity before loading the embedding model (which takes ~60s).
    # This fails fast if Qdrant is unreachable, avoiding wasted model load time.
    qdrant_url = get_qdrant_url(config)
    try:
        client.get_collections()
        log(f"Qdrant connected: {qdrant_url}")
    except Exception as exc:
        log_error(f"Cannot reach Qdrant at {qdrant_url} - {exc}")
        log_error("Start Qdrant first: scripts\\start_qdrant.bat <config_name>")
        return

    embed_model = get_embed_model(device=config.INDEX_EMBED_DEVICE, cfg=config)
    indexing_mode = getattr(config, "INDEXING_MODE", "dense")
    single_pass = getattr(config, "HYBRID_EMBED_SINGLE_PASS", True)

    # ── Branch label resolution ──────────────────────────────────
    # When branch_label is explicit, all points get that label.
    # Otherwise, resolve per-file from config source entries.
    _resolve_branch = build_branch_resolver(
        fixed_label=branch_label if branch_label is not None else _SENTINEL
    )

    # Get sparse encoder if needed (only for single-pass mode, or for two-pass after model switch)
    sparse_fn = None
    if indexing_mode in ("hybrid", "sparse") and single_pass:
        sparse_fn = get_sparse_encoder(cfg=config, device=config.INDEX_EMBED_DEVICE)

    def get_embedding_dim() -> int:
        probe = embed_model.get_text_embedding("dimension probe")
        if hasattr(probe, "tolist"):
            probe = probe.tolist()
        return len(probe)

    # Detect existing collection mode or create with correct schema
    collection_mode = detect_collection_mode(client, config.COLLECTION_NAME)
    is_hybrid = collection_mode == "hybrid" or (
        collection_mode == "unknown" and indexing_mode in ("hybrid", "sparse")
    )

    try:
        client.get_collection(collection_name=config.COLLECTION_NAME)
        # Collection exists — check provenance before proceeding
        check_provenance_for_indexing(client, config.COLLECTION_NAME, config)
    except UnexpectedResponse as exc:
        if "doesn't exist" in str(exc) or "Not found" in str(exc):
            dim = get_embedding_dim()
            if indexing_mode in ("hybrid", "sparse"):
                # Create collection with named dense + sparse vectors
                client.create_collection(
                    collection_name=config.COLLECTION_NAME,
                    vectors_config={
                        "text-dense": models.VectorParams(
                            size=dim, distance=models.Distance.COSINE
                        ),
                    },
                    sparse_vectors_config={
                        "text-sparse-new": models.SparseVectorParams(
                            index=models.SparseIndexParams(),
                        ),
                    },
                )
                is_hybrid = True
                log(f"Created hybrid collection '{config.COLLECTION_NAME}' (dim={dim})")
            else:
                client.create_collection(
                    collection_name=config.COLLECTION_NAME,
                    vectors_config=models.VectorParams(
                        size=dim, distance=models.Distance.COSINE
                    ),
                )
                log(f"Created collection '{config.COLLECTION_NAME}' (dim={dim})")
            # Store provenance on newly created collection
            set_collection_provenance(
                client,
                config.COLLECTION_NAME,
                get_embed_backend_family(config),
                dim,
            )
        else:
            raise

    current_states = (
        file_states if file_states is not None else get_current_file_states()
    )
    _save = save_fn if save_fn is not None else save_manifest
    _make_id = point_id_fn if point_id_fn is not None else make_qdrant_point_id
    fallback_files = []
    empty_files = []
    no_content_files = []
    save_batch_size = 10
    processed_since_save = 0

    # --- Counters for final summary ---
    total_vectors_added = 0
    total_vectors_deleted = 0
    total_files_added = 0
    total_files_modified = 0
    total_files_deleted = 0
    total_files_errored = 0
    total_zero_vectors_skipped = 0
    ext_node_counts: dict[str, int] = {}
    ext_file_counts: dict[str, int] = {}
    truncation_stats = TruncationStats()

    def _delete_vectors_for_file(file_key: str) -> None:
        """Delete all Qdrant points matching a file path.

        Uses an exact match on the canonical file_key produced by
        ``normalize_file_key()`` — keys are already in their final canonical
        form (using last path segment or map_to_path), no further mapping needed.

        When ``branch_label`` is set, also filters by branch so that only
        the overlay vectors are deleted (main-branch vectors are preserved).
        """
        must_conditions: list = [
            models.FieldCondition(
                key="file_path",
                match=models.MatchValue(value=file_key),
            )
        ]
        if branch_label is not None:
            must_conditions.append(
                models.FieldCondition(
                    key="branch",
                    match=models.MatchValue(value=branch_label),
                )
            )
        selector = models.Filter(must=must_conditions)
        delete_timeout = getattr(config, "QDRANT_DELETE_TIMEOUT", 60)
        client.delete(
            collection_name=config.COLLECTION_NAME,
            points_selector=selector,
            timeout=delete_timeout,
        )

    # Handle deletes first
    for file_key in actions["delete"]:
        try:
            _delete_vectors_for_file(file_key)
            total_files_deleted += 1
            old_ids = manifest["files"].get(file_key, {}).get("vector_ids", [])
            total_vectors_deleted += len(old_ids)
            log(f"Deleted vectors for {file_key}")
        except Exception as e:
            total_files_errored += 1
            log_error(f"Deleting vectors for {file_key}: {e}")

        if file_key in manifest["files"]:
            del manifest["files"][file_key]

    if actions["delete"]:
        _save(manifest)

    # Handle adds and modifies
    files_to_process = actions["add"] + actions["modify"]
    total_files = len(files_to_process)

    # ── Cross-file chunk pooling ─────────────────────────────────
    pool_size = int(getattr(config, "EMBED_POOL_SIZE", 512))
    pool_max_files = int(getattr(config, "EMBED_POOL_MAX_FILES", 150))
    pool = ChunkPool(max_chunks=pool_size, max_files=pool_max_files)
    histogram = ChunkHistogram()

    # ── Double-buffered upsert (Phase 2) ─────────────────────────
    # Background thread handles Qdrant upsert I/O while the main thread
    # embeds the next pool.  At most one upsert in flight at a time.
    _upsert_executor = ThreadPoolExecutor(
        max_workers=1, thread_name_prefix="upsert-worker"
    )
    _pending_upsert: Future | None = None

    def _drain_pending_upsert() -> None:
        """Block until the previous background upsert completes.

        Must be called before starting the next embedding pass or saving
        the manifest, to ensure all counters and manifest entries are
        up-to-date.  Re-raises any exception from the background thread.
        """
        nonlocal _pending_upsert
        nonlocal total_vectors_added, total_files_added, total_files_modified
        nonlocal total_files_errored, total_zero_vectors_skipped
        nonlocal processed_since_save

        if _pending_upsert is None:
            return
        try:
            result = _pending_upsert.result()
            # Apply deferred counter updates from the background thread
            total_vectors_added += result["vectors_added"]
            total_files_added += result["files_added"]
            total_files_modified += result["files_modified"]
            total_files_errored += result["files_errored"]
            total_zero_vectors_skipped += result["zero_vectors_skipped"]
            processed_since_save += result["files_processed"]
            if processed_since_save >= save_batch_size:
                _save(manifest)
                processed_since_save = 0
        except Exception:
            log_error("[upsert-worker] Background upsert failed — see above")
            raise
        finally:
            _pending_upsert = None

    def _flush_pool() -> None:
        """Embed all pooled chunks cross-file, then submit upsert to background thread.

        Phase 2 double-buffer: embedding runs on the main thread (GPU-bound
        critical path), while the previous pool's upsert runs on a background
        thread (I/O-bound, releases GIL).  ``_drain_pending_upsert()`` is
        called first to ensure the previous upsert finished before we start
        modifying counters or the manifest.
        """
        nonlocal _pending_upsert

        if pool.is_empty:
            return

        # ── Step 1: Drain previous background upsert ─────────────
        _drain_pending_upsert()

        all_docs, file_entries = pool.collect()
        pool_chunks = len(all_docs)
        pool_files = pool.file_count
        log(f"Flushing pool: {pool_chunks:,} chunks from {pool_files} files")

        # ── Step 2: Dense embedding (main thread, GPU-bound) ─────
        with timing_tracker.measure("embedding"):

            def progress_cb(embedded, total):
                if VERBOSE:
                    log(f"  Pool embedded {embedded}/{total} nodes")

            dense_embeddings = embed_dense_batch(
                embed_model,
                all_docs,
                progress_callback=progress_cb,
                cfg=config,
            )

        dense_embeddings = list(dense_embeddings)

        # Sanitize dense vectors (replace -0.0/NaN/Inf with 0.0)
        dense_embeddings, fix_counts = sanitize_dense_vectors(dense_embeddings)

        # Log all-zero vectors
        offset = 0
        for entry in pool.files():
            for i in range(len(entry.documents)):
                global_i = offset + i
                if fix_counts[global_i] > 0 and is_zero_vector(
                    dense_embeddings[global_i]
                ):
                    text_preview = (entry.nodes[i].get_content() or "")[:200]
                    log_warn(
                        f"All-zero dense vector for node {i} "
                        f"in {entry.file_key}: {text_preview!r}"
                    )
            offset += len(entry.documents)

        # ── Step 3: Sparse embedding (main thread, CPU-bound) ────
        sparse_dicts_all = None
        if is_hybrid and sparse_fn is not None:
            with timing_tracker.measure("sparse_embedding"):

                def sparse_progress_cb(embedded, total):
                    if VERBOSE:
                        log(f"  Pool sparse embedded {embedded}/{total} nodes")

                sparse_dicts_all = embed_sparse_batch(
                    sparse_fn,
                    all_docs,
                    progress_callback=sparse_progress_cb,
                    cfg=config,
                )

        # ── Step 4: Build per-file upsert work items (main thread, CPU) ──
        per_file_results = pool.distribute(dense_embeddings, sparse_dicts_all)

        upsert_work_items: list[dict] = []
        for entry, file_dense, file_sparse in per_file_results:
            # Build sparse vectors for this file
            file_sparse_vectors = None
            if file_sparse is not None:
                file_sparse_vectors = _sparse_dicts_to_vectors(file_sparse)

            # Build Qdrant points
            points, zero_count = _build_qdrant_points(
                nodes_or_payloads=entry.nodes,
                dense_vecs=file_dense,
                ids=entry.ids,
                sparse_vectors=file_sparse_vectors,
                is_hybrid=is_hybrid,
                resolve_branch=_resolve_branch,
                file_key=entry.file_key,
                verbose=VERBOSE,
            )

            upsert_work_items.append(
                {
                    "points": points,
                    "zero_count": zero_count,
                    "file_key": entry.file_key,
                    "ids": entry.ids,
                    "file_info": entry.file_info,
                    "action_type": entry.action_type,
                }
            )

        # ── Step 5: Submit upsert to background thread ───────────
        # The background thread handles Qdrant I/O (releases GIL) while
        # the main thread continues parsing/chunking the next pool.
        _pending_upsert = _upsert_executor.submit(
            _do_background_upsert, upsert_work_items
        )

        # Cleanup pool immediately — data is captured in upsert_work_items
        pool.clear()
        gc.collect()
        cuda_clear_cache()

    def _do_background_upsert(work_items: list[dict]) -> dict:
        """Execute per-file upserts on the background thread.

        Returns a dict of counter deltas to be applied by the main thread
        in ``_drain_pending_upsert()``.  This avoids concurrent writes to
        the nonlocal counters.

        All log messages are prefixed with [upsert-worker].
        """
        counters = {
            "vectors_added": 0,
            "files_added": 0,
            "files_modified": 0,
            "files_errored": 0,
            "zero_vectors_skipped": 0,
            "files_processed": 0,
        }
        upsert_batch_size = 500

        for item in work_items:
            points = item["points"]
            file_key = item["file_key"]
            ids = item["ids"]
            file_info = item["file_info"]
            action_type = item["action_type"]
            zero_count = item["zero_count"]

            counters["zero_vectors_skipped"] += zero_count

            with timing_tracker.measure("upsert"):
                try:
                    total_batches = (
                        len(points) + upsert_batch_size - 1
                    ) // upsert_batch_size
                    for batch_idx in range(total_batches):
                        start_idx = batch_idx * upsert_batch_size
                        end_idx = min(start_idx + upsert_batch_size, len(points))
                        batch = points[start_idx:end_idx]
                        client.upsert(
                            collection_name=config.COLLECTION_NAME, points=batch
                        )
                    log(f"  [upsert-worker] Added {len(points)} vectors for {file_key}")
                    manifest["files"][file_key] = _make_manifest_entry(file_info, ids)
                    counters["vectors_added"] += len(points)
                    if action_type == "add":
                        counters["files_added"] += 1
                    else:
                        counters["files_modified"] += 1
                except Exception as e:
                    log_error(f"[upsert-worker] Adding {file_key}: {e}")
                    counters["files_errored"] += 1

            counters["files_processed"] += 1

        return counters

    # Two-pass hybrid embedding: initialize SQLite for dense vector storage
    sqlite_db_path: Path = None  # type: ignore[assignment]
    file_node_ids_map: dict[str, list[str]] = {}  # file_key -> list of node_ids
    files_for_second_pass: list[
        tuple
    ] = []  # (file_key, ids, file_info, action_type) — no documents, texts in SQLite payload
    if is_hybrid and not single_pass:
        sqlite_db_path = get_sqlite_path(config.get_index_path())
        init_sqlite_db(sqlite_db_path)
        log(f"Initialized temp SQLite store for dense vectors: {sqlite_db_path}")
    for file_index, file_key in enumerate(files_to_process, start=1):
        action_type = "add" if file_key in actions["add"] else "modify"
        # Remove old points if modify
        if action_type == "modify" and file_key in manifest["files"]:
            try:
                old_ids = manifest["files"][file_key].get("vector_ids", [])
                total_vectors_deleted += len(old_ids)
                _delete_vectors_for_file(file_key)
            except Exception as e:
                log_error(f"Deleting old vectors for {file_key}: {e}")

        # Load and add new content
        file_info = current_states.get(file_key)
        if not file_info:
            continue

        file_branch = _resolve_branch(file_key)
        branch_tag = f" [{file_branch}]" if file_branch else ""
        log(f"Processing ({file_index}/{total_files}) {file_key}{branch_tag}...")

        # Track per-operation timing
        with timing_tracker.measure("parse_file"):
            nodes = load_nodes_for_file(file_info)

        if not nodes:
            try:
                if Path(file_info["full_path"]).stat().st_size == 0:
                    empty_files.append(file_key)
                    manifest["files"][file_key] = _make_manifest_entry(
                        file_info, [], empty=True
                    )
                else:
                    no_content_files.append(file_key)
                    manifest["files"][file_key] = _make_manifest_entry(
                        file_info, [], no_content=True
                    )
            except Exception:
                no_content_files.append(file_key)
            log_warn(f"No content loaded for {file_key}")
            continue

        if any(node.metadata.get("parse_error") for node in nodes):
            fallback_files.append(file_key)

        if VERBOSE:
            log(f"  Nodes: {len(nodes)}")

        # Track extension stats
        ext = Path(file_key).suffix.lower() or "(none)"
        ext_file_counts[ext] = ext_file_counts.get(ext, 0) + 1
        ext_node_counts[ext] = ext_node_counts.get(ext, 0) + len(nodes)

        ids = [_make_id(file_key, i) for i in range(len(nodes))]
        documents = [node.text for node in nodes]

        # Collect histogram data (char lengths always, token lengths when available)
        histogram.add_char_lengths([len(d) for d in documents])
        histogram.increment_files()

        # Check for truncation: the tokenizer's max_length cap silently
        # truncates long chunks.  Track what's being lost.
        file_trunc = check_truncation(embed_model, documents, verbose=VERBOSE)
        truncation_stats.merge(file_trunc)
        # Collect token lengths from truncation stats (available for non-TEI models)
        if file_trunc.token_lengths:
            histogram.add_token_lengths(file_trunc.token_lengths)
        if file_trunc.truncated_chunks > 0:
            if VERBOSE:
                for info in file_trunc.truncated_details:
                    log_warn(
                        f"  Chunk {info.index} truncated: "
                        f"{info.token_count:,} tokens -> {info.max_length:,} "
                        f"({info.char_count:,} chars) | {info.text_preview!r}"
                    )
            elif file_trunc.truncated_chunks >= 3:
                log_warn(
                    f"  {file_trunc.truncated_chunks} chunks truncated "
                    f"(max_length={file_trunc.max_length}, "
                    f"use --verbose for details)"
                )

        # ── Two-pass path: embed per-file (pool not used) ────────
        if is_hybrid and not single_pass:
            with timing_tracker.measure("embedding"):

                def progress_cb(embedded, total):
                    if VERBOSE:
                        log(f"  Embedded {embedded}/{total} nodes")

                # Two-pass: flush dense vectors to SQLite after each batch to save RAM
                def on_dense_batch(original_indices: list, batch_embs: list) -> None:
                    nonlocal total_zero_vectors_skipped

                    # Fix 1: sanitize dense vectors (replace -0.0/NaN/Inf with 0.0)
                    batch_embs, fix_counts = sanitize_dense_vectors(batch_embs)

                    # Log individual all-zero vectors (entire vector was bad)
                    for pos, (idx, fc) in enumerate(zip(original_indices, fix_counts)):
                        if fc > 0 and is_zero_vector(batch_embs[pos]):
                            text_preview = (nodes[idx].get_content() or "")[:200]
                            log_warn(
                                f"All-zero dense vector for node {idx} "
                                f"in {file_key}: {text_preview!r}"
                            )

                    with timing_tracker.measure("dense_save_sqlite"):
                        node_data = []
                        for idx, dense_vec in zip(original_indices, batch_embs):
                            vid = ids[idx]
                            text_value = nodes[idx].get_content() or ""
                            payload = {**nodes[idx].metadata, "text": text_value}
                            # Add branch label (same logic as single-pass path)
                            file_branch = _resolve_branch(file_key)
                            if file_branch is not None:
                                payload["branch"] = file_branch
                            # file_path is already in canonical form (no mapping needed)
                            node_data.append((vid, dense_vec, payload))
                        save_dense_vectors_sqlite(sqlite_db_path, node_data)

                embeddings = embed_dense_batch(
                    embed_model,
                    documents,
                    progress_callback=progress_cb,
                    on_batch=on_dense_batch,
                    cfg=config,
                )

            file_node_ids_map[file_key] = ids
            files_for_second_pass.append((file_key, ids, file_info, action_type))
            log(f"  Saved {len(ids)} dense vectors to SQLite for {file_key}")
            # Inter-file cleanup: free large per-file objects and reclaim VRAM
            del nodes, documents, embeddings, ids
            gc.collect()
            cuda_clear_cache()
            processed_since_save += 1
            if processed_since_save >= save_batch_size:
                _save(manifest)
                processed_since_save = 0
            continue

        # ── Single-pass path: add to cross-file pool ─────────────
        pool.add(file_key, file_info, nodes, ids, documents, action_type)

        if pool.should_flush():
            _flush_pool()

    # Final flush for remaining chunks in the pool
    _flush_pool()

    # Drain the last background upsert and shut down the executor
    try:
        _drain_pending_upsert()
    finally:
        _upsert_executor.shutdown(wait=True)
    if processed_since_save > 0:
        _save(manifest)
        processed_since_save = 0

    # Two-pass hybrid embedding: second pass for sparse embedding + upsert
    if is_hybrid and not single_pass and files_for_second_pass:
        with timing_tracker.measure("model_unload"):
            del embed_model
            embed_model = None
            cuda_clear_cache()
            gc.collect()
        log("Dense model unloaded, VRAM freed")

        with timing_tracker.measure("sparse_model_load"):
            from qdrant.vector_store import get_sparse_encoder

            sparse_fn = get_sparse_encoder(cfg=config, device=config.INDEX_EMBED_DEVICE)
        log("Sparse model loaded")

        total_files_2nd_pass = len(files_for_second_pass)
        for file_index_2nd, (
            file_key,
            ids,
            file_info,
            action_type,
        ) in enumerate(files_for_second_pass, start=1):
            file_branch_2nd = _resolve_branch(file_key)
            branch_tag_2nd = f" [{file_branch_2nd}]" if file_branch_2nd else ""
            log(
                f"Sparse embedding ({file_index_2nd}/{total_files_2nd_pass}) {file_key}{branch_tag_2nd}..."
            )

            with timing_tracker.measure("dense_read_sqlite"):
                dense_data = read_dense_vectors_sqlite(sqlite_db_path, ids)
                if len(dense_data) != len(ids):
                    log_warn(f"Missing dense vectors for some nodes in {file_key}")

            # Reconstruct document texts from SQLite payload for sparse embedding
            documents = [
                dense_data[vid][1].get("text", "") if vid in dense_data else ""
                for vid in ids
            ]

            with timing_tracker.measure("sparse_embedding"):

                def progress_cb(embedded, total):
                    if VERBOSE:
                        log(f"  Sparse embedded {embedded}/{total} nodes")

                sparse_dicts = embed_sparse_batch(
                    sparse_fn,
                    documents,
                    progress_callback=progress_cb,
                    cfg=config,
                )
                sparse_vectors = _sparse_dicts_to_vectors(sparse_dicts)

            # Build payloads and dense vecs in ID order for _build_qdrant_points
            payloads_ordered = []
            dense_vecs_ordered = []
            for vid in ids:
                if vid in dense_data:
                    dense_vec, payload = dense_data[vid]
                    payloads_ordered.append(payload)
                    dense_vecs_ordered.append(dense_vec)
                else:
                    # Missing — placeholder (will be skipped as zero vector)
                    payloads_ordered.append({"text": ""})
                    dense_vecs_ordered.append([0.0])

            points, zero_count = _build_qdrant_points(
                nodes_or_payloads=payloads_ordered,
                dense_vecs=dense_vecs_ordered,
                ids=ids,
                sparse_vectors=sparse_vectors,
                is_hybrid=True,
                resolve_branch=_resolve_branch,
                file_key=file_key,
                verbose=VERBOSE,
            )
            total_zero_vectors_skipped += zero_count

            success, vectors_added = _upsert_and_record(
                client=client,
                collection_name=config.COLLECTION_NAME,
                points=points,
                file_key=file_key,
                ids=ids,
                file_info=file_info,
                action_type=action_type,
                manifest=manifest,
                timing_tracker=timing_tracker,
                verbose_label="hybrid ",
            )
            if success:
                total_vectors_added += vectors_added
                if action_type == "add":
                    total_files_added += 1
                else:
                    total_files_modified += 1
            else:
                total_files_errored += 1

            processed_since_save += 1
            if processed_since_save >= save_batch_size:
                _save(manifest)
                processed_since_save = 0

        with timing_tracker.measure("sqlite_cleanup"):
            cleanup_sqlite(sqlite_db_path)
        log("Temp SQLite store cleaned up")

    _save(manifest)
    log("Refresh completed")

    # ── Save chunk histogram ─────────────────────────────────────
    if histogram.total_chunks > 0:
        try:
            hist_path = histogram.save(
                index_path=config.get_index_path(),
                config_name=config.COLLECTION_NAME,
                model_name=getattr(config, "MODEL_NAME", "unknown"),
                branch=branch_label or "",
            )
            log(f"Chunk histogram saved to {hist_path}")
        except Exception as e:
            log_warn(f"Failed to save chunk histogram: {e}")
        histogram.log_summary()

    # ── Print final summary ──────────────────────────────────────
    _print_refresh_summary(
        actions=actions,
        manifest=manifest,
        client=client,
        total_vectors_added=total_vectors_added,
        total_vectors_deleted=total_vectors_deleted,
        total_files_added=total_files_added,
        total_files_modified=total_files_modified,
        total_files_deleted=total_files_deleted,
        total_files_errored=total_files_errored,
        ext_file_counts=ext_file_counts,
        ext_node_counts=ext_node_counts,
        fallback_files=fallback_files,
        empty_files=empty_files,
        no_content_files=no_content_files,
        is_hybrid=is_hybrid,
        total_zero_vectors_skipped=total_zero_vectors_skipped,
        truncation_stats=truncation_stats,
    )

    timing_tracker.print_summary()


def _print_refresh_summary(
    *,
    actions,
    manifest,
    client,
    total_vectors_added: int,
    total_vectors_deleted: int,
    total_files_added: int,
    total_files_modified: int,
    total_files_deleted: int,
    total_files_errored: int,
    ext_file_counts: dict,
    ext_node_counts: dict,
    fallback_files: list,
    empty_files: list,
    no_content_files: list,
    is_hybrid: bool,
    total_zero_vectors_skipped: int = 0,
    truncation_stats: TruncationStats | None = None,
) -> None:
    """Print a comprehensive post-indexing summary."""

    # Query Qdrant for final collection stats
    try:
        collection_info = client.get_collection(collection_name=config.COLLECTION_NAME)
        final_points = collection_info.points_count
        collection_status = str(collection_info.status)
    except Exception:
        final_points = "?"
        collection_status = "unknown"

    manifest_files = len(manifest.get("files", {}))

    log_raw()
    log_raw("=" * 70)
    log_raw("INDEXING SUMMARY")
    log_raw("=" * 70)
    log_raw()
    log_raw(f"  Collection:          {config.COLLECTION_NAME}")
    log_raw(f"  Mode:                {'hybrid' if is_hybrid else 'dense'}")
    log_raw(f"  Qdrant:              {config.QDRANT_HOST}:{config.QDRANT_PORT}")
    log_raw(f"  Status:              {collection_status}")
    log_raw()
    log_raw("-" * 70)
    log_raw("  CHANGES")
    log_raw("-" * 70)
    log_raw(f"  Files added:         {total_files_added:>10,}")
    log_raw(f"  Files modified:      {total_files_modified:>10,}")
    log_raw(f"  Files deleted:       {total_files_deleted:>10,}")
    log_raw(f"  Files errored:       {total_files_errored:>10,}")
    log_raw(f"  Vectors added:       {total_vectors_added:>10,}")
    log_raw(f"  Vectors deleted:     {total_vectors_deleted:>10,}")
    log_raw()
    log_raw("-" * 70)
    log_raw("  COLLECTION TOTALS")
    log_raw("-" * 70)
    log_raw(f"  Total points:        {final_points:>10,}")
    log_raw(f"  Manifest files:      {manifest_files:>10,}")

    # Per-extension breakdown (only if we processed files)
    if ext_file_counts:
        log_raw()
        log_raw("-" * 70)
        log_raw("  PROCESSED BY EXTENSION")
        log_raw("-" * 70)
        for ext in sorted(ext_file_counts):
            fc = ext_file_counts[ext]
            nc = ext_node_counts.get(ext, 0)
            log_raw(f"    {ext:12s}  {fc:>6,} files  {nc:>8,} nodes")

    # Embedding truncation section
    ts = truncation_stats
    if ts is not None and ts.total_chunks > 0:
        log_raw()
        log_raw("-" * 70)
        log_raw("  EMBEDDING TRUNCATION")
        log_raw("-" * 70)
        log_raw("  The embedding model has a hard token limit (max sequence length).")
        log_raw("  Chunks longer than this limit are silently cut off at the cap —")
        log_raw("  tokens beyond the limit are not embedded and are invisible to")
        log_raw("  semantic search.  Truncated chunks will still match BM25 keyword")
        log_raw("  search but dense/hybrid recall may be degraded for content that")
        log_raw("  falls past the cut point.")
        log_raw()
        log_raw(f"  Max sequence length:   {ts.max_length:>10,} tokens")
        log_raw(f"  Total chunks:          {ts.total_chunks:>10,}")
        log_raw(f"  Truncated chunks:      {ts.truncated_chunks:>10,}")
        if ts.truncated_chunks > 0:
            pct_chunks = 100.0 * ts.truncated_chunks / ts.total_chunks
            log_raw(
                f"  Truncated %:           {pct_chunks:>9.1f}%  (share of chunks that were cut)"
            )
            log_raw()
            log_raw("  Of the truncated chunks only:")
            log_raw(
                f"  Tokens before cap:     {ts.total_tokens_before:>10,}  (actual chunk length)"
            )
            log_raw(
                f"  Tokens after cap:      {ts.total_tokens_after:>10,}  (what was embedded)"
            )
            log_raw(
                f"  Tokens removed by cap: {ts.tokens_lost:>10,}  (content lost to truncation)"
            )
            log_raw(
                f"  Cap removal %:         {ts.truncation_pct:>9.2f}%  (tokens lost / tokens before)"
            )

    # Warnings section
    has_warnings = (
        fallback_files
        or empty_files
        or no_content_files
        or total_zero_vectors_skipped > 0
    )
    if has_warnings:
        log_raw()
        log_raw("-" * 70)
        log_raw("  WARNINGS")
        log_raw("-" * 70)

    if fallback_files:
        log_raw(f"  Parse errors (full-file fallback):  {len(fallback_files)}")
        counts: dict[str, int] = {}
        for path in fallback_files:
            suffix = Path(path).suffix.lower() or "(none)"
            counts[suffix] = counts.get(suffix, 0) + 1
        for suffix, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            log_raw(f"    {suffix}: {count}")

    if empty_files:
        log_raw(f"  Empty files (0 bytes):              {len(empty_files)}")

    if no_content_files:
        log_raw(f"  No content extracted:               {len(no_content_files)}")

    if total_zero_vectors_skipped > 0:
        log_raw(f"  Zero-vector nodes skipped:          {total_zero_vectors_skipped}")

    if total_files_errored > 0:
        log_raw(f"  Errors:                             {total_files_errored}")

    log_raw()
    log_raw("=" * 70)
    log_raw()


parser = argparse.ArgumentParser(description="RAG Indexer")
parser.add_argument(
    "--config",
    help="Config name (e.g., 'self-index') or path to config file",
)
parser.add_argument(
    "--regenerate-manifest",
    action="store_true",
    help="Regenerate manifest from existing index (one-time bootstrap)",
)
parser.add_argument(
    "--verbose",
    action="store_true",
    help="Print verbose refresh diagnostics",
)
parser.add_argument(
    "--clear",
    action="store_true",
    help="Clear the vector collection and manifest before indexing (requires --yes)",
)
parser.add_argument(
    "--yes",
    action="store_true",
    help="Skip all confirmations (use with --clear)",
)
parser.add_argument(
    "--log-to-file",
    action="store_true",
    help="Also log to a timestamped file in the index directory",
)
parser.add_argument(
    "--collect-perf-stats",
    action="store_true",
    help="Collect GPU stats via nvidia-smi during indexing (CUDA only)",
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Compute file actions without embedding (diagnostic mode)",
)
parser.add_argument(
    "--calculate-histogram",
    action="store_true",
    help=(
        "Generate chunk histograms without embedding or Qdrant. "
        "Reads all source files, runs them through the reader pipeline, "
        "and saves chunk_histogram.json (and per-branch variants). "
        "No embedding model or Docker containers are needed."
    ),
)
args = parser.parse_args()

config = config_loader.get_config(config_path=args.config)

VERBOSE = args.verbose

# Initialize timing tracker with verbose setting
timing_tracker = TimingTracker(verbose=VERBOSE)

# --log-to-file: tee all output to a timestamped log file in the index directory
if args.log_to_file:
    from shared.log import configure_tee

    _log_ts = datetime.now().strftime("%Y%m%d%H%M%S")
    _log_file = Path(config.get_index_path()) / f"index_rag_{_log_ts}.log"
    _log_file.parent.mkdir(parents=True, exist_ok=True)
    configure_tee(str(_log_file))
    log(f"Logging to file: {_log_file}")


def run_dry_run():
    """Run in dry-run mode: compute file actions without embedding."""
    from config_loader import get_repo_groups, resolve_source_entries
    from shared.manifest import (
        compute_file_hash,
        is_excluded,
        normalize_file_key,
    )

    log("[DRY-RUN] Computing file actions without embedding...")
    log_raw()

    manifest = load_manifest()
    if manifest is None:
        log("No manifest found - will index all files")
        old_files = {}
    else:
        old_files = manifest.get("files", {})
        log(f"Loaded manifest with {len(old_files)} entries")

    current_states = get_current_file_states()
    log(f"Scanned {len(current_states)} files on disk")

    actions = determine_actions(old_files, current_states, manifest=manifest)

    log_raw()
    log_raw("=" * 70)
    log_raw("DRY-RUN RESULTS")
    log_raw("=" * 70)
    log_raw(f"  Files to ADD:     {len(actions['add']):6d}")
    log_raw(f"  Files to MODIFY:  {len(actions['modify']):6d}")
    log_raw(f"  Files to DELETE:  {len(actions['delete']):6d}")
    log_raw("-" * 70)

    if actions["add"]:
        log_raw(f"\n  ADD ({len(actions['add'])} files):")
        for f in sorted(actions["add"])[:20]:
            log_raw(f"    + {f}")
        if len(actions["add"]) > 20:
            log_raw(f"    ... and {len(actions['add']) - 20} more")

    if actions["modify"]:
        log_raw(f"\n  MODIFY ({len(actions['modify'])} files):")
        for f in sorted(actions["modify"])[:20]:
            current = current_states.get(f)
            old_entry = old_files.get(f)
            cur_hash = current.get("hash", "")[:12] if current else "N/A"
            old_hash = old_entry.get("hash", "")[:12] if old_entry else "N/A"
            cur_mtime = int(current.get("mtime", 0)) if current else 0
            old_mtime = int(old_entry.get("mtime", 0)) if old_entry else 0
            hash_diff = (
                "HASH"
                if (
                    current
                    and old_entry
                    and current.get("hash") != old_entry.get("hash")
                )
                else ""
            )
            mtime_diff = "MTIME" if cur_mtime != old_mtime else ""
            reason = ", ".join([r for r in [hash_diff, mtime_diff] if r])
            log_raw(f"    M {f}")
            log_raw(f"       old: mtime={old_mtime} hash={old_hash}")
            log_raw(f"       new: mtime={cur_mtime} hash={cur_hash} [{reason}]")
        if len(actions["modify"]) > 20:
            log_raw(f"    ... and {len(actions['modify']) - 20} more")

    if actions["delete"]:
        log_raw(f"\n  DELETE ({len(actions['delete'])} files):")
        for f in sorted(actions["delete"])[:20]:
            log_raw(f"    - {f}")
        if len(actions["delete"]) > 20:
            log_raw(f"    ... and {len(actions['delete']) - 20} more")

    log_raw()
    log_raw("=" * 70)
    log_raw()
    log("[DRY-RUN] Complete. No embeddings were created.")
    sys.exit(0)


def run_calculate_histogram():
    """Generate chunk histograms without embedding or Qdrant.

    Reads all source files through the reader pipeline (chunking only),
    collects character length distributions, and saves histogram JSON files.
    No embedding model, no Docker containers, no Qdrant needed.

    For branch overlays, reads changed files via git and generates separate
    per-branch histogram files (``chunk_histogram_branch_<name>.json``).
    """
    from config_loader import get_repo_groups

    log("[HISTOGRAM] Generating chunk histograms (no embedding)...")
    log_raw()

    # ── Main branch histogram ──
    current_states = get_current_file_states()
    log(f"[HISTOGRAM] Scanned {len(current_states)} source files")

    histogram = ChunkHistogram()
    errored = 0

    for i, (file_key, file_info) in enumerate(sorted(current_states.items()), 1):
        if i % 500 == 0 or i == len(current_states):
            log(f"[HISTOGRAM] Processing file {i}/{len(current_states)}...")
        try:
            nodes = load_nodes_for_file(file_info)
            if nodes:
                histogram.add_char_lengths([len(node.text) for node in nodes])
                histogram.increment_files()
        except Exception as e:
            errored += 1
            if errored <= 5:
                log_warn(f"[HISTOGRAM] Failed to chunk {file_key}: {e}")
            elif errored == 6:
                log_warn("[HISTOGRAM] Suppressing further chunk errors...")

    if histogram.total_chunks > 0:
        hist_path = histogram.save(
            index_path=config.get_index_path(),
            config_name=config.COLLECTION_NAME,
            model_name=getattr(config, "MODEL_NAME", "unknown"),
        )
        log(f"[HISTOGRAM] Main branch histogram saved to {hist_path}")
        histogram.log_summary()
    else:
        log_warn("[HISTOGRAM] No chunks produced for main branch")

    if errored:
        log_warn(f"[HISTOGRAM] {errored} files failed to chunk")

    # ── Branch overlay histograms ──
    repo_groups = get_repo_groups(config)
    has_branches = any(g.get("branches") for g in repo_groups)

    if has_branches:
        from shared.git_ops import (
            GitError,
            branch_exists,
            diff_branches,
            read_files_to_temp_dir,
        )

        for group in repo_groups:
            repo_path = group["repo_path"]
            main_branch = group["main_branch"]
            branches = group.get("branches", [])

            for feature_branch in branches:
                log(f"[HISTOGRAM] Processing branch overlay: {feature_branch}")

                try:
                    if not branch_exists(repo_path, feature_branch):
                        log_warn(
                            f"[HISTOGRAM] Branch '{feature_branch}' not found, skipping"
                        )
                        continue
                except GitError as exc:
                    log_warn(
                        f"[HISTOGRAM] Cannot check branch '{feature_branch}': {exc}"
                    )
                    continue

                try:
                    git_prefixes = group.get("git_prefixes", [])
                    changes = diff_branches(
                        repo_path,
                        main_branch,
                        feature_branch,
                        paths=git_prefixes if git_prefixes else None,
                    )
                except GitError as exc:
                    log_warn(f"[HISTOGRAM] Cannot diff {feature_branch}: {exc}")
                    continue

                if not changes:
                    log(f"[HISTOGRAM] No changes on {feature_branch}, skipping")
                    continue

                # Filter to non-deleted, valid-extension files
                valid_exts = _collect_branch_extensions(group)
                add_modify_paths = [
                    git_path
                    for status, git_path in changes
                    if status != "D"
                    and "." in git_path
                    and ("." + git_path.rsplit(".", 1)[-1]).lower() in valid_exts
                ]

                if not add_modify_paths:
                    log(f"[HISTOGRAM] No indexable files on {feature_branch}")
                    continue

                # Read files from git to temp dir
                temp_dir = None
                try:
                    temp_dir = read_files_to_temp_dir(
                        repo_path, feature_branch, add_modify_paths
                    )

                    branch_histogram = ChunkHistogram()
                    for git_path in add_modify_paths:
                        full_path = Path(temp_dir) / git_path.replace("\\", "/")
                        if not full_path.exists():
                            continue

                        mapping = _map_git_path_to_file_key(git_path, group)
                        if mapping is None:
                            continue
                        file_key, _ = mapping

                        file_info = {
                            "file_path": file_key,
                            "full_path": str(full_path),
                        }
                        try:
                            nodes = load_nodes_for_file(file_info)
                            if nodes:
                                branch_histogram.add_char_lengths(
                                    [len(node.text) for node in nodes]
                                )
                                branch_histogram.increment_files()
                        except Exception:
                            pass

                    if branch_histogram.total_chunks > 0:
                        bh_path = branch_histogram.save(
                            index_path=config.get_index_path(),
                            config_name=config.COLLECTION_NAME,
                            model_name=getattr(config, "MODEL_NAME", "unknown"),
                            branch=feature_branch,
                        )
                        log(
                            f"[HISTOGRAM] Branch '{feature_branch}' histogram "
                            f"saved to {bh_path}"
                        )
                        branch_histogram.log_summary()
                    else:
                        log_warn(f"[HISTOGRAM] No chunks produced for {feature_branch}")

                finally:
                    if temp_dir and Path(temp_dir).exists():
                        shutil.rmtree(temp_dir, ignore_errors=True)

    log_raw()
    log("[HISTOGRAM] Complete. No embeddings were created.")
    sys.exit(0)


if args.dry_run:
    run_dry_run()

if args.calculate_histogram:
    run_calculate_histogram()

# Ensure Qdrant is available for operations that need it
# (--regenerate-manifest, --clear, and normal indexing all need Qdrant)
if not ensure_qdrant_running(config):
    log_error("Qdrant is not available. Cannot proceed.")
    sys.exit(1)

# Ensure TEI is running if configured (auto-start Docker container)
if getattr(config, "USE_TEI", False):
    if not ensure_tei_running(config):
        log_error("TEI embedding server is not available. Cannot proceed.")
        sys.exit(1)

if args.regenerate_manifest:
    regenerate_manifest()
    sys.exit(0)

if args.clear:
    if not args.yes:
        log_warn("This will DELETE the vector collection and manifest!")
        log_raw(f"  Collection: {config.COLLECTION_NAME}")
        log_raw(f"  Index path: {config.get_index_path()}")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != "YES":
            log("Aborted.")
            sys.exit(0)

    log("Clearing vector collection and manifest...")
    client = get_qdrant_client(config)
    try:
        client.delete_collection(collection_name=config.COLLECTION_NAME)
        log(f"Deleted collection '{config.COLLECTION_NAME}'")
    except Exception as e:
        log_warn(f"Collection may not exist: {e}")

    manifest_path = get_manifest_path()
    if manifest_path.exists():
        manifest_path.unlink()
        log("Deleted manifest")

    sqlite_path = get_sqlite_path(config.get_index_path())
    if sqlite_path.exists():
        sqlite_path.unlink()
        log(f"Deleted temp SQLite store: {sqlite_path}")

    log("Done.")

manifest = load_manifest()

if manifest is None:
    log("No manifest found - regenerating from vector store...")
    regenerate_manifest()
    manifest = load_manifest()
    if manifest is None:
        if not confirm_full_index(
            "You are about to perform full indexing from scratch!"
        ):
            log("Aborted. No changes made.")
            sys.exit(0)
        log("Proceeding with full indexing...")
        mode = "full"
    else:
        log("Regen complete - performing incremental refresh")
        mode = "refresh"
else:
    log("Manifest found - running in refresh mode")
    mode = "refresh"

# --collect-perf-stats: start GPU stats background collector
if args.collect_perf_stats:
    from shared.gpu_stats import start_gpu_stats, stop_gpu_stats

    _stats_ts = datetime.now().strftime("%Y%m%d%H%M%S")
    _stats_file = Path(config.get_index_path()) / f"gpu_stats_{_stats_ts}.csv"
    start_gpu_stats(_stats_file, interval=2.0)
else:
    stop_gpu_stats = None  # type: ignore[assignment]

try:
    run_indexing(mode)
finally:
    if stop_gpu_stats is not None:
        stop_gpu_stats()
    cuda_clear_cache()
    from shared.log import close_tee

    close_tee()
