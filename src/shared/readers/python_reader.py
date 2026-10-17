"""
Python file reader (.py, .pyi) using Tree-sitter AST.

Follows the Java/Kotlin chunk conventions (with ``#`` comments), so Python
chunks get the same node types and the same kind of self-describing header
as every other class-based language, and the reranker treats them alike:

    # File: reranker.py
    # Module: shared.reranker
    # Class: class OrderService(BaseService, metaclass=ABCMeta)

``# Module:`` is the dotted module path, found by walking up the directories
that contain an ``__init__.py`` (``src/shared/reranker.py`` ->
``shared.reranker``); a file outside any package uses its stem.

Chunking strategy:

1. **Class summary** (``class_summary``) for every class, including nested
   classes (``Outer > Inner``): decorators + ``class`` header, the first
   paragraph of the docstring, class attributes and the signatures of all
   methods (decorators, ``async``, parameters and return annotation, no
   bodies).  Large classes also get a compact ``class_overview``.
2. **Functions and methods** -> ``method_declaration`` (``__init__`` ->
   ``constructor_declaration``), with decorators and docstring.  Runs of three
   or more trivial methods (<= 6 lines: properties, dunder methods, stub
   ``...`` bodies in ``.pyi`` files) are grouped into one ``method_group``.
3. **Assignments**: consecutive module-level or class-level assignments are
   grouped into one chunk: ``constant_declaration`` when every target is
   UPPER_CASE, otherwise ``field_declaration``.
4. **Imports** (``import``, ``from ... import``, ``from __future__``) -> one
   ``import_group`` chunk per file.
5. **Module docstring** -> ``block_comment``; other top-level statements
   (``if __name__ == "__main__":``, ``try``/``if`` blocks, calls) -> one
   ``script_body`` chunk.
6. Oversized splitting and the ``full_file`` fallback work as in the Java
   reader.
"""

import dataclasses
import re
import textwrap
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
from shared.rerank_profile import java_style_profile, simple_stem_pattern

_parser = get_parser("python")

IMPORT_NODES = {"import_statement", "import_from_statement", "future_import_statement"}
_UPPER = re.compile(r"^_*[A-Z][A-Z0-9_]*$")
MAX_DOC_CHARS = 400


def module_path(file: Path) -> str:
    """Dotted module path of *file* (package dirs contain ``__init__.py``)."""
    parts = [] if file.stem == "__init__" else [file.stem]
    parent = file.parent
    try:
        while (parent / "__init__.py").exists() or (parent / "__init__.pyi").exists():
            parts.insert(0, parent.name)
            if parent.parent == parent:
                break
            parent = parent.parent
    except OSError:
        pass
    return ".".join(parts) or file.stem


def source_block(node: Node, content_bytes: bytes) -> str:
    """Text of *node* with the indentation of nested code removed.

    Methods start at a column > 0; tree-sitter text begins at the ``def``
    keyword while the following lines keep their class indentation, so the
    common indent is restored on the first line and removed from all lines.
    """
    text = node_text(node, content_bytes)
    col = node.start_point[1]
    if col == 0 or "\n" not in text:
        return text
    return textwrap.dedent(" " * col + text).strip("\n")


def _unwrap(node: Node) -> Node:
    """``decorated_definition`` -> the wrapped class/function definition."""
    if node.type == "decorated_definition":
        d = node.child_by_field_name("definition")
        if d is not None:
            return d
    return node


def _name(node: Node, content_bytes: bytes) -> Optional[str]:
    n = _unwrap(node).child_by_field_name("name")
    return node_text(n, content_bytes) if n is not None else None


def _decorators(node: Node, content_bytes: bytes) -> List[str]:
    if node.type != "decorated_definition":
        return []
    return [collapse(node_text(c, content_bytes)) for c in node.children if c.type == "decorator"]


def header(node: Node, content_bytes: bytes) -> str:
    """``@dataclass class A(B)`` / ``async def f(x: int) -> str``, no body."""
    d = _unwrap(node)
    sig = text_until(d, content_bytes, d.child_by_field_name("body"))
    return " ".join(_decorators(node, content_bytes) + [sig])


def docstring(defn: Node, content_bytes: bytes) -> Optional[str]:
    body = _unwrap(defn).child_by_field_name("body") if defn.type != "module" else defn
    if body is None:
        return None
    for c in body.children:
        if c.type == "comment":
            continue
        sn = _string_of(c)
        return node_text(sn, content_bytes) if sn is not None else None
    return None


