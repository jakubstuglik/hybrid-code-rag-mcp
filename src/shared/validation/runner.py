"""
shared.validation.runner -- Query execution and evaluation logic.

Provides setup() to initialize the retrieval pipeline, run_query() to
execute a single query, and evaluate_test() to score results against
PassCriteria. This module is config-agnostic -- it works with any
project's test cases.
"""

import os
import re
import sys
import asyncio
from typing import List, Optional, Tuple, Any

import config_loader
from shared.embedding import get_embed_model
from qdrant.vector_store import get_qdrant_vector_store, detect_collection_mode
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from shared.reranker import rerank_results, get_retrieval_top_k

from shared.validation.models import PassCriteria, TestCase, TestResult


# ────────────────────────────────────────────────────────────────────
# Setup
# ────────────────────────────────────────────────────────────────────


def setup(config_name=None, alpha_override=None):
    """Load config, embedding model, and create the retriever index.

    Args:
        config_name: Config name or path (passed to config_loader).
        alpha_override: Override HYBRID_ALPHA from config.

    Returns:
        Tuple of (index, mode, alpha, config).
    """
    config = config_loader.get_config(config_name=config_name)

    alpha = (
        alpha_override
        if alpha_override is not None
        else getattr(config, "HYBRID_ALPHA", 0.5)
    )

    print(f"Loading embedding model ({config.MODEL_NAME}) on cpu...", file=sys.stderr)
    embed_model = get_embed_model(device="cpu", cfg=config)

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

    return index, mode, alpha, config


# ────────────────────────────────────────────────────────────────────
# Query execution
# ────────────────────────────────────────────────────────────────────


def run_query(index, mode, alpha, query, top_k=8):
    """Execute a single retrieval query and return reranked nodes.

    Args:
        index: VectorStoreIndex instance.
        mode: Collection mode ("hybrid" or "dense").
        alpha: Hybrid alpha value (0.0=BM25, 1.0=dense).
        query: Query text.
        top_k: Number of results to return.

    Returns:
        List of reranked NodeWithScore objects.
    """
    fetch_k = get_retrieval_top_k(query, top_k)

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
    nodes = rerank_results(nodes, query, desired_top_k=top_k, verbose=False)
    return nodes


# ────────────────────────────────────────────────────────────────────
# Node matching helpers
# ────────────────────────────────────────────────────────────────────


def _node_matches(node, criteria: PassCriteria) -> bool:
    """Check if a single retrieved node matches ALL specified criteria."""
    meta = node.node.metadata
    content = node.node.get_content() or ""
    node_type = meta.get("node_type", meta.get("type", ""))
    file_path = meta.get("file_path", "")
    class_name = meta.get("class_name", "")

    if criteria.node_types is not None:
        if node_type not in criteria.node_types:
            return False

    if criteria.file_pattern is not None:
        if not re.search(criteria.file_pattern, file_path):
            return False

    if criteria.text_pattern is not None:
        if not re.search(criteria.text_pattern, content):
            return False

    if criteria.class_name_pattern is not None:
        if not re.search(criteria.class_name_pattern, class_name or ""):
            return False

    return True


def _file_matches(node, criteria: PassCriteria) -> bool:
    """Check if just the file_path matches (for PARTIAL evaluation)."""
    if criteria.file_pattern is None:
        return False
    file_path = node.node.metadata.get("file_path", "")
    return bool(re.search(criteria.file_pattern, file_path))


def _type_matches(node, criteria: PassCriteria) -> bool:
    """Check if just the node_type matches (for PARTIAL evaluation)."""
    if criteria.node_types is None:
        return False
    node_type = node.node.metadata.get("node_type", node.node.metadata.get("type", ""))
    return node_type in criteria.node_types


def _text_matches(node, criteria: PassCriteria) -> bool:
    """Check if just the text_pattern matches (for PARTIAL evaluation)."""
    if criteria.text_pattern is None:
        return False
    content = node.node.get_content() or ""
    return bool(re.search(criteria.text_pattern, content))


# ────────────────────────────────────────────────────────────────────
# Evaluation
# ────────────────────────────────────────────────────────────────────


def _build_node_infos(nodes, top_k: int) -> list:
    """Build a list of node info dicts from retrieved nodes."""
    node_infos = []
    for i, n in enumerate(nodes[:top_k], 1):
        meta = n.node.metadata
        node_infos.append(
            {
                "position": i,
                "node_type": meta.get("node_type", meta.get("type", "?")),
                "file_path": meta.get("file_path", "?"),
                "score": round(n.score, 4) if n.score is not None else None,
                "class_name": meta.get("class_name", ""),
            }
        )
    return node_infos


