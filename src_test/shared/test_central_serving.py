# SPDX-License-Identifier: Apache-2.0
"""Centralized serving: indexer publishes state, a serving-only MCP reads it.

Covers the indexer publish step (index_rag), the report rendered from the
Qdrant state with no manifest directory, the sparse-query precompute used
to keep BM25 off the event loop, and the pinned Qdrant image.
"""

from __future__ import annotations

import asyncio
import json
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT / "src"), str(_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from qdrant_client import QdrantClient, models  # noqa: E402

from shared import index_meta as im  # noqa: E402
from shared import index_state  # noqa: E402
from shared.overlay import overlay_manifest_filename  # noqa: E402

from src_test.shared.test_index_meta import DIM, FakeEmbed, NoMetadataClient  # noqa: E402

COLL = "unit_test_collection"


@pytest.fixture
def qclient():
    c = QdrantClient(":memory:")
    c.create_collection(
        COLL,
        vectors_config={"text-dense": models.VectorParams(size=DIM, distance=models.Distance.COSINE)},
        sparse_vectors_config={"text-sparse": models.SparseVectorParams()},
    )
    return c


def _main_manifest():
    return {
        "files": {"src/a.py": {"vector_ids": ["1"]}, "src/b.py": {"vector_ids": ["2"]}},
        "repo_commits": {"repo": {"main_branch": "master", "commit": "a" * 40,
                                  "indexed_at": "2026-01-01T00:00:00Z"}},
        "index_run": {"completed_at": "2026-01-01T00:00:00Z", "embed_backend": "tei",
                      "indexer_version": "0.0.0", "mode": "refresh"},
        "indexer_version": "0.0.0",
    }


def _write_overlay(index_dir: Path, label: str, tombstones, files=None, kind="branch"):
    data = {"branch": label, "kind": kind, "merge_base": "b" * 40,
            "last_branch_commit": "c" * 40, "overlay_signature": "sig",
            "files": files or {"src/c.py": {"vector_ids": ["3"]}}, "tombstones": tombstones}
    (index_dir / overlay_manifest_filename(label)).write_text(json.dumps(data), encoding="utf-8")


# ── Indexer: publish ─────────────────────────────────────────────


@pytest.fixture
def indexer(tmp_path, qclient):
    from src_test._index_rag_loader import load_index_rag, make_fake_config

    cfg = make_fake_config(tmp_path, QDRANT_HOST="localhost", QDRANT_PORT=6333,
                           SPARSE_MODEL_NAME="Qdrant/bm25", USE_TEI=True)
    mod = load_index_rag(cfg)
    mod.get_qdrant_client = lambda *_a, **_k: qclient
    mod.get_embed_model = lambda **_k: FakeEmbed()
    return mod, cfg, Path(cfg.get_index_path())


def test_publish_end_of_run_with_overlays_and_backfill(indexer, qclient):
    mod, cfg, index_dir = indexer
    _write_overlay(index_dir, "feature/x", ["src/b.py"])
    big = [f"gone/{i}.py" for i in range(2300)]
    _write_overlay(index_dir, "v1.0", big, kind="tag")
    mod._STATE_MAIN_MANIFEST = _main_manifest()

    with patch.object(qclient, "create_payload_index") as cpi:
        mod._publish_index_state("end of run", ensure_provenance=True)
    assert cpi.call_args.kwargs["field_name"] == "file_path"

    doc, source = im.read_index_state(qclient, COLL)
    assert source == im.SOURCE_METADATA
    assert doc["indexed_files"] == 2
    assert doc["repo_commits"]["repo"]["commit"] == "a" * 40
    assert set(doc["overlays"]) == {"feature/x", "v1.0"}
    assert doc["overlays"]["v1.0"]["kind"] == "tag"
    assert doc["overlays"]["v1.0"]["tombstone_parts"] == 3
    # No per-file entries in the state document
    assert "src/a.py" not in json.dumps(doc)
    cache = im.IndexStateCache(lambda: qclient, COLL)
    assert cache.tombstones("feature/x") == ["src/b.py"]
    assert cache.tombstones("v1.0") == sorted(big)
    # Provenance backfilled
    prov, _ = im.read_provenance(qclient, COLL)
    assert prov["model_name"] == "unit-test-model" and prov["dimension"] == DIM


def test_publish_after_overlay_removed(indexer, qclient):
    mod, cfg, index_dir = indexer
    _write_overlay(index_dir, "feature/x", ["src/b.py"])
    mod._STATE_MAIN_MANIFEST = _main_manifest()
    mod._publish_index_state("overlay feature/x")
    (index_dir / overlay_manifest_filename("feature/x")).unlink()
    mod._publish_index_state("end of run")
    doc, _ = im.read_index_state(qclient, COLL)
    assert doc["overlays"] == {}
    first = im.read_index_state(qclient, COLL)[0]
    assert first["overlays"] == {}
    points, _ = qclient.scroll(COLL, limit=100, with_payload=True)
    assert not [p for p in points if im.TOMBSTONES_KEY in (p.payload or {})]


def test_publish_falls_back_without_metadata(indexer, qclient):
    mod, cfg, index_dir = indexer
    proxy = NoMetadataClient(qclient)
    mod.get_qdrant_client = lambda *_a, **_k: proxy
    mod._STATE_MAIN_MANIFEST = _main_manifest()
    mod._publish_index_state("end of run")
    doc, source = im.read_index_state(proxy, COLL)
    assert source == im.SOURCE_STATE_POINT and doc["indexed_files"] == 2


def test_publish_disabled_and_failures_are_warnings(indexer, qclient):
    mod, cfg, index_dir = indexer
    mod._STATE_MAIN_MANIFEST = _main_manifest()
    cfg.INDEX_STATE_PUBLISH = False
    mod._publish_index_state("end of run")
    assert im.read_index_state(qclient, COLL) == (None, None)
    cfg.INDEX_STATE_PUBLISH = True

    def boom(*_a, **_k):
        raise ConnectionError("qdrant down")

    mod.get_qdrant_client = boom
    mod._publish_index_state("end of run")  # must not raise


def test_backfill_skipped_on_dimension_mismatch(indexer, qclient):
    mod, cfg, index_dir = indexer
    mod.get_embed_model = lambda **_k: FakeEmbed(dim=DIM + 3)
    mod._STATE_MAIN_MANIFEST = _main_manifest()
    mod._publish_index_state("end of run", ensure_provenance=True)
    assert im.read_provenance(qclient, COLL)[0] is None


def test_file_path_index_optional(indexer, qclient):
    mod, cfg, _ = indexer
    cfg.QDRANT_FILE_PATH_INDEX = False
    with patch.object(qclient, "create_payload_index") as cpi:
        mod.ensure_file_path_payload_index(qclient)
    cpi.assert_not_called()
    cfg.QDRANT_FILE_PATH_INDEX = True
    with patch.object(qclient, "create_payload_index") as cpi:
        mod.ensure_file_path_payload_index(qclient)
    assert cpi.call_count == 1
    # Already indexed: not created again
    info = qclient.get_collection(COLL)
    info.payload_schema = {"file_path": object()}
    with patch.object(qclient, "get_collection", return_value=info), patch.object(
        qclient, "create_payload_index"
    ) as cpi:
        mod.ensure_file_path_payload_index(qclient)
    cpi.assert_not_called()


def test_new_collection_gets_full_provenance(indexer, qclient):
    mod, cfg, _ = indexer
    mod._write_new_collection_provenance(qclient, FakeEmbed(), DIM)
    prov, legacy = im.read_provenance(qclient, COLL)
    assert legacy == "tei" and prov["fingerprint"]["count"] == len(im.FINGERPRINT_TEXTS)


# ── Serving-only report (no manifest directory) ──────────────────


def _serving_cfg(tmp_path):
    missing = tmp_path / "no-such-index-dir"
    return types.SimpleNamespace(
        COLLECTION_NAME=COLL, QDRANT_HOST="qdrant-host", QDRANT_PORT=6333,
        MCP_SERVER_NAME="central-rag", get_index_path=lambda: str(missing),
    )


def test_report_from_qdrant_state_without_manifest(tmp_path, qclient):
    overlays = {"feature/x": {"branch": "feature/x", "kind": "branch", "last_branch_commit": "c" * 40,
                              "file_count": 4}}
    doc = index_state.build_state_document(_main_manifest(), {}, COLL)
    doc["overlays"] = overlays
    im.publish_index_state(qclient, COLL, doc, {"feature/x": ["d1", "d2"]})
    cfg = _serving_cfg(tmp_path)
    state, source = im.IndexStateCache(lambda: qclient, COLL).state()
    report = index_state.build_index_state_report(
        cfg, state=state, state_source=source, provenance_lines=["model: m | quant: fp16"])
    assert "- state_source: qdrant collection metadata" in report
    assert "- indexed_files: 2" in report
    assert "indexed_commit: " + "a" * 40 in report
    assert "feature/x@ccccccc (4 files, 2 deleted)" in report
    assert "## Embedding provenance" in report and "quant: fp16" in report
    assert not Path(cfg.get_index_path()).exists()


def test_report_without_state_or_manifest(tmp_path):
    report = index_state.build_index_state_report(_serving_cfg(tmp_path))
    assert "No index manifest found" in report


def test_report_manifest_path_unchanged(tmp_path):
    index_dir = tmp_path / "idx"
    index_dir.mkdir()
    (index_dir / "index_manifest.json").write_text(json.dumps(_main_manifest()), encoding="utf-8")
    _write_overlay(index_dir, "feature/x", ["gone.py"])
    cfg = types.SimpleNamespace(COLLECTION_NAME=COLL, MCP_SERVER_NAME="s", get_index_path=lambda: str(index_dir))
    report = index_state.build_index_state_report(cfg)
    assert "state_source" not in report and "deleted" not in report
    assert "feature/x@ccccccc (1 files)" in report


# ── Sparse query precompute (BM25 off the event loop) ────────────


def test_precomputed_sparse_fn_context_isolation():
    import threading

    from qdrant.vector_store import PrecomputedSparseQueryFn, precompute_sparse_query

    calls = []

    def encoder(texts):
        calls.append((texts[0], threading.current_thread() is threading.main_thread()))
        return [[len(texts[0])]], [[1.0]]

    fn = PrecomputedSparseQueryFn(encoder)
    store = types.SimpleNamespace(_sparse_query_fn=fn)

    async def request(q):
        assert await precompute_sparse_query(store, q)
        await asyncio.sleep(0)  # let the other request run in between
        return fn([q])

    async def main():
        return await asyncio.gather(request("aa"), request("bbbb"))

    results = asyncio.run(main())
    assert results == [([[2]], [[1.0]]), ([[4]], [[1.0]])]
    # Encoded once per request, in worker threads
    assert sorted(calls) == [("aa", False), ("bbbb", False)]
    # Without precompute (or for another text) it encodes inline as before
    assert fn(["cc"]) == ([[2]], [[1.0]])
    assert calls[-1] == ("cc", True)


def test_precompute_noop_for_dense_store():
    from qdrant.vector_store import precompute_sparse_query

    assert asyncio.run(precompute_sparse_query(types.SimpleNamespace(_sparse_query_fn=None), "q")) is False


# ── Pinned Qdrant image ──────────────────────────────────────────


def test_qdrant_image_pinned_and_configurable():
    from shared import docker_utils as du

    assert du.QDRANT_IMAGE.endswith(":v1.17.0") and ":latest" not in du.QDRANT_IMAGE
    assert du.get_qdrant_image(types.SimpleNamespace()) == du.QDRANT_IMAGE
    assert du.get_qdrant_image(types.SimpleNamespace(QDRANT_DOCKER_IMAGE="  ")) == du.QDRANT_IMAGE
    custom = types.SimpleNamespace(QDRANT_DOCKER_IMAGE="registry.local/qdrant:v1.16.3")
    assert du.get_qdrant_image(custom) == "registry.local/qdrant:v1.16.3"
    with patch.object(du, "_run_docker") as run:
        du._create_container("ctr", 6333, "/vol", "registry.local/qdrant:v1.16.3")
    assert run.call_args[0][0][-1] == "registry.local/qdrant:v1.16.3"
