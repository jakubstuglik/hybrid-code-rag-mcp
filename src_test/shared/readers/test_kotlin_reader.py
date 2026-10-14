"""
Tests for shared/readers/kotlin_reader.py - Kotlin reader with Tree-sitter AST.

Covers: registry wiring (.kt/.kts), context prefix format (identical to the
Java reader), class/object/interface/companion/enum/sealed/data classes,
nested classes, top-level and extension functions, properties, type aliases,
secondary constructors, init blocks, import grouping, trivial-method grouping,
oversized splitting, .kts scripts, grammar-gap recovery (ERROR nodes),
fallbacks, and header consistency across Delphi, Java and Kotlin.
"""

import re
from pathlib import Path

import pytest

from shared.readers import READER_REGISTRY, get_reader
from shared.readers.java_reader import JavaFileReader
from shared.readers.java_reader import _build_context_prefix as java_prefix
from shared.readers.kotlin_reader import (
    KotlinFileReader,
    _build_context_prefix,
)
from shared.readers.pascal_reader import DelphiFileReader


SAMPLE = '''package com.example.orders

import java.util.UUID
import kotlinx.coroutines.flow.Flow as KFlow

@Service
class OrderService(private val repo: OrderRepository) : BaseService(), Auditable {
    private val cache = mutableMapOf<Long, Order>()

    constructor() : this(InMemoryRepository())

    init {
        log("created")
    }

    fun findOpen(customerId: Long): List<Order> {
        val all = repo.findByCustomer(customerId)
        log("findOpen")
        audit(customerId)
        validate(all)
        return all.filterNot { it.closed }
    }

    companion object Factory {
        const val MAX = 100
        fun create(): OrderService = OrderService()
    }

    inner class Line(val sku: String) {
        fun describeLine(): String {
            val text = "line " + sku
            return text
        }
    }
}

data class Order(val id: Long, val closed: Boolean = false)

sealed class Result {
    data class Ok(val value: Order) : Result()
    object Fail : Result()
}

enum class Status(val code: Int) {
    OPEN(1), CLOSED(2);
    fun label() = name.lowercase()
}

interface OrderRepository {
    fun findByCustomer(id: Long): List<Order>
}

object Registry : Auditable {
    fun register(o: Order) { println(o) }
}

typealias OrderId = Long

val DEFAULT_LIMIT = 50

fun Order.describe(): String = "Order $id closed=$closed"

suspend fun loadAll(repo: OrderRepository): List<Order> {
    return repo.findByCustomer(1L)
}
'''


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture
def reader() -> KotlinFileReader:
    return KotlinFileReader()


@pytest.fixture
def sample_docs(tmp_path, reader):
    return reader.load_data(_write(tmp_path, "OrderService.kt", SAMPLE))


def _by_type(docs, node_type):
    return [d for d in docs if d.metadata["node_type"] == node_type]


def _summary(docs, class_name):
    found = [
        d
        for d in _by_type(docs, "class_summary")
        if d.metadata.get("class_name") == class_name
    ]
    assert found, f"no class_summary for {class_name}"
    return found[0]


def _prefix_lines(text):
    out = []
    for line in text.split("\n"):
        if not line.startswith("// "):
            break
        out.append(line)
    return out


# ── Registry ─────────────────────────────────────────────────────────────


class TestRegistry:
    def test_kt_registered(self):
        assert isinstance(READER_REGISTRY[".kt"], KotlinFileReader)

    def test_kts_registered(self):
        assert isinstance(READER_REGISTRY[".kts"], KotlinFileReader)

    def test_get_reader_path_and_upper_case(self):
        assert isinstance(get_reader(Path("A/B/Foo.KT")), KotlinFileReader)
        assert isinstance(get_reader(Path("build.gradle.kts")), KotlinFileReader)

    def test_existing_readers_untouched(self):
        assert isinstance(READER_REGISTRY[".java"], JavaFileReader)
        assert isinstance(READER_REGISTRY[".pas"], DelphiFileReader)


