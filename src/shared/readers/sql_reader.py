"""
SQL file reader (.sql) using Tree-sitter AST with a T-SQL heuristic chunker fallback.
"""

from pathlib import Path
from typing import List, Optional

from llama_index.core import Document
from tree_sitter import Node
from tree_sitter_language_pack import get_parser

from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding_and_bytes,
)
from shared.readers.tsql_chunker import chunk_tsql
from shared.log import log_warn

_parser = get_parser("sql")

# Node types that represent named SQL objects (CREATE PROCEDURE, CREATE TABLE, etc.)
_NAMED_OBJECT_TYPES = {
    "create_function",
    "create_procedure",
    "create_trigger",
    "create_view",
    "create_table",
}


class SQLFileReader(BaseFileReader):
    """Semantic chunking for SQL files using Tree-sitter AST, falling back to
    heuristic T-SQL chunking for unsupported dialects."""

    NODE_TYPES = {
        "create_function",
        "create_procedure",
        "create_trigger",
        "create_view",
        "create_table",
        "alter_table",
        "drop_table",
        "select",
        "statement",
        "set_statement",
        "create_index",
    }

    # Minimum size to consider a chunk "valid" (avoids keeping tiny fragments like SET X ON)
    MIN_CHUNK_SIZE = 50

    # If the file produces more than this many AST chunks, it means the parser fragmented it due to dialect mismatch (T-SQL)
    MAX_FRAGMENTATION_THRESHOLD = 15

    @staticmethod
    def _extract_object_name(node: Node, content_bytes: bytes) -> Optional[str]:
        """Extract the schema-qualified object name from a CREATE/ALTER AST node.

        Walks the immediate children looking for an identifier or
        dotted_name / schema_qualified_name.  Returns e.g.
        ``[dbo].[MyProc]`` or ``MyTable``, or None if not found.
        """
        # Heuristic: the object name is usually the first identifier-like
        # child after the keyword tokens (CREATE, PROCEDURE, etc.).
        for child in node.children:
            ctype = child.type
            # Common tree-sitter-sql name node types
            if ctype in (
                "identifier",
                "dotted_name",
                "object_reference",
                "schema_qualified_name",
            ):
                return (
                    content_bytes[child.start_byte : child.end_byte]
                    .decode("utf-8", errors="replace")
                    .strip()
                )
        return None

    def _fallback_split(self, content: str, metadata: dict) -> List[Document]:
        """Use the heuristic T-SQL chunker to split content semantically.

        This replaces the old TokenTextSplitter approach with structure-aware
        splitting that understands GO batches, procedure boundaries, dash
        separators, UNION ALL, dynamic SQL blocks, etc.
        """
        tsql_chunks = chunk_tsql(content)
        documents = []
        for chunk in tsql_chunks:
            chunk_metadata = {
                **metadata,
                "node_type": chunk.node_type,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
            }
            if chunk.object_name:
                chunk_metadata["object_name"] = chunk.object_name
            if chunk.object_type:
                chunk_metadata["object_type"] = chunk.object_type
            if chunk.parameters:
                chunk_metadata["parameters"] = chunk.parameters

            documents.append(Document(text=chunk.text, metadata=chunk_metadata))
        return documents

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents = []
        try:
            content, content_bytes = read_file_with_encoding_and_bytes(file)
        except Exception as e:
            log_warn(f"Failed to read {file}: {e}")
            return []

        if not content.strip():
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)

        base_metadata = {"file_path": file_path_str, **file_datetime}

        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            log_warn(f"Tree-sitter SQL parse failed for {file}: {e}")
            return self._fallback_split(content, base_metadata)

        # Check if the root node indicates a massive syntax error (common for T-SQL stored procedures)
        root = tree.root_node
        has_root_error = False
        for child in root.children:
            if child.type == "ERROR":
                has_root_error = True
                break

        if has_root_error:
            # If the parser couldn't understand the top-level structure, the dialect is unsupported.
            # Fall back to T-SQL heuristic chunking immediately.
            return self._fallback_split(content, base_metadata)

        def traverse(node: Node) -> None:
            # Check if this node is one of our target statements
            if node.type in self.NODE_TYPES:
                chunk_text = (
                    content_bytes[node.start_byte : node.end_byte]
                    .decode("utf-8", errors="replace")
                    .strip()
                )
                if len(chunk_text) >= self.MIN_CHUNK_SIZE:
                    chunk_meta = {
                        **base_metadata,
                        "node_type": node.type,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                    }
                    # Extract object name for named SQL objects
                    if node.type in _NAMED_OBJECT_TYPES:
                        obj_name = self._extract_object_name(node, content_bytes)
                        if obj_name:
                            chunk_meta["object_name"] = obj_name
                        # Derive object_type from node_type
                        # e.g. "create_procedure" -> "PROCEDURE"
                        chunk_meta["object_type"] = node.type.replace(
                            "create_", ""
                        ).upper()
                    documents.append(Document(text=chunk_text, metadata=chunk_meta))
                return  # Skip children to avoid duplicate nested chunks

            # Only traverse children if this wasn't a matched target statement
            for child in node.children:
                traverse(child)

        traverse(root)

        # If AST parsing fragmented the file into too many tiny unhelpful chunks (e.g. 40+ chunks for a single SP)
        if len(documents) > self.MAX_FRAGMENTATION_THRESHOLD:
            return self._fallback_split(content, base_metadata)

        # If we got valid AST chunks, return them!
        if documents:
            return documents

        # If AST parsing found nothing usable (or file is just small), return the whole file
        return [
            Document(
                text=content,
                metadata={
                    **base_metadata,
                    "node_type": "full_file",
                },
            )
        ]
