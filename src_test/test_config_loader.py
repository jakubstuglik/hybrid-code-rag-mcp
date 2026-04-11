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

import config as base_config
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
    mod.COLLECTION_NAME = "myproject_rag"
    mod.QDRANT_PORT = 6333
    mod.MCP_SERVER_NAME = "myproject-rag"
    mod.MCP_TOOL_NAME = "search_myproject"
    mod.SOURCE_DIRS = [{"path": "source", "extensions": [".pas"]}]
    mod.QDRANT_MODE = "local"
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
    """Tests for get_config() with no override — raises RuntimeError (config.py is not standalone)."""

    def test_no_args_raises(self, monkeypatch):
        """get_config() with no arguments raises RuntimeError — config.py cannot run standalone."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="No project config specified"):
                get_config()

    def test_no_args_error_message_mentions_config_flag(self, monkeypatch):
        """Error message tells the user to pass --config."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="--config"):
                get_config()

    def test_no_override_when_env_not_set_raises(self, monkeypatch):
        """With no args and no RAG_CONFIG env var, raises RuntimeError."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="No project config specified"):
                get_config()


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

    def test_config_path_nonexistent_file_raises(self, tmp_path):
        """config_path to a non-existent .py file raises RuntimeError."""
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="Project config not found"):
                get_config(config_path=str(tmp_path / "nonexistent.py"))

    def test_config_path_nonexistent_dir_raises(self, tmp_path):
        """config_path to a non-existent directory raises RuntimeError."""
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="Project config not found"):
                get_config(config_path=str(tmp_path / "no_such_dir" / "config.py"))


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
        _write_override_config(override_dir / "config.py", "QDRANT_PORT = 7777\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name=str(override_dir))

        assert result.QDRANT_PORT == 7777

    def test_config_name_nonexistent_raises(self, monkeypatch):
        """config_name pointing to non-existent dir raises RuntimeError."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="Project config not found"):
                get_config(config_name="nonexistent-config-dir")


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

    def test_env_var_nonexistent_raises(self, monkeypatch):
        """RAG_CONFIG pointing to non-existent dir raises RuntimeError."""
        monkeypatch.setenv("RAG_CONFIG", "/nonexistent/path")
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="Project config not found"):
                get_config()

    def test_env_var_not_set_raises(self, monkeypatch):
        """No RAG_CONFIG env var and no args raises RuntimeError."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="No project config specified"):
                get_config()


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
        _write_override_config(path_dir / "config.py", "QDRANT_PORT = 1111\n")

        name_dir = tmp_path / "from-name"
        name_dir.mkdir()
        _write_override_config(name_dir / "config.py", "QDRANT_PORT = 2222\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(path_dir), config_name=str(name_dir))

        assert result.QDRANT_PORT == 1111

    def test_config_name_beats_env_var(self, tmp_path, monkeypatch):
        """config_name takes priority over RAG_CONFIG env var."""
        name_dir = tmp_path / "from-name"
        name_dir.mkdir()
        _write_override_config(name_dir / "config.py", "QDRANT_PORT = 2222\n")

        env_dir = tmp_path / "from-env"
        env_dir.mkdir()
        _write_override_config(env_dir / "config.py", "QDRANT_PORT = 3333\n")
        monkeypatch.setenv("RAG_CONFIG", str(env_dir))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name=str(name_dir))

        assert result.QDRANT_PORT == 2222

    def test_config_path_beats_env_var(self, tmp_path, monkeypatch):
        """config_path takes priority over RAG_CONFIG env var."""
        path_dir = tmp_path / "from-path"
        path_dir.mkdir()
        _write_override_config(path_dir / "config.py", "QDRANT_PORT = 1111\n")

        env_dir = tmp_path / "from-env"
        env_dir.mkdir()
        _write_override_config(env_dir / "config.py", "QDRANT_PORT = 3333\n")
        monkeypatch.setenv("RAG_CONFIG", str(env_dir))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(path_dir))

        assert result.QDRANT_PORT == 1111

    def test_all_three_set_config_path_wins(self, tmp_path, monkeypatch):
        """When all three sources are set, config_path wins."""
        path_dir = tmp_path / "from-path"
        path_dir.mkdir()
        _write_override_config(path_dir / "config.py", "QDRANT_PORT = 1111\n")

        name_dir = tmp_path / "from-name"
        name_dir.mkdir()
        _write_override_config(name_dir / "config.py", "QDRANT_PORT = 2222\n")

        env_dir = tmp_path / "from-env"
        env_dir.mkdir()
        _write_override_config(env_dir / "config.py", "QDRANT_PORT = 3333\n")
        monkeypatch.setenv("RAG_CONFIG", str(env_dir))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(path_dir), config_name=str(name_dir))

        assert result.QDRANT_PORT == 1111

    def test_env_var_used_when_no_args(self, tmp_path, monkeypatch):
        """When no args are passed, RAG_CONFIG env var is used."""
        env_dir = tmp_path / "from-env"
        env_dir.mkdir()
        _write_override_config(env_dir / "config.py", "QDRANT_PORT = 3333\n")
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
        # Auto-set based on override location (temp dir + qdrant)
        assert result.BASE_PATH == str(override_file.parent / "qdrant")
        assert result.MODEL_PATH == "index_bge_m3"
        assert result.MCP_SERVER_NAME == "myproject-rag"
        assert result.UNIQUE_BASE_ATTR == "only_in_base"

    def test_override_adds_new_attributes(self, tmp_path):
        """Override can add attributes not present in base config."""
        override_file = tmp_path / "override.py"
        _write_override_config(override_file, "NEW_OVERRIDE_ATTR = 'hello'\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        assert result.NEW_OVERRIDE_ATTR == "hello"
        # Auto-set based on override location
        assert result.BASE_PATH == str(override_file.parent / "qdrant")

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
        # Auto-set based on override location
        assert result.BASE_PATH == str(override_file.parent / "qdrant")
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
            patch("config_loader.spec_from_file_location", return_value=None),
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
            patch("config_loader.spec_from_file_location", return_value=fake_spec),
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
            patch("config_loader.spec_from_file_location", return_value=fake_spec),
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
            patch("config_loader.spec_from_file_location", return_value=fake_spec),
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

    def test_override_file_does_not_exist_raises(self, tmp_path):
        """When the resolved override path doesn't exist, raise RuntimeError."""
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="Project config not found"):
                get_config(config_path=str(tmp_path / "does_not_exist.py"))

    def test_empty_override_file_returns_merged(self, tmp_path):
        """An empty override file merges nothing — result has auto-set BASE_PATH."""
        override_file = tmp_path / "empty_override.py"
        _write_override_config(override_file, "")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        # Should be a merged module (not the base itself) with auto-set BASE_PATH
        assert result is not fake_base
        # Auto-set based on override location
        assert result.BASE_PATH == str(override_file.parent / "qdrant")
        assert result.QDRANT_PORT == 6333
        assert result.COLLECTION_NAME == "myproject_rag"

    def test_config_path_empty_string_raises(self, monkeypatch):
        """Empty string config_path is falsy, falls through to no-config error."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="No project config specified"):
                get_config(config_path="")

    def test_config_name_empty_string_raises(self, monkeypatch):
        """Empty string config_name is falsy, falls through to no-config error."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="No project config specified"):
                get_config(config_name="")

    def test_config_path_is_directory_without_config_py_raises(self, tmp_path):
        """config_path pointing to a dir without config.py raises RuntimeError."""
        empty_dir = tmp_path / "empty-dir"
        empty_dir.mkdir()

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="Project config not found"):
                get_config(config_path=str(empty_dir))

    def test_override_with_only_comments(self, tmp_path):
        """An override file with only comments — BASE_PATH auto-set."""
        override_file = tmp_path / "comments_only.py"
        _write_override_config(
            override_file, "# This is a comment\n# Another comment\n"
        )

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))

        # Auto-set based on override location
        assert result.BASE_PATH == str(override_file.parent / "qdrant")
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
        _write_override_config(nested_dir / "config.py", "QDRANT_PORT = 8888\n")

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
        """config_path that is a non-.py file (not a dir) appends /config.py — raises if missing."""
        # Path like "self-index" that doesn't exist as a dir and has no .py suffix
        # will try Path("self-index") / "config.py" -- which won't exist, so RuntimeError raised
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="Project config not found"):
                get_config(config_path="nonexistent-thing")


