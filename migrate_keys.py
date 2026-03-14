"""
Migrate manifest keys and Qdrant point IDs after SOURCE_DIRS path refactoring.

The refactoring changed how canonical file keys are derived:
  OLD: normalize_file_key("source", rel) → "source/rel"
  NEW: normalize_file_key(path, rel, source_dir=sd) → "delphi_src/rel"  (last segment)

This means:
  - Manifest keys change: "source/X" → "delphi_src/X", "schemas/X" → "sql_srcipt/6RedGate/X"
  - Qdrant point UUIDs change: uuid5(NAMESPACE_URL, "source/X:i") → uuid5(NAMESPACE_URL, "delphi_src/X:i")
  - Qdrant payloads (file_path) are ALREADY correct (map_path_to_qdrant was applied at index time)

This script:
  1. Reads the manifest and renames keys according to KEY_MAPPINGS
  2. For each renamed file, computes old and new UUIDs from the manifest vector_ids
  3. Fetches old points from Qdrant, upserts them with new UUIDs, deletes old points
  4. Saves the updated manifest

No re-embedding is performed.  Vectors and payloads are preserved as-is.

Usage:
    python migrate_keys.py                  # Migrate production index
    python migrate_keys.py --dry-run        # Preview changes without writing
    python migrate_keys.py --config self-index  # Migrate a different config (unlikely needed)
"""

import argparse
import json
import uuid
from pathlib import Path

import config_loader
from shared.log import log, log_raw, log_warn, log_error

# ── Key mappings: old prefix → new prefix ──────────────────────────
# These reflect the specific SOURCE_DIRS change in this refactoring.
# Old config: {"path": "source", "map_to_path": "delphi_src"} → manifest key prefix "source/"
# New config: {"path": "../informica_2_0/delphi_src"} → manifest key prefix "delphi_src/"
#
# Old config: {"path": "schemas", "map_to_path": "sql_srcipt/6RedGate"} → manifest key prefix "schemas/"
# New config: {"path": "../informica_2_0/sql_srcipt/6RedGate", "map_to_path": "sql_srcipt/6RedGate"} → same
KEY_MAPPINGS = [
    ("source/", "delphi_src/"),
    ("schemas/", "sql_srcipt/6RedGate/"),
]


