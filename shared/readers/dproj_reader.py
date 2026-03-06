"""
Delphi project file reader (.dproj) using XML parsing.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional

from llama_index.core import Document

from shared.readers._base import BaseFileReader, get_file_datetime
from shared.log import log_warn


class DPROJFileReader(BaseFileReader):
    """Reader for Delphi .dproj XML files that extracts project metadata."""

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
            log_warn(f"XML parse error for {file}: {e}")
            if content:
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
            log_warn(f"Could not read {file}: {e}")
            return []

        file_path_str = str(file)
        file_datetime = get_file_datetime(file)
        lines = content.split("\n")

        # Project name / GUID
        proj_name = root.get("ProjectGuid", "")
        for prop_group in root.findall(".//PropertyGroup"):
            name_elem = prop_group.find("Name")
            if name_elem is not None and name_elem.text:
                proj_name = name_elem.text
                break

        documents.append(
            Document(
                text=f"Project: {proj_name}",
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

        # Per-configuration property groups
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
                    documents.append(
                        Document(
                            text=f"Config: {config_name}\n" + "\n".join(config_lines),
                            metadata={
                                "file_path": file_path_str,
                                "node_type": "project_config",
                                "config": config_name,
                                "condition": condition,
                                **file_datetime,
                            },
                        )
                    )

        # Item groups (included files / compile units)
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
