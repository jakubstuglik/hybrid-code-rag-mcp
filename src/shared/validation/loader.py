"""
shared.validation.loader -- YAML test definition loading.

Loads validation test cases from a YAML file located at:
    project-configs/<config_name>/validation_tests.yaml

Pass ``yaml_path`` to load a suite from any caller-supplied path instead.

YAML schema is documented in docs/validation/validation-tests-guide.md.
"""

import os
import sys
from typing import List, Optional

import yaml

from shared.validation.models import PassCriteria, TestCase


def _parse_criteria(raw: dict) -> PassCriteria:
    """Parse a criteria dict from YAML into a PassCriteria dataclass.

    Args:
        raw: Dict with optional keys: node_types, file_pattern, text_pattern,
             max_position, partial_position, class_name_pattern, multi_file.

    Returns:
        PassCriteria instance.
    """
    return PassCriteria(
        node_types=raw.get("node_types"),
        file_pattern=raw.get("file_pattern"),
        text_pattern=raw.get("text_pattern"),
        max_position=raw.get("max_position", 3),
        partial_position=raw.get("partial_position", 5),
        class_name_pattern=raw.get("class_name_pattern"),
        multi_file=raw.get("multi_file", False),
    )


def _parse_test_case(raw: dict) -> TestCase:
    """Parse a single test case dict from YAML into a TestCase dataclass.

    Args:
        raw: Dict with keys: id, category, query, description, criteria,
             and optional: difficulty, aspect.

    Returns:
        TestCase instance.

    Raises:
        ValueError: If required fields are missing.
    """
    required_fields = ["id", "category", "query", "description", "criteria"]
    for field in required_fields:
        if field not in raw:
            raise ValueError(
                f"Test case missing required field '{field}': {raw.get('id', '?')}"
            )

    return TestCase(
        id=raw["id"],
        category=raw["category"],
        query=raw["query"],
        description=raw["description"],
        pass_criteria=_parse_criteria(raw["criteria"]),
        difficulty=raw.get("difficulty", "Medium"),
        aspect=raw.get("aspect", "Hybrid"),
    )


def _read_test_case_list(yaml_path: str, source_label: str) -> List[TestCase]:
    """Parse a validation YAML file into test cases.

    Args:
        yaml_path: Filesystem path of the YAML suite.
        source_label: Name used in error messages (config name or path).

    Returns:
        Non-empty list of TestCase objects.

    Raises:
        ValueError: If the YAML root is not a list, an entry is not a mapping,
            a required field is missing, or the list is empty.
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    if not isinstance(raw_data, list):
        raise ValueError(
            f"validation_tests.yaml must be a YAML list of test cases, "
            f"got {type(raw_data).__name__}"
        )

    test_cases = []
    for i, raw in enumerate(raw_data):
        if not isinstance(raw, dict):
            raise ValueError(
                f"Test case #{i + 1} must be a YAML mapping, got {type(raw).__name__}"
            )
        test_cases.append(_parse_test_case(raw))

    if not test_cases:
        raise ValueError(
            f"validation_tests.yaml for '{source_label}' contains no test cases"
        )

    return test_cases


def load_test_cases(
    config_name: str,
    project_root: Optional[str] = None,
    yaml_path: Optional[str] = None,
) -> List[TestCase]:
    """Load validation test cases from YAML.

    Default location is ``project-configs/<config_name>/validation_tests.yaml``.
    Pass ``yaml_path`` to load a suite that lives outside this repository
    (for example next to the codebase being measured). ``config_name`` still
    selects which index ``validate_rag.py`` queries; it is not required to
    match a directory when ``yaml_path`` is set.

    Args:
        config_name: Config directory name (e.g. "config_myproject").
            Used as the source label when ``yaml_path`` is omitted.
        project_root: Project root directory. Auto-detected if None.
        yaml_path: Optional caller-supplied suite path. When set, this file
            is loaded instead of the config-relative default.

    Returns:
        List of TestCase objects.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        ValueError: If YAML is malformed or test cases have missing fields.
    """
    if yaml_path:
        path = os.path.abspath(yaml_path)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"No validation_tests.yaml found at '{path}'.\n"
                f"Pass an existing suite via yaml_path or --tests.\n"
                f"See docs/validation/validation-tests-guide.md for schema."
            )
        return _read_test_case_list(path, path)

    if project_root is None:
        # Auto-detect: this file is at src/shared/validation/loader.py
        # Project root is 3 levels up
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )

    default_path = os.path.join(
        project_root, "project-configs", config_name, "validation_tests.yaml"
    )

    if not os.path.exists(default_path):
        raise FileNotFoundError(
            f"No validation_tests.yaml found for config '{config_name}'.\n"
            f"Expected: {default_path}\n"
            f"Create a YAML test file. See docs/validation/validation-tests-guide.md for schema."
        )

    return _read_test_case_list(default_path, config_name)
