"""Query shape, adaptive hybrid alpha, and the shared retriever path."""

import threading
import types

import pytest

from shared.fusion import hybrid_fusion_fn
from shared.query_shape import (
    adaptive_result_fields,
    alpha_for_query,
    classify_query,
    resolve_hybrid_alpha_mode,
    resolve_hybrid_alphas,
    validate_hybrid_alpha_settings,
)
from shared.branch_dedup import build_branch_filter
from shared.retrieval import (
    build_retriever_kwargs,
    open_query_retriever,
    retriever_kwargs_for_query,
    retriever_ready_message,
)

_NL = "how does the scheduler pick the next task"
_LONG = (
    "the scheduler looks at every runnable task and picks the one that has "
    "waited longest on the run queue so that interactive work stays responsive "
    "under a heavy load from many cores"
)

# (label, query, shape). More than 40 queries, several languages, plus the
# empty / whitespace / unicode / punctuation / number edges.
CLASSIFY_CASES = [
    ("c-snake", "do_numa_page", "identifier"),
    ("c-macro", "SYSCALL_DEFINE", "identifier"),
    ("c-allcaps", "EINTR", "identifier"),
    ("c-null", "NULL", "identifier"),
    ("c-page-size", "PAGE_SIZE", "identifier"),
    ("c-gfp", "GFP_KERNEL", "identifier"),
    ("cpp-qual", "Store::flush", "identifier"),
    ("cpp-arrow", "node->next", "identifier"),
    ("cpp-short-arrow", "a->b", "identifier"),
    ("cpp-arrow-call", "obj->release()", "identifier"),
    ("rust-qual", "foo::bar", "identifier"),
    ("rust-push", "vector::push_back", "identifier"),
    ("rust-path", "src/foo/bar.rs", "identifier"),
    ("py-dunder", "__init__", "identifier"),
    ("py-snake", "get_user_for_jwt", "identifier"),
    ("java-camel", "getUserForJWT", "identifier"),
    ("java-pascal", "ArrayList", "identifier"),
    ("java-calc", "CalculateDiscount", "identifier"),
    ("delphi-pascal", "TdmOrders", "identifier"),
    ("go-qual", "fmt.Println", "identifier"),
    ("go-method", "ServeHTTP", "identifier"),
    ("php-var", "$session", "identifier"),
    ("php-var-short", "$var", "identifier"),
    ("php-static", "Foo::bar()", "identifier"),
    ("cs-type", "HttpClient", "identifier"),
    ("cs-interface", "IDisposable", "identifier"),
    ("cs-qual", "StringBuilder.Append", "identifier"),
    ("path-kernel", "include/linux/sched.h", "identifier"),
    ("glob-header", "*.h", "identifier"),
    ("dotted-header", "sched.h", "identifier"),
    ("backtick", "`do_numa_page`", "identifier"),
    ("backtick-path", "`include/linux/sched.h`", "identifier"),
    ("define", "#define SYSCALL_DEFINE", "identifier"),
    ("include", "#include <linux/sched.h>", "identifier"),
    ("dot-call", "a.b()", "identifier"),
    ("call", "schedule()", "identifier"),
    ("keyword-struct", "struct page_pool", "identifier"),
    ("keyword-fn", "function main", "identifier"),
    ("where-defined", "where is do_numa_page defined", "identifier"),
    ("call-in-short-question", "How does schedule() pick a task?", "identifier"),
    ("plain-budget-3", "please explain the do_numa_page helper", "identifier"),
    ("inner-cap-short", "iOS", "identifier"),
    ("shouted-sentence", "HOW DOES THE SCHEDULER PICK THE NEXT TASK", "identifier"),
    ("qualified-type", "namespace::Type", "identifier"),
    ("empty", "", "mixed"),
    ("whitespace", "   \n\t  ", "mixed"),
    ("punctuation", "??? !!!", "mixed"),
    ("numbers", "123 456 789 0", "mixed"),
    ("two-plain-words", "page fault", "mixed"),
    ("three-plain-words", "what is this", "mixed"),
    ("two-capitals", "OK", "mixed"),
    ("keyword-too-short", "struct rq", "mixed"),
    ("backtick-stop", "`the`", "mixed"),
    ("unicode-one-word", "żądanie", "mixed"),
    ("plain-budget-4", "please explain the do_numa_page helper routine", "mixed"),
    (
        "natural-plus-one-ident",
        "how does the scheduler pick the next task using do_numa_page",
        "mixed",
    ),
    ("shouted-stop-words", "HOW DOES THE", "mixed"),
    ("natural", _NL, "natural"),
    ("natural-long", _LONG, "natural"),
    ("unicode-phrase", "jak działa planista zadań w jądrze", "natural"),
    ("no-code-token", "which function that handles timers", "natural"),
]


