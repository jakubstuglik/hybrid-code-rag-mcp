# SPDX-License-Identifier: Apache-2.0
"""Index state, tombstones and embedding provenance stored in Qdrant.

Uses qdrant-client's in-memory mode (supports collection metadata) and a
wrapper that emulates a server without collection metadata.
"""

from __future__ import annotations

import hashlib
import math
import sys
import types
from pathlib import Path

from unittest.mock import patch

import pytest

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from qdrant_client import QdrantClient, models  # noqa: E402

from shared import index_meta as im  # noqa: E402
from shared.branch_dedup import build_branch_filter  # noqa: E402

DIM = 8


class FakeEmbed:
    """Deterministic embedding model: a hash of seed + text."""

    def __init__(self, dim: int = DIM, seed: str = "model-a", served: str | None = None):
        self.dim = dim
        self.seed = seed
        self.served = served
        self.calls = 0

    def get_query_embedding(self, text: str):
        self.calls += 1
        digest = hashlib.sha256(f"{self.seed}|{text}".encode()).digest()
        raw = [(digest[i % len(digest)] - 127.5) / 127.5 for i in range(self.dim)]
        norm = math.sqrt(sum(x * x for x in raw)) or 1.0
        return [x / norm for x in raw]

    def served_model_name(self):
        return self.served


class Noisy(FakeEmbed):
    """Same model as FakeEmbed plus a small perturbation (other precision)."""

    def __init__(self, eps: float, **kw):
        super().__init__(**kw)
        self.eps = eps

    def get_query_embedding(self, text: str):
        vec = super().get_query_embedding(text)
        return [x + (self.eps if i % 2 else -self.eps) for i, x in enumerate(vec)]


class NoMetadataClient:
    """Proxy for a Qdrant server without collection metadata support.

    mode="reject": update_collection(metadata=...) raises;
    mode="ignore": accepted but never stored (get_collection hides it).
    """

    def __init__(self, inner: QdrantClient, mode: str = "reject"):
        self._inner = inner
        self._mode = mode

    def update_collection(self, collection_name, metadata=None, **kw):
        if metadata is not None and self._mode == "reject":
            raise RuntimeError("Unknown field 'metadata'")
        if kw:
            return self._inner.update_collection(collection_name=collection_name, **kw)
        return True

    def get_collection(self, collection_name):
        info = self._inner.get_collection(collection_name=collection_name)
        info.config.metadata = None
        return info

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _cfg(**kw):
    values = dict(
        MODEL_NAME="org/model-a",
        EMBEDDING_QUANT=None,
        EMBED_QUERY_PREFIX=None,
        EMBED_TEXT_PREFIX=None,
        EMBED_TRUNCATE_DIM=None,
        SPARSE_MODEL_NAME="Qdrant/bm25",
        EMBED_BACKEND=None,
        USE_TEI=True,
        EMBEDDING_MODE=None,
    )
    values.update(kw)
    return types.SimpleNamespace(**values)


@pytest.fixture
def client():
    c = QdrantClient(":memory:")
    c.create_collection(
        "dense",
        vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE),
    )
    c.create_collection(
        "hybrid",
        vectors_config={"text-dense": models.VectorParams(size=DIM, distance=models.Distance.COSINE)},
        sparse_vectors_config={"text-sparse": models.SparseVectorParams()},
    )
    return c


def _add_chunk(client, name, pid, branch, file_path="a.py"):
    layout = im.collection_vector_params(client, name)
    vec = FakeEmbed().get_query_embedding(file_path)
    vector = {"text-dense": vec} if layout["names"] else vec
    client.upsert(
        collection_name=name,
        points=[models.PointStruct(id=pid, vector=vector, payload={"branch": branch, "file_path": file_path})],
    )


# ── Helpers ──────────────────────────────────────────────────────


def test_tombstone_ids_are_deterministic_and_distinct():
    assert im.tombstone_point_id("feat", 0, "ab") == im.tombstone_point_id("feat", 0, "ab")
    assert im.tombstone_point_id("feat", 0, "ab") != im.tombstone_point_id("feat", 1, "ab")
    assert im.tombstone_point_id("feat", 0, "ab") != im.tombstone_point_id("other", 0, "ab")
    assert im.tombstone_point_id("feat", 0, "ab") != im.tombstone_point_id("feat", 0, "cd")


def _ids(client, name, label):
    doc, _ = im.read_index_state(client, name)
    return im._part_ids(label, doc["overlays"][label])


