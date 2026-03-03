"""
Dump all tree-sitter nodes for a file to a UTF-8 text file.

Usage:
    python -m qdrant.dump_tokens --file "source/Common/DISP_File/OPERIBUS_DISPFileFrame.pas" --out tmp/operibus_tokens.txt
"""

import argparse
from pathlib import Path

from tree_sitter_language_pack import get_parser

from shared.readers import read_file_with_encoding_and_bytes


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Dump tree-sitter tokens")
    parser.add_argument("--file", required=True, help="Path to Pascal file")
    parser.add_argument("--out", default="tmp/ts_tokens.txt", help="Output file path")
    args = parser.parse_args()

    file_path = Path(args.file)
    text, content_bytes = read_file_with_encoding_and_bytes(file_path)

    parser_ts = get_parser("pascal")
    tree = parser_ts.parse(content_bytes)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def snippet(start_byte: int, end_byte: int) -> str:
        return content_bytes[start_byte:end_byte].decode("utf-8", errors="replace")

    lines = []
    lines.append(f"FILE: {file_path.as_posix()}")
    lines.append("---")

    def traverse(node) -> None:
        if node.type in NODE_TYPES:
            block = [
                f"TYPE: {node.type}",
                f"LINES: {node.start_point[0] + 1}-{node.end_point[0] + 1}",
                f"BYTES: {node.start_byte}-{node.end_byte}",
                "TEXT:",
                snippet(node.start_byte, node.end_byte).rstrip(),
                "---",
            ]
            lines.extend(block)
        for child in node.children:
            traverse(child)

    traverse(tree.root_node)

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
