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
import queue
import shutil
import subprocess
import threading
import uuid
import time
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait

os.environ["TORCHVISION_DISABLE_META_REGISTRATIONS"] = "1"

import argparse

import config_loader
from config_loader import resolve_source_entries
from shared.log import log, log_raw, log_error, log_warn
from shared.version import __version__ as HCR_VERSION
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
    uses_tei_container,
)
from shared.indexing import load_all_sources
from shared.manifest import (
    compute_file_hash,
    filter_out_gitignored,
    find_source_files,
    normalize_file_key,
    resolve_key_to_disk_path,
    validate_source_dirs,
)
from shared.qdrant_client import get_qdrant_client, get_qdrant_url
from shared.upsert_batching import DEFAULT_MAX_UPSERT_BYTES, upsert_in_batches
from shared.docker_utils import ensure_qdrant_running, ensure_tei_running
from shared.hybrid_embed import (
    get_sqlite_path,
    init_sqlite_db,
    save_dense_vectors_sqlite,
    read_dense_vectors_sqlite,
    cleanup_sqlite,
)
from shared.chunk_pool import ChunkPool, ChunkHistogram
from shared.symbol_policy import configure_symbol_policy  # noqa: E402
from shared.manifest_saver import (  # noqa: E402
    ManifestSaver,
    manifest_save_interval,
    read_json_file,
    write_manifest_file,
)
from shared.pending_points import (  # noqa: E402
    JOURNAL_SUFFIX,
    PendingJournal,
    PendingRecoveryError,
    journal_path_for,
    read_journal,
    remove_journal,
    unresolved_keys,
)
from shared.sql_dialect import (
    manifest_dialect_fields,
    sql_dialect_changed,
    sql_dialect_for_file,
)
from typing import Callable, Any
from dataclasses import dataclass, field

# Sentinel for build_branch_resolver() default arg (distinguish "not passed" from None)
_SENTINEL: Any = object()


# ────────────────────────────────────────────────────────────────────
# Parse-ahead result: produced by the background parser thread,
# consumed by the main embedding thread.
# ────────────────────────────────────────────────────────────────────
@dataclass
class _ParsedFile:
    """Result of parsing a single file on the background thread."""

    file_index: int
    file_key: str
    action_type: str
    file_info: dict
    nodes: list  # list of TextNode (may be empty)
    ids: list[str]
    documents: list[str]
    is_empty_file: bool = False
    is_no_content: bool = False
    has_parse_error: bool = False
    parse_time_s: float = 0.0


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

    def record(self, name: str, elapsed: float) -> None:
        """Record a pre-measured timing (e.g. from a background thread)."""
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
        manifest = read_json_file(manifest_path)
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


def _write_manifest_timed(path: Path, manifest: dict, label: str) -> None:
    """Write a manifest file and log how long it took.

    ``MANIFEST_SAVE_INTERVAL_S > 0`` switches to compact JSON written
    atomically; the default keeps the pretty-printed in-place write.
    """
    compact = manifest_save_interval(config) > 0
    t0 = time.perf_counter()
    size = write_manifest_file(path, manifest, compact=compact)
    elapsed = time.perf_counter() - t0
    log(
        f"[MANIFEST] {label}: saved {len(manifest.get('files', {})):,} files "
        f"({size / 1e6:.1f} MB, {'compact' if compact else 'indent'}) "
        f"in {elapsed:.3f}s"
    )


