"""
shared/reranker.py -- Post-retrieval reranking for hybrid search results.

Detects query intent (overview vs keyword) and adjusts result ordering
to promote structurally appropriate chunk types. This fixes the BM25
saturation problem where every chunk from a class gets the same 0.50
score because they all contain the class name in their context prefix.

The structural (chunk-type) arithmetic only activates for "overview"
queries like "What is TdmOrders?" or "What classes are in base42?".
For other queries the original order is kept unless one of the query-intent
rules below fires:

    - code-shaped identifiers in the query (``snake_case``, ``camelCase``,
      ``PascalCase`` with two or more humps, ``Owner::member``,
      ``Owner.member``, ``obj->member``) promote chunks that *declare* that
      name (reader metadata, profile ``declaration_name_patterns`` and
      generic ``def`` / ``function`` / ``name(`` signature rules); a matching
      owner adds a small extra bonus;
    - test files (core ``tests/`` rule + profile ``test_path_patterns``) are
      demoted unless the query mentions tests;
    - binding / glue-layer chunks (profile ``binding_path_patterns`` /
      ``binding_text_patterns``) are demoted unless the query asks about
      bindings, wrappers or a C API;
    - declaration-only chunks (profile ``is_declaration_chunk``) are demoted
      unless the query asks for declarations / headers.

In overview queries an exact class-name match additionally beats a class
whose name merely contains the target.

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
from dataclasses import dataclass
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
        self._profile_by_ext: Dict[str, Optional[RerankProfile]] = {}

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

    def profile_for_path(self, path: str) -> Optional[RerankProfile]:
        """The active profile of the reader that handles *path* (by extension)."""
        m = re.search(r"(\.[A-Za-z0-9_+-]+)$", path or "")
        ext = m.group(1).lower() if m else ""
        if ext in self._profile_by_ext:
            return self._profile_by_ext[ext]
        profile = None
        if ext:
            try:
                from shared.readers import get_reader

                reader = get_reader(ext)
                candidate = getattr(reader, "rerank_profile", None) if reader is not None else None
                if candidate is not None and candidate.name in self.names:
                    profile = candidate
            except Exception:  # noqa: BLE001 - registry import issues must not break ranking
                profile = None
        self._profile_by_ext[ext] = profile
        return profile

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

    # Code-shaped identifiers the capitalised pattern cannot see: camelCase,
    # snake_case and both parts of Owner::member ("scrapeLoop",
    # "get_or_create", "Str::slug").
    for owner, name in extract_code_identifiers(query):
        if owner:
            targets.append(owner)
        targets.append(name)

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
# Code identifiers, declared names and query intents (all queries)
# ────────────────────────────────────────────────────────────────────

# File extensions that must not be read as the member part of ``Owner.member``
# ("scrape.go", "Startup.cs").
_FILE_EXTENSIONS = frozenset(
    "py pyi cs go php ts tsx js jsx mjs cjs mts cts cc cpp cxx h hh hpp hxx c "
    "java kt kts groovy gradle pas dpr dpk dfm fmx fr3 sql xml yaml yml json md "
    "txt ini cfg toml rb rs swift scala vue html css scss".split()
)

# ``Owner::member`` / ``Owner->member`` / ``Owner.member``.
_QUALIFIED_IDENT = re.compile(
    r"(?<![\w$])([A-Za-z_$][\w$]*)\s*(::|->|\.)\s*(~?[A-Za-z_$][\w$]*)(?![\w$])"
)
# snake_case / SCREAMING_SNAKE: get_or_create, BCRYPT_ROUNDS, _detect_changes
_SNAKE_IDENT = re.compile(r"(?<![\w$])(_?[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+)(?![\w$])")
# camelCase starting lowercase: chunkById, getUserForJWT
_CAMEL_IDENT = re.compile(r"(?<![\w$])([a-z][a-z0-9]*[A-Z][A-Za-z0-9]*)(?![\w$])")
# PascalCase with at least two humps: IsTrivialMove, DocumentsStore
_PASCAL_IDENT = re.compile(r"(?<![\w$])([A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+)(?![\w$])")


def extract_code_identifiers(
    query: str, keep_case: bool = False
) -> List[Tuple[Optional[str], str]]:
    """Extract identifiers that look like code from a query.

    Returns ``(owner, name)`` pairs, lowercased unless ``keep_case``; ``owner`` is set for
    qualified names (``Compaction::IsTrivialMove`` -> ``("compaction",
    "istrivialmove")``) and None otherwise.  Plain English words never
    qualify: an identifier needs an underscore, an internal capital letter
    or a qualifier.
    """
    found: List[Tuple[Optional[str], str]] = []
    consumed = []
    for m in _QUALIFIED_IDENT.finditer(query):
        owner, sep, member = m.group(1), m.group(2), m.group(3)
        if sep == "." and (member.lower() in _FILE_EXTENSIONS or len(owner) < 2 or len(member) < 2):
            continue
        member = member.lstrip("~")
        found.append((owner, member) if keep_case else (owner.lower(), member.lower()))
        consumed.append(m.span())

    def _free(span: Tuple[int, int]) -> bool:
        return not any(a <= span[0] < b for a, b in consumed)

    for pattern in (_SNAKE_IDENT, _CAMEL_IDENT, _PASCAL_IDENT):
        for m in pattern.finditer(query):
            if _free(m.span(1)):
                name = m.group(1)
                found.append((None, name if keep_case else name.lower()))
    seen = set()
    out = []
    for item in found:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


# Leading lines of a chunk that are not code: context headers written by the
# readers ("// File: x", "# Module: y", "// Class: z"), comments, decorators.
_HEADER_LINE = re.compile(r"^\s*(?://|#|--)\s*[A-Za-z][A-Za-z ]{0,24}:\s")
_COMMENT_LINE = re.compile(r"^\s*(?://|#(?!\[)|/\*|\*|--|\(\*|\{\s*[^}]*\}\s*$)")
_DECORATOR_LINE = re.compile(r"^\s*(?:@[\w.$]+|#\[|\[[A-Z][\w.]*(?:\(.*\))?\]\s*$)")

# Generic declaration forms understood by the core.
_DECL_KEYWORD = re.compile(
    r"\b(?:def|function|func|fn|class|interface|struct|enum|trait|record|type|"
    r"procedure|sub|module|namespace|object|union|typedef)\s+"
    r"([A-Za-z_$][\w$]*)(?:\s*(?:::|\.)\s*(~?[A-Za-z_$][\w$]*))?"
)
_SIGNATURE = re.compile(
    r"(?<![\w$])([A-Za-z_$][\w$]*)(?:\s*(?:::|\.)\s*(~?[A-Za-z_$][\w$]*))?\s*(?:<[^<>()]*>)?\s*\("
)
_NOT_DECLARED_NAMES = frozenset(
    "if for while switch catch return new sizeof typeof await async super this "
    "foreach using lock fixed elif with assert print func function def fn class "
    "struct enum interface record type procedure sub decltype static_assert "
    "alignof noexcept operator template explicit constexpr inline virtual static "
    "public private protected internal final override abstract export default "
    "const let var void int bool char long short double float unsigned signed "
    "auto string throw throws when match case do else try finally yield lambda "
    "macro define defined include import from require".split()
)

_DECLARED_NAME_META_KEYS = ("object_name", "function_name", "method_name", "symbol_name")


def _strip_owner(name: str) -> str:
    """``Foo<T>`` / ``*Foo`` / ``Outer > Inner`` / ``ns::Foo`` -> ``foo``."""
    name = re.sub(r"<.*", "", name or "")
    name = re.split(r"\s*>\s*|::|\.", name)[-1] if name else ""
    return name.strip().lstrip("*&").lower()


def _first_code_lines(text: str, limit: int = 2) -> List[str]:
    lines: List[str] = []
    in_block = False
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if in_block:
            if "*/" in line:
                in_block = False
            continue
        if line.startswith("/*") and "*/" not in line:
            in_block = True
            continue
        if _HEADER_LINE.match(line) or _COMMENT_LINE.match(line) or _DECORATOR_LINE.match(line):
            continue
        lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def chunk_declared_names(
    meta: dict, text: str, profiles: ProfilesArg = None
) -> Tuple[frozenset, frozenset]:
    """Names a chunk declares, lowercased.

    Returns ``(names, qualified)`` where ``qualified`` holds ``(owner,
    name)`` pairs for ``Owner::name`` style definitions.  Sources: reader
    metadata (``object_name``, ``function_name``, ...), the
    ``declaration_name_patterns`` of the profile that owns the chunk's file
    (by extension) and the generic keyword / ``name(`` signature rules,
    applied to the first code lines of the chunk.
    """
    pset = get_profile_set(profiles)
    profile = pset.profile_for_path(_norm_path(meta))
    names = set()
    qualified = set()
    for key in _DECLARED_NAME_META_KEYS:
        value = meta.get(key)
        if value:
            names.add(_strip_owner(str(value)))
    code = _first_code_lines(text)
    if code:
        first = code[0]
        own = list(profile.declaration_name_patterns) if profile is not None else []
        patterns = own + [_DECL_KEYWORD]
        for pat in patterns:
            for m in pat.finditer(first):
                g1 = m.group(1)
                g2 = m.group(2) if (m.re.groups or 0) >= 2 else None
                if g2:
                    qualified.add((_strip_owner(g1), g2.lstrip("~").lower()))
                    names.add(g2.lstrip("~").lower())
                elif g1 and g1.lower() not in _NOT_DECLARED_NAMES:
                    names.add(g1.lower())
        # Generic "name(" signature: only the first candidate, and not for
        # assignments / calls on the right-hand side of '='.
        for m in _SIGNATURE.finditer(first):
            head = first[: m.start()]
            if "=" in head.replace("==", "") or re.search(r"\breturn\b", head):
                break
            g1, g2 = m.group(1), m.group(2)
            if g2:
                qualified.add((_strip_owner(g1), g2.lstrip("~").lower()))
                names.add(g2.lstrip("~").lower())
                break
            if g1.lower() in _NOT_DECLARED_NAMES:
                continue
            names.add(g1.lower())
            break
    names.discard("")
    return frozenset(names), frozenset(qualified)


# Queries that ask about tests / bindings / declarations switch the matching
# demotion off.
_TEST_QUERY = re.compile(
    r"\b(?:tests?|testing|tested|unit[- ]?tests?|specs?|fixtures?|mocks?|stubs?|"
    r"assert\w*|pytest|junit|phpunit|xunit|nunit|gtest|test_\w+|\w+_test)\b"
    r"|[a-z0-9]Tests?\b",
)
_BINDING_QUERY = re.compile(
    r"\b(?:jni|java|c\s+api|capi|ffi|bindings?|wrappers?|extern\s+\"?c\"?)\b", re.IGNORECASE
)
_DECLARATION_QUERY = re.compile(
    r"\b(?:declar\w*|headers?|prototypes?|signatures?|interfaces?|abstract|forward)\b",
    re.IGNORECASE,
)

# Generic test locations (every language); profiles add their own.
_CORE_TEST_PATHS = compile_all([r"(?:^|/)(?:tests|__tests__|__mocks__)/"])


def query_mentions_tests(query: str) -> bool:
    return bool(_TEST_QUERY.search(query or "")) or bool(
        re.search(r"\btests?\b", query or "", re.IGNORECASE)
    )


def _norm_path(meta: dict) -> str:
    return (meta.get("file_path") or "").replace("\\", "/")


def _is_test_path(path: str, profile: Optional[RerankProfile]) -> bool:
    if not path:
        return False
    if any(p.search(path) for p in _CORE_TEST_PATHS):
        return True
    return profile is not None and any(p.search(path) for p in profile.test_path_patterns)


def _is_binding_chunk(path: str, text: str, profile: Optional[RerankProfile]) -> bool:
    if profile is None:
        return False
    if any(p.search(path) for p in profile.binding_path_patterns):
        return True
    return bool(text) and any(p.search(text) for p in profile.binding_text_patterns)


# Score adjustments outside the overview arithmetic.
_DECLARED_NAME_BONUS = 0.25   # chunk declares the identifier the query names
_QUALIFIED_OWNER_BONUS = 0.10  # ... and its owner matches Owner::name too
_TEST_FILE_PENALTY = 0.15      # test code when the query is not about tests
_BINDING_PENALTY = 0.15        # glue layers when the query is not about bindings
_DECLARATION_PENALTY = 0.10    # declaration-only chunks in non-overview queries
_EXACT_CLASS_BONUS = 0.20      # overview chunk of exactly the named class
_PARTIAL_CLASS_PENALTY = 0.10  # overview chunk whose class only contains it


class QueryIntent:
    """Per-query facts shared by every candidate (computed once)."""

    def __init__(self, query: str, pset: "ProfileSet", is_overview: bool):
        self.is_overview = is_overview
        self.code_idents = extract_code_identifiers(query)
        self.wants_tests = query_mentions_tests(query)
        self.wants_bindings = bool(_BINDING_QUERY.search(query or ""))
        self.wants_declarations = bool(_DECLARATION_QUERY.search(query or ""))
        self.pset = pset


def _intent_adjustment(meta: dict, text: str, node_type: str, intent: QueryIntent) -> float:
    """Adjustments that apply to overview and non-overview queries alike
    (test / binding demotion) plus the non-overview identifier and
    declaration rules."""
    pset = intent.pset
    path = _norm_path(meta)
    profile = pset.profile_for_path(path)
    delta = 0.0

    if not intent.wants_tests and _is_test_path(path, profile):
        delta -= _TEST_FILE_PENALTY

    if not intent.wants_bindings and _is_binding_chunk(path, text, profile):
        delta -= _BINDING_PENALTY

    if not intent.is_overview:
        if intent.code_idents:
            names, qualified = chunk_declared_names(meta, text, pset)
            class_name = _strip_owner(meta.get("class_name") or "")
            best = 0.0
            for owner, name in intent.code_idents:
                if name not in names:
                    continue
                bonus = _DECLARED_NAME_BONUS
                if owner is not None and (
                    (owner, name) in qualified or owner == class_name
                ):
                    bonus += _QUALIFIED_OWNER_BONUS
                best = max(best, bonus)
            delta += best
        if (
            not intent.wants_declarations
            and profile is not None
            and profile.is_declaration_chunk is not None
            and profile.is_declaration_chunk(node_type, path)
        ):
            delta -= _DECLARATION_PENALTY
    return delta


def _exact_class_adjustment(meta: dict, node_type: str, targets: List[str], pset: "ProfileSet") -> float:
    """Overview queries: the summary of exactly the named class beats summaries
    of classes whose names merely contain it (``Engine`` vs ``EngineOpts``)."""
    if not targets or node_type not in pset.overview_types:
        return 0.0
    cls = _strip_owner(meta.get("class_name") or "")
    if not cls:
        return 0.0
    if cls in targets:
        return _EXACT_CLASS_BONUS
    if any(len(t) >= 3 and t in cls for t in targets):
        return -_PARTIAL_CLASS_PENALTY
    return 0.0


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


def _node_text(n) -> str:
    """Chunk text of a NodeWithScore, or '' for objects without text."""
    node = getattr(n, "node", None)
    if node is None:
        return ""
    text = getattr(node, "text", None)
    if isinstance(text, str):
        return text
    get_content = getattr(node, "get_content", None)
    if callable(get_content):
        try:
            value = get_content()
            return value if isinstance(value, str) else ""
        except Exception:  # noqa: BLE001
            return ""
    return ""


# ────────────────────────────────────────────────────────────────────
# Pool-level options (configurable, off by default)
# ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RerankOptions:
    """Optional pool-level rules, set from config by ``rerank_options_for_config``.

    Attributes:
        core_mention_penalty: Demotion for any chunk that mentions an
            identifier the query names while another candidate declares it
            (``RERANK_CORE_MENTION_PENALTY``; 0 = off).
        profile_mention: Apply the per-language ``mention_penalty`` of the
            chunk's profile (``RERANK_PROFILE_MENTION``).
        type_intent: Apply the profiles' ``type_intent_rules``
            (``RERANK_TYPE_INTENT``).
        file_cap: When the query asks about several places (``A and B``,
            ``both``, ``across`` ...), at most this many results per file
            keep their rank; the rest move behind the other candidates
            (``RERANK_FILE_CAP``; 0 = off).
        deprioritized_paths: Path globs (``fnmatch``, ``/`` separators) of
            code that is rarely the answer (vendored copies, tooling, samples);
            matching chunks lose ``deprioritized_penalty`` unless the query
            names a part of the glob (``DEPRIORITIZED_PATHS``).
        prototype_yield: Extra demotion for a declaration-only chunk
            (prototype) when a candidate with a body declares the same
            identifier the query names (``RERANK_PROTOTYPE_YIELD``; 0 = off).
    """

    core_mention_penalty: float = 0.0
    profile_mention: bool = False
    type_intent: bool = False
    file_cap: int = 0
    deprioritized_paths: Tuple[str, ...] = ()
    deprioritized_penalty: float = 0.10
    prototype_yield: float = 0.0

    @property
    def active(self) -> bool:
        return bool(
            self.core_mention_penalty
            or self.profile_mention
            or self.type_intent
            or self.file_cap
            or self.deprioritized_paths
            or self.prototype_yield
        )


def rerank_options_for_config(cfg) -> RerankOptions:
    """Read the pool-level rerank options from a config module."""
    if cfg is None:
        return RerankOptions()
    return RerankOptions(
        core_mention_penalty=float(getattr(cfg, "RERANK_CORE_MENTION_PENALTY", 0.0) or 0.0),
        profile_mention=bool(getattr(cfg, "RERANK_PROFILE_MENTION", False)),
        type_intent=bool(getattr(cfg, "RERANK_TYPE_INTENT", False)),
        file_cap=int(getattr(cfg, "RERANK_FILE_CAP", 0) or 0),
        deprioritized_paths=tuple(getattr(cfg, "DEPRIORITIZED_PATHS", ()) or ()),
        deprioritized_penalty=float(getattr(cfg, "DEPRIORITIZED_PATH_PENALTY", 0.10)),
        prototype_yield=float(getattr(cfg, "RERANK_PROTOTYPE_YIELD", 0.0) or 0.0),
    )


# Queries that ask about more than one place.
_MULTI_PLACE_QUERY = re.compile(
    r"\b(?:and|both|versus|vs|across|between|each|implementations|callers|"
    r"everywhere|all\s+(?:places|callers|users|implementations))\b",
    re.IGNORECASE,
)


def _glob_words(glob: str) -> List[str]:
    return [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", glob)]


def _path_deprioritized(path: str, query: str, globs: Tuple[str, ...]) -> bool:
    import fnmatch

    q = (query or "").lower()
    for g in globs:
        if fnmatch.fnmatchcase(path, g):
            if any(re.search(r"\b" + re.escape(w) + r"\b", q) for w in _glob_words(g)):
                return False
            return True
    return False


def _mentions(text: str, name: str) -> bool:
    return bool(re.search(r"(?<![\w$])" + re.escape(name) + r"(?![\w$])", text or "", re.IGNORECASE))


def _pool_adjustments(
    items: list, query: str, pset: "ProfileSet", intent: "QueryIntent", options: RerankOptions
) -> List[float]:
    """Deltas from the pool-level options for ``items`` = [(meta, text, node_type)]."""
    deltas = [0.0] * len(items)
    if not options.active:
        return deltas
    paths = [_norm_path(m) for m, _, _ in items]
    profiles = [pset.profile_for_path(p) for p in paths]

    if options.type_intent:
        for i, (meta, text, node_type) in enumerate(items):
            prof = profiles[i]
            if prof is None:
                continue
            best = 0.0
            for pattern, types, bonus in prof.type_intent_rules:
                if node_type in types and pattern.search(query or ""):
                    best = max(best, bonus)
            deltas[i] += best

    if options.deprioritized_paths:
        for i, path in enumerate(paths):
            if _path_deprioritized(path, query, options.deprioritized_paths):
                deltas[i] -= options.deprioritized_penalty

    wants_mention = options.core_mention_penalty or options.profile_mention
    if (wants_mention or options.prototype_yield) and intent.code_idents and not intent.is_overview:
        idents = {name for _, name in intent.code_idents}
        declared = []
        for meta, text, _ in items:
            names, _q = chunk_declared_names(meta, text, pset)
            declared.append(names & idents)
        declared_any = set().union(*declared) if declared else set()
        body_declared = set()
        decl_flags = []
        for i, (meta, text, node_type) in enumerate(items):
            prof = profiles[i]
            is_decl = bool(
                prof is not None
                and prof.is_declaration_chunk is not None
                and prof.is_declaration_chunk(node_type, paths[i])
            )
            decl_flags.append(is_decl)
            if not is_decl:
                body_declared |= declared[i]
        for i, (meta, text, node_type) in enumerate(items):
            if wants_mention and not declared[i]:
                hit = [n for n in declared_any if _mentions(text, n)]
                if hit:
                    pen = options.core_mention_penalty
                    prof = profiles[i]
                    if options.profile_mention and prof is not None:
                        pen = max(pen, prof.mention_penalty)
                    deltas[i] -= pen
            if (
                options.prototype_yield
                and decl_flags[i]
                and not intent.wants_declarations
                and declared[i] & body_declared
            ):
                deltas[i] -= options.prototype_yield
    return deltas


def _apply_file_cap(ranked: list, cap: int) -> list:
    """Keep at most ``cap`` results per file in rank order; the rest follow."""
    seen: Dict[str, int] = {}
    head, tail = [], []
    for n in ranked:
        meta = n.node.metadata if hasattr(n, "node") else {}
        path = _norm_path(meta or {})
        seen[path] = seen.get(path, 0) + 1
        (head if seen[path] <= cap else tail).append(n)
    return head + tail


def rerank_results(
    nodes: list,
    query: str,
    desired_top_k: Optional[int] = None,
    verbose: bool = False,
    profiles: ProfilesArg = None,
    options: Optional[RerankOptions] = None,
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
        options: Pool-level rules (see ``RerankOptions``); None = all off.

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
    intent = QueryIntent(query, pset, is_overview)

    if verbose:
        log(
            f"[rerank] overview={is_overview}, domain={domain}, "
            f"profiles={list(pset.names)}, targets={targets}, "
            f"code_idents={intent.code_idents}, wants_tests={intent.wants_tests}, "
            f"candidates={len(nodes)}, desired_top_k={desired_top_k}"
        )

    options = options or RerankOptions()
    pool_items = []
    if options.active:
        for n in nodes:
            meta = (n.node.metadata if hasattr(n, "node") else {}) or {}
            pool_items.append((meta, _node_text(n), meta.get("node_type", meta.get("type", "text"))))
    pool_deltas = _pool_adjustments(pool_items, query, pset, intent, options) if options.active else [0.0] * len(nodes)

    scored: List[Tuple[float, int, object]] = []
    changed = False
    for i, n in enumerate(nodes):
        meta = n.node.metadata if hasattr(n, "node") else {}
        meta = meta or {}
        node_type = meta.get("node_type", meta.get("type", "text"))
        original_score = n.score if hasattr(n, "score") else 0.0
        original_score = original_score or 0.0
        text = _node_text(n)

        adjusted = _compute_rerank_score(
            original_score, node_type, meta, is_overview, domain, targets, pset
        )
        if is_overview and domain is None:
            adjusted += _exact_class_adjustment(meta, node_type, targets, pset)
        adjusted += _intent_adjustment(meta, text, node_type, intent)
        adjusted += pool_deltas[i]
        if adjusted != original_score:
            changed = True

        if verbose and adjusted != original_score:
            file_path = meta.get("file_path", "?")
            log(
                f"[rerank] {node_type:30s} {file_path:40s} "
                f"score {original_score:.4f} -> {adjusted:.4f} "
                f"(delta={adjusted - original_score:+.4f})"
            )

        scored.append((adjusted, i, n))

    multi_place = bool(options.file_cap) and bool(_MULTI_PLACE_QUERY.search(query or ""))

    if not is_overview and not changed and not multi_place:
        if verbose:
            log("[rerank] skipping rerank (not overview query, no intent signal)")
        if desired_top_k is not None:
            return nodes[:desired_top_k]
        return nodes

    # Sort by adjusted score descending, then by original position (stable)
    scored.sort(key=lambda x: (-x[0], x[1]))
    reranked = [item[2] for item in scored]
    if multi_place:
        reranked = _apply_file_cap(reranked, options.file_cap)

    if desired_top_k is not None:
        reranked = reranked[:desired_top_k]

    if verbose:
        log(
            f"[rerank] done, returning {len(reranked)} results, "
            f"top node_type={reranked[0].node.metadata.get('node_type', '?')}"
        )

    return reranked
