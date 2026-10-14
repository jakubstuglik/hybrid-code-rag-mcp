"""
Content-coverage regressions for the Kotlin reader found on a real Android
codebase: empty-body classes, doc comments inside classes, multi-line enum
entries and enum entries with bodies.
"""

from pathlib import Path

import pytest

from shared.readers.kotlin_reader import KotlinFileReader


def _load(tmp_path: Path, src: str, name: str = "F.kt"):
    p = tmp_path / name
    p.write_text(src, encoding="utf-8")
    return KotlinFileReader().load_data(p)


def _all_text(docs):
    return "\n".join(d.text for d in docs)


class TestEmptyBodyClass:
    def test_exception_with_empty_body_is_indexed(self, tmp_path):
        src = (
            "package a.b\n\n"
            "class RegisterPaymentException(\n"
            "    val reason: PaymentErrorReason,\n"
            "    val history: String,\n"
            "    val statusMessage: String?\n"
            ") : Exception() {\n}\n"
        )
        docs = _load(tmp_path, src)
        summaries = [d for d in docs if d.metadata["node_type"] == "class_summary"]
        assert len(summaries) == 1
        s = summaries[0]
        assert s.metadata["class_name"] == "RegisterPaymentException"
        assert "// Class: class RegisterPaymentException(" in s.text
        assert "val statusMessage: String?" in s.text
        assert s.metadata["start_line"] == 3

    def test_class_with_only_comment_in_body(self, tmp_path):
        src = "class Callback : IBaseCallback {\n    // nothing to do here yet\n}\n"
        docs = _load(tmp_path, src)
        assert any(
            d.metadata["node_type"] == "class_summary" and "class Callback : IBaseCallback" in d.text
            for d in docs
        )

    def test_data_class_with_empty_body_keeps_all_params(self, tmp_path):
        params = "\n".join(
            f'    /* Field {i} doc. */\n    @SerializedName("f{i}")\n    val f{i}: kotlin.Boolean,'
            for i in range(7)
        )
        src = f"package m\n\ndata class DaysDTO (\n{params}\n) {{\n}}\n"
        text = _all_text(_load(tmp_path, src))
        for i in range(7):
            assert f"val f{i}: kotlin.Boolean" in text
            assert f"Field {i} doc." in text


class TestDocComments:
    SRC = (
        "package d\n\n"
        "class Service {\n"
        "    /**\n"
        "     * Computes the fare for the passenger.\n"
        "     */\n"
        "    fun fare(km: Int): Int {\n"
        "        val base = 3\n"
        "        return base * km\n"
        "    }\n\n"
        "    // Max seats per bus\n"
        "    val maxSeats = 50\n\n"
        "    /** Nested helper. */\n"
        "    class Helper {\n"
        "        fun help(): Int {\n"
        "            return 1\n"
        "        }\n"
        "    }\n"
        "}\n"
    )

    def test_kdoc_attached_to_function(self, tmp_path):
        docs = _load(tmp_path, self.SRC)
        f = [d for d in docs if d.metadata.get("function_name") == "fare"][0]
        assert "Computes the fare for the passenger." in f.text
        # prefix still first, doc before the code
        assert f.text.index("// Class: class Service") < f.text.index("/**") < f.text.index("fun fare")

    def test_line_comment_attached_to_property(self, tmp_path):
        docs = _load(tmp_path, self.SRC)
        p = [d for d in docs if d.metadata["node_type"] == "field_declaration"][0]
        assert "// Max seats per bus" in p.text

    def test_kdoc_attached_to_nested_class_summary(self, tmp_path):
        docs = _load(tmp_path, self.SRC)
        s = [d for d in docs if d.metadata.get("class_name") == "Helper" and d.metadata["node_type"] == "class_summary"][0]
        assert s.text.startswith("// File: F.kt\n// Package: d\n// Class: Service > class Helper\n/** Nested helper. */")

    def test_comment_separated_by_blank_line_not_attached(self, tmp_path):
        src = (
            "class S {\n"
            "    /** Orphan comment that is not attached anywhere. */\n\n"
            "    fun g(): Int {\n        return 2\n    }\n}\n"
        )
        docs = _load(tmp_path, src)
        g = [d for d in docs if d.metadata.get("function_name") == "g"][0]
        assert "Orphan comment" not in g.text

    def test_no_duplicate_top_level_kdoc(self, tmp_path):
        src = "/** Top level documentation for the class Foo here. */\nclass Foo {\n    fun a(): Int {\n        return 1\n    }\n}\n"
        text = _all_text(_load(tmp_path, src))
        assert text.count("Top level documentation") == 1


class TestEnumEntries:
    def test_multiline_entry_arguments_in_summary(self, tmp_path):
        src = (
            "enum class TicketType(val code: Int, val label: String) {\n"
            "    SINGLE(\n        1,\n        \"Jednorazowy\"\n    ),\n"
            "    MONTHLY(2, \"Miesieczny\");\n"
            "}\n"
        )
        s = [d for d in _load(tmp_path, src) if d.metadata["node_type"] == "class_summary"][0]
        assert 'SINGLE( 1, "Jednorazowy" )' in s.text
        assert 'MONTHLY(2, "Miesieczny")' in s.text

    def test_entry_with_body_emitted(self, tmp_path):
        src = (
            "enum class Op {\n"
            "    PLUS {\n        override fun apply(a: Int, b: Int) = a + b\n    },\n"
            "    MINUS {\n        override fun apply(a: Int, b: Int) = a - b\n    };\n"
            "    abstract fun apply(a: Int, b: Int): Int\n"
            "}\n"
        )
        docs = _load(tmp_path, src)
        s = [d for d in docs if d.metadata["node_type"] == "class_summary"][0]
        assert "PLUS { ... }" in s.text
        consts = [d for d in docs if d.metadata["node_type"] == "enum_constant"]
        assert len(consts) == 2
        assert any("a - b" in d.text for d in consts)
        assert all(d.text.startswith("// File: F.kt\n// Class: enum class Op") for d in consts)

    def test_simple_entries_not_emitted_separately(self, tmp_path):
        docs = _load(tmp_path, "enum class Color { RED, GREEN, BLUE }\n")
        assert not [d for d in docs if d.metadata["node_type"] == "enum_constant"]


class TestEnumEntryComments:
    SRC = (
        "package a.b\n\n"
        "enum class Card(val code: Long) {\n"
        "    /** Empty card. */\n"
        "    EMPTY(-2),           // QR code or missing\n"
        "    UNKNOWN(-1),         // Unknown card type\n"
        "    // Classic card\n"
        "    CLASSIC(1);\n\n"
        "    fun isKnown() = code > 0\n"
        "}\n"
    )

    def _summary(self, tmp_path):
        docs = _load(tmp_path, self.SRC)
        return next(d for d in docs if d.metadata["node_type"] == "class_summary").text

    def test_trailing_comment_kept_on_entry_line(self, tmp_path):
        s = self._summary(tmp_path)
        assert "EMPTY(-2)  // QR code or missing" in s
        assert "UNKNOWN(-1)  // Unknown card type" in s

    def test_leading_doc_kept_above_entry(self, tmp_path):
        s = self._summary(tmp_path)
        assert "/** Empty card. */\n    EMPTY(-2)" in s or "/** Empty card. */\nEMPTY(-2)" in s.replace("    ", "")
        assert "// Classic card" in s

    def test_trailing_comment_not_duplicated_as_next_doc(self, tmp_path):
        s = self._summary(tmp_path)
        assert s.count("QR code or missing") == 1
        assert s.count("Unknown card type") == 1
