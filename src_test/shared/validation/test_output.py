"""
Tests for shared/validation/output.py -- Result formatting.

Tests cover:
    - _truncate(): string truncation with ellipsis
    - _get_rating(): score percentage to rating string mapping
    - get_categories(): ordered unique category extraction
    - print_results(): terminal output (smoke test via stdout capture)
    - output_json(): JSON output structure validation
"""

import json
import sys
from io import StringIO

import pytest

import shared.validation.output as output_module
from shared.validation.models import PassCriteria, TestCase, TestResult


# ────────────────────────────────────────────────
# TestTruncate
# ────────────────────────────────────────────────


class TestTruncate:
    """Tests for _truncate() -- string truncation."""

    def test_short_string_unchanged(self):
        """String shorter than max_len is returned unchanged."""
        assert output_module._truncate("Hello", 10) == "Hello"

    def test_exact_length_unchanged(self):
        """String exactly max_len is returned unchanged."""
        assert output_module._truncate("Hello", 5) == "Hello"

    def test_long_string_truncated(self):
        """String longer than max_len is truncated with ellipsis."""
        result = output_module._truncate("Hello World!", 8)
        assert result == "Hello..."
        assert len(result) == 8

    def test_min_length(self):
        """Very short max_len still works (edge case)."""
        result = output_module._truncate("Hello", 3)
        assert result == "..."
        assert len(result) == 3

    def test_empty_string(self):
        """Empty string returned unchanged."""
        assert output_module._truncate("", 10) == ""


# ────────────────────────────────────────────────
# TestGetRating
# ────────────────────────────────────────────────


class TestGetRating:
    """Tests for _get_rating() -- percentage to rating mapping."""

    def test_outstanding(self):
        assert output_module._get_rating(95.0) == "Outstanding"
        assert output_module._get_rating(100.0) == "Outstanding"

    def test_excellent(self):
        assert output_module._get_rating(90.0) == "Excellent"
        assert output_module._get_rating(94.9) == "Excellent"

    def test_good(self):
        assert output_module._get_rating(80.0) == "Good"
        assert output_module._get_rating(89.9) == "Good"

    def test_acceptable(self):
        assert output_module._get_rating(70.0) == "Acceptable"
        assert output_module._get_rating(79.9) == "Acceptable"

    def test_needs_improvement(self):
        assert output_module._get_rating(60.0) == "Needs Improvement"
        assert output_module._get_rating(69.9) == "Needs Improvement"

    def test_poor(self):
        assert output_module._get_rating(0.0) == "Poor"
        assert output_module._get_rating(59.9) == "Poor"


# ────────────────────────────────────────────────
# TestGetCategories
# ────────────────────────────────────────────────


class TestGetCategories:
    """Tests for get_categories() -- ordered unique category list."""

    def _tc(self, id_: str, category: str) -> TestCase:
        return TestCase(
            id=id_,
            category=category,
            query="q",
            description="d",
            pass_criteria=PassCriteria(),
        )

    def test_single_category(self):
        cases = [self._tc("T01", "Cat A"), self._tc("T02", "Cat A")]
        assert output_module.get_categories(cases) == ["Cat A"]

    def test_multiple_categories_ordered(self):
        cases = [
            self._tc("T01", "Cat A"),
            self._tc("T02", "Cat B"),
            self._tc("T03", "Cat A"),
            self._tc("T04", "Cat C"),
        ]
        assert output_module.get_categories(cases) == ["Cat A", "Cat B", "Cat C"]

    def test_empty_list(self):
        assert output_module.get_categories([]) == []

    def test_preserves_first_appearance_order(self):
        """Categories appear in the order of first occurrence."""
        cases = [
            self._tc("T01", "Zebra"),
            self._tc("T02", "Alpha"),
            self._tc("T03", "Zebra"),
        ]
        assert output_module.get_categories(cases) == ["Zebra", "Alpha"]


# ────────────────────────────────────────────────
# TestPrintResults
# ────────────────────────────────────────────────