def _cfg(**kwargs):
    return types.SimpleNamespace(**kwargs)


def _adaptive(**kwargs):
    base = {"HYBRID_ALPHA_MODE": "adaptive", "HYBRID_ALPHA": 0.5}
    base.update(kwargs)
    return _cfg(**base)


class _FakeIndex:
    """Records each as_retriever call and returns a fresh object."""

    def __init__(self):
        self.made = []

    def as_retriever(self, **kwargs):
        retriever = types.SimpleNamespace(alpha=kwargs.get("alpha"), kwargs=dict(kwargs))
        self.made.append(retriever)
        return retriever


def test_classify_table_covers_at_least_40_queries():
    assert len(CLASSIFY_CASES) >= 40
    assert len({query for _label, query, _shape in CLASSIFY_CASES}) == len(CLASSIFY_CASES)


@pytest.mark.parametrize(
    "label,query,expected",
    CLASSIFY_CASES,
    ids=[case[0] for case in CLASSIFY_CASES],
)
def test_classify_query(label, query, expected):
    assert classify_query(query) == expected
    assert classify_query(query) == expected  # deterministic


def test_classify_none_is_mixed():
    assert classify_query(None) == "mixed"


# ── alpha resolution ──────────────────────────────────────────────


def test_mode_defaults_and_normalizes():
    assert resolve_hybrid_alpha_mode(None) == "fixed"
    assert resolve_hybrid_alpha_mode(_cfg()) == "fixed"
    assert resolve_hybrid_alpha_mode(_cfg(HYBRID_ALPHA_MODE=None)) == "fixed"
    assert resolve_hybrid_alpha_mode(_cfg(HYBRID_ALPHA_MODE="FIXED")) == "fixed"
    assert resolve_hybrid_alpha_mode(_cfg(HYBRID_ALPHA_MODE="  Adaptive ")) == "adaptive"


@pytest.mark.parametrize(
    "raw",
    ["rank", "", "auto", "rrf", 1, True, False, 0.5, ["adaptive"]],
)
def test_unknown_mode_raises(raw):
    with pytest.raises(ValueError, match="HYBRID_ALPHA_MODE"):
        resolve_hybrid_alpha_mode(_cfg(HYBRID_ALPHA_MODE=raw))


def test_ident_none_and_missing_mean_default():
    for cfg in (
        _adaptive(),
        _adaptive(HYBRID_ALPHA_IDENT=None, HYBRID_ALPHA_MIXED=None, HYBRID_ALPHA_NL=None),
    ):
        alphas = resolve_hybrid_alphas(cfg)
        assert alphas["identifier"] == 0.3
        assert alphas["mixed"] == 0.5
        assert alphas["natural"] == 0.5


def test_class_alphas_and_base_fallback():
    cfg = _adaptive(HYBRID_ALPHA=0.55, HYBRID_ALPHA_IDENT=0, HYBRID_ALPHA_MIXED=1, HYBRID_ALPHA_NL=0.25)
    alphas = resolve_hybrid_alphas(cfg)
    assert alphas == {"identifier": 0.0, "mixed": 1.0, "natural": 0.25}
    # None falls back to an explicit base, not to HYBRID_ALPHA.
    overridden = resolve_hybrid_alphas(cfg, base_alpha=0.8)
    assert overridden["mixed"] == 1.0  # explicit value stays
    assert overridden["natural"] == 0.25
    bare = resolve_hybrid_alphas(_adaptive(HYBRID_ALPHA=0.55), base_alpha=0.8)
    assert bare["identifier"] == 0.3
    assert bare["mixed"] == 0.8
    assert bare["natural"] == 0.8


