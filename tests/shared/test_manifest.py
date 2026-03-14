"""
Tests for shared/manifest.py — file manifest utilities.

Tests cover:
    - normalize_file_key(): canonical path key building, ./ stripping, backslash handling
    - compute_file_hash(): SHA256 hashing, error handling for unreadable files
    - is_excluded(): fnmatch pattern matching, empty patterns, nested paths
    - get_source_files(): config-driven file discovery with mocking
    - Integration: combined usage patterns
"""

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import shared.manifest as manifest_module


# ────────────────────────────────────────────────
# TestNormalizeFileKey
# ────────────────────────────────────────────────


class TestNormalizeFileKey:
    """Tests for normalize_file_key() — canonical file key construction."""

    def test_normal_source_dir_and_relative_path(self):
        """A non-dot source dir produces 'dir/relative' format."""
        result = manifest_module.normalize_file_key("source", "Common/foo.pas")
        assert result == "source/Common/foo.pas"

    def test_dot_source_dir_strips_leading_dot_slash(self):
        """Source dir '.' should strip the leading './' from the result."""
        result = manifest_module.normalize_file_key(".", "config.py")
        assert result == "config.py"

    def test_dot_source_dir_with_nested_path(self):
        """Source dir '.' with nested relative path strips './' prefix."""
        result = manifest_module.normalize_file_key(".", "shared/manifest.py")
        assert result == "shared/manifest.py"

    def test_backslashes_replaced_with_forward_slashes(self):
        """Backslashes in either argument are normalized to forward slashes."""
        result = manifest_module.normalize_file_key("source", "Common\\foo.pas")
        assert result == "source/Common/foo.pas"

    def test_backslashes_in_source_dir(self):
        """Backslashes in the source_dir_path are also normalized."""
        result = manifest_module.normalize_file_key("src\\code", "unit1.pas")
        assert result == "src/code/unit1.pas"

    def test_both_args_have_backslashes(self):
        """Both arguments with backslashes are fully normalized."""
        result = manifest_module.normalize_file_key("src\\lib", "sub\\dir\\file.py")
        assert result == "src/lib/sub/dir/file.py"

    def test_deeply_nested_path(self):
        """Deeply nested relative paths are joined correctly."""
        result = manifest_module.normalize_file_key("source", "a/b/c/d/e/file.pas")
        assert result == "source/a/b/c/d/e/file.pas"

    def test_single_file_no_subdirectory(self):
        """Relative path with no subdirectory works correctly."""
        result = manifest_module.normalize_file_key("schemas", "create.sql")
        assert result == "schemas/create.sql"

    def test_dot_source_dir_only_strips_first_dot_slash(self):
        """Only the leading './' is stripped, not deeper occurrences."""
        result = manifest_module.normalize_file_key(".", "./nested/file.py")
        assert result == "nested/file.py"

    def test_empty_relative_path(self):
        """Empty relative path produces just the source dir (edge case)."""
        result = manifest_module.normalize_file_key("source", "")
        assert result == "source/"

    def test_empty_source_dir(self):
        """Empty source dir with a relative path (edge case)."""
        result = manifest_module.normalize_file_key("", "file.py")
        assert result == "file.py"

    def test_dot_source_with_extension_only(self):
        """Source dir '.' with file in root."""
        result = manifest_module.normalize_file_key(".", "index_rag.py")
        assert result == "index_rag.py"


# ────────────────────────────────────────────────
# TestGetCanonicalPrefix
# ────────────────────────────────────────────────


