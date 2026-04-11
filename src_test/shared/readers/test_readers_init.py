"""
Tests for shared/readers/__init__.py — reader registry and file loading entry point.

Tests cover:
    - READER_REGISTRY: expected extensions, correct types, shared instances
    - get_reader(): lookup by extension, case insensitivity, unknown extensions
    - load_nodes_for_file(): real files, unknown extensions, metadata injection
    - load_nodes_for_file() with mocked readers: controlled nodes, metadata, passthrough
    - Integration: real file round-trip through the registry
"""

from pathlib import Path
from typing import List, Optional
from unittest.mock import patch, MagicMock

import pytest

from llama_index.core.schema import TextNode

import shared.readers as readers_module
from shared.readers import get_reader, load_nodes_for_file, READER_REGISTRY
from shared.readers._base import BaseFileReader
from shared.readers.pascal_reader import DelphiFileReader
from shared.readers.sql_reader import SQLFileReader
from shared.readers.python_reader import PythonFileReader
from shared.readers.text_reader import TextFileReader
from shared.readers.dfm_reader import DFMFileReader
from shared.readers.dproj_reader import DPROJFileReader
from shared.readers.fr3_reader import FR3Reader
from shared.readers.hbm_reader import HBMFileReader
from shared.readers.java_reader import JavaFileReader
from shared.readers.js_reader import JSFileReader
from shared.readers.jrxml_reader import JRXMLFileReader


# ────────────────────────────────────────────────
# READER_REGISTRY
# ────────────────────────────────────────────────


