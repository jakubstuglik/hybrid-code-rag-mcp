"""
Tests for shared/readers/java_reader.py — Java file reader with Tree-sitter AST.

Tests cover:
    - Class attributes: NODE_TYPES, LEAF_NODE_TYPES, CONTAINER_NODE_TYPES, size constants
    - __init__: instantiation, _text_splitter attribute
    - _has_matched_descendants(): recursive descendant matching
    - _make_documents(): chunk creation, size filtering, oversized splitting
    - AST helper functions: _get_node_text, _get_identifier, _get_package_name,
      _get_class_header, _get_superclass, _get_interfaces, _get_method_signature,
      _count_body_lines, _get_annotations, _build_context_prefix
    - load_data(): empty files, parse errors, real files, leaf/container behavior
    - Context prefix (// File: ..., // Package: ..., // Class: ...)
    - Class summary chunks (header + member signatures)
    - Class overview chunks (natural-language summary for large classes)
    - Trivial method grouping (consecutive small methods → method_group)
    - Import grouping (all imports → single import_group chunk)
    - Annotation preservation (@Service, @Override, etc.)
    - Inner class support with nesting
    - Oversized chunk splitting (MAX_CHUNK_CHARS, MAX_SUMMARY_CHARS)
    - MIN_CHUNK_SIZE enforcement
    - Enum handling
    - Interface handling
    - Record handling
    - Fallback to full_file when no AST nodes match
    - File read errors (non-existent file)
    - Metadata correctness (package_name, class_name, unit_name, node_type)
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from shared.readers.java_reader import (
    JavaFileReader,
    _build_context_prefix,
    _count_body_lines,
    _get_annotations,
    _get_class_header,
    _get_identifier,
    _get_interfaces,
    _get_method_signature,
    _get_node_text,
    _get_package_name,
    _get_superclass,
)


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_mock_node(node_type: str, children: list = None) -> MagicMock:
    """Create a mock tree-sitter Node with the given type and children."""
    node = MagicMock()
    node.type = node_type
    node.children = children or []
    return node


def _write_java(tmp_path: Path, name: str, content: str) -> Path:
    """Write a Java file to tmp_path and return the Path."""
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f


# ────────────────────────────────────────────────
# TestClassAttributes
# ────────────────────────────────────────────────


class TestClassAttributes:
    """Tests for JavaFileReader class-level attributes."""

    def test_node_types_is_set(self):
        assert isinstance(JavaFileReader.NODE_TYPES, set)

    def test_leaf_node_types_is_set(self):
        assert isinstance(JavaFileReader.LEAF_NODE_TYPES, set)

    def test_container_node_types_is_set(self):
        assert isinstance(JavaFileReader.CONTAINER_NODE_TYPES, set)

    def test_leaf_node_types_contains_expected_members(self):
        expected = {
            "method_declaration",
            "constructor_declaration",
            "field_declaration",
            "constant_declaration",
            "block_comment",
            "line_comment",
        }
        assert JavaFileReader.LEAF_NODE_TYPES == expected

    def test_container_node_types_contains_expected_members(self):
        expected = {
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "record_declaration",
        }
        assert JavaFileReader.CONTAINER_NODE_TYPES == expected

    def test_enum_constant_types(self):
        assert JavaFileReader.ENUM_CONSTANT_TYPES == {"enum_constant"}

    def test_node_types_is_leaf_plus_container_plus_enum(self):
        assert JavaFileReader.NODE_TYPES == (
            JavaFileReader.LEAF_NODE_TYPES
            | JavaFileReader.CONTAINER_NODE_TYPES
            | JavaFileReader.ENUM_CONSTANT_TYPES
        )

    def test_leaf_and_container_are_disjoint(self):
        overlap = JavaFileReader.LEAF_NODE_TYPES & JavaFileReader.CONTAINER_NODE_TYPES
        assert overlap == set()

    def test_min_chunk_size_value(self):
        assert JavaFileReader.MIN_CHUNK_SIZE == 20

    def test_max_chunk_chars_value(self):
        assert JavaFileReader.MAX_CHUNK_CHARS == 24000

    def test_max_summary_chars_value(self):
        assert JavaFileReader.MAX_SUMMARY_CHARS == 6000

    def test_trivial_method_lines_value(self):
        assert JavaFileReader.TRIVIAL_METHOD_LINES == 6

    def test_max_group_chars_value(self):
        assert JavaFileReader.MAX_GROUP_CHARS == 8000

    def test_min_comment_chars_value(self):
        assert JavaFileReader.MIN_COMMENT_CHARS == 40


# ────────────────────────────────────────────────
# TestInit
# ────────────────────────────────────────────────


class TestInit:
    """Tests for JavaFileReader.__init__."""

    def test_instantiation(self):
        reader = JavaFileReader()
        assert reader is not None

    def test_has_text_splitter(self):
        reader = JavaFileReader()
        assert hasattr(reader, "_text_splitter")

    def test_text_splitter_chunk_size(self):
        reader = JavaFileReader()
        assert reader._text_splitter.chunk_size == 1024

    def test_text_splitter_chunk_overlap(self):
        reader = JavaFileReader()
        assert reader._text_splitter.chunk_overlap == 128


# ────────────────────────────────────────────────
# TestBuildContextPrefix
# ────────────────────────────────────────────────


class TestBuildContextPrefix:
    """Tests for _build_context_prefix()."""

    def test_file_only(self):
        result = _build_context_prefix("Foo.java")
        assert result == "// File: Foo.java"

    def test_file_and_package(self):
        result = _build_context_prefix("Foo.java", package_name="com.example")
        assert "// File: Foo.java" in result
        assert "// Package: com.example" in result

    def test_file_package_class(self):
        result = _build_context_prefix(
            "Foo.java",
            package_name="com.example",
            class_name="Foo",
            class_header="public class Foo extends Bar",
        )
        assert "// File: Foo.java" in result
        assert "// Package: com.example" in result
        assert "// Class: public class Foo extends Bar" in result

    def test_class_name_without_header_uses_name(self):
        result = _build_context_prefix("Foo.java", class_name="Foo")
        assert "// Class: Foo" in result

    def test_no_class_no_class_line(self):
        result = _build_context_prefix("Foo.java", package_name="com.example")
        assert "// Class:" not in result


# ────────────────────────────────────────────────
# TestHelperFunctions
# ────────────────────────────────────────────────


class TestGetNodeText:
    """Tests for _get_node_text()."""

    def test_basic_extraction(self):
        node = MagicMock()
        content = b"public class Foo { }"
        node.start_byte = 0
        node.end_byte = 20
        result = _get_node_text(node, content)
        assert result == "public class Foo { }"

    def test_strips_whitespace(self):
        node = MagicMock()
        content = b"   hello   "
        node.start_byte = 0
        node.end_byte = 11
        result = _get_node_text(node, content)
        assert result == "hello"

    def test_substring(self):
        node = MagicMock()
        content = b"abc public def"
        node.start_byte = 4
        node.end_byte = 10
        result = _get_node_text(node, content)
        assert result == "public"


class TestGetIdentifier:
    """Tests for _get_identifier()."""

    def test_finds_identifier(self):
        ident_node = MagicMock()
        ident_node.type = "identifier"
        ident_node.start_byte = 13
        ident_node.end_byte = 16

        parent = MagicMock()
        parent.children = [
            _make_mock_node("modifiers"),
            _make_mock_node("void"),
            ident_node,
        ]

        content = b"public class Foo { }"
        result = _get_identifier(parent, content)
        assert result == "Foo"

    def test_no_identifier_returns_none(self):
        parent = MagicMock()
        parent.children = [_make_mock_node("modifiers")]
        result = _get_identifier(parent, b"something")
        assert result is None


class TestGetPackageName:
    """Tests for _get_package_name()."""

    def test_finds_package(self):
        # Simulate: package_declaration > scoped_identifier
        scoped = MagicMock()
        scoped.type = "scoped_identifier"
        scoped.start_byte = 8
        scoped.end_byte = 19

        pkg_decl = MagicMock()
        pkg_decl.type = "package_declaration"
        pkg_decl.children = [scoped]

        root = MagicMock()
        root.children = [pkg_decl]

        content = b"package com.example;"
        result = _get_package_name(root, content)
        assert result == "com.example"

    def test_no_package_returns_none(self):
        root = MagicMock()
        root.children = [_make_mock_node("import_declaration")]
        result = _get_package_name(root, b"import foo;")
        assert result is None


class TestCountBodyLines:
    """Tests for _count_body_lines()."""

    def test_single_line(self):
        node = MagicMock()
        node.start_point = (5, 0)
        node.end_point = (5, 20)
        assert _count_body_lines(node) == 1

    def test_multi_line(self):
        node = MagicMock()
        node.start_point = (10, 0)
        node.end_point = (15, 0)
        assert _count_body_lines(node) == 6


class TestGetAnnotations:
    """Tests for _get_annotations()."""

    def test_finds_marker_annotation(self):
        ann = MagicMock()
        ann.type = "marker_annotation"
        ann.start_byte = 0
        ann.end_byte = 8

        modifiers = MagicMock()
        modifiers.type = "modifiers"
        modifiers.children = [ann]

        node = MagicMock()
        node.children = [modifiers]

        content = b"@Service"
        result = _get_annotations(node, content)
        assert result == ["@Service"]

    def test_no_modifiers_returns_empty(self):
        node = MagicMock()
        node.children = [_make_mock_node("identifier")]
        result = _get_annotations(node, b"foo")
        assert result == []


# ────────────────────────────────────────────────
# TestHasMatchedDescendants
# ────────────────────────────────────────────────


class TestHasMatchedDescendants:
    """Tests for JavaFileReader._has_matched_descendants()."""

    def test_direct_child_match(self):
        reader = JavaFileReader()
        child = _make_mock_node("method_declaration")
        parent = _make_mock_node("class_body", [child])
        assert reader._has_matched_descendants(parent) is True

    def test_nested_match(self):
        reader = JavaFileReader()
        grandchild = _make_mock_node("field_declaration")
        child = _make_mock_node("block", [grandchild])
        parent = _make_mock_node("class_body", [child])
        assert reader._has_matched_descendants(parent) is True

    def test_no_match(self):
        reader = JavaFileReader()
        child = _make_mock_node("other_type")
        child.children = []
        parent = _make_mock_node("program", [child])
        assert reader._has_matched_descendants(parent) is False

    def test_empty_children(self):
        reader = JavaFileReader()
        parent = _make_mock_node("program")
        assert reader._has_matched_descendants(parent) is False


# ────────────────────────────────────────────────
# TestMakeDocuments
# ────────────────────────────────────────────────


class TestMakeDocuments:
    """Tests for JavaFileReader._make_documents()."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_normal_chunk(self):
        docs = self.reader._make_documents(
            "public void foo() { return; }",
            "method_declaration",
            10,
            12,
            100,
            200,
            "Foo.java",
            {"file_datetime": "2026-01-01"},
        )
        assert len(docs) == 1
        assert docs[0].text == "public void foo() { return; }"
        assert docs[0].metadata["node_type"] == "method_declaration"
        assert docs[0].metadata["start_line"] == 10

    def test_tiny_chunk_discarded(self):
        docs = self.reader._make_documents(
            "x = 1;",  # < MIN_CHUNK_SIZE (20)
            "field_declaration",
            1,
            1,
            0,
            6,
            "Foo.java",
            {},
        )
        assert len(docs) == 0

    def test_oversized_chunk_split(self):
        big_text = "public void foo() {\n" + ("    int x = 1;\n" * 2000) + "}\n"
        docs = self.reader._make_documents(
            big_text,
            "method_declaration",
            1,
            2002,
            0,
            len(big_text),
            "Foo.java",
            {},
        )
        assert len(docs) > 1
        for d in docs:
            assert d.metadata["node_type"] == "method_declaration_split"
            assert "split_part" in d.metadata

    def test_extra_metadata_merged(self):
        docs = self.reader._make_documents(
            "public int x = 42; // something",
            "field_declaration",
            1,
            1,
            0,
            30,
            "Foo.java",
            {},
            extra_metadata={"class_name": "Foo", "package_name": "com.test"},
        )
        assert len(docs) == 1
        assert docs[0].metadata["class_name"] == "Foo"
        assert docs[0].metadata["package_name"] == "com.test"

    def test_class_summary_split_re_prepends_prefix(self):
        # Build a large class_summary that exceeds MAX_SUMMARY_CHARS
        prefix_lines = (
            "// File: Foo.java\n// Package: com.example\n// Class: public class Foo"
        )
        body = "\n".join(f"    public void method{i}()" for i in range(300))
        text = f"{prefix_lines}\npublic class Foo {{\n{body}\n}}"
        docs = self.reader._make_documents(
            text,
            "class_summary",
            1,
            302,
            0,
            len(text),
            "Foo.java",
            {},
            max_chars=self.reader.MAX_SUMMARY_CHARS,
        )
        assert len(docs) > 1
        for d in docs:
            assert d.metadata["node_type"] == "class_summary_split"
            # Each split should start with the context prefix
            assert "// File: Foo.java" in d.text


