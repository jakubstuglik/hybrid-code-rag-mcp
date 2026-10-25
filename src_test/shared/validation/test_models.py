"""
Tests for shared/validation/models.py -- PassCriteria, TestCase, TestResult dataclasses.

Tests cover:
    - PassCriteria: default values, custom values, all-None fields
    - TestCase: required fields, default difficulty/aspect
    - TestResult: all fields, optional fields default to None
"""

import pytest

from shared.validation.models import PassCriteria, TestCase, TestResult, with_language


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
            file_pattern=r"OrdersDM\.pas$",
            text_pattern=r"TdmOrders",
            max_position=1,
            partial_position=3,
            class_name_pattern=r"^TdmOrders$",
            multi_file=True,
        )
        assert c.node_types == ["class_overview", "class_summary"]
        assert c.file_pattern == r"OrdersDM\.pas$"
        assert c.text_pattern == r"TdmOrders"
        assert c.max_position == 1
        assert c.partial_position == 3
        assert c.class_name_pattern == r"^TdmOrders$"
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
            query="What is TdmOrders?",
            description="Should find TdmOrders class overview",
            pass_criteria=c,
        )
        assert tc.id == "T01"
        assert tc.category == "Class Overview Queries"
        assert tc.query == "What is TdmOrders?"
        assert tc.description == "Should find TdmOrders class overview"
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
        assert tc.query_pl is None
        assert tc.query_en is None
        assert tc.lang is None

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
            query="What is TdmOrders?",
            result="PASS",
            match_position=1,
            match_node_type="class_overview",
            match_file="OrdersDM.pas",
            match_score=0.8534,
        )
        assert r.result == "PASS"
        assert r.match_position == 1
        assert r.match_node_type == "class_overview"
        assert r.match_file == "OrdersDM.pas"
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
        assert r.alpha is None
        assert r.query_shape is None


# ────────────────────────────────────────────────
# TestWithLanguage
# ────────────────────────────────────────────────


class TestWithLanguage:
    """with_language copies a test onto Polish, English, or the default."""

    def _bilingual(self) -> TestCase:
        return TestCase(
            id="U01",
            category="Uploads",
            query="placeholder",
            description="Retry logic for failed uploads",
            pass_criteria=PassCriteria(),
            query_class="semantic",
            query_pl="Gdzie jest logika ponawiania nieudanych wysyłek?",
            query_en="Where is the retry logic for failed uploads?",
        )

    def test_copy_does_not_mutate_and_selects_polish(self):
        """Requested Polish replaces query and records lang pl."""
        original = self._bilingual()
        chosen = with_language(original, "pl")
        assert chosen is not original
        assert original.query == "placeholder"
        assert original.lang is None
        assert chosen.query == original.query_pl
        assert chosen.lang == "pl"
        assert chosen.query_en == original.query_en
        assert chosen.query_class == "semantic"

    def test_default_prefers_english(self):
        """lang None uses English when both languages are present."""
        chosen = with_language(self._bilingual(), None)
        assert chosen.lang == "en"
        assert chosen.query == "Where is the retry logic for failed uploads?"

    def test_legacy_query_is_used_for_every_language(self):
        """A neutral query stays put and lang stays unset."""
        original = TestCase(
            id="L1",
            category="Cat",
            query="shared neutral question",
            description="d",
            pass_criteria=PassCriteria(),
        )
        for lang in (None, "pl", "en"):
            chosen = with_language(original, lang)
            assert chosen is not original
            assert chosen.query == "shared neutral question"
            assert chosen.lang is None
            assert chosen.query_pl is None
            assert chosen.query_en is None

    def test_missing_language_falls_back_to_the_other(self):
        """The copy records the language that actually supplied the text."""
        polish_only = TestCase(
            id="P1",
            category="Cat",
            query="x",
            description="d",
            pass_criteria=PassCriteria(),
            query_pl="Gdzie jest klasa UploadQueue?",
        )
        fallen_back = with_language(polish_only, "en")
        assert fallen_back.lang == "pl"
        assert fallen_back.query == "Gdzie jest klasa UploadQueue?"
        assert with_language(polish_only, None).lang == "pl"

    def test_unsupported_lang_raises(self):
        """Only pl, en, and the default are accepted."""
        with pytest.raises(ValueError, match="lang must be"):
            with_language(self._bilingual(), "both")
