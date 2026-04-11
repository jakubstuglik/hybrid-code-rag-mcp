"""
Java file reader (.java) using Tree-sitter AST.

Chunking strategy — class-context-aware with intelligent grouping:

1. **Context prefix on every chunk**: Each chunk starts with a comment block
   identifying the file name, package, and (if applicable) the owning class
   with its inheritance, so every chunk is self-describing for RAG search.

2. **Class summary chunk**: For each class/interface/enum/record, emit a
   dedicated chunk containing the declaration header plus all field and method
   signatures (no bodies).  This answers "What is OAuthEpLoginService?" and
   "What methods does IPAdminConnectionsLogic have?".

3. **Class overview chunk**: For large classes where the summary exceeds
   MAX_SUMMARY_CHARS, emit a compact natural-language overview (~500-2000 chars)
   with member counts and signature list.  Critical for dense embedding quality.

4. **Leaf/container AST walk**: ``method_declaration``,
   ``constructor_declaration``, ``field_declaration``, ``constant_declaration``,
   ``enum_constant``, ``import_declaration``, and ``block_comment`` are leaf
   nodes (emitted as-is).  ``class_declaration``, ``interface_declaration``,
   ``enum_declaration``, and ``record_declaration`` are container nodes (recurse
   into children if they have matched descendants).

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

_parser = get_parser("java")


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

    Works for class_declaration, interface_declaration, enum_declaration,
    record_declaration, method_declaration, constructor_declaration.
    """
    for child in node.children:
        if child.type == "identifier":
            return (
                content_bytes[child.start_byte : child.end_byte]
                .decode("utf-8", errors="replace")
                .strip()
            )
    return None


def _get_package_name(root: Node, content_bytes: bytes) -> Optional[str]:
    """Extract the package name from the root AST node."""
    for child in root.children:
        if child.type == "package_declaration":
            # package_declaration > scoped_identifier
            for sub in child.children:
                if sub.type in ("scoped_identifier", "identifier"):
                    return (
                        content_bytes[sub.start_byte : sub.end_byte]
                        .decode("utf-8", errors="replace")
                        .strip()
                    )
    return None


def _get_class_header(node: Node, content_bytes: bytes) -> str:
    """Extract the class/interface/enum/record header line (no body).

    Returns e.g.:
        '@Service public class OAuthEpLoginService'
        'public interface IPAdminConnectionsLogic extends IPersistenceAwareLogic<...>'
        'public enum EOauthLoginStatus'
        'public record TokenData(String hash, long timestamp)'
    """
    # Find the class_body/interface_body/enum_body — everything before it is the header
    body_types = {"class_body", "interface_body", "enum_body"}
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
    # Collapse multi-line headers to single line
    header = " ".join(header.split())
    return header


def _get_superclass(node: Node, content_bytes: bytes) -> Optional[str]:
    """Extract 'extends Foo' from a class_declaration."""
    for child in node.children:
        if child.type == "superclass":
            for sub in child.children:
                if sub.type in ("type_identifier", "generic_type"):
                    return _get_node_text(sub, content_bytes)
    return None


def _get_interfaces(node: Node, content_bytes: bytes) -> List[str]:
    """Extract 'implements Foo, Bar' or 'extends Foo, Bar' (for interfaces)."""
    result = []
    for child in node.children:
        if child.type in ("super_interfaces", "extends_interfaces"):
            for sub in child.children:
                if sub.type == "type_list":
                    for item in sub.children:
                        if item.type in ("type_identifier", "generic_type"):
                            result.append(_get_node_text(item, content_bytes))
    return result


def _get_method_signature(node: Node, content_bytes: bytes) -> str:
    """Extract method/constructor signature without the body.

    Returns e.g.:
        'public void writeBunch(List<PAddBunchPrimaryDataSO> bunch, long carrierId)'
        '@Override public T findById(Long id)'
    """
    # Find the block (body) — everything before it is the signature
    sig_end = node.end_byte
    for child in node.children:
        if child.type in ("block", "constructor_body"):
            sig_end = child.start_byte
            break

    sig = (
        content_bytes[node.start_byte : sig_end]
        .decode("utf-8", errors="replace")
        .strip()
        .rstrip("{")
        .strip()
    )
    # Collapse multi-line signatures
    sig = " ".join(sig.split())
    return sig


