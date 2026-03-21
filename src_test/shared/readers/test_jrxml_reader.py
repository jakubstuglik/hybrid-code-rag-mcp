"""
Tests for shared/readers/jrxml_reader.py — JasperReports .jrxml reader.

Tests cover:
    - XML helpers: _get_text, _short_class_name
    - Parameter extraction: names, types, defaults
    - Field extraction: names, types
    - Variable extraction: user-defined, built-in filtering
    - Group extraction: names, expressions
    - Band extraction: sections, heights, element counts
    - Subreport extraction: expressions
    - Expression extraction: non-trivial filtering, trivial exclusion
    - Overview builder: all sections, context prefix
    - Expressions builder: grouping by type
    - JRXMLFileReader: load_data() for various report structures
    - Empty file, parse error fallback
    - Metadata correctness (unit_name, report_name, node_type)
    - extra_info forwarding
"""

from pathlib import Path

import pytest

from shared.readers.jrxml_reader import (
    JRXMLFileReader,
    _build_expressions_chunk,
    _build_report_overview,
    _extract_all_expressions,
    _extract_bands,
    _extract_fields,
    _extract_groups,
    _extract_parameters,
    _extract_subreports,
    _extract_variables,
    _get_text,
    _short_class_name,
    _TRIVIAL_EXPR_RE,
)

import xml.etree.ElementTree as ET


# ────────────────────────────────────────────────
# Test JRXML samples
# ────────────────────────────────────────────────

_NS = "{http://jasperreports.sourceforge.net/jasperreports}"

SIMPLE_REPORT = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
    name="SimpleReport" pageWidth="595" pageHeight="842"
    columnWidth="555" leftMargin="20" rightMargin="20"
    topMargin="20" bottomMargin="20">
  <parameter name="title" class="java.lang.String">
    <defaultValueExpression><![CDATA["Default Title"]]></defaultValueExpression>
  </parameter>
  <parameter name="startDate" class="java.util.Date"/>
  <field name="id" class="java.lang.Long"/>
  <field name="name" class="java.lang.String"/>
  <field name="amount" class="java.math.BigDecimal"/>
  <detail>
    <band height="20">
      <textField>
        <reportElement x="0" y="0" width="100" height="20"/>
        <textFieldExpression><![CDATA[$F{{name}}]]></textFieldExpression>
      </textField>
      <textField>
        <reportElement x="100" y="0" width="100" height="20"/>
        <textFieldExpression><![CDATA[$F{{amount}} != null ? $F{{amount}}.toString() : "N/A"]]></textFieldExpression>
      </textField>
    </band>
  </detail>
  <summary>
    <band height="30">
      <textField>
        <reportElement x="0" y="0" width="200" height="20"/>
        <textFieldExpression><![CDATA["Total: " + $V{{REPORT_COUNT}}]]></textFieldExpression>
      </textField>
    </band>
  </summary>
</jasperReport>"""

REPORT_WITH_GROUPS = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
    name="GroupedReport" pageWidth="595" pageHeight="842">
  <field name="category" class="java.lang.String"/>
  <field name="item" class="java.lang.String"/>
  <field name="price" class="java.math.BigDecimal"/>
  <variable name="categoryTotal" class="java.math.BigDecimal" calculation="Sum">
    <variableExpression><![CDATA[$F{{price}}]]></variableExpression>
  </variable>
  <variable name="grandTotal" class="java.math.BigDecimal" calculation="Sum">
    <variableExpression><![CDATA[$F{{price}}]]></variableExpression>
  </variable>
  <group name="CategoryGroup">
    <groupExpression><![CDATA[$F{{category}}]]></groupExpression>
  </group>
  <detail>
    <band height="20">
      <textField>
        <reportElement x="0" y="0" width="200" height="20"/>
        <textFieldExpression><![CDATA[$F{{item}}]]></textFieldExpression>
      </textField>
    </band>
  </detail>
</jasperReport>"""