# ── Context prefix ───────────────────────────────────────────────────────


class TestContextPrefix:
    def test_full(self):
        assert _build_context_prefix("A.kt", "p.q", "A", "class A") == (
            "// File: A.kt\n// Package: p.q\n// Class: class A"
        )

    def test_no_package(self):
        assert _build_context_prefix("A.kt", None, "A", None) == (
            "// File: A.kt\n// Class: A"
        )

    def test_file_only(self):
        assert _build_context_prefix("A.kt") == "// File: A.kt"

    @pytest.mark.parametrize(
        "args",
        [
            ("X.kt",),
            ("X.kt", "a.b"),
            ("X.kt", "a.b", "X"),
            ("X.kt", "a.b", "X", "public class X"),
            ("X.kt", None, "X", "object X"),
        ],
    )
    def test_identical_to_java(self, args):
        assert _build_context_prefix(*args) == java_prefix(*args)


# ── Chunks of the sample file ────────────────────────────────────────────


class TestSampleFile:
    def test_every_chunk_has_file_and_package(self, sample_docs):
        assert sample_docs
        for d in sample_docs:
            lines = _prefix_lines(d.text)
            assert lines[0] == "// File: OrderService.kt", d.text
            assert lines[1] == "// Package: com.example.orders", d.text

    def test_metadata_common(self, sample_docs):
        for d in sample_docs:
            assert d.metadata["package_name"] == "com.example.orders"
            assert d.metadata["unit_name"] == "OrderService"
            assert d.metadata["file_path"].endswith("OrderService.kt")

    def test_import_group(self, sample_docs):
        imports = _by_type(sample_docs, "import_group")
        assert len(imports) == 1
        assert "import java.util.UUID" in imports[0].text
        assert "import kotlinx.coroutines.flow.Flow as KFlow" in imports[0].text
        assert "// Class:" not in imports[0].text
        assert imports[0].metadata["start_line"] == 3
        assert imports[0].metadata["end_line"] == 4

    def test_class_summary_header_and_members(self, sample_docs):
        d = _summary(sample_docs, "OrderService")
        assert (
            "// Class: @Service class OrderService(private val repo: OrderRepository)"
            " : BaseService(), Auditable" in d.text
        )
        assert "    fun findOpen(customerId: Long): List<Order>" in d.text
        assert "    constructor() : this(InMemoryRepository())" in d.text
        assert "    init { ... }" in d.text
        assert "    private val cache = mutableMapOf<Long, Order>()" in d.text
        assert "    companion object Factory { ... }" in d.text
        assert "    inner class Line(val sku: String) { ... }" in d.text
        # No bodies in summary
        assert "validate(all)" not in d.text
        assert d.metadata["kotlin_kind"] == "class"

    def test_method_chunk_has_class_line(self, sample_docs):
        m = [
            d
            for d in _by_type(sample_docs, "method_declaration")
            if d.metadata.get("function_name") == "findOpen"
        ][0]
        assert _prefix_lines(m.text)[2].startswith("// Class: @Service class OrderService(")
        assert "validate(all)" in m.text
        assert m.metadata["class_name"] == "OrderService"

    def test_secondary_constructor_and_init(self, sample_docs):
        ctor = _by_type(sample_docs, "constructor_declaration")
        assert ctor and "constructor() : this(" in ctor[0].text
        init = _by_type(sample_docs, "initializer_block")
        assert init and 'log("created")' in init[0].text

    def test_property(self, sample_docs):
        fields = _by_type(sample_docs, "field_declaration")
        texts = "\n".join(d.text for d in fields)
        assert "private val cache" in texts
        assert "const val MAX = 100" in texts
        top = [d for d in fields if "DEFAULT_LIMIT" in d.text][0]
        assert "// Class:" not in top.text

    def test_companion_object(self, sample_docs):
        d = _summary(sample_docs, "Factory")
        assert "// Class: OrderService > companion object Factory" in d.text
        assert "fun create(): OrderService" in d.text
        assert d.metadata["kotlin_kind"] == "companion object"
        assert d.metadata["outer_class"] == "OrderService"

    def test_unnamed_companion(self, tmp_path, reader):
        src = "class A {\n    companion object {\n        fun make(): A = A()\n    }\n}\n"
        docs = reader.load_data(_write(tmp_path, "A.kt", src))
        d = _summary(docs, "Companion")
        assert "// Class: A > companion object" in d.text
        assert d.metadata["outer_class"] == "A"

    def test_nested_inner_class(self, sample_docs):
        d = _summary(sample_docs, "Line")
        assert "// Class: OrderService > inner class Line(val sku: String)" in d.text
        assert d.metadata["outer_class"] == "OrderService"
        m = [
            x
            for x in sample_docs
            if x.metadata.get("function_name") == "describeLine"
        ][0]
        assert "// Class: OrderService > inner class Line(val sku: String)" in m.text

    def test_data_class_without_body(self, sample_docs):
        d = _summary(sample_docs, "Order")
        assert "// Class: data class Order(val id: Long, val closed: Boolean = false)" in d.text
        assert d.metadata["kotlin_kind"] == "data class"

    def test_sealed_class_and_subtypes(self, sample_docs):
        d = _summary(sample_docs, "Result")
        assert d.metadata["kotlin_kind"] == "sealed class"
        assert "data class Ok(val value: Order) : Result() { ... }" in d.text
        assert "object Fail : Result() { ... }" in d.text
        assert _summary(sample_docs, "Ok").metadata["outer_class"] == "Result"
        assert _summary(sample_docs, "Fail").metadata["kotlin_kind"] == "object"

    def test_enum_class(self, sample_docs):
        d = _summary(sample_docs, "Status")
        assert d.metadata["kotlin_kind"] == "enum class"
        assert "    OPEN(1)" in d.text and "    CLOSED(2)" in d.text
        # member after ';' is recovered even though the grammar wraps it in ERROR
        assert "    fun label()" in d.text
        # enum entries are covered by the summary, no standalone chunks
        assert not _by_type(sample_docs, "enum_constant")

    def test_interface_abstract_member(self, sample_docs):
        d = _summary(sample_docs, "OrderRepository")
        assert d.metadata["kotlin_kind"] == "interface"
        assert "    fun findByCustomer(id: Long): List<Order>" in d.text

    def test_object_declaration(self, sample_docs):
        d = _summary(sample_docs, "Registry")
        assert "// Class: object Registry : Auditable" in d.text
        assert d.metadata["kotlin_kind"] == "object"

    def test_type_alias(self, sample_docs):
        ta = _by_type(sample_docs, "type_alias_declaration")
        assert ta and "typealias OrderId = Long" in ta[0].text
        assert "// Class:" not in ta[0].text

    def test_extension_function(self, sample_docs):
        ext = [
            d
            for d in _by_type(sample_docs, "method_declaration")
            if d.metadata.get("function_name") == "describe"
        ][0]
        assert ext.metadata["receiver_type"] == "Order"
        assert "fun Order.describe(): String" in ext.text
        assert "// Class:" not in ext.text
        assert "class_name" not in ext.metadata

    def test_top_level_suspend_function(self, sample_docs):
        f = [
            d
            for d in sample_docs
            if d.metadata.get("function_name") == "loadAll"
        ][0]
        assert f.text.startswith(
            "// File: OrderService.kt\n// Package: com.example.orders\nsuspend fun loadAll("
        )
        assert "receiver_type" not in f.metadata

    def test_line_numbers(self, sample_docs):
        d = _summary(sample_docs, "OrderService")
        assert d.metadata["start_line"] == 6
        for x in sample_docs:
            assert 1 <= x.metadata["start_line"] <= x.metadata["end_line"]


