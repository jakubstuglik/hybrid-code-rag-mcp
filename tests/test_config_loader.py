"""
Tests for config_loader.py — config loading with optional overrides.

Tests cover:
    - get_config(): no override returns base config
    - config_path argument: .py file, directory, non-.py file
    - config_name argument: name-based resolution
    - RAG_CONFIG environment variable fallback
    - Priority: config_path > config_name > env var
    - Merging: override values merge over base, unset values preserved
    - Function rebinding: rebound functions see merged module globals
    - Error handling: spec is None, spec.loader is None, exec_module raises
    - Edge cases: override file doesn't exist, empty override
    - Integration: full integration using real config files from repo
"""

import builtins
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import config_loader as loader_module
from config_loader import get_config


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────

_real_import = builtins.__import__


def _make_fake_base_config(**kwargs) -> types.ModuleType:
    """Create a fake base config module with sensible defaults.

    Any keyword arguments override the defaults.
    """
    mod = types.ModuleType("config")
    mod.BASE_PATH = "./qdrant"
    mod.MODEL_PATH = "index_bge_m3"
    mod.COLLECTION_NAME = "informica_rag"
    mod.QDRANT_PORT = 6333
    mod.MCP_SERVER_NAME = "informica-rag"
    mod.MCP_TOOL_NAME = "search_informica"
    mod.SOURCE_DIRS = [{"path": "source", "extensions": [".pas"]}]
    mod.UNIQUE_BASE_ATTR = "only_in_base"

    def get_index_path() -> str:
        return f"{BASE_PATH}/{MODEL_PATH}"  # noqa: F821

    def get_qdrant_path() -> str:
        return f"{BASE_PATH}/{MODEL_PATH}"  # noqa: F821

    # Bind these functions with the module dict as globals so rebinding works
    mod.get_index_path = types.FunctionType(
        get_index_path.__code__, mod.__dict__, "get_index_path"
    )
    mod.get_qdrant_path = types.FunctionType(
        get_qdrant_path.__code__, mod.__dict__, "get_qdrant_path"
    )
    mod.__dict__.update(kwargs)
    return mod


def _write_override_config(path: Path, content: str) -> Path:
    """Write a config.py override file and return its path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _patch_base_import(fake_base):
    """Return a context manager that patches __import__ to return fake_base for 'config'."""

    def _patched_import(name, *args, **kwargs):
        if name == "config":
            return fake_base
        return _real_import(name, *args, **kwargs)

    return patch("builtins.__import__", side_effect=_patched_import)


# ────────────────────────────────────────────────
# TestGetConfigNoOverride
# ────────────────────────────────────────────────


class TestGetConfigNoOverride:
    """Tests for get_config() with no override — returns base config."""

    def test_no_args_returns_base_config(self, monkeypatch):
        """get_config() with no arguments returns the base config module."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()
        assert result is fake_base

    def test_no_args_has_base_attributes(self, monkeypatch):
        """Returned base config has expected attributes."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()
        assert result.BASE_PATH == "./qdrant"
        assert result.COLLECTION_NAME == "informica_rag"
        assert result.QDRANT_PORT == 6333

    def test_no_override_when_env_not_set(self, monkeypatch):
        """With no args and no RAG_CONFIG env var, returns base config."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()
        assert result is fake_base


# ────────────────────────────────────────────────
# TestGetConfigWithConfigPath
# ────────────────────────────────────────────────


