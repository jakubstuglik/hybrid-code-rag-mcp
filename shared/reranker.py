"""
shared/reranker.py -- Post-retrieval reranking for hybrid search results.

Detects query intent (overview vs keyword) and adjusts result ordering
to promote structurally appropriate chunk types. This fixes the BM25
saturation problem where every chunk from a class gets the same 0.50
score because they all contain the class name in their context prefix.

The reranker does NOT change scores for keyword/precise queries -- it
only activates for "overview" queries like "What is TdmMain?" or
"What classes are in emar105?".

For overview queries, the recommended pattern is to over-fetch from the
vector store (e.g., 3x the desired top_k) and then let the reranker
sort and trim to the desired count.  This gives the reranker a larger
candidate pool so that overview-type chunks (class_overview, class_summary,
dfm_form_header) that scored lower in raw hybrid search still have a
chance to surface after score adjustment.

Use ``get_retrieval_top_k(query, desired_top_k)`` to compute the
over-fetch count, then pass ``desired_top_k`` to ``rerank_results``
so it trims the output back.
"""

import re
from typing import List, Optional, Tuple

from shared.log import log


# ────────────────────────────────────────────────────────────────────
# Over-fetch configuration
# ────────────────────────────────────────────────────────────────────

# For overview queries, retrieve this many times more candidates than
# the user-requested top_k.  The reranker trims back to the desired
# count after score adjustment.  5x means a top_k=8 query fetches 40
# candidates -- enough to surface class_overview/class_summary chunks
# that the raw hybrid scorer placed at position 20-40.  These chunks
# often have low raw scores because their large size dilutes the dense
# embedding, but they are THE most useful chunks for overview queries.
OVERFETCH_MULTIPLIER = 5


# ────────────────────────────────────────────────────────────────────
# Query intent detection
# ────────────────────────────────────────────────────────────────────

# Patterns that indicate an "overview" query wanting class/file summaries
_OVERVIEW_PATTERNS = [
    # "What is X" / "What does X do"
    re.compile(r"\bwhat\s+is\s+", re.IGNORECASE),
    re.compile(r"\bwhat\s+does\s+\S+\s+do\b", re.IGNORECASE),
    # "Describe X" / "Explain X" / "Tell me about X"
    re.compile(r"\bdescribe\s+", re.IGNORECASE),
    re.compile(r"\bexplain\s+", re.IGNORECASE),
    re.compile(r"\btell\s+me\s+about\s+", re.IGNORECASE),
    # "What classes are in X" / "What methods does X have"
    re.compile(r"\bwhat\s+classes\s+", re.IGNORECASE),
    re.compile(r"\bwhat\s+methods\s+", re.IGNORECASE),
    re.compile(r"\bwhat\s+fields\s+", re.IGNORECASE),
    re.compile(r"\bwhat\s+properties\s+", re.IGNORECASE),
    # "Overview of X" / "Summary of X" / "Structure of X"
    re.compile(r"\boverview\s+of\s+", re.IGNORECASE),
    re.compile(r"\bsummary\s+of\s+", re.IGNORECASE),
    re.compile(r"\bstructure\s+of\s+", re.IGNORECASE),
    # "X class" / "X form" / "X data module" (when asking about the thing itself)
    re.compile(r"\bclass\s+overview\b", re.IGNORECASE),
    re.compile(r"\bform\s+overview\b", re.IGNORECASE),
    # "How does X work"
    re.compile(r"\bhow\s+does\s+\S+\s+work\b", re.IGNORECASE),
    # "What does the X form look like"
    re.compile(r"\bwhat\s+does\s+the\s+.+\s+look\s+like\b", re.IGNORECASE),
    # "X form components" / "X components"
    re.compile(r"\bform\s+components\b", re.IGNORECASE),
    re.compile(r"\bframe\s+components\b", re.IGNORECASE),
]

