"""
Delphi/Pascal file reader (.pas, .dpr) using Tree-sitter AST.

Chunking strategy — class-context-aware with intelligent grouping:

1. **Context prefix on every chunk**: Each chunk starts with a comment block
   identifying the unit name and (if applicable) the owning class, so every
   chunk is self-describing for RAG search.

2. **Class summary chunk (P0)**: For each ``declClass``, emit a dedicated
   chunk containing the class header line (``TFoo = class(TBar)``) plus all
   ``declSection`` declarations (the interface overview).  This answers
   "what is TFoo and what can it do?".

3. **Leaf/container AST walk**: ``defProc``, ``declProc``, ``declSection``,
   ``declVar``, ``declConst``, and ``comment`` are leaf nodes (emitted as-is).
   ``declClass`` and ``declType`` are containers (recurse into children).

4. **Trivial method grouping (P1)**: Consecutive ``defProc`` nodes whose
   bodies are ≤ TRIVIAL_METHOD_LINES lines get grouped into a single
   "method_group" chunk.  This collapses 500 getter/setter chunks into
   ~10-20 grouped chunks while preserving BM25 keyword searchability.

5. **Uses clause (P5)**: ``declUses`` nodes are emitted as chunks so that
   module dependency information is indexed.

6. **Oversized splitting**: Chunks exceeding MAX_CHUNK_CHARS are split with
   TokenTextSplitter.  Small chunks (< MIN_CHUNK_SIZE) are discarded.
"""

import re
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

_parser = get_parser("pascal")


# ────────────────────────────────────────────────
# AST helper functions
# ────────────────────────────────────────────────


def _get_unit_name(root: Node, content_bytes: bytes) -> Optional[str]:
    """Extract the unit/program/library name from the root AST node."""
    for child in root.children:
        if child.type in ("unit", "program", "library"):
            for sub in child.children:
                if sub.type == "moduleName":
                    return (
                        content_bytes[sub.start_byte : sub.end_byte]
                        .decode("utf-8", errors="replace")
                        .strip()
                    )
    return None


def _get_class_header(decl_type_node: Node, content_bytes: bytes) -> Optional[str]:
    """Extract 'TClassName = class(TParent)' from a declType node.

    The AST structure is: declType > [identifier, kEq, declClass, ;]
    where declClass > [kClass, (, typeref, ), ...sections..., kEnd].
    We want just the first line: the class name, '=', and class(TParent).
    """
    identifier = None
    class_part = None

    for child in decl_type_node.children:
        if child.type == "identifier" and identifier is None:
            identifier = (
                content_bytes[child.start_byte : child.end_byte]
                .decode("utf-8", errors="replace")
                .strip()
            )
        elif child.type in ("declClass", "declIntf"):
            # Get just the first line of the class/interface declaration
            full_text = content_bytes[child.start_byte : child.end_byte].decode(
                "utf-8", errors="replace"
            )
            # Take up to the first newline (the class(...) part)
            first_line = full_text.split("\n")[0].strip()
            class_part = first_line

    if identifier and class_part:
        return f"{identifier} = {class_part}"
    return None


def _get_class_name_from_decl_type(
    decl_type_node: Node, content_bytes: bytes
) -> Optional[str]:
    """Extract just the class/interface name (e.g. 'TdmMain') from a declType."""
    for child in decl_type_node.children:
        if child.type == "identifier":
            return (
                content_bytes[child.start_byte : child.end_byte]
                .decode("utf-8", errors="replace")
                .strip()
            )
    return None


def _get_class_name_from_def_proc(node: Node, content_bytes: bytes) -> Optional[str]:
    """Extract class name from a defProc like 'procedure TMyClass.DoStuff'.

    AST: defProc > declProc > genericDot > [identifier(TMyClass), kDot, identifier(Method)]
    """
    for child in node.children:
        if child.type == "declProc":
            for sub in child.children:
                if sub.type == "genericDot":
                    for gchild in sub.children:
                        if gchild.type == "identifier":
                            return (
                                content_bytes[gchild.start_byte : gchild.end_byte]
                                .decode("utf-8", errors="replace")
                                .strip()
                            )
    return None


def _get_node_text(node: Node, content_bytes: bytes) -> str:
    """Extract text content from an AST node."""
    return (
        content_bytes[node.start_byte : node.end_byte]
        .decode("utf-8", errors="replace")
        .strip()
    )


