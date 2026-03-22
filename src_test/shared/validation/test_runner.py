"""
Tests for shared/validation/runner.py -- Query evaluation logic.

Tests cover:
    - _node_matches(): full match against all criteria dimensions
    - _file_matches(), _type_matches(), _text_matches(): single-dimension partial checks
    - _build_node_infos(): node info dict construction
    - evaluate_test(): PASS, PARTIAL (full match beyond max_position),
      PARTIAL (single-dimension), FAIL outcomes
    - _evaluate_multi_file(): multi-file PASS, PARTIAL (beyond max_position),
      PARTIAL (single file), FAIL

Note: setup() and run_query() require Qdrant/embedding infrastructure and are
not unit-tested here. They are covered by integration tests.
"""

import pytest

import shared.validation.runner as runner_module
from shared.validation.models import PassCriteria, TestCase, TestResult


# ────────────────────────────────────────────────
# Lightweight mocks (no LlamaIndex dependency)
# ────────────────────────────────────────────────


class MockNode:
    """Lightweight mock for LlamaIndex TextNode."""

    def __init__(self, metadata: dict, content: str = ""):
        self.metadata = metadata
        self._content = content

    def get_content(self):
        return self._content


class MockNodeWithScore:
    """Lightweight mock for LlamaIndex NodeWithScore."""

    def __init__(self, score: float, metadata: dict, content: str = ""):
        self.score = score
        self.node = MockNode(metadata, content)


def _make_node(
    score: float,
    node_type: str = "defProc",
    file_path: str = "src/Foo.pas",
    class_name: str = "",
    content: str = "",
) -> MockNodeWithScore:
    """Convenience factory for mock nodes."""
    return MockNodeWithScore(
        score=score,
        metadata={
            "node_type": node_type,
            "file_path": file_path,
            "class_name": class_name,
        },
        content=content,
    )


# ────────────────────────────────────────────────
# TestNodeMatches
# ────────────────────────────────────────────────


class TestNodeMatches:
    """Tests for _node_matches() -- full match against all criteria."""

    def test_all_none_criteria_matches_anything(self):
        """PassCriteria with all defaults matches any node."""
        node = _make_node(0.5, node_type="defProc", file_path="Foo.pas")
        criteria = PassCriteria()
        assert runner_module._node_matches(node, criteria) is True

    def test_node_type_match(self):
        """Matches when node_type is in the allowed list."""
        node = _make_node(0.5, node_type="class_overview")
        criteria = PassCriteria(node_types=["class_overview", "class_summary"])
        assert runner_module._node_matches(node, criteria) is True

    def test_node_type_mismatch(self):
        """Fails when node_type is not in the allowed list."""
        node = _make_node(0.5, node_type="defProc")
        criteria = PassCriteria(node_types=["class_overview"])
        assert runner_module._node_matches(node, criteria) is False

    def test_file_pattern_match(self):
        """Matches when file_path matches regex."""
        node = _make_node(0.5, file_path="src/MainDM.pas")
        criteria = PassCriteria(file_pattern=r"MainDM\.pas$")
        assert runner_module._node_matches(node, criteria) is True

    def test_file_pattern_mismatch(self):
        """Fails when file_path doesn't match regex."""
        node = _make_node(0.5, file_path="src/Other.pas")
        criteria = PassCriteria(file_pattern=r"MainDM\.pas$")
        assert runner_module._node_matches(node, criteria) is False

    def test_text_pattern_match(self):
        """Matches when content contains text_pattern regex."""
        node = _make_node(0.5, content="class TdmMain extends TDataModule")
        criteria = PassCriteria(text_pattern=r"TdmMain")
        assert runner_module._node_matches(node, criteria) is True

    def test_text_pattern_mismatch(self):
        """Fails when content doesn't contain text_pattern."""
        node = _make_node(0.5, content="class TfrmOther extends TForm")
        criteria = PassCriteria(text_pattern=r"TdmMain")
        assert runner_module._node_matches(node, criteria) is False

    def test_class_name_pattern_match(self):
        """Matches when class_name matches regex."""
        node = _make_node(0.5, class_name="TdmMain")
        criteria = PassCriteria(class_name_pattern=r"^TdmMain$")
        assert runner_module._node_matches(node, criteria) is True

    def test_class_name_pattern_mismatch(self):
        """Fails when class_name doesn't match regex."""
        node = _make_node(0.5, class_name="TfrmOther")
        criteria = PassCriteria(class_name_pattern=r"^TdmMain$")
        assert runner_module._node_matches(node, criteria) is False

    def test_class_name_empty_string(self):
        """Empty class_name fails to match a specific pattern."""
        node = _make_node(0.5, class_name="")
        criteria = PassCriteria(class_name_pattern=r"^TdmMain$")
        assert runner_module._node_matches(node, criteria) is False

    def test_multiple_criteria_all_must_match(self):
        """All specified criteria must match for a full match."""
        node = _make_node(
            0.5,
            node_type="class_overview",
            file_path="src/MainDM.pas",
            content="TdmMain data module",
        )
        criteria = PassCriteria(
            node_types=["class_overview"],
            file_pattern=r"MainDM\.pas$",
            text_pattern=r"TdmMain",
        )
        assert runner_module._node_matches(node, criteria) is True

    def test_multiple_criteria_one_fails(self):
        """If any one criterion fails, the full match fails."""
        node = _make_node(
            0.5,
            node_type="defProc",  # wrong type
            file_path="src/MainDM.pas",
            content="TdmMain procedure",
        )
        criteria = PassCriteria(
            node_types=["class_overview"],
            file_pattern=r"MainDM\.pas$",
            text_pattern=r"TdmMain",
        )
        assert runner_module._node_matches(node, criteria) is False

    def test_node_type_fallback_to_type_key(self):
        """Falls back to 'type' metadata key if 'node_type' is missing."""
        node = MockNodeWithScore(
            score=0.5,
            metadata={"type": "class_overview", "file_path": "Foo.pas"},
        )
        criteria = PassCriteria(node_types=["class_overview"])
        assert runner_module._node_matches(node, criteria) is True


