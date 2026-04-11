"""
Tests for shared/readers/dfm_reader.py — Delphi .dfm file reader with depth-aware parsing.

Tests cover:
    - _strip_binary_data(): binary hex block removal, placeholder preservation
    - _parse_dfm_tree(): tree parsing, depth tracking, object/inherited keywords
    - _form_header_lines(): form header extraction
    - _context_prefix(): context comment generation
    - _group_small_siblings(): grouping logic for small same-type objects
    - DFMFileReader.load_data(): full integration tests against real test files
    - Bug D1 fix: nesting-aware end detection
    - Bug D1b fix: inherited keyword support
    - Edge cases: empty files, no objects, single object, deeply nested
    - Metadata correctness on all document types
    - MIN_CHUNK_SIZE filtering
    - Grouping of small same-type objects (MainDM pattern)
"""

from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from shared.readers.dfm_reader import (
    _strip_binary_data,
    _parse_dfm_tree,
    _form_header_lines,
    _context_prefix,
    _group_small_siblings,
    DFMFileReader,
    DFMObject,
    MIN_CHUNK_SIZE,
    MAX_GROUP_CHARS,
    SMALL_OBJECT_CHARS,
)
from llama_index.core import Document


# Path to real sample files
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLE_FILES = _PROJECT_ROOT / "test_sources"


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_simple_dfm(objects_count: int = 3) -> str:
    """Build a simple flat DFM with N child objects."""
    lines = ["object frmTest: TfrmTest", "  Caption = 'Test'"]
    for i in range(objects_count):
        lines.extend(
            [
                f"  object Button{i}: TButton",
                f"    Left = {i * 100}",
                f"    Top = 10",
                f"    Caption = 'Button{i}'",
                "  end",
            ]
        )
    lines.append("end")
    return "\n".join(lines)


def _make_nested_dfm() -> str:
    """Build a DFM with nested objects (depth 3)."""
    return "\n".join(
        [
            "object frmMain: TfrmMain",
            "  Caption = 'Main'",
            "  object Panel1: TPanel",
            "    Left = 0",
            "    object Toolbar1: TToolBar",
            "      Left = 0",
            "      object btn1: TToolButton",
            "        Left = 0",
            "      end",
            "      object btn2: TToolButton",
            "        Left = 23",
            "      end",
            "    end",
            "    object ListView1: TListView",
            "      Left = 0",
            "    end",
            "  end",
            "  object StatusBar1: TStatusBar",
            "    Left = 0",
            "  end",
            "end",
        ]
    )


def _make_inherited_dfm() -> str:
    """Build a DFM using 'inherited' keyword at root and child levels."""
    return "\n".join(
        [
            "inherited frmChild: TfrmChild",
            "  Caption = 'Child Form'",
            "  inherited Panel1: TPanel",
            "    Left = 10",
            "  end",
            "  object NewButton: TButton",
            "    Left = 20",
            "  end",
            "end",
        ]
    )


# ────────────────────────────────────────────────
# TestStripBinaryData
# ────────────────────────────────────────────────


class TestStripBinaryData:
    """Tests for _strip_binary_data() — binary hex block removal."""

    def test_no_binary_data(self):
        """Content without binary blocks passes through unchanged."""
        content = "object frmTest: TfrmTest\n  Left = 0\nend"
        assert _strip_binary_data(content) == content

    def test_single_binary_block(self):
        """Single binary block is replaced with placeholder."""
        content = (
            "  Picture.Data = {\n"
            "    0A544A504547496D\n"
            "    480000FFE1009045}\n"
            "  Left = 0"
        )
        result = _strip_binary_data(content)
        assert "{<binary data removed>}" in result
        assert "0A544A504547496D" not in result
        assert "Left = 0" in result

    def test_multiple_binary_blocks(self):
        """Multiple binary blocks are all replaced."""
        content = (
            "  Bitmap = {\n    AABB}\n"
            "  Left = 0\n"
            "  Glyph.Data = {\n    CCDD\n    EEFF}\n"
            "  Top = 10"
        )
        result = _strip_binary_data(content)
        assert result.count("{<binary data removed>}") == 2
        assert "Left = 0" in result
        assert "Top = 10" in result

    def test_preserves_property_name(self):
        """The property name before the binary block is preserved."""
        content = "  Picture.Data = {\n    AABBCCDD}\n"
        result = _strip_binary_data(content)
        assert "Picture.Data = {<binary data removed>}" in result

    def test_inline_braces_not_matched(self):
        """Inline braces (like Filters={}) should not trigger binary removal."""
        content = "  Filters = 'Name={*}'\n  Left = 0"
        result = _strip_binary_data(content)
        # Should pass through unchanged since the regex requires the line
        # to end with just { after the =
        assert "Filters = 'Name={*}'" in result