def _count_body_lines(node: Node) -> int:
    """Count the number of source lines in a defProc body.

    Returns the total line span of the node.
    """
    return node.end_point[0] - node.start_point[0] + 1


def _build_class_index(root: Node, content_bytes: bytes) -> Dict[str, str]:
    """Build a mapping from class name -> class header line.

    Walks the AST looking for declType nodes containing declClass or declIntf.
    Returns e.g. {'TdmMain': 'TdmMain = class(TDataModule)', ...}
    """
    index: Dict[str, str] = {}

    def walk(node: Node) -> None:
        if node.type == "declType":
            name = _get_class_name_from_decl_type(node, content_bytes)
            header = _get_class_header(node, content_bytes)
            if name and header:
                index[name] = header
            # Don't recurse into declType children for more declTypes
            # (they don't nest this way in Pascal)
            return
        for child in node.children:
            walk(child)

    walk(root)
    return index


def _build_context_prefix(
    unit_name: Optional[str],
    file_name: str,
    class_name: Optional[str] = None,
    class_header: Optional[str] = None,
) -> str:
    """Build a context prefix comment for chunk self-identification.

    Examples:
        // Unit: MainDM (MainDM.pas)
        // Class: TdmMain = class(TDataModule)

        // Unit: Splash (Splash.pas)
    """
    parts = []
    display_name = unit_name or Path(file_name).stem
    parts.append(f"// Unit: {display_name} ({file_name})")
    if class_name and class_header:
        parts.append(f"// Class: {class_header}")
    elif class_name:
        parts.append(f"// Class: {class_name}")

    return "\n".join(parts)


# Pascal keywords that indicate commented-out code when found at the
# start of a comment line (after stripping the // or { prefix).
_COMMENTED_OUT_CODE_KEYWORDS = re.compile(
    r"^(?:"
    r"function\s|procedure\s|begin\b|end[;.]|end\b|Result\s*:=|"
    r"if\s|else\b|var\b|for\s|while\s|repeat\b|until\b|"
    r"try\b|except\b|finally\b|raise\b|"
    r"inherited\b|exit\b|Break\b|Continue\b|"
    r"OutputDebugString|ShowMessage|"
    r"\w+\s*:=|"  # assignment
    r"\w+\.\w+\s*:=|"  # qualified assignment
    r"\w+\.\w+\(|"  # method call
    r"\w+\.\w+\.\w+|"  # dotted expression
    r"FreeAndNil\(|\.Free\b"
    r")",
    re.IGNORECASE,
)


def _is_commented_out_code(text: str) -> bool:
    """Detect if a comment block is primarily commented-out Pascal code.

    Returns True if more than 50% of non-empty lines look like code.
    This is used to skip commented-out code blocks that pollute search
    results — they match BM25 keywords but provide no useful context.
    """
    lines = text.strip().splitlines()
    if not lines:
        return False

    code_lines = 0
    total_lines = 0
    for line in lines:
        # Strip comment prefix: // or { } or (* *)
        stripped = line.strip()
        if stripped.startswith("//"):
            stripped = stripped[2:].strip()
        elif stripped.startswith("{"):
            stripped = stripped[1:].rstrip("}").strip()
        elif stripped.startswith("(*"):
            stripped = stripped[2:].rstrip("*)").strip()

        if not stripped:
            continue
        total_lines += 1

        if _COMMENTED_OUT_CODE_KEYWORDS.match(stripped):
            code_lines += 1

    if total_lines < 3:
        return False  # Too few lines to judge reliably
    return code_lines / total_lines > 0.5


# ────────────────────────────────────────────────
# Reader class
# ────────────────────────────────────────────────