def test_chunk_tombstones_sorted_unique_and_bounded():
    parts = im.chunk_tombstones(["c", "a", "b", "a"], per_point=2)
    assert parts == [["a", "b"], ["c"]]
    assert im.chunk_tombstones([], per_point=5) == []
    with pytest.raises(ValueError):
        im.chunk_tombstones(["a"], per_point=0)


def test_vector_layout_unnamed_and_named(client):
    dense = im.collection_vector_params(client, "dense")
    assert dense["dimension"] == DIM and dense["names"] is None and not dense["hybrid"]
    assert dense["distance"].lower() == "cosine"
    hybrid = im.collection_vector_params(client, "hybrid")
    assert hybrid["names"] == ["text-dense"] and hybrid["hybrid"]
    assert im.collection_vector_params(client, "missing") is None


# ── Index state ──────────────────────────────────────────────────


def _doc(*labels):
    return {"collection": "dense", "indexed_files": 3, "repo_commits": {"r": {"commit": "abc"}},
            "overlays": {label: {"branch": label, "kind": "branch"} for label in labels}}


def test_old_collection_without_state(client):
    assert im.read_index_state(client, "dense") == (None, None)
    cache = im.IndexStateCache(lambda: client, "dense")
    assert cache.state() == (None, None)
    assert cache.tombstones("feat") is None  # caller falls back to the manifest


def test_publish_into_metadata(client):
    stats = im.publish_index_state(client, "dense", _doc("feat"), {"feat": ["x.py", "y.py"]})
    assert stats.target == im.SOURCE_METADATA
    assert stats.state_bytes > 0 and stats.tombstone_points_written == 1
    doc, source = im.read_index_state(client, "dense")
    assert source == im.SOURCE_METADATA
    assert doc["repo_commits"]["r"]["commit"] == "abc"
    entry = doc["overlays"]["feat"]
    assert entry["tombstone_count"] == 2 and entry["tombstone_parts"] == 1
    # The state point is not used when metadata works
    assert im.read_reserved_points(client, "dense", [im.STATE_POINT_ID]) == {}
    cache = im.IndexStateCache(lambda: client, "dense")
    assert cache.tombstones("feat") == ["x.py", "y.py"]
    assert cache.tombstones("not-indexed") == []


def test_metadata_patch_keeps_other_keys(client):
    client.update_collection(collection_name="dense", metadata={"owner_key": {"a": 1}})
    im.publish_index_state(client, "dense", _doc(), {})
    meta = im.read_collection_metadata(client, "dense")
    assert meta["owner_key"] == {"a": 1} and im.INDEX_STATE_KEY in meta


@pytest.mark.parametrize("mode", ["reject", "ignore"])
def test_fallback_without_metadata_support(client, mode):
    proxy = NoMetadataClient(client, mode)
    stats = im.publish_index_state(proxy, "hybrid", _doc("feat"), {"feat": ["d.py"]})
    assert stats.target == im.SOURCE_STATE_POINT
    doc, source = im.read_index_state(proxy, "hybrid")
    assert source == im.SOURCE_STATE_POINT
    assert doc["overlays"]["feat"]["tombstone_count"] == 1
    assert im.IndexStateCache(lambda: proxy, "hybrid").tombstones("feat") == ["d.py"]


def test_metadata_wins_over_stale_state_point(client):
    proxy = NoMetadataClient(client, "reject")
    im.publish_index_state(proxy, "dense", {**_doc(), "indexed_files": 1}, {})
    im.publish_index_state(client, "dense", {**_doc(), "indexed_files": 2}, {})
    doc, source = im.read_index_state(client, "dense")
    assert source == im.SOURCE_METADATA and doc["indexed_files"] == 2


