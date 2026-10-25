# SPDX-License-Identifier: Apache-2.0
"""Optional cross-encoder stage: blend, config, and both query paths."""

import asyncio
import math
import types
from pathlib import Path

import pytest
from llama_index.core.schema import NodeWithScore, TextNode

import shared.cross_encoder as ce
import shared.reranker as reranker_module
import shared.validation.runner as runner_module
from shared.branch_dedup import build_branch_filter
from shared.retrieval import build_retriever_kwargs
from shared.validation.runner import parse_overrides


def _cfg(**kwargs):
    return types.SimpleNamespace(**kwargs)


def _node(node_id: str, score, text: str, file_path: str = "src/widget.c"):
    inner = TextNode(id_=node_id, text=text, metadata={"file_path": file_path, "node_type": "text"})
    return NodeWithScore(node=inner, score=score)


class _FakeEncoder:
    def __init__(self, scores):
        self.scores = scores
        self.calls = []

    def rerank(self, query, documents, batch_size=64, **kwargs):
        docs = list(documents)
        self.calls.append({"query": query, "docs": docs, "batch_size": batch_size})
        if self.scores is None:
            return None
        return iter(self.scores)


@pytest.fixture(autouse=True)
def _clear_cache():
    ce._ENCODERS.clear()
    yield
    ce._ENCODERS.clear()


def _patch_encoder(monkeypatch, scores):
    encoder = _FakeEncoder(scores)
    monkeypatch.setattr(ce, "get_cross_encoder", lambda model_name, device: encoder)
    return encoder


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        return 1.0 / (1.0 + math.exp(-value))
    z = math.exp(value)
    return z / (1.0 + z)


# ── config ────────────────────────────────────────────────────


def test_root_config_defaults_keep_the_stage_off():
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "config.py"
    spec = importlib.util.spec_from_file_location("root_config_cross_encoder", path)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    assert cfg.RERANK_CROSS_ENCODER_MODEL is None
    assert cfg.RERANK_CROSS_ENCODER_POOL == 32
    assert cfg.RERANK_CROSS_ENCODER_WEIGHT == 0.5
    assert cfg.RERANK_CROSS_ENCODER_DOC_CHARS == 1000
    assert cfg.RERANK_CROSS_ENCODER_DEVICE == "cpu"
    assert cfg.RERANK_CROSS_ENCODER_BATCH == 16


def test_missing_keys_use_defaults_and_stay_off():
    assert ce.cross_encoder_model_name(None) is None
    assert ce.cross_encoder_model_name(_cfg()) is None
    assert ce.cross_encoder_model_name(_cfg(RERANK_CROSS_ENCODER_MODEL="  ")) is None
    ce.validate_cross_encoder_settings(None)
    ce.validate_cross_encoder_settings(_cfg(RERANK_CROSS_ENCODER_MODEL=None))
    settings = ce.resolve_cross_encoder_settings(_cfg(RERANK_CROSS_ENCODER_MODEL="org/model"))
    assert settings.pool == 32
    assert settings.weight == 0.5
    assert settings.doc_chars == 1000
    assert settings.device == "cpu"
    assert settings.batch == 16


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"RERANK_CROSS_ENCODER_WEIGHT": 1.1}, "RERANK_CROSS_ENCODER_WEIGHT"),
        ({"RERANK_CROSS_ENCODER_WEIGHT": -0.01}, "RERANK_CROSS_ENCODER_WEIGHT"),
        ({"RERANK_CROSS_ENCODER_WEIGHT": True}, "RERANK_CROSS_ENCODER_WEIGHT"),
        ({"RERANK_CROSS_ENCODER_WEIGHT": "0.5"}, "RERANK_CROSS_ENCODER_WEIGHT"),
        ({"RERANK_CROSS_ENCODER_POOL": 0}, "RERANK_CROSS_ENCODER_POOL"),
        ({"RERANK_CROSS_ENCODER_POOL": -3}, "RERANK_CROSS_ENCODER_POOL"),
        ({"RERANK_CROSS_ENCODER_POOL": True}, "RERANK_CROSS_ENCODER_POOL"),
        ({"RERANK_CROSS_ENCODER_POOL": 32.0}, "RERANK_CROSS_ENCODER_POOL"),
        ({"RERANK_CROSS_ENCODER_DOC_CHARS": 0}, "RERANK_CROSS_ENCODER_DOC_CHARS"),
        ({"RERANK_CROSS_ENCODER_DOC_CHARS": False}, "RERANK_CROSS_ENCODER_DOC_CHARS"),
        ({"RERANK_CROSS_ENCODER_BATCH": 0}, "RERANK_CROSS_ENCODER_BATCH"),
        ({"RERANK_CROSS_ENCODER_DEVICE": "gpu"}, "RERANK_CROSS_ENCODER_DEVICE"),
        ({"RERANK_CROSS_ENCODER_DEVICE": 1}, "RERANK_CROSS_ENCODER_DEVICE"),
        ({"RERANK_CROSS_ENCODER_MODEL": 5}, "RERANK_CROSS_ENCODER_MODEL"),
    ],
)
def test_invalid_settings_raise(kwargs, match):
    with pytest.raises(ValueError, match=match):
        ce.validate_cross_encoder_settings(_cfg(**kwargs))