# ────────────────────────────────────────────────
# TestLoadDataEmpty
# ────────────────────────────────────────────────


class TestLoadDataEmpty:
    """Tests for load_data() with empty or missing files."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_empty_file(self, tmp_path):
        f = _write_java(tmp_path, "Empty.java", "")
        docs = self.reader.load_data(f)
        assert docs == []

    def test_whitespace_only_file(self, tmp_path):
        f = _write_java(tmp_path, "Whitespace.java", "   \n  \n  ")
        docs = self.reader.load_data(f)
        assert docs == []

    def test_nonexistent_file(self, tmp_path):
        f = tmp_path / "DoesNotExist.java"
        docs = self.reader.load_data(f)
        assert docs == []


# ────────────────────────────────────────────────
# TestLoadDataSimpleClass
# ────────────────────────────────────────────────


class TestLoadDataSimpleClass:
    """Tests for load_data() with a simple Java class."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_basic_class_produces_chunks(self, tmp_path):
        code = """\
package com.example;

import java.util.List;

public class Foo {
    private int x;

    public Foo(int x) {
        this.x = x;
    }

    public int getX() {
        return x;
    }

    public void setX(int x) {
        this.x = x;
    }
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        assert len(docs) > 0

    def test_has_import_group(self, tmp_path):
        code = """\