def _count_body_lines(node: Node) -> int:
    """Count the number of source lines in a node."""
    return node.end_point[0] - node.start_point[0] + 1


def _get_annotations(node: Node, content_bytes: bytes) -> List[str]:
    """Extract annotation strings from a node's modifiers child."""
    annotations = []
    for child in node.children:
        if child.type == "modifiers":
            for sub in child.children:
                if sub.type in ("marker_annotation", "annotation"):
                    annotations.append(_get_node_text(sub, content_bytes))
    return annotations


def _build_context_prefix(
    file_name: str,
    package_name: Optional[str] = None,
    class_name: Optional[str] = None,
    class_header: Optional[str] = None,
) -> str:
    """Build a context prefix comment for chunk self-identification.

    Examples:
        // File: OAuthEpLoginService.java
        // Package: com.example.app.businessLogic.auth
        // Class: @Service public class OAuthEpLoginService

        // File: IPAdminConnectionsLogic.java
        // Package: com.example.app.businessLogic.adminConnections
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


class JavaFileReader(BaseFileReader):
    """Semantic chunking for Java files using Tree-sitter AST.

    Produces self-describing chunks with context prefixes, class summary
    chunks, import group chunks, and grouped trivial methods.
    """

    # Leaf node types: always emit as-is, never recurse into children.
    LEAF_NODE_TYPES = {
        "method_declaration",
        "constructor_declaration",
        "field_declaration",
        "constant_declaration",
        "block_comment",
        "line_comment",
    }

    # Container node types: recurse if matched descendants exist,
    # otherwise emit the whole container as one chunk.
    CONTAINER_NODE_TYPES = {
        "class_declaration",
        "interface_declaration",
        "enum_declaration",
        "record_declaration",
    }

    # Types that can appear inside enum_body as enum constants
    ENUM_CONSTANT_TYPES = {"enum_constant"}

    # All recognised node types (leaf + container + enum constants)
    NODE_TYPES = LEAF_NODE_TYPES | CONTAINER_NODE_TYPES | ENUM_CONSTANT_TYPES

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

    def _has_matched_descendants(self, node: Node) -> bool:
        """Return True if any descendant of *node* matches NODE_TYPES."""
        for child in node.children:
            if child.type in self.NODE_TYPES:
                return True
            if self._has_matched_descendants(child):
                return True
        return False

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
        """Create Document(s) from a chunk, splitting if oversized.

        Args:
            max_chars: Override MAX_CHUNK_CHARS for this call.  Used for
                class_summary chunks which need a lower threshold to avoid
                zero-vector embeddings on large classes.
        """
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
        """Build a class summary chunk: header + all member signatures (no bodies).

        For a class like OAuthEpLoginService, this produces:
            // File: OAuthEpLoginService.java
            // Package: com.example.app.businessLogic.auth
            // Class: @Service public class OAuthEpLoginService
            @Service
            public class OAuthEpLoginService {
                private final IPUsersLogic usersLogic;
                private final ISellClientsLogic sellClientsLogic;
                @Autowired
                public OAuthEpLoginService(IPUsersLogic usersLogic, ...)
                public EOauthLoginStatus login(CustomAuthentication customAuthentication, ...)
                private void cancelOAuthLogin(HttpServletRequest request, ...)
                private void sendMailAddressConfirmationMail(HttpServletRequest req, ...)
                private void logUserIn(HttpSession session, PHSystemUser user)
            }
        """
        # Find the body node
        body_node = None
        body_types = {"class_body", "interface_body", "enum_body"}
        for child in node.children:
            if child.type in body_types:
                body_node = child
                break

        if body_node is None:
            return None

        header = _get_class_header(node, content_bytes)
        if not header:
            return None

        members: List[str] = []

        def _collect_member(child: Node) -> None:
            """Add a member entry from a body child to the summary."""
            if child.type in ("{", "}", ";", ","):
                return

            if child.type == "field_declaration":
                text = _get_node_text(child, content_bytes)
                first_line = text.split("\n")[0].strip()
                members.append(f"    {first_line}")

            elif child.type == "constant_declaration":
                text = _get_node_text(child, content_bytes)
                first_line = text.split("\n")[0].strip()
                members.append(f"    {first_line}")

            elif child.type in ("method_declaration", "constructor_declaration"):
                sig = _get_method_signature(child, content_bytes)
                members.append(f"    {sig}")

            elif child.type == "enum_constant":
                text = _get_node_text(child, content_bytes)
                first_line = text.split("\n")[0].strip()
                members.append(f"    {first_line}")

            elif child.type == "block_comment":
                pass  # Skip javadoc in summary — too verbose

            elif child.type in self.CONTAINER_NODE_TYPES:
                inner_header = _get_class_header(child, content_bytes)
                if inner_header:
                    members.append(f"    {inner_header} {{ ... }}")

            elif child.type == "record_declaration":
                inner_header = _get_class_header(child, content_bytes)
                if inner_header:
                    members.append(f"    {inner_header} {{ ... }}")

            elif child.type == "enum_body_declarations":
                # In Java, enum methods/fields come after the constants
                # and are wrapped in an enum_body_declarations node.
                for sub in child.children:
                    _collect_member(sub)

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
        """Build a compact class overview chunk for large classes.

        Unlike class_summary (full declaration signatures), this produces a
        concise overview (~500-2000 chars) containing:
        - A natural-language summary sentence
        - The class/interface header
        - Member names grouped by category (fields, methods, inner types)

        Only produced when the full class_summary exceeds MAX_SUMMARY_CHARS.
        """
        header = _get_class_header(node, content_bytes)
        if not header:
            return None

        # Determine kind (class, interface, enum, record)
        kind = "class"
        if node.type == "interface_declaration":
            kind = "interface"
        elif node.type == "enum_declaration":
            kind = "enum"
        elif node.type == "record_declaration":
            kind = "record"

        # Determine abstract
        is_abstract = "abstract " in header

        # Extract extends/implements
        superclass = _get_superclass(node, content_bytes)
        interfaces = _get_interfaces(node, content_bytes)

        # Count and collect members
        body_node = None
        body_types = {"class_body", "interface_body", "enum_body"}
        for child in node.children:
            if child.type in body_types:
                body_node = child
                break
        if body_node is None:
            return None

        fields: List[str] = []
        methods: List[str] = []
        constructors: List[str] = []
        inner_types: List[str] = []
        enum_constants: List[str] = []

        MAX_MEMBERS = 20

        def _collect_overview_member(child: Node) -> None:
            """Collect member names for the overview."""
            if child.type in ("{", "}", ";", ","):
                return
            if child.type == "field_declaration":
                name = _get_identifier(child, content_bytes)
                if name:
                    fields.append(name)
                else:
                    for sub in child.children:
                        if sub.type == "variable_declarator":
                            vname = _get_identifier(sub, content_bytes)
                            if vname:
                                fields.append(vname)
            elif child.type == "constant_declaration":
                for sub in child.children:
                    if sub.type == "variable_declarator":
                        vname = _get_identifier(sub, content_bytes)
                        if vname:
                            fields.append(vname)
            elif child.type == "method_declaration":
                name = _get_identifier(child, content_bytes)
                if name:
                    methods.append(name)
            elif child.type == "constructor_declaration":
                name = _get_identifier(child, content_bytes)
                if name:
                    constructors.append(name)
            elif child.type == "enum_constant":
                name = _get_identifier(child, content_bytes)
                if name:
                    enum_constants.append(name)
            elif child.type in self.CONTAINER_NODE_TYPES:
                name = _get_identifier(child, content_bytes)
                if name:
                    inner_types.append(name)
            elif child.type == "enum_body_declarations":
                for sub in child.children:
                    _collect_overview_member(sub)

        for child in body_node.children:
            _collect_overview_member(child)

        # Build natural-language summary
        parts = []
        if is_abstract:
            parts.append(f"abstract {kind}")
        else:
            parts.append(kind)

        inherits_parts = []
        if superclass:
            inherits_parts.append(f"extends {superclass}")
        if interfaces:
            kw = "extends" if kind == "interface" else "implements"
            inherits_parts.append(f"{kw} {', '.join(interfaces)}")
        inherits_str = f" {' '.join(inherits_parts)}" if inherits_parts else ""

        member_parts = []
        if enum_constants:
            member_parts.append(f"{len(enum_constants)} enum constants")
        if fields:
            member_parts.append(f"{len(fields)} fields")
        if constructors:
            member_parts.append(f"{len(constructors)} constructors")
        if methods:
            member_parts.append(f"{len(methods)} methods")
        if inner_types:
            member_parts.append(f"{len(inner_types)} inner types")
        member_desc = ", ".join(member_parts) if member_parts else "no members"

        summary_sentence = (
            f"// {class_name} is a Java {' '.join(parts)}{inherits_str} "
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
        if constructors:
            shown = constructors[:MAX_MEMBERS]
            line = f"  constructors: {', '.join(shown)}"
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
        """Group consecutive trivial method/constructor nodes into combined chunks.

        Args:
            methods: List of (node, class_name_or_empty) tuples.
            content_bytes: Source file bytes.
            context_prefix: The context prefix for the owning class.
            file_path_str: File path string.
            file_datetime: File datetime dict.

        Returns:
            List of Documents (one per group).
        """
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
                    extra_metadata=merged_meta,
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
            log_warn(f"Tree-sitter Java parse failed for {file}: {e}")
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
        package_name = _get_package_name(root, content_bytes)

        # Base prefix for chunks not inside a class
        base_prefix = _build_context_prefix(file_name, package_name)

        # ── Collect imports into a single group ──
        imports: List[Node] = []
        for child in root.children:
            if child.type == "import_declaration":
                imports.append(child)

        if imports:
            import_texts = [_get_node_text(imp, content_bytes) for imp in imports]
            import_chunk = f"{base_prefix}\n" + "\n".join(import_texts)
            first_imp = imports[0]
            last_imp = imports[-1]
            meta: dict = {"node_type": "import_group"}
            if package_name:
                meta["package_name"] = package_name
            meta["unit_name"] = file.stem
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

        # ── Build class index: name -> header string ──
        class_index: Dict[str, str] = {}

        def _index_classes(node: Node) -> None:
            if node.type in self.CONTAINER_NODE_TYPES:
                name = _get_identifier(node, content_bytes)
                if name:
                    class_index[name] = _get_class_header(node, content_bytes)
            for child in node.children:
                _index_classes(child)

        _index_classes(root)

        # Track which classes have had summaries emitted
        emitted_class_summaries: set = set()

        # ── Collect raw chunks from AST ──
        # Each entry: (node_type, node, full_text, class_name_or_empty)
        raw_chunks: List[Tuple[str, Node, str, str]] = []

        def traverse(
            node: Node,
            current_class: Optional[str] = None,
            class_nesting: Optional[List[str]] = None,
        ) -> None:
            """Walk the AST and collect chunks."""
            if class_nesting is None:
                class_nesting = []

            # ── Container nodes (class/interface/enum/record) ──
            if node.type in self.CONTAINER_NODE_TYPES:
                class_name = _get_identifier(node, content_bytes)
                class_header = _get_class_header(node, content_bytes)

                new_nesting = (
                    class_nesting + [class_name] if class_name else class_nesting
                )
                display_class = (
                    " > ".join(new_nesting) if len(new_nesting) > 1 else class_name
                )

                prefix = _build_context_prefix(
                    file_name, package_name, display_class, class_header
                )

                # Emit class summary
                summary = self._build_class_summary(node, content_bytes, prefix)
                if summary:
                    raw_chunks.append(
                        ("class_summary", node, summary, class_name or "")
                    )
                    if class_name:
                        emitted_class_summaries.add(class_name)

                    # Emit class_overview for large classes
                    if len(summary) > self.MAX_SUMMARY_CHARS:
                        overview = self._build_class_overview(
                            node,
                            content_bytes,
                            prefix,
                            display_class or class_name or "",
                        )
                        if overview:
                            raw_chunks.append(
                                ("class_overview", node, overview, class_name or "")
                            )

                # Recurse into body children
                body_types = {"class_body", "interface_body", "enum_body"}
                for child in node.children:
                    if child.type in body_types:
                        for body_child in child.children:
                            traverse(
                                body_child,
                                current_class=class_name,
                                class_nesting=new_nesting,
                            )
                return

            # ── Leaf nodes ──
            if node.type in self.LEAF_NODE_TYPES:
                chunk_text = _get_node_text(node, content_bytes)

                # Skip tiny comments
                if node.type in ("block_comment", "line_comment"):
                    if len(chunk_text) < self.MIN_COMMENT_CHARS:
                        return
                    # Skip comments inside classes that have summaries
                    if current_class and current_class in emitted_class_summaries:
                        return

                class_header = class_index.get(current_class or "", None)
                display_class = (
                    " > ".join(class_nesting)
                    if class_nesting and len(class_nesting) > 1
                    else current_class
                )
                prefix = _build_context_prefix(
                    file_name, package_name, display_class, class_header
                )
                full_text = f"{prefix}\n{chunk_text}"
                raw_chunks.append((node.type, node, full_text, current_class or ""))
                return

            # ── Enum constants ──
            if node.type == "enum_constant":
                chunk_text = _get_node_text(node, content_bytes)
                # Enum constants are usually small; skip standalone emission
                # if there's a class_summary (they're already included there).
                if current_class and current_class in emitted_class_summaries:
                    return
                class_header = class_index.get(current_class or "", None)
                prefix = _build_context_prefix(
                    file_name, package_name, current_class, class_header
                )
                full_text = f"{prefix}\n{chunk_text}"
                raw_chunks.append(
                    ("enum_constant", node, full_text, current_class or "")
                )
                return

            # ── Non-matched node: recurse into children ──
            for child in node.children:
                traverse(
                    child, current_class=current_class, class_nesting=class_nesting
                )

        # Traverse top-level children (skip imports, already handled)
        for child in root.children:
            if child.type == "import_declaration":
                continue
            if child.type == "package_declaration":
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
                        class_header = class_index.get(class_name, None)
                        prefix = _build_context_prefix(
                            file_name,
                            package_name,
                            class_name if class_name else None,
                            class_header,
                        )
                        group_meta: dict = {}
                        if package_name:
                            group_meta["package_name"] = package_name
                        group_meta["unit_name"] = file.stem
                        if class_name:
                            group_meta["class_name"] = class_name
                        documents.extend(
                            self._group_trivial_methods(
                                trivial_run,
                                content_bytes,
                                prefix,
                                file_path_str,
                                file_datetime,
                                extra_metadata=group_meta or None,
                            )
                        )
                        i = j
                        continue
                    # Not enough for a group — fall through to single-chunk emit

            # Single chunk emit
            emit_max = self.MAX_SUMMARY_CHARS if node_type == "class_summary" else None
            chunk_meta: dict = {}
            if package_name:
                chunk_meta["package_name"] = package_name
            chunk_meta["unit_name"] = file.stem
            if class_name:
                chunk_meta["class_name"] = class_name
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
                    max_chars=emit_max,
                )
            )
            i += 1

        # Fallback: if no documents were produced at all
        if not documents:
            fallback_meta: dict = {
                "file_path": file_path_str,
                "node_type": "full_file",
                **file_datetime,
            }
            if package_name:
                fallback_meta["package_name"] = package_name
            fallback_meta["unit_name"] = file.stem
            documents.append(
                Document(
                    text=content,
                    metadata=fallback_meta,
                )
            )

        return documents
