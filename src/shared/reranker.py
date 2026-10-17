"""
shared/reranker.py -- Post-retrieval reranking for hybrid search results.

Detects query intent (overview vs keyword) and adjusts result ordering
to promote structurally appropriate chunk types. This fixes the BM25
saturation problem where every chunk from a class gets the same 0.50
score because they all contain the class name in their context prefix.

The reranker does NOT change scores for keyword/precise queries -- it
only activates for "overview" queries like "What is TdmOrders?" or
"What classes are in base42?".

For overview queries, the recommended pattern is to over-fetch from the
vector store (e.g., 3x the desired top_k) and then let the reranker
sort and trim to the desired count.  This gives the reranker a larger
candidate pool so that overview-type chunks (class_overview, class_summary,
dfm_form_header) that scored lower in raw hybrid search still have a
chance to surface after score adjustment.

Use ``get_retrieval_top_k(query, desired_top_k)`` to compute the
over-fetch count, then pass ``desired_top_k`` to ``rerank_results``
so it trims the output back.

Generic core + per-reader profiles:

    The core in this module knows only generic concepts: overview-query
    phrasing, target identifiers (path components, capitalised identifiers,
    digit-bearing stems), the primary overview chunks ``class_overview`` /
    ``class_summary`` (+``_split``), ``method_group``, comment and
    ``import_group`` chunks, and the score arithmetic.

    Language- and format-specific knowledge (Delphi, forms, reports, project
    files, ORM mappings, SQL, Java-style languages, JS/TS, C/C++, ...) lives
    in ``RerankProfile`` objects (``shared/rerank_profile.py``) attached to
    the readers in ``READER_REGISTRY``.  Only the profiles of readers that
    index files in the project are active (``rerank_profiles_for_config``);
    ``RERANK_PROFILES = [...]`` in a project config overrides the selection.
    Passing ``profiles=None`` to the public functions activates every
    registered profile.
"""

import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

from shared.log import log
from shared.rerank_profile import QueryDomain, RerankProfile, compile_all

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
# Increased from 5 to 10 in iteration-004: for very large files like
# OrderForm.pas (400+ chunks), class_overview was at raw position #16,
# outside the 40-candidate pool (5*8).  10x gives 80 candidates, enough
# to capture overview chunks that land in the 15-60 range.
OVERFETCH_MULTIPLIER = 10


# ────────────────────────────────────────────────────────────────────
# Generic (language-neutral) query intent detection
# ────────────────────────────────────────────────────────────────────

# Phrasings that indicate an "overview" query wanting class/file summaries.
# Profiles add format-specific phrasings (e.g. "report structure").
_CORE_OVERVIEW_PATTERNS = compile_all(
    [
        # "What is X" / "What does X do"
        r"\bwhat\s+is\s+",
        r"\bwhat\s+does\s+\S+\s+do\b",
        # "Describe X" / "Explain X" / "Tell me about X"
        r"\bdescribe\s+",
        r"\bexplain\s+",
        r"\btell\s+me\s+about\s+",
        # "What classes are in X" / "What methods does X have"
        r"\bwhat\s+classes\s+",
        r"\bwhat\s+methods\s+",
        r"\bwhat\s+fields\s+",
        r"\bwhat\s+properties\s+",
        # "Overview of X" / "Summary of X" / "Structure of X"
        r"\boverview\s+of\s+",
        r"\bsummary\s+of\s+",
        r"\bstructure\s+of\s+",
        r"\bclass\s+overview\b",
        # "How does X work"
        r"\bhow\s+does\s+\S+\s+work\b",
        # "What does the X look like"
        r"\bwhat\s+does\s+the\s+.+\s+look\s+like\b",
        # "Show me the structure/overview/summary of X"
        r"\bshow\s+me\s+the\s+structure\b",
        r"\bshow\s+me\s+the\s+overview\b",
        r"\bshow\s+me\s+the\s+summary\b",
        # "What does X import / use" -- dependency overview
        r"\bwhat\s+does\s+\S+\s+import\b",
        r"\bwhat\s+does\s+\S+\s+use\b",
        # "I need to add/modify/change X" -- implies wanting to see structure first
        r"\bI\s+need\s+to\s+(?:add|modify|change|update|extend)\b",
        # "I need/want to understand X" -- explicit overview request
        r"\b(?:I\s+need|I\s+want)\s+to\s+understand\b",
        # "What are the main classes/modules" -- structural overview
        r"\bwhat\s+are\s+the\s+main\b",
        # "List the methods/classes/fields"
        r"\blist\s+the\s+(?:methods|classes|fields|properties)\b",
    ]
)