REPORT_WITH_SUBREPORT = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
    name="MainReport" pageWidth="595" pageHeight="842">
  <parameter name="SUBREPORT_DIR" class="java.lang.String"/>
  <field name="id" class="java.lang.Long"/>
  <detail>
    <band height="200">
      <subreport>
        <reportElement x="0" y="0" width="555" height="100"/>
        <subreportExpression><![CDATA[$P{{SUBREPORT_DIR}} + "subItems.jasper"]]></subreportExpression>
      </subreport>
    </band>
  </detail>
</jasperReport>"""

REPORT_WITH_MANY_BANDS = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
    name="AllBands" pageWidth="595" pageHeight="842">
  <field name="data" class="java.lang.String"/>
  <title>
    <band height="50">
      <staticText><reportElement x="0" y="0" width="200" height="20"/></staticText>
    </band>
  </title>
  <pageHeader>
    <band height="30">
      <staticText><reportElement x="0" y="0" width="200" height="20"/></staticText>
    </band>
  </pageHeader>
  <columnHeader>
    <band height="20">
      <staticText><reportElement x="0" y="0" width="100" height="20"/></staticText>
    </band>
  </columnHeader>
  <detail>
    <band height="20">
      <textField>
        <reportElement x="0" y="0" width="200" height="20"/>
        <textFieldExpression><![CDATA[$F{{data}}]]></textFieldExpression>
      </textField>
    </band>
  </detail>
  <columnFooter>
    <band height="20">
      <staticText><reportElement x="0" y="0" width="200" height="20"/></staticText>
    </band>
  </columnFooter>
  <pageFooter>
    <band height="30">
      <staticText><reportElement x="0" y="0" width="200" height="20"/></staticText>
    </band>
  </pageFooter>
  <summary>
    <band height="40">
      <staticText><reportElement x="0" y="0" width="200" height="20"/></staticText>
    </band>
  </summary>
</jasperReport>"""

MINIMAL_REPORT = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
    name="Minimal" pageWidth="595" pageHeight="842">
  <detail>
    <band height="20"/>
  </detail>
</jasperReport>"""

INVALID_XML = """<?xml version="1.0"?>
<jasperReport name="Broken">
  <field name="x"
"""

MANY_EXPRESSIONS_REPORT = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports"
    name="ExprReport" pageWidth="595" pageHeight="842">
  <field name="a" class="java.lang.String"/>
  <field name="b" class="java.lang.Integer"/>
  <detail>
    <band height="100">
      <textField>
        <reportElement x="0" y="0" width="100" height="20"/>
        <textFieldExpression><![CDATA[$F{{a}} + " - " + $F{{b}}]]></textFieldExpression>
      </textField>
      <textField>
        <reportElement x="0" y="20" width="100" height="20"/>
        <textFieldExpression><![CDATA[$F{{b}} > 0 ? "Positive" : "Zero or Negative"]]></textFieldExpression>
      </textField>
      <textField>
        <reportElement x="0" y="40" width="100" height="20"/>
        <textFieldExpression><![CDATA[new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date())]]></textFieldExpression>
      </textField>
      <textField>
        <reportElement x="0" y="60" width="100" height="20">
          <printWhenExpression><![CDATA[$F{{b}} != null && $F{{b}} > 100]]></printWhenExpression>
        </reportElement>
        <textFieldExpression><![CDATA["High value: " + $F{{b}}]]></textFieldExpression>
      </textField>
    </band>
  </detail>
</jasperReport>"""


# ────────────────────────────────────────────────
# XML helpers
# ────────────────────────────────────────────────


