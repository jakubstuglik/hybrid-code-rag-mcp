"""
Qt Designer form reader (.ui).

Same shape as the DFM reader:

- One form-header chunk for the root widget, its title, and custom widgets.
- One chunk per direct child widget. Nested widgets stay with that parent.
- Consecutive small widgets of the same class are grouped.
- Signal/slot connections are their own chunk.
- Every chunk starts with ``// Form: ClassName (file.ui)``.

``UI_CHUNK_CONTEXT`` (default off) keeps that text. When it is on, every chunk
also carries the window title and a parent-directory file name, object chunks
carry the parent widget path, the form header lists visible texts, consecutive
tiny siblings of any class are merged, and a container larger than
``MAX_GROUP_CHARS`` is split into its children.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Sequence, Tuple
from xml.etree.ElementTree import Element

from llama_index.core import Document

from shared.log import log_warn
from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding,
)
from shared.rerank_profile import QueryDomain, RerankProfile, compile_all

MIN_CHUNK_SIZE = 20
MAX_GROUP_CHARS = 4000
SMALL_OBJECT_CHARS = 500
# Body length below which consecutive siblings merge when UI_CHUNK_CONTEXT is on.
CONTEXT_SIZE_FLOOR = 300
# Cap for the form header's visible-text list (the joined texts, not the label).
VISIBLE_TEXT_CHAR_CAP = 1500
_VISIBLE_TRUNC = " [...]"

# Human-visible string properties. Enums, numbers, bools and geometry are not.
_VISIBLE_TEXT_PROPS = frozenset(
    {
        "text",
        "toolTip",
        "statusTip",
        "whatsThis",
        "title",
        "placeholderText",
        "windowTitle",
    }
)

# Process-wide copy of UI_CHUNK_CONTEXT. The indexer sets it at startup.
# extra_info["ui_chunk_context"] overrides it for one file. Default off.
_UI_CHUNK_CONTEXT = False

_Item = Tuple[str, Element]

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


def _as_bool(raw: object) -> bool:
    if isinstance(raw, str):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    return bool(raw)


def configure_ui_chunk_context(cfg: object) -> bool:
    """Read ``UI_CHUNK_CONTEXT`` from a config object. Missing means off."""
    global _UI_CHUNK_CONTEXT
    _UI_CHUNK_CONTEXT = _as_bool(getattr(cfg, "UI_CHUNK_CONTEXT", False))
    return _UI_CHUNK_CONTEXT


def set_ui_chunk_context(enabled: bool) -> None:
    """Set the process-wide flag. Tests use this; the indexer uses configure."""
    global _UI_CHUNK_CONTEXT
    _UI_CHUNK_CONTEXT = bool(enabled)


def get_ui_chunk_context() -> bool:
    return _UI_CHUNK_CONTEXT


def _context_enabled(extra_info: Optional[dict]) -> bool:
    """Per-file extra_info wins; otherwise the process-wide config flag."""
    if extra_info is not None and "ui_chunk_context" in extra_info:
        return _as_bool(extra_info.get("ui_chunk_context"))
    return _UI_CHUNK_CONTEXT


def _string_values(elem: Element) -> List[str]:
    """Plain ``<string>`` values under one property or attribute, in order."""
    values: List[str] = []
    for node in elem.iter():
        if node is elem or _local(node.tag) != "string":
            continue
        value = " ".join("".join(node.itertext()).split())
        if value:
            values.append(value)
    return values


def _direct_string_prop(elem: Element, name: str) -> str:
    for child in list(elem):
        if _local(child.tag) != "property" or child.get("name") != name:
            continue
        values = _string_values(child)
        if values:
            return values[0]
    return ""


def _direct_attr_string(elem: Element, name: str) -> str:
    for child in list(elem):
        if _local(child.tag) != "attribute" or child.get("name") != name:
            continue
        values = _string_values(child)
        if values:
            return values[0]
    return ""


def _segment_title(elem: Element) -> str:
    """Tab title, group-box title, or window title. Not a button caption."""
    return (
        _direct_attr_string(elem, "title")
        or _direct_string_prop(elem, "title")
        or _direct_string_prop(elem, "windowTitle")
    )


def _path_segment(elem: Element) -> str:
    name = elem.get("name") or elem.get("class") or "widget"
    title = _segment_title(elem).replace('"', "'")
    if title:
        return f'{name} "{title}"'
    return name


def _format_path(chain: Sequence[Element]) -> str:
    return " > ".join(_path_segment(elem) for elem in chain)


def _display_file(file: Path) -> str:
    """``parent/file.ui``. Never an absolute path."""
    parent = file.parent.name
    if parent and parent not in (".",):
        return f"{parent}/{file.name}"
    return file.name


def _context_header(
    display_file: str, form_class: str, window_title: str, path: str
) -> str:
    title = " ".join(window_title.split())
    title_line = f"// Title: {title}" if title else "// Title:"
    return "\n".join(
        [
            f"// Form: {form_class} ({display_file})",
            title_line,
            f"// Path: {path}",
        ]
    )


def _collect_visible_texts(root: Element) -> List[str]:
    """Visible strings in document order, duplicates removed."""
    seen = set()
    texts: List[str] = []
    for elem in root.iter():
        tag = _local(elem.tag)
        if tag not in ("property", "attribute"):
            continue
        name = elem.get("name") or ""
        if name not in _VISIBLE_TEXT_PROPS:
            continue
        for value in _string_values(elem):
            if value in seen:
                continue
            seen.add(value)
            texts.append(value)
    return texts


def _format_visible_texts(texts: Sequence[str]) -> str:
    """Join texts up to ``VISIBLE_TEXT_CHAR_CAP``, then a truncation marker."""
    if not texts:
        return ""
    limit = VISIBLE_TEXT_CHAR_CAP
    marker = _VISIBLE_TRUNC
    kept: List[str] = []
    used = 0
    truncated = False
    for text in texts:
        extra = len(text) if not kept else len(text) + 3
        if used + extra > limit:
            truncated = True
            break
        kept.append(text)
        used += extra
    if not kept:
        room = max(limit - len(marker), 0)
        return "Visible texts: " + texts[0][:room].rstrip() + marker
    body = " | ".join(kept)
    if truncated:
        room = limit - len(marker)
        if len(body) > room:
            body = body[:room].rstrip()
        while body.endswith(" |"):
            body = body[:-2]
        body += marker
    return "Visible texts: " + body


def _attribute_lines(elem: Element, indent: str) -> List[str]:
    lines: List[str] = []
    for child in list(elem):
        if _local(child.tag) != "attribute":
            continue
        name = child.get("name") or ""
        if name not in _VISIBLE_TEXT_PROPS:
            continue
        for value in _string_values(child):
            lines.append(f"{indent}{name}: {value}")
    return lines


def _item_text_lines(elem: Element, indent: str) -> List[str]:
    """Combo, list and table item texts that are not nested widgets."""
    lines: List[str] = []

    def walk(node: Element) -> None:
        for child in list(node):
            tag = _local(child.tag)
            if tag == "widget":
                continue
            if tag in ("item", "column", "row"):
                for prop in list(child):
                    if _local(prop.tag) != "property":
                        continue
                    name = prop.get("name") or ""
                    if name not in _VISIBLE_TEXT_PROPS:
                        continue
                    for value in _string_values(prop):
                        lines.append(f"{indent}item {name}: {value}")
                walk(child)
            elif tag == "layout":
                walk(child)

    walk(elem)
    return lines


def _render_widget_context(
    elem: Element, indent: str = "", include_children: bool = True
) -> str:
    """Plain-text widget tree used only when ``UI_CHUNK_CONTEXT`` is on."""
    widget_class = elem.get("class") or "QWidget"
    name = elem.get("name") or ""
    lines = [f"{indent}widget {widget_class} {name}".rstrip()]
    child_indent = indent + "  "
    lines.extend(_property_lines(elem, child_indent))
    lines.extend(_attribute_lines(elem, child_indent))
    lines.extend(_item_text_lines(elem, child_indent))
    if include_children:
        for child in _direct_widgets(elem):
            rendered = _render_widget_context(child, child_indent)
            if rendered.strip():
                lines.append(rendered)
    return "\n".join(lines)


def _context_body(kind: str, elem: Element) -> str:
    if kind == "shell":
        return _render_widget_context(elem, include_children=False)
    return _render_widget_context(elem)


def _merge_context_items(items: Sequence[_Item]) -> List[List[_Item]]:
    """Merge consecutive bodies below the floor, up to ``MAX_GROUP_CHARS``.

    Callers pass siblings of one parent only.
    """
    groups: List[List[_Item]] = []
    current: List[_Item] = []
    current_chars = 0

    for item in items:
        size = len(_context_body(item[0], item[1]))
        is_tiny = size < CONTEXT_SIZE_FLOOR
        if is_tiny and current:
            if current_chars + size <= MAX_GROUP_CHARS:
                current.append(item)
                current_chars += size
                continue
            groups.append(current)
            current = [item]
            current_chars = size
            continue
        if current:
            groups.append(current)
            current = []
            current_chars = 0
        if is_tiny:
            current = [item]
            current_chars = size
        else:
            groups.append([item])

    if current:
        groups.append(current)
    return groups


def _action_lines(root: Element) -> List[str]:
    lines: List[str] = []
    detail_names = ("toolTip", "statusTip", "whatsThis", "placeholderText", "title")
    for elem in root.iter():
        if _local(elem.tag) != "action":
            continue
        name = elem.get("name") or ""
        bits: List[str] = []
        text = _direct_string_prop(elem, "text")
        if text:
            bits.append(text)
        for prop_name in detail_names:
            value = _direct_string_prop(elem, prop_name)
            if value:
                bits.append(f"{prop_name}: {value}")
        if not name and not bits:
            continue
        label = name or "action"
        lines.append(f"{label}: {' | '.join(bits)}" if bits else label)
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

        if _context_enabled(extra_info):
            return self._load_with_context(
                file,
                content,
                root,
                widget,
                form_class,
                file_path,
                file_datetime,
                unit_name,
            )

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

    def _load_with_context(
        self,
        file: Path,
        content: str,
        root: Element,
        widget: Element,
        form_class: str,
        file_path: str,
        file_datetime: dict,
        unit_name: str,
    ) -> List[Document]:
        widget_name = widget.get("name") or form_class or file.stem
        widget_class = widget.get("class") or "QWidget"
        window_title = _direct_string_prop(widget, "windowTitle")
        display = _display_file(file)

        def header(path: str) -> str:
            return _context_header(display, form_class, window_title, path)

        documents: List[Document] = []
        header_lines = [
            header(_format_path([widget])),
            f"class: {form_class}",
            f"widget: {widget_class} name={widget_name}",
        ]
        header_lines.extend(_property_lines(widget, ""))
        custom = _custom_widget_lines(root)
        if custom:
            header_lines.append("custom widgets: " + ", ".join(custom))
        actions = _action_lines(root)
        if actions:
            header_lines.append("actions:")
            header_lines.extend(f"  {line}" for line in actions)
        visible = _format_visible_texts(_collect_visible_texts(root))
        if visible:
            header_lines.append(visible)
        documents.append(
            self._doc(
                "\n".join(header_lines),
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
        documents.extend(
            self._emit_context_level(
                _direct_widgets(widget),
                [widget],
                header,
                content,
                file_path,
                unit_name,
                form_class,
                widget_name,
                widget_class,
                file_datetime,
            )
        )
        connections = _connection_lines(root)
        if connections:
            conn_text = (
                header(_format_path([widget]))
                + "\n// Connections\n"
                + "\n".join(connections)
            )
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
        return documents

    def _emit_context_level(
        self,
        children: List[Element],
        parent_chain: List[Element],
        header,
        content: str,
        file_path: str,
        unit_name: str,
        form_class: str,
        form_name: str,
        form_type: str,
        file_datetime: dict,
    ) -> List[Document]:
        items: List[_Item] = []
        for elem in children:
            full = _render_widget_context(elem)
            if len(full) > MAX_GROUP_CHARS and _direct_widgets(elem):
                items.append(("shell", elem))
            else:
                items.append(("whole", elem))

        documents: List[Document] = []
        for group in _merge_context_items(items):
            documents.append(
                self._context_group_doc(
                    group,
                    parent_chain,
                    header,
                    content,
                    file_path,
                    unit_name,
                    form_class,
                    form_name,
                    form_type,
                    file_datetime,
                )
            )
            for kind, elem in group:
                if kind != "shell":
                    continue
                documents.extend(
                    self._emit_context_level(
                        _direct_widgets(elem),
                        parent_chain + [elem],
                        header,
                        content,
                        file_path,
                        unit_name,
                        form_class,
                        form_name,
                        form_type,
                        file_datetime,
                    )
                )
        return documents

    def _context_group_doc(
        self,
        group: Sequence[_Item],
        parent_chain: Sequence[Element],
        header,
        content: str,
        file_path: str,
        unit_name: str,
        form_class: str,
        form_name: str,
        form_type: str,
        file_datetime: dict,
    ) -> Document:
        bodies: List[str] = []
        names: List[str] = []
        classes: List[str] = []
        for kind, elem in group:
            bodies.append(_context_body(kind, elem))
            names.append(elem.get("name") or "")
            classes.append(elem.get("class") or "")

        if len(group) == 1:
            path = _format_path(list(parent_chain) + [group[0][1]])
            text = header(path) + "\n" + bodies[0]
            return self._doc(
                text,
                "ui_object",
                file_path,
                unit_name,
                form_class,
                form_name,
                form_type,
                names[0],
                classes[0],
                _line_of(content, names[0]),
                file_datetime,
            )

        if len(set(classes)) == 1 and classes[0]:
            banner = f"// Object group: {len(group)} x {classes[0]}"
            object_type = classes[0]
        else:
            banner = f"// Object group: {len(group)}"
            object_type = ", ".join(classes)
        path = _format_path(parent_chain)
        text = header(path) + "\n" + banner + "\n" + "\n".join(bodies)
        return self._doc(
            text,
            "ui_object_group",
            file_path,
            unit_name,
            form_class,
            form_name,
            form_type,
            ", ".join(names),
            object_type,
            _line_of(content, names[0]),
            file_datetime,
        )

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


# ────────────────────────────────────────────────
# Rerank profile (query-time ranking knowledge, see shared/rerank_profile.py)
# ────────────────────────────────────────────────

_FORM_OVERVIEW_QUERY_PATTERNS = compile_all(
    [r"\bform\s+overview\b", r"\bform\s+components\b", r"\bframe\s+components\b"]
)
_FORM_QUERY_PATTERNS = compile_all(
    [
        r"\bform\s+components\b",
        r"\bframe\s+components\b",
        r"\bform\s+layout\b",
        r"\bform\s+header\b",
        r"\bform\s+overview\b",
        r"\bvisual\s+layout\b",
        r"\bUI\s+components\b",
        r"\bform\s+controls\b",
    ]
)

RERANK_PROFILE = RerankProfile(
    name="qt_forms",
    overview_query_patterns=_FORM_OVERVIEW_QUERY_PATTERNS,
    target_patterns=compile_all([r"\b([A-Za-z][A-Za-z0-9_]*)\.ui\b"]),
    artifact_overview_types=frozenset({"ui_form_header"}),
    domains=(
        QueryDomain(
            name="form",
            priority=50,
            patterns=_FORM_QUERY_PATTERNS
            + compile_all([r"\.ui\b", r"\bqt\s+(?:form|dialog|widget)s?\b"]),
            primary_types=frozenset({"ui_form_header"}),
        ),
    ),
)

UiFileReader.rerank_profile = RERANK_PROFILE
