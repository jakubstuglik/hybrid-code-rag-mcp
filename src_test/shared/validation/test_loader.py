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
            "file_pattern": r"OrdersDM\.pas$",
            "text_pattern": "TdmOrders",
            "max_position": 2,
            "partial_position": 4,
            "class_name_pattern": "^TdmOrders$",
            "multi_file": True,
        }
        c = loader_module._parse_criteria(raw)
        assert c.node_types == ["class_overview", "class_summary"]
        assert c.file_pattern == r"OrdersDM\.pas$"
        assert c.text_pattern == "TdmOrders"
        assert c.max_position == 2
        assert c.partial_position == 4
        assert c.class_name_pattern == "^TdmOrders$"
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
        assert tc.query_class is None

    def test_query_class_canonical(self):
        """semantic, exact and mixed are stored lowercase."""
        raw = {
            "id": "T03",
            "category": "Cat",
            "query": "q",
            "description": "d",
            "criteria": {},
            "query_class": "Semantic",
        }
        tc = loader_module._parse_test_case(raw)
        assert tc.query_class == "semantic"
        raw["query_class"] = "exact"
        assert loader_module._parse_test_case(raw).query_class == "exact"
        raw["query_class"] = " mixed "
        assert loader_module._parse_test_case(raw).query_class == "mixed"

    def test_query_class_unknown_warns_and_unclassified(self):
        """Anything other than the three classes warns and stays unclassified."""
        raw = {
            "id": "T04",
            "category": "Cat",
            "query": "q",
            "description": "d",
            "criteria": {},
            "query_class": "keyword",
        }
        with pytest.warns(UserWarning, match="treated as unclassified"):
            tc = loader_module._parse_test_case(raw)
        assert tc.query_class is None

    def test_query_class_absent_or_null(self):
        """Missing and null query_class stay unclassified without a warning."""
        raw = {
            "id": "T05",
            "category": "Cat",
            "query": "q",
            "description": "d",
            "criteria": {},
        }
        import warnings

        with warnings.catch_warnings(record=True) as recorded:
            warnings.simplefilter("always")
            tc = loader_module._parse_test_case(raw)
        assert tc.query_class is None
        assert recorded == []
        raw["query_class"] = None
        tc = loader_module._parse_test_case(raw)
        assert tc.query_class is None

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

    def test_external_yaml_path_loads(self):
        """A caller-supplied path loads even when no project-configs dir exists."""
        yaml_content = """\
- id: EXT1
  category: Precise Identifier Search
  query: Where is PrepareDataSet?
  description: Exact symbol from an external suite
  difficulty: Easy
  aspect: Sparse
  criteria:
    text_pattern: "PrepareDataSet"
    max_position: 2
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            external = os.path.join(tmpdir, "suite.yaml")
            with open(external, "w", encoding="utf-8") as handle:
                handle.write(yaml_content)
            cases = loader_module.load_test_cases(
                "config_not_in_this_repo",
                project_root=tmpdir,
                yaml_path=external,
            )
            assert len(cases) == 1
            assert cases[0].id == "EXT1"
            assert cases[0].category == "Precise Identifier Search"
            assert cases[0].query == "Where is PrepareDataSet?"
            assert cases[0].pass_criteria.text_pattern == "PrepareDataSet"
            assert cases[0].pass_criteria.max_position == 2
            assert cases[0].query_class is None
            assert not os.path.exists(os.path.join(tmpdir, "project-configs"))

    def test_yaml_query_class_roundtrip(self):
        """A suite with query_class loads it; a suite without it still loads."""
        yaml_content = """\
- id: T01
  category: Cat
  query: how does caching work
  description: d
  query_class: semantic
  criteria: {}
- id: T02
  category: Cat
  query: FindWidget
  description: d
  query_class: exact
  criteria: {}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_yaml(tmpdir, "cls_cfg", yaml_content)
            cases = loader_module.load_test_cases("cls_cfg", project_root=tmpdir)
            assert [c.query_class for c in cases] == ["semantic", "exact"]

    def test_external_yaml_path_missing_raises(self):
        """A missing caller-supplied path raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = os.path.join(tmpdir, "missing.yaml")
            with pytest.raises(FileNotFoundError, match="No validation_tests.yaml found"):
                loader_module.load_test_cases(
                    "anything", project_root=tmpdir, yaml_path=missing
                )


# ────────────────────────────────────────────────
# TestBilingualLoad
# ────────────────────────────────────────────────


_BILINGUAL_YAML = """\
- id: L1
  category: Neutral
  query: shared neutral question
  description: Legacy wording used for every language
  criteria: {}