class TestGetText:
    """Tests for _get_text() helper."""

    def test_element_with_text(self):
        elem = ET.fromstring("<tag>hello world</tag>")
        assert _get_text(elem) == "hello world"

    def test_element_with_whitespace(self):
        elem = ET.fromstring("<tag>  spaced  </tag>")
        assert _get_text(elem) == "spaced"

    def test_none_element(self):
        assert _get_text(None) == ""

    def test_empty_element(self):
        elem = ET.fromstring("<tag/>")
        assert _get_text(elem) == ""


class TestShortClassName:
    """Tests for _short_class_name()."""

    def test_fully_qualified(self):
        assert _short_class_name("java.lang.String") == "String"

    def test_already_short(self):
        assert _short_class_name("String") == "String"

    def test_deep_package(self):
        assert _short_class_name("java.math.BigDecimal") == "BigDecimal"


class TestTrivialExprRegex:
    """Tests for _TRIVIAL_EXPR_RE — trivial expression filtering."""

    def test_field_reference_is_trivial(self):
        assert _TRIVIAL_EXPR_RE.match("$F{name}")

    def test_param_reference_is_trivial(self):
        assert _TRIVIAL_EXPR_RE.match("$P{title}")

    def test_variable_reference_is_trivial(self):
        assert _TRIVIAL_EXPR_RE.match("$V{total}")

    def test_concatenation_is_not_trivial(self):
        assert not _TRIVIAL_EXPR_RE.match('$F{a} + " " + $F{b}')

    def test_ternary_is_not_trivial(self):
        assert not _TRIVIAL_EXPR_RE.match('$F{x} != null ? $F{x} : "N/A"')

    def test_string_literal_is_not_trivial(self):
        assert not _TRIVIAL_EXPR_RE.match('"Total: "')

    def test_method_call_is_not_trivial(self):
        assert not _TRIVIAL_EXPR_RE.match("$F{name}.toUpperCase()")


# ────────────────────────────────────────────────
# Extraction functions
# ────────────────────────────────────────────────


class TestExtractParameters:
    """Tests for _extract_parameters()."""

    def test_parameters_from_simple_report(self):
        root = ET.fromstring(SIMPLE_REPORT)
        params = _extract_parameters(root)
        assert len(params) == 2
        names = [p[0] for p in params]
        assert "title" in names
        assert "startDate" in names

    def test_parameter_types(self):
        root = ET.fromstring(SIMPLE_REPORT)
        params = _extract_parameters(root)
        title_param = [p for p in params if p[0] == "title"][0]
        assert title_param[1] == "String"

    def test_parameter_default(self):
        root = ET.fromstring(SIMPLE_REPORT)
        params = _extract_parameters(root)
        title_param = [p for p in params if p[0] == "title"][0]
        assert '"Default Title"' in title_param[2]

    def test_no_parameters(self):
        root = ET.fromstring(MINIMAL_REPORT)
        params = _extract_parameters(root)
        assert params == []


class TestExtractFields:
    """Tests for _extract_fields()."""

    def test_fields_from_simple_report(self):
        root = ET.fromstring(SIMPLE_REPORT)
        fields = _extract_fields(root)
        assert len(fields) == 3
        names = [f[0] for f in fields]
        assert "id" in names
        assert "name" in names
        assert "amount" in names

    def test_field_types_short(self):
        root = ET.fromstring(SIMPLE_REPORT)
        fields = _extract_fields(root)
        id_field = [f for f in fields if f[0] == "id"][0]
        assert id_field[1] == "Long"

    def test_no_fields(self):
        root = ET.fromstring(MINIMAL_REPORT)
        fields = _extract_fields(root)
        assert fields == []