# ────────────────────────────────────────────────
# TestParseDfmTree
# ────────────────────────────────────────────────


class TestParseDfmTree:
    """Tests for _parse_dfm_tree() — DFM tree construction."""

    def test_empty_lines_returns_none(self):
        """Empty input returns None."""
        assert _parse_dfm_tree([]) is None

    def test_no_object_lines_returns_none(self):
        """Lines without object/inherited returns None."""
        lines = ["  Left = 0", "  Top = 10"]
        assert _parse_dfm_tree(lines) is None

    def test_simple_root_only(self):
        """Root object with properties only, no children."""
        lines = [
            "object frmTest: TfrmTest",
            "  Left = 0",
            "  Top = 0",
            "end",
        ]
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert root.name == "frmTest"
        assert root.obj_type == "TfrmTest"
        assert root.children == []
        assert root.start_line == 0
        assert root.end_line == 3

    def test_flat_children(self):
        """Root with flat (non-nested) children."""
        content = _make_simple_dfm(3)
        lines = content.split("\n")
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert len(root.children) == 3
        assert root.children[0].name == "Button0"
        assert root.children[1].name == "Button1"
        assert root.children[2].name == "Button2"

    def test_nested_children_depth_tracking(self):
        """Nested objects are correctly tracked as children of their parents."""
        content = _make_nested_dfm()
        lines = content.split("\n")
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert root.name == "frmMain"
        # 2 depth-1 children: Panel1 and StatusBar1
        assert len(root.children) == 2
        panel = root.children[0]
        assert panel.name == "Panel1"
        assert panel.obj_type == "TPanel"
        # Panel has 2 depth-2 children: Toolbar1 and ListView1
        assert len(panel.children) == 2
        toolbar = panel.children[0]
        assert toolbar.name == "Toolbar1"
        # Toolbar has 2 depth-3 children: btn1 and btn2
        assert len(toolbar.children) == 2
        assert toolbar.children[0].name == "btn1"
        assert toolbar.children[1].name == "btn2"

    def test_inherited_keyword_parsed(self):
        """'inherited' keyword is handled identically to 'object'."""
        content = _make_inherited_dfm()
        lines = content.split("\n")
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert root.name == "frmChild"
        assert root.obj_type == "TfrmChild"
        # 2 children: inherited Panel1 and object NewButton
        assert len(root.children) == 2
        assert root.children[0].name == "Panel1"
        assert root.children[1].name == "NewButton"

    def test_index_notation_stripped_from_type(self):
        """Object type with [N] index notation is cleaned."""
        lines = [
            "object frmTest: TfrmTest",
            "  object Panel1: TPanel [0]",
            "    Left = 0",
            "  end",
            "end",
        ]
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert root.children[0].obj_type == "TPanel"

    def test_end_detection_respects_nesting(self):
        """Bug D1: 'end' at inner depth should not close outer object."""
        content = _make_nested_dfm()
        lines = content.split("\n")
        root = _parse_dfm_tree(lines)
        panel = root.children[0]
        # Panel should include ALL nested content up to its own 'end'
        assert "TToolBar" in panel.text
        assert "TToolButton" in panel.text
        assert "btn1" in panel.text
        assert "btn2" in panel.text

    def test_object_text_includes_full_block(self):
        """Each object's text includes everything from 'object' to 'end'."""
        lines = [
            "object frmTest: TfrmTest",
            "  object Btn: TButton",
            "    Left = 10",
            "    Caption = 'Click'",
            "  end",
            "end",
        ]
        root = _parse_dfm_tree(lines)
        btn = root.children[0]
        assert btn.text.startswith("  object Btn: TButton")
        assert "Left = 10" in btn.text
        assert "Caption = 'Click'" in btn.text
        assert btn.text.strip().endswith("end")


