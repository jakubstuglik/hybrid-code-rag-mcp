# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0
"""Index state and embedding provenance stored in Qdrant itself.

A serving-only MCP instance (centralized topology: the indexer runs on one
machine, the MCP server on another) has no access to the indexer's manifest
files. Everything the server needs from them is published into the
collection by the indexer:

* **Index state document** (``INDEX_STATE_KEY``): repo commits, the last
  ``index_run``, indexer versions, source snapshots, the number of indexed
  files and one summary per branch/tag overlay. It is small (a few KB, it
  grows with the number of repos and overlays, not with files) and lives in
  the collection ``metadata`` (Qdrant >= 1.16, PATCH semantics: only the
  keys written are replaced). On older Qdrant servers it is stored in the
  payload of the reserved point ``STATE_POINT_ID`` instead.
* **Overlay tombstones** (file keys deleted on a branch): they can be large,
  so they are never put into the metadata. They are stored in reserved
  points, ``TOMBSTONES_PER_POINT`` keys per point, one series per overlay.
  The state document carries their count, number of parts and a SHA-256.
* **Embedding provenance** (``PROVENANCE_KEY``): model name, quantization,
  dimension, distance, prefixes, truncate dim, sparse model, indexer
  version and an embedding *fingerprint* (query embeddings of a few fixed
  texts). It is written into the payload of the existing provenance
  sentinel point (``PROVENANCE_POINT_ID``) and, without the fingerprint
  vectors, into the collection metadata.

Reserved points carry ``branch == RESERVED_BRANCH`` so that the MCP branch
filter (``branch`` in the requested labels, or no ``branch`` at all) never
returns them, the branch backfill leaves them alone and overlay cleanup
(delete by overlay label) never touches them. Their dense vectors are zero
and they have no sparse vector.

All functions take the Qdrant client as an argument; nothing here opens a
connection on its own.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from shared.log import log, log_warn

# ── Reserved ids and keys ─────────────────────────────────────────

#: Existing provenance sentinel (also read by older releases: ``embed_backend``).
PROVENANCE_POINT_ID = "00000000-0000-0000-0000-000000000001"
#: Fallback holder of the index state document (Qdrant < 1.16).
STATE_POINT_ID = "00000000-0000-0000-0000-000000000002"
#: ``branch`` value of every reserved point (never a real branch label).
RESERVED_BRANCH = "__hcr_reserved__"

INDEX_STATE_KEY = "hcr_index_state"
PROVENANCE_KEY = "hcr_provenance"
TOMBSTONES_KEY = "hcr_tombstones"
STATE_SCHEMA = 1
PROVENANCE_SCHEMA = 1

#: File keys per tombstone point (≈100 bytes per key → ≈100 KB payload).
TOMBSTONES_PER_POINT = 1000

#: Fixed texts whose query embeddings form the provenance fingerprint.
FINGERPRINT_TEXTS: Tuple[str, ...] = (
    "def add(a, b):\n    return a + b",
    "SELECT id, name FROM customers WHERE active = 1 ORDER BY name",
    "How is the database connection pool closed when the service shuts down?",
)
#: Default minimum cosine between stored and live fingerprint vectors.
DEFAULT_FINGERPRINT_MIN_COSINE = 0.98
#: Decimals kept when storing fingerprint vectors.
_FINGERPRINT_DECIMALS = 6

SOURCE_METADATA = "qdrant collection metadata"
SOURCE_STATE_POINT = "qdrant reserved point"


# ── Small helpers ─────────────────────────────────────────────────


def _json_bytes(obj: Any) -> int:
    return len(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def tombstone_point_id(label: str, part: int, digest: str = "") -> str:
    """Deterministic id of tombstone part *part* of overlay *label*.

    The id includes the tombstone digest, so a new tombstone set is written
    next to the old one and the state document switches to it in one write;
    readers of the previous document still find their parts.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"hcr-tombstones::{label}::{digest[:16]}::{part}"))


def _part_ids(label: str, entry: dict) -> List[str]:
    parts = int(entry.get("tombstone_parts") or 0)
    digest = entry.get("tombstones_sha256") or ""
    return [tombstone_point_id(label, i, digest) for i in range(parts)]