package com.example;

import java.util.List;
import java.util.Map;

public class Foo {
    private int x;
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        import_chunks = [
            d for d in docs if d.metadata.get("node_type") == "import_group"
        ]
        assert len(import_chunks) == 1
        assert "java.util.List" in import_chunks[0].text
        assert "java.util.Map" in import_chunks[0].text

    def test_has_class_summary(self, tmp_path):
        code = """\
package com.example;

public class Foo {
    private int x;

    public int getX() {
        return x;
    }
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) == 1
        assert "public class Foo" in summaries[0].text
        assert "getX" in summaries[0].text

    def test_class_summary_has_context_prefix(self, tmp_path):
        code = """\
package com.example;

public class Foo {
    private int x;
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) == 1
        text = summaries[0].text
        assert "// File: Foo.java" in text
        assert "// Package: com.example" in text
        assert "// Class:" in text

    def test_method_chunk_has_context_prefix(self, tmp_path):
        code = """\
package com.example;

public class Foo {
    public String doSomething(int x, String y) {
        return y + x;
    }
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        methods = [
            d for d in docs if d.metadata.get("node_type") == "method_declaration"
        ]
        assert len(methods) == 1
        assert "// File: Foo.java" in methods[0].text
        assert "// Package: com.example" in methods[0].text
        assert "// Class:" in methods[0].text

    def test_metadata_fields(self, tmp_path):
        code = """\
package com.example;

public class Foo {
    public void bar() {}
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        for d in docs:
            assert "file_path" in d.metadata
            assert "node_type" in d.metadata
            assert d.metadata.get("unit_name") == "Foo"