def save_manifest(manifest):
    """Save manifest based on store type."""
    if manifest is None:
        return
    _write_manifest_timed(get_manifest_path(), manifest, "main")


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
    Tag overlays use the same function with the tag's configured name.
    """
    from shared.overlay import make_overlay_point_id

    return make_overlay_point_id(branch, file_key, index)


def get_current_file_states():
    """Get current state of all source files, driven by resolved SOURCE_DIRS."""
    states = {}
    respect_gitignore = bool(getattr(config, "RESPECT_GITIGNORE", True))
    parse_workers = int(getattr(config, "INDEX_PARSE_WORKERS", 1) or 1)
    if parse_workers < 1:
        parse_workers = 1

    def _state_for_file(f: Path, dir_path: Path, source_dir: dict) -> tuple[str, dict] | None:
        try:
            mtime = f.stat().st_mtime
            hash_val = compute_file_hash(f)
            relative_path = f.relative_to(dir_path).as_posix()
            path_key = normalize_file_key(
                source_dir["path"], relative_path, source_dir=source_dir
            )
            state = {
                "file_path": path_key,
                "full_path": str(f),
                "mtime": mtime,
                "hash": hash_val,
            }
            state.update(sql_dialect_for_file(source_dir, f.name))
            return path_key, state
        except Exception:
            return None

    for source_dir in resolve_source_entries(config):
        dir_path = Path(source_dir["path"])
        if not dir_path.exists():
            continue
        exclude_patterns = source_dir.get("exclude", [])
        candidates = find_source_files(
            dir_path, source_dir["extensions"], exclude_patterns
        )

        filtered = filter_out_gitignored(
            candidates, source_dir, respect_gitignore=respect_gitignore
        )
        if parse_workers == 1 or len(filtered) < 32:
            for f in filtered:
                item = _state_for_file(f, dir_path, source_dir)
                if item:
                    states[item[0]] = item[1]
        else:
            with ThreadPoolExecutor(max_workers=parse_workers) as pool:
                for item in pool.map(
                    lambda f: _state_for_file(f, dir_path, source_dir), filtered
                ):
                    if item:
                        states[item[0]] = item[1]

    return states


def load_nodes_for_file(file_info):
    """Load and process nodes for a specific file using the reader registry.

    After the reader produces nodes, ``disk_path`` metadata is stamped on
    every node so that it is stored in Qdrant payload.  This lets consumers
    (MCP server, validation scripts) resolve the on-disk location without
    needing the config at query time.
    """
    from shared.readers import load_nodes_for_file as _registry_load

    nodes = _registry_load(file_info)

    # Stamp disk_path from file_info (pre-computed in the main loop) or
    # resolve it from the canonical key using the current config.
    disk_path = file_info.get("disk_path")
    if not disk_path:
        canonical_key = file_info.get("file_path", "")
        if canonical_key:
            disk_path = resolve_key_to_disk_path(canonical_key, cfg=config)

    if disk_path:
        for node in nodes:
            node.metadata["disk_path"] = disk_path

    return nodes


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

    global _STATE_MAIN_MANIFEST
    if mode == "full":
        _STATE_MAIN_MANIFEST = run_full_indexing()
    else:
        _STATE_MAIN_MANIFEST = run_refresh_indexing()

    # ── Branch / tag overlay support (after main indexing) ─────────
    from config_loader import get_repo_groups
    from shared.overlay import configured_overlays

    repo_groups = get_repo_groups(config)
    has_git_repos = len(repo_groups) > 0
    has_branches = any(configured_overlays(g) for g in repo_groups)

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
        # No overlays configured, but we still need to clean up
        # branch/tag overlays that were previously indexed and have since
        # been removed from the config.
        _cleanup_stale_branches(configured_branches=set())

    # Serving-only MCP servers read index state and provenance from Qdrant.
    _publish_index_state("end of run", ensure_provenance=True)


# Main manifest of the current run (set by run_indexing); the state document
# published after each overlay update is built from it without re-reading
# the (possibly very large) manifest file.
_STATE_MAIN_MANIFEST: dict | None = None


def ensure_file_path_payload_index(client=None) -> None:
    """Keyword payload index on ``file_path`` (deletes filter on it).

    Skipped when ``QDRANT_FILE_PATH_INDEX`` is false or the index exists.
    Creating it does not change any search result.
    """
    from qdrant_client import models

    if not getattr(config, "QDRANT_FILE_PATH_INDEX", True):
        return
    client = client or get_qdrant_client(config)
    try:
        info = client.get_collection(collection_name=config.COLLECTION_NAME)
        schema = getattr(info, "payload_schema", None) or {}
        if "file_path" in schema:
            return
        client.create_payload_index(
            collection_name=config.COLLECTION_NAME,
            field_name="file_path",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        log("Qdrant payload index on 'file_path' field ensured")
    except Exception as exc:
        if "already exists" not in str(exc).lower():
            log_warn(f"Could not create 'file_path' payload index: {exc}")


def _ensure_full_provenance(client) -> None:
    """Backfill full embedding provenance on collections that lack it."""
    from shared import index_meta

    stored, _legacy = index_meta.read_provenance(client, config.COLLECTION_NAME)
    if stored is not None:
        return
    layout = index_meta.collection_vector_params(client, config.COLLECTION_NAME)
    if layout is None:
        return
    embed_model = get_embed_model(device=config.INDEX_EMBED_DEVICE, cfg=config)
    prov = index_meta.build_provenance(
        config, embed_model, layout, backend_family=get_embed_backend_family(config)
    )
    if prov["dimension"] != layout["dimension"]:
        log_error(
            f"Not backfilling provenance: the embedding model returns "
            f"{prov['dimension']}-d vectors, the collection stores {layout['dimension']}-d"
        )
        return
    size = index_meta.write_provenance(client, config.COLLECTION_NAME, prov)
    log(f"[PROVENANCE] backfilled full embedding provenance ({size} bytes)")
    for line in index_meta.format_provenance(prov):
        log(f"[PROVENANCE]   {line}")


def _publish_index_state(reason: str, *, ensure_provenance: bool = False) -> None:
    """Publish the index state (and overlay tombstones) into Qdrant.

    Never fails the run: problems are logged as warnings. Disabled with
    ``INDEX_STATE_PUBLISH = False``.
    """
    if not getattr(config, "INDEX_STATE_PUBLISH", True):
        return
    from shared import index_meta
    from shared.index_state import build_state_document, load_overlay_manifests

    try:
        client = get_qdrant_client(config)
        if index_meta.collection_vector_params(client, config.COLLECTION_NAME) is None:
            log_warn(f"[INDEX STATE] collection not readable; state not published ({reason})")
            return
        ensure_file_path_payload_index(client)
        if ensure_provenance:
            _ensure_full_provenance(client)
        manifest = _STATE_MAIN_MANIFEST if _STATE_MAIN_MANIFEST is not None else load_manifest()
        if manifest is None:
            return
        overlays = load_overlay_manifests(config)
        doc = build_state_document(manifest, overlays, config.COLLECTION_NAME)
        tombstones = {label: list(data.get("tombstones") or []) for label, data in overlays.items()}
        stats = index_meta.publish_index_state(
            client,
            config.COLLECTION_NAME,
            doc,
            tombstones,
            per_point=int(
                getattr(config, "INDEX_STATE_TOMBSTONES_PER_POINT", None)
                or index_meta.TOMBSTONES_PER_POINT
            ),
        )
        log(f"[INDEX STATE] published ({reason}): {stats.summary()}")
    except Exception as exc:  # noqa: BLE001 - publishing must not fail indexing
        log_warn(f"[INDEX STATE] could not publish index state ({reason}): {exc}")


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
    recover_pending_points(manifest)
    current_states = get_current_file_states()
    actions = determine_actions(manifest["files"], current_states, manifest=manifest)

    log(f"Found {len(actions['add'])} files to index (full rebuild after --clear)")
    log_refresh_changes(
        actions,
        current_states,
        manifest["files"],
        branch_resolver=build_branch_resolver(),
    )

    # Reuse the scan: a second get_current_file_states() would re-walk and
    # re-hash every source file before the first embedding request.
    perform_refresh_qdrant(actions, manifest, file_states=current_states)

    # Bookkeeping only (commits / timestamps / fingerprints) — no re-embed
    _finalize_manifest_bookkeeping(manifest, mode="full")
    save_manifest(manifest)
    return manifest


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

    # Repair points left by a run that was killed between Qdrant and the
    # manifest save, before deciding what changed.
    recover_pending_points(manifest)

    # Get current file states
    current_states = get_current_file_states()

    # Determine actions (enhanced with git-diff acceleration)
    actions = determine_actions(manifest["files"], current_states, manifest=manifest)

    if not actions["add"] and not actions["modify"] and not actions["delete"]:
        log("No changes detected - index is up to date")
        if VERBOSE:
            log_verbose_refresh(actions, current_states, manifest["files"])
        # Still refresh bookkeeping when nothing changed (first run with
        # git-aware config, or after pulling code that adds index_run fields)
        _finalize_manifest_bookkeeping(manifest, mode="refresh_noop")
        save_manifest(manifest)
        return manifest

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
    # Reuse the scan: a second get_current_file_states() would re-walk and
    # re-hash every source file before the first embedding request.
    perform_refresh_qdrant(actions, manifest, file_states=current_states)

    # Bookkeeping only (commits / timestamps / fingerprints) — no re-embed
    _finalize_manifest_bookkeeping(manifest, mode="refresh")
    save_manifest(manifest)
    return manifest


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
    """Build a map: repo_key → list of resolved source entries.

    Uses ``make_repo_key()`` for platform-independent keys (directory name only).
    Used by the git-diff fast path to associate manifest file keys with
    their parent repo group.
    """
    from shared.manifest import make_repo_key

    result: dict[str, list[dict]] = {}
    for entry in resolved_entries:
        if entry["_entry_type"] != "git_repo":
            continue
        repo_key = make_repo_key(entry["_repo_path"])
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
    always deleted. A SQL file whose ``sql_dialect`` differs from the
    manifest is modified even when the hash and mtime match. A missing
    manifest dialect means ``tsql``.

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
    from shared.manifest import make_repo_key, migrate_repo_commits

    actions: dict[str, list] = {"add": [], "modify": [], "delete": []}

    # ── Build per-repo-group skips using git-diff fast path ──────────
    # skip_hash_check: set of path_keys whose hashes we can skip entirely
    #                  (commits match AND mtime unchanged)
    skip_hash_check: set[str] = set()

    if manifest is not None:
        repo_commits = manifest.get("repo_commits", {})
        # Migrate old absolute-path keys to platform-independent format
        repo_commits, was_migrated = migrate_repo_commits(repo_commits)
        if was_migrated:
            manifest["repo_commits"] = repo_commits
        repo_groups = get_repo_groups(config)
        resolved = resolve_source_entries(config)
        repo_entry_map = _build_repo_group_file_map(resolved)
        threshold = getattr(config, "DIFF_FULL_REINDEX_THRESHOLD", 0.5)

        for group in repo_groups:
            repo_path = group["repo_path"]
            main_branch = group["main_branch"]
            repo_key = make_repo_key(repo_path)
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
                    if int(stored_mtime) == int(current_mtime) and not (
                        sql_dialect_changed(old_entry, current)
                    ):
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

                # Mark repo-group files not in the changed set as skip,
                # but ONLY if their mtime also hasn't changed.  Without
                # the mtime guard, uncommitted working-copy edits to files
                # that aren't in the commit-range diff would be silently
                # skipped (the git diff only covers committed changes).
                for path_key in repo_manifest_keys:
                    if path_key in current_states and path_key not in changed_file_keys:
                        old_entry = old_files.get(path_key, {})
                        current = current_states[path_key]
                        stored_mtime = old_entry.get("mtime", 0)
                        current_mtime = current.get("mtime", 0)
                        if int(stored_mtime) == int(current_mtime) and not (
                            sql_dialect_changed(old_entry, current)
                        ):
                            skip_hash_check.add(path_key)
                        # else: mtime changed → let the main loop hash-compare

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
            # Dialect is not part of the file hash, so compare it too.
            hash_changed = current["hash"] != old_entry.get("hash", "")
            if hash_changed or sql_dialect_changed(old_entry, current):
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

    The ``repo_commits`` dict in the manifest is keyed by the repo directory
    name (platform-independent, via ``make_repo_key()``) and stores:
      - ``main_branch``: branch name
      - ``commit``: HEAD commit hash at this point in time
      - ``indexed_at``: UTC ISO timestamp when this commit was recorded
        (additive; older manifests without it remain valid)
    """
    from config_loader import get_repo_groups
    from shared.git_ops import get_branch_head, validate_git_repo, GitError
    from shared.manifest import (
        make_repo_key,
        migrate_repo_commits,
        prune_repo_commits,
    )
    from shared.index_state import utc_iso_now

    repo_groups = get_repo_groups(config)
    if not repo_groups:
        # No git repos configured any more: drop stale entries, if any.
        stale = manifest.get("repo_commits")
        if isinstance(stale, dict) and stale:
            for key in prune_repo_commits(stale, set()):
                log(f"Removed repo_commits entry of unconfigured repo: {key}")
        return

    repo_commits = manifest.get("repo_commits", {})
    # Migrate old absolute-path keys before updating
    repo_commits, _ = migrate_repo_commits(repo_commits)
    # Repos removed from the config keep no commit entry
    configured = {make_repo_key(g["repo_path"]) for g in repo_groups}
    for key in prune_repo_commits(repo_commits, configured):
        log(f"Removed repo_commits entry of unconfigured repo: {key}")
    now = utc_iso_now()

    for group in repo_groups:
        repo_path = group["repo_path"]
        main_branch = group["main_branch"]
        repo_key = make_repo_key(repo_path)

        try:
            if not validate_git_repo(repo_path):
                log_warn(f"Not a git repo: {repo_path}, skipping commit tracking")
                continue
            commit = get_branch_head(repo_path, main_branch)
            repo_commits[repo_key] = {
                "main_branch": main_branch,
                "commit": commit,
                "indexed_at": now,
            }
        except GitError as exc:
            log_warn(f"Cannot get HEAD for {main_branch} in {repo_path}: {exc}")

    manifest["repo_commits"] = repo_commits


def _update_index_run_meta(manifest: dict, mode: str) -> None:
    """Record lightweight last-run metadata on the manifest (no re-embed).

    Additive fields only — safe for production refresh of old manifests.
    """
    from shared.index_state import utc_iso_now
    from shared.version import __version__, stamp_manifest_version

    stamp_manifest_version(manifest)
    manifest["index_run"] = {
        "indexer_version": __version__,
        "completed_at": utc_iso_now(),
        "mode": mode,
        "embed_backend": get_embed_backend_family(config),
        "model_name": getattr(config, "MODEL_NAME", None),
    }
    quant = getattr(config, "EMBEDDING_QUANT", None)
    if quant:
        manifest["index_run"]["embedding_quant"] = str(quant)


def _update_source_snapshots(manifest: dict) -> None:
    """Refresh ``source_snapshots`` bookkeeping from current manifest files."""
    from shared.index_state import build_source_snapshots

    try:
        manifest["source_snapshots"] = build_source_snapshots(manifest, config)
    except Exception as exc:
        log_warn(f"Could not update source_snapshots: {exc}")


def _finalize_manifest_bookkeeping(manifest: dict, mode: str) -> None:
    """Update repo commits, index_run, and source snapshots then leave to caller to save."""
    _update_repo_commits(manifest)
    _update_index_run_meta(manifest, mode)
    _update_source_snapshots(manifest)


# ── Branch overlay indexing ──────────────────────────────────────


def _get_branch_manifest_path(branch: str) -> Path:
    """Return path to an overlay manifest file.

    The file name stays ``index_manifest_branch_<sanitized>.json`` for
    branch and tag overlays.
    """
    from shared.overlay import overlay_manifest_filename

    index_path = Path(config.get_index_path()).resolve()
    return index_path / overlay_manifest_filename(branch)


def _load_branch_manifest(branch: str) -> dict:
    """Load an overlay manifest (branch or tag), returning empty structure if absent."""
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
    """Persist an overlay manifest (branch or tag) to disk."""
    _write_manifest_timed(_get_branch_manifest_path(branch), manifest, branch)


