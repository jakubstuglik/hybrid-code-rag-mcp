"""
shared.validation.loader -- YAML test definition loading.

Loads validation test cases from a YAML file located at:
    project-configs/<config_name>/validation_tests.yaml

Pass ``yaml_path`` to load a suite from any caller-supplied path instead.

A test has either a legacy language-neutral ``query`` or bilingual
``query_pl`` / ``query_en`` (one or both). Criteria and the other fields are
shared. ``load_test_cases(..., lang=None)`` keeps legacy suites on ``query``
and uses English, then Polish, for a bilingual test. ``lang="pl"`` or
``"en"`` selects that language, falling back to the other with one warning
per test. ``strict_lang=True`` rejects any test that lacks either language
and any duplicate id.

YAML schema is documented in docs/validation/validation-tests-guide.md.
"""

import os
import warnings
from typing import Dict, List, Optional

import yaml

from shared.validation.models import PassCriteria, TestCase, with_language

# Canonical query classes. Anything else warns and is stored as unclassified.
_QUERY_CLASSES = frozenset({"semantic", "exact", "mixed"})


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


def _parse_query_class(raw: dict, test_id: str) -> Optional[str]:
    """Return a canonical query class, or None when the field is absent.

    ``semantic``, ``exact`` and ``mixed`` are accepted in any case. Any other
    present value warns and is treated as unclassified (None) so a typo cannot
    silently join a score bucket.
    """
    if "query_class" not in raw or raw.get("query_class") is None:
        return None
    value = raw.get("query_class")
    if isinstance(value, str):
        canonical = value.strip().lower()
        if canonical in _QUERY_CLASSES:
            return canonical
    warnings.warn(
        f"Test {test_id}: query_class {value!r} is not one of "
        f"semantic, exact, mixed; treated as unclassified",
        UserWarning,
        stacklevel=2,
    )
    return None


def _require_lang_text(raw: dict, key: str, test_id: str) -> str:
    """Return a non-empty language query, or raise ValueError."""
    value = raw.get(key)
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(
            f"Test {test_id}: {key} must be a non-empty string, got {value!r}"
        )
    return value


def _parse_test_case(raw: dict) -> TestCase:
    """Parse a single test case dict from YAML into a TestCase dataclass.

    The active ``query`` is the default language (English if present, else
    Polish, else the legacy neutral query). Callers that need another
    language use ``with_language``.

    Args:
        raw: Dict with keys: id, category, description, criteria, and either
             ``query`` or at least one of ``query_pl`` / ``query_en``.
             Optional: difficulty, aspect, query_class.

    Returns:
        TestCase instance.

    Raises:
        ValueError: If required fields are missing, ``query`` is combined
            with a language query, or a language value is empty or not a string.
    """
    required_fields = ["id", "category", "description", "criteria"]
    for field in required_fields:
        if field not in raw:
            raise ValueError(
                f"Test case missing required field '{field}': {raw.get('id', '?')}"
            )

    test_id = str(raw.get("id", "?"))
    has_legacy = "query" in raw
    has_pl = "query_pl" in raw
    has_en = "query_en" in raw
    if has_legacy and (has_pl or has_en):
        raise ValueError(
            f"Test {test_id}: ambiguous: use query_pl/query_en or query, not both"
        )

    query_pl = _require_lang_text(raw, "query_pl", test_id) if has_pl else None
    query_en = _require_lang_text(raw, "query_en", test_id) if has_en else None
    if not has_legacy and query_pl is None and query_en is None:
        raise ValueError(f"Test case missing required field 'query': {test_id}")

    legacy_query = raw["query"] if has_legacy else ""
    parsed = TestCase(
        id=raw["id"],
        category=raw["category"],
        query=legacy_query,
        description=raw["description"],
        pass_criteria=_parse_criteria(raw["criteria"]),
        difficulty=raw.get("difficulty", "Medium"),
        aspect=raw.get("aspect", "Hybrid"),
        query_class=_parse_query_class(raw, test_id),
        query_pl=query_pl,
        query_en=query_en,
    )
    return with_language(parsed, None)


