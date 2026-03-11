"""
Tests for shared/readers/tsql_chunker.py -- heuristic T-SQL chunker.

Tests cover:
    - TSqlChunk dataclass, Constants, _split_on_go, _is_preamble_batch
    - _is_ddl_batch, _classify_ddl_batch, _detect_object, _extract_parameters
    - _make_context_prefix, _find_body_start, _find_declarations_end
    - _find_section_boundaries, _find_dynamic_sql_ranges, _split_at_boundaries
    - _group_small_ddl_batches, _force_split_oversized, chunk_tsql
    - Integration with real test_sources SQL files
"""

from pathlib import Path
from typing import List

import pytest

from shared.readers.tsql_chunker import (
    TSqlChunk,
    MIN_CHUNK_CHARS,
    MAX_CHUNK_CHARS,
    FORCE_SPLIT_CHARS,
    chunk_tsql,
    _split_on_go,
    _is_preamble_batch,
    _is_ddl_batch,
    _classify_ddl_batch,
    _detect_object,
    _extract_parameters,
    _make_context_prefix,
    _find_body_start,
    _find_declarations_end,
    _find_section_boundaries,
    _find_dynamic_sql_ranges,
    _split_at_boundaries,
    _group_small_ddl_batches,
    _force_split_oversized,
)


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_TEST_SOURCES = _PROJECT_ROOT / "test_sources"


def _chunk_node_types(chunks):
    return [c.node_type for c in chunks]


# ----
# TestTSqlChunk
# ----


class TestTSqlChunk:
    """Tests for the TSqlChunk dataclass."""

    def test_required_fields(self):
        """TSqlChunk should require text, node_type, start_line, end_line."""
        chunk = TSqlChunk(
            text="SELECT 1", node_type="sql_batch", start_line=1, end_line=1
        )
        assert chunk.text == "SELECT 1"
        assert chunk.node_type == "sql_batch"
        assert chunk.start_line == 1
        assert chunk.end_line == 1

    def test_optional_fields_default_to_none(self):
        """object_name, object_type, parameters should default to None."""
        chunk = TSqlChunk(text="X", node_type="t", start_line=1, end_line=1)
        assert chunk.object_name is None
        assert chunk.object_type is None
        assert chunk.parameters is None

    def test_is_dataclass(self):
        """TSqlChunk should be a dataclass."""
        assert hasattr(TSqlChunk, "__dataclass_fields__")


class TestConstants:
    """Tests for module-level constants."""

    def test_min_chunk_chars(self):
        assert MIN_CHUNK_CHARS == 100

    def test_max_chunk_chars(self):
        assert MAX_CHUNK_CHARS == 12000

    def test_force_split_chars(self):
        assert FORCE_SPLIT_CHARS == 16000

    def test_min_less_than_max(self):
        assert MIN_CHUNK_CHARS < MAX_CHUNK_CHARS

    def test_max_less_than_force_split(self):
        assert MAX_CHUNK_CHARS < FORCE_SPLIT_CHARS


class TestSplitOnGo:
    """Tests for _split_on_go() -- GO batch boundary splitting."""

    def test_single_batch_no_go(self):
        lines = ["SELECT 1", "SELECT 2"]
        batches = _split_on_go(lines)
        assert len(batches) == 1
        assert batches[0][0] == ["SELECT 1", "SELECT 2"]

    def test_two_batches(self):
        lines = ["SELECT 1", "GO", "SELECT 2"]
        batches = _split_on_go(lines)
        assert len(batches) == 2
        assert batches[0][0] == ["SELECT 1"]
        assert batches[1][0] == ["SELECT 2"]

    def test_go_case_insensitive(self):
        lines = ["SELECT 1", "go", "SELECT 2"]
        assert len(_split_on_go(lines)) == 2

    def test_go_with_whitespace(self):
        lines = ["SELECT 1", "  GO  ", "SELECT 2"]
        assert len(_split_on_go(lines)) == 2

    def test_empty_batches_dropped(self):
        lines = ["SELECT 1", "GO", "GO", "SELECT 2"]
        assert len(_split_on_go(lines)) == 2

    def test_trailing_go(self):
        lines = ["SELECT 1", "GO"]
        assert len(_split_on_go(lines)) == 1

    def test_empty_input(self):
        assert _split_on_go([]) == []

    def test_three_batches(self):
        lines = ["A", "GO", "B", "GO", "C"]
        assert len(_split_on_go(lines)) == 3