class TestExtractVariables:
    """Tests for _extract_variables()."""

    def test_variables_from_grouped_report(self):
        root = ET.fromstring(REPORT_WITH_GROUPS)
        variables = _extract_variables(root)
        assert len(variables) == 2
        names = [v[0] for v in variables]
        assert "categoryTotal" in names
        assert "grandTotal" in names

    def test_variable_calculation(self):
        root = ET.fromstring(REPORT_WITH_GROUPS)
        variables = _extract_variables(root)
        cat_var = [v for v in variables if v[0] == "categoryTotal"][0]
        assert cat_var[2] == "Sum"

    def test_variable_expression(self):
        root = ET.fromstring(REPORT_WITH_GROUPS)
        variables = _extract_variables(root)
        cat_var = [v for v in variables if v[0] == "categoryTotal"][0]
        assert "$F{price}" in cat_var[3]

    def test_no_variables(self):
        root = ET.fromstring(MINIMAL_REPORT)
        variables = _extract_variables(root)
        assert variables == []


class TestExtractGroups:
    """Tests for _extract_groups()."""

    def test_group_from_grouped_report(self):
        root = ET.fromstring(REPORT_WITH_GROUPS)
        groups = _extract_groups(root)
        assert len(groups) == 1
        assert groups[0][0] == "CategoryGroup"
        assert "$F{category}" in groups[0][1]

    def test_no_groups(self):
        root = ET.fromstring(SIMPLE_REPORT)
        groups = _extract_groups(root)
        assert groups == []


class TestExtractBands:
    """Tests for _extract_bands()."""

    def test_bands_from_all_bands_report(self):
        root = ET.fromstring(REPORT_WITH_MANY_BANDS)
        bands = _extract_bands(root)
        section_names = [b[0] for b in bands]
        assert "title" in section_names
        assert "pageHeader" in section_names
        assert "detail" in section_names
        assert "summary" in section_names
        assert len(bands) == 7

    def test_band_height(self):
        root = ET.fromstring(REPORT_WITH_MANY_BANDS)
        bands = _extract_bands(root)
        title_band = [b for b in bands if b[0] == "title"][0]
        assert title_band[1] == 50

    def test_band_element_count(self):
        root = ET.fromstring(REPORT_WITH_MANY_BANDS)
        bands = _extract_bands(root)
        detail_band = [b for b in bands if b[0] == "detail"][0]
        assert detail_band[2] == 1  # one textField

    def test_minimal_report_bands(self):
        root = ET.fromstring(MINIMAL_REPORT)
        bands = _extract_bands(root)
        assert len(bands) == 1
        assert bands[0][0] == "detail"


class TestExtractSubreports:
    """Tests for _extract_subreports()."""

    def test_subreport_expression(self):
        root = ET.fromstring(REPORT_WITH_SUBREPORT)
        subreports = _extract_subreports(root)
        assert len(subreports) == 1
        assert "subItems.jasper" in subreports[0]

    def test_no_subreports(self):
        root = ET.fromstring(SIMPLE_REPORT)
        subreports = _extract_subreports(root)
        assert subreports == []


class TestExtractAllExpressions:
    """Tests for _extract_all_expressions()."""

    def test_filters_trivial_expressions(self):
        root = ET.fromstring(SIMPLE_REPORT)
        expressions = _extract_all_expressions(root)
        # $F{name} is trivial and should be filtered out
        texts = [e[1] for e in expressions]
        assert not any(t == "$F{name}" for t in texts)

    def test_keeps_non_trivial_expressions(self):
        root = ET.fromstring(MANY_EXPRESSIONS_REPORT)
        expressions = _extract_all_expressions(root)
        # Should have concatenation, ternary, date format, printWhen
        assert len(expressions) >= 4
        texts = [e[1] for e in expressions]
        assert any("+" in t for t in texts)
        assert any("?" in t for t in texts)

    def test_empty_report(self):
        root = ET.fromstring(MINIMAL_REPORT)
        expressions = _extract_all_expressions(root)
        assert expressions == []


# ────────────────────────────────────────────────
# Overview builder
# ────────────────────────────────────────────────


