"""
Tests for shared/validation/models.py -- PassCriteria, TestCase, TestResult dataclasses.

Tests cover:
    - PassCriteria: default values, custom values, all-None fields
    - TestCase: required fields, default difficulty/aspect
    - TestResult: all fields, optional fields default to None
"""

import pytest

from shared.validation.models import PassCriteria, TestCase, TestResult


# ────────────────────────────────────────────────
# TestPassCriteria
# ────────────────────────────────────────────────


class TestPassCriteria:
    """Tests for PassCriteria dataclass."""

    def test_defaults(self):
        """All optional fields default to None, max_position=3, partial_position=5."""
        c = PassCriteria()
        assert c.node_types is None
        assert c.file_pattern is None
        assert c.text_pattern is None
        assert c.max_position == 3
        assert c.partial_position == 5
        assert c.class_name_pattern is None
        assert c.multi_file is False

    def test_custom_values(self):
        """All fields can be set via constructor."""
        c = PassCriteria(
            node_types=["class_overview", "class_summary"],
            file_pattern=r"MainDM\.pas$",
            text_pattern=r"TdmMain",
            max_position=1,
            partial_position=3,
            class_name_pattern=r"^TdmMain$",
            multi_file=True,
        )
        assert c.node_types == ["class_overview", "class_summary"]
        assert c.file_pattern == r"MainDM\.pas$"
        assert c.text_pattern == r"TdmMain"
        assert c.max_position == 1
        assert c.partial_position == 3
        assert c.class_name_pattern == r"^TdmMain$"
        assert c.multi_file is True

    def test_node_types_empty_list(self):
        """Empty node_types list is different from None (matches nothing)."""
        c = PassCriteria(node_types=[])
        assert c.node_types == []
        assert c.node_types is not None

    def test_single_node_type(self):
        """Single-element node_types list."""
        c = PassCriteria(node_types=["defProc"])
        assert c.node_types == ["defProc"]

    def test_multi_file_default_false(self):
        """multi_file defaults to False."""
        c = PassCriteria()
        assert c.multi_file is False


# ────────────────────────────────────────────────
# TestTestCase
# ────────────────────────────────────────────────


class TestTestCase:
    """Tests for TestCase dataclass."""

    def test_required_fields(self):
        """TestCase stores all required fields."""
        c = PassCriteria(node_types=["class_overview"])
        tc = TestCase(
            id="T01",
            category="Class Overview Queries",
            query="What is TdmMain?",
            description="Should find TdmMain class overview",
            pass_criteria=c,
        )
        assert tc.id == "T01"
        assert tc.category == "Class Overview Queries"
        assert tc.query == "What is TdmMain?"
        assert tc.description == "Should find TdmMain class overview"
        assert tc.pass_criteria is c

    def test_defaults(self):
        """difficulty defaults to 'Medium', aspect defaults to 'Hybrid'."""
        tc = TestCase(
            id="T01",
            category="Cat",
            query="q",
            description="d",
            pass_criteria=PassCriteria(),
        )
        assert tc.difficulty == "Medium"
        assert tc.aspect == "Hybrid"

    def test_custom_difficulty_and_aspect(self):
        """Custom difficulty and aspect can be set."""
        tc = TestCase(
            id="T02",
            category="Cat",
            query="q",
            description="d",
            pass_criteria=PassCriteria(),
            difficulty="Hard",
            aspect="Dense",
        )
        assert tc.difficulty == "Hard"
        assert tc.aspect == "Dense"


# ────────────────────────────────────────────────
# TestTestResult
# ────────────────────────────────────────────────


class TestTestResult:
    """Tests for TestResult dataclass."""

    def test_pass_result(self):
        """PASS result with full match details."""
        r = TestResult(
            id="T01",
            category="Cat",
            query="What is TdmMain?",
            result="PASS",
            match_position=1,
            match_node_type="class_overview",
            match_file="MainDM.pas",
            match_score=0.8534,
        )
        assert r.result == "PASS"
        assert r.match_position == 1
        assert r.match_node_type == "class_overview"
        assert r.match_file == "MainDM.pas"
        assert r.match_score == 0.8534
        assert r.detail is None
        assert r.all_nodes is None

    def test_fail_result(self):
        """FAIL result with detail and all_nodes."""
        nodes = [
            {
                "position": 1,
                "node_type": "defProc",
                "file_path": "other.pas",
                "score": 0.5,
            }
        ]
        r = TestResult(
            id="T02",
            category="Cat",
            query="q",
            result="FAIL",
            detail="No matching nodes found",
            all_nodes=nodes,
        )
        assert r.result == "FAIL"
        assert r.match_position is None
        assert r.match_node_type is None
        assert r.detail == "No matching nodes found"
        assert len(r.all_nodes) == 1

    def test_partial_result(self):
        """PARTIAL result with detail."""
        r = TestResult(
            id="T03",
            category="Cat",
            query="q",
            result="PARTIAL",
            match_position=4,
            match_node_type="defProc",
            match_file="foo.pas",
            match_score=0.3,
            detail="Full match at position 4 (>3)",
        )
        assert r.result == "PARTIAL"
        assert r.match_position == 4
        assert r.detail == "Full match at position 4 (>3)"

    def test_defaults_are_none(self):
        """Optional fields default to None."""
        r = TestResult(id="T01", category="Cat", query="q", result="FAIL")
        assert r.match_position is None
        assert r.match_node_type is None
        assert r.match_file is None
        assert r.match_score is None
        assert r.detail is None
        assert r.all_nodes is None
