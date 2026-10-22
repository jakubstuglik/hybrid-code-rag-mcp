"""
Rust file reader (.rs) using Tree-sitter AST (``rust`` grammar).

Rust has no classes, so the reader maps Rust items onto the node types the
Java/Go readers emit and the reranker understands:

    // File: walk.rs
    // Module: tests::helpers
    // Class: impl<'s, M: Matcher> Searcher<'s, M>

Chunking strategy:

1. **Context prefix**: ``// File:`` on every chunk, ``// Module:`` inside
   inline ``mod`` blocks (``outer::inner``), and ``// Class:`` with the
   ``impl`` or ``trait`` header for associated items.
2. **Types**: every ``struct``, ``enum`` and ``union`` gets a
   ``class_summary`` chunk: doc comment, attributes and the full declaration,
   followed by the member signatures of every ``impl`` block of that type
   **in the same file**, one block per impl header (inherent and trait
   impls).  Large ones also get a ``class_overview`` (fields or variants,
   methods, implemented and derived traits).
3. **Traits** -> ``class_summary`` with the trait header and the signatures
   of its associated functions, types and constants.  Default method bodies
   become ``method_declaration`` chunks of the trait.
4. **impl blocks** of a type that is not declared in the file (a trait impl
   for a foreign type, a blanket impl) get their own ``class_summary``.
5. **Functions and methods** -> ``method_declaration`` (``function_name``,
   ``class_name`` = the impl type, ``impl_trait`` for trait impls);
   ``new`` / ``new_*`` in an inherent impl that return ``Self`` or the type
   -> ``constructor_declaration``.
6. ``type`` aliases -> ``type_alias_declaration``; ``const`` ->
   ``constant_declaration``; ``static`` -> ``field_declaration``;
   ``macro_rules!`` -> ``macro_definition``; ``extern`` blocks ->
   ``extern_block``; item-level macro calls (``thread_local!``,
   ``lazy_static!``) -> ``macro_invocation``; ``use`` / ``extern crate`` /
   ``mod name;`` -> one ``import_group`` per module.
7. Inline ``mod`` blocks are walked recursively and also get a
   ``module_summary`` listing their items.
8. ``///`` and ``/** */`` doc comments and ``#[...]`` attributes directly
   above an item are kept with it; ``//!`` module docs and other long
   free-standing comments become ``block_comment`` chunks.  A ``#[cfg(...)]``
   on an item or an enclosing module is recorded as ``cfg`` metadata.
9. ``object_name`` holds the declared name (used by the exact symbol
   lookup); chunks that declare several names (summaries, method groups,
   extern blocks) list them all in ``symbols``, so ``SYMBOLS_PER_SPLIT_PART``
   and ``SYMBOLS_MAX_PER_CHUNK`` apply as for C/C++.
10. Trivial-method grouping (``method_group``), oversized splitting and the
    ``full_file`` fallback work as in the other structured readers.

Tree-sitter recovers from syntax errors: the valid items of a broken file
are still chunked.  Items produced by macros are not visible to the reader.
"""

import dataclasses
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from llama_index.core import Document
from tree_sitter import Node
from tree_sitter_language_pack import get_parser

from shared.log import log_warn
from shared.readers._base import get_file_datetime, read_file_with_encoding_and_bytes
from shared.readers._structured import (
    RawChunk,
    StructuredReaderBase,
    collapse,
    node_text,
    text_until,
)
from shared.rerank_profile import (
    JAVA_STYLE_DETAIL_TYPES,
    JAVA_STYLE_OVERVIEW_TYPES,
    compile_all,
    java_style_profile,
    simple_stem_pattern,
)

_parser = get_parser("rust")

