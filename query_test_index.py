"""
query_test_index.py -- Evaluate chunk quality against the test index.
Tests both use cases:
  1. Big-picture understanding queries
  2. Precise keyword / BM25 search queries
"""

import sys
import argparse
import asyncio

# ── Setup ────────────────────────────────────────────────────────────
import config_loader
import shared.manifest
from shared.embedding import get_embed_model
from qdrant.vector_store import get_qdrant_vector_store, detect_collection_mode
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStoreQueryMode


def setup(alpha_override=None):
    config = config_loader.get_config()
    shared.manifest.config = config

    alpha = (
        alpha_override
        if alpha_override is not None
        else getattr(config, "HYBRID_ALPHA", 0.5)
    )

    print(f"Loading embedding model ({config.MODEL_NAME}) on cpu...", file=sys.stderr)
    embed_model = get_embed_model(device="cpu")

    storage_context, client, _ = get_qdrant_vector_store(
        text_key="text", cfg=config, device="cpu"
    )

    mode = detect_collection_mode(client, config.COLLECTION_NAME)
    print(
        f"Collection: {config.COLLECTION_NAME}, mode: {mode}, alpha: {alpha}",
        file=sys.stderr,
    )

    index = VectorStoreIndex.from_vector_store(
        storage_context.vector_store, embed_model=embed_model
    )

    return index, mode, alpha


def run_query(index, mode, alpha, query, description="", desired_top_k=8):
    from shared.reranker import rerank_results, get_retrieval_top_k

    fetch_k = get_retrieval_top_k(query, desired_top_k)

    print(f"\n{'=' * 80}")
    if description:
        print(f"USE CASE: {description}")
    print(f"QUERY: {query}")
    if fetch_k != desired_top_k:
        print(f"OVERFETCH: {fetch_k} candidates (desired {desired_top_k})")
    print(f"{'=' * 80}")

    if mode == "hybrid":
        retriever = index.as_retriever(
            similarity_top_k=fetch_k,
            vector_store_query_mode=VectorStoreQueryMode.HYBRID,
            alpha=alpha,
            sparse_top_k=fetch_k,
        )
    else:
        retriever = index.as_retriever(similarity_top_k=fetch_k)

    nodes = asyncio.run(retriever.aretrieve(query))
    nodes = rerank_results(nodes, query, desired_top_k=desired_top_k, verbose=True)

    for i, n in enumerate(nodes, 1):
        meta = n.node.metadata
        content = n.node.get_content() or ""
        file_path = meta.get("file_path", "?")
        node_type = meta.get("node_type", meta.get("type", "?"))
        start_line = meta.get("start_line", "?")
        end_line = meta.get("end_line", "?")

        # Show first 500 chars of content
        preview = content[:500].replace("\n", "\n    ")

        print(
            f"\n  [{i}] score={n.score:.4f}  {file_path}  L{start_line}-{end_line}  type={node_type}"
        )
        print(f"    {preview}")
        if len(content) > 500:
            print(f"    ... ({len(content)} chars total)")

    print()
    return nodes


def main(alpha_override=None):
    index, mode, alpha = setup(alpha_override=alpha_override)

    # ── Use Case 1: Big-picture understanding queries ──────────────
    print("\n" + "#" * 80)
    print("# USE CASE 1: Big-picture understanding")
    print("#" * 80)

    run_query(
        index,
        mode,
        alpha,
        "What is TdmMain and what does it do?",
        "Class overview - should find class summary chunk with fields and methods",
    )

    run_query(
        index,
        mode,
        alpha,
        "What classes are in emar105.classes.pas?",
        "File overview - should find class summaries for TEmar105_OIK, TEmar105_File, etc.",
    )

    run_query(
        index,
        mode,
        alpha,
        "What is TfrmMainTurdus?",
        "Main form class - should find class summary with component declarations",
    )

    run_query(
        index,
        mode,
        alpha,
        "What does the Splash form look like?",
        "Simple form - should find Splash.pas class + Splash.dfm form header",
    )

    # ── Use Case 2: Precise keyword/BM25 search ──────────────────
    print("\n" + "#" * 80)
    print("# USE CASE 2: Precise keyword search (BM25)")
    print("#" * 80)

    run_query(
        index,
        mode,
        alpha,
        "REPORT_TYPE_PUNCTUALITY_RIDES",
        "Exact constant name - should find where this constant is used/defined",
    )

    run_query(
        index,
        mode,
        alpha,
        "PrepareDataSet",
        "Method name - should find PrepareDataSet method implementation(s)",
    )

    run_query(
        index,
        mode,
        alpha,
        "OpenConnection",
        "Method name - should find TdmMain.OpenConnection and related methods",
    )

    run_query(
        index,
        mode,
        alpha,
        "SLS_ReliefExport_Bilety_Get",
        "SQL stored procedure - should find the T-SQL procedure definition",
    )

    run_query(
        index,
        mode,
        alpha,
        "TCK_FarePrice_GetPriceForXDesignation",
        "SQL stored procedure - should find procedure signature and body",
    )

    run_query(
        index,
        mode,
        alpha,
        "GetCardSerialNumber",
        "Getter method in emar105 - should find in method group, not individual chunk",
    )

    # ── Use Case 3: Cross-file / dependency queries ──────────────
    print("\n" + "#" * 80)
    print("# USE CASE 3: Cross-file and dependency queries")
    print("#" * 80)

    run_query(
        index,
        mode,
        alpha,
        "uses clause MainDM",
        "Dependencies - should find MainDM.pas uses clause chunk",
    )

    run_query(
        index,
        mode,
        alpha,
        "TClientDataSet cdsStoredProc",
        "Field declarations - should find TdmMain published section with dataset fields",
    )

    # ── Use Case 4: DFM queries ──────────────────────────────────
    print("\n" + "#" * 80)
    print("# USE CASE 4: DFM form file queries")
    print("#" * 80)

    run_query(
        index,
        mode,
        alpha,
        "MainTurdus form components",
        "DFM overview - should find MainTurdus.dfm form header or component groups",
    )

    run_query(
        index,
        mode,
        alpha,
        "SFTP frame components",
        "DFM frame - should find WithFrame_SFTP.dfm",
    )

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--alpha",
        type=float,
        default=None,
        help="Override HYBRID_ALPHA (0.0=BM25 only, 1.0=dense only)",
    )
    args = parser.parse_args()
    main(alpha_override=args.alpha)
