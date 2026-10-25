"""CLI test: validate_rag.py --tests loads a caller-supplied suite.

--list returns before index setup, so this does not contact Qdrant.
The diagnostic-rank test mocks retrieval so it does not contact Qdrant either.
Language runs mock retrieval the same way.
"""

import json
import os
import sys
import tempfile
import types

import pytest

import validate_rag


def test_list_loads_external_suite(capsys, monkeypatch):
    """--tests PATH --list prints the external case and does not require a config dir."""
    yaml_content = """\
- id: EXT1
  category: Precise Identifier Search
  query: Where is PrepareDataSet?
  description: Exact symbol from an external suite
  criteria:
    text_pattern: "PrepareDataSet"
    max_position: 2
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        suite = os.path.join(tmpdir, "suite.yaml")
        with open(suite, "w", encoding="utf-8") as handle:
            handle.write(yaml_content)
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "validate_rag.py",
                "--config",
                "config_not_in_this_repo",
                "--tests",
                suite,
                "--list",
            ],
        )
        validate_rag.main()
        out = capsys.readouterr().out
        assert "EXT1" in out
        assert "Where is PrepareDataSet?" in out
        assert "Precise Identifier Search" in out
        assert "Total: 1 tests" in out


def _write_suite(path, test_id, query):
    path.write_text(
        f"""\
- id: {test_id}
  category: Cat
  query: {query}
  description: d
  query_class: semantic
  criteria:
    file_pattern: "Missing\\\\.py$"
