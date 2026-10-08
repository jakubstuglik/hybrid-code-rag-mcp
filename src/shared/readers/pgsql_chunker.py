"""Statement chunker for PostgreSQL scripts.

Dollar quotes, strings, comments, and parentheses hide semicolons. Each
CREATE TABLE, FUNCTION, PROCEDURE, TRIGGER, RULE, VIEW, or COMMENT is its
own chunk. A long statement is split after that, with the object name kept
on every piece. This path does not call the T-SQL chunker.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from shared.readers._base import decompose_identifier


MAX_CHUNK_CHARS = 12000
MIN_STATEMENT_CHARS = 50

_IDENT = r'(?:"(?:[^"]|"")*"|[A-Za-z_][A-Za-z0-9_$]*)'
_QNAME = rf"{_IDENT}(?:\s*\.\s*{_IDENT})*"
_DOLLAR = re.compile(r"\$[A-Za-z0-9_]*\$")

_LABELS = {
    "FUNCTION": "Function",
    "PROCEDURE": "Procedure",
    "TABLE": "Table",
    "TRIGGER": "Trigger",
    "RULE": "Rule",
    "INDEX": "Index",
    "VIEW": "View",
    "SEQUENCE": "Sequence",
    "SCHEMA": "Schema",
    "COMMENT": "Comment",
    "INSERT": "Insert",
}

# First match wins. Longer object kinds stay above generic statements.
_SPECS = [
    (
        "FUNCTION",
        "pgsql_create_function",
        re.compile(
            rf"^CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+({_QNAME})",
            re.IGNORECASE,
        ),
    ),
    (
        "PROCEDURE",
        "pgsql_create_procedure",
        re.compile(
            rf"^CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+({_QNAME})",
            re.IGNORECASE,
        ),
    ),
    (
        "TABLE",
        "pgsql_create_table",
        re.compile(
            rf"^CREATE\s+(?:OR\s+REPLACE\s+)?"
            rf"(?:UNLOGGED\s+|TEMP(?:ORARY)?\s+|GLOBAL\s+|LOCAL\s+)*"
            rf"TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?({_QNAME})",
            re.IGNORECASE,
        ),
    ),
    (
        "TRIGGER",
        "pgsql_create_trigger",
        re.compile(
            rf"^CREATE\s+(?:OR\s+REPLACE\s+)?(?:CONSTRAINT\s+)?TRIGGER\s+({_IDENT})",
            re.IGNORECASE,
        ),
    ),
    (
        "RULE",
        "pgsql_create_rule",
        re.compile(
            rf"^CREATE\s+(?:OR\s+REPLACE\s+)?RULE\s+({_IDENT})",
            re.IGNORECASE,
        ),
    ),
    (
        "INDEX",
        "pgsql_create_index",
        re.compile(
            rf"^CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:CONCURRENTLY\s+)?"
            rf"(?:IF\s+NOT\s+EXISTS\s+)?({_IDENT})",
            re.IGNORECASE,
        ),
    ),
    (
        "VIEW",
        "pgsql_create_view",
        re.compile(
            rf"^CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP(?:ORARY)?\s+)?"
            rf"(?:RECURSIVE\s+)?VIEW\s+({_QNAME})",
            re.IGNORECASE,
        ),
    ),
    (
        "SEQUENCE",
        "pgsql_create_sequence",
        re.compile(
            rf"^CREATE\s+(?:OR\s+REPLACE\s+)?SEQUENCE\s+"
            rf"(?:IF\s+NOT\s+EXISTS\s+)?({_QNAME})",
            re.IGNORECASE,
        ),
    ),
    (
        "SCHEMA",
        "pgsql_create_schema",
        re.compile(
            rf"^CREATE\s+SCHEMA\s+(?:IF\s+NOT\s+EXISTS\s+)?({_IDENT})",
            re.IGNORECASE,
        ),
    ),
    (
        "COMMENT",
        "pgsql_comment",
        re.compile(
            rf"^COMMENT\s+ON\s+(?:COLUMN|TABLE|FUNCTION|PROCEDURE|TRIGGER|"
            rf"VIEW|INDEX|SCHEMA|SEQUENCE|CONSTRAINT)\s+({_QNAME})",
            re.IGNORECASE,
        ),
    ),
    (
        "TABLE",
        "pgsql_alter",
        re.compile(
            rf"^ALTER\s+TABLE\s+(?:ONLY\s+)?(?:IF\s+EXISTS\s+)?({_QNAME})",
            re.IGNORECASE,
        ),
    ),
    (
        "SEQUENCE",
        "pgsql_alter",
        re.compile(
            rf"^ALTER\s+SEQUENCE\s+(?:IF\s+EXISTS\s+)?({_QNAME})",
            re.IGNORECASE,
        ),
    ),
    (
        "INSERT",
        "pgsql_statement",
        re.compile(rf"^INSERT\s+INTO\s+({_QNAME})", re.IGNORECASE),
    ),
]


@dataclass
class PgChunk:
    """One PostgreSQL chunk, or one piece of a split statement."""

    text: str
    node_type: str
    start_line: int
    end_line: int
    object_name: Optional[str] = None
    object_type: Optional[str] = None


def chunk_postgresql(content: str) -> List[PgChunk]:
    """Split a PostgreSQL script into object chunks.

    Args:
        content: Full script text.

    Returns:
        Chunks in file order. Whitespace-only input returns an empty list.
    """
    if not content or not content.strip():
        return []

    chunks: List[PgChunk] = []
    for text, start_line, end_line in _split_statements(content):
        code = _strip_leading_comments(text)
        if not code:
            continue
        obj_type, node_type, obj_name = _classify(code)
        if obj_name is None and len(code) < MIN_STATEMENT_CHARS:
            continue
        body_start, body_end = _content_span(text, start_line, end_line)
        chunks.extend(
            _pack(text.strip(), node_type, body_start, body_end, obj_name, obj_type)
        )
    return chunks


def _split_statements(content: str) -> List[tuple]:
    """Split on semicolons that are outside quotes, comments, and parentheses."""
    statements = []
    length = len(content)
    index = 0
    start = 0
    line = 1
    start_line = 1
    paren = 0

    while index < length:
        char = content[index]
        nxt = content[index + 1] if index + 1 < length else ""

        if char == "-" and nxt == "-":
            newline = content.find("\n", index)
            index = length if newline < 0 else newline
            continue

        if char == "/" and nxt == "*":
            end = content.find("*/", index + 2)
            if end < 0:
                line += content[index:].count("\n")
                index = length
            else:
                line += content[index : end + 2].count("\n")
                index = end + 2
            continue

        if char == "'":
            index, line = _skip_quoted(content, index, line, "'")
            continue

        if char == '"':
            index, line = _skip_quoted(content, index, line, '"')
            continue

        if char == "$":
            match = _DOLLAR.match(content, index)
            if match:
                tag = match.group(0)
                close = content.find(tag, match.end())
                if close < 0:
                    line += content[index:].count("\n")
                    index = length
                else:
                    end = close + len(tag)
                    line += content[index:end].count("\n")
                    index = end
                continue

        if char == "(":
            paren += 1
        elif char == ")" and paren > 0:
            paren -= 1
        elif char == ";" and paren == 0:
            text = content[start : index + 1]
            if text.strip():
                statements.append((text, start_line, line))
            start = index + 1
            start_line = line
            index += 1
            continue

        if char == "\n":
            line += 1
        index += 1

    tail = content[start:]
    if tail.strip():
        statements.append((tail, start_line, line))
    return statements


def _skip_quoted(content: str, index: int, line: int, quote: str) -> tuple:
    """Skip a single-quoted string or a double-quoted identifier."""
    cursor = index + 1
    length = len(content)
    while cursor < length:
        if content[cursor] == quote:
            if cursor + 1 < length and content[cursor + 1] == quote:
                cursor += 2
                continue
            cursor += 1
            break
        cursor += 1
    line += content[index:cursor].count("\n")
    return cursor, line


def _strip_leading_comments(text: str) -> str:
    """Return the statement with leading whitespace and comments removed."""
    index = 0
    length = len(text)
    while index < length:
        while index < length and text[index] in " \t\r\n":
            index += 1
        if text.startswith("--", index):
            newline = text.find("\n", index)
            index = length if newline < 0 else newline + 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            index = length if end < 0 else end + 2
            continue
        break
    return text[index:].strip()


def _classify(code: str) -> tuple:
    """Return object type, node type, and object name for one statement."""
    for obj_type, node_type, pattern in _SPECS:
        match = pattern.match(code)
        if match:
            return obj_type, node_type, _unquote_name(match.group(1))
    return None, "pgsql_statement", None


def _unquote_name(name: str) -> str:
    parts = re.split(r"\s*\.\s*", name.strip())
    cleaned = []
    for part in parts:
        if len(part) >= 2 and part[0] == '"' and part[-1] == '"':
            cleaned.append(part[1:-1].replace('""', '"'))
        else:
            cleaned.append(part)
    return ".".join(cleaned)


def _content_span(text: str, start_line: int, end_line: int) -> tuple:
    """Move the start line past leading whitespace in the raw statement."""
    line = start_line
    for char in text:
        if char not in " \t\r\n":
            break
        if char == "\n":
            line += 1
    return line, max(line, end_line)


def _prefix(obj_type: Optional[str], obj_name: Optional[str]) -> str:
    if not obj_name:
        return ""
    label = _LABELS.get(obj_type or "", "Object")
    lines = [f"-- {label}: {obj_name}"]
    leaf = obj_name.split(".")[-1]
    description = decompose_identifier(leaf)
    if description and description.lower() != leaf.lower():
        lines.append(f"-- Description: {description.lower()}")
    return "\n".join(lines) + "\n"


def _pack(
    body: str,
    node_type: str,
    start_line: int,
    end_line: int,
    obj_name: Optional[str],
    obj_type: Optional[str],
) -> List[PgChunk]:
    prefix = _prefix(obj_type, obj_name)
    if len(prefix) + len(body) <= MAX_CHUNK_CHARS:
        return [
            PgChunk(
                text=prefix + body,
                node_type=node_type,
                start_line=start_line,
                end_line=end_line,
                object_name=obj_name,
                object_type=obj_type,
            )
        ]

    split_type = node_type if node_type.endswith("_split") else node_type + "_split"
    lines = body.splitlines()
    chunks: List[PgChunk] = []
    buffer: List[str] = []
    buffer_len = 0
    line_cursor = start_line
    buffer_start = start_line

    def flush(last_line: int) -> None:
        if not buffer:
            return
        chunks.append(
            PgChunk(
                text=prefix + "\n".join(buffer),
                node_type=split_type,
                start_line=buffer_start,
                end_line=max(buffer_start, last_line),
                object_name=obj_name,
                object_type=obj_type,
            )
        )

    for line in lines:
        piece_len = len(line) + 1
        if buffer and len(prefix) + buffer_len + piece_len > MAX_CHUNK_CHARS:
            flush(line_cursor - 1)
            buffer = [line]
            buffer_len = piece_len
            buffer_start = line_cursor
        else:
            buffer.append(line)
            buffer_len += piece_len
        line_cursor += 1
    flush(line_cursor - 1)
    return chunks