# ── Behaviour shared with Java ───────────────────────────────────────────


class TestGroupingAndSplitting:
    def test_trivial_methods_grouped(self, tmp_path, reader):
        src = "package p\n\nclass Bean {\n" + "".join(
            f"    fun get{i}(): Int = {i}\n" for i in range(5)
        ) + "}\n"
        docs = reader.load_data(_write(tmp_path, "Bean.kt", src))
        groups = _by_type(docs, "method_group")
        assert len(groups) == 1
        g = groups[0]
        assert g.metadata["group_count"] == 5
        assert g.text.startswith(
            "// File: Bean.kt\n// Package: p\n// Class: class Bean\n// Method group: 5 methods"
        )
        assert not _by_type(docs, "method_declaration")

    def test_two_trivial_methods_not_grouped(self, tmp_path, reader):
        src = "class Bean {\n    fun a(): Int = 1\n    fun b(): Int = 2\n}\n"
        docs = reader.load_data(_write(tmp_path, "Bean.kt", src))
        assert not _by_type(docs, "method_group")
        assert len(_by_type(docs, "method_declaration")) == 2

    def test_oversized_function_split_keeps_prefix(self, tmp_path, reader):
        body = "\n".join(f'        println("line number {i} of a very long function")' for i in range(1200))
        src = f"package big\n\nclass Big {{\n    fun huge() {{\n{body}\n    }}\n}}\n"
        docs = reader.load_data(_write(tmp_path, "Big.kt", src))
        parts = _by_type(docs, "method_declaration_split")
        assert len(parts) > 1
        for p in parts:
            assert p.text.startswith("// File: Big.kt\n// Package: big\n// Class: class Big\n")

    def test_large_class_gets_overview(self, tmp_path, reader):
        members = "".join(
            f"    fun operationNumber{i}(argumentOne: String, argumentTwo: Int): Map<String, List<Int>> {{\n"
            f"        return emptyMap()\n        // padding line\n        // padding line\n"
            f"        // padding line\n        // padding line\n    }}\n"
            for i in range(80)
        )
        src = f"package big\n\nabstract class Huge : Base() {{\n{members}}}\n"
        docs = reader.load_data(_write(tmp_path, "Huge.kt", src))
        ov = _by_type(docs, "class_overview")
        assert len(ov) == 1
        assert "// Huge is a Kotlin abstract class extending Base() with 80 functions." in ov[0].text
        assert "... (60 more)" in ov[0].text
        assert _by_type(docs, "class_summary_split")

    def test_short_comment_skipped_long_kept(self, tmp_path, reader):
        src = (
            "package c\n\n// tiny\n"
            "/* This is a long standalone block comment describing the module purpose. */\n"
            "fun f(): Int {\n    return 1\n}\n"
        )
        docs = reader.load_data(_write(tmp_path, "C.kt", src))
        comments = _by_type(docs, "block_comment")
        assert len(comments) == 1
        assert "long standalone block comment" in comments[0].text


