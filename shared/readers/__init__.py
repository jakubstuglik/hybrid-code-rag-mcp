"""
Reader registry for the shared/readers package.

Maps file extensions to reader instances and exposes a single
`load_nodes_for_file()` entry point used by indexing code.

Adding a new reader:
    1. Create a new module in this directory implementing BaseFileReader.
    2. Import the class here and add it to READER_REGISTRY.
    No other files need to change.
"""

from pathlib import Path
from typing import Dict, List, Optional

from llama_index.core.schema import TextNode

from shared.readers._base import BaseFileReader
from shared.readers.pascal_reader import DelphiFileReader
from shared.readers.sql_reader import SQLFileReader
from shared.readers.dfm_reader import DFMFileReader
from shared.readers.dproj_reader import DPROJFileReader
from shared.readers.fr3_reader import FR3Reader

# ────────────────────────────────────────────────
# Extension → reader registry
# ────────────────────────────────────────────────

READER_REGISTRY: Dict[str, BaseFileReader] = {
    ".pas":   DelphiFileReader(),
    ".dpr":   DelphiFileReader(),
    ".sql":   SQLFileReader(),
    ".dfm":   DFMFileReader(),
    ".dproj": DPROJFileReader(),
    ".fr3":   FR3Reader(),
}


def get_reader(extension: str) -> Optional[BaseFileReader]:
    """Return the registered reader for a file extension, or None."""
    return READER_REGISTRY.get(extension.lower())


def load_nodes_for_file(
    file_info: dict,
    extra_info: Optional[dict] = None,
) -> List[TextNode]:
    """
    Load and parse a single file into TextNodes using the registry.

    Args:
        file_info: dict with keys:
            - "full_path"  – absolute path to the file on disk
            - "file_path"  – relative/normalised path stored in metadata
        extra_info: optional extra metadata forwarded to the reader

    Returns:
        List of TextNodes with "file_path" metadata set to the relative key.
    """
    full_path = Path(file_info["full_path"])
    relative_path = file_info["file_path"]

    reader = get_reader(full_path.suffix)
    if reader is None:
        return []

    nodes = reader.load_nodes(full_path, extra_info)

    for node in nodes:
        node.metadata["file_path"] = relative_path

    return nodes


__all__ = [
    # Registry API
    "READER_REGISTRY",
    "get_reader",
    "load_nodes_for_file",
    # Reader classes
    "BaseFileReader",
    "DelphiFileReader",
    "SQLFileReader",
    "DFMFileReader",
    "DPROJFileReader",
    "FR3Reader",
]