# ────────────────────────────────────────────────
# TestFileMatches / TestTypeMatches / TestTextMatches
# ────────────────────────────────────────────────


class TestFileMatches:
    """Tests for _file_matches() -- single-dimension file check."""

    def test_matches(self):
        node = _make_node(0.5, file_path="src/MainDM.pas")
        assert (
            runner_module._file_matches(
                node, PassCriteria(file_pattern=r"MainDM\.pas$")
            )
            is True
        )

    def test_no_file_pattern(self):
        """Returns False when no file_pattern is specified."""
        node = _make_node(0.5, file_path="src/MainDM.pas")
        assert runner_module._file_matches(node, PassCriteria()) is False

    def test_mismatch(self):
        node = _make_node(0.5, file_path="src/Other.pas")
        assert (
            runner_module._file_matches(
                node, PassCriteria(file_pattern=r"MainDM\.pas$")
            )
            is False
        )


class TestTypeMatches:
    """Tests for _type_matches() -- single-dimension type check."""

    def test_matches(self):
        node = _make_node(0.5, node_type="class_overview")
        assert (
            runner_module._type_matches(
                node, PassCriteria(node_types=["class_overview"])
            )
            is True
        )

    def test_no_node_types(self):
        """Returns False when no node_types specified."""
        node = _make_node(0.5, node_type="class_overview")
        assert runner_module._type_matches(node, PassCriteria()) is False

    def test_mismatch(self):
        node = _make_node(0.5, node_type="defProc")
        assert (
            runner_module._type_matches(
                node, PassCriteria(node_types=["class_overview"])
            )
            is False
        )


class TestTextMatches:
    """Tests for _text_matches() -- single-dimension text check."""

    def test_matches(self):
        node = _make_node(0.5, content="TdmMain class overview")
        assert (
            runner_module._text_matches(node, PassCriteria(text_pattern=r"TdmMain"))
            is True
        )

    def test_no_text_pattern(self):
        """Returns False when no text_pattern specified."""
        node = _make_node(0.5, content="TdmMain class overview")
        assert runner_module._text_matches(node, PassCriteria()) is False

    def test_mismatch(self):
        node = _make_node(0.5, content="Something else")
        assert (
            runner_module._text_matches(node, PassCriteria(text_pattern=r"TdmMain"))
            is False
        )


# ────────────────────────────────────────────────
# TestBuildNodeInfos
# ────────────────────────────────────────────────


