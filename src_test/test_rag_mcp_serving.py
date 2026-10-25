# SPDX-License-Identifier: Apache-2.0
"""Serving-only MCP server: no manifest directory, state from Qdrant.

Runs ``rag_mcp.main()`` with Docker/TEI/network replaced by fakes and an
in-memory Qdrant, then calls the registered tools in-process.
"""

from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _p in (str(_ROOT / "src"), str(_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from qdrant_client import QdrantClient, models  # noqa: E402

import rag_mcp  # noqa: E402
from shared import index_meta as im  # noqa: E402
from shared import index_state  # noqa: E402
from src_test.shared.test_index_meta import DIM, FakeEmbed  # noqa: E402

COLL = "serving_test"


def _cfg(tmp_path, **kw):
    import config as base

    values = {k: getattr(base, k) for k in dir(base) if k.isupper()}
    missing = tmp_path / "no-manifest-here"
    values.update(
        COLLECTION_NAME=COLL,
        MODEL_NAME="org/model-a",
        MCP_EMBED_DEVICE="cpu",
        INDEXING_MODE="dense",
        USE_TEI=False,
        SOURCE_DIRS=[],
        get_index_path=lambda: str(missing),
    )
    values.update(kw)
    return types.SimpleNamespace(**values)


@pytest.fixture
def qclient():
    c = QdrantClient(":memory:")
    c.create_collection(
        COLL, vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE)
    )
    return c


def _publish(qclient, cfg, family="tei"):
    layout = im.collection_vector_params(qclient, COLL)
    im.write_provenance(qclient, COLL, im.build_provenance(cfg, FakeEmbed(), layout, backend_family=family))
    manifest = {
        "files": {"a.py": {}},
        "repo_commits": {"repo": {"main_branch": "master", "commit": "f" * 40}},
        "index_run": {"completed_at": "2026-01-02T03:04:05Z", "embed_backend": family},
    }
    doc = index_state.build_state_document(manifest, {}, COLL)
    doc["overlays"] = {"feature/y": {"branch": "feature/y", "kind": "branch",
                                     "last_branch_commit": "e" * 40, "file_count": 1}}
    im.publish_index_state(qclient, COLL, doc, {"feature/y": ["a.py"]})


def _run_main(cfg, qclient, argv, embed=None, tool=None):
    """Run main(); with *tool*, call that tool while the fakes are active."""
    captured = {}

    def fake_run(self, *a, **k):
        captured["mcp"] = self

    from mcp.server.fastmcp import FastMCP
    import qdrant.vector_store as vs
    from llama_index.core import VectorStoreIndex

    with patch.object(sys, "argv", ["rag_mcp.py", *argv]), \
            patch.object(rag_mcp.config_loader, "get_config", return_value=cfg), \
            patch.object(rag_mcp, "ensure_qdrant_running", return_value=True), \
            patch.object(rag_mcp, "ensure_tei_running", side_effect=AssertionError("TEI started")), \
            patch.object(rag_mcp, "get_qdrant_client", return_value=qclient), \
            patch("shared.embedding.get_embed_model", return_value=embed or FakeEmbed()), \
            patch.object(vs, "get_qdrant_vector_store",
                         return_value=(types.SimpleNamespace(vector_store=object()), None, None)), \
            patch.object(VectorStoreIndex, "from_vector_store", return_value=object()), \
            patch.object(FastMCP, "run", fake_run):
        rag_mcp.main()
        if tool:
            return _tool_text(asyncio.run(captured["mcp"].call_tool(tool, {})))
    return captured["mcp"]


def _tool_text(result):
    content = result[0] if isinstance(result, tuple) else result
    return "".join(getattr(c, "text", "") for c in content)


def test_get_index_state_from_qdrant_without_manifest(tmp_path, qclient):
    cfg = _cfg(tmp_path)
    _publish(qclient, cfg)
    text = _run_main(cfg, qclient, ["--lazy-init"], tool="get_index_state")
    assert "state_source: qdrant collection metadata" in text
    assert "indexed_commit: " + "f" * 40 in text
    assert "feature/y@eeeeeee (1 files, 1 deleted)" in text
    assert not Path(cfg.get_index_path()).exists()


def test_get_index_state_old_collection_no_manifest(tmp_path, qclient):
    text = _run_main(_cfg(tmp_path), qclient, ["--lazy-init"], tool="get_index_state")
    assert "No index manifest found" in text


def test_remote_mode_ignores_tei_and_accepts_tei_built_collection(tmp_path, qclient):
    cfg = _cfg(tmp_path, EMBEDDING_MODE="remote", EMBEDDING_URL="http://embed:8080", USE_TEI=True)
    _publish(qclient, cfg, family="tei")
    # Eager build: provenance verified, TEI never started
    text = _run_main(cfg, qclient, [], tool="get_index_state")
    assert "## Embedding provenance" in text and "org/model-a" in text


def test_wrong_model_is_fatal_at_startup(tmp_path, qclient):
    _publish(qclient, _cfg(tmp_path))
    with pytest.raises(SystemExit) as exc:
        _run_main(_cfg(tmp_path, MODEL_NAME="org/other"), qclient, [])
    assert exc.value.code == 1


def test_wrong_weights_fingerprint_is_fatal(tmp_path, qclient):
    cfg = _cfg(tmp_path)
    _publish(qclient, cfg)
    with pytest.raises(SystemExit):
        _run_main(cfg, qclient, [], embed=FakeEmbed(seed="random-vectors"))


def test_wrong_dimension_on_old_collection_is_fatal(tmp_path, qclient):
    with pytest.raises(SystemExit):
        _run_main(_cfg(tmp_path), qclient, [], embed=FakeEmbed(dim=DIM * 2))


def test_local_tei_mode_still_ensures_tei(tmp_path, qclient):
    with pytest.raises(AssertionError, match="TEI started"):
        _run_main(_cfg(tmp_path, USE_TEI=True), qclient, ["--lazy-init"])


def test_search_tool_asks_for_english_queries(tmp_path, qclient):
    """Clients see the English-query rule in the query schema and server instructions."""
    mcp = _run_main(_cfg(tmp_path), qclient, ["--lazy-init"])
    assert mcp.instructions == rag_mcp.SERVER_INSTRUCTIONS
    assert "English" in mcp.instructions
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    search = next(t for t in tools.values() if "query" in t.inputSchema.get("properties", {}))
    desc = search.inputSchema["properties"]["query"]["description"]
    assert desc == rag_mcp.QUERY_PARAMETER_DESCRIPTION
    assert desc.startswith("Search query, written in English.")
    assert "\"Accès refusé à l'opération\"" in desc
    assert "verbatim" in desc