_COMMENT_TYPES = ("line_comment", "block_comment")
_TYPE_ITEMS = {"struct_item": "struct", "enum_item": "enum", "union_item": "union"}
_IMPORT_ITEMS = ("use_declaration", "extern_crate_declaration")
_CFG = re.compile(r"^#\[\s*cfg\s*\((.*)\)\s*\]$", re.DOTALL)
_DERIVE = re.compile(r"^#\[\s*derive\s*\((.*)\)\s*\]$", re.DOTALL)
# rgtest!(name, ...) / matches!(name, "a", "b"): the first argument names the item
_MACRO_FIRST_ARG = re.compile(r"^[(\[{]\s*([A-Za-z_]\w*)\s*,")
_MACRO_STATIC = re.compile(r"\bstatic\s+(?:ref\s+)?(?:mut\s+)?([A-Za-z_]\w*)\s*:")


def _end_row(node: Node) -> int:
    """Last source row of *node*; a ``//`` comment node includes its newline."""
    row, col = node.end_point
    if col == 0 and row > node.start_point[0]:
        return row - 1
    return row


def _is_inner_doc(node: Node, content_bytes: bytes) -> bool:
    """``//!`` / ``/*!`` comments document the enclosing module."""
    return node.type in _COMMENT_TYPES and node_text(node, content_bytes).startswith(("//!", "/*!"))


def _leading(node: Node, content_bytes: bytes) -> Tuple[Node, List[Node]]:
    """Doc comments and attributes directly above *node* (no blank line).

    Returns ``(first_node, nodes)`` in source order; ``first_node`` is *node*
    itself when there is nothing above it.
    """
    out: List[Node] = []
    prev = node.prev_sibling
    row = node.start_point[0]
    while (
        prev is not None
        and prev.type in (*_COMMENT_TYPES, "attribute_item")
        and _end_row(prev) >= row - 1
        and not _is_inner_doc(prev, content_bytes)
    ):
        out.append(prev)
        row = prev.start_point[0]
        prev = prev.prev_sibling
    out.reverse()
    return (out[0] if out else node), out


def _attached(node: Node) -> bool:
    """True when the comment run starting at *node* sits right above an item."""
    nxt = node.next_sibling
    last = node
    while nxt is not None and nxt.type in _COMMENT_TYPES and nxt.start_point[0] <= _end_row(last) + 1:
        last = nxt
        nxt = nxt.next_sibling
    return (
        nxt is not None
        and nxt.type not in ("{", "}")
        and nxt.start_point[0] <= _end_row(last) + 1
    )


def _name(node: Node, content_bytes: bytes) -> str:
    n = node.child_by_field_name("name")
    return node_text(n, content_bytes) if n is not None else ""


def _type_base(node: Optional[Node], content_bytes: bytes) -> str:
    """``Foo<'a, T>`` / ``a::b::Foo`` / ``&mut Foo`` / ``dyn Foo`` -> ``Foo``."""
    if node is None:
        return ""
    if node.type in ("type_identifier", "identifier"):
        return node_text(node, content_bytes)
    if node.type == "generic_type":
        return _type_base(node.child_by_field_name("type"), content_bytes)
    if node.type in ("scoped_type_identifier", "scoped_identifier"):
        return _type_base(node.child_by_field_name("name"), content_bytes)
    for c in node.named_children:
        if c.type in ("lifetime", "mutable_specifier"):
            continue
        r = _type_base(c, content_bytes)
        if r:
            return r
    return collapse(node_text(node, content_bytes))


def _type_params(node: Node, content_bytes: bytes) -> List[str]:
    for c in node.children:
        if c.type == "type_parameters":
            names = []
            for p in c.named_children:
                if p.type == "type_identifier":
                    names.append(node_text(p, content_bytes))
                else:
                    n = p.child_by_field_name("name")
                    if n is None:
                        n = next((x for x in p.named_children if x.type == "type_identifier"), None)
                    if n is not None and n.type == "type_identifier":
                        names.append(node_text(n, content_bytes))
            return names
    return []


def _header(node: Node, content_bytes: bytes) -> str:
    """Declaration text up to its body, on one line."""
    return text_until(node, content_bytes, node.child_by_field_name("body")).rstrip(";").strip()


def _signature(node: Node, content_bytes: bytes) -> str:
    """Signature line of an associated item (no body, no trailing ``;``)."""
    if node.type == "function_item":
        return _header(node, content_bytes)
    return collapse(node_text(node, content_bytes)).rstrip(";").strip()