def _pending_journal_path(branch_label: str | None = None) -> Path:
    """Journal of not-yet-saved Qdrant changes for the main or an overlay manifest."""
    if branch_label is None:
        return journal_path_for(get_manifest_path())
    return journal_path_for(_get_branch_manifest_path(branch_label))


def file_delete_filters(
    file_keys: list[str],
    branch_label: str | None = None,
    resolve_branch: Callable[[str], str | None] | None = None,
) -> list:
    """Qdrant filters that select the points of *file_keys* on one branch.

    With *branch_label* (an overlay run): ``file_path`` in the keys and
    ``branch == branch_label``.

    Main-branch run (no *branch_label*): the keys are grouped by the label
    *resolve_branch* gives them, which is the ``branch`` value main-branch
    points of that file carry. A git file's filter is ``file_path`` in the
    keys and (``branch == <main label>`` or no ``branch`` field, as written
    before branch labels existed), so the branch and tag overlay points of
    the same path survive. Files without a label (plain source sets, no
    overlays) are matched by ``file_path`` alone.
    """
    from qdrant_client import models

    def _path_cond(keys):
        return models.FieldCondition(key="file_path", match=models.MatchAny(any=keys))

    if branch_label is not None:
        return [
            models.Filter(
                must=[
                    _path_cond(list(file_keys)),
                    models.FieldCondition(
                        key="branch", match=models.MatchValue(value=branch_label)
                    ),
                ]
            )
        ]
    groups: dict[str | None, list[str]] = {}
    for key in file_keys:
        label = resolve_branch(key) if resolve_branch is not None else None
        groups.setdefault(label, []).append(key)
    filters = []
    for label, keys in groups.items():
        if label is None:
            filters.append(models.Filter(must=[_path_cond(keys)]))
            continue
        filters.append(
            models.Filter(
                must=[_path_cond(keys)],
                should=[
                    models.FieldCondition(
                        key="branch", match=models.MatchValue(value=label)
                    ),
                    models.IsEmptyCondition(is_empty=models.PayloadField(key="branch")),
                ],
            )
        )
    return filters


def _delete_points_for_file_keys(
    client, file_keys: list[str], branch_label=None, resolve_branch=None
) -> None:
    """Delete the points of *file_keys* on one branch (batched filter deletes).

    With *branch_label* only that overlay's points are deleted; without it
    only main-branch points (see ``file_delete_filters``).
    """
    chunk_size = int(getattr(config, "QDRANT_DELETE_CHUNK_SIZE", 500) or 500)
    if chunk_size < 1:
        chunk_size = 500
    delete_timeout = getattr(config, "QDRANT_DELETE_TIMEOUT", 60)
    for offset in range(0, len(file_keys), chunk_size):
        chunk = file_keys[offset : offset + chunk_size]
        for selector in file_delete_filters(chunk, branch_label, resolve_branch):
            client.delete(
                collection_name=config.COLLECTION_NAME,
                points_selector=selector,
                timeout=delete_timeout,
            )


def recover_pending_points(
    manifest: dict,
    *,
    branch_label: str | None = None,
    client=None,
    save_fn=None,
) -> list[str]:
    """Repair what an interrupted run left between Qdrant and the manifest.

    Reads the pending journal (``<manifest>.pending.jsonl``). Every file the
    journal and the manifest disagree on gets its points deleted and its
    manifest entry dropped; the manifest is saved, then the journal is
    removed. The caller's change detection then re-indexes those files from
    disk (or forgets them when they are gone). Main-branch recovery deletes
    main-branch points only; overlay points of the same paths stay.

    When the delete fails (Qdrant unreachable or erroring) nothing is
    changed, the journal is kept and ``PendingRecoveryError`` is raised: the
    run must stop, because re-adding those files without deleting their old
    points first could leave stale chunks behind.

    Returns the repaired file keys.
    """
    path = _pending_journal_path(branch_label)
    journal = read_journal(path)
    if not journal:
        remove_journal(path)
        return []
    files = manifest.setdefault("files", {})
    stale = unresolved_keys(journal, files)
    where = f" for {branch_label}" if branch_label else ""
    if stale:
        try:
            if client is None:
                client = get_qdrant_client(config)
            _delete_points_for_file_keys(
                client,
                stale,
                branch_label=branch_label,
                resolve_branch=None if branch_label is not None else build_branch_resolver(),
            )
        except Exception as exc:
            log_error(
                f"[RECOVER] Could not delete points of {len(stale)} file(s) left by an "
                f"interrupted run{where}: {exc}. Keeping the journal; stopping this run."
            )
            raise PendingRecoveryError(
                f"recovery of {len(stale)} file(s){where} failed: {exc}"
            ) from exc
        for key in stale:
            files.pop(key, None)
        if save_fn is None:
            save_manifest(manifest)
        else:
            save_fn(manifest)
        log_warn(
            f"[RECOVER] An earlier run{where} stopped between Qdrant and the manifest: "
            f"deleted the points of {len(stale)} file(s); they are re-indexed now."
        )
    remove_journal(path)
    return stale


def _verify_unchanged_since_scan(file_key: str, file_info: dict) -> dict:
    """Return *file_info*, or a copy with an empty hash if the file changed.

    The manifest stores the hash taken when the files were scanned, but the
    reader opens the file later. When the file changed in between, the
    chunks no longer match that hash; an empty hash never matches a file on
    disk, so the next refresh re-indexes the file.
    """
    full_path = file_info.get("full_path")
    expected = file_info.get("hash")
    if not full_path or not expected:
        return file_info
    if compute_file_hash(Path(full_path)) == expected:
        return file_info
    log_warn(
        f"{file_key} changed while it was being indexed; "
        f"it is re-indexed on the next refresh"
    )
    return {**file_info, "hash": ""}


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


def _write_new_collection_provenance(client, embed_model, dim: int) -> None:
    """Full provenance for a new collection; legacy sentinel when that fails."""
    from shared import index_meta

    family = get_embed_backend_family(config)
    try:
        layout = index_meta.collection_vector_params(client, config.COLLECTION_NAME)
        prov = index_meta.build_provenance(config, embed_model, layout, backend_family=family)
        size = index_meta.write_provenance(client, config.COLLECTION_NAME, prov)
        log(f"Stored embedding provenance: {prov.get('model_name')} ({size} bytes)")
    except Exception as exc:  # noqa: BLE001 - keep the old minimal record
        log_warn(f"Full provenance not stored ({exc}); storing backend family only")
        set_collection_provenance(client, config.COLLECTION_NAME, family, dim)