""",
        encoding="utf-8",
    )


def test_validation_tests_file_used_when_tests_omitted(capsys, monkeypatch, tmp_path):
    """VALIDATION_TESTS_FILE selects the suite when --tests is not passed."""
    suite = tmp_path / "from_config.yaml"
    _write_suite(suite, "CFG1", "from-config")
    monkeypatch.setattr(
        "config_loader.get_config",
        lambda **kwargs: types.SimpleNamespace(VALIDATION_TESTS_FILE=str(suite)),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_rag.py", "--config", "config_not_in_this_repo", "--list"],
    )
    validate_rag.main()
    out = capsys.readouterr().out
    assert "CFG1" in out
    assert "from-config" in out


def test_tests_flag_wins_over_validation_tests_file(capsys, monkeypatch, tmp_path):
    """--tests is used even when the config names a different file."""
    configured = tmp_path / "configured.yaml"
    explicit = tmp_path / "explicit.yaml"
    _write_suite(configured, "CFG1", "from-config")
    _write_suite(explicit, "CLI1", "from-cli")

    def fail_if_called(**kwargs):
        raise AssertionError("config should not be loaded when --tests is set")

    monkeypatch.setattr("config_loader.get_config", fail_if_called)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(explicit),
            "--list",
        ],
    )
    validate_rag.main()
    out = capsys.readouterr().out
    assert "CLI1" in out
    assert "CFG1" not in out


def test_diag_rank_uses_a_separate_search(capsys, monkeypatch, tmp_path):
    """--diag-rank fetches N on a second call and does not alter the score."""
    suite = tmp_path / "suite.yaml"
    _write_suite(suite, "D1", "where-is-it")
    calls = []

    def fake_setup(**kwargs):
        return "index", "dense", 0.5, types.SimpleNamespace()

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        calls.append(top_k)
        return []

    monkeypatch.setattr(validate_rag, "setup", fake_setup)
    monkeypatch.setattr(validate_rag, "run_query", fake_run_query)
    monkeypatch.setattr(
        validate_rag,
        "rerank_profiles_for_config",
        lambda cfg: types.SimpleNamespace(names=["none"]),
    )
    monkeypatch.setattr(validate_rag, "adaptive_result_fields", lambda *a, **k: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--json",
            "--diag-rank",
            "20",
            "--top-k",
            "8",
        ],
    )
    validate_rag.main()
    data = json.loads(capsys.readouterr().out)
    assert calls == [8, 20]
    test = data["tests"][0]
    assert test["result"] == "FAIL"
    assert test["diag_rank"] is None
    assert test["diag_top3_files"] == []
    assert test["query_class"] == "semantic"
    assert data["by_query_class"]["semantic"]["n"] == 1
    assert data["fail_count"] == 1


def test_without_diag_rank_search_runs_once(capsys, monkeypatch, tmp_path):
    """Default runs do not add diagnostic keys."""
    suite = tmp_path / "suite.yaml"
    _write_suite(suite, "D2", "plain")
    calls = []

    monkeypatch.setattr(
        validate_rag, "setup", lambda **kwargs: ("index", "dense", 0.5, types.SimpleNamespace())
    )

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        calls.append(top_k)
        return []

    monkeypatch.setattr(validate_rag, "run_query", fake_run_query)
    monkeypatch.setattr(
        validate_rag,
        "rerank_profiles_for_config",
        lambda cfg: types.SimpleNamespace(names=["none"]),
    )
    monkeypatch.setattr(validate_rag, "adaptive_result_fields", lambda *a, **k: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--json",
        ],
    )
    validate_rag.main()
    data = json.loads(capsys.readouterr().out)
    assert calls == [8]
    assert "diag_rank" not in data["tests"][0]
    assert "by_query_class" in data
    assert "lang" not in data
    assert "lang" not in data["tests"][0]


class _Doc:
    def __init__(self, text, file_path):
        self.metadata = {
            "file_path": file_path,
            "node_type": "method_declaration",
            "class_name": "UploadQueue",
        }
        self._text = text

    def get_content(self):
        return self._text


class _Hit:
    def __init__(self, text, file_path):
        self.node = _Doc(text, file_path)
        self.score = 0.91


def _patch_index(monkeypatch, run_query):
    """Replace index setup and retrieval. Returns a setup-call counter."""
    state = {"setup": 0}

    def fake_setup(**kwargs):
        state["setup"] += 1
        return "index", "dense", 0.5, types.SimpleNamespace()

    monkeypatch.setattr(validate_rag, "setup", fake_setup)
    monkeypatch.setattr(validate_rag, "run_query", run_query)
    monkeypatch.setattr(
        validate_rag,
        "rerank_profiles_for_config",
        lambda cfg: types.SimpleNamespace(names=["none"]),
    )
    monkeypatch.setattr(validate_rag, "adaptive_result_fields", lambda *a, **k: None)
    return state


_BOTH_SUITE = """\
- id: U01
  category: Uploads
  description: Retry logic for failed uploads
  query_class: semantic
  query_pl: "Gdzie jest logika ponawiania nieudanych wysyłek?"
  query_en: "Where is the retry logic for failed uploads?"
  criteria:
    file_pattern: "upload_queue\\\\.py$"
    text_pattern: "retry"
    max_position: 1
    partial_position: 5
- id: U02
  category: Uploads
  description: Class lookup, same identifier, different wording
  query_class: exact
  query_pl: "Gdzie jest klasa UploadQueue?"
  query_en: "Where is class UploadQueue?"
  criteria:
    file_pattern: "upload_queue\\\\.py$"
    text_pattern: "UploadQueue"
    max_position: 1
    partial_position: 5
- id: U03
  category: Neutral
  description: Legacy query used for every language
  query_class: mixed
  query: "shared neutral question"
  criteria:
    file_pattern: "notes\\\\.md$"
    text_pattern: "neutral"
    max_position: 1
- id: U04
  category: Fallback
  description: English only, Polish falls back
  query_class: semantic
  query_en: "Where is the retry counter?"
  criteria:
    file_pattern: "upload_queue\\\\.py$"
    text_pattern: "counter"
    max_position: 1