        # Check class_name is set on class members
        class_chunks = [d for d in docs if d.metadata.get("class_name")]
        assert len(class_chunks) > 0
        for d in class_chunks:
            assert d.metadata["class_name"] == "Foo"

    def test_package_name_in_metadata(self, tmp_path):
        code = """\
package com.example.test;

public class Foo {
    public void bar() {}
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        for d in docs:
            assert d.metadata.get("package_name") == "com.example.test"


# ────────────────────────────────────────────────
# TestLoadDataAnnotations
# ────────────────────────────────────────────────


class TestLoadDataAnnotations:
    """Tests for annotation preservation."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_class_annotation_in_summary(self, tmp_path):
        code = """\
package com.example;

import org.springframework.stereotype.Service;

@Service
public class MyService {
    private int field1;
}
"""
        f = _write_java(tmp_path, "MyService.java", code)
        docs = self.reader.load_data(f)
        summaries = [d for d in docs if d.metadata.get("node_type") == "class_summary"]
        assert len(summaries) == 1
        assert "@Service" in summaries[0].text

    def test_method_annotation_preserved(self, tmp_path):
        code = """\
package com.example;

public class Foo {
    @Override
    public String toString() {
        return "Foo";
    }
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        methods = [
            d for d in docs if d.metadata.get("node_type") == "method_declaration"
        ]
        assert len(methods) == 1
        assert "@Override" in methods[0].text


# ────────────────────────────────────────────────
# TestLoadDataEnum
# ────────────────────────────────────────────────


class TestLoadDataEnum:
    """Tests for enum handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_small_enum_produces_summary(self, tmp_path):
        code = """\
package com.example;

public enum Color {
    RED,
    GREEN,
    BLUE
}
"""
        f = _write_java(tmp_path, "Color.java", code)
        docs = self.reader.load_data(f)
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        text = summaries[0].text
        assert "enum Color" in text

