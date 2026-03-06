"""
FastReport template reader (.fr3) using XML parsing.

This reader overrides load_nodes() to apply a SentenceSplitter internally,
so callers always get correctly-sized TextNodes without any external setup.
"""

import html
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

from shared.readers._base import BaseFileReader, get_file_datetime
from llama_index.core.schema import TextNode


class FR3Reader(BaseFileReader):
    """
    Extracts scripts, memo texts, bands and dataset schemas from FastReport .fr3 files.

    A SentenceSplitter (chunk_size=1000, chunk_overlap=100) is applied inside
    load_nodes() so callers do not need to handle this themselves.
    """

    _splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=100)

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents = []
        content = None
        file_path_str = str(file)

        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            root = ET.fromstring(content)
        except ET.ParseError as e:
            print(f"XML parse error for {file}: {e}")
            if content:
                documents.append(
                    Document(
                        text=content[:5000],
                        metadata={
                            "file_path": file_path_str,
                            "type": "raw_fr3",
                            "parse_error": str(e),
                            **get_file_datetime(file),
                        },
                    )
                )
            return documents
        except Exception as e:
            print(f"Could not read {file}: {e}")
            return []

        file_datetime = get_file_datetime(file)

        # Pascal script embedded in report root
        script_text = root.get("ScriptText.Text", "")
        if script_text:
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

        # Report variables
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

        # Data sources
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

        # Dataset schemas
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

        # Page / band / memo content
        for page in root.findall(".//Page"):
            page_name = page.get("Name", "UnnamedPage")
            for band in page.findall(".//Band"):
                band_name = band.get("Name", "UnnamedBand")
                band_type = band.get("Type", "Unknown")

                band_props = [
                    f"{k}={v}"
                    for k, v in band.attrib.items()
                    if k not in ("Name", "Type") and v
                ]
                band_desc = f"Band: {band_name} Type={band_type}"
                if band_props:
                    band_desc += " " + ", ".join(band_props[:5])

                memo_texts = []
                for memo in band.findall(".//Memo"):
                    memo_name = memo.get("Name", "")
                    text_elem = memo.find("Text")
                    memo_text = ""
                    if text_elem is not None and text_elem.text:
                        memo_text = text_elem.text.strip()
                    elif text_elem is not None:
                        memo_text = text_elem.text or ""

                    if memo_text:
                        prefix = f"Memo: {memo_name}" if memo_name else "Memo"
                        memo_texts.append(f"{prefix}: {memo_text}")
                    elif memo_name:
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
                elif band_desc:
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

        # Top-level report properties
        report_props = [
            f"{k}={root.get(k)}"
            for k in root.attrib
            if k and root.get(k)
        ]
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

    def load_nodes(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[TextNode]:
        """Parse and apply sentence splitting, returning TextNodes."""
        docs = self.load_data(file, extra_info)
        if not docs:
            return []
        return self._splitter.get_nodes_from_documents(docs)
