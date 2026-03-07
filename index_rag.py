"""
Main entry point for RAG indexer.
"""

import os
import sys
import json
import shutil
import uuid
import time
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

os.environ["TORCHVISION_DISABLE_META_REGISTRATIONS"] = "1"

import argparse

import config_loader
from shared.log import log, log_raw, log_error, log_warn
from shared.embedding import get_embed_model
from shared.indexing import load_all_sources
from shared.manifest import compute_file_hash, is_excluded, normalize_file_key


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
    """Resolve a stored file_path to an actual file on disk."""
    normalized = file_path.replace("\\", "/")
    # Strip leading "./" properly (prefix, not character set)
    if normalized.startswith("./"):
        normalized = normalized[2:]
    candidate = Path(normalized)
    if candidate.exists():
        return candidate

    # If the metadata already includes a base prefix, try it directly
    for source_dir in config.SOURCE_DIRS:
        prefix = source_dir["path"].replace("\\", "/")
        if normalized.startswith(prefix + "/"):
            candidate = Path(normalized)
            if candidate.exists():
                return candidate

    # Try under each configured source root
    for source_dir in config.SOURCE_DIRS:
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
    for source_dir in config.SOURCE_DIRS:
        root_abs = Path(source_dir["path"]).resolve()
        try:
            rel = resolved_abs.relative_to(root_abs).as_posix()
            return normalize_file_key(source_dir["path"], rel)
        except ValueError:
            continue

    return cleaned


def regenerate_manifest_qdrant():
    """Rebuild the manifest by scanning the Qdrant collection."""
    from qdrant.vector_store import get_qdrant_vector_store
    from qdrant_client.http.exceptions import UnexpectedResponse

    log("[REGENERATE MANIFEST] Scanning Qdrant collection...")
    _, client, _ = get_qdrant_vector_store(cfg=config)
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
            file_path = payload.get("file_path")
            if not file_path:
                continue
            normalized = normalize_manifest_key(file_path)
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


def get_current_file_states():
    """Get current state of all source files, driven by config.SOURCE_DIRS."""
    states = {}

    for source_dir in config.SOURCE_DIRS:
        dir_path = Path(source_dir["path"])
        if not dir_path.exists():
            continue
        exclude_patterns = source_dir.get("exclude", [])
        for ext in source_dir["extensions"]:
            for f in dir_path.rglob(f"*{ext}"):
                if f.is_file() and not is_excluded(f, exclude_patterns):
                    try:
                        mtime = f.stat().st_mtime
                        hash_val = compute_file_hash(f)
                        relative_path = f.relative_to(dir_path).as_posix()
                        path_key = normalize_file_key(source_dir["path"], relative_path)
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


def run_indexing(mode="full"):
    """Run the indexing process: full rebuild or incremental refresh."""
    if mode == "full":
        return run_full_indexing()
    else:
        return run_refresh_indexing()


def run_full_indexing():
    """Run the full indexing process."""
    from llama_index.core import VectorStoreIndex

    log("[STORE TYPE] Using Qdrant backend")

    embed_model = get_embed_model()

    from qdrant.vector_store import get_qdrant_vector_store

    storage_context, qdrant_client, _ = get_qdrant_vector_store(cfg=config)

    all_nodes, file_states = load_all_sources()

    step = len(config.SOURCE_DIRS) + 2
    log(f"[{step}/{step}] Creating vector index and embedding...")
    index = VectorStoreIndex(
        all_nodes,
        embed_model=embed_model,
        storage_context=storage_context,
        embed_batch_size=config.EMBED_BATCH_SIZE,
        show_progress=True,
    )

    log("Persisting to disk...")
    index.storage_context.persist(persist_dir=config.get_index_path())

    # Build manifest from file_states (canonical path keys with hashes)
    manifest = {"files": {}}
    for path_key, state in file_states.items():
        manifest["files"][path_key] = {
            "file_path": path_key,
            "mtime": state["mtime"],
            "hash": state["hash"],
            "vector_ids": [],  # IDs not easily accessible in full-index path
        }
    save_manifest(manifest)

    # Per-extension summary
    ext_counts: dict[str, int] = {}
    for node in all_nodes:
        fp = node.metadata.get("file_path", "")
        ext = Path(fp).suffix.lower() if fp else "(none)"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

    log_raw()
    log_raw("=" * 70)
    log_raw("INDEX CREATED SUCCESSFULLY")
    log_raw("=" * 70)
    log_raw(f"  TOTAL NODES: {len(all_nodes):>6}")
    for ext in sorted(ext_counts):
        log_raw(f"    {ext}: {ext_counts[ext]:>6} nodes")
    log_raw("=" * 70)
    log_raw()

    log(f"Index persisted to: {config.get_index_path()}")


