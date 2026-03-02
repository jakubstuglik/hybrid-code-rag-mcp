# index_delphi_chroma.py
# Full recursive indexer for Delphi project + SQL + Docs + FastReport .fr3
# Windows compatible - February 2026 style

import os
import sys
import json
import hashlib

os.environ["TORCHVISION_DISABLE_META_REGISTRATIONS"] = "1"

from pathlib import Path
from typing import List, Any, Optional, Dict

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Document,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import CodeSplitter, SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.core.readers.base import BaseReader
import chromadb
import argparse

import config


# ────────────────────────────────────────────────
# Manifest Functions
# ────────────────────────────────────────────────


def get_manifest_path() -> Path:
    """Get path to manifest file (in same directory as index)."""
    index_path = Path(config.INDEX_PATH).resolve()
    return index_path / "index_manifest.json"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"      Warning: Could not hash {file_path}: {e}")
        return ""


def get_source_files() -> List[Path]:
    """Get all source files that should be indexed."""
    source_extensions = [".pas", ".dpr", ".dfm", ".fr3", ".sql"]
    files = []

    if Path("source").exists():
        for ext in source_extensions:
            files.extend(Path("source").rglob(f"*{ext}"))

    if Path("schemas").exists():
        files.extend(Path("schemas").rglob("*.sql"))

    return sorted(files)


def load_manifest() -> Optional[Dict]:
    """Load existing manifest or return None."""
    manifest_path = get_manifest_path()
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_manifest(manifest: Dict) -> None:
    """Save manifest to disk."""
    manifest_path = get_manifest_path()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def regenerate_manifest_from_index() -> None:
    """Generate manifest from existing Chroma index."""
    print("\n[REGENERATE MANIFEST] Connecting to existing index...")

    db = chromadb.PersistentClient(path=config.INDEX_PATH)
    collection = db.get_or_create_collection(config.COLLECTION_NAME)

    total_count = collection.count()
    print(f"      Found {total_count} documents in collection")

    manifest: Dict = {"files": {}}
    seen_files: set = set()  # Only keep unique file paths

    # Use pagination to avoid "too many SQL variables" error
    batch_size = 1000
    for offset in range(0, total_count, batch_size):
        results = collection.get(limit=batch_size, offset=offset)

        if results and results.get("ids"):
            ids = results["ids"]
            metadatas = results.get("metadatas") or []
            for idx, chroma_id in enumerate(ids):
                metadata = metadatas[idx] if idx < len(metadatas) else {}
                file_path = (
                    metadata.get("file_path", "") if isinstance(metadata, dict) else ""
                )

                # Only process each file once (first chunk)
                if file_path and file_path not in seen_files:
                    seen_files.add(file_path)
                    path = Path(file_path)
                    if path.exists():
                        file_hash = compute_file_hash(path)
                        manifest["files"][file_path] = {
                            "hash": file_hash,
                            "chroma_id": chroma_id,
                        }

        if (offset + batch_size) % 10000 == 0 or offset + batch_size >= total_count:
            print(
                f"      Processed {min(offset + batch_size, total_count)}/{total_count} documents..."
            )

    save_manifest(manifest)
    print(f"      Created manifest with {len(manifest['files'])} unique files")