# ── Scripts, edge cases, fallbacks ───────────────────────────────────────


class TestEdgeCases:
    def test_kts_script(self, tmp_path, reader):
        src = (
            'plugins {\n    kotlin("jvm") version "2.0.0"\n}\n\n'
            'dependencies {\n    implementation("org.example:lib:1.0")\n}\n\n'
            'fun helperVersion(): String = "1.0"\n'
        )
        docs = reader.load_data(_write(tmp_path, "build.gradle.kts", src))
        script = _by_type(docs, "script_body")
        assert len(script) == 1
        assert script[0].text.startswith("// File: build.gradle.kts\nplugins {")
        assert "org.example:lib:1.0" in script[0].text
        assert any(d.metadata.get("function_name") == "helperVersion" for d in docs)

    def test_kt_top_level_statements_ignored_without_crash(self, tmp_path, reader):
        docs = reader.load_data(_write(tmp_path, "X.kt", "fun main() {\n    println(1)\n}\n"))
        assert not _by_type(docs, "script_body")

    def test_empty_file(self, tmp_path, reader):
        assert reader.load_data(_write(tmp_path, "E.kt", "   \n")) == []

    def test_missing_file(self, tmp_path, reader):
        assert reader.load_data(tmp_path / "missing.kt") == []

    def test_fallback_full_file(self, tmp_path, reader):
        docs = reader.load_data(_write(tmp_path, "P.kt", "package only.here\n"))
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"
        assert docs[0].metadata["package_name"] == "only.here"

    def test_no_package(self, tmp_path, reader):
        docs = reader.load_data(
            _write(tmp_path, "N.kt", "class N {\n    fun go(): Int {\n        return 42\n    }\n}\n")
        )
        for d in docs:
            assert "// Package:" not in d.text
            assert "package_name" not in d.metadata

    def test_generic_reified_extension(self, tmp_path, reader):
        src = (
            "package g\n\n"
            "inline fun <reified T : Any> Map<String, Any>.getTyped(key: String): T? {\n"
            "    return this[key] as? T\n}\n"
        )
        docs = reader.load_data(_write(tmp_path, "G.kt", src))
        f = [d for d in docs if d.metadata.get("function_name") == "getTyped"][0]
        assert f.metadata["receiver_type"] == "Map<String, Any>"

    def test_annotated_multiline_header_collapsed(self, tmp_path, reader):
        src = (
            "package a\n\n@Entity\n@Table(name = \"orders\")\n"
            "class OrderEntity(\n    val id: Long,\n    val name: String\n) : Base() {\n"
            "    fun touch() {\n        println(id)\n    }\n}\n"
        )
        docs = reader.load_data(_write(tmp_path, "OrderEntity.kt", src))
        d = _summary(docs, "OrderEntity")
        assert (
            '// Class: @Entity @Table(name = "orders") class OrderEntity( val id: Long, val name: String ) : Base()'
            in d.text
        )

    def test_reader_via_load_nodes_for_file(self, tmp_path):
        from shared.readers import load_nodes_for_file

        p = _write(tmp_path, "OrderService.kt", SAMPLE)
        nodes = load_nodes_for_file({"full_path": str(p), "file_path": "src/OrderService.kt"})
        assert nodes
        assert all(n.metadata["file_path"] == "src/OrderService.kt" for n in nodes)