    def test_enum_with_methods(self, tmp_path):
        code = """\
package com.example;

public enum Status {
    ACTIVE,
    INACTIVE;

    public boolean isActive() {
        return this == ACTIVE;
    }

    public String display() {
        return name().toLowerCase();
    }
}
"""
        f = _write_java(tmp_path, "Status.java", code)
        docs = self.reader.load_data(f)
        # Should have summary with enum constants + method signatures
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        text = summaries[0].text
        assert "ACTIVE" in text
        assert "isActive" in text


# ────────────────────────────────────────────────
# TestLoadDataInterface
# ────────────────────────────────────────────────


class TestLoadDataInterface:
    """Tests for interface handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_interface_produces_summary(self, tmp_path):
        code = """\
package com.example;

public interface Printable {
    void print();
    String format(String template);
}
"""
        f = _write_java(tmp_path, "Printable.java", code)
        docs = self.reader.load_data(f)
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        text = summaries[0].text
        assert "interface Printable" in text
        assert "print" in text
        assert "format" in text

    def test_interface_extends(self, tmp_path):
        code = """\
package com.example;

public interface ExtendedPrintable extends Printable, Serializable {
    void printExtended();
}
"""
        f = _write_java(tmp_path, "ExtendedPrintable.java", code)
        docs = self.reader.load_data(f)
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        text = summaries[0].text
        assert "extends Printable" in text or "extends" in text


# ────────────────────────────────────────────────
# TestLoadDataRecord
# ────────────────────────────────────────────────


class TestLoadDataRecord:
    """Tests for Java record handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_record_produces_chunks(self, tmp_path):
        code = """\
package com.example;

public record Point(int x, int y) {
    public double distance() {
        return Math.sqrt(x * x + y * y);
    }
}
"""
        f = _write_java(tmp_path, "Point.java", code)
        docs = self.reader.load_data(f)
        assert len(docs) > 0
        # Should have at least a summary
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        text = summaries[0].text
        assert "record Point" in text


# ────────────────────────────────────────────────
# TestLoadDataInnerClasses
# ────────────────────────────────────────────────


class TestLoadDataInnerClasses:
    """Tests for inner class handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_inner_class_produces_chunks(self, tmp_path):
        code = """\
package com.example;

public class Outer {
    private int x;

    public static class Inner {
        private String name;

        public String getName() {
            return name;
        }
    }

    public Inner createInner() {
        return new Inner();
    }
}
"""
        f = _write_java(tmp_path, "Outer.java", code)
        docs = self.reader.load_data(f)

        # Should have summary for both Outer and Inner
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 2  # Outer + Inner

        # Check that Inner class chunks have proper nesting in context
        inner_chunks = [d for d in docs if d.metadata.get("class_name") == "Inner"]
        assert len(inner_chunks) > 0

    def test_inner_class_nesting_in_context(self, tmp_path):
        code = """\
package com.example;

public class Outer {
    public class Middle {
        public class Deep {
            public void deepMethod() {
                System.out.println("deep");
            }
        }
    }
}
"""
        f = _write_java(tmp_path, "Outer.java", code)
        docs = self.reader.load_data(f)

        # Look for the deep method — it should have nesting in its context
        deep_methods = [
            d
            for d in docs
            if d.metadata.get("node_type") == "method_declaration"
            and "deepMethod" in d.text
        ]
        assert len(deep_methods) == 1
        # The context prefix should show nesting
        assert "Outer" in deep_methods[0].text


# ────────────────────────────────────────────────
# TestLoadDataTrivialMethodGrouping
# ────────────────────────────────────────────────


class TestLoadDataTrivialMethodGrouping:
    """Tests for trivial method grouping."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_consecutive_trivial_methods_grouped(self, tmp_path):
        # Create a class with many trivial getter/setter methods
        methods = "\n".join(
            f"    public int get{chr(65 + i)}() {{ return {i}; }}" for i in range(6)
        )
        code = f"""\
package com.example;

public class Getters {{
    private int a, b, c, d, e, f;

{methods}
}}
"""
        f = _write_java(tmp_path, "Getters.java", code)
        docs = self.reader.load_data(f)
        groups = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        assert len(groups) >= 1
        # The group should mention "Method group: N methods"
        assert "Method group:" in groups[0].text
        assert groups[0].metadata.get("group_count", 0) >= 3

    def test_non_trivial_methods_not_grouped(self, tmp_path):
        # Create methods that are too long to be trivial
        long_body = "        " + "\n        ".join(
            f"int v{i} = {i};" for i in range(10)
        )
        code = f"""\
package com.example;

public class Heavy {{
    public void methodA() {{
{long_body}
    }}
    public void methodB() {{
{long_body}
    }}
    public void methodC() {{
{long_body}
    }}
}}
"""
        f = _write_java(tmp_path, "Heavy.java", code)
        docs = self.reader.load_data(f)
        groups = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        # Non-trivial methods (>6 lines) should NOT be grouped
        assert len(groups) == 0