def _attr_values(attrs: List[Node], content_bytes: bytes, pattern: "re.Pattern") -> List[str]:
    out = []
    for a in attrs:
        if a.type != "attribute_item":
            continue
        m = pattern.match(collapse(node_text(a, content_bytes)))
        if m:
            out.append(m.group(1).strip())
    return out


@dataclasses.dataclass
class _Impl:
    node: Node
    header: str
    type_name: str
    trait_name: str
    members: List[Node]


@dataclasses.dataclass
class _Scope:
    """One module level (the file or an inline ``mod``)."""

    path: List[str]
    cfg: List[str]
    raw: List[RawChunk] = dataclasses.field(default_factory=list)
    imports: List[Node] = dataclasses.field(default_factory=list)


class RustFileReader(StructuredReaderBase):
    """Semantic chunking for Rust files using Tree-sitter AST."""

    COMMENT = "//"
    SCOPE_LABEL = "Module"
    LANGUAGE = "Rust"
    MAX_MODULE_ITEMS = 60  # item lines listed in a module_summary

    def load_data(self, file: Path, extra_info: Optional[dict] = None) -> List[Document]:
        try:
            content, content_bytes = read_file_with_encoding_and_bytes(file)
        except Exception as e:
            log_warn(f"Failed to read {file}: {e}")
            return []
        if not content.strip():
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)
        base_meta: dict = {"unit_name": file.stem}

        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            log_warn(f"Tree-sitter Rust parse failed for {file}: {e}")
            return [self.fallback_document(content, file_path_str, file_datetime, base_meta, parse_error=str(e))]

        walker = _Walker(self, file.name, content_bytes)
        walker.collect(tree.root_node)
        walker.walk(tree.root_node, [], [])

        documents: List[Document] = []
        for scope in walker.scopes:
            meta = dict(base_meta)
            if scope.path:
                meta["module_path"] = "::".join(scope.path)
            if scope.imports:
                text = walker.prefix(scope.path) + "\n" + "\n".join(
                    node_text(i, content_bytes) for i in scope.imports
                )
                chunk = RawChunk.from_node("import_group", scope.imports[-1], text, start_node=scope.imports[0])
                documents.extend(self.make_documents(chunk, file_path_str, file_datetime, meta))
            documents.extend(self.emit(scope.raw, file_path_str, file_datetime, meta))
        if not documents:
            documents.append(self.fallback_document(content, file_path_str, file_datetime, base_meta))
        return documents

    def emit(self, raw, file_path_str, file_datetime, base_meta):
        out: List[RawChunk] = []
        i = 0
        methods = ("method_declaration", "constructor_declaration")
        while i < len(raw):
            ch = raw[i]
            trivial = ch.lines <= self.TRIVIAL_METHOD_LINES
            j = i + 1
            if ch.node_type in methods and trivial:
                while (
                    j < len(raw)
                    and raw[j].node_type in methods
                    and raw[j].class_name == ch.class_name
                    and raw[j].lines <= self.TRIVIAL_METHOD_LINES
                ):
                    j += 1
            elif ch.node_type == "macro_invocation" and trivial:
                while (
                    j < len(raw)
                    and raw[j].node_type == "macro_invocation"
                    and raw[j].extra.get("macro_name") == ch.extra.get("macro_name")
                    and raw[j].class_name == ch.class_name
                    and raw[j].lines <= self.TRIVIAL_METHOD_LINES
                ):
                    j += 1
            if j - i < self.MIN_GROUP_RUN:
                out.append(ch)
                i += 1
                continue
            run = raw[i:j]
            i = j
            if ch.node_type == "macro_invocation":
                out.extend(self._macro_groups(run))
                continue
            # A method group must not inherit the object_name of its first
            # member: the grouped names go to symbols instead.
            names = [r.extra.get("object_name") for r in run if r.extra.get("object_name")]
            for r in run:
                r.extra = {k: v for k, v in r.extra.items() if k not in ("object_name", "symbols")}
                if names:
                    r.extra["symbols"] = names
            out.extend(run)
        return super().emit(out, file_path_str, file_datetime, base_meta)

    def _macro_groups(self, run: List[RawChunk]) -> List[RawChunk]:
        """Runs of short calls of one macro (test tables such as
        ``matches!(name, ...)``) become ``macro_group`` chunks."""
        prefix = self.prefix_of(run[0].text)
        macro = run[0].extra.get("macro_name", "")
        groups: List[List[RawChunk]] = [[]]
        chars = 0
        for ch in run:
            if groups[-1] and chars + len(ch.body) > self.MAX_GROUP_CHARS:
                groups.append([])
                chars = 0
            groups[-1].append(ch)
            chars += len(ch.body)
        out = []
        for g in groups:
            names = list(dict.fromkeys(r.extra["object_name"] for r in g if r.extra.get("object_name")))
            extra = {k: v for k, v in g[0].extra.items() if k not in ("object_name", "symbols")}
            extra["group_count"] = len(g)
            if names:
                extra["symbols"] = names
            text = f"{prefix}\n{self.COMMENT} Macro group: {len(g)} calls of {macro}!\n" + "\n".join(r.body for r in g)
            out.append(
                RawChunk(
                    node_type="macro_group",
                    text=text,
                    start_line=g[0].start_line,
                    end_line=g[-1].end_line,
                    start_byte=g[0].start_byte,
                    end_byte=g[-1].end_byte,
                    class_name=g[0].class_name,
                    lines=sum(r.lines for r in g),
                    extra=extra,
                )
            )
        return out


