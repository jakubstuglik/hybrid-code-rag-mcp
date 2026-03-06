"""
Delphi/Pascal file reader (.pas, .dpr) using Tree-sitter AST.
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

_parser = get_parser("pascal")


class DelphiFileReader(BaseFileReader):
    """Semantic chunking for Delphi Pascal files using Tree-sitter AST."""

    NODE_TYPES = {
        "declProc",
        "defProc",
        "declClass",
        "declVar",
        "declField",
        "declProp",
        "declSection",
        "declConst",
        "declType",
        "comment",
    }

    MIN_CHUNK_SIZE = 50

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents = []
        try:
            content, content_bytes = read_file_with_encoding_and_bytes(file)
        except Exception as e:
            print(f"Failed to read {file}: {e}")
            return []

        if not content.strip():
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)

        try:
            tree = _parser.parse(content_bytes)
        except Exception as e:
            print(f"Tree-sitter parse failed for {file}: {e}")
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "parse_error": str(e),
                        **file_datetime,
                    },
                )
            )
            return documents

        def traverse(node: Node) -> None:
            if node.type in self.NODE_TYPES:
                chunk_text = (
                    content_bytes[node.start_byte : node.end_byte]
                    .decode("utf-8", errors="replace")
                    .strip()
                )
                if len(chunk_text) > self.MIN_CHUNK_SIZE:
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": node.type,
                                "start_line": node.start_point[0] + 1,
                                "end_line": node.end_point[0] + 1,
                                "start_byte": node.start_byte,
                                "end_byte": node.end_byte,
                                **file_datetime,
                            },
                        )
                    )
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)

        if not documents:
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        **file_datetime,
                    },
                )
            )

        return documents