class TestPrintResults:
    """Smoke tests for print_results() -- captures stdout."""

    def _make_result(
        self, id_: str, result: str, category: str = "Cat A"
    ) -> TestResult:
        return TestResult(
            id=id_,
            category=category,
            query="test query",
            result=result,
            match_position=1 if result == "PASS" else None,
            match_node_type="class_overview" if result == "PASS" else None,
            match_file="Foo.pas" if result == "PASS" else None,
            match_score=0.85 if result == "PASS" else None,
            detail="No match" if result == "FAIL" else None,
            all_nodes=[
                {
                    "position": 1,
                    "node_type": "defProc",
                    "file_path": "x.pas",
                    "score": 0.5,
                }
            ],
        )

    def _make_tc(self, id_: str, category: str = "Cat A") -> TestCase:
        return TestCase(
            id=id_,
            category=category,
            query="test query",
            description="desc",
            pass_criteria=PassCriteria(node_types=["class_overview"]),
        )

    def test_basic_output(self, capsys):
        """print_results produces output with score and rating."""
        results = [self._make_result("T01", "PASS")]
        test_cases = [self._make_tc("T01")]
        output_module.print_results(results, 0.5, "test_config", test_cases)
        captured = capsys.readouterr()
        assert "PASS" in captured.out
        assert "100.0%" in captured.out
        assert "Outstanding" in captured.out

    def test_mixed_results(self, capsys):
        """Output handles PASS + FAIL mix."""
        results = [
            self._make_result("T01", "PASS"),
            self._make_result("T02", "FAIL"),
        ]
        test_cases = [self._make_tc("T01"), self._make_tc("T02")]
        output_module.print_results(results, 0.5, "cfg", test_cases)
        captured = capsys.readouterr()
        assert "1 PASS" in captured.out
        assert "1 FAIL" in captured.out
        assert "50.0%" in captured.out

    def test_fail_shows_detail(self, capsys):
        """FAIL result shows expected criteria and reason."""
        results = [self._make_result("T01", "FAIL")]
        test_cases = [self._make_tc("T01")]
        output_module.print_results(results, 0.5, "cfg", test_cases)
        captured = capsys.readouterr()
        assert "Expected:" in captured.out
        assert "class_overview" in captured.out

    def test_verbose_shows_nodes_for_pass(self, capsys):
        """Verbose mode shows node details even for PASS."""
        results = [self._make_result("T01", "PASS")]
        test_cases = [self._make_tc("T01")]
        output_module.print_results(results, 0.5, "cfg", test_cases, verbose=True)
        captured = capsys.readouterr()
        assert "<-- MATCH" in captured.out

    def test_empty_results(self, capsys):
        """Empty results list produces valid output."""
        output_module.print_results([], 0.5, "cfg", [])
        captured = capsys.readouterr()
        assert "0 PASS" in captured.out
        assert "0 FAIL" in captured.out

    def test_category_summary(self, capsys):
        """Category summary section is present."""
        results = [
            self._make_result("T01", "PASS", "Cat A"),
            self._make_result("T02", "FAIL", "Cat B"),
        ]
        test_cases = [
            self._make_tc("T01", "Cat A"),
            self._make_tc("T02", "Cat B"),
        ]
        output_module.print_results(results, 0.5, "cfg", test_cases)
        captured = capsys.readouterr()
        assert "Category Summary:" in captured.out
        assert "Cat A" in captured.out
        assert "Cat B" in captured.out


# ────────────────────────────────────────────────
# TestOutputJson
# ────────────────────────────────────────────────


class TestOutputJson:
    """Tests for output_json() -- JSON structure validation."""

    def _make_result(self, id_: str, result: str) -> TestResult:
        return TestResult(
            id=id_,
            category="Cat",
            query="q",
            result=result,
            match_position=1 if result == "PASS" else None,
            match_node_type="class_overview" if result == "PASS" else None,
            match_file="Foo.pas" if result == "PASS" else None,
            match_score=0.85 if result == "PASS" else None,
            detail="No match" if result == "FAIL" else None,
            all_nodes=[
                {"position": 1, "node_type": "x", "file_path": "y", "score": 0.5}
            ],
        )

    def _make_tc(self, id_: str) -> TestCase:
        return TestCase(
            id=id_,
            category="Cat",
            query="q",
            description="d",
            pass_criteria=PassCriteria(
                node_types=["class_overview"],
                file_pattern=r"Foo\.pas$",
                max_position=3,
            ),
            difficulty="Medium",
            aspect="Hybrid",
        )

    def test_json_structure(self, capsys):
        """JSON output has correct top-level structure."""
        results = [self._make_result("T01", "PASS")]
        test_cases = [self._make_tc("T01")]
        output_module.output_json(results, 0.5, "cfg", test_cases)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["alpha"] == 0.5
        assert data["config"] == "cfg"
        assert data["total_tests"] == 1
        assert data["pass_count"] == 1
        assert data["partial_count"] == 0
        assert data["fail_count"] == 0
        assert data["score"] == 2
        assert data["max_score"] == 2
        assert data["score_pct"] == 100.0
        assert data["rating"] == "Outstanding"
        assert len(data["tests"]) == 1

    def test_json_test_entry(self, capsys):
        """Individual test entry has expected fields."""
        results = [self._make_result("T01", "PASS")]
        test_cases = [self._make_tc("T01")]
        output_module.output_json(results, 0.5, "cfg", test_cases)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        test_entry = data["tests"][0]
        assert test_entry["id"] == "T01"
        assert test_entry["result"] == "PASS"
        assert test_entry["match_position"] == 1
        assert "criteria" in test_entry
        assert test_entry["criteria"]["node_types"] == ["class_overview"]
        assert test_entry["description"] == "d"
        assert test_entry["difficulty"] == "Medium"

    def test_json_fail_includes_detail(self, capsys):
        """FAIL result includes detail in JSON."""
        results = [self._make_result("T01", "FAIL")]
        test_cases = [self._make_tc("T01")]
        output_module.output_json(results, 0.5, "cfg", test_cases)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["tests"][0]["detail"] == "No match"

    def test_json_mixed_results(self, capsys):
        """Mixed PASS/FAIL results produce correct counts."""
        results = [
            self._make_result("T01", "PASS"),
            self._make_result("T02", "FAIL"),
        ]
        test_cases = [self._make_tc("T01"), self._make_tc("T02")]
        output_module.output_json(results, 0.5, "cfg", test_cases)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["pass_count"] == 1
        assert data["fail_count"] == 1
        assert data["score_pct"] == 50.0
        assert data["rating"] == "Poor"

    def test_json_empty_results(self, capsys):
        """Empty results produce valid JSON with zero counts."""
        output_module.output_json([], 0.5, "cfg", [])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["total_tests"] == 0
        assert data["score_pct"] == 0.0
        assert data["tests"] == []