def make_qdrant_point_id(file_key: str, index: int) -> str:
    """Create a deterministic UUID for a Qdrant point.  Must match index_rag.py."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{file_key}:{index}"))


def remap_key(old_key: str) -> str | None:
    """Apply KEY_MAPPINGS to an old manifest key.  Returns new key or None if no mapping."""
    for old_prefix, new_prefix in KEY_MAPPINGS:
        if old_key.startswith(old_prefix):
            return new_prefix + old_key[len(old_prefix) :]
    return None


def get_manifest_path(cfg) -> Path:
    """Get manifest path from config."""
    index_path = Path(cfg.get_index_path()).resolve()
    return index_path / "index_manifest.json"


def load_manifest(manifest_path: Path) -> dict | None:
    """Load manifest from disk."""
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_manifest(manifest: dict, manifest_path: Path) -> None:
    """Save manifest to disk."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def migrate(cfg, dry_run: bool = False) -> None:
    """Run the migration."""
    from qdrant_client import QdrantClient, models

    manifest_path = get_manifest_path(cfg)
    manifest = load_manifest(manifest_path)
    if manifest is None or "files" not in manifest:
        log_error(f"No manifest found at {manifest_path}")
        return

    files = manifest["files"]
    log(f"Loaded manifest with {len(files)} files")

    # ── Phase 1: Identify keys to rename ────────────────────────────
    renames: list[tuple[str, str, list[str]]] = []  # (old_key, new_key, vector_ids)
    unchanged_count = 0

    for old_key, entry in list(files.items()):
        new_key = remap_key(old_key)
        if new_key is None:
            unchanged_count += 1
            continue
        if new_key == old_key:
            unchanged_count += 1
            continue
        vector_ids = entry.get("vector_ids", [])
        renames.append((old_key, new_key, vector_ids))

    log(f"Keys to rename:  {len(renames)}")
    log(f"Keys unchanged:  {unchanged_count}")

    if not renames:
        log("Nothing to migrate.")
        return

    # Show sample renames
    log_raw()
    log_raw("Sample renames:")
    for old_key, new_key, _ in renames[:5]:
        log_raw(f"  {old_key}")
        log_raw(f"    -> {new_key}")
    if len(renames) > 5:
        log_raw(f"  ... and {len(renames) - 5} more")
    log_raw()

    # ── Phase 2: Compute UUID remappings ────────────────────────────
    # For each file, the manifest stores vector_ids as a list.  The index
    # in the list corresponds to the chunk index used for UUID generation.
    # old_uuid = uuid5(NAMESPACE_URL, "source/X:i")
    # new_uuid = uuid5(NAMESPACE_URL, "delphi_src/X:i")
    uuid_remap: dict[str, str] = {}  # old_uuid → new_uuid
    files_with_no_vectors = 0

    for old_key, new_key, vector_ids in renames:
        if not vector_ids:
            files_with_no_vectors += 1
            continue
        for i, stored_uuid in enumerate(vector_ids):
            expected_old = make_qdrant_point_id(old_key, i)
            new_uuid = make_qdrant_point_id(new_key, i)
            if stored_uuid != expected_old:
                # This shouldn't happen — means the manifest was written with
                # a different key than we expect.  Log and skip.
                log_warn(
                    f"UUID mismatch for {old_key} chunk {i}: "
                    f"manifest={stored_uuid}, expected={expected_old}"
                )
                # Still try to migrate using the stored UUID as the old ID
                uuid_remap[stored_uuid] = new_uuid
            else:
                uuid_remap[stored_uuid] = new_uuid

    log(f"UUIDs to remap:  {len(uuid_remap)}")
    if files_with_no_vectors:
        log(f"Files with no vectors (empty/no_content): {files_with_no_vectors}")

    if dry_run:
        log_raw()
        log("[DRY RUN] Would rename manifest keys and remap Qdrant point IDs.")
        log(f"  Manifest keys to rename: {len(renames)}")
        log(f"  Qdrant UUIDs to remap:   {len(uuid_remap)}")

        # Show a few UUID remap samples
        samples = list(uuid_remap.items())[:3]
        for old_uuid, new_uuid in samples:
            log_raw(f"  {old_uuid} -> {new_uuid}")
        log("[DRY RUN] No changes written.")
        return

    # ── Phase 3: Remap Qdrant point IDs ─────────────────────────────
    from shared.qdrant_client import get_qdrant_client as _get_client

    client = _get_client(cfg)

    # Verify connectivity
    try:
        client.get_collection(collection_name=cfg.COLLECTION_NAME)
    except Exception as exc:
        log_error(f"Cannot access collection '{cfg.COLLECTION_NAME}': {exc}")
        return

    # Process in batches: fetch old points, create new points, delete old
    batch_size = 100
    old_uuids = list(uuid_remap.keys())
    total_migrated = 0
    total_missing = 0
    total_batches = (len(old_uuids) + batch_size - 1) // batch_size

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(old_uuids))
        batch_old_ids = old_uuids[start:end]

        # Fetch existing points with vectors
        fetched = client.retrieve(
            collection_name=cfg.COLLECTION_NAME,
            ids=batch_old_ids,
            with_payload=True,
            with_vectors=True,
        )

        # Build lookup of fetched points
        fetched_by_id = {str(p.id): p for p in fetched}

        # Create new points and collect old IDs to delete
        new_points = []
        ids_to_delete = []

        for old_uuid in batch_old_ids:
            new_uuid = uuid_remap[old_uuid]
            point = fetched_by_id.get(old_uuid)
            if point is None:
                # Point doesn't exist in Qdrant (zero-vector skip, or already deleted)
                total_missing += 1
                continue

            # Create new point with new UUID, same vectors and payload
            new_point = models.PointStruct(
                id=new_uuid,
                vector=point.vector,  # type: ignore[arg-type]  # VectorOutput is runtime-compatible with VectorStruct
                payload=point.payload,
            )
            new_points.append(new_point)
            ids_to_delete.append(old_uuid)

        # Upsert new points first, then delete old (atomic per batch)
        if new_points:
            client.upsert(
                collection_name=cfg.COLLECTION_NAME,
                points=new_points,
            )
            client.delete(
                collection_name=cfg.COLLECTION_NAME,
                points_selector=models.PointIdsList(points=ids_to_delete),
            )
            total_migrated += len(new_points)

        if (batch_idx + 1) % 10 == 0 or batch_idx == total_batches - 1:
            log(
                f"  Qdrant migration progress: {end}/{len(old_uuids)} UUIDs "
                f"({total_migrated} migrated, {total_missing} missing)"
            )

    log(
        f"Qdrant migration complete: {total_migrated} points migrated, {total_missing} missing"
    )

    # ── Phase 4: Update manifest keys ───────────────────────────────
    for old_key, new_key, vector_ids in renames:
        entry = files.pop(old_key)
        # Update vector_ids to new UUIDs
        new_vector_ids = []
        for vid in entry.get("vector_ids", []):
            new_vid = uuid_remap.get(vid, vid)
            new_vector_ids.append(new_vid)
        entry["vector_ids"] = new_vector_ids
        entry["file_path"] = new_key
        files[new_key] = entry

    save_manifest(manifest, manifest_path)
    log(f"Manifest saved with {len(files)} files (renamed {len(renames)} keys)")

    # ── Summary ─────────────────────────────────────────────────────
    log_raw()
    log_raw("=" * 60)
    log_raw("MIGRATION SUMMARY")
    log_raw("=" * 60)
    log_raw(f"  Manifest keys renamed:    {len(renames)}")
    log_raw(f"  Qdrant points migrated:   {total_migrated}")
    log_raw(f"  Qdrant points missing:    {total_missing}")
    log_raw(f"  Manifest keys unchanged:  {unchanged_count}")
    log_raw("=" * 60)
    log_raw()
    log("Migration complete.  Run the indexer in refresh mode to verify.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate manifest keys and Qdrant point IDs after SOURCE_DIRS path refactoring"
    )
    parser.add_argument(
        "--config",
        help="Config name (e.g., 'self-index') or path to config file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to manifest or Qdrant",
    )
    args = parser.parse_args()

    config = config_loader.get_config(config_path=args.config)
    migrate(config, dry_run=args.dry_run)