class DelphiFileReader(BaseFileReader):
    """Semantic chunking for Delphi Pascal files using Tree-sitter AST.

    Produces self-describing chunks with context prefixes, class summary
    chunks, uses clause chunks, and grouped trivial methods.
    """

    # All AST node types we recognise as potential chunks.
    NODE_TYPES = {
        "declProc",
        "defProc",
        "declClass",
        "declVar",
        "declSection",
        "declConst",
        "declType",
        "declUses",
        "comment",
    }

    # Leaf-like node types: always emit as-is, never decompose into children.
    LEAF_NODE_TYPES = {
        "defProc",  # procedure/function implementation (with body)
        "declProc",  # procedure/function forward declaration
        "declSection",  # visibility section (private/public/published/protected)
        "declVar",  # var block (top-level or inside a procedure)
        "declConst",  # const block
        "declUses",  # uses clause (interface or implementation)
        "comment",  # comment block
    }

    # Container node types: only emit if no matched descendants exist.
    CONTAINER_NODE_TYPES = {
        "declClass",  # class declaration
        "declType",  # type block
    }

    MIN_CHUNK_SIZE = 20  # Discard chunks smaller than this (chars)
    MAX_CHUNK_CHARS = 24000  # ~6000 tokens -- split oversized chunks
    MAX_SUMMARY_CHARS = 6000  # Max chars before splitting class_summary chunks.
    # Large classes (TdmMain ~19K, TfrmMainTurdus ~22K) produce zero-vector
    # embeddings when kept as a single chunk -- the model can't embed 19K+
    # chars of field declarations into a meaningful 768-dim vector.
    TRIVIAL_METHOD_LINES = 6  # defProc bodies <= this many lines are "trivial"
    MAX_GROUP_CHARS = 8000  # Max chars for a grouped trivial-method chunk
    # Tiny declSection chunks (raw content < this many chars, excluding
    # context prefix) are suppressed when a class_summary chunk already
    # covers them.  These produce degenerate embeddings that rank #1 on
    # every query with score≈0.5 (BUG 3 in AGENTS.md evaluation).
    MIN_DECL_SECTION_CHARS = 200
    # Minimum raw comment text length (before context prefix) to emit as
    # a standalone chunk.  Bare number comments like "// 46" (5 chars) get
    # inflated by the context prefix (~46 chars) and pass MIN_CHUNK_SIZE,
    # then rank high in BM25 because the prefix contains the file name.
    MIN_COMMENT_CHARS = 40

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
            max_chars: Override MAX_CHUNK_CHARS for this call. Used for
                class_summary chunks which need a lower threshold (6K)
                to avoid zero-vector embeddings on large classes.
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

        # For class_summary splits, extract the context prefix (lines
        # starting with "//") so we can re-prepend it to every split part.
        # Without this, only split_part=0 inherits the class name, making
        # parts 1-N invisible to BM25 for class-name queries (Q1 fix).
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
            # Re-prepend context prefix to split parts that lost it
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
        decl_type_node: Node,
        content_bytes: bytes,
        context_prefix: str,
    ) -> Optional[str]:
        """Build a class summary chunk: header + all declSection declarations.

        For a class like TdmMain, this produces:
            // Unit: MainDM (MainDM.pas)
            // Class: TdmMain = class(TDataModule)
            TdmMain = class(TDataModule)
              published
                cdsStoredProc...: TClientDataSet;
                ...
              private
                FTCPIPServerMethods: TObject;
                ...
              public
                function OpenConnection: boolean;
                ...
            end;
        """
        # Find the declClass or declIntf child
        decl_class = None
        for child in decl_type_node.children:
            if child.type in ("declClass", "declIntf"):
                decl_class = child
                break
        if not decl_class:
            return None

        # Get the full class declaration text (including all sections)
        full_text = _get_node_text(decl_type_node, content_bytes)
        if not full_text:
            return None

        return f"{context_prefix}\n{full_text}"

    def _build_class_overview(
        self,
        decl_type_node: Node,
        content_bytes: bytes,
        context_prefix: str,
        class_name: str,
    ) -> Optional[str]:
        """Build a compact class overview chunk for large classes.

        Unlike class_summary (full declaration, can be 20K+), this produces
        a concise overview (~500-2000 chars) containing:
        - A natural-language summary sentence describing the class
        - The class header (e.g. TdmMain = class(TDataModule))
        - Each visibility section with its member names (up to 20 per section)

        The natural-language sentence is critical for dense embedding: it gives
        the embedding model text semantically close to queries like
        "What is TdmMain?" — without it, the chunk is just a list of
        identifiers that embeds far from natural language questions.

        Only produced when the full class_summary exceeds MAX_SUMMARY_CHARS
        (i.e., when it would be split).  For small classes, the unsplit
        class_summary already serves this purpose.
        """
        # Find the declClass or declIntf child
        decl_class = None
        is_interface = False
        for child in decl_type_node.children:
            if child.type == "declClass":
                decl_class = child
                break
            elif child.type == "declIntf":
                decl_class = child
                is_interface = True
                break
        if not decl_class:
            return None

        class_header = _get_class_header(decl_type_node, content_bytes)
        if not class_header:
            return None

        # Extract parent class name from class header
        parent_class = None
        if "(" in class_header and ")" in class_header:
            paren_start = class_header.index("(")
            paren_end = class_header.index(")")
            parent_class = class_header[paren_start + 1 : paren_end].strip()

        MAX_MEMBERS_PER_SECTION = 20
        sections: List[str] = []

        # Track member counts by category for the summary sentence
        total_fields = 0
        total_methods = 0
        total_properties = 0
        section_summaries: List[str] = []  # e.g. "150 published fields"

        for child in decl_class.children:
            if child.type != "declSection":
                continue

            # Get visibility keyword (first child: kPublished, kPrivate, etc.)
            visibility = "unknown"
            for sub in child.children:
                if sub.type.startswith("k"):
                    vis_text = _get_node_text(sub, content_bytes).lower()
                    if vis_text in ("published", "private", "protected", "public"):
                        visibility = vis_text
                        break

            # Collect member names and count by category
            members: List[str] = []
            sec_fields = 0
            sec_methods = 0
            sec_properties = 0
            for sub in child.children:
                if sub.type in ("declProc", "declProcRef"):
                    text = _get_node_text(sub, content_bytes)
                    first_line = text.split("\n")[0].strip().rstrip(";")
                    members.append(f"  {first_line}")
                    sec_methods += 1
                elif sub.type == "declField":
                    text = _get_node_text(sub, content_bytes)
                    first_line = text.split("\n")[0].strip().rstrip(";")
                    members.append(f"  {first_line}")
                    sec_fields += 1
                elif sub.type in ("declVar", "declConst"):
                    text = _get_node_text(sub, content_bytes)
                    first_line = text.split("\n")[0].strip().rstrip(";")
                    members.append(f"  {first_line}")
                    sec_fields += 1
                elif sub.type == "declProp":
                    text = _get_node_text(sub, content_bytes)
                    first_line = text.split("\n")[0].strip().rstrip(";")
                    members.append(f"  {first_line}")
                    sec_properties += 1

            total_fields += sec_fields
            total_methods += sec_methods
            total_properties += sec_properties

            # Build per-section summary for the description
            sec_parts = []
            if sec_fields:
                sec_parts.append(f"{sec_fields} fields")
            if sec_methods:
                sec_parts.append(f"{sec_methods} methods")
            if sec_properties:
                sec_parts.append(f"{sec_properties} properties")
            if sec_parts:
                section_summaries.append(f"{visibility}: {', '.join(sec_parts)}")

            total = len(members)
            if total > MAX_MEMBERS_PER_SECTION:
                shown = members[:MAX_MEMBERS_PER_SECTION]
                shown.append(f"  ... ({total - MAX_MEMBERS_PER_SECTION} more members)")
                members = shown

            if members:
                section_text = f"  {visibility}\n" + "\n".join(members)
                sections.append(section_text)

        if not sections:
            return None

        # Build natural-language summary sentence
        kind = "interface" if is_interface else "class"
        inherits = f" inheriting from {parent_class}" if parent_class else ""
        member_parts = []
        if total_fields:
            member_parts.append(f"{total_fields} fields")
        if total_methods:
            member_parts.append(f"{total_methods} methods")
        if total_properties:
            member_parts.append(f"{total_properties} properties")
        member_desc = ", ".join(member_parts) if member_parts else "no members"

        # Section breakdown (e.g. "published: 150 fields; private: 60 methods")
        section_desc = "; ".join(section_summaries) if section_summaries else ""

        unit_name = (
            context_prefix.split("(")[0].split(":")[-1].strip()
            if ":" in context_prefix
            else ""
        )
        summary_sentence = (
            f"// {class_name} is a Delphi {kind}{inherits} "
            f"with {member_desc} ({section_desc})."
        )

        overview = (
            f"{context_prefix}\n"
            f"{summary_sentence}\n"
            f"{class_header}\n" + "\n".join(sections) + "\nend;"
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
        """Group consecutive trivial defProc nodes into combined chunks.

        Args:
            methods: List of (node, class_name_or_None) tuples for
                     consecutive trivial methods.
            content_bytes: Source file bytes.
            context_prefix: The context prefix for the owning class.
            file_path_str: File path string.
            file_datetime: File datetime dict.

        Returns:
            List of Documents (one per group).
        """
        if not methods:
            return []

        docs = []
        current_group: List[Node] = []
        current_chars = 0

        def flush_group() -> None:
            if not current_group:
                return
            texts = []
            for m in current_group:
                texts.append(_get_node_text(m, content_bytes))

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
            log_warn(f"Tree-sitter parse failed for {file}: {e}")
            # Try to extract unit_name from the raw text for the fallback
            fallback_unit = ""
            for line in content.split("\n")[:5]:
                stripped = line.strip()
                if stripped.lower().startswith("unit ") and stripped.endswith(";"):
                    fallback_unit = stripped[5:-1].strip()
                    break
            fallback_meta: dict = {
                "file_path": file_path_str,
                "node_type": "full_file",
                "parse_error": str(e),
                **file_datetime,
            }
            if fallback_unit:
                fallback_meta["unit_name"] = fallback_unit
            documents.append(
                Document(
                    text=content,
                    metadata=fallback_meta,
                )
            )
            return documents

        root = tree.root_node
        unit_name = _get_unit_name(root, content_bytes)
        class_index = _build_class_index(root, content_bytes)

        # Base prefix for chunks not inside a class
        base_prefix = _build_context_prefix(unit_name, file_name)

        # Track which declType nodes have had summaries emitted
        emitted_class_summaries: set = set()

        # Collect defProc nodes for grouping (keyed by class name)
        # We'll do a two-pass approach:
        # Pass 1: collect all leaf chunks from the AST
        # Pass 2: group trivial methods

        # ── Collect raw chunks from AST ──
        raw_chunks: List[Tuple[str, Node, str, str]] = []
        # Each entry: (node_type, node, context_prefix, class_name_or_empty)

        def _find_enclosing_class(node: Node) -> Optional[str]:
            """Walk up from a node to find the enclosing declType's class name."""
            # For defProc nodes in the implementation section, use genericDot
            if node.type == "defProc":
                return _get_class_name_from_def_proc(node, content_bytes)
            return None

        def traverse(node: Node, current_class: Optional[str] = None) -> None:
            """Walk the AST and collect chunks."""

            # ── declUses: emit uses clause ──
            if node.type == "declUses":
                chunk_text = _get_node_text(node, content_bytes)
                prefix = _build_context_prefix(unit_name, file_name)
                full_text = f"{prefix}\n{chunk_text}"
                raw_chunks.append(("declUses", node, full_text, ""))
                return

            # ── declType container: emit class summary + recurse ──
            if node.type == "declType":
                class_name = _get_class_name_from_decl_type(node, content_bytes)
                class_header = class_index.get(class_name or "", None)

                # Check if this declType contains a class/interface
                has_class_or_intf = any(
                    c.type in ("declClass", "declIntf") for c in node.children
                )

                if has_class_or_intf and class_name:
                    # Emit class summary chunk
                    class_prefix = _build_context_prefix(
                        unit_name, file_name, class_name, class_header
                    )
                    summary = self._build_class_summary(
                        node, content_bytes, class_prefix
                    )
                    if summary:
                        raw_chunks.append(
                            ("class_summary", node, summary, class_name or "")
                        )
                        emitted_class_summaries.add(class_name)

                        # Emit a compact class_overview chunk when the class
                        # summary is too large and will be split.  Split parts
                        # lose semantic coherence, so the overview provides a
                        # concise NL summary for "What is TClassName?" queries.
                        if len(summary) > self.MAX_SUMMARY_CHARS:
                            overview = self._build_class_overview(
                                node, content_bytes, class_prefix, class_name
                            )
                            if overview:
                                raw_chunks.append(
                                    (
                                        "class_overview",
                                        node,
                                        overview,
                                        class_name or "",
                                    )
                                )

                    # Recurse into children with class context
                    if self._has_matched_descendants(node):
                        for child in node.children:
                            traverse(child, current_class=class_name)
                    # If no matched descendants, the summary alone is enough
                    return

                # Non-class declType (e.g. type alias, record, enum)
                if self._has_matched_descendants(node):
                    for child in node.children:
                        traverse(child, current_class=current_class)
                else:
                    chunk_text = _get_node_text(node, content_bytes)
                    prefix = _build_context_prefix(
                        unit_name,
                        file_name,
                        current_class,
                        class_index.get(current_class or "", None),
                    )
                    full_text = f"{prefix}\n{chunk_text}"
                    raw_chunks.append(
                        ("declType", node, full_text, current_class or "")
                    )
                return

            # ── declClass container: recurse into sections ──
            if node.type == "declClass":
                # The class name comes from the parent declType, passed as current_class
                if self._has_matched_descendants(node):
                    for child in node.children:
                        traverse(child, current_class=current_class)
                else:
                    chunk_text = _get_node_text(node, content_bytes)
                    class_header = class_index.get(current_class or "", None)
                    prefix = _build_context_prefix(
                        unit_name, file_name, current_class, class_header
                    )
                    full_text = f"{prefix}\n{chunk_text}"
                    raw_chunks.append(
                        ("declClass", node, full_text, current_class or "")
                    )
                return

            # ── Leaf nodes: emit with context prefix ──
            if node.type in self.LEAF_NODE_TYPES:
                chunk_text = _get_node_text(node, content_bytes)

                # Skip tiny comment chunks that have no standalone semantic
                # value.  Without this, comments like "// 46" get inflated
                # by the context prefix and rank high in BM25 because the
                # prefix contains the file name (Q2 noise fix).
                if node.type == "comment" and len(chunk_text) < self.MIN_COMMENT_CHARS:
                    return

                # Skip commented-out code blocks.  These are large comment
                # blocks that contain Pascal code (assignments, begin/end,
                # procedure calls, etc.) left in the source as reference.
                # They pollute BM25 search because they match code keywords
                # but provide no useful context (Q2 cross-file noise fix).
                if node.type == "comment" and _is_commented_out_code(chunk_text):
                    return

                # Skip standalone comment chunks inside classes that already
                # have a class_summary.  The comment text is already included
                # in the class_summary (or class_summary_split parts), so
                # emitting it separately is pure duplication that competes
                # in search ranking (Q2 cross-file noise fix).
                if (
                    node.type == "comment"
                    and current_class
                    and current_class in emitted_class_summaries
                ):
                    return

                # Skip tiny declSection chunks whose class already has a
                # class_summary chunk.  These produce degenerate embeddings
                # that rank #1 on every query (BUG 3).
                if (
                    node.type == "declSection"
                    and current_class
                    and current_class in emitted_class_summaries
                    and len(chunk_text) < self.MIN_DECL_SECTION_CHARS
                ):
                    return

                # Determine class context
                effective_class = current_class
                if node.type == "defProc" and not effective_class:
                    effective_class = _get_class_name_from_def_proc(node, content_bytes)

                class_header = class_index.get(effective_class or "", None)
                prefix = _build_context_prefix(
                    unit_name, file_name, effective_class, class_header
                )
                full_text = f"{prefix}\n{chunk_text}"
                raw_chunks.append((node.type, node, full_text, effective_class or ""))
                return

            # ── Non-matched node: recurse into children ──
            for child in node.children:
                traverse(child, current_class=current_class)

        traverse(root)

        # ── Pass 2: Group trivial methods and emit all chunks ──
        # Process raw_chunks, grouping consecutive trivial defProc nodes
        # that share the same class name.
        i = 0
        while i < len(raw_chunks):
            node_type, node, full_text, class_name = raw_chunks[i]

            if node_type == "defProc":
                # Check if this is a trivial method
                line_count = _count_body_lines(node)
                if line_count <= self.TRIVIAL_METHOD_LINES:
                    # Collect consecutive trivial methods for same class
                    trivial_run: List[Tuple[Node, str]] = [(node, class_name)]
                    j = i + 1
                    while j < len(raw_chunks):
                        ntype, nnode, _, ncls = raw_chunks[j]
                        if (
                            ntype == "defProc"
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
                            unit_name,
                            file_name,
                            class_name if class_name else None,
                            class_header,
                        )
                        group_meta: dict = {}
                        if unit_name:
                            group_meta["unit_name"] = unit_name
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
                    # Not enough for a group — emit individually
                    # Fall through to single-chunk emit below

            # Single chunk emit -- class_summary uses lower max_chars
            # to avoid zero-vector embeddings on large classes
            emit_max = self.MAX_SUMMARY_CHARS if node_type == "class_summary" else None
            chunk_meta: dict = {}
            if unit_name:
                chunk_meta["unit_name"] = unit_name
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
            fallback_meta2: dict = {
                "file_path": file_path_str,
                "node_type": "full_file",
                **file_datetime,
            }
            if unit_name:
                fallback_meta2["unit_name"] = unit_name
            documents.append(
                Document(
                    text=content,
                    metadata=fallback_meta2,
                )
            )

        return documents