class TestGetCanonicalPrefix:
    """Tests for _get_canonical_prefix() — canonical prefix derivation."""

    def test_map_to_path_takes_priority(self):
        """When map_to_path is set, it overrides the path-based prefix."""
        sd = {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "delphi_src"

    def test_multi_segment_map_to_path(self):
        """Multi-segment map_to_path is returned verbatim."""
        sd = {
            "path": "schemas",
            "map_to_path": "sql_srcipt/6RedGate",
            "extensions": [".sql"],
        }
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "sql_srcipt/6RedGate"

    def test_last_segment_of_simple_path(self):
        """Without map_to_path, returns the last segment of path."""
        sd = {"path": "source", "extensions": [".pas"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "source"

    def test_last_segment_of_relative_path(self):
        """Relative path with parent traversal returns just the last segment."""
        sd = {"path": "../informica_2_0/delphi_src", "extensions": [".pas"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "delphi_src"

    def test_deeply_nested_path(self):
        """Deeply nested path returns only the last segment."""
        sd = {"path": "a/b/c/d/target", "extensions": [".pas"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "target"

    def test_dot_path_returns_empty(self):
        """Path '.' returns empty string (root directory)."""
        sd = {"path": ".", "extensions": [".py"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == ""

    def test_empty_path_returns_empty(self):
        """Empty path returns empty string."""
        sd = {"path": "", "extensions": [".py"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == ""

    def test_backslashes_normalized(self):
        """Backslashes in path are normalized to forward slashes."""
        sd = {"path": "..\\informica_2_0\\delphi_src", "extensions": [".pas"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "delphi_src"

    def test_backslashes_in_map_to_path_normalized(self):
        """Backslashes in map_to_path are normalized."""
        sd = {"path": "schemas", "map_to_path": "sql_srcipt\\6RedGate"}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "sql_srcipt/6RedGate"

    def test_trailing_slash_stripped(self):
        """Trailing slash on path is stripped before extracting last segment."""
        sd = {"path": "source/", "extensions": [".pas"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "source"

    def test_trailing_slash_on_map_to_path_stripped(self):
        """Trailing slash on map_to_path is stripped."""
        sd = {"path": "x", "map_to_path": "delphi_src/"}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == "delphi_src"

    def test_missing_path_key_returns_empty(self):
        """Missing path key in dict defaults to empty string."""
        sd = {"extensions": [".pas"]}
        result = manifest_module._get_canonical_prefix(sd)
        assert result == ""


# ────────────────────────────────────────────────
# TestNormalizeFileKeyWithSourceDir
# ────────────────────────────────────────────────


class TestNormalizeFileKeyWithSourceDir:
    """Tests for normalize_file_key() with source_dir= parameter (new canonical path)."""

    def test_source_dir_with_map_to_path(self):
        """With map_to_path, canonical prefix comes from map_to_path."""
        sd = {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]}
        result = manifest_module.normalize_file_key(
            sd["path"], "Common/foo.pas", source_dir=sd
        )
        assert result == "delphi_src/Common/foo.pas"

    def test_source_dir_with_relative_path(self):
        """Without map_to_path, last segment of path is the prefix."""
        sd = {"path": "../informica_2_0/delphi_src", "extensions": [".pas"]}
        result = manifest_module.normalize_file_key(
            sd["path"], "Common/foo.pas", source_dir=sd
        )
        assert result == "delphi_src/Common/foo.pas"

    def test_source_dir_same_key_regardless_of_disk_path(self):
        """Two different disk paths with same last segment produce identical keys."""
        sd_old = {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]}
        sd_new = {"path": "../informica_2_0/delphi_src", "extensions": [".pas"]}
        key_old = manifest_module.normalize_file_key(
            sd_old["path"], "Common/foo.pas", source_dir=sd_old
        )
        key_new = manifest_module.normalize_file_key(
            sd_new["path"], "Common/foo.pas", source_dir=sd_new
        )
        assert key_old == key_new == "delphi_src/Common/foo.pas"

    def test_source_dir_multi_segment_map_to_path(self):
        """Multi-segment map_to_path produces multi-segment prefix."""
        sd = {
            "path": "schemas",
            "map_to_path": "sql_srcipt/6RedGate",
            "extensions": [".sql"],
        }
        result = manifest_module.normalize_file_key(
            sd["path"], "dbo.Proc.sql", source_dir=sd
        )
        assert result == "sql_srcipt/6RedGate/dbo.Proc.sql"

    def test_source_dir_dot_path(self):
        """Dot path with source_dir produces key without prefix."""
        sd = {"path": ".", "extensions": [".py"]}
        result = manifest_module.normalize_file_key(".", "config.py", source_dir=sd)
        assert result == "config.py"

    def test_source_dir_empty_path(self):
        """Empty path with source_dir produces key without prefix."""
        sd = {"path": "", "extensions": [".py"]}
        result = manifest_module.normalize_file_key("", "shared/log.py", source_dir=sd)
        assert result == "shared/log.py"

    def test_legacy_call_without_source_dir(self):
        """Without source_dir=, uses source_dir_path directly (backward compat)."""
        result = manifest_module.normalize_file_key("source", "Common/foo.pas")
        assert result == "source/Common/foo.pas"

    def test_source_dir_none_uses_legacy(self):
        """Explicitly passing source_dir=None uses legacy behavior."""
        result = manifest_module.normalize_file_key(
            "source", "Common/foo.pas", source_dir=None
        )
        assert result == "source/Common/foo.pas"

    def test_backslashes_in_relative_path_normalized(self):
        """Backslashes in relative_posix are normalized even with source_dir."""
        sd = {"path": "../informica_2_0/delphi_src", "extensions": [".pas"]}
        result = manifest_module.normalize_file_key(
            sd["path"], "Common\\foo.pas", source_dir=sd
        )
        assert result == "delphi_src/Common/foo.pas"


# ────────────────────────────────────────────────
# TestResolveKeyToDiskPath
# ────────────────────────────────────────────────


class TestResolveKeyToDiskPath:
    """Tests for resolve_key_to_disk_path() — canonical key to disk path resolution."""

    @staticmethod
    def _make_cfg(source_dirs):
        return type("MockConfig", (), {"SOURCE_DIRS": source_dirs})

    def test_simple_map_to_path_resolution(self):
        """Key with map_to_path prefix resolves to disk path."""
        cfg = self._make_cfg(
            [
                {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]},
            ]
        )
        result = manifest_module.resolve_key_to_disk_path(
            "delphi_src/Common/foo.pas", cfg=cfg
        )
        assert result == "source/Common/foo.pas"

    def test_multi_segment_map_to_path_resolution(self):
        """Multi-segment map_to_path prefix resolves correctly."""
        cfg = self._make_cfg(
            [
                {
                    "path": "schemas",
                    "map_to_path": "sql_srcipt/6RedGate",
                    "extensions": [".sql"],
                },
            ]
        )
        result = manifest_module.resolve_key_to_disk_path(
            "sql_srcipt/6RedGate/dbo.Proc.sql", cfg=cfg
        )
        assert result == "schemas/dbo.Proc.sql"

    def test_relative_path_last_segment_resolution(self):
        """Canonical key using last segment of relative path resolves correctly."""
        cfg = self._make_cfg(
            [
                {"path": "../informica_2_0/delphi_src", "extensions": [".pas"]},
            ]
        )
        result = manifest_module.resolve_key_to_disk_path(
            "delphi_src/Common/foo.pas", cfg=cfg
        )
        assert result == "../informica_2_0/delphi_src/Common/foo.pas"

    def test_dot_path_resolution(self):
        """Keys for root-dir source (path='.') resolve as-is."""
        cfg = self._make_cfg(
            [
                {"path": ".", "extensions": [".py"]},
            ]
        )
        result = manifest_module.resolve_key_to_disk_path("config.py", cfg=cfg)
        assert result == "config.py"

    def test_no_matching_prefix_returns_key_unchanged(self):
        """When no SOURCE_DIR matches, key is returned unchanged."""
        cfg = self._make_cfg(
            [
                {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]},
            ]
        )
        result = manifest_module.resolve_key_to_disk_path("unknown/file.txt", cfg=cfg)
        assert result == "unknown/file.txt"

    def test_exact_prefix_match_without_trailing_slash(self):
        """Canonical key equal to prefix (no file part) resolves to raw path."""
        cfg = self._make_cfg(
            [
                {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]},
            ]
        )
        result = manifest_module.resolve_key_to_disk_path("delphi_src", cfg=cfg)
        assert result == "source"

    def test_cfg_required(self):
        """Calling without cfg raises ValueError."""
        with pytest.raises(ValueError, match="cfg is required"):
            manifest_module.resolve_key_to_disk_path("delphi_src/foo.pas")

    def test_backslashes_normalized(self):
        """Backslashes in canonical key are normalized."""
        cfg = self._make_cfg(
            [
                {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]},
            ]
        )
        result = manifest_module.resolve_key_to_disk_path(
            "delphi_src\\Common\\foo.pas", cfg=cfg
        )
        assert result == "source/Common/foo.pas"

    def test_multiple_source_dirs(self):
        """Correct source dir is matched when multiple are configured."""
        cfg = self._make_cfg(
            [
                {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]},
                {
                    "path": "schemas",
                    "map_to_path": "sql_srcipt/6RedGate",
                    "extensions": [".sql"],
                },
            ]
        )
        assert (
            manifest_module.resolve_key_to_disk_path("delphi_src/foo.pas", cfg=cfg)
            == "source/foo.pas"
        )
        assert (
            manifest_module.resolve_key_to_disk_path(
                "sql_srcipt/6RedGate/bar.sql", cfg=cfg
            )
            == "schemas/bar.sql"
        )

    def test_roundtrip_normalize_then_resolve(self):
        """normalize_file_key + resolve_key_to_disk_path round-trips correctly."""
        sd = {"path": "../informica_2_0/delphi_src", "extensions": [".pas"]}
        cfg = self._make_cfg([sd])
        key = manifest_module.normalize_file_key(
            sd["path"], "Common/foo.pas", source_dir=sd
        )
        disk = manifest_module.resolve_key_to_disk_path(key, cfg=cfg)
        assert key == "delphi_src/Common/foo.pas"
        assert disk == "../informica_2_0/delphi_src/Common/foo.pas"


# ────────────────────────────────────────────────
# TestValidateSourceDirs
# ────────────────────────────────────────────────


class TestValidateSourceDirs:
    """Tests for validate_source_dirs() — duplicate prefix collision detection."""

    @staticmethod
    def _make_cfg(source_dirs):
        return type("MockConfig", (), {"SOURCE_DIRS": source_dirs})

    def test_no_collisions(self):
        """Distinct prefixes produce no errors."""
        cfg = self._make_cfg(
            [
                {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]},
                {
                    "path": "schemas",
                    "map_to_path": "sql_srcipt/6RedGate",
                    "extensions": [".sql"],
                },
            ]
        )
        errors = manifest_module.validate_source_dirs(cfg=cfg)
        assert errors == []

    def test_collision_detected(self):
        """Two dirs with same canonical prefix produce an error."""
        cfg = self._make_cfg(
            [
                {"path": "source", "map_to_path": "delphi_src", "extensions": [".pas"]},
                {"path": "../other/delphi_src", "extensions": [".pas"]},
            ]
        )
        errors = manifest_module.validate_source_dirs(cfg=cfg)
        assert len(errors) == 1
        assert "collision" in errors[0].lower() or "delphi_src" in errors[0]

    def test_same_last_segment_collision(self):
        """Two paths with same last segment but no map_to_path collide."""
        cfg = self._make_cfg(
            [
                {"path": "a/src", "extensions": [".py"]},
                {"path": "b/src", "extensions": [".py"]},
            ]
        )
        errors = manifest_module.validate_source_dirs(cfg=cfg)
        assert len(errors) == 1

    def test_map_to_path_disambiguates(self):
        """map_to_path can prevent collisions from same last segment."""
        cfg = self._make_cfg(
            [
                {"path": "a/src", "map_to_path": "src_a", "extensions": [".py"]},
                {"path": "b/src", "map_to_path": "src_b", "extensions": [".py"]},
            ]
        )
        errors = manifest_module.validate_source_dirs(cfg=cfg)
        assert errors == []

    def test_single_dir_no_collision(self):
        """Single source dir cannot have collisions."""
        cfg = self._make_cfg(
            [
                {"path": "source", "extensions": [".pas"]},
            ]
        )
        errors = manifest_module.validate_source_dirs(cfg=cfg)
        assert errors == []

    def test_empty_source_dirs(self):
        """Empty SOURCE_DIRS list produces no errors."""
        cfg = self._make_cfg([])
        errors = manifest_module.validate_source_dirs(cfg=cfg)
        assert errors == []

    def test_cfg_required(self):
        """Calling without cfg raises ValueError."""
        with pytest.raises(ValueError, match="cfg is required"):
            manifest_module.validate_source_dirs()


# ────────────────────────────────────────────────
# TestMapPathToQdrant
# ────────────────────────────────────────────────


class TestMapPathToQdrant:
    """Tests for map_path_to_qdrant() — mapping local paths to Qdrant paths."""

    def test_map_path_to_qdrant_with_mapping(self):
        mock_config = type(
            "MockConfig",
            (),
            {
                "SOURCE_DIRS": [
                    {
                        "path": "source",
                        "map_to_path": "delphi_src",
                        "extensions": [".pas"],
                    },
                    {
                        "path": "schemas",
                        "map_to_path": "sql_script/6RedGate",
                        "extensions": [".sql"],
                    },
                ]
            },
        )

        assert (
            manifest_module.map_path_to_qdrant("source/Common/foo.pas", cfg=mock_config)
            == "delphi_src/Common/foo.pas"
        )
        assert (
            manifest_module.map_path_to_qdrant("schemas/dbo.Table.sql", cfg=mock_config)
            == "sql_script/6RedGate/dbo.Table.sql"
        )
        assert (
            manifest_module.map_path_to_qdrant("source", cfg=mock_config)
            == "delphi_src"
        )
        assert (
            manifest_module.map_path_to_qdrant("schemas/", cfg=mock_config)
            == "sql_script/6RedGate/"
        )

    def test_map_path_to_qdrant_with_empty_source(self):
        mock_config = type(
            "MockConfig",
            (),
            {
                "SOURCE_DIRS": [
                    {"path": "", "map_to_path": "mapped_root", "extensions": [".pas"]},
                ]
            },
        )

        assert (
            manifest_module.map_path_to_qdrant("foo.pas", cfg=mock_config)
            == "mapped_root/foo.pas"
        )
        assert (
            manifest_module.map_path_to_qdrant("nested/foo.pas", cfg=mock_config)
            == "mapped_root/nested/foo.pas"
        )
        mock_config_no_map = type(
            "MockConfig",
            (),
            {
                "SOURCE_DIRS": [
                    {"path": "source", "extensions": [".pas"]},
                ]
            },
        )

        assert (
            manifest_module.map_path_to_qdrant(
                "source/Common/foo.pas", cfg=mock_config_no_map
            )
            == "source/Common/foo.pas"
        )


# ────────────────────────────────────────────────
# TestMapPathFromQdrant
# ────────────────────────────────────────────────


class TestMapPathFromQdrant:
    """Tests for map_path_from_qdrant() — mapping Qdrant paths back to local paths."""

    def test_map_path_from_qdrant_with_mapping(self):
        mock_config = type(
            "MockConfig",
            (),
            {
                "SOURCE_DIRS": [
                    {
                        "path": "source",
                        "map_to_path": "delphi_src",
                        "extensions": [".pas"],
                    },
                    {
                        "path": "schemas",
                        "map_to_path": "sql_script/6RedGate",
                        "extensions": [".sql"],
                    },
                ]
            },
        )

        assert (
            manifest_module.map_path_from_qdrant(
                "delphi_src/Common/foo.pas", cfg=mock_config
            )
            == "source/Common/foo.pas"
        )
        assert (
            manifest_module.map_path_from_qdrant(
                "sql_script/6RedGate/dbo.Table.sql", cfg=mock_config
            )
            == "schemas/dbo.Table.sql"
        )
        assert (
            manifest_module.map_path_from_qdrant("delphi_src", cfg=mock_config)
            == "source"
        )
        assert (
            manifest_module.map_path_from_qdrant(
                "sql_script/6RedGate/", cfg=mock_config
            )
            == "schemas/"
        )

    def test_map_path_from_qdrant_with_empty_source(self):
        mock_config = type(
            "MockConfig",
            (),
            {
                "SOURCE_DIRS": [
                    {"path": "", "map_to_path": "mapped_root", "extensions": [".pas"]},
                ]
            },
        )

        assert (
            manifest_module.map_path_from_qdrant("mapped_root/foo.pas", cfg=mock_config)
            == "foo.pas"
        )
        assert (
            manifest_module.map_path_from_qdrant(
                "mapped_root/nested/foo.pas", cfg=mock_config
            )
            == "nested/foo.pas"
        )
        mock_config_no_map = type(
            "MockConfig",
            (),
            {
                "SOURCE_DIRS": [
                    {"path": "source", "extensions": [".pas"]},
                ]
            },
        )

        assert (
            manifest_module.map_path_from_qdrant(
                "source/Common/foo.pas", cfg=mock_config_no_map
            )
            == "source/Common/foo.pas"
        )


# ────────────────────────────────────────────────
# TestComputeFileHash
# ────────────────────────────────────────────────


class TestComputeFileHash:
    """Tests for compute_file_hash() — SHA256 file hashing."""

    def test_hash_of_known_content(self, tmp_path: Path):
        """Hash of a file with known content matches expected SHA256."""
        test_file = tmp_path / "test.txt"
        content = b"hello world"
        test_file.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()
        result = manifest_module.compute_file_hash(test_file)
        assert result == expected

    def test_hash_of_empty_file(self, tmp_path: Path):
        """Hash of an empty file returns SHA256 of empty bytes."""
        test_file = tmp_path / "empty.txt"
        test_file.write_bytes(b"")
        expected = hashlib.sha256(b"").hexdigest()
        result = manifest_module.compute_file_hash(test_file)
        assert result == expected

    def test_hash_of_binary_content(self, tmp_path: Path):
        """Hash works correctly for binary file content."""
        test_file = tmp_path / "binary.bin"
        content = bytes(range(256)) * 100
        test_file.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()
        result = manifest_module.compute_file_hash(test_file)
        assert result == expected

    def test_hash_of_large_file(self, tmp_path: Path):
        """Hash works correctly for files larger than the 8192-byte chunk size."""
        test_file = tmp_path / "large.bin"
        # 3 full chunks + partial
        content = b"A" * 8192 + b"B" * 8192 + b"C" * 8192 + b"D" * 100
        test_file.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()
        result = manifest_module.compute_file_hash(test_file)
        assert result == expected

    def test_hash_deterministic(self, tmp_path: Path):
        """Calling compute_file_hash twice on the same file returns the same hash."""
        test_file = tmp_path / "repeat.txt"
        test_file.write_bytes(b"deterministic content")
        hash1 = manifest_module.compute_file_hash(test_file)
        hash2 = manifest_module.compute_file_hash(test_file)
        assert hash1 == hash2

    def test_different_files_different_hashes(self, tmp_path: Path):
        """Two files with different content produce different hashes."""
        file1 = tmp_path / "a.txt"
        file2 = tmp_path / "b.txt"
        file1.write_bytes(b"content A")
        file2.write_bytes(b"content B")
        hash1 = manifest_module.compute_file_hash(file1)
        hash2 = manifest_module.compute_file_hash(file2)
        assert hash1 != hash2

    @patch.object(manifest_module, "log_warn")
    def test_nonexistent_file_returns_empty_and_warns(self, mock_warn: MagicMock):
        """A non-existent file path returns '' and logs a warning."""
        result = manifest_module.compute_file_hash(Path("/nonexistent/path/file.txt"))
        assert result == ""
        mock_warn.assert_called_once()
        assert "Could not hash" in mock_warn.call_args[0][0]

    @patch.object(manifest_module, "log_warn")
    def test_unreadable_file_returns_empty_and_warns(
        self, mock_warn: MagicMock, tmp_path: Path
    ):
        """A file that raises on read returns '' and logs a warning."""
        fake_path = tmp_path / "unreadable.txt"
        fake_path.write_bytes(b"data")
        # Patch open to raise PermissionError
        with patch("builtins.open", side_effect=PermissionError("access denied")):
            result = manifest_module.compute_file_hash(fake_path)
        assert result == ""
        mock_warn.assert_called_once()
        assert "Could not hash" in mock_warn.call_args[0][0]

    def test_hash_returns_hex_string_of_correct_length(self, tmp_path: Path):
        """The returned hash is a 64-character hex string (SHA256)."""
        test_file = tmp_path / "length.txt"
        test_file.write_bytes(b"test")
        result = manifest_module.compute_file_hash(test_file)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


# ────────────────────────────────────────────────
# TestIsExcluded
# ────────────────────────────────────────────────


class TestIsExcluded:
    """Tests for is_excluded() — fnmatch-based path exclusion."""

    def test_empty_patterns_returns_false(self):
        """An empty exclude list never excludes anything."""
        result = manifest_module.is_excluded(Path("src/foo.py"), [])
        assert result is False

    def test_none_like_empty_patterns_returns_false(self):
        """An empty list is falsy, so it should return False."""
        result = manifest_module.is_excluded(Path("any/path/file.txt"), [])
        assert result is False

    def test_matching_directory_name(self):
        """A path containing __pycache__ matches the '__pycache__' pattern."""
        result = manifest_module.is_excluded(
            Path("src/__pycache__/module.pyc"), ["__pycache__"]
        )
        assert result is True

    def test_matching_file_extension_pattern(self):
        """A .pyc file matches the '*.pyc' pattern."""
        result = manifest_module.is_excluded(Path("src/module.pyc"), ["*.pyc"])
        assert result is True

    def test_no_match(self):
        """A path that doesn't match any pattern returns False."""
        result = manifest_module.is_excluded(
            Path("src/main.py"), ["__pycache__", "*.pyc", "node_modules"]
        )
        assert result is False

    def test_node_modules_excluded(self):
        """The 'node_modules' pattern matches a path part named node_modules."""
        result = manifest_module.is_excluded(
            Path("project/node_modules/pkg/index.js"), ["node_modules"]
        )
        assert result is True

    def test_wildcard_prefix_pattern(self):
        """A pattern like 'index_*' matches directory names starting with index_."""
        result = manifest_module.is_excluded(
            Path("project/index_data/file.txt"), ["index_*"]
        )
        assert result is True

    def test_wildcard_prefix_no_match(self):
        """A pattern like 'index_*' does NOT match 'indexed' (no underscore)."""
        result = manifest_module.is_excluded(
            Path("project/indexed/file.txt"), ["index_*"]
        )
        assert result is False

    def test_multiple_patterns_first_matches(self):
        """When multiple patterns are given, the first match wins."""
        result = manifest_module.is_excluded(
            Path(".venv/lib/site-packages/pkg.py"), [".venv", "node_modules"]
        )
        assert result is True

    def test_multiple_patterns_second_matches(self):
        """When multiple patterns are given, a later pattern can match."""
        result = manifest_module.is_excluded(
            Path("src/node_modules/pkg/file.js"), ["__pycache__", "node_modules"]
        )
        assert result is True

    def test_deeply_nested_match(self):
        """A pattern matches a part at any depth in the path."""
        result = manifest_module.is_excluded(
            Path("a/b/c/d/__pycache__/e.pyc"), ["__pycache__"]
        )
        assert result is True

    def test_root_file_no_match(self):
        """A root-level file with no matching pattern returns False."""
        result = manifest_module.is_excluded(Path("README.md"), ["__pycache__"])
        assert result is False

    def test_exact_filename_pattern(self):
        """An exact filename pattern matches that specific file part."""
        result = manifest_module.is_excluded(Path("src/secret.env"), ["secret.env"])
        assert result is True

    def test_dot_venv_pattern(self):
        """The '.venv' pattern correctly matches the .venv directory."""
        result = manifest_module.is_excluded(Path(".venv/bin/python"), [".venv"])
        assert result is True

    def test_test_sources_pattern(self):
        """The 'test_sources' pattern from config example works."""
        result = manifest_module.is_excluded(
            Path("project/test_sources/data.pas"), ["test_sources"]
        )
        assert result is True

    def test_backup_pattern(self):
        """The 'backup' pattern matches a backup directory."""
        result = manifest_module.is_excluded(Path("project/backup/old.pas"), ["backup"])
        assert result is True

    # ── Multi-segment pattern tests ──

    def test_multi_segment_exact_match(self):
        """A multi-segment pattern 'TURDUS/ENG' matches the path segment pair."""
        result = manifest_module.is_excluded(
            Path("source/TURDUS/ENG/unit.pas"), ["TURDUS/ENG"]
        )
        assert result is True

    def test_multi_segment_no_match(self):
        """A multi-segment pattern 'TURDUS/ENG' does NOT match 'TURDUS/CZE'."""
        result = manifest_module.is_excluded(
            Path("source/TURDUS/CZE/unit.pas"), ["TURDUS/ENG"]
        )
        assert result is False

    def test_multi_segment_multiple_patterns(self):
        """Multiple multi-segment patterns — second one matches."""
        result = manifest_module.is_excluded(
            Path("source/TURDUS/UKR/form.dfm"),
            ["TURDUS/ENG", "TURDUS/SRM", "TURDUS/UKR"],
        )
        assert result is True

    def test_multi_segment_deeply_nested(self):
        """Multi-segment pattern matches at any depth in the path."""
        result = manifest_module.is_excluded(
            Path("a/b/TURDUS/ENG/c/d.pas"), ["TURDUS/ENG"]
        )
        assert result is True

    def test_multi_segment_with_wildcard(self):
        """Multi-segment pattern with fnmatch wildcard: 'TURDUS/E*' matches 'TURDUS/ENG'."""
        result = manifest_module.is_excluded(
            Path("source/TURDUS/ENG/unit.pas"), ["TURDUS/E*"]
        )
        assert result is True

    def test_multi_segment_wildcard_no_match(self):
        """Multi-segment wildcard 'TURDUS/E*' does NOT match 'TURDUS/SRM'."""
        result = manifest_module.is_excluded(
            Path("source/TURDUS/SRM/unit.pas"), ["TURDUS/E*"]
        )
        assert result is False

    def test_multi_segment_backslash_normalised(self):
        r"""Backslash in pattern 'TURDUS\\ENG' is normalised to forward slash."""
        result = manifest_module.is_excluded(
            Path("source/TURDUS/ENG/unit.pas"), ["TURDUS\\ENG"]
        )
        assert result is True

    def test_mixed_single_and_multi_patterns(self):
        """A mix of single-segment and multi-segment patterns works correctly."""
        result = manifest_module.is_excluded(
            Path("source/__pycache__/mod.pyc"), ["TURDUS/ENG", "__pycache__"]
        )
        assert result is True

    def test_multi_segment_only_partial_path_no_match(self):
        """Pattern 'TURDUS/ENG' does NOT match if only 'TURDUS' appears without 'ENG' next."""
        result = manifest_module.is_excluded(
            Path("source/TURDUS/CZE/ENG/unit.pas"), ["TURDUS/ENG"]
        )
        assert result is False

    def test_three_segment_pattern(self):
        """A three-segment pattern 'a/b/c' matches correctly."""
        result = manifest_module.is_excluded(Path("root/a/b/c/file.txt"), ["a/b/c"])
        assert result is True

    def test_three_segment_pattern_no_match(self):
        """A three-segment pattern 'a/b/c' does NOT match 'a/b/d'."""
        result = manifest_module.is_excluded(Path("root/a/b/d/file.txt"), ["a/b/c"])
        assert result is False


# ────────────────────────────────────────────────
# TestGetSourceFiles
# ────────────────────────────────────────────────


class TestGetSourceFiles:
    """Tests for get_source_files() — config-driven file discovery."""

    @staticmethod
    def _make_cfg(source_dirs):
        """Helper to create a mock config with SOURCE_DIRS."""
        return type("MockConfig", (), {"SOURCE_DIRS": source_dirs})

    def test_finds_files_by_extension(self, tmp_path: Path):
        """get_source_files() returns files matching configured extensions."""
        # Create directory structure
        src = tmp_path / "src"
        src.mkdir()
        (src / "unit1.pas").write_text("unit Unit1;")
        (src / "unit2.pas").write_text("unit Unit2;")
        (src / "readme.txt").write_text("not indexed")

        mock_config = self._make_cfg(
            [
                {"path": str(src), "extensions": [".pas"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 2
        names = [f.name for f in result]
        assert "unit1.pas" in names
        assert "unit2.pas" in names
        assert "readme.txt" not in names

    def test_finds_files_recursively(self, tmp_path: Path):
        """get_source_files() recurses into subdirectories."""
        src = tmp_path / "src"
        sub = src / "sub"
        sub.mkdir(parents=True)
        (src / "root.pas").write_text("root")
        (sub / "nested.pas").write_text("nested")

        mock_config = self._make_cfg(
            [
                {"path": str(src), "extensions": [".pas"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 2
        names = [f.name for f in result]
        assert "root.pas" in names
        assert "nested.pas" in names

    def test_multiple_extensions(self, tmp_path: Path):
        """get_source_files() collects files of all configured extensions."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "unit.pas").write_text("pas")
        (src / "project.dpr").write_text("dpr")
        (src / "form.dfm").write_text("dfm")
        (src / "notes.txt").write_text("txt")

        mock_config = self._make_cfg(
            [
                {"path": str(src), "extensions": [".pas", ".dpr", ".dfm"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 3
        names = [f.name for f in result]
        assert "unit.pas" in names
        assert "project.dpr" in names
        assert "form.dfm" in names

    def test_multiple_source_dirs(self, tmp_path: Path):
        """get_source_files() collects from multiple source directories."""
        src1 = tmp_path / "source"
        src2 = tmp_path / "schemas"
        src1.mkdir()
        src2.mkdir()
        (src1 / "unit.pas").write_text("pas")
        (src2 / "create.sql").write_text("sql")

        mock_config = self._make_cfg(
            [
                {"path": str(src1), "extensions": [".pas"]},
                {"path": str(src2), "extensions": [".sql"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 2
        names = [f.name for f in result]
        assert "unit.pas" in names
        assert "create.sql" in names

    def test_nonexistent_directory_is_skipped(self, tmp_path: Path):
        """A source dir that doesn't exist is silently skipped."""
        existing = tmp_path / "existing"
        existing.mkdir()
        (existing / "file.pas").write_text("content")

        mock_config = self._make_cfg(
            [
                {"path": str(tmp_path / "nonexistent"), "extensions": [".pas"]},
                {"path": str(existing), "extensions": [".pas"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 1
        assert result[0].name == "file.pas"

    def test_exclude_patterns_filter_out_files(self, tmp_path: Path):
        """Files in excluded directories are not returned."""
        src = tmp_path / "src"
        cache = src / "__pycache__"
        cache.mkdir(parents=True)
        (src / "main.py").write_text("main")
        (cache / "main.cpython-311.pyc").write_text("bytecode")

        mock_config = self._make_cfg(
            [
                {
                    "path": str(src),
                    "extensions": [".py", ".pyc"],
                    "exclude": ["__pycache__"],
                },
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 1
        assert result[0].name == "main.py"

    def test_exclude_with_wildcard_pattern(self, tmp_path: Path):
        """Wildcard exclude patterns (e.g. 'index_*') work correctly."""
        src = tmp_path / "project"
        idx = src / "index_data"
        idx.mkdir(parents=True)
        (src / "main.py").write_text("main")
        (idx / "vectors.bin").write_text("data")

        mock_config = self._make_cfg(
            [
                {
                    "path": str(src),
                    "extensions": [".py", ".bin"],
                    "exclude": ["index_*"],
                },
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 1
        assert result[0].name == "main.py"

    def test_no_exclude_key_defaults_to_empty(self, tmp_path: Path):
        """A source_dir without 'exclude' key doesn't filter anything."""
        src = tmp_path / "src"
        cache = src / "__pycache__"
        cache.mkdir(parents=True)
        (src / "main.py").write_text("main")
        (cache / "cached.py").write_text("cached")

        mock_config = self._make_cfg(
            [
                {"path": str(src), "extensions": [".py"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 2

    def test_returns_sorted_list(self, tmp_path: Path):
        """get_source_files() returns paths in sorted order."""
        src = tmp_path / "src"
        src.mkdir()
        # Create files in non-alphabetical order
        (src / "zebra.pas").write_text("z")
        (src / "alpha.pas").write_text("a")
        (src / "middle.pas").write_text("m")

        mock_config = self._make_cfg(
            [
                {"path": str(src), "extensions": [".pas"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        names = [f.name for f in result]
        assert names == sorted(names)

    def test_empty_source_dirs(self):
        """An empty SOURCE_DIRS list returns no files."""
        mock_config = self._make_cfg([])
        result = manifest_module.get_source_files(cfg=mock_config)

        assert result == []

    def test_directory_with_no_matching_files(self, tmp_path: Path):
        """A directory with no files matching the extension returns empty."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "readme.txt").write_text("text")
        (src / "notes.md").write_text("markdown")

        mock_config = self._make_cfg(
            [
                {"path": str(src), "extensions": [".pas"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert result == []

    def test_only_regular_files_returned(self, tmp_path: Path):
        """Directories matching the glob pattern are not returned (is_file check)."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "unit.pas").write_text("unit")
        # Create a directory that ends in .pas (unusual but possible)
        (src / "weird.pas").mkdir()

        mock_config = self._make_cfg(
            [
                {"path": str(src), "extensions": [".pas"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert len(result) == 1
        assert result[0].name == "unit.pas"

    def test_all_dirs_nonexistent_returns_empty(self):
        """When all configured source dirs are missing, return empty list."""
        mock_config = self._make_cfg(
            [
                {"path": "/does/not/exist/at/all", "extensions": [".pas"]},
                {"path": "/also/missing", "extensions": [".sql"]},
            ]
        )
        result = manifest_module.get_source_files(cfg=mock_config)

        assert result == []


# ────────────────────────────────────────────────
# TestIntegration
# ────────────────────────────────────────────────


class TestIntegration:
    """Integration tests combining multiple manifest functions."""

    def test_normalize_key_then_hash_workflow(self, tmp_path: Path):
        """Simulates the indexing workflow: normalize key + compute hash."""
        src = tmp_path / "source"
        src.mkdir()
        test_file = src / "unit1.pas"
        test_file.write_bytes(b"unit Unit1; interface implementation end.")

        key = manifest_module.normalize_file_key("source", "unit1.pas")
        file_hash = manifest_module.compute_file_hash(test_file)

        assert key == "source/unit1.pas"
        assert len(file_hash) == 64

    def test_get_source_files_with_exclusion_and_hashing(self, tmp_path: Path):
        """Full pipeline: discover files with exclusions, then hash each one."""
        src = tmp_path / "code"
        sub = src / "sub"
        excluded = src / "__pycache__"
        sub.mkdir(parents=True)
        excluded.mkdir()
        (src / "main.py").write_bytes(b"print('hello')")
        (sub / "util.py").write_bytes(b"def foo(): pass")
        (excluded / "main.cpython.pyc").write_bytes(b"bytecode")

        mock_config = type(
            "MockConfig",
            (),
            {
                "SOURCE_DIRS": [
                    {
                        "path": str(src),
                        "extensions": [".py", ".pyc"],
                        "exclude": ["__pycache__"],
                    },
                ]
            },
        )
        files = manifest_module.get_source_files(cfg=mock_config)

        assert len(files) == 2
        # All files should be hashable
        for f in files:
            h = manifest_module.compute_file_hash(f)
            assert len(h) == 64
            assert h != ""

    def test_is_excluded_with_normalize_key(self):
        """Verify that is_excluded and normalize_file_key work together conceptually."""
        path = Path("source/__pycache__/module.pyc")
        assert manifest_module.is_excluded(path, ["__pycache__"]) is True

        # The key would still be normalized if we needed it
        key = manifest_module.normalize_file_key("source", "__pycache__/module.pyc")
        assert key == "source/__pycache__/module.pyc"

    def test_manifest_dict_building(self, tmp_path: Path):
        """Simulates building a manifest dict {key: hash} from source files."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.pas").write_bytes(b"unit A;")
        (src / "b.pas").write_bytes(b"unit B;")

        mock_config = type(
            "MockConfig",
            (),
            {
                "SOURCE_DIRS": [
                    {"path": str(src), "extensions": [".pas"]},
                ]
            },
        )
        files = manifest_module.get_source_files(cfg=mock_config)

        manifest = {}
        for f in files:
            key = manifest_module.normalize_file_key(
                str(src), f.relative_to(src).as_posix()
            )
            manifest[key] = manifest_module.compute_file_hash(f)

        assert len(manifest) == 2
        # All values are valid SHA256 hex strings
        for key, hash_val in manifest.items():
            assert len(hash_val) == 64
            assert all(c in "0123456789abcdef" for c in hash_val)

    @patch.object(manifest_module, "log_warn")
    def test_hash_error_does_not_break_pipeline(
        self, mock_warn: MagicMock, tmp_path: Path
    ):
        """A hash failure on one file returns '' but doesn't crash the pipeline."""
        src = tmp_path / "src"
        src.mkdir()
        good_file = src / "good.pas"
        good_file.write_bytes(b"unit Good;")

        good_hash = manifest_module.compute_file_hash(good_file)
        bad_hash = manifest_module.compute_file_hash(Path("/nonexistent/bad.pas"))

        assert len(good_hash) == 64
        assert bad_hash == ""
        mock_warn.assert_called_once()
