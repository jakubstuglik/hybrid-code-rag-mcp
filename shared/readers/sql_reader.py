"""
SQL file reader (.sql) using Tree-sitter AST with a Text Splitter fallback.
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

_parser = get_parser("sql")


class SQLFileReader(BaseFileReader):
    """Semantic chunking for SQL files using Tree-sitter AST, falling back to text splitting for unsupported dialects like T-SQL."""

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

    def __init__(self):
        super().__init__()
        # Fallback splitter for files that fail AST parsing or fragment too heavily
        self.text_splitter = TokenTextSplitter(
            chunk_size=1024,
            chunk_overlap=128,
        )

    def _fallback_split(self, content: str, metadata: dict) -> List[Document]:
        """Use TokenTextSplitter to split the raw text intelligently."""
        # The splitter produces strings; we wrap them in Documents
        chunks = self.text_splitter.split_text(content)
        documents = []
        for chunk in chunks:
            if len(chunk.strip()) > self.MIN_CHUNK_SIZE:
                documents.append(
                    Document(
                        text=chunk,
                        metadata={**metadata, "node_type": "text_split_chunk"},
                    )
                )
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
            # Fall back to text splitting immediately.
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
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                **base_metadata,
                                "node_type": node.type,
                                "start_line": node.start_point[0] + 1,
                                "end_line": node.end_point[0] + 1,
                            },
                        )
                    )
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