def test_device_accepts_cpu_and_cuda_case_insensitively():
    cpu = ce.resolve_cross_encoder_settings(_cfg(RERANK_CROSS_ENCODER_DEVICE=" CPU "))
    cuda = ce.resolve_cross_encoder_settings(_cfg(RERANK_CROSS_ENCODER_DEVICE="CUDA"))
    assert cpu.device == "cpu"
    assert cuda.device == "cuda"
    ends = ce.resolve_cross_encoder_settings(
        _cfg(RERANK_CROSS_ENCODER_WEIGHT=0, RERANK_CROSS_ENCODER_WEIGHT_IGNORED=None)
    )
    assert ends.weight == 0.0
    one = ce.resolve_cross_encoder_settings(_cfg(RERANK_CROSS_ENCODER_WEIGHT=1))
    assert one.weight == 1.0


def test_config_loader_rejects_invalid_weight(tmp_path):
    from config_loader import _validate_config

    cfg = types.SimpleNamespace(
        QDRANT_MODE="local",
        SOURCE_DIRS=[],
        RERANK_CROSS_ENCODER_WEIGHT=2,
    )
    with pytest.raises(RuntimeError, match=r"RERANK_CROSS_ENCODER_WEIGHT must be a number in \[0, 1\]"):
        _validate_config(cfg, str(tmp_path / "cfg.py"))


def test_set_overrides_parse_model_pool_and_weight():
    parsed = parse_overrides(
        [
            "RERANK_CROSS_ENCODER_MODEL=jinaai/jina-reranker-v1-turbo-en",
            "RERANK_CROSS_ENCODER_POOL=32",
            "RERANK_CROSS_ENCODER_WEIGHT=0.5",
            "RERANK_CROSS_ENCODER_MODEL_OFF=None",
        ]
    )
    assert parsed["RERANK_CROSS_ENCODER_MODEL"] == "jinaai/jina-reranker-v1-turbo-en"
    assert parsed["RERANK_CROSS_ENCODER_POOL"] == 32
    assert parsed["RERANK_CROSS_ENCODER_WEIGHT"] == 0.5
    assert parsed["RERANK_CROSS_ENCODER_MODEL_OFF"] is None


# ── score_and_blend ───────────────────────────────────────────


