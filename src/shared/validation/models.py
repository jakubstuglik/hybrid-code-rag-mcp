"""
shared.validation.models -- Data structures for RAG validation tests.

Pure dataclasses with no external dependencies. Used by all other validation
modules and by per-config validation_tests.yaml definitions.
"""

from dataclasses import dataclass, field
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
        query: The query text to send to the RAG retriever.
        description: Human-readable description of what we expect.
        pass_criteria: Criteria for evaluating PASS/PARTIAL/FAIL.
        difficulty: Easy / Medium / Hard -- for reporting only.
        aspect: Dense / Sparse / Hybrid / Reranker -- which subsystem is tested.
    """

    id: str
    category: str
    query: str
    description: str
    pass_criteria: PassCriteria
    difficulty: str = "Medium"
    aspect: str = "Hybrid"


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