# ── Header consistency across Delphi / Java / Kotlin ────────────────────

JAVA_SRC = '''package com.example.orders;

public class OrderService extends BaseService {
    public java.util.List<Order> findOpen(long customerId) {
        java.util.List<Order> all = repo.findByCustomer(customerId);
        log("findOpen");
        validate(all);
        return all;
    }
}
'''

KOTLIN_SRC = '''package com.example.orders

class OrderService : BaseService() {
    fun findOpen(customerId: Long): List<Order> {
        val all = repo.findByCustomer(customerId)
        log("findOpen")
        validate(all)
        return all
    }
}
'''

PASCAL_SRC = '''unit OrderService;

interface

type
  TOrderService = class(TBaseService)
  public
    function FindOpen(CustomerId: Integer): TOrderList;
  end;

implementation

function TOrderService.FindOpen(CustomerId: Integer): TOrderList;
begin
  Result := FRepo.FindByCustomer(CustomerId);
  Log('FindOpen');
  Validate(Result);
end;

end.
'''

_HEADER_LINE = re.compile(r"^// (File|Package|Unit|Class): .+$")


class TestHeaderConsistency:
    @pytest.fixture
    def all_docs(self, tmp_path):
        return {
            "java": JavaFileReader().load_data(_write(tmp_path, "OrderService.java", JAVA_SRC)),
            "kotlin": KotlinFileReader().load_data(_write(tmp_path, "OrderService.kt", KOTLIN_SRC)),
            "pascal": DelphiFileReader().load_data(_write(tmp_path, "OrderService.pas", PASCAL_SRC)),
        }

    @staticmethod
    def _labels(text):
        return [_HEADER_LINE.match(l).group(1) for l in _prefix_lines(text) if _HEADER_LINE.match(l)]

    def test_every_chunk_starts_with_context_header(self, all_docs):
        for lang, docs in all_docs.items():
            assert docs, lang
            for d in docs:
                assert _prefix_lines(d.text), (lang, d.text)
                assert _HEADER_LINE.match(d.text.split("\n")[0]), (lang, d.text)

    def test_class_member_chunks_have_class_line(self, all_docs):
        for lang, node_type in (
            ("java", "method_declaration"),
            ("kotlin", "method_declaration"),
            ("pascal", "defProc"),
        ):
            chunks = [d for d in all_docs[lang] if d.metadata["node_type"] == node_type]
            assert chunks, lang
            for c in chunks:
                assert self._labels(c.text)[-1] == "Class", (lang, c.text)
                assert c.metadata["class_name"].lstrip("T") == "OrderService"

    def test_jvm_languages_identical_label_sequence(self, all_docs):
        for node_type in ("class_summary", "method_declaration"):
            java = [d for d in all_docs["java"] if d.metadata["node_type"] == node_type][0]
            kt = [d for d in all_docs["kotlin"] if d.metadata["node_type"] == node_type][0]
            assert self._labels(java.text) == self._labels(kt.text) == ["File", "Package", "Class"]
            assert _prefix_lines(java.text)[1] == _prefix_lines(kt.text)[1]

    def test_pascal_label_sequence(self, all_docs):
        d = [x for x in all_docs["pascal"] if x.metadata["node_type"] == "defProc"][0]
        assert self._labels(d.text) == ["Unit", "Class"]
        assert d.text.startswith("// Unit: OrderService (OrderService.pas)\n// Class: TOrderService = class(TBaseService)")

    def test_class_line_carries_inheritance(self, all_docs):
        lines = {
            lang: [l for l in _prefix_lines([d for d in docs if d.metadata["node_type"] == "class_summary"][0].text) if l.startswith("// Class:")][0]
            for lang, docs in all_docs.items()
        }
        assert lines["java"] == "// Class: public class OrderService extends BaseService"
        assert lines["kotlin"] == "// Class: class OrderService : BaseService()"
        assert lines["pascal"] == "// Class: TOrderService = class(TBaseService)"

    def test_shared_metadata_keys(self, all_docs):
        for lang, docs in all_docs.items():
            for d in docs:
                assert "unit_name" in d.metadata, lang
                assert d.metadata["unit_name"] == "OrderService"