def test_blend_weights_zero_half_and_one(monkeypatch):
    nodes = [_node("a", 0.2, "alpha"), _node("b", 0.8, "beta")]
    _patch_encoder(monkeypatch, [0.0, 2.0])
    cfg = _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=0.0)
    off = ce.score_and_blend(nodes, "storage layout", cfg)
    assert [n.node.node_id for n in off] == ["b", "a"]
    assert off[0].score == pytest.approx(0.8)
    assert off[1].score == pytest.approx(0.2)

    half = ce.score_and_blend(
        nodes,
        "storage layout",
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=0.5),
    )
    # a: 0.5 * sigmoid(0) + 0.5 * 0.2 ; b: 0.5 * sigmoid(2) + 0.5 * 0.8
    expect_a = 0.5 * _sigmoid(0.0) + 0.5 * 0.2
    expect_b = 0.5 * _sigmoid(2.0) + 0.5 * 0.8
    by_id = {n.node.node_id: n.score for n in half}
    assert by_id["a"] == pytest.approx(expect_a)
    assert by_id["b"] == pytest.approx(expect_b)
    assert [n.node.node_id for n in half] == ["b", "a"]

    flipped = ce.score_and_blend(
        nodes,
        "storage layout",
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=1),
    )
    assert [n.node.node_id for n in flipped] == ["b", "a"]
    assert flipped[0].score == pytest.approx(_sigmoid(2.0))
    assert flipped[1].score == pytest.approx(_sigmoid(0.0))


def test_weight_one_orders_by_cross_encoder_not_fused_score(monkeypatch):
    nodes = [_node("low", 0.95, "low"), _node("high", 0.05, "high")]
    _patch_encoder(monkeypatch, [-4.0, 4.0])
    out = ce.score_and_blend(
        nodes,
        "storage layout",
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=1),
    )
    assert [n.node.node_id for n in out] == ["high", "low"]
    assert out[0].score == pytest.approx(_sigmoid(4.0))


def test_ties_keep_input_order(monkeypatch):
    nodes = [_node("a", 0.4, "a"), _node("b", 0.4, "b"), _node("c", 0.1, "c")]
    _patch_encoder(monkeypatch, [0.0, 0.0, 0.0])
    out = ce.score_and_blend(
        nodes,
        "storage layout",
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=0.5),
    )
    assert [n.node.node_id for n in out] == ["a", "b", "c"]


def test_score_and_blend_does_not_mutate_callers(monkeypatch):
    nodes = [_node("a", 0.3, "alpha body"), _node("b", None, "beta body")]
    _patch_encoder(monkeypatch, [1.0, 0.0])
    out = ce.score_and_blend(
        nodes,
        "storage layout",
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=1),
    )
    assert nodes[0].score == 0.3
    assert nodes[1].score is None
    assert nodes[0].node.text == "alpha body"
    assert all(isinstance(n, NodeWithScore) for n in out)
    assert all(copy is not original for copy, original in zip(out, nodes))
    assert out[0].node is nodes[0].node or out[1].node is nodes[0].node


def test_empty_pool_skips_the_model(monkeypatch):
    def boom(model_name, device):
        raise AssertionError("model loaded for an empty pool")

    monkeypatch.setattr(ce, "get_cross_encoder", boom)
    assert ce.score_and_blend([], "storage layout", _cfg(RERANK_CROSS_ENCODER_MODEL="org/model")) == []


def test_none_return_and_short_or_none_scores_keep_fused(monkeypatch):
    nodes = [_node("a", 0.2, "a"), _node("b", 0.6, "b"), _node("c", 0.4, "c")]
    warnings = []
    monkeypatch.setattr(ce, "log_warn", warnings.append)

    _patch_encoder(monkeypatch, None)
    missing = ce.score_and_blend(
        nodes, "q", _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=1)
    )
    assert [n.score for n in missing] == pytest.approx([0.6, 0.4, 0.2])

    _patch_encoder(monkeypatch, [2.0])
    short = ce.score_and_blend(
        nodes, "q", _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=1)
    )
    by_id = {n.node.node_id: n.score for n in short}
    assert by_id["a"] == pytest.approx(_sigmoid(2.0))
    assert by_id["b"] == pytest.approx(0.6)
    assert by_id["c"] == pytest.approx(0.4)

    _patch_encoder(monkeypatch, [1.0, None, float("nan")])
    mixed = ce.score_and_blend(
        nodes, "q", _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=1)
    )
    by_id = {n.node.node_id: n.score for n in mixed}
    assert by_id["a"] == pytest.approx(_sigmoid(1.0))
    assert by_id["b"] == pytest.approx(0.6)
    assert by_id["c"] == pytest.approx(0.4)
    assert warnings


