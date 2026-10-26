"""Tests for SQL dialect selection in SQLFileReader."""

from pathlib import Path

from shared.readers import load_nodes_for_file
from shared.readers.sql_reader import SQLFileReader
from shared.readers.tsql_chunker import chunk_tsql


_PLPGSQL = """CREATE TABLE contractors
(
   name character varying(70) NOT NULL,
   contractor_id serial NOT NULL
);
CREATE OR REPLACE FUNCTION process_update_contractors()
  RETURNS trigger AS
$BODY$
    BEGIN
    UPDATE customers SET name=NEW.name WHERE source_id=NEW.contractor_id;
    RETURN NEW;
    END
$BODY$
  LANGUAGE plpgsql VOLATILE;
CREATE TRIGGER update_contractors
  AFTER UPDATE ON contractors
  FOR EACH ROW EXECUTE PROCEDURE process_update_contractors();
"""

_TSQL = "CREATE PROCEDURE dbo.MyProc @Id int AS BEGIN SELECT @Id; END\nGO\n"


def _write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


class TestSqlDialectPath:
    def test_default_dialect_still_uses_tsql_chunker(self, tmp_path):
        path = _write(tmp_path, "proc.sql", _TSQL)
        docs = SQLFileReader().load_data(path)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "procedure_full"
        assert docs[0].metadata["object_name"] == "dbo.MyProc"

    def test_explicit_tsql_matches_the_default(self, tmp_path):
        path = _write(tmp_path, "proc.sql", _TSQL)
        docs = SQLFileReader().load_data(path, {"sql_dialect": "tsql"})
        assert docs[0].metadata["node_type"] == "procedure_full"

    def test_postgresql_chunks_keep_object_names(self, tmp_path):
        path = _write(tmp_path, "create_contractors.sql", _PLPGSQL)
        docs = SQLFileReader().load_data(path, {"sql_dialect": "PostgreSQL"})
        by_name = {doc.metadata.get("object_name"): doc for doc in docs}
        assert by_name["contractors"].metadata["object_type"] == "TABLE"
        assert by_name["contractors"].metadata["node_type"] == "pgsql_create_table"
        function = by_name["process_update_contractors"]
        assert function.metadata["object_type"] == "FUNCTION"
        assert function.metadata["node_type"] == "pgsql_create_function"
        assert "UPDATE customers" in function.text
        assert "LANGUAGE plpgsql" in function.text
        assert by_name["update_contractors"].metadata["object_type"] == "TRIGGER"
        assert "sql_dialect" not in function.metadata
        assert "hash" not in function.metadata

    def test_postgresql_does_not_call_tsql_chunker(self, tmp_path, monkeypatch):
        calls = {"n": 0}
        real = chunk_tsql

        def _wrap(content):
            calls["n"] += 1
            return real(content)

        monkeypatch.setattr("shared.readers.sql_reader.chunk_tsql", _wrap)
        path = _write(tmp_path, "proc.sql", _TSQL)
        docs = SQLFileReader().load_data(path, {"sql_dialect": "postgresql"})
        assert calls["n"] == 0
        assert docs
        assert all(
            doc.metadata["node_type"].startswith("pgsql_") for doc in docs
        )

    def test_registry_forwards_dialect_from_file_info(self, tmp_path):
        path = _write(tmp_path, "create_contractors.sql", _PLPGSQL)
        nodes = load_nodes_for_file(
            {
                "full_path": str(path),
                "file_path": "sql/create_contractors.sql",
                "sql_dialect": "postgresql",
                "hash": "abc",
                "mtime": 1,
            }
        )
        names = {node.metadata.get("object_name") for node in nodes}
        assert "process_update_contractors" in names
        assert nodes[0].metadata["file_path"] == "sql/create_contractors.sql"
        assert "hash" not in nodes[0].metadata
        assert "mtime" not in nodes[0].metadata


_SKIP_META = {"file_path", "creation_datetime", "modification_datetime"}

_PG_FUNCTION = """CREATE OR REPLACE FUNCTION calc_order_discount(order_total numeric)
RETURNS numeric AS $BODY$
BEGIN
    RETURN order_total * 0.1;
END
$BODY$ LANGUAGE plpgsql;
"""

_PG_TABLE = """CREATE TABLE customer_orders (
    order_id integer NOT NULL,
    customer_id integer NOT NULL
);
"""

_TSQL_PROC = (
    "CREATE PROCEDURE dbo.calc_order_discount @OrderTotal int AS "
    "BEGIN SELECT @OrderTotal; END\nGO\n"
)


def _write_bytes(directory: Path, name: str, data: bytes) -> Path:
    path = directory / name
    path.write_bytes(data)
    return path


def _pair(tmp_path: Path, name: str, body: str, extra=None):
    raw = body.encode("utf-8")
    bom_dir = tmp_path / "bom"
    plain_dir = tmp_path / "plain"
    bom_dir.mkdir()
    plain_dir.mkdir()
    reader = SQLFileReader()
    bom_docs = reader.load_data(
        _write_bytes(bom_dir, name, b"\xef\xbb\xbf" + raw), extra
    )
    plain_docs = reader.load_data(_write_bytes(plain_dir, name, raw), extra)
    return bom_docs, plain_docs


def _signature(docs):
    signed = []
    for doc in docs:
        meta = {key: value for key, value in doc.metadata.items() if key not in _SKIP_META}
        signed.append((doc.text, meta))
    return signed


def _assert_no_bom(docs):
    for doc in docs:
        assert "\ufeff" not in doc.text
        for value in doc.metadata.values():
            if isinstance(value, str):
                assert "\ufeff" not in value


class TestLeadingUtf8Bom:
    def test_postgresql_function_keeps_name_and_matches_plain(self, tmp_path):
        bom_docs, plain_docs = _pair(
            tmp_path, "discount.sql", _PG_FUNCTION, {"sql_dialect": "postgresql"}
        )
        assert len(bom_docs) == 1
        assert bom_docs[0].metadata["node_type"] == "pgsql_create_function"
        assert bom_docs[0].metadata["object_name"] == "calc_order_discount"
        assert bom_docs[0].metadata["start_line"] == 1
        assert plain_docs[0].metadata["start_line"] == 1
        _assert_no_bom(bom_docs)
        assert _signature(bom_docs) == _signature(plain_docs)

    def test_postgresql_table_keeps_name_and_matches_plain(self, tmp_path):
        bom_docs, plain_docs = _pair(
            tmp_path, "orders.sql", _PG_TABLE, {"sql_dialect": "postgresql"}
        )
        assert len(bom_docs) == 1
        assert bom_docs[0].metadata["node_type"] == "pgsql_create_table"
        assert bom_docs[0].metadata["object_name"] == "customer_orders"
        assert bom_docs[0].metadata["start_line"] == 1
        assert plain_docs[0].metadata["start_line"] == 1
        _assert_no_bom(bom_docs)
        assert _signature(bom_docs) == _signature(plain_docs)

    def test_tsql_procedure_keeps_name_and_matches_plain(self, tmp_path):
        bom_docs, plain_docs = _pair(tmp_path, "discount.sql", _TSQL_PROC)
        assert len(bom_docs) == 1
        assert bom_docs[0].metadata["node_type"] == "procedure_full"
        assert bom_docs[0].metadata["object_name"] == "dbo.calc_order_discount"
        assert bom_docs[0].metadata["start_line"] == 1
        assert plain_docs[0].metadata["start_line"] == 1
        assert "@OrderTotal" in bom_docs[0].text
        _assert_no_bom(bom_docs)
        assert _signature(bom_docs) == _signature(plain_docs)