def tombstones_digest(keys: Iterable[str]) -> str:
    """SHA-256 of the sorted, newline-joined tombstone keys."""
    data = "\n".join(sorted(set(keys))).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def chunk_tombstones(keys: Iterable[str], per_point: int = TOMBSTONES_PER_POINT) -> List[List[str]]:
    """Split sorted unique *keys* into parts of at most *per_point* keys."""
    if per_point < 1:
        raise ValueError("per_point must be >= 1")
    ordered = sorted(set(keys))
    return [ordered[i : i + per_point] for i in range(0, len(ordered), per_point)]


def collection_vector_params(client: Any, collection_name: str) -> Optional[dict]:
    """Dense vector layout of a collection, or None when it cannot be read.

    Returns ``{"dimension", "distance", "names": [named dense vectors] or
    None for an unnamed vector, "hybrid": bool}``.
    """
    try:
        info = client.get_collection(collection_name=collection_name)
        params = info.config.params
    except Exception:
        return None
    vectors = getattr(params, "vectors", None)
    sparse = getattr(params, "sparse_vectors", None) or {}
    if isinstance(vectors, dict):
        if not vectors:
            return None
        name = "text-dense" if "text-dense" in vectors else sorted(vectors)[0]
        vp = vectors[name]
        names: Optional[List[str]] = sorted(vectors)
    else:
        vp = vectors
        names = None
    if vp is None or getattr(vp, "size", None) is None:
        return None
    distance = getattr(vp, "distance", None)
    distance = getattr(distance, "value", distance)
    return {
        "dimension": int(vp.size),
        "distance": str(distance) if distance is not None else None,
        "names": names,
        "sizes": {n: int(vectors[n].size) for n in names} if names else None,
        "hybrid": bool(isinstance(sparse, dict) and sparse),
    }


def _zero_vector(layout: dict) -> Any:
    if layout.get("names"):
        return {n: [0.0] * layout["sizes"][n] for n in layout["names"]}
    return [0.0] * layout["dimension"]


# ── Collection metadata (Qdrant >= 1.16) ─────────────────────────


def read_collection_metadata(client: Any, collection_name: str) -> Optional[dict]:
    """The collection ``metadata`` dict, ``{}`` when empty, None if unreadable.

    Servers or clients without collection metadata support return ``{}``.
    """
    try:
        info = client.get_collection(collection_name=collection_name)
    except Exception:
        return None
    meta = getattr(getattr(info, "config", None), "metadata", None)
    return dict(meta) if isinstance(meta, dict) else {}


def write_collection_metadata(client: Any, collection_name: str, patch: dict) -> bool:
    """PATCH *patch* into the collection metadata; True when it was stored.

    Verified by reading it back: a server that does not know collection
    metadata may reject the field or silently ignore it, both mean False.
    """
    try:
        client.update_collection(collection_name=collection_name, metadata=patch)
    except Exception as exc:  # noqa: BLE001 - old server/client: use the fallback
        log(f"[INDEX STATE] collection metadata not available ({type(exc).__name__}: {exc})")
        return False
    stored = read_collection_metadata(client, collection_name) or {}
    for key, value in patch.items():
        if _canonical(stored.get(key)) != _canonical(value):
            log("[INDEX STATE] collection metadata not stored by the server; using reserved points")
            return False
    return True


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


# ── Reserved points ───────────────────────────────────────────────


def write_reserved_point(client: Any, collection_name: str, point_id: str, payload: dict,
                         layout: Optional[dict] = None) -> int:
    """Upsert one reserved point (zero vector); return the payload size in bytes."""
    from qdrant_client import models

    layout = layout or collection_vector_params(client, collection_name)
    if layout is None:
        raise RuntimeError(f"cannot read vector layout of collection '{collection_name}'")
    body = dict(payload)
    body["branch"] = RESERVED_BRANCH
    client.upsert(
        collection_name=collection_name,
        points=[models.PointStruct(id=point_id, vector=_zero_vector(layout), payload=body)],
    )
    return _json_bytes(body)


def read_reserved_points(client: Any, collection_name: str, ids: List[str]) -> Dict[str, dict]:
    """``{id: payload}`` of the reserved points that exist (missing ids skipped)."""
    if not ids:
        return {}
    points = client.retrieve(
        collection_name=collection_name, ids=list(ids), with_payload=True, with_vectors=False
    )
    return {str(p.id): (p.payload or {}) for p in points or []}


