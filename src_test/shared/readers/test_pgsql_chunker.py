"""Tests for the PostgreSQL statement chunker."""

from shared.readers.pgsql_chunker import chunk_postgresql


_CONTRACTORS = """CREATE TABLE contractors
(
   name character varying(70) NOT NULL,
   contractor_id serial NOT NULL,
  CONSTRAINT contractors_pkey PRIMARY KEY (contractor_id)
)
WITH ( OIDS=FALSE );
COMMENT ON COLUMN contractors.accounting_id IS 'Contractor ID in the accounting system';

CREATE OR REPLACE FUNCTION process_update_contractors()
  RETURNS trigger AS
$BODY$
    BEGIN
    UPDATE customers SET name=NEW.name WHERE source_id=NEW.contractor_id AND source=3;
    RETURN NEW;
    END
$BODY$
  LANGUAGE plpgsql VOLATILE;

CREATE TRIGGER update_contractors
  AFTER UPDATE
  ON contractors
  FOR EACH ROW
  EXECUTE PROCEDURE process_update_contractors();
"""


def _one(chunks, object_type, object_name):
    matches = [
        chunk
        for chunk in chunks
        if chunk.object_type == object_type and chunk.object_name == object_name
    ]
    assert len(matches) == 1
    return matches[0]


class TestChunkPostgresql:
    def test_empty_file_has_no_chunks(self):
        assert chunk_postgresql("") == []
        assert chunk_postgresql("  \n\t") == []

    def test_mixed_script_splits_table_function_trigger_and_comment(self):
        chunks = chunk_postgresql(_CONTRACTORS)
        table = _one(chunks, "TABLE", "contractors")
        function = _one(chunks, "FUNCTION", "process_update_contractors")
        trigger = _one(chunks, "TRIGGER", "update_contractors")
        comment = _one(chunks, "COMMENT", "contractors.accounting_id")

        assert table.node_type == "pgsql_create_table"
        assert "PRIMARY KEY" in table.text
        assert "process_update_contractors" not in table.text
        assert table.text.startswith("-- Table: contractors")
        assert table.start_line == 1

        assert function.node_type == "pgsql_create_function"
        assert "UPDATE customers" in function.text
        assert "LANGUAGE plpgsql" in function.text
        assert function.text.startswith("-- Function: process_update_contractors")
        assert "process update contractors" in function.text
        assert function.start_line > table.end_line

        assert trigger.node_type == "pgsql_create_trigger"
        assert "EXECUTE PROCEDURE" in trigger.text
        assert comment.node_type == "pgsql_comment"
        assert "accounting system" in comment.text

    def test_dollar_quote_hides_semicolons(self):
        text = """
CREATE FUNCTION quote_job() RETURNS void AS
$$
BEGIN
  PERFORM 'a;b';
END
$$
LANGUAGE plpgsql;
"""
        chunks = chunk_postgresql(text)
        assert len(chunks) == 1
        chunk = chunks[0]
        assert chunk.object_name == "quote_job"
        assert chunk.object_type == "FUNCTION"
        assert "a;b" in chunk.text
        assert "LANGUAGE plpgsql" in chunk.text

    def test_create_procedure_uses_dollar_quotes(self):
        text = """
CREATE PROCEDURE public.do_work(a integer)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO t VALUES (a);
END;
$$;
"""
        chunks = chunk_postgresql(text)
        assert len(chunks) == 1
        assert chunks[0].object_type == "PROCEDURE"
        assert chunks[0].object_name == "public.do_work"
        assert chunks[0].node_type == "pgsql_create_procedure"
        assert "INSERT INTO t" in chunks[0].text

    def test_rule_and_quoted_index_names(self):
        text = """
CREATE OR REPLACE RULE bmfirma_notify_delete AS
    ON DELETE TO bmfirma DO
 NOTIFY bmfirma;
CREATE UNIQUE INDEX "idx name" ON bmfirma (kod);
CREATE TABLE public.firmy (id int);
"""
        chunks = chunk_postgresql(text)
        rule = _one(chunks, "RULE", "bmfirma_notify_delete")
        index = _one(chunks, "INDEX", "idx name")
        table = _one(chunks, "TABLE", "public.firmy")
        assert rule.node_type == "pgsql_create_rule"
        assert index.node_type == "pgsql_create_index"
        assert table.node_type == "pgsql_create_table"

    def test_semicolon_inside_quotes_is_not_a_split(self):
        text = (
            "INSERT INTO t VALUES ('a;b');\n"
            "SELECT 'kept-statement-text-long-enough-to-remain';\n"
        )
        chunks = chunk_postgresql(text)
        assert len(chunks) == 2
        assert "a;b" in chunks[0].text
        assert "SELECT" not in chunks[0].text
        assert "kept-statement-text" in chunks[1].text

    def test_semicolon_inside_parentheses_stays_in_the_rule(self):
        text = """
CREATE RULE r AS ON INSERT TO t DO INSTEAD (
  INSERT INTO a VALUES (1);
  INSERT INTO b VALUES (2);
);
"""
        chunks = chunk_postgresql(text)
        assert len(chunks) == 1
        assert chunks[0].object_name == "r"
        assert "INSERT INTO a" in chunks[0].text
        assert "INSERT INTO b" in chunks[0].text

    def test_long_statement_is_split(self):
        rows = ",\n".join(f"('{i:05d}')" for i in range(2000))
        text = f"INSERT INTO miejscowosci VALUES\n{rows};\n"
        chunks = chunk_postgresql(text)
        assert len(chunks) >= 2
        assert all(chunk.node_type == "pgsql_statement_split" for chunk in chunks)
        assert all(len(chunk.text) <= 12000 for chunk in chunks)
        assert all(chunk.text.startswith("-- Insert: miejscowosci") for chunk in chunks)
        assert all(chunk.object_name == "miejscowosci" for chunk in chunks)
        joined = "\n".join(chunk.text for chunk in chunks)
        assert "('00000')" in joined
        assert "('01999')" in joined