# ────────────────────────────────────────────────
# TestFormHeaderLines
# ────────────────────────────────────────────────


class TestFormHeaderLines:
    """Tests for _form_header_lines() — form header extraction."""

    def test_header_includes_root_declaration(self):
        """Header should start with the root object declaration."""
        content = _make_simple_dfm(1)
        lines = content.split("\n")
        root = _parse_dfm_tree(lines)
        header = _form_header_lines(root, lines)
        assert header[0] == "object frmTest: TfrmTest"

    def test_header_includes_properties(self):
        """Header should include form-level properties."""
        content = _make_simple_dfm(1)
        lines = content.split("\n")
        root = _parse_dfm_tree(lines)
        header = _form_header_lines(root, lines)
        assert any("Caption" in line for line in header)

    def test_header_excludes_child_objects(self):
        """Header should stop before the first child object."""
        content = _make_simple_dfm(3)
        lines = content.split("\n")
        root = _parse_dfm_tree(lines)
        header = _form_header_lines(root, lines)
        combined = "\n".join(header)
        assert "TButton" not in combined

    def test_header_root_with_no_properties(self):
        """Root with no properties before children gives just declaration."""
        content = "object frmEmpty: TfrmEmpty\n  object Btn: TButton\n    Left = 0\n  end\nend"
        lines = content.split("\n")
        root = _parse_dfm_tree(lines)
        header = _form_header_lines(root, lines)
        assert len(header) == 1
        assert header[0] == "object frmEmpty: TfrmEmpty"


# ────────────────────────────────────────────────
# TestContextPrefix
# ────────────────────────────────────────────────


class TestContextPrefix:
    """Tests for _context_prefix() — context comment generation."""

    def test_format(self):
        """Prefix should follow the expected format."""
        result = _context_prefix("Splash.dfm", "frmSplash", "TfrmSplash")
        assert result == "// Form: TfrmSplash (Splash.dfm)"

    def test_includes_file_name(self):
        """Prefix should contain the file name."""
        result = _context_prefix("MyForm.dfm", "frmMy", "TfrmMy")
        assert "MyForm.dfm" in result

    def test_includes_form_type(self):
        """Prefix should contain the form type."""
        result = _context_prefix("Test.dfm", "frmTest", "TfrmTest")
        assert "TfrmTest" in result


# ────────────────────────────────────────────────
# TestGroupSmallSiblings
# ────────────────────────────────────────────────


class TestGroupSmallSiblings:
    """Tests for _group_small_siblings() — grouping consecutive small same-type objects."""

    def _make_obj(self, name: str, obj_type: str, char_count: int) -> DFMObject:
        """Create a DFMObject with controlled char count."""
        # Build lines that produce approximately the desired char count
        text = "x" * max(char_count - 1, 1)
        return DFMObject(
            name=name,
            obj_type=obj_type,
            start_line=0,
            end_line=0,
            lines=[text],
        )

    def test_empty_input(self):
        """Empty list produces empty groups."""
        assert _group_small_siblings([]) == []

    def test_single_large_object(self):
        """A single large object becomes a solo group."""
        obj = self._make_obj("Panel1", "TPanel", 1000)
        groups = _group_small_siblings([obj])
        assert len(groups) == 1
        assert len(groups[0]) == 1
        assert groups[0][0].name == "Panel1"

    def test_consecutive_small_same_type_grouped(self):
        """Consecutive small objects of same type are grouped."""
        objs = [self._make_obj(f"cds{i}", "TClientDataSet", 100) for i in range(5)]
        groups = _group_small_siblings(objs)
        assert len(groups) == 1
        assert len(groups[0]) == 5

    def test_different_types_not_grouped(self):
        """Small objects of different types become separate groups."""
        objs = [
            self._make_obj("btn1", "TButton", 100),
            self._make_obj("lbl1", "TLabel", 100),
            self._make_obj("btn2", "TButton", 100),
        ]
        groups = _group_small_siblings(objs)
        assert len(groups) == 3

    def test_group_split_at_max_chars(self):
        """Groups are split when they exceed MAX_GROUP_CHARS."""
        # Each object ~450 chars, so ~8 fit in 4000 chars
        objs = [self._make_obj(f"cds{i}", "TClientDataSet", 450) for i in range(20)]
        groups = _group_small_siblings(objs)
        # Should be multiple groups, each <= MAX_GROUP_CHARS
        assert len(groups) > 1
        for group in groups:
            total = sum(o.char_count for o in group)
            assert total <= MAX_GROUP_CHARS

    def test_large_object_breaks_grouping(self):
        """A large object in the middle breaks the sequence."""
        objs = [
            self._make_obj("cds1", "TClientDataSet", 100),
            self._make_obj("cds2", "TClientDataSet", 100),
            self._make_obj("Panel1", "TPanel", 1000),
            self._make_obj("cds3", "TClientDataSet", 100),
            self._make_obj("cds4", "TClientDataSet", 100),
        ]
        groups = _group_small_siblings(objs)
        assert len(groups) == 3
        assert len(groups[0]) == 2  # cds1, cds2
        assert len(groups[1]) == 1  # Panel1 (large)
        assert len(groups[2]) == 2  # cds3, cds4


