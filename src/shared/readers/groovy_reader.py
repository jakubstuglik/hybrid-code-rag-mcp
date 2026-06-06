"""
Groovy file reader (.groovy) using Tree-sitter AST.

Chunking strategy — class-context-aware with intelligent grouping:

1. **Context prefix on every chunk**: Each chunk starts with a comment block
   identifying the file name, package, and (if applicable) the owning class
   with its inheritance, so every chunk is self-describing for RAG search.

2. **Class summary chunk**: For each class/interface/enum, emit a dedicated
   chunk containing the declaration header plus all field and method signatures
   (no bodies).  This answers "What is OAuthEpLoginService?" and
   "What methods does IPAdminConnectionsLogic have?".

3. **Class overview chunk**: For large classes where the summary exceeds
   MAX_SUMMARY_CHARS, emit a compact natural-language overview (~500-2000 chars)
   with member counts and signature list.  Critical for dense embedding quality.

4. **Leaf/container AST walk**: Groovy's AST uses `command` nodes for all declarations.
   We classify them by inspecting child patterns:
   - Import commands (unit("import")) → leaf, grouped into import_group
   - Field commands (type + variable name units, no body block) → leaf
   - Method commands (return type unit + func + block body) → leaf
   - Constructor commands (name + arg_block + block body, no return type) → leaf
   - Class/interface/enum commands → container nodes (recurse into children)
   - Enum constant commands (end_command inside enum) → leaf

5. **Trivial method grouping**: Consecutive method/constructor nodes whose
   bodies are <= TRIVIAL_METHOD_LINES lines get grouped into a single
   "method_group" chunk.  Collapses getter/setter/delegate chains.

6. **Import grouping**: All import declarations are collected into a single
   "import_group" chunk rather than emitting each import as a separate chunk.

7. **Annotation-aware**: Annotations on classes, methods, and fields are
   included in the chunk text.  Spring annotations (@Service, @Repository,
   @Autowired, @Transactional) are preserved for semantic search.

8. **Inner class support**: Inner/nested classes are recursed into with
   proper class context nesting (e.g. "Class: OuterClass > InnerClass").

9. **Oversized splitting**: Chunks exceeding MAX_CHUNK_CHARS are split with
   TokenTextSplitter.  Small chunks (< MIN_CHUNK_SIZE) are discarded.

Node types emitted:
    class_summary, class_summary_split, class_overview,
    method_declaration, method_declaration_split,
    constructor_declaration, constructor_declaration_split,
    field_declaration, constant_declaration, enum_constant,
    import_group, block_comment, method_group, full_file
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

_parser = get_parser("groovy")


# ────────────────────────────────────────────────
# AST helper functions for Groovy
# ────────────────────────────────────────────────


def _get_node_text(node: Node, content_bytes: bytes) -> str:
    """Extract text content from an AST node."""
    return (
        content_bytes[node.start_byte : node.end_byte]
        .decode("utf-8", errors="replace")
        .strip()
    )


def _get_node_text_raw(node: Node, content_bytes: bytes) -> str:
    """Extract raw text content from an AST node (unstripped)."""
    return (
        content_bytes[node.start_byte : node.end_byte]
        .decode("utf-8", errors="replace")
    )


def _get_identifier(node: Node, content_bytes: bytes) -> Optional[str]:
    """Extract the identifier (name) from a declaration node.

    Works for class commands, method blocks, enum blocks, etc.
    Handles Groovy's nested structure: block > unit > func > identifier
    """
    # Try direct identifier child
    for child in node.children:
        if child.type == "identifier":
            return (
                content_bytes[child.start_byte : child.end_byte]
                .decode("utf-8", errors="replace")
                .strip()
            )
    # Try func > identifier pattern (for methods)
    for child in node.children:
        if child.type == "func":
            for sub in child.children:
                if sub.type == "identifier":
                    return (
                        content_bytes[sub.start_byte : sub.end_byte]
                        .decode("utf-8", errors="replace")
                        .strip()
                    )
    # Try unit > func > identifier pattern (for Groovy methods inside blocks)
    for child in node.children:
        if child.type == "unit":
            for subsub in child.children:
                if subsub.type == "func":
                    for func_child in subsub.children:
                        if func_child.type == "identifier":
                            return (
                                content_bytes[
                                    func_child.start_byte : func_child.end_byte
                                ]
                                .decode("utf-8", errors="replace")
                                .strip()
                            )
    # Try block > unit > identifier pattern (for class/enum names)
    for child in node.children:
        if child.type == "block":
            for sub in child.children:
                if sub.type == "unit":
                    for subsub in sub.children:
                        if subsub.type == "identifier":
                            return (
                                content_bytes[subsub.start_byte : subsub.end_byte]
                                .decode("utf-8", errors="replace")
                                .strip()
                            )
    return None


def _get_first_unit_text(node: Node, content_bytes: bytes) -> Optional[str]:
    """Get the text of the first 'unit' child node."""
    for child in node.children:
        if child.type == "unit":
            return (
                content_bytes[child.start_byte : child.end_byte]
                .decode("utf-8", errors="replace")
                .strip()
            )
    return None


def _get_command_kind(node: Node, content_bytes: bytes) -> Optional[str]:
    """Determine what kind of command this is.

    Returns one of: 'import', 'class', 'interface', 'enum', 'field', 'method', 'constructor'
    or None if it's not a declaration command (e.g. annotation-only, or non-command node).
    """
    if node.type not in ("command", "end_command"):
        return None

    if node.type == "end_command":
        return "enum_constant"

    # Check first child unit for top-level keywords
    first_unit = _get_first_unit_text(node, content_bytes)

    if first_unit == "import":
        return "import"
    elif first_unit == "package":
        return "package"
    elif first_unit == "class":
        return "class"
    elif first_unit == "interface":
        return "interface"
    elif first_unit == "enum":
        return "enum"

    # Not a top-level keyword — check if this is a nested command (field, method, constructor)
    # Check for annotation-only commands (e.g., @Autowired on its own line)
    has_annotation = False
    for child in node.children:
        if child.type == "decorate":
            has_annotation = True
            break

    if has_annotation and not any(c.type == "block" for c in node.children):
        # Annotation-only command (no body, no field declaration) — skip it
        return None

    # Check if this command has a block body (method/constructor) vs no block (field)
    has_block = False
    for child in node.children:
        if child.type == "block":
            has_block = True
            break

    if has_block:
        # Has a block body — could be method, constructor, or annotated field with initializer
        # Check if first unit is a return type (not 'def', not an annotation)
        units_text = []
        for child in node.children:
            if child.type == "unit":
                text = (
                    content_bytes[child.start_byte : child.end_byte]
                    .decode("utf-8", errors="replace")
                    .strip()
                )
                units_text.append(text)

        # If first unit is a known type or keyword (void, int, String, def), this is likely a method/constructor
        return_type_keywords = {
            "void",
            "int",
            "String",
            "boolean",
            "byte",
            "short",
            "long",
            "char",
            "def",
        }
        if units_text and units_text[0] in return_type_keywords:
            # Has a return type + block — this is a method
            # Verify it has a func > identifier pattern for the method name
            for child in node.children:
                if child.type == "block":
                    block_name = _get_identifier(child, content_bytes)
                    if block_name and block_name not in (
                        "class",
                        "interface",
                        "enum",
                    ):
                        return "method"

        # No return type keyword but has a block — this is a constructor
        # Verify it has a func > identifier pattern for the constructor name
        for child in node.children:
            if child.type == "block":
                block_name = _get_identifier(child, content_bytes)
                if block_name and block_name not in (
                    "{",
                    "}",
                    "class",
                    "interface",
                    "enum",
                ):
                    return "constructor"

    # If no block body, check for interface method declarations (no body but has return type + func name)
    has_func_identifier = False
    for child in node.children:
        if child.type == "unit":
            for subsub in child.children:
                if subsub.type == "func":
                    for func_child in subsub.children:
                        if func_child.type == "identifier":
                            has_func_identifier = True
                            break

    if not has_block and has_func_identifier:
        # No body block but has return type + method name — this is an interface method declaration
        return "method"

    # Check for enum constants (end_command children)
    has_end_command = False
    for child in node.children:
        if child.type == "end_command":
            has_end_command = True
            break

    if has_end_command:
        return "enum_constant"

    return "field"


def _get_class_header(node: Node, content_bytes: bytes) -> str:
    """Extract the class/interface/enum header line (no body).

    Returns e.g.:
        'class MyService'
        'interface IPersistenceAwareLogic<T>'
        'enum EOauthLoginStatus'
    """
    # Get the keyword from first unit child
    keyword = _get_first_unit_text(node, content_bytes)

    # Get the name from inside the block
    name = None
    for child in node.children:
        if child.type == "block":
            # Look for the class/enum/interface name (first unit inside block)
            for sub in child.children:
                if sub.type == "unit":
                    for subsub in sub.children:
                        if subsub.type == "identifier":
                            name = (
                                content_bytes[subsub.start_byte : subsub.end_byte]
                                .decode("utf-8", errors="replace")
                                .strip()
                            )
                            break
                    if name:
                        break
            break

    if keyword and name:
        return f"{keyword} {name}"
    elif keyword:
        return keyword
    else:
        # Fallback to raw text
        return _get_node_text(node, content_bytes).strip()


def _get_method_signature(node: Node, content_bytes: bytes) -> str:
    """Extract method/constructor signature without the body (Groovy-aware).

    The groovy tree-sitter puts the declarator (name + params) inside a 'block'
    child for methods. We take the raw text of the command and cut before the
    first '{' that starts the implementation body.
    """
    raw = _get_node_text_raw(node, content_bytes)
    # Cut at the opening { of the body (first occurrence is sufficient for sig)
    if "{" in raw:
        sig = raw.split("{", 1)[0]
    else:
        sig = raw
    sig = sig.strip().rstrip("{").strip()
    # Collapse multi-line / extra ws
    sig = " ".join(sig.split())
    return sig


def _count_body_lines(node: Node) -> int:
    """Count the number of source lines in a node."""
    return node.end_point[0] - node.start_point[0] + 1


def _get_annotations(node: Node, content_bytes: bytes) -> List[str]:
    """Extract annotation strings from decorate nodes."""
    annotations = []
    for child in node.children:
        if child.type == "decorate":
            text = (
                content_bytes[child.start_byte : child.end_byte]
                .decode("utf-8", errors="replace")
                .strip()
            )
            annotations.append(text)
    return annotations


def _build_context_prefix(
    file_name: str,
    package_name: Optional[str] = None,
    class_name: Optional[str] = None,
    class_header: Optional[str] = None,
) -> str:
    """Build a context prefix comment for chunk self-identification.

    Examples:
        // File: MyService.groovy
        // Package: com.example.app
        // Class: @Service public class MyService

        // File: IPAdminConnectionsLogic.groovy
        // Package: com.example.app
        // Class: public interface IPAdminConnectionsLogic extends IPersistenceAwareLogic<...>
    """
    parts = [f"// File: {file_name}"]
    if package_name:
        parts.append(f"// Package: {package_name}")
    if class_name and class_header:
        parts.append(f"// Class: {class_header}")
    elif class_name:
        parts.append(f"// Class: {class_name}")
    return "\n".join(parts)


# ────────────────────────────────────────────────
# Reader class
# ────────────────────────────────────────────────


class GroovyFileReader(BaseFileReader):
    """Semantic chunking for Groovy files using Tree-sitter AST.

    Produces self-describing chunks with context prefixes, class summary
    chunks, import group chunks, and grouped trivial methods.
    """

    # Container node types: top-level commands that contain other declarations
    CONTAINER_NODE_TYPES = {"class", "interface", "enum"}

    # All recognized command kinds (import, field, method, constructor)
    LEAF_COMMAND_KINDS = {"import", "field", "method", "constructor", "enum_constant"}

    MIN_CHUNK_SIZE = 20  # Discard chunks smaller than this (chars)
    MAX_CHUNK_CHARS = 24000  # ~6000 tokens — split oversized chunks
    MAX_SUMMARY_CHARS = 6000  # Max chars before splitting class_summary
    TRIVIAL_METHOD_LINES = 6  # Methods <= this are "trivial" for grouping
    MAX_GROUP_CHARS = 8000  # Max chars for a grouped trivial-method chunk
    MIN_COMMENT_CHARS = 40  # Min raw comment text to emit standalone

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

        # Oversized chunk: split with TokenTextSplitter
        parts = self._text_splitter.split_text(chunk_text)

        # For class_summary splits, re-prepend the context prefix so every
        # split part is self-identifying for BM25 class-name queries.
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
        """Build a class summary chunk: header + all member signatures (no bodies)."""
        # Find the body block node
        body_node = None
        for child in node.children:
            if child.type == "block":
                body_node = child
                break

        if body_node is None:
            return None

        header = _get_class_header(node, content_bytes)
        if not header:
            return None

        members: List[str] = []

        def _collect_member(child: Node) -> None:
            """Add a member entry from a block child to the summary."""
            if child.type not in ("command", "end_command"):
                return
            kind = _get_command_kind(child, content_bytes)
            if not kind:
                return

            if kind == "field":
                text = _get_node_text(child, content_bytes).strip()
                # Get just the first line
                first_line = text.split("\n")[0].strip()
                members.append(f"    {first_line}")

            elif kind in ("method", "constructor"):
                sig = _get_method_signature(child, content_bytes)
                members.append(f"    {sig}")

            elif kind == "enum_constant":
                text = _get_node_text(child, content_bytes).strip()
                first_line = text.split("\n")[0].strip()
                members.append(f"    {first_line}")

            elif kind in self.CONTAINER_NODE_TYPES:
                # Nested class/interface/enum
                inner_header = _get_class_header(child, content_bytes)
                if inner_header:
                    members.append(f"    {inner_header} {{ ... }}")

            elif kind == "import":
                pass  # Skip imports in summary

        for child in body_node.children:
            _collect_member(child)

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
        """Build a compact class overview chunk for large classes."""
        header = _get_class_header(node, content_bytes)
        if not header:
            return None

        # Determine kind (class, interface, enum)
        kind = "class"
        first_unit = _get_first_unit_text(node, content_bytes)
        if first_unit == "interface":
            kind = "interface"
        elif first_unit == "enum":
            kind = "enum"

        # Count and collect members
        body_node = None
        for child in node.children:
            if child.type == "block":
                body_node = child
                break
        if body_node is None:
            return None

        fields: List[str] = []
        methods: List[str] = []
        enum_constants: List[str] = []
        inner_types: List[str] = []

        MAX_MEMBERS = 20

        def _collect_overview_member(child: Node) -> None:
            """Collect member names for the overview."""
            if child.type not in ("command", "end_command"):
                return
            kind = _get_command_kind(child, content_bytes)
            if not kind:
                return

            if kind == "field":
                # Get field name (last unit before semicolon or end)
                for sub in child.children:
                    if sub.type == "unit":
                        text = content_bytes[sub.start_byte : sub.end_byte].decode("utf-8", errors="replace").strip()
                        if text not in ("private", "public", "protected", "static", "final", "def"):
                            fields.append(text)

            elif kind in ("method", "constructor"):
                # Get method name from block > unit > func > identifier
                for sub in child.children:
                    if sub.type == "block":
                        name = _get_identifier(sub, content_bytes)
                        if name and name not in ("class", "interface", "enum"):
                            methods.append(name)

            elif kind == "enum_constant":
                text = _get_node_text(child, content_bytes).strip()
                first_line = text.split("\n")[0].strip()
                enum_constants.append(first_line)

            elif kind in self.CONTAINER_NODE_TYPES:
                name = _get_identifier(child, content_bytes)
                if name:
                    inner_types.append(name)

        for child in body_node.children:
            _collect_overview_member(child)

        # Build natural-language summary
        member_parts = []
        if enum_constants:
            member_parts.append(f"{len(enum_constants)} enum constants")
        if fields:
            member_parts.append(f"{len(fields)} fields")
        if methods:
            member_parts.append(f"{len(methods)} methods")
        if inner_types:
            member_parts.append(f"{len(inner_types)} inner types")
        member_desc = ", ".join(member_parts) if member_parts else "no members"

        summary_sentence = (
            f"// {class_name} is a Groovy {' '.join([kind])} "
            f"with {member_desc}."
        )

        # Build member lists (truncated)
        sections: List[str] = []
        if enum_constants:
            shown = enum_constants[:MAX_MEMBERS]
            line = f"  constants: {', '.join(shown)}"
            if len(enum_constants) > MAX_MEMBERS:
                line += f" ... ({len(enum_constants) - MAX_MEMBERS} more)"
            sections.append(line)
        if fields:
            shown = fields[:MAX_MEMBERS]
            line = f"  fields: {', '.join(shown)}"
            if len(fields) > MAX_MEMBERS:
                line += f" ... ({len(fields) - MAX_MEMBERS} more)"
            sections.append(line)
        if methods:
            shown = methods[:MAX_MEMBERS]
            line = f"  methods: {', '.join(shown)}"
            if len(methods) > MAX_MEMBERS:
                line += f" ... ({len(methods) - MAX_MEMBERS} more)"
            sections.append(line)
        if inner_types:
            shown = inner_types[:MAX_MEMBERS]
            line = f"  inner types: {', '.join(shown)}"
            sections.append(line)

        section_text = "\n".join(sections) if sections else ""
        overview = (
            f"{context_prefix}\n{summary_sentence}\n{header} {{\n{section_text}\n}}"
        )
        return overview

    def _group_trivial_methods(
        self,
        methods: List[Tuple[Node, str]],
        content_bytes: bytes,
        context_prefix: str,
        file_path_str: str,
        file_datetime: dict,
        extra_metadata: Optional[dict] = None,
    ) -> List[Document]:
        """Group consecutive trivial method/constructor nodes into combined chunks."""
        if not methods:
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
                f"// Method group: {count} methods\n" + "\n\n".join(texts)
            )
            first = current_group[0]
            last = current_group[-1]
            merged_meta = {"group_count": count}
            if extra_metadata:
                merged_meta.update(extra_metadata)
            docs.extend(
                self._make_documents(
                    group_text,
                    "method_group",
                    first.start_point[0] + 1,
                    last.end_point[0] + 1,
                    first.start_byte,
                    last.end_byte,
                    file_path_str,
                    file_datetime,
                    extra_metadata=merged_meta or None,
                )
            )

        for node, _ in methods:
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

        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            log_warn(f"Tree-sitter Groovy parse failed for {file}: {e}")
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

        # ── Collect imports into a single group ──
        imports: List[Node] = []
        for child in root.children:
            kind = _get_command_kind(child, content_bytes)
            if kind == "import":
                imports.append(child)

        if imports:
            import_texts = [_get_node_text(imp, content_bytes).strip() for imp in imports]
            import_chunk = f"// File: {file_name}\n" + "\n".join(import_texts)
            first_imp = imports[0]
            last_imp = imports[-1]
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
                )
            )

        # ── Build class index: name -> header string ──
        class_index: Dict[str, str] = {}

        def _index_classes(node: Node) -> None:
            kind = _get_command_kind(node, content_bytes)
            if kind in self.CONTAINER_NODE_TYPES:
                name = _get_identifier(node, content_bytes)
                if name:
                    class_index[name] = _get_class_header(node, content_bytes)
            # Recurse into blocks (class bodies)
            for child in node.children:
                if child.type == "block":
                    for sub in child.children:
                        _index_classes(sub)

        _index_classes(root)

        # Track which classes have had summaries emitted
        emitted_class_summaries: set = set()

        # ── Collect raw chunks from AST ──
        raw_chunks: List[Tuple[str, Node, str, str]] = []

        def traverse(node: Node, current_class: Optional[str] = None, class_nesting: Optional[List[str]] = None) -> None:
            """Walk the AST and collect chunks."""
            if class_nesting is None:
                class_nesting = []

            # Only process actual declaration commands, end_commands (enum consts), block comments, source root.
            # This prevents emitting structural tokens (unit name, "{", "}", inner statements) as fields.
            if node.type not in ("command", "end_command", "block_comment", "source_file"):
                return

            kind = _get_command_kind(node, content_bytes)

            # ── Container nodes (class/interface/enum) ──
            if kind in self.CONTAINER_NODE_TYPES:
                class_name = _get_identifier(node, content_bytes)
                class_header = _get_class_header(node, content_bytes)

                new_nesting = (class_nesting + [class_name] if class_name else class_nesting)
                display_class = " > ".join(new_nesting) if len(new_nesting) > 1 else class_name

                prefix = _build_context_prefix(file_name, None, display_class, class_header)

                # Emit class summary
                summary = self._build_class_summary(node, content_bytes, prefix)
                if summary:
                    raw_chunks.append(("class_summary", node, summary, class_name or ""))
                    if class_name:
                        emitted_class_summaries.add(class_name)

                    # Emit class_overview for large classes
                    if len(summary) > self.MAX_SUMMARY_CHARS:
                        overview = self._build_class_overview(
                            node, content_bytes, prefix, display_class or class_name or ""
                        )
                        if overview:
                            raw_chunks.append(("class_overview", node, overview, class_name or ""))

                # Recurse into body children (inside block)
                for child in node.children:
                    if child.type == "block":
                        for body_child in child.children:
                            traverse(
                                body_child,
                                current_class=class_name,
                                class_nesting=new_nesting,
                            )
                return

            # ── Leaf commands (import, field, method, constructor, enum_constant) ──
            if kind and kind in self.LEAF_COMMAND_KINDS:
                chunk_text = _get_node_text(node, content_bytes).strip()

                # Skip tiny comments
                if node.type == "block_comment":
                    if len(chunk_text) < self.MIN_COMMENT_CHARS:
                        return
                    # Skip comments inside classes that have summaries
                    if current_class and current_class in emitted_class_summaries:
                        return

                # Only emit enum_constant chunks when we are inside an enum (prevents
                # grammar artifacts from method bodies etc. being emitted as constants).
                if kind == "enum_constant" and not current_class:
                    return

                class_header = class_index.get(current_class or "", None)
                display_class = " > ".join(class_nesting) if class_nesting and len(class_nesting) > 1 else current_class
                prefix = _build_context_prefix(file_name, None, display_class, class_header)
                full_text = f"{prefix}\n{chunk_text}"

                # Map kind to node_type
                if kind == "import":
                    return  # Imports handled separately above
                elif kind == "field":
                    node_type = "field_declaration"
                elif kind in ("method", "constructor"):
                    node_type = "method_declaration" if kind == "method" else "constructor_declaration"
                elif kind == "enum_constant":
                    node_type = "enum_constant"
                else:
                    node_type = kind

                raw_chunks.append((node_type, node, full_text, current_class or ""))
                return

            # ── Block comments (at any level) ──
            if node.type == "block_comment":
                chunk_text = _get_node_text(node, content_bytes).strip()
                if len(chunk_text) >= self.MIN_COMMENT_CHARS:
                    class_header = class_index.get(current_class or "", None)
                    display_class = " > ".join(class_nesting) if class_nesting and len(class_nesting) > 1 else current_class
                    prefix = _build_context_prefix(file_name, None, display_class, class_header)
                    full_text = f"{prefix}\n{chunk_text}"
                    raw_chunks.append(("block_comment", node, full_text, current_class or ""))
                return

            # ── Non-matched node: recurse into children ──
            for child in node.children:
                traverse(child, current_class=current_class, class_nesting=class_nesting)

        # Traverse top-level children (imports and packages handled separately / skipped)
        for child in root.children:
            kind = _get_command_kind(child, content_bytes)
            if kind in ("import", "package"):
                continue
            traverse(child)

        # ── Pass 2: Group trivial methods and emit all chunks ──
        i = 0
        while i < len(raw_chunks):
            node_type, node, full_text, class_name = raw_chunks[i]

            if node_type in ("method_declaration", "constructor_declaration"):
                line_count = _count_body_lines(node)
                if line_count <= self.TRIVIAL_METHOD_LINES:
                    # Collect consecutive trivial methods for same class
                    trivial_run: List[Tuple[Node, str]] = [(node, class_name)]
                    j = i + 1
                    while j < len(raw_chunks):
                        ntype, nnode, _, ncls = raw_chunks[j]
                        if (
                            ntype in ("method_declaration", "constructor_declaration")
                            and ncls == class_name
                            and _count_body_lines(nnode) <= self.TRIVIAL_METHOD_LINES
                        ):
                            trivial_run.append((nnode, ncls))
                            j += 1
                        else:
                            break

                    if len(trivial_run) >= 3:
                        # Group them
                        prefix = _build_context_prefix(file_name, None, class_name if class_name else None, None)
                        group_meta: dict = {}
                        if class_name:
                            group_meta["class_name"] = class_name
                        group_meta["unit_name"] = file.stem
                        documents.extend(
                            self._group_trivial_methods(
                                trivial_run, content_bytes, prefix, file_path_str, file_datetime,
                                extra_metadata=group_meta or None,
                            )
                        )
                        i = j
                        continue

            # Single chunk emit
            chunk_meta: dict = {}
            if class_name:
                chunk_meta["class_name"] = class_name
            chunk_meta["unit_name"] = file.stem
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
                    extra_metadata=chunk_meta or None,
                )
            )
            i += 1

        # Fallback: if no documents were produced at all
        if not documents:
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        **file_datetime,
                    },
                )
            )

        return documents