class TestGetConfigWithConfigPath:
    """Tests for get_config(config_path=...) — direct file/directory path."""

    def test_config_path_py_file(self, tmp_path):
        """config_path pointing to a .py file loads that file as override."""
        override_file = tmp_path / "custom_config.py"
        _write_override_config(override_file, "QDRANT_PORT = 9999\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.QDRANT_PORT == 9999

    def test_config_path_directory(self, tmp_path):
        """config_path pointing to a directory loads dir/config.py."""
        override_dir = tmp_path / "my-config"
        override_dir.mkdir()
        _write_override_config(
            override_dir / "config.py", "COLLECTION_NAME = 'custom_collection'\n"
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_dir))

        assert result.COLLECTION_NAME == "custom_collection"

    def test_config_path_non_py_suffix_treated_as_dir(self, tmp_path):
        """config_path with non-.py suffix is treated as directory name."""
        override_dir = tmp_path / "self-index"
        override_dir.mkdir()
        _write_override_config(
            override_dir / "config.py", "MCP_SERVER_NAME = 'self-rag'\n"
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_dir))

        assert result.MCP_SERVER_NAME == "self-rag"

    def test_config_path_no_suffix_appends_config_py(self, tmp_path):
        """A config_path without .py extension gets /config.py appended."""
        override_dir = tmp_path / "myconfig"
        override_dir.mkdir()
        _write_override_config(
            override_dir / "config.py", "BASE_PATH = 'custom-path'\n"
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_dir))

        assert result.BASE_PATH == "custom-path"

    def test_config_path_nonexistent_file_returns_base(self, tmp_path):
        """config_path to a non-existent .py file returns base config."""
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(tmp_path / "nonexistent.py"))
        assert result is fake_base

    def test_config_path_nonexistent_dir_returns_base(self, tmp_path):
        """config_path to a non-existent directory returns base config."""
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(
                config_path=str(tmp_path / "no_such_dir" / "config.py")
            )
        assert result is fake_base


# ────────────────────────────────────────────────
# TestGetConfigWithConfigName
# ────────────────────────────────────────────────


class TestGetConfigWithConfigName:
    """Tests for get_config(config_name=...) — name-based config resolution."""

    def test_config_name_resolves_to_name_slash_config_py(self, tmp_path, monkeypatch):
        """config_name='x' loads './x/config.py'."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        override_dir = tmp_path / "my-override"
        override_dir.mkdir()
        _write_override_config(
            override_dir / "config.py", "QDRANT_PORT = 7777\n"
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name=str(override_dir))

        assert result.QDRANT_PORT == 7777

    def test_config_name_nonexistent_returns_base(self, monkeypatch):
        """config_name pointing to non-existent dir returns base config."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name="nonexistent-config-dir")
        assert result is fake_base


# ────────────────────────────────────────────────
# TestGetConfigWithEnvVar
# ────────────────────────────────────────────────


