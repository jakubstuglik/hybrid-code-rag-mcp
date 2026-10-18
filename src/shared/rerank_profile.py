"""
shared/rerank_profile.py -- Per-reader rerank profiles.

The reranker core (``shared/reranker.py``) only knows generic concepts:
overview queries, target identifiers, primary overview chunks
(``class_overview`` / ``class_summary``), comments, imports and the score
arithmetic.  Everything that is specific to a language or file format --
which node types are overview or detail chunks, how file names look in a
query, extra phrasings that mean "give me an overview", and query domains
such as "this is about a report / a form / a mapping" -- lives in a
``RerankProfile`` attached to the reader that produces those chunks
(``rerank_profile`` attribute of the reader class, see
``shared/readers/__init__.py``).

Only the profiles of readers that index files in a project are active for
that project's queries (``reranker.rerank_profiles_for_config``), so, for
example, Delphi form rules never fire on a Java-only index.  A project
config can override the selection with ``RERANK_PROFILES``.

This module has no dependencies besides ``re`` so reader modules can import
it cheaply.
"""

import re
from dataclasses import dataclass, field
from typing import Callable, FrozenSet, List, Optional, Pattern, Sequence, Tuple


def compile_all(patterns: Sequence[str], flags: int = re.IGNORECASE) -> Tuple[Pattern, ...]:
    """Compile a list of regex strings (case-insensitive by default)."""
    return tuple(re.compile(p, flags) for p in patterns)


@dataclass(frozen=True)
class QueryDomain:
    """A query intent that makes one family of chunks the primary answer.

    When an overview query matches any of ``patterns``, chunks whose
    ``node_type`` is in ``primary_types`` get the primary overview bonus and
    ordinary class summaries are demoted to supporting context.  If several
    domains match, the one with the lowest ``priority`` wins.  Profiles may
    declare the same domain name (e.g. Delphi and Qt forms both declare
    ``"form"``); active declarations are merged.
    """

    name: str
    priority: int
    patterns: Tuple[Pattern, ...]
    primary_types: FrozenSet[str]


@dataclass(frozen=True)
class RerankProfile:
    """Language/format-specific rerank knowledge contributed by one reader.

    Attributes:
        name: Stable identifier used in ``RERANK_PROFILES`` overrides.
        overview_query_patterns: Extra phrasings that make a query an
            overview query (in addition to the generic core patterns).
        target_patterns: Regexes that pull target identifiers (file stems,
            class names, object names) out of a query.  ``group(1)`` is used
            when the pattern has a group, else the whole match.
        overview_types: Secondary overview chunk types (moderate bonus).
        artifact_overview_types: Overview chunks of non-code artefacts
            (forms, reports, project files, mappings).  In standard mode they
            get only a small bonus, and a penalty when the query names a code
            class (see ``targets_code_class``).
        detail_types: Detail chunk types (mild penalty in overview queries).
        import_types: Import/include list chunk types (heavier penalty).
        domains: Query domains this profile contributes.
        targets_code_class: Optional predicate over the extracted targets:
            True when the query names a code class of this language, which
            demotes artefact overviews (a form header is not the answer to
            "What is TOrderForm?").
        declaration_name_patterns: Regexes applied to the first code lines
            of a chunk that capture the name the chunk declares (a method,
            function, property, constant, ...).  ``group(1)`` is the name; an
            optional ``group(2)`` makes ``group(1)`` the owner and ``group(2)``
            the member (``Owner::member``).  The core adds a generic
            ``name(`` signature rule, so profiles only cover forms it misses.
        test_path_patterns: Regexes over the normalised file path (``/``
            separators) that identify test code of this language.  Matching
            chunks are demoted when the query does not ask about tests.
        binding_path_patterns / binding_text_patterns: Regexes over the
            file path / chunk text that identify thin glue layers (foreign
            language bindings, C API wrappers).  They are demoted unless the
            query asks for bindings.
        is_declaration_chunk: Optional predicate ``(node_type, file_path)``
            that is True for chunks holding only declarations (headers,
            prototypes).  For non-overview queries the implementation is
            preferred over such chunks.
        mention_penalty: Demotion for a chunk of this language that only
            mentions (calls, references) an identifier the query names while
            another candidate declares it.  Applied when the
            ``RERANK_PROFILE_MENTION`` option is on.
        type_intent_rules: ``(query_pattern, node_types, bonus)`` triples:
            when the query matches ``query_pattern`` (e.g. asks for an
            enumeration or flag values), chunks of this language with one of
            ``node_types`` gain ``bonus``.  Applied when the
            ``RERANK_TYPE_INTENT`` option is on.
    """

    name: str
    overview_query_patterns: Tuple[Pattern, ...] = ()
    target_patterns: Tuple[Pattern, ...] = ()
    overview_types: FrozenSet[str] = frozenset()
    artifact_overview_types: FrozenSet[str] = frozenset()
    detail_types: FrozenSet[str] = frozenset()
    import_types: FrozenSet[str] = frozenset()
    domains: Tuple[QueryDomain, ...] = ()
    targets_code_class: Optional[Callable[[List[str]], bool]] = field(
        default=None, compare=False
    )
    declaration_name_patterns: Tuple[Pattern, ...] = ()
    test_path_patterns: Tuple[Pattern, ...] = ()
    binding_path_patterns: Tuple[Pattern, ...] = ()
    binding_text_patterns: Tuple[Pattern, ...] = ()
    is_declaration_chunk: Optional[Callable[[str, str], bool]] = field(
        default=None, compare=False
    )
    mention_penalty: float = 0.0
    type_intent_rules: Tuple[Tuple[Pattern, FrozenSet[str], float], ...] = ()


# Node types shared by every reader that follows the Java chunk conventions
# (Java, Kotlin, Groovy, Python, C#, Go, PHP).  ``class_overview`` /
# ``class_summary`` / ``method_group`` / comments / ``import_group`` are core
# types handled by the reranker itself.
JAVA_STYLE_DETAIL_TYPES = frozenset(
    {
        "method_declaration",
        "method_declaration_split",
        "constructor_declaration",
        "constructor_declaration_split",
        "field_declaration",
        "constant_declaration",
        "enum_constant",
    }
)
JAVA_STYLE_OVERVIEW_TYPES = frozenset({"type_alias_declaration"})


def java_style_profile(
    name: str,
    file_stem_pattern: str,
    test_paths: Sequence[str] = (),
    declaration_names: Sequence[str] = (),
) -> RerankProfile:
    """Profile for a reader that emits the Java chunk conventions."""
    return RerankProfile(
        name=name,
        target_patterns=compile_all([file_stem_pattern]),
        overview_types=JAVA_STYLE_OVERVIEW_TYPES,
        detail_types=JAVA_STYLE_DETAIL_TYPES,
        test_path_patterns=compile_all(test_paths),
        declaration_name_patterns=compile_all(declaration_names, 0),
    )


# Stem pattern for "Name.ext" mentions of the Python/C#/Go/PHP/Groovy
# readers (a leading underscore is allowed for private Python modules).
def simple_stem_pattern(ext_alternation: str) -> str:
    return r"(?<![\w.])([A-Za-z_][A-Za-z0-9_]*)\.(?:" + ext_alternation + r")\b"
