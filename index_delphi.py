"""
Main entry point for Informica RAG indexer.

Supports both Chroma and Qdrant backends based on config.py STORE_TYPE setting.
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
import chromadb

os.environ["TORCHVISION_DISABLE_META_REGISTRATIONS"] = "1"

import argparse

import config
from shared.embedding import get_embed_model
from shared.indexing import load_all_sources
from shared.manifest import compute_file_hash
from qdrant import fix_paths as qdrant_fix_paths


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
            print(f"        {name}: {elapsed:.3f}s ({count} items)")

    def print_summary(self):
        print("\n" + "=" * 70)
        print("TIMING SUMMARY")
        print("=" * 70)
        total = sum(self.timings.values())
        for name, elapsed in sorted(self.timings.items(), key=lambda x: -x[1]):
            count = self.counts[name]
            pct = 100 * elapsed / total if total > 0 else 0
            print(f"  {name:30s}: {elapsed:8.2f}s ({count:5d} items) {pct:5.1f}%")
        print("-" * 70)
        print(f"  {'TOTAL':30s}: {total:8.2f}s")
        print("=" * 70 + "\n")


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
    """Regenerate manifest based on store type."""
    if config.STORE_TYPE == "chroma":
        from chroma.index_chroma import (
            regenerate_manifest_from_index as chroma_regenerate_manifest,
        )

        chroma_regenerate_manifest()
    else:
        regenerate_manifest_qdrant()


def resolve_manifest_path(file_path: str) -> Path | None:
    """Resolve a stored file_path to an actual file on disk."""
    normalized = file_path.replace("\\", "/").lstrip("./")
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
    """Normalize a manifest key to include the source dir prefix when possible."""
    normalized = file_path.replace("\\", "/").lstrip("./")
    resolved = resolve_manifest_path(normalized)
    if not resolved:
        return normalized

    resolved_abs = resolved.resolve()
    for source_dir in config.SOURCE_DIRS:
        root_abs = Path(source_dir["path"]).resolve()
        try:
            rel = resolved_abs.relative_to(root_abs).as_posix()
            return f"{source_dir['path']}/{rel}"
        except ValueError:
            continue

    return normalized


def regenerate_manifest_qdrant():
    """Rebuild the manifest by scanning the Qdrant collection."""
    from qdrant.vector_store import get_qdrant_vector_store
    from qdrant_client.http.exceptions import UnexpectedResponse

    print("\n[REGENERATE MANIFEST] Scanning Qdrant collection...")
    _, client, _ = get_qdrant_vector_store()
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
                print(f"      Collection '{config.COLLECTION_NAME}' not found.")
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
    print("      Manifest rebuilt from Qdrant collection")


def fix_paths():
    """Fix paths based on store type."""
    if config.STORE_TYPE == "chroma":
        from chroma.index_chroma import fix_absolute_paths as chroma_fix_paths

        chroma_fix_paths()
    else:
        qdrant_fix_paths.fix_absolute_paths()


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
        for ext in source_dir["extensions"]:
            for f in dir_path.rglob(f"*{ext}"):
                if f.is_file():
                    try:
                        mtime = f.stat().st_mtime
                        hash_val = compute_file_hash(f)
                        relative_path = f.relative_to(dir_path).as_posix()
                        path_key = f"{source_dir['path']}/{relative_path}"
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
    print(f"\n[WARNING] {message}")
    print("This will take a VERY LONG TIME and may be resource-intensive.")
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

    print(f"\n[STORE TYPE] Using {config.STORE_TYPE.upper()} backend")

    embed_model = get_embed_model()

    if config.STORE_TYPE == "chroma":
        from chroma.vector_store import get_chroma_vector_store

        storage_context, db, collection = get_chroma_vector_store()
    else:
        from qdrant.vector_store import get_qdrant_vector_store

        storage_context, qdrant_client, _ = get_qdrant_vector_store()

    all_nodes, file_states = load_all_sources()

    step = len(config.SOURCE_DIRS) + 2
    print(f"\n[{step}/{step}] Creating vector index and embedding...")
    index = VectorStoreIndex(
        all_nodes,
        embed_model=embed_model,
        storage_context=storage_context,
        embed_batch_size=config.EMBED_BATCH_SIZE,
        show_progress=True,
    )

    print("      Persisting to disk...")
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

    print("\n" + "=" * 70)
    print("Delphi RAG Index Created Successfully")
    print(f"  TOTAL NODES: {len(all_nodes):>6}")
    for ext in sorted(ext_counts):
        print(f"    {ext}: {ext_counts[ext]:>6} nodes")
    print("=" * 70 + "\n")

    print(f"Index persisted to: {config.get_index_path()}")


def run_refresh_indexing():
    """Run incremental refresh process."""
    print("\n[MODE] Refreshing index incrementally...")

    manifest = load_manifest()
    if not manifest or "files" not in manifest:
        print("No valid manifest found for refresh - switching to full indexing")
        return run_full_indexing()

    # Get current file states
    current_states = get_current_file_states()

    # Determine actions
    actions = determine_actions(manifest["files"], current_states)

    if not actions["add"] and not actions["modify"] and not actions["delete"]:
        print("No changes detected - index is up to date")
        if VERBOSE:
            log_verbose_refresh(actions, current_states, manifest["files"])
        return

    print(
        f"  Found {len(actions['add'])} new files, {len(actions['modify'])} modified, {len(actions['delete'])} deleted"
    )
    log_refresh_changes(actions, current_states, manifest["files"])
    if VERBOSE:
        log_verbose_refresh(actions, current_states, manifest["files"])

    # Perform updates
    if config.STORE_TYPE == "chroma":
        perform_refresh_chroma(actions, manifest)
    else:
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

    def log_group(action_label, grouped):
        print(f"\n  [{action_label.upper()}]")
        for key in list(dir_labels) + ["other"]:
            items = grouped.get(key, [])
            if not items:
                continue
            print(f"    {key}: {len(items)}")
            for item in items:
                print(f"      - {item}")

    if actions["add"]:
        log_group("add", add_grouped)
    if actions["modify"]:
        log_group("modify", modify_grouped)
    if actions["delete"]:
        log_group("delete", delete_grouped)


def log_verbose_refresh(actions, current_states, manifest_files) -> None:
    """Verbose diagnostics for refresh operations."""
    print("\n[VERBOSE]")
    print(f"  Manifest entries: {len(manifest_files):,}")
    print(f"  Current files:    {len(current_states):,}")

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
        print(f"  {label} extensions: {top}")

    def print_diff_samples(label, items, limit=5):
        if not items:
            return
        print(f"  {label} samples:")
        for item in items[:limit]:
            current = current_states.get(item)
            previous = manifest_files.get(item)
            cur_mtime = int(current["mtime"]) if current else None
            cur_hash = current.get("hash") if current else None
            prev_mtime = int(previous.get("mtime", 0)) if previous else None
            prev_hash = previous.get("hash") if previous else None
            print(
                f"    {item} | mtime {prev_mtime} -> {cur_mtime} | hash {prev_hash} -> {cur_hash}"
            )

    print_diff_samples("add", actions["add"])
    print_diff_samples("modify", actions["modify"])
    print_diff_samples("delete", actions["delete"])


def perform_refresh_chroma(actions, manifest):
    """Perform refresh operations on Chroma DB."""
    db = chromadb.PersistentClient(path=config.get_index_path())
    collection = db.get_or_create_collection(config.COLLECTION_NAME)

    embed_model = get_embed_model()

    current_states = get_current_file_states()
    fallback_files = []
    empty_files = []
    no_content_files = []
    save_batch_size = 10
    processed_since_save = 0

    # Handle deletes first
    for file_key in actions["delete"]:
        vector_ids = manifest["files"][file_key].get("vector_ids", [])
        if vector_ids:
            try:
                collection.delete(ids=vector_ids)
                print(f"      Deleted vectors for {file_key}")
            except Exception as e:
                print(f"      Error deleting {file_key}: {e}")
        del manifest["files"][file_key]

    if actions["delete"]:
        save_manifest(manifest)

    # Handle adds and modifies (reload and insert)
    files_to_process = actions["add"] + actions["modify"]
    total_files = len(files_to_process)
    for file_index, file_key in enumerate(files_to_process, start=1):
        action_type = "add" if file_key in actions["add"] else "modify"
        # Remove old ids if modify
        if action_type == "modify" and file_key in manifest["files"]:
            vector_ids = manifest["files"][file_key].get("vector_ids", [])
            if vector_ids:
                try:
                    collection.delete(ids=vector_ids)
                    print(f"      Removed old vectors for {file_key}")
                except Exception as e:
                    print(f"      Error removing old {file_key}: {e}")

        # Load and add new content
        file_info = current_states.get(file_key)
        if not file_info:
            continue

        print(f"      Processing ({file_index}/{total_files}) {file_key}...")

        # Load nodes for this file
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
            print(f"      No content loaded for {file_key}")
            continue

        if any(node.metadata.get("parse_error") for node in nodes):
            fallback_files.append(file_key)

        if VERBOSE:
            print(f"      Nodes: {len(nodes)}")

        # Convert nodes to Chroma format
        id_prefix = file_key.replace("/", "__")
        ids = [f"{id_prefix}_{i}" for i in range(len(nodes))]
        documents = [node.text for node in nodes]
        metadatas = [node.metadata for node in nodes]

        # Sort by text length for better memory locality (reduces CUDA allocator stalls)
        sorted_pairs = sorted(
            zip(documents, ids, metadatas, nodes), key=lambda x: len(x[0])
        )
        documents, ids, metadatas, nodes = (
            zip(*sorted_pairs) if sorted_pairs else ([], [], [], [])
        )
        documents = list(documents)
        ids = list(ids)
        metadatas = list(metadatas)
        nodes = list(nodes)

        # Embed documents
        if VERBOSE:
            embeddings = []
            total_nodes = len(documents)
            max_tokens = config.EMBED_BATCH_MAX_TOKENS
            batch_docs = []
            batch_chars = 0
            embedded_count = 0

            for doc in documents:
                doc_chars = len(doc)
                # Rough estimate: ~4 chars per token
                doc_tokens = doc_chars // 4

                # Start new batch if adding this doc would exceed limit
                if batch_docs and (batch_chars + doc_chars) > max_tokens * 4:
                    # Process current batch
                    t0 = time.perf_counter()
                    batch_emb = embed_model.get_text_embedding_batch(batch_docs)
                    t1 = time.perf_counter()
                    if hasattr(batch_emb, "tolist"):
                        batch_emb = batch_emb.tolist()
                    embeddings.extend(batch_emb)
                    embedded_count += len(batch_docs)
                    print(
                        f"      [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Embedded {embedded_count}/{total_nodes} nodes ({t1 - t0:.2f}s)"
                    )
                    batch_docs = []
                    batch_chars = 0

                batch_docs.append(doc)
                batch_chars += doc_chars

            # Process remaining
            if batch_docs:
                t0 = time.perf_counter()
                batch_emb = embed_model.get_text_embedding_batch(batch_docs)
                t1 = time.perf_counter()
                if hasattr(batch_emb, "tolist"):
                    batch_emb = batch_emb.tolist()
                embeddings.extend(batch_emb)
                embedded_count += len(batch_docs)
                print(
                    f"      [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Embedded {embedded_count}/{total_nodes} nodes ({t1 - t0:.2f}s)"
                )
        else:
            # Non-verbose: sort by length and batch by size
            max_tokens = config.EMBED_BATCH_MAX_TOKENS
            embeddings = []
            batch_docs = []
            batch_chars = 0

            for doc in documents:
                doc_chars = len(doc)
                if batch_docs and (batch_chars + doc_chars) > max_tokens * 4:
                    batch_emb = embed_model.get_text_embedding_batch(batch_docs)
                    if hasattr(batch_emb, "tolist"):
                        batch_emb = batch_emb.tolist()
                    embeddings.extend(batch_emb)
                    batch_docs = []
                    batch_chars = 0

                batch_docs.append(doc)
                batch_chars += doc_chars

            if batch_docs:
                batch_emb = embed_model.get_text_embedding_batch(batch_docs)
                if hasattr(batch_emb, "tolist"):
                    batch_emb = batch_emb.tolist()
                embeddings.extend(batch_emb)

        # Add to collection
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                documents=documents,
            )
            print(f"      Added {len(nodes)} vectors for {file_key}")

            # Update manifest
            manifest["files"][file_key] = {
                "file_path": file_info["file_path"],
                "mtime": file_info["mtime"],
                "hash": file_info["hash"],
                "vector_ids": ids,
            }
        except Exception as e:
            print(f"      Error adding {file_key}: {e}")

        processed_since_save += 1
        if processed_since_save >= save_batch_size:
            save_manifest(manifest)
            processed_since_save = 0

    save_manifest(manifest)
    print("Chroma refresh completed")

    if fallback_files:
        print("\n[FALLBACK] Full-file nodes due to parse errors")
        counts = {}
        for path in fallback_files:
            suffix = Path(path).suffix.lower() or "(none)"
            counts[suffix] = counts.get(suffix, 0) + 1
        for suffix, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {suffix}: {count}")
        print(f"  total files: {len(fallback_files)}")

    if empty_files:
        print("\n[EMPTY FILES] No content to index")
        counts = {}
        for path in empty_files:
            suffix = Path(path).suffix.lower() or "(none)"
            counts[suffix] = counts.get(suffix, 0) + 1
        for suffix, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {suffix}: {count}")
        print(f"  total files: {len(empty_files)}")

    if no_content_files:
        print("\n[NO CONTENT] Non-empty files with no nodes")
        counts = {}
        for path in no_content_files:
            suffix = Path(path).suffix.lower() or "(none)"
            counts[suffix] = counts.get(suffix, 0) + 1
        for suffix, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {suffix}: {count}")
        print(f"  total files: {len(no_content_files)}")


def perform_refresh_qdrant(actions, manifest):
    """Perform refresh operations on Qdrant DB."""
    from qdrant_client import QdrantClient, models
    from qdrant_client.http.exceptions import UnexpectedResponse

    if config.QDRANT_USE_DOCKER:
        client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    else:
        qdrant_path = config.get_index_path()
        client = QdrantClient(path=qdrant_path)

    embed_model = get_embed_model()

    def get_embedding_dim() -> int:
        probe = embed_model.get_text_embedding("dimension probe")
        if hasattr(probe, "tolist"):
            probe = probe.tolist()
        return len(probe)

    try:
        client.get_collection(collection_name=config.COLLECTION_NAME)
    except UnexpectedResponse as exc:
        if "doesn't exist" in str(exc) or "Not found" in str(exc):
            dim = get_embedding_dim()
            client.create_collection(
                collection_name=config.COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=dim, distance=models.Distance.COSINE
                ),
            )
            print(f"      Created collection '{config.COLLECTION_NAME}' (dim={dim})")
        else:
            raise

    current_states = get_current_file_states()
    fallback_files = []
    empty_files = []
    no_content_files = []
    save_batch_size = 10
    processed_since_save = 0

    # Handle deletes first (by file_path filter to avoid invalid IDs)
    for file_key in actions["delete"]:
        try:
            selector = models.Filter(
                must=[
                    models.FieldCondition(
                        key="file_path", match=models.MatchValue(value=file_key)
                    )
                ]
            )
            client.delete(
                collection_name=config.COLLECTION_NAME,
                points_selector=selector,
            )
            print(f"      Deleted vectors for {file_key}")
        except Exception as e:
            print(f"      Error deleting vectors for {file_key}: {e}")

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
            except Exception as e:
                print(f"      Error deleting old vectors for {file_key}: {e}")

        # Load and add new content
        file_info = current_states.get(file_key)
        if not file_info:
            continue

        print(f"      Processing ({file_index}/{total_files}) {file_key}...")

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
            print(f"      No content loaded for {file_key}")
            continue

        if any(node.metadata.get("parse_error") for node in nodes):
            fallback_files.append(file_key)

        if VERBOSE:
            print(f"      Nodes: {len(nodes)}")

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
            embeddings = []

            if VERBOSE:
                max_tokens = config.EMBED_BATCH_MAX_TOKENS
                batch_docs = []
                batch_chars = 0
                embedded_count = 0

                for doc in documents:
                    doc_chars = len(doc)
                    if batch_docs and (batch_chars + doc_chars) > max_tokens * 4:
                        t0 = time.perf_counter()
                        batch_emb = embed_model.get_text_embedding_batch(batch_docs)
                        t1 = time.perf_counter()
                        if hasattr(batch_emb, "tolist"):
                            batch_emb = batch_emb.tolist()
                        embeddings.extend(batch_emb)
                        embedded_count += len(batch_docs)
                        print(
                            f"      [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Embedded {embedded_count}/{total_nodes} nodes ({t1 - t0:.2f}s)"
                        )
                        batch_docs = []
                        batch_chars = 0

                    batch_docs.append(doc)
                    batch_chars += doc_chars

                if batch_docs:
                    t0 = time.perf_counter()
                    batch_emb = embed_model.get_text_embedding_batch(batch_docs)
                    t1 = time.perf_counter()
                    if hasattr(batch_emb, "tolist"):
                        batch_emb = batch_emb.tolist()
                    embeddings.extend(batch_emb)
                    embedded_count += len(batch_docs)
                    print(
                        f"      [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Embedded {embedded_count}/{total_nodes} nodes ({t1 - t0:.2f}s)"
                    )
            else:
                max_tokens = config.EMBED_BATCH_MAX_TOKENS
                batch_docs = []
                batch_chars = 0

                for doc in documents:
                    doc_chars = len(doc)
                    if batch_docs and (batch_chars + doc_chars) > max_tokens * 4:
                        batch_emb = embed_model.get_text_embedding_batch(batch_docs)
                        if hasattr(batch_emb, "tolist"):
                            batch_emb = batch_emb.tolist()
                        embeddings.extend(batch_emb)
                        batch_docs = []
                        batch_chars = 0

                    batch_docs.append(doc)
                    batch_chars += doc_chars

                if batch_docs:
                    batch_emb = embed_model.get_text_embedding_batch(batch_docs)
                    if hasattr(batch_emb, "tolist"):
                        batch_emb = batch_emb.tolist()
                    embeddings.extend(batch_emb)

        embeddings = (
            embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings
        )

        for i, (node, vector, vid) in enumerate(zip(nodes, embeddings, ids)):
            text_value = node.get_content() or ""
            payload = {
                **node.metadata,
                "text": text_value,
            }
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
                print(f"      Added {len(points)} vectors for {file_key}")

                # Update manifest
                manifest["files"][file_key] = {
                    "file_path": file_info["file_path"],
                    "mtime": file_info["mtime"],
                    "hash": file_info["hash"],
                    "vector_ids": ids,
                }
            except Exception as e:
                print(f"      Error adding {file_key}: {e}")

        processed_since_save += 1
        if processed_since_save >= save_batch_size:
            save_manifest(manifest)
            processed_since_save = 0

    save_manifest(manifest)
    print("Qdrant refresh completed")

    if fallback_files:
        print("\n[FALLBACK] Full-file nodes due to parse errors")
        counts = {}
        for path in fallback_files:
            suffix = Path(path).suffix.lower() or "(none)"
            counts[suffix] = counts.get(suffix, 0) + 1
        for suffix, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {suffix}: {count}")
        print(f"  total files: {len(fallback_files)}")

    if empty_files:
        print("\n[EMPTY FILES] No content to index")
        counts = {}
        for path in empty_files:
            suffix = Path(path).suffix.lower() or "(none)"
            counts[suffix] = counts.get(suffix, 0) + 1
        for suffix, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {suffix}: {count}")
        print(f"  total files: {len(empty_files)}")

    if no_content_files:
        print("\n[NO CONTENT] Non-empty files with no nodes")
        counts = {}
        for path in no_content_files:
            suffix = Path(path).suffix.lower() or "(none)"
            counts[suffix] = counts.get(suffix, 0) + 1
        for suffix, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {suffix}: {count}")
        print(f"  total files: {len(no_content_files)}")

    timing_tracker.print_summary()


parser = argparse.ArgumentParser(description="Informica RAG Indexer")
parser.add_argument(
    "--regenerate-manifest",
    action="store_true",
    help="Regenerate manifest from existing index (one-time bootstrap)",
)
parser.add_argument(
    "--fix-paths",
    action="store_true",
    help="Fix absolute paths in vector DB to relative paths",
)
parser.add_argument(
    "--force-full-index",
    action="store_true",
    help="Force full re-indexing (WARNING: requires confirmation)",
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

VERBOSE = args.verbose

# Initialize timing tracker with verbose setting
timing_tracker = TimingTracker(verbose=VERBOSE)

if args.regenerate_manifest:
    regenerate_manifest()
    sys.exit(0)

if args.fix_paths:
    fix_paths()
    sys.exit(0)

if args.clear:
    if not args.yes:
        print("\n[WARNING] This will DELETE the vector collection and manifest!")
        print(f"  Collection: {config.COLLECTION_NAME}")
        print(f"  Index path: {config.get_index_path()}")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != "YES":
            print("Aborted.")
            sys.exit(0)

    print("\n[INFO] Clearing vector collection and manifest...")
    from qdrant_client import QdrantClient

    if config.QDRANT_USE_DOCKER:
        client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    else:
        client = QdrantClient(path=config.get_index_path())
    try:
        client.delete_collection(collection_name=config.COLLECTION_NAME)
        print(f"      Deleted collection '{config.COLLECTION_NAME}'")
    except Exception as e:
        print(f"      Collection may not exist: {e}")

    manifest_path = get_manifest_path()
    if manifest_path.exists():
        manifest_path.unlink()
        print(f"      Deleted manifest")

    print("      Done.\n")

manifest = load_manifest()

if manifest is None:
    print("\n[INFO] No manifest found - regenerating from vector store...")
    regenerate_manifest()
    manifest = load_manifest()
    if manifest is None:
        if not confirm_full_index(
            "You are about to perform full indexing from scratch!"
        ):
            print("Aborted. No changes made.")
            sys.exit(0)
        print("\n[INFO] Proceeding with full indexing...")
        mode = "full"
    else:
        print("      Regen complete - performing incremental refresh")
        mode = "refresh"
elif args.force_full_index:
    if not confirm_full_index(
        "You are about to delete the existing index and rebuild from scratch! This cannot be undone."
    ):
        print("Aborted. No changes made.")
        sys.exit(0)
    print("\n[INFO] Proceeding with full re-indexing...")
    index_path = Path(config.get_index_path())
    if index_path.exists():
        shutil.rmtree(index_path)
        print(f"      Deleted existing index at: {index_path}")
    manifest_path = get_manifest_path()
    if manifest_path.exists():
        manifest_path.unlink()
    mode = "full"
else:
    print("\n[INFO] Manifest found - running in refresh mode")
    mode = "refresh"

run_indexing(mode)