# ────────────────────────────────────────────────
# TestDFMFileReaderLoadData
# ────────────────────────────────────────────────


class TestDFMFileReaderLoadData:
    """Tests for DFMFileReader.load_data() — full document generation."""

    def setup_method(self):
        self.reader = DFMFileReader()

    def test_empty_file_returns_empty(self, tmp_path):
        """Empty file returns no documents."""
        f = tmp_path / "empty.dfm"
        f.write_text("", encoding="utf-8")
        docs = self.reader.load_data(f)
        assert docs == []

    def test_whitespace_only_file_returns_empty(self, tmp_path):
        """File with only whitespace returns no documents."""
        f = tmp_path / "blank.dfm"
        f.write_text("   \n\n  \n", encoding="utf-8")
        docs = self.reader.load_data(f)
        assert docs == []

    def test_nonexistent_file_returns_empty(self, tmp_path):
        """Non-existent file returns empty list."""
        f = tmp_path / "missing.dfm"
        docs = self.reader.load_data(f)
        assert docs == []

    def test_unparseable_content_returns_full_file(self, tmp_path):
        """Content without any object declarations falls back to full_file."""
        f = tmp_path / "noobj.dfm"
        f.write_text("Left = 0\nTop = 10\nCaption = 'test'\n")
        docs = self.reader.load_data(f)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"

    def test_simple_flat_produces_header_plus_children(self, tmp_path):
        """Simple flat DFM produces a form header + one doc per child."""
        f = tmp_path / "flat.dfm"
        f.write_text(_make_simple_dfm(3), encoding="utf-8")
        docs = self.reader.load_data(f)
        # 1 header + 3 children (each button is small but they're all
        # TButton so they may get grouped)
        node_types = [d.metadata["node_type"] for d in docs]
        assert "dfm_form_header" in node_types
        # Either 3 individual dfm_object docs or grouped
        non_header = [d for d in docs if d.metadata["node_type"] != "dfm_form_header"]
        assert len(non_header) >= 1

    def test_nested_objects_stay_with_parent(self, tmp_path):
        """Nested objects are included in their depth-1 parent's chunk."""
        f = tmp_path / "nested.dfm"
        f.write_text(_make_nested_dfm(), encoding="utf-8")
        docs = self.reader.load_data(f)

        # Find the Panel1 chunk
        panel_docs = [d for d in docs if d.metadata.get("object_name") == "Panel1"]
        assert len(panel_docs) == 1
        panel_text = panel_docs[0].text
        # Panel chunk should contain all nested children
        assert "TToolBar" in panel_text
        assert "btn1" in panel_text
        assert "btn2" in panel_text
        assert "TListView" in panel_text

    def test_inherited_keyword_handled(self, tmp_path):
        """DFM files using 'inherited' keyword are parsed correctly."""
        f = tmp_path / "inherited.dfm"
        f.write_text(_make_inherited_dfm(), encoding="utf-8")
        docs = self.reader.load_data(f)

        assert len(docs) >= 2  # header + at least 1 child doc
        header = [d for d in docs if d.metadata["node_type"] == "dfm_form_header"]
        assert len(header) == 1
        assert header[0].metadata["form_type"] == "TfrmChild"

    def test_context_prefix_in_all_chunks(self, tmp_path):
        """Every chunk should start with the context prefix comment."""
        f = tmp_path / "test.dfm"
        f.write_text(_make_nested_dfm(), encoding="utf-8")
        docs = self.reader.load_data(f)

        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert doc.text.startswith("// Form:")

    def test_metadata_has_form_info(self, tmp_path):
        """All non-fallback documents should have form_name and form_type."""
        f = tmp_path / "test.dfm"
        f.write_text(_make_simple_dfm(2), encoding="utf-8")
        docs = self.reader.load_data(f)

        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert "form_name" in doc.metadata
                assert "form_type" in doc.metadata
                assert doc.metadata["form_name"] == "frmTest"
                assert doc.metadata["form_type"] == "TfrmTest"

    def test_metadata_has_file_path(self, tmp_path):
        """All documents should have file_path metadata."""
        f = tmp_path / "test.dfm"
        f.write_text(_make_simple_dfm(1), encoding="utf-8")
        docs = self.reader.load_data(f)
        for doc in docs:
            assert "file_path" in doc.metadata
            assert str(f) in doc.metadata["file_path"]

    def test_metadata_has_datetime(self, tmp_path):
        """All documents should have creation/modification datetime."""
        f = tmp_path / "test.dfm"
        f.write_text(_make_simple_dfm(1), encoding="utf-8")
        docs = self.reader.load_data(f)
        for doc in docs:
            assert "creation_datetime" in doc.metadata
            assert "modification_datetime" in doc.metadata

    def test_metadata_has_line_numbers(self, tmp_path):
        """Documents should have start_line and end_line metadata."""
        f = tmp_path / "test.dfm"
        f.write_text(_make_nested_dfm(), encoding="utf-8")
        docs = self.reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert "start_line" in doc.metadata
                assert "end_line" in doc.metadata
                assert doc.metadata["start_line"] >= 1
                assert doc.metadata["end_line"] >= doc.metadata["start_line"]


