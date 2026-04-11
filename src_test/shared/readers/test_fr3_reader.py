"""
Tests for shared/readers/fr3_reader.py — FastReport .fr3 file reader.

Tests cover:
    - _context_prefix(): context comment generation
    - _decode_text(): HTML entity decoding
    - _extract_memo_text(): memo name and text extraction
    - _extract_all_memos(): recursive memo collection
    - _classify_memo_text(): memo classification (label, data_binding, aggregation, expression)
    - _format_memo_line(): memo formatting for chunk output
    - _band_description(): band description with DataSetName, DrillDown, Condition
    - FR3Reader.load_data(): full integration tests against real test files
    - SettlementWithCarriersByRides.fr3: 5 bands, 54 memos, no script
    - ListOfPrintOut.fr3: 4 bands + 2 GroupHeaders with DrillDown, non-trivial script
    - Edge cases: malformed XML, empty file, no pages, no memos
    - Metadata correctness on all document types
    - MIN_CHUNK_SIZE filtering
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from shared.readers.fr3_reader import (
    _context_prefix,
    _decode_text,
    _extract_memo_text,
    _extract_all_memos,
    _classify_memo_text,
    _format_memo_line,
    _band_description,
    FR3Reader,
    MIN_CHUNK_SIZE,
    _BAND_TAGS,
    _BAND_TYPE_NAMES,
)
from llama_index.core import Document


# Path to real sample files
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLE_FILES = _PROJECT_ROOT / "test_sources"


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_minimal_fr3(
    report_stem: str = "TestReport",
    bands: str = "",
    script: str = "",
    description: str = "",
    variables: str = "",
) -> str:
    """Build a minimal FR3 XML string for unit testing."""
    desc_attr = (
        f' ReportOptions.Description.Text="{description}"' if description else ""
    )
    script_attr = (
        f' ScriptText.Text="{script}"'
        if script
        else ' ScriptText.Text="&#13;&#10;begin&#13;&#10;&#13;&#10;end."'
    )
    var_section = variables
    return (
        f'<?xml version="1.0" encoding="utf-8"?>\n'
        f'<TfrxReport Version="6.0" ScriptLanguage="PascalScript"{desc_attr}{script_attr}>\n'
        f'  <TfrxReportPage Name="Page1">\n'
        f"    {bands}\n"
        f"  </TfrxReportPage>\n"
        f"  {var_section}\n"
        f"</TfrxReport>"
    )


def _make_band_xml(
    tag: str = "TfrxMasterData",
    name: str = "Band1",
    memos: list | None = None,
    ds_name: str = "",
    drill_down: str = "",
    condition: str = "",
) -> str:
    """Build a band element XML string with optional memos."""
    attrs = f'Name="{name}"'
    if ds_name:
        attrs += f' DataSetName="{ds_name}"'
    if drill_down:
        attrs += f' DrillDown="{drill_down}"'
    if condition:
        attrs += f' Condition="{condition}"'

    if memos is None:
        memos = []

    memo_xml = "\n".join(
        f'      <TfrxMemoView Name="{m_name}" Text="{m_text.replace(chr(38), "&amp;").replace(chr(60), "&lt;").replace(chr(62), "&gt;").replace(chr(34), "&quot;")}"/>'
        for m_name, m_text in memos
    )

    return f"    <{tag} {attrs}>\n{memo_xml}\n    </{tag}>"


# ────────────────────────────────────────────────
# TestContextPrefix
# ────────────────────────────────────────────────


class TestContextPrefix:
    """Tests for _context_prefix()."""

    def test_basic_prefix(self):
        result = _context_prefix("Report1.fr3", "Report1")
        assert result == "// Report: Report1 (Report1.fr3)"

    def test_prefix_with_spaces(self):
        result = _context_prefix("My Report.fr3", "My Report")
        assert result == "// Report: My Report (My Report.fr3)"

    def test_prefix_with_special_chars(self):
        result = _context_prefix("Report_v2.1.fr3", "Report_v2.1")
        assert result == "// Report: Report_v2.1 (Report_v2.1.fr3)"


# ────────────────────────────────────────────────
# TestDecodeText
# ────────────────────────────────────────────────


class TestDecodeText:
    """Tests for _decode_text() — HTML entity decoding."""

    def test_crlf_entities(self):
        assert _decode_text("Line1&#13;&#10;Line2") == "Line1\nLine2"

    def test_html_entities(self):
        assert _decode_text("&#60;value&#62;") == "<value>"

    def test_quote_entities(self):
        assert _decode_text("&#34;quoted&#34;") == '"quoted"'

    def test_amp_entity(self):
        assert _decode_text("A&#38;B") == "A&B"

    def test_plain_text(self):
        assert _decode_text("plain text") == "plain text"

    def test_empty_string(self):
        assert _decode_text("") == ""

    def test_cr_only(self):
        assert _decode_text("A\rB") == "A\nB"


# ────────────────────────────────────────────────
# TestExtractMemoText
# ────────────────────────────────────────────────


class TestExtractMemoText:
    """Tests for _extract_memo_text()."""

    def test_basic_memo(self):
        elem = ET.fromstring('<TfrxMemoView Name="Memo1" Text="Hello"/>')
        name, text = _extract_memo_text(elem)
        assert name == "Memo1"
        assert text == "Hello"

    def test_memo_no_text(self):
        elem = ET.fromstring('<TfrxMemoView Name="Memo1"/>')
        name, text = _extract_memo_text(elem)
        assert name == "Memo1"
        assert text == ""

    def test_memo_empty_text(self):
        elem = ET.fromstring('<TfrxMemoView Name="Memo1" Text=""/>')
        name, text = _extract_memo_text(elem)
        assert name == "Memo1"
        assert text == ""

    def test_memo_with_entities(self):
        elem = ET.fromstring(
            '<TfrxMemoView Name="m1" Text="[MasterDataSet.&#34;Field&#34;]"/>'
        )
        name, text = _extract_memo_text(elem)
        assert name == "m1"
        assert text == '[MasterDataSet."Field"]'

    def test_memo_no_name(self):
        elem = ET.fromstring('<TfrxMemoView Text="text"/>')
        name, text = _extract_memo_text(elem)
        assert name == ""
        assert text == "text"


# ────────────────────────────────────────────────
# TestExtractAllMemos
# ────────────────────────────────────────────────


class TestExtractAllMemos:
    """Tests for _extract_all_memos() — recursive memo extraction."""

    def test_flat_memos(self):
        xml = """
        <Band>
            <TfrxMemoView Name="M1" Text="A"/>
            <TfrxMemoView Name="M2" Text="B"/>
        </Band>
        """
        parent = ET.fromstring(xml)
        memos = _extract_all_memos(parent)
        assert len(memos) == 2
        assert memos[0] == ("M1", "A")
        assert memos[1] == ("M2", "B")

    def test_nested_memos(self):
        xml = """
        <Band>
            <TfrxMemoView Name="M1" Text="A"/>
            <SubBand>
                <TfrxMemoView Name="M2" Text="B"/>
            </SubBand>
        </Band>
        """
        parent = ET.fromstring(xml)
        memos = _extract_all_memos(parent)
        assert len(memos) == 2

    def test_no_memos(self):
        xml = "<Band><Other Name='X'/></Band>"
        parent = ET.fromstring(xml)
        memos = _extract_all_memos(parent)
        assert len(memos) == 0

    def test_skips_empty_name_and_text(self):
        xml = "<Band><TfrxMemoView/></Band>"
        parent = ET.fromstring(xml)
        memos = _extract_all_memos(parent)
        assert len(memos) == 0


# ────────────────────────────────────────────────
# TestClassifyMemoText
# ────────────────────────────────────────────────


class TestClassifyMemoText:
    """Tests for _classify_memo_text()."""

    def test_empty(self):
        assert _classify_memo_text("") == "empty"

    def test_label(self):
        assert _classify_memo_text("Bilety normalne") == "label"

    def test_data_binding(self):
        assert _classify_memo_text('[MasterDataSet."Field"]') == "data_binding"

    def test_aggregation_sum(self):
        assert _classify_memo_text('[SUM(<MasterDataSet."Field">)]') == "aggregation"

    def test_aggregation_count(self):
        assert _classify_memo_text("[COUNT(something)]") == "aggregation"

    def test_aggregation_avg(self):
        assert _classify_memo_text("[AVG(value)]") == "aggregation"

    def test_expression(self):
        assert _classify_memo_text("[Page#]") == "expression"

    def test_expression_line_number(self):
        assert _classify_memo_text("[Line]") == "expression"

    def test_label_with_brackets_no_dot(self):
        # Has brackets but no dot — treated as expression
        assert _classify_memo_text("[TotalPages#]") == "expression"

    def test_label_no_brackets(self):
        assert _classify_memo_text("RAZEM:") == "label"


# ────────────────────────────────────────────────
# TestFormatMemoLine
# ────────────────────────────────────────────────


class TestFormatMemoLine:
    """Tests for _format_memo_line()."""

    def test_label(self):
        result = _format_memo_line("mmoTitle", "Title Text")
        assert result == '  mmoTitle: "Title Text"'

    def test_data_binding(self):
        result = _format_memo_line("dbField", '[DS."Field"]')
        assert result == '  dbField: [DS."Field"]  (data binding)'

    def test_aggregation(self):
        result = _format_memo_line("sum1", '[SUM(<DS."F">)]')
        assert result == '  sum1: [SUM(<DS."F">)]  (aggregation)'

    def test_expression(self):
        result = _format_memo_line("pageNum", "[Page#]")
        assert result == "  pageNum: [Page#]  (expression)"

    def test_empty_text(self):
        result = _format_memo_line("empty", "")
        assert result == "  empty"

    def test_name_only(self):
        result = _format_memo_line("standalone", "")
        assert result == "  standalone"


# ────────────────────────────────────────────────
# TestBandDescription
# ────────────────────────────────────────────────


class TestBandDescription:
    """Tests for _band_description()."""

    def test_basic_band(self):
        elem = ET.fromstring('<TfrxMasterData Name="MasterData"/>')
        desc = _band_description(elem)
        assert desc == 'MasterData band "MasterData"'

    def test_band_with_dataset(self):
        elem = ET.fromstring(
            '<TfrxMasterData Name="Band1" DataSetName="MasterDataSet"/>'
        )
        desc = _band_description(elem)
        assert "DataSet=MasterDataSet" in desc

    def test_band_with_drilldown(self):
        elem = ET.fromstring('<TfrxGroupHeader Name="GH1" DrillDown="True"/>')
        desc = _band_description(elem)
        assert "DrillDown=True" in desc
        assert "GroupHeader" in desc

    def test_band_with_condition(self):
        elem = ET.fromstring('<TfrxGroupHeader Name="GH1" Condition="[Field]"/>')
        desc = _band_description(elem)
        assert "Condition=" in desc

    def test_band_no_name(self):
        elem = ET.fromstring("<TfrxPageHeader/>")
        desc = _band_description(elem)
        assert desc == "PageHeader band"

    def test_unknown_band_type(self):
        elem = ET.fromstring('<TfrxCustomBand Name="CB1"/>')
        desc = _band_description(elem)
        assert desc == 'TfrxCustomBand band "CB1"'


# ────────────────────────────────────────────────
# TestFR3ReaderUnit — unit tests with synthetic XML
# ────────────────────────────────────────────────


class TestFR3ReaderUnit:
    """Unit tests for FR3Reader.load_data() with synthetic FR3 XML."""

    def setup_method(self):
        self.reader = FR3Reader()

    def test_minimal_report_with_one_band(self, tmp_path):
        """A report with one band and two memos produces overview + band chunk."""
        band = _make_band_xml(
            tag="TfrxMasterData",
            name="MasterData",
            ds_name="DS1",
            memos=[("M1", "Label"), ("M2", '[DS1."Field"]')],
        )
        xml = _make_minimal_fr3("TestReport", bands=band)
        fr3_file = tmp_path / "TestReport.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)

        # Should have overview + band content
        assert len(docs) >= 2
        overview = [d for d in docs if d.metadata["node_type"] == "fr3_report_overview"]
        bands = [d for d in docs if d.metadata["node_type"] == "fr3_band_content"]
        assert len(overview) == 1
        assert len(bands) == 1

    def test_overview_contains_band_summary(self, tmp_path):
        """Overview chunk should list bands and memo counts."""
        band = _make_band_xml(
            tag="TfrxPageHeader",
            name="PH1",
            memos=[("M1", "Header"), ("M2", "Sub"), ("M3", "Col")],
        )
        xml = _make_minimal_fr3("Test", bands=band)
        fr3_file = tmp_path / "Test.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        overview = [
            d for d in docs if d.metadata["node_type"] == "fr3_report_overview"
        ][0]

        assert "3 memo views" in overview.text
        assert "PageHeader" in overview.text

    def test_context_prefix_on_all_chunks(self, tmp_path):
        """Every chunk should start with the context prefix."""
        band = _make_band_xml(
            tag="TfrxMasterData",
            name="BD1",
            memos=[("M1", "Text")],
        )
        xml = _make_minimal_fr3("Report1", bands=band)
        fr3_file = tmp_path / "Report1.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        for doc in docs:
            assert doc.text.startswith("// Report: Report1 (Report1.fr3)")

    def test_trivial_script_not_emitted(self, tmp_path):
        """Trivial script (begin\\n\\nend.) should not produce a script chunk."""
        band = _make_band_xml(tag="TfrxMasterData", name="B1", memos=[("M1", "X")])
        # Default script is trivial
        xml = _make_minimal_fr3("T", bands=band)
        fr3_file = tmp_path / "T.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        scripts = [d for d in docs if d.metadata["node_type"] == "fr3_pascal_script"]
        assert len(scripts) == 0

    def test_nontrivial_script_emitted(self, tmp_path):
        """Non-trivial script should produce a script chunk."""
        band = _make_band_xml(tag="TfrxMasterData", name="B1", memos=[("M1", "X")])
        script_text = "&#13;&#10;procedure Foo;&#13;&#10;begin&#13;&#10;  ShowMessage('hi');&#13;&#10;end;&#13;&#10;&#13;&#10;begin&#13;&#10;end."
        xml = _make_minimal_fr3("T", bands=band, script=script_text)
        fr3_file = tmp_path / "T.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        scripts = [d for d in docs if d.metadata["node_type"] == "fr3_pascal_script"]
        assert len(scripts) == 1
        assert "procedure Foo" in scripts[0].text
        assert scripts[0].metadata["unit_name"] == "T"

    def test_band_content_metadata(self, tmp_path):
        """Band content chunks should have correct metadata."""
        band = _make_band_xml(
            tag="TfrxMasterData",
            name="MD",
            ds_name="MyDS",
            memos=[
                ("L1", "Label"),
                ("B1", '[MyDS."Field"]'),
                ("S1", '[SUM(<MyDS."Total">)]'),
            ],
        )
        xml = _make_minimal_fr3("R", bands=band)
        fr3_file = tmp_path / "R.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        band_doc = [d for d in docs if d.metadata["node_type"] == "fr3_band_content"][0]

        assert band_doc.metadata["band_type"] == "MasterData"
        assert band_doc.metadata["band_name"] == "MD"
        assert band_doc.metadata["memo_count"] == 3
        assert band_doc.metadata["label_count"] == 1
        assert band_doc.metadata["binding_count"] == 1
        assert band_doc.metadata["unit_name"] == "R"

    def test_data_source_extraction_in_overview(self, tmp_path):
        """Overview should list unique data sources from bindings."""
        band = _make_band_xml(
            tag="TfrxMasterData",
            name="B1",
            memos=[
                ("B1", '[DS1."F1"]'),
                ("B2", '[DS1."F2"]'),
                ("B3", '[DS2."F3"]'),
            ],
        )
        xml = _make_minimal_fr3("R", bands=band)
        fr3_file = tmp_path / "R.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        overview = [
            d for d in docs if d.metadata["node_type"] == "fr3_report_overview"
        ][0]

        assert "DS1" in overview.text
        assert "DS2" in overview.text
        assert "Data sources:" in overview.text

    def test_empty_band_not_emitted(self, tmp_path):
        """A band with no memos should not produce a band_content chunk."""
        band_xml = '    <TfrxMasterData Name="Empty"></TfrxMasterData>'
        xml = _make_minimal_fr3("R", bands=band_xml)
        fr3_file = tmp_path / "R.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        band_docs = [d for d in docs if d.metadata["node_type"] == "fr3_band_content"]
        assert len(band_docs) == 0

    def test_description_in_overview(self, tmp_path):
        """Report description should appear in overview."""
        band = _make_band_xml(tag="TfrxMasterData", name="B1", memos=[("M1", "text")])
        xml = _make_minimal_fr3(
            "R", bands=band, description="This is a test report about tickets."
        )
        fr3_file = tmp_path / "R.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        overview = [
            d for d in docs if d.metadata["node_type"] == "fr3_report_overview"
        ][0]
        assert "This is a test report about tickets." in overview.text

    def test_xml_parse_error_fallback(self, tmp_path):
        """Malformed XML should produce a raw_fr3 fallback chunk."""
        fr3_file = tmp_path / "Bad.fr3"
        fr3_file.write_text("<TfrxReport><broken", encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "raw_fr3"
        assert "parse_error" in docs[0].metadata

    def test_empty_file_returns_empty(self, tmp_path):
        """Empty file should return empty list (no content to fallback to)."""
        fr3_file = tmp_path / "Empty.fr3"
        fr3_file.write_text("", encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        # Empty string -> parse error -> no content -> empty
        assert len(docs) == 0

    def test_multiple_pages(self, tmp_path):
        """Report with multiple pages should note each in overview."""
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<TfrxReport Version="6.0" ScriptLanguage="PascalScript" '
            'ScriptText.Text="&#13;&#10;begin&#13;&#10;&#13;&#10;end.">\n'
            '  <TfrxReportPage Name="Page1">\n'
            '    <TfrxMasterData Name="B1">'
            '<TfrxMemoView Name="M1" Text="P1"/>'
            "</TfrxMasterData>\n"
            "  </TfrxReportPage>\n"
            '  <TfrxReportPage Name="Page2" Orientation="poLandscape">\n'
            '    <TfrxMasterData Name="B2">'
            '<TfrxMemoView Name="M2" Text="P2"/>'
            "</TfrxMasterData>\n"
            "  </TfrxReportPage>\n"
            "</TfrxReport>"
        )
        fr3_file = tmp_path / "Multi.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        docs = self.reader.load_data(fr3_file)
        overview = [
            d for d in docs if d.metadata["node_type"] == "fr3_report_overview"
        ][0]
        assert "Pages: 2" in overview.text
        assert overview.metadata["page_count"] == 2


# ────────────────────────────────────────────────
# TestFR3ReaderLoadNodes
# ────────────────────────────────────────────────


class TestFR3ReaderLoadNodes:
    """Tests for FR3Reader.load_nodes()."""

    def setup_method(self):
        self.reader = FR3Reader()

    def test_load_nodes_returns_textnodes(self, tmp_path):
        """load_nodes should return TextNode objects."""
        band = _make_band_xml(tag="TfrxMasterData", name="B1", memos=[("M1", "text")])
        xml = _make_minimal_fr3("T", bands=band)
        fr3_file = tmp_path / "T.fr3"
        fr3_file.write_text(xml, encoding="utf-8")

        from llama_index.core.schema import TextNode

        nodes = self.reader.load_nodes(fr3_file)
        assert len(nodes) >= 1
        for node in nodes:
            assert isinstance(node, TextNode)


# ────────────────────────────────────────────────
# TestFR3ReaderSettlement — integration with real file
# ────────────────────────────────────────────────


class TestFR3ReaderSettlement:
    """Integration tests against SettlementWithCarriersByRides.fr3."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reader = FR3Reader()
        self.file = _SAMPLE_FILES / "SettlementWithCarriersByRides.fr3"
        if not self.file.exists():
            pytest.skip("Test source file not found")
        self.docs = self.reader.load_data(self.file)

    def test_total_chunk_count(self):
        """Should produce overview + 5 band chunks (no script, no variables)."""
        # 5 bands: PageHeader, MasterData, PageFooter, ReportTitle, ReportSummary
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_report_overview"
        ]
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        scripts = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_pascal_script"
        ]
        variables = [d for d in self.docs if d.metadata["node_type"] == "fr3_variables"]

        assert len(overview) == 1
        assert len(bands) == 5
        assert len(scripts) == 0  # Trivial script
        assert len(variables) == 0

    def test_overview_content(self):
        """Overview should contain report name, band listing, data source."""
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_report_overview"
        ][0]

        assert "SettlementWithCarriersByRides" in overview.text
        assert "PageHeader" in overview.text
        assert "MasterData" in overview.text
        assert "ReportSummary" in overview.text
        assert "MasterDataSet" in overview.text
        assert "Data sources:" in overview.text

    def test_overview_metadata(self):
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_report_overview"
        ][0]

        assert overview.metadata["unit_name"] == "SettlementWithCarriersByRides"
        assert overview.metadata["page_count"] == 1
        assert overview.metadata["band_count"] == 5
        assert overview.metadata["has_script"] is False

    def test_page_header_band(self):
        """PageHeader band should have 21 memos with Polish labels."""
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        ph_bands = [d for d in bands if d.metadata["band_type"] == "PageHeader"]
        assert len(ph_bands) == 1

        ph = ph_bands[0]
        assert ph.metadata["memo_count"] == 21
        assert "Bilety normalne" in ph.text
        assert "Relacja" in ph.text
        assert "Numer kursu" in ph.text
        assert "Razem" in ph.text

    def test_master_data_band(self):
        """MasterData band should have 16 memos with data bindings."""
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        md_bands = [d for d in bands if d.metadata["band_type"] == "MasterData"]
        assert len(md_bands) == 1

        md = md_bands[0]
        assert md.metadata["memo_count"] == 16
        assert '[MasterDataSet."RideNumber"]' in md.text
        assert '[MasterDataSet."NormalTicketVal"]' in md.text
        assert "data binding" in md.text

    def test_report_summary_band(self):
        """ReportSummary band should have 13 memos with SUM aggregations."""
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        rs_bands = [d for d in bands if d.metadata["band_type"] == "ReportSummary"]
        assert len(rs_bands) == 1

        rs = rs_bands[0]
        assert rs.metadata["memo_count"] == 13
        assert "RAZEM:" in rs.text
        assert "aggregation" in rs.text

    def test_report_title_band(self):
        """ReportTitle band should have 2 memos."""
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        rt_bands = [d for d in bands if d.metadata["band_type"] == "ReportTitle"]
        assert len(rt_bands) == 1
        assert rt_bands[0].metadata["memo_count"] == 2

    def test_page_footer_band(self):
        """PageFooter band should have 2 memos."""
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        pf_bands = [d for d in bands if d.metadata["band_type"] == "PageFooter"]
        assert len(pf_bands) == 1
        assert pf_bands[0].metadata["memo_count"] == 2

    def test_context_prefix_on_all(self):
        """All chunks should have context prefix."""
        for doc in self.docs:
            assert doc.text.startswith(
                "// Report: SettlementWithCarriersByRides (SettlementWithCarriersByRides.fr3)"
            )

    def test_file_path_metadata(self):
        """All chunks should have correct file_path."""
        for doc in self.docs:
            assert doc.metadata["file_path"] == str(self.file)