- id: U05
  category: Neutral
  description: Same PASS, different match position
  query_class: mixed
  query_pl: "Gdzie jest licznik wysyłek?"
  query_en: "Where is the upload counter?"
  criteria:
    file_pattern: "upload_queue\\\\.py$"
    text_pattern: "attempts"
    max_position: 3
"""


def _nodes_for(query):
    """Different hits per language. Identical text gets the same hits."""
    if query.startswith("Gdzie jest logika"):
        return [_Hit("retry", "src/upload_queue.py")]
    if query.startswith("Where is the retry logic"):
        return []
    if query.startswith("Gdzie jest klasa"):
        return [
            _Hit("nope", "other.py"),
            _Hit("class UploadQueue", "src/upload_queue.py"),
        ]
    if query.startswith("Where is class"):
        return [_Hit("class UploadQueue", "src/upload_queue.py")]
    if query == "shared neutral question":
        return [_Hit("neutral", "docs/notes.md")]
    if query == "Where is the retry counter?":
        return [_Hit("counter", "src/upload_queue.py")]
    if query.startswith("Gdzie jest licznik"):
        return [_Hit("attempts", "src/upload_queue.py")]
    if query.startswith("Where is the upload counter"):
        return [
            _Hit("nope", "other.py"),
            _Hit("attempts", "src/upload_queue.py"),
        ]
    raise AssertionError(query)


def _write_text(path, content):
    path.write_text(content, encoding="utf-8")


def test_lang_both_json_deltas_and_changed_tests(capsys, monkeypatch, tmp_path):
    """One setup, two passes, EN-minus-PL deltas, and tests that moved."""
    suite = tmp_path / "suite.yaml"
    _write_text(suite, _BOTH_SUITE)
    queries = []

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        queries.append((query, top_k))
        return _nodes_for(query)

    state = _patch_index(monkeypatch, fake_run_query)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "both",
            "--json",
        ],
    )
    with pytest.warns(UserWarning, match="U04"):
        validate_rag.main()
    data = json.loads(capsys.readouterr().out)
    assert state["setup"] == 1
    assert [top_k for _query, top_k in queries] == [8] * 10
    assert queries[0][0].startswith("Gdzie jest logika")
    assert queries[5][0].startswith("Where is the retry logic")
    assert set(data) == {
        "lang",
        "config",
        "alpha",
        "pl",
        "en",
        "delta",
        "changed_tests",
        "fallback_tests",
    }
    assert data["lang"] == "both"
    assert data["alpha"] == 0.5
    assert data["config"] == "config_not_in_this_repo"
    assert data["pl"]["lang"] == "pl"
    assert data["en"]["lang"] == "en"
    assert data["pl"]["score_pct"] == 90.0
    assert data["en"]["score_pct"] == 80.0
    assert data["delta"]["score_pct"] == -10.0
    assert data["delta"]["by_query_class"] == {
        "semantic": -50.0,
        "exact": 50.0,
        "mixed": 0.0,
    }
    assert data["delta"]["by_category"] == {
        "Uploads": -25.0,
        "Neutral": 0.0,
        "Fallback": 0.0,
    }
    pl_tests = {row["id"]: row for row in data["pl"]["tests"]}
    en_tests = {row["id"]: row for row in data["en"]["tests"]}
    assert pl_tests["U01"]["lang"] == "pl"
    assert pl_tests["U01"]["result"] == "PASS"
    assert pl_tests["U01"]["match_position"] == 1
    assert en_tests["U01"]["result"] == "FAIL"
    assert en_tests["U01"]["match_position"] is None
    assert en_tests["U01"]["lang"] == "en"
    assert pl_tests["U02"]["result"] == "PARTIAL"
    assert pl_tests["U02"]["match_position"] == 2
    assert en_tests["U02"]["result"] == "PASS"
    assert en_tests["U02"]["match_position"] == 1
    assert pl_tests["U03"]["lang"] is None
    assert pl_tests["U03"]["query"] == "shared neutral question"
    assert en_tests["U03"]["query"] == "shared neutral question"
    assert pl_tests["U04"]["lang"] == "en"
    assert pl_tests["U04"]["result"] == "PASS"
    assert pl_tests["U05"]["result"] == "PASS"
    assert pl_tests["U05"]["match_position"] == 1
    assert en_tests["U05"]["result"] == "PASS"
    assert en_tests["U05"]["match_position"] == 2
    assert data["pl"]["by_query_class"]["semantic"]["n"] == 2
    assert data["pl"]["by_query_class"]["semantic"]["score_pct"] == 100.0
    assert data["en"]["by_query_class"]["semantic"]["score_pct"] == 50.0
    assert data["pl"]["by_query_class"]["exact"]["score_pct"] == 50.0
    assert data["en"]["by_query_class"]["exact"]["score_pct"] == 100.0
    changed = {row["id"]: row for row in data["changed_tests"]}
    assert set(changed) == {"U01", "U02", "U05"}
    assert changed["U01"]["query_class"] == "semantic"
    assert changed["U01"]["pl_result"] == "PASS"
    assert changed["U01"]["pl_position"] == 1
    assert changed["U01"]["en_result"] == "FAIL"
    assert changed["U01"]["en_position"] is None
    assert changed["U05"]["query_class"] == "mixed"
    assert changed["U05"]["pl_result"] == "PASS"
    assert changed["U05"]["en_result"] == "PASS"
    assert changed["U05"]["pl_position"] == 1
    assert changed["U05"]["en_position"] == 2
    assert data["fallback_tests"] == {"pl": ["U04"], "en": []}


def test_lang_both_text_summary_skips_per_test_detail(capsys, monkeypatch, tmp_path):
    """Without --verbose the comparison is the summary, not two full reports."""
    suite = tmp_path / "suite.yaml"
    _write_text(suite, _BOTH_SUITE)

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        return _nodes_for(query)

    _patch_index(monkeypatch, fake_run_query)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "both",
        ],
    )
    with pytest.warns(UserWarning, match="U04"):
        validate_rag.main()
    out = capsys.readouterr().out
    assert "Overall PL: 90.0% (4 PASS, 1 PARTIAL, 0 FAIL, n=5)" in out
    assert "Overall EN: 80.0% (4 PASS, 0 PARTIAL, 1 FAIL, n=5)" in out
    assert "Delta (EN-PL): -10.0 pp" in out
    assert "semantic n=2" in out
    assert "exact n=1" in out
    assert "U01  semantic  PL PASS@1  EN FAIL@-" in out
    assert "U05  mixed  PL PASS@1  EN PASS@2" in out
    assert "Expected:" not in out
    assert "nieudanych" not in out


def test_lang_both_verbose_prints_each_pass(capsys, monkeypatch, tmp_path):
    """--verbose adds the full per-language report for each pass."""
    suite = tmp_path / "suite.yaml"
    _write_text(suite, _BOTH_SUITE)

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        return _nodes_for(query)

    _patch_index(monkeypatch, fake_run_query)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "both",
            "--verbose",
        ],
    )
    with pytest.warns(UserWarning, match="U04"):
        validate_rag.main()
    out = capsys.readouterr().out
    assert "lang=pl" in out
    assert "lang=en" in out
    assert "nieudanych" in out
    assert "Expected:" in out
    assert "Delta (EN-PL):" in out


def test_lang_pl_json_has_lang_keys(capsys, monkeypatch, tmp_path):
    """--lang pl adds the top-level and per-test lang keys."""
    suite = tmp_path / "suite.yaml"
    _write_text(
        suite,
        """\