# ────────────────────────────────────────────────
# TestGroupingBehavior
# ────────────────────────────────────────────────


class TestGroupingBehavior:
    """Tests for small object grouping in the reader."""

    def setup_method(self):
        self.reader = DFMFileReader()

    def test_many_small_same_type_grouped(self, tmp_path):
        """Many small same-type objects are grouped into fewer chunks."""
        # Build a DFM with 20 small TClientDataSet objects
        lines = ["object dmMain: TdmMain", "  OldCreateOrder = False"]
        for i in range(20):
            lines.extend(
                [
                    f"  object cds{i}: TClientDataSet",
                    f"    Tag = {i}",
                    "    Aggregates = <>",
                    "    Params = <>",
                    "  end",
                ]
            )
        lines.append("end")

        f = tmp_path / "data.dfm"
        f.write_text("\n".join(lines), encoding="utf-8")
        docs = self.reader.load_data(f)

        # Should produce header + grouped docs (fewer than 20)
        non_header = [d for d in docs if d.metadata["node_type"] != "dfm_form_header"]
        assert len(non_header) < 20
        # At least one should be a group
        group_docs = [d for d in docs if d.metadata["node_type"] == "dfm_object_group"]
        assert len(group_docs) >= 1

    def test_group_metadata_has_object_count(self, tmp_path):
        """Grouped chunk text should mention the count."""
        lines = ["object dmMain: TdmMain", "  OldCreateOrder = False"]
        for i in range(5):
            lines.extend(
                [
                    f"  object cds{i}: TClientDataSet",
                    f"    Tag = {i}",
                    "  end",
                ]
            )
        lines.append("end")

        f = tmp_path / "data.dfm"
        f.write_text("\n".join(lines), encoding="utf-8")
        docs = self.reader.load_data(f)

        group_docs = [d for d in docs if d.metadata["node_type"] == "dfm_object_group"]
        assert len(group_docs) >= 1
        # Group text should mention count and type
        text = group_docs[0].text
        assert "TClientDataSet" in text
        assert "Object group:" in text