- id: E1
  category: Fallback
  query_en: "Where is the retry logic for failed uploads?"
  description: English only
  criteria: {}
- id: B1
  category: Uploads
  query_pl: "Gdzie jest logika ponawiania nieudanych wysyłek?"
  query_en: "Where is the retry logic for failed uploads?"
  description: Same question in both languages
  query_class: semantic
  criteria:
    text_pattern: retry
"""


class TestBilingualLoad:
    """query_pl / query_en share one expected result."""

    def _write(self, tmpdir, content, name="validation_tests.yaml"):
        config_dir = os.path.join(tmpdir, "project-configs", "cfg")
        os.makedirs(config_dir, exist_ok=True)
        path = os.path.join(config_dir, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def test_legacy_suite_fields_stay_unset(self):
        """A query-only suite loads with lang None and no language texts."""
        yaml_content = """\
- id: T01
  category: Cat
  query: What is Foo?
  description: d
  criteria: {}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write(tmpdir, yaml_content)
            import warnings

            with warnings.catch_warnings(record=True) as recorded:
                warnings.simplefilter("always")
                cases = loader_module.load_test_cases("cfg", project_root=tmpdir)
                again = loader_module.load_test_cases(
                    "cfg", project_root=tmpdir, lang="pl"
                )
            assert recorded == []
            assert cases[0].query == "What is Foo?"
            assert cases[0].query_pl is None
            assert cases[0].query_en is None
            assert cases[0].lang is None
            assert again[0].query == "What is Foo?"
            assert again[0].lang is None

    def test_default_english_polish_and_explicit(self):
        """Default uses English, then Polish; pl and en select that text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write(tmpdir, _BILINGUAL_YAML)
            import warnings

            with warnings.catch_warnings(record=True) as recorded:
                warnings.simplefilter("always")
                default = loader_module.load_test_cases("cfg", project_root=tmpdir)
                english = loader_module.load_test_cases(
                    "cfg", project_root=tmpdir, lang="en"
                )
            assert recorded == []
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                polish = loader_module.load_test_cases(
                    "cfg", project_root=tmpdir, lang="pl"
                )
            by_default = {tc.id: tc for tc in default}
            assert by_default["L1"].lang is None
            assert by_default["L1"].query == "shared neutral question"
            assert by_default["E1"].lang == "en"
            assert by_default["B1"].lang == "en"
            assert by_default["B1"].query.startswith("Where is")
            assert by_default["B1"].query_pl.startswith("Gdzie")
            by_pl = {tc.id: tc for tc in polish}
            assert by_pl["B1"].lang == "pl"
            assert by_pl["B1"].query.startswith("Gdzie")
            assert by_pl["E1"].lang == "en"
            by_en = {tc.id: tc for tc in english}
            assert by_en["B1"].lang == "en"
            assert by_en["B1"].query_class == "semantic"

    def test_polish_only_defaults_to_polish(self):
        """A test with only query_pl is bilingual and defaults to Polish."""
        yaml_content = """\