@pytest.mark.parametrize(
    "key",
    ["HYBRID_ALPHA_IDENT", "HYBRID_ALPHA_MIXED", "HYBRID_ALPHA_NL"],
)
@pytest.mark.parametrize(
    "value",
    [True, False, "0.3", "nope", -0.01, 1.01, float("nan"), float("inf"), float("-inf")],
)
def test_bad_class_alpha_rejected(key, value):
    cfg = _adaptive(**{key: value})
    with pytest.raises(ValueError, match=key):
        resolve_hybrid_alphas(cfg)
    with pytest.raises(ValueError, match=key):
        alpha_for_query(cfg, "do_numa_page")
    with pytest.raises(ValueError, match=key):
        validate_hybrid_alpha_settings(cfg)


def test_validate_accepts_defaults_and_bounds():
    validate_hybrid_alpha_settings(None)
    validate_hybrid_alpha_settings(_cfg())
    validate_hybrid_alpha_settings(
        _adaptive(HYBRID_ALPHA_IDENT=0, HYBRID_ALPHA_MIXED=1, HYBRID_ALPHA_NL=None)
    )


def test_fixed_mode_returns_base_for_every_query():
    cfg = _cfg(HYBRID_ALPHA=0.42, HYBRID_ALPHA_MODE="fixed", HYBRID_ALPHA_IDENT=0.1)
    queries = [query for _label, query, _shape in CLASSIFY_CASES]
    shapes = set()
    for query in queries:
        shape, alpha = alpha_for_query(cfg, query)
        shapes.add(shape)
        assert alpha == 0.42
        assert alpha_for_query(cfg, query, base_alpha=0.8)[1] == 0.8
    assert shapes == {"identifier", "mixed", "natural"}


def test_adaptive_class_alphas_and_alpha_override():
    cfg = _adaptive()
    assert alpha_for_query(cfg, "do_numa_page") == ("identifier", 0.3)
    assert alpha_for_query(cfg, "page fault") == ("mixed", 0.5)
    assert alpha_for_query(cfg, _NL) == ("natural", 0.5)
    # --alpha replaces the base used for mixed / natural defaults.
    assert alpha_for_query(cfg, "do_numa_page", base_alpha=0.8) == ("identifier", 0.3)
    assert alpha_for_query(cfg, "page fault", base_alpha=0.8)[1] == 0.8
    assert alpha_for_query(cfg, _NL, base_alpha=0.8)[1] == 0.8
    # 0.0 is a real base, not "missing".
    assert alpha_for_query(cfg, _NL, base_alpha=0.0)[1] == 0.0
    explicit = _adaptive(HYBRID_ALPHA_IDENT=0.2, HYBRID_ALPHA_MIXED=0.4, HYBRID_ALPHA_NL=0.9)
    assert alpha_for_query(explicit, "do_numa_page", base_alpha=0.8)[1] == 0.2
    assert alpha_for_query(explicit, "page fault", base_alpha=0.8)[1] == 0.4
    assert alpha_for_query(explicit, _NL, base_alpha=0.8)[1] == 0.9


def test_missing_config_is_fixed_base():
    assert alpha_for_query(None, "do_numa_page") == ("identifier", 0.5)
    assert alpha_for_query(None, _NL)[1] == 0.5


# ── retriever kwargs: fixed path unchanged, adaptive per query ───


def test_fixed_kwargs_match_build_retriever_kwargs():
    cfg = _cfg(
        HYBRID_ALPHA=0.42,
        HYBRID_ALPHA_MODE="fixed",
        HYBRID_ALPHA_IDENT=0.1,
        HYBRID_PREFETCH_K=30,
    )
    for query in ("do_numa_page", _NL, _LONG, ""):
        kwargs, shape, mode = retriever_kwargs_for_query(
            cfg, 8, True, query, qdrant_filters="F"
        )
        assert mode == "fixed" and shape is None
        assert kwargs == build_retriever_kwargs(cfg, 8, True, qdrant_filters="F")
        assert kwargs["alpha"] == 0.42
        overridden, shape_b, mode_b = retriever_kwargs_for_query(
            cfg, 8, True, query, qdrant_filters="F", base_alpha=0.7
        )
        assert mode_b == "fixed" and shape_b is None
        assert overridden == build_retriever_kwargs(
            cfg, 8, True, alpha=0.7, qdrant_filters="F"
        )