# ────────────────────────────────────────────────────────────────────
# Core chunk types (emitted by many readers)
# ────────────────────────────────────────────────────────────────────

# Primary overview types -- the chunks that best answer "What is X?"
PRIMARY_OVERVIEW_TYPES = frozenset({"class_overview", "class_summary", "class_summary_split"})

# Comment chunks: match keywords well but are rarely the answer to an
# overview query; penalized when they come from a non-target file.
COMMENT_TYPES = frozenset({"comment", "comment_split", "block_comment"})

# Generic detail and import chunk types (profiles add their own).
CORE_DETAIL_TYPES = frozenset({"method_group", "method_group_split"})
CORE_IMPORT_TYPES = frozenset({"import_group"})


# ────────────────────────────────────────────────────────────────────
# Active profile set
# ────────────────────────────────────────────────────────────────────


def _unique_patterns(patterns: Iterable) -> Tuple:
    seen = set()
    out = []
    for p in patterns:
        key = (p.pattern, p.flags)
        if key not in seen:
            seen.add(key)
            out.append(p)
    return tuple(out)


class ProfileSet:
    """The merged view of the rerank profiles active for one index."""

    def __init__(self, profiles: Sequence[RerankProfile]):
        uniq: Dict[str, RerankProfile] = {}
        for p in profiles:
            uniq.setdefault(p.name, p)
        self.profiles: Tuple[RerankProfile, ...] = tuple(uniq.values())
        self.names: Tuple[str, ...] = tuple(uniq)

        ps = self.profiles
        self.overview_query_patterns = _unique_patterns(
            list(_CORE_OVERVIEW_PATTERNS) + [x for p in ps for x in p.overview_query_patterns]
        )
        self.target_patterns = _unique_patterns(x for p in ps for x in p.target_patterns)
        self.secondary_overview_types = frozenset().union(*(p.overview_types for p in ps))
        self.artifact_overview_types = frozenset().union(
            *(p.artifact_overview_types for p in ps)
        )
        self.detail_types = CORE_DETAIL_TYPES.union(*(p.detail_types for p in ps))
        self.import_types = CORE_IMPORT_TYPES.union(*(p.import_types for p in ps))
        self.class_target_predicates = tuple(
            p.targets_code_class for p in ps if p.targets_code_class is not None
        )

        merged: Dict[str, QueryDomain] = {}
        for p in ps:
            for d in p.domains:
                if d.name in merged:
                    m = merged[d.name]
                    d = QueryDomain(
                        name=d.name,
                        priority=min(m.priority, d.priority),
                        patterns=_unique_patterns(list(m.patterns) + list(d.patterns)),
                        primary_types=m.primary_types | d.primary_types,
                    )
                merged[d.name] = d
        # Ordered by priority: the first matching domain wins.
        self.domains: Dict[str, QueryDomain] = dict(
            sorted(merged.items(), key=lambda kv: (kv[1].priority, kv[0]))
        )
        domain_primary = frozenset().union(*(d.primary_types for d in self.domains.values()))

        # Every chunk type that counts as an overview of something.
        self.overview_types = (
            PRIMARY_OVERVIEW_TYPES
            | self.secondary_overview_types
            | self.artifact_overview_types
            | domain_primary
        )

    def __repr__(self) -> str:
        return f"ProfileSet({', '.join(self.names)})"


ProfilesArg = Union[None, ProfileSet, Sequence[RerankProfile]]

_ALL_PROFILE_SET: Optional[ProfileSet] = None


def all_profiles() -> Tuple[RerankProfile, ...]:
    """Every rerank profile registered with a reader in READER_REGISTRY."""
    from shared.readers import all_rerank_profiles

    return tuple(all_rerank_profiles())


def get_profile_set(profiles: ProfilesArg = None) -> ProfileSet:
    """Normalise a ``profiles`` argument; ``None`` means all registered profiles."""
    global _ALL_PROFILE_SET
    if isinstance(profiles, ProfileSet):
        return profiles
    if profiles is None:
        if _ALL_PROFILE_SET is None:
            _ALL_PROFILE_SET = ProfileSet(all_profiles())
        return _ALL_PROFILE_SET
    return ProfileSet(list(profiles))


