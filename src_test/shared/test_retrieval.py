"""Tests for shared/retrieval.py -- retriever kwargs and fusion depth."""

import asyncio
import threading
import types

from llama_index.core.vector_stores.types import VectorStoreQueryMode

from shared.retrieval import build_retriever_kwargs, hybrid_prefetch_k


def _cfg(**kw):
    return types.SimpleNamespace(**kw)


def test_default_legs_equal_fetch_k():
    kw = build_retriever_kwargs(_cfg(HYBRID_ALPHA=0.5), 8, hybrid=True)
    assert kw["similarity_top_k"] == 8 and kw["sparse_top_k"] == 8
    assert "hybrid_top_k" not in kw
    assert kw["vector_store_query_mode"] == VectorStoreQueryMode.HYBRID
    assert kw["alpha"] == 0.5


def test_prefetch_deepens_legs_but_keeps_fused_size():
    kw = build_retriever_kwargs(_cfg(HYBRID_PREFETCH_K=30), 8, hybrid=True, alpha=0.3)
    assert kw["similarity_top_k"] == 30 and kw["sparse_top_k"] == 30
    assert kw["hybrid_top_k"] == 8
    assert kw["alpha"] == 0.3


def test_prefetch_never_below_fetch_k():
    assert hybrid_prefetch_k(_cfg(HYBRID_PREFETCH_K=20), 80) == 80
    assert hybrid_prefetch_k(None, 8) == 8


def test_dense_ignores_prefetch_and_passes_filter():
    kw = build_retriever_kwargs(_cfg(HYBRID_PREFETCH_K=30), 8, hybrid=False, qdrant_filters="F")
    assert kw == {"similarity_top_k": 8, "vector_store_kwargs": {"qdrant_filters": "F"}}


# ── symbol lookup ─────────────────────────────────────────────

from shared.retrieval import (
    add_symbol_candidates,
    aretrieve_with_symbol_lookup,
    fetch_symbol_candidates,
    merge_symbol_candidates,
    query_symbol_names,
)


class _N:
    def __init__(self, nid):
        self.node_id = nid
        self.metadata = {}


class _NWS:
    def __init__(self, nid, score):
        self.node = _N(nid)
        self.score = score


def test_query_symbol_names_keeps_case_and_forms():
    names = query_symbol_names("Where is try_to_wake_up defined and what does struct rq hold?")
    assert "try_to_wake_up" in names and "rq" not in names  # too short
    assert query_symbol_names("How does schedule() pick a task?") == ["schedule"]
    assert "DocumentStore" in query_symbol_names("What does DocumentStore::save do?")
    assert "save" in query_symbol_names("What does DocumentStore::save do?")
    assert "page_pool" in query_symbol_names("what is struct page_pool")
    assert query_symbol_names("how are pages reclaimed") == []


def test_query_symbol_names_skips_stop_words():
    assert query_symbol_names("which function that handles timers") == []


def test_merge_symbol_candidates_dedup_and_bar_score():
    pool = [_NWS("a", 0.9), _NWS("b", 0.5), _NWS("c", 0.3)]
    extra = [_NWS("b", None), _NWS("x", None)]
    out = merge_symbol_candidates(pool, extra, top_k=2)
    assert [n.node.node_id for n in out] == ["a", "b", "c", "x"]
    assert out[-1].score == 0.5
    out = merge_symbol_candidates(pool[:], [_NWS("y", None)], top_k=8, mode="top")
    assert out[-1].score == 0.9


def test_fetch_disabled_by_default():
    assert fetch_symbol_candidates(object(), "find try_to_wake_up", _cfg()) == []


def test_add_symbol_candidates_noop_without_names():
    pool = [_NWS("a", 0.9)]
    assert add_symbol_candidates(None, pool, "how are pages reclaimed", _cfg(SYMBOL_LOOKUP_K=4), 8) is pool


def test_fetch_builds_filter_and_parses():
    calls = {}

    class Client:
        def query_points(self, **kw):
            calls.update(kw)
            return types.SimpleNamespace(points=["p1"])

    class Store:
        client = Client()
        collection_name = "c"
        dense_vector_name = "text-dense"
        enable_hybrid = True

        def parse_to_query_result(self, pts):
            from llama_index.core.schema import TextNode
            return types.SimpleNamespace(nodes=[TextNode(id_="p1", text="x")])

    out = fetch_symbol_candidates(Store(), "find try_to_wake_up", _cfg(SYMBOL_LOOKUP_K=3), query_embedding=[0.1])
    assert len(out) == 1 and out[0].node.node_id == "p1"
    assert calls["limit"] == 3 and calls["using"] == "text-dense"
    cond = calls["query_filter"].must[0]
    assert cond.key == "object_name" and cond.match.any == ["try_to_wake_up"]


# ── one shared query embedding, lookup concurrent with retrieval ──

class _Embed:
    def __init__(self, fail=False):
        self.async_calls = []
        self.sync_calls = 0
        self.fail = fail

    async def aget_agg_embedding_from_queries(self, queries):
        self.async_calls.append(list(queries))
        if self.fail:
            raise RuntimeError("TEI down")
        return [0.25, 0.5]

    def get_query_embedding(self, query):
        self.sync_calls += 1
        return [9.0]