def test_dense_collection_ignores_alpha_mode():
    cfg = _adaptive(HYBRID_ALPHA_IDENT=0.1)
    kwargs, shape, mode = retriever_kwargs_for_query(
        cfg, 8, False, "do_numa_page", qdrant_filters="F", base_alpha=0.2
    )
    assert mode == "adaptive" and shape is None
    assert kwargs == build_retriever_kwargs(cfg, 8, False, qdrant_filters="F")
    assert "alpha" not in kwargs


@pytest.mark.parametrize("fusion", ["minmax", "rrf", "dbsf"])
def test_adaptive_alpha_with_each_fusion_mode(fusion):
    cfg = _adaptive(HYBRID_FUSION=fusion, HYBRID_RRF_K=20, HYBRID_ALPHA_IDENT=0.3)
    assert alpha_for_query(cfg, "do_numa_page") == ("identifier", 0.3)
    assert alpha_for_query(cfg, _NL) == ("natural", 0.5)
    kwargs, shape, mode = retriever_kwargs_for_query(cfg, 8, True, "Store::flush")
    assert mode == "adaptive" and shape == "identifier" and kwargs["alpha"] == 0.3
    assert "hybrid_fusion_fn" not in kwargs
    fusion_fn = hybrid_fusion_fn(cfg)
    if fusion == "minmax":
        assert fusion_fn is None
    elif fusion == "rrf":
        assert fusion_fn.rrf_k == 20.0
    else:
        assert fusion_fn.fusion_mode == "dbsf"


def test_open_query_retriever_does_not_mutate_a_shared_retriever():
    index = _FakeIndex()
    cfg = _adaptive(HYBRID_ALPHA_IDENT=0.3)
    first, first_kw, first_shape, first_mode = open_query_retriever(
        index, cfg, "do_numa_page", 8, True, qdrant_filters="F"
    )
    second, second_kw, second_shape, second_mode = open_query_retriever(
        index, cfg, _NL, 12, True, qdrant_filters="G"
    )
    assert first is not second
    assert first_mode == second_mode == "adaptive"
    assert first_shape == "identifier" and first.alpha == 0.3
    assert second_shape == "natural" and second.alpha == 0.5
    assert first_kw["alpha"] == 0.3 and second_kw["alpha"] == 0.5
    assert first_kw["vector_store_kwargs"]["qdrant_filters"] == "F"
    assert second_kw["vector_store_kwargs"]["qdrant_filters"] == "G"
    first.alpha = 0.9
    assert second.alpha == 0.5
    assert index.made[0].alpha == 0.9
    assert index.made[1].alpha == 0.5


def test_fixed_open_query_retriever_uses_one_alpha():
    index = _FakeIndex()
    cfg = _cfg(HYBRID_ALPHA=0.42, HYBRID_ALPHA_MODE="fixed", HYBRID_ALPHA_IDENT=0.1)
    first, first_kw, first_shape, first_mode = open_query_retriever(
        index, cfg, "do_numa_page", 8, True
    )
    second, second_kw, second_shape, second_mode = open_query_retriever(index, cfg, _NL, 8, True)
    assert first_mode == second_mode == "fixed"
    assert first_shape is None and second_shape is None
    assert first.alpha == second.alpha == 0.42
    assert first_kw == second_kw == build_retriever_kwargs(cfg, 8, True)
    assert first is not second


