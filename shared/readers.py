from typing import List, Optional
from pathlib import Path
from llama_index.core import Document
from llama_index.core.readers.base import BaseReader
from tree_sitter import Node
from tree_sitter_language_pack import get_language, get_parser
import xml.etree.ElementTree as ET

PASCAL_LANGUAGE = get_language("pascal")
parser_global = get_parser("pascal")

SQL_LANGUAGE = get_language("sql")
sql_parser = get_parser("sql")


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

        for page in root.findall(".//Page"):
            page_name = page.get("Name", "UnnamedPage")

            for band in page.findall(".//Band"):
                band_name = band.get("Name", "UnnamedBand")
                band_type = band.get("Type", "Unknown")

                band_props = []
                for key, value in band.attrib.items():
                    if key not in ("Name", "Type") and value:
                        band_props.append(f"{key}={value}")
                band_desc = f"Band: {band_name} Type={band_type}"
                if band_props:
                    band_desc += " " + ", ".join(band_props[:5])

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

        if not documents and content:
            documents.append(
                Document(
                    text=content[:8000],
                    metadata={"file_path": file_path_str, "type": "raw_fr3"},
                )
            )

        return documents
