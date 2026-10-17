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


def java_style_profile(name: str, file_stem_pattern: str) -> RerankProfile:
    """Profile for a reader that emits the Java chunk conventions."""
    return RerankProfile(
        name=name,
        target_patterns=compile_all([file_stem_pattern]),
        overview_types=JAVA_STYLE_OVERVIEW_TYPES,
        detail_types=JAVA_STYLE_DETAIL_TYPES,
    )


# Stem pattern for "Name.ext" mentions of the Python/C#/Go/PHP/Groovy
# readers (a leading underscore is allowed for private Python modules).
def simple_stem_pattern(ext_alternation: str) -> str:
    return r"(?<![\w.])([A-Za-z_][A-Za-z0-9_]*)\.(?:" + ext_alternation + r")\b"