class TestBuildNodeInfos:
    """Tests for _build_node_infos() -- node info dict construction."""

    def test_basic(self):
        """Builds correct info dicts from nodes."""
        nodes = [
            _make_node(
                0.8534,
                node_type="class_overview",
                file_path="Foo.pas",
                class_name="TFoo",
            ),
            _make_node(0.7123, node_type="defProc", file_path="Bar.pas"),
        ]
        infos = runner_module._build_node_infos(nodes, top_k=8)
        assert len(infos) == 2
        assert infos[0]["position"] == 1
        assert infos[0]["node_type"] == "class_overview"
        assert infos[0]["file_path"] == "Foo.pas"
        assert infos[0]["score"] == 0.8534
        assert infos[0]["class_name"] == "TFoo"
        assert infos[1]["position"] == 2

    def test_respects_top_k(self):
        """Only includes top_k nodes."""
        nodes = [_make_node(0.5 - i * 0.1) for i in range(10)]
        infos = runner_module._build_node_infos(nodes, top_k=3)
        assert len(infos) == 3

    def test_none_score(self):
        """None score is preserved as None."""
        node = MockNodeWithScore(
            score=None,
            metadata={"node_type": "defProc", "file_path": "x.pas"},
        )
        infos = runner_module._build_node_infos([node], top_k=8)
        assert infos[0]["score"] is None

    def test_empty_nodes(self):
        """Empty nodes list produces empty infos."""
        infos = runner_module._build_node_infos([], top_k=8)
        assert infos == []

    def test_fallback_type_key(self):
        """Falls back to 'type' metadata key when 'node_type' missing."""
        node = MockNodeWithScore(
            score=0.5,
            metadata={"type": "full_file", "file_path": "x.txt"},
        )
        infos = runner_module._build_node_infos([node], top_k=8)
        assert infos[0]["node_type"] == "full_file"


# ────────────────────────────────────────────────
# TestEvaluateTest
# ────────────────────────────────────────────────


class TestEvaluateTest:
    """Tests for evaluate_test() -- PASS / PARTIAL / FAIL evaluation."""

    def _make_tc(self, criteria: PassCriteria, tc_id: str = "T01") -> TestCase:
        """Helper to create a TestCase with given criteria."""
        return TestCase(
            id=tc_id,
            category="Test Cat",
            query="test query",
            description="test desc",
            pass_criteria=criteria,
        )

    def test_pass_at_position_1(self):
        """Full match at position 1 -> PASS."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                file_pattern=r"Foo\.pas$",
                max_position=3,
            )
        )
        nodes = [
            _make_node(0.9, node_type="class_overview", file_path="src/Foo.pas"),
            _make_node(0.7, node_type="defProc", file_path="src/Bar.pas"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PASS"
        assert result.match_position == 1
        assert result.match_node_type == "class_overview"

    def test_pass_at_max_position(self):
        """Full match at position == max_position -> PASS."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                max_position=3,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc"),
            _make_node(0.8, node_type="defProc"),
            _make_node(0.7, node_type="class_overview"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PASS"
        assert result.match_position == 3

    def test_partial_full_match_beyond_max(self):
        """Full match at position > max_position but <= partial_position -> PARTIAL."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                max_position=2,
                partial_position=5,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc"),
            _make_node(0.8, node_type="defProc"),
            _make_node(0.7, node_type="class_overview"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PARTIAL"
        assert result.match_position == 3
        assert "Full match at position 3" in result.detail

    def test_partial_file_only_match(self):
        """File matches but type doesn't -> PARTIAL (single-dimension)."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                file_pattern=r"Foo\.pas$",
                max_position=1,
                partial_position=3,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc", file_path="src/Foo.pas"),
            _make_node(0.8, node_type="defProc", file_path="src/Bar.pas"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PARTIAL"
        assert "file_path match" in result.detail

    def test_partial_type_only_match(self):
        """Type matches but file doesn't -> PARTIAL (single-dimension)."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                file_pattern=r"Foo\.pas$",
                max_position=1,
                partial_position=3,
            )
        )
        nodes = [
            _make_node(0.9, node_type="class_overview", file_path="src/Other.pas"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PARTIAL"
        assert "node_type match" in result.detail

    def test_partial_text_only_match(self):
        """Text matches but type/file don't -> PARTIAL (single-dimension)."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                file_pattern=r"Foo\.pas$",
                text_pattern=r"TdmMain",
                max_position=1,
                partial_position=3,
            )
        )
        nodes = [
            _make_node(
                0.9,
                node_type="defProc",
                file_path="src/Other.pas",
                content="TdmMain procedure body",
            ),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PARTIAL"
        assert "text_pattern match" in result.detail

    def test_fail_no_matches(self):
        """No matching nodes at all -> FAIL."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                file_pattern=r"NonExistent\.pas$",
                max_position=3,
                partial_position=5,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc", file_path="src/Other.pas"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "FAIL"
        assert "No matching nodes" in result.detail

    def test_fail_empty_nodes(self):
        """Empty node list -> FAIL."""
        tc = self._make_tc(PassCriteria(node_types=["class_overview"]))
        result = runner_module.evaluate_test(tc, [])
        assert result.result == "FAIL"

    def test_all_nodes_populated(self):
        """all_nodes field is always populated in result."""
        tc = self._make_tc(PassCriteria())
        nodes = [_make_node(0.9)]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.all_nodes is not None
        assert len(result.all_nodes) == 1

    def test_result_preserves_tc_fields(self):
        """Result carries id, category, query from the test case."""
        tc = TestCase(
            id="T42",
            category="Special Cat",
            query="Special query",
            description="desc",
            pass_criteria=PassCriteria(),
        )
        nodes = [_make_node(0.5)]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.id == "T42"
        assert result.category == "Special Cat"
        assert result.query == "Special query"

    def test_partial_beyond_partial_position_is_fail(self):
        """Full match beyond partial_position -> FAIL (not PARTIAL)."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                max_position=1,
                partial_position=2,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc"),
            _make_node(0.8, node_type="defProc"),
            _make_node(
                0.7, node_type="class_overview"
            ),  # position 3, beyond partial_position=2
        ]
        result = runner_module.evaluate_test(tc, nodes)
        # position 3 > partial_position=2, and no single-dim matches within partial
        assert result.result == "FAIL"

    def test_top_k_limits_evaluation(self):
        """evaluate_test respects top_k parameter."""
        tc = self._make_tc(PassCriteria(node_types=["class_overview"], max_position=5))
        nodes = [_make_node(0.9 - i * 0.1, node_type="defProc") for i in range(4)]
        nodes.append(_make_node(0.4, node_type="class_overview"))  # position 5
        # top_k=3 -> only considers first 3 nodes
        result = runner_module.evaluate_test(tc, nodes, top_k=3)
        assert result.result == "FAIL"


