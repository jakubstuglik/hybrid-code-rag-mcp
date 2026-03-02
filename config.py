# Configuration for Informica RAG
# Edit these values in one place to affect both indexer and MCP

MODEL_NAME = "BAAI/bge-m3"  # Big model
# MODEL_NAME = "BAAI/bge-small-en-v1.5" # small model
INDEX_PATH = "./index_bge_m3"  # Big model path
# INDEX_PATH = "./index_storage_bge_small_v1.5" # Small model path

COLLECTION_NAME = "delphi_rag"

EMBED_MODEL_KWARGS = {
    "torch_dtype": "float16"
}  # saves VRAM + faster, empty dict for default

INDEX_EMBED_DEVICE = "cuda"  # Device for indexing (cuda/cpu)
MCP_EMBED_DEVICE = "cpu"  # Device for MCP server (cuda/cpu)