def tombstone_point_ids_in_collection(client: Any, collection_name: str,
                                     page_size: int = 256) -> List[str]:
    """Ids of every tombstone point in the collection (any overlay, any digest).

    Reserved points (``branch == RESERVED_BRANCH``) that carry a
    ``TOMBSTONES_KEY`` payload; payloads are not transferred.
    """
    from qdrant_client import models

    flt = models.Filter(
        must=[models.FieldCondition(key="branch", match=models.MatchValue(value=RESERVED_BRANCH))],
        must_not=[models.IsEmptyCondition(is_empty=models.PayloadField(key=TOMBSTONES_KEY))],
    )
    ids: List[str] = []
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection_name, scroll_filter=flt, limit=page_size,
            offset=offset, with_payload=False, with_vectors=False,
        )
        ids.extend(str(p.id) for p in points or [])
        if offset is None:
            return ids


def _missing_reserved_points(client: Any, collection_name: str, ids: List[str]) -> bool:
    """True when any of *ids* does not exist (or cannot be checked)."""
    if not ids:
        return False
    try:
        points = client.retrieve(
            collection_name=collection_name, ids=list(ids), with_payload=False, with_vectors=False
        )
    except Exception:  # noqa: BLE001 - cannot tell: rewrite the parts
        return True
    return {str(p.id) for p in points or []} != {str(i) for i in ids}


def delete_reserved_points(client: Any, collection_name: str, ids: List[str]) -> None:
    if not ids:
        return
    from qdrant_client import models

    client.delete(
        collection_name=collection_name,
        points_selector=models.PointIdsList(points=list(ids)),
    )


# ── Index state document ──────────────────────────────────────────


def read_index_state(client: Any, collection_name: str) -> Tuple[Optional[dict], Optional[str]]:
    """Return ``(state document, source)``; ``(None, None)`` when absent.

    Collection metadata wins over the reserved state point (a server that
    was upgraded after a fallback write keeps a stale point behind).
    """
    meta = read_collection_metadata(client, collection_name)
    if meta is None:
        return None, None
    doc = meta.get(INDEX_STATE_KEY)
    if isinstance(doc, dict):
        return doc, SOURCE_METADATA
    try:
        payloads = read_reserved_points(client, collection_name, [STATE_POINT_ID])
    except Exception:
        return None, None
    doc = payloads.get(STATE_POINT_ID, {}).get(INDEX_STATE_KEY)
    if isinstance(doc, dict):
        return doc, SOURCE_STATE_POINT
    return None, None


@dataclass
class PublishStats:
    """What one ``publish_index_state`` call wrote."""

    target: str = ""
    state_bytes: int = 0
    tombstone_bytes: int = 0
    tombstone_points_written: int = 0
    tombstone_points_deleted: int = 0
    seconds: float = 0.0

    def summary(self) -> str:
        return (
            f"target={self.target}, state={self.state_bytes} B, "
            f"tombstones={self.tombstone_bytes} B in {self.tombstone_points_written} point(s) "
            f"written, {self.tombstone_points_deleted} deleted, {self.seconds * 1000:.0f} ms"
        )


