"""
Main entry point for Informica RAG indexer.

Supports both Chroma and Qdrant backends based on config.py STORE_TYPE setting.
"""

import os
import sys
import json
import shutil
from pathlib import Path

os.environ["TORCHVISION_DISABLE_META_REGISTRATIONS"] = "1"

import argparse

import config
from shared.embedding import get_embed_model
from shared.indexing import load_all_sources, combine_nodes
from chroma.index_chroma import (
    get_manifest_path as chroma_get_manifest_path,
    load_manifest as chroma_load_manifest,
    save_manifest as chroma_save_manifest,
    regenerate_manifest_from_index as chroma_regenerate_manifest,
    fix_absolute_paths as chroma_fix_paths,
)
from qdrant import fix_paths as qdrant_fix_paths


def get_manifest_path():
    """Get manifest path based on store type."""
    index_path = Path(config.get_index_path()).resolve()
    return index_path / "index_manifest.json"


def load_manifest():
    """Load manifest based on store type."""
    manifest_path = get_manifest_path()
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_manifest(manifest):
    """Save manifest based on store type."""
    manifest_path = get_manifest_path()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def regenerate_manifest():
    """Regenerate manifest based on store type."""
    if config.STORE_TYPE == "chroma":
        chroma_regenerate_manifest()
    else:
        print(
            "\n[REGENERATE MANIFEST] Qdrant manifest regeneration not yet implemented"
        )
        print("      (Vectors are already in Qdrant, manifest is less critical)")


def fix_paths():
    """Fix paths based on store type."""
    if config.STORE_TYPE == "chroma":
        chroma_fix_paths()
    else:
        qdrant_fix_paths.fix_absolute_paths()


def run_indexing():
    """Run the full indexing process."""
    from llama_index.core import VectorStoreIndex

    print(f"\n[STORE TYPE] Using {config.STORE_TYPE.upper()} backend")

    embed_model = get_embed_model()

    if config.STORE_TYPE == "chroma":
        from chroma.vector_store import get_chroma_vector_store

        storage_context, db, collection = get_chroma_vector_store()
    else:
        from qdrant.vector_store import get_qdrant_vector_store

        storage_context, qdrant_client = get_qdrant_vector_store()

    delphi_nodes, dfm_nodes, fr3_nodes, sql_nodes = load_all_sources()
    all_nodes = combine_nodes(delphi_nodes, dfm_nodes, fr3_nodes, sql_nodes)

    print("\n[6/6] Creating vector index and embedding...")
    index = VectorStoreIndex(
        all_nodes,
        embed_model=embed_model,
        storage_context=storage_context,
        embed_batch_size=64,
        show_progress=True,
    )

    print("      Persisting to disk...")
    index.storage_context.persist(persist_dir=config.get_index_path())

    print("\n" + "=" * 70)
    print("Delphi RAG Index Created Successfully")
    print(f"  • Delphi/Pascal chunks (.pas/.dpr)       : {len(delphi_nodes):>6}")
    print(f"  • Delphi .dfm chunks                     : {len(dfm_nodes):>6}")
    print(f"  • FastReport .fr3 chunks                  : {len(fr3_nodes):>6}")
    print(f"  • SQL schema chunks                       : {len(sql_nodes):>6}")
    print("-" * 70)
    print(f"  TOTAL NODES                               : {len(all_nodes):>6}")
    print("=" * 70 + "\n")

    print(f"Index persisted to: {config.get_index_path()}")


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
args = parser.parse_args()

if args.regenerate_manifest:
    regenerate_manifest()
    sys.exit(0)

if args.fix_paths:
    fix_paths()
    sys.exit(0)

manifest = load_manifest()

if manifest is None:
    print("\n[INFO] No manifest found - performing full indexing")
    mode = "full"
elif args.force_full_index:
    print(
        "\n[WARNING] You are about to delete the existing index and rebuild from scratch!"
    )
    print("This will take a VERY LONG TIME and cannot be undone.")
    response = input("Type 'YES' to confirm full re-indexing: ")
    if response.strip() != "YES":
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

run_indexing()
