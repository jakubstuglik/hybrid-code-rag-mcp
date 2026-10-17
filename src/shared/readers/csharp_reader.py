"""
C# file reader (.cs) using Tree-sitter AST (``csharp`` grammar).

Modelled on the Java reader, so C# chunks carry the same context prefix and
node types as Java/Kotlin chunks and the reranker treats them alike:

    // File: OrderService.cs
    // Namespace: Acme.Orders
    // Class: [Serializable] public partial class OrderService : BaseService, IOrderService

Chunking strategy:

1. **Namespaces**: block namespaces (``namespace A.B { ... }``, also nested)
   and file-scoped namespaces (``namespace A.B;``) set the ``// Namespace:``
   line of every chunk that follows.
2. **Types**: classes, structs, interfaces, records (class and struct) and
   enums each get a ``class_summary`` chunk (header + member signatures, no
   bodies) and, when large, a ``class_overview`` chunk.  Nested types use the
   ``Outer > Inner`` class chain.  ``partial`` types get a summary per file
   (metadata ``partial: True``).  Body-less records
   (``public record Point(int X, int Y);``) are emitted whole as their summary.
3. **Members**: methods, local operators, destructors -> ``method_declaration``;
   constructors -> ``constructor_declaration``; fields, properties, indexers
   and events -> ``field_declaration``; delegates -> ``type_alias_declaration``.
   ``///`` XML doc comments directly above a member are kept with it.
4. **using directives** -> one ``import_group`` chunk per file.
5. **Top-level statements** (C# 9 ``Program.cs``) -> one ``script_body`` chunk.
6. Trivial-method grouping (``method_group``), oversized splitting and the
   ``full_file`` fallback work as in the Java reader.
"""

from pathlib import Path
from typing import List, Optional

from llama_index.core import Document
from tree_sitter import Node
from tree_sitter_language_pack import get_parser

from shared.log import log_warn
from shared.readers._base import get_file_datetime, read_file_with_encoding_and_bytes
from shared.readers._structured import (
    RawChunk,
    StructuredReaderBase,
    collapse,
    nested_header,
    node_text,
    text_until,
)

_parser = get_parser("csharp")

TYPE_NODES = {
    "class_declaration": "class",
    "struct_declaration": "struct",
    "interface_declaration": "interface",
    "record_declaration": "record",
    "record_struct_declaration": "record struct",
    "enum_declaration": "enum",
}
NAMESPACE_NODES = {"namespace_declaration", "file_scoped_namespace_declaration"}
METHOD_NODES = {
    "method_declaration",
    "operator_declaration",
    "conversion_operator_declaration",
    "destructor_declaration",
}
FIELD_NODES = {
    "field_declaration",
    "property_declaration",
    "indexer_declaration",
    "event_declaration",
    "event_field_declaration",
}
BODY_NODES = {"declaration_list", "enum_member_declaration_list"}
CODE_BODY_NODES = {"block", "arrow_expression_clause"}


def _name(node: Node, content_bytes: bytes) -> Optional[str]:
    n = node.child_by_field_name("name")
    if n is not None:
        return node_text(n, content_bytes)
    for child in node.children:
        if child.type == "identifier":
            return node_text(child, content_bytes)
    return None


def _body(node: Node) -> Optional[Node]:
    for child in node.children:
        if child.type in BODY_NODES:
            return child
    return None


def _modifiers(node: Node, content_bytes: bytes) -> List[str]:
    return [node_text(c, content_bytes) for c in node.children if c.type == "modifier"]


def type_header(node: Node, content_bytes: bytes) -> str:
    return text_until(node, content_bytes, _body(node)).rstrip(";").strip()


def member_signature(node: Node, content_bytes: bytes) -> str:
    """Signature of a member without its body."""
    if node.type in FIELD_NODES and node.type not in ("property_declaration", "indexer_declaration"):
        return collapse(node_text(node, content_bytes))
    stop = None
    for child in node.children:
        if child.type in CODE_BODY_NODES or child.type == "accessor_list":
            stop = child
            break
    sig = text_until(node, content_bytes, stop).rstrip(";").strip()
    if stop is not None and stop.type == "accessor_list":
        kinds = []
        for acc in stop.children:
            if acc.type == "accessor_declaration":
                words = [
                    node_text(c, content_bytes)
                    for c in acc.children
                    if c.type in ("modifier", "get", "set", "init", "add", "remove")
                    or (not c.is_named and c.type in ("get", "set", "init", "add", "remove"))
                ]
                kinds.append(" ".join(words) or node_text(acc, content_bytes).split("{")[0].split("=>")[0].strip().rstrip(";"))
        sig = f"{sig} {{ {' '.join(k + ';' for k in kinds)} }}"
    elif stop is not None and stop.type == "arrow_expression_clause" and node.type in (
        "property_declaration",
        "indexer_declaration",
    ):
        sig = f"{sig} => ..."
    return sig


