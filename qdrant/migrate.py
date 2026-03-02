"""
Migration script: Chroma to Qdrant

Usage:
    python -m qdrant.migrate

This script exports vectors from Chroma and imports them into Qdrant,
preserving all metadata for later path fixing.
"""

import chromadb
from qdrant_client import QdrantClient, models
import config
import os

os.environ["TORCHVISION_DISABLE_META_REGISTRATIONS"] = "1"


def migrate_chroma_to_qdrant():
    """Migrate vectors from Chroma to Qdrant."""
    chroma_path = config.get_chroma_path()
    qdrant_path = config.get_qdrant_path()

    print("\n" + "=" * 60)
    print("CHROMA TO QDRANT MIGRATION")
    print("=" * 60)
    print(f"Source (Chroma): {chroma_path}")
    print(f"Target (Qdrant): {qdrant_path}")

    print("\n[1/4] Connecting to source Chroma DB...")
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    collection = chroma_client.get_or_create_collection(config.COLLECTION_NAME)

    total_count = collection.count()
    print(f"      Found {total_count} vectors in Chroma")

    if total_count == 0:
        print("      No vectors to migrate. Exiting.")
        return

    print("\n[2/4] Connecting to target Qdrant DB...")
    if config.QDRANT_USE_DOCKER:
        qdrant_client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
        )
        print(
            f"      Using Qdrant Docker server at {config.QDRANT_HOST}:{config.QDRANT_PORT}"
        )
    else:
        qdrant_client = QdrantClient(path=qdrant_path)
        print(f"      Using local Qdrant at {qdrant_path}")

    try:
        qdrant_client.get_collection(collection_name=config.COLLECTION_NAME)
        print(f"      Collection '{config.COLLECTION_NAME}' already exists")
    except Exception:
        print(f"      Creating collection '{config.COLLECTION_NAME}'...")
        qdrant_client.create_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=1024, distance=models.Distance.COSINE
            ),
        )
        print(f"      Collection created successfully")

    vectors_upserted = 0
    batch_size = 100

    print("\n[3/4] Migrating vectors (batch processing)...")

    for offset in range(0, total_count, batch_size):
        current_batch_size = min(batch_size, total_count - offset)
        results = collection.get(
            limit=current_batch_size,
            offset=offset,
            include=["embeddings", "metadatas", "documents"],
        )

        if not results or not results.get("ids"):
            continue

        ids = results["ids"]
        raw_embeddings = results.get("embeddings")
        embeddings = list(raw_embeddings) if raw_embeddings is not None else []
        metadatas = results.get("metadatas") or []
        documents = results.get("documents") or []

        points = []
        for i, point_id in enumerate(ids):
            embedding = embeddings[i] if i < len(embeddings) else None
            metadata = metadatas[i] if i < len(metadatas) else {}
            document = documents[i] if i < len(documents) else ""

            if embedding is None:
                continue

            point = models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "document": document,
                    **{k: v for k, v in metadata.items() if v is not None},
                },
            )
            points.append(point)

        if points:
            qdrant_client.upsert(collection_name=config.COLLECTION_NAME, points=points)
            vectors_upserted += len(points)

        progress = min(offset + batch_size, total_count)
        if progress % 1000 == 0 or progress == total_count:
            print(
                f"      Progress: {progress}/{total_count} ({100 * progress // total_count}%)"
            )

    print(f"\n[4/4] Migration complete!")
    print(f"      Total vectors migrated: {vectors_upserted}")
    print("=" * 60)
    print("\nYou can now run: python index_delphi.py --fix-paths")


if __name__ == "__main__":
    migrate_chroma_to_qdrant()