# ────────────────────────────────────────────────
# TestEvaluateMultiFile
# ────────────────────────────────────────────────


class TestEvaluateMultiFile:
    """Tests for evaluate_test() with multi_file=True criteria."""

    def _make_tc(self, criteria: PassCriteria, tc_id: str = "T01") -> TestCase:
        return TestCase(
            id=tc_id,
            category="Cross-File",
            query="cross-file query",
            description="needs 2+ files",
            pass_criteria=criteria,
        )

    def test_pass_two_files(self):
        """Two matching files within max_position -> PASS."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["defProc"],
                multi_file=True,
                max_position=5,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc", file_path="src/Foo.pas"),
            _make_node(0.8, node_type="defProc", file_path="src/Bar.pas"),
            _make_node(0.7, node_type="defProc", file_path="src/Baz.pas"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PASS"
        assert result.match_position == 1

    def test_partial_two_files_beyond_max_position(self):
        """Two files match but first match beyond max_position -> PARTIAL."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["defProc"],
                multi_file=True,
                max_position=1,
                partial_position=5,
            )
        )
        nodes = [
            _make_node(0.9, node_type="class_overview", file_path="src/Foo.pas"),
            _make_node(0.8, node_type="defProc", file_path="src/Bar.pas"),
            _make_node(0.7, node_type="defProc", file_path="src/Baz.pas"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PARTIAL"
        assert "Multi-file match" in result.detail

    def test_partial_single_file(self):
        """Only one file matches -> PARTIAL (need >=2)."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["defProc"],
                multi_file=True,
                max_position=5,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc", file_path="src/Foo.pas"),
            _make_node(0.8, node_type="defProc", file_path="src/Foo.pas"),  # same file
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "PARTIAL"
        assert "Only 1 file matched" in result.detail

    def test_fail_no_matches(self):
        """No matching nodes -> FAIL."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["class_overview"],
                multi_file=True,
                max_position=5,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc", file_path="src/Foo.pas"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        assert result.result == "FAIL"
        assert "No matching nodes" in result.detail

    def test_fail_empty_nodes(self):
        """Empty node list -> FAIL."""
        tc = self._make_tc(PassCriteria(multi_file=True))
        result = runner_module.evaluate_test(tc, [])
        assert result.result == "FAIL"

    def test_multi_file_same_basename_different_dirs(self):
        """Same basename in different directories counts as different files."""
        tc = self._make_tc(
            PassCriteria(
                node_types=["defProc"],
                multi_file=True,
                max_position=5,
            )
        )
        nodes = [
            _make_node(0.9, node_type="defProc", file_path="module_a/Foo.pas"),
            _make_node(0.8, node_type="defProc", file_path="module_b/Foo.pas"),
        ]
        result = runner_module.evaluate_test(tc, nodes)
        # _evaluate_multi_file uses os.path.basename, so "Foo.pas" == "Foo.pas" -> 1 file
        assert result.result == "PARTIAL"
        assert "Only 1 file matched" in result.detail