class TestIsPreambleBatch:
    """Tests for _is_preamble_batch()."""

    def test_quoted_identifier(self):
        assert _is_preamble_batch(["SET QUOTED_IDENTIFIER ON"]) is True

    def test_ansi_nulls(self):
        assert _is_preamble_batch(["SET ANSI_NULLS ON"]) is True

    def test_nocount(self):
        assert _is_preamble_batch(["SET NOCOUNT ON"]) is True

    def test_multiple_preamble(self):
        assert (
            _is_preamble_batch(["SET QUOTED_IDENTIFIER ON", "", "SET ANSI_NULLS ON"])
            is True
        )

    def test_non_preamble_set(self):
        assert _is_preamble_batch(["SET @Var = 1"]) is False

    def test_create_proc_not_preamble(self):
        assert _is_preamble_batch(["CREATE PROCEDURE dbo.Foo"]) is False

    def test_empty_lines_only(self):
        assert _is_preamble_batch(["", "  "]) is True

    def test_mixed_preamble_and_code(self):
        assert _is_preamble_batch(["SET ANSI_NULLS ON", "SELECT 1"]) is False


class TestIsDdlBatch:
    """Tests for _is_ddl_batch()."""

    def test_alter_table(self):
        assert _is_ddl_batch(["ALTER TABLE dbo.Foo ADD CONSTRAINT ..."]) is True

    def test_create_index(self):
        assert _is_ddl_batch(["CREATE NONCLUSTERED INDEX IX_Foo ON dbo.T"]) is True

    def test_exec_statement(self):
        assert _is_ddl_batch(["EXEC sp_addextendedproperty"]) is True

    def test_create_proc_not_ddl(self):
        assert _is_ddl_batch(["CREATE PROCEDURE dbo.Foo AS SELECT 1"]) is False

    def test_select_not_ddl(self):
        assert _is_ddl_batch(["SELECT * FROM dbo.T"]) is False

    def test_comment_then_alter(self):
        assert _is_ddl_batch(["-- FK", "ALTER TABLE dbo.Foo ADD CONSTRAINT"]) is True

    def test_empty_batch(self):
        assert _is_ddl_batch([]) is False


class TestClassifyDdlBatch:
    """Tests for _classify_ddl_batch()."""

    def test_alter_table(self):
        assert _classify_ddl_batch(["ALTER TABLE dbo.T ADD x INT"]) == "alter_table"

    def test_create_index(self):
        assert (
            _classify_ddl_batch(["CREATE NONCLUSTERED INDEX IX ON dbo.T(x)"])
            == "create_index"
        )

    def test_exec(self):
        assert _classify_ddl_batch(["EXEC sp_something"]) == "exec_statement"

    def test_unknown(self):
        assert _classify_ddl_batch(["SELECT 1"]) == "ddl_statement"


class TestDetectObject:
    """Tests for _detect_object()."""

    def test_create_procedure(self):
        lines = ["CREATE PROCEDURE [dbo].[MyProc]", "@x INT", "AS", "SELECT 1"]
        obj_type, obj_name, params = _detect_object(lines)
        assert obj_type == "PROCEDURE"
        assert obj_name == "[dbo].[MyProc]"

    def test_create_function(self):
        lines = ["CREATE FUNCTION dbo.MyFunc(@x INT)", "RETURNS TABLE"]
        obj_type, obj_name, _ = _detect_object(lines)
        assert obj_type == "FUNCTION"
        assert obj_name == "dbo.MyFunc"

    def test_create_table(self):
        lines = ["CREATE TABLE [dbo].[SLS_Ticket]", "(", "[ID] bigint NOT NULL"]
        obj_type, obj_name, _ = _detect_object(lines)
        assert obj_type == "TABLE"

    def test_no_create_returns_none(self):
        obj_type, obj_name, params = _detect_object(["SELECT * FROM dbo.T"])
        assert obj_type is None
        assert obj_name is None
        assert params is None

    def test_alter_table_detected(self):
        lines = ["ALTER TABLE [dbo].[SLS_Ticket] ADD CONSTRAINT FK_X"]
        obj_type, _, _ = _detect_object(lines)
        assert obj_type == "TABLE"

    def test_procedure_extracts_params(self):
        lines = [
            "CREATE PROCEDURE dbo.MyProc(",
            "  @x INT,",
            "  @y NVARCHAR(50)",
            ")",
            "AS",
            "BEGIN",
        ]
        _, _, params = _detect_object(lines)
        assert params is not None
        assert "@x" in params
        assert "@y" in params

    def test_table_no_params(self):
        lines = ["CREATE TABLE [dbo].[T]", "(", "[ID] INT"]
        _, _, params = _detect_object(lines)
        assert params is None