def _evaluate_multi_file(
    tc: TestCase, nodes, criteria: PassCriteria, node_infos: list, top_k: int
) -> TestResult:
    """Evaluate a multi_file test case."""
    matched_files = set()
    first_match_pos = None
    first_match_info = None

    for i, n in enumerate(nodes[:top_k], 1):
        if _node_matches(n, criteria):
            file_path = n.node.metadata.get("file_path", "")
            basename = os.path.basename(file_path)
            matched_files.add(basename)
            if first_match_pos is None:
                first_match_pos = i
                first_match_info = node_infos[i - 1]

    if (
        len(matched_files) >= 2
        and first_match_pos is not None
        and first_match_pos <= criteria.max_position
    ):
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PASS",
            match_position=first_match_pos,
            match_node_type=first_match_info["node_type"],
            match_file=first_match_info["file_path"],
            match_score=first_match_info["score"],
            all_nodes=node_infos,
        )

    if (
        len(matched_files) >= 2
        and first_match_pos is not None
        and first_match_pos <= criteria.partial_position
    ):
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PARTIAL",
            match_position=first_match_pos,
            match_node_type=first_match_info["node_type"],
            match_file=first_match_info["file_path"],
            match_score=first_match_info["score"],
            detail=(
                f"Multi-file match at position {first_match_pos} "
                f"(>{criteria.max_position}), {len(matched_files)} files"
            ),
            all_nodes=node_infos,
        )

    if len(matched_files) == 1 and first_match_pos is not None:
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PARTIAL",
            match_position=first_match_pos,
            match_node_type=first_match_info["node_type"],
            match_file=first_match_info["file_path"],
            match_score=first_match_info["score"],
            detail=f"Only 1 file matched (need >=2): {matched_files}",
            all_nodes=node_infos,
        )

    return TestResult(
        id=tc.id,
        category=tc.category,
        query=tc.query,
        result="FAIL",
        detail="No matching nodes found in top results",
        all_nodes=node_infos,
    )


def evaluate_test(tc: TestCase, nodes, top_k: int = 8) -> TestResult:
    """Evaluate retrieval results against a test case's pass criteria.

    Args:
        tc: The test case definition.
        nodes: List of NodeWithScore from the retriever.
        top_k: Number of results to consider.

    Returns:
        TestResult with PASS / PARTIAL / FAIL and match details.
    """
    criteria = tc.pass_criteria
    node_infos = _build_node_infos(nodes, top_k)

    # Handle multi_file test: PASS requires matches from >= 2 different files
    if criteria.multi_file:
        return _evaluate_multi_file(tc, nodes, criteria, node_infos, top_k)

    # Standard (non multi_file) evaluation
    first_full_match_pos = None
    first_full_match_info = None
    first_partial_file_pos = None
    first_partial_type_pos = None
    first_partial_text_pos = None

    for i, n in enumerate(nodes[:top_k], 1):
        info = node_infos[i - 1]

        # Full match check
        if _node_matches(n, criteria):
            if first_full_match_pos is None:
                first_full_match_pos = i
                first_full_match_info = info

        # Partial match checks (file only, type only, text only)
        if first_partial_file_pos is None and _file_matches(n, criteria):
            first_partial_file_pos = i
        if first_partial_type_pos is None and _type_matches(n, criteria):
            first_partial_type_pos = i
        if first_partial_text_pos is None and _text_matches(n, criteria):
            first_partial_text_pos = i

    # PASS: full match at position <= max_position
    if (
        first_full_match_pos is not None
        and first_full_match_pos <= criteria.max_position
    ):
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PASS",
            match_position=first_full_match_pos,
            match_node_type=first_full_match_info["node_type"],
            match_file=first_full_match_info["file_path"],
            match_score=first_full_match_info["score"],
            all_nodes=node_infos,
        )

    # PARTIAL: full match at position <= partial_position
    if (
        first_full_match_pos is not None
        and first_full_match_pos <= criteria.partial_position
    ):
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PARTIAL",
            match_position=first_full_match_pos,
            match_node_type=first_full_match_info["node_type"],
            match_file=first_full_match_info["file_path"],
            match_score=first_full_match_info["score"],
            detail=f"Full match at position {first_full_match_pos} (>{criteria.max_position})",
            all_nodes=node_infos,
        )

    # PARTIAL: file_path matches but node_type doesn't (or vice versa)
    partial_reasons = []
    if (
        first_partial_file_pos is not None
        and first_partial_file_pos <= criteria.partial_position
    ):
        partial_reasons.append(f"file_path match at #{first_partial_file_pos}")
    if (
        first_partial_type_pos is not None
        and first_partial_type_pos <= criteria.partial_position
    ):
        partial_reasons.append(f"node_type match at #{first_partial_type_pos}")
    if (
        first_partial_text_pos is not None
        and first_partial_text_pos <= criteria.partial_position
    ):
        partial_reasons.append(f"text_pattern match at #{first_partial_text_pos}")

    if partial_reasons:
        best_pos = min(
            p
            for p in [
                first_partial_file_pos,
                first_partial_type_pos,
                first_partial_text_pos,
            ]
            if p is not None and p <= criteria.partial_position
        )
        best_info = node_infos[best_pos - 1]
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PARTIAL",
            match_position=best_pos,
            match_node_type=best_info["node_type"],
            match_file=best_info["file_path"],
            match_score=best_info["score"],
            detail=f"Partial: {', '.join(partial_reasons)}",
            all_nodes=node_infos,
        )

    # FAIL: no matching node in top results
    return TestResult(
        id=tc.id,
        category=tc.category,
        query=tc.query,
        result="FAIL",
        detail="No matching nodes found in top results",
        all_nodes=node_infos,
    )
