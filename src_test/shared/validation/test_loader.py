"""
Tests for shared/validation/loader.py -- YAML test definition loading.

Tests cover:
    - _parse_criteria(): default values, custom values, all fields
    - _parse_test_case(): required fields, missing fields, defaults
    - load_test_cases(): valid YAML, missing file, malformed YAML, empty list
    - Path resolution with explicit project_root
"""

import os
import tempfile

import pytest

import shared.validation.loader as loader_module
from shared.validation.models import PassCriteria, TestCase


# ────────────────────────────────────────────────
# TestParseCriteria
# ────────────────────────────────────────────────


class TestParseCriteria:
    """Tests for _parse_criteria() -- YAML dict to PassCriteria conversion."""

    def test_empty_dict(self):
        """Empty dict produces defaults."""
        c = loader_module._parse_criteria({})
        assert c.node_types is None
        assert c.file_pattern is None
        assert c.text_pattern is None
        assert c.max_position == 3
        assert c.partial_position == 5
        assert c.class_name_pattern is None
        assert c.multi_file is False

    def test_all_fields(self):
        """All criteria fields are parsed."""
        raw = {
            "node_types": ["class_overview", "class_summary"],
            "file_pattern": r"MainDM\.pas$",
            "text_pattern": "TdmMain",
            "max_position": 2,
            "partial_position": 4,
            "class_name_pattern": "^TdmMain$",
            "multi_file": True,
        }
        c = loader_module._parse_criteria(raw)
        assert c.node_types == ["class_overview", "class_summary"]
        assert c.file_pattern == r"MainDM\.pas$"
        assert c.text_pattern == "TdmMain"
        assert c.max_position == 2
        assert c.partial_position == 4
        assert c.class_name_pattern == "^TdmMain$"
        assert c.multi_file is True

    def test_partial_fields(self):
        """Only some criteria fields present."""
        raw = {"node_types": ["defProc"], "max_position": 1}
        c = loader_module._parse_criteria(raw)
        assert c.node_types == ["defProc"]
        assert c.max_position == 1
        assert c.file_pattern is None
        assert c.partial_position == 5  # default

    def test_unknown_keys_ignored(self):
        """Unknown keys in the criteria dict are silently ignored."""
        raw = {"node_types": ["defProc"], "bogus_key": 42}
        c = loader_module._parse_criteria(raw)
        assert c.node_types == ["defProc"]


# ────────────────────────────────────────────────
# TestParseTestCase
# ────────────────────────────────────────────────


class TestParseTestCase:
    """Tests for _parse_test_case() -- YAML dict to TestCase conversion."""

    def test_minimal_valid(self):
        """Minimal valid test case with only required fields."""
        raw = {
            "id": "T01",
            "category": "Cat A",
            "query": "What is Foo?",
            "description": "Find Foo class",
            "criteria": {"node_types": ["class_overview"]},
        }
        tc = loader_module._parse_test_case(raw)
        assert tc.id == "T01"
        assert tc.category == "Cat A"
        assert tc.query == "What is Foo?"
        assert tc.description == "Find Foo class"
        assert tc.pass_criteria.node_types == ["class_overview"]
        assert tc.difficulty == "Medium"  # default
        assert tc.aspect == "Hybrid"  # default

    def test_with_difficulty_and_aspect(self):
        """Optional difficulty and aspect are parsed."""
        raw = {
            "id": "T02",
            "category": "Cat B",
            "query": "q",
            "description": "d",
            "criteria": {},
            "difficulty": "Hard",
            "aspect": "Sparse",
        }
        tc = loader_module._parse_test_case(raw)
        assert tc.difficulty == "Hard"
        assert tc.aspect == "Sparse"

    def test_missing_id_raises(self):
        """Missing 'id' field raises ValueError."""
        raw = {
            "category": "Cat",
            "query": "q",
            "description": "d",
            "criteria": {},
        }
        with pytest.raises(ValueError, match="missing required field 'id'"):
            loader_module._parse_test_case(raw)

    def test_missing_category_raises(self):
        """Missing 'category' field raises ValueError."""
        raw = {"id": "T01", "query": "q", "description": "d", "criteria": {}}
        with pytest.raises(ValueError, match="missing required field 'category'"):
            loader_module._parse_test_case(raw)

    def test_missing_query_raises(self):
        """Missing 'query' field raises ValueError."""
        raw = {"id": "T01", "category": "Cat", "description": "d", "criteria": {}}
        with pytest.raises(ValueError, match="missing required field 'query'"):
            loader_module._parse_test_case(raw)

    def test_missing_description_raises(self):
        """Missing 'description' field raises ValueError."""
        raw = {"id": "T01", "category": "Cat", "query": "q", "criteria": {}}
        with pytest.raises(ValueError, match="missing required field 'description'"):
            loader_module._parse_test_case(raw)

    def test_missing_criteria_raises(self):
        """Missing 'criteria' field raises ValueError."""
        raw = {"id": "T01", "category": "Cat", "query": "q", "description": "d"}
        with pytest.raises(ValueError, match="missing required field 'criteria'"):
            loader_module._parse_test_case(raw)