def rerank_profiles_for_config(cfg) -> ProfileSet:
    """Select the rerank profiles for a project config.

    ``RERANK_PROFILES`` in the config (a list of profile names, or
    ``"all"``) overrides the selection.  Otherwise the profiles of the
    readers registered for the configured source extensions are used, so
    only languages that are actually indexed influence ranking.  Falls back
    to all profiles when no extension maps to a profile.
    """
    registered = {p.name: p for p in all_profiles()}

    override = getattr(cfg, "RERANK_PROFILES", None)
    if override:
        names = [override] if isinstance(override, str) else list(override)
        if any(str(n).lower() == "all" for n in names):
            return get_profile_set(None)
        unknown = [n for n in names if n not in registered]
        if unknown:
            log(
                f"[rerank] unknown RERANK_PROFILES entries ignored: {unknown}; "
                f"available: {sorted(registered)}"
            )
        return ProfileSet([registered[n] for n in names if n in registered])

    from shared.readers import get_reader

    extensions: List[str] = []
    try:
        import config_loader

        for entry in config_loader.resolve_source_entries(cfg):
            extensions.extend(entry.get("extensions") or [])
    except Exception as exc:  # noqa: BLE001 - config shape varies; fall back below
        log(f"[rerank] could not read source extensions from config: {exc}")
        extensions.extend(getattr(cfg, "EXTENSIONS", None) or [])

    selected: List[RerankProfile] = []
    for ext in extensions:
        ext = str(ext).strip()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = "." + ext
        reader = get_reader(ext)
        profile = getattr(reader, "rerank_profile", None) if reader is not None else None
        if profile is not None and profile not in selected:
            selected.append(profile)

    if not selected:
        return get_profile_set(None)
    return ProfileSet(selected)


# ────────────────────────────────────────────────────────────────────
# Query intent detection
# ────────────────────────────────────────────────────────────────────


def is_overview_query(query: str, profiles: ProfilesArg = None) -> bool:
    """Detect if a query is asking for an overview/summary of a class, file, or module."""
    pset = get_profile_set(profiles)
    return any(p.search(query) for p in pset.overview_query_patterns)


def is_domain_query(domain: str, query: str, profiles: ProfilesArg = None) -> bool:
    """True if the query matches the patterns of the named, active query domain."""
    d = get_profile_set(profiles).domains.get(domain)
    return d is not None and any(p.search(query) for p in d.patterns)


def detect_query_domain(query: str, profiles: ProfilesArg = None) -> Optional[str]:
    """Return the highest-priority active domain the query matches, or None."""
    for name, d in get_profile_set(profiles).domains.items():
        if any(p.search(query) for p in d.patterns):
            return name
    return None


def get_retrieval_top_k(query: str, desired_top_k: int, profiles: ProfilesArg = None) -> int:
    """Return the number of candidates to fetch from the vector store.

    For overview queries, returns ``desired_top_k * OVERFETCH_MULTIPLIER``
    so that the reranker has a larger pool to work with.  For non-overview
    queries, returns ``desired_top_k`` unchanged.
    """
    if is_overview_query(query, profiles):
        return desired_top_k * OVERFETCH_MULTIPLIER
    return desired_top_k


# ────────────────────────────────────────────────────────────────────
# Target identifier extraction
# ────────────────────────────────────────────────────────────────────

# Path-qualified file references (e.g. "Common/Shared/ReportUtils.pas").
_PATH_FILE = re.compile(r"((?:[A-Za-z][A-Za-z0-9_]*/)+[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9]+)?)")

# Bare file/unit stems without extension that the capitalized-word pattern
# below cannot see: lowercase names containing a digit, e.g. "core2",
# "http2", "sha256" ("What classes are in core2?").
_FILE_STEM_NO_EXT = re.compile(r"\b([a-z][a-z_]*[0-9][a-z0-9_]*)\b")

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
        "look",
        "like",
        "show",
        "find",
        "list",
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