def test_doc_chars_batch_and_query_are_passed(monkeypatch):
    encoder = _patch_encoder(monkeypatch, [0.0])
    text = "abcdefghijklmnopqrstuvwxyz"
    ce.score_and_blend(
        [_node("a", 0.5, text)],
        "storage layout",
        _cfg(
            RERANK_CROSS_ENCODER_MODEL="org/model",
            RERANK_CROSS_ENCODER_DOC_CHARS=4,
            RERANK_CROSS_ENCODER_BATCH=3,
        ),
    )
    assert encoder.calls[0]["query"] == "storage layout"
    assert encoder.calls[0]["docs"] == ["abcd"]
    assert encoder.calls[0]["batch_size"] == 3


def test_numpy_style_score_is_accepted(monkeypatch):
    class _Float:
        def __float__(self):
            return 0.0

    _patch_encoder(monkeypatch, [_Float()])
    out = ce.score_and_blend(
        [_node("a", 0.25, "a")],
        "q",
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=1),
    )
    assert out[0].score == pytest.approx(_sigmoid(0.0))


# ── loader ────────────────────────────────────────────────────


def test_loader_is_cached_per_model_and_device(monkeypatch):
    calls = []

    def construct(model_name, device):
        calls.append((model_name, device))
        return _FakeEncoder([0.0])

    monkeypatch.setattr(ce, "_construct_cross_encoder", construct)
    monkeypatch.setattr(ce, "log", lambda *_a, **_k: None)
    first = ce.get_cross_encoder("org/one", "cpu")
    second = ce.get_cross_encoder("org/one", "cpu")
    ce.get_cross_encoder("org/one", "cuda")
    ce.get_cross_encoder("org/two", "cpu")
    assert first is second
    assert calls == [("org/one", "cpu"), ("org/one", "cuda"), ("org/two", "cpu")]


def test_model_load_logs_one_line(monkeypatch):
    messages = []
    monkeypatch.setattr(ce, "_construct_cross_encoder", lambda model_name, device: _FakeEncoder([0.0]))
    monkeypatch.setattr(ce, "log", messages.append)
    ce.get_cross_encoder("org/model", "cpu")
    ce.get_cross_encoder("org/model", "cpu")
    assert messages == ["Cross-encoder 'org/model' loaded on cpu"]


def test_cuda_falls_back_to_cpu_and_does_not_retry(monkeypatch):
    calls = []
    warnings = []
    messages = []

    def construct(model_name, device):
        calls.append(device)
        if device == "cuda":
            raise RuntimeError("CUDAExecutionProvider missing")
        return _FakeEncoder([0.0])

    monkeypatch.setattr(ce, "_construct_cross_encoder", construct)
    monkeypatch.setattr(ce, "log_warn", warnings.append)
    monkeypatch.setattr(ce, "log", messages.append)
    cuda = ce.get_cross_encoder("org/model", "cuda")
    again = ce.get_cross_encoder("org/model", "cuda")
    cpu = ce.get_cross_encoder("org/model", "cpu")
    assert cuda is again is cpu
    assert calls == ["cuda", "cpu"]
    assert len(warnings) == 1
    assert "CPU" in warnings[0]
    assert messages == ["Cross-encoder 'org/model' loaded on cpu"]


# ── fused pool ────────────────────────────────────────────────


def test_stage_off_keeps_fetch_k():
    cfg = _cfg(RERANK_CROSS_ENCODER_MODEL=None, RERANK_CROSS_ENCODER_POOL=100)
    rank = ce.begin_query_rank(cfg, "storage layout", 8, profiles=[])
    assert rank.enabled is False
    assert rank.base_fetch_k == 8
    assert rank.fetch_k == 8