class TestExtractParameters:
    """Tests for _extract_parameters()."""

    def test_single_param_inline(self):
        lines = ["CREATE PROCEDURE dbo.Foo(@x INT)", "AS", "SELECT 1"]
        result = _extract_parameters(lines)
        assert result is not None
        assert "@x INT" in result

    def test_multi_line_params(self):
        lines = [
            "CREATE PROCEDURE [dbo].[Bar](",
            "  @a NVARCHAR(10),",
            "  @b INT = 0",
            ")",
            "AS",
        ]
        result = _extract_parameters(lines)
        assert "@a" in result
        assert "@b" in result

    def test_no_params_returns_none(self):
        lines = ["CREATE PROCEDURE dbo.NoParams", "AS", "SELECT 1"]
        assert _extract_parameters(lines) is None

    def test_stops_at_as(self):
        lines = [
            "CREATE PROCEDURE dbo.Foo(",
            "  @x INT",
            ")",
            "AS",
            "BEGIN",
            "  DECLARE @y INT",
        ]
        result = _extract_parameters(lines)
        assert "@x" in result
        assert "@y" not in result

    def test_comments_skipped(self):
        lines = [
            "CREATE PROCEDURE dbo.Foo(",
            "  @a INT,",
            "  -- comment",
            "  @b VARCHAR(20)",
            ")",
            "AS",
        ]
        result = _extract_parameters(lines)
        assert "@a" in result
        assert "@b" in result

    def test_no_create_returns_none(self):
        assert _extract_parameters(["SELECT 1"]) is None

    def test_long_params_truncated(self):
        params = ", ".join([f"@p{i} NVARCHAR(MAX)" for i in range(30)])
        lines = [f"CREATE PROCEDURE dbo.Big({params})", "AS"]
        result = _extract_parameters(lines)
        assert len(result) <= 200


class TestMakeContextPrefix:
    """Tests for _make_context_prefix()."""

    def test_procedure_with_params(self):
        prefix = _make_context_prefix("PROCEDURE", "dbo.MyProc", "@x INT")
        assert "-- Procedure: dbo.MyProc" in prefix
        assert "-- Parameters: @x INT" in prefix

    def test_no_params(self):
        prefix = _make_context_prefix("FUNCTION", "dbo.MyFunc", None)
        assert "-- Function: dbo.MyFunc" in prefix
        assert "Parameters" not in prefix

    def test_none_name_returns_empty(self):
        assert _make_context_prefix("PROCEDURE", None, None) == ""

    def test_ends_with_newline(self):
        prefix = _make_context_prefix("PROCEDURE", "dbo.X", None)
        assert prefix.endswith("\n")

    def test_none_type_uses_object(self):
        prefix = _make_context_prefix(None, "dbo.X", None)
        assert "-- Object: dbo.X" in prefix


class TestFindBodyStart:
    """Tests for _find_body_start()."""

    def test_standalone_as(self):
        lines = ["CREATE PROCEDURE dbo.Foo", "AS", "SELECT 1"]
        assert _find_body_start(lines) == 2

    def test_as_begin(self):
        lines = ["CREATE PROCEDURE dbo.Foo", "AS", "BEGIN", "SELECT 1"]
        assert _find_body_start(lines) == 3

    def test_as_begin_same_line(self):
        lines = ["CREATE PROCEDURE dbo.Foo", "AS BEGIN", "SELECT 1"]
        assert _find_body_start(lines) == 2

    def test_no_as_returns_none(self):
        lines = ["SELECT 1", "FROM dbo.T"]
        assert _find_body_start(lines) is None


class TestFindDeclarationsEnd:
    """Tests for _find_declarations_end()."""

    def test_declare_lines_included(self):
        lines = ["DECLARE @x INT", "DECLARE @y VARCHAR(50)", "SELECT @x, @y"]
        assert _find_declarations_end(lines, 0) == 2

    def test_set_variable_included(self):
        lines = ["DECLARE @x INT", "SET @x = 1", "SELECT @x"]
        assert _find_declarations_end(lines, 0) == 2

    def test_empty_lines_dont_stop(self):
        lines = ["DECLARE @x INT", "", "SET @x = 1", "SELECT @x"]
        assert _find_declarations_end(lines, 0) == 3

    def test_select_ends_declarations(self):
        lines = ["DECLARE @x INT", "SELECT * FROM dbo.T"]
        assert _find_declarations_end(lines, 0) == 1

    def test_body_start_offset(self):
        lines = [
            "CREATE PROCEDURE dbo.Foo",
            "AS",
            "BEGIN",
            "DECLARE @x INT",
            "SET @x = 1",
            "SELECT @x",
        ]
        assert _find_declarations_end(lines, 3) == 5

    def test_set_preamble_included(self):
        lines = ["SET NOCOUNT ON", "DECLARE @x INT", "SELECT @x"]
        assert _find_declarations_end(lines, 0) == 2

    def test_no_declarations(self):
        lines = ["SELECT 1 AS x", "FROM dbo.T"]
        assert _find_declarations_end(lines, 0) == 0