# Patterns that indicate the query targets DFM/form content specifically.
# When matched, the reranker swaps the bonus: DFM chunks get the primary
# bonus and class_summary types get the lower bonus.  This prevents class
# code chunks from outranking DFM form headers on explicitly DFM-targeted
# queries like "SFTP frame components" or "MainTurdus form components".
_DFM_QUERY_PATTERNS = [
    re.compile(r"\bform\s+components\b", re.IGNORECASE),
    re.compile(r"\bframe\s+components\b", re.IGNORECASE),
    re.compile(r"\bform\s+layout\b", re.IGNORECASE),
    re.compile(r"\bform\s+header\b", re.IGNORECASE),
    re.compile(r"\bdfm\b", re.IGNORECASE),
    re.compile(r"\.dfm\b", re.IGNORECASE),
    re.compile(r"\bform\s+overview\b", re.IGNORECASE),
    re.compile(r"\bvisual\s+layout\b", re.IGNORECASE),
    re.compile(r"\bUI\s+components\b", re.IGNORECASE),
    re.compile(r"\bform\s+controls\b", re.IGNORECASE),
]

# Chunk types that are "overview" types -- preferred for overview queries
_OVERVIEW_CHUNK_TYPES = frozenset(
    {
        "class_overview",
        "class_summary",
        "class_summary_split",
        "dfm_form_header",
        "procedure_header",
        "function_header",
        "procedure_full",
        "function_full",
        "declUses",
    }
)

# DFM overview types -- these describe the visual form layout, not the class code.
# Separated from the general secondary overview types because they need different
# score adjustments depending on whether the query targets a Pascal class vs a form.
_DFM_OVERVIEW_TYPES = frozenset(
    {
        "dfm_form_header",
    }
)

# Chunk types that are "detail" types -- less useful as top results for overview queries
_DETAIL_CHUNK_TYPES = frozenset(
    {
        "comment",
        "comment_split",
        "method_group",
        "method_group_split",
        "defProc",
        "defProc_split",
        "declProc",
        "declProc_split",
        "declVar",
        "declVar_split",
        "declConst",
        "declConst_split",
        "declSection",
        "declSection_split",
    }
)


def is_overview_query(query: str) -> bool:
    """Detect if a query is asking for an overview/summary of a class, file, or module."""
    for pattern in _OVERVIEW_PATTERNS:
        if pattern.search(query):
            return True
    return False


def is_dfm_query(query: str) -> bool:
    """Detect if a query specifically targets DFM/form content.

    When True, the reranker swaps the bonus hierarchy: DFM overview types
    get the primary bonus instead of class_summary/class_overview.  This
    ensures that queries like "SFTP frame components" or "MainTurdus form
    components" promote DFM form headers above class code summaries.
    """
    for pattern in _DFM_QUERY_PATTERNS:
        if pattern.search(query):
            return True
    return False


def get_retrieval_top_k(query: str, desired_top_k: int) -> int:
    """Return the number of candidates to fetch from the vector store.

    For overview queries, returns ``desired_top_k * OVERFETCH_MULTIPLIER``
    so that the reranker has a larger pool to work with.  For non-overview
    queries, returns ``desired_top_k`` unchanged.
    """
    if is_overview_query(query):
        return desired_top_k * OVERFETCH_MULTIPLIER
    return desired_top_k


# ────────────────────────────────────────────────────────────────────
# Target identifier extraction
# ────────────────────────────────────────────────────────────────────

# Pascal/Delphi identifiers: TdmMain, TfrmMainTurdus, TEmar105_OIK
# Note: second char can be lowercase (Tdm, Tfrm) — Delphi convention varies
_PASCAL_IDENT = re.compile(r"\bT[a-zA-Z][a-zA-Z0-9_]+\b")

# File names without extension: emar105.classes, MainDM, MainTurdus
_FILE_STEM = re.compile(
    r"\b([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*)\.pas\b", re.IGNORECASE
)
_FILE_STEM_NO_EXT = re.compile(
    r"\b(emar105|MainDM|MainTurdus|Splash|SalesReport|BaseEditorForm)\b", re.IGNORECASE
)