# ────────────────────────────────────────────────
# TestConstants
# ────────────────────────────────────────────────


class TestConstants:
    """Tests for module-level constants."""

    def test_min_chunk_size(self):
        assert MIN_CHUNK_SIZE == 20

    def test_max_group_chars(self):
        assert MAX_GROUP_CHARS == 4000

    def test_small_object_chars(self):
        assert SMALL_OBJECT_CHARS == 500


# ────────────────────────────────────────────────
# Integration tests with real sample DFM files
# ────────────────────────────────────────────────


class TestIntegrationRealFiles:
    """Integration tests using actual DFM sample files."""

    def setup_method(self):
        self.reader = DFMFileReader()

    @pytest.mark.skipif(
        not (_SAMPLE_FILES / "Splash.dfm").exists(),
        reason="test_sources/Splash.dfm not available",
    )
    def test_splash_dfm(self):
        """Splash.dfm: flat form with binary image data."""
        docs = self.reader.load_data(_SAMPLE_FILES / "Splash.dfm")
        assert len(docs) >= 1

        # Should have a form header
        headers = [d for d in docs if d.metadata["node_type"] == "dfm_form_header"]
        assert len(headers) == 1
        assert headers[0].metadata["form_type"] == "TfrmSplash"

        # Binary data should be stripped
        all_text = " ".join(d.text for d in docs)
        assert "494C01011000" not in all_text
        assert "<binary data removed>" in all_text or "TfrmSplash" in all_text

    @pytest.mark.skipif(
        not (_SAMPLE_FILES / "MainDM.dfm").exists(),
        reason="test_sources/MainDM.dfm not available",
    )
    def test_main_dm_dfm(self):
        """MainDM.dfm: 153 flat TClientDataSet objects — should be grouped."""
        docs = self.reader.load_data(_SAMPLE_FILES / "MainDM.dfm")
        assert len(docs) >= 2  # at least header + some chunks

        # Should have far fewer chunks than 153 individual objects
        non_header = [d for d in docs if d.metadata["node_type"] != "dfm_form_header"]
        # With grouping, should be significantly fewer than 153
        assert len(non_header) < 100

        # Should have group chunks
        group_docs = [d for d in docs if d.metadata["node_type"] == "dfm_object_group"]
        assert len(group_docs) >= 1

        # Form type should be TdmMain
        headers = [d for d in docs if d.metadata["node_type"] == "dfm_form_header"]
        assert headers[0].metadata["form_type"] == "TdmMain"

    @pytest.mark.skipif(
        not (_SAMPLE_FILES / "MainTurdus.dfm").exists(),
        reason="test_sources/MainTurdus.dfm not available",
    )
    def test_main_turdus_dfm(self):
        """MainTurdus.dfm: inherited form with deep nesting and binary data."""
        docs = self.reader.load_data(_SAMPLE_FILES / "MainTurdus.dfm")
        assert len(docs) >= 2

        # Should handle 'inherited' keyword
        headers = [d for d in docs if d.metadata["node_type"] == "dfm_form_header"]
        assert len(headers) == 1
        assert headers[0].metadata["form_type"] == "TfrmMainTurdus"
        assert headers[0].metadata["form_name"] == "frmMainTurdus"

        # Binary data should be stripped
        all_text = " ".join(d.text for d in docs)
        assert "494C01011000" not in all_text

        # Context prefix should be in all chunks
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert doc.text.startswith("// Form:")

    @pytest.mark.skipif(
        not (_SAMPLE_FILES / "WithFrame_SFTP.dfm").exists(),
        reason="test_sources/WithFrame_SFTP.dfm not available",
    )
    def test_with_frame_sftp_dfm(self):
        """WithFrame_SFTP.dfm: frame with nested toolbar and binary data."""
        docs = self.reader.load_data(_SAMPLE_FILES / "WithFrame_SFTP.dfm")
        assert len(docs) >= 2

        headers = [d for d in docs if d.metadata["node_type"] == "dfm_form_header"]
        assert len(headers) == 1
        assert headers[0].metadata["form_type"] == "TframeSFTP_Send"

        # PanLog chunk should contain nested Toolbar and ToolButtons
        pan_docs = [d for d in docs if d.metadata.get("object_name") == "PanLog"]
        if pan_docs:
            text = pan_docs[0].text
            assert "TToolBar" in text or "Toolbar2" in text

        # Binary data should be stripped
        all_text = " ".join(d.text for d in docs)
        assert "494C01011000" not in all_text