class TestReaderRegistry:
    """Tests for READER_REGISTRY — extension-to-reader mapping."""

    EXPECTED_EXTENSIONS = [
        ".pas",
        ".dpr",
        ".sql",
        ".py",
        ".java",
        ".js",
        ".ts",
        ".tsx",
        ".dfm",
        ".dproj",
        ".fr3",
        ".hbm.xml",
        ".jrxml",
        ".bat",
        ".sh",
        ".txt",
        ".md",
        ".json",
        ".jsonc",
        ".yml",
        ".yaml",
        ".xml",
        ".jsp",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".properties",
        ".http",
        ".gradle",
        ".wsdl",
        ".xsd",
        ".cfg",
        ".ini",
        ".toml",
    ]

    def test_registry_contains_all_expected_extensions(self):
        """All documented extensions should be present in the registry."""
        for ext in self.EXPECTED_EXTENSIONS:
            assert ext in READER_REGISTRY, f"Missing extension: {ext}"

    def test_registry_has_no_extra_extensions(self):
        """Registry should only contain the expected set of extensions."""
        assert set(READER_REGISTRY.keys()) == set(self.EXPECTED_EXTENSIONS)

    def test_all_readers_are_base_file_reader_instances(self):
        """Every value in the registry should be a BaseFileReader instance."""
        for ext, reader in READER_REGISTRY.items():
            assert isinstance(reader, BaseFileReader), (
                f"Reader for {ext} is not a BaseFileReader: {type(reader)}"
            )

    def test_text_extensions_share_same_instance(self):
        """All text/config extensions should share the same TextFileReader instance."""
        text_exts = [
            ".bat",
            ".sh",
            ".txt",
            ".md",
            ".json",
            ".jsonc",
            ".yml",
            ".yaml",
            ".xml",
            ".jsp",
            ".html",
            ".htm",
            ".css",
            ".scss",
            ".properties",
            ".http",
            ".gradle",
            ".wsdl",
            ".xsd",
            ".cfg",
            ".ini",
            ".toml",
        ]
        first = READER_REGISTRY[text_exts[0]]
        for ext in text_exts[1:]:
            assert READER_REGISTRY[ext] is first, (
                f"Reader for {ext} is not the same instance as {text_exts[0]}"
            )

    def test_text_reader_is_correct_type(self):
        """The shared text reader should be a TextFileReader instance."""
        assert isinstance(READER_REGISTRY[".txt"], TextFileReader)

    def test_pas_and_dpr_are_different_instances(self):
        """.pas and .dpr should use separate DelphiFileReader instances."""
        assert READER_REGISTRY[".pas"] is not READER_REGISTRY[".dpr"]

    def test_pas_reader_type(self):
        """.pas should map to a DelphiFileReader."""
        assert isinstance(READER_REGISTRY[".pas"], DelphiFileReader)

    def test_dpr_reader_type(self):
        """.dpr should map to a DelphiFileReader."""
        assert isinstance(READER_REGISTRY[".dpr"], DelphiFileReader)

    def test_sql_reader_type(self):
        """.sql should map to an SQLFileReader."""
        assert isinstance(READER_REGISTRY[".sql"], SQLFileReader)

    def test_py_reader_type(self):
        """.py should map to a PythonFileReader."""
        assert isinstance(READER_REGISTRY[".py"], PythonFileReader)

    def test_dfm_reader_type(self):
        """.dfm should map to a DFMFileReader."""
        assert isinstance(READER_REGISTRY[".dfm"], DFMFileReader)

    def test_dproj_reader_type(self):
        """.dproj should map to a DPROJFileReader."""
        assert isinstance(READER_REGISTRY[".dproj"], DPROJFileReader)

    def test_fr3_reader_type(self):
        """.fr3 should map to an FR3Reader."""
        assert isinstance(READER_REGISTRY[".fr3"], FR3Reader)

    def test_hbm_xml_reader_type(self):
        """.hbm.xml compound extension should map to an HBMFileReader."""
        assert isinstance(READER_REGISTRY[".hbm.xml"], HBMFileReader)

    def test_java_reader_type(self):
        """.java should map to a JavaFileReader."""
        assert isinstance(READER_REGISTRY[".java"], JavaFileReader)

    def test_js_reader_type(self):
        """.js should map to a JSFileReader."""
        assert isinstance(READER_REGISTRY[".js"], JSFileReader)

    def test_ts_reader_type(self):
        """.ts should map to a JSFileReader."""
        assert isinstance(READER_REGISTRY[".ts"], JSFileReader)

    def test_tsx_reader_type(self):
        """.tsx should map to a JSFileReader."""
        assert isinstance(READER_REGISTRY[".tsx"], JSFileReader)

    def test_js_ts_tsx_share_same_type(self):
        """.js, .ts, .tsx should all use JSFileReader instances."""
        for ext in [".js", ".ts", ".tsx"]:
            assert isinstance(READER_REGISTRY[ext], JSFileReader), (
                f"{ext} is not a JSFileReader"
            )

    def test_jrxml_reader_type(self):
        """.jrxml should map to a JRXMLFileReader."""
        assert isinstance(READER_REGISTRY[".jrxml"], JRXMLFileReader)


# ────────────────────────────────────────────────
# get_reader() — compound extensions
# ────────────────────────────────────────────────


