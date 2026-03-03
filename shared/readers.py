from typing import List, Optional
from pathlib import Path
from datetime import datetime
from llama_index.core import Document
from llama_index.core.readers.base import BaseReader
from tree_sitter import Node
from tree_sitter_language_pack import get_language, get_parser
import xml.etree.ElementTree as ET

PASCAL_LANGUAGE = get_language("pascal")
parser_global = get_parser("pascal")

SQL_LANGUAGE = get_language("sql")
sql_parser = get_parser("sql")


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
            content, content_bytes = read_file_with_encoding_and_bytes(file)
        except Exception as e:
            print(f"Failed to read {file}: {e}")
            return []

        if not content.strip():
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)

        try:
            tree = parser_global.parse(content_bytes)
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
            node_type = node.type

            if node_type in self.NODE_TYPES:
                chunk_text = (
                    content_bytes[node.start_byte : node.end_byte]
                    .decode("utf-8", errors="replace")
                    .strip()
                )
                if len(chunk_text) > 50:
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": node_type,
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
            content, content_bytes = read_file_with_encoding_and_bytes(file)
        except Exception as e:
            print(f"Failed to read {file}: {e}")
            return []

        if not content.strip():
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)

        try:
            tree = sql_parser.parse(content_bytes)
        except Exception as e:
            print(f"Tree-sitter SQL parse failed for {file}: {e}")
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
            node_type = node.type

            if node_type in self.NODE_TYPES:
                chunk_text = (
                    content_bytes[node.start_byte : node.end_byte]
                    .decode("utf-8", errors="replace")
                    .strip()
                )
                if len(chunk_text) > 30:
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": node_type,
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


class DFMFileReader(BaseReader):
    """Custom reader for Delphi .dfm files with line tracking"""

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

        file_path_str = str(file)
        lines = content.split("\n")
        file_datetime = get_file_datetime(file)

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("object "):
                obj_start = i
                obj_name = (
                    line[7:].split(":")[0].strip() if ":" in line else line[7:].strip()
                )
                obj_type = line[7:].split(":")[1].strip() if ":" in line else "TObject"

                obj_lines = [lines[i]]
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith("end"):
                    obj_lines.append(lines[j])
                    j += 1
                if j < len(lines):
                    obj_lines.append(lines[j])

                obj_text = "\n".join(obj_lines)
                if len(obj_text) > 30:
                    start_byte = sum(len(lines[k]) + 1 for k in range(i))
                    end_byte = start_byte + len(obj_text)

                    documents.append(
                        Document(
                            text=obj_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": "dfm_object",
                                "object_name": obj_name,
                                "object_type": obj_type,
                                "start_line": i + 1,
                                "end_line": j + 1,
                                "start_byte": start_byte,
                                "end_byte": end_byte,
                                **file_datetime,
                            },
                        )
                    )
                i = j
            else:
                i += 1

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


class DPROJFileReader(BaseReader):
    """Custom reader for Delphi .dproj files with line tracking"""

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents = []
        content = None
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            root = ET.fromstring(content)
        except ET.ParseError as e:
            print(f"XML parse error for {file}: {e}")
            if content and len(content) > 0:
                documents.append(
                    Document(
                        text=content[:5000],
                        metadata={
                            "file_path": str(file),
                            "type": "raw_dproj",
                            "parse_error": str(e),
                            **get_file_datetime(file),
                        },
                    )
                )
            return documents
        except Exception as e:
            print(f"Could not read {file}: {e}")
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)
        lines = content.split("\n")

        proj_name = root.get("ProjectGuid", "")
        for prop_group in root.findall(".//PropertyGroup"):
            name_elem = prop_group.find("Name")
            if name_elem is not None and name_elem.text:
                proj_name = name_elem.text
                break

        proj_info = f"Project: {proj_name}"
        documents.append(
            Document(
                text=proj_info,
                metadata={
                    "file_path": file_path_str,
                    "node_type": "project_info",
                    "project_name": proj_name,
                    "start_line": 1,
                    "end_line": len(lines),
                    "start_byte": 0,
                    "end_byte": len(content),
                    **file_datetime,
                },
            )
        )

        for config_group in root.findall(".//PropertyGroup[@Condition]"):
            condition = config_group.get("Condition", "")
            config_name = ""
            for key in ["CfgType", "BaseConfiguration", "Configuration"]:
                elem = config_group.find(key)
                if elem is not None and elem.text:
                    config_name = elem.text
                    break

            if config_name:
                config_lines = []
                for child in list(config_group)[:10]:
                    if child.text and child.text.strip():
                        config_lines.append(f"{child.tag}: {child.text.strip()}")

                if config_lines:
                    config_text = f"Config: {config_name}\n" + "\n".join(config_lines)
                    documents.append(
                        Document(
                            text=config_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": "project_config",
                                "config": config_name,
                                "condition": condition,
                                **file_datetime,
                            },
                        )
                    )

        for item_group in root.findall(".//ItemGroup"):
            for child in list(item_group)[:5]:
                if child.get("Include"):
                    documents.append(
                        Document(
                            text=f"{child.tag}: {child.get('Include')}",
                            metadata={
                                "file_path": file_path_str,
                                "node_type": "project_item",
                                "item_type": child.tag,
                                "item_include": child.get("Include"),
                                **file_datetime,
                            },
                        )
                    )

        if not documents:
            documents.append(
                Document(
                    text=content[:8000],
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        **file_datetime,
                    },
                )
            )

        return documents


class FastReportFR3Parser:
    """Extracts scripts, memo texts, bands and dataset schemas from .fr3 files"""

    def load(self, file_path: str) -> List[Document]:
        documents = []
        content = None
        file_path_obj = Path(file_path)

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
                            **get_file_datetime(file_path_obj),
                        },
                    )
                )
            return documents
        except Exception as e:
            print(f"Could not read {file_path}: {e}")
            return []

        file_path_str = str(file_path)
        file_datetime = get_file_datetime(file_path_obj)

        line_offsets = [0]
        for i, char in enumerate(content):
            if char == "\n":
                line_offsets.append(i + 1)

        def get_line_from_offset(offset: int) -> int:
            for idx, line_start in enumerate(line_offsets):
                if line_start > offset:
                    return idx
            return len(line_offsets)

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
                            "start_line": 1,
                            "end_line": len(content.split("\n")),
                            **file_datetime,
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
                        metadata={
                            "file_path": file_path_str,
                            "type": "variable",
                            **file_datetime,
                        },
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
                        metadata={
                            "file_path": file_path_str,
                            "type": "datasource",
                            **file_datetime,
                        },
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
                        metadata={
                            "file_path": file_path_str,
                            "type": "dataset_schema",
                            **file_datetime,
                        },
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
                                **file_datetime,
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
                    metadata={
                        "file_path": file_path_str,
                        "type": "report_props",
                        **file_datetime,
                    },
                )
            )

        if not documents and content:
            documents.append(
                Document(
                    text=content[:8000],
                    metadata={
                        "file_path": file_path_str,
                        "type": "raw_fr3",
                        **file_datetime,
                    },
                )
            )

        return documents
