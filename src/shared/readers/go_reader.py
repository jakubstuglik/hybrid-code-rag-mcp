"""
Go file reader (.go) using Tree-sitter AST (``go`` grammar).

Go has no classes, so the reader maps Go declarations onto the node types
the Java/Kotlin readers emit and the reranker understands:

    // File: store.go
    // Package: orders
    // Class: type Order struct

Chunking strategy:

1. **Context prefix**: ``// File:`` and ``// Package:`` on every chunk; methods
   additionally get ``// Class: type <Receiver> struct|interface|...`` for
   their receiver type, so a method chunk names the type it belongs to.
2. **Types**: every ``struct`` and ``interface`` type gets a ``class_summary``
   chunk: the full type declaration (fields / method set) followed by the
   signatures of all methods declared on it **in the same file** (collected by
   receiver type, pointer or value).  Large ones also get a
   ``class_overview``.  Other named types (``type ID int``, ``type B = int``,
   function types) become ``type_alias_declaration`` chunks.
3. **Functions and methods** -> ``method_declaration`` (metadata
   ``function_name``, and ``receiver_type`` / ``class_name`` for methods).
   Functions named ``New<Type>`` are attached to ``<Type>`` like constructors
   (``constructor_declaration``) when that type is declared in the file.
4. ``const`` blocks -> ``constant_declaration``; ``var`` blocks ->
   ``field_declaration``; imports -> one ``import_group``.
5. ``//`` doc comments directly above a declaration are kept with it; the
   package doc comment and other long free-standing comments become
   ``block_comment`` chunks.
6. Trivial-method grouping (``method_group``), oversized splitting and the
   ``full_file`` fallback work as in the Java reader.

Methods declared in other files of the same package are not part of the
summary (the reader sees one file at a time).
"""

from pathlib import Path
from typing import Dict, List, Optional

from llama_index.core import Document
from tree_sitter import Node
from tree_sitter_language_pack import get_parser

from shared.log import log_warn
from shared.readers._base import get_file_datetime, read_file_with_encoding_and_bytes
from shared.readers._structured import (
    RawChunk,
    StructuredReaderBase,
    free_comment_block,
    node_text,
    text_until,
)

_parser = get_parser("go")


def _receiver_type(node: Node, content_bytes: bytes) -> Optional[str]:
    """``func (o *Order[T]) X()`` -> ``Order``."""
    recv = node.child_by_field_name("receiver")
    if recv is None:
        return None

    def find(n: Node) -> Optional[str]:
        if n.type == "type_identifier":
            return node_text(n, content_bytes)
        for c in n.children:
            r = find(c)
            if r:
                return r
        return None

    return find(recv)


def _signature(node: Node, content_bytes: bytes) -> str:
    return text_until(node, content_bytes, node.child_by_field_name("body"))


def _leading_doc(node: Node, content_bytes: bytes) -> Optional[str]:
    docs: List[str] = []
    prev = node.prev_sibling
    row = node.start_point[0]
    while prev is not None and prev.type == "comment" and prev.end_point[0] >= row - 1:
        docs.append(node_text(prev, content_bytes))
        row = prev.start_point[0]
        prev = prev.prev_sibling
    if not docs:
        return None
    return "\n".join(reversed(docs))


def _type_kind(spec: Node) -> str:
    t = spec.child_by_field_name("type")
    if spec.type == "type_alias":
        return "alias"
    if t is None:
        return "type"
    return {"struct_type": "struct", "interface_type": "interface"}.get(t.type, "type")