class TestBuildReportOverview:
    """Tests for _build_report_overview()."""

    def _build(self, xml_str):
        root = ET.fromstring(xml_str)
        report_name = root.get("name", "Test")
        prefix = f"<!-- JRXML: {report_name} (test.jrxml) -->"
        return _build_report_overview(root, prefix, report_name, "test.jrxml")

    def test_contains_context_prefix(self):
        overview = self._build(SIMPLE_REPORT)
        assert "<!-- JRXML: SimpleReport" in overview

    def test_contains_report_name(self):
        overview = self._build(SIMPLE_REPORT)
        assert "JasperReport: SimpleReport" in overview

    def test_contains_page_dimensions(self):
        overview = self._build(SIMPLE_REPORT)
        assert "595x842" in overview

    def test_contains_parameters(self):
        overview = self._build(SIMPLE_REPORT)
        assert "Parameters (2)" in overview
        assert "title : String" in overview
        assert "startDate : Date" in overview

    def test_contains_fields(self):
        overview = self._build(SIMPLE_REPORT)
        assert "Fields (3)" in overview
        assert "id : Long" in overview
        assert "name : String" in overview
        assert "amount : BigDecimal" in overview

    def test_contains_bands(self):
        overview = self._build(REPORT_WITH_MANY_BANDS)
        assert "Bands (7)" in overview
        assert "Title: height=50" in overview
        assert "Detail: height=20" in overview

    def test_contains_groups(self):
        overview = self._build(REPORT_WITH_GROUPS)
        assert "Groups (1)" in overview
        assert "CategoryGroup" in overview

    def test_contains_subreports(self):
        overview = self._build(REPORT_WITH_SUBREPORT)
        assert "Subreports (1)" in overview
        assert "subItems.jasper" in overview

    def test_contains_variables(self):
        overview = self._build(REPORT_WITH_GROUPS)
        assert "Variables" in overview
        assert "categoryTotal" in overview

    def test_minimal_report_overview(self):
        overview = self._build(MINIMAL_REPORT)
        assert "JasperReport: Minimal" in overview
        assert "Parameters" not in overview
        assert "Fields" not in overview


# ────────────────────────────────────────────────
# Expressions builder
# ────────────────────────────────────────────────


class TestBuildExpressionsChunk:
    """Tests for _build_expressions_chunk()."""

    def test_groups_by_type(self):
        expressions = [
            ("textFieldExpression", '$F{a} + " - " + $F{b}'),
            ("textFieldExpression", '$F{x} > 0 ? "Y" : "N"'),
            ("printWhenExpression", "$F{b} != null"),
        ]
        prefix = "<!-- JRXML: Test (test.jrxml) -->"
        result = _build_expressions_chunk(expressions, prefix)
        assert "textField (2)" in result
        assert "printWhen (1)" in result

    def test_contains_context_prefix(self):
        expressions = [("textFieldExpression", "expr1")]
        prefix = "<!-- JRXML: TestReport (test.jrxml) -->"
        result = _build_expressions_chunk(expressions, prefix)
        assert result.startswith("<!-- JRXML: TestReport")


# ────────────────────────────────────────────────
# JRXMLFileReader — class attributes
# ────────────────────────────────────────────────


class TestJRXMLFileReaderAttributes:
    """Tests for JRXMLFileReader class attributes."""

    def test_min_chunk_size(self):
        reader = JRXMLFileReader()
        assert reader.MIN_CHUNK_SIZE == 20

    def test_is_base_file_reader(self):
        from shared.readers._base import BaseFileReader

        reader = JRXMLFileReader()
        assert isinstance(reader, BaseFileReader)


# ────────────────────────────────────────────────
# JRXMLFileReader — load_data() with real temp files
# ────────────────────────────────────────────────


