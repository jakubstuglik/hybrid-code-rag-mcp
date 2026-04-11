"""
Hibernate Mapping (.hbm.xml) file reader.

Produces structured chunks from Hibernate HBM XML mapping files,
which define the ORM mapping between Java entity classes and database tables.

Chunking strategy:
    1. **Entity overview chunk** (``hbm_entity_overview``): A compact, human-readable
       summary of the entity mapping, including:
       - Java class name (short + fully-qualified)
       - Database table name
       - Primary key strategy (sequence ID, composite-id, or bare ID)
       - Property → column mappings with types and constraints
       - Collection associations (set, bag, list, map)
       - Soft-delete pattern (sql-delete statement)
       - Applied filters
       - Version/optimistic-locking column

    2. **Raw mapping chunk** (``hbm_raw_mapping``): Emitted only for large files
       (> MAX_OVERVIEW_CHARS) — the full XML content with context prefix. This
       enables precise property/column name lookups.

    Context prefix on every chunk: ``<!-- HBM: ClassName (TableName) -->``

Node types emitted:
    hbm_entity_overview, hbm_raw_mapping, full_file
"""

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
# XML parsing helpers
# ────────────────────────────────────────────────


def _strip_doctype(content: str) -> str:
    """Remove DOCTYPE declaration that causes ET.fromstring to fail.

    Hibernate HBM files use a DTD reference that Python's XML parser
    cannot resolve, causing a parse error. We strip it since we don't
    need DTD validation.
    """
    import re

    return re.sub(r"<!DOCTYPE[^>]*>", "", content, count=1)


def _short_class_name(fqn: str) -> str:
    """Extract short class name from fully-qualified name.

    ``com.example.app.persistence.dbo.impl.PHStop`` → ``PHStop``
    """
    return fqn.rsplit(".", 1)[-1] if "." in fqn else fqn


def _attr(elem: ET.Element, name: str, default: str = "") -> str:
    """Get attribute value with default."""
    return elem.get(name, default)


# ────────────────────────────────────────────────
# Entity analysis
# ────────────────────────────────────────────────


def _extract_id_info(class_elem: ET.Element) -> Tuple[str, List[str]]:
    """Extract primary key information.

    Returns:
        (strategy_description, key_column_names)
    """
    # Simple ID
    id_elem = class_elem.find("id")
    if id_elem is not None:
        id_name = _attr(id_elem, "name", "?")
        id_col = _attr(id_elem, "column", "")
        # Column might be nested
        if not id_col:
            col_elem = id_elem.find("column")
            if col_elem is not None:
                id_col = _attr(col_elem, "name", "")

        # Generator
        gen_elem = id_elem.find("generator")
        if gen_elem is not None:
            gen_class = _attr(gen_elem, "class", "")
            gen_short = gen_class.rsplit(".", 1)[-1] if "." in gen_class else gen_class
            param_elem = gen_elem.find("param")
            seq_name = (
                param_elem.text.strip()
                if param_elem is not None and param_elem.text
                else ""
            )
            if seq_name:
                return (
                    f"sequence ID ({gen_short}, seq={seq_name})",
                    [id_col or id_name],
                )
            return (f"sequence ID ({gen_short})", [id_col or id_name])
        return (f"simple ID", [id_col or id_name])

    # Composite ID
    comp_elem = class_elem.find("composite-id")
    if comp_elem is not None:
        key_cols = []
        for kp in comp_elem.findall("key-property"):
            col = _attr(kp, "column", _attr(kp, "name", "?"))
            key_cols.append(col)
        return (f"composite-id ({len(key_cols)} columns)", key_cols)

    return ("unknown", [])


def _extract_properties(
    class_elem: ET.Element,
) -> List[Dict[str, str]]:
    """Extract property mappings."""
    props = []
    for prop in class_elem.findall("property"):
        name = _attr(prop, "name")
        column = _attr(prop, "column", name.upper())
        not_null = _attr(prop, "not-null", "")
        prop_type = _attr(prop, "type", "")
        read_only = (
            _attr(prop, "update") == "false" and _attr(prop, "insert") == "false"
        )
        formula = _attr(prop, "formula", "")

        info: Dict[str, str] = {"name": name, "column": column}
        if not_null == "true":
            info["not_null"] = "true"
        if prop_type:
            info["type"] = prop_type
        if read_only:
            info["read_only"] = "true"
        if formula:
            info["formula"] = formula
        props.append(info)
    return props


