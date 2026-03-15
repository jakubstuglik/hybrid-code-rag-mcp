"""
Dump a tree-sitter chunk to a UTF-8 file for VS Code inspection.

Usage:
    python -m tests.debug.dump_snippet --file "source/Common/DISP_File/OPERIBUS_DISPFileFrame.pas" --token RS_NO_CITY_VERSION
"""

import argparse
from pathlib import Path

from tree_sitter_language_pack import get_parser


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


def read_with_encoding(file_path: Path) -> tuple[str, str]:
    encodings = ["utf-8", "windows-1250", "cp1250", "latin-1"]
    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding), encoding
        except Exception:
            continue
    return file_path.read_text(encoding="utf-8", errors="replace"), "utf-8+replace"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dump tree-sitter chunk for inspection"
    )
    parser.add_argument("--file", required=True, help="Path to Pascal file")
    parser.add_argument("--token", required=True, help="Token to search inside chunks")
    parser.add_argument("--out", default="tmp/ts_snippet.txt", help="Output file path")
    args = parser.parse_args()

    file_path = Path(args.file)
    content, encoding = read_with_encoding(file_path)
    raw = content.encode("utf-8")

    parser_ts = get_parser("pascal")
    tree = parser_ts.parse(raw)

    def snippet(start_byte: int, end_byte: int) -> str:
        return raw[start_byte:end_byte].decode("utf-8", errors="replace")

    match = None

    def traverse(node) -> None:
        nonlocal match
        if match is not None:
            return
        if node.type in NODE_TYPES:
            text = snippet(node.start_byte, node.end_byte).strip()
            if args.token in text:
                match = (node, text)
                return
        for child in node.children:
            traverse(child)

    traverse(tree.root_node)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if match is None:
        out_path.write_text(f"Token not found: {args.token}\n", encoding="utf-8")
        return 1

    node, text = match
    header = (
        f"FILE: {file_path.as_posix()}\n"
        f"ENCODING: {encoding}\n"
        f"NODE TYPE: {node.type}\n"
        f"LINES: {node.start_point[0] + 1}-{node.end_point[0] + 1}\n"
        f"BYTES: {node.start_byte}-{node.end_byte}\n"
        "---\n"
    )
    out_path.write_text(header + text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