class TestFindSectionBoundaries:
    """Tests for _find_section_boundaries()."""

    def test_dash_separator(self):
        lines = ["SELECT 1", "-" * 20, "SELECT 2"]
        assert 1 in _find_section_boundaries(lines)

    def test_union_all(self):
        lines = ["SELECT 1", "UNION ALL", "SELECT 2"]
        assert 1 in _find_section_boundaries(lines)

    def test_union_alone(self):
        lines = ["SELECT 1", "UNION", "SELECT 2"]
        assert 1 in _find_section_boundaries(lines)

    def test_goto_label(self):
        lines = ["SELECT 1", "MyLabel:", "SELECT 2"]
        assert 1 in _find_section_boundaries(lines)

    def test_no_boundaries(self):
        lines = ["SELECT a, b", "FROM dbo.T", "WHERE x = 1"]
        assert _find_section_boundaries(lines) == []

    def test_consecutive_dashes_single_boundary(self):
        lines = [
            "SELECT 1",
            "-" * 25,
            "-" * 22 + "BILETY" + "-" * 3,
            "-" * 25,
            "SELECT 2",
        ]
        boundaries = _find_section_boundaries(lines)
        assert len(boundaries) == 1
        assert 1 in boundaries

    def test_boundary_not_at_line_zero(self):
        lines = ["UNION ALL", "SELECT 1"]
        assert 0 not in _find_section_boundaries(lines)


class TestFindDynamicSqlRanges:
    """Tests for _find_dynamic_sql_ranges()."""

    def test_simple_dynamic_sql(self):
        lines = [
            "SET @Sql = 'SELECT 1'",
            "SET @Sql = @Sql + ' FROM dbo.T'",
            "EXEC(@Sql)",
        ]
        ranges = _find_dynamic_sql_ranges(lines)
        assert len(ranges) == 1
        assert ranges[0] == (0, 2)

    def test_no_dynamic_sql(self):
        lines = ["SELECT 1", "FROM dbo.T"]
        assert _find_dynamic_sql_ranges(lines) == []

    def test_with_if_append(self):
        lines = [
            "SET @Sql = 'SELECT 1'",
            "IF @flag = 1 SET @Sql = @Sql + ' WHERE x = 1'",
            "EXEC(@Sql)",
        ]
        ranges = _find_dynamic_sql_ranges(lines)
        assert len(ranges) == 1
        assert ranges[0] == (0, 2)


class TestSplitAtBoundaries:
    """Tests for _split_at_boundaries()."""

    def test_no_boundaries(self):
        lines = ["A", "B", "C"]
        sections = _split_at_boundaries(lines, [])
        assert len(sections) == 1
        assert sections[0][0] == ["A", "B", "C"]

    def test_single_boundary(self):
        lines = ["A", "B", "C", "D"]
        sections = _split_at_boundaries(lines, [2])
        assert len(sections) == 2
        assert sections[0][0] == ["A", "B"]
        assert sections[1][0] == ["C", "D"]

    def test_multiple_boundaries(self):
        lines = ["A", "B", "C", "D", "E"]
        sections = _split_at_boundaries(lines, [1, 3])
        assert len(sections) == 3

    def test_empty_body(self):
        assert _split_at_boundaries([], []) == []


class TestGroupSmallDdlBatches:
    """Tests for _group_small_ddl_batches()."""

    def test_no_ddl_unchanged(self):
        chunks = [
            TSqlChunk(
                text="X" * 200, node_type="procedure_body", start_line=1, end_line=10
            )
        ]
        result = _group_small_ddl_batches(chunks)
        assert len(result) == 1

    def test_small_ddl_grouped(self):
        chunks = [
            TSqlChunk(
                text="ALTER TABLE T1 ADD x INT",
                node_type="alter_table",
                start_line=1,
                end_line=2,
            ),
            TSqlChunk(
                text="ALTER TABLE T1 ADD y INT",
                node_type="alter_table",
                start_line=3,
                end_line=4,
            ),
            TSqlChunk(
                text="ALTER TABLE T1 ADD z INT",
                node_type="alter_table",
                start_line=5,
                end_line=6,
            ),
        ]
        result = _group_small_ddl_batches(chunks)
        assert len(result) == 1
        assert "T1 ADD x" in result[0].text
        assert "T1 ADD z" in result[0].text

    def test_grouped_same_type_suffix(self):
        chunks = [
            TSqlChunk(
                text="ALTER TABLE T ADD a",
                node_type="alter_table",
                start_line=1,
                end_line=1,
            ),
            TSqlChunk(
                text="ALTER TABLE T ADD b",
                node_type="alter_table",
                start_line=2,
                end_line=2,
            ),
        ]
        result = _group_small_ddl_batches(chunks)
        assert result[0].node_type == "alter_table_group"

    def test_mixed_types_ddl_group(self):
        chunks = [
            TSqlChunk(
                text="ALTER TABLE T ADD a",
                node_type="alter_table",
                start_line=1,
                end_line=1,
            ),
            TSqlChunk(
                text="CREATE INDEX IX ON T(a)",
                node_type="create_index",
                start_line=2,
                end_line=2,
            ),
        ]
        result = _group_small_ddl_batches(chunks)
        assert result[0].node_type == "ddl_group"

    def test_single_ddl_no_group_suffix(self):
        chunks = [
            TSqlChunk(
                text="ALTER TABLE T ADD a",
                node_type="alter_table",
                start_line=1,
                end_line=1,
            )
        ]
        result = _group_small_ddl_batches(chunks)
        assert result[0].node_type == "alter_table"

    def test_group_preserves_lines(self):
        chunks = [
            TSqlChunk(
                text="ALTER TABLE T ADD a",
                node_type="alter_table",
                start_line=10,
                end_line=12,
            ),
            TSqlChunk(
                text="ALTER TABLE T ADD b",
                node_type="alter_table",
                start_line=15,
                end_line=18,
            ),
        ]
        result = _group_small_ddl_batches(chunks)
        assert result[0].start_line == 10
        assert result[0].end_line == 18


