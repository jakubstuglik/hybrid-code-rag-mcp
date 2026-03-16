"""Branch-aware query filtering and post-retrieval deduplication.

This module provides:
  - Qdrant filter construction for branch-aware queries
  - Post-retrieval dedup: prefer feature-branch chunks over main-branch
  - Tombstone filtering for deleted files

Used by ``rag_mcp.py`` when the ``branch`` parameter is specified.
"""

from typing import List, Optional

from shared.log import log


# ── Qdrant filter construction ───────────────────────────────────


def build_branch_filter(
    main_branch: str,
    feature_branch: Optional[str] = None,
):
    """Build a Qdrant filter for branch-aware queries.

    Args:
        main_branch: Name of the main branch (e.g. "develop").
        feature_branch: Optional feature branch name.  When None, only
            main-branch and non-git (branch IS NULL) chunks are returned.

    Returns:
        A ``qdrant_client.models.Filter`` instance.

    Filter logic:
      - No feature_branch: ``branch == main_branch OR branch IS NULL``
      - With feature_branch: ``branch == main_branch OR branch == feature_branch OR branch IS NULL``

    The ``branch IS NULL`` clause ensures non-git ``source_set`` chunks
    (which have no branch field) always pass through.
    """
    from qdrant_client import models

    match_values = [main_branch]
    if feature_branch:
        match_values.append(feature_branch)

    return models.Filter(
        should=[
            # Match main branch (and feature branch if specified)
            models.FieldCondition(
                key="branch",
                match=models.MatchAny(any=match_values),
            ),
            # Match chunks with no branch field (non-git source_set chunks).
            # Use IsEmptyCondition (field absent from payload) rather than
            # IsNullCondition (field present with null value) — non-git
            # chunks never have the branch key written at all.
            models.IsEmptyCondition(
                is_empty=models.PayloadField(key="branch"),
            ),
        ],
    )


# ── Post-retrieval deduplication ─────────────────────────────────


def dedup_branch_results(
    nodes,
    feature_branch: str,
    tombstones: Optional[List[str]] = None,
    desired_top_k: int = 8,
):
    """Deduplicate retrieval results, preferring feature-branch chunks.

    When the same ``file_path`` appears in both main-branch and
    feature-branch results, only the feature-branch version is kept.
    Non-git chunks (no ``branch`` metadata) are always kept.

    Args:
        nodes: List of ``NodeWithScore`` from the retriever.
        feature_branch: The requested feature branch name.
        tombstones: List of file_path keys deleted on the feature branch.
            Results matching these are removed.
        desired_top_k: Target number of results after dedup.

    Returns:
        Deduplicated list of ``NodeWithScore``, trimmed to ``desired_top_k``.
    """
    if not nodes:
        return nodes

    tombstone_set = set(tombstones) if tombstones else set()

    # Group by file_path, tracking which branch each result belongs to
    # We process in order (highest score first) to preserve ranking
    seen_files: dict[str, list] = {}  # file_path -> list of (node, is_branch)
    no_file_path: list = []  # nodes without file_path (shouldn't happen, but safe)

    for node in nodes:
        meta = node.node.metadata if hasattr(node.node, "metadata") else {}
        file_path = meta.get("file_path", "")
        branch = meta.get("branch")

        if not file_path:
            no_file_path.append(node)
            continue

        # Filter tombstones: files deleted on the feature branch
        if file_path in tombstone_set:
            continue

        is_feature = branch == feature_branch
        is_branchless = branch is None  # non-git chunk

        if file_path not in seen_files:
            seen_files[file_path] = []

        seen_files[file_path].append((node, is_feature, is_branchless))

    # Resolve: for each file_path, prefer feature-branch chunks
    result = []

    for file_path, entries in seen_files.items():
        feature_entries = [e for e in entries if e[1]]  # is_feature
        branchless_entries = [e for e in entries if e[2]]  # is_branchless
        main_entries = [e for e in entries if not e[1] and not e[2]]

        if feature_entries:
            # Feature branch wins — keep all feature-branch chunks for this file
            result.extend(n for n, _, _ in feature_entries)
        elif branchless_entries:
            # Non-git chunks — always keep
            result.extend(n for n, _, _ in branchless_entries)
        else:
            # Only main-branch chunks — keep them (no feature override)
            result.extend(n for n, _, _ in main_entries)

    # Add back nodes without file_path
    result.extend(no_file_path)

    # Sort by score (descending) to restore ranking
    result.sort(key=lambda n: n.score if n.score is not None else 0, reverse=True)

    return result[:desired_top_k]


def get_branch_tombstones(feature_branch: str, config) -> List[str]:
    """Load tombstones for a feature branch from its manifest.

    Args:
        feature_branch: Branch name.
        config: Merged config module.

    Returns:
        List of file_path keys that are deleted on the feature branch.
    """
    import json
    from pathlib import Path
    from shared.git_ops import sanitize_branch_name

    index_path = Path(config.get_index_path()).resolve()
    safe = sanitize_branch_name(feature_branch)
    manifest_path = index_path / f"index_manifest_branch_{safe}.json"

    if not manifest_path.exists():
        return []

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tombstones", [])
    except Exception:
        return []


def get_main_branch_name(config) -> str:
    """Get the main branch name from config.

    Inspects SOURCE_DIRS for git_repo entries and returns the main_branch
    of the first one found.  Falls back to "master" if none configured.
    """
    source_dirs = getattr(config, "SOURCE_DIRS", [])
    for entry in source_dirs:
        if entry.get("type") == "git_repo":
            return entry.get("main_branch", "master")
    return "master"
