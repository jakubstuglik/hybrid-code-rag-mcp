"""
Tests for the query-intent rules of shared/reranker.py that apply beyond the
overview arithmetic:

    - extract_code_identifiers(): camelCase / snake_case / Owner::member
    - chunk_declared_names(): names a chunk declares (metadata, profile
      patterns, generic keyword and signature rules)
    - declared-name bonus for non-overview queries (incl. qualified names)
    - test-file demotion unless the query asks about tests
    - binding / glue-layer demotion (C++ profile)
    - declaration-only chunk demotion (C++ profile)
    - exact class name beats a partial match in overview queries
"""

import pytest

import shared.reranker as R
from shared.readers.cpp_reader import RERANK_PROFILE as CPP
from shared.readers.go_reader import RERANK_PROFILE as GO
from shared.readers.js_reader import RERANK_PROFILE as JS
from shared.readers.php_reader import RERANK_PROFILE as PHP
from shared.readers.python_reader import RERANK_PROFILE as PY


class _Node:
    def __init__(self, metadata, text=""):
        self.metadata = metadata
        self.text = text


class _Scored:
    def __init__(self, score, metadata, text=""):
        self.score = score
        self.node = _Node(metadata, text)


def _order(nodes):
    return [n.node.metadata["file_path"] for n in nodes]


# ────────────────────────────────────────────────
# extract_code_identifiers
# ────────────────────────────────────────────────


class TestExtractCodeIdentifiers:
    @pytest.mark.parametrize(
        "query, expected",
        [
            ("get_or_create", [(None, "get_or_create")]),
            ("loadUserFromToken", [(None, "loaduserfromtoken")]),
            ("IsTrivialMove", [(None, "istrivialmove")]),
            ("MAX_RETRY_COUNT default", [(None, "max_retry_count")]),
            ("Parser::ParseHeader", [("parser", "parseheader")]),
            ("TextHelper.toSlug", [("texthelper", "toslug")]),
            ("conn->flushBuffers", [("conn", "flushbuffers")]),
        ],
    )
    def test_code_shaped(self, query, expected):
        assert R.extract_code_identifiers(query) == expected

    @pytest.mark.parametrize(
        "query",
        ["how are orders stored", "What is the Engine?", "server.go routes", "e.g. this one", "Startup.cs"],
    )
    def test_plain_words_and_file_names_are_not_identifiers(self, query):
        assert R.extract_code_identifiers(query) == []

    def test_overview_targets_include_camel_and_snake(self):
        targets = R.extract_target_identifiers("What is the requestLoop struct?")
        assert "requestloop" in targets
        targets = R.extract_target_identifiers("Explain Parser::ParseHeader")
        assert {"parser", "parseheader"} <= set(targets)


# ────────────────────────────────────────────────
# chunk_declared_names
# ────────────────────────────────────────────────


class TestChunkDeclaredNames:
    def _names(self, path, text, meta=None, profiles=None):
        m = {"file_path": path, **(meta or {})}
        return R.chunk_declared_names(m, text, profiles)

    def test_metadata_name(self):
        names, _ = self._names("a/b.py", "# File: b.py\ndef run():\n    pass", {"function_name": "run"})
        assert "run" in names

    def test_python_def_and_constant(self):
        assert "load_items" in self._names("m.py", "# File: m.py\n# Module: m\ndef load_items(a):\n  return a", profiles=[PY])[0]
        assert "max_size" in self._names("m.py", "# File: m.py\nMAX_SIZE = 10\nOTHER = 2", profiles=[PY])[0]

    def test_cpp_qualified_definition(self):
        names, qualified = self._names(
            "db/store.cc",
            "// File: store.cc\n// Namespace: ns\n// Class: Store\nStatus Store::Flush(const FlushOptions& o) {\n  return Status::OK();\n}",
            profiles=[CPP],
        )
        assert "flush" in names
        assert ("store", "flush") in qualified

    def test_go_method_receiver(self):
        names, qualified = self._names(
            "tsdb/head.go", "// File: head.go\n// Package: tsdb\n// Truncate drops old data.\nfunc (h *Head) Truncate(mint int64) error {\n}",
            profiles=[GO],
        )
        assert "truncate" in names
        assert ("head", "truncate") in qualified

    def test_php_method(self):
        names, _ = self._names(
            "src/Query.php", "// File: Query.php\n// Class: Query\npublic function chunkById($count, callable $cb)\n{\n}",
            profiles=[PHP],
        )
        assert "chunkbyid" in names

    def test_ts_arrow_property_after_jsdoc_and_decorator(self):
        names, _ = self._names(
            "app/stores/ItemsStore.ts",
            "// File: ItemsStore.ts\n// Class: class ItemsStore\n/**\n * Loads recent items.\n */\n@action\nfetchRecent = async (options?: Paging) => {\n}",
            profiles=[JS],
        )
        assert "fetchrecent" in names

    def test_call_on_right_hand_side_is_not_a_declaration(self):
        names, _ = self._names("a.ts", "// File: a.ts\nconst limiter = createLimiter(10);", profiles=[JS])
        assert "createlimiter" not in names
        assert "limiter" in names

    def test_profile_patterns_only_apply_to_their_own_files(self):
        # PHP's ``const NAME`` rule must not read C++ parameter types.
        names, _ = self._names(
            "db/store.cc", "Status Store::Put(const WriteOptions& o, const Slice& k) {\n}", profiles=[CPP, PHP]
        )
        assert "writeoptions" not in names