class TestForceSplitOversized:
    """Tests for _force_split_oversized()."""

    def test_normal_chunk_unchanged(self):
        chunk = TSqlChunk(
            text="SELECT 1\n" * 10,
            node_type="procedure_body",
            start_line=1,
            end_line=10,
        )
        result = _force_split_oversized([chunk])
        assert len(result) == 1

    def test_oversized_chunk_split(self):
        big_text = "\n".join([f"SELECT column_{i}" for i in range(2000)])
        chunk = TSqlChunk(
            text=big_text,
            node_type="procedure_body",
            start_line=1,
            end_line=2000,
            object_name="dbo.BigProc",
            object_type="PROCEDURE",
        )
        result = _force_split_oversized([chunk])
        assert len(result) > 1
        for sub in result:
            assert len(sub.text) <= FORCE_SPLIT_CHARS + 500

    def test_split_preserves_node_type(self):
        big_text = "\n".join([f"SELECT col{i}" for i in range(2000)])
        chunk = TSqlChunk(
            text=big_text, node_type="procedure_body", start_line=1, end_line=2000
        )
        for sub in _force_split_oversized([chunk]):
            assert sub.node_type == "procedure_body"

    def test_split_preserves_object_info(self):
        big_text = "\n".join([f"-- line {i}" for i in range(2000)])
        chunk = TSqlChunk(
            text=big_text,
            node_type="procedure_body",
            start_line=1,
            end_line=2000,
            object_name="dbo.BigProc",
            object_type="PROCEDURE",
        )
        for sub in _force_split_oversized([chunk]):
            assert sub.object_name == "dbo.BigProc"

    def test_empty_list(self):
        assert _force_split_oversized([]) == []


class TestChunkTsql:
    """Tests for chunk_tsql() -- the main entry point."""

    def test_empty_content(self):
        assert chunk_tsql("") == []

    def test_preamble_only_skipped(self):
        content = "SET QUOTED_IDENTIFIER ON\nGO\nSET ANSI_NULLS ON\nGO"
        assert chunk_tsql(content) == []

    def test_simple_procedure(self):
        content = (
            "SET ANSI_NULLS ON\nGO\n"
            "CREATE PROCEDURE dbo.SimpleProc(@x INT)\n"
            "AS\n"
            "BEGIN\n"
            "  DECLARE @y INT\n"
            "  SET @y = @x + 1\n"
            "  SELECT @y FROM dbo.Table1 WHERE Column1 = @x AND Column2 IS NOT NULL AND Column3 > 0\n"
            "END\nGO"
        )
        result = chunk_tsql(content)
        assert len(result) >= 1
        assert any(c.object_name is not None for c in result)

    def test_small_chunks_filtered(self):
        content = "SET ANSI_NULLS ON\nGO\nSELECT 1\nGO"
        for c in chunk_tsql(content):
            assert len(c.text.strip()) >= MIN_CHUNK_CHARS

    def test_procedure_body_has_context_prefix(self):
        content = (
            "CREATE PROCEDURE [dbo].[TestProc](\n"
            "  @a INT,\n  @b VARCHAR(50)\n)\nAS\nBEGIN\n"
            "  DECLARE @x INT\n  SET @x = 1\n"
            "  " + "-" * 30 + "\n"
            "  SELECT @x FROM dbo.Table1 WHERE Column1 = @a AND Column2 = @b AND LEN(Column3) > 10\n"
            "  " + "-" * 30 + "\n"
            "  SELECT @x FROM dbo.Table2 WHERE Column4 = @a AND Column5 = @b AND Column6 IS NOT NULL\n"
            "END\n"
        )
        body_chunks = [c for c in chunk_tsql(content) if "body" in c.node_type]
        for c in body_chunks:
            assert "-- Procedure: [dbo].[TestProc]" in c.text

    def test_all_chunks_have_required_fields(self):
        content = (
            "SET ANSI_NULLS ON\nGO\n"
            "CREATE PROCEDURE dbo.P(@x INT)\nAS\nBEGIN\n"
            "  DECLARE @v INT\n  SET @v = @x\n"
            "  SELECT @v AS Result, @x AS Input, GETDATE() AS RunTime\n"
            "  FROM dbo.SomeTable WHERE ID = @v AND Status = 1 AND Deleted = 0\n"
            "END\nGO"
        )
        for c in chunk_tsql(content):
            assert isinstance(c.text, str)
            assert len(c.text.strip()) >= MIN_CHUNK_CHARS
            assert isinstance(c.node_type, str) and c.node_type
            assert c.start_line >= 1
            assert c.end_line >= c.start_line


