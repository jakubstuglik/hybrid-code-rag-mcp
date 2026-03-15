"""Round-trip test for branch overlay add/remove.

Tests both:
  1. Direct Qdrant vector counts (branch payload filtering)
  2. MCP search function (filter + dedup + rerank pipeline)

Usage:
  python -m tests.test_branch_roundtrip --config config_informica --phase A   # after removal
  python -m tests.test_branch_roundtrip --config config_informica --phase B   # after re-add
"""

import argparse
import asyncio
import sys
import time

import config_loader
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from shared.embedding import get_embed_model
from shared.branch_dedup import (
    build_branch_filter,
    dedup_branch_results,
    get_branch_tombstones,
    get_main_branch_name,
)
from shared.reranker import rerank_results, get_retrieval_top_k
from qdrant.vector_store import get_qdrant_vector_store, detect_collection_mode
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStoreQueryMode


BRANCH = "task/T37523"
# Files known to exist on both develop and the branch
TEST_FILES = [
    "delphi_src/Common/DISP_File/Export4EPO/ExportEPO2DBF.pas",
    "delphi_src/TURDUS/KMChoiceForms.pas",
    "delphi_src/TURDUS/Globals.pas",
]
# Queries that should hit branch-modified files
TEST_QUERIES = [
    ("ChoiceBusStand function in KMChoiceForms", "delphi_src/TURDUS/KMChoiceForms.pas"),
    (
        "ExportEPO2DBF PrepareSQL_LiteDatabase",
        "delphi_src/Common/DISP_File/Export4EPO/ExportEPO2DBF.pas",
    ),
    (
        "RS_NO_FILE constant ExportEPO2DBF",
        "delphi_src/Common/DISP_File/Export4EPO/ExportEPO2DBF.pas",
    ),
]

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def test_qdrant_direct(config, phase: str):
    """Test 1: Direct Qdrant counts."""
    print("\n" + "=" * 70)
    print("TEST 1: Direct Qdrant vector counts")
    print("=" * 70)

    c = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    collection = config.COLLECTION_NAME

    # Count branch vectors
    branch_count = c.count(
        collection,
        count_filter=Filter(
            must=[
                FieldCondition(key="branch", match=MatchValue(value=BRANCH)),
            ]
        ),
    ).count

    total_count = c.get_collection(collection).points_count

    print(f"  Collection:     {collection}")
    print(f"  Total vectors:  {total_count}")
    print(f"  Branch vectors: {branch_count}")
    print()

    ok = True
    if phase == "A":
        # After removal: branch vectors should be 0
        if branch_count == 0:
            print(f"  {PASS} Branch vectors removed (count=0)")
        else:
            print(f"  {FAIL} Expected 0 branch vectors, got {branch_count}")
            ok = False
    elif phase == "B":
        # After re-add: branch vectors should be ~1215
        if branch_count > 0:
            print(f"  {PASS} Branch vectors present (count={branch_count})")
        else:
            print(f"  {FAIL} Expected >0 branch vectors, got {branch_count}")
            ok = False

    # Per-file checks
    for fpath in TEST_FILES:
        main_count = c.count(
            collection,
            count_filter=Filter(
                must=[
                    FieldCondition(key="branch", match=MatchValue(value="develop")),
                    FieldCondition(key="file_path", match=MatchValue(value=fpath)),
                ]
            ),
        ).count
        br_count = c.count(
            collection,
            count_filter=Filter(
                must=[
                    FieldCondition(key="branch", match=MatchValue(value=BRANCH)),
                    FieldCondition(key="file_path", match=MatchValue(value=fpath)),
                ]
            ),
        ).count
        fname = fpath.split("/")[-1]
        print(f"  {fname:40s}  develop={main_count:4d}  branch={br_count:4d}", end="")
        if phase == "A" and br_count > 0:
            print(f"  {FAIL}")
            ok = False
        elif phase == "B" and br_count == 0:
            print(f"  {FAIL}")
            ok = False
        else:
            print(f"  {PASS}")

    return ok


