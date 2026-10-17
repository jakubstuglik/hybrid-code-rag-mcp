"""
Kotlin file reader (.kt, .kts) using Tree-sitter AST.

Mirrors the Java/Groovy readers so that Kotlin chunks carry exactly the same
context-prefix header as Java chunks (and the same structure as Delphi unit
chunks):

    // File: OrderService.kt
    // Package: com.example.orders
    // Class: @Service class OrderService(private val repo: OrderRepository) : BaseService()

Chunking strategy (same as Java):

1. **Context prefix on every chunk**: ``// File:``, ``// Package:`` (when the
   file declares one) and ``// Class:`` (when the chunk belongs to a
   class/object/interface/companion object).  Top-level functions and
   properties get the File/Package lines only, like Delphi routines outside
   a class get only the ``// Unit:`` line.
2. **Class summary chunk**: declaration header plus member signatures (no
   bodies) for every class, interface, object, enum class and companion
   object.  A compact **class overview** chunk is added for large types.
3. **Leaf chunks**: functions (member, top-level and extension), secondary
   constructors, ``init`` blocks, properties, type aliases, enum entries and
   long comments.
4. **Trivial method grouping** and **import grouping** as in Java.
5. ``.kts`` scripts: top-level statements that are not declarations are
   collected into a single ``script_body`` chunk.

Node types emitted reuse the Java names so the reranker treats Kotlin like
Java/Groovy without any reranker change:
    class_summary, class_overview, method_declaration,
    constructor_declaration, field_declaration, enum_constant,
    import_group, block_comment, method_group, full_file (+ ``_split``),
    plus ``type_alias_declaration``, ``initializer_block`` and ``script_body``.

Grammar notes (tree-sitter-kotlin from tree_sitter_language_pack):
    * interfaces are ``class_declaration`` nodes with an ``interface`` token;
    * abstract interface members and enum-class members after ``;`` may be
      wrapped in ``ERROR`` nodes; the reader descends into ``ERROR`` nodes
      inside class bodies so those members are still found;
    * a ``where`` clause that starts on a new line is not recognised (the
      newline ends the declaration), so the file is parsed from a
      line-preserving copy where that line break is moved after ``where``
      (see ``_join_where_clauses``).
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
from shared.rerank_profile import java_style_profile

_parser = get_parser("kotlin")

_CONTAINER_TYPES = {"class_declaration", "object_declaration", "companion_object"}
_BODY_TYPES = {"class_body", "enum_class_body"}
_COMMENT_TYPES = {"multiline_comment", "line_comment"}


# ---------------------------------------------------------------------------
# Parse-input normalisation
# ---------------------------------------------------------------------------

# Line break(s) + ``where`` + constraint start (``T :``, optionally annotated).
# The look-behind requires a non-blank character before the break, i.e. the
# end of the declaration head (return type, ``)``, ``>``, supertype, ...).
_WHERE_ON_NEW_LINE = re.compile(
    rb"(?<=\S)([ \t]*(?:\r?\n[ \t]*)+)where(\s+)(?=(?:@[\w.]+\s+)*[A-Za-z_]\w*\s*:)"
)
_LINE_BREAK = re.compile(rb"\r?\n")


def _join_where_clauses(content_bytes: bytes) -> bytes:
    """Copy of *content_bytes* in which ``where`` clauses parse correctly.

    tree-sitter-kotlin treats a line break before ``where`` as the end of the
    declaration::

        fun <T> pick(a: T, b: T): T
            where T : Comparable<T> { ... }

    so the function ends at ``: T``, the ``where`` line becomes a bogus
    property and the body (and the rest of the class) is mis-parsed.  A line
    break *after* ``where`` is fine, so the whitespace around the keyword is
    rearranged to `` where<line breaks><padding>``.  The copy has the same
    length and the same line breaks, so every byte offset and line number of
    the declarations, bodies and following code is unchanged; the reader
    keeps taking all text from the original bytes.  Whitespace inside strings
    and block comments is harmless to move; a break that ends a ``//``
    comment is left alone.
    """
    if b"where" not in content_bytes:
        return content_bytes

    def repl(match: "re.Match[bytes]") -> bytes:
        region = match.group(0)
        line_start = content_bytes.rfind(b"\n", 0, match.start()) + 1
        if b"//" in content_bytes[line_start : match.start()]:
            return region
        breaks = b"".join(_LINE_BREAK.findall(match.group(1) + match.group(2)))
        new = b" where" + breaks
        if len(new) > len(region):
            return region
        return new + b" " * (len(region) - len(new))

    return _WHERE_ON_NEW_LINE.sub(repl, content_bytes)


# ---------------------------------------------------------------------------
# AST helper functions
# ---------------------------------------------------------------------------


def _text(node: Node, content_bytes: bytes) -> str:
    return (
        content_bytes[node.start_byte : node.end_byte]
        .decode("utf-8", errors="replace")
        .strip()
    )


def _collapse(text: str) -> str:
    return " ".join(text.split())


def _get_package_name(root: Node, content_bytes: bytes) -> Optional[str]:
    for child in root.children:
        if child.type == "package_header":
            for sub in child.children:
                if sub.type == "identifier":
                    return _text(sub, content_bytes)
    return None


def _get_name(node: Node, content_bytes: bytes) -> Optional[str]:
    """Name of a class/object/companion/function/type alias declaration."""
    if node.type == "property_declaration":
        for child in node.children:
            if child.type == "variable_declaration":
                for sub in child.children:
                    if sub.type == "simple_identifier":
                        return _text(sub, content_bytes)
            if child.type == "multi_variable_declaration":
                return _text(child, content_bytes)
        return None
    if node.type == "enum_entry":
        for child in node.children:
            if child.type == "simple_identifier":
                return _text(child, content_bytes)
        return None
    if node.type == "function_declaration":
        for child in node.children:
            if child.type == "simple_identifier":
                return _text(child, content_bytes)
        return None
    for child in node.children:
        if child.type in ("type_identifier", "simple_identifier"):
            return _text(child, content_bytes)
    if node.type == "companion_object":
        return "Companion"
    return None


def _get_body(node: Node) -> Optional[Node]:
    for child in node.children:
        if child.type in _BODY_TYPES:
            return child
    return None


def _header_until(node: Node, content_bytes: bytes, stop_types) -> str:
    """Declaration text up to (excluding) the first child of *stop_types*.

    Leading comments attached to the node are skipped so the header starts at
    the first modifier/keyword.
    """
    start = node.start_byte
    end = node.end_byte
    for child in node.children:
        if child.type in stop_types:
            end = child.start_byte
            break
    header = content_bytes[start:end].decode("utf-8", errors="replace").strip()
    return _collapse(header).rstrip("{").strip()


def _get_class_header(node: Node, content_bytes: bytes) -> str:
    """e.g. ``@Ann data class P(val x: Int) : Base(), I`` / ``companion object Factory``."""
    return _header_until(node, content_bytes, _BODY_TYPES)


def _get_function_signature(node: Node, content_bytes: bytes) -> str:
    """Function signature without the body (block or ``= expr``)."""
    return _header_until(node, content_bytes, {"function_body"})


def _get_constructor_signature(node: Node, content_bytes: bytes) -> str:
    return _header_until(node, content_bytes, {"statements", "block", "{"})


def _get_property_signature(node: Node, content_bytes: bytes) -> str:
    """Property declaration without initializer/accessor bodies."""
    stop = {"getter", "setter", "property_delegate"}
    end = node.end_byte
    for child in node.children:
        if child.type in stop:
            end = child.start_byte
            break
    text = content_bytes[node.start_byte : end].decode("utf-8", errors="replace")
    first = text.strip().split("\n")[0].strip()
    return first


def _get_receiver_type(node: Node, content_bytes: bytes) -> Optional[str]:
    for child in node.children:
        if child.type == "receiver_type":
            return _text(child, content_bytes)
    return None


def _class_kind(node: Node, content_bytes: bytes) -> str:
    """Return interface/object/companion object/enum class/data class/... ."""
    if node.type == "companion_object":
        return "companion object"
    if node.type == "object_declaration":
        return "object"
    modifiers: List[str] = []
    keyword = "class"
    for child in node.children:
        if child.type == "modifiers":
            for sub in child.children:
                if sub.type in ("class_modifier", "inheritance_modifier"):
                    modifiers.append(_text(sub, content_bytes))
        elif not child.is_named and child.type in ("interface", "class"):
            keyword = child.type
        elif not child.is_named and child.type in ("enum", "data", "sealed"):
            modifiers.append(child.type)
    if keyword == "interface":
        return "fun interface" if "fun" in modifiers else "interface"
    for mod in ("enum", "data", "sealed", "annotation", "value", "inline", "abstract"):
        if mod in modifiers:
            return f"{mod} class"
    return "class"


def _get_supertypes(node: Node, content_bytes: bytes) -> List[str]:
    result = []
    for child in node.children:
        if child.type == "delegation_specifier":
            result.append(_collapse(_text(child, content_bytes)))
        elif child.type == "delegation_specifiers":
            for sub in child.children:
                if sub.type == "delegation_specifier":
                    result.append(_collapse(_text(sub, content_bytes)))
    return result


def _iter_members(body: Node):
    """Yield body children, descending into ERROR nodes (grammar gaps)."""
    for child in body.children:
        if child.type == "ERROR":
            yield from _iter_members(child)
        else:
            yield child


def _leading_doc(node: Node, content_bytes: bytes) -> Optional[str]:
    """Doc comment(s) directly preceding *node* (KDoc ``/** */`` or ``//``).

    Consecutive comments immediately above the declaration are collected
    (no blank-line gap required).
    """
    docs: List[str] = []
    prev = node.prev_sibling
    expected_row = node.start_point[0]
    while prev is not None and prev.type in _COMMENT_TYPES:
        if prev.end_point[0] < expected_row - 1:
            break
        docs.append(_text(prev, content_bytes))
        expected_row = prev.start_point[0]
        prev = prev.prev_sibling
    if not docs:
        return None
    return "\n".join(reversed(docs))


def _count_lines(node: Node) -> int:
    return node.end_point[0] - node.start_point[0] + 1


def _nested_class_header(nesting: List[str], class_header: Optional[str]) -> Optional[str]:
    """Prefix a nested type's header with its outer-class chain.

    ``["Outer", "Middle", "Inner"]`` + ``"static class Inner"`` ->
    ``"Outer > Middle > static class Inner"``.  Top-level types (nesting of
    length <= 1) are returned unchanged.
    """
    if not class_header or not nesting or len(nesting) <= 1:
        return class_header
    return " > ".join(nesting[:-1]) + " > " + class_header


def _build_context_prefix(
    file_name: str,
    package_name: Optional[str] = None,
    class_name: Optional[str] = None,
    class_header: Optional[str] = None,
) -> str:
    """Same format as the Java reader's context prefix.

    Examples:
        // File: OrderService.kt
        // Package: com.example.orders
        // Class: class OrderService(private val repo: OrderRepository)
    """
    parts = [f"// File: {file_name}"]
    if package_name:
        parts.append(f"// Package: {package_name}")
    if class_name and class_header:
        parts.append(f"// Class: {class_header}")
    elif class_name:
        parts.append(f"// Class: {class_name}")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Reader class
# ---------------------------------------------------------------------------


class KotlinFileReader(BaseFileReader):
    """Semantic chunking for Kotlin files using Tree-sitter AST."""

    # Kotlin AST node type -> emitted node_type (Java-compatible names)
    LEAF_NODE_MAP = {
        "function_declaration": "method_declaration",
        "secondary_constructor": "constructor_declaration",
        "property_declaration": "field_declaration",
        "anonymous_initializer": "initializer_block",
        "type_alias": "type_alias_declaration",
        "multiline_comment": "block_comment",
        "line_comment": "block_comment",
    }
    LEAF_NODE_TYPES = set(LEAF_NODE_MAP)
    CONTAINER_NODE_TYPES = set(_CONTAINER_TYPES)
    ENUM_CONSTANT_TYPES = {"enum_entry"}
    NODE_TYPES = LEAF_NODE_TYPES | CONTAINER_NODE_TYPES | ENUM_CONSTANT_TYPES

    MIN_CHUNK_SIZE = 20
    MAX_CHUNK_CHARS = 24000
    MAX_SUMMARY_CHARS = 6000
    TRIVIAL_METHOD_LINES = 6
    MAX_GROUP_CHARS = 8000
    MIN_COMMENT_CHARS = 40

    _METHOD_TYPES = ("method_declaration", "constructor_declaration")

    def __init__(self):
        super().__init__()
        self._text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=128)

    # -- document creation (identical behaviour to Java) -------------------

    def _make_documents(
        self,
        chunk_text: str,
        node_type: str,
        start_line: int,
        end_line: int,
        start_byte: int,
        end_byte: int,
        file_path_str: str,
        file_datetime: dict,
        extra_metadata: Optional[dict] = None,
        max_chars: Optional[int] = None,
    ) -> List[Document]:
        if len(chunk_text) < self.MIN_CHUNK_SIZE:
            return []
        threshold = max_chars if max_chars is not None else self.MAX_CHUNK_CHARS
        base_metadata = {
            "file_path": file_path_str,
            "node_type": node_type,
            "start_line": start_line,
            "end_line": end_line,
            "start_byte": start_byte,
            "end_byte": end_byte,
            **file_datetime,
        }
        if extra_metadata:
            base_metadata.update(extra_metadata)
        if len(chunk_text) <= threshold:
            return [Document(text=chunk_text, metadata=base_metadata)]

        parts = self._text_splitter.split_text(chunk_text)
        # Every split part keeps the context prefix (Java only does this for
        # class_summary; for Kotlin all split parts stay self-describing).
        prefix_lines = []
        for line in chunk_text.split("\n"):
            if line.startswith("// File:") or line.startswith("// Package:") or line.startswith("// Class:"):
                prefix_lines.append(line)
            else:
                break
        context_prefix = "\n".join(prefix_lines)
        docs = []
        for i, part in enumerate(parts):
            if len(part.strip()) < self.MIN_CHUNK_SIZE:
                continue
            text = part
            if context_prefix and not part.startswith("// File:"):
                text = f"{context_prefix}\n{part}"
            docs.append(
                Document(
                    text=text,
                    metadata={
                        **base_metadata,
                        "node_type": f"{node_type}_split",
                        "split_part": i,
                        "split_total": len(parts),
                    },
                )
            )
        return docs

    # -- summaries ---------------------------------------------------------

    def _member_line(self, child: Node, content_bytes: bytes) -> Optional[str]:
        t = child.type
        if t == "function_declaration":
            return _get_function_signature(child, content_bytes)
        if t == "secondary_constructor":
            return _get_constructor_signature(child, content_bytes)
        if t == "property_declaration":
            return _get_property_signature(child, content_bytes)
        if t == "enum_entry":
            # Whole entry (constructor arguments may span lines); an entry
            # body is summarised as ``{ ... }`` and emitted as its own chunk.
            line = _header_until(child, content_bytes, {"class_body"}).rstrip(",")
            if _get_body(child) is not None:
                line += " { ... }"
            if len(line) > 300:
                line = line[:297] + "..."
            # Same-line trailing comment (``A(1),  // meaning``), possibly
            # after the separating comma token.
            nxt = child.next_sibling
            if nxt is not None and nxt.type in (",", ";"):
                nxt = nxt.next_sibling
            if (
                nxt is not None
                and nxt.type in _COMMENT_TYPES
                and nxt.start_point[0] == child.end_point[0]
            ):
                line += "  " + _collapse(_text(nxt, content_bytes))
            # Doc comments above the entry; skip a comment that trails the
            # previous entry on its own line (already attached there).
            docs: List[str] = []
            prev = child.prev_sibling
            row = child.start_point[0]
            while prev is not None and prev.type in _COMMENT_TYPES:
                if prev.end_point[0] < row - 1:
                    break
                before = prev.prev_sibling
                if before is not None and before.type in (",", ";"):
                    before = before.prev_sibling
                if (
                    before is not None
                    and before.type not in _COMMENT_TYPES
                    and before.end_point[0] == prev.start_point[0]
                ):
                    break
                docs.append(_collapse(_text(prev, content_bytes)))
                row = prev.start_point[0]
                prev = prev.prev_sibling
            if docs:
                line = "\n".join(reversed(docs)) + "\n" + line
            return line
        if t == "anonymous_initializer":
            return "init { ... }"
        if t == "type_alias":
            return _collapse(_text(child, content_bytes))
        if t in _CONTAINER_TYPES:
            header = _get_class_header(child, content_bytes)
            return f"{header} {{ ... }}" if header else None
        return None

    def _build_class_summary(
        self, node: Node, content_bytes: bytes, context_prefix: str
    ) -> Optional[str]:
        body = _get_body(node)
        if body is None:
            return None
        header = _get_class_header(node, content_bytes)
        if not header:
            return None
        members = []
        for child in _iter_members(body):
            line = self._member_line(child, content_bytes)
            if line:
                members.append(f"    {line}")
        if not members:
            return None
        return f"{context_prefix}\n{header} {{\n" + "\n".join(members) + "\n}"

    def _build_class_overview(
        self, node: Node, content_bytes: bytes, context_prefix: str, class_name: str
    ) -> Optional[str]:
        body = _get_body(node)
        header = _get_class_header(node, content_bytes)
        if body is None or not header:
            return None
        kind = _class_kind(node, content_bytes)
        buckets: Dict[str, List[str]] = {
            "constants": [],
            "properties": [],
            "constructors": [],
            "functions": [],
            "inner types": [],
        }
        for child in _iter_members(body):
            name = _get_name(child, content_bytes)
            if child.type == "enum_entry" and name:
                buckets["constants"].append(name)
            elif child.type == "property_declaration" and name:
                buckets["properties"].append(name)
            elif child.type == "secondary_constructor":
                buckets["constructors"].append("constructor")
            elif child.type == "function_declaration" and name:
                buckets["functions"].append(name)
            elif child.type in _CONTAINER_TYPES and name:
                buckets["inner types"].append(name)
        supertypes = _get_supertypes(node, content_bytes)
        inherits = f" extending {', '.join(supertypes)}" if supertypes else ""
        counts = [f"{len(v)} {k}" for k, v in buckets.items() if v]
        member_desc = ", ".join(counts) if counts else "no members"
        sentence = f"// {class_name} is a Kotlin {kind}{inherits} with {member_desc}."
        max_members = 20
        sections = []
        for k, v in buckets.items():
            if not v:
                continue
            line = f"  {k}: {', '.join(v[:max_members])}"
            if len(v) > max_members:
                line += f" ... ({len(v) - max_members} more)"
            sections.append(line)
        return f"{context_prefix}\n{sentence}\n{header} {{\n" + "\n".join(sections) + "\n}"

    # -- main entry --------------------------------------------------------

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents: List[Document] = []
        try:
            content, content_bytes = read_file_with_encoding_and_bytes(file)
        except Exception as e:
            log_warn(f"Failed to read {file}: {e}")
            return []
        if not content.strip():
            return []

        file_path_str = str(file)
        file_name = file.name
        file_datetime = get_file_datetime(file)
        is_script = file.suffix.lower() == ".kts"

        try:
            tree = _parser.parse(_join_where_clauses(content_bytes))
        except Exception as e:
            log_warn(f"Tree-sitter Kotlin parse failed for {file}: {e}")
            return [
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "parse_error": str(e),
                        **file_datetime,
                    },
                )
            ]

        root = tree.root_node
        package_name = _get_package_name(root, content_bytes)
        base_prefix = _build_context_prefix(file_name, package_name)

        def base_meta(class_name: Optional[str] = None) -> dict:
            meta: dict = {}
            if package_name:
                meta["package_name"] = package_name
            meta["unit_name"] = file.stem
            if class_name:
                meta["class_name"] = class_name
            return meta

        # ── Imports → single import_group ──
        imports: List[Node] = []
        for child in root.children:
            if child.type == "import_list":
                imports.extend(c for c in child.children if c.type == "import_header")
            elif child.type == "import_header":
                imports.append(child)
        if imports:
            texts = []
            for imp in imports:
                # import_header may swallow a following comment; keep only the
                # import itself.
                end = imp.start_byte
                for c in imp.children:
                    if c.type not in _COMMENT_TYPES:
                        end = c.end_byte
                texts.append(
                    _collapse(content_bytes[imp.start_byte:end].decode("utf-8", errors="replace"))
                )
            last_end_node = imports[-1]
            for c in imports[-1].children:
                if c.type not in _COMMENT_TYPES:
                    last_end_node = c
            meta = base_meta()
            documents.extend(
                self._make_documents(
                    f"{base_prefix}\n" + "\n".join(texts),
                    "import_group",
                    imports[0].start_point[0] + 1,
                    last_end_node.end_point[0] + 1,
                    imports[0].start_byte,
                    last_end_node.end_byte,
                    file_path_str,
                    file_datetime,
                    extra_metadata=meta,
                )
            )

        emitted_summaries: set = set()
        # (node_type, node, full_text, class_name, extra_meta)
        raw: List[Tuple[str, Node, str, str, dict]] = []
        script_nodes: List[Node] = []

        def prefix_for(
            current_class: Optional[str], nesting: List[str], header: Optional[str]
        ) -> str:
            display = " > ".join(nesting) if len(nesting) > 1 else current_class
            return _build_context_prefix(
                file_name, package_name, display, _nested_class_header(nesting, header)
            )

        def traverse(
            node: Node,
            current_class: Optional[str],
            nesting: List[str],
            current_header: Optional[str] = None,
        ) -> None:
            if node.type in _CONTAINER_TYPES:
                name = _get_name(node, content_bytes) or ""
                header = _get_class_header(node, content_bytes)
                new_nesting = nesting + [name] if name else nesting
                display = " > ".join(new_nesting) if len(new_nesting) > 1 else name
                prefix = _build_context_prefix(
                    file_name, package_name, display, _nested_class_header(new_nesting, header)
                )
                extra = {"kotlin_kind": _class_kind(node, content_bytes)}
                if current_class:
                    extra["outer_class"] = current_class
                summary = self._build_class_summary(node, content_bytes, prefix)
                if summary is None and header:
                    # Body-less or empty-body declaration (``data class
                    # Order(val id: Long)``, ``class FooException(...) : Exception() {}``,
                    # ``object Empty``): the declaration *is* the whole API.
                    summary = f"{prefix}\n{_text(node, content_bytes)}"
                if summary and current_class:
                    doc = _leading_doc(node, content_bytes)
                    if doc:
                        summary = summary.replace(f"{prefix}\n", f"{prefix}\n{doc}\n", 1)
                if summary:
                    raw.append(("class_summary", node, summary, name, extra))
                    emitted_summaries.add(name)
                    if len(summary) > self.MAX_SUMMARY_CHARS:
                        overview = self._build_class_overview(
                            node, content_bytes, prefix, display or name
                        )
                        if overview:
                            raw.append(("class_overview", node, overview, name, extra))
                body = _get_body(node)
                if body is not None:
                    for child in _iter_members(body):
                        traverse(child, name, new_nesting, header)
                return

            if node.type in self.LEAF_NODE_MAP:
                chunk_text = _text(node, content_bytes)
                if node.type in _COMMENT_TYPES:
                    if len(chunk_text) < self.MIN_COMMENT_CHARS:
                        return
                    if current_class and current_class in emitted_summaries:
                        return
                extra: dict = {}
                if node.type == "function_declaration":
                    receiver = _get_receiver_type(node, content_bytes)
                    if receiver:
                        extra["receiver_type"] = receiver
                    fname = _get_name(node, content_bytes)
                    if fname:
                        extra["function_name"] = fname
                if current_class and node.type not in _COMMENT_TYPES:
                    # Doc comments inside a summarised class are not emitted
                    # standalone; keep them with the member they document.
                    doc = _leading_doc(node, content_bytes)
                    if doc:
                        chunk_text = f"{doc}\n{chunk_text}"
                full = f"{prefix_for(current_class, nesting, current_header)}\n{chunk_text}"
                raw.append((self.LEAF_NODE_MAP[node.type], node, full, current_class or "", extra))
                return

            if node.type == "enum_entry":
                if (
                    current_class
                    and current_class in emitted_summaries
                    and _get_body(node) is None
                ):
                    return
                full = f"{prefix_for(current_class, nesting, current_header)}\n{_text(node, content_bytes)}"
                raw.append(("enum_constant", node, full, current_class or "", {}))
                return

            for child in node.children:
                traverse(child, current_class, nesting, current_header)

        skip_top = {"package_header", "import_list", "import_header", "shebang_line", "file_annotation"}
        for child in root.children:
            if child.type in skip_top:
                # The grammar attaches comments that follow the package/import
                # headers to those nodes; recover them as standalone comments.
                stack = list(child.children)
                while stack:
                    n = stack.pop(0)
                    if n.type in _COMMENT_TYPES:
                        traverse(n, None, [])
                    else:
                        stack.extend(n.children)
                continue
            if is_script and child.is_named and child.type not in self.NODE_TYPES and child.type != "ERROR":
                script_nodes.append(child)
                continue
            traverse(child, None, [])

        # ── Pass 2: trivial-method grouping + emit ──
        i = 0
        while i < len(raw):
            node_type, node, full_text, class_name, extra = raw[i]
            if node_type in self._METHOD_TYPES and _count_lines(node) <= self.TRIVIAL_METHOD_LINES:
                run = [node]
                j = i + 1
                while j < len(raw):
                    nt, nn, _, nc, _ = raw[j]
                    if nt in self._METHOD_TYPES and nc == class_name and _count_lines(nn) <= self.TRIVIAL_METHOD_LINES:
                        run.append(nn)
                        j += 1
                    else:
                        break
                if len(run) >= 3:
                    # Same prefix as the first method of the run.
                    prefix_lines = []
                    for ln in full_text.split("\n"):
                        if not ln.startswith(("// File:", "// Package:", "// Class:")):
                            break
                        prefix_lines.append(ln)
                    prefix = "\n".join(prefix_lines)
                    documents.extend(
                        self._group_trivial_methods(
                            run, content_bytes, prefix, file_path_str, file_datetime,
                            base_meta(class_name or None),
                        )
                    )
                    i = j
                    continue
            meta = base_meta(class_name or None)
            meta.update(extra)
            documents.extend(
                self._make_documents(
                    full_text,
                    node_type,
                    node.start_point[0] + 1,
                    node.end_point[0] + 1,
                    node.start_byte,
                    node.end_byte,
                    file_path_str,
                    file_datetime,
                    extra_metadata=meta,
                    max_chars=self.MAX_SUMMARY_CHARS if node_type == "class_summary" else None,
                )
            )
            i += 1

        if script_nodes:
            body = "\n".join(_text(n, content_bytes) for n in script_nodes)
            documents.extend(
                self._make_documents(
                    f"{base_prefix}\n{body}",
                    "script_body",
                    script_nodes[0].start_point[0] + 1,
                    script_nodes[-1].end_point[0] + 1,
                    script_nodes[0].start_byte,
                    script_nodes[-1].end_byte,
                    file_path_str,
                    file_datetime,
                    extra_metadata=base_meta(),
                )
            )

        if not documents:
            meta = {"file_path": file_path_str, "node_type": "full_file", **file_datetime}
            meta.update(base_meta())
            documents.append(Document(text=content, metadata=meta))
        return documents

    def _group_trivial_methods(
        self,
        nodes: List[Node],
        content_bytes: bytes,
        context_prefix: str,
        file_path_str: str,
        file_datetime: dict,
        extra_metadata: Optional[dict] = None,
    ) -> List[Document]:
        docs: List[Document] = []
        group: List[Node] = []
        chars = 0

        def flush() -> None:
            if not group:
                return
            texts = [_text(m, content_bytes) for m in group]
            text = f"{context_prefix}\n// Method group: {len(group)} methods\n" + "\n\n".join(texts)
            meta = {"group_count": len(group)}
            if extra_metadata:
                meta.update(extra_metadata)
            docs.extend(
                self._make_documents(
                    text, "method_group",
                    group[0].start_point[0] + 1, group[-1].end_point[0] + 1,
                    group[0].start_byte, group[-1].end_byte,
                    file_path_str, file_datetime, extra_metadata=meta,
                )
            )

        for n in nodes:
            length = len(_text(n, content_bytes))
            if group and chars + length > self.MAX_GROUP_CHARS:
                flush()
                group = []
                chars = 0
            group.append(n)
            chars += length
        flush()
        return docs


# ────────────────────────────────────────────────
# Rerank profile (query-time ranking knowledge, see shared/rerank_profile.py)
# ────────────────────────────────────────────────

# Dotted stems allowed: build.gradle.kts -> build.gradle
RERANK_PROFILE = java_style_profile(
    "kotlin", r"\b([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*)\.kts?\b"
)

KotlinFileReader.rerank_profile = RERANK_PROFILE