class GoFileReader(StructuredReaderBase):
    """Semantic chunking for Go files using Tree-sitter AST."""

    COMMENT = "//"
    SCOPE_LABEL = "Package"
    LANGUAGE = "Go"

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
            log_warn(f"Tree-sitter Go parse failed for {file}: {e}")
            return [self.fallback_document(content, file_path_str, file_datetime, base_meta, parse_error=str(e))]

        root = tree.root_node
        package = None
        for child in root.children:
            if child.type == "package_clause":
                for sub in child.children:
                    if sub.type == "package_identifier":
                        package = node_text(sub, content_bytes)
        if package:
            base_meta["package_name"] = package

        # Pass 1: named types and methods by receiver
        types: Dict[str, Node] = {}
        type_headers: Dict[str, str] = {}
        methods_by_type: Dict[str, List[Node]] = {}
        for child in root.children:
            if child.type == "type_declaration":
                for spec in child.children:
                    if spec.type in ("type_spec", "type_alias"):
                        n = spec.child_by_field_name("name")
                        if n is not None:
                            name = node_text(n, content_bytes)
                            types[name] = spec
                            kind = _type_kind(spec)
                            type_headers[name] = f"type {name} {kind}" if kind in ("struct", "interface") else f"type {name}"
            elif child.type == "method_declaration":
                r = _receiver_type(child, content_bytes)
                if r:
                    methods_by_type.setdefault(r, []).append(child)
        constructors: Dict[str, str] = {}
        for child in root.children:
            if child.type == "function_declaration":
                n = child.child_by_field_name("name")
                fname = node_text(n, content_bytes) if n is not None else ""
                if fname.startswith("New") and fname[3:] in types and _type_kind(types[fname[3:]]) == "struct":
                    constructors[fname] = fname[3:]

        def prefix_for(class_name: Optional[str] = None) -> str:
            return self.build_prefix(file_name, package, class_name, type_headers.get(class_name or ""))

        raw: List[RawChunk] = []
        imports: List[Node] = []

        def doc_and_text(node: Node) -> str:
            txt = node_text(node, content_bytes)
            doc = _leading_doc(node, content_bytes)
            return f"{doc}\n{txt}" if doc else txt

        def emit_type(decl: Node, spec: Node, single: bool) -> None:
            n = spec.child_by_field_name("name")
            if n is None:
                return
            name = node_text(n, content_bytes)
            kind = _type_kind(spec)
            # Whole declaration text when the spec is the only one in the
            # ``type`` declaration (keeps the doc comment), else just the spec.
            src = decl if single else spec
            txt = doc_and_text(src) if single else node_text(spec, content_bytes)
            if not txt.startswith(("type", "//", "/*")):
                txt = f"type {txt}"
            if kind not in ("struct", "interface"):
                raw.append(
                    RawChunk.from_node(
                        "type_alias_declaration", spec, f"{prefix_for()}\n{txt}", name,
                        body=txt, extra={"go_kind": kind}, start_node=src,
                    )
                )
                return
            methods = methods_by_type.get(name, [])
            ctor_names = [f for f, tname in constructors.items() if tname == name]
            lines = [txt]
            if ctor_names or methods:
                lines.append("")
                lines.append(f"// Methods of {name} in {file_name}:")
                for f in ctor_names:
                    for c in root.children:
                        if c.type == "function_declaration":
                            nn = c.child_by_field_name("name")
                            if nn is not None and node_text(nn, content_bytes) == f:
                                lines.append(_signature(c, content_bytes))
                for m in methods:
                    lines.append(_signature(m, content_bytes))
            prefix = prefix_for(name)
            summary = f"{prefix}\n" + "\n".join(lines)
            extra = {"go_kind": kind}
            raw.append(RawChunk.from_node("class_summary", spec, summary, name, extra=extra, start_node=src))
            if len(summary) > self.MAX_SUMMARY_CHARS:
                fields: List[str] = []
                tnode = spec.child_by_field_name("type")
                for f in tnode.children if tnode is not None else []:
                    if f.type == "field_declaration_list":
                        for fd in f.children:
                            if fd.type == "field_declaration":
                                for idn in fd.children:
                                    if idn.type in ("field_identifier", "type_identifier"):
                                        fields.append(node_text(idn, content_bytes))
                                        break
                method_names = []
                for m in methods:
                    nn = m.child_by_field_name("name")
                    if nn is not None:
                        method_names.append(node_text(nn, content_bytes))
                overview = self.overview_text(
                    prefix, name, kind, f"type {name} {kind}", "",
                    {"fields": fields, "constructors": ctor_names, "methods": method_names},
                )
                raw.append(RawChunk.from_node("class_overview", spec, overview, name, extra=extra, start_node=src))

        for child in root.children:
            t = child.type
            if t == "import_declaration":
                imports.append(child)
            elif t == "type_declaration":
                specs = [s for s in child.children if s.type in ("type_spec", "type_alias")]
                for spec in specs:
                    emit_type(child, spec, len(specs) == 1)
            elif t in ("function_declaration", "method_declaration"):
                n = child.child_by_field_name("name")
                fname = node_text(n, content_bytes) if n is not None else ""
                body = doc_and_text(child)
                extra = {"function_name": fname} if fname else {}
                cls = ""
                node_type = "method_declaration"
                if t == "method_declaration":
                    cls = _receiver_type(child, content_bytes) or ""
                    if cls:
                        extra["receiver_type"] = cls
                elif fname in constructors:
                    cls = constructors[fname]
                    node_type = "constructor_declaration"
                raw.append(
                    RawChunk.from_node(node_type, child, f"{prefix_for(cls or None)}\n{body}", cls, body=body, extra=extra)
                )
            elif t in ("const_declaration", "var_declaration"):
                body = doc_and_text(child)
                nt = "constant_declaration" if t == "const_declaration" else "field_declaration"
                raw.append(RawChunk.from_node(nt, child, f"{prefix_for()}\n{body}", "", body=body))
            elif t == "comment":
                block = free_comment_block(child, detached_next=("package_clause",))
                if block is None:
                    continue  # doc comment kept with its declaration, or not the run's first line
                txt = "\n".join(node_text(b, content_bytes) for b in block)
                if len(txt) >= self.MIN_COMMENT_CHARS:
                    raw.append(RawChunk.from_node("block_comment", block[-1], f"{prefix_for()}\n{txt}", start_node=block[0]))

        documents: List[Document] = []
        if imports:
            text = prefix_for() + "\n" + "\n".join(node_text(i, content_bytes) for i in imports)
            chunk = RawChunk.from_node("import_group", imports[-1], text, start_node=imports[0])
            documents.extend(self.make_documents(chunk, file_path_str, file_datetime, base_meta))
        documents.extend(self.emit(raw, file_path_str, file_datetime, base_meta))
        if not documents:
            documents.append(self.fallback_document(content, file_path_str, file_datetime, base_meta))
        return documents