- id: P1
  category: Uploads
  query_pl: "Gdzie jest klasa UploadQueue?"
  description: d
  criteria: {}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write(tmpdir, yaml_content)
            cases = loader_module.load_test_cases("cfg", project_root=tmpdir)
            assert cases[0].query == "Gdzie jest klasa UploadQueue?"
            assert cases[0].lang == "pl"
            assert cases[0].query_en is None

    def test_fallback_warns_and_records_language_used(self):
        """One warning names the test; lang is the language actually used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write(tmpdir, _BILINGUAL_YAML)
            import warnings

            with warnings.catch_warnings(record=True) as recorded:
                warnings.simplefilter("always")
                cases = loader_module.load_test_cases(
                    "cfg", project_root=tmpdir, lang="pl"
                )
            user = [w for w in recorded if issubclass(w.category, UserWarning)]
            assert len(user) == 1
            assert "E1" in str(user[0].message)
            assert "B1" not in str(user[0].message)
            by_id = {tc.id: tc for tc in cases}
            assert by_id["E1"].lang == "en"
            assert by_id["E1"].query.startswith("Where is")
            assert by_id["L1"].lang is None
            assert by_id["B1"].lang == "pl"

    def test_ambiguous_query_and_language(self):
        """query together with query_pl or query_en is rejected."""
        for key in ("query_pl", "query_en"):
            raw = {
                "id": "T01",
                "category": "Cat",
                "query": "neutral",
                key: "Where is the UploadQueue?",
                "description": "d",
                "criteria": {},
            }
            with pytest.raises(
                ValueError,
                match="ambiguous: use query_pl/query_en or query, not both",
            ):
                loader_module._parse_test_case(raw)

    @pytest.mark.parametrize("key", ["query_pl", "query_en"])
    @pytest.mark.parametrize("value", ["", "   ", None, 3, False])
    def test_empty_or_non_string_language_value(self, key, value):
        """Empty and non-string language texts are a ValueError."""
        raw = {
            "id": "T09",
            "category": "Cat",
            key: value,
            "description": "d",
            "criteria": {},
        }
        with pytest.raises(ValueError, match="non-empty string"):
            loader_module._parse_test_case(raw)

    def test_strict_lang_lists_every_incomplete_id(self):
        """strict_lang names every test that lacks Polish or English."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write(tmpdir, _BILINGUAL_YAML)
            with pytest.raises(ValueError, match="missing query_pl or query_en") as caught:
                loader_module.load_test_cases(
                    "cfg", project_root=tmpdir, strict_lang=True
                )
            message = str(caught.value)
            assert "L1" in message
            assert "E1" in message
            assert "B1" not in message

    def test_strict_lang_duplicate_ids(self):
        """strict_lang fails when the same id appears twice."""
        yaml_content = """\
- id: DUP
  category: Uploads
  query_pl: "Gdzie jest klasa UploadQueue?"
  query_en: "Where is class UploadQueue?"
  description: d
  criteria: {}
- id: DUP
  category: Uploads
  query_pl: "Gdzie jest inna klasa UploadQueue?"
  query_en: "Where is the other UploadQueue?"
  description: d
  criteria: {}
- id: OK1
  category: Uploads
  query_pl: "Gdzie?"
  query_en: "Where?"
  description: d
  criteria: {}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write(tmpdir, yaml_content)
            with pytest.raises(ValueError, match="duplicate test ids: DUP") as caught:
                loader_module.load_test_cases(
                    "cfg", project_root=tmpdir, lang="en", strict_lang=True
                )
            assert "missing query_pl" not in str(caught.value)
            cases = loader_module.load_test_cases(
                "cfg", project_root=tmpdir, lang="en", strict_lang=False
            )
            assert [tc.id for tc in cases] == ["DUP", "DUP", "OK1"]

    def test_strict_lang_reports_missing_and_duplicates_together(self):
        """One error lists incomplete tests and duplicate ids."""
        yaml_content = """\
- id: T01
  category: Cat
  query: neutral only
  description: d
  criteria: {}
- id: T01
  category: Cat
  query_pl: "Gdzie jest kolejka?"
  query_en: "Where is the queue?"
  description: d
  criteria: {}
- id: T02
  category: Cat
  query_pl: "Gdzie jest plik?"
  description: d
  criteria: {}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write(tmpdir, yaml_content)
            with pytest.raises(ValueError) as caught:
                loader_module.load_test_cases(
                    "cfg", project_root=tmpdir, strict_lang=True
                )
            message = str(caught.value)
            assert "T01" in message
            assert "T02" in message
            assert "missing query_pl or query_en" in message
            assert "duplicate test ids" in message

    def test_strict_lang_accepts_a_complete_suite(self):
        """A suite with both languages loads under strict_lang."""
        yaml_content = """\
- id: B1
  category: Uploads
  query_pl: "Gdzie jest logika ponawiania nieudanych wysyłek?"
  query_en: "Where is the retry logic for failed uploads?"
  description: d
  criteria: {}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write(tmpdir, yaml_content)
            cases = loader_module.load_test_cases(
                "cfg", project_root=tmpdir, lang="pl", strict_lang=True
            )
            assert cases[0].lang == "pl"
            assert cases[0].query.startswith("Gdzie")

    def test_unsupported_lang_raises(self):
        """lang is pl, en, or omitted."""
        with pytest.raises(ValueError, match="lang must be"):
            loader_module.load_test_cases("cfg", lang="both")
        with pytest.raises(ValueError, match="lang must be"):
            loader_module.load_test_cases("cfg", lang="de")