def test_pool_widens_and_never_shrinks_below_fetch_k():
    wide = ce.begin_query_rank(
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_POOL=32),
        "storage layout",
        8,
        profiles=[],
    )
    assert wide.base_fetch_k == 8
    assert wide.fetch_k == 32
    narrow = ce.begin_query_rank(
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_POOL=1),
        "storage layout",
        8,
        profiles=[],
    )
    assert narrow.fetch_k == 8


def test_overview_query_keeps_overfetch_above_the_pool():
    rank = ce.begin_query_rank(
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_POOL=32),
        "What is Widget?",
        8,
        profiles=[],
    )
    assert rank.base_fetch_k == 80
    assert rank.fetch_k == 80


def test_finish_off_calls_rerank_only(monkeypatch):
    seen = {}

    def rerank(nodes, query, desired_top_k=None, verbose=False, profiles=None, options=None):
        seen["nodes"] = nodes
        seen["verbose"] = verbose
        seen["top_k"] = desired_top_k
        return ["reranked"]

    def boom(*_a, **_k):
        raise AssertionError("score_and_blend called while the stage is off")

    monkeypatch.setattr(reranker_module, "rerank_results", rerank)
    monkeypatch.setattr(ce, "score_and_blend", boom)
    nodes = [_node("a", 0.2, "a")]
    rank = ce.begin_query_rank(_cfg(), "storage layout", 8, profiles=[])
    assert rank.finish(nodes, verbose=False) == ["reranked"]
    assert seen["nodes"] is nodes
    assert seen["verbose"] is False
    assert seen["top_k"] == 8


def test_finish_on_blends_before_rerank(monkeypatch):
    order = []

    def blend(nodes, query, cfg):
        order.append("blend")
        return list(reversed(nodes))

    def rerank(nodes, query, desired_top_k=None, verbose=False, profiles=None, options=None):
        order.append("rerank")
        return nodes

    monkeypatch.setattr(ce, "score_and_blend", blend)
    monkeypatch.setattr(reranker_module, "rerank_results", rerank)
    nodes = [_node("a", 0.2, "a"), _node("b", 0.9, "b")]
    rank = ce.begin_query_rank(
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model"), "storage layout", 8, profiles=[]
    )
    out = rank.finish(nodes, verbose=True)
    assert order == ["blend", "rerank"]
    assert [n.node.node_id for n in out] == ["b", "a"]


def test_symbol_candidates_are_scored(monkeypatch):
    from shared.retrieval import merge_symbol_candidates

    pool = [_node("body", 0.4, "ordinary body")]
    extra = [_node("sym", None, "declared symbol body")]
    merged = merge_symbol_candidates(pool, extra, top_k=8, mode="top")
    encoder = _patch_encoder(monkeypatch, [-2.0, 4.0])
    out = ce.score_and_blend(
        merged,
        "flush_buffer",
        _cfg(RERANK_CROSS_ENCODER_MODEL="org/model", RERANK_CROSS_ENCODER_WEIGHT=1),
    )
    assert "declared symbol body" in encoder.calls[0]["docs"]
    assert out[0].node.node_id == "sym"


# ── validation runner ─────────────────────────────────────────


class _Index:
    def __init__(self):
        self.kwargs = None

    def as_retriever(self, **kwargs):
        self.kwargs = kwargs
        return object()


def _install_retrieve(monkeypatch, nodes, extra):
    async def fake_retrieve(*_args, **_kwargs):
        return nodes, extra

    monkeypatch.setattr("shared.retrieval.aretrieve_with_symbol_lookup", fake_retrieve)


