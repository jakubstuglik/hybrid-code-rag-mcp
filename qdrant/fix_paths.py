"""
Fix absolute paths in Qdrant vector store.

Usage:
    python -m qdrant.fix_paths
"""

from pathlib import Path
from qdrant_client import QdrantClient
import config


def fix_absolute_paths():
    """Fix absolute paths in Qdrant DB to relative paths."""
    print("\n[FIX PATHS] Connecting to Qdrant index...")

    source_dir = Path("source").resolve()
    schemas_dir = Path("schemas").resolve()

    print(f"      source dir: {source_dir}")
    print(f"      schemas dir: {schemas_dir}")

    if config.QDRANT_USE_DOCKER:
        qdrant_client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
        )
        print(
            f"      Using Qdrant Docker server at {config.QDRANT_HOST}:{config.QDRANT_PORT}"
        )
    else:
        qdrant_path = config.get_index_path()
        qdrant_client = QdrantClient(path=qdrant_path)
        print(f"      Using local Qdrant at {qdrant_path}")

    total_count = qdrant_client.count(collection_name=config.COLLECTION_NAME)
    print(f"      Found {total_count} documents in collection")

    batch_size = 100
    total_fixed = 0
    offset = 0

    print("\n      Processing documents...")
    while offset < total_count:
        results = qdrant_client.scroll(
            collection_name=config.COLLECTION_NAME,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        points = results[0]
        next_offset = results[1]

        if not points:
            break

        updates = []
        for point in points:
            payload = point.payload
            file_path = payload.get("file_path", "")

            if not file_path:
                continue

            path = Path(file_path)

            if path.is_absolute():
                try:
                    if path.is_relative_to(source_dir):
                        rel_path = "source" / path.relative_to(source_dir)
                        new_path = str(rel_path)
                        payload["file_path"] = new_path
                        updates.append({"id": point.id, "payload": payload})
                        total_fixed += 1
                    elif path.is_relative_to(schemas_dir):
                        rel_path = "schemas" / path.relative_to(schemas_dir)
                        new_path = str(rel_path)
                        payload["file_path"] = new_path
                        updates.append({"id": point.id, "payload": payload})
                        total_fixed += 1
                except (ValueError, OSError):
                    pass

        if updates:
            qdrant_client.upsert(collection_name=config.COLLECTION_NAME, points=updates)

        offset = next_offset

        if offset % 1000 == 0 or offset >= total_count:
            print(
                f"      Processed {min(offset, total_count)}/{total_count} documents..."
            )

    print(f"\n      Fixed {total_fixed} absolute paths to relative paths")
    print("\n[COMPLETE] Path fixing finished!")


if __name__ == "__main__":
    fix_absolute_paths()