def _doc_summary(doc: Optional[str]) -> Optional[str]:
    """First paragraph of a docstring, capped at MAX_DOC_CHARS."""
    if not doc:
        return None
    text = doc.strip()
    for q in ('"""', "'''", '"', "'"):
        if text.startswith(q) or text[1:].startswith(q) or text[2:].startswith(q):
            text = text.lstrip("rRbBuUfF").strip(q[0])
            break
    para = text.strip().split("\n\n")[0]
    para = collapse(para)
    if len(para) > MAX_DOC_CHARS:
        para = para[:MAX_DOC_CHARS].rsplit(" ", 1)[0] + " ..."
    return para or None


_ASSIGN = ("assignment", "augmented_assignment")


def _assignments(stmt: Node) -> List[Node]:
    """Assignment nodes of a statement (the grammar may or may not wrap them
    in ``expression_statement``)."""
    if stmt.type in _ASSIGN:
        return [stmt]
    if stmt.type == "expression_statement":
        return [c for c in stmt.children if c.type in _ASSIGN]
    return []


def _assignment_targets(stmt: Node, content_bytes: bytes) -> List[str]:
    names = []
    for c in _assignments(stmt):
        left = c.child_by_field_name("left")
        if left is not None:
            names.extend(re.findall(r"[A-Za-z_]\w*", node_text(left, content_bytes))[:3])
    return names


def _is_assignment(stmt: Node) -> bool:
    return bool(_assignments(stmt))


def _string_of(stmt: Node) -> Optional[Node]:
    """The string node of a bare string statement (docstring candidate)."""
    if stmt.type == "string":
        return stmt
    if stmt.type == "expression_statement" and len(stmt.children) == 1 and stmt.children[0].type == "string":
        return stmt.children[0]
    return None


def _is_docstring_stmt(stmt: Node) -> bool:
    return _string_of(stmt) is not None