# General capitalized-word pattern for target extraction.  Matches PascalCase,
# camelCase, ALLCAPS (>= 3 chars), and underscore_separated identifiers that
# look like file stems or code identifiers.  Filtered against a stop-word set
# to exclude common English words that happen to start with uppercase.
_GENERAL_IDENT = re.compile(r"\b([A-Z][A-Za-z0-9_]{2,})\b")

# Common English words that start with uppercase in natural language queries.
# These should NOT be treated as target identifiers.
_TARGET_STOP_WORDS = frozenset(
    {
        "what",
        "does",
        "how",
        "where",
        "when",
        "who",
        "which",
        "why",
        "the",
        "this",
        "that",
        "these",
        "those",
        "with",
        "from",
        "into",
        "about",
        "tell",
        "describe",
        "explain",
        "overview",
        "summary",
        "structure",
        "class",
        "form",
        "frame",
        "components",
        "layout",
        "header",
        "visual",
        "controls",
        "defined",
        "export",
        "import",
        "how",
        "are",
        "all",
        "any",
        "has",
        "have",
        "get",
        "set",
        "for",
        "not",
        "and",
        "but",
        "the",
        "look",
        "like",
        "show",
        "find",
        "list",
        "what",
        "fields",
        "methods",
        "properties",
        "classes",
        "procedures",
        "functions",
        "types",
        "data",
        "module",
        "work",
    }
)

# SQL procedure names
_SQL_PROC = re.compile(r"\b((?:dbo\.)?[A-Z][A-Za-z0-9_]+(?:_[A-Za-z0-9]+)+)\b")


def extract_target_identifiers(query: str) -> List[str]:
    """Extract likely target class/file/procedure names from a query.

    Returns a list of identifiers that the user is probably asking about,
    lowercased for case-insensitive matching.
    """
    targets = []

    # Pascal class names (T-prefixed)
    for m in _PASCAL_IDENT.finditer(query):
        targets.append(m.group().lower())

    # File names with .pas extension
    for m in _FILE_STEM.finditer(query):
        targets.append(m.group(1).lower())

    # Known file stems without extension (common in queries)
    for m in _FILE_STEM_NO_EXT.finditer(query):
        targets.append(m.group().lower())

    # SQL procedure names
    for m in _SQL_PROC.finditer(query):
        targets.append(m.group().lower())

    # General capitalized identifiers (PascalCase, ALLCAPS, etc.)
    # These catch identifiers not matched by the specific patterns above,
    # like "SFTP" or "BaseEditorForm" when used without .pas extension.
    for m in _GENERAL_IDENT.finditer(query):
        word = m.group(1)
        if word.lower() not in _TARGET_STOP_WORDS:
            targets.append(word.lower())

    return list(set(targets))


# ────────────────────────────────────────────────────────────────────
# File-target matching
# ────────────────────────────────────────────────────────────────────


def _chunk_matches_target(meta: dict, targets: List[str]) -> bool:
    """Check if a chunk's file_path or class_name metadata matches any target identifier."""
    if not targets:
        return False  # No target extracted — can't determine relevance

    file_path = (meta.get("file_path") or "").lower()
    class_name = (meta.get("class_name") or "").lower()
    unit_name = (meta.get("unit_name") or "").lower()
    object_name = (meta.get("object_name") or "").lower()
    content_lower = ""  # We'll check content only if needed

    for target in targets:
        # Direct class name match
        if class_name and target in class_name:
            return True
        # Unit name match
        if unit_name and target in unit_name:
            return True
        # SQL object name match (procedure, function, table, view, trigger)
        if object_name and target in object_name:
            return True
        # File path match (e.g., "emar105" in "emar105.classes.pas")
        if file_path and target in file_path:
            return True

    return False


# ────────────────────────────────────────────────────────────────────
# Score adjustment calculation
# ────────────────────────────────────────────────────────────────────

# Bonus for overview chunk types when query is an overview query.
# "Secondary" overview types: procedure_header, function_header, declUses, etc.
_OVERVIEW_BONUS = 0.25