def fix_absolute_paths() -> None:
    """Fix absolute paths in Chroma DB to relative paths."""
    print("\n[FIX PATHS] Connecting to existing index...")

    # Get resolved paths for source and schemas directories
    source_dir = Path("source").resolve()
    schemas_dir = Path("schemas").resolve()

    print(f"      source dir: {source_dir}")
    print(f"      schemas dir: {schemas_dir}")

    db = chromadb.PersistentClient(path=config.INDEX_PATH)
    collection = db.get_or_create_collection(config.COLLECTION_NAME)

    total_count = collection.count()
    print(f"      Found {total_count} documents in collection")

    batch_size = 100
    total_fixed = 0

    for offset in range(0, total_count, batch_size):
        results = collection.get(limit=batch_size, offset=offset)

        if results and results.get("ids"):
            ids = results["ids"]
            metadatas = results.get("metadatas") or []

            for idx, chroma_id in enumerate(ids):
                metadata = metadatas[idx] if idx < len(metadatas) else {}

                if not isinstance(metadata, dict):
                    continue

                file_path = metadata.get("file_path", "")

                if not file_path:
                    continue

                path = Path(file_path)

                # Check if it's an absolute path and convert to relative
                if path.is_absolute():
                    try:
                        # Try to make relative to source or schemas
                        if path.is_relative_to(source_dir):
                            rel_path = "source" / path.relative_to(source_dir)
                            new_path = str(rel_path)
                            metadata["file_path"] = new_path
                            collection.update(ids=[chroma_id], metadatas=[metadata])
                            total_fixed += 1
                        elif path.is_relative_to(schemas_dir):
                            rel_path = "schemas" / path.relative_to(schemas_dir)
                            new_path = str(rel_path)
                            metadata["file_path"] = new_path
                            collection.update(ids=[chroma_id], metadatas=[metadata])
                            total_fixed += 1
                    except (ValueError, OSError):
                        # Path is not relative to source or schemas
                        pass

        if (offset + batch_size) % 10000 == 0 or offset + batch_size >= total_count:
            print(
                f"      Processed {min(offset + batch_size, total_count)}/{total_count} documents..."
            )

    print(f"      Fixed {total_fixed} absolute paths to relative paths")


# ────────────────────────────────────────────────
# CLI Argument Parsing
# ────────────────────────────────────────────────

parser = argparse.ArgumentParser(description="Informica RAG Indexer")
parser.add_argument(
    "--regenerate-manifest",
    action="store_true",
    help="Regenerate manifest from existing index (one-time bootstrap)",
)
parser.add_argument(
    "--fix-paths",
    action="store_true",
    help="Fix absolute paths in Chroma DB to relative paths",
)
parser.add_argument(
    "--force-full-index",
    action="store_true",
    help="Force full re-indexing (WARNING: requires confirmation)",
)
args = parser.parse_args()

# Handle --regenerate-manifest first
if args.regenerate_manifest:
    regenerate_manifest_from_index()
    sys.exit(0)

# Handle --fix-paths
if args.fix_paths:
    fix_absolute_paths()
    sys.exit(0)

# Check manifest for refresh mode
manifest = load_manifest()

if manifest is None:
    # No manifest - do full indexing
    print("\n[INFO] No manifest found - performing full indexing")
    mode = "full"
elif args.force_full_index:
    # User requested full re-index - require confirmation
    print(
        "\n[WARNING] You are about to delete the existing index and rebuild from scratch!"
    )
    print("This will take a VERY LONG TIME and cannot be undone.")
    response = input("Type 'YES' to confirm full re-indexing: ")
    if response.strip() != "YES":
        print("Aborted. No changes made.")
        sys.exit(0)
    print("\n[INFO] Proceeding with full re-indexing...")
    # Delete existing index
    import shutil

    index_path = Path(config.INDEX_PATH)
    if index_path.exists():
        shutil.rmtree(index_path)
        print(f"      Deleted existing index at: {index_path}")
    # Remove manifest too so it gets regenerated
    manifest_path = get_manifest_path()
    if manifest_path.exists():
        manifest_path.unlink()
    mode = "full"
else:
    # Manifest exists - do refresh
    print("\n[INFO] Manifest found - running in refresh mode")
    mode = "refresh"


# ────────────────────────────────────────────────
# Tree-sitter (using tree-sitter-language-pack)
# ────────────────────────────────────────────────
from tree_sitter import Parser, Node
from tree_sitter_language_pack import get_language, get_parser

PASCAL_LANGUAGE = get_language("pascal")
parser_global = get_parser("pascal")  # pre-configured Parser

SQL_LANGUAGE = get_language("sql")
sql_parser = get_parser("sql")


def node_from_doc(doc: Document) -> TextNode:
    """Convert a Document to a TextNode, preserving metadata."""
    return TextNode(
        text=doc.text,
        metadata=doc.metadata,
    )