# ────────────────────────────────────────────────
# Non-overview identifier queries
# ────────────────────────────────────────────────


class TestDeclaredNameBonus:
    def test_definition_beats_test_using_the_name(self):
        nodes = [
            _Scored(0.50, {"node_type": "method_declaration", "file_path": "tests/items/tests.py", "function_name": "test_get_or_create"}, "def test_get_or_create(self):\n  Item.objects.get_or_create(a=1)"),
            _Scored(0.40, {"node_type": "method_declaration", "file_path": "pkg/models/query.py", "function_name": "get_or_create"}, "def get_or_create(self, defaults=None, **kwargs):\n  pass"),
        ]
        out = R.rerank_results(nodes, "get_or_create", profiles=[PY])
        assert _order(out)[0] == "pkg/models/query.py"

    def test_qualified_owner_match_wins(self):
        nodes = [
            _Scored(0.50, {"node_type": "cpp_function", "file_path": "db/other.cc", "class_name": "Other", "object_name": "Flush"}, "Status Other::Flush() {\n}"),
            _Scored(0.45, {"node_type": "cpp_function", "file_path": "db/store.cc", "class_name": "Store", "object_name": "Flush"}, "Status Store::Flush() {\n}"),
        ]
        out = R.rerank_results(nodes, "Store::Flush", profiles=[CPP])
        assert _order(out)[0] == "db/store.cc"

    def test_plain_query_without_signals_keeps_order(self):
        nodes = [
            _Scored(0.8, {"node_type": "method_declaration", "file_path": "a.py"}, "def a():\n pass"),
            _Scored(0.7, {"node_type": "method_declaration", "file_path": "b.py"}, "def b():\n pass"),
        ]
        out = R.rerank_results(nodes, "how are orders stored", profiles=[PY])
        assert out == nodes


# ────────────────────────────────────────────────
# Test-file demotion
# ────────────────────────────────────────────────


class TestTestFileDemotion:
    def _nodes(self):
        return [
            _Scored(0.50, {"node_type": "method_declaration", "file_path": "pkg/store_test.go"}, "func TestStore(t *testing.T) {\n}"),
            _Scored(0.42, {"node_type": "method_declaration", "file_path": "pkg/store.go"}, "func compact(s *Store) {\n}"),
        ]

    def test_demoted_when_query_is_not_about_tests(self):
        out = R.rerank_results(self._nodes(), "compact the store files", profiles=[GO])
        assert _order(out)[0] == "pkg/store.go"

    @pytest.mark.parametrize("query", ["store compaction tests", "unit test for compact", "StoreTest compact"])
    def test_kept_when_query_asks_for_tests(self, query):
        out = R.rerank_results(self._nodes(), query, profiles=[GO])
        assert _order(out)[0] == "pkg/store_test.go"

    @pytest.mark.parametrize(
        "path, profile, expected",
        [
            ("tests/test_views.py", PY, True),
            ("pkg/test_views.py", PY, True),
            ("pkg/testing/helpers.py", PY, False),
            ("server/a.test.ts", JS, True),
            ("src/__tests__/a.ts", JS, True),
            ("db/db_test.cc", CPP, True),
            ("db/db.cc", CPP, False),
            ("tests/Unit/QueueTest.php", PHP, True),
            ("src/Queue/Worker.php", PHP, False),
        ],
    )
    def test_test_path_rules(self, path, profile, expected):
        assert R._is_test_path(path, profile) is expected

    def test_query_mentions_tests(self):
        assert R.query_mentions_tests("tests for the parser")
        assert R.query_mentions_tests("ParserTest setup")
        assert R.query_mentions_tests("assertQueryCount helper")
        assert not R.query_mentions_tests("latest contest results")