def test_mcp_search(config, phase: str):
    """Test 2: MCP search pipeline (filter + dedup + rerank)."""
    print("\n" + "=" * 70)
    print("TEST 2: MCP search pipeline (branch-aware)")
    print("=" * 70)

    print("  Loading embedding model on cpu...", file=sys.stderr)
    embed_model = get_embed_model(device="cpu", cfg=config)
    storage_context, qdrant_client, _ = get_qdrant_vector_store(cfg=config)

    mode = detect_collection_mode(qdrant_client, config.COLLECTION_NAME)
    is_hybrid = mode == "hybrid"
    alpha = getattr(config, "HYBRID_ALPHA", 0.5)

    index = VectorStoreIndex.from_vector_store(
        storage_context.vector_store, embed_model=embed_model
    )

    main_branch = get_main_branch_name(config)
    top_k = 8
    all_ok = True

    for query_text, expected_file in TEST_QUERIES:
        print(f"\n  QUERY: {query_text}")
        print(f"  Expected file: {expected_file.split('/')[-1]}")

        # ── Search WITH branch ──
        qdrant_filter = build_branch_filter(
            main_branch=main_branch, feature_branch=BRANCH
        )
        fetch_k = get_retrieval_top_k(query_text, top_k)
        branch_overfetch = 2
        fetch_k = fetch_k * branch_overfetch

        retriever_kwargs = {
            "similarity_top_k": fetch_k,
            "vector_store_kwargs": {"qdrant_filters": qdrant_filter},
        }
        if is_hybrid:
            retriever_kwargs.update(
                {
                    "vector_store_query_mode": VectorStoreQueryMode.HYBRID,
                    "alpha": alpha,
                    "sparse_top_k": fetch_k,
                }
            )
        retriever = index.as_retriever(**retriever_kwargs)
        nodes = asyncio.run(retriever.aretrieve(query_text))

        # Dedup
        tombstones = get_branch_tombstones(BRANCH, config)
        dedup_target = max(top_k, fetch_k // branch_overfetch)
        nodes = dedup_branch_results(
            nodes,
            feature_branch=BRANCH,
            tombstones=tombstones,
            desired_top_k=dedup_target,
        )

        # Rerank
        nodes = rerank_results(nodes, query_text, desired_top_k=top_k, verbose=False)

        # Analyze results
        branch_hits = []
        main_hits = []
        for i, n in enumerate(nodes):
            meta = n.node.metadata
            fp = meta.get("file_path", "")
            br = meta.get("branch", "")
            nt = meta.get("node_type", "")
            fname = fp.split("/")[-1] if fp else "?"
            tag = f"[{br}]" if br else "[develop]"
            print(f"    #{i + 1:2d} {tag:20s} {nt:25s} {fname}")
            if br == BRANCH and fp == expected_file:
                branch_hits.append(i + 1)
            elif fp == expected_file:
                main_hits.append(i + 1)

        if phase == "A":
            # Branch removed: should NOT see any branch-tagged results
            has_any_branch = any(n.node.metadata.get("branch") == BRANCH for n in nodes)
            if has_any_branch:
                print(f"    {FAIL} Found branch results after branch removal!")
                all_ok = False
            elif main_hits:
                print(
                    f"    {PASS} No branch results; main branch hit at #{main_hits[0]}"
                )
            else:
                print(
                    f"    {PASS} No branch results (file may not rank in top-{top_k} without branch)"
                )

        elif phase == "B":
            # Branch present: should see branch-tagged results for the expected file,
            # and they should be preferred over main-branch dupes
            if branch_hits:
                # Check dedup: for the same file, branch should appear INSTEAD of main
                has_main_dupe = any(
                    n.node.metadata.get("file_path") == expected_file
                    and n.node.metadata.get("branch") != BRANCH
                    and n.node.metadata.get("node_type")
                    == nodes[branch_hits[0] - 1].node.metadata.get("node_type")
                    for n in nodes
                )
                if has_main_dupe:
                    print(
                        f"    {FAIL} Branch hit at #{branch_hits[0]} but main dupe NOT suppressed"
                    )
                    all_ok = False
                else:
                    print(
                        f"    {PASS} Branch hit at #{branch_hits[0]}, main dupe suppressed by dedup"
                    )
            else:
                # Acceptable if main hit is present — branch might not rank top-k for this query
                if main_hits:
                    print(
                        f"    PARTIAL Branch not in top-{top_k} but main at #{main_hits[0]}"
                    )
                else:
                    print(f"    {FAIL} Neither branch nor main hit in top-{top_k}")
                    all_ok = False

        # ── Search WITHOUT branch (main-only) ──
        qdrant_filter_main = build_branch_filter(
            main_branch=main_branch, feature_branch=None
        )
        retriever_kwargs_main = {
            "similarity_top_k": top_k,
            "vector_store_kwargs": {"qdrant_filters": qdrant_filter_main},
        }
        if is_hybrid:
            retriever_kwargs_main.update(
                {
                    "vector_store_query_mode": VectorStoreQueryMode.HYBRID,
                    "alpha": alpha,
                    "sparse_top_k": top_k,
                }
            )
        retriever_main = index.as_retriever(**retriever_kwargs_main)
        nodes_main = asyncio.run(retriever_main.aretrieve(query_text))
        nodes_main = rerank_results(
            nodes_main, query_text, desired_top_k=top_k, verbose=False
        )

        has_branch_in_main = any(
            n.node.metadata.get("branch") == BRANCH for n in nodes_main
        )
        if has_branch_in_main:
            print(f"    {FAIL} Main-only query returned branch results!")
            all_ok = False
        else:
            print(f"    {PASS} Main-only query correctly excludes branch vectors")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Branch overlay round-trip test")
    parser.add_argument("--config", required=True, help="Config name")
    parser.add_argument(
        "--phase",
        required=True,
        choices=["A", "B"],
        help="A=after branch removal, B=after branch re-add",
    )
    args = parser.parse_args()

    config = config_loader.get_config(args.config)

    print(
        f"Phase {args.phase}: {'Branch REMOVED' if args.phase == 'A' else 'Branch RE-ADDED'}"
    )
    print(f"Config: {args.config}")
    print(f"Branch: {BRANCH}")

    ok1 = test_qdrant_direct(config, args.phase)
    ok2 = test_mcp_search(config, args.phase)

    print("\n" + "=" * 70)
    if ok1 and ok2:
        print(f"OVERALL: {PASS} — All checks passed for phase {args.phase}")
    else:
        print(f"OVERALL: {FAIL} — Some checks failed")
    print("=" * 70)

    sys.exit(0 if (ok1 and ok2) else 1)


if __name__ == "__main__":
    main()
