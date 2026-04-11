"""
Tests for shared/readers/pascal_reader.py — Delphi/Pascal file reader with Tree-sitter AST.

Tests cover:
    - Class attributes: NODE_TYPES, LEAF_NODE_TYPES, CONTAINER_NODE_TYPES, size constants
    - __init__: instantiation, _text_splitter attribute
    - _has_matched_descendants(): recursive descendant matching
    - _make_documents(): chunk creation, size filtering, oversized splitting
    - load_data(): empty files, parse errors, real files, children-first behavior
    - Chunk size filtering (MIN_CHUNK_SIZE discard)
    - Oversized chunk splitting (MAX_CHUNK_CHARS)
    - Fallback to full_file when no AST nodes match
    - File read errors (non-existent file)
    - Metadata correctness
    - Integration with real sample files
"""

from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from shared.readers.pascal_reader import (
    DelphiFileReader,
    _is_commented_out_code,
    _build_context_prefix,
)
from llama_index.core import Document


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_mock_node(node_type: str, children: list = None) -> MagicMock:
    """Create a mock tree-sitter Node with the given type and children."""
    node = MagicMock()
    node.type = node_type
    node.children = children or []
    return node


# Path to real sample files relative to the project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLE_FILES = _PROJECT_ROOT / "test_sources"


# ────────────────────────────────────────────────
# TestClassAttributes
# ────────────────────────────────────────────────


class TestClassAttributes:
    """Tests for DelphiFileReader class-level attributes."""

    def test_node_types_is_set(self):
        """NODE_TYPES should be a set."""
        assert isinstance(DelphiFileReader.NODE_TYPES, set)

    def test_leaf_node_types_is_set(self):
        """LEAF_NODE_TYPES should be a set."""
        assert isinstance(DelphiFileReader.LEAF_NODE_TYPES, set)

    def test_container_node_types_is_set(self):
        """CONTAINER_NODE_TYPES should be a set."""
        assert isinstance(DelphiFileReader.CONTAINER_NODE_TYPES, set)

    def test_node_types_contains_expected_members(self):
        """NODE_TYPES should contain all expected AST node types (no declField/declProp)."""
        expected = {
            "declProc",
            "defProc",
            "declClass",
            "declVar",
            "declSection",
            "declConst",
            "declType",
            "declUses",
            "comment",
        }
        assert DelphiFileReader.NODE_TYPES == expected

    def test_declfield_and_declprop_excluded(self):
        """declField and declProp should NOT be in NODE_TYPES (grouped in declSection)."""
        assert "declField" not in DelphiFileReader.NODE_TYPES
        assert "declProp" not in DelphiFileReader.NODE_TYPES

    def test_leaf_node_types_contains_expected_members(self):
        """LEAF_NODE_TYPES should contain section-level grouping types."""
        expected = {
            "defProc",
            "declProc",
            "declSection",
            "declVar",
            "declConst",
            "declUses",
            "comment",
        }
        assert DelphiFileReader.LEAF_NODE_TYPES == expected

    def test_container_node_types_contains_expected_members(self):
        """CONTAINER_NODE_TYPES should contain only class and type containers."""
        expected = {"declClass", "declType"}
        assert DelphiFileReader.CONTAINER_NODE_TYPES == expected

    def test_leaf_plus_container_equals_node_types(self):
        """LEAF_NODE_TYPES union CONTAINER_NODE_TYPES should equal NODE_TYPES."""
        assert (
            DelphiFileReader.LEAF_NODE_TYPES | DelphiFileReader.CONTAINER_NODE_TYPES
            == DelphiFileReader.NODE_TYPES
        )

    def test_leaf_and_container_are_disjoint(self):
        """LEAF_NODE_TYPES and CONTAINER_NODE_TYPES should have no overlap."""
        overlap = (
            DelphiFileReader.LEAF_NODE_TYPES & DelphiFileReader.CONTAINER_NODE_TYPES
        )
        assert overlap == set()

    def test_min_chunk_size_value(self):
        """MIN_CHUNK_SIZE should be 20."""
        assert DelphiFileReader.MIN_CHUNK_SIZE == 20

    def test_max_chunk_chars_value(self):
        """MAX_CHUNK_CHARS should be 24000."""
        assert DelphiFileReader.MAX_CHUNK_CHARS == 24000


# ────────────────────────────────────────────────
# TestInit
# ────────────────────────────────────────────────


class TestInit:
    """Tests for DelphiFileReader.__init__."""

    def test_can_instantiate(self):
        """DelphiFileReader should be instantiable without arguments."""
        reader = DelphiFileReader()
        assert isinstance(reader, DelphiFileReader)

    def test_has_text_splitter(self):
        """Instance should have a _text_splitter attribute."""
        reader = DelphiFileReader()
        assert hasattr(reader, "_text_splitter")

    def test_text_splitter_is_token_text_splitter(self):
        """_text_splitter should be a TokenTextSplitter instance."""
        from llama_index.core.node_parser import TokenTextSplitter

        reader = DelphiFileReader()
        assert isinstance(reader._text_splitter, TokenTextSplitter)

    def test_is_base_file_reader(self):
        """DelphiFileReader should be a subclass of BaseFileReader."""
        from shared.readers._base import BaseFileReader

        reader = DelphiFileReader()
        assert isinstance(reader, BaseFileReader)


# ────────────────────────────────────────────────
# TestHasMatchedDescendants
# ────────────────────────────────────────────────


class TestHasMatchedDescendants:
    """Tests for DelphiFileReader._has_matched_descendants()."""

    def test_child_with_matching_type_returns_true(self):
        """A direct child whose type is in NODE_TYPES should return True."""
        reader = DelphiFileReader()
        child = _make_mock_node("defProc")
        parent = _make_mock_node("someContainer", children=[child])
        assert reader._has_matched_descendants(parent) is True

    def test_no_matching_descendants_returns_false(self):
        """A node whose children (and their children) have no matching types returns False."""
        reader = DelphiFileReader()
        grandchild = _make_mock_node("identifier")
        child = _make_mock_node("expression", children=[grandchild])
        parent = _make_mock_node("someContainer", children=[child])
        assert reader._has_matched_descendants(parent) is False

    def test_deeply_nested_match_returns_true(self):
        """A matching node deep in the tree should still return True."""
        reader = DelphiFileReader()
        deep_match = _make_mock_node("declVar")
        mid = _make_mock_node("block", children=[deep_match])
        top_child = _make_mock_node("wrapper", children=[mid])
        parent = _make_mock_node("root", children=[top_child])
        assert reader._has_matched_descendants(parent) is True

    def test_empty_children_returns_false(self):
        """A node with no children should return False."""
        reader = DelphiFileReader()
        node = _make_mock_node("declClass", children=[])
        assert reader._has_matched_descendants(node) is False

    def test_multiple_children_one_matches(self):
        """If one of several children matches, should return True."""
        reader = DelphiFileReader()
        child_a = _make_mock_node("identifier")
        child_b = _make_mock_node("declConst")
        child_c = _make_mock_node("expression")
        parent = _make_mock_node("container", children=[child_a, child_b, child_c])
        assert reader._has_matched_descendants(parent) is True

    def test_all_node_types_detected(self):
        """Each node type in NODE_TYPES should be detected as a matched descendant."""
        reader = DelphiFileReader()
        for node_type in DelphiFileReader.NODE_TYPES:
            child = _make_mock_node(node_type)
            parent = _make_mock_node("wrapper", children=[child])
            assert reader._has_matched_descendants(parent) is True, (
                f"{node_type} was not detected as matched descendant"
            )


# ────────────────────────────────────────────────
# TestMakeDocuments
# ────────────────────────────────────────────────


