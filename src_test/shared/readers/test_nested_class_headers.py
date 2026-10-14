"""
Nested-class ``// Class:`` headers for the Java and Kotlin readers.

Nested types carry their outer-class chain in the ``// Class:`` line:
``// Class: Outer > Middle > static class Inner``.  Top-level types are
unchanged.  Java and Kotlin must use the byte-identical format.
"""

from pathlib import Path

import pytest

from shared.readers.java_reader import JavaFileReader
from shared.readers.java_reader import _nested_class_header as java_nested
from shared.readers.kotlin_reader import KotlinFileReader
from shared.readers.kotlin_reader import _nested_class_header as kotlin_nested


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def _class_line(text: str) -> str:
    for line in text.split("\n"):
        if line.startswith("// Class:"):
            return line
        if not line.startswith("// "):
            break
    return ""


def _summary(docs, class_name):
    for d in docs:
        if d.metadata["node_type"].startswith("class_summary") and d.metadata.get("class_name") == class_name:
            return d
    raise AssertionError(f"no class_summary for {class_name}")


def _member(docs, needle):
    for d in docs:
        if not d.metadata["node_type"].startswith("class_") and needle in d.text:
            return d
    raise AssertionError(f"no member chunk containing {needle!r}")


# ── Helper ──────────────────────────────────────────────────────────────


class TestHelper:
    @pytest.mark.parametrize("fn", [java_nested, kotlin_nested])
    def test_top_level_unchanged(self, fn):
        assert fn(["A"], "public class A") == "public class A"
        assert fn([], "class A") == "class A"

    @pytest.mark.parametrize("fn", [java_nested, kotlin_nested])
    def test_chain(self, fn):
        assert fn(["A", "B"], "class B") == "A > class B"
        assert fn(["A", "B", "C"], "static class C") == "A > B > static class C"

    @pytest.mark.parametrize("fn", [java_nested, kotlin_nested])
    def test_none_header(self, fn):
        assert fn(["A", "B"], None) is None

    def test_identical_implementations(self):
        for nesting, header in (
            (["A"], "class A"),
            (["A", "B"], "inner class B"),
            (["A", "B", "C"], "enum class C"),
        ):
            assert java_nested(nesting, header) == kotlin_nested(nesting, header)


# ── Java ────────────────────────────────────────────────────────────────

JAVA_SRC = '''package com.example;

public class Outer extends Base {
    public void outerWork() {
        int a = 1;
        int b = 2;
        System.out.println(a + b);
    }

    public static class StaticNested {
        public void nestedWork() {
            int c = 3;
            System.out.println(c);
        }

        static class Deep {
            void deepWork() {
                int d = 4;
                System.out.println(d);
            }
        }
    }

    public class Inner implements Runnable {
        public void run() {
            int e = 5;
            System.out.println(e);
        }
    }

    enum Mode {
        FAST, SLOW;
        int speed() {
            int s = 1;
            return s;
        }
    }

    interface Callback {
        void onDone(String result);
    }
}
'''


class TestJavaNested:
    @pytest.fixture
    def docs(self, tmp_path):
        return JavaFileReader().load_data(_write(tmp_path, "Outer.java", JAVA_SRC))

    def test_top_level_unchanged(self, docs):
        assert _class_line(_summary(docs, "Outer").text) == "// Class: public class Outer extends Base"
        assert _class_line(_member(docs, "outerWork").text) == "// Class: public class Outer extends Base"

    def test_static_nested(self, docs):
        expected = "// Class: Outer > public static class StaticNested"
        assert _class_line(_summary(docs, "StaticNested").text) == expected
        assert _class_line(_member(docs, "nestedWork").text) == expected

    def test_multi_level(self, docs):
        expected = "// Class: Outer > StaticNested > static class Deep"
        assert _class_line(_summary(docs, "Deep").text) == expected
        assert _class_line(_member(docs, "deepWork").text) == expected

    def test_inner(self, docs):
        expected = "// Class: Outer > public class Inner implements Runnable"
        assert _class_line(_summary(docs, "Inner").text) == expected
        assert _class_line(_member(docs, "public void run()").text) == expected

    def test_nested_enum(self, docs):
        expected = "// Class: Outer > enum Mode"
        assert _class_line(_summary(docs, "Mode").text) == expected
        assert _class_line(_member(docs, "int speed()").text) == expected

    def test_nested_interface(self, docs):
        assert _class_line(_summary(docs, "Callback").text) == "// Class: Outer > interface Callback"

    def test_summary_body_header_not_prefixed(self, docs):
        # Only the prefix line changes; the declaration line inside the summary stays raw.
        assert "\npublic static class StaticNested {\n" in _summary(docs, "StaticNested").text

    def test_trivial_group_in_nested_keeps_chain(self, tmp_path):
        src = "package g;\n\npublic class Holder {\n    public static class Bean {\n" + "".join(
            f"        public int get{i}() {{ return {i}; }}\n" for i in range(4)
        ) + "    }\n}\n"
        docs = JavaFileReader().load_data(_write(tmp_path, "Holder.java", src))
        groups = [d for d in docs if d.metadata["node_type"] == "method_group"]
        assert len(groups) == 1
        assert _class_line(groups[0].text) == "// Class: Holder > public static class Bean"