# ────────────────────────────────────────────────
# TestDFMObject
# ────────────────────────────────────────────────


class TestDFMObject:
    """Tests for the DFMObject dataclass."""

    def test_text_property(self):
        """text property joins lines with newlines."""
        obj = DFMObject(
            name="test",
            obj_type="TTest",
            start_line=0,
            end_line=2,
            lines=["line1", "line2", "line3"],
        )
        assert obj.text == "line1\nline2\nline3"

    def test_char_count_property(self):
        """char_count returns length of joined text."""
        obj = DFMObject(
            name="test",
            obj_type="TTest",
            start_line=0,
            end_line=0,
            lines=["hello world"],
        )
        assert obj.char_count == 11

    def test_default_children_empty(self):
        """children defaults to empty list."""
        obj = DFMObject(
            name="test",
            obj_type="TTest",
            start_line=0,
            end_line=0,
        )
        assert obj.children == []

    def test_default_lines_empty(self):
        """lines defaults to empty list."""
        obj = DFMObject(
            name="test",
            obj_type="TTest",
            start_line=0,
            end_line=0,
        )
        assert obj.lines == []
        assert obj.text == ""
        assert obj.char_count == 0


# ────────────────────────────────────────────────
# TestCollectionSyntax
# ────────────────────────────────────────────────


