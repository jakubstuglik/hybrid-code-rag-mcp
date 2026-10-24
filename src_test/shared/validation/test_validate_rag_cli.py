"""CLI test: validate_rag.py --tests loads a caller-supplied suite.

--list returns before index setup, so this does not contact Qdrant.
The diagnostic-rank test mocks retrieval so it does not contact Qdrant either.
"""

import json
import os
import sys
import tempfile
import types

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