- id: U01
  category: Uploads
  description: d
  query_pl: "Gdzie jest logika ponawiania nieudanych wysyłek?"
  query_en: "Where is the retry logic for failed uploads?"
  criteria:
    text_pattern: "retry"
- id: L1
  category: Neutral
  description: d
  query: "shared neutral question"
  criteria: {}
""",
    )

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        if query.startswith("Gdzie"):
            return [_Hit("retry", "src/upload_queue.py")]
        return []

    state = _patch_index(monkeypatch, fake_run_query)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "pl",
            "--json",
        ],
    )
    validate_rag.main()
    data = json.loads(capsys.readouterr().out)
    assert state["setup"] == 1
    assert data["lang"] == "pl"
    by_id = {row["id"]: row for row in data["tests"]}
    assert by_id["U01"]["lang"] == "pl"
    assert by_id["U01"]["query"].startswith("Gdzie")
    assert by_id["U01"]["result"] == "PASS"
    assert by_id["L1"]["lang"] is None
    assert by_id["L1"]["query"] == "shared neutral question"
    assert "changed_tests" not in data


def test_lang_both_legacy_suite_notes_and_matches(capsys, monkeypatch, tmp_path):
    """A neutral suite may run both passes; stderr says there is nothing to compare."""
    suite = tmp_path / "suite.yaml"
    _write_text(
        suite,
        """\
