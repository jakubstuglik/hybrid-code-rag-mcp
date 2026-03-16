"""
Tests for shared/readers/_base.py — base classes and shared utilities for file readers.

Tests cover:
    - get_file_datetime(): file stat timestamps, ISO format, errors
    - read_file_with_encoding(): UTF-8, Windows-1250, Latin-1, fallback
    - read_file_with_encoding_and_bytes(): same encodings, tuple return, UTF-8 bytes
    - node_from_doc(): Document-to-TextNode conversion, metadata preservation
    - BaseFileReader: abstract enforcement, default load_nodes() behavior
    - Integration: concrete reader round-trip through real files
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
from unittest.mock import patch, MagicMock

import pytest

from shared.readers._base import (
    get_file_datetime,
    read_file_with_encoding,
    read_file_with_encoding_and_bytes,
    node_from_doc,
    BaseFileReader,
)
from llama_index.core import Document
from llama_index.core.schema import TextNode


# ────────────────────────────────────────────────
# get_file_datetime()
# ────────────────────────────────────────────────


class TestGetFileDatetime:
    """Tests for get_file_datetime() — file stat timestamp extraction."""

    def test_returns_dict_with_expected_keys(self, tmp_path):
        """Result dict should contain creation_datetime and modification_datetime."""
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = get_file_datetime(f)
        assert "creation_datetime" in result
        assert "modification_datetime" in result
        assert len(result) == 2

    def test_values_are_iso_format_strings(self, tmp_path):
        """Both datetime values should be valid ISO-format strings."""
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = get_file_datetime(f)
        # datetime.fromisoformat should not raise
        creation = datetime.fromisoformat(result["creation_datetime"])
        modification = datetime.fromisoformat(result["modification_datetime"])
        assert isinstance(creation, datetime)
        assert isinstance(modification, datetime)

    def test_recently_created_file(self, tmp_path):
        """A freshly-created file should have timestamps close to now."""
        f = tmp_path / "recent.txt"
        before = datetime.now()
        f.write_text("content")
        after = datetime.now()
        result = get_file_datetime(f)
        mod_dt = datetime.fromisoformat(result["modification_datetime"])
        # Allow 1 second tolerance to avoid microsecond timing races
        from datetime import timedelta

        tolerance = timedelta(seconds=1)
        assert before - tolerance <= mod_dt <= after + tolerance

    def test_nonexistent_file_raises(self, tmp_path):
        """Calling with a nonexistent path should raise FileNotFoundError or OSError."""
        fake = tmp_path / "nonexistent.txt"
        with pytest.raises((FileNotFoundError, OSError)):
            get_file_datetime(fake)


# ────────────────────────────────────────────────
# read_file_with_encoding()
# ────────────────────────────────────────────────


class TestReadFileWithEncoding:
    """Tests for read_file_with_encoding() — multi-encoding fallback reader."""

    def test_utf8_file(self, tmp_path):
        """A UTF-8 file with standard ASCII content is read correctly."""
        f = tmp_path / "utf8.txt"
        f.write_text("Hello, world!", encoding="utf-8")
        assert read_file_with_encoding(f) == "Hello, world!"

    def test_utf8_file_with_unicode(self, tmp_path):
        """A UTF-8 file with multi-byte Unicode is read correctly."""
        text = "Delphi \u2014 \u0414\u0435\u043b\u044c\u0444\u0438"
        f = tmp_path / "utf8_unicode.txt"
        f.write_text(text, encoding="utf-8")
        assert read_file_with_encoding(f) == text

    def test_windows_1250_file(self, tmp_path):
        """A Windows-1250 file with Czech characters falls back correctly."""
        # Windows-1250: \xe8=\u010d, \xf8=\u0159, \x9e=\u017e
        f = tmp_path / "win1250.txt"
        f.write_bytes(b"P\xf8\xedli\x9a \x9elu\x9dou\xe8k\xfd")
        result = read_file_with_encoding(f)
        # UTF-8 decode should fail, windows-1250 should succeed
        assert isinstance(result, str)
        assert len(result) > 0

    def test_latin1_file(self, tmp_path):
        """A file with Latin-1 specific bytes (0x80-0x9F range that differs from Win-1250)."""
        # \xe9 = e-acute in both Latin-1 and Win-1250, but the text should read fine
        f = tmp_path / "latin1.txt"
        f.write_bytes(b"caf\xe9")
        result = read_file_with_encoding(f)
        assert isinstance(result, str)
        assert "caf" in result

    def test_empty_file(self, tmp_path):
        """An empty file should return an empty string."""
        f = tmp_path / "empty.txt"
        f.write_text("")
        assert read_file_with_encoding(f) == ""

    def test_fallback_to_replace(self, tmp_path):
        """When all encodings fail, fallback to UTF-8 with errors='replace'."""
        f = tmp_path / "bad.bin"
        f.write_bytes(b"\xff\xfe")  # content doesn't matter, we mock

        # Mock read_text to fail for all 4 encodings, then succeed on fallback
        call_count = 0
        original_read_text = Path.read_text

        def mock_read_text(self_path, *args, encoding=None, errors=None, **kwargs):
            nonlocal call_count
            if errors == "replace":
                # This is the final fallback call
                return original_read_text(self_path, encoding="utf-8", errors="replace")
            call_count += 1
            raise UnicodeDecodeError("test", b"", 0, 1, "mock failure")

        with patch.object(Path, "read_text", mock_read_text):
            result = read_file_with_encoding(f)

        assert isinstance(result, str)
        # All 4 encodings were tried before fallback
        assert call_count == 4


# ────────────────────────────────────────────────
# read_file_with_encoding_and_bytes()
# ────────────────────────────────────────────────


class TestReadFileWithEncodingAndBytes:
    """Tests for read_file_with_encoding_and_bytes() — returns (str, bytes) tuple."""

    def test_returns_tuple(self, tmp_path):
        """Return value should be a tuple of (str, bytes)."""
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = read_file_with_encoding_and_bytes(f)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], bytes)

    def test_utf8_text_and_bytes_match(self, tmp_path):
        """For a UTF-8 file, text and bytes should match."""
        text = "Hello, UTF-8 world!"
        f = tmp_path / "utf8.txt"
        f.write_text(text, encoding="utf-8")
        result_text, result_bytes = read_file_with_encoding_and_bytes(f)
        assert result_text == text
        assert result_bytes == text.encode("utf-8")

    def test_bytes_are_always_utf8(self, tmp_path):
        """Even for Windows-1250 source files, the bytes should be UTF-8 encoded."""
        # Write Windows-1250 encoded content
        f = tmp_path / "win1250.txt"
        f.write_bytes(b"P\xf8\xedli\x9a \x9elu\x9dou\xe8k\xfd")
        result_text, result_bytes = read_file_with_encoding_and_bytes(f)
        # The bytes should be the UTF-8 encoding of the decoded text
        assert result_bytes == result_text.encode("utf-8")
        # And decoding the bytes back should give the same text
        assert result_bytes.decode("utf-8") == result_text

    def test_utf8_unicode_text_and_bytes(self, tmp_path):
        """Multi-byte unicode content should have matching text and bytes."""
        text = "\u010d\u0159\u017e \u2014 Czech chars"
        f = tmp_path / "unicode.txt"
        f.write_text(text, encoding="utf-8")
        result_text, result_bytes = read_file_with_encoding_and_bytes(f)
        assert result_text == text
        assert result_bytes == text.encode("utf-8")

    def test_empty_file(self, tmp_path):
        """An empty file should return ('', b'')."""
        f = tmp_path / "empty.txt"
        f.write_text("")
        result_text, result_bytes = read_file_with_encoding_and_bytes(f)
        assert result_text == ""
        assert result_bytes == b""

    def test_fallback_to_replace(self, tmp_path):
        """When all encodings fail, fallback with errors='replace'."""
        f = tmp_path / "bad.bin"
        f.write_bytes(b"\xff\xfe")

        call_count = 0
        original_read_text = Path.read_text

        def mock_read_text(self_path, *args, encoding=None, errors=None, **kwargs):
            nonlocal call_count
            if errors == "replace":
                return original_read_text(self_path, encoding="utf-8", errors="replace")
            call_count += 1
            raise UnicodeDecodeError("test", b"", 0, 1, "mock failure")

        with patch.object(Path, "read_text", mock_read_text):
            result_text, result_bytes = read_file_with_encoding_and_bytes(f)

        assert isinstance(result_text, str)
        assert isinstance(result_bytes, bytes)
        assert result_bytes == result_text.encode("utf-8")
        assert call_count == 4


# ────────────────────────────────────────────────
# node_from_doc()
# ────────────────────────────────────────────────


class TestNodeFromDoc:
    """Tests for node_from_doc() — Document to TextNode conversion."""

    def test_converts_document_to_textnode(self):
        """Result should be a TextNode instance."""
        doc = Document(text="some code", metadata={"file": "test.pas"})
        node = node_from_doc(doc)
        assert isinstance(node, TextNode)

    def test_text_is_preserved(self):
        """The node text should match the document text exactly."""
        doc = Document(text="procedure DoStuff;", metadata={})
        node = node_from_doc(doc)
        assert node.text == "procedure DoStuff;"

    def test_metadata_is_preserved(self):
        """All metadata keys and values should be preserved."""
        meta = {
            "file_path": "src/unit1.pas",
            "language": "pascal",
            "line_start": 10,
        }
        doc = Document(text="code", metadata=meta)
        node = node_from_doc(doc)
        assert node.metadata["file_path"] == "src/unit1.pas"
        assert node.metadata["language"] == "pascal"
        assert node.metadata["line_start"] == 10

    def test_empty_metadata(self):
        """A document with empty metadata should produce a node with empty metadata."""
        doc = Document(text="some text", metadata={})
        node = node_from_doc(doc)
        # metadata may include llama-index internal keys, but none of ours
        assert isinstance(node.metadata, dict)

    def test_empty_text(self):
        """A document with empty text should produce a node with empty text."""
        doc = Document(text="", metadata={"key": "val"})
        node = node_from_doc(doc)
        assert node.text == ""
        assert node.metadata["key"] == "val"

    def test_multiline_text(self):
        """Multi-line text content should be preserved exactly."""
        text = "line 1\nline 2\nline 3"
        doc = Document(text=text, metadata={})
        node = node_from_doc(doc)
        assert node.text == text

    def test_unicode_text(self):
        """Unicode characters in text should be preserved."""
        text = "// \u010cesk\u00fd koment\u00e1\u0159"
        doc = Document(text=text, metadata={})
        node = node_from_doc(doc)
        assert node.text == text


# ────────────────────────────────────────────────
# BaseFileReader
# ────────────────────────────────────────────────


class _StubReader(BaseFileReader):
    """Concrete test implementation of BaseFileReader."""

    def __init__(self, docs: Optional[List[Document]] = None):
        self._docs = docs or []
        self._last_file = None
        self._last_extra_info = None

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        """Return pre-configured documents, recording call args."""
        self._last_file = file
        self._last_extra_info = extra_info
        return self._docs


class TestBaseFileReader:
    """Tests for the BaseFileReader abstract base class."""

    def test_cannot_instantiate_directly(self):
        """BaseFileReader is abstract and cannot be instantiated."""
        with pytest.raises(TypeError, match="abstract method"):
            BaseFileReader()

    def test_concrete_subclass_must_implement_load_data(self):
        """A subclass without load_data should raise TypeError."""

        class IncompleteReader(BaseFileReader):
            pass

        with pytest.raises(TypeError, match="abstract method"):
            IncompleteReader()

    def test_concrete_subclass_can_be_instantiated(self):
        """A subclass that implements load_data should work."""
        reader = _StubReader()
        assert isinstance(reader, BaseFileReader)

    def test_load_nodes_calls_load_data(self, tmp_path):
        """Default load_nodes() should delegate to load_data()."""
        doc = Document(text="hello", metadata={"key": "val"})
        reader = _StubReader(docs=[doc])
        f = tmp_path / "test.txt"
        f.write_text("hello")

        nodes = reader.load_nodes(f)
        assert reader._last_file == f
        assert len(nodes) == 1
        assert isinstance(nodes[0], TextNode)
        assert nodes[0].text == "hello"

    def test_load_nodes_with_multiple_documents(self, tmp_path):
        """load_nodes() should convert all documents to TextNodes."""
        docs = [
            Document(text="first", metadata={"idx": 1}),
            Document(text="second", metadata={"idx": 2}),
            Document(text="third", metadata={"idx": 3}),
        ]
        reader = _StubReader(docs=docs)
        f = tmp_path / "test.txt"
        f.write_text("content")

        nodes = reader.load_nodes(f)
        assert len(nodes) == 3
        assert nodes[0].text == "first"
        assert nodes[1].text == "second"
        assert nodes[2].text == "third"

    def test_load_nodes_with_empty_document_list(self, tmp_path):
        """load_nodes() with no documents should return empty list."""
        reader = _StubReader(docs=[])
        f = tmp_path / "test.txt"
        f.write_text("content")

        nodes = reader.load_nodes(f)
        assert nodes == []

    def test_extra_info_is_passed_through(self, tmp_path):
        """extra_info should be forwarded from load_nodes to load_data."""
        reader = _StubReader(docs=[])
        f = tmp_path / "test.txt"
        f.write_text("content")
        extra = {"source": "test", "version": 2}

        reader.load_nodes(f, extra_info=extra)
        assert reader._last_extra_info == extra

    def test_extra_info_default_is_none(self, tmp_path):
        """Without extra_info, load_data should receive None."""
        reader = _StubReader(docs=[])
        f = tmp_path / "test.txt"
        f.write_text("content")

        reader.load_nodes(f)
        assert reader._last_extra_info is None

    def test_load_nodes_preserves_metadata(self, tmp_path):
        """Metadata from documents should be preserved in nodes."""
        meta = {"file_path": "src/test.pas", "language": "pascal"}
        doc = Document(text="code", metadata=meta)
        reader = _StubReader(docs=[doc])
        f = tmp_path / "test.pas"
        f.write_text("code")

        nodes = reader.load_nodes(f)
        assert nodes[0].metadata["file_path"] == "src/test.pas"
        assert nodes[0].metadata["language"] == "pascal"


# ────────────────────────────────────────────────
# Integration tests
# ────────────────────────────────────────────────


class TestIntegration:
    """Integration tests — full round-trip through reader components."""

    def test_concrete_reader_with_real_file(self, tmp_path):
        """Create a concrete reader, load a real file, verify nodes."""
        f = tmp_path / "example.pas"
        f.write_text(
            "unit Example;\n\ninterface\n\nimplementation\n\nend.", encoding="utf-8"
        )

        class SimpleReader(BaseFileReader):
            def load_data(
                self, file: Path, extra_info: Optional[dict] = None
            ) -> List[Document]:
                content = read_file_with_encoding(file)
                meta = get_file_datetime(file)
                meta["file_path"] = str(file.name)
                if extra_info:
                    meta.update(extra_info)
                return [Document(text=content, metadata=meta)]

        reader = SimpleReader()
        nodes = reader.load_nodes(f)

        assert len(nodes) == 1
        assert nodes[0].text.startswith("unit Example;")
        assert "file_path" in nodes[0].metadata
        assert nodes[0].metadata["file_path"] == "example.pas"
        assert "creation_datetime" in nodes[0].metadata
        assert "modification_datetime" in nodes[0].metadata

    def test_round_trip_with_metadata(self, tmp_path):
        """Full round-trip: file -> reader -> nodes -> verify all metadata."""
        f = tmp_path / "data.sql"
        sql_content = "CREATE TABLE users (\n  id INTEGER PRIMARY KEY\n);"
        f.write_text(sql_content, encoding="utf-8")

        class SQLStubReader(BaseFileReader):
            def load_data(
                self, file: Path, extra_info: Optional[dict] = None
            ) -> List[Document]:
                content = read_file_with_encoding(file)
                meta = get_file_datetime(file)
                meta["file_path"] = str(file.name)
                meta["language"] = "sql"
                if extra_info:
                    meta.update(extra_info)
                return [Document(text=content, metadata=meta)]

        reader = SQLStubReader()
        extra = {"project": "test_project"}
        nodes = reader.load_nodes(f, extra_info=extra)

        assert len(nodes) == 1
        node = nodes[0]
        assert node.text == sql_content
        assert node.metadata["file_path"] == "data.sql"
        assert node.metadata["language"] == "sql"
        assert node.metadata["project"] == "test_project"
        # Timestamps should be valid ISO strings
        datetime.fromisoformat(node.metadata["creation_datetime"])
        datetime.fromisoformat(node.metadata["modification_datetime"])

    def test_round_trip_with_windows_1250_file(self, tmp_path):
        """Round-trip with a Windows-1250 encoded file preserves content."""
        f = tmp_path / "czech.pas"
        # Write Windows-1250 bytes: "Příliš" has specific byte representation
        f.write_bytes(b"// P\xf8\xedli\x9a \x9elu\x9dou\xe8k\xfd\n")

        class PasReader(BaseFileReader):
            def load_data(
                self, file: Path, extra_info: Optional[dict] = None
            ) -> List[Document]:
                content = read_file_with_encoding(file)
                return [Document(text=content, metadata={"file_path": file.name})]

        reader = PasReader()
        nodes = reader.load_nodes(f)

        assert len(nodes) == 1
        assert isinstance(nodes[0].text, str)
        assert len(nodes[0].text) > 0
        assert nodes[0].metadata["file_path"] == "czech.pas"

    def test_encoding_and_bytes_round_trip(self, tmp_path):
        """read_file_with_encoding_and_bytes result bytes decode to the same text."""
        f = tmp_path / "roundtrip.txt"
        original = "Hello \u010d\u0159\u017e \u2014 test"
        f.write_text(original, encoding="utf-8")

        text, raw_bytes = read_file_with_encoding_and_bytes(f)
        assert text == original
        assert raw_bytes.decode("utf-8") == original

    def test_node_from_doc_used_in_load_nodes(self, tmp_path):
        """Verify that load_nodes internally uses node_from_doc correctly."""
        docs = [
            Document(text="A", metadata={"idx": 0}),
            Document(text="B", metadata={"idx": 1}),
        ]

        # Manually convert and compare with load_nodes output
        expected_nodes = [node_from_doc(d) for d in docs]

        reader = _StubReader(docs=docs)
        f = tmp_path / "test.txt"
        f.write_text("whatever")

        actual_nodes = reader.load_nodes(f)

        assert len(actual_nodes) == len(expected_nodes)
        for actual, expected in zip(actual_nodes, expected_nodes):
            assert actual.text == expected.text
            assert actual.metadata["idx"] == expected.metadata["idx"]


# ────────────────────────────────────────────────
# decompose_identifier()
# ────────────────────────────────────────────────

from shared.readers._base import decompose_identifier


class TestDecomposeIdentifier:
    """Tests for decompose_identifier() — identifier-to-natural-language decomposition."""

    # --- Basic CamelCase splitting ---

    def test_basic_camelcase_two_words(self):
        """Simple CamelCase identifier splits into two words."""
        assert decompose_identifier("FarePrice") == "Fare Price"

    def test_basic_camelcase_three_words(self):
        """Three-word CamelCase identifier."""
        assert decompose_identifier("GetPriceFor") == "Get Price For"

    def test_camelcase_single_uppercase_letter(self):
        """A single uppercase letter between words is its own word."""
        assert (
            decompose_identifier("GetPriceForXDesignation")
            == "Get Price For X Designation"
        )

    def test_camelcase_all_caps_acronym(self):
        """All-caps acronym followed by a capitalized word splits correctly."""
        assert decompose_identifier("XMLParser") == "XML Parser"

    def test_camelcase_all_caps_acronym_https(self):
        """Multi-char all-caps acronym followed by CamelCase."""
        assert decompose_identifier("HTTPSConnection") == "HTTPS Connection"

    # --- Underscore splitting ---

    def test_underscore_split_simple(self):
        """Underscores separate parts that are then processed individually."""
        assert decompose_identifier("Relief_Export") == "Relief Export"

    def test_underscore_with_abbreviation(self):
        """Underscore-separated part that is a known abbreviation gets expanded."""
        assert decompose_identifier("TCK_FarePrice") == "Ticket Fare Price"

    def test_multiple_underscores(self):
        """Multiple underscore-separated parts."""
        assert decompose_identifier("SLS_Relief_Export") == "Sales Relief Export"

    def test_leading_underscore_ignored(self):
        """Leading underscore produces an empty part that is skipped."""
        assert decompose_identifier("_private") == "private"

    def test_double_underscore(self):
        """Double underscore produces empty parts that are skipped."""
        assert decompose_identifier("__double") == "double"

    def test_underscore_with_camelcase(self):
        """Underscore splitting combined with CamelCase splitting."""
        assert decompose_identifier("T_underscore") == "T underscore"

    # --- Delphi T-prefix stripping ---

    def test_t_prefix_stripped_from_type_name(self):
        """T-prefix is stripped when followed by an uppercase letter (Delphi type)."""
        assert decompose_identifier("TDataModule") == "Data Module"

    def test_t_prefix_stripped_from_tform(self):
        """T-prefix stripped from a simple two-part type name."""
        assert decompose_identifier("TForm") == "Form"

    def test_t_prefix_not_stripped_from_all_caps(self):
        """T-prefix is NOT stripped from all-caps identifiers like TCP."""
        assert decompose_identifier("TCP") == "TCP"

    def test_t_prefix_stripped_from_known_lowercase_abbreviation(self):
        """T-prefix IS stripped when followed by known abbreviation (frm, dm)."""
        # 'Tfrm' — T followed by 'frm' which is in _DELPHI_LOWER_PREFIXES
        # T is stripped, 'frm' is expanded to 'Form' via _ABBREVIATION_MAP
        assert decompose_identifier("TfrmMainTurdus") == "Form Main Turdus"

    def test_t_prefix_stripped_from_tclient(self):
        """T-prefix stripped from TClient (T + uppercase C)."""
        assert decompose_identifier("TClientDataSet") == "Client Data Set"

    # --- Schema prefix stripping ---

    def test_dbo_schema_stripped(self):
        """dbo. schema prefix is stripped."""
        assert decompose_identifier("dbo.SomeProc") == "Some Procedure"

    def test_sys_schema_stripped(self):
        """sys. schema prefix is stripped."""
        assert decompose_identifier("sys.objects") == "objects"

    def test_schema_with_abbreviation(self):
        """Schema prefix stripped then abbreviation expansion on remainder."""
        assert decompose_identifier("dbo.TCK_FarePrice") == "Ticket Fare Price"

    def test_schema_only_dot_no_name(self):
        """Schema prefix with nothing after the dot returns empty string."""
        assert decompose_identifier("dbo.") == ""

    def test_multiple_dots_takes_last(self):
        """Multiple dots — takes the last segment."""
        assert decompose_identifier("schema.dbo.MyProc") == "My Procedure"

    # --- Known abbreviation expansion ---

    def test_abbreviation_tck(self):
        """TCK expands to Ticket."""
        assert decompose_identifier("TCK") == "Ticket"

    def test_abbreviation_sls(self):
        """SLS expands to Sales."""
        assert decompose_identifier("SLS") == "Sales"

    def test_abbreviation_dm(self):
        """DM expands to DataModule."""
        assert decompose_identifier("DM") == "DataModule"

    def test_abbreviation_frm_uppercase(self):
        """FRM expands to Form."""
        assert decompose_identifier("FRM") == "Form"

    def test_abbreviation_frm_lowercase(self):
        """Lowercase 'frm' also expands to Form via upper() lookup."""
        assert decompose_identifier("frm") == "Form"

    def test_abbreviation_bilety_czech(self):
        """Czech word Bilety expands to Tickets (case-sensitive match)."""
        assert decompose_identifier("Bilety") == "Tickets"

    def test_abbreviation_proc(self):
        """PROC expands to Procedure."""
        assert decompose_identifier("PROC") == "Procedure"

    def test_abbreviation_cfg(self):
        """CFG expands to Config."""
        assert decompose_identifier("CFG") == "Config"

    def test_abbreviation_rep(self):
        """REP expands to Report."""
        assert decompose_identifier("REP") == "Report"

    # --- Combined / docstring examples ---

    def test_combined_tck_fare_price_full(self):
        """Full combined example from docstring."""
        result = decompose_identifier("TCK_FarePrice_GetPriceForXDesignation")
        assert result == "Ticket Fare Price Get Price For X Designation"

    def test_combined_sls_relief_export(self):
        """Full combined example from docstring."""
        result = decompose_identifier("SLS_ReliefExport_Bilety_Get")
        assert result == "Sales Relief Export Tickets Get"

    def test_combined_dbo_tck(self):
        """Schema + abbreviation combined example from docstring."""
        assert decompose_identifier("dbo.TCK_FarePrice") == "Ticket Fare Price"

    def test_combined_tdatamodule(self):
        """T-prefix + CamelCase from docstring."""
        assert decompose_identifier("TDataModule") == "Data Module"

    def test_combined_rep_type_punctuality(self):
        """Underscore abbreviation + CamelCase."""
        result = decompose_identifier("REP_TypePunctuality")
        assert result == "Report Type Punctuality"

    # --- Nested abbreviation in CamelCase ---

    def test_abbreviation_after_camelcase_split(self):
        """An abbreviation that appears as a CamelCase segment gets expanded."""
        # CFG is a known abbreviation; after camel split "CFG" + "Manager"
        assert decompose_identifier("CFGManager") == "Config Manager"

    def test_some_proc_expands_proc(self):
        """'Proc' camel-part with upper 'PROC' in map expands to Procedure."""
        # "SomeProc" -> camel split -> "Some", "Proc" -> "Proc".upper()="PROC" -> "Procedure"
        assert decompose_identifier("SomeProc") == "Some Procedure"

    # --- Edge cases ---

    def test_empty_string(self):
        """Empty string returns empty string."""
        assert decompose_identifier("") == ""

    def test_single_lowercase_word(self):
        """A single lowercase word returns as-is."""
        assert decompose_identifier("hello") == "hello"

    def test_single_uppercase_letter(self):
        """A single uppercase letter returns as-is."""
        assert decompose_identifier("A") == "A"

    def test_single_char_t(self):
        """Single 'T' is too short for T-prefix logic (len < 2)."""
        assert decompose_identifier("T") == "T"

    def test_all_lowercase_with_underscores(self):
        """All lowercase with underscores just splits on underscores."""
        assert decompose_identifier("get_something") == "get something"

    def test_lowercase_start_camelcase(self):
        """Lowercase-start CamelCase (like Java methods) splits correctly."""
        assert decompose_identifier("getSomething") == "get Something"

    def test_tfrm_main_turdus_actual_behavior(self):
        """TfrmMainTurdus: T stripped (frm is known Delphi abbreviation).
        frm expands to Form, Camel split produces 'Form', 'Main', 'Turdus'."""
        assert decompose_identifier("TfrmMainTurdus") == "Form Main Turdus"

    def test_tdm_main_actual_behavior(self):
        """TdmMain: T stripped (dm is known Delphi abbreviation).
        dm expands to DataModule, then 'Main' from CamelCase split."""
        assert decompose_identifier("TdmMain") == "DataModule Main"
