# SPDX-License-Identifier: Apache-2.0
"""The MCP search tool and run_query share one retrieval pipeline."""

import asyncio
import json
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest
from llama_index.core.schema import NodeWithScore, TextNode

import shared.search as search_mod
from qdrant.vector_store import PrecomputedSparseQueryFn
from shared.query_shape import alpha_for_query

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT / "src"), str(_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TOP_K = 4
TOPIC = "topic"


def _spec(node_id, score, file_path, node_type, text, branch=None, stamp_alpha=False, **meta):
    payload = {"file_path": file_path, "node_type": node_type}
    if branch is not None:
        payload["branch"] = branch
    payload.update(meta)
    return {
        "id": node_id,
        "score": score,
        "text": text,
        "stamp_alpha": stamp_alpha,
        "meta": payload,
    }


def _pool(main, decoy_branch=None):
    """Synthetic chunks. ``decoy_branch`` is a high-score label the filter must drop."""
    rows = [
        _spec(
            "detail-0", 0.90, "src/helper_0.py", "method_declaration",
            "def helper_0():\n    return 0\n", branch=main, stamp_alpha=True,
        ),
        _spec(
            "detail-0-topic", 0.93, "src/helper_0.py", "method_declaration",
            "def helper_0():\n    return 'topic'\n", branch=TOPIC,
        ),
        _spec(
            "gone", 0.95, "src/gone.py", "method_declaration",
            "def gone():\n    return None\n", branch=main,
        ),
        _spec(
            "extra-kept", 0.94, "src/extra.py", "method_declaration",
            "def extra_kept():\n    return 1\n", branch=main,
        ),
        _spec(
            "detail-1", 0.80, "src/helper_1.py", "method_declaration",
            "def helper_1():\n    return 1\n", branch=main,
        ),
        _spec(
            "detail-2", 0.70, "src/helper_2.py", "method_declaration",
            "def helper_2():\n    return 2\n", branch=main,
        ),
        _spec(
            "detail-3", 0.60, "src/helper_3.py", "method_declaration",
            "def helper_3():\n    return 3\n", branch=main,
        ),
        _spec(
            "class-summary", 0.55, "src/widget.py", "class_summary",
            "class Widget:\n    pass\n", branch=main, class_name="Widget",
        ),
        _spec(
            "branchless", 0.40, "docs/notes.md", "block_comment",
            "Notes about the buffer.\n",
        ),
        _spec(
            "foreign", 0.99, "src/foreign.py", "method_declaration",
            "def foreign():\n    return 1\n", branch="elsewhere",
        ),
    ]
    if decoy_branch:
        rows.append(
            _spec(
                "from-state", 0.98, "src/from_state.py", "method_declaration",
                "def from_state():\n    return 1\n", branch=decoy_branch,
            )
        )
    return rows


def _walk(node, visit):
    if node is None:
        return
    visit(node)
    children = list(getattr(node, "must", None) or [])
    children += list(getattr(node, "should", None) or [])
    for child in children:
        _walk(child, visit)


def _match_any(qfilter, key):
    found = []

    def visit(node):
        match = getattr(node, "match", None)
        if getattr(node, "key", None) == key and match is not None:
            found.extend(list(getattr(match, "any", None) or []))

    _walk(qfilter, visit)
    return found


def _payload_branch_allowed(qfilter, branch):
    """True when a chunk with this branch value passes ``qfilter``.

    ``branch is None`` means the payload has no branch key (non-git chunk).
    """
    if qfilter is None:
        return True
    saw = False
    allowed = False

    def visit(node):
        nonlocal saw, allowed
        if getattr(node, "is_empty", None) is not None:
            saw = True
            if branch is None:
                allowed = True
        if getattr(node, "key", None) == "branch":
            names = _match_any(node, "branch")
            if names:
                saw = True
                if branch in names:
                    allowed = True

    _walk(qfilter, visit)
    return allowed if saw else True


class _Client:
    """Qdrant stand-in: symbol lookup is local, every other call hits ``inner``."""

    def __init__(self, inner, main_branch):
        self._inner = inner
        self.main_branch = main_branch

    def _hit(self, qfilter):
        if "flush_buffer" not in (
            _match_any(qfilter, "object_name") + _match_any(qfilter, "symbols")
        ):
            return False
        return _payload_branch_allowed(qfilter, self.main_branch)

    def query_points(self, **kwargs):
        points = ["hit"] if self._hit(kwargs.get("query_filter")) else []
        return types.SimpleNamespace(points=points)

    def scroll(self, **kwargs):
        points = ["hit"] if self._hit(kwargs.get("scroll_filter")) else []
        return points, None

    def __getattr__(self, name):
        return getattr(self._inner, name)


class _Store:
    def __init__(self, client, main_branch):
        self.client = client
        self.collection_name = "parity"
        self.dense_vector_name = "text-dense"
        self.enable_hybrid = True
        self.main_branch = main_branch
        self.encodes = 0
        store = self

        def encode(_texts):
            store.encodes += 1
            return ([[1]], [[1.0]])

        self._sparse_query_fn = PrecomputedSparseQueryFn(encode)

    def parse_to_query_result(self, points):
        if not points:
            return types.SimpleNamespace(nodes=[])
        node = TextNode(
            id_="decl-flush_buffer",
            text="def flush_buffer():\n    return None\n",
            metadata={
                "file_path": "src/buffer.py",
                "node_type": "method_declaration",
                "object_name": "flush_buffer",
                "branch": self.main_branch,
            },
        )
        return types.SimpleNamespace(nodes=[node])


class _Retriever:
    def __init__(self, kwargs, pool):
        self.kwargs = kwargs
        self.pool = pool

    async def aretrieve(self, _query):
        alpha = self.kwargs.get("alpha") or 0.0
        qfilter = (self.kwargs.get("vector_store_kwargs") or {}).get("qdrant_filters")
        k = self.kwargs.get("hybrid_top_k", self.kwargs.get("similarity_top_k"))
        scored = []
        for spec in self.pool:
            branch = spec["meta"].get("branch") if "branch" in spec["meta"] else None
            if not _payload_branch_allowed(qfilter, branch):
                continue
            score = spec["score"]
            if spec["stamp_alpha"]:
                score = round(score + float(alpha), 5)
            scored.append((score, spec))
        scored.sort(key=lambda item: item[0], reverse=True)
        out = []
        for score, spec in scored[:k]:
            node = TextNode(id_=spec["id"], text=spec["text"], metadata=dict(spec["meta"]))
            out.append(NodeWithScore(node=node, score=score))
        return out


class _Index:
    def __init__(self, store, pool):
        self.vector_store = store
        self.pool = pool
        self.calls = []

    def as_retriever(self, **kwargs):
        self.calls.append(kwargs)
        return _Retriever(kwargs, self.pool)


def _pairs(nodes):
    return [(n.node.node_id, n.score) for n in nodes]


def _kw_view(kwargs):
    qfilter = (kwargs.get("vector_store_kwargs") or {}).get("qdrant_filters")
    view = {key: value for key, value in kwargs.items() if key != "vector_store_kwargs"}
    view["branches"] = _match_any(qfilter, "branch")
    return view


def _cfg(tmp_path, collection, git_main):
    import config as base
    from shared.overlay import overlay_manifest_filename

    index_dir = tmp_path / "idx"
    index_dir.mkdir()
    manifest = index_dir / overlay_manifest_filename(TOPIC)
    # Wrong on purpose: Qdrant tombstones are src/gone.py. A manifest fallback
    # would hide src/extra.py instead.
    manifest.write_text(json.dumps({"tombstones": ["src/extra.py"]}), encoding="utf-8")

    if git_main:
        sources = [{
            "type": "git_repo",
            "path": "repo",
            "main_branch": git_main,
            "sources": [{"path": "src", "extensions": [".py"]}],
        }]
    else:
        sources = [{"type": "source_set", "path": "src", "extensions": [".py"]}]

    values = {key: getattr(base, key) for key in dir(base) if key.isupper()}
    values.update(
        COLLECTION_NAME=collection,
        MODEL_NAME="org/model-a",
        MCP_EMBED_DEVICE="cpu",
        INDEXING_MODE="hybrid",
        USE_TEI=False,
        SOURCE_DIRS=sources,
        get_index_path=lambda: str(index_dir),
        HYBRID_ALPHA_MODE="adaptive",
        RERANK_CROSS_ENCODER_MODEL=None,
        RERANK_PROFILE_MENTION=False,
        RERANK_TYPE_INTENT=False,
        RERANK_FILE_CAP=0,
        DEPRIORITIZED_PATHS=(),
        RERANK_PROTOTYPE_YIELD=0.0,
        RERANK_BODY_PREFERENCE=0.0,
    )
    return types.SimpleNamespace(**values)


def _publish(qclient, cfg, collection):
    from shared import index_meta as im
    from shared import index_state

    doc = index_state.build_state_document(
        {
            "files": {},
            "repo_commits": {"repo": {"main_branch": "trunk", "commit": "a" * 40}},
            "index_run": {"completed_at": "2026-01-02T03:04:05Z", "embed_backend": "pytorch"},
        },
        {},
        collection,
    )
    doc["overlays"] = {
        TOPIC: {
            "branch": TOPIC,
            "kind": "branch",
            "last_branch_commit": "b" * 40,
            "file_count": 1,
        }
    }
    im.publish_index_state(qclient, collection, doc, {TOPIC: ["src/gone.py"]})


def _tool_text(result):
    content = result[0] if isinstance(result, tuple) else result
    return "".join(getattr(block, "text", "") for block in content)


def _ids(pairs):
    return [node_id for node_id, _score in pairs]


# ── run_query contract ────────────────────────────────────────


def test_run_query_requires_cfg():
    from shared.validation.runner import run_query

    with pytest.raises(ValueError, match="cfg"):
        run_query(object(), "dense", 0.5, "flush_buffer", cfg=None)


def test_profiles_none_derives_from_config(monkeypatch):
    from shared.validation.runner import run_query

    sentinel = types.SimpleNamespace(names=("python",))
    seen = {}

    def fake_profiles(cfg):
        seen["derived"] = cfg
        return sentinel

    class _Session:
        enabled = False
        base_fetch_k = 2
        fetch_k = 2

        def finish(self, nodes, *, verbose):
            seen["profiles"] = self.profiles
            seen["verbose"] = verbose
            return ["ranked"]

    def begin(_cfg_obj, _query, _top_k, profiles=None):
        session = _Session()
        session.profiles = profiles
        return session

    async def fake_retrieve(*_args, **_kwargs):
        return [], []

    monkeypatch.setattr("shared.reranker.rerank_profiles_for_config", fake_profiles)
    monkeypatch.setattr("shared.cross_encoder.begin_query_rank", begin)
    monkeypatch.setattr("shared.retrieval.aretrieve_with_symbol_lookup", fake_retrieve)

    cfg = types.SimpleNamespace(HYBRID_ALPHA=0.5, HYBRID_ALPHA_MODE="fixed")

    class Index:
        def as_retriever(self, **_kwargs):
            return object()

    assert run_query(Index(), "dense", 0.5, "flush_buffer", top_k=2, cfg=cfg) == ["ranked"]
    assert seen["derived"] is cfg
    assert seen["profiles"] is sentinel
    assert seen["verbose"] is False

    seen.clear()
    run_query(Index(), "dense", 0.5, "flush_buffer", top_k=2, profiles=[], cfg=cfg)
    assert "derived" not in seen
    assert seen["profiles"] == []


def test_timeout_reads_the_mcp_environment(monkeypatch):
    from shared.validation.runner import run_query

    seen = {}

    async def fake_wait(awaitable, timeout):
        seen["timeout"] = timeout
        return await awaitable

    async def fake_retrieve(*_args, **_kwargs):
        return [], []

    monkeypatch.setenv("MCP_QUERY_TIMEOUT_SECONDS", "3.5")
    monkeypatch.setattr(asyncio, "wait_for", fake_wait)
    monkeypatch.setattr("shared.retrieval.aretrieve_with_symbol_lookup", fake_retrieve)

    cfg = types.SimpleNamespace(
        HYBRID_ALPHA=0.5,
        HYBRID_ALPHA_MODE="fixed",
        RERANK_PROFILES=["python"],
        RERANK_CROSS_ENCODER_MODEL=None,
    )

    class Index:
        def as_retriever(self, **_kwargs):
            return object()

    run_query(Index(), "dense", 0.5, "storage layout", top_k=2, cfg=cfg)
    assert seen["timeout"] == 3.5


# ── MCP tool vs run_query ─────────────────────────────────────


QUERIES = [
    ("flush_buffer", ""),
    ("how does the scheduler pick the next task", ""),
    ("What is Widget?", ""),
    ("what units does the buffer export", ""),
    ("flush_buffer", TOPIC),
]


@pytest.mark.parametrize("git_main", [None, "develop"])
def test_mcp_and_run_query_return_the_same_nodes(tmp_path, monkeypatch, git_main):
    """Identifier, natural, overview and overlay queries match, ids and scores."""
    from mcp.server.fastmcp import FastMCP
    from llama_index.core import VectorStoreIndex
    from qdrant_client import QdrantClient, models

    import rag_mcp
    from shared.validation.runner import run_query
    from src_test.shared.test_index_meta import DIM, FakeEmbed

    monkeypatch.delenv("MCP_QUERY_TIMEOUT_SECONDS", raising=False)
    collection = "parity_git" if git_main else "parity_serving"
    main = git_main or "trunk"
    cfg = _cfg(tmp_path, collection, git_main)
    qclient = QdrantClient(":memory:")
    qclient.create_collection(
        collection,
        vectors_config={
            "text-dense": models.VectorParams(size=DIM, distance=models.Distance.COSINE)
        },
        sparse_vectors_config={"text-sparse": models.SparseVectorParams()},
    )
    _publish(qclient, cfg, collection)

    pool = _pool(main, decoy_branch="trunk" if git_main else None)
    store = _Store(_Client(qclient, main), main)
    index = _Index(store, pool)
    recorded = []
    lines = []
    real = search_mod.asearch

    async def spy(index_arg, query, **kwargs):
        nodes = await real(index_arg, query, **kwargs)
        recorded.append(_pairs(nodes))
        return nodes

    monkeypatch.setattr(search_mod, "asearch", spy)
    monkeypatch.setattr(rag_mcp, "log", lambda message: lines.append(message))

    captured = {}

    def fake_run(self, *_args, **_kwargs):
        captured["mcp"] = self

    import qdrant.vector_store as vs

    with patch.object(sys, "argv", ["rag_mcp.py", "--lazy-init"]), \
            patch.object(rag_mcp.config_loader, "get_config", return_value=cfg), \
            patch.object(rag_mcp, "ensure_qdrant_running", return_value=True), \
            patch.object(
                rag_mcp, "ensure_tei_running", side_effect=AssertionError("TEI started")
            ), \
            patch.object(rag_mcp, "get_qdrant_client", return_value=qclient), \
            patch("shared.embedding.get_embed_model", return_value=FakeEmbed()), \
            patch.object(
                vs, "get_qdrant_vector_store",
                return_value=(types.SimpleNamespace(vector_store=store), None, None),
            ), \
            patch.object(VectorStoreIndex, "from_vector_store", return_value=index), \
            patch.object(FastMCP, "run", fake_run):
        rag_mcp.main()
        mcp = captured["mcp"]
        for query, branch in QUERIES:
            before = store.encodes
            log_at = len(lines)
            args = {"query": query, "top_k": TOP_K}
            if branch:
                args["branch"] = branch
            text = _tool_text(asyncio.run(mcp.call_tool("search_rag", args)))
            mcp_pairs = recorded[-1]
            run_pairs = _pairs(run_query(
                index, "hybrid", cfg.HYBRID_ALPHA, query, top_k=TOP_K, cfg=cfg, branch=branch,
            ))
            assert recorded[-1] == run_pairs
            assert mcp_pairs == run_pairs, (query, branch, mcp_pairs, run_pairs)
            assert _kw_view(index.calls[-1]) == _kw_view(index.calls[-2])
            _shape, expected_alpha = alpha_for_query(cfg, query, base_alpha=cfg.HYBRID_ALPHA)
            assert index.calls[-1]["alpha"] == expected_alpha
            assert _kw_view(index.calls[-1])["branches"] == ([main, TOPIC] if branch else [main])
            assert store.encodes == before + 2
            fresh = lines[log_at:]
            assert any(
                f"branch filter: main={main}, feature={branch or 'none'}" in line
                for line in fresh
            )
            assert "FILE:" in text

    by_query = {}
    # Re-read the paired results from the last loop via a second pass stored above.
    # ``recorded`` is [mcp, run, mcp, run, ...] in QUERIES order.
    for i, (query, branch) in enumerate(QUERIES):
        by_query[(query, branch)] = _ids(recorded[i * 2])

    ident = by_query[("flush_buffer", "")]
    natural = by_query[("how does the scheduler pick the next task", "")]
    overview = by_query[("What is Widget?", "")]
    narrow = by_query[("what units does the buffer export", "")]
    feature = by_query[("flush_buffer", TOPIC)]

    assert "decl-flush_buffer" in ident
    assert "detail-0" in ident
    assert "gone" in ident
    assert "extra-kept" in ident
    assert "foreign" not in ident
    assert "class-summary" not in ident
    assert "detail-0-topic" not in ident

    assert "decl-flush_buffer" not in natural
    assert "class-summary" not in natural
    assert "foreign" not in natural

    assert "class-summary" in overview
    assert "foreign" not in overview

    # Pascal-only overview phrasing. Python is the only active profile, so
    # this is not an overview query and the low-score summary stays out.
    assert "class-summary" not in narrow
    assert "foreign" not in narrow

    assert "detail-0-topic" in feature
    assert "extra-kept" in feature
    assert "decl-flush_buffer" in feature
    assert "detail-0" not in feature
    assert "gone" not in feature
    assert "foreign" not in feature
    if git_main:
        assert "from-state" not in ident
        assert "from-state" not in feature
