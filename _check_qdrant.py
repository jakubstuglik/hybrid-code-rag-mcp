"""Check Qdrant collection status."""
from qdrant_client import QdrantClient

c = QdrantClient(host="localhost", port=6333)
info = c.get_collection("informica_rag")

print(f"Collection: informica_rag")
print(f"Status: {info.status}")
print(f"Points: {info.points_count:,}")
print(f"Segments: {info.segments_count}")
print()

print("Dense vectors:")
if info.config.params.vectors:
    for name, cfg in info.config.params.vectors.items():
        print(f"  {name}: dim={cfg.size}, distance={cfg.distance}")
else:
    print("  (default config)")

print()
print("Sparse vectors:")
if info.config.params.sparse_vectors:
    for name, sparams in info.config.params.sparse_vectors.items():
        print(f"  {name}: {sparams}")
else:
    print("  none")

print()
print("Optimizer status:", info.optimizer_status)
