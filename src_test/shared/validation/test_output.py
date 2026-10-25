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
        assert "Query class:" not in captured.out

    def test_query_class_summary_only_when_set(self, capsys):
        """Per-class lines appear only when at least one test has query_class."""
        results = [
            self._make_result("T01", "PASS", "Cat A"),
            self._make_result("T02", "PARTIAL", "Cat A"),
            self._make_result("T03", "FAIL", "Cat A"),
        ]
        test_cases = [
            self._make_tc("T01"),
            self._make_tc("T02"),
            self._make_tc("T03"),
        ]
        test_cases[0].query_class = "semantic"
        test_cases[1].query_class = "semantic"
        test_cases[2].query_class = "exact"
        output_module.print_results(results, 0.5, "cfg", test_cases)
        captured = capsys.readouterr()
        assert "Query class:" in captured.out
        assert "semantic    75.0%" in captured.out
        assert "n=2" in captured.out
        assert "exact" in captured.out
        assert "n=1" in captured.out
        assert "mixed" not in captured.out

    def test_header_unchanged_without_lang(self, capsys):
        """Omitting lang keeps the previous header line."""
        output_module.print_results(
            [self._make_result("T01", "PASS")],
            0.5,
            "cfg",
            [self._make_tc("T01")],
        )
        first = capsys.readouterr().out.splitlines()[0]
        assert first == "RAG Validation: 1 tests, alpha=0.50, index=cfg"

    def test_header_names_the_language(self, capsys):
        """A requested language is printed on the header line."""
        output_module.print_results(
            [self._make_result("T01", "FAIL")],
            0.5,
            "cfg",
            [self._make_tc("T01")],
            lang="pl",
        )
        first = capsys.readouterr().out.splitlines()[0]
        assert first == "RAG Validation: 1 tests, alpha=0.50, index=cfg, lang=pl"


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
        assert "alpha" not in test_entry
        assert "query_shape" not in test_entry

    def test_json_includes_adaptive_fields_when_set(self, capsys):
        """Per-test alpha and query_shape appear only when the runner set them."""
        result = self._make_result("T01", "PASS")
        result.alpha = 0.0
        result.query_shape = "identifier"
        output_module.output_json([result], 0.5, "cfg", [self._make_tc("T01")])
        data = json.loads(capsys.readouterr().out)
        assert data["alpha"] == 0.5
        assert data["tests"][0]["alpha"] == 0.0
        assert data["tests"][0]["query_shape"] == "identifier"

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

    def test_json_omits_new_keys_when_unset(self, capsys):
        """Suites without query_class or diag stay on the previous JSON shape."""
        results = [self._make_result("T01", "PASS")]
        output_module.output_json(results, 0.5, "cfg", [self._make_tc("T01")])
        data = json.loads(capsys.readouterr().out)
        assert "by_query_class" not in data
        assert "query_class" not in data["tests"][0]
        assert "diag_rank" not in data["tests"][0]
        assert "diag_top3_files" not in data["tests"][0]
        assert "lang" not in data
        assert "lang" not in data["tests"][0]

    def test_json_query_class_and_diag(self, capsys):
        """Class sub-scores and diagnostic fields are added only when set."""
        result = self._make_result("T01", "FAIL")
        result.diag_rank = None
        result.diag_top3_files = ["src/A.py", "src/B.py", "src/C.py"]
        tc = self._make_tc("T01")
        tc.query_class = "mixed"
        output_module.output_json([result], 0.5, "cfg", [tc])
        data = json.loads(capsys.readouterr().out)
        assert data["tests"][0]["query_class"] == "mixed"
        assert data["tests"][0]["diag_rank"] is None
        assert data["tests"][0]["diag_top3_files"] == ["src/A.py", "src/B.py", "src/C.py"]
        row = data["by_query_class"]["mixed"]
        assert row["n"] == 1
        assert row["fail_count"] == 1
        assert row["pass_count"] == 0
        assert row["score_pct"] == 0.0
        assert "semantic" not in data["by_query_class"]

    def test_json_omits_lang_unless_requested(self, capsys):
        """Legacy JSON has no lang keys; a requested language adds them."""
        results = [self._make_result("T01", "PASS")]
        cases = [self._make_tc("T01")]
        output_module.output_json(results, 0.5, "cfg", cases)
        data = json.loads(capsys.readouterr().out)
        assert "lang" not in data
        assert "lang" not in data["tests"][0]
        assert list(data.keys())[:2] == ["alpha", "config"]

        cases[0].lang = "en"
        output_module.output_json(results, 0.5, "cfg", cases, lang="en")
        data = json.loads(capsys.readouterr().out)
        assert data["lang"] == "en"
        assert data["tests"][0]["lang"] == "en"
        assert data["tests"][0]["result"] == "PASS"
        assert "by_query_class" not in data


class TestBilingualSummary:
    """Side-by-side score deltas use the same rounded percentages as JSON."""

    def _result(self, id_: str, result: str, category: str, position) -> TestResult:
        return TestResult(
            id=id_,
            category=category,
            query="q",
            result=result,
            match_position=position,
        )

    def _case(self, id_: str, category: str, query_class: str) -> TestCase:
        return TestCase(
            id=id_,
            category=category,
            query="q",
            description="d",
            pass_criteria=PassCriteria(),
            query_class=query_class,
        )

    def test_delta_by_class_and_changed_positions(self, capsys):
        """EN minus PL, per class and per category, plus a position-only change."""
        pl_results = [
            self._result("S1", "PASS", "Uploads", 1),
            self._result("E1", "PASS", "Uploads", 1),
        ]
        en_results = [
            self._result("S1", "FAIL", "Uploads", None),
            self._result("E1", "PASS", "Uploads", 2),
        ]
        cases = [
            self._case("S1", "Uploads", "semantic"),
            self._case("E1", "Uploads", "exact"),
        ]
        delta = output_module.language_delta(pl_results, en_results, cases)
        assert delta["score_pct"] == -50.0
        assert delta["by_query_class"] == {"semantic": -100.0, "exact": 0.0}
        assert delta["by_category"] == {"Uploads": -50.0}
        changed = output_module.changed_tests(pl_results, en_results, cases)
        assert [row["id"] for row in changed] == ["S1", "E1"]
        assert changed[1]["pl_result"] == "PASS"
        assert changed[1]["pl_position"] == 1
        assert changed[1]["en_result"] == "PASS"
        assert changed[1]["en_position"] == 2
        assert changed[1]["query_class"] == "exact"

        output_module.print_bilingual_summary(
            pl_results, en_results, 0.5, "cfg", cases
        )
        text = capsys.readouterr().out
        assert "lang=both" in text
        assert "Overall PL: 100.0% (2 PASS, 0 PARTIAL, 0 FAIL, n=2)" in text
        assert "Overall EN: 50.0% (1 PASS, 0 PARTIAL, 1 FAIL, n=2)" in text
        assert "Delta (EN-PL): -50.0 pp" in text
        assert "semantic n=2" not in text
        assert "semantic n=1" in text
        assert "exact n=1" in text
        assert "S1  semantic  PL PASS@1  EN FAIL@-" in text
        assert "E1  exact  PL PASS@1  EN PASS@2" in text
        assert "Expected:" not in text