def test_oversized_tombstones_split_shrink_and_remove(client):
    keys = [f"dir/file_{i:05d}.py" for i in range(2500)]
    stats = im.publish_index_state(client, "dense", _doc("big"), {"big": keys}, per_point=1000)
    assert stats.tombstone_points_written == 3
    doc, _ = im.read_index_state(client, "dense")
    assert doc["overlays"]["big"]["tombstone_parts"] == 3
    # The state document itself stays small: no keys in metadata
    assert stats.state_bytes < 2000
    cache = im.IndexStateCache(lambda: client, "dense", ttl_s=0)
    assert cache.tombstones("big") == sorted(keys)

    # Unchanged digest: nothing rewritten
    again = im.publish_index_state(client, "dense", _doc("big"), {"big": keys}, per_point=1000)
    assert again.tombstone_points_written == 0 and again.tombstone_points_deleted == 0

    # Shrink to one part: the new set is written next to the old one, then
    # the three old parts are deleted
    old_ids = _ids(client, "dense", "big")
    shrink = im.publish_index_state(client, "dense", _doc("big"), {"big": keys[:10]}, per_point=1000)
    assert shrink.tombstone_points_written == 1 and shrink.tombstone_points_deleted == 3
    assert im.read_reserved_points(client, "dense", old_ids) == {}
    new_ids = _ids(client, "dense", "big")
    assert len(new_ids) == 1 and list(im.read_reserved_points(client, "dense", new_ids)) == new_ids
    assert cache.tombstones("big") == sorted(keys[:10])

    # Overlay removed from config: all its parts deleted
    gone = im.publish_index_state(client, "dense", _doc(), {})
    assert gone.tombstone_points_deleted == 1
    assert im.read_reserved_points(client, "dense", new_ids) == {}
    assert cache.tombstones("big") == []


def test_reader_of_previous_document_keeps_its_tombstones(client):
    im.publish_index_state(client, "dense", _doc("feat"), {"feat": ["a"]})
    old_doc, _ = im.read_index_state(client, "dense")
    cache = im.IndexStateCache(lambda: client, "dense", ttl_s=0)
    assert cache.tombstones("feat") == ["a"]
    # Simulate the window after the new parts are written but before the
    # metadata switch: old parts still readable through the old document
    with patch.object(im, "delete_reserved_points"):
        im.publish_index_state(client, "dense", _doc("feat"), {"feat": ["a", "b"]})
    entry = {**old_doc["overlays"]["feat"], "label": "feat"}
    assert im.read_tombstones(client, "dense", entry) == ["a"]
    assert cache.tombstones("feat") == ["a", "b"]


def test_unreadable_parts_fall_back_to_previous_set(client):
    im.publish_index_state(client, "dense", _doc("feat"), {"feat": ["a"]})
    cache = im.IndexStateCache(lambda: client, "dense", ttl_s=0)
    assert cache.tombstones("feat") == ["a"]
    im.publish_index_state(client, "dense", _doc("feat"), {"feat": ["a", "b"]})
    im.delete_reserved_points(client, "dense", _ids(client, "dense", "feat"))
    assert cache.tombstones("feat") == ["a"]  # stale but complete


def test_missing_tombstone_part_raises_and_serving_falls_back(client):
    keys = [f"k{i}" for i in range(5)]
    im.publish_index_state(client, "dense", _doc("feat"), {"feat": keys}, per_point=2)
    im.delete_reserved_points(client, "dense", [_ids(client, "dense", "feat")[1]])
    cache = im.IndexStateCache(lambda: client, "dense")
    with pytest.raises(RuntimeError, match="missing"):
        cache.tombstones("feat")
    assert im.serving_tombstones(cache, "feat", lambda: ["from-manifest"]) == ["from-manifest"]


def test_serving_tombstones_prefers_qdrant(client):
    im.publish_index_state(client, "dense", _doc("feat"), {"feat": ["q.py"]})
    cache = im.IndexStateCache(lambda: client, "dense")
    assert im.serving_tombstones(cache, "feat", lambda: ["manifest.py"]) == ["q.py"]
    empty = im.IndexStateCache(lambda: client, "hybrid")  # nothing published
    assert im.serving_tombstones(empty, "feat", lambda: ["manifest.py"]) == ["manifest.py"]


def test_digest_mismatch_raises(client):
    im.publish_index_state(client, "dense", _doc("feat"), {"feat": ["a", "b"]})
    doc, _ = im.read_index_state(client, "dense")
    pid = _ids(client, "dense", "feat")[0]
    im.write_reserved_point(client, "dense", pid, {im.TOMBSTONES_KEY: {"keys": ["a"]}})
    entry = {**doc["overlays"]["feat"], "label": "feat"}
    with pytest.raises(RuntimeError, match="digest"):
        im.read_tombstones(client, "dense", entry)


def test_state_cache_ttl_and_errors(client):
    now = [0.0]
    reads = []

    def client_fn():
        reads.append(1)
        return client

    cache = im.IndexStateCache(client_fn, "dense", ttl_s=10, clock=lambda: now[0])
    cache.state()
    cache.state()
    assert len(reads) == 1
    now[0] = 11
    cache.state()
    assert len(reads) == 2

    im.publish_index_state(client, "dense", _doc(), {})
    now[0] = 30
    assert cache.state()[0] is not None

    def broken():
        raise ConnectionError("down")

    cache._client_fn = broken
    now[0] = 50
    assert cache.state()[0] is not None  # keeps serving the last good state