def read_file_with_encoding(file: Path) -> str:
    """Try to read file with UTF-8, fallback to Windows-1250."""
    encodings = ["utf-8", "windows-1250", "cp1250", "latin-1"]
    for encoding in encodings:
        try:
            return file.read_text(encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return file.read_text(encoding="utf-8", errors="replace")


class DelphiFileReader(BaseReader):
    """Custom reader for Delphi Pascal files using Tree-sitter AST"""

    NODE_TYPES = {
        "declProc",  # procedure/function declarations
        "defProc",  # procedure/function with body
        "declClass",  # class declarations
        "declVar",  # variable declarations
        "declField",  # class fields
        "declProp",  # property declarations
        "declSection",  # interface/implementation sections
        "declConst",  # constants
        "declType",  # type declarations
        "comment",  # comments
    }

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents = []
        try:
            content = read_file_with_encoding(file)
        except Exception as e:
            print(f"Failed to read {file}: {e}")
            return []

        if not content.strip():
            return []

        try:
            tree = parser_global.parse(bytes(content, "utf8"))
        except Exception as e:
            print(f"Tree-sitter parse failed for {file}: {e}")
            return []

        file_path_str = str(file)

        def traverse(node: Node) -> None:
            node_type = node.type

            if node_type in self.NODE_TYPES:
                chunk_text = content[node.start_byte : node.end_byte].strip()
                if len(chunk_text) > 50:
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": node_type,
                                "start_line": node.start_point[0] + 1,
                                "end_line": node.end_point[0] + 1,
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
                    metadata={"file_path": file_path_str, "node_type": "full_file"},
                )
            )

        return documents


delphi_reader = DelphiFileReader()


class SQLFileReader(BaseReader):
    """Custom reader for SQL files using Tree-sitter AST"""

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

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents = []
        try:
            content = read_file_with_encoding(file)
        except Exception as e:
            print(f"Failed to read {file}: {e}")
            return []

        if not content.strip():
            return []

        try:
            tree = sql_parser.parse(bytes(content, "utf8"))
        except Exception as e:
            print(f"Tree-sitter SQL parse failed for {file}: {e}")
            return []

        file_path_str = str(file)

        def traverse(node: Node) -> None:
            # Skip ERROR nodes themselves
            if node.type == "ERROR":
                return

            node_type = node.type

            if node_type in self.NODE_TYPES:
                chunk_text = content[node.start_byte : node.end_byte].strip()
                if len(chunk_text) > 30:
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": node_type,
                                "start_line": node.start_point[0] + 1,
                                "end_line": node.end_point[0] + 1,
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
                    metadata={"file_path": file_path_str, "node_type": "full_file"},
                )
            )

        return documents


sql_reader = SQLFileReader()

# ────────────────────────────────────────────────
# FastReport .fr3 structured XML parser
# ────────────────────────────────────────────────
from xml.etree import ElementTree as ET