class TestGetReaderCompoundExtensions:
    """Tests for get_reader() with compound extensions via Path objects."""

    def test_hbm_xml_path_returns_hbm_reader(self):
        """Path('Foo.hbm.xml') should return HBMFileReader, not None."""
        reader = get_reader(Path("some/dir/PHStop.hbm.xml"))
        assert isinstance(reader, HBMFileReader)

    def test_plain_xml_string_returns_text_reader(self):
        """String '.xml' should return TextFileReader (generic XML)."""
        reader = get_reader(".xml")
        assert isinstance(reader, TextFileReader)

    def test_hbm_xml_string_returns_hbm_reader(self):
        """String '.hbm.xml' should return HBMFileReader (direct registry lookup)."""
        reader = get_reader(".hbm.xml")
        assert isinstance(reader, HBMFileReader)

    def test_plain_xml_path_returns_text_reader(self):
        """Path('config.xml') should return TextFileReader (.xml now in registry)."""
        reader = get_reader(Path("config.xml"))
        assert isinstance(reader, TextFileReader)

    def test_compound_extension_takes_priority_over_final_suffix(self):
        """.hbm.xml compound extension should win over .xml text reader."""
        reader = get_reader(Path("entity/PHStop.hbm.xml"))
        assert isinstance(reader, HBMFileReader)

    def test_path_with_single_suffix_works(self):
        """Path('file.py') should use final suffix lookup."""
        reader = get_reader(Path("src/app.py"))
        assert isinstance(reader, PythonFileReader)

    def test_path_with_no_suffix_returns_none(self):
        """Path('Makefile') with no suffix should return None."""
        assert get_reader(Path("Makefile")) is None

    def test_path_case_insensitive(self):
        """Path with uppercase compound ext should still match."""
        # Path.suffixes preserves case, get_reader lowercases
        reader = get_reader(Path("entity/PHStop.HBM.XML"))
        assert isinstance(reader, HBMFileReader)

    def test_three_part_extension_uses_last_two(self):
        """Path('file.backup.hbm.xml') should match .hbm.xml via last two suffixes."""
        reader = get_reader(Path("file.backup.hbm.xml"))
        assert isinstance(reader, HBMFileReader)

    def test_unrelated_compound_extension_falls_through(self):
        """Path('file.test.py') — compound '.test.py' not registered, falls to '.py'."""
        reader = get_reader(Path("file.test.py"))
        assert isinstance(reader, PythonFileReader)


# ────────────────────────────────────────────────
# get_reader() — simple extensions
# ────────────────────────────────────────────────


class TestGetReader:
    """Tests for get_reader() — extension lookup."""

    def test_returns_reader_for_known_extension(self):
        """get_reader should return the registered reader for a known extension."""
        reader = get_reader(".py")
        assert reader is READER_REGISTRY[".py"]

    def test_returns_none_for_unknown_extension(self):
        """get_reader should return None for an unregistered extension."""
        assert get_reader(".xyz") is None

    def test_case_insensitive_uppercase(self):
        """get_reader should be case-insensitive (.PY returns same as .py)."""
        assert get_reader(".PY") is get_reader(".py")

    def test_case_insensitive_mixed_case(self):
        """get_reader should handle mixed case (.Pas)."""
        assert get_reader(".Pas") is READER_REGISTRY[".pas"]

    def test_extension_must_include_dot(self):
        """An extension without a leading dot should not match."""
        assert get_reader("py") is None

    def test_empty_string_returns_none(self):
        """An empty string should return None."""
        assert get_reader("") is None

    def test_returns_correct_reader_for_each_extension(self):
        """Every registered extension should return its specific reader."""
        for ext, expected_reader in READER_REGISTRY.items():
            result = get_reader(ext)
            assert result is expected_reader, (
                f"get_reader({ext!r}) returned wrong reader"
            )


# ────────────────────────────────────────────────
# load_nodes_for_file() — real files
# ────────────────────────────────────────────────


