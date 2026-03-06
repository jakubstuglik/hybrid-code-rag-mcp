"""
Fallback text file reader for any plain-text file (.txt, .bat, .md, etc.).

Reads the entire file and applies SentenceSplitter chunking.
Use this for file types that don't have a dedicated AST-based parser.
"""

from pathlib import Path
from typing import List, Optional

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    node_from_doc,
    read_file_with_encoding,
)
from shared.log import log_warn


class TextFileReader(BaseFileReader):
    """Generic text file reader with sentence-based chunking."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        try:
            content = read_file_with_encoding(file)
        except Exception as e:
            log_warn(f"Failed to read {file}: {e}")
            return []

        if not content.strip():
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)

        return [
            Document(
                text=content,
                metadata={
                    "file_path": file_path_str,
                    "node_type": "full_file",
                    **file_datetime,
                },
            )
        ]

    def load_nodes(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[TextNode]:
        """Split file content into overlapping chunks."""
        docs = self.load_data(file, extra_info)
        if not docs:
            return []

        splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        all_nodes: List[TextNode] = []
        for doc in docs:
            base_nodes = [node_from_doc(doc)]
            split_nodes = splitter.get_nodes_from_documents(
                [Document(text=doc.text, metadata=doc.metadata)]
            )
            if split_nodes:
                for node in split_nodes:
                    node.metadata = {**doc.metadata, **node.metadata}
                all_nodes.extend(split_nodes)
            else:
                all_nodes.extend(base_nodes)

        return all_nodes