class TestJRXMLFileReaderLoadData:
    """Tests for JRXMLFileReader.load_data() using temporary files."""

    @pytest.fixture
    def reader(self):
        return JRXMLFileReader()

    def _write_jrxml(self, tmp_path, content, filename="report.jrxml"):
        f = tmp_path / filename
        f.write_text(content, encoding="utf-8")
        return f

    def test_simple_report_produces_chunks(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, SIMPLE_REPORT)
        docs = reader.load_data(f)
        assert len(docs) >= 1
        assert docs[0].metadata["node_type"] == "jrxml_report_overview"

    def test_simple_report_has_expressions_chunk(self, reader, tmp_path):
        """Report with non-trivial expressions should produce expressions chunk."""
        f = self._write_jrxml(tmp_path, MANY_EXPRESSIONS_REPORT)
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]
        assert "jrxml_report_overview" in node_types
        assert "jrxml_expressions" in node_types

    def test_minimal_report_no_expressions_chunk(self, reader, tmp_path):
        """Minimal report with no expressions should only have overview."""
        f = self._write_jrxml(tmp_path, MINIMAL_REPORT)
        docs = reader.load_data(f)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "jrxml_report_overview"

    def test_metadata_fields(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, SIMPLE_REPORT, "myReport.jrxml")
        docs = reader.load_data(f)
        meta = docs[0].metadata
        assert meta["unit_name"] == "myReport"
        assert meta["report_name"] == "SimpleReport"
        assert meta["node_type"] == "jrxml_report_overview"
        assert "start_line" in meta
        assert "end_line" in meta
        assert "creation_datetime" in meta
        assert "modification_datetime" in meta

    def test_empty_file_returns_empty(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, "")
        docs = reader.load_data(f)
        assert docs == []

    def test_whitespace_only_returns_empty(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, "   \n\n  ")
        docs = reader.load_data(f)
        assert docs == []

    def test_xml_parse_error_returns_full_file(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, INVALID_XML)
        docs = reader.load_data(f)
        assert len(docs) == 1
        meta = docs[0].metadata
        assert meta["node_type"] == "full_file"
        assert "parse_error" in meta

    def test_extra_info_merged(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, MINIMAL_REPORT)
        extra = {"project": "test", "branch": "main"}
        docs = reader.load_data(f, extra_info=extra)
        meta = docs[0].metadata
        assert meta["project"] == "test"
        assert meta["branch"] == "main"

    def test_context_prefix_in_text(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, SIMPLE_REPORT, "invoice.jrxml")
        docs = reader.load_data(f)
        text = docs[0].text
        assert text.startswith("<!-- JRXML: SimpleReport (invoice.jrxml)")

    def test_report_with_subreport(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, REPORT_WITH_SUBREPORT)
        docs = reader.load_data(f)
        text = docs[0].text
        assert "Subreports" in text
        assert "subItems.jasper" in text

    def test_report_with_groups(self, reader, tmp_path):
        f = self._write_jrxml(tmp_path, REPORT_WITH_GROUPS)
        docs = reader.load_data(f)
        text = docs[0].text
        assert "Groups" in text
        assert "CategoryGroup" in text


# ────────────────────────────────────────────────
# JRXMLFileReader — load_nodes() (TextNode output)
# ────────────────────────────────────────────────


class TestJRXMLFileReaderLoadNodes:
    """Tests for load_nodes() — TextNode conversion."""

    @pytest.fixture
    def reader(self):
        return JRXMLFileReader()

    def test_returns_text_nodes(self, reader, tmp_path):
        from llama_index.core.schema import TextNode

        f = tmp_path / "test.jrxml"
        f.write_text(SIMPLE_REPORT, encoding="utf-8")
        nodes = reader.load_nodes(f)
        assert len(nodes) >= 1
        assert all(isinstance(n, TextNode) for n in nodes)

    def test_metadata_preserved(self, reader, tmp_path):
        f = tmp_path / "test.jrxml"
        f.write_text(SIMPLE_REPORT, encoding="utf-8")
        nodes = reader.load_nodes(f)
        meta = nodes[0].metadata
        assert meta["node_type"] == "jrxml_report_overview"
        assert meta["report_name"] == "SimpleReport"