# ────────────────────────────────────────────────
# TestValidateConfig
# ────────────────────────────────────────────────


class TestValidateConfig:
    """Tests for _validate_config() — QDRANT_MODE validation and QDRANT_USE_DOCKER removal."""

    def test_qdrant_use_docker_raises_runtime_error(self, tmp_path):
        """Config with QDRANT_USE_DOCKER raises RuntimeError with migration message."""
        override_file = tmp_path / "old_config.py"
        _write_override_config(override_file, "QDRANT_USE_DOCKER = True\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(
                RuntimeError, match="QDRANT_USE_DOCKER has been removed"
            ):
                get_config(config_path=str(override_file))

    def test_qdrant_use_docker_false_also_raises(self, tmp_path):
        """Even QDRANT_USE_DOCKER = False triggers the error (attribute must not exist)."""
        override_file = tmp_path / "old_config.py"
        _write_override_config(override_file, "QDRANT_USE_DOCKER = False\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(
                RuntimeError, match="QDRANT_USE_DOCKER has been removed"
            ):
                get_config(config_path=str(override_file))

    def test_qdrant_mode_invalid_value_raises(self, tmp_path):
        """QDRANT_MODE with invalid value raises RuntimeError."""
        override_file = tmp_path / "bad_mode.py"
        _write_override_config(override_file, "QDRANT_MODE = 'embedded'\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(
                RuntimeError, match="QDRANT_MODE must be 'local' or 'remote'"
            ):
                get_config(config_path=str(override_file))

    def test_qdrant_mode_none_raises(self, tmp_path):
        """QDRANT_MODE = None raises RuntimeError."""
        override_file = tmp_path / "none_mode.py"
        _write_override_config(override_file, "QDRANT_MODE = None\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(
                RuntimeError, match="QDRANT_MODE must be 'local' or 'remote'"
            ):
                get_config(config_path=str(override_file))

    def test_qdrant_mode_local_passes(self, tmp_path):
        """QDRANT_MODE = 'local' passes validation."""
        override_file = tmp_path / "local_mode.py"
        _write_override_config(override_file, "QDRANT_MODE = 'local'\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))
        assert result.QDRANT_MODE == "local"

    def test_qdrant_mode_remote_passes(self, tmp_path):
        """QDRANT_MODE = 'remote' passes validation."""
        override_file = tmp_path / "remote_mode.py"
        _write_override_config(override_file, "QDRANT_MODE = 'remote'\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(override_file))
        assert result.QDRANT_MODE == "remote"

    def test_error_message_includes_source_path(self, tmp_path):
        """RuntimeError for QDRANT_USE_DOCKER includes the source path."""
        override_file = tmp_path / "old_config.py"
        _write_override_config(override_file, "QDRANT_USE_DOCKER = True\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(
                RuntimeError, match=str(override_file).replace("\\", "\\\\")
            ):
                get_config(config_path=str(override_file))


# ────────────────────────────────────────────────
# TestIntegration
# ────────────────────────────────────────────────


class TestIntegration:
    """Integration tests using real config.py and self-index/config.py from the repo."""

    def test_no_config_raises(self, monkeypatch):
        """Loading with no override raises RuntimeError — config.py cannot run standalone."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        with pytest.raises(RuntimeError, match="No project config specified"):
            get_config()

    def test_no_config_error_mentions_config_flag(self, monkeypatch):
        """Error message tells user to pass --config flag."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        with pytest.raises(RuntimeError, match="--config"):
            get_config()

    def test_real_self_index_override_by_path(self):
        """Loading self-index override via config_path merges correctly."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_path="self-index/config.py")
        # Auto-set based on override location (absolute path)
        assert result.BASE_PATH == str(
            Path("self-index/config.py").parent.resolve() / "qdrant"
        )
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
        # Auto-set based on override location (absolute path)
        assert result.BASE_PATH == str(Path("self-index").resolve() / "qdrant")
        assert result.COLLECTION_NAME == "self_rag_index"

    def test_real_self_index_override_by_directory_path(self):
        """Loading self-index override via directory config_path merges correctly."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_path="self-index")
        # Auto-set based on override location (absolute path)
        assert result.BASE_PATH == str(Path("self-index").resolve() / "qdrant")
        assert result.COLLECTION_NAME == "self_rag_index"
        assert result.MCP_SERVER_NAME == "self-rag"

    def test_real_self_index_preserves_base_attrs(self):
        """Self-index override preserves base attrs not in the override."""
        self_index_path = Path("self-index/config.py")
        if not self_index_path.exists():
            pytest.skip("self-index/config.py not found in repo")

        result = get_config(config_name="self-index")
        # These are in base config but NOT overridden by self-index
        assert result.MODEL_NAME == base_config.MODEL_NAME
        # Note: DENSE_EMBED_BATCH_SIZE IS overridden in self-index (64 vs 128)
        # so we don't test it here
        assert result.HYBRID_ALPHA == base_config.HYBRID_ALPHA
        assert result.MCP_HOST == base_config.MCP_HOST

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

    def test_real_nonexistent_config_name_raises(self, monkeypatch):
        """A non-existent config_name raises RuntimeError with helpful message."""
        monkeypatch.delenv("RAG_CONFIG", raising=False)
        with pytest.raises(RuntimeError, match="Project config not found"):
            get_config(config_name="this-dir-does-not-exist-at-all")


# ────────────────────────────────────────────────
# TestRootLevelPyFileResolution
# ────────────────────────────────────────────────


class TestRootLevelPyFileResolution:
    """Tests for root-level .py config file resolution.

    config_loader now supports root-level .py config files (e.g.
    config_myproject.py) in addition to subdirectory configs (e.g.
    self-index/config.py).  When a name like 'config_myproject' is
    passed (no .py extension, not a directory), the loader first
    tries {name}/config.py, then falls back to {name}.py.
    """

    def test_config_path_name_falls_back_to_py_file(self, tmp_path):
        """config_path='foo' finds foo.py when foo/config.py doesn't exist."""
        py_file = tmp_path / "foo.py"
        _write_override_config(py_file, "QDRANT_PORT = 5555\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(tmp_path / "foo"))

        assert result.QDRANT_PORT == 5555

    def test_config_path_dir_preferred_over_py_file(self, tmp_path):
        """config_path='foo' prefers foo/config.py over foo.py when both exist."""
        # Create both: foo/config.py and foo.py
        dir_path = tmp_path / "foo"
        dir_path.mkdir()
        _write_override_config(dir_path / "config.py", "QDRANT_PORT = 1111\n")
        _write_override_config(tmp_path / "foo.py", "QDRANT_PORT = 2222\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(tmp_path / "foo"))

        # Directory config takes priority
        assert result.QDRANT_PORT == 1111

    def test_config_path_name_neither_dir_nor_py_raises(self, tmp_path):
        """config_path='foo' raises RuntimeError when neither foo/config.py nor foo.py exists."""
        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            with pytest.raises(RuntimeError, match="Project config not found"):
                get_config(config_path=str(tmp_path / "nonexistent"))

    def test_config_name_falls_back_to_py_file(self, tmp_path):
        """config_name='foo' finds foo.py when foo/config.py doesn't exist."""
        py_file = tmp_path / "bar.py"
        _write_override_config(py_file, "COLLECTION_NAME = 'bar_collection'\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name=str(tmp_path / "bar"))

        assert result.COLLECTION_NAME == "bar_collection"

    def test_config_name_dir_preferred_over_py_file(self, tmp_path):
        """config_name='foo' prefers foo/config.py over foo.py when both exist."""
        dir_path = tmp_path / "baz"
        dir_path.mkdir()
        _write_override_config(dir_path / "config.py", "COLLECTION_NAME = 'dir_coll'\n")
        _write_override_config(tmp_path / "baz.py", "COLLECTION_NAME = 'file_coll'\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_name=str(tmp_path / "baz"))

        assert result.COLLECTION_NAME == "dir_coll"

    def test_env_var_falls_back_to_py_file(self, tmp_path, monkeypatch):
        """RAG_CONFIG='foo' finds foo.py when foo/config.py doesn't exist."""
        py_file = tmp_path / "env_cfg.py"
        _write_override_config(py_file, "MCP_PORT = 9999\n")
        monkeypatch.setenv("RAG_CONFIG", str(tmp_path / "env_cfg"))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()

        assert result.MCP_PORT == 9999

    def test_env_var_dir_preferred_over_py_file(self, tmp_path, monkeypatch):
        """RAG_CONFIG='foo' prefers foo/config.py over foo.py when both exist."""
        dir_path = tmp_path / "env_both"
        dir_path.mkdir()
        _write_override_config(dir_path / "config.py", "MCP_PORT = 1111\n")
        _write_override_config(tmp_path / "env_both.py", "MCP_PORT = 2222\n")
        monkeypatch.setenv("RAG_CONFIG", str(tmp_path / "env_both"))

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config()

        assert result.MCP_PORT == 1111

    def test_root_level_py_base_path_auto_set(self, tmp_path):
        """Root-level .py config auto-sets BASE_PATH to parent_dir/qdrant."""
        py_file = tmp_path / "my_config.py"
        _write_override_config(py_file, "QDRANT_PORT = 7777\n")

        fake_base = _make_fake_base_config()
        with _patch_base_import(fake_base):
            result = get_config(config_path=str(tmp_path / "my_config"))

        # BASE_PATH should be {py_file.parent}/qdrant
        assert result.BASE_PATH == str(tmp_path / "qdrant")


# ────────────────────────────────────────────────
# TestProjectConfigLoadByName
# ────────────────────────────────────────────────


class TestProjectConfigLoadByName:
    """Tests that a project config in project-configs/ can be loaded by directory name."""

    def test_synthetic_config_loads_by_name(self, tmp_path, monkeypatch):
        """A synthetic config in project-configs/<name>/config.py loads via config_path='<name>'."""
        cfg_dir = tmp_path / "project-configs" / "config_myproject"
        cfg_file = cfg_dir / "config.py"
        _write_override_config(
            cfg_file,
            'COLLECTION_NAME = "myproject_rag"\n'
            "QDRANT_PORT = 7777\n"
            'MCP_SERVER_NAME = "myproject-rag"\n'
            'MCP_TOOL_NAME = "search_myproject"\n'
            'SOURCE_DIRS = [{"path": "src", "extensions": [".pas"]}]\n',
        )
        monkeypatch.chdir(tmp_path)
        result = get_config(config_path="config_myproject")
        assert result.COLLECTION_NAME == "myproject_rag"
        assert result.QDRANT_PORT == 7777
        assert result.MCP_SERVER_NAME == "myproject-rag"
        assert result.MCP_TOOL_NAME == "search_myproject"

    def test_synthetic_config_loads_by_py_path(self, tmp_path):
        """A synthetic config loads via its full file path."""
        cfg_dir = tmp_path / "project-configs" / "config_myproject"
        cfg_file = cfg_dir / "config.py"
        _write_override_config(
            cfg_file,
            'COLLECTION_NAME = "myproject_rag"\nMCP_SERVER_NAME = "myproject-rag"\n',
        )
        result = get_config(config_path=str(cfg_file))
        assert result.COLLECTION_NAME == "myproject_rag"
        assert result.MCP_SERVER_NAME == "myproject-rag"

    def test_synthetic_config_inherits_base_settings(self, tmp_path, monkeypatch):
        """Synthetic config inherits embedding model and batch sizes from base."""
        cfg_dir = tmp_path / "project-configs" / "config_myproject"
        cfg_file = cfg_dir / "config.py"
        _write_override_config(cfg_file, "QDRANT_PORT = 7777\n")
        monkeypatch.chdir(tmp_path)
        result = get_config(config_path="config_myproject")
        assert result.MODEL_NAME == base_config.MODEL_NAME
        assert result.EMBED_MODEL_KWARGS == base_config.EMBED_MODEL_KWARGS
        assert result.DENSE_EMBED_BATCH_SIZE == base_config.DENSE_EMBED_BATCH_SIZE
        assert result.HYBRID_ALPHA == base_config.HYBRID_ALPHA

    def test_synthetic_config_function_rebinding(self, tmp_path, monkeypatch):
        """Rebound functions in synthetic config work correctly."""
        cfg_dir = tmp_path / "project-configs" / "config_myproject"
        cfg_file = cfg_dir / "config.py"
        _write_override_config(cfg_file, "QDRANT_PORT = 7777\n")
        monkeypatch.chdir(tmp_path)
        result = get_config(config_path="config_myproject")
        assert result.get_index_path() == f"{result.BASE_PATH}/{result.MODEL_PATH}"

    def test_synthetic_config_base_path_is_config_dir_qdrant(
        self, tmp_path, monkeypatch
    ):
        """Synthetic config in project-configs/ sets BASE_PATH to {config_dir}/qdrant."""
        cfg_dir = tmp_path / "project-configs" / "config_myproject"
        cfg_file = cfg_dir / "config.py"
        _write_override_config(cfg_file, "QDRANT_PORT = 7777\n")
        monkeypatch.chdir(tmp_path)
        result = get_config(config_path="config_myproject")
        expected = str(cfg_dir.resolve() / "qdrant")
        assert result.BASE_PATH == expected


# ────────────────────────────────────────────────
# TestProjectConfigSeparateCollection
# ────────────────────────────────────────────────


class TestProjectConfigSeparateCollection:
    """Tests that two project configs have separate collection names."""

    def test_separate_configs_have_own_collections(self, tmp_path, monkeypatch):
        """Two synthetic configs each get their own collection name."""
        pc_dir = tmp_path / "project-configs"
        cfg1 = pc_dir / "config_alpha" / "config.py"
        cfg2 = pc_dir / "config_beta" / "config.py"
        _write_override_config(cfg1, 'COLLECTION_NAME = "alpha_rag"\n')
        _write_override_config(cfg2, 'COLLECTION_NAME = "beta_rag"\n')
        monkeypatch.chdir(tmp_path)
        r1 = get_config(config_path="config_alpha")
        r2 = get_config(config_path="config_beta")
        assert r1.COLLECTION_NAME == "alpha_rag"
        assert r2.COLLECTION_NAME == "beta_rag"
        assert r1.COLLECTION_NAME != r2.COLLECTION_NAME

    def test_separate_config_shares_qdrant_port(self, tmp_path, monkeypatch):
        """Two configs can share the same Qdrant port (same container, different collections)."""
        pc_dir = tmp_path / "project-configs"
        cfg1 = pc_dir / "config_alpha" / "config.py"
        cfg2 = pc_dir / "config_beta" / "config.py"
        _write_override_config(
            cfg1, 'COLLECTION_NAME = "alpha_rag"\nQDRANT_PORT = 6333\n'
        )
        _write_override_config(
            cfg2, 'COLLECTION_NAME = "beta_rag"\nQDRANT_PORT = 6333\n'
        )
        monkeypatch.chdir(tmp_path)
        r1 = get_config(config_path="config_alpha")
        r2 = get_config(config_path="config_beta")
        assert r1.QDRANT_PORT == 6333
        assert r2.QDRANT_PORT == 6333