class _Walker:
    """Collects the raw chunks of one file."""

    def __init__(self, reader: RustFileReader, file_name: str, content_bytes: bytes):
        self.r = reader
        self.file_name = file_name
        self.cb = content_bytes
        self.scopes: List[_Scope] = []
        self.types: Dict[str, int] = {}  # struct / enum / union / trait name -> start byte
        self.impls: Dict[str, List[_Impl]] = {}

    # -- helpers --------------------------------------------------------

    def prefix(self, path: List[str], header: Optional[str] = None) -> str:
        return self.r.build_prefix(self.file_name, "::".join(path) or None, None, header)

    def text_with_leading(self, node: Node) -> Tuple[Node, str, List[Node]]:
        first, lead = _leading(node, self.cb)
        parts = [node_text(n, self.cb) for n in lead] + [node_text(node, self.cb)]
        return first, "\n".join(parts), lead

    def make_impl(self, node: Node) -> _Impl:
        body = node.child_by_field_name("body")
        members = list(body.named_children) if body is not None else []
        tname = _type_base(node.child_by_field_name("type"), self.cb)
        trait = _type_base(node.child_by_field_name("trait"), self.cb) if node.child_by_field_name("trait") else ""
        if trait and tname in _type_params(node, self.cb):
            tname = trait  # blanket impl: impl<T: Display> Tr for T
        return _Impl(node, _header(node, self.cb), tname, trait, members)

    # -- pass 1: types and impls of the whole file ------------------------

    def collect(self, node: Node) -> None:
        for child in node.named_children:
            t = child.type
            if t in _TYPE_ITEMS or t == "trait_item":
                name = _name(child, self.cb)
                if name and name not in self.types:
                    self.types[name] = child.start_byte
            elif t == "impl_item":
                imp = self.make_impl(child)
                if imp.type_name:
                    self.impls.setdefault(imp.type_name, []).append(imp)
            elif t == "mod_item":
                body = child.child_by_field_name("body")
                if body is not None:
                    self.collect(body)

    # -- pass 2: chunks -------------------------------------------------

    def walk(self, container: Node, path: List[str], cfg: List[str]) -> _Scope:
        scope = _Scope(path=list(path), cfg=list(cfg))
        self.scopes.append(scope)
        for child in container.named_children:
            t = child.type
            if t in _IMPORT_ITEMS or (t == "mod_item" and child.child_by_field_name("body") is None):
                scope.imports.append(child)
            elif t in _COMMENT_TYPES:
                self.comment(scope, child)
            elif t in _TYPE_ITEMS:
                self.type_item(scope, child, _TYPE_ITEMS[t])
            elif t == "trait_item":
                self.trait_item(scope, child)
            elif t == "impl_item":
                self.impl_item(scope, child)
            elif t == "function_item":
                self.function(scope, child, None, None)
            elif t == "function_signature_item":
                self.simple(scope, child, "method_declaration", "fn", {"function_name": _name(child, self.cb)})
            elif t == "type_item":
                self.simple(scope, child, "type_alias_declaration", "type")
            elif t == "const_item":
                self.simple(scope, child, "constant_declaration", "const")
            elif t == "static_item":
                self.simple(scope, child, "field_declaration", "static")
            elif t == "macro_definition":
                self.simple(scope, child, "macro_definition", "macro")
            elif t == "foreign_mod_item":
                self.extern_block(scope, child)
            elif t == "macro_invocation" or (
                t == "expression_statement" and child.named_child_count == 1
                and child.named_children[0].type == "macro_invocation"
            ):
                self.macro_call(scope, child)
            elif t == "mod_item":
                self.module(scope, child)
        return scope

    def base_extra(self, scope: _Scope, kind: str, lead: List[Node], name: str = "") -> dict:
        extra: dict = {"rust_kind": kind}
        if name:
            extra["object_name"] = name
        cfg = scope.cfg + _attr_values(lead, self.cb, _CFG)
        if cfg:
            extra["cfg"] = " && ".join(dict.fromkeys(cfg))
        return extra

    def comment(self, scope: _Scope, node: Node) -> None:
        prev = node.prev_sibling
        if prev is not None and prev.type in _COMMENT_TYPES and _end_row(prev) >= node.start_point[0] - 1:
            if _is_inner_doc(prev, self.cb) == _is_inner_doc(node, self.cb):
                return  # not the first comment of its run
        inner = _is_inner_doc(node, self.cb)
        block = [node]
        nxt = node.next_sibling
        while (
            nxt is not None
            and nxt.type in _COMMENT_TYPES
            and nxt.start_point[0] <= _end_row(block[-1]) + 1
            and _is_inner_doc(nxt, self.cb) == inner
        ):
            block.append(nxt)
            nxt = nxt.next_sibling
        if not inner and _attached(block[-1]):
            return  # doc comment of the next item
        txt = "\n".join(node_text(b, self.cb) for b in block)
        if len(txt) >= self.r.MIN_COMMENT_CHARS:
            extra = {"rust_kind": "module_doc"} if inner else {}
            chunk = RawChunk.from_node(
                "block_comment", block[-1], f"{self.prefix(scope.path)}\n{txt}", extra=extra, start_node=block[0]
            )
            chunk.end_line = _end_row(block[-1]) + 1
            scope.raw.append(chunk)

    def simple(self, scope: _Scope, node: Node, node_type: str, kind: str, extra: Optional[dict] = None,
               class_name: str = "", header: Optional[str] = None) -> None:
        first, txt, lead = self.text_with_leading(node)
        name = _name(node, self.cb)
        ex = self.base_extra(scope, kind, lead, name)
        ex.update(extra or {})
        scope.raw.append(
            RawChunk.from_node(node_type, node, f"{self.prefix(scope.path, header)}\n{txt}", class_name,
                               body=txt, extra=ex, start_node=first)
        )

    def function(self, scope: _Scope, node: Node, imp: Optional[_Impl], trait_header: Optional[str],
                 trait_name: str = "") -> None:
        name = _name(node, self.cb)
        extra: dict = {"function_name": name} if name else {}
        node_type = "method_declaration"
        cls = ""
        header = None
        if imp is not None:
            cls = imp.type_name
            header = imp.header
            if imp.trait_name:
                extra["impl_trait"] = imp.trait_name
            ret = node.child_by_field_name("return_type")
            ret_txt = node_text(ret, self.cb) if ret is not None else ""
            if (
                not imp.trait_name
                and (name == "new" or name.startswith("new_"))
                and re.search(rf"\b(?:Self|{re.escape(cls)})\b", ret_txt)
            ):
                node_type = "constructor_declaration"
        elif trait_header is not None:
            cls = trait_name
            header = trait_header
        sig = _header(node, self.cb)
        if re.search(r"\basync\b", sig.split("fn", 1)[0]):
            extra["is_async"] = True
        self.simple(scope, node, node_type, "fn", extra, cls, header)

    # -- types ----------------------------------------------------------

    def impl_lines(self, imp: _Impl) -> List[str]:
        sigs = [
            _signature(m, self.cb)
            for m in imp.members
            if m.type in ("function_item", "function_signature_item", "const_item", "type_item", "associated_type")
        ]
        if not sigs:
            return [f"{imp.header} {{}}"]
        return [f"{imp.header} {{"] + [f"    {s}" for s in sigs] + ["}"]

    def member_names(self, imp: _Impl, kinds=("function_item",)) -> List[str]:
        return [_name(m, self.cb) for m in imp.members if m.type in kinds and _name(m, self.cb)]

    def type_item(self, scope: _Scope, node: Node, kind: str) -> None:
        name = _name(node, self.cb)
        if not name:
            return
        first, txt, lead = self.text_with_leading(node)
        header = _header(node, self.cb)
        impls = self.impls.get(name, []) if self.types.get(name) == node.start_byte else []
        lines = [txt]
        if impls:
            lines += ["", f"// Methods of {name} in {self.file_name}:"]
            for imp in impls:
                lines += self.impl_lines(imp)
        prefix = self.prefix(scope.path, header)
        summary = f"{prefix}\n" + "\n".join(lines)
        members = self.fields(node, kind)
        methods = [n for imp in impls for n in self.member_names(imp)]
        traits = [imp.trait_name for imp in impls if imp.trait_name]
        derives = [d.strip() for v in _attr_values(lead, self.cb, _DERIVE) for d in v.split(",") if d.strip()]
        extra = self.base_extra(scope, kind, lead, name)
        symbols = list(dict.fromkeys([name] + (members if kind == "enum" else []) + methods))
        if len(symbols) > 1:
            extra["symbols"] = symbols
        scope.raw.append(RawChunk.from_node("class_summary", node, summary, name, extra=extra, start_node=first))
        if len(summary) > self.r.MAX_SUMMARY_CHARS:
            label = "variants" if kind == "enum" else "fields"
            overview = self.r.overview_text(
                prefix, name, kind, header, "",
                {label: members, "methods": methods, "traits": list(dict.fromkeys(derives + traits))},
            )
            ov_extra = {k: v for k, v in extra.items() if k != "symbols"}
            scope.raw.append(RawChunk.from_node("class_overview", node, overview, name, extra=ov_extra, start_node=first))

    def fields(self, node: Node, kind: str) -> List[str]:
        body = node.child_by_field_name("body")
        if body is None:
            return []
        out = []
        for f in body.named_children:
            if f.type in ("field_declaration", "enum_variant"):
                n = f.child_by_field_name("name")
                if n is not None:
                    out.append(node_text(n, self.cb))
        return out

    def trait_item(self, scope: _Scope, node: Node) -> None:
        name = _name(node, self.cb)
        if not name:
            return
        first, _, lead = self.text_with_leading(node)
        header = _header(node, self.cb)
        body = node.child_by_field_name("body")
        members = list(body.named_children) if body is not None else []
        sigs = [
            _signature(m, self.cb)
            for m in members
            if m.type in ("function_item", "function_signature_item", "const_item", "type_item", "associated_type")
        ]
        doc = "\n".join(node_text(n, self.cb) for n in lead)
        decl = f"{header} {{\n" + "\n".join(f"    {s}" for s in sigs) + "\n}" if sigs else f"{header} {{}}"
        impls = self.impls.get(name, []) if self.types.get(name) == node.start_byte else []
        lines = [f"{doc}\n{decl}" if doc else decl]
        if impls:
            lines += ["", f"// Impls of {name} in {self.file_name}:"]
            for imp in impls:
                lines += self.impl_lines(imp)
        prefix = self.prefix(scope.path, header)
        summary = f"{prefix}\n" + "\n".join(lines)
        extra = self.base_extra(scope, "trait", lead, name)
        member_names = [_name(m, self.cb) for m in members if _name(m, self.cb)]
        symbols = list(dict.fromkeys([name] + member_names))
        if len(symbols) > 1:
            extra["symbols"] = symbols
        scope.raw.append(RawChunk.from_node("class_summary", node, summary, name, extra=extra, start_node=first))
        if len(summary) > self.r.MAX_SUMMARY_CHARS:
            fns = [_name(m, self.cb) for m in members if m.type in ("function_item", "function_signature_item")]
            assoc = [_name(m, self.cb) for m in members if m.type in ("associated_type", "const_item", "type_item")]
            overview = self.r.overview_text(prefix, name, "trait", header, "", {"methods": fns, "associated items": assoc})
            ov_extra = {k: v for k, v in extra.items() if k != "symbols"}
            scope.raw.append(RawChunk.from_node("class_overview", node, overview, name, extra=ov_extra, start_node=first))
        for m in members:
            if m.type == "function_item":
                self.function(scope, m, None, header, name)

    def impl_item(self, scope: _Scope, node: Node) -> None:
        imp = self.make_impl(node)
        first, _, lead = self.text_with_leading(node)
        if imp.type_name not in self.types:
            doc = "\n".join(node_text(n, self.cb) for n in lead)
            body = "\n".join(self.impl_lines(imp))
            txt = f"{doc}\n{body}" if doc else body
            extra = self.base_extra(scope, "impl", lead, imp.type_name)
            if imp.trait_name:
                extra["impl_trait"] = imp.trait_name
            names = [_name(m, self.cb) for m in imp.members if _name(m, self.cb)]
            symbols = list(dict.fromkeys([imp.type_name] + names))
            if len(symbols) > 1:
                extra["symbols"] = symbols
            scope.raw.append(
                RawChunk.from_node("class_summary", node, f"{self.prefix(scope.path, imp.header)}\n{txt}",
                                   imp.type_name, extra=extra, start_node=first)
            )
        impl_cfg = _attr_values(lead, self.cb, _CFG)
        member_scope = _Scope(path=scope.path, cfg=scope.cfg + impl_cfg, raw=scope.raw, imports=scope.imports)
        trait_extra = {"impl_trait": imp.trait_name} if imp.trait_name else {}
        for m in imp.members:
            if m.type == "function_item":
                self.function(member_scope, m, imp, None)
            elif m.type == "const_item":
                self.simple(member_scope, m, "constant_declaration", "const", trait_extra, imp.type_name, imp.header)
            elif m.type == "type_item":
                self.simple(member_scope, m, "type_alias_declaration", "type", trait_extra, imp.type_name, imp.header)
            elif m.type == "macro_invocation":
                self.macro_call(member_scope, m, imp.type_name, imp.header)

    def extern_block(self, scope: _Scope, node: Node) -> None:
        first, txt, lead = self.text_with_leading(node)
        body = node.child_by_field_name("body")
        names = [_name(m, self.cb) for m in (body.named_children if body is not None else []) if _name(m, self.cb)]
        extra = self.base_extra(scope, "extern", lead, names[0] if len(names) == 1 else "")
        if len(names) > 1:
            extra["symbols"] = names
        scope.raw.append(
            RawChunk.from_node("extern_block", node, f"{self.prefix(scope.path)}\n{txt}", body=txt, extra=extra, start_node=first)
        )

    def macro_call(self, scope: _Scope, node: Node, class_name: str = "", header: Optional[str] = None) -> None:
        first, txt, lead = self.text_with_leading(node)
        call = node if node.type == "macro_invocation" else node.named_children[0]
        macro = node_text(call.child_by_field_name("macro"), self.cb) if call.child_by_field_name("macro") else ""
        args = call.named_children[-1] if call.named_child_count else None
        names = list(dict.fromkeys(_MACRO_STATIC.findall(txt)))
        if not names and args is not None and args.type == "token_tree":
            m = _MACRO_FIRST_ARG.match(node_text(args, self.cb))
            if m:
                names = [m.group(1)]
        extra = self.base_extra(scope, "macro_call", lead, names[0] if len(names) == 1 else "")
        if macro:
            extra["macro_name"] = macro
        if len(names) > 1:
            extra["symbols"] = names
        scope.raw.append(
            RawChunk.from_node("macro_invocation", node, f"{self.prefix(scope.path, header)}\n{txt}", class_name,
                               body=txt, extra=extra, start_node=first)
        )

    def module(self, scope: _Scope, node: Node) -> None:
        name = _name(node, self.cb)
        body = node.child_by_field_name("body")
        first, _, lead = self.text_with_leading(node)
        cfg = scope.cfg + _attr_values(lead, self.cb, _CFG)
        items: List[str] = []
        names: List[str] = []
        for c in body.named_children:
            if c.type in (*_COMMENT_TYPES, "attribute_item", "macro_invocation", "expression_statement"):
                continue  # macro calls are listed in their own chunks
            if c.type in _IMPORT_ITEMS or c.type == "mod_item":
                line = text_until(c, self.cb, c.child_by_field_name("body"))
            elif c.type in ("function_item", "struct_item", "enum_item", "union_item", "trait_item", "impl_item",
                            "foreign_mod_item"):
                line = _header(c, self.cb)
            else:
                line = collapse(node_text(c, self.cb))
                if len(line) > 120:
                    line = line[:117] + "..."
            items.append(line.rstrip(";"))
            n = _name(c, self.cb)
            if n:
                names.append(n)
        shown = items[: self.r.MAX_MODULE_ITEMS]
        if len(items) > len(shown):
            shown.append(f"// ... ({len(items) - len(shown)} more)")
        items = shown
        doc = "\n".join(node_text(n, self.cb) for n in lead)
        header = text_until(node, self.cb, body)
        decl = f"{header} {{\n" + "\n".join(f"    {i}" for i in items) + "\n}"
        txt = f"{doc}\n{decl}" if doc else decl
        extra = self.base_extra(scope, "mod", lead, name)
        if cfg != scope.cfg:
            extra["cfg"] = " && ".join(dict.fromkeys(cfg))
        symbols = list(dict.fromkeys([name] + names))
        if len(symbols) > 1:
            extra["symbols"] = symbols
        if items:
            scope.raw.append(
                RawChunk.from_node("module_summary", node, f"{self.prefix(scope.path)}\n{txt}", extra=extra, start_node=first)
            )
        self.walk(body, scope.path + [name], cfg)