class FastReportFR3Parser:
    """Extracts scripts, memo texts, bands and dataset schemas from .fr3 files"""

    def load(self, file_path: str) -> List[Document]:
        documents = []
        content = None

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            root = ET.fromstring(content)
        except ET.ParseError as e:
            print(f"XML parse error for {file_path}: {e}")
            if content and len(content) > 0:
                documents.append(
                    Document(
                        text=content[:5000],
                        metadata={
                            "file_path": str(file_path),
                            "type": "raw_fr3",
                            "parse_error": str(e),
                        },
                    )
                )
            return documents
        except Exception as e:
            print(f"Could not read {file_path}: {e}")
            return []

        file_path_str = str(file_path)

        # 1. Report-level script - stored as root attribute
        script_text = root.get("ScriptText.Text", "")
        if script_text:
            import html

            decoded = html.unescape(script_text)
            if decoded.strip():
                documents.append(
                    Document(
                        text=decoded.strip(),
                        metadata={
                            "file_path": file_path_str,
                            "component": "Script",
                            "type": "pascal_script",
                        },
                    )
                )

        # 2. Variables
        for var in root.findall(".//Variable"):
            var_name = var.get("Name", "")
            var_value = var.get("Value", "")
            var_expression = var.get("Expression", "")
            if var_name or var_value or var_expression:
                doc_text = f"Variable: {var_name}"
                if var_value:
                    doc_text += f" = {var_value}"
                if var_expression:
                    doc_text += f" Expression: {var_expression}"
                documents.append(
                    Document(
                        text=doc_text,
                        metadata={"file_path": file_path_str, "type": "variable"},
                    )
                )

        # 3. DataSources
        for ds in root.findall(".//DataSource"):
            ds_name = ds.get("Name", "Unnamed")
            alias = ds.get("Alias", "")
            fields = [f.get("FieldName", "") for f in ds.findall(".//Field")]
            if ds_name:
                doc_text = f"DataSource: {ds_name}"
                if alias:
                    doc_text += f" Alias: {alias}"
                if fields:
                    doc_text += f" Fields: {', '.join(f for f in fields if f)}"
                documents.append(
                    Document(
                        text=doc_text,
                        metadata={"file_path": file_path_str, "type": "datasource"},
                    )
                )

        # 4. Datasets (legacy support)
        for ds in root.findall(".//DataSet"):
            ds_name = ds.get("Name", "Unnamed")
            fields: List[str] = [
                fname
                for f in ds.findall(".//Field")
                if (fname := f.get("FieldName")) is not None
            ]
            if fields:
                documents.append(
                    Document(
                        text=f"Dataset '{ds_name}' fields: {', '.join(fields)}",
                        metadata={"file_path": file_path_str, "type": "dataset_schema"},
                    )
                )

        # 5. Pages → Bands → Memos (extract all memo content + properties)
        for page in root.findall(".//Page"):
            page_name = page.get("Name", "UnnamedPage")
            page_obj = page.get("Obj", "")

            for band in page.findall(".//Band"):
                band_name = band.get("Name", "UnnamedBand")
                band_type = band.get("Type", "Unknown")

                # Extract band properties
                band_props = []
                for key, value in band.attrib.items():
                    if key not in ("Name", "Type") and value:
                        band_props.append(f"{key}={value}")
                band_desc = f"Band: {band_name} Type={band_type}"
                if band_props:
                    band_desc += " " + ", ".join(band_props[:5])

                # Extract all memos in this band
                memo_texts = []
                for memo in band.findall(".//Memo"):
                    memo_name = memo.get("Name", "")
                    memo_text = ""
                    text_elem = memo.find("Text")
                    if text_elem is not None and text_elem.text:
                        memo_text = text_elem.text.strip()
                    elif text_elem is not None:
                        memo_text = text_elem.text or ""

                    if memo_text:
                        memo_desc = f"Memo: {memo_name}" if memo_name else "Memo"
                        memo_texts.append(f"{memo_desc}: {memo_text}")
                    else:
                        # Still include memo with just properties if no text
                        if memo_name:
                            memo_texts.append(f"Memo: {memo_name}")

                if memo_texts:
                    documents.append(
                        Document(
                            text=band_desc + "\n" + "\n".join(memo_texts),
                            metadata={
                                "file_path": file_path_str,
                                "page": page_name,
                                "band": band_name,
                                "band_type": band_type,
                                "type": "band_content",
                            },
                        )
                    )
                else:
                    # Include band even if no memos - just properties
                    if band_desc:
                        documents.append(
                            Document(
                                text=band_desc,
                                metadata={
                                    "file_path": file_path_str,
                                    "page": page_name,
                                    "band": band_name,
                                    "band_type": band_type,
                                    "type": "band_empty",
                                },
                            )
                        )

        # 6. Report properties
        report_props = []
        for key in root.attrib:
            if key and root.get(key):
                report_props.append(f"{key}={root.get(key)}")
        if report_props:
            documents.append(
                Document(
                    text="Report: " + ", ".join(report_props[:10]),
                    metadata={"file_path": file_path_str, "type": "report_props"},
                )
            )

        # 7. If nothing extracted, add raw content
        if not documents and content:
            documents.append(
                Document(
                    text=content[:8000],
                    metadata={"file_path": file_path_str, "type": "raw_fr3"},
                )
            )

        return documents


fr3_parser = FastReportFR3Parser()

# ────────────────────────────────────────────────
# Embedding model & Chroma vector store
# ────────────────────────────────────────────────
embed_model = HuggingFaceEmbedding(
    model_name=config.MODEL_NAME,
    device=config.INDEX_EMBED_DEVICE,
    model_kwargs=config.EMBED_MODEL_KWARGS,
)