- id: L1
  category: Neutral
  description: d
  query: "shared neutral question"
  criteria:
    text_pattern: "neutral"
    max_position: 1
""",
    )

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        assert query == "shared neutral question"
        return [_Hit("neutral", "docs/notes.md")]

    state = _patch_index(monkeypatch, fake_run_query)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "both",
            "--json",
        ],
    )
    validate_rag.main()
    captured = capsys.readouterr()
    assert "no language-specific queries" in captured.err
    data = json.loads(captured.out)
    assert state["setup"] == 1
    assert data["delta"]["score_pct"] == 0.0
    assert data["changed_tests"] == []
    assert data["fallback_tests"] == {"pl": [], "en": []}
    assert data["pl"]["tests"][0]["query"] == data["en"]["tests"][0]["query"]
    assert data["pl"]["tests"][0]["lang"] is None


def test_lang_both_respects_test_and_category(capsys, monkeypatch, tmp_path):
    """--test and --category limit both passes to the same tests."""
    suite = tmp_path / "suite.yaml"
    _write_text(suite, _BOTH_SUITE)
    queries = []

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        queries.append(query)
        return _nodes_for(query)

    _patch_index(monkeypatch, fake_run_query)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "both",
            "--json",
            "--test",
            "U05",
        ],
    )
    # Loading still sees U04, which has no Polish query, so one warning fires
    # before --test drops that case.
    with pytest.warns(UserWarning, match="U04"):
        validate_rag.main()
    data = json.loads(capsys.readouterr().out)
    assert [row["id"] for row in data["pl"]["tests"]] == ["U05"]
    assert [row["id"] for row in data["en"]["tests"]] == ["U05"]
    assert data["delta"]["score_pct"] == 0.0
    assert data["changed_tests"][0]["id"] == "U05"
    assert len(queries) == 2

    queries.clear()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "both",
            "--json",
            "--category",
            "Uploads",
        ],
    )
    with pytest.warns(UserWarning, match="U04"):
        validate_rag.main()
    data = json.loads(capsys.readouterr().out)
    assert [row["id"] for row in data["pl"]["tests"]] == ["U01", "U02"]
    assert "Neutral" not in data["delta"]["by_category"]
    assert "Uploads" in data["delta"]["by_category"]


def test_lang_both_diag_rank_runs_on_each_pass(capsys, monkeypatch, tmp_path):
    """--diag-rank is a second search on the Polish pass and the English pass."""
    suite = tmp_path / "suite.yaml"
    _write_text(
        suite,
        """\
- id: U01
  category: Uploads
  description: d
  query_pl: "Gdzie jest logika ponawiania nieudanych wysyłek?"
  query_en: "Where is the retry logic for failed uploads?"
  criteria:
    text_pattern: "missing-token"
