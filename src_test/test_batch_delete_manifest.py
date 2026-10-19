# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Manifest stays put when a batched Qdrant delete fails."""

from __future__ import annotations

from typing import Any


def apply_delete_chunks(
    delete_keys: list[str],
    manifest_files: dict[str, Any],
    *,
    chunk_size: int,
    delete_chunk,
) -> tuple[list[str], list[str]]:
    """Mirror of perform_refresh_qdrant delete bookkeeping (success-only drop)."""
    dropped: list[str] = []
    failed: list[str] = []
    for offset in range(0, len(delete_keys), chunk_size):
        chunk = delete_keys[offset : offset + chunk_size]
        try:
            delete_chunk(chunk)
        except Exception:
            failed.extend(chunk)
            continue
        for key in chunk:
            manifest_files.pop(key, None)
            dropped.append(key)
    return dropped, failed


def test_failed_chunk_keeps_manifest_entries():
    files = {f"a/{i}.py": {"vector_ids": [i]} for i in range(6)}
    keys = list(files.keys())

    def delete_chunk(chunk: list[str]) -> None:
        # Fail the second chunk only
        if chunk[0].endswith("2.py"):
            raise RuntimeError("qdrant down")

    dropped, failed = apply_delete_chunks(
        keys, files, chunk_size=2, delete_chunk=delete_chunk
    )
    assert dropped == ["a/0.py", "a/1.py", "a/4.py", "a/5.py"]
    assert failed == ["a/2.py", "a/3.py"]
    assert "a/2.py" in files and "a/3.py" in files
    assert "a/0.py" not in files and "a/1.py" not in files