class TestIntegrationRealFiles:
    """Integration tests using real SQL files from test_sources/."""

    @pytest.fixture
    def company_branches_content(self):
        path = _TEST_SOURCES / "dbo.ADMIN_CompanyAllBranches.sql"
        if not path.exists():
            pytest.skip(f"Not found: {path}")
        return path.read_text(encoding="utf-8-sig")

    @pytest.fixture
    def sls_ticket_content(self):
        path = _TEST_SOURCES / "dbo.SLS_Ticket.sql"
        if not path.exists():
            pytest.skip(f"Not found: {path}")
        return path.read_text(encoding="utf-8-sig")

    @pytest.fixture
    def analysis_route_content(self):
        path = _TEST_SOURCES / "ADMIN_ReportDef_AnalysisRoute.sql"
        if not path.exists():
            pytest.skip(f"Not found: {path}")
        return path.read_text(encoding="utf-8-sig")

    @pytest.fixture
    def fare_price_content(self):
        path = _TEST_SOURCES / "dbo.TCK_FarePrice_GetPriceForXDesignation.sql"
        if not path.exists():
            pytest.skip(f"Not found: {path}")
        return path.read_text(encoding="utf-8-sig")

    @pytest.fixture
    def bilety_content(self):
        path = _TEST_SOURCES / "dbo.SLS_ReliefExport_Bilety_Get.sql"
        if not path.exists():
            pytest.skip(f"Not found: {path}")
        return path.read_text(encoding="utf-8-sig")

    @pytest.fixture
    def relief_payments_content(self):
        path = _TEST_SOURCES / "dbo.ADMIN_ReportDef_ReliefTicketPayments.sql"
        if not path.exists():
            pytest.skip(f"Not found: {path}")
        return path.read_text(encoding="utf-8-sig")

    # --- dbo.ADMIN_CompanyAllBranches.sql ---
    def test_company_branches_chunk_count(self, company_branches_content):
        chunks = chunk_tsql(company_branches_content)
        assert len(chunks) == 3

    def test_company_branches_object_name(self, company_branches_content):
        chunks = chunk_tsql(company_branches_content)
        names = {c.object_name for c in chunks if c.object_name}
        assert any("ADMIN_CompanyAllBranches" in n for n in names)

    def test_company_branches_object_type(self, company_branches_content):
        assert "PROCEDURE" in {
            c.object_type for c in chunk_tsql(company_branches_content) if c.object_type
        }

    def test_company_branches_has_header(self, company_branches_content):
        assert "procedure_header" in _chunk_node_types(
            chunk_tsql(company_branches_content)
        )

    def test_company_branches_has_parameter(self, company_branches_content):
        params = [
            c.parameters for c in chunk_tsql(company_branches_content) if c.parameters
        ]
        assert any("@company_id" in p for p in params)

    # --- dbo.SLS_Ticket.sql ---
    def test_sls_ticket_chunk_count(self, sls_ticket_content):
        assert len(chunk_tsql(sls_ticket_content)) == 2

    def test_sls_ticket_has_create_table(self, sls_ticket_content):
        assert "create_table" in _chunk_node_types(chunk_tsql(sls_ticket_content))

    def test_sls_ticket_ddl_grouped(self, sls_ticket_content):
        alter_chunks = [
            c for c in chunk_tsql(sls_ticket_content) if c.node_type == "alter_table"
        ]
        assert len(alter_chunks) == 0  # should be grouped

    def test_sls_ticket_table_name(self, sls_ticket_content):
        names = {c.object_name for c in chunk_tsql(sls_ticket_content) if c.object_name}
        assert any("SLS_Ticket" in (n or "") for n in names)

    # --- ADMIN_ReportDef_AnalysisRoute.sql ---
    def test_analysis_route_chunk_count(self, analysis_route_content):
        assert len(chunk_tsql(analysis_route_content)) == 12

    def test_analysis_route_has_body_sections(self, analysis_route_content):
        body = [c for c in chunk_tsql(analysis_route_content) if "body" in c.node_type]
        assert len(body) >= 2

    def test_analysis_route_context_prefix(self, analysis_route_content):
        body = [c for c in chunk_tsql(analysis_route_content) if "body" in c.node_type]
        for c in body:
            assert "ADMIN_ReportDef_AnalysisRoute" in c.text

    def test_analysis_route_params(self, analysis_route_content):
        params = [
            c.parameters for c in chunk_tsql(analysis_route_content) if c.parameters
        ]
        assert len(params) > 0
        assert "@DateFrom" in params[0]

    # --- dbo.TCK_FarePrice_GetPriceForXDesignation.sql ---
    def test_fare_price_chunk_count(self, fare_price_content):
        assert len(chunk_tsql(fare_price_content)) == 4

    def test_fare_price_is_function(self, fare_price_content):
        assert "FUNCTION" in {
            c.object_type for c in chunk_tsql(fare_price_content) if c.object_type
        }

    def test_fare_price_name(self, fare_price_content):
        names = {c.object_name for c in chunk_tsql(fare_price_content) if c.object_name}
        assert any("TCK_FarePrice" in (n or "") for n in names)

    def test_fare_price_has_header(self, fare_price_content):
        assert "function_header" in _chunk_node_types(chunk_tsql(fare_price_content))

    # --- dbo.SLS_ReliefExport_Bilety_Get.sql ---
    def test_bilety_chunk_count(self, bilety_content):
        chunks = chunk_tsql(bilety_content)
        assert 15 <= len(chunks) <= 30

    def test_bilety_max_chunk_size(self, bilety_content):
        for c in chunk_tsql(bilety_content):
            assert len(c.text) <= FORCE_SPLIT_CHARS + 1000

    def test_bilety_min_chunk_size(self, bilety_content):
        for c in chunk_tsql(bilety_content):
            assert len(c.text.strip()) >= MIN_CHUNK_CHARS

    def test_bilety_object_name(self, bilety_content):
        names = {c.object_name for c in chunk_tsql(bilety_content) if c.object_name}
        assert any("SLS_ReliefExport_Bilety_Get" in (n or "") for n in names)

    def test_bilety_has_header_and_body(self, bilety_content):
        node_types = set(_chunk_node_types(chunk_tsql(bilety_content)))
        assert "procedure_header" in node_types
        assert "procedure_body" in node_types

    # --- dbo.ADMIN_ReportDef_ReliefTicketPayments.sql ---
    def test_relief_payments_chunk_count(self, relief_payments_content):
        chunks = chunk_tsql(relief_payments_content)
        assert 30 <= len(chunks) <= 60

    def test_relief_payments_max_chunk_size(self, relief_payments_content):
        for c in chunk_tsql(relief_payments_content):
            assert len(c.text) <= FORCE_SPLIT_CHARS + 1000

    def test_relief_payments_context_prefix(self, relief_payments_content):
        body = [c for c in chunk_tsql(relief_payments_content) if "body" in c.node_type]
        for c in body:
            assert "ADMIN_ReportDef_ReliefTicketPayments" in c.text

    def test_relief_payments_object_type(self, relief_payments_content):
        assert "PROCEDURE" in {
            c.object_type for c in chunk_tsql(relief_payments_content) if c.object_type
        }

    # --- Cross-file tests ---
    def test_all_real_files_produce_chunks(self):
        sql_files = list(_TEST_SOURCES.glob("*.sql"))
        if not sql_files:
            pytest.skip("No SQL test source files found")
        for sql_file in sql_files:
            content = sql_file.read_text(encoding="utf-8-sig")
            chunks = chunk_tsql(content)
            assert len(chunks) >= 1, f"{sql_file.name} produced no chunks"

    def test_all_real_files_meet_min_size(self):
        sql_files = list(_TEST_SOURCES.glob("*.sql"))
        if not sql_files:
            pytest.skip("No SQL test source files found")
        for sql_file in sql_files:
            content = sql_file.read_text(encoding="utf-8-sig")
            for c in chunk_tsql(content):
                assert len(c.text.strip()) >= MIN_CHUNK_CHARS, (
                    f"{sql_file.name}: chunk too small ({len(c.text.strip())} chars)"
                )

    def test_no_chunk_is_empty(self):
        sql_files = list(_TEST_SOURCES.glob("*.sql"))
        if not sql_files:
            pytest.skip("No SQL test source files found")
        for sql_file in sql_files:
            content = sql_file.read_text(encoding="utf-8-sig")
            for c in chunk_tsql(content):
                assert c.text.strip(), (
                    f"{sql_file.name}: empty chunk at lines {c.start_line}-{c.end_line}"
                )


