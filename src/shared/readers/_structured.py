"""
Shared building blocks for the class/namespace-aware tree-sitter readers
added after the Java/Kotlin readers (Python, C#, Go, PHP).

The Java and Kotlin readers each carry their own copy of this logic.  The
newer readers use this module instead, so they all produce exactly the same
chunk layout and node types as Java/Kotlin, which is what the reranker in
``shared/reranker.py`` keys on:

* a **context prefix** on every chunk::

      // File: OrderService.cs
      // Namespace: Acme.Orders
      // Class: public partial class OrderService : BaseService

  (``#`` instead of ``//`` for Python, and the scope label is ``Package``,
  ``Namespace`` or ``Module`` depending on the language);
* ``class_summary`` (declaration header + member signatures, no bodies),
  ``class_overview`` (compact member list for large types), member chunks
  (``method_declaration``, ``constructor_declaration``, ``field_declaration``,
  ...), ``import_group``, ``block_comment`` and ``method_group`` for runs of
  trivial methods;
* oversized chunks split with ``TokenTextSplitter`` (``<type>_split``), with
  the context prefix re-prepended to every part of a split class summary.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter
from tree_sitter import Node

from shared.readers._base import BaseFileReader

METHOD_TYPES = ("method_declaration", "constructor_declaration")


def node_text(node: Node, content_bytes: bytes) -> str:
    """Source text of *node*, stripped."""
    return (
        content_bytes[node.start_byte : node.end_byte]
        .decode("utf-8", errors="replace")
        .strip()
    )


def collapse(text: str) -> str:
    """Collapse all whitespace runs to single spaces."""
    return " ".join(text.split())


def text_until(node: Node, content_bytes: bytes, stop: Optional[Node]) -> str:
    """Text of *node* up to (excluding) *stop*, collapsed to one line."""
    end = stop.start_byte if stop is not None else node.end_byte
    raw = content_bytes[node.start_byte : end].decode("utf-8", errors="replace")
    return collapse(raw).rstrip("{").rstrip(":").strip()


def line_count(node: Node) -> int:
    return node.end_point[0] - node.start_point[0] + 1


def nested_header(nesting: List[str], header: Optional[str]) -> Optional[str]:
    """``["Outer", "Inner"]`` + ``"class Inner"`` -> ``"Outer > class Inner"``."""
    if not header or len(nesting) <= 1:
        return header
    return " > ".join(nesting[:-1]) + " > " + header


def free_comment_block(node: Node, detached_next: tuple = ()) -> Optional[List[Node]]:
    """The run of adjacent comment nodes starting at *node*, if it stands alone.

    Grammars such as C#, Go and PHP emit one ``comment`` node per ``//`` line.
    Returns ``None`` when *node* is not the first comment of its run, or when
    the run sits directly above a declaration (it is that declaration's doc
    comment and is kept with it).  A following node whose type is in
    *detached_next* does not count as a declaration (e.g. Go's
    ``package_clause``).
    """
    prev = node.prev_sibling
    if prev is not None and prev.type == "comment" and prev.end_point[0] >= node.start_point[0] - 1:
        return None
    block = [node]
    nxt = node.next_sibling
    while nxt is not None and nxt.type == "comment" and nxt.start_point[0] <= block[-1].end_point[0] + 1:
        block.append(nxt)
        nxt = nxt.next_sibling
    if (
        nxt is not None
        and nxt.type not in detached_next
        and nxt.type not in ("{", "}")
        and nxt.start_point[0] <= block[-1].end_point[0] + 1
    ):
        return None
    return block


@dataclass
class RawChunk:
    """A chunk collected during the AST walk, before grouping/emission."""

    node_type: str
    text: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    class_name: str = ""
    lines: int = 1
    body: str = ""  # member text without prefix (used for method groups)
    extra: Dict = field(default_factory=dict)

    @classmethod
    def from_node(
        cls,
        node_type: str,
        node: Node,
        text: str,
        class_name: str = "",
        body: str = "",
        extra: Optional[dict] = None,
        start_node: Optional[Node] = None,
    ) -> "RawChunk":
        first = start_node or node
        return cls(
            node_type=node_type,
            text=text,
            start_line=first.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            start_byte=first.start_byte,
            end_byte=node.end_byte,
            class_name=class_name,
            lines=line_count(node),
            body=body,
            extra=dict(extra or {}),
        )


class StructuredReaderBase(BaseFileReader):
    """Common chunk emission for the Python, C#, Go and PHP readers."""

    COMMENT = "//"  # line-comment marker used in the context prefix
    SCOPE_LABEL = "Package"  # "Package" / "Namespace" / "Module"
    LANGUAGE = ""  # used in the class_overview sentence

    MIN_CHUNK_SIZE = 20  # Discard chunks smaller than this (chars)
    MAX_CHUNK_CHARS = 24000  # ~6000 tokens: split oversized chunks
    MAX_SUMMARY_CHARS = 6000  # class_summary split / overview threshold
    TRIVIAL_METHOD_LINES = 6  # methods <= this many lines are "trivial"
    MAX_GROUP_CHARS = 8000  # max chars of one method_group chunk
    MIN_COMMENT_CHARS = 40  # min chars of a standalone comment chunk
    MIN_GROUP_RUN = 3  # trivial methods needed to form a group
    MAX_OVERVIEW_MEMBERS = 20

    def __init__(self):
        super().__init__()
        self._text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=128)

    # -- prefix ---------------------------------------------------------

    def build_prefix(
        self,
        file_name: str,
        scope: Optional[str] = None,
        class_name: Optional[str] = None,
        class_header: Optional[str] = None,
    ) -> str:
        c = self.COMMENT
        parts = [f"{c} File: {file_name}"]
        if scope:
            parts.append(f"{c} {self.SCOPE_LABEL}: {scope}")
        if class_name or class_header:
            parts.append(f"{c} Class: {class_header or class_name}")
        return "\n".join(parts)

    def prefix_of(self, text: str) -> str:
        """The leading context-prefix lines of a chunk text."""
        c = self.COMMENT
        keys = (f"{c} File:", f"{c} {self.SCOPE_LABEL}:", f"{c} Class:")
        lines = []
        for ln in text.split("\n"):
            if not ln.startswith(keys):
                break
            lines.append(ln)
        return "\n".join(lines)

    # -- documents ------------------------------------------------------

    def make_documents(
        self,
        chunk: RawChunk,
        file_path_str: str,
        file_datetime: dict,
        base_meta: dict,
        max_chars: Optional[int] = None,
    ) -> List[Document]:
        text = chunk.text
        if len(text) < self.MIN_CHUNK_SIZE:
            return []
        threshold = max_chars if max_chars is not None else self.MAX_CHUNK_CHARS
        meta = {
            "file_path": file_path_str,
            "node_type": chunk.node_type,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "start_byte": chunk.start_byte,
            "end_byte": chunk.end_byte,
            **file_datetime,
        }
        meta.update(base_meta)
        if chunk.class_name:
            meta["class_name"] = chunk.class_name
        meta.update(chunk.extra)
        if len(text) <= threshold:
            return [Document(text=text, metadata=meta)]

        parts = self._text_splitter.split_text(text)
        prefix = self.prefix_of(text)
        docs = []
        for i, part in enumerate(parts):
            if len(part.strip()) < self.MIN_CHUNK_SIZE:
                continue
            body = part
            if prefix and not part.startswith(f"{self.COMMENT} File:"):
                body = f"{prefix}\n{part}"
            docs.append(
                Document(
                    text=body,
                    metadata={
                        **meta,
                        "node_type": f"{chunk.node_type}_split",
                        "split_part": i,
                        "split_total": len(parts),
                    },
                )
            )
        return docs

    def emit(
        self,
        raw: List[RawChunk],
        file_path_str: str,
        file_datetime: dict,
        base_meta: dict,
    ) -> List[Document]:
        """Group runs of trivial methods, then turn raw chunks into Documents."""
        documents: List[Document] = []
        i = 0
        while i < len(raw):
            ch = raw[i]
            if ch.node_type in METHOD_TYPES and ch.lines <= self.TRIVIAL_METHOD_LINES:
                j = i + 1
                while (
                    j < len(raw)
                    and raw[j].node_type in METHOD_TYPES
                    and raw[j].class_name == ch.class_name
                    and raw[j].lines <= self.TRIVIAL_METHOD_LINES
                ):
                    j += 1
                if j - i >= self.MIN_GROUP_RUN:
                    documents.extend(
                        self._group(raw[i:j], file_path_str, file_datetime, base_meta)
                    )
                    i = j
                    continue
            max_chars = self.MAX_SUMMARY_CHARS if ch.node_type == "class_summary" else None
            documents.extend(
                self.make_documents(ch, file_path_str, file_datetime, base_meta, max_chars)
            )
            i += 1
        return documents

    def _group(
        self,
        run: List[RawChunk],
        file_path_str: str,
        file_datetime: dict,
        base_meta: dict,
    ) -> List[Document]:
        prefix = self.prefix_of(run[0].text)
        docs: List[Document] = []
        group: List[RawChunk] = []
        chars = 0

        def flush() -> None:
            if not group:
                return
            text = (
                f"{prefix}\n{self.COMMENT} Method group: {len(group)} methods\n"
                + "\n\n".join(g.body for g in group)
            )
            chunk = RawChunk(
                node_type="method_group",
                text=text,
                start_line=group[0].start_line,
                end_line=group[-1].end_line,
                start_byte=group[0].start_byte,
                end_byte=group[-1].end_byte,
                class_name=group[0].class_name,
                extra={
                    **{k: v for k, v in group[0].extra.items() if k != "function_name"},
                    "group_count": len(group),
                },
            )
            docs.extend(self.make_documents(chunk, file_path_str, file_datetime, base_meta))

        for ch in run:
            if group and chars + len(ch.body) > self.MAX_GROUP_CHARS:
                flush()
                group = []
                chars = 0
            group.append(ch)
            chars += len(ch.body)
        flush()
        return docs

    # -- summaries ------------------------------------------------------

    def summary_text(
        self, prefix: str, header: str, members: List[str], open_: str = "{", close: str = "}"
    ) -> Optional[str]:
        """``prefix`` + ``header {`` + indented member lines + ``}``."""
        if not members:
            return None
        body = "\n".join(f"    {m}" for m in members)
        if close:
            return f"{prefix}\n{header} {open_}\n{body}\n{close}"
        return f"{prefix}\n{header}{open_}\n{body}"

    def overview_text(
        self,
        prefix: str,
        name: str,
        kind: str,
        header: str,
        inherits: str,
        sections: Dict[str, List[str]],
    ) -> str:
        """Compact natural-language overview of a large type.

        *sections* maps a plural label (``"fields"``, ``"methods"``...) to
        member names; empty sections are skipped.
        """
        counts = [f"{len(v)} {k}" for k, v in sections.items() if v]
        desc = ", ".join(counts) if counts else "no members"
        inh = f" {inherits}" if inherits else ""
        lang = f"{self.LANGUAGE} " if self.LANGUAGE else ""
        sentence = f"{self.COMMENT} {name} is a {lang}{kind}{inh} with {desc}."
        lines = []
        for label, names in sections.items():
            if not names:
                continue
            shown = names[: self.MAX_OVERVIEW_MEMBERS]
            line = f"  {label}: {', '.join(shown)}"
            if len(names) > self.MAX_OVERVIEW_MEMBERS:
                line += f" ... ({len(names) - self.MAX_OVERVIEW_MEMBERS} more)"
            lines.append(line)
        return f"{prefix}\n{sentence}\n{header} {{\n" + "\n".join(lines) + "\n}"

    @staticmethod
    def fallback_document(content: str, file_path_str: str, file_datetime: dict, base_meta: dict, **extra) -> Document:
        meta = {"file_path": file_path_str, "node_type": "full_file", **file_datetime}
        meta.update(base_meta)
        meta.update(extra)
        return Document(text=content, metadata=meta)


