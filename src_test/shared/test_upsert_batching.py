"""Tests for size-aware Qdrant upsert batching."""

import pytest

from shared.upsert_batching import is_split_worthy, split_batches, upsert_in_batches


def _size(p):
    return p["size"]


def _pts(*sizes):
    return [{"id": i, "size": s} for i, s in enumerate(sizes)]


def test_split_by_count():
    bs = split_batches(_pts(*[1] * 7), max_points=3, max_bytes=0, size_fn=_size)
    assert [len(b) for b in bs] == [3, 3, 1]


def test_split_by_bytes_and_oversize_point_alone():
    bs = split_batches(_pts(4, 4, 4, 20, 1), max_points=100, max_bytes=10, size_fn=_size)
    assert [[p["id"] for p in b] for b in bs] == [[0, 1], [2], [3], [4]]


def test_rejected_batch_is_halved_and_retried():
    sent = []

    def upsert(batch):
        if len(batch) > 2:
            raise RuntimeError("Unexpected Response: 400 (Bad Request) Payload error: JSON payload is larger than allowed")
        sent.append([p["id"] for p in batch])

    warnings = []
    calls = upsert_in_batches(upsert, _pts(*[1] * 5), max_points=5, max_bytes=0, warn=warnings.append, size_fn=_size)
    assert sorted(i for b in sent for i in b) == [0, 1, 2, 3, 4]
    assert all(len(b) <= 2 for b in sent)
    assert calls > 1 and warnings


def test_connection_abort_is_split_worthy():
    try:
        try:
            raise ConnectionAbortedError(10053, "connection aborted by host software")
        except ConnectionAbortedError as inner:
            raise RuntimeError("ResponseHandlingException") from inner
    except RuntimeError as e:
        assert is_split_worthy(e)


def test_other_errors_propagate_without_split():
    calls = []

    def upsert(batch):
        calls.append(len(batch))
        raise ValueError("wrong vector dimension")

    with pytest.raises(ValueError):
        upsert_in_batches(upsert, _pts(1, 1, 1, 1), max_points=4, max_bytes=0, size_fn=_size)
    assert calls == [4]


def test_single_oversize_point_raises():
    def upsert(batch):
        raise RuntimeError("Payload error: larger than allowed")

    with pytest.raises(RuntimeError):
        upsert_in_batches(upsert, _pts(50), max_points=10, max_bytes=10, size_fn=_size)


def test_qdrant_point_struct_size():
    models = pytest.importorskip("qdrant_client.models")
    from shared.upsert_batching import point_size

    p = models.PointStruct(id=1, vector=[0.5] * 8, payload={"text": "x" * 1000})
    assert point_size(p) > 1000


def test_timeout_is_split_worthy():
    assert is_split_worthy(TimeoutError("timed out"))
    assert is_split_worthy(RuntimeError("ResponseHandlingException: timed out"))