# DFM overview bonus -- lower than other secondary overview types because DFM
# chunks describe visual form layout, not class code.  For overview queries about
# Pascal classes, DFM form headers are informational but NOT the primary answer.
_DFM_OVERVIEW_BONUS = 0.10

# Higher bonus for "primary overview" chunk types (class_overview, class_summary)
# that directly answer "What is X?" questions.  These chunks often have very low
# raw hybrid scores (position 30-40) because their large size dilutes the dense
# embedding, but they are THE most useful results for overview queries.
# Increased from 0.50 to 0.65 to give class summaries stronger separation from
# DFM form headers which also score well in BM25 (they contain the class name).
_PRIMARY_OVERVIEW_BONUS = 0.65

# Primary overview types -- the specific chunks that best answer "What is X?"
_PRIMARY_OVERVIEW_TYPES = frozenset(
    {
        "class_overview",
        "class_summary",
        "class_summary_split",
    }
)

# Bonus for chunks whose file matches the query target
_TARGET_MATCH_BONUS = 0.15

# Penalty for comment chunks from non-target files
_CROSS_FILE_COMMENT_PENALTY = 0.30

# Penalty for overview chunks from non-target files (prevents cross-file interlopers).
# Increased from 0.20 to 0.30 to more aggressively suppress cross-file overview chunks
# that appear above the target's own chunks due to BM25 saturation.
_NON_TARGET_OVERVIEW_PENALTY = 0.30

# Penalty for detail chunks in overview queries (mild, just enough to break ties)
_DETAIL_PENALTY = 0.05

# Penalty for DFM chunks when the query targets a Pascal class (T-prefixed).
# DFM describes the visual form layout, not the class code.  When the user asks
# "What is TdmMain?", the DFM form header is not the answer -- the class_summary is.
_DFM_ON_CLASS_QUERY_PENALTY = 0.15


def _compute_rerank_score(
    original_score: float,
    node_type: str,
    meta: dict,
    is_overview: bool,
    is_dfm: bool,
    targets: List[str],
) -> float:
    """Compute an adjusted score for reranking.

    For overview queries:
      - Strong boost for primary overview types (class_overview, class_summary)
        that match the target -- these are THE answer to "What is X?"
      - When is_dfm=True, the bonus is SWAPPED: DFM chunks get the primary
        bonus and class_summary types get the lower bonus.  This ensures
        "form components" / "frame components" queries promote DFM form headers.
      - Moderate boost for structural overview types (proc headers, declUses)
      - Boost chunks from the target file/class
      - Penalize overview chunks from non-target files (cross-file interlopers)
      - Extra penalty for DFM chunks when query targets a Pascal class
        (only when is_dfm=False)
      - Penalize cross-file comment chunks
      - Mild penalty for detail chunks (defProc, method_group, etc.)

    For non-overview queries:
      - No changes (return original score)
    """
    if not is_overview:
        return original_score

    score = original_score
    matches_target = _chunk_matches_target(meta, targets)

    # Detect if the query targets a Pascal class (T-prefixed identifier)
    targets_pascal_class = any(t.startswith("t") and len(t) > 2 for t in targets)

    # DFM-query mode: swap bonus hierarchy so DFM chunks are primary
    if is_dfm:
        # DFM overview types get the PRIMARY bonus (they ARE the answer)
        if node_type in _DFM_OVERVIEW_TYPES:
            score += _PRIMARY_OVERVIEW_BONUS
        # Class summary types get the lower DFM bonus (supporting context only)
        elif node_type in _PRIMARY_OVERVIEW_TYPES:
            score += _DFM_OVERVIEW_BONUS
        # Other overview types get moderate boost (unchanged)
        elif node_type in _OVERVIEW_CHUNK_TYPES:
            score += _OVERVIEW_BONUS
    else:
        # Standard mode: class overview types are primary
        # Primary overview types get a strong boost
        if node_type in _PRIMARY_OVERVIEW_TYPES:
            score += _PRIMARY_OVERVIEW_BONUS
        # DFM overview types get a mild boost (lower than other secondary types)
        elif node_type in _DFM_OVERVIEW_TYPES:
            score += _DFM_OVERVIEW_BONUS
            # Extra penalty when query targets a Pascal class -- DFM form headers
            # are about visual layout, not class code
            if targets_pascal_class:
                score -= _DFM_ON_CLASS_QUERY_PENALTY
        # Other overview types get a moderate boost
        elif node_type in _OVERVIEW_CHUNK_TYPES:
            score += _OVERVIEW_BONUS

    # Boost chunks from the target file/class
    if matches_target:
        score += _TARGET_MATCH_BONUS

    # Penalize overview chunks from non-target files (when we have targets)
    # This prevents cross-file class_summary/class_overview from appearing
    # above the target's own chunks.
    if (
        (node_type in _OVERVIEW_CHUNK_TYPES or node_type in _PRIMARY_OVERVIEW_TYPES)
        and targets
        and not matches_target
    ):
        score -= _NON_TARGET_OVERVIEW_PENALTY

    # Penalize comment chunks from non-target files (only when we have targets)
    if node_type in ("comment", "comment_split") and targets and not matches_target:
        score -= _CROSS_FILE_COMMENT_PENALTY

    # Mild penalty for detail chunks that aren't overview types
    if node_type in _DETAIL_CHUNK_TYPES and node_type not in (
        "comment",
        "comment_split",
    ):
        score -= _DETAIL_PENALTY

    return score