class PythonFileReader(StructuredReaderBase):
    """Semantic chunking for Python files using Tree-sitter AST."""

    COMMENT = "#"
    SCOPE_LABEL = "Module"
    LANGUAGE = "Python"

    def _summary_members(self, body: Node, content_bytes: bytes) -> List[str]:
        members: List[str] = []
        for c in body.children:
            d = _unwrap(c)
            if d.type == "function_definition":
                members.append(header(c, content_bytes))
            elif d.type == "class_definition":
                members.append(f"{header(c, content_bytes)}: ...")
            elif _is_assignment(c):
                members.append(node_text(c, content_bytes).split("\n")[0].strip())
        return members

    def _overview(self, node: Node, body: Node, content_bytes: bytes, prefix: str, name: str) -> str:
        d = _unwrap(node)
        bases = d.child_by_field_name("superclasses")
        inherits = f"extends {collapse(node_text(bases, content_bytes))[1:-1]}" if bases is not None else ""
        sections = {"attributes": [], "constructors": [], "methods": [], "properties": [], "inner types": []}
        for c in body.children:
            u = _unwrap(c)
            n = _name(c, content_bytes)
            if u.type == "function_definition" and n:
                decos = " ".join(_decorators(c, content_bytes))
                if n == "__init__":
                    sections["constructors"].append(n)
                elif "@property" in decos or ".setter" in decos:
                    if n not in sections["properties"]:
                        sections["properties"].append(n)
                else:
                    sections["methods"].append(n)
            elif u.type == "class_definition" and n:
                sections["inner types"].append(n)
            elif _is_assignment(c):
                sections["attributes"].extend(_assignment_targets(c, content_bytes)[:1])
        return self.overview_text(prefix, name, "class", header(node, content_bytes), inherits, sections)

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
        module = module_path(file)
        base_meta: dict = {"module_name": module, "unit_name": file.stem}
        if "." in module:
            base_meta["package_name"] = module.rsplit(".", 1)[0]

        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            log_warn(f"Tree-sitter Python parse failed for {file}: {e}")
            return [self.fallback_document(content, file_path_str, file_datetime, base_meta, parse_error=str(e))]
        root = tree.root_node

        raw: List[RawChunk] = []
        imports: List[Node] = []
        script: List[Node] = []

        def prefix_for(nesting: List[str], hdr: Optional[str]) -> str:
            display = " > ".join(nesting) if nesting else None
            return self.build_prefix(file_name, module, display, nested_header(nesting, hdr))

        def flush_assignments(run: List[Node], nesting: List[str], hdr: Optional[str]) -> None:
            if not run:
                return
            names = [n for s in run for n in _assignment_targets(s, content_bytes)]
            nt = "constant_declaration" if names and all(_UPPER.match(n) for n in names) else "field_declaration"
            body = "\n".join(source_block(s, content_bytes) for s in run)
            cls = nesting[-1] if nesting else ""
            raw.append(
                RawChunk.from_node(nt, run[-1], f"{prefix_for(nesting, hdr)}\n{body}", cls, body=body, start_node=run[0])
            )
            run.clear()

        def walk_block(children: List[Node], nesting: List[str], hdr: Optional[str], top: bool) -> None:
            run: List[Node] = []
            for idx, c in enumerate(children):
                if _is_assignment(c):
                    run.append(c)
                    continue
                if c.type == "comment":
                    continue  # comments do not break a run of assignments
                flush_assignments(run, nesting, hdr)
                u = _unwrap(c)
                if c.type in IMPORT_NODES:
                    if top:
                        imports.append(c)
                    continue
                if u.type == "class_definition":
                    visit_class(c, nesting)
                elif u.type == "function_definition":
                    name = _name(c, content_bytes) or ""
                    body = source_block(c, content_bytes)
                    cls = nesting[-1] if nesting else ""
                    nt = "constructor_declaration" if (cls and name == "__init__") else "method_declaration"
                    extra = {"function_name": name} if name else {}
                    if c.type == "decorated_definition":
                        extra["decorators"] = _decorators(c, content_bytes)
                    raw.append(RawChunk.from_node(nt, c, f"{prefix_for(nesting, hdr)}\n{body}", cls, body=body, extra=extra))
                elif _is_docstring_stmt(c):
                    if top and idx == next((i for i, x in enumerate(children) if x.type != "comment"), -1):
                        txt = node_text(c, content_bytes)
                        if len(txt) >= self.MIN_COMMENT_CHARS:
                            raw.append(RawChunk.from_node("block_comment", c, f"{prefix_for([], None)}\n{txt}"))
                elif top and c.is_named:
                    script.append(c)
            flush_assignments(run, nesting, hdr)

        def visit_class(node: Node, nesting: List[str]) -> None:
            d = _unwrap(node)
            name = _name(node, content_bytes) or ""
            hdr = header(node, content_bytes)
            new_nesting = nesting + [name] if name else nesting
            prefix = prefix_for(new_nesting, hdr)
            body = d.child_by_field_name("body")
            members = self._summary_members(body, content_bytes) if body is not None else []
            doc = _doc_summary(docstring(node, content_bytes))
            lines = [f'"""{doc}"""'] if doc else []
            lines += members or ["..."]
            summary = f"{prefix}\n{hdr}:\n" + "\n".join(f"    {m}" for m in lines)
            extra = {"outer_class": nesting[-1]} if nesting else {}
            raw.append(RawChunk.from_node("class_summary", d, summary, name, extra=extra, start_node=node))
            if body is not None and len(summary) > self.MAX_SUMMARY_CHARS:
                ov = self._overview(node, body, content_bytes, prefix, " > ".join(new_nesting) or name)
                raw.append(RawChunk.from_node("class_overview", d, ov, name, extra=extra, start_node=node))
            if body is not None:
                walk_block(
                    [c for c in body.children if not _is_docstring_stmt(c) or c is not body.children[0]],
                    new_nesting, hdr, False,
                )

        walk_block(list(root.children), [], None, True)

        documents: List[Document] = []
        if imports:
            text = prefix_for([], None) + "\n" + "\n".join(node_text(i, content_bytes) for i in imports)
            chunk = RawChunk.from_node("import_group", imports[-1], text, start_node=imports[0])
            documents.extend(self.make_documents(chunk, file_path_str, file_datetime, base_meta))
        documents.extend(self.emit(raw, file_path_str, file_datetime, base_meta))
        if script:
            body = "\n".join(source_block(n, content_bytes) for n in script)
            chunk = RawChunk.from_node("script_body", script[-1], f"{prefix_for([], None)}\n{body}", start_node=script[0])
            documents.extend(self.make_documents(chunk, file_path_str, file_datetime, base_meta))
        if not documents:
            documents.append(self.fallback_document(content, file_path_str, file_datetime, base_meta))
        return documents


# ────────────────────────────────────────────────
# Rerank profile (query-time ranking knowledge, see shared/rerank_profile.py)
# ────────────────────────────────────────────────

RERANK_PROFILE = dataclasses.replace(
    java_style_profile(
        "python",
        simple_stem_pattern("pyi?"),
        # tests/ is a core rule; test_x.py, x_test.py, conftest.py
        test_paths=[r"(?:^|/)test_[^/]*\.pyi?$", r"_tests?\.pyi?$", r"(?:^|/)conftest\.py$"],
        # NAME = ..., name: Type = ...  (module constants, class attributes)
        declaration_names=[r"^([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=]+)?=(?!=)"],
    ),
    import_types=frozenset({"import_statement"}),
)

PythonFileReader.rerank_profile = RERANK_PROFILE