db = chromadb.PersistentClient(path=config.INDEX_PATH)
collection = db.get_or_create_collection(config.COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# ────────────────────────────────────────────────
# Load ALL sources — everything recursive
# ────────────────────────────────────────────────

print("\n[1/6] Loading Delphi/Pascal files (.pas, .dpr)...")

# 1. Delphi Pascal code (.pas, .dpr) - manually iterate to use custom reader
pascal_files = list(Path("source").rglob("*.pas")) + list(Path("source").rglob("*.dpr"))
print(f"      Found {len(pascal_files)} Pascal files")
delphi_docs: List[Document] = []
for f in pascal_files:
    delphi_docs.extend(delphi_reader.load_data(f))
print(f"      Loaded {len(delphi_docs)} Delphi documents")
# DelphiFileReader already chunks at semantic boundaries (procedures, functions, etc.)
# Just convert documents to nodes directly without re-splitting
delphi_nodes = [node_from_doc(doc) for doc in delphi_docs]
print(f"      Created {len(delphi_nodes)} nodes")

# 2. Delphi .dfm files (binary forms - read as text)
print("\n[2/6] Loading Delphi .dfm files...")
dfm_reader = SimpleDirectoryReader(
    input_dir="source",
    recursive=True,
    required_exts=[".dfm"],
)
dfm_docs = dfm_reader.load_data()
print(f"      Loaded {len(dfm_docs)} .dfm documents")
# DFM files are INI-like text, use SentenceSplitter
dfm_splitter = SentenceSplitter(chunk_size=800, chunk_overlap=100)
dfm_nodes = dfm_splitter.get_nodes_from_documents(dfm_docs)
print(f"      Created {len(dfm_nodes)} nodes")

# 3. FastReport .fr3 files
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

# Use SentenceSplitter for XML/FR3 content
fr3_splitter = SentenceSplitter(
    chunk_size=1000,
    chunk_overlap=100,
)
fr3_nodes = fr3_splitter.get_nodes_from_documents(fr3_docs)
print(f"      Created {len(fr3_nodes)} nodes")

# 4. SQL schema files - manually iterate to use custom reader
print("\n[4/6] Loading SQL schema files...")
sql_files = list(Path("schemas").rglob("*.sql"))
print(f"      Found {len(sql_files)} SQL files")
sql_docs: List[Document] = []
for f in sql_files:
    sql_docs.extend(sql_reader.load_data(f))
print(f"      Loaded {len(sql_docs)} SQL documents")
sql_nodes = [node_from_doc(doc) for doc in sql_docs]
print(f"      Created {len(sql_nodes)} nodes")

# ────────────────────────────────────────────────
# Combine all nodes and create index
# ────────────────────────────────────────────────
print("\n[5/6] Combining all nodes...")
all_nodes = delphi_nodes + dfm_nodes + fr3_nodes + sql_nodes
print(f"      Total nodes: {len(all_nodes)}")

print("\n[6/6] Creating vector index and embedding...")
index = VectorStoreIndex(
    all_nodes,
    embed_model=embed_model,
    storage_context=storage_context,
    embed_batch_size=64,  # good for 8 GB VRAM
    show_progress=True,
)

print("      Persisting to disk...")
index.storage_context.persist(persist_dir=config.INDEX_PATH)

# ────────────────────────────────────────────────
# Summary print
# ────────────────────────────────────────────────
print("\n" + "=" * 70)
print("Delphi RAG Index Created Successfully")
print(f"  • Delphi/Pascal chunks (.pas/.dpr)       : {len(delphi_nodes):>6}")
print(f"  • Delphi .dfm chunks                     : {len(dfm_nodes):>6}")
print(f"  • FastReport .fr3 chunks                  : {len(fr3_nodes):>6}")
print(f"  • SQL schema chunks                       : {len(sql_nodes):>6}")
print("-" * 70)
print(f"  TOTAL NODES                               : {len(all_nodes):>6}")
print("=" * 70 + "\n")

print("Index persisted to: ./index_storage")
print("You can now run the MCP server (delphi_rag_mcp.py)")
