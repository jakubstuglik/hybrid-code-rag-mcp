"""Tests for SQL dialect normalization and change detection."""

import pytest

from shared.sql_dialect import (
    canonical_sql_dialect,
    effective_sql_dialect,
    manifest_dialect_fields,
    sql_dialect_changed,
    sql_dialect_for_file,
)


class TestEffectiveSqlDialect:
    def test_missing_entry_is_tsql(self):
        assert effective_sql_dialect(None) == "tsql"
        assert effective_sql_dialect({}) == "tsql"

    def test_blank_is_tsql(self):
        assert effective_sql_dialect({"sql_dialect": "  "}) == "tsql"

    def test_case_is_folded(self):
        assert effective_sql_dialect({"sql_dialect": "PostgreSQL"}) == "postgresql"

    def test_unknown_value_is_kept(self):
        """A stored unknown value must not look like the tsql default."""
        assert effective_sql_dialect({"sql_dialect": "mysql"}) == "mysql"


class TestCanonicalSqlDialect:
    def test_postgresql_alias_is_canonical(self):
        assert canonical_sql_dialect(" PostgreSQL ") == "postgresql"

    def test_tsql_is_canonical(self):
        assert canonical_sql_dialect("tsql") == "tsql"

    def test_unknown_dialect_is_rejected(self):
        with pytest.raises(RuntimeError, match="mysql"):
            canonical_sql_dialect("mysql", " (in cfg.py)")

    def test_blank_dialect_is_rejected(self):
        with pytest.raises(RuntimeError, match="sql_dialect"):
            canonical_sql_dialect("  ", " at SOURCE_DIRS[0]")


class TestSqlDialectChanged:
    def test_missing_manifest_matches_tsql(self):
        old = {"hash": "h1"}
        current = {"hash": "h1", "sql_dialect": "tsql"}
        assert sql_dialect_changed(old, current) is False

    def test_missing_manifest_differs_from_postgresql(self):
        old = {"hash": "h1"}
        current = {"hash": "h1", "sql_dialect": "postgresql"}
        assert sql_dialect_changed(old, current) is True

    def test_same_postgresql_is_unchanged(self):
        old = {"sql_dialect": "postgresql"}
        current = {"sql_dialect": "PostgreSQL"}
        assert sql_dialect_changed(old, current) is False


class TestFileAndManifestFields:
    def test_sql_file_defaults_to_tsql(self):
        assert sql_dialect_for_file({}, "create_contractors.sql") == {
            "sql_dialect": "tsql"
        }

    def test_sql_file_keeps_postgresql(self):
        entry = {"sql_dialect": "postgresql"}
        assert sql_dialect_for_file(entry, "Create.SQL") == {
            "sql_dialect": "postgresql"
        }

    def test_non_sql_file_has_no_dialect_field(self):
        entry = {"sql_dialect": "postgresql"}
        assert sql_dialect_for_file(entry, "unit.pas") == {}

    def test_manifest_stores_dialect_for_sql_only(self):
        sql_info = {"file_path": "sql/create_contractors.sql"}
        pas_info = {"file_path": "Src/main.cpp", "sql_dialect": "postgresql"}
        assert manifest_dialect_fields(sql_info) == {"sql_dialect": "tsql"}
        assert manifest_dialect_fields(pas_info) == {}

    def test_manifest_stores_configured_dialect(self):
        info = {
            "file_path": "Resources/sql/create_contractors.sql",
            "sql_dialect": "postgresql",
        }
        assert manifest_dialect_fields(info) == {"sql_dialect": "postgresql"}
