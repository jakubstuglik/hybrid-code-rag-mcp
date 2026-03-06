# Example override config for self-indexing
# This file overrides values from the base config.py

SOURCE_DIRS = [
    {
        "path": ".",
        "extensions": [".py"],
        "exclude": ["source", "schemas", ".venv", "test_sources", "backup", "index_*"]
    },
]

BASE_PATH = "self-index"
COLLECTION_NAME = "self_rag_index"
MODEL_PATH = "index_rag_self"