class TestGetConfigWithEnvVar:
    """Tests for get_config() with RAG_CONFIG environment variable."""

    def test_env_var_loads_override(self, tmp_path, monkeypatch):
        """RAG_CONFIG env var points to a directory with config.py."""
        override_dir = tmp_path / "env-config"
        override_dir.mkdir()
        _write_override_config(
            override_dir / "config.py", "COLLECTION_NAME = 'env_collection'\n"
        )
        monkeypatch.setenv("RAG_CONFIG", str(override_dir))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()

        assert result.COLLECTION_NAME == "env_collection"

    def test_env_var_nonexistent_returns_base(self, monkeypatch):
        """RAG_CONFIG pointing to non-existent dir returns base config."""
        monkeypatch.setenv("RAG_CONFIG", "/nonexistent/path")
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()
        assert result is fake_base

    def test_env_var_not_set_returns_base(self, monkeypatch):
        """No RAG_CONFIG env var and no args returns base config."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()
        assert result is fake_base


# ────────────────────────────────────────────────
# TestGetConfigPriority
# ────────────────────────────────────────────────


class TestGetConfigPriority:
    """Tests for argument priority: config_path > config_name > env var."""

    def test_config_path_beats_config_name(self, tmp_path, monkeypatch):
        """config_path takes priority over config_name."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)

        path_dir = tmp_path / "from-path"
        path_dir.mkdir()
        _write_override_config(
            path_dir / "config.py", "QDRANT_PORT = 1111\n"
        )

        name_dir = tmp_path / "from-name"
        name_dir.mkdir()
        _write_override_config(
            name_dir / "config.py", "QDRANT_PORT = 2222\n"
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(
                config_path=str(path_dir), config_name=str(name_dir)
            )

        assert result.QDRANT_PORT == 1111

    def test_config_name_beats_env_var(self, tmp_path, monkeypatch):
        """config_name takes priority over RAG_CONFIG env var."""
        name_dir = tmp_path / "from-name"
        name_dir.mkdir()
        _write_override_config(
            name_dir / "config.py", "QDRANT_PORT = 2222\n"
        )

        env_dir = tmp_path / "from-env"
        env_dir.mkdir()
        _write_override_config(
            env_dir / "config.py", "QDRANT_PORT = 3333\n"
        )
        monkeypatch.setenv("RAG_CONFIG", str(env_dir))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name=str(name_dir))

        assert result.QDRANT_PORT == 2222

    def test_config_path_beats_env_var(self, tmp_path, monkeypatch):
        """config_path takes priority over RAG_CONFIG env var."""
        path_dir = tmp_path / "from-path"
        path_dir.mkdir()
        _write_override_config(
            path_dir / "config.py", "QDRANT_PORT = 1111\n"
        )

        env_dir = tmp_path / "from-env"
        env_dir.mkdir()
        _write_override_config(
            env_dir / "config.py", "QDRANT_PORT = 3333\n"
        )
        monkeypatch.setenv("RAG_CONFIG", str(env_dir))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(path_dir))

        assert result.QDRANT_PORT == 1111

    def test_all_three_set_config_path_wins(self, tmp_path, monkeypatch):
        """When all three sources are set, config_path wins."""
        path_dir = tmp_path / "from-path"
        path_dir.mkdir()
        _write_override_config(
            path_dir / "config.py", "QDRANT_PORT = 1111\n"
        )

        name_dir = tmp_path / "from-name"
        name_dir.mkdir()
        _write_override_config(
            name_dir / "config.py", "QDRANT_PORT = 2222\n"
        )

        env_dir = tmp_path / "from-env"
        env_dir.mkdir()
        _write_override_config(
            env_dir / "config.py", "QDRANT_PORT = 3333\n"
        )
        monkeypatch.setenv("RAG_CONFIG", str(env_dir))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(
                config_path=str(path_dir), config_name=str(name_dir)
            )

        assert result.QDRANT_PORT == 1111

    def test_env_var_used_when_no_args(self, tmp_path, monkeypatch):
        """When no args are passed, RAG_CONFIG env var is used."""
        env_dir = tmp_path / "from-env"
        env_dir.mkdir()
        _write_override_config(
            env_dir / "config.py", "QDRANT_PORT = 3333\n"
        )
        monkeypatch.setenv("RAG_CONFIG", str(env_dir))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()

        assert result.QDRANT_PORT == 3333


# ────────────────────────────────────────────────
# TestGetConfigMerging
# ────────────────────────────────────────────────