# ────────────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────────────


def rerank_results(
    nodes: list,
    query: str,
    desired_top_k: Optional[int] = None,
    verbose: bool = False,
) -> list:
    """Rerank retrieval results based on query intent and chunk types.

    Args:
        nodes: List of NodeWithScore objects from LlamaIndex retrieval.
        query: The original query string.
        desired_top_k: If set, trim the output to this many results after
            reranking.  When using over-fetch (see ``get_retrieval_top_k``),
            pass the *original* user-requested top_k here so that the
            extra candidates are removed after score adjustment.
        verbose: If True, log reranking details.

    Returns:
        The same list of nodes, re-sorted by adjusted scores and optionally
        trimmed to ``desired_top_k``.  The original score attribute on each
        node is NOT modified -- the reranking is done via sorting only.
    """
    if not nodes:
        return nodes

    is_overview = is_overview_query(query)
    targets = extract_target_identifiers(query) if is_overview else []
    dfm_mode = is_dfm_query(query) if is_overview else False

    if verbose:
        log(
            f"[rerank] overview={is_overview}, dfm={dfm_mode}, targets={targets}, "
            f"candidates={len(nodes)}, desired_top_k={desired_top_k}"
        )

    if not is_overview:
        # Non-overview queries: no reranking needed, just trim if requested
        if verbose:
            log("[rerank] skipping rerank (not overview query)")
        if desired_top_k is not None:
            return nodes[:desired_top_k]
        return nodes

    # Compute adjusted scores and sort
    scored: List[Tuple[float, int, object]] = []
    for i, n in enumerate(nodes):
        meta = n.node.metadata if hasattr(n, "node") else {}
        node_type = meta.get("node_type", meta.get("type", "text"))
        original_score = n.score if hasattr(n, "score") else 0.0

        adjusted = _compute_rerank_score(
            original_score, node_type, meta, is_overview, dfm_mode, targets
        )

        if verbose and adjusted != original_score:
            file_path = meta.get("file_path", "?")
            log(
                f"[rerank] {node_type:30s} {file_path:40s} "
                f"score {original_score:.4f} -> {adjusted:.4f} "
                f"(delta={adjusted - original_score:+.4f})"
            )

        scored.append((adjusted, i, n))

    # Sort by adjusted score descending, then by original position (stable)
    scored.sort(key=lambda x: (-x[0], x[1]))

    reranked = [item[2] for item in scored]

    # Trim to desired count (removes the over-fetched extras)
    if desired_top_k is not None:
        reranked = reranked[:desired_top_k]

    if verbose:
        log(
            f"[rerank] done, returning {len(reranked)} results, "
            f"top node_type={reranked[0].node.metadata.get('node_type', '?')}"
        )

    return reranked