def test_reserved_points_hidden_by_branch_filter(client):
    _add_chunk(client, "hybrid", 1, "master", "a.py")
    _add_chunk(client, "hybrid", 2, "feat", "b.py")
    im.publish_index_state(NoMetadataClient(client), "hybrid", _doc("feat"), {"feat": ["c.py"]})
    im.write_provenance(client, "hybrid", im.build_provenance(
        _cfg(), FakeEmbed(), im.collection_vector_params(client, "hybrid"), backend_family="tei"))
    flt = build_branch_filter(main_branch="master", feature_branch="feat")
    points, _ = client.scroll("hybrid", scroll_filter=flt, limit=100, with_payload=True)
    assert sorted(p.id for p in points) == [1, 2]
    # Reserved points carry the reserved branch label
    total, _ = client.scroll("hybrid", limit=100, with_payload=True)
    reserved = [p for p in total if (p.payload or {}).get("branch") == im.RESERVED_BRANCH]
    assert len(reserved) == 3  # state point, tombstone part, provenance sentinel


# ── Provenance ───────────────────────────────────────────────────


def _store(client, name="dense", cfg=None, model=None, family="tei"):
    cfg = cfg or _cfg()
    model = model or FakeEmbed()
    prov = im.build_provenance(cfg, model, im.collection_vector_params(client, name),
                               backend_family=family)
    im.write_provenance(client, name, prov)
    return prov


def test_provenance_roundtrip_and_metadata_summary(client):
    prov = _store(client, cfg=_cfg(EMBEDDING_QUANT="fp16"), model=FakeEmbed(served="org/model-a"))
    stored, legacy = im.read_provenance(client, "dense")
    assert legacy == "tei"
    assert stored["model_name"] == "org/model-a" and stored["quant"] == "fp16"
    assert stored["dimension"] == DIM and stored["distance"].lower() == "cosine"
    assert stored["served_model"] == "org/model-a"
    assert len(stored["fingerprint"]["vectors"]) == len(im.FINGERPRINT_TEXTS)
    meta = im.read_collection_metadata(client, "dense")[im.PROVENANCE_KEY]
    assert "vectors" not in meta["fingerprint"] and meta["model_name"] == prov["model_name"]
    lines = im.format_provenance(stored)
    assert any("org/model-a" in line and "fp16" in line for line in lines)


def test_provenance_from_metadata_when_sentinel_missing(client):
    _store(client)
    im.delete_reserved_points(client, "dense", [im.PROVENANCE_POINT_ID])
    stored, legacy = im.read_provenance(client, "dense")
    assert legacy is None and stored["model_name"] == "org/model-a"
    check = im.verify_provenance(stored, _cfg(), FakeEmbed(), im.collection_vector_params(client, "dense"))
    assert check.ok and any("fingerprint" in w for w in check.warnings)


def test_verify_same_setup_passes(client):
    stored = _store(client)
    check = im.verify_provenance(stored, _cfg(), FakeEmbed(), im.collection_vector_params(client, "dense"))
    assert check.ok, check.errors
    assert check.min_cosine == pytest.approx(1.0, abs=1e-5)


def test_verify_other_precision_passes(client):
    stored = _store(client)
    check = im.verify_provenance(stored, _cfg(), Noisy(1e-3), im.collection_vector_params(client, "dense"))
    assert check.ok and check.min_cosine > 0.99


@pytest.mark.parametrize(
    "cfg_kw, model, needle",
    [
        ({"MODEL_NAME": "org/other"}, None, "model name"),
        ({"EMBED_QUERY_PREFIX": "query: "}, None, "query prefix"),
        ({"EMBED_TEXT_PREFIX": "passage: "}, None, "document prefix"),
        ({"EMBED_TRUNCATE_DIM": 4}, None, "truncate dim"),
        ({}, FakeEmbed(seed="other-weights"), "fingerprint"),
        ({}, FakeEmbed(dim=DIM * 2), "dimension"),
    ],
)
def test_verify_mismatches_are_errors(client, cfg_kw, model, needle):
    stored = _store(client)
    check = im.verify_provenance(stored, _cfg(**cfg_kw), model or FakeEmbed(),
                                 im.collection_vector_params(client, "dense"))
    assert not check.ok
    assert any(needle in e for e in check.errors), check.errors