# ── Reranker target extraction ───────────────────────────────────────────


class TestRerankerTargets:
    def test_kt_file_stem(self):
        from shared.reranker import extract_target_identifiers

        assert "orderservice" in extract_target_identifiers("what does OrderService.kt do?")

    def test_kts_file_stem(self):
        from shared.reranker import extract_target_identifiers

        assert "build.gradle" in extract_target_identifiers("dependencies in build.gradle.kts")


class TestNestedHeaderConsistency:
    """Nested types: Java and Kotlin put the outer-class chain in ``// Class:``."""

    def test_nested_chain_identical_between_java_and_kotlin(self, tmp_path):
        java = JavaFileReader().load_data(_write(tmp_path, "OrderService.java",
            "package com.example.orders;\n\npublic class OrderService {\n"
            "    class Line {\n        void describe() {\n            int a = 1;\n"
            "            System.out.println(a);\n        }\n    }\n}\n"))
        kotlin = KotlinFileReader().load_data(_write(tmp_path, "OrderService.kt",
            "package com.example.orders\n\nclass OrderService {\n"
            "    class Line {\n        fun describe() {\n            val a = 1\n"
            "            println(a)\n        }\n    }\n}\n"))
        j = [d for d in java if d.metadata["node_type"] == "method_declaration"][0]
        k = [d for d in kotlin if d.metadata["node_type"] == "method_declaration"][0]
        assert _prefix_lines(j.text)[2] == _prefix_lines(k.text)[2] == "// Class: OrderService > class Line"
        assert _prefix_lines(j.text)[:2] == [
            "// File: OrderService.java", "// Package: com.example.orders"]
