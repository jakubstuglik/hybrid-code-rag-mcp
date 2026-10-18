"""
C and C++ file reader (.c, .h, .cpp) using Tree-sitter.

Chunking strategy:

1. Context prefix on every chunk: file name, namespace, and owning class.
2. Class summary: header plus member signatures, with no method bodies.
   Q_OBJECT, signals, and slots stay in the summary.
3. Class overview: a short natural-language summary when the class summary
   is longer than MAX_SUMMARY_CHARS.
4. One chunk per function body (inline or Class::method). Trivial bodies
   are grouped.
5. CVS ``$Log:`` comment blocks are left out of every chunk.
6. Includes are one include_group. Free prototypes are one declaration_group.

.h and .cpp are parsed as C++. .c is parsed as C.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter
from tree_sitter import Node
from tree_sitter_language_pack import get_parser

from shared.log import log_warn
from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding_and_bytes,
)
from shared.rerank_profile import RerankProfile, compile_all

_CPP_PARSER = get_parser("cpp")
_C_PARSER = get_parser("c")

_TYPE_SPECIFIERS = {"class_specifier", "struct_specifier", "union_specifier"}
_RECURSE_TYPES = {
    "translation_unit",
    "preproc_ifdef",
    "preproc_ifndef",
    "preproc_if",
    "preproc_else",
    "preproc_elif",
    "preproc_elifdef",
    "preproc_elifndef",
    "linkage_specification",
    "declaration_list",
    "template_declaration",
    "type_definition",
    "ERROR",
}
_NAME_TYPES = {
    "identifier",
    "field_identifier",
    "destructor_name",
    "operator_name",
    "type_identifier",
    "namespace_identifier",
    "template_function",
    "template_type",
}
_SCOPE_TYPES = {
    "namespace_identifier",
    "type_identifier",
    "template_type",
    "qualified_identifier",
}
_QT_PAREN_MACROS = (
    "Q_PROPERTY",
    "Q_ENUM",
    "Q_ENUMS",
    "Q_FLAGS",
    "Q_INTERFACES",
    "Q_CLASSINFO",
    "Q_DECLARE_METATYPE",
    "Q_DISABLE_COPY",
)


def _node_text(node: Node, content_bytes: bytes) -> str:
    """Return the source text of a node."""
    return content_bytes[node.start_byte : node.end_byte].decode(
        "utf-8", errors="replace"
    )


def _collapse(text: str) -> str:
    """Collapse whitespace to a single line."""
    return " ".join(text.split())


def _span_node(node: Node) -> Node:
    """Include a surrounding template_declaration in the chunk span."""
    parent = node.parent
    if parent is not None and parent.type == "template_declaration":
        return parent
    return node


def _blank_paren_macro(text: str, name: str) -> str:
    """Replace ``NAME(...)`` with spaces of the same length. Newlines stay."""
    needle = name
    start = 0
    while True:
        idx = text.find(needle, start)
        if idx == -1:
            return text
        after = idx + len(needle)
        if idx > 0 and (text[idx - 1].isalnum() or text[idx - 1] == "_"):
            start = after
            continue
        j = after
        while j < len(text) and text[j] in " \t":
            j += 1
        if j >= len(text) or text[j] != "(":
            start = after
            continue
        depth = 0
        k = j
        while k < len(text):
            ch = text[k]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    k += 1
                    text = text[:idx] + (" " * (k - idx)) + text[k:]
                    start = idx + (k - idx)
                    break
            k += 1
        else:
            return text


def _normalize_qt(text: str) -> str:
    """Rewrite Qt keywords so the C++ grammar can see the declarations.

    Replacements keep the same length and do not add or remove newlines,
    so tree-sitter line and byte positions still match the original text.
    """
    for name in _QT_PAREN_MACROS:
        text = _blank_paren_macro(text, name)

    def _access_slots(match: re.Match[str]) -> str:
        return (match.group(1) + ":").ljust(len(match.group(0)))

    text = re.sub(
        r"\b(public|protected|private)[ \t]+slots[ \t]*:",
        _access_slots,
        text,
    )
    text = re.sub(
        r"\bQ_SLOTS[ \t]*:",
        lambda m: "public:".ljust(len(m.group(0))),
        text,
    )
    text = re.sub(
        r"\bQ_SIGNALS[ \t]*:",
        lambda m: "public:".ljust(len(m.group(0))),
        text,
    )
    text = re.sub(
        r"\bsignals[ \t]*:",
        lambda m: "public:".ljust(len(m.group(0))),
        text,
    )
    text = re.sub(r"\bQ_OBJECT\b", lambda m: " " * len(m.group(0)), text)
    return text


# A line holding only an attribute-like annotation macro between a function's
# parameter list and its body, e.g. lock-context annotations:
#     static void f(struct x *p)
#         __releases(&p->lock)
#     {
_ANNOTATION_LINE = re.compile(
    r"(?m)(\)[ \t]*(?:/\*[^\n]*?\*/)?[ \t]*\n)"
    r"((?:[ \t]*(?:__[A-Za-z]\w*|[A-Z][A-Z0-9_]{2,})[ \t]*\((?:[^()\n]|\([^()\n]*\))*\)"
    r"[ \t]*(?:/\*[^\n]*?\*/)?[ \t]*\n)+)(?=[ \t]*\{)"
)


def _blank_annotation_lines(text: str) -> str:
    """Blank annotation-macro lines between ``)`` and ``{`` (same length,
    newlines kept) so the grammar sees a plain function definition."""

    def _repl(match: re.Match[str]) -> str:
        return match.group(1) + re.sub(r"[^\n]", " ", match.group(2))

    return _ANNOTATION_LINE.sub(_repl, text)


def _error_bytes(tree) -> int:
    """Bytes covered by ERROR / missing nodes (outermost only)."""
    total = 0
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "ERROR" or node.is_missing:
            total += max(node.end_byte - node.start_byte, 1)
            continue
        if node.has_error:
            stack.extend(node.children)
    return total


_DEFINITION_TYPES = {
    "function_definition",
    "struct_specifier",
    "union_specifier",
    "class_specifier",
    "enum_specifier",
    "preproc_def",
    "preproc_function_def",
}


def _definition_count(tree) -> int:
    """Definitions the walker can turn into chunks (bodies only)."""
    count = 0
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type in _DEFINITION_TYPES:
            if node.type in ("function_definition", "preproc_def", "preproc_function_def") or any(
                c.type in ("field_declaration_list", "enumerator_list") for c in node.children
            ):
                count += 1
        stack.extend(node.children)
    return count


def _parse_best(primary, secondary, data: bytes):
    """Parse with ``primary``; when the tree has errors and a ``secondary``
    grammar is given (``.h`` files are C or C++), also try it and keep the
    tree with more recognisable definitions (ties: fewer error bytes)."""
    tree = primary.parse(data)
    if not tree.root_node.has_error or secondary is None:
        return tree, primary
    alt = secondary.parse(data)
    a, b = _definition_count(alt), _definition_count(tree)
    if a > b or (a == b and _error_bytes(alt) < _error_bytes(tree)):
        return alt, secondary
    return tree, primary


def _strip_log_comments(text: str) -> str:
    """Remove block comments that carry a CVS ``$Log:`` history."""

    def _repl(match: re.Match[str]) -> str:
        if "$Log:" in match.group(0):
            return ""
        return match.group(0)

    return re.sub(r"/\*.*?\*/", _repl, text, flags=re.DOTALL)


def _is_log_comment(node: Node, content_bytes: bytes) -> bool:
    if node.type != "comment":
        return False
    return "$Log:" in _node_text(node, content_bytes)


def _has_field_body(node: Node) -> bool:
    return any(child.type == "field_declaration_list" for child in node.children)


def _find_first(node: Node, types: set[str]) -> Optional[Node]:
    """Depth-first search for the first descendant whose type is in ``types``."""
    if node.type in types:
        return node
    for child in node.children:
        found = _find_first(child, types)
        if found is not None:
            return found
    return None


def _type_name(node: Node, content_bytes: bytes) -> Optional[str]:
    for child in node.children:
        if child.type in ("type_identifier", "identifier", "template_type"):
            return _node_text(child, content_bytes).strip()
    return None


def _type_kind(node: Node, content_bytes: bytes) -> str:
    for child in node.children:
        if child.type in ("class", "struct", "union"):
            return child.type
        text = _node_text(child, content_bytes).strip()
        if text in ("class", "struct", "union"):
            return text
    if node.type == "struct_specifier":
        return "struct"
    if node.type == "union_specifier":
        return "union"
    return "class"


def _base_classes(node: Node, content_bytes: bytes) -> List[str]:
    bases: List[str] = []
    for child in node.children:
        if child.type != "base_class_clause":
            continue
        for sub in child.children:
            if sub.type in (
                "type_identifier",
                "qualified_identifier",
                "template_type",
            ):
                bases.append(_collapse(_node_text(sub, content_bytes)))
    return bases


def _class_header(node: Node, content_bytes: bytes) -> str:
    span = _span_node(node)
    end = span.end_byte
    for child in node.children:
        if child.type == "field_declaration_list":
            end = child.start_byte
            break
    header = content_bytes[span.start_byte : end].decode("utf-8", errors="replace")
    return _collapse(header)


def _split_qualified(node: Node, content_bytes: bytes) -> tuple[Optional[str], str]:
    """Return ``(scope, name)`` from a qualified_identifier or plain name."""
    if node.type == "qualified_identifier":
        scope: Optional[str] = None
        name = ""
        for child in node.children:
            if child.type in _SCOPE_TYPES:
                scope = _collapse(_node_text(child, content_bytes))
            elif child.type in _NAME_TYPES:
                name = _collapse(_node_text(child, content_bytes))
        if not name:
            name = _collapse(_node_text(node, content_bytes))
        return scope, name
    if node.type in _NAME_TYPES:
        return None, _collapse(_node_text(node, content_bytes))
    for child in node.children:
        if child.type in ("qualified_identifier",) or child.type in _NAME_TYPES:
            return _split_qualified(child, content_bytes)
        if child.type in (
            "pointer_declarator",
            "reference_declarator",
            "parenthesized_declarator",
            "abstract_pointer_declarator",
        ):
            return _split_qualified(child, content_bytes)
    return None, ""


def _function_declarator(node: Node) -> Optional[Node]:
    return _find_first(node, {"function_declarator"})


def _signature(node: Node, content_bytes: bytes) -> str:
    end = node.end_byte
    body = _find_first(node, {"compound_statement"})
    if body is not None:
        end = body.start_byte
    text = content_bytes[node.start_byte : end].decode("utf-8", errors="replace")
    return _collapse(text).rstrip(";").strip()


def _namespace_name(node: Node, content_bytes: bytes) -> Optional[str]:
    parts: List[str] = []
    for child in node.children:
        if child.type in (
            "namespace_identifier",
            "identifier",
            "nested_namespace_specifier",
        ):
            parts.append(_node_text(child, content_bytes).strip())
    if not parts:
        return None
    return "::".join(parts)


def _access_label(lines: List[str], node: Node) -> Optional[str]:
    """Read public/slots/signals from the original line. The parser saw a rewrite."""
    if node.start_point[0] >= len(lines):
        return None
    line = lines[node.start_point[0]]
    has_slots = re.search(r"\bslots\b|\bQ_SLOTS\b", line) is not None
    has_signals = re.search(r"\bsignals\b|\bQ_SIGNALS\b", line) is not None
    access_match = re.search(r"\b(public|protected|private)\b", line)
    access = access_match.group(1) if access_match else None
    if has_signals:
        return "signals"
    if has_slots and access:
        return f"{access} slots"
    if has_slots:
        return "slots"
    if access:
        return access
    return None


def _context_prefix(
    file_name: str,
    namespace: tuple[str, ...],
    class_header: Optional[str] = None,
    class_name: Optional[str] = None,
) -> str:
    parts = [f"// File: {file_name}"]
    shown = [part for part in namespace if part and part != "(anonymous)"]
    if shown:
        parts.append("// Namespace: " + "::".join(shown))
    if class_header:
        parts.append(f"// Class: {class_header}")
    elif class_name:
        parts.append(f"// Class: {class_name}")
    return "\n".join(parts)


def _is_include_guard(node: Node, content_bytes: bytes) -> bool:
    if node.type != "preproc_def":
        return False
    for child in node.children:
        if child.type == "preproc_arg" and _node_text(child, content_bytes).strip():
            return False
    return True


class CppFileReader(BaseFileReader):
    """Semantic chunking for C and C++ source files."""

    MIN_CHUNK_SIZE = 20
    MAX_CHUNK_CHARS = 24000
    MAX_SUMMARY_CHARS = 6000
    TRIVIAL_METHOD_LINES = 6
    MIN_TRIVIAL_RUN = 3
    MAX_GROUP_CHARS = 8000
    LONG_MACRO_LINES = 8

    def __init__(self) -> None:
        super().__init__()
        self._text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=128)

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        try:
            text, _ = read_file_with_encoding_and_bytes(file)
        except Exception as exc:
            log_warn(f"Failed to read {file}: {exc}")
            return []

        if not text.strip():
            return []

        normalized = _normalize_qt(text)
        if len(normalized) != len(text):
            normalized = text
        annotated = _blank_annotation_lines(normalized)
        if len(annotated) == len(normalized):
            normalized = annotated
        content_bytes = text.encode("utf-8")
        parse_bytes = normalized.encode("utf-8")
        if len(parse_bytes) != len(content_bytes):
            parse_bytes = content_bytes

        suffix = file.suffix.lower()
        parser = _C_PARSER if suffix == ".c" else _CPP_PARSER
        other = _C_PARSER if suffix == ".h" else None
        try:
            tree, used = _parse_best(parser, other, parse_bytes)
        except Exception as exc:
            log_warn(f"Tree-sitter parse failed for {file}: {exc}")
            return self._full_file(file, text)

        file_datetime = get_file_datetime(file)
        collector = _ChunkCollector(
            file_name=file.name,
            file_path=str(file),
            unit_name=file.stem,
            content_bytes=content_bytes,
            lines=text.splitlines(),
            file_datetime=file_datetime,
            reader=self,
            parser=used,
            parse_bytes=parse_bytes,
        )
        collector.walk(tree.root_node, ())
        documents = collector.documents()
        if documents:
            return documents
        return self._full_file(file, text)

    def _full_file(self, file: Path, text: str) -> List[Document]:
        stripped = _strip_log_comments(text).strip()
        if not stripped:
            return []
        return [
            Document(
                text=stripped,
                metadata={
                    "file_path": str(file),
                    "node_type": "full_file",
                    "unit_name": file.stem,
                    **get_file_datetime(file),
                },
            )
        ]

    def make_documents(
        self,
        chunk_text: str,
        node_type: str,
        start_line: int,
        end_line: int,
        start_byte: int,
        end_byte: int,
        file_path: str,
        file_datetime: dict,
        extra: Optional[dict] = None,
        max_chars: Optional[int] = None,
    ) -> List[Document]:
        """Build one document, or split parts when the text is too long."""
        if len(chunk_text.strip()) < self.MIN_CHUNK_SIZE:
            return []

        threshold = self.MAX_CHUNK_CHARS if max_chars is None else max_chars
        metadata = {
            "file_path": file_path,
            "node_type": node_type,
            "start_line": start_line,
            "end_line": end_line,
            "start_byte": start_byte,
            "end_byte": end_byte,
            **file_datetime,
        }
        if extra:
            metadata.update(extra)

        if len(chunk_text) <= threshold:
            return [Document(text=chunk_text, metadata=metadata)]

        prefix_lines: List[str] = []
        for line in chunk_text.split("\n"):
            if line.startswith("//"):
                prefix_lines.append(line)
            else:
                break
        prefix = "\n".join(prefix_lines)
        parts = self._text_splitter.split_text(chunk_text)
        docs: List[Document] = []
        for index, part in enumerate(parts):
            if len(part.strip()) < self.MIN_CHUNK_SIZE:
                continue
            piece = part
            if prefix and not part.startswith("//"):
                piece = f"{prefix}\n{part}"
            docs.append(
                Document(
                    text=piece,
                    metadata={
                        **metadata,
                        "node_type": f"{node_type}_split",
                        "split_part": index,
                        "split_total": len(parts),
                    },
                )
            )
        return docs


class _ChunkCollector:
    """Walk one translation unit and record chunks in source order."""

    def __init__(
        self,
        file_name: str,
        file_path: str,
        unit_name: str,
        content_bytes: bytes,
        lines: List[str],
        file_datetime: dict,
        reader: CppFileReader,
        parser=None,
        parse_bytes: Optional[bytes] = None,
    ) -> None:
        self.parser = parser
        self.parse_bytes = parse_bytes if parse_bytes is not None else content_bytes
        self.file_name = file_name
        self.file_path = file_path
        self.unit_name = unit_name
        self.content_bytes = content_bytes
        self.lines = lines
        self.file_datetime = file_datetime
        self.reader = reader
        self.includes: List[str] = []
        self.events: List[dict] = []

    def walk(self, node: Node, namespace: tuple[str, ...]) -> None:
        if _is_log_comment(node, self.content_bytes):
            return

        if node.type in _TYPE_SPECIFIERS and _has_field_body(node):
            self._emit_type(node, namespace)
            return

        if node.type == "enum_specifier":
            self._emit_enum(node, namespace)
            return

        if node.type == "function_definition":
            self._emit_function(node, namespace)
            return

        if node.type == "namespace_definition":
            name = _namespace_name(node, self.content_bytes)
            next_ns = namespace + ((name,) if name else ("(anonymous)",))
            for child in node.children:
                if child.type == "declaration_list":
                    self.walk(child, next_ns)
            return

        if node.type == "declaration":
            self._emit_declaration(node, namespace)
            return

        if node.type == "preproc_include":
            self.includes.append(_collapse(_node_text(node, self.content_bytes)))
            return

        if node.type in ("preproc_def", "preproc_function_def"):
            if not _is_include_guard(node, self.content_bytes):
                self._add_macro(node, namespace)
            return

        if node.type == "comment":
            return

        if node.type == "ERROR" and self._recover_error_region(node, namespace):
            return

        if node.type in _RECURSE_TYPES:
            children = node.children
            skip = -1
            for index, child in enumerate(children):
                if index == skip:
                    continue
                nxt = children[index + 1] if index + 1 < len(children) else None
                if nxt is not None and self._emit_macro_definition(child, nxt, namespace):
                    skip = index + 1
                    continue
                self.walk(child, namespace)

    # A region the grammar could not parse is re-parsed in pieces split at
    # lines that close a top-level block (``}`` / ``};`` in column 0), so one
    # unknown construct costs one definition instead of the rest of the file.
    MIN_RECOVERY_LINES = 30

    def _recover_error_region(self, node: Node, namespace: tuple[str, ...]) -> bool:
        if self.parser is None or getattr(self, "_in_recovery", False):
            return False
        if node.end_point[0] - node.start_point[0] + 1 < self.MIN_RECOVERY_LINES:
            return False
        data = self.parse_bytes
        start, end = node.start_byte, node.end_byte
        cuts = [start]
        for m in re.finditer(rb"\n\}[ \t]*;?[ \t]*(?=\n)", data[start:end]):
            cuts.append(start + m.end())
        cuts.append(end)
        if len(cuts) <= 2:
            return False
        for a, b in zip(cuts, cuts[1:]):
            if not data[a:b].strip():
                continue
            seg_line = data.count(b"\n", 0, a)
            # pad with newlines so rows match; bytes are shifted back below
            pad = seg_line
            buf = b"\n" * pad + data[a:b]
            try:
                tree = self.parser.parse(buf)
            except Exception:  # noqa: BLE001
                continue
            sub = _ChunkCollector(
                self.file_name, self.file_path, self.unit_name,
                b"\n" * pad + self.content_bytes[a:b], self.lines,
                self.file_datetime, self.reader, parser=self.parser, parse_bytes=buf,
            )
            sub._in_recovery = True
            sub.walk(tree.root_node, namespace)
            shift = a - pad
            for event in sub.events:
                for item in event.get("items", [event]):
                    if "start_byte" in item:
                        item["start_byte"] += shift
                        item["end_byte"] += shift
                self.events.append(event)
            self.includes.extend(sub.includes)
        return True

    def _emit_macro_definition(self, head: Node, body: Node, namespace: tuple[str, ...]) -> bool:
        """``NAME(args) { ... }`` at file scope: a function defined through a
        macro (``SYSCALL_DEFINE2(name, ...)``, ``TEST(Suite, Case)``).  The
        grammar sees a call statement without ``;`` followed by a block."""
        if body.type != "compound_statement" or head.type != "expression_statement":
            return False
        call = head.named_children[0] if head.named_children else None
        if call is None or call.type != "call_expression" or len(head.named_children) != 1:
            return False
        semi = [c for c in head.children if c.type == ";"]
        if semi and not semi[0].is_missing and semi[0].end_byte > semi[0].start_byte:
            return False
        if body.start_point[0] - call.end_point[0] > 1:
            return False
        func = call.child_by_field_name("function")
        args = call.child_by_field_name("arguments")
        if func is None or func.type != "identifier" or args is None:
            return False
        macro = _node_text(func, self.content_bytes)
        first = next((c for c in args.named_children), None)
        name = _node_text(first, self.content_bytes).strip() if first is not None and first.type == "identifier" else macro
        event = {
            "kind": "func",
            "namespace": namespace,
            "class_name": "",
            "class_header": None,
            "func_name": name,
            "text": self.content_bytes[head.start_byte : body.end_byte].decode("utf-8", errors="replace").strip(),
            "lines": body.end_point[0] - head.start_point[0] + 1,
            "start_line": head.start_point[0] + 1,
            "end_line": body.end_point[0] + 1,
            "start_byte": head.start_byte,
            "end_byte": body.end_byte,
            "macro": macro,
        }
        self._attach_comment(event, head)
        self.events.append(event)
        return True

    # Comments directly above a definition (doc comments, kernel-doc) become
    # part of its chunk.  License headers and CVS logs are left out.
    MAX_LEADING_COMMENT_CHARS = 2000

    def _leading_comment(self, node: Node) -> Optional[Node]:
        target = node
        while (
            target.prev_sibling is None or target.prev_sibling.type != "comment"
        ) and target.parent is not None and target.parent.type in (
            "declaration", "type_definition", "template_declaration", "field_declaration",
        ) and target.parent.start_byte == target.start_byte:
            target = target.parent
        first = None
        row = target.start_point[0]
        prev = target.prev_sibling
        while prev is not None and prev.type == "comment" and row - prev.end_point[0] <= 1:
            before = prev.prev_sibling
            if before is not None and before.end_point[0] == prev.start_point[0] and before.type != "comment":
                break  # trailing comment of the previous statement
            text = _node_text(prev, self.content_bytes)
            if "$Log:" in text or "SPDX-License-Identifier" in text or re.search(r"(?i)\bcopyright\b", text):
                break
            first = prev
            row = prev.start_point[0]
            prev = before
        return first

    def _attach_comment(self, event: dict, node: Node) -> None:
        first = self._leading_comment(node)
        if first is None:
            return
        start = first.start_byte
        comment = self.content_bytes[start : event["start_byte"]].decode("utf-8", errors="replace").strip()
        if not comment or len(comment) > self.MAX_LEADING_COMMENT_CHARS:
            if comment:
                comment = comment[-self.MAX_LEADING_COMMENT_CHARS :]
                nl = comment.find("\n")
                comment = comment[nl + 1 :] if nl >= 0 else comment
            if not comment:
                return
        event["text"] = comment + "\n" + event["text"]
        event["start_line"] = first.start_point[0] + 1
        event["start_byte"] = start
        if "lines" in event:
            event["lines"] = event["end_line"] - event["start_line"] + 1

    def _emit_declaration(self, node: Node, namespace: tuple[str, ...]) -> None:
        for child in node.children:
            if child.type in _TYPE_SPECIFIERS and _has_field_body(child):
                self._emit_type(child, namespace)
                return
            if child.type == "enum_specifier":
                self._emit_enum(child, namespace)
                return
        declarator = _function_declarator(node)
        if declarator is None:
            self._emit_initialized_data(node, namespace)
            return
        if _find_first(node, {"compound_statement"}) is not None:
            self._emit_function(node, namespace)
            return
        span = _span_node(node)
        self.events.append(
            {
                "kind": "proto",
                "namespace": namespace,
                "text": _signature(span, self.content_bytes) + ";",
                "start_line": span.start_point[0] + 1,
                "end_line": span.end_point[0] + 1,
                "start_byte": span.start_byte,
                "end_byte": span.end_byte,
            }
        )

    MIN_DATA_LINES = 3
    # Large tables (firmware blobs, register lists) are cut, not split.
    MAX_DATA_CHARS = 3000

    def _emit_initialized_data(self, node: Node, namespace: tuple[str, ...]) -> None:
        """File-scope variable with an aggregate initializer (an operations
        table, a lookup array): ``const struct ops x = { .open = f, ... };``."""
        if node.end_point[0] - node.start_point[0] + 1 < self.MIN_DATA_LINES:
            return
        init = next((c for c in node.children if c.type == "init_declarator"), None)
        if init is None:
            return
        value = init.child_by_field_name("value")
        if value is None or value.type != "initializer_list":
            return
        ident = _find_first(init.child_by_field_name("declarator") or init, {"identifier"})
        if ident is None:
            return
        name = _node_text(ident, self.content_bytes)
        prefix = _context_prefix(self.file_name, namespace)
        event = {
            "kind": "doc",
            "node_type": "variable_definition",
            "text": _node_text(node, self.content_bytes).strip(),
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "start_byte": node.start_byte,
            "end_byte": node.end_byte,
            "extra": {"unit_name": self.unit_name, "object_name": name},
            "max_chars": None,
        }
        self._attach_comment(event, node)
        text = event["text"]
        if len(text) > self.MAX_DATA_CHARS:
            cut = text.rfind("\n", 0, self.MAX_DATA_CHARS)
            text = text[: cut if cut > 0 else self.MAX_DATA_CHARS] + "\n\t/* ... */\n};"
        event["text"] = f"{prefix}\n{text}"
        self.events.append(event)

    def _emit_type(self, node: Node, namespace: tuple[str, ...]) -> None:
        name = _type_name(node, self.content_bytes)
        if not name:
            return
        span = _span_node(node)
        header = _class_header(node, self.content_bytes)
        kind = _type_kind(node, self.content_bytes)
        bases = _base_classes(node, self.content_bytes)
        prefix = _context_prefix(self.file_name, namespace, class_header=header)
        summary_lines, counts, functions = self._members(node, namespace, name, header)
        body = "\n".join(summary_lines)
        doc = {"text": "", "start_byte": span.start_byte, "end_line": span.end_point[0] + 1}
        self._attach_comment(doc, span)
        lead = doc["text"]
        summary_text = f"{prefix}\n{lead}{header} {{\n{body}\n}}"
        extra = {
            "class_name": name,
            "unit_name": self.unit_name,
            "object_name": name,
        }
        if len(summary_text) > self.reader.MAX_SUMMARY_CHARS:
            overview = self._overview(
                prefix, name, kind, bases, counts, summary_lines
            )
            self.events.append(
                {
                    "kind": "doc",
                    "node_type": "class_overview",
                    "text": overview,
                    "start_line": span.start_point[0] + 1,
                    "end_line": span.end_point[0] + 1,
                    "start_byte": span.start_byte,
                    "end_byte": span.end_byte,
                    "extra": extra,
                    "max_chars": None,
                }
            )
        self.events.append(
            {
                "kind": "doc",
                "node_type": "class_summary",
                "text": summary_text,
                "start_line": span.start_point[0] + 1,
                "end_line": span.end_point[0] + 1,
                "start_byte": span.start_byte,
                "end_byte": span.end_byte,
                "extra": extra,
                "max_chars": self.reader.MAX_SUMMARY_CHARS,
            }
        )
        self.events.extend(functions)

    def _members(
        self,
        type_node: Node,
        namespace: tuple[str, ...],
        class_name: str,
        class_header: str,
    ) -> tuple[List[str], dict, List[dict]]:
        lines: List[str] = []
        functions: List[dict] = []
        counts = {"methods": 0, "fields": 0, "slots": 0, "signals": 0}
        body = next(
            (
                child
                for child in type_node.children
                if child.type == "field_declaration_list"
            ),
            None,
        )
        if body is None:
            return lines, counts, functions

        class_bytes = self.content_bytes[type_node.start_byte : type_node.end_byte]
        if b"Q_OBJECT" in class_bytes:
            lines.append("Q_OBJECT")

        section = "public"
        for child in body.children:
            section = self._one_member(
                child, namespace, class_name, class_header, lines, functions, counts, section
            )
        return lines, counts, functions

    def _one_member(
        self,
        node: Node,
        namespace: tuple[str, ...],
        class_name: str,
        class_header: str,
        lines: List[str],
        functions: List[dict],
        counts: dict,
        section: str,
    ) -> str:
        if _is_log_comment(node, self.content_bytes):
            return section
        if node.type == "access_specifier":
            label = _access_label(self.lines, node)
            if label:
                section = label
                lines.append(f"{label}:")
            return section
        if node.type == "comment":
            comment = _collapse(_node_text(node, self.content_bytes))
            if comment and "$Log:" not in comment:
                lines.append(comment)
            return section
        if node.type in _TYPE_SPECIFIERS and _has_field_body(node):
            nested = _type_name(node, self.content_bytes)
            if nested:
                lines.append(f"{_type_kind(node, self.content_bytes)} {nested};")
                self._emit_type(node, namespace)
            return section
        if node.type == "enum_specifier":
            lines.append(_signature(node, self.content_bytes) + ";")
            return section
        if node.type in ("preproc_ifdef", "preproc_if", "preproc_else", "preproc_elif", "ERROR"):
            for child in node.children:
                section = self._one_member(
                    child,
                    namespace,
                    class_name,
                    class_header,
                    lines,
                    functions,
                    counts,
                    section,
                )
            return section
        if node.type in ("field_declaration", "declaration", "function_definition"):
            self._member_decl(
                node, namespace, class_name, class_header, lines, functions, counts, section
            )
            return section
        return section

    def _member_decl(
        self,
        node: Node,
        namespace: tuple[str, ...],
        class_name: str,
        class_header: str,
        lines: List[str],
        functions: List[dict],
        counts: dict,
        section: str,
    ) -> None:
        declarator = _function_declarator(node)
        has_body = _find_first(node, {"compound_statement"}) is not None
        if declarator is None and not has_body:
            enum_node = _find_first(node, {"enum_specifier"})
            if enum_node is not None:
                lines.append(_signature(enum_node, self.content_bytes) + ";")
                return
            field = _signature(node, self.content_bytes)
            if field and field not in ("{", "}"):
                lines.append(field + ";")
                counts["fields"] += 1
            return

        sig = _signature(node, self.content_bytes)
        if sig:
            lines.append(sig + ";")
        counts["methods"] += 1
        if section == "signals":
            counts["signals"] += 1
        elif section.endswith("slots"):
            counts["slots"] += 1
        if has_body:
            scope, func_name = (
                _split_qualified(declarator, self.content_bytes)
                if declarator is not None
                else (None, "")
            )
            functions.append(
                self._function_event(
                    node,
                    namespace,
                    scope or class_name,
                    func_name,
                    class_header,
                )
            )

    def _emit_function(self, node: Node, namespace: tuple[str, ...]) -> None:
        declarator = _function_declarator(node)
        scope, func_name = (
            _split_qualified(declarator, self.content_bytes)
            if declarator is not None
            else (None, "")
        )
        self.events.append(
            self._function_event(node, namespace, scope, func_name, None)
        )

    def _function_event(
        self,
        node: Node,
        namespace: tuple[str, ...],
        class_name: Optional[str],
        func_name: str,
        class_header: Optional[str],
    ) -> dict:
        span = _span_node(node)
        event = {
            "kind": "func",
            "namespace": namespace,
            "class_name": class_name or "",
            "class_header": class_header,
            "func_name": func_name,
            "text": _node_text(span, self.content_bytes).strip(),
            "lines": span.end_point[0] - span.start_point[0] + 1,
            "start_line": span.start_point[0] + 1,
            "end_line": span.end_point[0] + 1,
            "start_byte": span.start_byte,
            "end_byte": span.end_byte,
        }
        self._attach_comment(event, span)
        return event

    def _emit_enum(self, node: Node, namespace: tuple[str, ...]) -> None:
        name = _type_name(node, self.content_bytes) or ""
        prefix = _context_prefix(self.file_name, namespace, class_name=name or None)
        doc = {"text": _node_text(node, self.content_bytes).strip(), "start_byte": node.start_byte,
               "end_line": node.end_point[0] + 1}
        self._attach_comment(doc, node)
        text = doc["text"]
        extra = {"unit_name": self.unit_name}
        if name:
            extra["class_name"] = name
            extra["object_name"] = name
        self.events.append(
            {
                "kind": "doc",
                "node_type": "enum_declaration",
                "text": f"{prefix}\n{text}",
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "start_byte": node.start_byte,
                "end_byte": node.end_byte,
                "extra": extra,
                "max_chars": None,
            }
        )

    def _add_macro(self, node: Node, namespace: tuple[str, ...]) -> None:
        text = _node_text(node, self.content_bytes).strip()
        line_count = node.end_point[0] - node.start_point[0] + 1
        name_node = node.child_by_field_name("name")
        event = {
            "kind": "macro",
            "namespace": namespace,
            "text": text,
            "lines": line_count,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "start_byte": node.start_byte,
            "end_byte": node.end_byte,
            "name": _node_text(name_node, self.content_bytes) if name_node is not None else "",
        }
        self._attach_comment(event, node)
        self.events.append(event)

    def _overview(
        self,
        prefix: str,
        name: str,
        kind: str,
        bases: List[str],
        counts: dict,
        summary_lines: List[str],
    ) -> str:
        inherits = ""
        if bases:
            inherits = " inheriting from " + ", ".join(bases)
        plain_methods = counts["methods"] - counts["signals"] - counts["slots"]
        parts: List[str] = []
        if plain_methods or not (counts["signals"] or counts["slots"]):
            parts.append(f"{plain_methods} methods")
        if counts["fields"]:
            parts.append(f"{counts['fields']} fields")
        if counts["signals"]:
            parts.append(f"{counts['signals']} signals")
        if counts["slots"]:
            parts.append(f"{counts['slots']} slots")
        sentence = (
            f"{name} is a C++ {kind}{inherits} with " + ", ".join(parts) + "."
        )
        kept: List[str] = []
        used = len(prefix) + len(sentence)
        for line in summary_lines:
            if used + len(line) > 2000:
                break
            kept.append(line)
            used += len(line) + 1
        listing = "\n".join(kept)
        return f"{prefix}\n{sentence}\n{listing}".rstrip()

    def documents(self) -> List[Document]:
        docs: List[Document] = []
        if self.includes:
            prefix = _context_prefix(self.file_name, ())
            text = prefix + "\n" + "\n".join(self.includes)
            docs.extend(
                self.reader.make_documents(
                    text,
                    "include_group",
                    1,
                    1,
                    0,
                    0,
                    self.file_path,
                    self.file_datetime,
                    extra={"unit_name": self.unit_name},
                )
            )

        grouped = self._group_events(self.events)
        for event in grouped:
            if event["kind"] == "doc":
                docs.extend(
                    self.reader.make_documents(
                        event["text"],
                        event["node_type"],
                        event["start_line"],
                        event["end_line"],
                        event["start_byte"],
                        event["end_byte"],
                        self.file_path,
                        self.file_datetime,
                        extra=event.get("extra"),
                        max_chars=event.get("max_chars"),
                    )
                )
            elif event["kind"] == "func":
                docs.extend(self._function_docs([event], "cpp_function"))
            elif event["kind"] == "func_group":
                docs.extend(self._function_docs(event["items"], "method_group"))
            elif event["kind"] == "proto_group":
                docs.extend(self._text_group_docs(event, "declaration_group"))
            elif event["kind"] == "macro_group":
                node_type = (
                    "macro_definition"
                    if len(event["items"]) == 1
                    and event["items"][0]["lines"] > self.reader.LONG_MACRO_LINES
                    else "macro_group"
                )
                docs.extend(self._text_group_docs(event, node_type))
        return docs

    def _group_events(self, events: List[dict]) -> List[dict]:
        grouped: List[dict] = []
        index = 0
        while index < len(events):
            event = events[index]
            if event["kind"] == "func":
                run = [event]
                nxt = index + 1
                while (
                    nxt < len(events)
                    and events[nxt]["kind"] == "func"
                    and events[nxt]["class_name"] == event["class_name"]
                    and events[nxt]["namespace"] == event["namespace"]
                    and events[nxt]["lines"] <= self.reader.TRIVIAL_METHOD_LINES
                    and event["lines"] <= self.reader.TRIVIAL_METHOD_LINES
                ):
                    run.append(events[nxt])
                    nxt += 1
                if (
                    len(run) >= self.reader.MIN_TRIVIAL_RUN
                    and event["lines"] <= self.reader.TRIVIAL_METHOD_LINES
                ):
                    grouped.append({"kind": "func_group", "items": run})
                    index = nxt
                    continue
                grouped.append(event)
                index += 1
                continue
            if event["kind"] in ("proto", "macro"):
                run = [event]
                nxt = index + 1
                while (
                    nxt < len(events)
                    and events[nxt]["kind"] == event["kind"]
                    and events[nxt]["namespace"] == event["namespace"]
                ):
                    run.append(events[nxt])
                    nxt += 1
                kind = "proto_group" if event["kind"] == "proto" else "macro_group"
                grouped.append({"kind": kind, "items": run, "namespace": event["namespace"]})
                index = nxt
                continue
            grouped.append(event)
            index += 1
        return grouped

    def _function_docs(self, items: List[dict], node_type: str) -> List[Document]:
        first = items[0]
        class_name = first["class_name"]
        header = first.get("class_header")
        prefix = _context_prefix(
            self.file_name,
            first["namespace"],
            class_header=header if node_type != "cpp_function" else None,
            class_name=class_name or None,
        )
        if node_type == "cpp_function" and class_name and not header:
            prefix = _context_prefix(
                self.file_name, first["namespace"], class_name=class_name
            )
        body = "\n\n".join(item["text"] for item in items)
        if len(body) > self.reader.MAX_GROUP_CHARS and node_type == "method_group":
            docs: List[Document] = []
            for item in items:
                docs.extend(self._function_docs([item], "cpp_function"))
            return docs
        extra = {"unit_name": self.unit_name}
        if class_name:
            extra["class_name"] = class_name
        names = [item["func_name"] for item in items if item.get("func_name")]
        if names:
            extra["object_name"] = ", ".join(names)
            if len(names) > 1:
                extra["symbols"] = names
        return self.reader.make_documents(
            f"{prefix}\n{body}",
            node_type,
            first["start_line"],
            items[-1]["end_line"],
            first["start_byte"],
            items[-1]["end_byte"],
            self.file_path,
            self.file_datetime,
            extra=extra,
        )

    def _text_group_docs(self, event: dict, node_type: str) -> List[Document]:
        items = event["items"]
        prefix = _context_prefix(self.file_name, event["namespace"])
        text = prefix + "\n" + "\n".join(item["text"] for item in items)
        extra = {"unit_name": self.unit_name}
        names = [item["name"] for item in items if item.get("name")]
        if names:
            # every defined name, for the exact symbol lookup and the reranker
            extra["symbols"] = names
            if len(names) == 1:
                extra["object_name"] = names[0]
        return self.reader.make_documents(
            text,
            node_type,
            items[0]["start_line"],
            items[-1]["end_line"],
            items[0]["start_byte"],
            items[-1]["end_byte"],
            self.file_path,
            self.file_datetime,
            extra=extra,
        )


# ────────────────────────────────────────────────
# Rerank profile (query-time ranking knowledge, see shared/rerank_profile.py)
# ────────────────────────────────────────────────

_CPP_HEADER = re.compile(r"\.(?:h|hh|hpp|hxx|h\+\+|inl)$", re.IGNORECASE)


def _is_cpp_declaration_chunk(node_type: str, file_path: str) -> bool:
    """Prototype lists and the split parts of header class bodies hold
    declarations only; the definition lives elsewhere."""
    if node_type in ("declaration_group", "declaration_group_split"):
        return True
    return node_type == "class_summary_split" and bool(_CPP_HEADER.search(file_path or ""))


RERANK_PROFILE = RerankProfile(
    name="cpp",
    target_patterns=compile_all(
        [r"\b([A-Za-z][A-Za-z0-9_]*)\.(?:cpp|cc|cxx|hpp|hh|hxx|h|c|ino)\b"]
    ),
    overview_types=frozenset({"enum_declaration"}),
    detail_types=frozenset(
        {"cpp_function", "cpp_function_split", "declaration_group", "macro_group", "macro_definition"}
    ),
    import_types=frozenset({"include_group"}),
    # foo_test.cc, foo_unittest.cpp, test/ and testing/ folders
    test_path_patterns=compile_all(
        [
            r"_(?:unit)?tests?\.(?:cc|cpp|cxx|c|h|hpp)$",
            r"(?:^|/)test_[^/]*\.(?:cc|cpp|cxx|c)$",
            r"(?:^|/)(?:test|testing|testutil|test_util)/",
        ]
    ),
    # Thin glue layers: JNI bindings, C API wrappers, FFI / binding folders.
    binding_path_patterns=compile_all(
        [
            r"(?:^|/)[^/]*jni[^/]*/",
            r"(?:^|/)(?:bindings?|ffi)/",
            r"(?:^|/)c_api[^/]*/",
            r"(?:^|/)(?:c|c_api|capi)\.(?:cc|cpp|cxx|c|h)$",
            r"(?:^|/)[^/]*_c_api\.[^/]+$",
        ]
    ),
    binding_text_patterns=compile_all([r"\bJNIEnv\b", r"\bJNIEXPORT\b"], 0),
    is_declaration_chunk=_is_cpp_declaration_chunk,
    # A call site of the named function is not its definition.
    mention_penalty=0.10,
    # "... types / states / modes enumeration" -> enum; "... flags / bits" -> enum or #define.
    type_intent_rules=(
        (
            re.compile(
                r"\b(?:enums?|enumerat\w*|types|kinds|states|modes|codes|levels|"
                r"flags?|bits|bit\s?masks?|constants)\b",
                re.IGNORECASE,
            ),
            frozenset({"enum_declaration"}),
            0.15,
        ),
        (
            re.compile(r"\b(?:flags?|bits|bit\s?masks?|constants)\b", re.IGNORECASE),
            frozenset({"macro_group", "macro_definition"}),
            0.08,
        ),
    ),
)

CppFileReader.rerank_profile = RERANK_PROFILE
