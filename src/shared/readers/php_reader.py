"""
PHP file reader (.php) using Tree-sitter AST (``php`` grammar).

Modelled on the Java reader, so PHP chunks carry the same context prefix and
node types as Java/Kotlin chunks:

    // File: UserController.php
    // Namespace: App\\Http\\Controllers
    // Class: final class UserController extends Controller implements HasMiddleware

Chunking strategy:

1. **Namespaces**: both ``namespace A\\B;`` (applies to the rest of the file)
   and ``namespace A\\B { ... }`` set the ``// Namespace:`` line.
2. **Types**: classes, interfaces, traits and enums get a ``class_summary``
   chunk (header, used traits, constants, properties, enum cases and method
   signatures, no bodies) and, when large, a ``class_overview`` chunk.
3. **Members**: methods -> ``method_declaration`` (``__construct`` ->
   ``constructor_declaration``), properties -> ``field_declaration``, class
   constants -> ``constant_declaration``.  ``/** ... */`` doc blocks directly
   above a member are kept with it.  Top-level ``function`` definitions are
   ``method_declaration`` chunks without a ``// Class:`` line.
4. ``use`` imports -> one ``import_group`` chunk.
5. Other top-level statements (route files, config arrays, bootstrap code)
   -> one ``script_body`` chunk.
6. **Templates**: files that are mostly inline HTML (views, ``.phtml``-style
   PHP) and declare no class or function are chunked like plain text with
   the text reader's sentence splitter.
7. Trivial-method grouping (``method_group``), oversized splitting and the
   ``full_file`` fallback work as in the Java reader.
"""

from pathlib import Path
from typing import List, Optional

from llama_index.core import Document
from llama_index.core.schema import TextNode
from tree_sitter import Node
from tree_sitter_language_pack import get_parser

from shared.log import log_warn
from shared.readers._base import (
    get_file_datetime,
    node_from_doc,
    read_file_with_encoding_and_bytes,
)
from shared.readers._structured import (
    RawChunk,
    StructuredReaderBase,
    collapse,
    free_comment_block,
    nested_header,
    node_text,
    text_until,
)
from shared.readers.text_reader import TextFileReader
from shared.rerank_profile import java_style_profile, simple_stem_pattern

_parser = get_parser("php")

TYPE_NODES = {
    "class_declaration": "class",
    "interface_declaration": "interface",
    "trait_declaration": "trait",
    "enum_declaration": "enum",
}
BODY_NODES = {"declaration_list", "enum_declaration_list"}
TEMPLATE_TEXT_RATIO = 0.3  # inline HTML share above which a file is a template


def _name(node: Node, content_bytes: bytes) -> Optional[str]:
    n = node.child_by_field_name("name")
    if n is not None:
        return node_text(n, content_bytes)
    for c in node.children:
        if c.type == "name":
            return node_text(c, content_bytes)
    return None


def _body(node: Node) -> Optional[Node]:
    for c in node.children:
        if c.type in BODY_NODES:
            return c
    return None


def type_header(node: Node, content_bytes: bytes) -> str:
    return text_until(node, content_bytes, _body(node))


def _method_signature(node: Node, content_bytes: bytes) -> str:
    return text_until(node, content_bytes, node.child_by_field_name("body")).rstrip(";").strip()


def _leading_doc(node: Node, content_bytes: bytes) -> Optional[str]:
    prev = node.prev_sibling
    if prev is not None and prev.type == "comment" and prev.end_point[0] >= node.start_point[0] - 1:
        txt = node_text(prev, content_bytes)
        if txt.startswith("/**"):
            return txt
    return None


def _template_ratio(root: Node) -> float:
    total = max(root.end_byte - root.start_byte, 1)
    text_bytes = 0
    stack = [root]
    while stack:
        n = stack.pop()
        if n.type == "text":
            text_bytes += n.end_byte - n.start_byte
            continue
        stack.extend(n.children)
    return text_bytes / total