class TestLoadNodesForFile:
    """Tests for load_nodes_for_file() using real temporary files."""

    def test_returns_text_nodes_for_txt_file(self, tmp_path):
        """A .txt file with content should produce at least one TextNode."""
        f = tmp_path / "hello.txt"
        f.write_text("Hello, world! This is a test file with some content.")
        file_info = {
            "full_path": str(f),
            "file_path": "relative/hello.txt",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        assert all(isinstance(n, TextNode) for n in nodes)

    def test_returns_empty_list_for_unknown_extension(self, tmp_path):
        """An unknown extension should produce an empty list."""
        f = tmp_path / "data.xyz"
        f.write_text("some data")
        file_info = {
            "full_path": str(f),
            "file_path": "relative/data.xyz",
        }
        nodes = load_nodes_for_file(file_info)
        assert nodes == []

    def test_sets_file_path_metadata(self, tmp_path):
        """Each returned node should have file_path metadata set to relative path."""
        f = tmp_path / "note.txt"
        f.write_text("This is a sentence that is long enough to not be empty.")
        file_info = {
            "full_path": str(f),
            "file_path": "docs/note.txt",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        for node in nodes:
            assert node.metadata["file_path"] == "docs/note.txt"

    def test_extra_info_default_is_none(self, tmp_path):
        """Calling without extra_info should not raise an error."""
        f = tmp_path / "plain.txt"
        f.write_text("Content for testing without extra info.")
        file_info = {
            "full_path": str(f),
            "file_path": "plain.txt",
        }
        # Should not raise
        nodes = load_nodes_for_file(file_info)
        assert isinstance(nodes, list)

    def test_node_text_contains_file_content(self, tmp_path):
        """Node text should contain the actual file content."""
        content = "This is real file content for the test."
        f = tmp_path / "real.txt"
        f.write_text(content)
        file_info = {
            "full_path": str(f),
            "file_path": "real.txt",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        combined_text = " ".join(n.text for n in nodes)
        assert "real file content" in combined_text


# ────────────────────────────────────────────────
# load_nodes_for_file() — mocked reader
# ────────────────────────────────────────────────


class TestLoadNodesForFileMocked:
    """Tests for load_nodes_for_file() with mocked reader.load_nodes."""

    def _make_file_info(self, tmp_path, ext=".txt"):
        """Helper: create a temp file and return file_info dict."""
        f = tmp_path / f"test{ext}"
        f.write_text("placeholder")
        return {
            "full_path": str(f),
            "file_path": f"project/test{ext}",
        }

    def test_file_path_metadata_set_on_each_node(self, tmp_path):
        """load_nodes_for_file should set file_path metadata on every returned node."""
        file_info = self._make_file_info(tmp_path, ".txt")
        mock_nodes = [
            TextNode(text="chunk 1", metadata={"original": "a"}),
            TextNode(text="chunk 2", metadata={"original": "b"}),
            TextNode(text="chunk 3", metadata={"original": "c"}),
        ]
        reader = READER_REGISTRY[".txt"]
        with patch.object(reader, "load_nodes", return_value=mock_nodes):
            nodes = load_nodes_for_file(file_info)

        assert len(nodes) == 3
        for node in nodes:
            assert node.metadata["file_path"] == "project/test.txt"
            # Original metadata should also be preserved
            assert "original" in node.metadata

    def test_empty_node_list_returns_empty(self, tmp_path):
        """When the reader returns no nodes, load_nodes_for_file returns empty list."""
        file_info = self._make_file_info(tmp_path, ".py")
        reader = READER_REGISTRY[".py"]
        with patch.object(reader, "load_nodes", return_value=[]):
            nodes = load_nodes_for_file(file_info)

        assert nodes == []

    def test_extra_info_forwarded_to_reader(self, tmp_path):
        """extra_info should be passed through to the reader's load_nodes."""
        file_info = self._make_file_info(tmp_path, ".sql")
        extra = {"project": "my_project", "version": 3}
        reader = READER_REGISTRY[".sql"]
        with patch.object(reader, "load_nodes", return_value=[]) as mock_load:
            load_nodes_for_file(file_info, extra_info=extra)

        mock_load.assert_called_once()
        call_args = mock_load.call_args
        assert call_args[0][0] == Path(file_info["full_path"])
        assert call_args[0][1] == extra

    def test_extra_info_none_by_default(self, tmp_path):
        """Without extra_info, the reader should receive None."""
        file_info = self._make_file_info(tmp_path, ".txt")
        reader = READER_REGISTRY[".txt"]
        with patch.object(reader, "load_nodes", return_value=[]) as mock_load:
            load_nodes_for_file(file_info)

        mock_load.assert_called_once()
        call_args = mock_load.call_args
        assert call_args[0][1] is None

    def test_full_path_passed_as_path_object(self, tmp_path):
        """The reader should receive a Path object, not a string."""
        file_info = self._make_file_info(tmp_path, ".py")
        reader = READER_REGISTRY[".py"]
        with patch.object(reader, "load_nodes", return_value=[]) as mock_load:
            load_nodes_for_file(file_info)

        call_args = mock_load.call_args
        assert isinstance(call_args[0][0], Path)

    def test_single_node_gets_metadata(self, tmp_path):
        """Even a single returned node should have file_path metadata set."""
        file_info = self._make_file_info(tmp_path, ".txt")
        mock_node = TextNode(text="only node", metadata={})
        reader = READER_REGISTRY[".txt"]
        with patch.object(reader, "load_nodes", return_value=[mock_node]):
            nodes = load_nodes_for_file(file_info)

        assert len(nodes) == 1
        assert nodes[0].metadata["file_path"] == "project/test.txt"


# ────────────────────────────────────────────────
# Integration tests — real file round-trips
# ────────────────────────────────────────────────


class TestIntegration:
    """Integration tests — real files through the full registry pipeline."""

    def test_python_file_round_trip(self, tmp_path):
        """Create a .py file, load nodes, verify content is present."""
        f = tmp_path / "example.py"
        f.write_text(
            'def hello():\n    """Say hello."""\n    return \'Hello, world!\'\n',
            encoding="utf-8",
        )
        file_info = {
            "full_path": str(f),
            "file_path": "src/example.py",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        assert all(isinstance(n, TextNode) for n in nodes)
        combined = " ".join(n.text for n in nodes)
        assert "hello" in combined.lower()
        # file_path metadata should be the relative path
        for node in nodes:
            assert node.metadata["file_path"] == "src/example.py"

    def test_txt_file_round_trip(self, tmp_path):
        """Create a .txt file, load nodes, verify content."""
        content = "This is a plain text document for integration testing."
        f = tmp_path / "readme.txt"
        f.write_text(content, encoding="utf-8")
        file_info = {
            "full_path": str(f),
            "file_path": "docs/readme.txt",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        combined = " ".join(n.text for n in nodes)
        assert "plain text document" in combined
        for node in nodes:
            assert node.metadata["file_path"] == "docs/readme.txt"

    def test_unknown_extension_returns_empty(self, tmp_path):
        """A file with an unregistered extension returns empty list."""
        f = tmp_path / "archive.tar.gz"
        f.write_bytes(b"\x1f\x8b\x08\x00")
        file_info = {
            "full_path": str(f),
            "file_path": "archive.tar.gz",
        }
        nodes = load_nodes_for_file(file_info)
        assert nodes == []

    def test_bat_file_round_trip(self, tmp_path):
        """Create a .bat file, verify it uses TextFileReader and returns nodes."""
        f = tmp_path / "run.bat"
        f.write_text("@echo off\necho Hello from batch file\npause\n")
        file_info = {
            "full_path": str(f),
            "file_path": "scripts/run.bat",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        combined = " ".join(n.text for n in nodes)
        assert "echo" in combined.lower()
        for node in nodes:
            assert node.metadata["file_path"] == "scripts/run.bat"

    def test_json_file_round_trip(self, tmp_path):
        """A .json file should be handled by the text reader."""
        f = tmp_path / "config.json"
        f.write_text('{"key": "value", "number": 42}', encoding="utf-8")
        file_info = {
            "full_path": str(f),
            "file_path": "config.json",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        combined = " ".join(n.text for n in nodes)
        assert "key" in combined
        for node in nodes:
            assert node.metadata["file_path"] == "config.json"

    def test_extra_info_with_real_file(self, tmp_path):
        """extra_info should be accepted without errors on a real file."""
        f = tmp_path / "sample.txt"
        f.write_text("Sample content for extra_info integration test.")
        file_info = {
            "full_path": str(f),
            "file_path": "sample.txt",
        }
        extra = {"project": "integration_test"}
        # Should not raise
        nodes = load_nodes_for_file(file_info, extra_info=extra)
        assert isinstance(nodes, list)

    def test_hbm_xml_file_round_trip(self, tmp_path):
        """A .hbm.xml file should route through HBMFileReader via compound extension."""
        f = tmp_path / "PHStop.hbm.xml"
        hbm_content = """<?xml version="1.0"?>
<hibernate-mapping default-access="field">
  <class name="com.example.app.persistence.dbo.impl.PHStop" table="PT_STOP">
    <id name="id" column="ID_STOP">
      <generator class="sequence">
        <param name="sequence">SEQ_PT_STOP</param>
      </generator>
    </id>
    <property name="name" column="NAME" not-null="true"/>
    <property name="code" column="CODE"/>
  </class>
</hibernate-mapping>"""
        f.write_text(hbm_content, encoding="utf-8")
        file_info = {
            "full_path": str(f),
            "file_path": "persistence/PHStop.hbm.xml",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        combined = " ".join(n.text for n in nodes)
        assert "PHStop" in combined
        assert "PT_STOP" in combined
        for node in nodes:
            assert node.metadata["file_path"] == "persistence/PHStop.hbm.xml"
            assert node.metadata["node_type"] == "hbm_entity_overview"

    def test_java_file_round_trip(self, tmp_path):
        """A .java file should route through JavaFileReader."""
        f = tmp_path / "Hello.java"
        f.write_text(
            "package com.example;\n\npublic class Hello {\n"
            "    public String greet() {\n"
            '        return "Hello";\n'
            "    }\n"
            "}\n",
            encoding="utf-8",
        )
        file_info = {
            "full_path": str(f),
            "file_path": "src/Hello.java",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        combined = " ".join(n.text for n in nodes)
        assert "Hello" in combined
        for node in nodes:
            assert node.metadata["file_path"] == "src/Hello.java"

    def test_js_file_round_trip(self, tmp_path):
        """A .js file should route through JSFileReader."""
        f = tmp_path / "app.js"
        f.write_text(
            "function init() {\n    console.log('initialized');\n}\n",
            encoding="utf-8",
        )
        file_info = {
            "full_path": str(f),
            "file_path": "scripts/app.js",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        combined = " ".join(n.text for n in nodes)
        assert "init" in combined
        for node in nodes:
            assert node.metadata["file_path"] == "scripts/app.js"

    def test_jrxml_file_round_trip(self, tmp_path):
        """A .jrxml file should route through JRXMLFileReader."""
        f = tmp_path / "SalesReport.jrxml"
        jrxml_content = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
              name="SalesReport" pageWidth="595" pageHeight="842">
    <parameter name="startDate" class="java.util.Date"/>
    <parameter name="endDate" class="java.util.Date"/>
    <field name="productName" class="java.lang.String"/>
    <field name="quantity" class="java.lang.Integer"/>
    <field name="price" class="java.math.BigDecimal"/>
    <variable name="totalPrice" class="java.math.BigDecimal" calculation="Sum">
        <variableExpression><![CDATA[$F{price} * $F{quantity}]]></variableExpression>
    </variable>
    <detail>
        <band height="20">
            <textField>
                <reportElement x="0" y="0" width="200" height="20"/>
                <textFieldExpression><![CDATA[$F{productName}]]></textFieldExpression>
            </textField>
        </band>
    </detail>
</jasperReport>"""
        f.write_text(jrxml_content, encoding="utf-8")
        file_info = {
            "full_path": str(f),
            "file_path": "reports/SalesReport.jrxml",
        }
        nodes = load_nodes_for_file(file_info)
        assert len(nodes) >= 1
        combined = " ".join(n.text for n in nodes)
        assert "SalesReport" in combined
        for node in nodes:
            assert node.metadata["file_path"] == "reports/SalesReport.jrxml"
            assert "node_type" in node.metadata
            assert node.metadata["node_type"].startswith("jrxml_")