def publish_index_state(
    client: Any,
    collection_name: str,
    doc: dict,
    tombstones: Dict[str, List[str]],
    *,
    per_point: int = TOMBSTONES_PER_POINT,
) -> PublishStats:
    """Store *doc* and the overlay *tombstones* in the collection.

    ``doc["overlays"]`` must hold one entry per overlay label in
    *tombstones*; this function fills in ``tombstone_count``,
    ``tombstone_parts`` and ``tombstones_sha256`` per overlay. Tombstone
    points are only rewritten when an overlay's digest or number of parts
    changed, or when a part of the unchanged series is missing.

    After the document switch every tombstone point the new document does
    not reference is deleted: the parts of the previous document (never an
    id the new document uses: the ids depend on label, digest and part
    number only, so a series written with another ``per_point`` shares
    ids with the old one) and parts left behind by an earlier publish that
    stopped half-way. One publisher per collection is assumed (the cron
    guards run one indexer per config).
    """
    t0 = time.perf_counter()
    stats = PublishStats()
    layout = collection_vector_params(client, collection_name)
    if layout is None:
        raise RuntimeError(f"collection '{collection_name}' not readable; state not published")
    previous, _ = read_index_state(client, collection_name)
    prev_overlays = (previous or {}).get("overlays") or {}

    doc = dict(doc)
    overlays = {k: dict(v) for k, v in (doc.get("overlays") or {}).items()}
    for label in tombstones:
        overlays.setdefault(label, {})
    stale: List[str] = []
    referenced: set = set()
    for label, entry in overlays.items():
        keys = tombstones.get(label) or []
        parts = chunk_tombstones(keys, per_point)
        digest = tombstones_digest(keys)
        entry["tombstone_count"] = len(set(keys))
        entry["tombstone_parts"] = len(parts)
        entry["tombstones_sha256"] = digest
        new_ids = [tombstone_point_id(label, i, digest) for i in range(len(parts))]
        referenced.update(new_ids)
        prev = prev_overlays.get(label) or {}
        if (
            prev.get("tombstones_sha256") == digest
            and int(prev.get("tombstone_parts") or 0) == len(parts)
            and not _missing_reserved_points(client, collection_name, new_ids)
        ):
            continue  # unchanged and complete: the existing parts stay referenced
        for i, chunk in enumerate(parts):
            stats.tombstone_bytes += write_reserved_point(
                client,
                collection_name,
                tombstone_point_id(label, i, digest),
                {TOMBSTONES_KEY: {"overlay": label, "part": i, "parts": len(parts),
                                  "sha256": digest, "keys": chunk}},
                layout,
            )
            stats.tombstone_points_written += 1
        stale.extend(_part_ids(label, prev))
    for label, prev in prev_overlays.items():
        if label not in overlays:
            stale.extend(_part_ids(label, prev))
    # Never delete a part the new document references (same digest, other
    # per_point: the old and the new series share ids).
    stale = sorted(set(stale) - referenced)
    doc["overlays"] = overlays
    doc["schema"] = STATE_SCHEMA

    # Switch the document first, then drop the parts it no longer references.
    if write_collection_metadata(client, collection_name, {INDEX_STATE_KEY: doc}):
        stats.target = SOURCE_METADATA
        stats.state_bytes = _json_bytes({INDEX_STATE_KEY: doc})
    else:
        stats.target = SOURCE_STATE_POINT
        stats.state_bytes = write_reserved_point(
            client, collection_name, STATE_POINT_ID, {INDEX_STATE_KEY: doc}, layout
        )
    delete_reserved_points(client, collection_name, stale)
    stats.tombstone_points_deleted = len(stale)
    # Parts no document references (a publish stopped before its switch, or
    # its cleanup failed): delete them now. A failure here only leaves
    # unreferenced points behind; the next publish retries.
    try:
        orphans = sorted(
            set(tombstone_point_ids_in_collection(client, collection_name)) - referenced
        )
        delete_reserved_points(client, collection_name, orphans)
        stats.tombstone_points_deleted += len(orphans)
    except Exception as exc:  # noqa: BLE001 - the document is already switched
        log_warn(f"[INDEX STATE] unreferenced tombstone points not cleaned up: {exc}")
    stats.seconds = time.perf_counter() - t0
    return stats


def read_tombstones(client: Any, collection_name: str, entry: dict) -> List[str]:
    """Tombstone keys of one overlay entry of the state document.

    Raises ``RuntimeError`` when parts are missing or the digest does not
    match (a publish was interrupted half-way): the caller then falls back.
    """
    parts = int(entry.get("tombstone_parts") or 0)
    if parts <= 0:
        return []
    label = entry.get("label") or ""
    ids = _part_ids(label, entry)
    payloads = read_reserved_points(client, collection_name, ids)
    keys: List[str] = []
    for pid in ids:
        body = (payloads.get(pid) or {}).get(TOMBSTONES_KEY)
        if not isinstance(body, dict):
            raise RuntimeError(f"tombstone part {pid} of overlay '{label}' is missing")
        keys.extend(body.get("keys") or [])
    digest = entry.get("tombstones_sha256")
    if digest and tombstones_digest(keys) != digest:
        raise RuntimeError(f"tombstones of overlay '{label}' do not match their digest")
    return sorted(set(keys))