def run_refresh_indexing():
    """Run incremental refresh process."""
    log("[MODE] Refreshing index incrementally...")

    manifest = load_manifest()
    if not manifest or "files" not in manifest:
        log("No valid manifest found for refresh - switching to full indexing")
        return run_full_indexing()

    # Get current file states
    current_states = get_current_file_states()

    # Determine actions
    actions = determine_actions(manifest["files"], current_states)

    if not actions["add"] and not actions["modify"] and not actions["delete"]:
        log("No changes detected - index is up to date")
        if VERBOSE:
            log_verbose_refresh(actions, current_states, manifest["files"])
        return

    log(
        f"Found {len(actions['add'])} new, "
        f"{len(actions['modify'])} modified, "
        f"{len(actions['delete'])} deleted"
    )
    log_refresh_changes(actions, current_states, manifest["files"])
    if VERBOSE:
        log_verbose_refresh(actions, current_states, manifest["files"])

    # Perform updates
    perform_refresh_qdrant(actions, manifest)


def determine_actions(old_files, current_states):
    """Determine what files to add, modify, delete."""
    actions = {"add": [], "modify": [], "delete": []}

    # Find adds and modifies
    for path_key, current in current_states.items():
        if path_key not in old_files:
            actions["add"].append(path_key)
        else:
            old_entry = old_files[path_key]
            if current["hash"] != old_entry.get("hash", "") or int(
                current["mtime"]
            ) != int(old_entry.get("mtime", 0)):
                actions["modify"].append(path_key)

    # Find deletes
    for path_key in old_files:
        if path_key not in current_states:
            actions["delete"].append(path_key)

    return actions


def log_refresh_changes(actions, current_states, manifest_files) -> None:
    """Log changes detected, grouped by SOURCE_DIRS directories."""

    # Build prefix list dynamically from config
    dir_prefixes = [
        sd["path"].replace("\\", "/").rstrip("/") + "/"
        for sd in config.SOURCE_DIRS
    ]
    dir_labels = [sd["path"] for sd in config.SOURCE_DIRS]

    def classify(path_value: str) -> str:
        normalized = path_value.replace("\\", "/")
        for prefix, label in zip(dir_prefixes, dir_labels):
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

    def _log_group(action_label, grouped):
        log_raw(f"\n  [{action_label.upper()}]")
        for key in list(dir_labels) + ["other"]:
            items = grouped.get(key, [])
            if not items:
                continue
            log_raw(f"    {key}: {len(items)}")
            for item in items:
                log_raw(f"      - {item}")

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


