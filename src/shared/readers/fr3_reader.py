"""
FastReport template reader (.fr3) using XML parsing.

Extracts report structure, band content with memo texts and data bindings,
Pascal scripts, and variables from FastReport .fr3 XML files.

Chunking strategy:
- One fr3_report_overview chunk per file: report name, pages, bands, memo counts,
  data source bindings, variables — provides "what is this report?" context.
- One fr3_band_content chunk per band: all TfrxMemoView texts grouped together
  with band type context. Bands are the natural grouping unit (2-21 memos each).
- One fr3_pascal_script chunk if the report contains embedded PascalScript.
- One fr3_variables chunk if the report defines variables.
- Context prefix on every chunk: // Report: <stem> (<filename>)
"""

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from llama_index.core import Document
from llama_index.core.schema import TextNode

from shared.readers._base import BaseFileReader, get_file_datetime, node_from_doc
from shared.log import log_warn


# ────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────

# FastReport band element tag names (direct children of TfrxReportPage)
_BAND_TAGS = frozenset(
    {
        "TfrxPageHeader",
        "TfrxPageFooter",
        "TfrxReportTitle",
        "TfrxReportSummary",
        "TfrxMasterData",
        "TfrxDetailData",
        "TfrxGroupHeader",
        "TfrxGroupFooter",
        "TfrxColumnHeader",
        "TfrxColumnFooter",
        "TfrxOverlay",
        "TfrxChild",
        "TfrxHeader",
        "TfrxFooter",
    }
)

# Human-readable band type names
_BAND_TYPE_NAMES: Dict[str, str] = {
    "TfrxPageHeader": "PageHeader",
    "TfrxPageFooter": "PageFooter",
    "TfrxReportTitle": "ReportTitle",
    "TfrxReportSummary": "ReportSummary",
    "TfrxMasterData": "MasterData",
    "TfrxDetailData": "DetailData",
    "TfrxGroupHeader": "GroupHeader",
    "TfrxGroupFooter": "GroupFooter",
    "TfrxColumnHeader": "ColumnHeader",
    "TfrxColumnFooter": "ColumnFooter",
    "TfrxOverlay": "Overlay",
    "TfrxChild": "ChildBand",
    "TfrxHeader": "Header",
    "TfrxFooter": "Footer",
}

MIN_CHUNK_SIZE = 40  # Skip chunks smaller than this (chars of actual content)


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _context_prefix(file_name: str, report_stem: str) -> str:
    """Build context prefix line for a chunk."""
    return f"// Report: {report_stem} ({file_name})"


def _decode_text(raw: str) -> str:
    """Decode HTML entities in FR3 text attributes (&#13;&#10; -> newlines, etc.)."""
    return html.unescape(raw).replace("\r\n", "\n").replace("\r", "\n")


def _extract_memo_text(memo_elem: ET.Element) -> Tuple[str, str]:
    """Extract memo name and decoded text from a TfrxMemoView element.

    Returns:
        (name, text) tuple. Text may be empty.
    """
    name = memo_elem.get("Name", "")
    raw_text = memo_elem.get("Text", "")
    text = _decode_text(raw_text).strip() if raw_text else ""
    return name, text


def _extract_all_memos(parent: ET.Element) -> List[Tuple[str, str]]:
    """Recursively find all TfrxMemoView elements under parent.

    Returns list of (name, text) tuples, including nested ones (e.g. in sub-bands).
    """
    memos: List[Tuple[str, str]] = []
    for elem in parent.iter("TfrxMemoView"):
        name, text = _extract_memo_text(elem)
        if name or text:
            memos.append((name, text))
    return memos


def _classify_memo_text(text: str) -> str:
    """Classify a memo text as label, data_binding, aggregation, or expression."""
    if not text:
        return "empty"
    if (
        text.startswith("[SUM(")
        or text.startswith("[COUNT(")
        or text.startswith("[AVG(")
    ):
        return "aggregation"
    if text.startswith("[") and "." in text and text.endswith("]"):
        return "data_binding"
    if text.startswith("[") and text.endswith("]"):
        return "expression"
    return "label"


def _format_memo_line(name: str, text: str) -> str:
    """Format a single memo as a readable line for the chunk."""
    kind = _classify_memo_text(text)
    if text:
        if kind == "data_binding":
            return f"  {name}: {text}  (data binding)"
        elif kind == "aggregation":
            return f"  {name}: {text}  (aggregation)"
        elif kind == "expression":
            return f"  {name}: {text}  (expression)"
        else:
            return f'  {name}: "{text}"'
    return f"  {name}"