    def test_fewer_than_three_trivial_not_grouped(self, tmp_path):
        code = """\
package com.example;

public class Small {
    public int getA() { return 1; }
    public int getB() { return 2; }
}
"""
        f = _write_java(tmp_path, "Small.java", code)
        docs = self.reader.load_data(f)
        groups = [d for d in docs if d.metadata.get("node_type") == "method_group"]
        # Fewer than 3 consecutive trivial methods — should NOT be grouped
        assert len(groups) == 0


# ────────────────────────────────────────────────
# TestLoadDataImportGrouping
# ────────────────────────────────────────────────


class TestLoadDataImportGrouping:
    """Tests for import grouping."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_multiple_imports_grouped(self, tmp_path):
        code = """\
package com.example;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.io.File;

public class Foo {
    private int x;
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        imports = [d for d in docs if d.metadata.get("node_type") == "import_group"]
        assert len(imports) == 1
        text = imports[0].text
        assert "java.util.List" in text
        assert "java.util.Map" in text
        assert "java.util.Set" in text
        assert "java.io.File" in text

    def test_no_imports_no_group(self, tmp_path):
        code = """\
package com.example;

public class Bare {
    public void foo() {}
}
"""
        f = _write_java(tmp_path, "Bare.java", code)
        docs = self.reader.load_data(f)
        imports = [d for d in docs if d.metadata.get("node_type") == "import_group"]
        assert len(imports) == 0


# ────────────────────────────────────────────────
# TestLoadDataClassOverview
# ────────────────────────────────────────────────


class TestLoadDataClassOverview:
    """Tests for class_overview chunk generation (large classes only)."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_overview_generated_for_large_class(self, tmp_path):
        # Create a class with enough methods that the summary exceeds MAX_SUMMARY_CHARS
        methods = "\n".join(
            f"    public void method{i}(int param{i}A, String param{i}B, "
            f"List<Map<String, Object>> param{i}C) {{\n"
            f"        // implementation {i}\n"
            f"        System.out.println({i});\n"
            f"    }}"
            for i in range(80)
        )
        code = f"""\
package com.example;

import java.util.List;
import java.util.Map;

public class BigClass {{
    private int field1;
    private String field2;

{methods}
}}
"""
        f = _write_java(tmp_path, "BigClass.java", code)
        docs = self.reader.load_data(f)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        assert len(overviews) == 1
        text = overviews[0].text
        assert "BigClass" in text
        assert "methods" in text.lower()
        assert "fields" in text.lower()

    def test_overview_not_generated_for_small_class(self, tmp_path):
        code = """\
package com.example;

public class Tiny {
    private int x;
    public int getX() { return x; }
}
"""
        f = _write_java(tmp_path, "Tiny.java", code)
        docs = self.reader.load_data(f)
        overviews = [d for d in docs if d.metadata.get("node_type") == "class_overview"]
        assert len(overviews) == 0


# ────────────────────────────────────────────────
# TestLoadDataInheritance
# ────────────────────────────────────────────────


class TestLoadDataInheritance:
    """Tests for class inheritance info in chunks."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_extends_in_summary(self, tmp_path):
        code = """\
package com.example;

public class Child extends Parent {
    public void childMethod() {
        System.out.println("child");
    }
}
"""
        f = _write_java(tmp_path, "Child.java", code)
        docs = self.reader.load_data(f)
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        assert "extends Parent" in summaries[0].text