def test_concurrent_queries_keep_independent_alphas():
    index = _FakeIndex()
    cfg = _adaptive()
    barrier = threading.Barrier(2)
    found = {}

    def run(key, query):
        barrier.wait()
        found[key] = open_query_retriever(index, cfg, query, 8, True)

    threads = [
        threading.Thread(target=run, args=("ident", "do_numa_page")),
        threading.Thread(target=run, args=("natural", _NL)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    ident, natural = found["ident"][0], found["natural"][0]
    assert ident is not natural
    assert ident.alpha == 0.3
    assert natural.alpha == 0.5
    ident.alpha = 1
    assert natural.alpha == 0.5


def test_retriever_ready_message_mentions_mode():
    assert retriever_ready_message(False, {}, "adaptive", "identifier") == (
        "[MCP] retriever ready (dense)"
    )
    fixed = retriever_ready_message(True, {"alpha": 0.42, "sparse_top_k": 100}, "fixed", None)
    assert fixed == "[MCP] retriever ready (hybrid, alpha=0.42, mode=fixed, legs=100)"
    adaptive = retriever_ready_message(
        True, {"alpha": 0.3, "sparse_top_k": 8}, "adaptive", "identifier"
    )
    assert adaptive == (
        "[MCP] retriever ready (hybrid, alpha=0.3, mode=adaptive, "
        "shape=identifier, legs=8)"
    )


def test_adaptive_result_fields_only_for_hybrid_adaptive():
    adaptive = _adaptive()
    fixed = _cfg(HYBRID_ALPHA=0.5, HYBRID_ALPHA_MODE="fixed")
    assert adaptive_result_fields(fixed, "do_numa_page", 0.5, True) == {}
    assert adaptive_result_fields(adaptive, "do_numa_page", 0.5, False) == {}
    assert adaptive_result_fields(adaptive, "do_numa_page", 0.8, True) == {
        "query_shape": "identifier",
        "alpha": 0.3,
    }
    assert adaptive_result_fields(adaptive, _NL, 0.8, True) == {
        "query_shape": "natural",
        "alpha": 0.8,
    }
    assert adaptive_result_fields(adaptive, "page fault", 0.8, True)["query_shape"] == "mixed"


# ── validation runner uses the same kwargs ────────────────────────


def test_run_query_fixed_and_adaptive(monkeypatch):
    import shared.validation.runner as runner_module

    captured = {}

    class Index:
        def as_retriever(self, **kwargs):
            captured["kwargs"] = kwargs
            return object()

    async def fake_retrieve(*_args, **_kwargs):
        return [], []

    import shared.reranker as reranker_module

    monkeypatch.setattr("shared.retrieval.aretrieve_with_symbol_lookup", fake_retrieve)
    monkeypatch.setattr(
        "shared.retrieval.merge_symbol_candidates",
        lambda nodes, extra, top_k, mode="bar": nodes,
    )
    # run_query ranks through begin_query_rank, which calls these.
    monkeypatch.setattr(reranker_module, "rerank_results", lambda *_a, **_k: [])
    monkeypatch.setattr(
        reranker_module,
        "get_retrieval_top_k",
        lambda query, top_k, profiles=None: 17,
    )

    fixed = _cfg(
        HYBRID_ALPHA=0.5,
        HYBRID_ALPHA_MODE="fixed",
        HYBRID_ALPHA_IDENT=0.1,
        HYBRID_PREFETCH_K=40,
    )
    main_filter = build_branch_filter("master")
    runner_module.run_query(Index(), "hybrid", 0.5, "do_numa_page", top_k=8, cfg=fixed)
    assert captured["kwargs"] == build_retriever_kwargs(
        fixed, 17, True, alpha=0.5, qdrant_filters=main_filter
    )

    runner_module.run_query(Index(), "hybrid", 0.7, _NL, top_k=8, cfg=fixed)
    assert captured["kwargs"]["alpha"] == 0.7

    adaptive = _adaptive(HYBRID_PREFETCH_K=40)
    runner_module.run_query(Index(), "hybrid", 0.7, "do_numa_page", top_k=8, cfg=adaptive)
    assert captured["kwargs"]["alpha"] == 0.3
    runner_module.run_query(Index(), "hybrid", 0.7, _NL, top_k=8, cfg=adaptive)
    assert captured["kwargs"]["alpha"] == 0.7
    runner_module.run_query(Index(), "hybrid", 0.7, "page fault", top_k=8, cfg=adaptive)
    assert captured["kwargs"]["alpha"] == 0.7

    runner_module.run_query(Index(), "dense", 0.7, "do_numa_page", top_k=8, cfg=adaptive)
    assert captured["kwargs"] == build_retriever_kwargs(
        adaptive, 17, False, qdrant_filters=main_filter
    )
    assert "alpha" not in captured["kwargs"]
