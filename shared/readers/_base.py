"""
Base classes and shared utilities for all file readers.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from llama_index.core import Document
from llama_index.core.schema import TextNode


# ────────────────────────────────────────────────
# Shared file utilities
# ────────────────────────────────────────────────


def get_file_datetime(file_path: Path) -> dict:
    """Get file creation and modification datetimes."""
    stat = file_path.stat()
    return {
        "creation_datetime": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modification_datetime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def read_file_with_encoding(file: Path) -> str:
    """Try to read file with UTF-8, fallback to Windows-1250."""
    encodings = ["utf-8", "windows-1250", "cp1250", "latin-1"]
    for encoding in encodings:
        try:
            return file.read_text(encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return file.read_text(encoding="utf-8", errors="replace")


def read_file_with_encoding_and_bytes(file: Path) -> tuple[str, bytes]:
    """Read file text and return matching UTF-8 bytes."""
    encodings = ["utf-8", "windows-1250", "cp1250", "latin-1"]
    for encoding in encodings:
        try:
            text = file.read_text(encoding=encoding)
            return text, text.encode("utf-8")
        except (UnicodeDecodeError, UnicodeError):
            continue
    text = file.read_text(encoding="utf-8", errors="replace")
    return text, text.encode("utf-8")


def node_from_doc(doc: Document) -> TextNode:
    """Convert a Document to a TextNode, preserving metadata."""
    return TextNode(
        text=doc.text,
        metadata=doc.metadata,
    )


# ────────────────────────────────────────────────
# Base reader interface
# ────────────────────────────────────────────────


class BaseFileReader(ABC):
    """
    Unified interface for all file readers.

    Each reader must implement `load_data()` which returns raw Documents.
    The default `load_nodes()` converts those documents to TextNodes.
    Readers that need post-processing (e.g. sentence splitting) should
    override `load_nodes()`.
    """

    @abstractmethod
    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        """Parse a file and return a list of Documents."""
        ...

    def load_nodes(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[TextNode]:
        """
        Parse a file and return TextNodes ready for indexing.

        Default implementation wraps each Document into a TextNode.
        Override this method to apply splitters or other post-processing.
        """
        docs = self.load_data(file, extra_info)
        return [node_from_doc(doc) for doc in docs]
