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
    assert o.body_preference == 1.0


_BODY = "int handle_fault(struct vm_area_struct *vma)\n{\n\treturn 0;\n}"
_SUMMARY = "// File: mm.h\nstruct vm_fault {\n\tstruct vm_area_struct *vma;\n\tunsigned long address;\n}"


def test_type_summary_yields_to_body_in_behaviour_queries():
    summary = _n(0.70, "include/mm.h", node_type="class_summary", name="vm_fault", text=_SUMMARY)
    body = _n(0.62, "mm/memory.c", name="handle_fault", text=_BODY)
    opts = R.RerankOptions(body_preference=1.0)
    out = R.rerank_results([summary, body], "page fault handler for a vma", profiles=PSET, options=opts)
    assert _order(out)[0] == ("mm/memory.c", "handle_fault")
    # off: unchanged order
    out = R.rerank_results([summary, body], "page fault handler for a vma", profiles=PSET,
                           options=R.RerankOptions())
    assert _order(out)[0] == ("include/mm.h", "vm_fault")


def test_type_summary_kept_for_structure_queries_and_named_types():
    opts = R.RerankOptions(body_preference=1.0)
    for q in ("what fields describe a page fault", "struct describing a page fault", "vm_fault",
              "in-memory page fault information", "fault state tracked by the mm"):
        summary = _n(0.70, "include/mm.h", node_type="class_summary", name="vm_fault", text=_SUMMARY)
        body = _n(0.62, "mm/memory.c", name="handle_fault", text=_BODY)
        out = R.rerank_results([summary, body], q, profiles=PSET, options=opts)
        assert _order(out)[0] == ("include/mm.h", "vm_fault"), q


def test_type_summary_kept_when_it_mentions_a_query_identifier():
    """A field named in the query ("max_open_files option default") lives in
    the summary, so the summary keeps its rank."""
    text = "// File: options.h\nstruct db_options {\n\tint max_open_files = -1;\n\tbool paranoid = true;\n}"
    summary = _n(0.70, "include/options.h", node_type="class_summary", name="db_options", text=text)
    body = _n(0.62, "db/open.c", name="open_db", text="int open_db(void)\n{\n\treturn 0;\n}")
    out = R.rerank_results([summary, body], "max_open_files option default -1", profiles=PSET,
                           options=R.RerankOptions(body_preference=1.0))
    assert _order(out)[0] == ("include/options.h", "db_options")


def test_type_summary_kept_without_a_body_in_pool():
    summary = _n(0.70, "include/mm.h", node_type="class_summary", name="vm_fault", text=_SUMMARY)
    macro = _n(0.62, "include/mm.h", node_type="macro_group", name="FAULT_FLAG_WRITE", text="#define FAULT_FLAG_WRITE 1")
    out = R.rerank_results([summary, macro], "page fault handler for a vma", profiles=PSET,
                           options=R.RerankOptions(body_preference=1.0))
    assert _order(out)[0] == ("include/mm.h", "vm_fault")


def test_body_preference_ignores_profiles_without_summary_yield():
    from shared.readers.java_reader import JavaFileReader

    java = JavaFileReader.rerank_profile
    summary = _n(0.70, "src/A.java", node_type="class_summary", name="A", text="class A {}")
    body = _n(0.62, "src/B.java", node_type="method_declaration", name="run", text="void run() {}")
    out = R.rerank_results([summary, body], "how is the job executed", profiles=[java],
                           options=R.RerankOptions(body_preference=1.0))
    assert _order(out)[0] == ("src/A.java", "A")


def test_leading_double_underscore_identifiers_are_profile_scoped():
    q = "where is __alloc_pages_slowpath implemented"
    assert R.extract_code_identifiers(q) == []
    assert R.extract_code_identifiers(q, profiles=PSET) == [(None, "__alloc_pages_slowpath")]
    # dunder names are not C reserved identifiers
    assert R.extract_code_identifiers("python __init__ method", profiles=PSET) == []
    decl = _n(0.50, "mm/page_alloc.c", name="__alloc_pages_slowpath",
              text="static struct page *__alloc_pages_slowpath(gfp_t gfp)\n{\n}")
    other = _n(0.60, "mm/internal.h", node_type="class_summary", name="alloc_context",
               text="struct alloc_context {\n\tint x;\n}")
    out = R.rerank_results([other, decl], q, profiles=PSET)
    assert _order(out)[0] == ("mm/page_alloc.c", "__alloc_pages_slowpath")


def test_symbol_names_use_config_profiles():
    import shared.retrieval as RT

    q = "__schedule"
    assert RT.query_symbol_names(q) == []
    assert RT.query_symbol_names(q, R.get_profile_set(PSET)) == ["__schedule"]
    cfg = types.SimpleNamespace(RERANK_PROFILES=["cpp"])
    assert RT.query_symbol_names(q, RT._profiles_for(cfg)) == ["__schedule"]
    py = types.SimpleNamespace(RERANK_PROFILES=["python"])
    assert RT.query_symbol_names(q, RT._profiles_for(py)) == []