def extract_target_identifiers(query: str, profiles: ProfilesArg = None) -> List[str]:
    """Extract likely target class/file/procedure names from a query.

    Returns a list of identifiers that the user is probably asking about,
    lowercased for case-insensitive matching.  Generic rules live here;
    language-specific file-stem and identifier patterns come from the
    active profiles.
    """
    pset = get_profile_set(profiles)
    targets = []

    # Each path component AND the file stem become separate targets so
    # that _chunk_matches_target can score proportional matches.
    for m in _PATH_FILE.finditer(query):
        parts = m.group(1).replace("\\", "/").split("/")
        for part in parts:
            stem = re.sub(r"\.[A-Za-z0-9]+$", "", part)
            if stem and stem.lower() not in _TARGET_STOP_WORDS:
                targets.append(stem.lower())

    # Profile patterns: file stems with extensions, language identifiers.
    for pattern in pset.target_patterns:
        for m in pattern.finditer(query):
            value = m.group(1) if pattern.groups else m.group()
            targets.append(value.lower())

    # Bare lowercase stems with digits (no extension)
    for m in _FILE_STEM_NO_EXT.finditer(query):
        if len(m.group(1)) >= 4:
            targets.append(m.group(1).lower())

    # General capitalized identifiers (PascalCase, ALLCAPS, etc.), e.g.
    # "SFTP" or "BaseDialogForm" when used without a file extension.
    for m in _GENERAL_IDENT.finditer(query):
        word = m.group(1)
        if word.lower() not in _TARGET_STOP_WORDS:
            targets.append(word.lower())

    return list(set(targets))


# ────────────────────────────────────────────────────────────────────
# File-target matching
# ────────────────────────────────────────────────────────────────────


def _chunk_matches_target(meta: dict, targets: List[str]) -> float:
    """Score how well a chunk's metadata matches the extracted target identifiers.

    Returns a float from 0.0 (no match) to 1.0 (all targets match).
    This replaces the old boolean approach so that a chunk matching 3/3
    path components (e.g. ``Common/Shared/ReportUtils``) scores higher than
    one matching only 1/3 (e.g. just ``ReportUtils``).
    """
    if not targets:
        return 0.0  # No target extracted — can't determine relevance

    file_path = (meta.get("file_path") or "").lower()
    class_name = (meta.get("class_name") or "").lower()
    unit_name = (meta.get("unit_name") or "").lower()
    object_name = (meta.get("object_name") or "").lower()

    matched = 0
    for target in targets:
        # Direct class name match
        if class_name and target in class_name:
            matched += 1
            continue
        # Unit name match
        if unit_name and target in unit_name:
            matched += 1
            continue
        # SQL object name match (procedure, function, table, view, trigger)
        if object_name and target in object_name:
            matched += 1
            continue
        # File path match (e.g., "base42" in "base42.classes.pas",
        # or "common" in "Common/Shared/ReportUtils.pas")
        if file_path and target in file_path:
            matched += 1
            continue

    return matched / len(targets)


# ────────────────────────────────────────────────────────────────────
# Score adjustment calculation
# ────────────────────────────────────────────────────────────────────

# Moderate bonus for secondary overview types (procedure headers, uses
# clauses, type aliases, ...).
_OVERVIEW_BONUS = 0.25

# Small bonus for artefact overviews (forms, reports, project files,
# mappings) in standard mode, and for class summaries when a query domain
# makes an artefact the primary answer: informative, not the answer.
_SUPPORTING_OVERVIEW_BONUS = 0.10

# Bonus for the chunks that directly answer the query: class_overview /
# class_summary in standard mode, the domain's primary types in domain mode.
# These chunks often have very low raw hybrid scores (position 30-40) because
# their large size dilutes the dense embedding.
_PRIMARY_OVERVIEW_BONUS = 0.65

# Bonus for chunks whose file matches the query target
_TARGET_MATCH_BONUS = 0.15

# Penalty for comment chunks from non-target files
_CROSS_FILE_COMMENT_PENALTY = 0.30

# Penalty for overview chunks from non-target files (prevents cross-file
# interlopers that win through BM25 saturation), scaled by (1 - match).
_NON_TARGET_OVERVIEW_PENALTY = 0.40

# Penalty for import/include chunks -- they match many BM25 keywords but
# carry almost zero semantic value for overview queries.
_IMPORT_GROUP_PENALTY = 0.25

# Penalty for detail chunks in overview queries (mild, just enough to break ties)
_DETAIL_PENALTY = 0.05

# Penalty for artefact overviews when the query names a code class (an active
# profile's ``targets_code_class`` predicate): a form header is not the
# answer to "What is TOrderForm?" -- the class summary is.
_ARTIFACT_ON_CLASS_QUERY_PENALTY = 0.15


