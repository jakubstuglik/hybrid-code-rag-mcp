"""
shared.validation.models -- Data structures for RAG validation tests.

Pure dataclasses with no external dependencies, plus ``with_language`` which
copies a case onto Polish, English, or the default. Used by all other
validation modules and by per-config validation_tests.yaml definitions.
A test carries either a legacy language-neutral ``query`` or ``query_pl`` /
``query_en``. ``query`` on the case is always the text the runner sends.
"""

from dataclasses import dataclass, replace
from typing import List, Optional, Dict, Any


@dataclass
class PassCriteria:
    """Criteria for evaluating whether a retrieved node matches expectations.

    All fields are optional -- omitted fields are not checked. A node must
    satisfy ALL specified fields to count as a full match.

    Attributes:
        node_types: Acceptable node_type metadata values (None = any).
        file_pattern: Regex to match against file_path metadata.
        text_pattern: Regex to match against chunk text content.
        max_position: Position threshold for PASS (1-indexed, inclusive).
        partial_position: Position threshold for PARTIAL (1-indexed, inclusive).
        class_name_pattern: Regex to match against class_name metadata.
        multi_file: PASS requires matching results from >= 2 distinct files.
    """

    node_types: Optional[List[str]] = None
    file_pattern: Optional[str] = None
    text_pattern: Optional[str] = None
    max_position: int = 3
    partial_position: int = 5
    class_name_pattern: Optional[str] = None
    multi_file: bool = False


@dataclass
class TestCase:
    """A single RAG validation test case.

    Attributes:
        id: Unique identifier (e.g. "T01", "T02").
        category: Category name for grouping (e.g. "Class Overview Queries").
        query: Active query text sent to the RAG retriever. For a bilingual
            test this is the text selected for ``lang``; for a legacy test it
            is the language-neutral ``query`` from YAML.
        description: Human-readable description of what we expect.
        pass_criteria: Criteria for evaluating PASS/PARTIAL/FAIL.
        difficulty: Easy / Medium / Hard -- for reporting only.
        aspect: Dense / Sparse / Hybrid / Reranker -- which subsystem is tested.
        query_class: Optional semantic / exact / mixed label for sub-scores.
            None means unclassified. Absent from suites written before the field
            existed, which keeps their reports unchanged.
        query_pl: Polish query text. None when the test has no Polish wording.
        query_en: English query text. None when the test has no English wording.
        lang: Language the active ``query`` was taken from: ``"pl"``, ``"en"``,
            or None for a legacy language-neutral query.
    """

    id: str
    category: str
    query: str
    description: str
    pass_criteria: PassCriteria
    difficulty: str = "Medium"
    aspect: str = "Hybrid"
    query_class: Optional[str] = None
    query_pl: Optional[str] = None
    query_en: Optional[str] = None
    lang: Optional[str] = None


def with_language(test_case: TestCase, lang: Optional[str] = None) -> TestCase:
    """Return a copy whose active ``query`` is the text for ``lang``.

    A legacy test (no ``query_pl`` and no ``query_en``) keeps its query and
    ``lang`` None for every requested language, including ``"pl"`` and ``"en"``.

    ``lang=None`` selects ``query_en`` when that test has one, otherwise
    ``query_pl``. ``"pl"`` or ``"en"`` selects that text. When a bilingual
    test lacks the requested language, the other language is used and the
    copy's ``lang`` is the language actually used. The original is unchanged.

    Args:
        test_case: Test to copy.
        lang: ``"pl"``, ``"en"``, or None for the default language.

    Returns:
        Copy of ``test_case`` with ``query`` and ``lang`` set.

    Raises:
        ValueError: If ``lang`` is not ``"pl"``, ``"en"``, or None.
    """
    if lang not in (None, "pl", "en"):
        raise ValueError(f"lang must be 'pl', 'en', or None, got {lang!r}")

    polish = test_case.query_pl
    english = test_case.query_en
    if polish is None and english is None:
        return replace(test_case, lang=None)

    if lang is None:
        chosen = "en" if english is not None else "pl"
    elif lang == "pl":
        chosen = "pl" if polish is not None else "en"
    else:
        chosen = "en" if english is not None else "pl"
    text = polish if chosen == "pl" else english
    return replace(test_case, query=text, lang=chosen)


@dataclass
class TestResult:
    """Result of evaluating a single test case against retrieval results.

    Attributes:
        id: Test case ID.
        category: Test category name.
        query: The query that was run.
        result: "PASS", "PARTIAL", or "FAIL".
        match_position: 1-indexed position of the best matching node.
        match_node_type: node_type of the matched node.
        match_file: file_path of the matched node.
        match_score: Retrieval score of the matched node.
        detail: Explanation string for PARTIAL/FAIL results.
        all_nodes: Full list of retrieved node info dicts for audit.
        doc_hint_position: See below (documentation that points to the answer).
    """

    id: str
    category: str
    query: str
    result: str  # PASS / PARTIAL / FAIL
    match_position: Optional[int] = None
    match_node_type: Optional[str] = None
    match_file: Optional[str] = None
    match_score: Optional[float] = None
    detail: Optional[str] = None
    all_nodes: Optional[List[Dict[str, Any]]] = None
    # Position of the first documentation chunk (doc file or comment) in the
    # top-k that names the expected file or symbol; set for non-PASS results
    # only.  Informational: such a hit can still guide an agent to the
    # answer, but it does not change the score.
    doc_hint_position: Optional[int] = None
    # Wall time of the retrieval + rerank call for this test (ms).
    query_ms: Optional[float] = None
    # Per-query hybrid alpha and query shape. Set only when
    # HYBRID_ALPHA_MODE is adaptive and the collection is hybrid.
    # Fixed mode leaves both None so validation JSON is unchanged.
    alpha: Optional[float] = None
    query_shape: Optional[str] = None
    # Diagnostic search (--diag-rank). None means the flag was not used, so
    # JSON omits the keys. When the flag is used, diag_top3_files is a list
    # (possibly empty) and diag_rank is the 1-based full-match rank or None.
    diag_rank: Optional[int] = None
    diag_top3_files: Optional[List[str]] = None