def test_run_query_off_uses_the_same_kwargs_and_skips_blend(monkeypatch):
    captured = {}

    def rerank(nodes, query, desired_top_k=None, verbose=False, profiles=None, options=None):
        captured["nodes"] = nodes
        captured["verbose"] = verbose
        return nodes

    def boom(*_a, **_k):
        raise AssertionError("blend while off")

    monkeypatch.setattr(reranker_module, "rerank_results", rerank)
    monkeypatch.setattr(ce, "score_and_blend", boom)
    nodes = [_node("a", 0.5, "alpha")]
    _install_retrieve(monkeypatch, nodes, [])
    cfg = _cfg(
        HYBRID_ALPHA=0.5,
        HYBRID_ALPHA_MODE="fixed",
        HYBRID_PREFETCH_K=100,
        RERANK_CROSS_ENCODER_MODEL=None,
        RERANK_CROSS_ENCODER_POOL=32,
    )
    index = _Index()
    out = runner_module.run_query(index, "hybrid", 0.5, "storage layout", top_k=8, profiles=[], cfg=cfg)
    assert index.kwargs == build_retriever_kwargs(
        cfg, 8, True, alpha=0.5, qdrant_filters=build_branch_filter("master")
    )
    assert out[0] is nodes[0]
    assert captured["verbose"] is False


def test_run_query_widens_the_fused_pool_not_the_legs(monkeypatch):
    monkeypatch.setattr(reranker_module, "rerank_results", lambda *a, **k: a[0] if a else [])
    monkeypatch.setattr(ce, "score_and_blend", lambda nodes, query, cfg: nodes)
    _install_retrieve(monkeypatch, [], [])
    cfg = _cfg(
        HYBRID_ALPHA=0.5,
        HYBRID_ALPHA_MODE="fixed",
        HYBRID_PREFETCH_K=100,
        RERANK_CROSS_ENCODER_MODEL="org/model",
        RERANK_CROSS_ENCODER_POOL=32,
    )
    index = _Index()
    runner_module.run_query(index, "hybrid", 0.5, "storage layout", top_k=8, profiles=[], cfg=cfg)
    assert index.kwargs["hybrid_top_k"] == 32
    assert index.kwargs["similarity_top_k"] == 100
    assert index.kwargs["sparse_top_k"] == 100

    overview = _Index()
    runner_module.run_query(overview, "hybrid", 0.5, "What is Widget?", top_k=8, profiles=[], cfg=cfg)
    assert overview.kwargs["hybrid_top_k"] == 80
    assert overview.kwargs["similarity_top_k"] == 100


def test_run_query_scores_symbol_candidates(monkeypatch):
    seen = {}

    def blend(nodes, query, cfg):
        seen["ids"] = [n.node.node_id for n in nodes]
        return nodes

    monkeypatch.setattr(ce, "score_and_blend", blend)
    monkeypatch.setattr(reranker_module, "rerank_results", lambda nodes, *a, **k: nodes)
    _install_retrieve(
        monkeypatch,
        [_node("body", 0.4, "ordinary body")],
        [_node("sym", None, "declared symbol body")],
    )
    cfg = _cfg(
        HYBRID_ALPHA=0.5,
        HYBRID_ALPHA_MODE="fixed",
        HYBRID_PREFETCH_K=100,
        RERANK_CROSS_ENCODER_MODEL="org/model",
        SYMBOL_LOOKUP_SCORE="top",
    )
    runner_module.run_query(_Index(), "hybrid", 0.5, "flush_buffer", top_k=8, profiles=[], cfg=cfg)
    assert seen["ids"] == ["body", "sym"]


def test_run_query_uses_begin_query_rank(monkeypatch):
    """Replacing the shared helper changes fetch size and the result list."""

    class _Session:
        enabled = True
        base_fetch_k = 8
        fetch_k = 41

        def finish(self, nodes, *, verbose):
            return ["from-helper"]

    monkeypatch.setattr(ce, "begin_query_rank", lambda *a, **k: _Session())
    _install_retrieve(monkeypatch, [], [])
    cfg = _cfg(HYBRID_ALPHA=0.5, HYBRID_ALPHA_MODE="fixed", HYBRID_PREFETCH_K=100)
    index = _Index()
    out = runner_module.run_query(index, "hybrid", 0.5, "storage layout", top_k=8, cfg=cfg)
    assert out == ["from-helper"]
    assert index.kwargs["hybrid_top_k"] == 41