class PHPFileReader(StructuredReaderBase):
    """Semantic chunking for PHP files using Tree-sitter AST."""

    COMMENT = "//"
    SCOPE_LABEL = "Namespace"
    LANGUAGE = "PHP"

    def __init__(self):
        super().__init__()
        self._text_reader = TextFileReader()

    def load_nodes(self, file: Path, extra_info: Optional[dict] = None) -> List[TextNode]:
        docs = self.load_data(file, extra_info)
        if docs and docs[0].metadata.get("php_template"):
            return self._text_reader.load_nodes(file, extra_info)
        return [node_from_doc(d) for d in docs]

    def _summary_members(self, body: Node, content_bytes: bytes) -> List[str]:
        members: List[str] = []
        for c in body.children:
            t = c.type
            if t == "method_declaration":
                members.append(_method_signature(c, content_bytes))
            elif t in ("property_declaration", "const_declaration", "use_declaration", "enum_case"):
                members.append(collapse(node_text(c, content_bytes)))
        return members

    def _overview(self, node: Node, body: Node, content_bytes: bytes, prefix: str, name: str) -> str:
        kind = TYPE_NODES[node.type]
        hdr = type_header(node, content_bytes)
        for m in ("abstract", "final", "readonly"):
            if hdr.startswith(m + " ") or f" {m} " in hdr.split(kind)[0]:
                kind = f"{m} {kind}"
        inherits = []
        for c in node.children:
            if c.type in ("base_clause", "class_interface_clause"):
                inherits.append(collapse(node_text(c, content_bytes)))
        sections = {"traits": [], "constants": [], "cases": [], "properties": [], "constructors": [], "methods": []}
        for c in body.children:
            t = c.type
            if t == "use_declaration":
                sections["traits"].append(collapse(node_text(c, content_bytes))[4:].rstrip(";"))
            elif t == "const_declaration":
                for e in c.children:
                    if e.type == "const_element":
                        n = _name(e, content_bytes)
                        if n:
                            sections["constants"].append(n)
            elif t == "enum_case":
                n = _name(c, content_bytes)
                if n:
                    sections["cases"].append(n)
            elif t == "property_declaration":
                for e in c.children:
                    if e.type == "property_element":
                        sections["properties"].append(node_text(e, content_bytes).split("=")[0].strip())
            elif t == "method_declaration":
                n = _name(c, content_bytes) or ""
                sections["constructors" if n == "__construct" else "methods"].append(n)
        return self.overview_text(prefix, name, kind, hdr, " ".join(inherits), sections)

    def load_data(self, file: Path, extra_info: Optional[dict] = None) -> List[Document]:
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
        base_meta: dict = {"unit_name": file.stem}

        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            log_warn(f"Tree-sitter PHP parse failed for {file}: {e}")
            return [self.fallback_document(content, file_path_str, file_datetime, base_meta, parse_error=str(e))]
        root = tree.root_node

        raw: List[RawChunk] = []
        imports: List[Node] = []
        script: List[Node] = []
        namespaces: List[str] = []
        declared = [0]

        def prefix_for(ns: Optional[str], nesting: List[str], header: Optional[str]) -> str:
            display = " > ".join(nesting) if nesting else None
            return self.build_prefix(file_name, ns, display, nested_header(nesting, header))

        def ns_meta(ns: Optional[str]) -> dict:
            return {"package_name": ns, "namespace": ns} if ns else {}

        def with_doc(node: Node) -> str:
            txt = node_text(node, content_bytes)
            doc = _leading_doc(node, content_bytes)
            return f"{doc}\n{txt}" if doc else txt

        def walk(node: Node, ns: Optional[str], nesting: List[str], header: Optional[str], top: bool) -> None:
            t = node.type
            if t == "namespace_definition":
                n = node.child_by_field_name("name")
                name = node_text(n, content_bytes) if n is not None else None
                if name and name not in namespaces:
                    namespaces.append(name)
                body = node.child_by_field_name("body")
                if body is None:
                    state["ns"] = name
                else:
                    for c in body.children:
                        walk(c, name, nesting, header, True)
                return
            if t == "namespace_use_declaration":
                imports.append(node)
                return
            if t in TYPE_NODES:
                declared[0] += 1
                name = _name(node, content_bytes) or ""
                hdr = type_header(node, content_bytes)
                new_nesting = nesting + [name] if name else nesting
                prefix = prefix_for(ns, new_nesting, hdr)
                extra = {"php_kind": TYPE_NODES[t], **ns_meta(ns)}
                body = _body(node)
                summary = None
                if body is not None:
                    summary = self.summary_text(prefix, hdr, self._summary_members(body, content_bytes))
                if summary is None:
                    summary = f"{prefix}\n{node_text(node, content_bytes)}"
                doc = _leading_doc(node, content_bytes)
                if doc:
                    summary = summary.replace(f"{prefix}\n", f"{prefix}\n{doc}\n", 1)
                raw.append(RawChunk.from_node("class_summary", node, summary, name, extra=extra))
                if body is not None and len(summary) > self.MAX_SUMMARY_CHARS:
                    raw.append(
                        RawChunk.from_node(
                            "class_overview", node, self._overview(node, body, content_bytes, prefix, name), name, extra=extra
                        )
                    )
                if body is not None:
                    for c in body.children:
                        walk(c, ns, new_nesting, hdr, False)
                return
            leaf = None
            if t == "method_declaration":
                leaf = "constructor_declaration" if _name(node, content_bytes) == "__construct" else "method_declaration"
            elif t == "function_definition":
                leaf = "method_declaration"
                declared[0] += 1
            elif t == "property_declaration":
                leaf = "field_declaration"
            elif t == "const_declaration":
                leaf = "constant_declaration"
            if leaf:
                cls = nesting[-1] if nesting else ""
                body_text = with_doc(node)
                extra = dict(ns_meta(ns))
                if leaf in ("method_declaration", "constructor_declaration"):
                    n = _name(node, content_bytes)
                    if n:
                        extra["function_name"] = n
                raw.append(
                    RawChunk.from_node(leaf, node, f"{prefix_for(ns, nesting, header)}\n{body_text}", cls, body=body_text, extra=extra)
                )
                return
            if t in ("comment", "php_tag", "text_interpolation", "php_end_tag", "declare_statement", "use_declaration", "enum_case"):
                if t == "comment" and top:
                    block = free_comment_block(node)
                    txt = "\n".join(node_text(b, content_bytes) for b in block or [])
                    if block and len(txt) >= self.MIN_COMMENT_CHARS:
                        raw.append(
                            RawChunk.from_node(
                                "block_comment", block[-1], f"{prefix_for(ns, nesting, header)}\n{txt}",
                                extra=ns_meta(ns), start_node=block[0],
                            )
                        )
                return
            if top and node.is_named:
                script.append(node)
                return
            for c in node.children:
                walk(c, ns, nesting, header, top)

        state = {"ns": None}
        for child in root.children:
            walk(child, state["ns"], [], None, True)

        if declared[0] == 0 and _template_ratio(root) > TEMPLATE_TEXT_RATIO:
            return [self.fallback_document(content, file_path_str, file_datetime, base_meta, php_template=True)]

        first_ns = namespaces[0] if namespaces else None
        if namespaces:
            base_meta["namespaces"] = namespaces
        documents: List[Document] = []
        if imports:
            text = self.build_prefix(file_name, first_ns) + "\n" + "\n".join(node_text(i, content_bytes) for i in imports)
            chunk = RawChunk.from_node("import_group", imports[-1], text, start_node=imports[0], extra=ns_meta(first_ns))
            documents.extend(self.make_documents(chunk, file_path_str, file_datetime, base_meta))
        documents.extend(self.emit(raw, file_path_str, file_datetime, base_meta))
        if script:
            body = "\n".join(node_text(n, content_bytes) for n in script)
            chunk = RawChunk.from_node(
                "script_body", script[-1], f"{self.build_prefix(file_name, first_ns)}\n{body}", start_node=script[0], extra=ns_meta(first_ns)
            )
            documents.extend(self.make_documents(chunk, file_path_str, file_datetime, base_meta))
        if not documents:
            documents.append(self.fallback_document(content, file_path_str, file_datetime, base_meta))
        return documents


# ────────────────────────────────────────────────
# Rerank profile (query-time ranking knowledge, see shared/rerank_profile.py)
# ────────────────────────────────────────────────

RERANK_PROFILE = java_style_profile(
    "php",
    simple_stem_pattern("php"),
    test_paths=[r"(?:^|/)tests?/", r"Test\.php$"],
    # const NAME = ..., public $name = ..., 'key' => ...
    declaration_names=[r"\bconst\s+([A-Za-z_][A-Za-z0-9_]*)", r"^(?:[a-z]+\s+)*(?:\??[\w\\|]+\s+)?\$([A-Za-z_][A-Za-z0-9_]*)"],
)

PHPFileReader.rerank_profile = RERANK_PROFILE
