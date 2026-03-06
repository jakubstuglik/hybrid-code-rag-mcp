"""
Repair Qdrant payloads missing text/document fields.

This scans points and backfills payload["text"] and payload["document"]
from existing payload or from disk using file_path + line metadata.

Usage:
    python -m qdrant.repair_payload
"""

from pathlib import Path
import time
from typing import Optional, Tuple

from qdrant_client import QdrantClient

import config
from shared.readers._base import read_file_with_encoding


def _safe_int(value) -> Optional[int]:
    try:
        return int(value)
    except Exception:
        return None


def _load_from_disk(payload: dict, max_chars: int = 4000) -> Optional[str]:
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
            snippet = text

    return snippet[:max_chars] if snippet else None


def _get_client() -> QdrantClient:
    if config.QDRANT_USE_DOCKER:
        return QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    return QdrantClient(path=config.get_index_path())


def repair_payloads(batch_size: int = 1000) -> Tuple[int, int, int, int, int]:
    client = _get_client()
    fixed = 0
    skipped = 0
    from_disk = 0
    document_to_text = 0
    document_removed = 0

    offset = None
    processed = 0
    start = time.perf_counter()
    while True:
        points, next_offset = client.scroll(
            collection_name=config.COLLECTION_NAME,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        if not points:
            break

        for point in points:
            payload = point.payload or {}
            text_value = payload.get("text")
            document_value = payload.get("document")

            update = {}
            if not text_value and document_value:
                update["text"] = document_value
                document_to_text += 1

            if not text_value and not document_value:
                disk_text = _load_from_disk(payload)
                if disk_text:
                    update["text"] = disk_text
                    from_disk += 1

            if update:
                client.set_payload(
                    collection_name=config.COLLECTION_NAME,
                    payload=update,
                    points=[point.id],
                )
                fixed += 1

            if document_value is not None:
                client.delete_payload(
                    collection_name=config.COLLECTION_NAME,
                    keys=["document"],
                    points=[point.id],
                )
                document_removed += 1

            if not update and document_value is None:
                skipped += 1

            processed += 1

        elapsed = time.perf_counter() - start
        rate = processed / elapsed if elapsed else 0
        print(
            f"[REPAIR] processed {processed:,} | updated {fixed:,} | removed document {document_removed:,} "
            f"| {rate:,.0f}/s",
            flush=True,
        )

        if next_offset is None:
            break
        offset = next_offset

    return fixed, skipped, from_disk, document_to_text, document_removed


if __name__ == "__main__":
    print("[REPAIR] Scanning Qdrant payloads...")
    fixed, skipped, from_disk, document_to_text, document_removed = repair_payloads()
    print(f"[REPAIR] updated points: {fixed}")
    print(f"[REPAIR] already ok: {skipped}")
    print(f"[REPAIR] document->text: {document_to_text}")
    print(f"[REPAIR] filled from disk: {from_disk}")
    print(f"[REPAIR] document removed: {document_removed}")