def ensure_symbol_payload_index(client=None) -> None:
    """Keyword payload indexes on ``SYMBOL_LOOKUP_FIELDS`` (``object_name``,
    ``symbols``) so the exact symbol lookup does not scan.  Created for
    new collections only; existing collections keep working without it."""
    from qdrant_client import models

    fields = getattr(config, "SYMBOL_LOOKUP_FIELDS", None) or ["object_name"]
    if isinstance(fields, str):
        fields = [fields]
    client = client or get_qdrant_client(config)
    for field in fields:
        try:
            client.create_payload_index(
                collection_name=config.COLLECTION_NAME,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            log(f"Qdrant payload index on '{field}' field ensured")
        except Exception as exc:
            if "already exists" not in str(exc).lower():
                log_warn(f"Could not create '{field}' payload index: {exc}")


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
    from shared.overlay import map_git_path_to_file_key

    return map_git_path_to_file_key(git_path, group)


def _stamp_overlay_manifest(
    branch_manifest: dict,
    *,
    kind: str,
    merge_base: str | None,
    resolved_commit: str | None,
    repo_path: str,
    name: str,
    signature: str | None = None,
) -> None:
    """Record diff progress on an overlay manifest.

    Branch runs write ``merge_base`` and ``last_branch_commit`` only.
    Tag runs write ``last_resolved_commit`` and leave the branch keys alone.
    """
    from shared.git_ops import GitError, get_branch_head
    from shared.overlay import manifest_progress_fields

    branch_head = None
    if kind == "branch":
        try:
            branch_head = get_branch_head(repo_path, name)
        except GitError:
            branch_head = None
    branch_manifest.update(
        manifest_progress_fields(
            kind=kind,
            merge_base=merge_base,
            branch_head=branch_head,
            resolved_commit=resolved_commit,
        )
    )
    branch_manifest["kind"] = kind
    if signature:
        branch_manifest["overlay_signature"] = signature
    else:
        branch_manifest.pop("overlay_signature", None)
    try:
        from shared.index_state import utc_iso_now

        branch_manifest["indexed_at"] = utc_iso_now()
    except Exception:
        pass


def _overlay_unchanged_since_last_run(label: str, signature: str) -> bool:
    """True when the stored overlay signature matches and its points exist.

    A manifest that lists files while Qdrant holds no points for the label
    (collection cleared) is not trusted; the full run then re-embeds it.
    """
    manifest = _load_branch_manifest(label)
    if manifest.get("overlay_signature") != signature:
        return False
    if read_journal(_pending_journal_path(label)):
        return False  # an interrupted run left changes to repair
    if not manifest.get("files"):
        return True
    try:
        from qdrant_client import models as _models

        client = get_qdrant_client(config)
        count = client.count(
            collection_name=config.COLLECTION_NAME,
            count_filter=_models.Filter(
                must=[
                    _models.FieldCondition(
                        key="branch", match=_models.MatchValue(value=label)
                    )
                ]
            ),
            exact=False,
        ).count
    except Exception as exc:
        log_warn(f"Could not count Qdrant vectors for {label}: {exc}")
        return False
    return count > 0


def run_branch_overlay_indexing() -> None:
    """Index configured overlays for every git repo group.

    Branch overlays diff with the merge-base (three-dot). Tag overlays diff
    the tag commit against the main tip. Both read blobs with ``git show``
    (no checkout), upsert points whose ``branch`` payload is the overlay
    name, and store tombstones for deletes. Removing an overlay from config
    deletes its points and manifest on the next run.
    """
    from config_loader import get_repo_groups
    from shared.git_ops import GitError, read_files_to_temp_dir
    from shared.overlay import (
        configured_overlays,
        diff_overlay,
        overlay_signature,
        reconcile_overlay_actions,
        skip_when_diff_empty,
    )

    repo_groups = get_repo_groups(config)
    if not repo_groups:
        return

    # Collect all (repo, branch) pairs that should exist
    configured_branches: set[tuple[str, str]] = set()

    for group in repo_groups:
        repo_path = group["repo_path"]
        main_branch = group["main_branch"]
        overlays = configured_overlays(group)
        if not overlays:
            continue

        for spec in overlays:
            feature_branch = spec["name"]
            kind = spec["kind"]
            configured_branches.add((repo_path, feature_branch))
            label = f"[{kind.upper()}]"

            log(
                f"{label} Processing overlay: {feature_branch} "
                f"(repo={repo_path}, main={main_branch})"
            )

            # ── Resolve the ref and diff ──
            # Branch: three-dot diff from the merge-base.
            # Tag: tree diff of the peeled commit against the main tip.
            git_prefixes = group.get("git_prefixes", [])
            try:
                diff = diff_overlay(
                    repo_path,
                    main_branch,
                    spec,
                    paths=git_prefixes if git_prefixes else None,
                )
            except GitError as exc:
                log_warn(f"Cannot diff {feature_branch} vs {main_branch}: {exc}")
                continue
            if diff is None:
                if kind == "branch":
                    log_warn(
                        f"Branch '{feature_branch}' not found in {repo_path}, skipping"
                    )
                else:
                    log_warn(
                        f"Tag '{feature_branch}' not found in {repo_path}, skipping"
                    )
                continue

            changes = diff.changes
            merge_base = diff.merge_base
            resolved_commit = diff.resolved_commit
            read_at = diff.read_at

            # Same refs and settings as the last completed run: the diff, the
            # blobs and their hashes would be identical, so skip reading files.
            signature = overlay_signature(repo_path, main_branch, diff, group)
            if signature and _overlay_unchanged_since_last_run(
                feature_branch, signature
            ):
                log(f"{label} {feature_branch} overlay is up to date (refs unchanged)")
                continue

            # Empty three-dot diffs have always skipped the branch overlay,
            # including any points already stored. An empty tag diff means
            # the tag tree matches main, so stored tag points must be deleted.
            if not changes and skip_when_diff_empty(kind):
                log(f"{label} No changes on {feature_branch}, skipping")
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
                    f"{label} {feature_branch} has {total_changes} changed files "
                    f"— this is a very large overlay"
                )

            log(
                f"{label} {feature_branch}: {len(add_modify_git_paths)} changed files in diff, "
                f"{len(deleted_git_paths)} deleted"
            )

            # ── Load branch manifest ──
            branch_manifest = _load_branch_manifest(feature_branch)
            recover_pending_points(
                branch_manifest,
                branch_label=feature_branch,
                save_fn=lambda m, b=feature_branch: _save_branch_manifest(b, m),
            )
            overlay_journal = PendingJournal(_pending_journal_path(feature_branch))
            overlay_failed = False

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
                if kind == "branch":
                    log(f"{label} No indexable changes on {feature_branch}")
                    # Still update manifest merge_base. Do not touch points.
                    branch_manifest["merge_base"] = merge_base
                    branch_manifest["kind"] = kind
                    # Stamp the signature too, so the next run with the same
                    # refs skips straight away like any other overlay.
                    if signature:
                        branch_manifest["overlay_signature"] = signature
                    else:
                        branch_manifest.pop("overlay_signature", None)
                    _save_branch_manifest(feature_branch, branch_manifest)
                    _publish_index_state(f"overlay {feature_branch}")
                    continue
                old_count = len(branch_manifest.get("files") or {})
                if old_count == 0:
                    log(f"{label} No indexable changes on {feature_branch}")
                    branch_manifest["tombstones"] = []
                    _stamp_overlay_manifest(
                        branch_manifest,
                        kind=kind,
                        merge_base=merge_base,
                        resolved_commit=resolved_commit,
                        repo_path=repo_path,
                        name=feature_branch,
                        signature=signature,
                    )
                    _save_branch_manifest(feature_branch, branch_manifest)
                    _publish_index_state(f"overlay {feature_branch}")
                    continue
                # The tag no longer differs on any indexable path. Fall
                # through with an empty file set so previous points are deleted.
                log(
                    f"{label} {feature_branch}: no remaining differences; "
                    f"removing {old_count} overlay file(s)"
                )

            # ── Read files from git to temp dir ──
            git_paths_to_read = [info["git_path"] for info in files_to_index.values()]
            temp_dir = None
            try:
                if git_paths_to_read:
                    temp_dir = read_files_to_temp_dir(
                        repo_path, read_at, git_paths_to_read
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
                        log_warn(f"{label} Temp file missing: {full_path}")
                        continue

                    try:
                        hash_val = compute_file_hash(full_path)
                    except Exception:
                        log_warn(f"{label} Cannot hash: {full_path}")
                        continue

                    branch_states[file_key] = {
                        "file_path": file_key,
                        "full_path": str(full_path),
                        "mtime": 0,  # git doesn't preserve mtime
                        "hash": hash_val,
                    }

                # ── Determine actions vs branch manifest ──
                old_files = branch_manifest.get("files", {})
                actions = reconcile_overlay_actions(old_files, branch_states)

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
                                f"{label} Could not count Qdrant vectors for "
                                f"{feature_branch}: {_exc}. Assuming up to date."
                            )
                            qdrant_branch_count = manifest_file_count  # skip re-index

                        if qdrant_branch_count == 0:
                            log_warn(
                                f"{label} {feature_branch}: manifest claims "
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
                    log(f"{label} {feature_branch} overlay is up to date")
                    _stamp_overlay_manifest(
                        branch_manifest,
                        kind=kind,
                        merge_base=merge_base,
                        resolved_commit=resolved_commit,
                        repo_path=repo_path,
                        name=feature_branch,
                        signature=signature,
                    )
                    _save_branch_manifest(feature_branch, branch_manifest)
                    _publish_index_state(f"overlay {feature_branch}")
                    continue

                log(
                    f"{label} {feature_branch}: "
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

                # ── Delete stale branch vectors (batched MatchAny) ──
                if actions["delete"]:
                    from qdrant_client import models as _qd_models

                    client = get_qdrant_client(config)
                    del_keys = list(actions["delete"])
                    chunk_size = int(
                        getattr(config, "QDRANT_DELETE_CHUNK_SIZE", 500) or 500
                    )
                    if chunk_size < 1:
                        chunk_size = 500
                    delete_timeout = getattr(config, "QDRANT_DELETE_TIMEOUT", 60)
                    for offset in range(0, len(del_keys), chunk_size):
                        chunk = del_keys[offset : offset + chunk_size]
                        overlay_journal.record((k, None) for k in chunk)
                        try:
                            client.delete(
                                collection_name=config.COLLECTION_NAME,
                                points_selector=_qd_models.Filter(
                                    must=[
                                        _qd_models.FieldCondition(
                                            key="file_path",
                                            match=_qd_models.MatchAny(any=chunk),
                                        ),
                                        _qd_models.FieldCondition(
                                            key="branch",
                                            match=_qd_models.MatchValue(
                                                value=feature_branch
                                            ),
                                        ),
                                    ]
                                ),
                                timeout=delete_timeout,
                            )
                        except Exception as exc:
                            log_warn(
                                f"{label} Failed to delete vectors for "
                                f"{len(chunk)} files on {feature_branch}: {exc}"
                            )
                            overlay_failed = True
                            continue
                        for del_key in chunk:
                            old_files.pop(del_key, None)
                        log(
                            f"{label} Deleted vectors for {len(chunk)} files "
                            f"on {feature_branch}"
                        )

                # ── Embed and upsert changed files ──
                if actions["add"] or actions["modify"]:
                    from functools import partial

                    complete = perform_refresh_qdrant(
                        actions=actions,
                        manifest=branch_manifest,
                        branch_label=feature_branch,
                        file_states=branch_states,
                        point_id_fn=partial(make_branch_point_id, feature_branch),
                        save_fn=lambda m: _save_branch_manifest(feature_branch, m),
                    )
                    if not complete:
                        overlay_failed = True

                # ── Update tombstones ──
                # The signature lets the next run skip this overlay, so it is
                # stored only when every delete and upsert of this run worked.
                branch_manifest["tombstones"] = sorted(tombstone_keys)
                _stamp_overlay_manifest(
                    branch_manifest,
                    kind=kind,
                    merge_base=merge_base,
                    resolved_commit=resolved_commit,
                    repo_path=repo_path,
                    name=feature_branch,
                    signature=None if overlay_failed else signature,
                )

                _save_branch_manifest(feature_branch, branch_manifest)
                overlay_journal.finish(branch_manifest.get("files", {}))
                _publish_index_state(f"overlay {feature_branch}")
                if overlay_failed:
                    log_warn(
                        f"{label} {feature_branch} overlay incomplete (Qdrant errors); "
                        f"the next run retries it"
                    )
                else:
                    log(f"{label} {feature_branch} overlay indexing complete")

            finally:
                # Clean up temp directory
                if temp_dir and Path(temp_dir).exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)

    # ── Clean up overlays (branches and tags) removed from config ──
    _cleanup_stale_branches(configured_branches)


def _main_branch_labels() -> set[str]:
    """``branch`` labels of main-branch points (each git repo's main branch)."""
    try:
        from config_loader import get_repo_groups

        return {g["main_branch"] for g in get_repo_groups(config) if g.get("main_branch")}
    except Exception:  # noqa: BLE001 - no git repos configured or bad config
        return set()


def _cleanup_stale_branches(configured_branches: set[tuple[str, str]]) -> None:
    """Remove branch and tag overlays no longer in config from Qdrant and disk.

    Scans for overlay manifest files on disk. If an overlay is not in the
    configured set, deletes its Qdrant vectors, manifest file and chunk histogram.
    Vectors are deleted by the overlay's ``branch`` label (which also catches
    points the manifest never recorded) unless that label is the main branch
    of a configured repository; then only the manifest's point ids are
    deleted. When the delete fails the manifest is kept, so the next run
    retries.
    The log prefix comes from the manifest ``kind`` (inferred for old manifests).
    """
    from qdrant_client import models
    from shared.git_ops import sanitize_branch_name
    from shared.overlay import overlay_histogram_path, overlay_kind_from_manifest

    index_path = Path(config.get_index_path()).resolve()
    main_labels = _main_branch_labels()

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

        kind = overlay_kind_from_manifest(branch_data)
        label = f"[{kind.upper()}]"
        log(f"{label} Cleaning up removed {kind}: {branch_name}")

        # Delete all vectors for this branch from Qdrant
        all_ids = []
        for file_entry in branch_data.get("files", {}).values():
            all_ids.extend(file_entry.get("vector_ids", []))

        by_label = branch_name not in main_labels
        if all_ids or by_label:
            try:
                client = get_qdrant_client(config)
                # Delete in batches
                batch_size = 1000
                for batch_idx in range(0, len(all_ids), batch_size):
                    batch = all_ids[batch_idx : batch_idx + batch_size]
                    client.delete(
                        collection_name=config.COLLECTION_NAME,
                        points_selector=models.PointIdsList(points=batch),
                    )
                if by_label:
                    client.delete(
                        collection_name=config.COLLECTION_NAME,
                        points_selector=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="branch",
                                    match=models.MatchValue(value=branch_name),
                                )
                            ]
                        ),
                    )
                log(f"{label} Deleted {len(all_ids)} vectors for {branch_name}")
            except Exception as exc:
                log_warn(
                    f"{label} Failed to delete vectors for {branch_name}: {exc}. "
                    f"Keeping its manifest; the next run retries."
                )
                continue

        # Delete the manifest file
        try:
            manifest_file.unlink()
            log(f"{label} Deleted manifest for {branch_name}")
        except Exception as exc:
            log_warn(f"{label} Failed to delete manifest: {exc}")
        remove_journal(journal_path_for(manifest_file))

        histogram_file = overlay_histogram_path(manifest_file)
        if histogram_file != manifest_file and histogram_file.exists():
            try:
                histogram_file.unlink()
                log(f"{label} Deleted chunk histogram for {branch_name}")
            except Exception as exc:
                log_warn(f"{label} Failed to delete chunk histogram for {branch_name}: {exc}")


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