# ── Kotlin ──────────────────────────────────────────────────────────────

KOTLIN_SRC = '''package com.example

class OrderService : BaseService() {
    fun outerWork() {
        val a = 1
        println(a)
    }

    companion object Factory {
        fun create(): OrderService {
            val s = OrderService()
            return s
        }
    }

    class Nested {
        fun nestedWork() {
            val c = 3
            println(c)
        }

        class Deep {
            fun deepWork() {
                val d = 4
                println(d)
            }
        }
    }

    inner class Inner : Runnable {
        override fun run() {
            val e = 5
            println(e)
        }
    }

    enum class Mode { FAST, SLOW }

    interface Callback {
        fun onDone(result: String)
    }
}

class Plain {
    companion object {
        fun make(): Plain {
            val p = Plain()
            return p
        }
    }
}
'''


class TestKotlinNested:
    @pytest.fixture
    def docs(self, tmp_path):
        return KotlinFileReader().load_data(_write(tmp_path, "OrderService.kt", KOTLIN_SRC))

    def test_top_level_unchanged(self, docs):
        assert _class_line(_summary(docs, "OrderService").text) == "// Class: class OrderService : BaseService()"
        assert _class_line(_member(docs, "fun outerWork").text) == "// Class: class OrderService : BaseService()"

    def test_named_companion(self, docs):
        expected = "// Class: OrderService > companion object Factory"
        assert _class_line(_summary(docs, "Factory").text) == expected
        assert _class_line(_member(docs, "fun create()").text) == expected

    def test_anonymous_companion(self, docs):
        expected = "// Class: Plain > companion object"
        assert _class_line(_summary(docs, "Companion").text) == expected
        assert _class_line(_member(docs, "fun make()").text) == expected

    def test_nested_and_multi_level(self, docs):
        assert _class_line(_summary(docs, "Nested").text) == "// Class: OrderService > class Nested"
        expected = "// Class: OrderService > Nested > class Deep"
        assert _class_line(_summary(docs, "Deep").text) == expected
        assert _class_line(_member(docs, "fun deepWork").text) == expected

    def test_inner(self, docs):
        expected = "// Class: OrderService > inner class Inner : Runnable"
        assert _class_line(_summary(docs, "Inner").text) == expected
        assert _class_line(_member(docs, "override fun run()").text) == expected

    def test_nested_enum_and_interface(self, docs):
        assert _class_line(_summary(docs, "Mode").text) == "// Class: OrderService > enum class Mode"
        assert _class_line(_summary(docs, "Callback").text) == "// Class: OrderService > interface Callback"


# ── Cross-language format ───────────────────────────────────────────────


class TestJavaKotlinNestedConsistency:
    def test_same_chain_format(self, tmp_path):
        java = JavaFileReader().load_data(_write(tmp_path, "A.java",
            "package p;\n\npublic class A {\n    static class B {\n        static class C {\n"
            "            void work() {\n                int x = 1;\n                System.out.println(x);\n"
            "            }\n        }\n    }\n}\n"))
        kotlin = KotlinFileReader().load_data(_write(tmp_path, "A.kt",
            "package p\n\nclass A {\n    class B {\n        class C {\n"
            "            fun work() {\n                val x = 1\n                println(x)\n"
            "            }\n        }\n    }\n}\n"))
        j = _class_line(_member(java, "work()").text)
        k = _class_line(_member(kotlin, "fun work()").text)
        assert j == "// Class: A > B > static class C"
        assert k == "// Class: A > B > class C"
        assert j.rsplit(" > ", 1)[0] == k.rsplit(" > ", 1)[0] == "// Class: A > B"