def test_verify_quant(client):
    stored = _store(client, cfg=_cfg(EMBEDDING_QUANT="fp16"))
    layout = im.collection_vector_params(client, "dense")
    bad = im.verify_provenance(stored, _cfg(EMBEDDING_QUANT="q8_0"), FakeEmbed(), layout)
    assert any("quantization" in e for e in bad.errors)
    same = im.verify_provenance(stored, _cfg(EMBEDDING_QUANT="FP16"), FakeEmbed(), layout)
    assert same.ok and not same.warnings
    one_side = im.verify_provenance(stored, _cfg(), FakeEmbed(), layout)
    assert one_side.ok and any("one side" in w for w in one_side.warnings)


def test_verify_sparse_model_on_hybrid(client):
    stored = _store(client, name="hybrid")
    layout = im.collection_vector_params(client, "hybrid")
    check = im.verify_provenance(stored, _cfg(SPARSE_MODEL_NAME="other/sparse"), FakeEmbed(), layout)
    assert any("sparse model" in e for e in check.errors)


def test_verify_without_model_only_warns(client):
    stored = _store(client)
    check = im.verify_provenance(stored, _cfg(), None, im.collection_vector_params(client, "dense"))
    assert check.ok and check.warnings


def test_verify_endpoint_failure_is_error(client):
    class Down(FakeEmbed):
        def get_query_embedding(self, text):
            raise ConnectionError("refused")

    stored = _store(client)
    check = im.verify_provenance(stored, _cfg(), Down(), im.collection_vector_params(client, "dense"))
    assert any("endpoint failed" in e for e in check.errors)


def test_fingerprint_threshold_config():
    assert im.fingerprint_min_cosine(_cfg()) == im.DEFAULT_FINGERPRINT_MIN_COSINE
    assert im.fingerprint_min_cosine(_cfg(EMBEDDING_FINGERPRINT_MIN_COSINE=0.5)) == 0.5
    with pytest.raises(ValueError):
        im.fingerprint_min_cosine(_cfg(EMBEDDING_FINGERPRINT_MIN_COSINE=1.5))


def test_threshold_controls_noisy_model(client):
    stored = _store(client)
    layout = im.collection_vector_params(client, "dense")
    strict = _cfg(EMBEDDING_FINGERPRINT_MIN_COSINE=0.999999)
    assert not im.verify_provenance(stored, strict, Noisy(0.05), layout).ok


def test_families_compatible():
    assert im.families_compatible("tei", "openai")
    assert im.families_compatible("openai", "tei")
    assert im.families_compatible("tei", "tei")
    assert im.families_compatible(None, "pytorch")
    assert not im.families_compatible("pytorch", "tei")
    assert not im.families_compatible("openai", "pytorch")


# ── Serving startup check ────────────────────────────────────────


def test_serving_check_passes_and_logs(client):
    _store(client)
    lines = im.check_serving_provenance(client, "dense", _cfg(), FakeEmbed(served="org/model-a"))
    assert any("org/model-a" in line for line in lines)
    assert any("min cosine" in line for line in lines)


def test_serving_check_wrong_model_is_fatal(client):
    _store(client)
    with pytest.raises(im.ProvenanceMismatchError, match="model name"):
        im.check_serving_provenance(client, "dense", _cfg(MODEL_NAME="org/wrong"), FakeEmbed())
    with pytest.raises(im.ProvenanceMismatchError, match="fingerprint"):
        im.check_serving_provenance(client, "dense", _cfg(), FakeEmbed(seed="random"))


def test_serving_check_old_collection_warns_but_checks_dimension(client):
    lines = im.check_serving_provenance(client, "dense", _cfg(), FakeEmbed())
    assert "no embedding provenance" in lines[0]
    with pytest.raises(im.ProvenanceMismatchError, match="dimension"):
        im.check_serving_provenance(client, "dense", _cfg(), FakeEmbed(dim=DIM + 1))


def test_serving_check_legacy_sentinel_tei_vs_openai_passes(client):
    layout = im.collection_vector_params(client, "dense")
    im.write_reserved_point(client, "dense", im.PROVENANCE_POINT_ID,
                            {"embed_backend": "tei", "_provenance_sentinel": True}, layout)
    lines = im.check_serving_provenance(client, "dense", _cfg(EMBEDDING_MODE="remote"), FakeEmbed())
    assert "no embedding provenance" in lines[0]


def test_main_branch_from_state():
    assert im.main_branch_from_state(None) is None
    assert im.main_branch_from_state({"repo_commits": {}}) is None
    doc = {"repo_commits": {"b": {"main_branch": "develop"}, "a": {"main_branch": "main"}}}
    assert im.main_branch_from_state(doc) == "main"