class IndexStateCache:
    """Thread-safe, time-limited cache of the index state read from Qdrant.

    Used by the MCP server: the state document is re-read at most every
    ``ttl_s`` seconds, tombstones only when an overlay's digest changes.
    """

    def __init__(self, client_fn: Callable[[], Any], collection_name: str, ttl_s: float = 10.0,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self._client_fn = client_fn
        self._collection = collection_name
        self._ttl = max(0.0, float(ttl_s))
        self._clock = clock
        self._lock = threading.Lock()
        self._state: Tuple[Optional[dict], Optional[str]] = (None, None)
        self._loaded_at: Optional[float] = None
        self._tombstones: Dict[str, Tuple[str, List[str]]] = {}

    def state(self) -> Tuple[Optional[dict], Optional[str]]:
        with self._lock:
            now = self._clock()
            if self._loaded_at is None or now - self._loaded_at >= self._ttl:
                try:
                    self._state = read_index_state(self._client_fn(), self._collection)
                except Exception as exc:  # noqa: BLE001 - keep serving the last state
                    log_warn(f"[INDEX STATE] could not read state from Qdrant: {exc}")
                    if self._loaded_at is None:
                        self._state = (None, None)
                self._loaded_at = now
            return self._state

    def tombstones(self, label: str) -> Optional[List[str]]:
        """Tombstones of *label* from Qdrant; None when Qdrant has no state.

        An overlay that is not in a published state document has no
        tombstones (``[]``): the document lists every indexed overlay.
        """
        doc, _ = self.state()
        if doc is None:
            return None
        entry = (doc.get("overlays") or {}).get(label)
        if not entry:
            return []
        digest = entry.get("tombstones_sha256") or ""
        with self._lock:
            cached = self._tombstones.get(label)
            if cached and cached[0] == digest:
                return list(cached[1])
        try:
            keys = read_tombstones(self._client_fn(), self._collection, {**entry, "label": label})
        except Exception:
            if cached:
                # Keep the last complete set rather than none at all
                log_warn(f"[INDEX STATE] tombstones of {label!r} unreadable; using the previous set")
                return list(cached[1])
            raise
        with self._lock:
            self._tombstones[label] = (digest, keys)
        return list(keys)


def main_branch_from_state(doc: Optional[dict]) -> Optional[str]:
    """Main branch label recorded by the indexer (first repo, sorted by key)."""
    commits = (doc or {}).get("repo_commits") or {}
    for _key, rc in sorted(commits.items()):
        if isinstance(rc, dict) and rc.get("main_branch"):
            return str(rc["main_branch"])
    return None


def serving_tombstones(cache: "IndexStateCache", label: str,
                       fallback: Callable[[], List[str]]) -> List[str]:
    """Overlay tombstones for search: Qdrant first, *fallback* (manifest) else.

    The fallback is used for collections without published state and when
    the tombstone points cannot be read (e.g. a publish is half-way).
    """
    try:
        keys = cache.tombstones(label)
    except Exception as exc:  # noqa: BLE001 - fall back to the manifest
        log_warn(f"[INDEX STATE] tombstones of {label!r} not readable from Qdrant: {exc}")
        keys = None
    if keys is None:
        return list(fallback() or [])
    return keys


# ── Embedding provenance ──────────────────────────────────────────


def _cosine(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _norm_str(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _as_list(vec: Any) -> List[float]:
    if hasattr(vec, "tolist"):
        vec = vec.tolist()
    return [float(x) for x in vec]


def fingerprint_vectors(embed_model: Any, texts: Iterable[str] = FINGERPRINT_TEXTS) -> List[List[float]]:
    """Query embeddings of *texts* through *embed_model* (query prefix applied)."""
    return [_as_list(embed_model.get_query_embedding(t)) for t in texts]


def fingerprint_texts_digest(texts: Iterable[str] = FINGERPRINT_TEXTS) -> str:
    return hashlib.sha256("\x1f".join(texts).encode("utf-8")).hexdigest()[:16]


def served_model_name(embed_model: Any) -> Optional[str]:
    """Model name the embedding endpoint reports, when it reports one."""
    fn = getattr(embed_model, "served_model_name", None)
    if not callable(fn):
        return None
    try:
        return fn()
    except Exception:  # noqa: BLE001 - informational only
        return None


def expected_sparse_model(cfg: Any, hybrid: bool) -> Optional[str]:
    if not hybrid:
        return None
    return getattr(cfg, "SPARSE_MODEL_NAME", None) or None


def build_provenance(
    cfg: Any,
    embed_model: Any,
    layout: Optional[dict],
    *,
    backend_family: str,
    vectors: Optional[List[List[float]]] = None,
) -> dict:
    """Provenance record for *cfg* + *embed_model* (computes the fingerprint)."""
    from shared.index_state import utc_iso_now
    from shared.version import __version__

    if vectors is None:
        vectors = fingerprint_vectors(embed_model)
    hybrid = bool(layout and layout.get("hybrid"))
    rounded = [[round(x, _FINGERPRINT_DECIMALS) for x in v] for v in vectors]
    return {
        "schema": PROVENANCE_SCHEMA,
        "model_name": getattr(cfg, "MODEL_NAME", None),
        "quant": _norm_str(getattr(cfg, "EMBEDDING_QUANT", None)) or None,
        "dimension": len(vectors[0]) if vectors else (layout or {}).get("dimension"),
        "distance": (layout or {}).get("distance"),
        "query_prefix": _norm_str(getattr(cfg, "EMBED_QUERY_PREFIX", None)),
        "text_prefix": _norm_str(getattr(cfg, "EMBED_TEXT_PREFIX", None)),
        "truncate_dim": getattr(cfg, "EMBED_TRUNCATE_DIM", None) or None,
        "sparse_model": expected_sparse_model(cfg, hybrid),
        "embed_backend": backend_family,
        "served_model": served_model_name(embed_model),
        "indexer_version": __version__,
        "written_at": utc_iso_now(),
        "fingerprint": {
            "texts_digest": fingerprint_texts_digest(),
            "count": len(rounded),
            "vectors": rounded,
        },
    }


def write_provenance(client: Any, collection_name: str, prov: dict) -> int:
    """Store *prov* in the sentinel point and (without vectors) in metadata.

    Returns the number of bytes written.
    """
    payload = {
        "embed_backend": prov.get("embed_backend"),
        "_provenance_sentinel": True,
        PROVENANCE_KEY: prov,
    }
    size = write_reserved_point(client, collection_name, PROVENANCE_POINT_ID, payload)
    summary = provenance_summary(prov)
    if write_collection_metadata(client, collection_name, {PROVENANCE_KEY: summary}):
        size += _json_bytes({PROVENANCE_KEY: summary})
    return size


def provenance_summary(prov: dict) -> dict:
    """*prov* without the fingerprint vectors (for collection metadata/logs)."""
    out = {k: v for k, v in prov.items() if k != "fingerprint"}
    fp = prov.get("fingerprint") or {}
    if fp:
        out["fingerprint"] = {
            "texts_digest": fp.get("texts_digest"),
            "count": fp.get("count"),
            "vectors_sha256": hashlib.sha256(_canonical(fp.get("vectors")).encode()).hexdigest()[:16],
        }
    return out


def read_provenance(client: Any, collection_name: str) -> Tuple[Optional[dict], Optional[str]]:
    """Return ``(provenance, legacy_backend)`` of a collection.

    ``provenance`` is the full record (None for collections written before
    full provenance existed); ``legacy_backend`` is the old ``embed_backend``
    family string of the sentinel (None when there is no sentinel).
    """
    try:
        payload = read_reserved_points(client, collection_name, [PROVENANCE_POINT_ID]).get(
            PROVENANCE_POINT_ID
        )
    except Exception:
        payload = None
    prov = None
    legacy = None
    if payload:
        legacy = payload.get("embed_backend")
        if isinstance(payload.get(PROVENANCE_KEY), dict):
            prov = payload[PROVENANCE_KEY]
    if prov is None:
        meta = read_collection_metadata(client, collection_name) or {}
        if isinstance(meta.get(PROVENANCE_KEY), dict):
            prov = meta[PROVENANCE_KEY]
    return prov, legacy


@dataclass
class ProvenanceCheck:
    """Outcome of ``verify_provenance``."""

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    min_cosine: Optional[float] = None
    live_dimension: Optional[int] = None

    @property
    def ok(self) -> bool:
        return not self.errors


def fingerprint_min_cosine(cfg: Any) -> float:
    raw = getattr(cfg, "EMBEDDING_FINGERPRINT_MIN_COSINE", None)
    if raw is None:
        return DEFAULT_FINGERPRINT_MIN_COSINE
    value = float(raw)
    if math.isnan(value) or not -1.0 <= value <= 1.0:
        raise ValueError("EMBEDDING_FINGERPRINT_MIN_COSINE must be within [-1, 1]")
    return value


def verify_provenance(
    stored: dict,
    cfg: Any,
    embed_model: Any,
    layout: Optional[dict],
    *,
    live_vectors: Optional[List[List[float]]] = None,
) -> ProvenanceCheck:
    """Compare stored provenance with *cfg* and the live *embed_model*.

    Errors (fatal for the caller): model name, quantization (when both
    sides name one), prefixes, truncate dim, sparse model, real embedding
    dimension vs stored and collection dimension, fingerprint cosine below
    ``EMBEDDING_FINGERPRINT_MIN_COSINE``. Warnings: quantization named on
    one side only, missing fingerprint, fingerprint texts changed.
    """
    check = ProvenanceCheck()
    threshold = fingerprint_min_cosine(cfg)

    def cmp(label: str, stored_v: Any, live_v: Any) -> None:
        if _norm_str(stored_v) != _norm_str(live_v):
            check.errors.append(
                f"{label}: collection was indexed with {stored_v!r}, this server uses {live_v!r}"
            )

    cmp("model name", stored.get("model_name"), getattr(cfg, "MODEL_NAME", None))
    s_quant = _norm_str(stored.get("quant")).lower()
    l_quant = _norm_str(getattr(cfg, "EMBEDDING_QUANT", None)).lower()
    if s_quant and l_quant and s_quant != l_quant:
        check.errors.append(
            f"quantization: collection was indexed with {stored.get('quant')!r}, "
            f"this server uses {getattr(cfg, 'EMBEDDING_QUANT', None)!r}"
        )
    elif s_quant != l_quant:
        check.warnings.append(
            f"quantization named on one side only (collection: {stored.get('quant')!r}, "
            f"config EMBEDDING_QUANT: {getattr(cfg, 'EMBEDDING_QUANT', None)!r}); "
            "relying on the fingerprint"
        )
    cmp("query prefix", stored.get("query_prefix"), getattr(cfg, "EMBED_QUERY_PREFIX", None))
    cmp("document prefix", stored.get("text_prefix"), getattr(cfg, "EMBED_TEXT_PREFIX", None))
    cmp(
        "truncate dim",
        stored.get("truncate_dim") or "",
        getattr(cfg, "EMBED_TRUNCATE_DIM", None) or "",
    )
    hybrid = bool(layout and layout.get("hybrid"))
    live_sparse = expected_sparse_model(cfg, hybrid)
    if stored.get("sparse_model") and live_sparse:
        cmp("sparse model", stored.get("sparse_model"), live_sparse)

    if live_vectors is None and embed_model is None:
        check.warnings.append("no embedding model given; dimension and fingerprint not checked")
        return check
    fp = stored.get("fingerprint") or {}
    texts_ok = fp.get("texts_digest") == fingerprint_texts_digest()
    try:
        vectors = live_vectors if live_vectors is not None else fingerprint_vectors(embed_model)
    except Exception as exc:  # noqa: BLE001 - reported as a clear startup error
        check.errors.append(f"embedding endpoint failed for the fingerprint texts: {exc}")
        return check
    dim = len(vectors[0]) if vectors else None
    check.live_dimension = dim
    if stored.get("dimension") is not None and dim != int(stored["dimension"]):
        check.errors.append(
            f"embedding dimension: collection was indexed with {stored['dimension']}, "
            f"the embedding endpoint returns {dim}"
        )
    if layout and layout.get("dimension") is not None and dim != layout["dimension"]:
        check.errors.append(
            f"embedding dimension: the collection stores {layout['dimension']}-d vectors, "
            f"the embedding endpoint returns {dim}"
        )
    stored_vectors = fp.get("vectors") or []
    if not stored_vectors:
        check.warnings.append("no embedding fingerprint stored; fingerprint not checked")
    elif not texts_ok:
        check.warnings.append("fingerprint texts changed since indexing; fingerprint not checked")
    elif dim is not None and all(len(v) == dim for v in stored_vectors):
        cosines = [_cosine(a, b) for a, b in zip(stored_vectors, vectors)]
        check.min_cosine = min(cosines) if cosines else None
        if check.min_cosine is not None and check.min_cosine < threshold:
            check.errors.append(
                f"embedding fingerprint: min cosine {check.min_cosine:.4f} < {threshold} "
                "(same texts embed differently: different model, weights, quantization "
                "or prefixes)"
            )
        elif check.min_cosine is not None:
            check.info.append(
                f"fingerprint min cosine {check.min_cosine:.6f} (threshold {threshold})"
            )
    return check


def format_provenance(prov: Optional[dict]) -> List[str]:
    """Human-readable lines describing a provenance record."""
    if not prov:
        return ["no embedding provenance stored"]
    fp = prov.get("fingerprint") or {}
    return [
        f"model: {prov.get('model_name')} | quant: {prov.get('quant') or 'unspecified'}"
        f" | backend: {prov.get('embed_backend')}"
        + (f" | served as: {prov['served_model']}" if prov.get("served_model") else ""),
        f"vectors: {prov.get('dimension')}-d {prov.get('distance') or ''}".rstrip()
        + f" | truncate_dim: {prov.get('truncate_dim') or 'native'}"
        + f" | sparse: {prov.get('sparse_model') or 'none'}",
        f"prefixes: query={prov.get('query_prefix')!r} document={prov.get('text_prefix')!r}",
        f"written by indexer {prov.get('indexer_version')} at {prov.get('written_at')}"
        f" | fingerprint: {fp.get('count') or 0} text(s)",
    ]


def families_compatible(stored: Optional[str], current: Optional[str]) -> bool:
    """Legacy backend-family check (collections without full provenance).

    ``tei`` and ``openai`` are HTTP servers that may serve the very same
    model (TEI also answers ``/v1/embeddings``), so they are not flagged;
    ``pytorch`` vs a server family still is.
    """
    if stored is None or current is None or stored == current:
        return True
    server = {"tei", "openai"}
    return stored in server and current in server


class ProvenanceMismatchError(RuntimeError):
    """The embedding setup does not match the collection's provenance."""


def check_serving_provenance(client: Any, collection_name: str, cfg: Any,
                             embed_model: Any) -> List[str]:
    """MCP startup check; returns human-readable provenance lines.

    Logs the stored provenance and the model the endpoint reports, embeds
    the fingerprint texts through *embed_model* and raises
    ``ProvenanceMismatchError`` on any mismatch. Collections without full
    provenance only get a warning (plus a dimension check); the next
    indexer run backfills it.
    """
    layout = collection_vector_params(client, collection_name)
    served = served_model_name(embed_model)
    if served:
        log(f"[MCP] embedding endpoint serves model: {served}")
    stored, legacy = read_provenance(client, collection_name)
    if stored is None:
        from shared.embedding import get_embed_backend_family

        current = get_embed_backend_family(cfg)
        if not families_compatible(legacy, current):
            log_warn(
                f"[MCP] EMBEDDING BACKEND MISMATCH: collection '{collection_name}' was built "
                f"with {legacy}, this server uses {current}; results may be degraded"
            )
        log_warn(
            f"[MCP] WARNING: collection '{collection_name}' has no embedding provenance "
            "(indexed by an older release). Model, quantization and fingerprint are NOT "
            "verified; the next index refresh stores them."
        )
        if layout and layout.get("dimension"):
            dim = len(_as_list(embed_model.get_query_embedding(FINGERPRINT_TEXTS[0])))
            if dim != layout["dimension"]:
                raise ProvenanceMismatchError(
                    f"  - embedding dimension: the collection stores {layout['dimension']}-d "
                    f"vectors, the embedding endpoint returns {dim}"
                )
        return ["no embedding provenance stored (older index; backfilled by the next refresh)"]
    lines = format_provenance(stored)
    log("[MCP] Embedding provenance of the collection:")
    for line in lines:
        log(f"[MCP]   {line}")
    check = verify_provenance(stored, cfg, embed_model, layout)
    for warning in check.warnings:
        log_warn(f"[MCP] provenance warning: {warning}")
    if check.errors:
        raise ProvenanceMismatchError("\n".join(f"  - {e}" for e in check.errors))
    for info in check.info:
        log(f"[MCP] provenance: {info}")
    log("[MCP] embedding provenance verified")
    return lines + check.info