def test_invalid_override_fails_at_query_time(monkeypatch):
    _install_retrieve(monkeypatch, [], [])
    cfg = _cfg(
        HYBRID_ALPHA=0.5,
        HYBRID_ALPHA_MODE="fixed",
        RERANK_CROSS_ENCODER_MODEL="org/model",
        RERANK_CROSS_ENCODER_WEIGHT=2,
    )
    with pytest.raises(ValueError, match="RERANK_CROSS_ENCODER_WEIGHT"):
        runner_module.run_query(_Index(), "dense", 0.5, "storage layout", top_k=8, cfg=cfg)


# ── MCP search path ───────────────────────────────────────────


def test_mcp_search_uses_begin_query_rank(monkeypatch, tmp_path):
    """The registered search tool takes fetch size and ranking from the helper."""
    import sys
    from unittest.mock import patch

    from mcp.server.fastmcp import FastMCP
    from llama_index.core import VectorStoreIndex
    from qdrant_client import QdrantClient, models

    import rag_mcp
    from src_test.shared.test_index_meta import DIM, FakeEmbed

    coll = "serving_cross_encoder"
    qclient = QdrantClient(":memory:")
    qclient.create_collection(
        coll, vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE)
    )
    import config as base

    values = {k: getattr(base, k) for k in dir(base) if k.isupper()}
    values.update(
        COLLECTION_NAME=coll,
        MODEL_NAME="org/model-a",
        MCP_EMBED_DEVICE="cpu",
        INDEXING_MODE="dense",
        USE_TEI=False,
        SOURCE_DIRS=[],
        get_index_path=lambda: str(tmp_path / "no-manifest"),
        RERANK_CROSS_ENCODER_MODEL=None,
    )
    cfg = types.SimpleNamespace(**values)

    recorded = {}

    class _Session:
        enabled = True
        base_fetch_k = 8
        fetch_k = 32

        def finish(self, nodes, *, verbose):
            recorded["verbose"] = verbose
            recorded["ids"] = [n.node.node_id for n in nodes]
            return nodes

    monkeypatch.setattr(ce, "begin_query_rank", lambda *a, **k: _Session())

    class Index:
        def __init__(self):
            self.kwargs = None

        def as_retriever(self, **kwargs):
            self.kwargs = kwargs
            recorded["kwargs"] = kwargs
            return object()

    index = Index()
    nodes = [_node("body", 0.4, "ordinary body")]
    extra = [_node("sym", None, "declared symbol body")]

    async def fake_retrieve(*_a, **_k):
        return nodes, extra

    captured = {}

    def fake_run(self, *a, **k):
        captured["mcp"] = self

    import qdrant.vector_store as vs

    with patch.object(sys, "argv", ["rag_mcp.py", "--lazy-init"]), \
            patch.object(rag_mcp.config_loader, "get_config", return_value=cfg), \
            patch.object(rag_mcp, "ensure_qdrant_running", return_value=True), \
            patch.object(rag_mcp, "ensure_tei_running", side_effect=AssertionError("TEI started")), \
            patch.object(rag_mcp, "get_qdrant_client", return_value=qclient), \
            patch("shared.embedding.get_embed_model", return_value=FakeEmbed()), \
            patch.object(
                vs, "get_qdrant_vector_store",
                return_value=(types.SimpleNamespace(vector_store=object()), None, None),
            ), \
            patch.object(VectorStoreIndex, "from_vector_store", return_value=index), \
            patch("shared.retrieval.aretrieve_with_symbol_lookup", fake_retrieve), \
            patch.object(FastMCP, "run", fake_run):
        rag_mcp.main()
        asyncio.run(captured["mcp"].call_tool("search_rag", {"query": "flush_buffer", "top_k": 8}))

    assert recorded["kwargs"]["similarity_top_k"] == 32
    assert recorded["verbose"] is True
    assert recorded["ids"] == ["body", "sym"]
