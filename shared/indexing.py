from typing import List
from pathlib import Path
from llama_index.core import Document
from llama_index.core.schema import TextNode

from shared.readers import (
    DelphiFileReader,
    SQLFileReader,
    FastReportFR3Parser,
    DFMFileReader,
)


def node_from_doc(doc: Document) -> TextNode:
    """Convert a Document to a TextNode, preserving metadata."""
    return TextNode(
        text=doc.text,
        metadata=doc.metadata,
    )


def load_all_sources() -> tuple:
    """Load all source files and return nodes.

    Returns:
        tuple: (delphi_nodes, dfm_nodes, fr3_nodes, sql_nodes)
    """
    delphi_reader = DelphiFileReader()
    sql_reader = SQLFileReader()
    fr3_parser = FastReportFR3Parser()

    print("\n[1/6] Loading Delphi/Pascal files (.pas, .dpr)...")

    pascal_files = list(Path("source").rglob("*.pas")) + list(
        Path("source").rglob("*.dpr")
    )
    print(f"      Found {len(pascal_files)} Pascal files")
    delphi_docs: List[Document] = []
    for f in pascal_files:
        delphi_docs.extend(delphi_reader.load_data(f))
    print(f"      Loaded {len(delphi_docs)} Delphi documents")
    delphi_nodes = [node_from_doc(doc) for doc in delphi_docs]
    print(f"      Created {len(delphi_nodes)} nodes")

    print("\n[2/6] Loading Delphi .dfm files...")
    dfm_reader = DFMFileReader()
    dfm_files = list(Path("source").rglob("*.dfm"))
    print(f"      Found {len(dfm_files)} .dfm files")
    dfm_docs: List[Document] = []
    for f in dfm_files:
        dfm_docs.extend(dfm_reader.load_data(f))
    print(f"      Loaded {len(dfm_docs)} .dfm documents")
    dfm_nodes = [node_from_doc(doc) for doc in dfm_docs]
    print(f"      Created {len(dfm_nodes)} nodes")

    print("\n[3/6] Loading FastReport .fr3 files...")
    fr3_files = list(Path("source").rglob("*.fr3"))
    print(f"      Found {len(fr3_files)} .fr3 files")

    fr3_docs: List[Document] = []
    for f in fr3_files:
        fr3_docs.extend(fr3_parser.load(str(f)))
    print(f"      Created {len(fr3_docs)} nodes")
    fr3_nodes = [node_from_doc(doc) for doc in fr3_docs]

    print("\n[4/6] Loading SQL schema files...")
    sql_files = list(Path("schemas").rglob("*.sql"))
    print(f"      Found {len(sql_files)} SQL files")
    sql_docs: List[Document] = []
    for f in sql_files:
        sql_docs.extend(sql_reader.load_data(f))
    print(f"      Loaded {len(sql_docs)} SQL documents")
    sql_nodes = [node_from_doc(doc) for doc in sql_docs]
    print(f"      Created {len(sql_nodes)} nodes")

    return delphi_nodes, dfm_nodes, fr3_nodes, sql_nodes


def combine_nodes(delphi_nodes, dfm_nodes, fr3_nodes, sql_nodes) -> List[TextNode]:
    """Combine all nodes into a single list."""
    print("\n[5/6] Combining all nodes...")
    all_nodes = delphi_nodes + dfm_nodes + fr3_nodes + sql_nodes
    print(f"      Total nodes: {len(all_nodes)}")
    return all_nodes
