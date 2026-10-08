"""
Qt Designer form reader (.ui).

Same shape as the DFM reader:

- One form-header chunk for the root widget, its title, and custom widgets.
- One chunk per direct child widget. Nested widgets stay with that parent.
- Consecutive small widgets of the same class are grouped.
- Signal/slot connections are their own chunk.
- Every chunk starts with ``// Form: ClassName (file.ui)``.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional
from xml.etree.ElementTree import Element

from llama_index.core import Document

from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding,
)
from shared.log import log_warn

MIN_CHUNK_SIZE = 20
MAX_GROUP_CHARS = 4000
SMALL_OBJECT_CHARS = 500

# Properties that describe layout pixels, not behaviour or labels.
_SKIP_PROPERTIES = {
    "geometry",
    "sizePolicy",
    "minimumSize",
    "maximumSize",
    "font",
    "palette",
    "iconSize",
    "spacing",
    "margin",
    "leftMargin",
    "topMargin",
    "rightMargin",
    "bottomMargin",
    "frameShadow",
    "frameShape",
    "orientation",
    "sizeHint",
    "cursor",
}

def _local(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _direct_widgets(elem: Element) -> List[Element]:
    """Widgets inside this element, not widgets nested in those widgets."""
    found: List[Element] = []
    for child in list(elem):
        tag = _local(child.tag)
        if tag == "widget":
            found.append(child)
        elif tag in ("layout", "item"):
            found.extend(_direct_widgets(child))
    return found


def _property_lines(elem: Element, indent: str) -> List[str]:
    lines: List[str] = []
    for child in list(elem):
        if _local(child.tag) != "property":
            continue
        name = child.get("name") or ""
        if name in _SKIP_PROPERTIES:
            continue
        for node in child.iter():
            tag = _local(node.tag)
            value = (node.text or "").strip()
            if not value:
                continue
            if tag == "string" or tag in ("enum", "set"):
                lines.append(f"{indent}{name}: {value}")
    return lines


def _render_widget(elem: Element, indent: str = "") -> str:
    widget_class = elem.get("class") or "QWidget"
    name = elem.get("name") or ""
    lines = [f"{indent}widget {widget_class} {name}".rstrip()]
    lines.extend(_property_lines(elem, indent + "  "))
    for child in _direct_widgets(elem):
        rendered = _render_widget(child, indent + "  ")
        if rendered.strip():
            lines.append(rendered)
    return "\n".join(lines)


def _line_of(content: str, name: str) -> int:
    if not name:
        return 1
    needle = f'name="{name}"'
    idx = content.find(needle)
    if idx == -1:
        return 1
    return content.count("\n", 0, idx) + 1


def _context_prefix(file_name: str, form_class: str) -> str:
    return f"// Form: {form_class} ({file_name})"


def _custom_widget_lines(root: Element) -> List[str]:
    lines: List[str] = []
    for custom in root.iter():
        if _local(custom.tag) != "customwidget":
            continue
        class_name = ""
        extends = ""
        header = ""
        for child in list(custom):
            tag = _local(child.tag)
            value = (child.text or "").strip()
            if tag == "class":
                class_name = value
            elif tag == "extends":
                extends = value
            elif tag == "header":
                header = value
        if not class_name:
            continue
        piece = class_name
        if extends:
            piece += f" extends {extends}"
        if header:
            piece += f" ({header})"
        lines.append(piece)
    return lines


def _connection_lines(root: Element) -> List[str]:
    lines: List[str] = []
    for conn in root.iter():
        if _local(conn.tag) != "connection":
            continue
        fields = {}
        for child in list(conn):
            tag = _local(child.tag)
            if tag in ("sender", "signal", "receiver", "slot"):
                fields[tag] = (child.text or "").strip()
        if not fields.get("signal") and not fields.get("slot"):
            continue
        lines.append(
            f"{fields.get('sender', '?')}.{fields.get('signal', '?')} -> "
            f"{fields.get('receiver', '?')}.{fields.get('slot', '?')}"
        )
    return lines


class UiFileReader(BaseFileReader):
    """Reader for Qt Designer .ui files."""

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        try:
            content = read_file_with_encoding(file)
        except Exception as exc:
            log_warn(f"Failed to read {file}: {exc}")
            return []

        if not content.strip():
            return []

        file_path = str(file)
        file_datetime = get_file_datetime(file)
        unit_name = file.stem

        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return [
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path,
                        "node_type": "full_file",
                        "unit_name": unit_name,
                        **file_datetime,
                    },
                )
            ]

        widget = next(
            (child for child in list(root) if _local(child.tag) == "widget"),
            None,
        )
        if widget is None:
            return [
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path,
                        "node_type": "full_file",
                        "unit_name": unit_name,
                        **file_datetime,
                    },
                )
            ]

        form_class = ""
        for child in list(root):
            if _local(child.tag) == "class" and (child.text or "").strip():
                form_class = child.text.strip()
                break
        widget_name = widget.get("name") or form_class or file.stem
        widget_class = widget.get("class") or "QWidget"
        if not form_class:
            form_class = widget_name

        prefix = _context_prefix(file.name, form_class)
        documents: List[Document] = []

        header_lines = [
            f"class: {form_class}",
            f"widget: {widget_class} name={widget_name}",
        ]
        header_lines.extend(_property_lines(widget, ""))
        custom = _custom_widget_lines(root)
        if custom:
            header_lines.append("custom widgets: " + ", ".join(custom))
        header_text = prefix + "\n" + "\n".join(header_lines)
        if len(header_text.strip()) >= MIN_CHUNK_SIZE:
            documents.append(
                self._doc(
                    header_text,
                    "ui_form_header",
                    file_path,
                    unit_name,
                    form_class,
                    widget_name,
                    widget_class,
                    widget_name,
                    widget_class,
                    _line_of(content, widget_name),
                    file_datetime,
                )
            )

        children = _direct_widgets(widget)
        groups = _group_small(children)
        for group in groups:
            if len(group) == 1:
                child = group[0]
                rendered = _render_widget(child)
                chunk = prefix + "\n" + rendered
                if len(chunk.strip()) < MIN_CHUNK_SIZE:
                    continue
                documents.append(
                    self._doc(
                        chunk,
                        "ui_object",
                        file_path,
                        unit_name,
                        form_class,
                        widget_name,
                        widget_class,
                        child.get("name") or "",
                        child.get("class") or "",
                        _line_of(content, child.get("name") or ""),
                        file_datetime,
                    )
                )
            else:
                names = [item.get("name") or "" for item in group]
                common = group[0].get("class") or ""
                body = "\n".join(_render_widget(item) for item in group)
                chunk = prefix + f"\n// Object group: {len(group)} x {common}\n" + body
                if len(chunk.strip()) < MIN_CHUNK_SIZE:
                    continue
                documents.append(
                    self._doc(
                        chunk,
                        "ui_object_group",
                        file_path,
                        unit_name,
                        form_class,
                        widget_name,
                        widget_class,
                        ", ".join(names),
                        common,
                        _line_of(content, names[0]),
                        file_datetime,
                    )
                )

        connections = _connection_lines(root)
        if connections:
            conn_text = prefix + "\n// Connections\n" + "\n".join(connections)
            if len(conn_text.strip()) >= MIN_CHUNK_SIZE:
                documents.append(
                    self._doc(
                        conn_text,
                        "ui_connections",
                        file_path,
                        unit_name,
                        form_class,
                        widget_name,
                        widget_class,
                        widget_name,
                        widget_class,
                        1,
                        file_datetime,
                    )
                )

        if not documents:
            return [
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path,
                        "node_type": "full_file",
                        "class_name": form_class,
                        "unit_name": unit_name,
                        **file_datetime,
                    },
                )
            ]
        return documents

    def _doc(
        self,
        text: str,
        node_type: str,
        file_path: str,
        unit_name: str,
        form_class: str,
        form_name: str,
        form_type: str,
        object_name: str,
        object_type: str,
        start_line: int,
        file_datetime: dict,
    ) -> Document:
        return Document(
            text=text,
            metadata={
                "file_path": file_path,
                "node_type": node_type,
                "object_name": object_name,
                "object_type": object_type,
                "form_name": form_name,
                "form_type": form_type,
                "class_name": form_class,
                "unit_name": unit_name,
                "start_line": start_line,
                **file_datetime,
            },
        )


def _group_small(children: List[Element]) -> List[List[Element]]:
    """Group consecutive small widgets that share a class. Same rule as DFM."""
    groups: List[List[Element]] = []
    current: List[Element] = []
    current_type: Optional[str] = None
    current_chars = 0

    for child in children:
        rendered = _render_widget(child)
        size = len(rendered)
        widget_class = child.get("class") or ""
        is_small = size < SMALL_OBJECT_CHARS

        if is_small and widget_class == current_type and current:
            if current_chars + size <= MAX_GROUP_CHARS:
                current.append(child)
                current_chars += size
                continue
            groups.append(current)
            current = [child]
            current_type = widget_class
            current_chars = size
            continue

        if current:
            groups.append(current)
            current = []
            current_type = None
            current_chars = 0

        if is_small:
            current = [child]
            current_type = widget_class
            current_chars = size
        else:
            groups.append([child])

    if current:
        groups.append(current)
    return groups
