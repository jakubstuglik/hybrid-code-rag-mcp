"""Tests for the pool-level RerankOptions of shared/reranker.py."""

import types

import shared.reranker as R
from shared.readers.cpp_reader import RERANK_PROFILE as CPP


class _Node:
    def __init__(self, metadata, text=""):
        self.metadata = metadata
        self.text = text
        self.node_id = metadata.get("file_path", "") + metadata.get("object_name", "")

    def get_content(self):
        return self.text


class _Scored:
    def __init__(self, score, metadata, text=""):
        self.score = score
        self.node = _Node(metadata, text)


def _n(score, path, node_type="cpp_function", name="", text=""):
    return _Scored(score, {"file_path": path, "node_type": node_type, "object_name": name}, text)


def _order(nodes):
    return [(n.node.metadata["file_path"], n.node.metadata["object_name"]) for n in nodes]


PSET = [CPP]


def test_defaults_are_off():
    assert not R.RerankOptions().active
    assert not R.rerank_options_for_config(None).active
    cfg = types.SimpleNamespace(RERANK_FILE_CAP=2, DEPRIORITIZED_PATHS=["tools/*"])
    o = R.rerank_options_for_config(cfg)
    assert o.file_cap == 2 and o.deprioritized_paths == ("tools/*",) and o.active


def test_mention_penalty_only_when_a_declarer_is_in_pool():
    caller = _n(0.60, "a/x.c", name="wake_one", text="int wake_one(void)\n{\n\treturn do_wake_task(p);\n}")
    other = _n(0.58, "a/z.c", name="unrelated", text="int unrelated(void)\n{\n\treturn 0;\n}")
    definer = _n(0.40, "a/y.c", name="do_wake_task", text="int do_wake_task(struct t *p)\n{\n}")
    opts = R.RerankOptions(profile_mention=True)
    out = R.rerank_results([caller, other, definer], "do_wake_task", profiles=PSET, options=opts)
    assert _order(out)[0] == ("a/y.c", "do_wake_task")
    # caller (mention) drops below the unrelated chunk
    assert _order(out).index(("a/x.c", "wake_one")) > _order(out).index(("a/z.c", "unrelated"))
    # no declarer in pool: no penalty, caller keeps its rank
    out = R.rerank_results([caller, other], "do_wake_task", profiles=PSET, options=opts)
    assert _order(out)[0] == ("a/x.c", "wake_one")


def test_prototype_yields_to_body():
    proto = _n(0.7, "inc/t.h", node_type="declaration_group", name="tick_fn",
               text="void tick_fn(int cpu);")
    body = _n(0.5, "k/t.c", name="tick_fn", text="void tick_fn(int cpu)\n{\n}")
    out = R.rerank_results([proto, body], "tick_fn", profiles=PSET,
                           options=R.RerankOptions(prototype_yield=0.2))
    assert _order(out)[0] == ("k/t.c", "tick_fn")


def test_type_intent_boosts_enum():
    fn = _n(0.50, "k/a.c", name="map_alloc", text="int map_alloc(void)\n{\n}")
    en = _n(0.40, "inc/b.h", node_type="enum_declaration", name="map_kind",
            text="enum map_kind {\n A,\n B,\n};")
    q = "which map types exist"
    out = R.rerank_results([fn, en], q, profiles=PSET, options=R.RerankOptions())
    assert _order(out)[0] == ("k/a.c", "map_alloc")
    out = R.rerank_results([fn, en], q, profiles=PSET, options=R.RerankOptions(type_intent=True))
    assert _order(out)[0] == ("inc/b.h", "map_kind")


def test_deprioritized_paths_unless_named():
    tool = _n(0.50, "proj/tools/lib/a.c", name="parse_args")
    core = _n(0.45, "proj/core/a.c", name="parse_opts")
    opts = R.RerankOptions(deprioritized_paths=("*/tools/*",))
    out = R.rerank_results([tool, core], "argument parsing", profiles=PSET, options=opts)
    assert _order(out)[0][0] == "proj/core/a.c"
    out = R.rerank_results([tool, core], "argument parsing in tools", profiles=PSET, options=opts)
    assert _order(out)[0][0] == "proj/tools/lib/a.c"


def test_file_cap_on_multi_place_queries():
    a1, a2, a3 = (_n(0.9 - i * 0.01, "x/a.c", name=f"f{i}") for i in range(3))
    b1 = _n(0.5, "x/b.c", name="g")
    opts = R.RerankOptions(file_cap=2)
    out = R.rerank_results([a1, a2, a3, b1], "reader and writer paths", profiles=PSET, options=opts)
    assert [p for p, _ in _order(out)] == ["x/a.c", "x/a.c", "x/b.c", "x/a.c"]
    out = R.rerank_results([a1, a2, a3, b1], "reader path", profiles=PSET, options=opts)
    assert [p for p, _ in _order(out)] == ["x/a.c", "x/a.c", "x/a.c", "x/b.c"]


def test_root_config_defaults_are_the_validated_combination():
    """The shipped defaults are the combination validated end to end
    (deep fusion 100, symbol lookup, all pool-level rules except the core
    mention penalty, which is left to the per-language profiles)."""
    import importlib.util
    import pathlib

    path = pathlib.Path(__file__).resolve().parents[2] / "config.py"
    spec = importlib.util.spec_from_file_location("root_config_defaults", path)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)

    assert cfg.HYBRID_PREFETCH_K == 100
    assert cfg.SYMBOL_LOOKUP_K == 4
    assert cfg.SYMBOL_LOOKUP_SCORE == "top"
    o = R.rerank_options_for_config(cfg)
    assert o.active
    assert o.core_mention_penalty == 0.0
    assert o.profile_mention and o.type_intent
    assert o.file_cap == 2
    assert o.deprioritized_paths == ("*/tools/*", "*/tests/*", "*/test/*", "*/testing/*")
    assert o.deprioritized_penalty == 0.10
    assert o.prototype_yield == 0.3