def refresh_changes_log_limit(cfg) -> int:
    """``LOG_REFRESH_CHANGES_MAX`` as a non-negative int (0 = no limit).

    Missing, invalid, zero or negative values all mean "list every path",
    the classic behaviour.
    """
    raw = getattr(cfg, "LOG_REFRESH_CHANGES_MAX", 0)
    if isinstance(raw, bool):
        return 0
    try:
        value = int(raw or 0)
    except (TypeError, ValueError):
        return 0
    return value if value > 0 else 0


def log_refresh_changes(
    actions, current_states, manifest_files, branch_label=None, branch_resolver=None
) -> None:
    """Log changes detected, grouped by SOURCE_DIRS directories.

    Args:
        actions: Dict with 'add', 'modify', 'delete' lists of path keys.
        current_states: Mapping of path key → file state info.
        manifest_files: Mapping of path key → manifest entry.
        branch_label: Fixed branch label appended to every filename
            (e.g. ``"feature/my-feature"`` for branch overlay runs).
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

    # LOG_REFRESH_CHANGES_MAX caps the listed paths per action (0 = list
    # all). VERBOSE always lists everything.
    path_limit = 0 if VERBOSE else refresh_changes_log_limit(config)

    def _log_group(action_label, grouped):
        log_raw(f"\n  [{action_label.upper()}]")
        # Replace empty string labels with "root" for display
        display_labels = [label if label else "root" for label in dir_labels]
        budget = path_limit
        hidden = 0
        for key in display_labels + ["other"]:
            # Map back to actual key (empty string -> "")
            actual_key = key if key != "root" else ""
            items = grouped.get(actual_key, [])
            if not items:
                continue
            log_raw(f"    {key}: {len(items)}")
            shown = items if not path_limit else items[: max(budget, 0)]
            for item in shown:
                log_raw(f"      - {item}{_item_suffix(item)}")
            if path_limit:
                budget -= len(shown)
                hidden += len(items) - len(shown)
        if hidden:
            log_raw(
                f"    ... {hidden:,} more {action_label} path(s) not listed "
                f"(LOG_REFRESH_CHANGES_MAX={path_limit}; VERBOSE lists all)"
            )

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
    entry.update(manifest_dialect_fields(file_info))
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
    """Perform refresh operations on Qdrant DB (see ``_perform_refresh_qdrant_impl``).

    Owns the manifest saver for the run. ``MANIFEST_SAVE_INTERVAL_S`` (default
    ``0``) keeps the classic behaviour: a synchronous save after every batch
    of processed files. A positive value saves at most every N seconds on a
    background thread, and always saves synchronously at the end of the run
    and when the run fails (exception or Ctrl+C), so a resume redoes at most
    N seconds of work. The manifest only ever holds files whose points were
    upserted, so every snapshot is safe to resume from.

    Before points of a file are deleted or upserted, the change is appended
    to the pending journal (``shared.pending_points``); a run killed before
    the manifest save is repaired by ``recover_pending_points`` on the next
    run.

    Returns True when the run reached Qdrant and every delete and upsert
    worked, False otherwise (Qdrant unreachable, failed deletes or upserts).
    """
    base_save = save_fn if save_fn is not None else save_manifest
    saver = ManifestSaver(base_save, interval_s=manifest_save_interval(config))
    journal = PendingJournal(_pending_journal_path(branch_label))
    try:
        outcome = _perform_refresh_qdrant_impl(
            actions,
            manifest,
            branch_label=branch_label,
            file_states=file_states,
            point_id_fn=point_id_fn,
            saver=saver,
            journal=journal,
        )
    except BaseException:
        if saver.background:
            try:
                saver.save_now(manifest)
                log_warn("[MANIFEST] run failed; progress saved for resume")
            except Exception as exc:  # noqa: BLE001 - keep the original error
                log_error(f"[MANIFEST] could not save manifest after failure: {exc}")
        raise
    finally:
        saver.close()
    saver.log_summary()
    if not outcome["reached_end"]:
        return False
    # The manifest in memory is the one just saved: keep only journal
    # entries it does not cover (failed deletes/upserts) for the next run.
    unresolved = journal.finish(manifest.get("files", {}))
    if unresolved:
        log_warn(
            f"[MANIFEST] {len(unresolved)} file(s) not in sync with Qdrant after "
            f"errors; the next run repairs them"
        )
    return outcome["errors"] == 0 and not unresolved


def _perform_refresh_qdrant_impl(
    actions,
    manifest,
    branch_label=None,
    file_states=None,
    point_id_fn=None,
    saver=None,
    journal=None,
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
        saver: ``ManifestSaver`` used for periodic and final manifest saves.
            ``None`` means a synchronous saver around ``save_manifest``.
        journal: ``PendingJournal`` that records each Qdrant change before it
            is made. ``None`` means the journal of this manifest.

    Returns:
        ``{"reached_end": bool, "errors": int}``: ``reached_end`` is False
        when Qdrant could not be reached; ``errors`` counts failed files.
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
        return {"reached_end": False, "errors": 0}

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
        check_provenance_for_indexing(
            client, config.COLLECTION_NAME, config, embed_model=embed_model
        )
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
            # Keyword index for the exact symbol lookup (SYMBOL_LOOKUP_K)
            ensure_symbol_payload_index(client)
            ensure_file_path_payload_index(client)
            # Store full provenance on newly created collection
            _write_new_collection_provenance(client, embed_model, dim)
        else:
            raise

    current_states = (
        file_states if file_states is not None else get_current_file_states()
    )
    if saver is None:
        saver = ManifestSaver(save_manifest)
    if journal is None:
        journal = PendingJournal(_pending_journal_path(branch_label))
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

    def _delete_vectors_for_files(file_keys: list[str]) -> None:
        """Delete all Qdrant points matching any of the given file paths.

        Batches ``file_path`` values into ``MatchAny`` filter deletes (chunk
        size ``QDRANT_DELETE_CHUNK_SIZE``, default 500) so a large refresh
        does not issue one RPC per file.

        Uses the canonical file_key produced by ``normalize_file_key()`` —
        keys are already in their final canonical form (using last path
        segment or map_to_path), no further mapping needed.

        When ``branch_label`` is set, also filters by branch so that only
        the overlay vectors are deleted (main-branch vectors are preserved).
        Without it only main-branch vectors are deleted; branch and tag
        overlay vectors of the same paths are preserved.
        """
        if not file_keys:
            return
        _delete_points_for_file_keys(
            client,
            list(file_keys),
            branch_label=branch_label,
            resolve_branch=_resolve_branch,
        )

    # Handle deletes first — batch by filter; drop manifest entries only
    # after the chunk's delete succeeded (keeps manifest consistent with
    # Qdrant when a delete fails).
    delete_keys = list(actions["delete"])
    if delete_keys:
        chunk_size = int(getattr(config, "QDRANT_DELETE_CHUNK_SIZE", 500) or 500)
        if chunk_size < 1:
            chunk_size = 500
        for offset in range(0, len(delete_keys), chunk_size):
            chunk = delete_keys[offset : offset + chunk_size]
            journal.record((k, None) for k in chunk)
            try:
                _delete_vectors_for_files(chunk)
            except Exception as e:
                total_files_errored += len(chunk)
                log_error(
                    f"Deleting vectors for {len(chunk)} files "
                    f"(chunk {offset // chunk_size + 1}): {e}"
                )
                continue
            for file_key in chunk:
                total_files_deleted += 1
                old_ids = manifest["files"].get(file_key, {}).get("vector_ids", [])
                total_vectors_deleted += len(old_ids)
                if file_key in manifest["files"]:
                    del manifest["files"][file_key]
            log(
                f"Deleted vectors for {len(chunk)} files "
                f"(chunk {offset // chunk_size + 1}, "
                f"{min(offset + chunk_size, len(delete_keys))}/{len(delete_keys)})"
            )
        # Persist deletions right away (one save, also in interval mode).
        saver.save_now(manifest)

    # Handle adds and modifies
    files_to_process = actions["add"] + actions["modify"]
    total_files = len(files_to_process)

    # Validate INDEX_PARSE_WORKERS before touching the collection: a bad
    # value must fail fast, not after HNSW indexing has been deferred
    # (nothing would restore it on that error path).
    _parse_workers = int(getattr(config, "INDEX_PARSE_WORKERS", 1) or 1)
    if _parse_workers < 1:
        _parse_workers = 1

    # ── Defer HNSW index building during bulk ingest (Option C) ──
    # Set indexing_threshold high so Qdrant skips HNSW construction
    # during upserts (segment optimizer still merges, but no expensive
    # graph building).  Restored to default after all upserts finish.
    # This reduces SSD I/O + CPU contention from background HNSW work
    # that was measured to double parse_file times in later quartiles.
    _hnsw_deferred = False
    _HNSW_DEFER_THRESHOLD = 200_000  # effectively infinite for our corpus
    _HNSW_RESTORE_THRESHOLD = 10_000  # Qdrant default
    if total_files > 0:
        try:
            client.update_collection(
                collection_name=config.COLLECTION_NAME,
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=_HNSW_DEFER_THRESHOLD,
                ),
            )
            _hnsw_deferred = True
            log(
                f"HNSW indexing deferred (indexing_threshold={_HNSW_DEFER_THRESHOLD:,}) "
                f"for bulk ingest of {total_files:,} files"
            )
        except Exception as exc:
            log_warn(f"Could not defer HNSW indexing: {exc}")

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
    _flush_seq: int = 0  # flush sequence counter for instrumentation

    # -- Pipelined embedding (EMBED_PIPELINE_DEPTH > 0) -------------------
    # Legacy flush is strictly serial on the main thread:
    #   drain -> dense (GPU busy) -> sanitize -> sparse (CPU, GPU idle)
    #   -> build points (CPU, GPU idle) -> submit upsert -> parse next pool
    # so the GPU idles during sparse/build and while the next pool is being
    # filled, and each pool ends with a tail where TEI's queue runs dry.
    # In pipeline mode the main thread only parses and submits pools:
    #   dense-worker(s): embed pool N (several pools in flight keep TEI's
    #                    queue full across pool boundaries)
    #   post-worker:     sanitize + sparse + build + upsert for pool N, in
    #                    dense-completion order (not FIFO)
    # Manifest bookkeeping stays on the main thread (_reap_pipeline), so no
    # other thread mutates the manifest dict while it is being saved.
    pipeline_depth = int(getattr(config, "EMBED_PIPELINE_DEPTH", 0) or 0)
    _dense_executor = None
    _post_executor = None
    _inflight: list = []  # (dense_future, done_future) per pool
    if pipeline_depth > 0:
        from shared.embedding import TEIEmbedding as _TEI

        _dense_workers = pipeline_depth if isinstance(embed_model, _TEI) else 1
        _dense_executor = ThreadPoolExecutor(
            max_workers=_dense_workers, thread_name_prefix="dense-worker"
        )
        _post_executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="post-worker"
        )
        log(
            f"Embedding pipeline enabled: depth={pipeline_depth} "
            f"dense_workers={_dense_workers}"
        )

    def _post_process_pool(flush_id, entries, all_docs, dense_future, t_sub):
        """post-worker: wait for dense, then sanitize/sparse/build/upsert."""
        dense_embeddings = list(dense_future.result())
        t_dense_done = time.perf_counter()
        dense_embeddings, fix_counts = sanitize_dense_vectors(dense_embeddings)
        for entry in entries:
            for i in range(len(entry.documents)):
                gi = entry.global_start + i
                if fix_counts[gi] > 0 and is_zero_vector(dense_embeddings[gi]):
                    text_preview = (entry.nodes[i].get_content() or "")[:200]
                    log_warn(
                        f"All-zero dense vector for node {i} "
                        f"in {entry.file_key}: {text_preview!r}"
                    )
        t0 = time.perf_counter()
        sparse_dicts_all = None
        if is_hybrid and sparse_fn is not None:
            with timing_tracker.measure("sparse_embedding"):
                sparse_dicts_all = embed_sparse_batch(sparse_fn, all_docs, cfg=config)
        t_sparse = time.perf_counter() - t0
        t0 = time.perf_counter()
        work_items = []
        for entry in entries:
            a, b = entry.global_start, entry.global_start + len(entry.documents)
            fs = sparse_dicts_all[a:b] if sparse_dicts_all is not None else None
            points, zero_count = _build_qdrant_points(
                nodes_or_payloads=entry.nodes,
                dense_vecs=dense_embeddings[a:b],
                ids=entry.ids,
                sparse_vectors=_sparse_dicts_to_vectors(fs) if fs is not None else None,
                is_hybrid=is_hybrid,
                resolve_branch=_resolve_branch,
                file_key=entry.file_key,
                verbose=VERBOSE,
            )
            work_items.append(
                {
                    "points": points,
                    "zero_count": zero_count,
                    "file_key": entry.file_key,
                    "ids": entry.ids,
                    "file_info": entry.file_info,
                    "action_type": entry.action_type,
                }
            )
        t_build = time.perf_counter() - t0
        t0 = time.perf_counter()
        counters = _do_background_upsert(work_items, apply_manifest=False)
        t_upsert = time.perf_counter() - t0
        log(
            f"[PIPE {flush_id:03d}] dense_wait={t_dense_done - t_sub:.3f}s "
            f"sparse={t_sparse:.3f}s build={t_build:.3f}s upsert={t_upsert:.3f}s "
            f"chunks={len(all_docs)} files={len(entries)}"
        )
        return counters

    def _apply_pipeline_result(result: dict) -> None:
        nonlocal total_vectors_added, total_files_added, total_files_modified
        nonlocal total_files_errored, total_zero_vectors_skipped
        nonlocal processed_since_save
        for file_key, entry in result.get("manifest_updates", []):
            manifest["files"][file_key] = entry
        total_vectors_added += result["vectors_added"]
        total_files_added += result["files_added"]
        total_files_modified += result["files_modified"]
        total_files_errored += result["files_errored"]
        total_zero_vectors_skipped += result["zero_vectors_skipped"]
        processed_since_save += result["files_processed"]
        if processed_since_save >= save_batch_size and saver.request(manifest):
            processed_since_save = 0

    def _reap_pipeline(max_inflight: int) -> None:
        """Apply finished pools (any order); block while too much is in flight.

        Blocks while more than *max_inflight* pools are still in the dense
        stage, or more than 2 * max_inflight pools are not fully applied
        (memory bound).  Pools complete out of order: a large pool must not
        hold back the slots of smaller pools submitted after it (head-of-line
        blocking left TEI with a single pool's requests in flight).
        Order does not matter for the index: pools hold disjoint files and
        point IDs, and the manifest is only updated here on the main thread.
        """
        while _inflight:
            done = [it for it in _inflight if it[1].done()]
            for it in done:
                _inflight.remove(it)
                _apply_pipeline_result(it[1].result())  # re-raises worker errors
            dense_pending = [it[0] for it in _inflight if not it[0].done()]
            if len(dense_pending) > max_inflight:
                wait(dense_pending, return_when=FIRST_COMPLETED)
            elif len(_inflight) > 2 * max_inflight:
                wait([it[1] for it in _inflight], return_when=FIRST_COMPLETED)
            else:
                return

    def _flush_pool_pipelined() -> None:
        nonlocal _flush_seq
        if pool.is_empty:
            return
        _flush_seq += 1
        flush_id = _flush_seq
        # Bound memory / in-flight work: wait until a slot is free.
        t0 = time.perf_counter()
        _reap_pipeline(pipeline_depth)
        t_wait = time.perf_counter() - t0
        entries = pool.files()  # copy of FileEntry list
        journal.record((e.file_key, e.file_info.get("hash")) for e in entries)
        all_docs = [d for e in entries for d in e.documents]
        log(
            f"Flushing pool #{flush_id}: {len(all_docs):,} chunks from "
            f"{len(entries)} files (pipelined, wait={t_wait:.3f}s, "
            f"inflight={len(_inflight)})"
        )

        def _dense_job(docs=all_docs):
            with timing_tracker.measure("embedding"):
                return embed_dense_batch(embed_model, docs, cfg=config)

        t_sub = time.perf_counter()
        dense_future = _dense_executor.submit(_dense_job)
        done_future: Future = Future()

        def _chain_post(df, args=(flush_id, entries, all_docs, dense_future, t_sub)):
            # Post-process as soon as THIS pool's dense finished (no FIFO).
            pf = _post_executor.submit(_post_process_pool, *args)

            def _relay(f):
                exc = f.exception()
                if exc is not None:
                    done_future.set_exception(exc)
                else:
                    done_future.set_result(f.result())

            pf.add_done_callback(_relay)

        dense_future.add_done_callback(_chain_post)
        _inflight.append((dense_future, done_future))
        pool.clear()

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
            if processed_since_save >= save_batch_size and saver.request(manifest):
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

        Emits a ``[FLUSH nn]`` log line with per-phase timings (ms precision)
        for instrumentation / GPU utilization analysis.
        """
        nonlocal _pending_upsert, _flush_seq

        if pipeline_depth > 0:
            return _flush_pool_pipelined()
        if pool.is_empty:
            return

        _flush_seq += 1
        flush_id = _flush_seq
        t_flush_start = time.perf_counter()

        # ── Step 1: Drain previous background upsert ─────────────
        t0 = time.perf_counter()
        _drain_pending_upsert()
        t_drain = time.perf_counter() - t0

        all_docs, file_entries = pool.collect()
        pool_chunks = len(all_docs)
        pool_files = pool.file_count
        log(
            f"Flushing pool #{flush_id}: {pool_chunks:,} chunks from {pool_files} files"
        )

        # ── Step 2: Dense embedding (main thread, GPU-bound) ─────
        t0 = time.perf_counter()
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
        t_dense = time.perf_counter() - t0

        dense_embeddings = list(dense_embeddings)

        # Sanitize dense vectors (replace -0.0/NaN/Inf with 0.0)
        t0 = time.perf_counter()
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
        t_sanitize = time.perf_counter() - t0

        # ── Step 3: Sparse embedding (main thread, CPU-bound) ────
        t0 = time.perf_counter()
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
        t_sparse = time.perf_counter() - t0

        # ── Step 4: Build per-file upsert work items (main thread, CPU) ──
        t0 = time.perf_counter()
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
        t_build = time.perf_counter() - t0

        # ── Step 5: Submit upsert to background thread ───────────
        # The background thread handles Qdrant I/O (releases GIL) while
        # the main thread continues parsing/chunking the next pool.
        t0 = time.perf_counter()
        journal.record(
            (item["file_key"], item["file_info"].get("hash"))
            for item in upsert_work_items
        )
        _pending_upsert = _upsert_executor.submit(
            _do_background_upsert, upsert_work_items
        )
        t_submit = time.perf_counter() - t0

        t_flush_total = time.perf_counter() - t_flush_start

        # ── Instrumentation summary line ─────────────────────────
        # Build dense sub-phase detail if available (TEI concurrent path)
        dense_detail = ""
        if (
            hasattr(embed_model, "last_concurrent_timings")
            and embed_model.last_concurrent_timings
        ):
            ct = embed_model.last_concurrent_timings
            dense_detail = (
                f" dense_sub[prep={ct['prep']:.3f}s "
                f"submit={ct['submit']:.3f}s "
                f"inflight={ct['inflight']:.3f}s "
                f"batches={ct['mini_batches']}]"
            )

        log(
            f"[FLUSH {flush_id:03d}] "
            f"drain={t_drain:.3f}s "
            f"dense={t_dense:.3f}s{dense_detail} "
            f"sanitize={t_sanitize:.3f}s "
            f"sparse={t_sparse:.3f}s "
            f"build={t_build:.3f}s "
            f"submit={t_submit:.3f}s "
            f"total={t_flush_total:.3f}s "
            f"chunks={pool_chunks} files={pool_files}"
        )

        # Cleanup pool immediately — data is captured in upsert_work_items
        pool.clear()
        gc.collect()
        cuda_clear_cache()

    def _do_background_upsert(
        work_items: list[dict], apply_manifest: bool = True
    ) -> dict:
        """Execute cross-file batched upserts on the background thread.

        Optimization: instead of upserting per-file (which produced 150+
        individual Qdrant calls per pool for small-file regions), we collect
        ALL points from ALL files into one flat list and upsert in batches
        of 500.  Manifest bookkeeping (pure CPU dict updates) runs after
        all upserts complete.

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
            "manifest_updates": [],
        }
        upsert_batch_size = int(getattr(config, "QDRANT_UPSERT_BATCH_SIZE", 500))
        upsert_max_bytes = int(
            getattr(config, "QDRANT_UPSERT_MAX_BYTES", DEFAULT_MAX_UPSERT_BYTES)
        )

        # ── Phase 1: Collect all points from all files ────────────
        all_points = []
        for item in work_items:
            counters["zero_vectors_skipped"] += item["zero_count"]
            all_points.extend(item["points"])

        # ── Phase 2: Bulk upsert across all files in batches ──────
        total_upserted = 0
        with timing_tracker.measure("upsert"):
            try:
                total_batches = upsert_in_batches(
                    lambda batch: client.upsert(
                        collection_name=config.COLLECTION_NAME, points=batch
                    ),
                    all_points,
                    max_points=upsert_batch_size,
                    max_bytes=upsert_max_bytes,
                    warn=lambda m: log_warn(f"[upsert-worker] {m}"),
                )
                total_upserted = len(all_points)
            except Exception as e:
                log_error(
                    f"[upsert-worker] Bulk upsert failed "
                    f"({len(all_points)} points, {len(work_items)} files): {e}"
                )
                # Mark ALL files as errored since we can't know which
                # points succeeded in a partial failure
                for item in work_items:
                    counters["files_errored"] += 1
                    counters["files_processed"] += 1
                return counters

        log(
            f"  [upsert-worker] Bulk upserted {total_upserted} vectors "
            f"({total_batches} batches) from {len(work_items)} files"
        )

        # ── Phase 3: Manifest bookkeeping (CPU only, no I/O) ─────
        for item in work_items:
            file_key = item["file_key"]
            m_entry = _make_manifest_entry(item["file_info"], item["ids"])
            if apply_manifest:
                manifest["files"][file_key] = m_entry
            else:
                counters["manifest_updates"].append((file_key, m_entry))
            counters["vectors_added"] += len(item["points"])
            if item["action_type"] == "add":
                counters["files_added"] += 1
            else:
                counters["files_modified"] += 1
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

    # ── Parse-ahead thread (Option A) ────────────────────────────
    # Background thread reads files and runs tree-sitter parsing while
    # the main thread embeds the current pool.  This overlaps CPU-bound
    # parsing with GPU-bound embedding, eliminating the ~1s inter-flush
    # gap measured in the baseline (201s / 22.8% of wall time).
    #
    # Queue maxsize=2: allows parser to be 1-2 files ahead without
    # unbounded memory.  None sentinel signals completion.
    _parse_q_size = int(getattr(config, "EMBED_PARSE_QUEUE_SIZE", 2) or 2)
    _parse_queue: queue.Queue[_ParsedFile | None] = queue.Queue(maxsize=_parse_q_size)
    _parser_error: list[BaseException] = []  # captures parser thread exception

    def _parse_one_file(
        file_index: int, file_key: str, file_info: dict
    ) -> _ParsedFile:
        """Parse a single file into a ``_ParsedFile`` (thread-safe)."""
        action_type = "add" if file_key in actions["add"] else "modify"
        t0 = time.perf_counter()
        nodes = load_nodes_for_file(file_info)
        parse_time = time.perf_counter() - t0
        # The entry must describe the content that was read, not the scan.
        file_info = _verify_unchanged_since_scan(file_key, file_info)

        is_empty_file = False
        is_no_content = False
        ids: list[str] = []
        documents: list[str] = []

        if not nodes:
            try:
                if Path(file_info["full_path"]).stat().st_size == 0:
                    is_empty_file = True
                else:
                    is_no_content = True
            except Exception:
                is_no_content = True
        else:
            ids = [_make_id(file_key, i) for i in range(len(nodes))]
            documents = [node.text for node in nodes]

        has_parse_error = bool(
            nodes and any(n.metadata.get("parse_error") for n in nodes)
        )
        return _ParsedFile(
            file_index=file_index,
            file_key=file_key,
            action_type=action_type,
            file_info=file_info,
            nodes=nodes or [],
            ids=ids,
            documents=documents,
            is_empty_file=is_empty_file,
            is_no_content=is_no_content,
            has_parse_error=has_parse_error,
            parse_time_s=parse_time,
        )

    def _parser_thread_fn() -> None:
        """Background thread: iterate files, parse, put results on queue.

        Runs the file I/O + tree-sitter parsing that was previously the
        inter-flush CPU gap.  Each parsed file is put on ``_parse_queue``
        for the main thread to consume, **in ``files_to_process`` order**
        (deterministic point IDs and manifest updates).

        With ``INDEX_PARSE_WORKERS == 1`` (default) parsing stays sequential.
        With ``N > 1`` a thread pool of size N parses ahead; tree-sitter
        releases the GIL so workers overlap on CPU. Results are still
        enqueued in input order.
        """
        parse_workers = _parse_workers
        try:
            if parse_workers == 1:
                for file_index, file_key in enumerate(files_to_process, start=1):
                    file_info = current_states.get(file_key)
                    if not file_info:
                        continue
                    parsed = _parse_one_file(file_index, file_key, file_info)
                    _parse_queue.put(parsed)
            else:
                from collections import deque

                pending: deque = deque()
                max_inflight = max(parse_workers * 2, parse_workers)
                items = list(enumerate(files_to_process, start=1))
                next_i = 0
                with ThreadPoolExecutor(max_workers=parse_workers) as pool:
                    while next_i < len(items) or pending:
                        while next_i < len(items) and len(pending) < max_inflight:
                            file_index, file_key = items[next_i]
                            next_i += 1
                            file_info = current_states.get(file_key)
                            if not file_info:
                                continue
                            pending.append(
                                pool.submit(
                                    _parse_one_file, file_index, file_key, file_info
                                )
                            )
                        if not pending:
                            break
                        # Oldest future first → same order as sequential path
                        parsed = pending.popleft().result()
                        _parse_queue.put(parsed)
        except Exception as exc:
            _parser_error.append(exc)
        finally:
            _parse_queue.put(None)  # sentinel: no more files

    # Start the parser thread (_parse_workers validated before HNSW defer)
    _parser_thread = threading.Thread(
        target=_parser_thread_fn,
        name="parse-ahead",
        daemon=True,
    )
    _parser_thread.start()
    log(
        f"Parse-ahead thread started (queue maxsize={_parse_q_size}, "
        f"INDEX_PARSE_WORKERS={_parse_workers})"
    )

    # ── Main loop: consume parsed files from queue ────────────────
    while True:
        parsed = _parse_queue.get()
        if parsed is None:
            # Sentinel: parser thread is done
            break

        # Check for parser thread error
        if _parser_error:
            raise _parser_error[0]

        file_key = parsed.file_key
        action_type = parsed.action_type
        file_info = parsed.file_info

        # Remove old points if modify. When that fails, the file is skipped
        # and keeps its old manifest entry: upserting anyway would leave the
        # old chunks beyond the new chunk count in Qdrant for good.
        if action_type == "modify" and file_key in manifest["files"]:
            journal.record([(file_key, None)])
            try:
                old_ids = manifest["files"][file_key].get("vector_ids", [])
                _delete_vectors_for_files([file_key])
                total_vectors_deleted += len(old_ids)
            except Exception as e:
                log_error(
                    f"Deleting old vectors for {file_key}: {e}; skipping the file, "
                    f"it is retried on the next refresh"
                )
                total_files_errored += 1
                continue

        file_branch = _resolve_branch(file_key)
        branch_tag = f" [{file_branch}]" if file_branch else ""
        log(f"Processing ({parsed.file_index}/{total_files}) {file_key}{branch_tag}...")

        # Record parse timing
        timing_tracker.record("parse_file", parsed.parse_time_s)

        nodes = parsed.nodes
        ids = parsed.ids
        documents = parsed.documents

        if not nodes:
            if parsed.is_empty_file:
                empty_files.append(file_key)
                manifest["files"][file_key] = _make_manifest_entry(
                    file_info, [], empty=True
                )
            else:
                no_content_files.append(file_key)
                manifest["files"][file_key] = _make_manifest_entry(
                    file_info, [], no_content=True
                )
            journal.record([(file_key, file_info.get("hash"))])
            log_warn(f"No content loaded for {file_key}")
            continue

        if parsed.has_parse_error:
            fallback_files.append(file_key)

        if VERBOSE:
            log(f"  Nodes: {len(nodes)}")

        # Track extension stats
        ext = Path(file_key).suffix.lower() or "(none)"
        ext_file_counts[ext] = ext_file_counts.get(ext, 0) + 1
        ext_node_counts[ext] = ext_node_counts.get(ext, 0) + len(nodes)

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
            if processed_since_save >= save_batch_size and saver.request(manifest):
                processed_since_save = 0
            continue

        # ── Single-pass path: add to cross-file pool ─────────────
        pool.add(file_key, file_info, nodes, ids, documents, action_type)

        if pool.should_flush():
            _flush_pool()
        elif _inflight:
            _reap_pipeline(pipeline_depth)

    # Check for parser thread error after sentinel
    if _parser_error:
        raise _parser_error[0]

    # Wait for parser thread to fully finish
    _parser_thread.join(timeout=5.0)

    # Final flush for remaining chunks in the pool
    _flush_pool()

    # Drain the last background upsert and shut down the executor
    try:
        _reap_pipeline(0)
        _drain_pending_upsert()
    finally:
        _upsert_executor.shutdown(wait=True)
        if _dense_executor is not None:
            _dense_executor.shutdown(wait=True)
            _post_executor.shutdown(wait=True)
    if processed_since_save > 0:
        saver.save_now(manifest)
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

            journal.record([(file_key, file_info.get("hash"))])
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
            if processed_since_save >= save_batch_size and saver.request(manifest):
                processed_since_save = 0

        with timing_tracker.measure("sqlite_cleanup"):
            cleanup_sqlite(sqlite_db_path)
        log("Temp SQLite store cleaned up")

    # ── Restore HNSW indexing after bulk ingest ─────────────────
    # This triggers Qdrant's background optimizer to build HNSW graphs
    # for all segments that accumulated during the deferred period.
    if _hnsw_deferred:
        try:
            client.update_collection(
                collection_name=config.COLLECTION_NAME,
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=_HNSW_RESTORE_THRESHOLD,
                ),
            )
            log(
                f"HNSW indexing restored (indexing_threshold={_HNSW_RESTORE_THRESHOLD:,}) "
                f"— background optimizer will build indexes"
            )
        except Exception as exc:
            log_warn(
                f"Could not restore HNSW indexing threshold: {exc}. "
                f"Manually set indexing_threshold={_HNSW_RESTORE_THRESHOLD} "
                f"via Qdrant API if search is slow."
            )

    saver.save_now(manifest)
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
    return {"reached_end": True, "errors": total_files_errored}


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
    "--version",
    action="version",
    version=f"hybrid-code-rag-mcp {HCR_VERSION}",
)
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

# SYMBOLS_PER_SPLIT_PART / SYMBOLS_MAX_PER_CHUNK for the readers (defaults
# keep the classic payload).
_symbol_policy = configure_symbol_policy(config)

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

log(f"hybrid-code-rag-mcp {HCR_VERSION} indexer")
if not _symbol_policy.is_default:
    log(
        f"Symbols payload: per_split_part={_symbol_policy.per_split_part} "
        f"max_per_chunk={_symbol_policy.max_per_chunk or 'unlimited'}"
    )


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

    For branch and tag overlays, reads changed files via git and generates
    separate per-overlay histogram files (``chunk_histogram_branch_<name>.json``).
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

    # ── Overlay histograms (branches and tags) ──
    repo_groups = get_repo_groups(config)
    from shared.overlay import configured_overlays

    has_branches = any(configured_overlays(g) for g in repo_groups)

    if has_branches:
        from shared.git_ops import GitError, read_files_to_temp_dir
        from shared.overlay import diff_overlay

        for group in repo_groups:
            repo_path = group["repo_path"]
            main_branch = group["main_branch"]

            for spec in configured_overlays(group):
                feature_branch = spec["name"]
                log(f"[HISTOGRAM] Processing branch overlay: {feature_branch}")

                git_prefixes = group.get("git_prefixes", [])
                try:
                    diff = diff_overlay(
                        repo_path,
                        main_branch,
                        spec,
                        paths=git_prefixes if git_prefixes else None,
                    )
                except GitError as exc:
                    log_warn(f"[HISTOGRAM] Cannot diff {feature_branch}: {exc}")
                    continue
                if diff is None:
                    log_warn(
                        f"[HISTOGRAM] Overlay '{feature_branch}' not found, skipping"
                    )
                    continue

                changes = diff.changes
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
                        repo_path, diff.read_at, add_modify_paths
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

# Ensure TEI is running if configured (auto-start Docker container).
# Not for EMBEDDING_MODE = "remote" or the OpenAI-compatible backend.
if uses_tei_container(config):
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

    # Branch-overlay manifests too: otherwise the overlay is reported as
    # "up to date" after --clear and its points are never re-indexed.
    for branch_manifest in Path(config.get_index_path()).glob(
        "index_manifest_branch_*.json"
    ):
        branch_manifest.unlink()
        log(f"Deleted branch manifest {branch_manifest.name}")

    for journal_file in Path(config.get_index_path()).glob(
        "index_manifest*" + JOURNAL_SUFFIX
    ):
        journal_file.unlink()
        log(f"Deleted pending journal {journal_file.name}")

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

    # Resolve which GPU index to monitor.
    # TEI path: TEI_GPU tells us which GPU the Docker container uses.
    # PyTorch path: INDEX_EMBED_DEVICE tells us the CUDA device.
    _monitor_gpu: int | None = None
    if getattr(config, "USE_TEI", False):
        _tei_gpu = str(getattr(config, "TEI_GPU", "auto")).strip().lower()
        if _tei_gpu == "cpu":
            _monitor_gpu = None  # no GPU to monitor
        elif _tei_gpu in ("auto", ""):
            # TEI auto-selected the best GPU — resolve the same way docker_utils does
            try:
                from shared.docker_utils import _detect_available_gpus, _pick_best_gpu

                _gpus = _detect_available_gpus()
                if _gpus:
                    _monitor_gpu = _pick_best_gpu(_gpus)["index"]
            except Exception:
                pass
        else:
            try:
                _monitor_gpu = int(_tei_gpu)
            except ValueError:
                pass
    else:
        _dev = str(getattr(config, "INDEX_EMBED_DEVICE", "cpu")).strip().lower()
        if _dev in ("auto", "cuda"):
            try:
                from shared.docker_utils import _detect_available_gpus, _pick_best_gpu

                _gpus = _detect_available_gpus()
                if _gpus:
                    _monitor_gpu = _pick_best_gpu(_gpus)["index"]
            except Exception:
                pass
        elif _dev.startswith("cuda:"):
            try:
                _monitor_gpu = int(_dev.split(":")[1])
            except (ValueError, IndexError):
                pass
        elif _dev.isdigit():
            _monitor_gpu = int(_dev)
        # else: cpu — _monitor_gpu stays None

    start_gpu_stats(_stats_file, interval=0.33, gpu_index=_monitor_gpu)
else:
    stop_gpu_stats = None  # type: ignore[assignment]

_exit_code = 0
try:
    run_indexing(mode)
except PendingRecoveryError as exc:
    log_error(f"Stopped: {exc}. Fix Qdrant and run again; the journal is kept.")
    _exit_code = 3
finally:
    if stop_gpu_stats is not None:
        stop_gpu_stats()
    cuda_clear_cache()
    from shared.log import close_tee

    close_tee()

if _exit_code:
    sys.exit(_exit_code)