def _enforce_strict_lang(cases: List[TestCase]) -> None:
    """Reject tests that lack either language, and duplicate ids.

    One error lists every offending id so a lint pass shows the whole suite.
    """
    missing: List[str] = []
    seen_missing = set()
    counts: Dict[str, int] = {}
    for tc in cases:
        counts[tc.id] = counts.get(tc.id, 0) + 1
        if tc.query_pl is None or tc.query_en is None:
            if tc.id not in seen_missing:
                missing.append(str(tc.id))
                seen_missing.add(tc.id)
    duplicates = [str(test_id) for test_id, count in counts.items() if count > 1]
    parts = []
    if missing:
        listed = ", ".join(missing)
        parts.append(f"tests missing query_pl or query_en: {listed}")
    if duplicates:
        listed = ", ".join(duplicates)
        parts.append(f"duplicate test ids: {listed}")
    if parts:
        raise ValueError("; ".join(parts))


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


def _activate_language(cases: List[TestCase], lang: Optional[str]) -> List[TestCase]:
    """Copy each test onto ``lang``, warning once per fallback."""
    activated = []
    for tc in cases:
        chosen = with_language(tc, lang)
        if lang in ("pl", "en") and chosen.lang not in (None, lang):
            warnings.warn(
                f"Test {tc.id}: no query_{lang}; using query_{chosen.lang}",
                UserWarning,
                stacklevel=4,
            )
        activated.append(chosen)
    return activated


def load_test_cases(
    config_name: str,
    project_root: Optional[str] = None,
    yaml_path: Optional[str] = None,
    lang: Optional[str] = None,
    strict_lang: bool = False,
) -> List[TestCase]:
    """Load validation test cases from YAML.

    Default location is ``project-configs/<config_name>/validation_tests.yaml``.
    Pass ``yaml_path`` to load a suite that lives outside this repository
    (for example next to the codebase being measured). ``config_name`` still
    selects which index ``validate_rag.py`` queries; it is not required to
    match a directory when ``yaml_path`` is set.

    ``lang=None`` leaves a legacy ``query`` unchanged and, for a bilingual
    test, uses ``query_en`` when present, otherwise ``query_pl``. ``"pl"``
    or ``"en"`` uses that language. A bilingual test that lacks it falls
    back to the other language: one UserWarning names the test, and
    ``TestCase.lang`` is the language actually used. A legacy test keeps
    ``query`` and ``lang`` None. ``strict_lang=True`` fails if any test
    lacks ``query_pl`` or ``query_en``, or if any id is duplicated.

    Args:
        config_name: Config directory name (e.g. "config_myproject").
            Used as the source label when ``yaml_path`` is omitted.
        project_root: Project root directory. Auto-detected if None.
        yaml_path: Optional caller-supplied suite path. When set, this file
            is loaded instead of the config-relative default.
        lang: ``"pl"``, ``"en"``, or None for the default language.
        strict_lang: Require both languages on every test, and unique ids.

    Returns:
        List of TestCase objects with ``query`` set for ``lang``.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        ValueError: If YAML is malformed, test cases have missing fields,
            ``lang`` is not supported, or ``strict_lang`` finds a gap.
    """
    if lang not in (None, "pl", "en"):
        raise ValueError(f"lang must be 'pl', 'en', or omitted, got {lang!r}")

    if yaml_path:
        path = os.path.abspath(yaml_path)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"No validation_tests.yaml found at '{path}'.\n"
                f"Pass an existing suite via yaml_path or --tests.\n"
                f"See docs/validation/validation-tests-guide.md for schema."
            )
        return _finish_load(_read_test_case_list(path, path), lang, strict_lang)

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

    return _finish_load(
        _read_test_case_list(default_path, config_name), lang, strict_lang
    )


def _finish_load(
    cases: List[TestCase], lang: Optional[str], strict_lang: bool
) -> List[TestCase]:
    """Apply the strict-language lint, then select ``lang``."""
    if strict_lang:
        _enforce_strict_lang(cases)
    return _activate_language(cases, lang)
