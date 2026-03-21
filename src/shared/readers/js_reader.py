"""
JavaScript/TypeScript file reader (.js, .ts) using Tree-sitter AST.

Chunking strategy — module-context-aware with intelligent grouping:

1. **Context prefix on every chunk**: Each chunk starts with a comment block
   identifying the file name and (if applicable) the owning class/namespace,
   so every chunk is self-describing for RAG search.

2. **Class summary chunk**: For each ES6 class, emit a dedicated chunk
   containing the declaration header plus all field and method signatures
   (no bodies).  This answers "What is ResponseError?" and "What methods
   does SearchingResultsComponent have?".

3. **Class overview chunk**: For large classes where the summary exceeds
   MAX_SUMMARY_CHARS, emit a compact natural-language overview.

4. **IIFE drilling**: Immediately-Invoked Function Expressions (common in
   legacy JS) are drilled through to find the real content inside.
   ``(function() { ... })()`` is unwrapped to process inner declarations.

5. **AMD/require module drilling**: ``define(['deps'], function($) { ... })``
   and ``require(['deps'], function() { ... })`` patterns are drilled
   through to process the callback body.

6. **Export unwrapping (TypeScript)**: ``export_statement`` nodes are
   unwrapped to process the actual declaration child.

7. **Prototype method grouping**: Consecutive ``Foo.prototype.method = ...``
   assignments on the same constructor are grouped together.

8. **Trivial function grouping**: Consecutive small function declarations
   (<=6 lines) are grouped into a single chunk.

9. **Import grouping**: All import/require statements are collected into a
   single "import_group" chunk.

10. **Interface/type alias support (TypeScript)**: ``interface_declaration``
    and ``type_alias_declaration`` are emitted as dedicated chunks.

Node types emitted:
    class_summary, class_summary_split, class_overview,
    function_declaration, function_declaration_split,
    method_definition, method_definition_split,
    generator_function_declaration,
    arrow_function, arrow_function_split,
    variable_declaration, lexical_declaration,
    interface_declaration, type_alias_declaration,
    import_group, comment,
    function_group, prototype_group,
    assignment_expression, expression_statement,
    full_file
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter
from tree_sitter import Node
from tree_sitter_language_pack import get_parser

from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding_and_bytes,
)
from shared.log import log_warn

_js_parser = get_parser("javascript")
_ts_parser = get_parser("typescript")


# ────────────────────────────────────────────────
# AST helper functions
# ────────────────────────────────────────────────


def _get_node_text(node: Node, content_bytes: bytes) -> str:
    """Extract text content from an AST node."""
    return (
        content_bytes[node.start_byte : node.end_byte]
        .decode("utf-8", errors="replace")
        .strip()
    )


def _get_identifier(node: Node, content_bytes: bytes) -> Optional[str]:
    """Extract the identifier (name) from a declaration node.

    Works for function_declaration, class_declaration, method_definition,
    interface_declaration, type_alias_declaration, etc.
    """
    for child in node.children:
        if child.type in ("identifier", "property_identifier", "type_identifier"):
            return (
                content_bytes[child.start_byte : child.end_byte]
                .decode("utf-8", errors="replace")
                .strip()
            )
    return None


def _count_body_lines(node: Node) -> int:
    """Count the number of source lines in a node."""
    return node.end_point[0] - node.start_point[0] + 1


def _is_iife(node: Node) -> bool:
    """Check if a node is an IIFE pattern: (function(){ ... })() or !function(){ ... }().

    IIFE patterns in the AST:
    - expression_statement > call_expression > parenthesized_expression > function_expression
    - expression_statement > call_expression > function_expression (with !)
    - expression_statement > parenthesized_expression > call_expression > function_expression
      (alternate form where the outer parens are separate from the call)
    """
    if node.type != "expression_statement":
        return False
    for child in node.children:
        if child.type == "call_expression":
            return _is_iife_call(child)
        # Alternate: (call_expression)(args) parsed as paren > call
        if child.type == "parenthesized_expression":
            for sub in child.children:
                if sub.type == "call_expression":
                    return _is_iife_call(sub)
    return False


def _is_iife_call(node: Node) -> bool:
    """Check if a call_expression is an IIFE call."""
    if node.type != "call_expression":
        return False
    for child in node.children:
        if child.type == "parenthesized_expression":
            for sub in child.children:
                if sub.type in ("function_expression", "arrow_function"):
                    return True
        if child.type in ("function_expression", "arrow_function"):
            return True
    return False


def _get_iife_body(node: Node) -> Optional[Node]:
    """Extract the statement_block from an IIFE expression_statement.

    Returns the statement_block node inside the function, or None.
    """
    if node.type != "expression_statement":
        return None
    for child in node.children:
        if child.type == "call_expression":
            return _get_iife_call_body(child)
        # Alternate: paren > call_expression
        if child.type == "parenthesized_expression":
            for sub in child.children:
                if sub.type == "call_expression":
                    return _get_iife_call_body(sub)
    return None


def _get_iife_call_body(node: Node) -> Optional[Node]:
    """Extract the statement_block from an IIFE call_expression."""
    if node.type != "call_expression":
        return None
    for child in node.children:
        if child.type == "parenthesized_expression":
            for sub in child.children:
                if sub.type in ("function_expression", "arrow_function"):
                    return _get_function_body(sub)
        if child.type in ("function_expression", "arrow_function"):
            return _get_function_body(child)
    return None


def _get_function_body(node: Node) -> Optional[Node]:
    """Get the statement_block body from a function/arrow node."""
    for child in node.children:
        if child.type == "statement_block":
            return child
    return None


def _is_amd_define(node: Node, content_bytes: bytes) -> bool:
    """Check if a node is an AMD define() or require() call wrapping a module.

    Patterns:
        define(['jquery', ...], function($) { ... })
        require(['deps'], function() { ... })
        (function(require, define) { define([...], function(...) { ... }); })(require, define)
    """
    if node.type == "expression_statement":
        for child in node.children:
            if child.type == "call_expression":
                return _is_amd_call(child, content_bytes)
    return False


def _is_amd_call(node: Node, content_bytes: bytes) -> bool:
    """Check if a call_expression is define() or require() with a callback."""
    if node.type != "call_expression":
        return False
    func_node = node.children[0] if node.children else None
    if func_node is None:
        return False
    func_name = _get_node_text(func_node, content_bytes)
    return func_name in ("define", "require")


def _get_amd_callback_body(node: Node, content_bytes: bytes) -> Optional[Node]:
    """Extract the statement_block from the AMD define/require callback.

    define(['deps'], function($) { <body> })
    """
    if node.type != "expression_statement":
        return None
    for child in node.children:
        if child.type == "call_expression":
            return _get_amd_call_body(child, content_bytes)
    return None


def _get_amd_call_body(call_node: Node, content_bytes: bytes) -> Optional[Node]:
    """Get the callback body from a define/require call_expression."""
    if not _is_amd_call(call_node, content_bytes):
        return None
    # Arguments is the arguments node
    for child in call_node.children:
        if child.type == "arguments":
            # Find the function argument (last argument is typically the callback)
            for arg in reversed(child.children):
                if arg.type in ("function_expression", "arrow_function"):
                    return _get_function_body(arg)
    return None


def _is_prototype_assignment(node: Node, content_bytes: bytes) -> Optional[str]:
    """Check if node is Foo.prototype.bar = function(...) { ... }.

    Returns the constructor name (e.g. "Foo") if it's a prototype assignment,
    or None otherwise.
    """
    if node.type != "expression_statement":
        return None
    for child in node.children:
        if child.type == "assignment_expression":
            lhs = child.children[0] if child.children else None
            if lhs is None or lhs.type != "member_expression":
                return None
            lhs_text = _get_node_text(lhs, content_bytes)
            if ".prototype." in lhs_text:
                # Extract constructor name: "Foo.prototype.bar" -> "Foo"
                parts = lhs_text.split(".prototype.")
                if len(parts) >= 2:
                    return parts[0]
    return None


def _get_prototype_method_name(node: Node, content_bytes: bytes) -> Optional[str]:
    """Extract the method name from a prototype assignment.

    Foo.prototype.bar = function() { ... } -> "bar"
    """
    if node.type != "expression_statement":
        return None
    for child in node.children:
        if child.type == "assignment_expression":
            lhs = child.children[0] if child.children else None
            if lhs is None or lhs.type != "member_expression":
                return None
            lhs_text = _get_node_text(lhs, content_bytes)
            if ".prototype." in lhs_text:
                parts = lhs_text.split(".prototype.")
                if len(parts) >= 2:
                    return parts[-1]
    return None


def _get_class_header_js(node: Node, content_bytes: bytes) -> str:
    """Extract the class header line (no body).

    Returns e.g.:
        'export class ResponseError extends Error'
        'class Slider'
    """
    body_types = {"class_body"}
    header_end = node.end_byte
    for child in node.children:
        if child.type in body_types:
            header_end = child.start_byte
            break

    header = (
        content_bytes[node.start_byte : header_end]
        .decode("utf-8", errors="replace")
        .strip()
    )
    header = " ".join(header.split())
    return header


def _get_method_signature_js(node: Node, content_bytes: bytes) -> str:
    """Extract method/function signature without the body.

    For method_definition, function_declaration, etc.
    """
    sig_end = node.end_byte
    for child in node.children:
        if child.type == "statement_block":
            sig_end = child.start_byte
            break

    sig = (
        content_bytes[node.start_byte : sig_end]
        .decode("utf-8", errors="replace")
        .strip()
        .rstrip("{")
        .strip()
    )
    sig = " ".join(sig.split())
    return sig


def _get_superclass_js(node: Node, content_bytes: bytes) -> Optional[str]:
    """Extract 'extends Foo' from a class_declaration."""
    found_extends = False
    for child in node.children:
        if child.type == "class_heritage":
            for sub in child.children:
                if sub.type in ("identifier", "member_expression"):
                    return _get_node_text(sub, content_bytes)
        # Fallback: look for extends keyword
        if _get_node_text(child, content_bytes) == "extends":
            found_extends = True
            continue
        if found_extends and child.type in ("identifier", "member_expression"):
            return _get_node_text(child, content_bytes)
    return None


def _unwrap_export(node: Node) -> Node:
    """If node is an export_statement, return the actual declaration child.

    export class Foo { ... }  ->  class_declaration
    export function bar() {}  ->  function_declaration
    export const x = ...      ->  lexical_declaration
    export default ...        ->  the inner node
    """
    if node.type != "export_statement":
        return node
    for child in node.children:
        if child.type in (
            "class_declaration",
            "function_declaration",
            "generator_function_declaration",
            "lexical_declaration",
            "variable_declaration",
            "interface_declaration",
            "type_alias_declaration",
            "enum_declaration",
            "abstract_class_declaration",
        ):
            return child
    return node


def _build_context_prefix(
    file_name: str,
    class_name: Optional[str] = None,
    class_header: Optional[str] = None,
) -> str:
    """Build a context prefix comment for chunk self-identification.

    Examples:
        // File: connectionsSearcher.js

        // File: EPodroznikCarPooling.ts
        // Class: ResponseError extends Error
    """
    parts = [f"// File: {file_name}"]
    if class_name and class_header:
        parts.append(f"// Class: {class_header}")
    elif class_name:
        parts.append(f"// Class: {class_name}")
    return "\n".join(parts)


# ────────────────────────────────────────────────
# Reader class
# ────────────────────────────────────────────────


class JSFileReader(BaseFileReader):
    """Semantic chunking for JavaScript/TypeScript files using Tree-sitter AST.

    Produces self-describing chunks with context prefixes, class summary
    chunks, import group chunks, IIFE drilling, and grouped trivial functions.
    """

    # Leaf node types: always emit as-is, never recurse.
    LEAF_TYPES = {
        "function_declaration",
        "generator_function_declaration",
        "comment",
    }

    # Container types: recurse if matched descendants exist.
    CONTAINER_TYPES = {
        "class_declaration",
        "abstract_class_declaration",
    }

    # TS-specific leaf types
    TS_LEAF_TYPES = {
        "interface_declaration",
        "type_alias_declaration",
        "enum_declaration",
    }

    # Import/require statement types
    IMPORT_TYPES = {
        "import_statement",
    }

    MIN_CHUNK_SIZE = 20  # Discard chunks smaller than this (chars)
    MAX_CHUNK_CHARS = 24000  # ~6000 tokens — split oversized chunks
    MAX_SUMMARY_CHARS = 6000
    TRIVIAL_FUNC_LINES = 6  # Functions <= this are "trivial" for grouping
    MAX_GROUP_CHARS = 8000
    MIN_COMMENT_CHARS = 40

    def __init__(self):
        super().__init__()
        self._text_splitter = TokenTextSplitter(
            chunk_size=1024,
            chunk_overlap=128,
        )

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
        """Create Document(s) from a chunk, splitting if oversized."""
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

        # Oversized: split with TokenTextSplitter
        parts = self._text_splitter.split_text(chunk_text)

        # For class_summary splits, re-prepend context prefix
        context_prefix = ""
        if node_type == "class_summary":
            prefix_lines = []
            for line in chunk_text.split("\n"):
                if line.startswith("//"):
                    prefix_lines.append(line)
                else:
                    break
            if prefix_lines:
                context_prefix = "\n".join(prefix_lines)

        docs = []
        for i, part in enumerate(parts):
            if len(part.strip()) < self.MIN_CHUNK_SIZE:
                continue
            text = part
            if context_prefix and not part.startswith("//"):
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

    def _build_class_summary(
        self,
        node: Node,
        content_bytes: bytes,
        context_prefix: str,
    ) -> Optional[str]:
        """Build a class summary: header + all member signatures (no bodies).

        For ES6 class like:
            export class ResponseError extends Error {
                constructor(private readonly _errorData: ApiError)
                getErrorData()
            }
        """
        body_node = None
        for child in node.children:
            if child.type == "class_body":
                body_node = child
                break

        if body_node is None:
            return None

        header = _get_class_header_js(node, content_bytes)
        if not header:
            return None

        members: List[str] = []

        for child in body_node.children:
            if child.type in ("{", "}", ";"):
                continue

            if child.type == "method_definition":
                sig = _get_method_signature_js(child, content_bytes)
                members.append(f"    {sig}")

            elif child.type in (
                "public_field_definition",
                "field_definition",
                "property_definition",
            ):
                text = _get_node_text(child, content_bytes)
                first_line = text.split("\n")[0].strip()
                members.append(f"    {first_line}")

            elif child.type == "comment":
                pass  # Skip comments in summary

            elif child.type in self.CONTAINER_TYPES:
                inner_header = _get_class_header_js(child, content_bytes)
                if inner_header:
                    members.append(f"    {inner_header} {{ ... }}")

        if not members:
            return None

        body_text = "\n".join(members)
        return f"{context_prefix}\n{header} {{\n{body_text}\n}}"

    def _build_class_overview(
        self,
        node: Node,
        content_bytes: bytes,
        context_prefix: str,
        class_name: str,
    ) -> Optional[str]:
        """Build a compact class overview for large classes."""
        header = _get_class_header_js(node, content_bytes)
        if not header:
            return None

        is_abstract = "abstract " in header
        superclass = _get_superclass_js(node, content_bytes)

        body_node = None
        for child in node.children:
            if child.type == "class_body":
                body_node = child
                break
        if body_node is None:
            return None

        fields: List[str] = []
        methods: List[str] = []
        constructors: List[str] = []

        for child in body_node.children:
            if child.type in ("{", "}", ";"):
                continue
            if child.type == "method_definition":
                name = _get_identifier(child, content_bytes)
                if name == "constructor":
                    constructors.append(name)
                elif name:
                    methods.append(name)
            elif child.type in (
                "public_field_definition",
                "field_definition",
                "property_definition",
            ):
                name = _get_identifier(child, content_bytes)
                if name:
                    fields.append(name)

        kind = "abstract class" if is_abstract else "class"
        inherits_str = f" extends {superclass}" if superclass else ""

        member_parts = []
        if fields:
            member_parts.append(f"{len(fields)} fields")
        if constructors:
            member_parts.append(f"{len(constructors)} constructors")
        if methods:
            member_parts.append(f"{len(methods)} methods")
        member_desc = ", ".join(member_parts) if member_parts else "no members"

        summary_sentence = (
            f"// {class_name} is a JavaScript/TypeScript {kind}{inherits_str} "
            f"with {member_desc}."
        )

        MAX_MEMBERS = 20
        sections: List[str] = []
        if fields:
            shown = fields[:MAX_MEMBERS]
            line = f"  fields: {', '.join(shown)}"
            if len(fields) > MAX_MEMBERS:
                line += f" ... ({len(fields) - MAX_MEMBERS} more)"
            sections.append(line)
        if constructors:
            sections.append(f"  constructors: {', '.join(constructors)}")
        if methods:
            shown = methods[:MAX_MEMBERS]
            line = f"  methods: {', '.join(shown)}"
            if len(methods) > MAX_MEMBERS:
                line += f" ... ({len(methods) - MAX_MEMBERS} more)"
            sections.append(line)

        section_text = "\n".join(sections)
        return f"{context_prefix}\n{summary_sentence}\n{header} {{\n{section_text}\n}}"

    def _group_functions(
        self,
        funcs: List[Tuple[Node, str, str]],
        content_bytes: bytes,
        context_prefix: str,
        file_path_str: str,
        file_datetime: dict,
        extra_metadata: Optional[dict] = None,
        group_type: str = "function_group",
    ) -> List[Document]:
        """Group consecutive trivial functions into combined chunks.

        Args:
            funcs: List of (node, node_type, class_name_or_empty) tuples.
            group_type: The node_type for the group chunk.
        """
        if not funcs:
            return []

        docs: List[Document] = []
        current_group: List[Node] = []
        current_chars = 0

        def flush_group() -> None:
            if not current_group:
                return
            texts = [_get_node_text(m, content_bytes) for m in current_group]
            count = len(current_group)
            group_text = (
                f"{context_prefix}\n"
                f"// {group_type}: {count} items\n" + "\n\n".join(texts)
            )
            first = current_group[0]
            last = current_group[-1]
            merged_meta = {"group_count": count}
            if extra_metadata:
                merged_meta.update(extra_metadata)
            docs.extend(
                self._make_documents(
                    group_text,
                    group_type,
                    first.start_point[0] + 1,
                    last.end_point[0] + 1,
                    first.start_byte,
                    last.end_byte,
                    file_path_str,
                    file_datetime,
                    extra_metadata=merged_meta,
                )
            )

        for node, _, _ in funcs:
            text = _get_node_text(node, content_bytes)
            text_len = len(text)

            if current_group and current_chars + text_len > self.MAX_GROUP_CHARS:
                flush_group()
                current_group = []
                current_chars = 0

            current_group.append(node)
            current_chars += text_len

        flush_group()
        return docs

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
        is_typescript = file.suffix.lower() in (".ts", ".tsx")

        parser = _ts_parser if is_typescript else _js_parser

        try:
            tree = parser.parse(content_bytes)
        except Exception as e:
            log_warn(f"Tree-sitter JS/TS parse failed for {file}: {e}")
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "parse_error": str(e),
                        **file_datetime,
                    },
                )
            )
            return documents

        root = tree.root_node
        base_prefix = _build_context_prefix(file_name)

        # ── Collect imports into a single group ──
        imports: List[Node] = []
        # Also collect require() calls at top level as imports
        for child in root.children:
            actual = _unwrap_export(child) if is_typescript else child
            if actual.type in ("import_statement",):
                imports.append(child)  # Use original node (with export if any)
            elif actual.type in (
                "variable_declaration",
                "lexical_declaration",
            ) and "require(" in _get_node_text(actual, content_bytes):
                imports.append(child)

        if imports:
            import_texts = [_get_node_text(imp, content_bytes) for imp in imports]
            import_chunk = f"{base_prefix}\n" + "\n".join(import_texts)
            first_imp = imports[0]
            last_imp = imports[-1]
            meta: dict = {"unit_name": file.stem}
            documents.extend(
                self._make_documents(
                    import_chunk,
                    "import_group",
                    first_imp.start_point[0] + 1,
                    last_imp.end_point[0] + 1,
                    first_imp.start_byte,
                    last_imp.end_byte,
                    file_path_str,
                    file_datetime,
                    extra_metadata=meta,
                )
            )

        import_nodes: Set[int] = {id(n) for n in imports}

        # Track emitted class summaries
        emitted_class_summaries: set = set()

        # ── Collect raw chunks ──
        # (node_type, node, full_text, context_name)
        raw_chunks: List[Tuple[str, Node, str, str]] = []

        def _process_node(
            node: Node,
            current_class: Optional[str] = None,
            class_header: Optional[str] = None,
        ) -> None:
            """Process a single AST node, collecting chunks."""
            prefix = _build_context_prefix(file_name, current_class, class_header)

            # ── ES6 class ──
            if node.type in ("class_declaration", "abstract_class_declaration"):
                cls_name = _get_identifier(node, content_bytes)
                cls_header = _get_class_header_js(node, content_bytes)

                cls_prefix = _build_context_prefix(file_name, cls_name, cls_header)

                # Emit class summary
                summary = self._build_class_summary(node, content_bytes, cls_prefix)
                if summary:
                    raw_chunks.append(("class_summary", node, summary, cls_name or ""))
                    if cls_name:
                        emitted_class_summaries.add(cls_name)

                    # Emit overview for large classes
                    if len(summary) > self.MAX_SUMMARY_CHARS:
                        overview = self._build_class_overview(
                            node,
                            content_bytes,
                            cls_prefix,
                            cls_name or "",
                        )
                        if overview:
                            raw_chunks.append(
                                (
                                    "class_overview",
                                    node,
                                    overview,
                                    cls_name or "",
                                )
                            )

                # Recurse into class body
                for child in node.children:
                    if child.type == "class_body":
                        for body_child in child.children:
                            if body_child.type in ("{", "}", ";"):
                                continue
                            _process_node(
                                body_child,
                                current_class=cls_name,
                                class_header=cls_header,
                            )
                return

            # ── Method definition (inside a class) ──
            if node.type == "method_definition":
                chunk_text = _get_node_text(node, content_bytes)
                full_text = f"{prefix}\n{chunk_text}"
                raw_chunks.append(
                    ("method_definition", node, full_text, current_class or "")
                )
                return

            # ── Field definitions (inside a class) ──
            if node.type in (
                "public_field_definition",
                "field_definition",
                "property_definition",
            ):
                chunk_text = _get_node_text(node, content_bytes)
                if len(chunk_text) >= self.MIN_CHUNK_SIZE:
                    full_text = f"{prefix}\n{chunk_text}"
                    raw_chunks.append(
                        ("field_definition", node, full_text, current_class or "")
                    )
                return

            # ── Function declarations ──
            if node.type in ("function_declaration", "generator_function_declaration"):
                chunk_text = _get_node_text(node, content_bytes)
                full_text = f"{prefix}\n{chunk_text}"
                raw_chunks.append((node.type, node, full_text, current_class or ""))
                return

            # ── TypeScript-specific: interface, type alias, enum ──
            if node.type in self.TS_LEAF_TYPES:
                chunk_text = _get_node_text(node, content_bytes)
                full_text = f"{prefix}\n{chunk_text}"
                raw_chunks.append((node.type, node, full_text, current_class or ""))
                return

            # ── Comments (standalone) ──
            if node.type == "comment":
                chunk_text = _get_node_text(node, content_bytes)
                if len(chunk_text) >= self.MIN_COMMENT_CHARS:
                    # Skip comments inside classes with summaries
                    if current_class and current_class in emitted_class_summaries:
                        return
                    full_text = f"{prefix}\n{chunk_text}"
                    raw_chunks.append(("comment", node, full_text, current_class or ""))
                return

            # ── Variable/lexical declarations (outside classes) ──
            # These include: var App = { ... }, const foo = () => { ... }, etc.
            if node.type in ("variable_declaration", "lexical_declaration"):
                chunk_text = _get_node_text(node, content_bytes)
                # Only emit if non-trivial
                if len(chunk_text) >= self.MIN_CHUNK_SIZE:
                    # Check if this is a large object literal or arrow function
                    node_type_out = node.type
                    # Check for arrow functions as value
                    for child in node.children:
                        if child.type == "variable_declarator":
                            for sub in child.children:
                                if sub.type == "arrow_function":
                                    node_type_out = "arrow_function"
                    full_text = f"{prefix}\n{chunk_text}"
                    raw_chunks.append(
                        (node_type_out, node, full_text, current_class or "")
                    )
                return

            # ── Expression statements (prototype assignments, namespace assignments) ──
            if node.type == "expression_statement":
                # Check for prototype assignment
                proto_class = _is_prototype_assignment(node, content_bytes)
                if proto_class is not None:
                    chunk_text = _get_node_text(node, content_bytes)
                    if len(chunk_text) >= self.MIN_CHUNK_SIZE:
                        full_text = f"{prefix}\n{chunk_text}"
                        raw_chunks.append(
                            (
                                "expression_statement",
                                node,
                                full_text,
                                proto_class,
                            )
                        )
                    return

                # Other expression statements (assignments, calls)
                chunk_text = _get_node_text(node, content_bytes)
                if len(chunk_text) >= self.MIN_CHUNK_SIZE:
                    full_text = f"{prefix}\n{chunk_text}"
                    raw_chunks.append(("expression_statement", node, full_text, ""))
                return

            # ── Fall through: recurse into children ──
            for child in node.children:
                _process_node(child, current_class, class_header)

        # ── Process top-level children ──
        for child in root.children:
            # Skip already-collected imports
            if id(child) in import_nodes:
                continue

            # Unwrap export_statement for TS
            actual = _unwrap_export(child) if is_typescript else child

            # Check for IIFE and drill through
            if _is_iife(child):
                body = _get_iife_body(child)
                if body:
                    # Check if the IIFE body contains an AMD define()
                    drilled = False
                    for sub in body.children:
                        if _is_amd_define(sub, content_bytes):
                            amd_body = _get_amd_callback_body(sub, content_bytes)
                            if amd_body:
                                for amd_child in amd_body.children:
                                    _process_node(amd_child)
                                drilled = True
                                break
                    if not drilled:
                        for sub in body.children:
                            _process_node(sub)
                    continue
                # If we can't get the body, fall through to process as-is

            # Check for AMD define() at top level
            if _is_amd_define(child, content_bytes):
                amd_body = _get_amd_callback_body(child, content_bytes)
                if amd_body:
                    for sub in amd_body.children:
                        _process_node(sub)
                    continue

            # Normal node processing (use unwrapped for TS exports)
            if actual is not child and actual.type != "export_statement":
                _process_node(actual)
            else:
                _process_node(child)

        # ── Pass 2: Group trivial functions and prototype methods, emit all ──
        i = 0
        while i < len(raw_chunks):
            node_type, node, full_text, context_name = raw_chunks[i]

            # Group consecutive trivial function_declarations
            if node_type in (
                "function_declaration",
                "generator_function_declaration",
            ):
                line_count = _count_body_lines(node)
                if line_count <= self.TRIVIAL_FUNC_LINES:
                    trivial_run: List[Tuple[Node, str, str]] = [
                        (node, node_type, context_name)
                    ]
                    j = i + 1
                    while j < len(raw_chunks):
                        ntype, nnode, _, nctx = raw_chunks[j]
                        if (
                            ntype
                            in (
                                "function_declaration",
                                "generator_function_declaration",
                            )
                            and _count_body_lines(nnode) <= self.TRIVIAL_FUNC_LINES
                        ):
                            trivial_run.append((nnode, ntype, nctx))
                            j += 1
                        else:
                            break

                    if len(trivial_run) >= 3:
                        meta = {"unit_name": file.stem}
                        documents.extend(
                            self._group_functions(
                                trivial_run,
                                content_bytes,
                                base_prefix,
                                file_path_str,
                                file_datetime,
                                extra_metadata=meta,
                                group_type="function_group",
                            )
                        )
                        i = j
                        continue

            # Group consecutive prototype methods for same constructor
            if (
                node_type == "expression_statement"
                and context_name
                and _is_prototype_assignment(node, content_bytes) is not None
            ):
                proto_run: List[Tuple[Node, str, str]] = [
                    (node, node_type, context_name)
                ]
                j = i + 1
                while j < len(raw_chunks):
                    ntype, nnode, _, nctx = raw_chunks[j]
                    if (
                        ntype == "expression_statement"
                        and nctx == context_name
                        and _is_prototype_assignment(nnode, content_bytes) is not None
                    ):
                        proto_run.append((nnode, ntype, nctx))
                        j += 1
                    else:
                        break

                if len(proto_run) >= 3:
                    proto_prefix = _build_context_prefix(
                        file_name, context_name, f"{context_name}.prototype"
                    )
                    meta = {
                        "unit_name": file.stem,
                        "class_name": context_name,
                    }
                    documents.extend(
                        self._group_functions(
                            proto_run,
                            content_bytes,
                            proto_prefix,
                            file_path_str,
                            file_datetime,
                            extra_metadata=meta,
                            group_type="prototype_group",
                        )
                    )
                    i = j
                    continue

            # Group consecutive trivial method_definitions in a class
            if node_type == "method_definition":
                line_count = _count_body_lines(node)
                if line_count <= self.TRIVIAL_FUNC_LINES:
                    method_run: List[Tuple[Node, str, str]] = [
                        (node, node_type, context_name)
                    ]
                    j = i + 1
                    while j < len(raw_chunks):
                        ntype, nnode, _, nctx = raw_chunks[j]
                        if (
                            ntype == "method_definition"
                            and nctx == context_name
                            and _count_body_lines(nnode) <= self.TRIVIAL_FUNC_LINES
                        ):
                            method_run.append((nnode, ntype, nctx))
                            j += 1
                        else:
                            break

                    if len(method_run) >= 3:
                        cls_header_str = None
                        if context_name:
                            cls_header_str = context_name
                        method_prefix = _build_context_prefix(
                            file_name, context_name, cls_header_str
                        )
                        meta = {"unit_name": file.stem}
                        if context_name:
                            meta["class_name"] = context_name
                        documents.extend(
                            self._group_functions(
                                method_run,
                                content_bytes,
                                method_prefix,
                                file_path_str,
                                file_datetime,
                                extra_metadata=meta,
                                group_type="function_group",
                            )
                        )
                        i = j
                        continue

            # Single chunk emit
            emit_max = self.MAX_SUMMARY_CHARS if node_type == "class_summary" else None
            chunk_meta: dict = {"unit_name": file.stem}
            if context_name:
                chunk_meta["class_name"] = context_name
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
                    extra_metadata=chunk_meta,
                    max_chars=emit_max,
                )
            )
            i += 1

        # Fallback: if no documents were produced at all
        if not documents:
            fallback_meta: dict = {
                "file_path": file_path_str,
                "node_type": "full_file",
                "unit_name": file.stem,
                **file_datetime,
            }
            documents.append(
                Document(
                    text=content,
                    metadata=fallback_meta,
                )
            )

        return documents
