"""
Migration script: Chroma to Qdrant

Exports vectors from Chroma, fixes absolute paths to relative during migration,
and imports them into Qdrant. Includes post-migration verification.

Usage:
    python -m qdrant.migrate
"""

import chromadb
from qdrant_client import QdrantClient, models
import os
import sys
import time

sys.path.insert(0, ".")
sys.path.insert(0, "..")
import config

os.environ["TORCHVISION_DISABLE_META_REGISTRATIONS"] = "1"

# All known absolute prefixes -> relative prefix mappings
# Longer/more specific prefixes first to avoid partial matches
PATH_PREFIX_MAP = [
    ("C:\\GitRepos\\informica_2_0\\delphi_src\\", "source/"),
    ("C:\\GitRepos\\informica_2_0\\sql_srcipt\\6RedGate\\", "schemas/"),
    ("C:\\GitRepos\\informica-rag\\source\\", "source/"),
    ("C:\\GitRepos\\informica-rag\\schemas\\", "schemas/"),
]


def fix_file_path(file_path: str) -> tuple[str, bool]:
    """Convert an absolute file_path to a relative one.

    Returns:
        (new_path, was_fixed) tuple
    """
    if not file_path:
        return file_path, False

    for old_prefix, new_prefix in PATH_PREFIX_MAP:
        if file_path.lower().startswith(old_prefix.lower()):
            rel_part = file_path[len(old_prefix) :]
            new_path = new_prefix + rel_part.replace("\\", "/")
            return new_path, True

    return file_path, False


