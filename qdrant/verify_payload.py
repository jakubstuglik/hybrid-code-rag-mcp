"""
Verify Qdrant payload text matches source snippets.

Usage:
    python -m qdrant.verify_payload
    python -m qdrant.verify_payload --limit 50
"""

import argparse
from pathlib import Path
from typing import Optional

from qdrant_client import QdrantClient

import config
from shared.readers import read_file_with_encoding, read_file_with_encoding_and_bytes


def _safe_int(value) -> Optional[int]:
    try:
        return int(value)
    except Exception:
        return None


def _load_snippet(payload: dict, max_chars: int = 4000) -> Optional[str]:
    file_path = payload.get("file_path")
    if not file_path:
        return None

    path = Path(file_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / file_path

    try:
        text = read_file_with_encoding(path)
    except Exception:
        return None

    start_byte = _safe_int(payload.get("start_byte"))
    end_byte = _safe_int(payload.get("end_byte"))
    if start_byte is not None and end_byte is not None and start_byte <= end_byte:
        try:
            _, content_bytes = read_file_with_encoding_and_bytes(path)
            snippet = content_bytes[start_byte:end_byte].decode(
                "utf-8", errors="replace"
            )
            return snippet[:max_chars] if snippet else None
        except Exception:
            return None

    start_line = _safe_int(payload.get("start_line"))
    end_line = _safe_int(payload.get("end_line"))
    if start_line and end_line and start_line <= end_line:
        lines = text.splitlines()
        snippet = "\n".join(lines[start_line - 1 : end_line])
    else:
        start_char = _safe_int(payload.get("start_char_idx"))
        end_char = _safe_int(payload.get("end_char_idx"))
        if start_char is not None and end_char is not None and start_char <= end_char:
            snippet = text[start_char:end_char]
        else:
            return None

    if not snippet:
        return None
    return snippet[:max_chars]


def _get_client() -> QdrantClient:
    if config.QDRANT_USE_DOCKER:
        return QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    return QdrantClient(path=config.get_index_path())


def _find_in_file(text: str, needle: str) -> Optional[int]:
    if not needle:
        return None
    idx = text.find(needle)
    if idx >= 0:
        return idx
    return None


def _print_example(payload: dict, text_value: str, snippet: Optional[str]) -> None:
    file_path = payload.get("file_path", "?")
    start_line = payload.get("start_line", "?")
    end_line = payload.get("end_line", "?")
    file_text = None
    if file_path and file_path != "?":
        path = Path(file_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parent.parent / file_path
        try:
            file_text = read_file_with_encoding(path)
        except Exception:
            file_text = None

    file_len = len(file_text) if file_text is not None else None
    text_len = len(text_value or "")

    found_line = None
    if file_text and text_value:
        idx = _find_in_file(file_text, text_value)
        if idx is not None:
            found_line = file_text.count("\n", 0, idx) + 1

    print("\n[EXAMPLE]")
    print(f"FILE: {file_path}")
    print(f"LINES: {start_line}–{end_line}")
    if file_len is not None:
        print(f"FILE LEN: {file_len} chars")
    print(f"TEXT LEN: {text_len} chars")
    if found_line is not None:
        print(f"TEXT FOUND AT LINE: {found_line}")
    print("--- payload[text] (first 400 chars) ---")
    print((text_value or "")[:400])
    print("--- snippet from disk (first 400 chars) ---")
    print((snippet or "")[:400])


def _line_for_index(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def verify(limit: int, max_chars: int, show_examples: int) -> None:
    client = _get_client()

    points, _ = client.scroll(
        collection_name=config.COLLECTION_NAME,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )

    checked = 0
    matched = 0
    matched_by_location = 0
    missing_text = 0
    missing_meta = 0
    shown = 0

    for point in points:
        payload = point.payload or {}
        text_value = payload.get("text")
        if not text_value:
            missing_text += 1
            continue

        snippet = _load_snippet(payload, max_chars=max_chars)
        if snippet is None:
            missing_meta += 1
            continue

        checked += 1
        is_match = (
            text_value == snippet
            or text_value.startswith(snippet)
            or snippet.startswith(text_value)
        )

        file_path = payload.get("file_path")
        found_line = None
        if file_path:
            path = Path(file_path)
            if not path.is_absolute():
                path = Path(__file__).resolve().parent.parent / file_path
            try:
                file_text = read_file_with_encoding(path)
                idx = _find_in_file(file_text, text_value)
                if idx is not None:
                    found_line = _line_for_index(file_text, idx)
            except Exception:
                found_line = None

        start_line = _safe_int(payload.get("start_line"))
        end_line = _safe_int(payload.get("end_line"))
        if found_line is not None and start_line and end_line:
            if start_line <= found_line <= end_line:
                matched_by_location += 1
        if is_match:
            matched += 1

        if shown < show_examples:
            _print_example(payload, text_value, snippet)
            shown += 1

    print(f"[VERIFY] checked: {checked}")
    print(f"[VERIFY] matched (text vs snippet): {matched}")
    print(f"[VERIFY] matched by location: {matched_by_location}")
    print(f"[VERIFY] missing text: {missing_text}")
    print(f"[VERIFY] missing line/char metadata: {missing_meta}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Qdrant payload text")
    parser.add_argument(
        "--limit", type=int, default=25, help="Number of points to sample"
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=4000,
        help="Max chars used when comparing snippets",
    )
    parser.add_argument(
        "--show-examples",
        type=int,
        default=3,
        help="Number of samples to print",
    )
    args = parser.parse_args()

    verify(limit=args.limit, max_chars=args.max_chars, show_examples=args.show_examples)
