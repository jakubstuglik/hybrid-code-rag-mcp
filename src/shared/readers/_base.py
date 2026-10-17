"""
Base classes and shared utilities for all file readers.
"""

import json
import os
import re
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
# Identifier name decomposition
# ────────────────────────────────────────────────

# Generic abbreviations used in Pascal and SQL identifiers.
# Upper-case keys match any casing of an identifier part; other keys match
# case-sensitively.  Project-specific prefixes and words (for example
# module prefixes or non-English table names) do not belong here: put them
# in a JSON object file and point ``HCR_ABBREVIATIONS_FILE`` at it, or call
# ``register_abbreviations()`` from a private config.
_ABBREVIATION_MAP = {
    "REP": "Report",
    "RPT": "Report",
    "ORD": "Order",
    "INV": "Inventory",
    "PKG": "Package",
    "CFG": "Config",
    "MGR": "Manager",
    "MSG": "Message",
    "SVC": "Service",
    "FRM": "Form",
    "DM": "DataModule",
    "DB": "Database",
    "TBL": "Table",
    "COL": "Column",
    "IDX": "Index",
    "PRC": "Procedure",
    "FNC": "Function",
    "PROC": "Procedure",
    "FUNC": "Function",
    "Export": "Export",
    "Import": "Import",
}

ABBREVIATIONS_FILE_ENV = "HCR_ABBREVIATIONS_FILE"


def register_abbreviations(mapping: dict) -> None:
    """Add project-specific abbreviation expansions (e.g. ``{"ACC": "Account"}``).

    Affects chunk descriptions produced after the call, so re-index the
    affected files (``--clear``) after changing the mapping.
    """
    for key, value in mapping.items():
        if isinstance(key, str) and isinstance(value, str) and key and value:
            _ABBREVIATION_MAP[key] = value


def _load_abbreviations_file() -> None:
    path = os.environ.get(ABBREVIATIONS_FILE_ENV)
    if not path:
        return
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return
    if isinstance(data, dict):
        register_abbreviations(data)


_load_abbreviations_file()

# Regex that splits on CamelCase boundaries.
# Handles: "ItemPrice" -> ["Item", "Price"], "XMLParser" -> ["XML", "Parser"]
_CAMEL_SPLIT_RE = re.compile(
    r"(?<=[a-z])(?=[A-Z])"  # aB -> a|B
    r"|(?<=[A-Z])(?=[A-Z][a-z])"  # ABc -> A|Bc
)

# Known Delphi T-prefix abbreviations that start lowercase.
# When an identifier starts with T + one of these, strip the T.
# E.g. "Tfrm" -> strip T -> "frm" -> expand to "Form"
_DELPHI_LOWER_PREFIXES = {"frm", "dm", "ds", "db", "tbl", "qry", "rpt"}


def decompose_identifier(name: str) -> str:
    """Decompose a code identifier into natural-language words.

    Handles CamelCase, underscore separation, Delphi T-prefix stripping,
    SQL schema prefix stripping (dbo.), and known abbreviation expansion.

    Examples:
        "TDataModule"  -> "Data Module"
        "INV_ItemPrice_GetPriceForCategory" -> "Inventory Item Price Get Price For Category"
        "RPT_DailyExport_Items_Get" -> "Report Daily Export Items Get"
        "dbo.INV_ItemPrice" -> "Inventory Item Price"
        "TfrmOrderForm" -> "Form Order Form"

    Returns:
        Space-separated words derived from the identifier.  Empty string
        if the input is empty or produces no meaningful words.
    """
    if not name:
        return ""

    # Strip schema prefix (dbo., sys., etc.)
    if "." in name:
        name = name.split(".")[-1]

    # Split on underscores first
    parts = name.split("_")

    words: List[str] = []
    for part in parts:
        if not part:
            continue

        # Check if the whole part is a known abbreviation (case-insensitive keys)
        upper = part.upper()
        if upper in _ABBREVIATION_MAP:
            words.append(_ABBREVIATION_MAP[upper])
            continue

        # Check case-sensitive keys (mixed-case words registered by a project)
        if part in _ABBREVIATION_MAP:
            words.append(_ABBREVIATION_MAP[part])
            continue

        # Strip Delphi T-prefix if this looks like a type name.
        # Two cases:
        # 1. T + uppercase letter (e.g. TDataModule, TForm)
        # 2. T + known lowercase abbreviation (e.g. Tfrm, Tdm)
        stripped = part
        if len(part) >= 2 and part[0] == "T" and not part.isupper():
            remainder = part[1:]
            if part[1].isupper():
                # Case 1: T + uppercase
                stripped = remainder
            else:
                # Case 2: check if remainder starts with known abbreviation
                remainder_lower = remainder.lower()
                for prefix in _DELPHI_LOWER_PREFIXES:
                    if remainder_lower.startswith(prefix):
                        stripped = remainder
                        break

        # CamelCase split
        camel_parts = _CAMEL_SPLIT_RE.split(stripped)
        for cp in camel_parts:
            if not cp:
                continue
            # Expand abbreviation if the camel part itself is known
            cp_upper = cp.upper()
            if cp_upper in _ABBREVIATION_MAP:
                words.append(_ABBREVIATION_MAP[cp_upper])
            elif cp in _ABBREVIATION_MAP:
                words.append(_ABBREVIATION_MAP[cp])
            else:
                words.append(cp)

    return " ".join(words)


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

    ``rerank_profile`` (a ``shared.rerank_profile.RerankProfile``) carries the
    reader's query-time ranking knowledge: which of its chunk types are
    overview/detail/import chunks, how its file names appear in queries, and
    any query domains.  ``None`` means the reader adds nothing beyond the
    generic reranker core.
    """

    rerank_profile = None

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