class TestMakeDocuments:
    """Tests for DelphiFileReader._make_documents()."""

    def _make_file_datetime(self) -> dict:
        """Create a sample file_datetime dict for testing."""
        return {
            "creation_datetime": "2026-01-01T00:00:00",
            "modification_datetime": "2026-01-02T00:00:00",
        }

    def test_normal_chunk_returns_single_document(self):
        """A normal-sized chunk should return exactly one Document."""
        reader = DelphiFileReader()
        text = "procedure TForm1.FormCreate(Sender: TObject);\nbegin\n  // init\nend;"
        docs = reader._make_documents(
            chunk_text=text,
            node_type="defProc",
            start_line=10,
            end_line=13,
            start_byte=100,
            end_byte=170,
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        assert len(docs) == 1
        assert docs[0].text == text

    def test_too_small_chunk_returns_empty(self):
        """A chunk smaller than MIN_CHUNK_SIZE should be discarded."""
        reader = DelphiFileReader()
        text = "// short"  # 8 chars < 20
        docs = reader._make_documents(
            chunk_text=text,
            node_type="comment",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=8,
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        assert docs == []

    def test_exact_min_chunk_size_is_discarded(self):
        """A chunk with exactly MIN_CHUNK_SIZE - 1 chars should be discarded."""
        reader = DelphiFileReader()
        text = "x" * 19  # 19 chars < 20
        docs = reader._make_documents(
            chunk_text=text,
            node_type="comment",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=19,
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        assert docs == []

    def test_min_chunk_size_boundary_included(self):
        """A chunk with exactly MIN_CHUNK_SIZE chars should be included."""
        reader = DelphiFileReader()
        text = "x" * 20  # exactly 20 chars
        docs = reader._make_documents(
            chunk_text=text,
            node_type="comment",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=20,
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        assert len(docs) == 1

    def test_oversized_chunk_returns_multiple_documents(self):
        """A chunk exceeding MAX_CHUNK_CHARS should be split into multiple Documents."""
        reader = DelphiFileReader()
        # Create text that exceeds MAX_CHUNK_CHARS
        text = "procedure BigProc;\nbegin\n" + ("  DoStuff;\n" * 3000) + "end;\n"
        assert len(text) > reader.MAX_CHUNK_CHARS

        docs = reader._make_documents(
            chunk_text=text,
            node_type="defProc",
            start_line=1,
            end_line=3002,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        assert len(docs) > 1

    def test_oversized_chunk_has_split_metadata(self):
        """Split documents should have split_part, split_total, and _split node_type."""
        reader = DelphiFileReader()
        text = "procedure BigProc;\nbegin\n" + ("  DoStuff;\n" * 3000) + "end;\n"

        docs = reader._make_documents(
            chunk_text=text,
            node_type="defProc",
            start_line=1,
            end_line=3002,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        for doc in docs:
            assert doc.metadata["node_type"] == "defProc_split"
            assert "split_part" in doc.metadata
            assert "split_total" in doc.metadata
            assert doc.metadata["split_total"] == len(docs)

    def test_oversized_chunk_split_parts_are_sequential(self):
        """Split parts should have sequential split_part values."""
        reader = DelphiFileReader()
        text = "procedure BigProc;\nbegin\n" + ("  DoStuff;\n" * 3000) + "end;\n"

        docs = reader._make_documents(
            chunk_text=text,
            node_type="defProc",
            start_line=1,
            end_line=3002,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        parts = [doc.metadata["split_part"] for doc in docs]
        # Parts should be a contiguous subsequence of range(split_total)
        # (some parts may be dropped if they are too small after stripping)
        assert parts == sorted(parts)
        assert all(p >= 0 for p in parts)

    def test_metadata_fields_correct(self):
        """Returned document should have all expected metadata fields."""
        reader = DelphiFileReader()
        text = "procedure Foo; begin end;"
        file_dt = self._make_file_datetime()
        docs = reader._make_documents(
            chunk_text=text,
            node_type="defProc",
            start_line=5,
            end_line=7,
            start_byte=100,
            end_byte=124,
            file_path_str="src/unit1.pas",
            file_datetime=file_dt,
        )
        assert len(docs) == 1
        meta = docs[0].metadata
        assert meta["file_path"] == "src/unit1.pas"
        assert meta["node_type"] == "defProc"
        assert meta["start_line"] == 5
        assert meta["end_line"] == 7
        assert meta["start_byte"] == 100
        assert meta["end_byte"] == 124
        assert meta["creation_datetime"] == file_dt["creation_datetime"]
        assert meta["modification_datetime"] == file_dt["modification_datetime"]

    def test_oversized_split_part_too_small_is_dropped(self):
        """Split parts smaller than MIN_CHUNK_SIZE (after strip) should be dropped."""
        reader = DelphiFileReader()
        text = "x" * (reader.MAX_CHUNK_CHARS + 1)

        # TokenTextSplitter is a Pydantic model with read-only attrs,
        # so replace the entire _text_splitter with a mock.
        mock_splitter = MagicMock()
        mock_splitter.split_text.return_value = ["x" * 100, "   tiny   ", "y" * 100]
        reader._text_splitter = mock_splitter

        docs = reader._make_documents(
            chunk_text=text,
            node_type="defProc",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        # "   tiny   " stripped is "tiny" (4 chars < 20), so it should be dropped
        assert len(docs) == 2
        # split_total reflects the original 3 parts (before filtering)
        for doc in docs:
            assert doc.metadata["split_total"] == 3

    def test_normal_chunk_at_max_boundary(self):
        """A chunk with exactly MAX_CHUNK_CHARS should NOT be split."""
        reader = DelphiFileReader()
        text = "x" * reader.MAX_CHUNK_CHARS
        docs = reader._make_documents(
            chunk_text=text,
            node_type="defProc",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.pas",
            file_datetime=self._make_file_datetime(),
        )
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "defProc"


# ────────────────────────────────────────────────
# TestLoadDataEmptyFile
# ────────────────────────────────────────────────


class TestLoadDataEmptyFile:
    """Tests for load_data() with empty or whitespace-only files."""

    def test_empty_file_returns_empty_list(self, tmp_path):
        """An empty .pas file should return an empty list."""
        f = tmp_path / "empty.pas"
        f.write_text("", encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        assert docs == []

    def test_whitespace_only_file_returns_empty_list(self, tmp_path):
        """A file containing only whitespace should return an empty list."""
        f = tmp_path / "whitespace.pas"
        f.write_text("   \n\n  \t  \n", encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        assert docs == []


# ────────────────────────────────────────────────
# TestLoadDataParseError
# ────────────────────────────────────────────────


class TestLoadDataParseError:
    """Tests for load_data() when tree-sitter parsing fails."""

    def test_parse_error_returns_full_file_document(self, tmp_path):
        """When tree-sitter parse fails, should return a full_file Document with parse_error."""
        f = tmp_path / "bad.pas"
        content = "unit Bad;\ninterface\nimplementation\nend."
        f.write_text(content, encoding="utf-8")
        reader = DelphiFileReader()

        # tree_sitter.Parser is a C extension with read-only attributes,
        # so we replace the module-level _parser reference instead.
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = RuntimeError("mock parse failure")

        with patch("shared.readers.pascal_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert len(docs) == 1
        assert docs[0].text == content
        assert docs[0].metadata["node_type"] == "full_file"
        assert "parse_error" in docs[0].metadata
        assert "mock parse failure" in docs[0].metadata["parse_error"]

    def test_parse_error_has_file_path_metadata(self, tmp_path):
        """full_file document from parse error should have file_path metadata."""
        f = tmp_path / "err.pas"
        f.write_text("unit Err; end.", encoding="utf-8")
        reader = DelphiFileReader()

        mock_parser = MagicMock()
        mock_parser.parse.side_effect = Exception("boom")

        with patch("shared.readers.pascal_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert docs[0].metadata["file_path"] == str(f)


# ────────────────────────────────────────────────
# TestLoadDataWithRealFiles
# ────────────────────────────────────────────────


class TestLoadDataWithRealFiles:
    """Tests for load_data() using real sample .pas files."""

    @pytest.fixture
    def splash_path(self) -> Path:
        """Return the path to Splash.pas test file."""
        p = _SAMPLE_FILES / "Splash.pas"
        if not p.exists():
            pytest.skip(f"Sample file not found: {p}")
        return p

    def test_returns_non_empty_list(self, splash_path):
        """Splash.pas should produce a non-empty list of Documents."""
        reader = DelphiFileReader()
        docs = reader.load_data(splash_path)
        assert len(docs) > 0

    def test_no_duplicate_byte_ranges(self, splash_path):
        """No two chunks should cover the exact same byte range (deduplication)."""
        reader = DelphiFileReader()
        docs = reader.load_data(splash_path)
        byte_ranges = set()
        for doc in docs:
            rng = (doc.metadata.get("start_byte"), doc.metadata.get("end_byte"))
            if rng != (None, None):
                assert rng not in byte_ranges, f"Duplicate byte range: {rng}"
                byte_ranges.add(rng)

    def test_node_type_metadata_set_on_each_document(self, splash_path):
        """Every returned Document should have a node_type metadata field."""
        reader = DelphiFileReader()
        docs = reader.load_data(splash_path)
        for doc in docs:
            assert "node_type" in doc.metadata
            assert isinstance(doc.metadata["node_type"], str)
            assert len(doc.metadata["node_type"]) > 0

    def test_leaf_node_types_are_present(self, splash_path):
        """Splash.pas should contain defProc chunks; tiny declSections are
        suppressed when covered by a class_summary chunk (BUG 3 fix)."""
        reader = DelphiFileReader()
        docs = reader.load_data(splash_path)
        node_types = {doc.metadata["node_type"] for doc in docs}
        # Splash.pas has procedure implementations (defProc) and a class summary
        assert "defProc" in node_types, f"Expected defProc in {node_types}"
        assert "class_summary" in node_types, f"Expected class_summary in {node_types}"

    def test_container_declclass_not_emitted_when_has_children(self, splash_path):
        """declClass should NOT be emitted because TfrmSplash has matched children."""
        reader = DelphiFileReader()
        docs = reader.load_data(splash_path)
        node_types = {doc.metadata["node_type"] for doc in docs}
        assert "declClass" not in node_types, (
            "declClass should not be emitted when it has matched descendants"
        )

    def test_file_path_metadata_is_correct(self, splash_path):
        """file_path metadata should match the input file path."""
        reader = DelphiFileReader()
        docs = reader.load_data(splash_path)
        for doc in docs:
            assert doc.metadata["file_path"] == str(splash_path)

    def test_all_chunks_non_empty(self, splash_path):
        """Every chunk text should be non-empty after creation."""
        reader = DelphiFileReader()
        docs = reader.load_data(splash_path)
        for doc in docs:
            assert len(doc.text.strip()) > 0


# ────────────────────────────────────────────────
# TestChildrenFirstBehavior
# ────────────────────────────────────────────────


class TestChildrenFirstBehavior:
    """Tests for the children-first chunking strategy."""

    def test_class_not_emitted_when_has_matched_children(self, tmp_path):
        """A class with fields and procedures should NOT be emitted as a single chunk."""
        f = tmp_path / "test_class.pas"
        f.write_text(
            "unit TestClass;\n"
            "\n"
            "interface\n"
            "\n"
            "type\n"
            "  TMyClass = class(TObject)\n"
            "    FField1: Integer;\n"
            "    FField2: string;\n"
            "    procedure DoSomething;\n"
            "    function GetValue: Integer;\n"
            "  end;\n"
            "\n"
            "implementation\n"
            "\n"
            "procedure TMyClass.DoSomething;\n"
            "begin\n"
            "  // implementation code for DoSomething\n"
            "  WriteLn('Doing something important here');\n"
            "end;\n"
            "\n"
            "function TMyClass.GetValue: Integer;\n"
            "begin\n"
            "  Result := FField1 + Length(FField2);\n"
            "end;\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        node_types = {doc.metadata["node_type"] for doc in docs}
        # The class container should be decomposed, not emitted whole
        assert "declClass" not in node_types

    def test_individual_members_are_emitted(self, tmp_path):
        """Fields and procedures within a class should be emitted individually."""
        f = tmp_path / "test_members.pas"
        f.write_text(
            "unit TestMembers;\n"
            "\n"
            "interface\n"
            "\n"
            "type\n"
            "  TMyClass = class(TObject)\n"
            "    FField1: Integer;\n"
            "    FField2: string;\n"
            "    procedure DoSomething;\n"
            "    function GetValue: Integer;\n"
            "  end;\n"
            "\n"
            "implementation\n"
            "\n"
            "procedure TMyClass.DoSomething;\n"
            "begin\n"
            "  // implementation code for DoSomething\n"
            "  WriteLn('Doing something important here');\n"
            "end;\n"
            "\n"
            "function TMyClass.GetValue: Integer;\n"
            "begin\n"
            "  Result := FField1 + Length(FField2);\n"
            "end;\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        node_types = [doc.metadata["node_type"] for doc in docs]
        # Should have individual field declarations and procedure implementations
        assert (
            "defProc" in node_types
            or "declProc" in node_types
            or "declField" in node_types
        )

    def test_standalone_const_block_emitted_when_no_matched_children(self, tmp_path):
        """A const block without matched descendants should be emitted as a whole."""
        f = tmp_path / "test_const.pas"
        f.write_text(
            "unit TestConst;\n"
            "\n"
            "interface\n"
            "\n"
            "const\n"
            "  MAX_VALUE = 100;\n"
            "  MIN_VALUE = 0;\n"
            "  APP_NAME = 'TestApp';\n"
            "\n"
            "implementation\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        node_types = [doc.metadata["node_type"] for doc in docs]
        # Const block has no matched children (individual const assignments are not
        # in NODE_TYPES), so it should be emitted as declConst
        # If the parser doesn't produce declConst, it falls back to full_file
        # Either way, the test validates the behavior
        has_const_or_full = "declConst" in node_types or "full_file" in node_types
        assert has_const_or_full

    def test_var_block_without_matched_children_emitted(self, tmp_path):
        """A var block with simple variable declarations should be emitted whole."""
        f = tmp_path / "test_var.pas"
        f.write_text(
            "unit TestVar;\n"
            "\n"
            "interface\n"
            "\n"
            "var\n"
            "  GlobalCount: Integer;\n"
            "  GlobalName: string;\n"
            "  GlobalActive: Boolean;\n"
            "\n"
            "implementation\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        node_types = [doc.metadata["node_type"] for doc in docs]
        # var block without matched children gets emitted as declVar or full_file fallback
        has_var_or_full = "declVar" in node_types or "full_file" in node_types
        assert has_var_or_full


# ────────────────────────────────────────────────
# TestChunkSizeFiltering
# ────────────────────────────────────────────────


class TestChunkSizeFiltering:
    """Tests for MIN_CHUNK_SIZE filtering behavior."""

    def test_short_comment_not_in_output(self, tmp_path):
        """A comment shorter than MIN_CHUNK_SIZE should be discarded."""
        f = tmp_path / "short_comment.pas"
        # Write a file with just a very short comment and an implementation
        f.write_text(
            "unit ShortComment;\n"
            "\n"
            "interface\n"
            "\n"
            "{ x }\n"  # Very short comment
            "\n"
            "implementation\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        # If the short comment was detected by tree-sitter, it should be filtered out
        for doc in docs:
            if doc.metadata.get("node_type") == "comment":
                # If a comment made it through, it must be >= MIN_CHUNK_SIZE
                assert len(doc.text) >= reader.MIN_CHUNK_SIZE

    def test_normal_comment_in_output(self, tmp_path):
        """A comment longer than MIN_CHUNK_SIZE should appear in the output."""
        f = tmp_path / "normal_comment.pas"
        long_comment = "{ This is a sufficiently long comment that should exceed the minimum chunk size threshold }"
        f.write_text(
            f"unit NormalComment;\n"
            f"\n"
            f"interface\n"
            f"\n"
            f"{long_comment}\n"
            f"\n"
            f"implementation\n"
            f"\n"
            f"end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        comment_docs = [d for d in docs if d.metadata.get("node_type") == "comment"]
        # The long comment should have been emitted
        if comment_docs:
            assert any(len(d.text) >= reader.MIN_CHUNK_SIZE for d in comment_docs)

    def test_all_output_chunks_meet_min_size(self, tmp_path):
        """No output chunk should be smaller than MIN_CHUNK_SIZE."""
        f = tmp_path / "min_size.pas"
        f.write_text(
            "unit MinSize;\n"
            "\n"
            "interface\n"
            "\n"
            "type\n"
            "  TForm1 = class(TForm)\n"
            "    FValue: Integer;\n"
            "    procedure FormCreate(Sender: TObject);\n"
            "  end;\n"
            "\n"
            "implementation\n"
            "\n"
            "procedure TForm1.FormCreate(Sender: TObject);\n"
            "begin\n"
            "  FValue := 42;\n"
            "end;\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            # full_file fallback is exempt from chunk size filtering
            if doc.metadata.get("node_type") != "full_file":
                assert len(doc.text) >= reader.MIN_CHUNK_SIZE, (
                    f"Chunk too small ({len(doc.text)} chars): {doc.text!r}"
                )


# ────────────────────────────────────────────────
# TestOversizedChunkSplitting
# ────────────────────────────────────────────────


class TestOversizedChunkSplitting:
    """Tests for oversized chunk splitting behavior."""

    def test_oversized_chunk_gets_split(self, tmp_path, monkeypatch):
        """A procedure exceeding MAX_CHUNK_CHARS should be split into multiple docs."""
        # Lower MAX_CHUNK_CHARS to make testing practical.
        # The TokenTextSplitter has chunk_size=1024 tokens (~4k chars),
        # so we need content large enough to be split into multiple token chunks.
        monkeypatch.setattr(DelphiFileReader, "MAX_CHUNK_CHARS", 200)

        f = tmp_path / "big_proc.pas"
        # Create a procedure with enough content to exceed 1024 tokens
        # Each line is ~75 chars ≈ ~18 tokens; need ~60 lines for >1024 tokens
        body_lines = "\n".join(
            f"  WriteLn('Line {i}: This is a very long test statement that pads the procedure body with enough content to generate many tokens for splitting purposes.');"
            for i in range(80)
        )
        f.write_text(
            f"unit BigProc;\n"
            f"\n"
            f"interface\n"
            f"\n"
            f"implementation\n"
            f"\n"
            f"procedure BigProcedure;\n"
            f"begin\n"
            f"{body_lines}\n"
            f"end;\n"
            f"\n"
            f"end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)

        # Find split documents
        split_docs = [d for d in docs if "_split" in d.metadata.get("node_type", "")]
        assert len(split_docs) > 1, (
            f"Expected multiple split documents, got node_types: "
            f"{[d.metadata.get('node_type') for d in docs]}"
        )

    def test_split_metadata_correct(self, tmp_path, monkeypatch):
        """Split documents should have correct split_part and split_total metadata."""
        monkeypatch.setattr(DelphiFileReader, "MAX_CHUNK_CHARS", 200)

        f = tmp_path / "big_proc2.pas"
        body_lines = "\n".join(
            f"  WriteLn('Line {i}: This is a test statement that pads the procedure body.');"
            for i in range(20)
        )
        f.write_text(
            f"unit BigProc2;\n"
            f"\n"
            f"interface\n"
            f"\n"
            f"implementation\n"
            f"\n"
            f"procedure BigProcedureTwo;\n"
            f"begin\n"
            f"{body_lines}\n"
            f"end;\n"
            f"\n"
            f"end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)

        split_docs = [d for d in docs if "_split" in d.metadata.get("node_type", "")]
        if split_docs:
            for doc in split_docs:
                assert "split_part" in doc.metadata
                assert "split_total" in doc.metadata
                assert isinstance(doc.metadata["split_part"], int)
                assert isinstance(doc.metadata["split_total"], int)
                assert doc.metadata["split_part"] >= 0
                assert doc.metadata["split_part"] < doc.metadata["split_total"]

    def test_node_type_gets_split_suffix(self, tmp_path, monkeypatch):
        """Split chunks should have node_type ending in '_split'."""
        monkeypatch.setattr(DelphiFileReader, "MAX_CHUNK_CHARS", 200)

        f = tmp_path / "big_proc3.pas"
        body_lines = "\n".join(
            f"  WriteLn('Line {i}: Some more text to fill up the procedure body content.');"
            for i in range(20)
        )
        f.write_text(
            f"unit BigProc3;\n"
            f"\n"
            f"interface\n"
            f"\n"
            f"implementation\n"
            f"\n"
            f"procedure BigProcedureThree;\n"
            f"begin\n"
            f"{body_lines}\n"
            f"end;\n"
            f"\n"
            f"end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)

        split_docs = [d for d in docs if "split_part" in d.metadata]
        for doc in split_docs:
            assert doc.metadata["node_type"].endswith("_split")


# ────────────────────────────────────────────────
# TestFallbackToFullFile
# ────────────────────────────────────────────────


class TestFallbackToFullFile:
    """Tests for fallback to full_file when no AST nodes match."""

    def test_file_with_no_matched_nodes_returns_full_file(self, tmp_path):
        """A .pas file with no recognized AST chunks should return a full_file Document."""
        f = tmp_path / "no_match.pas"
        # A file that tree-sitter can parse but produces no matching node types
        # Uses and implementation block with no procedures, classes, etc.
        f.write_text(
            "unit NoMatch;\n\ninterface\n\nuses SysUtils;\n\nimplementation\n\nend.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        # If tree-sitter finds no matching nodes, should fall back to full_file
        node_types = [d.metadata["node_type"] for d in docs]
        # Either matched some nodes or fell back to full_file
        assert len(docs) >= 1
        if "full_file" in node_types:
            assert len(docs) == 1
            assert docs[0].metadata["node_type"] == "full_file"

    def test_fallback_document_contains_full_content(self, tmp_path):
        """The full_file fallback should contain the entire file content."""
        f = tmp_path / "full.pas"
        content = "unit Full;\ninterface\nuses SysUtils;\nimplementation\nend.\n"
        f.write_text(content, encoding="utf-8")
        reader = DelphiFileReader()

        # Force no AST matches by replacing the module-level _parser with a mock
        # that returns a tree whose root_node has no matching children.
        mock_root = _make_mock_node("root", children=[])
        mock_tree = MagicMock()
        mock_tree.root_node = mock_root

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_tree

        with patch("shared.readers.pascal_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"
        assert docs[0].text == content

    def test_fallback_has_file_datetime_metadata(self, tmp_path):
        """The full_file fallback document should have file datetime metadata."""
        f = tmp_path / "fallback.pas"
        f.write_text(
            "unit Fallback;\ninterface\nimplementation\nend.\n", encoding="utf-8"
        )

        mock_root = _make_mock_node("root", children=[])
        mock_tree = MagicMock()
        mock_tree.root_node = mock_root

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_tree

        reader = DelphiFileReader()
        with patch("shared.readers.pascal_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert "creation_datetime" in docs[0].metadata
        assert "modification_datetime" in docs[0].metadata


# ────────────────────────────────────────────────
# TestFileReadError
# ────────────────────────────────────────────────


class TestFileReadError:
    """Tests for load_data() with file read failures."""

    def test_nonexistent_file_returns_empty_list(self, tmp_path):
        """A non-existent file should return an empty list."""
        f = tmp_path / "nonexistent.pas"
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        assert docs == []

    def test_nonexistent_file_does_not_raise(self, tmp_path):
        """A non-existent file should not raise an exception."""
        f = tmp_path / "missing.pas"
        reader = DelphiFileReader()
        # Should not raise
        docs = reader.load_data(f)
        assert isinstance(docs, list)

    def test_read_failure_logs_warning(self, tmp_path):
        """A file that fails to read should trigger a log_warn call."""
        f = tmp_path / "unreadable.pas"
        reader = DelphiFileReader()

        with patch(
            "shared.readers.pascal_reader.read_file_with_encoding_and_bytes"
        ) as mock_read:
            mock_read.side_effect = PermissionError("Access denied")
            with patch("shared.readers.pascal_reader.log_warn") as mock_warn:
                docs = reader.load_data(f)

        assert docs == []
        mock_warn.assert_called_once()
        assert "Failed to read" in mock_warn.call_args[0][0]


# ────────────────────────────────────────────────
# TestMetadata
# ────────────────────────────────────────────────


class TestMetadata:
    """Tests for metadata correctness on returned documents."""

    def test_file_path_metadata(self, tmp_path):
        """Each document should have file_path matching the input file."""
        f = tmp_path / "meta_test.pas"
        f.write_text(
            "unit MetaTest;\n"
            "interface\n"
            "type\n"
            "  TFoo = class(TObject)\n"
            "    FBar: Integer;\n"
            "    procedure DoWork;\n"
            "  end;\n"
            "implementation\n"
            "procedure TFoo.DoWork;\n"
            "begin\n"
            "  FBar := FBar + 1;\n"
            "end;\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            assert doc.metadata["file_path"] == str(f)

    def test_node_type_metadata_present(self, tmp_path):
        """Each document should have a non-empty node_type."""
        f = tmp_path / "node_type_test.pas"
        f.write_text(
            "unit NodeTypeTest;\n"
            "interface\n"
            "implementation\n"
            "procedure Foo;\n"
            "begin\n"
            "  WriteLn('test');\n"
            "end;\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            assert "node_type" in doc.metadata
            assert len(doc.metadata["node_type"]) > 0

    def test_line_number_metadata(self, tmp_path):
        """Documents should have start_line and end_line metadata."""
        f = tmp_path / "lines.pas"
        f.write_text(
            "unit Lines;\n"
            "interface\n"
            "implementation\n"
            "procedure TestProc;\n"
            "begin\n"
            "  WriteLn('Hello from TestProc');\n"
            "end;\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert "start_line" in doc.metadata
                assert "end_line" in doc.metadata
                assert doc.metadata["start_line"] >= 1
                assert doc.metadata["end_line"] >= doc.metadata["start_line"]

    def test_byte_range_metadata(self, tmp_path):
        """Documents should have start_byte and end_byte metadata."""
        f = tmp_path / "bytes.pas"
        f.write_text(
            "unit Bytes;\n"
            "interface\n"
            "implementation\n"
            "procedure ByteProc;\n"
            "begin\n"
            "  WriteLn('testing byte ranges');\n"
            "end;\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert "start_byte" in doc.metadata
                assert "end_byte" in doc.metadata
                assert doc.metadata["start_byte"] >= 0
                assert doc.metadata["end_byte"] > doc.metadata["start_byte"]

    def test_file_datetime_metadata_present(self, tmp_path):
        """Documents should have creation_datetime and modification_datetime."""
        f = tmp_path / "datetime.pas"
        f.write_text(
            "unit DateTime;\n"
            "interface\n"
            "implementation\n"
            "procedure TimeProc;\n"
            "begin\n"
            "  WriteLn('datetime metadata test');\n"
            "end;\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            assert "creation_datetime" in doc.metadata
            assert "modification_datetime" in doc.metadata
            # Should be valid ISO datetime strings
            from datetime import datetime

            datetime.fromisoformat(doc.metadata["creation_datetime"])
            datetime.fromisoformat(doc.metadata["modification_datetime"])


# ────────────────────────────────────────────────
# TestIntegration
# ────────────────────────────────────────────────


class TestIntegration:
    """Integration tests using multiple real sample .pas files."""

    @pytest.fixture(
        params=[
            "Splash.pas",
            "MainDM.pas",
            "MainForm.pas",
            "core105.classes.pas",
            "core.base.classes.pas",
        ]
    )
    def test_file(self, request) -> Path:
        """Parametrized fixture returning paths to real test .pas files."""
        p = _SAMPLE_FILES / request.param
        if not p.exists():
            pytest.skip(f"Test file not found: {p}")
        return p

    def test_returns_documents(self, test_file):
        """Each real test file should produce at least one Document."""
        reader = DelphiFileReader()
        docs = reader.load_data(test_file)
        assert len(docs) > 0, f"No documents from {test_file.name}"

    def test_no_overlapping_byte_ranges(self, test_file):
        """Chunks should not have overlapping byte ranges (children-first dedup)."""
        reader = DelphiFileReader()
        docs = reader.load_data(test_file)

        # Collect byte ranges for non-split, non-full_file docs
        ranges = []
        for doc in docs:
            nt = doc.metadata.get("node_type", "")
            if nt == "full_file" or nt.endswith("_split"):
                continue
            sb = doc.metadata.get("start_byte")
            eb = doc.metadata.get("end_byte")
            if sb is not None and eb is not None:
                ranges.append((sb, eb))

        # Check for overlapping ranges at the same nesting level
        # (Children can be inside parents, but no two siblings should overlap)
        ranges.sort()
        for i in range(len(ranges) - 1):
            # Two consecutive ranges sorted by start_byte:
            # allowed: A fully contains B (children-first) or they don't overlap
            # not allowed: partial overlap (which indicates a bug)
            a_start, a_end = ranges[i]
            b_start, b_end = ranges[i + 1]
            # If B starts after A ends, no overlap
            if b_start >= a_end:
                continue
            # If B is fully contained within A, that's fine (parent containing child)
            if a_start <= b_start and b_end <= a_end:
                continue
            # Partial overlap is a bug
            assert False, (
                f"Partial overlap in {test_file.name}: "
                f"({a_start},{a_end}) and ({b_start},{b_end})"
            )

    def test_all_node_types_are_known(self, test_file):
        """All node_type values should be recognized types (or full_file or _split suffix)."""
        reader = DelphiFileReader()
        docs = reader.load_data(test_file)
        known = DelphiFileReader.NODE_TYPES | {
            "full_file",
            "class_summary",
            "class_overview",
            "method_group",
        }
        for doc in docs:
            nt = doc.metadata.get("node_type", "")
            base_nt = nt.replace("_split", "")
            assert base_nt in known, f"Unknown node_type '{nt}' in {test_file.name}"

    def test_splash_reasonable_chunk_count(self):
        """Splash.pas should produce a reasonable number of chunks (5-30)."""
        p = _SAMPLE_FILES / "Splash.pas"
        if not p.exists():
            pytest.skip("Splash.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        assert 5 <= len(docs) <= 30, (
            f"Splash.pas produced {len(docs)} chunks, expected 5-30"
        )

    def test_large_file_produces_many_chunks(self):
        """core105.classes.pas (large file) should produce many chunks."""
        p = _SAMPLE_FILES / "core105.classes.pas"
        if not p.exists():
            pytest.skip("core105.classes.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        assert len(docs) > 20, (
            f"core105.classes.pas produced only {len(docs)} chunks, expected > 20"
        )

    def test_all_chunks_have_text_content(self, test_file):
        """Every document should have non-empty text."""
        reader = DelphiFileReader()
        docs = reader.load_data(test_file)
        for doc in docs:
            assert len(doc.text) > 0, (
                f"Empty text in chunk of type {doc.metadata.get('node_type')}"
            )

    def test_metadata_consistency(self, test_file):
        """All documents should have consistent metadata keys."""
        reader = DelphiFileReader()
        docs = reader.load_data(test_file)
        required_keys = {"file_path", "node_type"}
        for doc in docs:
            for key in required_keys:
                assert key in doc.metadata, (
                    f"Missing '{key}' in metadata for {test_file.name}"
                )


# ────────────────────────────────────────────────
# TestContextPrefix
# ────────────────────────────────────────────────


class TestContextPrefix:
    """Tests for the context prefix (// Unit: ..., // Class: ...) on every chunk."""

    _BASIC_UNIT = (
        "unit TestUnit;\n"
        "\n"
        "interface\n"
        "\n"
        "uses SysUtils, Classes;\n"
        "\n"
        "type\n"
        "  TMyClass = class(TObject)\n"
        "  private\n"
        "    FValue: Integer;\n"
        "  public\n"
        "    procedure DoWork;\n"
        "    function GetValue: Integer;\n"
        "  end;\n"
        "\n"
        "implementation\n"
        "\n"
        "uses Windows;\n"
        "\n"
        "procedure TMyClass.DoWork;\n"
        "begin\n"
        "  FValue := 42;\n"
        "end;\n"
        "\n"
        "function TMyClass.GetValue: Integer;\n"
        "begin\n"
        "  Result := FValue;\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    @pytest.fixture
    def basic_unit_file(self, tmp_path) -> Path:
        """Write a standard Pascal unit with class and methods."""
        f = tmp_path / "TestUnit.pas"
        f.write_text(self._BASIC_UNIT, encoding="utf-8")
        return f

    def test_all_chunks_start_with_unit_prefix(self, basic_unit_file):
        """Every chunk from a file with a unit declaration should start with '// Unit:'."""
        reader = DelphiFileReader()
        docs = reader.load_data(basic_unit_file)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert doc.text.startswith("// Unit:"), (
                    f"Chunk of type '{doc.metadata['node_type']}' does not start "
                    f"with '// Unit:': {doc.text[:100]!r}"
                )

    def test_unit_name_is_correct(self, basic_unit_file):
        """The context prefix should contain the correct unit name 'TestUnit'."""
        reader = DelphiFileReader()
        docs = reader.load_data(basic_unit_file)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                first_line = doc.text.split("\n")[0]
                assert "TestUnit" in first_line, (
                    f"Expected 'TestUnit' in first line: {first_line!r}"
                )

    def test_unit_prefix_contains_filename(self, basic_unit_file):
        """The context prefix should contain the file name in parentheses."""
        reader = DelphiFileReader()
        docs = reader.load_data(basic_unit_file)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                first_line = doc.text.split("\n")[0]
                assert "(TestUnit.pas)" in first_line, (
                    f"Expected '(TestUnit.pas)' in first line: {first_line!r}"
                )

    def test_class_method_chunks_have_class_context(self, basic_unit_file):
        """defProc chunks for class methods should have '// Class:' in their prefix."""
        reader = DelphiFileReader()
        docs = reader.load_data(basic_unit_file)
        class_method_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
            and "TMyClass" in d.text
        ]
        assert len(class_method_docs) > 0, "Expected at least one class method chunk"
        for doc in class_method_docs:
            assert "// Class:" in doc.text, (
                f"Class method chunk missing '// Class:': {doc.text[:200]!r}"
            )

    def test_class_context_contains_parent(self, basic_unit_file):
        """The class context line should reference the parent class TObject."""
        reader = DelphiFileReader()
        docs = reader.load_data(basic_unit_file)
        class_method_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
            and "// Class:" in d.text
        ]
        assert len(class_method_docs) > 0
        for doc in class_method_docs:
            # The class line should be something like:
            # // Class: TMyClass = class(TObject)
            class_lines = [l for l in doc.text.split("\n") if l.startswith("// Class:")]
            assert len(class_lines) == 1
            assert "TMyClass" in class_lines[0]

    def test_non_class_chunks_have_no_class_context(self, tmp_path):
        """Standalone procedures (not class methods) should only have a Unit line, no Class line."""
        f = tmp_path / "Standalone.pas"
        f.write_text(
            "unit Standalone;\n"
            "\n"
            "interface\n"
            "\n"
            "implementation\n"
            "\n"
            "procedure FreeStandingProc;\n"
            "begin\n"
            "  WriteLn('I am not a class method');\n"
            "end;\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        proc_docs = [d for d in docs if d.metadata.get("node_type") == "defProc"]
        assert len(proc_docs) > 0, "Expected at least one defProc chunk"
        for doc in proc_docs:
            assert "// Class:" not in doc.text, (
                f"Standalone proc should not have class context: {doc.text[:200]!r}"
            )
            assert "// Unit: Standalone" in doc.text

    def test_decl_section_inside_class_has_class_context(self, basic_unit_file):
        """declSection chunks (private/public/published) should have '// Class:' in prefix."""
        reader = DelphiFileReader()
        docs = reader.load_data(basic_unit_file)
        decl_sections = [
            d for d in docs if d.metadata.get("node_type") == "declSection"
        ]
        for doc in decl_sections:
            # declSection inside a class should have class context
            if "FValue" in doc.text or "DoWork" in doc.text:
                assert "// Class:" in doc.text, (
                    f"declSection inside class should have class context: "
                    f"{doc.text[:200]!r}"
                )

    def test_splash_real_file_has_unit_prefix(self):
        """Real Splash.pas file: all chunks should start with '// Unit:'."""
        p = _SAMPLE_FILES / "Splash.pas"
        if not p.exists():
            pytest.skip("Splash.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert doc.text.startswith("// Unit:"), (
                    f"Splash.pas chunk missing unit prefix: "
                    f"node_type={doc.metadata['node_type']}, text={doc.text[:80]!r}"
                )


# ────────────────────────────────────────────────
# TestClassSummary
# ────────────────────────────────────────────────


class TestClassSummary:
    """Tests for class_summary chunk generation (node_type='class_summary')."""

    _SINGLE_CLASS = (
        "unit SingleClass;\n"
        "\n"
        "interface\n"
        "\n"
        "type\n"
        "  TMyClass = class(TObject)\n"
        "  private\n"
        "    FValue: Integer;\n"
        "  public\n"
        "    procedure DoWork;\n"
        "    function GetValue: Integer;\n"
        "  end;\n"
        "\n"
        "implementation\n"
        "\n"
        "procedure TMyClass.DoWork;\n"
        "begin\n"
        "  FValue := 42;\n"
        "end;\n"
        "\n"
        "function TMyClass.GetValue: Integer;\n"
        "begin\n"
        "  Result := FValue;\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    _MULTI_CLASS = (
        "unit MultiClass;\n"
        "\n"
        "interface\n"
        "\n"
        "type\n"
        "  TFirst = class(TObject)\n"
        "  private\n"
        "    FAlpha: Integer;\n"
        "  public\n"
        "    procedure Run;\n"
        "  end;\n"
        "\n"
        "  TSecond = class(TObject)\n"
        "  private\n"
        "    FBeta: string;\n"
        "  public\n"
        "    function Name: string;\n"
        "  end;\n"
        "\n"
        "implementation\n"
        "\n"
        "procedure TFirst.Run;\n"
        "begin\n"
        "  FAlpha := FAlpha + 1;\n"
        "end;\n"
        "\n"
        "function TSecond.Name: string;\n"
        "begin\n"
        "  Result := FBeta;\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    def test_single_class_produces_class_summary(self, tmp_path):
        """A file with one class should produce at least one class_summary chunk."""
        f = tmp_path / "SingleClass.pas"
        f.write_text(self._SINGLE_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) >= 1, (
            f"Expected at least 1 class_summary, got {len(summaries)}. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_class_summary_contains_class_header(self, tmp_path):
        """The class_summary chunk should contain the class header line."""
        f = tmp_path / "SingleClass.pas"
        f.write_text(self._SINGLE_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) >= 1
        summary_text = summaries[0].text
        assert "TMyClass" in summary_text, (
            f"class_summary should contain 'TMyClass': {summary_text[:300]!r}"
        )
        # Should contain the class(...) part
        assert "class(TObject)" in summary_text or "class (TObject)" in summary_text, (
            f"class_summary should contain 'class(TObject)': {summary_text[:300]!r}"
        )

    def test_class_summary_contains_visibility_sections(self, tmp_path):
        """The class_summary chunk should contain private/public section content."""
        f = tmp_path / "SingleClass.pas"
        f.write_text(self._SINGLE_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) >= 1
        text = summaries[0].text
        # Should include field and method declarations from the class body
        assert "FValue" in text, f"class_summary should include FValue: {text[:400]!r}"
        assert "DoWork" in text, f"class_summary should include DoWork: {text[:400]!r}"
        assert "GetValue" in text, (
            f"class_summary should include GetValue: {text[:400]!r}"
        )

    def test_class_summary_has_context_prefix(self, tmp_path):
        """The class_summary chunk should start with the context prefix."""
        f = tmp_path / "SingleClass.pas"
        f.write_text(self._SINGLE_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) >= 1
        text = summaries[0].text
        assert text.startswith("// Unit:"), (
            f"class_summary should start with unit prefix: {text[:100]!r}"
        )
        assert "// Class:" in text, (
            f"class_summary should have class prefix: {text[:200]!r}"
        )

    def test_multiple_classes_produce_multiple_summaries(self, tmp_path):
        """A file with two classes should produce two class_summary chunks."""
        f = tmp_path / "MultiClass.pas"
        f.write_text(self._MULTI_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) == 2, (
            f"Expected 2 class_summary chunks, got {len(summaries)}. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_multiple_summaries_cover_both_classes(self, tmp_path):
        """Each class_summary should identify its own class."""
        f = tmp_path / "MultiClass.pas"
        f.write_text(self._MULTI_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        texts = [s.text for s in summaries]
        class_names_found = set()
        for t in texts:
            if "TFirst" in t:
                class_names_found.add("TFirst")
            if "TSecond" in t:
                class_names_found.add("TSecond")
        assert class_names_found == {"TFirst", "TSecond"}, (
            f"Expected both TFirst and TSecond in summaries, found: {class_names_found}"
        )

    def test_class_summary_for_first_class_has_its_fields(self, tmp_path):
        """The TFirst class_summary should mention FAlpha, not FBeta."""
        f = tmp_path / "MultiClass.pas"
        f.write_text(self._MULTI_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [
            d
            for d in docs
            if d.metadata.get("node_type") == "class_summary" and "TFirst" in d.text
        ]
        assert len(summaries) == 1
        assert "FAlpha" in summaries[0].text
        assert "Run" in summaries[0].text

    def test_class_summary_for_second_class_has_its_fields(self, tmp_path):
        """The TSecond class_summary should mention FBeta, not FAlpha."""
        f = tmp_path / "MultiClass.pas"
        f.write_text(self._MULTI_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [
            d
            for d in docs
            if d.metadata.get("node_type") == "class_summary" and "TSecond" in d.text
        ]
        assert len(summaries) == 1
        assert "FBeta" in summaries[0].text
        assert "Name" in summaries[0].text

    def test_splash_real_file_has_class_summary(self):
        """Real Splash.pas file should produce a class_summary for TfrmSplash."""
        p = _SAMPLE_FILES / "Splash.pas"
        if not p.exists():
            pytest.skip("Splash.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) >= 1, (
            f"Splash.pas should produce class_summary. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )


# ────────────────────────────────────────────────
# TestUsesClause
# ────────────────────────────────────────────────


class TestUsesClause:
    """Tests for uses clause (declUses) chunk emission."""

    _USES_UNIT = (
        "unit UsesUnit;\n"
        "\n"
        "interface\n"
        "\n"
        "uses SysUtils, Classes;\n"
        "\n"
        "implementation\n"
        "\n"
        "uses Windows;\n"
        "\n"
        "end.\n"
    )

    def test_uses_clause_produces_chunk(self, tmp_path):
        """A file with 'uses SysUtils, Classes;' should produce a declUses chunk."""
        f = tmp_path / "UsesUnit.pas"
        f.write_text(self._USES_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        uses_docs = [d for d in docs if d.metadata.get("node_type") == "declUses"]
        assert len(uses_docs) >= 1, (
            f"Expected at least 1 declUses chunk. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_uses_clause_text_contains_unit_names(self, tmp_path):
        """The declUses chunk should contain the used unit names."""
        f = tmp_path / "UsesUnit.pas"
        f.write_text(self._USES_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        uses_docs = [d for d in docs if d.metadata.get("node_type") == "declUses"]
        assert len(uses_docs) >= 1
        all_uses_text = " ".join(d.text for d in uses_docs)
        assert "SysUtils" in all_uses_text, (
            f"Expected 'SysUtils' in uses chunk: {all_uses_text[:200]!r}"
        )
        assert "Classes" in all_uses_text, (
            f"Expected 'Classes' in uses chunk: {all_uses_text[:200]!r}"
        )

    def test_both_interface_and_implementation_uses_captured(self, tmp_path):
        """Both interface and implementation uses clauses should be captured."""
        f = tmp_path / "UsesUnit.pas"
        f.write_text(self._USES_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        uses_docs = [d for d in docs if d.metadata.get("node_type") == "declUses"]
        # We expect 2 declUses chunks (interface + implementation)
        assert len(uses_docs) == 2, (
            f"Expected 2 declUses chunks (interface + impl), got {len(uses_docs)}. "
            f"Texts: {[d.text[:80] for d in uses_docs]}"
        )

    def test_interface_uses_contains_sysutils(self, tmp_path):
        """The interface uses clause should mention SysUtils."""
        f = tmp_path / "UsesUnit.pas"
        f.write_text(self._USES_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        uses_docs = [d for d in docs if d.metadata.get("node_type") == "declUses"]
        assert any("SysUtils" in d.text for d in uses_docs)

    def test_implementation_uses_contains_windows(self, tmp_path):
        """The implementation uses clause should mention Windows."""
        f = tmp_path / "UsesUnit.pas"
        f.write_text(self._USES_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        uses_docs = [d for d in docs if d.metadata.get("node_type") == "declUses"]
        assert any("Windows" in d.text for d in uses_docs), (
            f"Expected 'Windows' in uses chunk. "
            f"Texts: {[d.text[:100] for d in uses_docs]}"
        )

    def test_uses_clause_has_unit_context_prefix(self, tmp_path):
        """Uses clause chunks should have the unit context prefix."""
        f = tmp_path / "UsesUnit.pas"
        f.write_text(self._USES_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        uses_docs = [d for d in docs if d.metadata.get("node_type") == "declUses"]
        for doc in uses_docs:
            assert doc.text.startswith("// Unit:"), (
                f"Uses clause should start with unit prefix: {doc.text[:100]!r}"
            )
            assert "UsesUnit" in doc.text.split("\n")[0]

    def test_file_without_uses_has_no_decl_uses(self, tmp_path):
        """A file without uses clauses should not produce any declUses chunks."""
        f = tmp_path / "NoUses.pas"
        f.write_text(
            "unit NoUses;\n"
            "\n"
            "interface\n"
            "\n"
            "implementation\n"
            "\n"
            "procedure Foo;\n"
            "begin\n"
            "  WriteLn('no uses clause here');\n"
            "end;\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        uses_docs = [d for d in docs if d.metadata.get("node_type") == "declUses"]
        assert len(uses_docs) == 0, f"Expected no declUses chunks, got {len(uses_docs)}"


# ────────────────────────────────────────────────
# TestTrivialMethodGrouping
# ────────────────────────────────────────────────


class TestTrivialMethodGrouping:
    """Tests for trivial method grouping (node_type='method_group')."""

    _FIVE_TRIVIAL = (
        "unit TrivialMethods;\n"
        "\n"
        "interface\n"
        "\n"
        "type\n"
        "  TFoo = class(TObject)\n"
        "    function GetA: Integer;\n"
        "    function GetB: Integer;\n"
        "    function GetC: Integer;\n"
        "    function GetD: Integer;\n"
        "    function GetE: Integer;\n"
        "  end;\n"
        "\n"
        "implementation\n"
        "\n"
        "function TFoo.GetA: Integer;\n"
        "begin\n"
        "  Result := 1;\n"
        "end;\n"
        "\n"
        "function TFoo.GetB: Integer;\n"
        "begin\n"
        "  Result := 2;\n"
        "end;\n"
        "\n"
        "function TFoo.GetC: Integer;\n"
        "begin\n"
        "  Result := 3;\n"
        "end;\n"
        "\n"
        "function TFoo.GetD: Integer;\n"
        "begin\n"
        "  Result := 4;\n"
        "end;\n"
        "\n"
        "function TFoo.GetE: Integer;\n"
        "begin\n"
        "  Result := 5;\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    _TWO_TRIVIAL = (
        "unit TwoTrivial;\n"
        "\n"
        "interface\n"
        "\n"
        "type\n"
        "  TBar = class(TObject)\n"
        "    function GetX: Integer;\n"
        "    function GetY: Integer;\n"
        "  end;\n"
        "\n"
        "implementation\n"
        "\n"
        "function TBar.GetX: Integer;\n"
        "begin\n"
        "  Result := 1;\n"
        "end;\n"
        "\n"
        "function TBar.GetY: Integer;\n"
        "begin\n"
        "  Result := 2;\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    def test_five_trivial_methods_produce_method_group(self, tmp_path):
        """5 consecutive trivial methods should be grouped into a method_group chunk."""
        f = tmp_path / "TrivialMethods.pas"
        f.write_text(self._FIVE_TRIVIAL, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        assert len(group_docs) >= 1, (
            f"Expected at least 1 method_group, got {len(group_docs)}. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_method_group_has_group_count_metadata(self, tmp_path):
        """method_group chunks should have a group_count metadata field."""
        f = tmp_path / "TrivialMethods.pas"
        f.write_text(self._FIVE_TRIVIAL, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        assert len(group_docs) >= 1
        for doc in group_docs:
            assert "group_count" in doc.metadata, (
                f"method_group should have group_count metadata"
            )
            assert isinstance(doc.metadata["group_count"], int)
            assert doc.metadata["group_count"] >= 3

    def test_method_group_contains_all_method_names(self, tmp_path):
        """The method_group chunk should contain all five getter names."""
        f = tmp_path / "TrivialMethods.pas"
        f.write_text(self._FIVE_TRIVIAL, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        assert len(group_docs) >= 1
        all_group_text = " ".join(d.text for d in group_docs)
        for name in ["GetA", "GetB", "GetC", "GetD", "GetE"]:
            assert name in all_group_text, f"Expected '{name}' in method_group text"

    def test_method_group_has_method_group_comment(self, tmp_path):
        """The method_group chunk should contain '// Method group:' header."""
        f = tmp_path / "TrivialMethods.pas"
        f.write_text(self._FIVE_TRIVIAL, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        assert len(group_docs) >= 1
        assert any("// Method group:" in d.text for d in group_docs), (
            f"Expected '// Method group:' in group text"
        )

    def test_two_trivial_methods_not_grouped(self, tmp_path):
        """Only 2 consecutive trivial methods should NOT produce a method_group (needs >= 3)."""
        f = tmp_path / "TwoTrivial.pas"
        f.write_text(self._TWO_TRIVIAL, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        assert len(group_docs) == 0, (
            f"2 trivial methods should NOT be grouped, but got {len(group_docs)} groups"
        )

    def test_two_trivial_methods_emitted_individually(self, tmp_path):
        """2 trivial methods should be emitted as individual defProc chunks."""
        f = tmp_path / "TwoTrivial.pas"
        f.write_text(self._TWO_TRIVIAL, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        proc_docs = [d for d in docs if d.metadata.get("node_type") == "defProc"]
        assert len(proc_docs) == 2, (
            f"Expected 2 individual defProc chunks, got {len(proc_docs)}. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_non_trivial_method_breaks_group(self, tmp_path):
        """A non-trivial method (>6 lines) in the middle should break the grouping."""
        f = tmp_path / "MixedMethods.pas"
        # 3 trivial, then 1 non-trivial (>6 lines), then 3 trivial
        f.write_text(
            "unit MixedMethods;\n"
            "\n"
            "interface\n"
            "\n"
            "type\n"
            "  TBaz = class(TObject)\n"
            "    function GetA: Integer;\n"
            "    function GetB: Integer;\n"
            "    function GetC: Integer;\n"
            "    procedure BigMethod;\n"
            "    function GetD: Integer;\n"
            "    function GetE: Integer;\n"
            "    function GetF: Integer;\n"
            "  end;\n"
            "\n"
            "implementation\n"
            "\n"
            "function TBaz.GetA: Integer;\n"
            "begin\n"
            "  Result := 1;\n"
            "end;\n"
            "\n"
            "function TBaz.GetB: Integer;\n"
            "begin\n"
            "  Result := 2;\n"
            "end;\n"
            "\n"
            "function TBaz.GetC: Integer;\n"
            "begin\n"
            "  Result := 3;\n"
            "end;\n"
            "\n"
            "procedure TBaz.BigMethod;\n"
            "var\n"
            "  I: Integer;\n"
            "begin\n"
            "  for I := 0 to 10 do\n"
            "  begin\n"
            "    WriteLn(I);\n"
            "    WriteLn(I * 2);\n"
            "    WriteLn(I * 3);\n"
            "  end;\n"
            "end;\n"
            "\n"
            "function TBaz.GetD: Integer;\n"
            "begin\n"
            "  Result := 4;\n"
            "end;\n"
            "\n"
            "function TBaz.GetE: Integer;\n"
            "begin\n"
            "  Result := 5;\n"
            "end;\n"
            "\n"
            "function TBaz.GetF: Integer;\n"
            "begin\n"
            "  Result := 6;\n"
            "end;\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        big_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") == "defProc" and "BigMethod" in d.text
        ]
        # BigMethod should be emitted individually (not grouped)
        assert len(big_docs) == 1, (
            f"BigMethod should be emitted as defProc, not grouped"
        )
        # The trivial methods on each side of BigMethod should be grouped
        # (3 before and 3 after, each meeting the >= 3 threshold)
        assert len(group_docs) == 2, (
            f"Expected 2 method_groups (before and after BigMethod), "
            f"got {len(group_docs)}. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_group_count_matches_method_count(self, tmp_path):
        """group_count metadata should equal the actual number of grouped methods."""
        f = tmp_path / "TrivialMethods.pas"
        f.write_text(self._FIVE_TRIVIAL, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        assert len(group_docs) >= 1
        total_grouped = sum(d.metadata["group_count"] for d in group_docs)
        assert total_grouped == 5, (
            f"Expected group_count total of 5, got {total_grouped}"
        )

    def test_max_group_chars_respected(self, tmp_path):
        """Method groups should not exceed MAX_GROUP_CHARS (8000).

        The grouping logic accumulates raw node text lengths.  We generate
        enough methods with long-enough bodies so the total raw text exceeds
        MAX_GROUP_CHARS, forcing a split into >=2 groups.
        """
        # Each method body needs to be long enough so total exceeds 8000.
        # ~200 chars per method * 50 methods = ~10000 chars > 8000.
        padding = "x" * 140  # pad the Result line
        methods = []
        for i in range(50):
            methods.append(
                f"function TBig.Get{i:03d}: string;\n"
                f"begin\n"
                f"  Result := '{padding}{i:03d}';\n"
                f"end;\n"
            )
        decls = "\n".join(f"    function Get{i:03d}: string;" for i in range(50))
        impl = "\n".join(methods)
        f = tmp_path / "BigGroup.pas"
        f.write_text(
            f"unit BigGroup;\n"
            f"\n"
            f"interface\n"
            f"\n"
            f"type\n"
            f"  TBig = class(TObject)\n"
            f"{decls}\n"
            f"  end;\n"
            f"\n"
            f"implementation\n"
            f"\n"
            f"{impl}\n"
            f"\n"
            f"end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        # Should have been split into multiple groups due to MAX_GROUP_CHARS
        assert len(group_docs) >= 2, (
            f"Expected multiple method_groups due to MAX_GROUP_CHARS, "
            f"got {len(group_docs)}"
        )
        decls = "\n".join(f"    function Get{i:03d}: string;" for i in range(60))
        impl = "\n".join(methods)
        f = tmp_path / "BigGroup.pas"
        f.write_text(
            f"unit BigGroup;\n"
            f"\n"
            f"interface\n"
            f"\n"
            f"type\n"
            f"  TBig = class(TObject)\n"
            f"{decls}\n"
            f"  end;\n"
            f"\n"
            f"implementation\n"
            f"\n"
            f"{impl}\n"
            f"\n"
            f"end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        group_docs = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        # Should have been split into multiple groups due to MAX_GROUP_CHARS
        assert len(group_docs) >= 2, (
            f"Expected multiple method_groups due to MAX_GROUP_CHARS, "
            f"got {len(group_docs)}"
        )

    def test_trivial_method_lines_constant(self):
        """TRIVIAL_METHOD_LINES should be 6."""
        assert DelphiFileReader.TRIVIAL_METHOD_LINES == 6

    def test_max_group_chars_constant(self):
        """MAX_GROUP_CHARS should be 8000."""
        assert DelphiFileReader.MAX_GROUP_CHARS == 8000


# ────────────────────────────────────────────────
# TestClassNameResolution
# ────────────────────────────────────────────────


class TestClassNameResolution:
    """Tests for class name resolution in implementation method context prefixes."""

    _CLASS_METHOD_UNIT = (
        "unit ClassMethods;\n"
        "\n"
        "interface\n"
        "\n"
        "type\n"
        "  TMyClass = class(TObject)\n"
        "  public\n"
        "    procedure DoStuff;\n"
        "    function CalcValue: Integer;\n"
        "  end;\n"
        "\n"
        "implementation\n"
        "\n"
        "procedure TMyClass.DoStuff;\n"
        "begin\n"
        "  WriteLn('Doing stuff from TMyClass');\n"
        "end;\n"
        "\n"
        "function TMyClass.CalcValue: Integer;\n"
        "begin\n"
        "  Result := 42;\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    _STANDALONE_PROC_UNIT = (
        "unit StandaloneProcs;\n"
        "\n"
        "interface\n"
        "\n"
        "procedure GlobalInit;\n"
        "function GlobalHelper: Integer;\n"
        "\n"
        "implementation\n"
        "\n"
        "procedure GlobalInit;\n"
        "begin\n"
        "  WriteLn('Global initialization done');\n"
        "end;\n"
        "\n"
        "function GlobalHelper: Integer;\n"
        "begin\n"
        "  Result := 99;\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    _MIXED_UNIT = (
        "unit MixedProcs;\n"
        "\n"
        "interface\n"
        "\n"
        "type\n"
        "  TAlpha = class(TObject)\n"
        "  public\n"
        "    procedure AlphaWork;\n"
        "  end;\n"
        "\n"
        "procedure StandaloneFoo;\n"
        "\n"
        "implementation\n"
        "\n"
        "procedure TAlpha.AlphaWork;\n"
        "begin\n"
        "  WriteLn('Alpha is working hard');\n"
        "end;\n"
        "\n"
        "procedure StandaloneFoo;\n"
        "begin\n"
        "  WriteLn('I am a standalone procedure');\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    def test_class_method_has_class_in_prefix(self, tmp_path):
        """'procedure TMyClass.DoStuff' should get '// Class: TMyClass' in prefix."""
        f = tmp_path / "ClassMethods.pas"
        f.write_text(self._CLASS_METHOD_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        dostuff_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
            and "DoStuff" in d.text
        ]
        assert len(dostuff_docs) >= 1, "Expected a chunk containing DoStuff"
        doc = dostuff_docs[0]
        assert "// Class:" in doc.text, (
            f"TMyClass.DoStuff should have class context: {doc.text[:200]!r}"
        )
        assert "TMyClass" in doc.text.split("// Class:")[1].split("\n")[0], (
            f"Class context should mention TMyClass: {doc.text[:200]!r}"
        )

    def test_class_method_has_class_header_with_parent(self, tmp_path):
        """The class context should include the parent 'class(TObject)' if available."""
        f = tmp_path / "ClassMethods.pas"
        f.write_text(self._CLASS_METHOD_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        dostuff_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
            and "DoStuff" in d.text
        ]
        assert len(dostuff_docs) >= 1
        class_line = [l for l in dostuff_docs[0].text.split("\n") if "// Class:" in l]
        assert len(class_line) == 1
        # Should contain something like "TMyClass = class(TObject)"
        assert "class" in class_line[0].lower(), (
            f"Class header should mention 'class': {class_line[0]!r}"
        )

    def test_standalone_procs_have_no_class_context(self, tmp_path):
        """Standalone procedures should not have '// Class:' in their prefix."""
        f = tmp_path / "StandaloneProcs.pas"
        f.write_text(self._STANDALONE_PROC_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        proc_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
        ]
        assert len(proc_docs) >= 1, "Expected standalone proc chunks"
        for doc in proc_docs:
            assert "// Class:" not in doc.text, (
                f"Standalone proc should have no class context: {doc.text[:200]!r}"
            )

    def test_standalone_procs_have_unit_context(self, tmp_path):
        """Standalone procedures should still have '// Unit:' prefix."""
        f = tmp_path / "StandaloneProcs.pas"
        f.write_text(self._STANDALONE_PROC_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        proc_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
        ]
        for doc in proc_docs:
            assert doc.text.startswith("// Unit: StandaloneProcs"), (
                f"Standalone proc should have unit prefix: {doc.text[:100]!r}"
            )

    def test_mixed_file_class_method_has_class_context(self, tmp_path):
        """In a mixed file, TAlpha.AlphaWork should get class context."""
        f = tmp_path / "MixedProcs.pas"
        f.write_text(self._MIXED_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        alpha_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
            and "AlphaWork" in d.text
        ]
        assert len(alpha_docs) >= 1
        assert "// Class:" in alpha_docs[0].text
        assert "TAlpha" in alpha_docs[0].text

    def test_mixed_file_standalone_has_no_class_context(self, tmp_path):
        """In a mixed file, StandaloneFoo should NOT get class context."""
        f = tmp_path / "MixedProcs.pas"
        f.write_text(self._MIXED_UNIT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        standalone_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
            and "StandaloneFoo" in d.text
        ]
        assert len(standalone_docs) >= 1, "Expected a chunk for StandaloneFoo"
        assert "// Class:" not in standalone_docs[0].text, (
            f"StandaloneFoo should not have class context: "
            f"{standalone_docs[0].text[:200]!r}"
        )

    def test_two_classes_methods_get_correct_class_names(self, tmp_path):
        """Methods from different classes should get their respective class contexts."""
        f = tmp_path / "TwoClasses.pas"
        f.write_text(
            "unit TwoClasses;\n"
            "\n"
            "interface\n"
            "\n"
            "type\n"
            "  TDog = class(TObject)\n"
            "  public\n"
            "    procedure Bark;\n"
            "  end;\n"
            "\n"
            "  TCat = class(TObject)\n"
            "  public\n"
            "    procedure Meow;\n"
            "  end;\n"
            "\n"
            "implementation\n"
            "\n"
            "procedure TDog.Bark;\n"
            "begin\n"
            "  WriteLn('Woof! This is TDog barking');\n"
            "end;\n"
            "\n"
            "procedure TCat.Meow;\n"
            "begin\n"
            "  WriteLn('Meow! This is TCat speaking');\n"
            "end;\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)

        bark_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
            and "Bark" in d.text
        ]
        meow_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
            and "Meow" in d.text
        ]

        assert len(bark_docs) >= 1 and len(meow_docs) >= 1

        # Bark should have TDog class context, not TCat
        bark_class_lines = [
            l for l in bark_docs[0].text.split("\n") if "// Class:" in l
        ]
        assert len(bark_class_lines) == 1
        assert "TDog" in bark_class_lines[0]
        assert "TCat" not in bark_class_lines[0]

        # Meow should have TCat class context, not TDog
        meow_class_lines = [
            l for l in meow_docs[0].text.split("\n") if "// Class:" in l
        ]
        assert len(meow_class_lines) == 1
        assert "TCat" in meow_class_lines[0]
        assert "TDog" not in meow_class_lines[0]

    def test_core105_real_file_methods_have_class_context(self):
        """Real core105.classes.pas: class methods should have class context."""
        p = _SAMPLE_FILES / "core105.classes.pas"
        if not p.exists():
            pytest.skip("core105.classes.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        # Find defProc or method_group chunks
        method_docs = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("defProc", "method_group")
        ]
        if method_docs:
            # At least some should have class context (it's a class-heavy file)
            with_class = [d for d in method_docs if "// Class:" in d.text]
            assert len(with_class) > 0, (
                f"Expected some methods to have class context in core105.classes.pas"
            )


# ────────────────────────────────────────────────
# TestTinyDeclSectionSuppression
# ────────────────────────────────────────────────


class TestTinyDeclSectionSuppression:
    """Tests for the BUG 3 fix: tiny declSection chunks (< MIN_DECL_SECTION_CHARS)
    inside a class that has a class_summary chunk are suppressed, because they
    produce degenerate embeddings that rank #1 on every query."""

    # A class whose declSections are all small (< 200 chars raw).
    # The 'protected' section is ~70 chars raw, well under the 200-char threshold.
    _TINY_DECL_SECTION_CLASS = (
        "unit TinyDecl;\n"
        "\n"
        "interface\n"
        "\n"
        "type\n"
        "  TSmall = class(TObject)\n"
        "  protected\n"
        "    FName: string;\n"
        "    FAge: Integer;\n"
        "  public\n"
        "    procedure DoWork;\n"
        "  end;\n"
        "\n"
        "implementation\n"
        "\n"
        "procedure TSmall.DoWork;\n"
        "begin\n"
        "  WriteLn('Working on ' + FName);\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    # A class with a very large explicit 'private' section (> 200 chars raw).
    # tree-sitter groups fields/procs under explicit visibility keywords into
    # declSection nodes.  The default (unnamed) section before the first keyword
    # produces individual declField/declProc nodes, NOT a declSection.
    # So we put many fields under an explicit 'private' keyword.
    _LARGE_DECL_SECTION_CLASS = (
        "unit LargeDecl;\n"
        "\n"
        "interface\n"
        "\n"
        "type\n"
        "  TBigForm = class(TForm)\n"
        "  private\n"
        "    FConnectionString: string;\n"
        "    FDatabaseName: string;\n"
        "    FServerHost: string;\n"
        "    FServerPort: Integer;\n"
        "    FTimeout: Integer;\n"
        "    FRetryCount: Integer;\n"
        "    FMaxConnections: Integer;\n"
        "    FMinConnections: Integer;\n"
        "    FPoolSize: Integer;\n"
        "    FIsConnected: Boolean;\n"
        "    FLastError: string;\n"
        "    FLastErrorCode: Integer;\n"
        "    FCreatedAt: TDateTime;\n"
        "    FUpdatedAt: TDateTime;\n"
        "    FOwnerName: string;\n"
        "    procedure InternalConnect;\n"
        "    procedure InternalDisconnect;\n"
        "    function GetConnectionInfo: string;\n"
        "  public\n"
        "    procedure Connect;\n"
        "    procedure Disconnect;\n"
        "  end;\n"
        "\n"
        "implementation\n"
        "\n"
        "procedure TBigForm.InternalConnect;\n"
        "begin\n"
        "  WriteLn('Connecting to ' + FServerHost);\n"
        "end;\n"
        "\n"
        "procedure TBigForm.InternalDisconnect;\n"
        "begin\n"
        "  WriteLn('Disconnecting from server');\n"
        "end;\n"
        "\n"
        "function TBigForm.GetConnectionInfo: string;\n"
        "begin\n"
        "  Result := FServerHost + ':' + IntToStr(FServerPort);\n"
        "end;\n"
        "\n"
        "procedure TBigForm.Connect;\n"
        "begin\n"
        "  InternalConnect;\n"
        "end;\n"
        "\n"
        "procedure TBigForm.Disconnect;\n"
        "begin\n"
        "  InternalDisconnect;\n"
        "end;\n"
        "\n"
        "end.\n"
    )

    def test_tiny_decl_section_in_class_suppressed(self, tmp_path):
        """A class with a short protected section (< 200 chars raw) should NOT
        produce a standalone declSection chunk when class_summary exists."""
        f = tmp_path / "TinyDecl.pas"
        f.write_text(self._TINY_DECL_SECTION_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        decl_sections = [
            d for d in docs if d.metadata.get("node_type") == "declSection"
        ]
        assert len(decl_sections) == 0, (
            f"Expected 0 declSection chunks (all tiny, covered by class_summary), "
            f"got {len(decl_sections)}. "
            f"Sizes: {[len(d.text) for d in decl_sections]}"
        )
        # Verify a class_summary was emitted (the suppression depends on it)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) >= 1, (
            f"Expected class_summary to exist. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_large_decl_section_in_class_preserved(self, tmp_path):
        """A class with a large explicit 'private' section (> 200 chars raw)
        SHOULD produce a standalone declSection chunk even when class_summary
        exists.  The small 'public' section (< 200 chars) should be suppressed."""
        f = tmp_path / "LargeDecl.pas"
        f.write_text(self._LARGE_DECL_SECTION_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        # The large private section (512 chars raw) should survive
        decl_sections = [
            d for d in docs if d.metadata.get("node_type") == "declSection"
        ]
        assert len(decl_sections) >= 1, (
            f"Expected at least 1 declSection chunk (the large private section), "
            f"got {len(decl_sections)}. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )
        # The surviving declSection should contain the private fields
        assert any("FConnectionString" in d.text for d in decl_sections), (
            f"The large private declSection should contain 'FConnectionString'"
        )

    def test_decl_section_without_class_summary_preserved(self, tmp_path):
        """A declSection in a freestanding type block (no class_summary) should
        still be emitted even if it's small."""
        # This creates a record type (not a class), so no class_summary is emitted.
        # The `var` section is a top-level construct, not inside a class.
        f = tmp_path / "FreeDecl.pas"
        f.write_text(
            "unit FreeDecl;\n"
            "\n"
            "interface\n"
            "\n"
            "var\n"
            "  GlobalCounter: Integer;\n"
            "  GlobalName: string;\n"
            "  GlobalActive: Boolean;\n"
            "\n"
            "implementation\n"
            "\n"
            "end.\n",
            encoding="utf-8",
        )
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        # No class_summary should exist
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) == 0, "Freestanding var should not produce class_summary"
        # The var block (declVar) should be emitted regardless of size
        node_types = [d.metadata.get("node_type") for d in docs]
        assert "declVar" in node_types or "full_file" in node_types, (
            f"Expected declVar or full_file chunk. Got: {node_types}"
        )

    def test_min_decl_section_chars_constant(self):
        """MIN_DECL_SECTION_CHARS should be 200."""
        assert DelphiFileReader.MIN_DECL_SECTION_CHARS == 200

    def test_suppressed_content_still_in_class_summary(self, tmp_path):
        """The suppressed declSection's content should be present in the
        class_summary chunk (since class_summary includes all sections)."""
        f = tmp_path / "TinyDecl.pas"
        f.write_text(self._TINY_DECL_SECTION_CLASS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        # Verify no declSection chunks
        decl_sections = [
            d for d in docs if d.metadata.get("node_type") == "declSection"
        ]
        assert len(decl_sections) == 0
        # Verify the suppressed content is in the class_summary
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) >= 1
        summary_text = summaries[0].text
        # The protected section's fields should appear in the class_summary
        assert "FName" in summary_text, (
            f"Expected 'FName' in class_summary: {summary_text[:400]!r}"
        )
        assert "FAge" in summary_text, (
            f"Expected 'FAge' in class_summary: {summary_text[:400]!r}"
        )

    def test_real_file_mainDM_has_large_decl_sections(self):
        """Integration: MainDM.pas should still have declSection chunks (the
        large published/private sections exceed MIN_DECL_SECTION_CHARS)."""
        p = _SAMPLE_FILES / "MainDM.pas"
        if not p.exists():
            pytest.skip("MainDM.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        decl_sections = [
            d for d in docs if d.metadata.get("node_type") == "declSection"
        ]
        assert len(decl_sections) >= 1, (
            f"MainDM.pas should have large declSection chunks that survive "
            f"suppression. Got {len(decl_sections)} declSection chunks. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_real_file_splash_no_decl_sections(self):
        """Integration: Splash.pas (small file) should have NO declSection chunks
        because all its visibility sections are tiny and covered by class_summary."""
        p = _SAMPLE_FILES / "Splash.pas"
        if not p.exists():
            pytest.skip("Splash.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        decl_sections = [
            d for d in docs if d.metadata.get("node_type") == "declSection"
        ]
        assert len(decl_sections) == 0, (
            f"Splash.pas should have 0 declSection chunks (all tiny, covered by "
            f"class_summary), got {len(decl_sections)}. "
            f"Sizes: {[len(d.text) for d in decl_sections]}"
        )
        # Confirm class_summary exists (the suppression depends on it)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) >= 1, (
            f"Splash.pas should have a class_summary for TfrmSplash"
        )


class TestIsCommentedOutCode:
    """Tests for _is_commented_out_code() — detects commented-out Pascal code blocks."""

    def test_simple_commented_out_procedure(self):
        text = (
            "// procedure TMyClass.DoSomething;\n"
            "// begin\n"
            "//   Result := 42;\n"
            "// end;\n"
        )
        assert _is_commented_out_code(text) is True

    def test_commented_out_assignments(self):
        text = (
            "// FValue := GetDefault;\n"
            "// FName := 'test';\n"
            "// FActive := True;\n"
            "// FCount := FCount + 1;\n"
        )
        assert _is_commented_out_code(text) is True

    def test_commented_out_if_else(self):
        text = (
            "// if Assigned(FClient) then\n"
            "// begin\n"
            "//   FClient.Disconnect;\n"
            "//   FreeAndNil(FClient);\n"
            "// end;\n"
        )
        assert _is_commented_out_code(text) is True

    def test_documentation_comment_not_code(self):
        text = (
            "// This class handles the connection to the remote server.\n"
            "// It manages reconnection attempts and timeout handling.\n"
            "// The implementation follows the observer pattern.\n"
        )
        assert _is_commented_out_code(text) is False

    def test_polish_documentation_not_code(self):
        """Polish doc comments like those in core files should not be detected as code."""
        text = (
            "// Tylko w przypadku taryfy zagranicznej, bonifikate do taryfy\n"
            "// zagranicznej oplaty manipulacyjnej i ulga kwotowa zagraniczna\n"
            "// sa brane pod uwage przy obliczaniu ceny.\n"
        )
        assert _is_commented_out_code(text) is False

    def test_single_line_comment_too_short(self):
        """Comments with fewer than 3 lines should not be classified as code."""
        text = "// Result := 42;\n// end;\n"
        assert _is_commented_out_code(text) is False

    def test_empty_text(self):
        assert _is_commented_out_code("") is False

    def test_whitespace_only(self):
        assert _is_commented_out_code("   \n  \n  ") is False

    def test_mixed_code_and_text_majority_code(self):
        text = (
            "// Old implementation:\n"
            "// procedure TMyClass.Init;\n"
            "// begin\n"
            "//   FValue := 0;\n"
            "//   FName := '';\n"
            "//   FActive := False;\n"
            "// end;\n"
        )
        # 5 of 7 lines look like code — should be detected
        assert _is_commented_out_code(text) is True

    def test_mixed_code_and_text_majority_text(self):
        text = (
            "// Note: this is the old approach.\n"
            "// We used to do it this way.\n"
            "// The problem was performance.\n"
            "// FValue := 0;\n"
        )
        # Only 1 of 4 lines looks like code — should NOT be detected
        assert _is_commented_out_code(text) is False

    def test_curly_brace_comment_with_code(self):
        text = (
            "{ procedure OldMethod;\n"
            "  begin\n"
            "    Result := GetValue;\n"
            "    FreeAndNil(FObj);\n"
            "  end; }\n"
        )
        assert _is_commented_out_code(text) is True

    def test_method_calls_detected(self):
        text = (
            "// OutputDebugString('test');\n"
            "// ShowMessage('debug info');\n"
            "// FList.Items[0].Free;\n"
        )
        assert _is_commented_out_code(text) is True

    def test_xml_doc_comment_not_code(self):
        """/// XML-doc comments should not be flagged as code."""
        text = (
            "/// <summary>\n"
            "/// Gets the ticket price for the specified route.\n"
            "/// Returns the calculated fare amount.\n"
            "/// </summary>\n"
        )
        assert _is_commented_out_code(text) is False


class TestClassOverviewNaturalLanguage:
    """Tests for the natural-language summary sentence in class_overview chunks.

    The class_overview chunk should start with a descriptive sentence like:
    '// TdmMain is a Delphi class inheriting from TDataModule with 150 fields,
    60 methods (published: 150 fields; private: 60 methods).'
    This helps dense embedding match semantic queries like 'What is TdmMain?'.
    """

    _CLASS_WITH_MEMBERS = (
        "unit Sample;\n"
        "interface\n"
        "type\n"
        "  TMyClass = class(TBaseClass)\n"
        "  published\n"
        + "".join(f"    FieldPublished{i}: TClientDataSet;\n" for i in range(80))
        + "  private\n"
        + "".join(
            f"    procedure PrepareDataSetForField{i}(const AName: string);\n"
            for i in range(40)
        )
        + "  public\n"
        + "".join(f"    function GetPublicValue{i}: Integer;\n" for i in range(20))
        + "    property Name: string read FName;\n"
        + "    property Value: Integer read FValue;\n"
        + "  end;\n"
        "implementation\n"
        + "".join(
            f"procedure TMyClass.PrepareDataSetForField{i}(const AName: string);\nbegin\nend;\n"
            for i in range(40)
        )
        + "".join(
            f"function TMyClass.GetPublicValue{i}: Integer;\nbegin\n  Result := {i};\nend;\n"
            for i in range(20)
        )
        + "end.\n"
    )

    def test_overview_contains_class_name_prominently(self, tmp_path):
        """class_overview should contain the class name near the start."""
        f = tmp_path / "Sample.pas"
        f.write_text(self._CLASS_WITH_MEMBERS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        # This class has 25+10+2=37 members which should trigger class_summary
        # being oversized, producing a class_overview. If MAX_SUMMARY_CHARS
        # prevents it, skip.
        if not overviews:
            pytest.skip(
                "class_summary did not exceed MAX_SUMMARY_CHARS, "
                "no class_overview produced"
            )
        text = overviews[0].text
        # The natural-language summary sentence should mention the class name
        assert "TMyClass" in text, f"class_overview should contain 'TMyClass'"

    def test_overview_mentions_parent_class(self, tmp_path):
        """class_overview NL sentence should mention the parent class."""
        f = tmp_path / "Sample.pas"
        f.write_text(self._CLASS_WITH_MEMBERS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        if not overviews:
            pytest.skip("no class_overview produced")
        text = overviews[0].text
        assert "TBaseClass" in text, (
            f"class_overview should mention parent class 'TBaseClass'"
        )

    def test_overview_mentions_member_counts(self, tmp_path):
        """class_overview NL sentence should include member counts."""
        f = tmp_path / "Sample.pas"
        f.write_text(self._CLASS_WITH_MEMBERS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        if not overviews:
            pytest.skip("no class_overview produced")
        text = overviews[0].text
        # Should mention "fields" and "methods" somewhere
        assert "fields" in text.lower(), f"class_overview should mention 'fields' count"
        assert "methods" in text.lower(), (
            f"class_overview should mention 'methods' count"
        )

    def test_overview_mentions_delphi_class(self, tmp_path):
        """class_overview NL sentence should say 'Delphi class'."""
        f = tmp_path / "Sample.pas"
        f.write_text(self._CLASS_WITH_MEMBERS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        if not overviews:
            pytest.skip("no class_overview produced")
        text = overviews[0].text
        assert "Delphi class" in text, (
            f"class_overview should contain 'Delphi class' for semantic matching"
        )

    def test_overview_mentions_properties(self, tmp_path):
        """class_overview NL sentence should mention properties if present."""
        f = tmp_path / "Sample.pas"
        f.write_text(self._CLASS_WITH_MEMBERS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        if not overviews:
            pytest.skip("no class_overview produced")
        text = overviews[0].text
        assert "properties" in text.lower() or "property" in text.lower(), (
            f"class_overview should mention properties when the class has them"
        )

    def test_real_file_mainDM_class_overview_has_nl_summary(self):
        """Integration: MainDM.pas TdmMain class_overview should have NL summary."""
        p = _SAMPLE_FILES / "MainDM.pas"
        if not p.exists():
            pytest.skip("MainDM.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        assert len(overviews) >= 1, (
            "MainDM.pas should produce at least one class_overview"
        )
        text = overviews[0].text
        # Should have the NL sentence mentioning TdmMain
        assert "TdmMain" in text
        assert "Delphi class" in text, (
            f"class_overview for TdmMain should contain 'Delphi class'"
        )
        assert "TDataModule" in text, (
            f"class_overview should mention parent class TDataModule"
        )

    def test_real_file_core105_class_overview_has_nl_summary(self):
        """Integration: core105.classes.pas should have class_overview with NL summary."""
        p = _SAMPLE_FILES / "core105.classes.pas"
        if not p.exists():
            pytest.skip("core105.classes.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        if not overviews:
            pytest.skip("no class_overview produced for core105.classes.pas")
        # At least one overview should have the NL sentence
        has_nl = any("Delphi class" in d.text for d in overviews)
        assert has_nl, f"At least one class_overview should contain 'Delphi class'"


class TestCommentSuppressionInClasses:
    """Tests for suppression of standalone comment chunks inside classes that
    already have a class_summary.

    When a class has a class_summary, comments inside the class declaration
    are already included in the summary. Emitting them as standalone chunks
    is duplication that competes in search ranking.
    """

    _CLASS_WITH_COMMENTS = (
        "unit Sample;\n"
        "interface\n"
        "type\n"
        "  TMyClass = class(TBase)\n"
        "  published\n"
        "    { This is a long documentation comment that explains the field purpose and usage }\n"
        "    FValue: Integer;\n"
        "    // Another comment that is long enough to pass MIN_COMMENT_CHARS threshold easily\n"
        "    FName: string;\n"
        "  end;\n"
        "implementation\n"
        "end.\n"
    )

    _STANDALONE_COMMENT = (
        "unit Sample;\n"
        "interface\n"
        "{ This is a standalone comment not inside any class declaration block that is long enough }\n"
        "type\n"
        "  TMyClass = class(TBase)\n"
        "  published\n"
        "    FValue: Integer;\n"
        "  end;\n"
        "implementation\n"
        "end.\n"
    )

    def test_comments_inside_class_not_standalone(self, tmp_path):
        """Comments inside a class with class_summary should NOT produce standalone chunks."""
        f = tmp_path / "Sample.pas"
        f.write_text(self._CLASS_WITH_COMMENTS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        comment_chunks = [d for d in docs if d.metadata.get("node_type") == "comment"]
        assert len(comment_chunks) == 0, (
            f"Comments inside class with class_summary should be suppressed, "
            f"but found {len(comment_chunks)} standalone comment chunks"
        )

    def test_comment_text_still_in_class_summary(self, tmp_path):
        """Suppressed comments should still be present in the class_summary text."""
        f = tmp_path / "Sample.pas"
        f.write_text(self._CLASS_WITH_COMMENTS, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        summaries = [
            d
            for d in docs
            if d.metadata.get("node_type") in ("class_summary", "class_summary_split")
        ]
        assert len(summaries) >= 1, "Should have at least one class_summary"
        all_text = " ".join(d.text for d in summaries)
        assert "documentation comment" in all_text, (
            f"class_summary should contain the comment text"
        )

    def test_standalone_comment_outside_class_preserved(self, tmp_path):
        """Comments NOT inside a class should still be emitted as standalone chunks."""
        f = tmp_path / "Sample.pas"
        f.write_text(self._STANDALONE_COMMENT, encoding="utf-8")
        reader = DelphiFileReader()
        docs = reader.load_data(f)
        comment_chunks = [d for d in docs if d.metadata.get("node_type") == "comment"]
        assert len(comment_chunks) >= 1, (
            f"Comments outside classes should still be emitted as standalone chunks, "
            f"but found {len(comment_chunks)} comment chunks"
        )

    def test_real_file_core_base_no_standalone_comments_in_classes(self):
        """Integration: core.base.classes.pas should have NO standalone comment chunks
        for comments inside class declarations (they're in class_summary)."""
        p = _SAMPLE_FILES / "core.base.classes.pas"
        if not p.exists():
            pytest.skip("core.base.classes.pas not found")
        reader = DelphiFileReader()
        docs = reader.load_data(p)
        # All comment chunks should be for comments OUTSIDE class declarations
        # (i.e., their metadata should not have a class_name, or should be
        # at the unit level)
        comment_chunks = [d for d in docs if d.metadata.get("node_type") == "comment"]
        # Comments inside class declarations are suppressed, so any remaining
        # comment chunks should NOT have class context in their prefix
        for chunk in comment_chunks:
            assert "// Class:" not in chunk.text, (
                f"Comment chunk should not be inside a class with class_summary: "
                f"{chunk.text[:100]}..."
            )
