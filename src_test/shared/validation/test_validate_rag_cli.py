"""CLI test: validate_rag.py --tests loads a caller-supplied suite.

--list returns before index setup, so this does not contact Qdrant.
"""

import os
import sys
import tempfile

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
