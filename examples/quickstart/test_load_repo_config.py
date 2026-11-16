# SPDX-License-Identifier: Apache-2.0
"""Unit tests for examples/quickstart/load_repo_config.py."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from load_repo_config import (
    RepoConfigError,
    apply_to_globals,
    config_hash,
    main,
    resolve_source_dirs,
    validate,
)


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_validate_accepts_allowed_keys(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "repo_config.py",
        "SOURCE_DIRS = [{'path': 'src', 'extensions': ['.py']}]\n"
        "MCP_SERVER_NAME = 'myshop-rag'\n"
        "MCP_TOOL_NAME = 'search_myshop'\n"
        "MCP_TOOL_DESCRIPTION = 'Search myshop.'\n"
        "MCP_INDEX_STATE_TOOL_NAME = 'get_myshop_index_state'\n"
        "MCP_INDEX_STATE_EXTRA = 'ok'\n",
    )
    overrides = validate(path)
    assert overrides["MCP_TOOL_NAME"] == "search_myshop"
    assert overrides["MCP_INDEX_STATE_EXTRA"] == "ok"


def test_syntax_error_is_clear(tmp_path: Path) -> None:
    path = _write(tmp_path / "bad.py", "SOURCE_DIRS = [\n")
    with pytest.raises(RepoConfigError, match="syntax error") as excinfo:
        validate(path)
    assert "Traceback" not in str(excinfo.value)
    assert path.name in str(excinfo.value)


def test_missing_file_is_clear(tmp_path: Path) -> None:
    missing = tmp_path / "nope.py"
    with pytest.raises(RepoConfigError, match="does not exist"):
        validate(missing)


def test_infrastructure_key_is_rejected(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "repo_config.py",
        "MCP_TOOL_NAME = 'search_myshop'\n"
        "QDRANT_HOST = 'localhost'\n"
        "TEI_DTYPE = 'float16'\n",
    )
    with pytest.raises(RepoConfigError, match="infrastructure keys") as excinfo:
        validate(path)
    message = str(excinfo.value)
    assert "QDRANT_HOST" in message
    assert "TEI_DTYPE" in message
    assert "CPU/GPU" in message


def test_collection_name_is_rejected(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "repo_config.py",
        "MCP_TOOL_NAME = 'search_myshop'\n"
        "COLLECTION_NAME = 'myshop_rag'\n",
    )
    with pytest.raises(RepoConfigError, match="infrastructure keys") as excinfo:
        validate(path)
    assert "COLLECTION_NAME" in str(excinfo.value)


def test_unknown_key_is_rejected(tmp_path: Path) -> None:
    path = _write(tmp_path / "repo_config.py", "INDEX_PARSE_WORKERS = 8\n")
    with pytest.raises(RepoConfigError, match="unknown keys") as excinfo:
        validate(path)
    assert "INDEX_PARSE_WORKERS" in str(excinfo.value)
    assert "SOURCE_DIRS" in str(excinfo.value)


def test_resolve_source_dirs_joins_repo_root(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "docs").mkdir()
    resolved = resolve_source_dirs(
        [
            {"path": "src", "extensions": [".py"], "exclude": ["tests"]},
            {"path": "docs", "extensions": [".md"]},
        ],
        root,
    )
    assert resolved[0]["path"] == str((root / "src").resolve())
    assert resolved[0]["exclude"] == ["tests"]
    assert resolved[1]["path"] == str((root / "docs").resolve())


def test_resolve_source_dirs_rejects_escape(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    with pytest.raises(RepoConfigError, match="outside the repository root"):
        resolve_source_dirs([{"path": "../secret", "extensions": [".py"]}], root)


def test_apply_to_globals_overlays_and_resolves(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    path = _write(
        tmp_path / "repo_config.py",
        "SOURCE_DIRS = [{'path': 'src', 'extensions': ['.py']}]\n"
        "MCP_TOOL_NAME = 'search_myshop'\n",
    )
    target = {
        "SOURCE_DIRS": [{"path": str(root), "extensions": [".md"]}],
        "MCP_TOOL_NAME": "search_quickstart",
        "MCP_SERVER_NAME": "quickstart-rag",
    }
    apply_to_globals(target, path, root)
    assert target["MCP_TOOL_NAME"] == "search_myshop"
    assert target["MCP_SERVER_NAME"] == "quickstart-rag"
    assert target["SOURCE_DIRS"][0]["path"] == str((root / "src").resolve())


def test_config_hash_matches_sha256(tmp_path: Path) -> None:
    path = _write(tmp_path / "repo_config.py", "MCP_TOOL_NAME = 'search_myshop'\n")
    digest = config_hash(path)
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    assert main(["--hash", str(path)]) == 0


def test_main_validate_and_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = _write(tmp_path / "good.py", "MCP_TOOL_NAME = 'search_myshop'\n")
    assert main(["--validate", str(good)]) == 0
    missing = tmp_path / "missing.py"
    assert main(["--validate", str(missing)]) == 1
    err = capsys.readouterr().err
    assert "does not exist" in err
    assert "Traceback" not in err

    bad = _write(tmp_path / "bad.py", "def (\n")
    assert main(["--validate", str(bad)]) == 1
    err = capsys.readouterr().err
    assert "syntax error" in err
    assert "Traceback" not in err