def format_time(seconds: float) -> str:
    """Format seconds into human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
    else:
        return f"{seconds // 3600:.0f}h {seconds % 3600 // 60:.0f}m"


def format_rate(count: int, elapsed: float) -> str:
    """Format items/sec rate."""
    if elapsed <= 0:
        return "---"
    return f"{count / elapsed:,.0f}"


def migrate_chroma_to_qdrant():
    """Migrate vectors from Chroma to Qdrant with inline path fixing."""
    chroma_path = config.get_chroma_path()

    print()
    print("=" * 70)
    print("  CHROMA -> QDRANT MIGRATION (with path fixing)")
    print("=" * 70)
    print(f"  Source (Chroma): {chroma_path}")
    print(f"  Collection:      {config.COLLECTION_NAME}")
    print()
    print("  Path prefix mappings:")
    for old, new in PATH_PREFIX_MAP:
        print(f"    {old}")
        print(f"      -> {new}")
    print()

    # --- Step 1: Connect to Chroma ---
    print("[1/5] Connecting to Chroma...")
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    collection = chroma_client.get_or_create_collection(config.COLLECTION_NAME)

    total_count = collection.count()
    print(f"      Found {total_count:,} vectors in Chroma")

    # Get embedding dim from first Chroma vector
    sample_results = collection.get(limit=1, include=["embeddings"])
    embeddings_sample = sample_results.get("embeddings")
    if embeddings_sample is not None and len(embeddings_sample) > 0:
        dynamic_size = len(embeddings_sample[0])
        print(f"      Chroma embedding dim: {dynamic_size}")
    else:
        dynamic_size = 1024
        print("      No embeddings found, default dim 1024")

    if total_count == 0:
        print("      Nothing to migrate. Exiting.")
        return

    # --- Step 2: Connect to Qdrant ---
    print("\n[2/5] Connecting to Qdrant...")
    if config.QDRANT_USE_DOCKER:
        qdrant_client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
        )
        print(f"      Docker server at {config.QDRANT_HOST}:{config.QDRANT_PORT}")
    else:
        qdrant_path = config.get_qdrant_path()
        qdrant_client = QdrantClient(path=qdrant_path)
        print(f"      Local file at {qdrant_path}")

    # --- Step 3: Create fresh collection ---
    print("\n[3/5] Preparing Qdrant collection...")
    try:
        qdrant_client.get_collection(collection_name=config.COLLECTION_NAME)
        print(f"      Collection '{config.COLLECTION_NAME}' exists, deleting...")
        qdrant_client.delete_collection(collection_name=config.COLLECTION_NAME)
    except Exception:
        pass

    qdrant_client.create_collection(
        collection_name=config.COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=dynamic_size, distance=models.Distance.COSINE
        ),
    )
    print(f"      Collection '{config.COLLECTION_NAME}' created (dim={dynamic_size})")

    # --- Step 4: Migrate with path fixing ---
    print(f"\n[4/5] Migrating {total_count:,} vectors...")
    print()

    batch_size = 500
    vectors_upserted = 0
    paths_fixed = 0
    paths_already_relative = 0
    paths_unfixable = 0
    unfixable_examples = []
    skipped_no_embedding = 0

    # Track files for summary
    source_files = set()
    schemas_files = set()
    other_files = set()

    start_time = time.time()

    for offset in range(0, total_count, batch_size):
        current_batch_size = min(batch_size, total_count - offset)

        try:
            results = collection.get(
                limit=current_batch_size,
                offset=offset,
                include=["embeddings", "metadatas", "documents"],
            )
        except Exception as e:
            print(f"      ERROR at offset {offset}: {e}")
            continue

        if not results or not results.get("ids"):
            continue

        ids = results["ids"]
        raw_embeddings = results.get("embeddings")
        embeddings = (
            [list(emb) if hasattr(emb, "__iter__") else emb for emb in raw_embeddings]
            if raw_embeddings is not None
            else []
        )
        metadatas = results.get("metadatas") or []
        documents = results.get("documents") or []

        if len(ids) != len(embeddings):
            print(
                f"      WARNING: id/embedding mismatch at offset {offset}, skipping batch"
            )
            continue

        points = []
        for i, point_id in enumerate(ids):
            embedding = embeddings[i] if i < len(embeddings) else None
            metadata = metadatas[i] if i < len(metadatas) else {}
            document = documents[i] if i < len(documents) else ""

            if embedding is None or (
                isinstance(embedding, (list, tuple)) and len(embedding) == 0
            ):
                skipped_no_embedding += 1
                continue

            vector_list = [float(value) for value in embedding]

            # Build payload
            payload = {
                "document": document,
                **{k: v for k, v in metadata.items() if v is not None},
            }

            # Fix file_path inline
            file_path = payload.get("file_path", "")
            if file_path:
                new_path, was_fixed = fix_file_path(file_path)
                if was_fixed:
                    payload["file_path"] = new_path
                    paths_fixed += 1
                elif not os.path.isabs(file_path):
                    paths_already_relative += 1
                else:
                    paths_unfixable += 1
                    if len(unfixable_examples) < 20:
                        unfixable_examples.append(file_path)

                # Track unique files by category
                fp = payload["file_path"].replace("\\", "/")
                if fp.startswith("source/"):
                    source_files.add(fp)
                elif fp.startswith("schemas/"):
                    schemas_files.add(fp)
                else:
                    other_files.add(fp)

            point = models.PointStruct(
                id=point_id,
                vector=vector_list,
                payload=payload,
            )
            points.append(point)

        if points:
            try:
                qdrant_client.upsert(
                    collection_name=config.COLLECTION_NAME, points=points
                )
                vectors_upserted += len(points)
            except Exception as e:
                print(f"      ERROR upserting at offset {offset}: {e}")
                continue

        # Progress output
        progress = min(offset + batch_size, total_count)
        elapsed = time.time() - start_time
        rate = format_rate(progress, elapsed)
        pct = 100 * progress / total_count
        eta_sec = (
            (total_count - progress) / (progress / elapsed)
            if elapsed > 0 and progress > 0
            else 0
        )
        eta = format_time(eta_sec)

        if (progress % 5000 < batch_size) or progress >= total_count:
            bar_width = 30
            filled = int(bar_width * progress / total_count)
            bar = "#" * filled + "-" * (bar_width - filled)
            print(
                f"      [{bar}] {progress:>7,}/{total_count:,} "
                f"({pct:5.1f}%) | {rate} vec/s | ETA: {eta} | "
                f"fixed: {paths_fixed:,}"
            )

    total_time = time.time() - start_time

    # --- Step 5: Post-migration summary ---
    print("\n[5/5] Migration complete!")
    print()
    print("=" * 70)
    print("  MIGRATION SUMMARY")
    print("=" * 70)
    print(f"  Vectors migrated:    {vectors_upserted:>10,}")
    print(f"  Skipped (no embed):  {skipped_no_embedding:>10,}")
    print(f"  Total time:          {format_time(total_time):>10}")
    print(
        f"  Average rate:        {format_rate(vectors_upserted, total_time):>10} vec/s"
    )

    print()
    print("-" * 70)
    print("  PATH FIXING RESULTS")
    print("-" * 70)
    print(f"  Paths fixed:             {paths_fixed:>10,}")
    print(f"  Already relative:        {paths_already_relative:>10,}")
    print(f"  Unfixable (still abs):   {paths_unfixable:>10,}")

    print()
    print("-" * 70)
    print("  FILE DISTRIBUTION")
    print("-" * 70)
    print(f"  Unique source/ files:    {len(source_files):>10,}")
    print(f"  Unique schemas/ files:   {len(schemas_files):>10,}")
    print(f"  Unique other files:      {len(other_files):>10,}")
    print(
        f"  Total unique files:      {len(source_files) + len(schemas_files) + len(other_files):>10,}"
    )

    if unfixable_examples:
        print()
        print("-" * 70)
        print(f"  WARNING: {paths_unfixable} vectors have unfixable absolute paths!")
        print("  Examples:")
        for p in unfixable_examples:
            print(f"    {p}")

    if other_files:
        print()
        print("-" * 70)
        print(f"  WARNING: {len(other_files)} unique files NOT in source/ or schemas/!")
        print("  Examples:")
        for i, fp in enumerate(sorted(other_files)):
            if i >= 20:
                print(f"    ... and {len(other_files) - 20} more")
                break
            print(f"    {fp}")

    # Final Qdrant count verification
    print()
    print("-" * 70)
    print("  VERIFICATION")
    print("-" * 70)
    try:
        final_count = qdrant_client.count(collection_name=config.COLLECTION_NAME).count
        print(f"  Chroma source count:     {total_count:>10,}")
        print(f"  Qdrant final count:      {final_count:>10,}")
        if final_count == total_count:
            print("  Status:                  ALL GOOD - counts match!")
        elif final_count == vectors_upserted:
            print(
                f"  Status:                  OK - {total_count - final_count} skipped (no embeddings)"
            )
        else:
            print("  Status:                  MISMATCH - check for errors above")
    except Exception as e:
        print(f"  Could not verify: {e}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    migrate_chroma_to_qdrant()
