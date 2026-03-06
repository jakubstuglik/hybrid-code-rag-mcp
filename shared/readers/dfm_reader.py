"""
Delphi form file reader (.dfm) with line-by-line object block extraction.
"""

from pathlib import Path
from typing import List, Optional

from llama_index.core import Document

from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding,
)


class DFMFileReader(BaseFileReader):
    """Reader for Delphi .dfm files that extracts each top-level object block."""

    MIN_CHUNK_SIZE = 30

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
                obj_name = (
                    line[7:].split(":")[0].strip() if ":" in line else line[7:].strip()
                )
                obj_type = (
                    line[7:].split(":")[1].strip() if ":" in line else "TObject"
                )

                obj_lines = [lines[i]]
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith("end"):
                    obj_lines.append(lines[j])
                    j += 1
                if j < len(lines):
                    obj_lines.append(lines[j])

                obj_text = "\n".join(obj_lines)
                if len(obj_text) > self.MIN_CHUNK_SIZE:
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