# ────────────────────────────────────────────────
# C++: bindings and declaration-only chunks
# ────────────────────────────────────────────────


class TestCppPreferImplementation:
    def test_c_api_wrapper_demoted(self):
        nodes = [
            _Scored(0.50, {"node_type": "cpp_function", "file_path": "db/c.cc"}, "void lib_compact_range(lib_t* db) {\n  db->rep->CompactRange();\n}"),
            _Scored(0.40, {"node_type": "cpp_function", "file_path": "db/impl.cc", "class_name": "Impl", "object_name": "CompactRange"}, "Status Impl::CompactRange() {\n}"),
        ]
        out = R.rerank_results(nodes, "compact a range of keys", profiles=[CPP])
        assert _order(out)[0] == "db/impl.cc"

    def test_jni_glue_demoted_by_path_and_text(self):
        assert R._is_binding_chunk("java/libjni/portal.h", "", CPP)
        assert R._is_binding_chunk("src/glue.cc", "jobject f(JNIEnv* env) {}", CPP)
        assert not R._is_binding_chunk("db/impl.cc", "Status Impl::Get() {}", CPP)

    def test_binding_kept_when_query_asks_for_it(self):
        nodes = [
            _Scored(0.50, {"node_type": "cpp_function", "file_path": "db/c.cc"}, "void lib_open() {}"),
            _Scored(0.40, {"node_type": "cpp_function", "file_path": "db/impl.cc"}, "Status Impl::Open() {}"),
        ]
        out = R.rerank_results(nodes, "C API open function", profiles=[CPP])
        assert _order(out)[0] == "db/c.cc"

    def test_header_declarations_demoted_for_method_queries(self):
        nodes = [
            _Scored(0.45, {"node_type": "class_summary_split", "file_path": "include/store.h", "class_name": "Store"}, "virtual Status Write(const Options&, Batch*) = 0;"),
            _Scored(0.40, {"node_type": "cpp_function", "file_path": "db/store_write.cc", "class_name": "StoreImpl"}, "Status StoreImpl::Write(const Options& o, Batch* b) {\n}"),
        ]
        out = R.rerank_results(nodes, "apply a batch of updates", profiles=[CPP])
        assert _order(out)[0] == "db/store_write.cc"
        # ... but not when the query asks for the declaration
        out = R.rerank_results(nodes, "Write declaration in the header", profiles=[CPP])
        assert _order(out)[0] == "include/store.h"

    def test_declaration_predicate(self):
        pred = CPP.is_declaration_chunk
        assert pred("declaration_group", "a.cc")
        assert pred("class_summary_split", "a.h")
        assert not pred("class_summary_split", "a.cc")
        assert not pred("cpp_function", "a.h")


# ────────────────────────────────────────────────
# Exact class name beats partial
# ────────────────────────────────────────────────


class TestExactClassName:
    def test_exact_class_summary_beats_contained_name(self):
        nodes = [
            _Scored(0.60, {"node_type": "class_summary", "file_path": "query/engine.go", "class_name": "EngineOptions"}, "type EngineOptions struct {}"),
            _Scored(0.45, {"node_type": "class_summary", "file_path": "query/engine.go", "class_name": "Engine"}, "type Engine struct {}"),
        ]
        out = R.rerank_results(nodes, "Describe the Engine struct", profiles=[GO])
        assert out[0].node.metadata["class_name"] == "Engine"

    def test_adjustment_values(self):
        pset = R.get_profile_set([GO])
        assert R._exact_class_adjustment({"class_name": "Engine"}, "class_summary", ["engine"], pset) == R._EXACT_CLASS_BONUS
        assert R._exact_class_adjustment({"class_name": "EngineOptions"}, "class_summary", ["engine"], pset) == -R._PARTIAL_CLASS_PENALTY
        assert R._exact_class_adjustment({"class_name": "Engine"}, "method_declaration", ["engine"], pset) == 0.0
        assert R._exact_class_adjustment({"class_name": "List<T>"}, "class_summary", ["list"], pset) == R._EXACT_CLASS_BONUS