def _extract_collections(
    class_elem: ET.Element,
) -> List[Dict[str, str]]:
    """Extract collection associations (set, bag, list, map)."""
    collections = []
    for tag in ("set", "bag", "list", "map"):
        for elem in class_elem.findall(tag):
            coll_name = _attr(elem, "name")
            coll_table = _attr(elem, "table", "")
            cascade = _attr(elem, "cascade", "")
            fetch = _attr(elem, "fetch", "")
            where = _attr(elem, "where", "")

            # Key column
            key_elem = elem.find("key")
            key_col = _attr(key_elem, "column", "") if key_elem is not None else ""

            # Target entity or element type
            otm = elem.find("one-to-many")
            el = elem.find("element")
            mk = elem.find("map-key")

            info: Dict[str, str] = {
                "type": tag,
                "name": coll_name,
            }
            if coll_table:
                info["table"] = coll_table
            if key_col:
                info["key_column"] = key_col
            if otm is not None:
                info["target_class"] = _short_class_name(_attr(otm, "class", ""))
            if el is not None:
                info["element_type"] = _attr(el, "type", "")
                el_col = _attr(el, "column", "")
                if el_col:
                    info["element_column"] = el_col
            if mk is not None:
                info["map_key_column"] = _attr(mk, "column", "")
                info["map_key_type"] = _attr(mk, "type", "")
            if cascade:
                info["cascade"] = cascade
            if fetch:
                info["fetch"] = fetch
            if where:
                info["where"] = where
            collections.append(info)
    return collections


def _extract_filters(class_elem: ET.Element) -> List[str]:
    """Extract filter names."""
    return [_attr(f, "name") for f in class_elem.findall("filter") if _attr(f, "name")]


def _extract_sql_delete(class_elem: ET.Element) -> Optional[str]:
    """Extract sql-delete statement (soft-delete pattern)."""
    sd = class_elem.find("sql-delete")
    if sd is not None and sd.text:
        return sd.text.strip()
    return None


def _extract_version(class_elem: ET.Element) -> Optional[str]:
    """Extract version column for optimistic locking."""
    ver = class_elem.find("version")
    if ver is not None:
        return _attr(ver, "column", _attr(ver, "name", ""))
    return None


# ────────────────────────────────────────────────
# Overview builder
# ────────────────────────────────────────────────


def _build_entity_overview(
    class_elem: ET.Element,
    context_prefix: str,
    default_access: str,
) -> str:
    """Build a human-readable entity overview from the parsed XML."""
    fqn = _attr(class_elem, "name", "?")
    short_name = _short_class_name(fqn)
    table = _attr(class_elem, "table", "?")
    persister = _attr(class_elem, "persister", "")
    where_clause = _attr(class_elem, "where", "")

    id_strategy, key_cols = _extract_id_info(class_elem)
    properties = _extract_properties(class_elem)
    collections = _extract_collections(class_elem)
    filters = _extract_filters(class_elem)
    sql_delete = _extract_sql_delete(class_elem)
    version_col = _extract_version(class_elem)

    lines = [context_prefix]

    # Header
    lines.append(f"// Hibernate entity: {short_name}")
    lines.append(f"//   class: {fqn}")
    lines.append(f"//   table: {table}")
    if where_clause:
        lines.append(f"//   where: {where_clause}")
    lines.append(f"//   access: {default_access}")
    if persister:
        persister_short = _short_class_name(persister)
        lines.append(f"//   persister: {persister_short}")
    lines.append("")

    # ID
    lines.append(f"// Primary key: {id_strategy}")
    if key_cols:
        lines.append(f"//   columns: {', '.join(key_cols)}")
    lines.append("")

    # Version
    if version_col:
        lines.append(f"// Optimistic locking: version column {version_col}")
        lines.append("")

    # Classify properties
    business_props = []
    trace_props = []
    validity_props = []
    read_only_props = []
    formula_props = []

    for p in properties:
        name = p["name"]
        if name.startswith("trace"):
            trace_props.append(p)
        elif name.startswith("valid") and (
            "Timestamp" in name or "From" in name or "To" in name
        ):
            validity_props.append(p)
        elif p.get("formula"):
            formula_props.append(p)
        elif p.get("read_only") and not name.startswith("trace"):
            read_only_props.append(p)
        else:
            business_props.append(p)

    # Business properties
    if business_props:
        lines.append(f"// Properties ({len(business_props)}):")
        for p in business_props:
            parts = [f"{p['name']} → {p['column']}"]
            if p.get("not_null"):
                parts.append("NOT NULL")
            if p.get("type"):
                parts.append(f"type={p['type']}")
            lines.append(f"//   {', '.join(parts)}")
        lines.append("")

    # Read-only properties (from views)
    if read_only_props:
        lines.append(f"// Read-only properties ({len(read_only_props)}):")
        for p in read_only_props:
            parts = [f"{p['name']} → {p['column']}"]
            if p.get("type"):
                parts.append(f"type={p['type']}")
            lines.append(f"//   {', '.join(parts)}")
        lines.append("")

    # Formula properties (PostGIS computed)
    if formula_props:
        lines.append(f"// Computed properties ({len(formula_props)}):")
        for p in formula_props:
            lines.append(f"//   {p['name']} = {p.get('formula', '')}")
        lines.append("")

    # Validity period
    if validity_props:
        col_names = [p["column"] for p in validity_props]
        lines.append(f"// Validity period: {', '.join(col_names)}")
        lines.append("")

    # Trace columns
    if trace_props:
        col_names = [p["column"] for p in trace_props]
        lines.append(f"// Trace columns: {', '.join(col_names)}")
        lines.append("")

    # Collections
    if collections:
        lines.append(f"// Collections ({len(collections)}):")
        for c in collections:
            desc = f"{c['type']} {c['name']}"
            if c.get("table"):
                desc += f" (table={c['table']})"
            if c.get("target_class"):
                desc += f" → {c['target_class']}"
            if c.get("cascade"):
                desc += f" cascade={c['cascade']}"
            if c.get("where"):
                desc += f" where={c['where']}"
            lines.append(f"//   {desc}")
        lines.append("")

    # Soft-delete
    if sql_delete:
        lines.append(f"// Soft-delete: {sql_delete}")
        lines.append("")

    # Filters
    if filters:
        lines.append(f"// Filters: {', '.join(filters)}")

    return "\n".join(lines)


