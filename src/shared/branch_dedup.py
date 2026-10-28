"""Branch-aware query filtering and post-retrieval deduplication.

This module provides:
  - Qdrant filter construction for branch-aware queries
  - Post-retrieval dedup: prefer feature-branch chunks over main-branch
  - Tombstone filtering for deleted files

Used by ``rag_mcp.py`` when the ``branch`` parameter is specified. The
parameter takes any configured overlay name, branch or tag.
"""

from typing import List, Optional

from shared.log import log


# Passed to the MCP search tool's ``branch`` parameter. The value is an
# overlay label from config (a branch or a moving tag). An unknown or
# never-indexed label adds no points, so the caller still receives main.
BRANCH_PARAMETER_DESCRIPTION = (
    "Configured overlay name. When set, results include the main branch plus "
    "the overlay stored under this label. The overlay wins on the same path, "
    "and tombstones hide files the overlay deletes. "
    "Pass the overlay's name from config (a git branch or a moving tag). "
    "Use git branch --show-current when the checked-out branch is configured "
    "as an overlay. "
    "If the name has never been indexed, the filter matches nothing extra "
    "and you get main-branch results. "
    "Leave empty to search the configured main branch only."
)


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


def _node_metadata(node) -> dict:
    """Payload dict for a ``NodeWithScore``, or empty when it has none."""
    meta = node.node.metadata if hasattr(node.node, "metadata") else {}
    return meta or {}


def _partition_for_dedup(nodes, feature_branch: str, tombstone_set: set):
    """Group ``nodes`` by path the way branch dedup decides winners.

    Tombstoned paths are omitted. Chunks with no ``file_path`` are returned
    on their own, in input order. Each kept entry is
    ``(node, is_feature, is_branchless)``, also in input order.

    Returns:
        ``(seen_files, no_file_path)``.
    """
    seen_files: dict[str, list] = {}
    no_file_path: list = []

    for node in nodes:
        meta = _node_metadata(node)
        file_path = meta.get("file_path", "")
        branch = meta.get("branch")

        if not file_path:
            no_file_path.append(node)
            continue

        if file_path in tombstone_set:
            continue

        is_feature = branch == feature_branch
        is_branchless = branch is None
        if file_path not in seen_files:
            seen_files[file_path] = []
        seen_files[file_path].append((node, is_feature, is_branchless))

    return seen_files, no_file_path


def _prefer_overlay_entries(entries: list) -> list:
    """Nodes to keep for one path: feature, else branchless, else main."""
    feature_entries = [entry for entry in entries if entry[1]]
    branchless_entries = [entry for entry in entries if entry[2]]
    main_entries = [entry for entry in entries if not entry[1] and not entry[2]]

    if feature_entries:
        return [node for node, _, _ in feature_entries]
    if branchless_entries:
        return [node for node, _, _ in branchless_entries]
    return [node for node, _, _ in main_entries]


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
    seen_files, no_file_path = _partition_for_dedup(
        nodes, feature_branch, tombstone_set
    )

    result = []
    for entries in seen_files.values():
        result.extend(_prefer_overlay_entries(entries))
    result.extend(no_file_path)

    # Sort by score (descending) to restore ranking
    result.sort(key=lambda n: n.score if n.score is not None else 0, reverse=True)

    return result[:desired_top_k]


def filter_symbol_candidates(
    nodes,
    extra,
    feature_branch: str,
    tombstones: Optional[List[str]] = None,
):
    """Apply branch dedup to symbol-lookup hits and the main pool together.

    The overlay decision uses the union of ``nodes`` and ``extra``. A
    feature-branch chunk in either list hides the main-branch copy of that
    path in both. Tombstoned paths are removed from ``extra``. A symbol hit
    with no branch is kept unless that path also has a feature-branch chunk,
    which is the preference ``dedup_branch_results`` already uses.

    ``nodes`` is updated in place and loses only those shadowed main-branch
    copies. Tombstone removal, the score sort and the ``desired_top_k`` trim
    stay in ``dedup_branch_results``, so call that on ``nodes`` afterwards.
    Symbol hits are not given a score here.

    An empty ``extra`` is returned as given and ``nodes`` is left untouched.
    """
    if not extra:
        return extra

    tombstone_set = set(tombstones) if tombstones else set()
    seen_files, _no_file_path = _partition_for_dedup(
        list(nodes or []) + list(extra), feature_branch, tombstone_set
    )
    preferred_ids: set[int] = set()
    feature_files: set[str] = set()
    for file_path, entries in seen_files.items():
        if any(is_feature for _node, is_feature, _branchless in entries):
            feature_files.add(file_path)
        for node in _prefer_overlay_entries(entries):
            preferred_ids.add(id(node))

    surviving = []
    for node in extra:
        file_path = _node_metadata(node).get("file_path", "")
        if not file_path:
            surviving.append(node)
            continue
        if file_path in tombstone_set:
            continue
        if id(node) in preferred_ids:
            surviving.append(node)

    if nodes:
        kept = []
        for node in nodes:
            meta = _node_metadata(node)
            file_path = meta.get("file_path", "")
            branch = meta.get("branch")
            shadowed = (
                file_path
                and file_path in feature_files
                and branch != feature_branch
                and branch is not None
            )
            if not shadowed:
                kept.append(node)
        nodes[:] = kept
    return surviving


def get_branch_tombstones(feature_branch: str, config) -> List[str]:
    """Load tombstones for an overlay (branch or tag) from its manifest.

    Args:
        feature_branch: Configured overlay name.
        config: Merged config module.

    Returns:
        List of file_path keys that are deleted on the feature branch.
    """
    import json
    from pathlib import Path
    from shared.overlay import overlay_manifest_filename

    index_path = Path(config.get_index_path()).resolve()
    manifest_path = index_path / overlay_manifest_filename(feature_branch)

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