# ────────────────────────────────────────────────
# TestMakeContextPrefixDescription
# ────────────────────────────────────────────────


class TestMakeContextPrefixDescription:
    """Tests for _make_context_prefix() -- Description line with decomposed identifiers."""

    def test_procedure_includes_description_line(self):
        """Procedure with an object name should include -- Description: line."""
        result = _make_context_prefix(
            "PROCEDURE", "dbo.TCK_FarePrice_GetPriceForXDesignation", "@p1 int"
        )
        assert "-- Description:" in result

    def test_procedure_description_has_decomposed_words(self):
        """Description should contain decomposed words from the identifier."""
        result = _make_context_prefix(
            "PROCEDURE", "dbo.TCK_FarePrice_GetPriceForXDesignation", "@p1 int"
        )
        desc = [l for l in result.split("\n") if "-- Description:" in l][0]
        desc_text = desc.split("-- Description:")[1].strip()
        # TCK -> "Ticket", FarePrice -> "Fare Price", etc.
        assert "ticket" in desc_text, (
            f"Expected 'ticket' in description, got: {desc_text}"
        )
        assert "fare" in desc_text, f"Expected 'fare' in description, got: {desc_text}"
        assert "price" in desc_text, (
            f"Expected 'price' in description, got: {desc_text}"
        )

    def test_function_description_for_bilety(self):
        """SLS_ReliefExport_Bilety_Get -> description with 'sales relief export tickets get'."""
        result = _make_context_prefix("FUNCTION", "SLS_ReliefExport_Bilety_Get", None)
        desc = [l for l in result.split("\n") if "-- Description:" in l][0]
        desc_text = desc.split("-- Description:")[1].strip()
        # SLS -> "Sales", Bilety -> "Tickets"
        assert "sales" in desc_text, f"Expected 'sales' in: {desc_text}"
        assert "relief" in desc_text, f"Expected 'relief' in: {desc_text}"
        assert "export" in desc_text, f"Expected 'export' in: {desc_text}"
        assert "tickets" in desc_text, f"Expected 'tickets' in: {desc_text}"
        assert "get" in desc_text, f"Expected 'get' in: {desc_text}"

    def test_none_name_returns_empty_no_description(self):
        """_make_context_prefix(None, None, None) should return empty string."""
        result = _make_context_prefix(None, None, None)
        assert result == ""
        assert "Description" not in result

    def test_description_is_lowercased(self):
        """Description text should be lowercased."""
        result = _make_context_prefix(
            "PROCEDURE", "dbo.TCK_FarePrice_GetPriceForXDesignation", None
        )
        desc = [l for l in result.split("\n") if "-- Description:" in l][0]
        desc_text = desc.split("-- Description:")[1].strip()
        assert desc_text == desc_text.lower(), (
            f"Description should be lowercased, got: {desc_text}"
        )

    def test_description_is_last_line_before_trailing_newline(self):
        """Description should be the last content line (prefix ends with newline)."""
        result = _make_context_prefix("PROCEDURE", "dbo.MyProc", "@x INT")
        # Strip trailing newline, then check last line
        content_lines = result.rstrip("\n").split("\n")
        assert content_lines[-1].startswith("-- Description:")

    def test_description_without_params(self):
        """Description should appear even when params is None."""
        result = _make_context_prefix("FUNCTION", "dbo.MyFunc", None)
        assert "-- Description:" in result
        # Should NOT have Parameters line
        assert "Parameters" not in result

    def test_type_and_name_lines_still_present(self):
        """The original type and name lines should still be present."""
        result = _make_context_prefix(
            "PROCEDURE", "dbo.TCK_FarePrice_GetPriceForXDesignation", "@p1 int"
        )
        assert "-- Procedure: dbo.TCK_FarePrice_GetPriceForXDesignation" in result
        assert "-- Parameters: @p1 int" in result
        assert "-- Description:" in result

    def test_simple_name_still_gets_description(self):
        """Even a simple name like 'dbo.MyProc' should get a description line."""
        result = _make_context_prefix("PROCEDURE", "dbo.MyProc", None)
        assert "-- Description:" in result
        desc = [l for l in result.split("\n") if "-- Description:" in l][0]
        desc_text = desc.split("-- Description:")[1].strip()
        # "MyProc" -> CamelCase split -> "My Proc" lowered -> "my proc"
        assert "my" in desc_text
        assert "proc" in desc_text