def _compute_rerank_score(
    original_score: float,
    node_type: str,
    meta: dict,
    is_overview: bool,
    domain: Optional[str],
    targets: List[str],
    profiles: ProfilesArg = None,
) -> float:
    """Compute an adjusted score for reranking.

    For overview queries:
      - Standard mode (``domain`` is None): strong boost for primary overview
        types (class_overview, class_summary); moderate boost for secondary
        overview types; small boost for artefact overviews, minus a penalty
        when the query names a code class.
      - Domain mode: the domain's primary types get the strong boost, class
        summaries the small supporting bonus, other overview types the
        moderate one.
      - Boost chunks from the target file/class; penalize overview chunks
        from non-target files; penalize cross-file comments, import lists
        (heavy) and detail chunks (mild).

    For non-overview queries the original score is returned unchanged.
    """
    if not is_overview:
        return original_score

    pset = get_profile_set(profiles)
    score = original_score
    match_score = _chunk_matches_target(meta, targets)

    active_domain = pset.domains.get(domain) if domain else None
    if active_domain is not None:
        if node_type in active_domain.primary_types:
            score += _PRIMARY_OVERVIEW_BONUS
        elif node_type in PRIMARY_OVERVIEW_TYPES:
            score += _SUPPORTING_OVERVIEW_BONUS
        elif node_type in pset.overview_types:
            score += _OVERVIEW_BONUS
    else:
        if node_type in PRIMARY_OVERVIEW_TYPES:
            score += _PRIMARY_OVERVIEW_BONUS
        elif node_type in pset.artifact_overview_types:
            score += _SUPPORTING_OVERVIEW_BONUS
            if any(pred(targets) for pred in pset.class_target_predicates):
                score -= _ARTIFACT_ON_CLASS_QUERY_PENALTY
        elif node_type in pset.overview_types:
            score += _OVERVIEW_BONUS

    # Boost chunks from the target file/class, scaled by match proportion.
    if match_score > 0.0:
        score += _TARGET_MATCH_BONUS * match_score

    # Penalize overview chunks from non-target files, scaled by (1 - match).
    if node_type in pset.overview_types and targets and match_score < 1.0:
        score -= _NON_TARGET_OVERVIEW_PENALTY * (1.0 - match_score)

    # Penalize comment chunks from non-target files
    if node_type in COMMENT_TYPES and targets and match_score == 0.0:
        score -= _CROSS_FILE_COMMENT_PENALTY

    if node_type in pset.import_types:
        score -= _IMPORT_GROUP_PENALTY

    if node_type in pset.detail_types and node_type not in COMMENT_TYPES:
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
    profiles: ProfilesArg = None,
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
        profiles: Active rerank profiles (see ``rerank_profiles_for_config``);
            None activates every registered profile.

    Returns:
        The same list of nodes, re-sorted by adjusted scores and optionally
        trimmed to ``desired_top_k``.  The original score attribute on each
        node is NOT modified -- the reranking is done via sorting only.
    """
    if not nodes:
        return nodes

    pset = get_profile_set(profiles)
    is_overview = is_overview_query(query, pset)
    targets = extract_target_identifiers(query, pset) if is_overview else []
    domain = detect_query_domain(query, pset) if is_overview else None

    if verbose:
        log(
            f"[rerank] overview={is_overview}, domain={domain}, "
            f"profiles={list(pset.names)}, targets={targets}, "
            f"candidates={len(nodes)}, desired_top_k={desired_top_k}"
        )

    if not is_overview:
        if verbose:
            log("[rerank] skipping rerank (not overview query)")
        if desired_top_k is not None:
            return nodes[:desired_top_k]
        return nodes

    scored: List[Tuple[float, int, object]] = []
    for i, n in enumerate(nodes):
        meta = n.node.metadata if hasattr(n, "node") else {}
        node_type = meta.get("node_type", meta.get("type", "text"))
        original_score = n.score if hasattr(n, "score") else 0.0

        adjusted = _compute_rerank_score(
            original_score, node_type, meta, is_overview, domain, targets, pset
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

    if desired_top_k is not None:
        reranked = reranked[:desired_top_k]

    if verbose:
        log(
            f"[rerank] done, returning {len(reranked)} results, "
            f"top node_type={reranked[0].node.metadata.get('node_type', '?')}"
        )

    return reranked
