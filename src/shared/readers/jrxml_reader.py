"""
JasperReports template reader (.jrxml) using XML parsing.

Extracts report structure, parameters, fields, variables, and expressions
from JasperReports .jrxml XML files.

Chunking strategy:
    1. **Report overview chunk** (``jrxml_report_overview``): A compact, searchable
       summary of the report including:
       - Report name and page dimensions
       - All parameter names and types
       - All field names and types (the data model)
       - Variables with their expressions
       - Which bands are present (title, detail, summary, etc.)
       - Subreport references

    2. **Expressions chunk** (``jrxml_expressions``): All non-trivial expressions
       extracted from textField, printWhen, image, and variable expressions.
       This captures business logic embedded in the report layout.

    Only the report overview is emitted for small reports.  The expressions
    chunk is emitted when the file contains enough meaningful expressions.

    Context prefix on every chunk: ``<!-- JRXML: ReportName (filename.jrxml) -->``

Node types emitted:
    jrxml_report_overview, jrxml_expressions, full_file
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from llama_index.core import Document

from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding_and_bytes,
)
from shared.log import log_warn


# ────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────

# JasperReports XML namespace
_NS = "{http://jasperreports.sourceforge.net/jasperreports}"

# Band section tags in report order
_BAND_SECTIONS = [
    "title",
    "pageHeader",
    "columnHeader",
    "detail",
    "columnFooter",
    "pageFooter",
    "lastPageFooter",
    "summary",
    "noData",
    "background",
]

# Human-readable names
_BAND_NAMES: Dict[str, str] = {
    "title": "Title",
    "pageHeader": "Page Header",
    "columnHeader": "Column Header",
    "detail": "Detail",
    "columnFooter": "Column Footer",
    "pageFooter": "Page Footer",
    "lastPageFooter": "Last Page Footer",
    "summary": "Summary",
    "noData": "No Data",
    "background": "Background",
}

# Expression tags to extract
_EXPRESSION_TAGS = [
    "textFieldExpression",
    "printWhenExpression",
    "imageExpression",
    "variableExpression",
    "initialValueExpression",
    "groupExpression",
    "filterExpression",
    "connectionExpression",
    "dataSourceExpression",
]

# Minimum number of non-trivial expressions to emit an expressions chunk
_MIN_EXPRESSIONS_FOR_CHUNK = 3

# Trivial expression pattern: just a field/param reference like $F{name} or $P{x}
_TRIVIAL_EXPR_RE = re.compile(r"^\$[FPV]\{[^}]+\}$")


# ────────────────────────────────────────────────
# XML parsing helpers
# ────────────────────────────────────────────────


def _find_ns(tag: str, root: ET.Element) -> str:
    """Build a namespace-qualified tag.

    Handles both namespace-prefixed and bare JRXML files.
    """
    return f"{_NS}{tag}"


def _get_text(elem: Optional[ET.Element]) -> str:
    """Get text content of an element, stripped."""
    if elem is None:
        return ""
    return (elem.text or "").strip()


def _short_class_name(fqn: str) -> str:
    """java.lang.String → String."""
    return fqn.rsplit(".", 1)[-1] if "." in fqn else fqn


# ────────────────────────────────────────────────
# Report analysis
# ────────────────────────────────────────────────


def _extract_parameters(root: ET.Element) -> List[Tuple[str, str, str]]:
    """Extract parameters as (name, type, default_expr) tuples."""
    params = []
    for p in root.findall(f"{_NS}parameter"):
        name = p.get("name", "?")
        ptype = _short_class_name(p.get("class", "?"))
        default = _get_text(p.find(f"{_NS}defaultValueExpression"))
        params.append((name, ptype, default))
    return params


def _extract_fields(root: ET.Element) -> List[Tuple[str, str]]:
    """Extract fields as (name, type) tuples."""
    fields = []
    for f in root.findall(f"{_NS}field"):
        name = f.get("name", "?")
        ftype = _short_class_name(f.get("class", "?"))
        fields.append((name, ftype))
    return fields


def _extract_variables(root: ET.Element) -> List[Tuple[str, str, str, str]]:
    """Extract variables as (name, type, calculation, expression) tuples."""
    variables = []
    for v in root.findall(f"{_NS}variable"):
        name = v.get("name", "?")
        vtype = _short_class_name(v.get("class", "?"))
        calc = v.get("calculation", "")
        expr = _get_text(v.find(f"{_NS}variableExpression"))
        variables.append((name, vtype, calc, expr))
    return variables


def _extract_groups(root: ET.Element) -> List[Tuple[str, str]]:
    """Extract groups as (name, expression) tuples."""
    groups = []
    for g in root.findall(f"{_NS}group"):
        name = g.get("name", "?")
        expr = _get_text(g.find(f"{_NS}groupExpression"))
        groups.append((name, expr))
    return groups


def _extract_bands(root: ET.Element) -> List[Tuple[str, int, int]]:
    """Extract bands as (section_name, height, element_count) tuples."""
    bands = []
    for section in _BAND_SECTIONS:
        elem = root.find(f"{_NS}{section}")
        if elem is not None:
            band = elem.find(f"{_NS}band")
            if band is not None:
                height = int(band.get("height", "0") or "0")
                n_elements = len(list(band))
                bands.append((section, height, n_elements))
    return bands


def _extract_subreports(root: ET.Element) -> List[str]:
    """Extract subreport expressions (referenced sub-report file paths)."""
    subreports = []
    for sr in root.iter(f"{_NS}subreport"):
        expr_elem = sr.find(f"{_NS}subreportExpression")
        if expr_elem is not None and expr_elem.text:
            subreports.append(expr_elem.text.strip())
    return subreports


def _extract_all_expressions(
    root: ET.Element,
) -> List[Tuple[str, str]]:
    """Extract all expressions as (tag, text) tuples.

    Filters out trivial single-reference expressions.
    """
    expressions = []
    for tag in _EXPRESSION_TAGS:
        for elem in root.iter(f"{_NS}{tag}"):
            text = (elem.text or "").strip()
            if not text:
                continue
            # Skip trivial single references
            if _TRIVIAL_EXPR_RE.match(text):
                continue
            expressions.append((tag, text))
    return expressions


# ────────────────────────────────────────────────
# Overview and expressions builders
# ────────────────────────────────────────────────


def _build_report_overview(
    root: ET.Element,
    context_prefix: str,
    report_name: str,
    file_name: str,
) -> str:
    """Build a human-readable report overview."""
    page_width = root.get("pageWidth", "?")
    page_height = root.get("pageHeight", "?")
    orientation = root.get("orientation", "Portrait")
    is_title_new_page = root.get("isTitleNewPage", "false")

    params = _extract_parameters(root)
    fields = _extract_fields(root)
    variables = _extract_variables(root)
    groups = _extract_groups(root)
    bands = _extract_bands(root)
    subreports = _extract_subreports(root)

    lines = [context_prefix]

    # Header
    lines.append(f"// JasperReport: {report_name}")
    lines.append(f"//   file: {file_name}")
    lines.append(f"//   page: {page_width}x{page_height} ({orientation})")
    if is_title_new_page == "true":
        lines.append("//   title on new page: yes")
    lines.append("")

    # Parameters
    if params:
        lines.append(f"// Parameters ({len(params)}):")
        for name, ptype, default in params:
            parts = [f"{name} : {ptype}"]
            if default:
                parts.append(f"= {default}")
            lines.append(f"//   {' '.join(parts)}")
        lines.append("")

    # Fields (the data model — most important for search)
    if fields:
        lines.append(f"// Fields ({len(fields)}):")
        for name, ftype in fields:
            lines.append(f"//   {name} : {ftype}")
        lines.append("")

    # Variables
    if variables:
        # Split into JR built-in vs user-defined
        builtin = [
            v
            for v in variables
            if v[0].startswith("PAGE_")
            or v[0].startswith("COLUMN_")
            or v[0].startswith("REPORT_")
        ]
        user_vars = [v for v in variables if v not in builtin]

        if user_vars:
            lines.append(f"// Variables ({len(user_vars)}):")
            for name, vtype, calc, expr in user_vars:
                parts = [f"{name} : {vtype}"]
                if calc:
                    parts.append(f"({calc})")
                if expr:
                    parts.append(f"= {expr}")
                lines.append(f"//   {' '.join(parts)}")
            lines.append("")

    # Groups
    if groups:
        lines.append(f"// Groups ({len(groups)}):")
        for name, expr in groups:
            if expr:
                lines.append(f"//   {name}: {expr}")
            else:
                lines.append(f"//   {name}")
        lines.append("")

    # Bands
    if bands:
        lines.append(f"// Bands ({len(bands)}):")
        for section, height, n_elements in bands:
            display = _BAND_NAMES.get(section, section)
            lines.append(f"//   {display}: height={height}, elements={n_elements}")
        lines.append("")

    # Subreports
    if subreports:
        lines.append(f"// Subreports ({len(subreports)}):")
        for sr_expr in subreports:
            lines.append(f"//   {sr_expr}")
        lines.append("")

    return "\n".join(lines)


def _build_expressions_chunk(
    expressions: List[Tuple[str, str]],
    context_prefix: str,
) -> str:
    """Build an expressions chunk with all non-trivial expressions."""
    lines = [context_prefix]
    lines.append("// Report expressions (non-trivial)")
    lines.append("")

    # Group by expression type
    by_type: Dict[str, List[str]] = {}
    for tag, text in expressions:
        short_tag = tag.replace("Expression", "")
        by_type.setdefault(short_tag, []).append(text)

    for etype, exprs in by_type.items():
        lines.append(f"// {etype} ({len(exprs)}):")
        for expr in exprs:
            # Normalize whitespace in multi-line expressions
            clean = " ".join(expr.split())
            lines.append(f"//   {clean}")
        lines.append("")

    return "\n".join(lines)


# ────────────────────────────────────────────────
# JRXML File Reader
# ────────────────────────────────────────────────


class JRXMLFileReader(BaseFileReader):
    """Structured reader for JasperReports template (.jrxml) files.

    Produces 1-2 chunks per file:
    - ``jrxml_report_overview``: Human-readable report structure summary
    - ``jrxml_expressions``: Non-trivial expressions (business logic)
    """

    MIN_CHUNK_SIZE = 20

    def load_data(
        self,
        file: Path,
        extra_info: Optional[dict] = None,
    ) -> List[Document]:
        """Load and parse a JRXML file."""
        content, content_bytes = read_file_with_encoding_and_bytes(file)

        if not content.strip():
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)
        file_name = file.name
        report_stem = file.stem

        # Parse XML
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            log_warn(f"XML parse error in {file}: {e}")
            return [
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "parse_error": str(e),
                        "unit_name": report_stem,
                        **file_datetime,
                    },
                )
            ]

        # Extract report name (from XML attribute, falls back to filename stem)
        report_name = root.get("name", report_stem)

        context_prefix = f"<!-- JRXML: {report_name} ({file_name}) -->"

        # Build overview
        overview = _build_report_overview(root, context_prefix, report_name, file_name)

        documents: List[Document] = []

        # Base metadata (shared across chunks)
        base_metadata = {
            "file_path": file_path_str,
            "node_type": "jrxml_report_overview",
            "unit_name": report_stem,
            "report_name": report_name,
            "start_line": 1,
            "end_line": content.count("\n") + 1,
            "start_byte": 0,
            "end_byte": len(content_bytes),
            **file_datetime,
        }
        if extra_info:
            base_metadata.update(extra_info)

        documents.append(Document(text=overview, metadata=base_metadata))

        # Expressions chunk (only if enough non-trivial expressions)
        expressions = _extract_all_expressions(root)
        if len(expressions) >= _MIN_EXPRESSIONS_FOR_CHUNK:
            expr_text = _build_expressions_chunk(expressions, context_prefix)
            expr_metadata = {
                **base_metadata,
                "node_type": "jrxml_expressions",
            }
            documents.append(Document(text=expr_text, metadata=expr_metadata))

        return documents