# ────────────────────────────────────────────────
# TestFR3ReaderListOfPrintOut — integration with real file
# ────────────────────────────────────────────────


class TestFR3ReaderListOfPrintOut:
    """Integration tests against ListOfPrintOut.fr3."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reader = FR3Reader()
        self.file = _SAMPLE_FILES / "ListOfPrintOut.fr3"
        if not self.file.exists():
            pytest.skip("Test source file not found")
        self.docs = self.reader.load_data(self.file)

    def test_total_chunk_types(self):
        """Should have overview, band chunks, and a script chunk."""
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_report_overview"
        ]
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        scripts = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_pascal_script"
        ]

        assert len(overview) == 1
        assert len(bands) >= 4  # PageFooter, ReportTitle, 2 GroupHeaders, MasterData
        assert len(scripts) == 1  # Non-trivial script

    def test_script_chunk_content(self):
        """Script chunk should contain the drill-down visibility procedure."""
        scripts = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_pascal_script"
        ]
        assert len(scripts) == 1

        script = scripts[0]
        assert "Page1OnBeforePrint" in script.text
        assert "ExpandDrillDown" in script.text
        assert "mmoRowNumberHeader.visible" in script.text
        assert script.metadata["unit_name"] == "ListOfPrintOut"

    def test_description_in_overview(self):
        """Overview should contain drill-down description."""
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_report_overview"
        ][0]
        assert "drill-down" in overview.text.lower()

    def test_group_header_with_drilldown(self):
        """GroupHeader bands should be captured with DrillDown info."""
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        gh_bands = [d for d in bands if d.metadata["band_type"] == "GroupHeader"]
        assert len(gh_bands) == 2

        # Both GroupHeaders should have DrillDown
        for gh in gh_bands:
            assert "DrillDown" in gh.text

    def test_master_data_band_has_data_bindings(self):
        """MasterData band should have data bindings to ADOQuery1."""
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        md_bands = [d for d in bands if d.metadata["band_type"] == "MasterData"]
        assert len(md_bands) == 1

        md = md_bands[0]
        assert "data binding" in md.text
        assert '[MasterDataSet."Number"]' in md.text

    def test_overview_has_script_info(self):
        """Overview should mention embedded PascalScript."""
        overview = [
            d for d in self.docs if d.metadata["node_type"] == "fr3_report_overview"
        ][0]
        assert overview.metadata["has_script"] is True
        assert "PascalScript" in overview.text

    def test_group_header_condition(self):
        """GroupHeader bands should have Condition info."""
        bands = [d for d in self.docs if d.metadata["node_type"] == "fr3_band_content"]
        gh_bands = [d for d in bands if d.metadata["band_type"] == "GroupHeader"]

        # At least one should mention PrintTypeName condition
        conditions = [gh.text for gh in gh_bands]
        assert any("PrintTypeName" in c for c in conditions)

    def test_context_prefix_on_all(self):
        """All chunks should have context prefix."""
        for doc in self.docs:
            assert doc.text.startswith("// Report: ListOfPrintOut (ListOfPrintOut.fr3)")


# ────────────────────────────────────────────────
# TestBandTags — constants validation
# ────────────────────────────────────────────────


class TestBandTags:
    """Validate band tag constants."""

    def test_all_band_tags_have_names(self):
        """Every tag in _BAND_TAGS should have a human-readable name."""
        for tag in _BAND_TAGS:
            assert tag in _BAND_TYPE_NAMES, f"Missing name for {tag}"

    def test_known_tags_in_set(self):
        """Core band types should be in _BAND_TAGS."""
        expected = {
            "TfrxPageHeader",
            "TfrxPageFooter",
            "TfrxMasterData",
            "TfrxDetailData",
            "TfrxGroupHeader",
            "TfrxGroupFooter",
            "TfrxReportTitle",
            "TfrxReportSummary",
        }
        assert expected.issubset(_BAND_TAGS)