# ────────────────────────────────────────────────
# Rerank profile (query-time ranking knowledge, see shared/rerank_profile.py)
# ────────────────────────────────────────────────

_VIS = r"(?:pub(?:\s*\([^)]*\))?\s+)?"

RERANK_PROFILE = dataclasses.replace(
    java_style_profile(
        "rust",
        simple_stem_pattern("rs"),
        test_paths=[r"(?:^|/)benches/", r"(?:^|/)tests?\.rs$", r"_tests?\.rs$"],
        declaration_names=[
            # const / static items:  pub const MAX: usize = 4;
            rf"^{_VIS}(?:const|static(?:\s+mut)?)\s+([A-Za-z_]\w*)\s*:",
            # macro_rules! name
            r"^macro_rules!\s*([A-Za-z_]\w*)",
            # mod name
            rf"^{_VIS}mod\s+([A-Za-z_]\w*)",
        ],
    ),
    overview_types=JAVA_STYLE_OVERVIEW_TYPES | {"module_summary"},
    detail_types=JAVA_STYLE_DETAIL_TYPES | {"macro_definition", "macro_invocation", "macro_group", "extern_block"},
    binding_path_patterns=compile_all([r"(?:^|/)(?:ffi|sys)/", r"-sys/"]),
)

RustFileReader.rerank_profile = RERANK_PROFILE
