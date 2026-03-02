from typing import List
from pathlib import Path
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

from shared.readers import DelphiFileReader, SQLFileReader, FastReportFR3Parser


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
    dfm_reader = SimpleDirectoryReader(
        input_dir="source",
        recursive=True,
        required_exts=[".dfm"],
    )
    dfm_docs = dfm_reader.load_data()
    print(f"      Loaded {len(dfm_docs)} .dfm documents")
    dfm_splitter = SentenceSplitter(chunk_size=800, chunk_overlap=100)
    dfm_nodes = dfm_splitter.get_nodes_from_documents(dfm_docs)
    print(f"      Created {len(dfm_nodes)} nodes")

    print("\n[3/6] Loading FastReport .fr3 files...")
    fr3_reader = SimpleDirectoryReader(
        input_dir="source", recursive=True, required_exts=[".fr3"]
    )
    fr3_raw_docs = fr3_reader.load_data()
    print(f"      Loaded {len(fr3_raw_docs)} .fr3 raw documents")

    fr3_docs: List[Document] = []
    for raw in fr3_raw_docs:
        path = raw.metadata.get("file_path", "")
        if path:
            fr3_docs.extend(fr3_parser.load(path))
    print(f"      Parsed {len(fr3_docs)} FR3 components")

    fr3_splitter = SentenceSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    fr3_nodes = fr3_splitter.get_nodes_from_documents(fr3_docs)
    print(f"      Created {len(fr3_nodes)} nodes")

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
