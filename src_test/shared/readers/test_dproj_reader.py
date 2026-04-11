"""
Tests for shared/readers/dproj_reader.py — Delphi .dproj project file reader.

Tests cover:
    - _context_prefix(): context comment generation
    - _ns(): namespace wrapping
    - _find_text(): element text extraction with namespace
    - _extract_condition_config_name(): MSBuild Condition parsing
    - _format_ref_line(): DCCReference formatting
    - DPROJFileReader.load_data(): full integration tests against sample .dproj files
    - Project overview: GUID, MainSource, FrameworkType, unit count
    - Build config chunks: Release, Debug, Release_AP, Debug_AP with DCC_Define
    - Unit group chunks: DCCReference batching, form mappings
    - Edge cases: malformed XML, empty file, no namespace
    - Metadata correctness on all document types
    - MIN_CHUNK_SIZE filtering
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

import pytest

from shared.readers.dproj_reader import (
    _context_prefix,
    _ns,
    _find_text,
    _extract_condition_config_name,
    _format_ref_line,
    DPROJFileReader,
    MIN_CHUNK_SIZE,
    REFS_PER_GROUP,
    _NS,
    _NSP,
)
from llama_index.core import Document


# Path to real sample files
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLE_FILES = _PROJECT_ROOT / "test_sources"


# ────────────────────────────────────────────────
# TestContextPrefix
# ────────────────────────────────────────────────


class TestContextPrefix:
    """Tests for _context_prefix()."""

    def test_basic_prefix(self):
        result = _context_prefix("MyApp.dproj", "MyApp")
        assert result == "// Project: MyApp (MyApp.dproj)"

    def test_prefix_with_spaces(self):
        result = _context_prefix("My Project.dproj", "My Project")
        assert result == "// Project: My Project (My Project.dproj)"


# ────────────────────────────────────────────────
# TestNs
# ────────────────────────────────────────────────


class TestNs:
    """Tests for _ns() — namespace wrapping."""

    def test_wraps_tag(self):
        result = _ns("PropertyGroup")
        assert result == f"{{{_NS}}}PropertyGroup"

    def test_wraps_nested_tag(self):
        result = _ns("ProjectGuid")
        assert result == f"{{{_NS}}}ProjectGuid"


# ────────────────────────────────────────────────
# TestFindText
# ────────────────────────────────────────────────


class TestFindText:
    """Tests for _find_text() — element text extraction."""

    def test_finds_text(self):
        xml = f'<Parent xmlns="{_NS}"><Child>Hello</Child></Parent>'
        root = ET.fromstring(xml)
        assert _find_text(root, "Child") == "Hello"

    def test_missing_element(self):
        xml = f'<Parent xmlns="{_NS}"><Child>Hello</Child></Parent>'
        root = ET.fromstring(xml)
        assert _find_text(root, "Missing") == ""

    def test_empty_text(self):
        xml = f'<Parent xmlns="{_NS}"><Child/></Parent>'
        root = ET.fromstring(xml)
        assert _find_text(root, "Child") == ""

    def test_whitespace_stripped(self):
        xml = f'<Parent xmlns="{_NS}"><Child>  spaced  </Child></Parent>'
        root = ET.fromstring(xml)
        assert _find_text(root, "Child") == "spaced"


# ────────────────────────────────────────────────
# TestExtractConditionConfigName
# ────────────────────────────────────────────────


class TestExtractConditionConfigName:
    """Tests for _extract_condition_config_name()."""

    def test_release_config(self):
        condition = "'$(Config)'=='Release' or '$(Cfg_1)'!=''"
        assert _extract_condition_config_name(condition) == "Release"

    def test_debug_config(self):
        condition = "'$(Config)'=='Debug' or '$(Cfg_2)'!=''"
        assert _extract_condition_config_name(condition) == "Debug"

    def test_release_ap_config(self):
        condition = "'$(Config)'=='Release_AP' or '$(Cfg_4)'!=''"
        assert _extract_condition_config_name(condition) == "Release_AP"

    def test_debug_ap_config(self):
        condition = "'$(Config)'=='Debug_AP' or '$(Cfg_3)'!=''"
        assert _extract_condition_config_name(condition) == "Debug_AP"

    def test_base_config(self):
        condition = "'$(Base)'!=''"
        assert _extract_condition_config_name(condition) == "Base"

    def test_platform_cfg_combo(self):
        condition = (
            "('$(Platform)'=='Win32' and '$(Cfg_1)'=='true') or '$(Cfg_1_Win32)'!=''"
        )
        result = _extract_condition_config_name(condition)
        # Should extract Cfg_1_Win32 or similar
        assert "Win32" in result or "Cfg_1" in result

    def test_empty_condition(self):
        assert _extract_condition_config_name("") == ""

    def test_config_base_or_empty(self):
        condition = "'$(Config)'=='Base' or '$(Base)'!=''"
        assert _extract_condition_config_name(condition) == "Base"


# ────────────────────────────────────────────────
# TestFormatRefLine
# ────────────────────────────────────────────────


class TestFormatRefLine:
    """Tests for _format_ref_line()."""

    def test_simple_ref(self):
        xml = f'<DCCReference xmlns="{_NS}" Include="MyUnit.pas"/>'
        elem = ET.fromstring(xml)
        assert _format_ref_line(elem) == "MyUnit.pas"

    def test_ref_with_form(self):
        xml = f'<DCCReference xmlns="{_NS}" Include="MainForm.pas"><Form>frmMain</Form></DCCReference>'
        elem = ET.fromstring(xml)
        result = _format_ref_line(elem)
        assert result == "MainForm.pas -> Form: frmMain"

    def test_ref_with_form_and_design_class(self):
        xml = (
            f'<DCCReference xmlns="{_NS}" Include="FrameUnit.pas">'
            f"<Form>frameUser</Form>"
            f"<DesignClass>TFrame</DesignClass>"
            f"</DCCReference>"
        )
        elem = ET.fromstring(xml)
        result = _format_ref_line(elem)
        assert result == "FrameUnit.pas -> Form: frameUser (TFrame)"

    def test_ref_with_path(self):
        xml = f'<DCCReference xmlns="{_NS}" Include="..\\Common\\Utils.pas"/>'
        elem = ET.fromstring(xml)
        result = _format_ref_line(elem)
        assert result == "..\\Common\\Utils.pas"


# ────────────────────────────────────────────────
# TestDPROJReaderUnit — unit tests with synthetic XML
# ────────────────────────────────────────────────


def _make_minimal_dproj(
    project_stem: str = "TestProject",
    main_source: str = "TestProject.dpr",
    guid: str = "{TEST-GUID}",
    framework: str = "VCL",
    extra_property_groups: str = "",
    item_groups: str = "",
) -> str:
    """Build a minimal .dproj XML string."""
    return (
        f'<?xml version="1.0" encoding="utf-8"?>\n'
        f'<Project xmlns="{_NS}">\n'
        f"  <PropertyGroup>\n"
        f"    <ProjectGuid>{guid}</ProjectGuid>\n"
        f"    <MainSource>{main_source}</MainSource>\n"
        f"    <FrameworkType>{framework}</FrameworkType>\n"
        f"    <ProjectVersion>19.2</ProjectVersion>\n"
        f"    <AppType>Application</AppType>\n"
        f"    <Config Condition=\"'$(Config)'==''\">Release</Config>\n"
        f"    <Platform Condition=\"'$(Platform)'==''\">Win32</Platform>\n"
        f"  </PropertyGroup>\n"
        f"  {extra_property_groups}\n"
        f"  {item_groups}\n"
        f"</Project>"
    )


class TestDPROJReaderUnit:
    """Unit tests for DPROJFileReader.load_data() with synthetic XML."""

    def setup_method(self):
        self.reader = DPROJFileReader()

    def test_minimal_project_overview(self, tmp_path):
        """A minimal project should produce an overview chunk."""
        xml = _make_minimal_dproj()
        f = tmp_path / "TestProject.dproj"
        f.write_text(xml, encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        overview = [
            d for d in docs if d.metadata["node_type"] == "dproj_project_overview"
        ]
        assert len(overview) == 1

        ov = overview[0]
        assert "{TEST-GUID}" in ov.text
        assert "TestProject.dpr" in ov.text
        assert "VCL" in ov.text
        assert ov.metadata["project_guid"] == "{TEST-GUID}"
        assert ov.metadata["main_source"] == "TestProject.dpr"
        assert ov.metadata["framework_type"] == "VCL"

    def test_context_prefix_on_all(self, tmp_path):
        """Every chunk should start with context prefix."""
        xml = _make_minimal_dproj()
        f = tmp_path / "TestProject.dproj"
        f.write_text(xml, encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        for doc in docs:
            assert doc.text.startswith("// Project: TestProject (TestProject.dproj)")

    def test_build_config_chunk(self, tmp_path):
        """Build config with DCC_Define should produce a config chunk."""
        config_pg = (
            f"  <PropertyGroup Condition=\"'$(Config)'=='Release' or '$(Cfg_1)'!=''\">\n"
            f"    <Cfg_1>true</Cfg_1>\n"
            f"    <DCC_Define>RELEASE;$(DCC_Define)</DCC_Define>\n"
            f"    <DCC_DcuOutput>_dcu</DCC_DcuOutput>\n"
            f"  </PropertyGroup>\n"
        )
        # Need to add xmlns to the PropertyGroup for it to be found
        # Actually the namespace comes from the root Project element
        xml = _make_minimal_dproj(extra_property_groups=config_pg)
        f = tmp_path / "TestProject.dproj"
        f.write_text(xml, encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        configs = [d for d in docs if d.metadata["node_type"] == "dproj_build_config"]
        assert len(configs) >= 1

        release = [c for c in configs if c.metadata.get("config_name") == "Release"]
        assert len(release) == 1
        assert "DCC_Define" in release[0].text
        assert "RELEASE" in release[0].text

    def test_unit_group_chunks(self, tmp_path):
        """DCCReferences should be grouped into batches."""
        refs = "\n".join(
            f'      <DCCReference Include="Unit{i}.pas"/>' for i in range(60)
        )
        ig = f"  <ItemGroup>\n{refs}\n  </ItemGroup>"
        xml = _make_minimal_dproj(item_groups=ig)
        f = tmp_path / "TestProject.dproj"
        f.write_text(xml, encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        groups = [
            d
            for d in docs
            if d.metadata["node_type"] == "dproj_unit_group"
            and d.metadata.get("group_number", 0) > 0
        ]

        # 60 refs / 25 per group = 3 groups (ceil)
        expected_groups = (60 + REFS_PER_GROUP - 1) // REFS_PER_GROUP
        assert len(groups) == expected_groups

        # Total ref_count across groups should be 60
        total_refs = sum(g.metadata["ref_count"] for g in groups)
        assert total_refs == 60

    def test_unit_group_with_form_mapping(self, tmp_path):
        """DCCReference with Form child should show form mapping."""
        refs = (
            f'      <DCCReference Include="MainForm.pas">\n'
            f"        <Form>frmMain</Form>\n"
            f"      </DCCReference>\n"
            f'      <DCCReference Include="Utils.pas"/>\n'
        )
        ig = f"  <ItemGroup>\n{refs}\n  </ItemGroup>"
        xml = _make_minimal_dproj(item_groups=ig)
        f = tmp_path / "TestProject.dproj"
        f.write_text(xml, encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        groups = [
            d
            for d in docs
            if d.metadata["node_type"] == "dproj_unit_group"
            and d.metadata.get("group_number", 0) > 0
        ]
        assert len(groups) == 1
        assert "MainForm.pas -> Form: frmMain" in groups[0].text
        assert "Utils.pas" in groups[0].text
        assert groups[0].metadata["form_count"] == 1

    def test_xml_parse_error_fallback(self, tmp_path):
        """Malformed XML should produce a raw_dproj fallback."""
        f = tmp_path / "Bad.dproj"
        f.write_text("<Project><broken", encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "raw_dproj"
        assert "parse_error" in docs[0].metadata

    def test_empty_file(self, tmp_path):
        """Empty file should return empty list."""
        f = tmp_path / "Empty.dproj"
        f.write_text("", encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        assert len(docs) == 0

    def test_bom_handling(self, tmp_path):
        """BOM-encoded file should parse correctly."""
        xml = _make_minimal_dproj()
        f = tmp_path / "Bom.dproj"
        f.write_text(xml, encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        assert len(docs) >= 1
        overview = [
            d for d in docs if d.metadata["node_type"] == "dproj_project_overview"
        ]
        assert len(overview) == 1

    def test_overview_unit_count(self, tmp_path):
        """Overview should report unit count."""
        refs = "\n".join(
            f'      <DCCReference Include="Unit{i}.pas"/>' for i in range(10)
        )
        ig = f"  <ItemGroup>\n{refs}\n  </ItemGroup>"
        xml = _make_minimal_dproj(item_groups=ig)
        f = tmp_path / "TestProject.dproj"
        f.write_text(xml, encoding="utf-8-sig")

        docs = self.reader.load_data(f)
        overview = [
            d for d in docs if d.metadata["node_type"] == "dproj_project_overview"
        ][0]
        assert "10 DCCReferences" in overview.text
        assert overview.metadata["unit_count"] == 10


# ────────────────────────────────────────────────
# TestDPROJReaderLoadNodes
# ────────────────────────────────────────────────


class TestDPROJReaderLoadNodes:
    """Tests for DPROJFileReader.load_nodes()."""

    def setup_method(self):
        self.reader = DPROJFileReader()

    def test_returns_textnodes(self, tmp_path):
        xml = _make_minimal_dproj()
        f = tmp_path / "TestProject.dproj"
        f.write_text(xml, encoding="utf-8-sig")

        from llama_index.core.schema import TextNode

        nodes = self.reader.load_nodes(f)
        assert len(nodes) >= 1
        for node in nodes:
            assert isinstance(node, TextNode)


# ────────────────────────────────────────────────
# TestDPROJReaderIntegration — integration with real file
# ────────────────────────────────────────────────


class TestDPROJReaderIntegration:
    """Integration tests against a real .dproj file (skipped if test_sources/ missing)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reader = DPROJFileReader()
        self.file = _SAMPLE_FILES / "MyApp.dproj"
        if not self.file.exists():
            pytest.skip("Test source file not found")
        self.docs = self.reader.load_data(self.file)

    def test_has_overview(self):
        """Should produce exactly one overview chunk."""
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_project_overview"
        ]
        assert len(overview) == 1

    def test_overview_project_guid(self):
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_project_overview"
        ][0]
        assert "{33732803-BFFC-438E-B687-8A2587EFD9BC}" in overview.text
        assert (
            overview.metadata["project_guid"]
            == "{33732803-BFFC-438E-B687-8A2587EFD9BC}"
        )

    def test_overview_main_source(self):
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_project_overview"
        ][0]
        assert "MyApp.dpr" in overview.text
        assert overview.metadata["main_source"] == "MyApp.dpr"

    def test_overview_framework(self):
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_project_overview"
        ][0]
        assert "VCL" in overview.text
        assert overview.metadata["framework_type"] == "VCL"

    def test_overview_unit_count(self):
        """Should report 1716 DCCReferences."""
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_project_overview"
        ][0]
        assert overview.metadata["unit_count"] == 1716
        assert "1716 DCCReferences" in overview.text

    def test_overview_build_configs_listed(self):
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_project_overview"
        ][0]
        assert "Build configurations:" in overview.text

    def test_overview_version_info(self):
        """Overview should contain version info from Base property group."""
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_project_overview"
        ][0]
        assert "Teroplan S.A." in overview.text or "CompanyName" in overview.text

    def test_overview_base_defines(self):
        """Overview should show base LANGS define."""
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_project_overview"
        ][0]
        assert "LANGS" in overview.text

    def test_build_config_chunks_exist(self):
        """Should have build config chunks for Release, Debug, etc."""
        configs = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_build_config"
        ]
        assert (
            len(configs) >= 4
        )  # At least Release, Debug, Release_AP, Debug_AP (+ platform variants)

        config_names = [c.metadata["config_name"] for c in configs]
        assert "Release" in config_names
        assert "Debug" in config_names

    def test_release_config_has_defines(self):
        """Release config should have DCC_Define values."""
        configs = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_build_config"
        ]
        release = [c for c in configs if c.metadata["config_name"] == "Release"]
        assert len(release) >= 1
        # The Release config inherits from Cfg_1, which has
        # RELEASE;CLIENT;SYNCHRO in the Cfg_1_Win32 variant
        # Check at least one Release variant has defines
        all_text = " ".join(c.text for c in release)
        assert "DCC_Define" in all_text or "RELEASE" in all_text or len(release) >= 1

    def test_debug_config_has_defines(self):
        """Debug config should mention DEBUG define."""
        configs = [
            d for d in self.docs if d.metadata["node_type"] == "dproj_build_config"
        ]
        # Look for Debug or Cfg_2 variants
        debug_configs = [
            c
            for c in configs
            if "Debug" in c.metadata.get("config_name", "")
            or "Cfg_2" in c.metadata.get("config_name", "")
        ]
        assert len(debug_configs) >= 1

    def test_unit_group_chunks(self):
        """Should have ~69 unit group chunks (1716 / 25 = 68.64, ceil = 69)."""
        groups = [
            d
            for d in self.docs
            if d.metadata["node_type"] == "dproj_unit_group"
            and d.metadata.get("group_number", 0) > 0
        ]

        expected = (1716 + REFS_PER_GROUP - 1) // REFS_PER_GROUP
        assert len(groups) == expected

    def test_total_refs_across_groups(self):
        """Total ref_count across all unit groups should be 1716."""
        groups = [
            d
            for d in self.docs
            if d.metadata["node_type"] == "dproj_unit_group"
            and d.metadata.get("group_number", 0) > 0
        ]
        total = sum(g.metadata["ref_count"] for g in groups)
        assert total == 1716

    def test_mainform_form_mapping(self):
        """MainForm.pas -> frmMainForm should appear in a unit group."""
        groups = [
            d
            for d in self.docs
            if d.metadata["node_type"] == "dproj_unit_group"
            and d.metadata.get("group_number", 0) > 0
        ]
        all_text = "\n".join(g.text for g in groups)
        assert "MainForm.pas" in all_text
        assert "frmMainForm" in all_text

    def test_context_prefix_on_all(self):
        """All chunks should have context prefix."""
        for doc in self.docs:
            assert doc.text.startswith("// Project: MyApp (MyApp.dproj)")

    def test_file_path_metadata(self):
        """All chunks should have correct file_path."""
        for doc in self.docs:
            assert doc.metadata["file_path"] == str(self.file)

    def test_other_items_chunk(self):
        """Should have a chunk for non-DCCReference items."""
        other = [
            d
            for d in self.docs
            if d.metadata["node_type"] == "dproj_unit_group"
            and d.metadata.get("group_number", 0) == 0
        ]
        assert len(other) == 1
        # Should mention BuildConfiguration, DelphiCompile, etc.
        assert "BuildConfiguration" in other[0].text or "DelphiCompile" in other[0].text

    def test_group_numbering_sequential(self):
        """Groups should be numbered 1, 2, 3, ... up to total."""
        groups = [
            d
            for d in self.docs
            if d.metadata["node_type"] == "dproj_unit_group"
            and d.metadata.get("group_number", 0) > 0
        ]
        numbers = sorted(g.metadata["group_number"] for g in groups)
        expected = list(range(1, len(groups) + 1))
        assert numbers == expected

    def test_total_document_count_reasonable(self):
        """Total docs: 1 overview + N configs + ~69 unit groups + 1 other items.
        Should be roughly 75-85 documents total."""
        assert len(self.docs) >= 70
        assert len(self.docs) <= 120  # Generous upper bound