def _band_description(band_elem: ET.Element) -> str:
    """Build a human-readable description of a band element."""
    tag = band_elem.tag
    band_type = _BAND_TYPE_NAMES.get(tag, tag)
    name = band_elem.get("Name", "")

    parts = [f"{band_type} band"]
    if name:
        parts[0] = f'{band_type} band "{name}"'

    # Dataset info
    ds_name = band_elem.get("DataSetName", "")
    if ds_name:
        parts.append(f"DataSet={ds_name}")

    # DrillDown
    drill = band_elem.get("DrillDown", "")
    if drill.lower() == "true":
        parts.append("DrillDown=True")

    # Condition (for group headers)
    condition = band_elem.get("Condition", "")
    if condition:
        decoded = _decode_text(condition)
        parts.append(f"Condition={decoded}")

    return ", ".join(parts)


# ────────────────────────────────────────────────
# Reader
# ────────────────────────────────────────────────


class FR3Reader(BaseFileReader):
    """
    Extracts structured chunks from FastReport .fr3 XML files.

    Produces:
    - fr3_report_overview: one per file, summarizes report structure
    - fr3_band_content: one per band, groups all memo texts within a band
    - fr3_pascal_script: embedded PascalScript code
    - fr3_variables: report variables (if any)
    """

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents: List[Document] = []
        content: Optional[str] = None
        file_path_str = str(file)
        file_name = file.name
        report_stem = file.stem

        # ── Parse XML ──
        try:
            # Try utf-8-sig first (handles BOM), then utf-8
            try:
                with open(file, "r", encoding="utf-8-sig") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            root = ET.fromstring(content)
        except ET.ParseError as e:
            log_warn(f"XML parse error for {file}: {e}")
            if content:
                documents.append(
                    Document(
                        text=content[:5000],
                        metadata={
                            "file_path": file_path_str,
                            "node_type": "raw_fr3",
                            "parse_error": str(e),
                            **get_file_datetime(file),
                        },
                    )
                )
            return documents
        except Exception as e:
            log_warn(f"Could not read {file}: {e}")
            return []

        file_datetime = get_file_datetime(file)
        prefix = _context_prefix(file_name, report_stem)

        # ── Collect structural info for overview ──
        overview_lines: List[str] = [prefix]

        # Report-level attributes
        version = root.get("Version", "")
        script_lang = root.get("ScriptLanguage", "")
        description_raw = root.get("ReportOptions.Description.Text", "")
        description = _decode_text(description_raw).strip() if description_raw else ""

        overview_lines.append(
            f"FastReport template: {report_stem}"
            + (f" (v{version})" if version else "")
        )
        if description:
            overview_lines.append(f"Description: {description}")

        # ── Find all pages ──
        pages = root.findall("TfrxReportPage")
        if not pages:
            # Try as children of root (some FR3 files nest differently)
            pages = [child for child in root if child.tag == "TfrxReportPage"]

        overview_lines.append(f"Pages: {len(pages)}")

        band_chunks: List[Document] = []
        all_band_summaries: List[str] = []
        all_data_bindings: List[str] = []

        for page_idx, page in enumerate(pages):
            page_name = page.get("Name", f"Page{page_idx + 1}")
            orientation = page.get("Orientation", "")

            if len(pages) > 1:
                overview_lines.append(
                    f'  Page "{page_name}"'
                    + (f" ({orientation})" if orientation else "")
                )

            # ── Process bands within this page ──
            for child in page:
                if child.tag not in _BAND_TAGS:
                    continue

                band_desc = _band_description(child)
                memos = _extract_all_memos(child)

                # Collect data bindings for overview
                for memo_name, memo_text in memos:
                    kind = _classify_memo_text(memo_text)
                    if kind in ("data_binding", "aggregation"):
                        all_data_bindings.append(memo_text)

                # Band summary for overview
                band_summary = f"  {band_desc}: {len(memos)} memo views"
                all_band_summaries.append(band_summary)

                # ── Build band content chunk ──
                if memos:
                    chunk_lines = [prefix]
                    chunk_lines.append(f"// Band: {band_desc}")
                    chunk_lines.append("")

                    labels: List[str] = []
                    bindings: List[str] = []
                    aggregations: List[str] = []

                    for memo_name, memo_text in memos:
                        chunk_lines.append(_format_memo_line(memo_name, memo_text))
                        kind = _classify_memo_text(memo_text)
                        if kind == "label" and memo_text:
                            labels.append(memo_text)
                        elif kind == "data_binding":
                            bindings.append(memo_text)
                        elif kind == "aggregation":
                            aggregations.append(memo_text)

                    chunk_text = "\n".join(chunk_lines)

                    if len(chunk_text.strip()) >= MIN_CHUNK_SIZE:
                        band_chunks.append(
                            Document(
                                text=chunk_text,
                                metadata={
                                    "file_path": file_path_str,
                                    "node_type": "fr3_band_content",
                                    "unit_name": report_stem,
                                    "band_type": _BAND_TYPE_NAMES.get(
                                        child.tag, child.tag
                                    ),
                                    "band_name": child.get("Name", ""),
                                    "memo_count": len(memos),
                                    "label_count": len(labels),
                                    "binding_count": len(bindings),
                                    **file_datetime,
                                },
                            )
                        )

        # ── Finish overview ──
        if all_band_summaries:
            overview_lines.append("Bands:")
            overview_lines.extend(all_band_summaries)

        # Unique data sources referenced
        data_sources = set()
        for binding in all_data_bindings:
            # Extract dataset name from [DataSet."Field"] or [SUM(<DataSet."Field">)]
            stripped = binding.strip("[]")
            if stripped.startswith("SUM(") or stripped.startswith("COUNT("):
                # Remove function wrapper: SUM(<DataSet."Field">) -> DataSet."Field"
                inner = stripped.split("(", 1)[1].rstrip(")")
                inner = inner.strip("<>")
            else:
                inner = stripped
            if "." in inner:
                ds = inner.split(".")[0]
                data_sources.add(ds)

        if data_sources:
            overview_lines.append(f"Data sources: {', '.join(sorted(data_sources))}")

        # Variables
        variables: List[str] = []
        for var in root.findall(".//Variable"):
            var_name = var.get("Name", "")
            var_expression = var.get("Expression", "")
            if var_name:
                var_line = var_name
                if var_expression:
                    var_line += f" = {_decode_text(var_expression)}"
                variables.append(var_line)

        if variables:
            overview_lines.append(f"Variables: {', '.join(variables)}")

        # Script presence
        script_raw = root.get("ScriptText.Text", "")
        script_text = _decode_text(script_raw).strip() if script_raw else ""
        has_script = bool(script_text) and not re.fullmatch(
            r"begin\s*end\.", script_text
        )
        if has_script:
            # Count procedures in script
            proc_count = script_text.lower().count("procedure ")
            func_count = script_text.lower().count("function ")
            script_desc = f"Embedded PascalScript"
            if proc_count or func_count:
                parts = []
                if proc_count:
                    parts.append(f"{proc_count} procedure(s)")
                if func_count:
                    parts.append(f"{func_count} function(s)")
                script_desc += f" with {', '.join(parts)}"
            overview_lines.append(script_desc)

        # ── Emit overview chunk ──
        overview_text = "\n".join(overview_lines)
        if len(overview_text.strip()) >= MIN_CHUNK_SIZE:
            documents.append(
                Document(
                    text=overview_text,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "fr3_report_overview",
                        "unit_name": report_stem,
                        "page_count": len(pages),
                        "band_count": len(all_band_summaries),
                        "has_script": has_script,
                        **file_datetime,
                    },
                )
            )

        # ── Emit band chunks ──
        documents.extend(band_chunks)

        # ── Emit Pascal script chunk ──
        if has_script:
            script_chunk = prefix + "\n// Embedded PascalScript\n\n" + script_text
            documents.append(
                Document(
                    text=script_chunk,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "fr3_pascal_script",
                        "unit_name": report_stem,
                        "script_language": script_lang,
                        **file_datetime,
                    },
                )
            )

        # ── Emit variables chunk (grouped) ──
        if variables:
            var_text = prefix + "\n// Report Variables\n\n"
            var_text += "\n".join(f"  {v}" for v in variables)
            if len(var_text.strip()) >= MIN_CHUNK_SIZE:
                documents.append(
                    Document(
                        text=var_text,
                        metadata={
                            "file_path": file_path_str,
                            "node_type": "fr3_variables",
                            "unit_name": report_stem,
                            "variable_count": len(variables),
                            **file_datetime,
                        },
                    )
                )

        # ── Fallback if nothing extracted ──
        if not documents and content:
            documents.append(
                Document(
                    text=content[:8000],
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "raw_fr3",
                        "unit_name": report_stem,
                        **file_datetime,
                    },
                )
            )

        return documents

    def load_nodes(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[TextNode]:
        """Parse FR3 file and return TextNodes ready for indexing."""
        docs = self.load_data(file, extra_info)
        return [node_from_doc(doc) for doc in docs]