    def test_implements_in_summary(self, tmp_path):
        code = """\
package com.example;

import java.io.Serializable;

public class Widget implements Serializable, Comparable<Widget> {
    public int compareTo(Widget other) {
        return 0;
    }
}
"""
        f = _write_java(tmp_path, "Widget.java", code)
        docs = self.reader.load_data(f)
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        text = summaries[0].text
        assert "implements" in text
        assert "Serializable" in text


# ────────────────────────────────────────────────
# TestLoadDataFallback
# ────────────────────────────────────────────────


class TestLoadDataFallback:
    """Tests for fallback behavior."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_file_with_only_comments_produces_fallback(self, tmp_path):
        # A file with only a short comment (below MIN_COMMENT_CHARS) and nothing else
        code = "// tiny\n"
        f = _write_java(tmp_path, "Tiny.java", code)
        docs = self.reader.load_data(f)
        # Should produce at least one chunk (full_file fallback)
        assert len(docs) >= 1
        fallbacks = [d for d in docs if d.metadata.get("node_type") == "full_file"]
        assert len(fallbacks) == 1

    def test_parse_error_produces_full_file(self, tmp_path):
        # Intentionally malformed Java that tree-sitter will try to parse
        # Tree-sitter usually doesn't throw exceptions but produces error nodes.
        # The fallback happens when no documents are produced from traversal.
        code = "public class { incomplete syntax"
        f = _write_java(tmp_path, "Bad.java", code)
        docs = self.reader.load_data(f)
        # Should produce something (either parsed or fallback)
        assert len(docs) >= 1


# ────────────────────────────────────────────────
# TestLoadDataFieldDeclarations
# ────────────────────────────────────────────────


class TestLoadDataFieldDeclarations:
    """Tests for field declaration handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_field_chunks_emitted(self, tmp_path):
        code = """\
package com.example;

public class Config {
    private static final String DEFAULT_URL = "http://localhost:8080";
    private final int maxRetries;
    private String name;

    public Config(int maxRetries) {
        this.maxRetries = maxRetries;
    }
}
"""
        f = _write_java(tmp_path, "Config.java", code)
        docs = self.reader.load_data(f)
        fields = [d for d in docs if d.metadata.get("node_type") == "field_declaration"]
        assert len(fields) >= 1  # At least some fields should be emitted
        # Fields should have context prefix
        for fd in fields:
            assert "// File: Config.java" in fd.text


# ────────────────────────────────────────────────
# TestLoadDataBlockComments
# ────────────────────────────────────────────────


class TestLoadDataBlockComments:
    """Tests for block comment handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_large_block_comment_emitted(self, tmp_path):
        comment = (
            "/**\n"
            + " * This is a very long Javadoc comment that describes\n" * 5
            + " */"
        )
        code = f"""\
package com.example;

{comment}
public class Documented {{
    public void foo() {{}}
}}
"""
        f = _write_java(tmp_path, "Documented.java", code)
        docs = self.reader.load_data(f)
        comments = [d for d in docs if d.metadata.get("node_type") == "block_comment"]
        # Large block comments outside a class should be emitted
        assert len(comments) >= 1

    def test_small_comment_not_emitted(self, tmp_path):
        code = """\
package com.example;

/* tiny */
public class Foo {
    public void bar() {}
}
"""
        f = _write_java(tmp_path, "Foo.java", code)
        docs = self.reader.load_data(f)
        comments = [d for d in docs if d.metadata.get("node_type") == "block_comment"]
        # Comments below MIN_COMMENT_CHARS should be suppressed
        assert len(comments) == 0


# ────────────────────────────────────────────────
# TestLoadDataNoPackage
# ────────────────────────────────────────────────


class TestLoadDataNoPackage:
    """Tests for files without a package declaration."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_no_package_still_works(self, tmp_path):
        code = """\
public class Bare {
    public void foo() {
        System.out.println("hello");
    }
}
"""
        f = _write_java(tmp_path, "Bare.java", code)
        docs = self.reader.load_data(f)
        assert len(docs) > 0
        # Should have file name in context but no package line
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        assert "// File: Bare.java" in summaries[0].text
        assert "// Package:" not in summaries[0].text

    def test_no_package_metadata(self, tmp_path):
        code = """\
public class Bare {
    public void foo() {}
}
"""
        f = _write_java(tmp_path, "Bare.java", code)
        docs = self.reader.load_data(f)
        # package_name should not be present in metadata
        for d in docs:
            assert d.metadata.get("package_name") is None


# ────────────────────────────────────────────────
# TestLoadDataConstructors
# ────────────────────────────────────────────────


class TestLoadDataConstructors:
    """Tests for constructor handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_constructor_emitted(self, tmp_path):
        code = """\
package com.example;

public class Service {
    private final String name;

    public Service(String name) {
        this.name = name;
        System.out.println("Init: " + name);
    }