class _Store:
    collection_name = "c"
    dense_vector_name = "text-dense"
    enable_hybrid = True

    def __init__(self, on_query=None):
        self.calls = []
        store = self

        class Client:
            def query_points(self, **kw):
                store.calls.append(("query", kw))
                if on_query:
                    on_query()
                return types.SimpleNamespace(points=["p9"])

            def scroll(self, **kw):
                store.calls.append(("scroll", kw))
                return ["p9"], None

        self.client = Client()

    def parse_to_query_result(self, pts):
        from llama_index.core.schema import TextNode
        return types.SimpleNamespace(nodes=[TextNode(id_="p9", text="x")])


class _Index:
    def __init__(self, store, embed):
        self.vector_store = store
        self._embed_model = embed


class _Retriever:
    def __init__(self, before_return=None):
        self.args = []
        self.before_return = before_return

    async def aretrieve(self, q):
        self.args.append(q)
        if self.before_return:
            await self.before_return()
        return [_NWS("a", 0.9), _NWS("b", 0.4)]


def test_shared_embedding_is_used_by_retriever_and_lookup():
    from qdrant_client import models as qm

    branch = qm.Filter(must=[qm.FieldCondition(key="branch", match=qm.MatchValue(value="main"))])
    embed, store, ret = _Embed(), _Store(), _Retriever()
    cfg = _cfg(SYMBOL_LOOKUP_K=4)
    nodes, extra = asyncio.run(
        aretrieve_with_symbol_lookup(_Index(store, embed), ret, "find try_to_wake_up", cfg, branch)
    )
    assert embed.async_calls == [["find try_to_wake_up"]] and embed.sync_calls == 0
    bundle = ret.args[0]
    assert bundle.query_str == "find try_to_wake_up" and bundle.embedding == [0.25, 0.5]
    kind, kw = store.calls[0]
    assert kind == "query" and kw["query"] == [0.25, 0.5]
    assert kw["query_filter"].must[-1] == branch
    assert [n.node.node_id for n in nodes] == ["a", "b"]
    assert [n.node.node_id for n in extra] == ["p9"]
    merged = merge_symbol_candidates(nodes, extra, 8, mode="top")
    assert [n.node.node_id for n in merged] == ["a", "b", "p9"] and merged[-1].score == 0.9


def test_shared_embedding_matches_sequential_path():
    """Same pool as retrieval followed by add_symbol_candidates."""
    cfg = _cfg(SYMBOL_LOOKUP_K=4, SYMBOL_LOOKUP_SCORE="bar")
    index = _Index(_Store(), _Embed())
    nodes, extra = asyncio.run(
        aretrieve_with_symbol_lookup(index, _Retriever(), "find try_to_wake_up", cfg)
    )
    new = merge_symbol_candidates(nodes, extra, 2, mode="bar")
    old_pool = asyncio.run(_Retriever().aretrieve("find try_to_wake_up"))
    old = add_symbol_candidates(index, old_pool, "find try_to_wake_up", cfg, 2)
    assert [(n.node.node_id, n.score) for n in new] == [(n.node.node_id, n.score) for n in old]


def test_no_symbol_names_skips_embedding_and_lookup():
    embed, store, ret = _Embed(), _Store(), _Retriever()
    nodes, extra = asyncio.run(
        aretrieve_with_symbol_lookup(_Index(store, embed), ret, "how are pages reclaimed",
                                     _cfg(SYMBOL_LOOKUP_K=4))
    )
    assert ret.args == ["how are pages reclaimed"] and extra == []
    assert embed.async_calls == [] and store.calls == []


def test_lookup_disabled_passes_plain_query():
    embed, store, ret = _Embed(), _Store(), _Retriever()
    _, extra = asyncio.run(
        aretrieve_with_symbol_lookup(_Index(store, embed), ret, "find try_to_wake_up", _cfg())
    )
    assert ret.args == ["find try_to_wake_up"] and extra == [] and embed.async_calls == []


def test_embedding_failure_lets_retriever_embed_and_lookup_scrolls():
    embed, store, ret = _Embed(fail=True), _Store(), _Retriever()
    _, extra = asyncio.run(
        aretrieve_with_symbol_lookup(_Index(store, embed), ret, "find try_to_wake_up",
                                     _cfg(SYMBOL_LOOKUP_K=4))
    )
    assert ret.args == ["find try_to_wake_up"]
    assert store.calls[0][0] == "scroll" and len(extra) == 1


def test_lookup_runs_concurrently_with_retrieval():
    lookup_started = threading.Event()
    retrieval_waited = threading.Event()

    def on_query():
        lookup_started.set()

    async def before_return():
        # The main retrieval only finishes once the lookup is in flight.
        for _ in range(500):
            if lookup_started.is_set():
                retrieval_waited.set()
                return
            await asyncio.sleep(0.01)

    store, ret = _Store(on_query=on_query), _Retriever(before_return=before_return)
    asyncio.run(
        aretrieve_with_symbol_lookup(_Index(store, _Embed()), ret, "find try_to_wake_up",
                                     _cfg(SYMBOL_LOOKUP_K=4))
    )
    assert retrieval_waited.is_set()


def test_add_symbol_candidates_reuses_given_embedding():
    embed, store = _Embed(), _Store()
    pool = [_NWS("a", 0.9)]
    out = add_symbol_candidates(_Index(store, embed), pool, "find try_to_wake_up",
                                _cfg(SYMBOL_LOOKUP_K=4), 8, query_embedding=[0.1])
    assert embed.sync_calls == 0 and store.calls[0][1]["query"] == [0.1]
    assert [n.node.node_id for n in out] == ["a", "p9"]
