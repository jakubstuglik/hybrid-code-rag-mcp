# verify_paths.py - Run this after --fix-paths to verify paths are now relative
import chromadb
import config
from pathlib import Path

db = chromadb.PersistentClient(path=config.INDEX_PATH)
collection = db.get_or_create_collection(config.COLLECTION_NAME)

print(f"Total documents: {collection.count()}")
print("\nChecking first 20 documents for path format:")

results = collection.get(limit=20)
if results and results.get("ids"):
    metadatas = results.get("metadatas") or []
    for idx, chroma_id in enumerate(results["ids"]):
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        file_path = metadata.get("file_path", "") if isinstance(metadata, dict) else ""

        is_relative = not Path(file_path).is_absolute() if file_path else False
        prefix = "✓ RELATIVE" if is_relative else "✗ ABSOLUTE"

        print(f"  {prefix}: {file_path[:80]}...")

# Count relative vs absolute
print("\nCounting relative vs absolute paths (sampling 1000 docs)...")
results = collection.get(limit=1000)
relative_count = 0
absolute_count = 0

if results and results.get("ids"):
    metadatas = results.get("metadatas") or []
    for idx in range(len(results["ids"])):
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        file_path = metadata.get("file_path", "") if isinstance(metadata, dict) else ""

        if file_path:
            if Path(file_path).is_absolute():
                absolute_count += 1
            else:
                relative_count += 1

print(f"  Relative paths: {relative_count}")
print(f"  Absolute paths: {absolute_count}")