class TestGetConfigMerging:
    """Tests for config merging — override values merge over base."""

    def test_override_replaces_base_values(self, tmp_path):
        """Override attributes replace base config attributes."""
        override_file = tmp_path / "override.py"
        _write_override_config(
            override_file,
            "QDRANT_PORT = 9999\nCOLLECTION_NAME = 'override_collection'\n",
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.QDRANT_PORT == 9999
        assert result.COLLECTION_NAME == "override_collection"

    def test_base_values_preserved_when_not_overridden(self, tmp_path):
        """Base config attributes not in the override are preserved."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "QDRANT_PORT = 9999\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        # Overridden
        assert result.QDRANT_PORT == 9999
        # Preserved from base
        assert result.BASE_PATH == "./qdrant"
        assert result.MODEL_PATH == "index_bge_m3"
        assert result.MCP_SERVER_NAME == "informica-rag"
        assert result.UNIQUE_BASE_ATTR == "only_in_base"

    def test_override_adds_new_attributes(self, tmp_path):
        """Override can add attributes not present in base config."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "NEW_OVERRIDE_ATTR = 'hello'\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.NEW_OVERRIDE_ATTR == "hello"
        # Base attrs still there
        assert result.BASE_PATH == "./qdrant"

    def test_merged_module_is_new_object(self, tmp_path):
        """The merged config is a new ModuleType, not the base or override."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "QDRANT_PORT = 9999\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result is not fake_base
        assert isinstance(result, types.ModuleType)

    def test_merged_source_dirs_override(self, tmp_path):
        """Override SOURCE_DIRS fully replaces base SOURCE_DIRS."""
        override_file = tmp_path / "override.py"
        _write_override_config(
            override_file,
            'SOURCE_DIRS = [{"path": ".", "extensions": [".py"]}]\n',
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.SOURCE_DIRS == [{"path": ".", "extensions": [".py"]}]

    def test_merged_module_name_is_overwritten_by_override(self, tmp_path):
        """The merged module's __name__ is 'config_override' (from override module)."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "QDRANT_PORT = 9999\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        # merged.__dict__.update(override_mod.__dict__) overwrites __name__
        # because override_mod.__name__ == "config_override" (from spec_from_file_location)
        assert result.__name__ == "config_override"


# ────────────────────────────────────────────────
# TestGetConfigFunctionRebinding
# ────────────────────────────────────────────────


class TestGetConfigFunctionRebinding:
    """Tests for function rebinding — rebound functions see merged globals."""

    def test_rebound_function_uses_overridden_globals(self, tmp_path):
        """Functions in merged config see overridden attribute values."""
        override_file = tmp_path / "override.py"
        _write_override_config(
            override_file,
            "BASE_PATH = 'self-index'\nMODEL_PATH = 'index_rag_self'\n",
        )

        fake_base = _make_fake_base_config()

        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        # The rebound functions should see the overridden globals
        assert result.get_index_path() == "self-index/index_rag_self"
        assert result.get_qdrant_path() == "self-index/index_rag_self"

    def test_rebound_function_sees_base_values_for_non_overridden(self, tmp_path):
        """Rebound functions still see base values for non-overridden attributes."""
        override_file = tmp_path / "override.py"
        _write_override_config(
            override_file,
            "BASE_PATH = 'custom-path'\n",  # Only override BASE_PATH, not MODEL_PATH
        )

        fake_base = _make_fake_base_config()

        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        # BASE_PATH overridden, MODEL_PATH from base
        assert result.get_index_path() == "custom-path/index_bge_m3"

    def test_functions_are_rebound_as_new_objects(self, tmp_path):
        """Rebound functions are new FunctionType objects, not the originals."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "QDRANT_PORT = 9999\n")

        fake_base = _make_fake_base_config()
        original_func = fake_base.get_index_path

        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.get_index_path is not original_func
        assert callable(result.get_index_path)

    def test_function_with_defaults_preserved(self, tmp_path):
        """Function default parameter values are preserved after rebinding."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "QDRANT_PORT = 9999\n")

        fake_base = _make_fake_base_config()

        def my_func(x: int = 42) -> int:
            return x

        fake_base.my_func = my_func

        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.my_func() == 42
        assert result.my_func(100) == 100

    def test_non_function_attributes_not_rebound(self, tmp_path):
        """Non-function attributes (ints, strings, lists) are not affected by rebinding."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "QDRANT_PORT = 5555\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.QDRANT_PORT == 5555
        assert isinstance(result.QDRANT_PORT, int)
        assert result.BASE_PATH == "./qdrant"
        assert isinstance(result.BASE_PATH, str)

    def test_override_can_define_new_function(self, tmp_path):
        """A function defined in the override is available and rebound."""
        override_file = tmp_path / "override.py"
        _write_override_config(
            override_file,
            "CUSTOM_VAL = 'abc'\ndef custom_func():\n    return CUSTOM_VAL\n",
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.custom_func() == "abc"


# ────────────────────────────────────────────────
# TestGetConfigErrorHandling
# ────────────────────────────────────────────────


class TestGetConfigErrorHandling:
    """Tests for error handling — spec None, loader None, exec_module failure."""

    @patch.object(loader_module, "log_warn")
    def test_spec_is_none_returns_base_and_warns(self, mock_warn, tmp_path):
        """When spec_from_file_location returns None, return base config and warn."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "X = 1\n")

        fake_base = _make_fake_base_config()
        with (
            _patch_base_import(fake_base),
            patch(
                "config_loader.spec_from_file_location", return_value=None
            ),
        ):
            result = get_config(config_path=str(override_file))

        assert result is fake_base
        mock_warn.assert_called_once()
        assert "Could not load config" in mock_warn.call_args[0][0]

    @patch.object(loader_module, "log_warn")
    def test_spec_loader_is_none_returns_base_and_warns(self, mock_warn, tmp_path):
        """When spec.loader is None, return base config and warn."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "X = 1\n")

        fake_spec = MagicMock()
        fake_spec.loader = None

        fake_base = _make_fake_base_config()
        with (
            _patch_base_import(fake_base),
            patch(
                "config_loader.spec_from_file_location", return_value=fake_spec
            ),
        ):
            result = get_config(config_path=str(override_file))

        assert result is fake_base
        mock_warn.assert_called_once()
        assert "Could not load config" in mock_warn.call_args[0][0]

    @patch.object(loader_module, "log_warn")
    def test_exec_module_raises_returns_base_and_warns(self, mock_warn, tmp_path):
        """When spec.loader.exec_module raises, return base config and warn."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "X = 1\n")

        fake_spec = MagicMock()
        fake_spec.loader.exec_module.side_effect = SyntaxError("bad syntax")

        fake_base = _make_fake_base_config()
        with (
            _patch_base_import(fake_base),
            patch(
                "config_loader.spec_from_file_location", return_value=fake_spec
            ),
        ):
            result = get_config(config_path=str(override_file))

        assert result is fake_base
        mock_warn.assert_called_once()
        assert "Error loading" in mock_warn.call_args[0][0]
        assert "bad syntax" in mock_warn.call_args[0][0]

    @patch.object(loader_module, "log_warn")
    def test_exec_module_runtime_error(self, mock_warn, tmp_path):
        """A RuntimeError during exec_module is caught and returns base config."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "X = 1\n")

        fake_spec = MagicMock()
        fake_spec.loader.exec_module.side_effect = RuntimeError("import failed")

        fake_base = _make_fake_base_config()
        with (
            _patch_base_import(fake_base),
            patch(
                "config_loader.spec_from_file_location", return_value=fake_spec
            ),
        ):
            result = get_config(config_path=str(override_file))

        assert result is fake_base
        mock_warn.assert_called_once()
        assert "Error loading" in mock_warn.call_args[0][0]

    @patch.object(loader_module, "log_warn")
    def test_override_with_syntax_error_in_real_file(self, mock_warn, tmp_path):
        """A config file with a Python syntax error is handled gracefully."""
        override_file = tmp_path / "bad_config.py"
        _write_override_config(override_file, "QDRANT_PORT = !!invalid!!\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result is fake_base
        mock_warn.assert_called_once()


# ────────────────────────────────────────────────
# TestGetConfigEdgeCases
# ────────────────────────────────────────────────


class TestGetConfigEdgeCases:
    """Tests for edge cases — missing files, empty overrides, etc."""

    def test_override_file_does_not_exist_returns_base(self, tmp_path):
        """When the resolved override path doesn't exist, return base config."""
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(tmp_path / "does_not_exist.py"))
        assert result is fake_base

    def test_empty_override_file_returns_merged(self, tmp_path):
        """An empty override file merges nothing — result has all base attrs."""
        override_file = tmp_path / "empty_override.py"
        _write_override_config(override_file, "")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        # Should be a merged module (not the base itself) but with base values
        assert result is not fake_base
        assert result.BASE_PATH == "./qdrant"
        assert result.QDRANT_PORT == 6333
        assert result.COLLECTION_NAME == "informica_rag"

    def test_config_path_empty_string_returns_base(self, monkeypatch):
        """Empty string config_path is falsy, falls through to base."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path="")
        assert result is fake_base

    def test_config_name_empty_string_returns_base(self, monkeypatch):
        """Empty string config_name is falsy, falls through to base."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name="")
        assert result is fake_base

    def test_config_path_is_directory_without_config_py(self, tmp_path):
        """config_path pointing to a dir without config.py returns base."""
        empty_dir = tmp_path / "empty-dir"
        empty_dir.mkdir()

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(empty_dir))
        assert result is fake_base

    def test_override_with_only_comments(self, tmp_path):
        """An override file with only comments merges nothing special."""
        override_file = tmp_path / "comments_only.py"
        _write_override_config(
            override_file, "# This is a comment\n# Another comment\n"
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.BASE_PATH == "./qdrant"
        assert result.QDRANT_PORT == 6333

    def test_config_path_with_py_suffix_used_directly(self, tmp_path):
        """A .py path is used directly without appending /config.py."""
        override_file = tmp_path / "my_custom.py"
        _write_override_config(override_file, "QDRANT_PORT = 4444\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.QDRANT_PORT == 4444

    def test_config_name_with_nested_path(self, tmp_path):
        """config_name with a nested path (e.g. 'a/b') resolves correctly."""
        nested_dir = tmp_path / "a" / "b"
        nested_dir.mkdir(parents=True)
        _write_override_config(
            nested_dir / "config.py", "QDRANT_PORT = 8888\n"
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name=str(nested_dir))

        assert result.QDRANT_PORT == 8888

    def test_override_can_set_none_value(self, tmp_path):
        """Override can set an attribute to None."""
        override_file = tmp_path / "none_val.py"
        _write_override_config(override_file, "MCP_SERVER_NAME = None\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.MCP_SERVER_NAME is None

    def test_config_path_non_py_non_dir_appends_config_py(self, tmp_path):
        """config_path that is a non-.py file (not a dir) appends /config.py."""
        # Path like "self-index" that doesn't exist as a dir and has no .py suffix
        # will try Path("self-index") / "config.py" -- which won't exist, so base returned
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path="nonexistent-thing")
        assert result is fake_base


# ────────────────────────────────────────────────
# TestIntegration
# ────────────────────────────────────────────────


class TestIntegration:
    """Integration tests using real config.py and self-index/config.py from the repo."""

    def test_real_base_config_loads(self, monkeypatch):
        """Loading with no override returns the real base config."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        result = get_config()
        assert result.BASE_PATH == "./qdrant"
        assert result.COLLECTION_NAME == "informica_rag"
        assert result.QDRANT_PORT == 6333
        assert result.MCP_SERVER_NAME == "informica-rag"

    def test_real_base_config_has_functions(self, monkeypatch):
        """Real base config has get_index_path and get_qdrant_path functions."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        result = get_config()
        assert callable(result.get_index_path)
        assert callable(result.get_qdrant_path)
        assert result.get_index_path() == f"{result.BASE_PATH}/{result.MODEL_PATH}"

    def test_real_self_index_override_by_path(self):
        """Loading self-index override via config_path merges correctly."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_path="self-index/config.py")
        # Overridden values
        assert result.BASE_PATH == "self-index"
        assert result.COLLECTION_NAME == "self_rag_index"
        assert result.QDRANT_PORT == 6973
        assert result.MCP_SERVER_NAME == "self-rag"
        assert result.MCP_TOOL_NAME == "search_self_rag"

    def test_real_self_index_override_by_name(self):
        """Loading self-index override via config_name merges correctly."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_name="self-index")
        assert result.BASE_PATH == "self-index"
        assert result.COLLECTION_NAME == "self_rag_index"
        assert result.MCP_SERVER_NAME == "self-rag"

    def test_real_self_index_override_by_directory_path(self):
        """Loading self-index override via directory config_path merges correctly."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_path="self-index")
        assert result.BASE_PATH == "self-index"
        assert result.COLLECTION_NAME == "self_rag_index"

    def test_real_self_index_preserves_base_attrs(self):
        """Self-index override preserves base attrs not in the override."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_name="self-index")
        # These are in base config but NOT overridden by self-index
        assert result.MODEL_NAME == "BAAI/bge-m3"
        assert result.EMBED_BATCH_SIZE == 32
        assert result.HYBRID_ALPHA == 0.5
        assert result.MCP_HOST == "0.0.0.0"

    def test_real_self_index_function_rebinding(self):
        """Rebound functions in self-index config use overridden BASE_PATH."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_name="self-index")
        # get_index_path() should use overridden BASE_PATH and MODEL_PATH
        assert result.get_index_path() == f"{result.BASE_PATH}/{result.MODEL_PATH}"
        assert result.get_qdrant_path() == f"{result.BASE_PATH}/{result.MODEL_PATH}"

    def test_real_merged_is_module_type(self):
        """Real merged config is a ModuleType."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_name="self-index")
        assert isinstance(result, types.ModuleType)

    def test_real_nonexistent_config_name_returns_base(self, monkeypatch):
        """A non-existent config_name returns base config unchanged."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        result = get_config(config_name="this-dir-does-not-exist-at-all")
        assert result.BASE_PATH == "./qdrant"
        assert result.COLLECTION_NAME == "informica_rag"