# ────────────────────────────────────────────────
# TestLoadTestCases
# ────────────────────────────────────────────────


class TestLoadTestCases:
    """Tests for load_test_cases() -- full YAML file loading."""

    def _write_yaml(self, tmpdir, config_name, content):
        """Helper: write a YAML file at the expected path under tmpdir."""
        config_dir = os.path.join(tmpdir, "project-configs", config_name)
        os.makedirs(config_dir, exist_ok=True)
        yaml_path = os.path.join(config_dir, "validation_tests.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(content)
        return yaml_path

    def test_valid_single_test(self):
        """Single test case loads correctly."""
        yaml_content = """\
- id: T01
  category: Overview
  query: What is Foo?
  description: Find Foo class overview
  criteria:
    node_types:
      - class_overview
    file_pattern: "Foo\\\\.java$"
    max_position: 2
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "my_config", yaml_content)
            cases = loader_module.load_test_cases("my_config", project_root=tmpdir)
            assert len(cases) == 1
            tc = cases[0]
            assert tc.id == "T01"
            assert tc.category == "Overview"
            assert tc.pass_criteria.node_types == ["class_overview"]
            assert tc.pass_criteria.file_pattern == "Foo\\.java$"
            assert tc.pass_criteria.max_position == 2

    def test_valid_multiple_tests(self):
        """Multiple test cases load in order."""
        yaml_content = """\
- id: T01
  category: Cat A
  query: Query 1
  description: Desc 1
  criteria:
    node_types: [class_overview]

- id: T02
  category: Cat B
  query: Query 2
  description: Desc 2
  criteria:
    file_pattern: "Bar\\\\.pas$"
  difficulty: Hard
  aspect: Dense
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "test_cfg", yaml_content)
            cases = loader_module.load_test_cases("test_cfg", project_root=tmpdir)
            assert len(cases) == 2
            assert cases[0].id == "T01"
            assert cases[1].id == "T02"
            assert cases[1].difficulty == "Hard"
            assert cases[1].aspect == "Dense"

    def test_missing_file_raises(self):
        """FileNotFoundError when YAML doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(
                FileNotFoundError, match="No validation_tests.yaml found"
            ):
                loader_module.load_test_cases("nonexistent_config", project_root=tmpdir)

    def test_not_a_list_raises(self):
        """ValueError when YAML root is not a list."""
        yaml_content = "key: value\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "bad_cfg", yaml_content)
            with pytest.raises(ValueError, match="must be a YAML list"):
                loader_module.load_test_cases("bad_cfg", project_root=tmpdir)

    def test_non_dict_entry_raises(self):
        """ValueError when a list entry is not a dict."""
        yaml_content = "- just a string\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "bad_cfg2", yaml_content)
            with pytest.raises(ValueError, match="must be a YAML mapping"):
                loader_module.load_test_cases("bad_cfg2", project_root=tmpdir)

    def test_empty_list_raises(self):
        """ValueError when YAML is an empty list."""
        yaml_content = "[]\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "empty_cfg", yaml_content)
            with pytest.raises(ValueError, match="contains no test cases"):
                loader_module.load_test_cases("empty_cfg", project_root=tmpdir)

    def test_missing_required_field_in_entry(self):
        """ValueError bubbles up from _parse_test_case when field is missing."""
        yaml_content = """\
- id: T01
  query: Something
  description: Desc
  criteria: {}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "bad_entry", yaml_content)
            with pytest.raises(ValueError, match="missing required field 'category'"):
                loader_module.load_test_cases("bad_entry", project_root=tmpdir)

    def test_criteria_defaults_from_yaml(self):
        """Criteria defaults are applied when YAML omits them."""
        yaml_content = """\
- id: T01
  category: Cat
  query: q
  description: d
  criteria:
    text_pattern: "Hello"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "defaults_cfg", yaml_content)
            cases = loader_module.load_test_cases("defaults_cfg", project_root=tmpdir)
            tc = cases[0]
            assert tc.pass_criteria.text_pattern == "Hello"
            assert tc.pass_criteria.max_position == 3  # default
            assert tc.pass_criteria.partial_position == 5  # default
            assert tc.pass_criteria.node_types is None
            assert tc.pass_criteria.multi_file is False

    def test_multi_file_from_yaml(self):
        """multi_file: true is correctly loaded."""
        yaml_content = """\
- id: T01
  category: Cross-File
  query: q
  description: d
  criteria:
    multi_file: true
    node_types: [defProc]
    max_position: 5
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "mf_cfg", yaml_content)
            cases = loader_module.load_test_cases("mf_cfg", project_root=tmpdir)
            tc = cases[0]
            assert tc.pass_criteria.multi_file is True
            assert tc.pass_criteria.max_position == 5
