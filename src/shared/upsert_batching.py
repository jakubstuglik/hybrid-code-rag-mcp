"""Size-aware batching for Qdrant upserts.

Qdrant rejects any request whose JSON body exceeds ``service.max_request_size_mb``
(32 MB by default) with HTTP 400 "Payload error: JSON payload (...) is larger
than allowed".  While the client is still uploading, the server closes the
socket, which surfaces client-side as a connection abort/reset (e.g. WinError
10053/10054) rather than the 400.  Fixed point-count batches hit this on files
with many large chunks (e.g. generated register headers), so batches are also
capped by estimated serialized size, and a rejected batch is split in half and
retried.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Iterable, Optional

# Half of Qdrant's default 32 MB request limit leaves room for estimate error.
DEFAULT_MAX_UPSERT_BYTES = 16 * 1024 * 1024

_SPLIT_MARKERS = (
    "larger than allowed",
    "payload error",
    "10053",
    "10054",
    "connection aborted",
    "connection reset",
    "broken pipe",
    "remote end closed",
    "remoteprotocolerror",
    "server disconnected",
)


def point_size(point: Any) -> int:
    """Estimated JSON size of one point in bytes."""
    dump = getattr(point, "model_dump_json", None)
    if callable(dump):
        try:
            return len(dump())
        except Exception:  # pragma: no cover - fall through to json
            pass
    try:
        return len(json.dumps(point, default=str))
    except Exception:
        return len(str(point))


def split_batches(
    points: list, max_points: int, max_bytes: int,
    size_fn: Callable[[Any], int] = point_size,
) -> list[list]:
    """Split ``points`` into batches of at most ``max_points`` points and
    (estimated) ``max_bytes`` bytes.  A single oversize point gets its own batch."""
    max_points = max(1, int(max_points))
    batches: list[list] = []
    cur: list = []
    cur_bytes = 0
    for p in points:
        s = size_fn(p)
        if cur and (len(cur) >= max_points or (max_bytes and cur_bytes + s > max_bytes)):
            batches.append(cur)
            cur, cur_bytes = [], 0
        cur.append(p)
        cur_bytes += s
    if cur:
        batches.append(cur)
    return batches


def is_split_worthy(exc: BaseException) -> bool:
    """True when a failed upsert should be retried as two smaller requests."""
    seen: set[int] = set()
    e: Optional[BaseException] = exc
    while e is not None and id(e) not in seen:
        seen.add(id(e))
        text = f"{type(e).__name__} {e}".lower()
        if any(m in text for m in _SPLIT_MARKERS):
            return True
        if isinstance(e, (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
            return True
        e = e.__cause__ or e.__context__
    return False


def upsert_in_batches(
    upsert: Callable[[list], Any],
    points: list,
    max_points: int,
    max_bytes: int = DEFAULT_MAX_UPSERT_BYTES,
    warn: Optional[Callable[[str], None]] = None,
    size_fn: Callable[[Any], int] = point_size,
) -> int:
    """Upsert ``points`` via ``upsert(batch)``; returns the number of requests made.

    Batches are capped by count and estimated size; a batch rejected for size
    (or dropped mid-upload) is halved recursively.  Other errors, and a
    single point that still fails, propagate to the caller.
    """
    calls = 0

    def _send(batch: list) -> None:
        nonlocal calls
        calls += 1
        try:
            upsert(batch)
        except Exception as e:
            if len(batch) <= 1 or not is_split_worthy(e):
                raise
            mid = len(batch) // 2
            if warn:
                warn(f"upsert of {len(batch)} points rejected ({type(e).__name__}); retrying as 2 x ~{mid}")
            _send(batch[:mid])
            _send(batch[mid:])

    for b in split_batches(points, max_points, max_bytes, size_fn):
        _send(b)
    return calls


def batches_info(points: Iterable, max_points: int, max_bytes: int) -> tuple[int, int]:
    """(batch count, largest estimated batch bytes) — for logging/tests."""
    bs = split_batches(list(points), max_points, max_bytes)
    return len(bs), max((sum(point_size(p) for p in b) for b in bs), default=0)
