"""
Reader registry for the shared/readers package.

Maps file extensions to reader instances and exposes a single
`load_nodes_for_file()` entry point used by indexing code.

Supports **compound extensions** like ``.hbm.xml``: the registry
checks the last two suffixes (e.g. ``Path.suffixes[-2:]``) before
falling back to the final suffix.  This allows ``.hbm.xml`` to route
to a specialised reader while ``.xml`` falls through to the generic
text reader.

Adding a new reader:
    1. Create a new module in this directory implementing BaseFileReader.
    2. Import the class here and add it to READER_REGISTRY.
    No other files need to change.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from llama_index.core.schema import TextNode

from shared.readers._base import BaseFileReader
from shared.readers.pascal_reader import DelphiFileReader
from shared.readers.sql_reader import SQLFileReader
from shared.readers.dfm_reader import DFMFileReader
from shared.readers.dproj_reader import DPROJFileReader
from shared.readers.fr3_reader import FR3Reader
from shared.readers.python_reader import PythonFileReader
from shared.readers.java_reader import JavaFileReader
from shared.readers.js_reader import JSFileReader
from shared.readers.hbm_reader import HBMFileReader
from shared.readers.jrxml_reader import JRXMLFileReader
from shared.readers.text_reader import TextFileReader

# ────────────────────────────────────────────────
# Extension → reader registry
# ────────────────────────────────────────────────

_text_reader = TextFileReader()

READER_REGISTRY: Dict[str, BaseFileReader] = {
    # AST-based readers
    ".pas": DelphiFileReader(),
    ".dpr": DelphiFileReader(),
    ".sql": SQLFileReader(),
    ".py": PythonFileReader(),
    ".java": JavaFileReader(),
    ".js": JSFileReader(),
    ".ts": JSFileReader(),
    ".tsx": JSFileReader(),
    # Structured format readers
    ".dfm": DFMFileReader(),
    ".dproj": DPROJFileReader(),
    ".fr3": FR3Reader(),
    ".hbm.xml": HBMFileReader(),  # Compound extension — checked before ".xml"
    ".jrxml": JRXMLFileReader(),
    # Text/config readers (sentence-split chunking)
    ".bat": _text_reader,
    ".sh": _text_reader,
    ".txt": _text_reader,
    ".md": _text_reader,
    ".json": _text_reader,
    ".jsonc": _text_reader,
    ".yml": _text_reader,
    ".yaml": _text_reader,
    ".xml": _text_reader,
    ".jsp": _text_reader,
    ".html": _text_reader,
    ".htm": _text_reader,
    ".css": _text_reader,
    ".scss": _text_reader,
    ".properties": _text_reader,
    ".http": _text_reader,
    ".gradle": _text_reader,
    ".wsdl": _text_reader,
    ".xsd": _text_reader,
    ".cfg": _text_reader,
    ".ini": _text_reader,
    ".toml": _text_reader,
}


def get_reader(file_or_extension: Union[Path, str]) -> Optional[BaseFileReader]:
    """Return the registered reader, supporting compound extensions.

    Accepts either a ``Path`` object or a plain extension string.  When
    given a ``Path``, the last two suffixes are joined and checked first
    (e.g. ``Path("Foo.hbm.xml").suffixes[-2:]`` → ``".hbm.xml"``), then
    the final suffix alone (``".xml"``).  This lets compound extensions
    like ``.hbm.xml`` override single-extension fallbacks.
    """
    if isinstance(file_or_extension, Path):
        suffixes = file_or_extension.suffixes
        # Try compound extension first: ".hbm.xml" before ".xml"
        if len(suffixes) >= 2:
            compound = "".join(suffixes[-2:]).lower()
            reader = READER_REGISTRY.get(compound)
            if reader is not None:
                return reader
        # Fall back to final suffix
        if suffixes:
            return READER_REGISTRY.get(suffixes[-1].lower())
        return None
    # Backward compat: plain extension string (e.g. ".py")
    return READER_REGISTRY.get(file_or_extension.lower())


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

    reader = get_reader(full_path)
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
    "PythonFileReader",
    "JavaFileReader",
    "JSFileReader",
    "HBMFileReader",
    "JRXMLFileReader",
    "TextFileReader",
]