# ────────────────────────────────────────────────
# HBM File Reader
# ────────────────────────────────────────────────


class HBMFileReader(BaseFileReader):
    """Structured reader for Hibernate Mapping (.hbm.xml) files.

    Produces 1-2 chunks per file:
    - ``hbm_entity_overview``: Human-readable entity mapping summary
    - ``hbm_raw_mapping``: Full XML (only for large files)
    """

    MIN_CHUNK_SIZE = 20
    MAX_OVERVIEW_CHARS = 6000  # Above this, also emit raw mapping

    def load_data(
        self,
        file: Path,
        extra_info: Optional[dict] = None,
    ) -> List[Document]:
        """Load and parse an HBM XML file."""
        content, content_bytes = read_file_with_encoding_and_bytes(file)

        if not content.strip():
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)
        file_name = file.name

        # Strip entity class name from filename: PHStop.hbm.xml → PHStop
        entity_stem = file.stem  # "PHStop.hbm"
        if entity_stem.endswith(".hbm"):
            entity_stem = entity_stem[:-4]  # "PHStop"

        # Parse XML
        try:
            cleaned = _strip_doctype(content)
            root = ET.fromstring(cleaned)
        except ET.ParseError as e:
            log_warn(f"XML parse error in {file}: {e}")
            return [
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "parse_error": str(e),
                        "unit_name": entity_stem,
                        **file_datetime,
                    },
                )
            ]

        # Find class element
        class_elem = root.find("class")
        if class_elem is None:
            # No class element — emit as full_file
            return [
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "unit_name": entity_stem,
                        **file_datetime,
                    },
                )
            ]

        # Extract entity info
        fqn = _attr(class_elem, "name", entity_stem)
        short_name = _short_class_name(fqn)
        table = _attr(class_elem, "table", "?")
        default_access = _attr(root, "default-access", "field")

        context_prefix = f"<!-- HBM: {short_name} ({table}) — {file_name} -->"

        # Build overview
        overview = _build_entity_overview(class_elem, context_prefix, default_access)

        documents: List[Document] = []

        # Entity overview (always emitted)
        base_metadata = {
            "file_path": file_path_str,
            "node_type": "hbm_entity_overview",
            "unit_name": entity_stem,
            "class_name": short_name,
            "table_name": table,
            "package_name": fqn.rsplit(".", 1)[0] if "." in fqn else "",
            "start_line": 1,
            "end_line": content.count("\n") + 1,
            "start_byte": 0,
            "end_byte": len(content_bytes),
            **file_datetime,
        }
        if extra_info:
            base_metadata.update(extra_info)

        documents.append(Document(text=overview, metadata=base_metadata))

        # Raw mapping (only for large files where overview loses detail)
        if len(overview) > self.MAX_OVERVIEW_CHARS:
            raw_text = f"{context_prefix}\n{content}"
            raw_metadata = {
                **base_metadata,
                "node_type": "hbm_raw_mapping",
            }
            documents.append(Document(text=raw_text, metadata=raw_metadata))

        return documents