""",
    )
    calls = []

    def fake_run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None):
        calls.append(top_k)
        return []

    state = _patch_index(monkeypatch, fake_run_query)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "both",
            "--json",
            "--diag-rank",
            "4",
            "--top-k",
            "8",
        ],
    )
    validate_rag.main()
    data = json.loads(capsys.readouterr().out)
    assert state["setup"] == 1
    assert calls == [8, 4, 8, 4]
    assert data["pl"]["tests"][0]["diag_top3_files"] == []
    assert data["en"]["tests"][0]["diag_rank"] is None


def test_strict_lang_list_passes_without_index(capsys, monkeypatch, tmp_path):
    """--strict-lang --list lints a complete suite and shows both languages."""
    suite = tmp_path / "suite.yaml"
    _write_text(
        suite,
        """\
- id: U01
  category: Uploads
  description: d
  difficulty: Easy
  aspect: Sparse
  query_pl: "Gdzie jest logika ponawiania nieudanych wysyłek?"
  query_en: "Where is the retry logic for failed uploads?"
  criteria: {}
""",
    )

    def explode(**kwargs):
        raise AssertionError("index setup must not run")

    monkeypatch.setattr(validate_rag, "setup", explode)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--lang",
            "both",
            "--strict-lang",
            "--list",
        ],
    )
    validate_rag.main()
    out = capsys.readouterr().out
    assert "[pl,en]" in out
    assert "PL: Gdzie jest logika ponawiania nieudanych wysyłek?" in out
    assert "EN: Where is the retry logic for failed uploads?" in out
    assert "Total: 1 tests" in out


def test_strict_lang_list_fails_with_every_id(capsys, monkeypatch, tmp_path):
    """--strict-lang --list exits 1 and names every incomplete test."""
    suite = tmp_path / "suite.yaml"
    _write_text(
        suite,
        """\
- id: T01
  category: Cat
  description: d
  query: neutral only
  criteria: {}
- id: T02
  category: Cat
  description: d
  query_pl: "Gdzie jest kolejka?"
  criteria: {}
- id: T03
  category: Cat
  description: d
  query_en: "Where is the queue?"
  criteria: {}
- id: T04
  category: Cat
  description: d
  query_pl: "Gdzie?"
  query_en: "Where?"
  criteria: {}
""",
    )

    def explode(**kwargs):
        raise AssertionError("index setup must not run")

    monkeypatch.setattr(validate_rag, "setup", explode)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--strict-lang",
            "--list",
        ],
    )
    with pytest.raises(SystemExit) as caught:
        validate_rag.main()
    assert caught.value.code == 1
    err = capsys.readouterr().err
    assert "T01" in err
    assert "T02" in err
    assert "T03" in err
    assert "T04" not in err
    assert "missing query_pl or query_en" in err


def test_strict_lang_list_fails_on_duplicate_ids(capsys, monkeypatch, tmp_path):
    """Duplicate ids fail the lint even when every test has both languages."""
    suite = tmp_path / "suite.yaml"
    _write_text(
        suite,
        """\
- id: DUP
  category: Uploads
  description: d
  query_pl: "Gdzie jest klasa UploadQueue?"
  query_en: "Where is class UploadQueue?"
  criteria: {}
- id: DUP
  category: Uploads
  description: d
  query_pl: "Gdzie jest inna klasa?"
  query_en: "Where is the other class?"
  criteria: {}
""",
    )
    def explode(**kwargs):
        raise AssertionError("index setup must not run")

    monkeypatch.setattr(validate_rag, "setup", explode)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rag.py",
            "--config",
            "config_not_in_this_repo",
            "--tests",
            str(suite),
            "--strict-lang",
            "--list",
        ],
    )
    with pytest.raises(SystemExit) as caught:
        validate_rag.main()
    assert caught.value.code == 1
    err = capsys.readouterr().err
    assert "duplicate test ids: DUP" in err
    assert "missing query_pl" not in err