def perform_refresh_qdrant(actions, manifest):
    """Perform refresh operations on Qdrant DB."""
    from qdrant_client import QdrantClient, models
    from qdrant_client.http.exceptions import UnexpectedResponse
    from qdrant.vector_store import get_sparse_encoder, detect_collection_mode

    if config.QDRANT_USE_DOCKER:
        client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    else:
        qdrant_path = config.get_index_path()
        client = QdrantClient(path=qdrant_path)

    embed_model = get_embed_model()
    indexing_mode = getattr(config, "INDEXING_MODE", "dense")

    # Get sparse encoder if needed
    sparse_fn = None
    if indexing_mode in ("hybrid", "sparse"):
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
    except UnexpectedResponse as exc:
        if "doesn't exist" in str(exc) or "Not found" in str(exc):
            dim = get_embedding_dim()
            if indexing_mode in ("hybrid", "sparse") and sparse_fn is not None:
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
        else:
            raise

    current_states = get_current_file_states()
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
    ext_node_counts: dict[str, int] = {}
    ext_file_counts: dict[str, int] = {}

    def _delete_vectors_for_file(file_key: str) -> None:
        """Delete all Qdrant points matching a file path.

        Uses an exact match on the canonical file_key produced by
        ``normalize_file_key()`` — no variants needed since all keys
        are normalised through a single source of truth.
        """
        selector = models.Filter(
            must=[
                models.FieldCondition(
                    key="file_path",
                    match=models.MatchValue(value=file_key),
                )
            ]
        )
        client.delete(
            collection_name=config.COLLECTION_NAME,
            points_selector=selector,
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
        save_manifest(manifest)

    # Handle adds and modifies
    files_to_process = actions["add"] + actions["modify"]
    total_files = len(files_to_process)
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

        log(f"Processing ({file_index}/{total_files}) {file_key}...")

        # Track per-operation timing
        with timing_tracker.measure("parse_file"):
            nodes = load_nodes_for_file(file_info)

        if not nodes:
            try:
                if Path(file_info["full_path"]).stat().st_size == 0:
                    empty_files.append(file_key)
                    manifest["files"][file_key] = {
                        "file_path": file_info["file_path"],
                        "mtime": file_info["mtime"],
                        "hash": file_info["hash"],
                        "vector_ids": [],
                        "empty": True,
                    }
                else:
                    no_content_files.append(file_key)
                    manifest["files"][file_key] = {
                        "file_path": file_info["file_path"],
                        "mtime": file_info["mtime"],
                        "hash": file_info["hash"],
                        "vector_ids": [],
                        "no_content": True,
                    }
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

        # Convert to Qdrant points
        points = []
        ids = [make_qdrant_point_id(file_key, i) for i in range(len(nodes))]

        documents = [node.text for node in nodes]

        # Sort by text length for better memory locality
        sorted_pairs = sorted(zip(documents, ids, nodes), key=lambda x: len(x[0]))
        documents, ids, nodes = zip(*sorted_pairs) if sorted_pairs else ([], [], [])
        documents = list(documents)
        ids = list(ids)
        nodes = list(nodes)

        # Always track embedding time
        with timing_tracker.measure("embedding"):
            total_nodes = len(documents)
            max_tokens = config.EMBED_BATCH_MAX_TOKENS
            batch_docs = []
            batch_chars = 0
            embedded_count = 0
            embeddings = []

            def process_batch(batch):
                nonlocal embedded_count
                t0 = time.perf_counter()
                batch_emb = embed_model.get_text_embedding_batch(batch)
                t1 = time.perf_counter()
                if hasattr(batch_emb, "tolist"):
                    batch_emb = batch_emb.tolist()
                embeddings.extend(batch_emb)
                embedded_count += len(batch)
                if VERBOSE:
                    log(f"  Embedded {embedded_count}/{total_nodes} nodes ({t1 - t0:.2f}s)")

            for doc in documents:
                doc_chars = len(doc)
                if batch_docs and (batch_chars + doc_chars) > max_tokens * 4:
                    process_batch(batch_docs)
                    batch_docs = []
                    batch_chars = 0
                batch_docs.append(doc)
                batch_chars += doc_chars

            if batch_docs:
                process_batch(batch_docs)

        embeddings = (
            embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings
        )

        # Generate sparse embeddings if hybrid mode
        sparse_vectors = None
        if is_hybrid and sparse_fn is not None:
            with timing_tracker.measure("sparse_embedding"):
                sparse_indices, sparse_values = sparse_fn(documents)
                sparse_vectors = [
                    models.SparseVector(indices=idx, values=vals)
                    for idx, vals in zip(sparse_indices, sparse_values)
                ]

        for i, (node, dense_vec, vid) in enumerate(zip(nodes, embeddings, ids)):
            text_value = node.get_content() or ""
            payload = {
                **node.metadata,
                "text": text_value,
            }
            if is_hybrid and sparse_vectors is not None:
                vector = {
                    "text-dense": dense_vec,
                    "text-sparse-new": sparse_vectors[i],
                }
            else:
                vector = dense_vec
            point = models.PointStruct(id=vid, vector=vector, payload=payload)
            points.append(point)

        # Add to Qdrant (batch upsert to avoid 400 errors on large files)
        with timing_tracker.measure("upsert"):
            try:
                batch_size = 500
                total_batches = (len(points) + batch_size - 1) // batch_size
                for batch_idx in range(total_batches):
                    start_idx = batch_idx * batch_size
                    end_idx = min(start_idx + batch_size, len(points))
                    batch = points[start_idx:end_idx]
                    client.upsert(collection_name=config.COLLECTION_NAME, points=batch)
                total_vectors_added += len(points)
                if action_type == "add":
                    total_files_added += 1
                else:
                    total_files_modified += 1
                log(f"  Added {len(points)} vectors for {file_key}")

                # Update manifest
                manifest["files"][file_key] = {
                    "file_path": file_info["file_path"],
                    "mtime": file_info["mtime"],
                    "hash": file_info["hash"],
                    "vector_ids": ids,
                }
            except Exception as e:
                total_files_errored += 1
                log_error(f"Adding {file_key}: {e}")

        processed_since_save += 1
        if processed_since_save >= save_batch_size:
            save_manifest(manifest)
            processed_since_save = 0

    save_manifest(manifest)
    log("Refresh completed")

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

    # Warnings section
    has_warnings = fallback_files or empty_files or no_content_files
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
args = parser.parse_args()

config = config_loader.get_config(config_path=args.config)

VERBOSE = args.verbose

# Initialize timing tracker with verbose setting
timing_tracker = TimingTracker(verbose=VERBOSE)

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
    from qdrant_client import QdrantClient

    if config.QDRANT_USE_DOCKER:
        client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    else:
        client = QdrantClient(path=config.get_index_path())
    try:
        client.delete_collection(collection_name=config.COLLECTION_NAME)
        log(f"Deleted collection '{config.COLLECTION_NAME}'")
    except Exception as e:
        log_warn(f"Collection may not exist: {e}")

    manifest_path = get_manifest_path()
    if manifest_path.exists():
        manifest_path.unlink()
        log("Deleted manifest")

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

run_indexing(mode)
