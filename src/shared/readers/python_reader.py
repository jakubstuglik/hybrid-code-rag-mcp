"""
Python file reader (.py) using Tree-sitter AST.

Chunking strategy — leaf/container pattern with context prefixes:

1. **Context prefix on every chunk**: Each chunk starts with a comment block
   identifying the module name and (if applicable) the owning class, so every
   chunk is self-describing for RAG search.

2. **Leaf/container AST walk**: ``function_definition``, ``decorated_definition``,
   ``import_statement``, ``import_from_statement``, ``assignment``, and
   ``expression_statement`` are leaf nodes (emitted as-is, never recursed into).
   ``class_definition`` is a container node (recurse into children if it has
   matched descendants, otherwise emit the whole class as one chunk).

3. **Oversized splitting**: Chunks exceeding MAX_CHUNK_CHARS are split with
   TokenTextSplitter.  Small chunks (< MIN_CHUNK_SIZE) are discarded.
"""

from pathlib import Path
from typing import List, Optional

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

_parser = get_parser("python")


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


def _get_class_name(node: Node, content_bytes: bytes) -> Optional[str]:
    """Extract the class name from a class_definition node.

    AST structure: class_definition > name: identifier, ...
    """
    for child in node.children:
        if child.type == "identifier":
            return (
                content_bytes[child.start_byte : child.end_byte]
                .decode("utf-8", errors="replace")
                .strip()
            )
    return None


def _get_class_from_decorated(node: Node, content_bytes: bytes) -> Optional[str]:
    """If a decorated_definition wraps a class_definition, return the class name."""
    for child in node.children:
        if child.type == "class_definition":
            return _get_class_name(child, content_bytes)
    return None


def _get_module_name(file: Path) -> str:
    """Derive a module display name from the file path.

    Returns the stem (e.g. 'index_rag' from 'index_rag.py').
    """
    return file.stem


def _build_context_prefix(
    module_name: str,
    file_name: str,
    class_name: Optional[str] = None,
) -> str:
    """Build a context prefix comment for chunk self-identification.

    Examples:
        # File: index_rag (index_rag.py)

        # File: pascal_reader (pascal_reader.py)
        # Class: DelphiFileReader
    """
    parts = [f"# File: {module_name} ({file_name})"]
    if class_name:
        parts.append(f"# Class: {class_name}")
    return "\n".join(parts)


# ────────────────────────────────────────────────
# Reader class
# ────────────────────────────────────────────────


