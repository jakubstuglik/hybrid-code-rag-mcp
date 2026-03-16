"""
Delphi form file reader (.dfm) with depth-aware object block extraction.

Binary hex data between curly brackets (e.g. Bitmap, Picture.Data,
Glyph.Data, Icon.Data) is stripped before embedding because it is
irrelevant for RAG search and extremely slow to embed.

Parsing strategy:
- Parse the DFM into a tree using object/inherited/end depth tracking
- Emit a "form header" chunk with root form properties
- Split at depth 1 (direct children of root form)
- Nested children stay with their depth-1 parent
- Group consecutive small same-type depth-1 objects into single chunks
- Prepend a context prefix to every chunk identifying the parent form
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from llama_index.core import Document

from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding,
)
from shared.log import log_warn

# ────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────

MIN_CHUNK_SIZE = 20  # Skip chunks smaller than this (chars)
MAX_GROUP_CHARS = 4000  # Max chars for a grouped chunk of small siblings
SMALL_OBJECT_CHARS = 500  # Objects smaller than this are candidates for grouping

# ────────────────────────────────────────────────
# Binary data stripping
# ────────────────────────────────────────────────

# Matches a line like "    Bitmap = {" or "    Picture.Data = {"
# but NOT lines where { appears inside quotes (e.g. 'Filters={}')
_BINARY_OPEN_RE = re.compile(r"^(\s*[\w.]+\s*=\s*)\{\s*$")


def _strip_binary_data(content: str) -> str:
    """Remove binary hex data blocks from DFM text content.

    In Delphi text DFM files, binary data is stored as hex between
    curly brackets across multiple lines, e.g.:

        Bitmap = {
          494C010110001500...
          000000000000}

    This function replaces such blocks with a placeholder that preserves
    the property name for context while removing the large hex payload.
    """
    lines = content.split("\n")
    result: List[str] = []
    in_binary = False

    for line in lines:
        if in_binary:
            # Look for closing brace (may be appended to last hex line)
            if "}" in line:
                in_binary = False
            # Skip all binary data lines (including the closing one)
            continue

        m = _BINARY_OPEN_RE.match(line)
        if m:
            # Replace the opening line with a placeholder
            result.append(f"{m.group(1)}{{<binary data removed>}}")
            in_binary = True
        else:
            result.append(line)

    return "\n".join(result)


# ────────────────────────────────────────────────
# DFM tree structure
# ────────────────────────────────────────────────

# Matches: "  object Name: TType" or "  inherited Name: TType [0]"
_OBJECT_RE = re.compile(r"^\s*(object|inherited)\s+(\w+)\s*:\s*(\S+)")


@dataclass
class DFMObject:
    """A parsed DFM object node with its children."""

    name: str
    obj_type: str
    start_line: int  # 0-based line index
    end_line: int  # 0-based line index (inclusive, the 'end' line)
    lines: List[str] = field(default_factory=list)
    children: List["DFMObject"] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def char_count(self) -> int:
        return len(self.text)


def _parse_dfm_tree(
    all_lines: List[str],
) -> Optional[DFMObject]:
    """Parse DFM lines into a tree of DFMObject nodes.

    Returns the root form/datamodule/frame object, or None if
    the file doesn't start with an object/inherited line.
    """
    if not all_lines:
        return None

    # Find the root object line
    root_idx = -1
    for i, line in enumerate(all_lines):
        m = _OBJECT_RE.match(line)
        if m:
            root_idx = i
            break

    if root_idx == -1:
        return None

    # Recursive descent parser starting from root
    root, _ = _parse_object(all_lines, root_idx)
    return root


def _parse_object(all_lines: List[str], start: int) -> tuple["DFMObject", int]:
    """Parse a single object block starting at line index `start`.

    Returns (DFMObject, next_line_index) where next_line_index is
    the line after the closing 'end'.
    """
    m = _OBJECT_RE.match(all_lines[start])
    if not m:
        raise ValueError(
            f"Expected object/inherited at line {start + 1}: {all_lines[start]!r}"
        )

    name = m.group(2)
    # Strip optional index like "[0]" from type
    obj_type = m.group(3).split("[")[0].strip()

    obj = DFMObject(
        name=name,
        obj_type=obj_type,
        start_line=start,
        end_line=start,  # Will be updated
        lines=[all_lines[start]],
    )

    i = start + 1
    collection_depth = 0  # Track DFM collection blocks (Columns = <...end...end>)
    while i < len(all_lines):
        stripped = all_lines[i].strip()

        # Inside a collection block — all lines (including 'end' for items)
        # are property lines until the collection closes with '>' or 'end>'
        if collection_depth > 0:
            if stripped.endswith(">"):
                collection_depth -= 1
            obj.lines.append(all_lines[i])
            i += 1
            continue

        # Check if this line opens a collection (e.g., "  Columns = <")
        # but NOT self-closing empty collections like "= <>"
        if stripped.endswith("<") and not stripped.endswith("<>"):
            collection_depth += 1
            obj.lines.append(all_lines[i])
            i += 1
            continue

        if stripped == "end":
            # This 'end' closes our object
            obj.lines.append(all_lines[i])
            obj.end_line = i
            return obj, i + 1

        child_match = _OBJECT_RE.match(all_lines[i])
        if child_match:
            # Nested child object — recurse
            child, next_i = _parse_object(all_lines, i)
            obj.children.append(child)
            # Add child's lines to our lines
            for li in range(i, next_i):
                obj.lines.append(all_lines[li])
            i = next_i
        else:
            # Property line
            obj.lines.append(all_lines[i])
            i += 1

    # Reached end of file without closing 'end' — treat as complete
    obj.end_line = len(all_lines) - 1
    return obj, len(all_lines)


# ────────────────────────────────────────────────
# Chunking
# ────────────────────────────────────────────────


def _form_header_lines(root: DFMObject, all_lines: List[str]) -> List[str]:
    """Extract form header: root declaration + properties before first child.

    This gives the form's own properties (Caption, Size, etc.) without
    including any child component text.
    """
    result = [all_lines[root.start_line]]
    i = root.start_line + 1

    while i <= root.end_line:
        stripped = all_lines[i].strip()

        # Stop if we hit a child object or the closing 'end'
        if _OBJECT_RE.match(all_lines[i]) or stripped == "end":
            break

        result.append(all_lines[i])
        i += 1

    return result


def _context_prefix(file_name: str, form_name: str, form_type: str) -> str:
    """Build a 1-line context comment for chunk self-identification."""
    return f"// Form: {form_type} ({file_name})"


def _group_small_siblings(
    children: List[DFMObject],
) -> List[List[DFMObject]]:
    """Group consecutive small same-type depth-1 objects.

    Objects with char_count < SMALL_OBJECT_CHARS and the same obj_type
    are grouped together until the group exceeds MAX_GROUP_CHARS.
    Non-small or different-type objects become single-element groups.
    """
    groups: List[List[DFMObject]] = []
    current_group: List[DFMObject] = []
    current_type: Optional[str] = None
    current_chars = 0

    for child in children:
        is_small = child.char_count < SMALL_OBJECT_CHARS

        if is_small and child.obj_type == current_type:
            # Same type and small — try to add to current group
            if current_chars + child.char_count <= MAX_GROUP_CHARS:
                current_group.append(child)
                current_chars += child.char_count
                continue
            else:
                # Group full — flush and start new group
                groups.append(current_group)
                current_group = [child]
                current_type = child.obj_type
                current_chars = child.char_count
                continue

        # Flush current group if any
        if current_group:
            groups.append(current_group)

        if is_small:
            # Start new group with this type
            current_group = [child]
            current_type = child.obj_type
            current_chars = child.char_count
        else:
            # Large object — emit as solo group
            groups.append([child])
            current_group = []
            current_type = None
            current_chars = 0

    # Flush remaining group
    if current_group:
        groups.append(current_group)

    return groups


# ────────────────────────────────────────────────
# Reader
# ────────────────────────────────────────────────


class DFMFileReader(BaseFileReader):
    """Reader for Delphi .dfm files with depth-aware nested object parsing.

    Extracts each depth-1 object block (including nested children) as a
    separate chunk.  Groups consecutive small same-type objects to avoid
    producing hundreds of tiny chunks (e.g. 153 TClientDataSet objects).
    """

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents: List[Document] = []

        try:
            content = read_file_with_encoding(file)
        except Exception as e:
            log_warn(f"Failed to read {file}: {e}")
            return []

        if not content.strip():
            return []

        # Strip binary hex data before parsing
        content = _strip_binary_data(content)

        file_path_str = str(file)
        file_name = file.name
        all_lines = content.split("\n")
        file_datetime = get_file_datetime(file)

        # Parse into tree
        root = _parse_dfm_tree(all_lines)
        if root is None:
            # Couldn't parse — fall back to whole-file document
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "unit_name": file.stem,
                        **file_datetime,
                    },
                )
            )
            return documents

        form_name = root.name
        form_type = root.obj_type
        unit_name = file.stem
        prefix = _context_prefix(file_name, form_name, form_type)

        # ── Form header chunk ──
        header_lines = _form_header_lines(root, all_lines)
        header_text = prefix + "\n" + "\n".join(header_lines)

        if len(header_text.strip()) >= MIN_CHUNK_SIZE:
            start_byte = sum(len(all_lines[k]) + 1 for k in range(root.start_line))
            documents.append(
                Document(
                    text=header_text,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "dfm_form_header",
                        "object_name": form_name,
                        "object_type": form_type,
                        "form_name": form_name,
                        "form_type": form_type,
                        "class_name": form_type,
                        "unit_name": unit_name,
                        "start_line": root.start_line + 1,
                        "end_line": root.start_line + len(header_lines),
                        "start_byte": start_byte,
                        "end_byte": start_byte + len(header_text),
                        **file_datetime,
                    },
                )
            )

        # ── Depth-1 children chunks ──
        if root.children:
            groups = _group_small_siblings(root.children)

            for group in groups:
                if len(group) == 1:
                    # Single object chunk
                    child = group[0]
                    chunk_text = prefix + "\n" + child.text

                    if len(chunk_text.strip()) < MIN_CHUNK_SIZE:
                        continue

                    start_byte = sum(
                        len(all_lines[k]) + 1 for k in range(child.start_line)
                    )
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": "dfm_object",
                                "object_name": child.name,
                                "object_type": child.obj_type,
                                "form_name": form_name,
                                "form_type": form_type,
                                "class_name": form_type,
                                "unit_name": unit_name,
                                "start_line": child.start_line + 1,
                                "end_line": child.end_line + 1,
                                "start_byte": start_byte,
                                "end_byte": (start_byte + len(child.text)),
                                **file_datetime,
                            },
                        )
                    )
                else:
                    # Grouped chunk of small same-type objects
                    texts = [obj.text for obj in group]
                    names = [obj.name for obj in group]
                    common_type = group[0].obj_type
                    chunk_text = (
                        prefix
                        + f"\n// Object group: {len(group)} x "
                        + f"{common_type}\n"
                        + "\n".join(texts)
                    )

                    if len(chunk_text.strip()) < MIN_CHUNK_SIZE:
                        continue

                    first = group[0]
                    last = group[-1]
                    start_byte = sum(
                        len(all_lines[k]) + 1 for k in range(first.start_line)
                    )
                    end_byte_val = sum(
                        len(all_lines[k]) + 1 for k in range(last.end_line + 1)
                    )
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": "dfm_object_group",
                                "object_name": ", ".join(names),
                                "object_type": common_type,
                                "form_name": form_name,
                                "form_type": form_type,
                                "class_name": form_type,
                                "unit_name": unit_name,
                                "start_line": first.start_line + 1,
                                "end_line": last.end_line + 1,
                                "start_byte": start_byte,
                                "end_byte": end_byte_val,
                                **file_datetime,
                            },
                        )
                    )

        # Fallback: if no documents were produced at all
        if not documents:
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "class_name": form_type,
                        "unit_name": unit_name,
                        **file_datetime,
                    },
                )
            )

        return documents