def _leading_doc(node: Node, content_bytes: bytes) -> Optional[str]:
    """``///`` / ``/** */`` comments directly above *node*."""
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


def _is_doc_comment(node: Node) -> bool:
    """A comment immediately followed by a declaration (it is attached there)."""
    nxt = node.next_sibling
    return (
        nxt is not None
        and nxt.type != "comment"
        and nxt.start_point[0] <= node.end_point[0] + 1
    )


class CSharpFileReader(StructuredReaderBase):
    """Semantic chunking for C# files using Tree-sitter AST."""

    COMMENT = "//"
    SCOPE_LABEL = "Namespace"
    LANGUAGE = "C#"

    def _summary_members(self, body: Node, content_bytes: bytes) -> List[str]:
        members: List[str] = []
        for child in body.children:
            t = child.type
            if t in METHOD_NODES or t in FIELD_NODES or t in ("constructor_declaration", "delegate_declaration"):
                members.append(member_signature(child, content_bytes))
            elif t in TYPE_NODES:
                inner = type_header(child, content_bytes)
                members.append(f"{inner} {{ ... }}" if _body(child) is not None else inner)
            elif t == "enum_member_declaration":
                members.append(collapse(node_text(child, content_bytes)) + ",")
            elif t not in ("{", "}", ";", ",", "comment") and child.is_named:
                # preprocessor regions etc.: look one level inside
                for sub in child.children:
                    if sub.type in METHOD_NODES or sub.type in FIELD_NODES or sub.type == "constructor_declaration":
                        members.append(member_signature(sub, content_bytes))
        return members

    def _overview(self, node: Node, body: Node, content_bytes: bytes, prefix: str, name: str) -> str:
        kind = TYPE_NODES[node.type]
        mods = _modifiers(node, content_bytes)
        for m in ("abstract", "static", "sealed", "partial"):
            if m in mods:
                kind = f"{m} {kind}"
        inherits = ""
        for child in node.children:
            if child.type == "base_list":
                inherits = "inherits " + collapse(node_text(child, content_bytes)).lstrip(":").strip()
        sections = {
            "enum members": [],
            "fields": [],
            "properties": [],
            "events": [],
            "constructors": [],
            "methods": [],
            "inner types": [],
        }
        for child in body.children:
            t = child.type
            n = _name(child, content_bytes)
            if t == "enum_member_declaration" and n:
                sections["enum members"].append(n)
            elif t in ("field_declaration", "event_field_declaration"):
                for d in child.children:
                    if d.type == "variable_declaration":
                        for v in d.children:
                            if v.type == "variable_declarator":
                                vn = _name(v, content_bytes)
                                if vn:
                                    sections["events" if t.startswith("event") else "fields"].append(vn)
            elif t in ("property_declaration", "indexer_declaration") and n:
                sections["properties"].append(n if t == "property_declaration" else "this[]")
            elif t == "event_declaration" and n:
                sections["events"].append(n)
            elif t == "constructor_declaration" and n:
                sections["constructors"].append(n)
            elif t in METHOD_NODES:
                sections["methods"].append(n or t.replace("_declaration", ""))
            elif t in TYPE_NODES and n:
                sections["inner types"].append(n)
        return self.overview_text(prefix, name, kind, type_header(node, content_bytes), inherits, sections)

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
        base_meta = {"unit_name": file.stem}

        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            log_warn(f"Tree-sitter C# parse failed for {file}: {e}")
            return [self.fallback_document(content, file_path_str, file_datetime, base_meta, parse_error=str(e))]

        raw: List[RawChunk] = []
        usings: List[Node] = []
        script: List[Node] = []
        summarised: set = set()
        namespaces: List[str] = []

        def prefix_for(ns: Optional[str], nesting: List[str], header: Optional[str]) -> str:
            display = " > ".join(nesting) if nesting else None
            return self.build_prefix(file_name, ns, display, nested_header(nesting, header))

        def ns_meta(ns: Optional[str]) -> dict:
            return {"package_name": ns, "namespace": ns} if ns else {}

        def walk(node: Node, ns: Optional[str], nesting: List[str], header: Optional[str]) -> None:
            t = node.type
            if t in NAMESPACE_NODES:
                name_node = node.child_by_field_name("name")
                name = node_text(name_node, content_bytes) if name_node is not None else ""
                full = f"{ns}.{name}" if ns and name else (name or ns)
                if full and full not in namespaces:
                    namespaces.append(full)
                if t == "file_scoped_namespace_declaration":
                    state["ns"] = full
                    for child in node.children:
                        if child is not name_node:
                            walk(child, full, nesting, header)
                    return
                for child in node.children:
                    if child.type == "declaration_list":
                        for sub in child.children:
                            walk(sub, full, nesting, header)
                return

            if t == "using_directive":
                usings.append(node)
                return

            if t == "global_statement":
                script.append(node)
                return

            if t in TYPE_NODES:
                name = _name(node, content_bytes) or ""
                hdr = type_header(node, content_bytes)
                new_nesting = nesting + [name] if name else nesting
                prefix = prefix_for(ns, new_nesting, hdr)
                current = nesting[-1] if nesting else ""
                extra = {"csharp_kind": TYPE_NODES[t], **ns_meta(ns)}
                if "partial" in _modifiers(node, content_bytes):
                    extra["partial"] = True
                if current:
                    extra["outer_class"] = current
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
                summarised.add(name)
                if body is not None and len(summary) > self.MAX_SUMMARY_CHARS:
                    overview = self._overview(node, body, content_bytes, prefix, " > ".join(new_nesting) or name)
                    raw.append(RawChunk.from_node("class_overview", node, overview, name, extra=extra))
                if body is not None:
                    for child in body.children:
                        walk(child, ns, new_nesting, hdr)
                return

            leaf_type = None
            if t in METHOD_NODES or t == "local_function_statement":
                leaf_type = "method_declaration"
            elif t == "constructor_declaration":
                leaf_type = "constructor_declaration"
            elif t in FIELD_NODES:
                leaf_type = "field_declaration"
            elif t == "delegate_declaration":
                leaf_type = "type_alias_declaration"
            if leaf_type:
                current = nesting[-1] if nesting else ""
                body_text = node_text(node, content_bytes)
                doc = _leading_doc(node, content_bytes)
                if doc:
                    body_text = f"{doc}\n{body_text}"
                extra = dict(ns_meta(ns))
                n = _name(node, content_bytes)
                if n and t in ("method_declaration", "constructor_declaration", "local_function_statement", "delegate_declaration"):
                    extra["function_name"] = n
                text = f"{prefix_for(ns, nesting, header)}\n{body_text}"
                raw.append(RawChunk.from_node(leaf_type, node, text, current, body=body_text, extra=extra))
                return

            if t == "comment":
                current = nesting[-1] if nesting else ""
                if current and current in summarised:
                    return
                if _is_doc_comment(node):
                    return
                txt = node_text(node, content_bytes)
                if len(txt) < self.MIN_COMMENT_CHARS:
                    return
                text = f"{prefix_for(ns, nesting, header)}\n{txt}"
                raw.append(RawChunk.from_node("block_comment", node, text, current, extra=ns_meta(ns)))
                return

            for child in node.children:
                walk(child, ns, nesting, header)

        state = {"ns": None}
        for child in tree.root_node.children:
            walk(child, state["ns"], [], None)

        if namespaces:
            base_meta["namespaces"] = namespaces
        first_ns = namespaces[0] if namespaces else None

        documents: List[Document] = []
        if usings:
            text = self.build_prefix(file_name, first_ns) + "\n" + "\n".join(
                node_text(u, content_bytes) for u in usings
            )
            chunk = RawChunk.from_node("import_group", usings[-1], text, start_node=usings[0], extra=ns_meta(first_ns))
            documents.extend(self.make_documents(chunk, file_path_str, file_datetime, base_meta))

        documents.extend(self.emit(raw, file_path_str, file_datetime, base_meta))

        if script:
            body = "\n".join(node_text(n, content_bytes) for n in script)
            chunk = RawChunk.from_node(
                "script_body", script[-1], f"{self.build_prefix(file_name, first_ns)}\n{body}", start_node=script[0]
            )
            documents.extend(self.make_documents(chunk, file_path_str, file_datetime, base_meta))

        if not documents:
            documents.append(self.fallback_document(content, file_path_str, file_datetime, base_meta))
        return documents