class PythonFileReader(BaseFileReader):
    """Semantic chunking for Python files using Tree-sitter AST.

    Produces self-describing chunks with context prefixes.  Uses a
    leaf/container AST walk pattern: leaf nodes (functions, imports,
    assignments) are emitted as-is without recursion, while container
    nodes (class definitions) recurse into their children when matched
    descendants exist.
    """

    # Leaf node types: always emit as-is, never recurse into children.
    LEAF_NODE_TYPES = {
        "function_definition",
        "decorated_definition",
        "import_statement",
        "import_from_statement",
        "assignment",
        "expression_statement",
    }

    # Container node types: recurse if matched descendants exist,
    # otherwise emit the whole container as one chunk.
    CONTAINER_NODE_TYPES = {
        "class_definition",
    }

    # Union of both for convenience and backward compatibility.
    NODE_TYPES = LEAF_NODE_TYPES | CONTAINER_NODE_TYPES

    MIN_CHUNK_SIZE = 20  # Discard chunks smaller than this (chars)
    MAX_CHUNK_CHARS = 24000  # ~6000 tokens — split oversized chunks

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
    ) -> List[Document]:
        """Create Document(s) from a chunk, splitting if oversized.

        Chunks smaller than MIN_CHUNK_SIZE are discarded.
        Chunks larger than MAX_CHUNK_CHARS are split with TokenTextSplitter.
        """
        if len(chunk_text) < self.MIN_CHUNK_SIZE:
            return []

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

        if len(chunk_text) <= self.MAX_CHUNK_CHARS:
            return [Document(text=chunk_text, metadata=base_metadata)]

        # Oversized chunk: split with TokenTextSplitter
        parts = self._text_splitter.split_text(chunk_text)
        docs = []
        for i, part in enumerate(parts):
            if len(part.strip()) < self.MIN_CHUNK_SIZE:
                continue
            docs.append(
                Document(
                    text=part,
                    metadata={
                        **base_metadata,
                        "node_type": f"{node_type}_split",
                        "split_part": i,
                        "split_total": len(parts),
                    },
                )
            )
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
        module_name = _get_module_name(file)
        file_datetime = get_file_datetime(file)

        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            log_warn(f"Tree-sitter Python parse failed for {file}: {e}")
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "parse_error": str(e),
                        "module_name": module_name,
                        "unit_name": module_name,
                        **file_datetime,
                    },
                )
            )
            return documents

        # Base prefix for chunks not inside a class
        base_prefix = _build_context_prefix(module_name, file_name)

        def traverse(node: Node, current_class: Optional[str] = None) -> None:
            """Walk the AST using the leaf/container pattern."""

            # ── Leaf nodes: emit as-is, do NOT recurse ──
            if node.type in self.LEAF_NODE_TYPES:
                # Special case: a decorated_definition wrapping a class_definition
                # is actually a container — recurse like class_definition.
                if node.type == "decorated_definition":
                    inner_class_name = _get_class_from_decorated(node, content_bytes)
                    if inner_class_name is not None:
                        # Treat as container: recurse if has matched descendants
                        if self._has_matched_descendants(node):
                            for child in node.children:
                                traverse(child, current_class=current_class)
                        else:
                            chunk_text = _get_node_text(node, content_bytes)
                            prefix = _build_context_prefix(
                                module_name, file_name, current_class
                            )
                            full_text = f"{prefix}\n{chunk_text}"
                            documents.extend(
                                self._make_documents(
                                    full_text,
                                    node.type,
                                    node.start_point[0] + 1,
                                    node.end_point[0] + 1,
                                    node.start_byte,
                                    node.end_byte,
                                    file_path_str,
                                    file_datetime,
                                    extra_metadata={
                                        "module_name": module_name,
                                        "unit_name": module_name,
                                        **(
                                            {"class_name": current_class}
                                            if current_class
                                            else {}
                                        ),
                                    },
                                )
                            )
                        return

                chunk_text = _get_node_text(node, content_bytes)
                prefix = _build_context_prefix(module_name, file_name, current_class)
                full_text = f"{prefix}\n{chunk_text}"
                documents.extend(
                    self._make_documents(
                        full_text,
                        node.type,
                        node.start_point[0] + 1,
                        node.end_point[0] + 1,
                        node.start_byte,
                        node.end_byte,
                        file_path_str,
                        file_datetime,
                        extra_metadata={
                            "module_name": module_name,
                            "unit_name": module_name,
                            **({"class_name": current_class} if current_class else {}),
                        },
                    )
                )
                return  # Do NOT recurse into children

            # ── Container nodes: recurse if has matched descendants ──
            if node.type in self.CONTAINER_NODE_TYPES:
                class_name = _get_class_name(node, content_bytes)
                if self._has_matched_descendants(node):
                    for child in node.children:
                        traverse(child, current_class=class_name)
                else:
                    # No matched descendants — emit the whole container
                    chunk_text = _get_node_text(node, content_bytes)
                    prefix = _build_context_prefix(module_name, file_name, class_name)
                    full_text = f"{prefix}\n{chunk_text}"
                    documents.extend(
                        self._make_documents(
                            full_text,
                            node.type,
                            node.start_point[0] + 1,
                            node.end_point[0] + 1,
                            node.start_byte,
                            node.end_byte,
                            file_path_str,
                            file_datetime,
                            extra_metadata={
                                "module_name": module_name,
                                "unit_name": module_name,
                                **({"class_name": class_name} if class_name else {}),
                            },
                        )
                    )
                return

            # ── Non-matched node: recurse into children ──
            for child in node.children:
                traverse(child, current_class=current_class)

        traverse(tree.root_node)

        # Fallback: if no documents were produced at all
        if not documents:
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "module_name": module_name,
                        "unit_name": module_name,
                        **file_datetime,
                    },
                )
            )

        return documents
