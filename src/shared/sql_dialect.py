"""SQL dialect names shared by config loading and the indexer.

A missing dialect means T-SQL. That keeps existing indexes on the chunker
they were built with. PostgreSQL is selected per source path, not by sniffing
the file.
"""

from typing import Optional

DEFAULT_SQL_DIALECT = "tsql"
ALLOWED_SQL_DIALECTS = frozenset({DEFAULT_SQL_DIALECT, "postgresql"})


def effective_sql_dialect(entry: Optional[dict]) -> str:
    """Return the dialect stored on a manifest or file-state dict.

    A missing or blank value is ``tsql``. Any other text is stripped and
    lower-cased, including values this project does not index. Change
    detection uses that so a bad stored value does not look like the default.
    """
    if not entry:
        return DEFAULT_SQL_DIALECT
    raw = entry.get("sql_dialect")
    if not isinstance(raw, str):
        return DEFAULT_SQL_DIALECT
    text = raw.strip().lower()
    if not text:
        return DEFAULT_SQL_DIALECT
    return text


def canonical_sql_dialect(value: object, location: str = "") -> str:
    """Validate a config value and return ``tsql`` or ``postgresql``.

    Args:
        value: Raw ``sql_dialect`` from a SOURCE_DIRS entry.
        location: Suffix for the error, such as ``" at SOURCE_DIRS[0]"``.

    Raises:
        RuntimeError: The value is blank or not one of the allowed dialects.
    """
    where = location or ""
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(
            f"sql_dialect must be 'tsql' or 'postgresql'{where}."
        )
    text = value.strip().lower()
    if text not in ALLOWED_SQL_DIALECTS:
        raise RuntimeError(
            f"sql_dialect must be 'tsql' or 'postgresql', got {value!r}{where}."
        )
    return text


def sql_dialect_changed(old_entry: Optional[dict], current: Optional[dict]) -> bool:
    """True when the file must be re-chunked because the dialect changed."""
    return effective_sql_dialect(old_entry) != effective_sql_dialect(current)


def sql_dialect_for_file(source_entry: dict, filename: str) -> dict:
    """Dialect field for one file state. Only ``.sql`` files carry it."""
    if not str(filename).lower().endswith(".sql"):
        return {}
    return {"sql_dialect": effective_sql_dialect(source_entry)}


def manifest_dialect_fields(file_info: dict) -> dict:
    """Dialect field stored in the manifest. Only ``.sql`` files carry it.

    A missing value on an old manifest still means ``tsql``. Writing the
    default on newly indexed SQL files does not by itself force a reindex,
    because change detection treats a missing value as ``tsql``.
    """
    path = file_info.get("file_path") or file_info.get("full_path") or ""
    if not str(path).lower().endswith(".sql"):
        return {}
    return {"sql_dialect": effective_sql_dialect(file_info)}