class TestCollectionSyntax:
    """Tests for DFM collection syntax (Columns = < ... item ... end ... end>).

    DFM collections use angle-bracket delimited blocks where each 'item'
    is closed by a bare 'end' keyword.  Without collection_depth tracking,
    the bare 'end' inside a collection item would prematurely close the
    parent object.
    """

    def test_collection_items_do_not_close_parent(self):
        """An object with a collection should NOT be closed at the inner 'end'."""
        lines = [
            "object frmTest: TfrmTest",
            "  object lvLog: TListView",
            "    Columns = <",
            "      item",
            "        Caption = 'Time'",
            "        Width = 80",
            "      end",
            "      item",
            "        Caption = 'Event'",
            "        Width = 300",
            "      end>",
            "    ReadOnly = True",
            "    TabOrder = 1",
            "  end",
            "end",
        ]
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert root.name == "frmTest"
        # The lvLog object must be a child — not truncated by the inner 'end'
        assert len(root.children) == 1
        lv = root.children[0]
        assert lv.name == "lvLog"
        # Properties AFTER the collection must be present in the object text
        assert "ReadOnly = True" in lv.text
        assert "TabOrder = 1" in lv.text
        # The collection content must also be present
        assert "Columns = <" in lv.text
        assert "Caption = 'Time'" in lv.text
        assert "Caption = 'Event'" in lv.text

    def test_empty_collection_ignored(self):
        """Self-closing empty collection '<>' should not affect parsing."""
        lines = [
            "object frmTest: TfrmTest",
            "  object cds1: TClientDataSet",
            "    Aggregates = <>",
            "    Params = <>",
            "    Tag = 1",
            "  end",
            "  object cds2: TClientDataSet",
            "    Tag = 2",
            "  end",
            "end",
        ]
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert len(root.children) == 2
        assert root.children[0].name == "cds1"
        assert root.children[1].name == "cds2"
        # Properties after the empty collections must be present
        assert "Tag = 1" in root.children[0].text
        assert "Aggregates = <>" in root.children[0].text

    def test_nested_collections(self):
        """Multiple levels of collection nesting are tracked correctly."""
        lines = [
            "object frmTest: TfrmTest",
            "  object Grid1: TDBGrid",
            "    Columns = <",
            "      item",
            "        SubItems = <",
            "          item",
            "            Caption = 'Inner'",
            "          end>",
            "        Caption = 'Outer'",
            "      end>",
            "    Visible = True",
            "  end",
            "end",
        ]
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert len(root.children) == 1
        grid = root.children[0]
        assert grid.name == "Grid1"
        # Property after nested collection must survive
        assert "Visible = True" in grid.text
        # Inner collection content must be present
        assert "Caption = 'Inner'" in grid.text
        assert "Caption = 'Outer'" in grid.text

    def test_sibling_objects_after_collection_preserved(self):
        """Objects after an object containing a collection are preserved.

        This is the core WithFrame_SFTP.dfm bug: PB, SB, MemoAck, imgListViews
        would disappear because the 'end' inside lvLog's Columns collection
        prematurely closed PanLog.
        """
        lines = [
            "object frameSFTP: TframeSFTP",
            "  object PanLog: TPanel",
            "    Left = 0",
            "    object lvLog: TListView",
            "      Columns = <",
            "        item",
            "          Caption = 'Czas'",
            "          Width = 80",
            "        end",
            "        item",
            "          Caption = 'Zdarzenie'",
            "          Width = 300",
            "        end>",
            "      ReadOnly = True",
            "    end",
            "  end",
            "  object PB: TProgressBar",
            "    Left = 0",
            "  end",
            "  object SB: TStatusBar",
            "    Panels = <",
            "      item",
            "        Width = 280",
            "      end",
            "      item",
            "        Width = 135",
            "      end>",
            "  end",
            "  object MemoAck: TMemo",
            "    Visible = False",
            "  end",
            "end",
        ]
        root = _parse_dfm_tree(lines)
        assert root is not None
        assert root.name == "frameSFTP"
        # All 4 depth-1 children must be present
        child_names = [c.name for c in root.children]
        assert child_names == ["PanLog", "PB", "SB", "MemoAck"]
        # PanLog should contain lvLog with its collection
        assert "lvLog" in root.children[0].text
        assert "Columns = <" in root.children[0].text
        # SB should contain its own collection
        assert "Panels = <" in root.children[2].text

    def test_collection_end_with_angle_bracket(self):
        """'end>' correctly closes the collection without closing the object."""
        lines = [
            "object frmTest: TfrmTest",
            "  object SB: TStatusBar",
            "    Panels = <",
            "      item",
            "        Width = 100",
            "      end>",
            "    SimplePanel = False",
            "  end",
            "end",
        ]
        root = _parse_dfm_tree(lines)
        assert root is not None
        sb = root.children[0]
        assert sb.name == "SB"
        assert sb.obj_type == "TStatusBar"
        # The 'end>' must close the collection, not the object —
        # so SimplePanel must be in the object's text
        assert "SimplePanel = False" in sb.text
        # The collection content must be present
        assert "Width = 100" in sb.text

    @pytest.mark.skipif(
        not (_SAMPLE_FILES / "WithFrame_SFTP.dfm").exists(),
        reason="test_sources/WithFrame_SFTP.dfm not available",
    )
    def test_with_frame_sftp_has_all_children(self):
        """Integration: WithFrame_SFTP.dfm must produce chunks for all depth-1 children.

        Before the collection_depth fix, the 'end' keywords inside lvLog's
        Columns collection and SB's Panels collection would prematurely close
        PanLog and SB respectively, causing PB, SB, MemoAck, and imgListViews
        to be lost.
        """
        reader = DFMFileReader()
        docs = reader.load_data(_SAMPLE_FILES / "WithFrame_SFTP.dfm")

        # Collect all object names from chunk metadata
        object_names = set()
        for doc in docs:
            name = doc.metadata.get("object_name", "")
            # object_name may be comma-separated for grouped chunks
            for n in name.split(", "):
                if n:
                    object_names.add(n)

        # All 5 depth-1 children must appear in the output
        expected_children = {"PanLog", "PB", "SB", "MemoAck", "imgListViews"}
        missing = expected_children - object_names
        assert missing == set(), (
            f"Missing depth-1 children in output: {missing}. Found: {object_names}"
        )
