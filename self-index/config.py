# Example override config for self-indexing
# This file overrides values from the base config.py

SOURCE_DIRS = [
    {"path": "source", "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj"]},
]

COLLECTION_NAME = "delphi_rag_self"
MODEL_PATH = "index_self_20260306"