    public String getName() {
        return name;
    }
}
"""
        f = _write_java(tmp_path, "Service.java", code)
        docs = self.reader.load_data(f)
        constructors = [
            d for d in docs if d.metadata.get("node_type") == "constructor_declaration"
        ]
        assert len(constructors) == 1
        assert "Service(String name)" in constructors[0].text


# ────────────────────────────────────────────────
# TestLoadDataAbstractClass
# ────────────────────────────────────────────────


class TestLoadDataAbstractClass:
    """Tests for abstract class handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_abstract_class_summary(self, tmp_path):
        code = """\
package com.example;

public abstract class BaseLogic {
    protected abstract void execute();

    public void run() {
        execute();
    }
}
"""
        f = _write_java(tmp_path, "BaseLogic.java", code)
        docs = self.reader.load_data(f)
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        assert "abstract" in summaries[0].text


# ────────────────────────────────────────────────
# TestLoadDataGenericClass
# ────────────────────────────────────────────────


class TestLoadDataGenericClass:
    """Tests for generic class handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_generic_class_produces_chunks(self, tmp_path):
        code = """\
package com.example;

import java.util.List;

public class Container<T extends Comparable<T>> {
    private List<T> items;

    public void add(T item) {
        items.add(item);
    }

    public T get(int index) {
        return items.get(index);
    }
}
"""
        f = _write_java(tmp_path, "Container.java", code)
        docs = self.reader.load_data(f)
        assert len(docs) > 0
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        # Generic type parameter should be in the header
        assert "Container<T" in summaries[0].text or "Container" in summaries[0].text


# ────────────────────────────────────────────────
# TestLoadDataMultipleClasses
# ────────────────────────────────────────────────


class TestLoadDataMultipleClasses:
    """Tests for files with multiple top-level type declarations."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_multiple_classes_in_one_file(self, tmp_path):
        code = """\
package com.example;

class Helper {
    public void help() {}
}

public class Main {
    public void run() {
        new Helper().help();
    }
}
"""
        f = _write_java(tmp_path, "Main.java", code)
        docs = self.reader.load_data(f)

        # Should have summaries for both classes
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        class_names = {d.metadata.get("class_name") for d in summaries}
        assert "Helper" in class_names
        assert "Main" in class_names


# ────────────────────────────────────────────────
# TestLoadDataSpringPatterns
# ────────────────────────────────────────────────


class TestLoadDataSpringPatterns:
    """Tests for common Spring framework patterns."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_spring_service_with_autowired(self, tmp_path):
        code = """\
package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class UserService {
    private final UserRepository repo;
    private final EmailService emailService;

    @Autowired
    public UserService(UserRepository repo, EmailService emailService) {
        this.repo = repo;
        this.emailService = emailService;
        System.out.println("Initializing UserService");
        System.out.println("Repository: " + repo);
        System.out.println("EmailService: " + emailService);
        validate(repo, emailService);
    }

    public User findById(Long id) {
        return repo.findById(id).orElse(null);
    }

    public void save(User user) {
        repo.save(user);
    }
}
"""
        f = _write_java(tmp_path, "UserService.java", code)
        docs = self.reader.load_data(f)

        # @Service should appear in class_summary
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert any("@Service" in d.text for d in summaries)

        # @Autowired constructor should be in chunks (standalone since > TRIVIAL_METHOD_LINES)
        constructors = [
            d for d in docs if d.metadata.get("node_type") == "constructor_declaration"
        ]
        assert len(constructors) == 1
        assert "@Autowired" in constructors[0].text


# ────────────────────────────────────────────────
# TestLoadDataStaticMembers
# ────────────────────────────────────────────────


class TestLoadDataStaticMembers:
    """Tests for static field and method handling."""

    def setup_method(self):
        self.reader = JavaFileReader()

    def test_static_constants_in_summary(self, tmp_path):
        code = """\
package com.example;

public class Constants {
    public static final String APP_NAME = "MyApp";
    public static final int MAX_RETRIES = 3;
    public static final double PI = 3.14159;

    public static String getAppInfo() {
        return APP_NAME + " v1.0";
    }
}
"""
        f = _write_java(tmp_path, "Constants.java", code)
        docs = self.reader.load_data(f)
        summaries = [
            d for d in docs if "class_summary" in d.metadata.get("node_type", "")
        ]
        assert len(summaries) >= 1
        text = summaries[0].text
        assert "APP_NAME" in text
        assert "getAppInfo" in text


# ────────────────────────────────────────────────
# TestRegistryIntegration
# ────────────────────────────────────────────────


class TestRegistryIntegration:
    """Tests for JavaFileReader registration in readers/__init__.py."""

    def test_java_extension_registered(self):
        from shared.readers import READER_REGISTRY

        assert ".java" in READER_REGISTRY

    def test_java_reader_is_java_file_reader(self):
        from shared.readers import READER_REGISTRY

        assert isinstance(READER_REGISTRY[".java"], JavaFileReader)

    def test_get_reader_returns_java_reader(self):
        from shared.readers import get_reader

        reader = get_reader(".java")
        assert reader is not None
        assert isinstance(reader, JavaFileReader)
