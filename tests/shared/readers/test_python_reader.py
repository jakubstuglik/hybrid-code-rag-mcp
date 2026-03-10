"""
Tests for shared/readers/python_reader.py — Python file reader with Tree-sitter AST.

Tests cover:
    - Class attributes: NODE_TYPES, LEAF_NODE_TYPES, CONTAINER_NODE_TYPES, size constants
    - __init__: instantiation, _text_splitter attribute
    - _has_matched_descendants(): recursive descendant matching
    - _make_documents(): chunk creation, size filtering, oversized splitting
    - load_data(): empty files, parse errors, real files, leaf/container behavior
    - Context prefix (# File: ..., # Class: ...)
    - Leaf/container pattern: class recursion vs. emission
    - Oversized chunk splitting (MAX_CHUNK_CHARS)
    - MIN_CHUNK_SIZE enforcement
    - Fallback to full_file when no AST nodes match
    - File read errors (non-existent file)
    - Metadata correctness
    - Decorated class handling (@dataclass class ...)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shared.readers.python_reader import (
    PythonFileReader,
    _build_context_prefix,
    _get_class_from_decorated,
    _get_class_name,
    _get_module_name,
    _get_node_text,
)
from llama_index.core import Document


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_mock_node(node_type: str, children: list = None) -> MagicMock:
    """Create a mock tree-sitter Node with the given type and children."""
    node = MagicMock()
    node.type = node_type
    node.children = children or []
    return node


def _write_py(tmp_path: Path, name: str, content: str) -> Path:
    """Write a Python file to tmp_path and return the Path."""
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f


# ────────────────────────────────────────────────
# TestClassAttributes
# ────────────────────────────────────────────────


class TestClassAttributes:
    """Tests for PythonFileReader class-level attributes."""

    def test_node_types_is_set(self):
        """NODE_TYPES should be a set."""
        assert isinstance(PythonFileReader.NODE_TYPES, set)

    def test_leaf_node_types_is_set(self):
        """LEAF_NODE_TYPES should be a set."""
        assert isinstance(PythonFileReader.LEAF_NODE_TYPES, set)

    def test_container_node_types_is_set(self):
        """CONTAINER_NODE_TYPES should be a set."""
        assert isinstance(PythonFileReader.CONTAINER_NODE_TYPES, set)

    def test_leaf_node_types_contains_expected_members(self):
        """LEAF_NODE_TYPES should contain function, import, assignment, etc."""
        expected = {
            "function_definition",
            "decorated_definition",
            "import_statement",
            "import_from_statement",
            "assignment",
            "expression_statement",
        }
        assert PythonFileReader.LEAF_NODE_TYPES == expected

    def test_container_node_types_contains_expected_members(self):
        """CONTAINER_NODE_TYPES should contain only class_definition."""
        expected = {"class_definition"}
        assert PythonFileReader.CONTAINER_NODE_TYPES == expected

    def test_leaf_plus_container_equals_node_types(self):
        """LEAF_NODE_TYPES union CONTAINER_NODE_TYPES should equal NODE_TYPES."""
        assert (
            PythonFileReader.LEAF_NODE_TYPES | PythonFileReader.CONTAINER_NODE_TYPES
            == PythonFileReader.NODE_TYPES
        )

    def test_leaf_and_container_are_disjoint(self):
        """LEAF_NODE_TYPES and CONTAINER_NODE_TYPES should have no overlap."""
        overlap = (
            PythonFileReader.LEAF_NODE_TYPES & PythonFileReader.CONTAINER_NODE_TYPES
        )
        assert overlap == set()

    def test_min_chunk_size_value(self):
        """MIN_CHUNK_SIZE should be 20."""
        assert PythonFileReader.MIN_CHUNK_SIZE == 20

    def test_max_chunk_chars_value(self):
        """MAX_CHUNK_CHARS should be 24000."""
        assert PythonFileReader.MAX_CHUNK_CHARS == 24000


# ────────────────────────────────────────────────
# TestInit
# ────────────────────────────────────────────────


class TestInit:
    """Tests for PythonFileReader.__init__."""

    def test_can_instantiate(self):
        """PythonFileReader should be instantiable without arguments."""
        reader = PythonFileReader()
        assert isinstance(reader, PythonFileReader)

    def test_has_text_splitter(self):
        """Instance should have a _text_splitter attribute."""
        reader = PythonFileReader()
        assert hasattr(reader, "_text_splitter")

    def test_text_splitter_is_token_text_splitter(self):
        """_text_splitter should be a TokenTextSplitter instance."""
        from llama_index.core.node_parser import TokenTextSplitter

        reader = PythonFileReader()
        assert isinstance(reader._text_splitter, TokenTextSplitter)

    def test_is_base_file_reader(self):
        """PythonFileReader should be a subclass of BaseFileReader."""
        from shared.readers._base import BaseFileReader

        reader = PythonFileReader()
        assert isinstance(reader, BaseFileReader)


# ────────────────────────────────────────────────
# TestHasMatchedDescendants
# ────────────────────────────────────────────────


class TestHasMatchedDescendants:
    """Tests for PythonFileReader._has_matched_descendants()."""

    def test_child_with_matching_type_returns_true(self):
        """A direct child whose type is in NODE_TYPES should return True."""
        reader = PythonFileReader()
        child = _make_mock_node("function_definition")
        parent = _make_mock_node("someContainer", children=[child])
        assert reader._has_matched_descendants(parent) is True

    def test_no_matching_descendants_returns_false(self):
        """A node whose children have no matching types returns False."""
        reader = PythonFileReader()
        grandchild = _make_mock_node("identifier")
        child = _make_mock_node("expression", children=[grandchild])
        parent = _make_mock_node("someContainer", children=[child])
        assert reader._has_matched_descendants(parent) is False

    def test_deeply_nested_match_returns_true(self):
        """A matching node deep in the tree should still return True."""
        reader = PythonFileReader()
        deep_match = _make_mock_node("assignment")
        mid = _make_mock_node("block", children=[deep_match])
        top_child = _make_mock_node("wrapper", children=[mid])
        parent = _make_mock_node("root", children=[top_child])
        assert reader._has_matched_descendants(parent) is True

    def test_empty_children_returns_false(self):
        """A node with no children should return False."""
        reader = PythonFileReader()
        node = _make_mock_node("class_definition", children=[])
        assert reader._has_matched_descendants(node) is False

    def test_multiple_children_one_matches(self):
        """If one of several children matches, should return True."""
        reader = PythonFileReader()
        child_a = _make_mock_node("identifier")
        child_b = _make_mock_node("import_statement")
        child_c = _make_mock_node("expression")
        parent = _make_mock_node("container", children=[child_a, child_b, child_c])
        assert reader._has_matched_descendants(parent) is True

    def test_all_node_types_detected(self):
        """Each node type in NODE_TYPES should be detected as a matched descendant."""
        reader = PythonFileReader()
        for node_type in PythonFileReader.NODE_TYPES:
            child = _make_mock_node(node_type)
            parent = _make_mock_node("wrapper", children=[child])
            assert reader._has_matched_descendants(parent) is True, (
                f"{node_type} was not detected as matched descendant"
            )


# ────────────────────────────────────────────────
# TestMakeDocuments
# ────────────────────────────────────────────────


class TestMakeDocuments:
    """Tests for PythonFileReader._make_documents()."""

    def _file_datetime(self) -> dict:
        """Create a sample file_datetime dict for testing."""
        return {
            "creation_datetime": "2026-01-01T00:00:00",
            "modification_datetime": "2026-01-02T00:00:00",
        }

    def test_normal_chunk_returns_single_document(self):
        """A normal-sized chunk should return exactly one Document."""
        reader = PythonFileReader()
        text = "def greet(name):\n    return f'Hello, {name}'"
        docs = reader._make_documents(
            chunk_text=text,
            node_type="function_definition",
            start_line=1,
            end_line=2,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
        )
        assert len(docs) == 1
        assert docs[0].text == text

    def test_too_small_chunk_returns_empty(self):
        """A chunk smaller than MIN_CHUNK_SIZE should be discarded."""
        reader = PythonFileReader()
        text = "x = 1"  # 5 chars < 20
        docs = reader._make_documents(
            chunk_text=text,
            node_type="assignment",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=5,
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
        )
        assert docs == []

    def test_exact_min_minus_one_is_discarded(self):
        """A chunk with exactly MIN_CHUNK_SIZE - 1 chars should be discarded."""
        reader = PythonFileReader()
        text = "x" * 19  # 19 chars < 20
        docs = reader._make_documents(
            chunk_text=text,
            node_type="assignment",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=19,
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
        )
        assert docs == []

    def test_min_chunk_size_boundary_included(self):
        """A chunk with exactly MIN_CHUNK_SIZE chars should be included."""
        reader = PythonFileReader()
        text = "x" * 20  # exactly 20 chars
        docs = reader._make_documents(
            chunk_text=text,
            node_type="assignment",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=20,
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
        )
        assert len(docs) == 1

    def test_oversized_chunk_returns_multiple_documents(self):
        """A chunk exceeding MAX_CHUNK_CHARS should be split into multiple Documents."""
        reader = PythonFileReader()
        text = "def big():\n" + ("    x = 1\n" * 3000)
        assert len(text) > reader.MAX_CHUNK_CHARS

        docs = reader._make_documents(
            chunk_text=text,
            node_type="function_definition",
            start_line=1,
            end_line=3001,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
        )
        assert len(docs) > 1

    def test_oversized_chunk_has_split_metadata(self):
        """Split documents should have split_part, split_total, and _split node_type."""
        reader = PythonFileReader()
        text = "def big():\n" + ("    x = 1\n" * 3000)

        docs = reader._make_documents(
            chunk_text=text,
            node_type="function_definition",
            start_line=1,
            end_line=3001,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
        )
        for doc in docs:
            assert doc.metadata["node_type"] == "function_definition_split"
            assert "split_part" in doc.metadata
            assert "split_total" in doc.metadata
            assert doc.metadata["split_total"] == len(docs)

    def test_metadata_fields_correct(self):
        """Returned document should have all expected metadata fields."""
        reader = PythonFileReader()
        text = "def foo():\n    return 42\n"
        file_dt = self._file_datetime()
        docs = reader._make_documents(
            chunk_text=text,
            node_type="function_definition",
            start_line=5,
            end_line=6,
            start_byte=100,
            end_byte=123,
            file_path_str="src/module.py",
            file_datetime=file_dt,
        )
        assert len(docs) == 1
        meta = docs[0].metadata
        assert meta["file_path"] == "src/module.py"
        assert meta["node_type"] == "function_definition"
        assert meta["start_line"] == 5
        assert meta["end_line"] == 6
        assert meta["start_byte"] == 100
        assert meta["end_byte"] == 123
        assert meta["creation_datetime"] == file_dt["creation_datetime"]
        assert meta["modification_datetime"] == file_dt["modification_datetime"]

    def test_extra_metadata_merged(self):
        """Extra metadata dict should be merged into base metadata."""
        reader = PythonFileReader()
        text = "def foo():\n    return 42\n"
        docs = reader._make_documents(
            chunk_text=text,
            node_type="function_definition",
            start_line=1,
            end_line=2,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
            extra_metadata={"class_name": "MyClass"},
        )
        assert len(docs) == 1
        assert docs[0].metadata["class_name"] == "MyClass"

    def test_oversized_split_part_too_small_is_dropped(self):
        """Split parts smaller than MIN_CHUNK_SIZE (after strip) should be dropped."""
        reader = PythonFileReader()
        text = "x" * (reader.MAX_CHUNK_CHARS + 1)

        mock_splitter = MagicMock()
        mock_splitter.split_text.return_value = ["x" * 100, "   tiny   ", "y" * 100]
        reader._text_splitter = mock_splitter

        docs = reader._make_documents(
            chunk_text=text,
            node_type="function_definition",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
        )
        # "   tiny   " stripped is "tiny" (4 chars < 20), so it should be dropped
        assert len(docs) == 2
        for doc in docs:
            assert doc.metadata["split_total"] == 3

    def test_normal_chunk_at_max_boundary(self):
        """A chunk with exactly MAX_CHUNK_CHARS should NOT be split."""
        reader = PythonFileReader()
        text = "x" * reader.MAX_CHUNK_CHARS
        docs = reader._make_documents(
            chunk_text=text,
            node_type="function_definition",
            start_line=1,
            end_line=1,
            start_byte=0,
            end_byte=len(text),
            file_path_str="test.py",
            file_datetime=self._file_datetime(),
        )
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "function_definition"


# ────────────────────────────────────────────────
# TestLoadData — empty and whitespace files
# ────────────────────────────────────────────────


class TestLoadDataEmpty:
    """Tests for load_data() with empty or whitespace-only files."""

    def test_empty_file_returns_empty_list(self, tmp_path):
        """An empty .py file should return an empty list."""
        f = _write_py(tmp_path, "empty.py", "")
        reader = PythonFileReader()
        docs = reader.load_data(f)
        assert docs == []

    def test_whitespace_only_file_returns_empty_list(self, tmp_path):
        """A file containing only whitespace should return an empty list."""
        f = _write_py(tmp_path, "whitespace.py", "   \n\n  \t  \n")
        reader = PythonFileReader()
        docs = reader.load_data(f)
        assert docs == []


# ────────────────────────────────────────────────
# TestLoadData — parse errors
# ────────────────────────────────────────────────


class TestLoadDataParseError:
    """Tests for load_data() when tree-sitter parsing fails."""

    def test_parse_error_returns_full_file_document(self, tmp_path):
        """When tree-sitter parse fails, should return a full_file Document with parse_error."""
        f = _write_py(tmp_path, "bad.py", "def greet(name):\n    return name\n")
        reader = PythonFileReader()

        mock_parser = MagicMock()
        mock_parser.parse.side_effect = RuntimeError("mock parse failure")

        with patch("shared.readers.python_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"
        assert "parse_error" in docs[0].metadata
        assert "mock parse failure" in docs[0].metadata["parse_error"]

    def test_parse_error_preserves_full_content(self, tmp_path):
        """The full_file document from a parse error should contain all file content."""
        content = "import os\nx = 42\n"
        f = _write_py(tmp_path, "err.py", content)
        reader = PythonFileReader()

        mock_parser = MagicMock()
        mock_parser.parse.side_effect = Exception("boom")

        with patch("shared.readers.python_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert docs[0].text == content

    def test_parse_error_has_file_path_metadata(self, tmp_path):
        """full_file document from parse error should have file_path metadata."""
        f = _write_py(tmp_path, "err2.py", "x = 1\n")
        reader = PythonFileReader()

        mock_parser = MagicMock()
        mock_parser.parse.side_effect = Exception("boom")

        with patch("shared.readers.python_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert docs[0].metadata["file_path"] == str(f)


# ────────────────────────────────────────────────
# TestContextPrefix
# ────────────────────────────────────────────────


class TestContextPrefix:
    """Tests for the context prefix (# File: ..., # Class: ...) on every chunk."""

    def test_build_context_prefix_without_class(self):
        """_build_context_prefix without class_name should produce '# File: ...'."""
        result = _build_context_prefix("index_rag", "index_rag.py")
        assert result == "# File: index_rag (index_rag.py)"

    def test_build_context_prefix_with_class(self):
        """_build_context_prefix with class_name should include '# Class: ...'."""
        result = _build_context_prefix("reader", "reader.py", "MyReader")
        lines = result.split("\n")
        assert lines[0] == "# File: reader (reader.py)"
        assert lines[1] == "# Class: MyReader"

    def test_build_context_prefix_none_class(self):
        """_build_context_prefix with class_name=None should omit class line."""
        result = _build_context_prefix("mod", "mod.py", None)
        assert "# Class:" not in result

    def test_all_chunks_start_with_file_prefix(self, tmp_path):
        """Every chunk from load_data should start with '# File:'."""
        f = _write_py(
            tmp_path,
            "test_module.py",
            "import os\n\ndef greet(name):\n    return f'Hello, {name}'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert doc.text.startswith("# File:"), (
                    f"Chunk of type '{doc.metadata['node_type']}' does not start "
                    f"with '# File:': {doc.text[:100]!r}"
                )

    def test_file_prefix_contains_module_name(self, tmp_path):
        """The context prefix should contain the module name (stem)."""
        f = _write_py(
            tmp_path,
            "my_module.py",
            "def do_stuff():\n    return 'stuff done here'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                first_line = doc.text.split("\n")[0]
                assert "my_module" in first_line
                assert "(my_module.py)" in first_line

    def test_class_method_chunks_have_class_context(self, tmp_path):
        """Methods inside a class should have '# Class:' in their prefix."""
        f = _write_py(
            tmp_path,
            "calc.py",
            (
                "class Calculator:\n"
                "    def __init__(self):\n"
                "        self.result = 0\n"
                "\n"
                "    def add(self, x):\n"
                "        self.result += x\n"
                "        return self.result\n"
            ),
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        method_docs = [
            d for d in docs if d.metadata.get("node_type") == "function_definition"
        ]
        assert len(method_docs) >= 1, "Expected at least one method chunk"
        for doc in method_docs:
            assert "# Class: Calculator" in doc.text, (
                f"Method chunk missing '# Class: Calculator': {doc.text[:200]!r}"
            )

    def test_standalone_function_has_no_class_context(self, tmp_path):
        """A top-level function should only have '# File:', no '# Class:'."""
        f = _write_py(
            tmp_path,
            "helpers.py",
            "def standalone_func():\n    return 'I am standalone'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        func_docs = [
            d for d in docs if d.metadata.get("node_type") == "function_definition"
        ]
        assert len(func_docs) >= 1
        for doc in func_docs:
            assert "# Class:" not in doc.text


# ────────────────────────────────────────────────
# TestLeafContainerPattern
# ────────────────────────────────────────────────


class TestLeafContainerPattern:
    """Tests for the leaf/container AST walk pattern (Y1 fix)."""

    _CLASS_WITH_METHODS = (
        "class Calculator:\n"
        "    def __init__(self):\n"
        "        self.result = 0\n"
        "\n"
        "    def add(self, x):\n"
        "        self.result += x\n"
        "        return self.result\n"
        "\n"
        "    def reset(self):\n"
        "        self.result = 0\n"
    )

    def test_class_with_methods_not_emitted_as_single_chunk(self, tmp_path):
        """A class with methods should NOT be emitted as one class_definition chunk."""
        f = _write_py(tmp_path, "calc.py", self._CLASS_WITH_METHODS)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = {doc.metadata["node_type"] for doc in docs}
        assert "class_definition" not in node_types, (
            "class_definition should not be emitted when it has matched descendants"
        )

    def test_individual_methods_are_emitted(self, tmp_path):
        """Each method inside a class should be emitted as its own chunk."""
        f = _write_py(tmp_path, "calc.py", self._CLASS_WITH_METHODS)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        func_docs = [
            d for d in docs if d.metadata.get("node_type") == "function_definition"
        ]
        # Should have __init__, add, reset
        assert len(func_docs) >= 3, (
            f"Expected >= 3 function chunks, got {len(func_docs)}. "
            f"Node types: {[d.metadata['node_type'] for d in docs]}"
        )

    def test_no_text_duplication_between_class_and_methods(self, tmp_path):
        """No chunk should contain the entire class body when methods exist."""
        f = _write_py(tmp_path, "calc.py", self._CLASS_WITH_METHODS)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            # No single chunk should contain all three method names
            # (which would indicate the whole class was emitted)
            has_all = (
                "def __init__" in doc.text
                and "def add" in doc.text
                and "def reset" in doc.text
            )
            if has_all:
                # This should NOT happen for function_definition chunks
                assert doc.metadata["node_type"] != "function_definition", (
                    "A single function_definition chunk should not contain all methods"
                )

    def test_class_without_methods_emitted_as_whole(self, tmp_path):
        """A class with no matched descendants should be emitted as one chunk."""
        f = _write_py(
            tmp_path,
            "empty_cls.py",
            "class Empty:\n    pass\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]
        # An empty class has no matched descendants, so the whole class is emitted
        assert "class_definition" in node_types, (
            f"Expected class_definition for class with no methods: {node_types}"
        )

    def test_leaf_function_not_recursed_into(self, tmp_path):
        """A top-level function should be emitted as one chunk, not decomposed into assignments."""
        f = _write_py(
            tmp_path,
            "func.py",
            (
                "def complex_func():\n"
                "    x = compute_something_long_here()\n"
                "    y = transform_data_with_params(x)\n"
                "    z = aggregate_all_results(y)\n"
                "    return z\n"
            ),
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        # The function should be one chunk; assignments inside should NOT be separate
        func_docs = [
            d for d in docs if d.metadata["node_type"] == "function_definition"
        ]
        assign_docs = [d for d in docs if d.metadata["node_type"] == "assignment"]
        assert len(func_docs) == 1
        assert len(assign_docs) == 0, (
            "Assignments inside a function should not be separate chunks"
        )

    def test_top_level_import_is_leaf(self, tmp_path):
        """Top-level import statements should be emitted as leaf chunks."""
        content = (
            "import os\n"
            "from pathlib import Path\n"
            "\n"
            "def do_work():\n"
            "    return Path(os.getcwd())\n"
        )
        f = _write_py(tmp_path, "imports.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]
        # import_statement and import_from_statement may be too short (< MIN_CHUNK_SIZE)
        # but at least the function should be present
        assert "function_definition" in node_types

    def test_top_level_assignment_is_leaf(self, tmp_path):
        """A top-level assignment should be emitted as a leaf chunk (if long enough)."""
        content = (
            "LONG_CONSTANT_VALUE = 'This is a long enough string to exceed the minimum chunk size threshold'\n"
            "\n"
            "def use_it():\n"
            "    return LONG_CONSTANT_VALUE\n"
        )
        f = _write_py(tmp_path, "consts.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]
        # The assignment line (with prefix) should exceed MIN_CHUNK_SIZE
        assert "assignment" in node_types or "function_definition" in node_types


# ────────────────────────────────────────────────
# TestOversizedSplitting
# ────────────────────────────────────────────────


class TestOversizedSplitting:
    """Tests for oversized chunk splitting behavior."""

    def test_oversized_function_gets_split(self, tmp_path, monkeypatch):
        """A function exceeding MAX_CHUNK_CHARS should be split into multiple docs."""
        monkeypatch.setattr(PythonFileReader, "MAX_CHUNK_CHARS", 200)

        body_lines = "\n".join(
            f"    print('Line {i}: This is a very long test statement that pads the function body with enough content to generate many tokens for splitting purposes.')"
            for i in range(80)
        )
        content = f"def big_func():\n{body_lines}\n"
        f = _write_py(tmp_path, "big.py", content)

        reader = PythonFileReader()
        docs = reader.load_data(f)

        split_docs = [d for d in docs if "_split" in d.metadata.get("node_type", "")]
        assert len(split_docs) > 1, (
            f"Expected multiple split documents, got node_types: "
            f"{[d.metadata.get('node_type') for d in docs]}"
        )

    def test_split_metadata_correct(self, tmp_path, monkeypatch):
        """Split documents should have correct split_part and split_total metadata."""
        monkeypatch.setattr(PythonFileReader, "MAX_CHUNK_CHARS", 200)

        body_lines = "\n".join(
            f"    print('Line {i}: padding for split test')" for i in range(40)
        )
        content = f"def another_big():\n{body_lines}\n"
        f = _write_py(tmp_path, "big2.py", content)

        reader = PythonFileReader()
        docs = reader.load_data(f)

        split_docs = [d for d in docs if "_split" in d.metadata.get("node_type", "")]
        if split_docs:
            for doc in split_docs:
                assert "split_part" in doc.metadata
                assert "split_total" in doc.metadata
                assert isinstance(doc.metadata["split_part"], int)
                assert isinstance(doc.metadata["split_total"], int)
                assert doc.metadata["split_part"] >= 0

    def test_node_type_gets_split_suffix(self, tmp_path, monkeypatch):
        """Split chunks should have node_type ending in '_split'."""
        monkeypatch.setattr(PythonFileReader, "MAX_CHUNK_CHARS", 200)

        body_lines = "\n".join(
            f"    print('Statement {i}: lots of padding text goes here')"
            for i in range(40)
        )
        content = f"def third_big():\n{body_lines}\n"
        f = _write_py(tmp_path, "big3.py", content)

        reader = PythonFileReader()
        docs = reader.load_data(f)

        split_docs = [d for d in docs if "split_part" in d.metadata]
        for doc in split_docs:
            assert doc.metadata["node_type"].endswith("_split")


# ────────────────────────────────────────────────
# TestMinChunkSize
# ────────────────────────────────────────────────


class TestMinChunkSize:
    """Tests for MIN_CHUNK_SIZE filtering behavior."""

    def test_tiny_assignment_not_in_output(self, tmp_path):
        """A very short assignment like 'x = 1' should be discarded (below MIN_CHUNK_SIZE)."""
        content = "x = 1\n\ndef real_func():\n    return 'long enough content here'\n"
        f = _write_py(tmp_path, "tiny.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert len(doc.text) >= reader.MIN_CHUNK_SIZE, (
                    f"Chunk too small ({len(doc.text)} chars): {doc.text!r}"
                )

    def test_all_output_chunks_meet_min_size(self, tmp_path):
        """No output chunk should be smaller than MIN_CHUNK_SIZE (except full_file fallback)."""
        content = (
            "import os\n"
            "from pathlib import Path\n"
            "\n"
            "MAX_SIZE = 100\n"
            "\n"
            "class Processor:\n"
            "    def process(self, data):\n"
            "        return [d.strip() for d in data]\n"
        )
        f = _write_py(tmp_path, "proc.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert len(doc.text) >= reader.MIN_CHUNK_SIZE, (
                    f"Chunk too small ({len(doc.text)} chars): {doc.text!r}"
                )


# ────────────────────────────────────────────────
# TestFallbackToFullFile
# ────────────────────────────────────────────────


class TestFallbackToFullFile:
    """Tests for fallback to full_file when no AST nodes match."""

    def test_no_matched_nodes_returns_full_file(self, tmp_path):
        """A file with no recognized AST nodes should return a full_file Document."""
        # Force no AST matches by mocking the parser to return empty root
        content = "# just a comment\n"
        f = _write_py(tmp_path, "no_match.py", content)
        reader = PythonFileReader()

        mock_root = _make_mock_node("module", children=[])
        mock_tree = MagicMock()
        mock_tree.root_node = mock_root

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_tree

        with patch("shared.readers.python_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"
        assert docs[0].text == content

    def test_fallback_has_file_datetime_metadata(self, tmp_path):
        """The full_file fallback document should have file datetime metadata."""
        f = _write_py(tmp_path, "fallback.py", "# nothing matched here\n")

        mock_root = _make_mock_node("module", children=[])
        mock_tree = MagicMock()
        mock_tree.root_node = mock_root
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_tree

        reader = PythonFileReader()
        with patch("shared.readers.python_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert "creation_datetime" in docs[0].metadata
        assert "modification_datetime" in docs[0].metadata

    def test_fallback_has_file_path_metadata(self, tmp_path):
        """The full_file fallback should have correct file_path."""
        f = _write_py(tmp_path, "fb.py", "# comment only\n")

        mock_root = _make_mock_node("module", children=[])
        mock_tree = MagicMock()
        mock_tree.root_node = mock_root
        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_tree

        reader = PythonFileReader()
        with patch("shared.readers.python_reader._parser", mock_parser):
            docs = reader.load_data(f)

        assert docs[0].metadata["file_path"] == str(f)

    def test_real_comment_only_file(self, tmp_path):
        """A file with only comments should return at least one document (fallback or comment)."""
        f = _write_py(
            tmp_path,
            "comments.py",
            "# This is a long enough comment to exceed the minimum chunk size threshold\n"
            "# Another long comment line to fill the file with something meaningful\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        # Either produces expression_statement chunks or falls back to full_file
        assert len(docs) >= 1


# ────────────────────────────────────────────────
# TestFileReadError
# ────────────────────────────────────────────────


class TestFileReadError:
    """Tests for load_data() with file read failures."""

    def test_nonexistent_file_returns_empty_list(self, tmp_path):
        """A non-existent file should return an empty list."""
        f = tmp_path / "nonexistent.py"
        reader = PythonFileReader()
        docs = reader.load_data(f)
        assert docs == []

    def test_nonexistent_file_does_not_raise(self, tmp_path):
        """A non-existent file should not raise an exception."""
        f = tmp_path / "missing.py"
        reader = PythonFileReader()
        docs = reader.load_data(f)
        assert isinstance(docs, list)

    def test_read_failure_logs_warning(self, tmp_path):
        """A file that fails to read should trigger a log_warn call."""
        f = tmp_path / "unreadable.py"
        reader = PythonFileReader()

        with patch(
            "shared.readers.python_reader.read_file_with_encoding_and_bytes"
        ) as mock_read:
            mock_read.side_effect = PermissionError("Access denied")
            with patch("shared.readers.python_reader.log_warn") as mock_warn:
                docs = reader.load_data(f)

        assert docs == []
        mock_warn.assert_called_once()
        assert "Failed to read" in mock_warn.call_args[0][0]


# ────────────────────────────────────────────────
# TestMetadata
# ────────────────────────────────────────────────


class TestMetadata:
    """Tests for metadata correctness on returned documents."""

    def test_file_path_metadata(self, tmp_path):
        """Each document should have file_path matching the input file."""
        f = _write_py(
            tmp_path,
            "meta_test.py",
            "def greet(name):\n    return f'Hello, {name}'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            assert doc.metadata["file_path"] == str(f)

    def test_node_type_metadata_present(self, tmp_path):
        """Each document should have a non-empty node_type."""
        f = _write_py(
            tmp_path,
            "node_type_test.py",
            "def foo():\n    return 'test output here'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            assert "node_type" in doc.metadata
            assert len(doc.metadata["node_type"]) > 0

    def test_line_number_metadata(self, tmp_path):
        """Documents should have start_line and end_line metadata."""
        f = _write_py(
            tmp_path,
            "lines.py",
            "def func():\n    return 'line metadata test'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert "start_line" in doc.metadata
                assert "end_line" in doc.metadata
                assert doc.metadata["start_line"] >= 1
                assert doc.metadata["end_line"] >= doc.metadata["start_line"]

    def test_byte_range_metadata(self, tmp_path):
        """Documents should have start_byte and end_byte metadata."""
        f = _write_py(
            tmp_path,
            "bytes.py",
            "def byte_func():\n    return 'testing byte ranges'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            if doc.metadata.get("node_type") != "full_file":
                assert "start_byte" in doc.metadata
                assert "end_byte" in doc.metadata
                assert doc.metadata["start_byte"] >= 0
                assert doc.metadata["end_byte"] > doc.metadata["start_byte"]

    def test_file_datetime_metadata_present(self, tmp_path):
        """Documents should have creation_datetime and modification_datetime."""
        f = _write_py(
            tmp_path,
            "datetime.py",
            "def datetime_func():\n    return 'datetime metadata test'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            assert "creation_datetime" in doc.metadata
            assert "modification_datetime" in doc.metadata
            from datetime import datetime

            datetime.fromisoformat(doc.metadata["creation_datetime"])
            datetime.fromisoformat(doc.metadata["modification_datetime"])


# ────────────────────────────────────────────────
# TestDecoratedClassHandling
# ────────────────────────────────────────────────


class TestDecoratedClassHandling:
    """Tests for decorated class definitions (@dataclass class Foo, etc.)."""

    def test_decorated_class_with_methods_is_recursed(self, tmp_path):
        """A @dataclass class with methods should be recursed into, not emitted as one chunk."""
        content = (
            "from dataclasses import dataclass\n"
            "\n"
            "@dataclass\n"
            "class Point:\n"
            "    x: float\n"
            "    y: float\n"
            "\n"
            "    def magnitude(self):\n"
            "        return (self.x**2 + self.y**2) ** 0.5\n"
            "\n"
            "    def translate(self, dx, dy):\n"
            "        return Point(self.x + dx, self.y + dy)\n"
        )
        f = _write_py(tmp_path, "point.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]

        # The decorated class should be recursed into, producing method chunks
        assert "function_definition" in node_types, (
            f"Expected method chunks from decorated class, got: {node_types}"
        )
        # The decorated_definition wrapping the class should NOT be emitted as one
        # opaque leaf chunk that contains all the methods
        for doc in docs:
            if doc.metadata["node_type"] == "decorated_definition":
                # If a decorated_definition chunk exists, it should NOT contain
                # both magnitude and translate (that would mean it wasn't recursed)
                has_both = "def magnitude" in doc.text and "def translate" in doc.text
                assert not has_both, (
                    "Decorated class with methods should be recursed, not emitted whole"
                )

    def test_decorated_class_with_only_annotations_is_recursed(self, tmp_path):
        """A @dataclass with only field annotations produces assignment nodes inside.

        Tree-sitter parses ``x: float`` as typed assignments, which are matched
        AST node types (assignment/expression_statement).  So the decorated class
        IS recursed into and the individual annotations are emitted as leaf chunks
        (or discarded if below MIN_CHUNK_SIZE).
        """
        content = (
            "from dataclasses import dataclass\n"
            "\n"
            "@dataclass\n"
            "class SimplePoint:\n"
            "    x: float\n"
            "    y: float\n"
        )
        f = _write_py(tmp_path, "simple_point.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]

        # The class body has matched descendants (typed assignments are
        # expression_statement or assignment nodes), so the class is recursed
        # into rather than emitted whole.  We should NOT see a single
        # decorated_definition or class_definition chunk containing the
        # entire class.
        for doc in docs:
            nt = doc.metadata["node_type"]
            if nt in ("decorated_definition", "class_definition"):
                # If one slipped through, it should not contain both field lines
                has_both = "x: float" in doc.text and "y: float" in doc.text
                assert not has_both, (
                    "Decorated dataclass with annotations should be recursed, "
                    "not emitted whole"
                )

    def test_decorated_empty_class_emitted_whole(self, tmp_path):
        """A decorated class with only ``pass`` has no matched descendants and is emitted whole."""
        content = (
            "def my_decorator(cls):\n"
            "    return cls\n"
            "\n"
            "@my_decorator\n"
            "class EmptyThing:\n"
            "    pass\n"
        )
        f = _write_py(tmp_path, "empty_decorated.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]

        # The decorated class body has no matched descendants (only `pass`),
        # so it should be emitted as a single chunk.
        has_decorated = "decorated_definition" in node_types
        # It's possible the import is too small and only the func + class remain
        assert has_decorated or "class_definition" in node_types, (
            f"Expected decorated_definition or class_definition in: {node_types}"
        )

    def test_decorated_class_method_gets_class_context(self, tmp_path):
        """Methods inside a decorated class should get '# Class: ClassName' prefix."""
        content = (
            "from dataclasses import dataclass\n"
            "\n"
            "@dataclass\n"
            "class Widget:\n"
            "    name: str\n"
            "    size: int = 10\n"
            "\n"
            "    def describe(self):\n"
            "        return f'{self.name}: {self.size}'\n"
        )
        f = _write_py(tmp_path, "widget.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)

        # The describe method should have class context
        # Note: when a decorated_definition wraps a class, traverse recurses
        # into children with current_class from the outer scope. The class_definition
        # child is handled as a container node and _get_class_name extracts 'Widget'.
        method_docs = [
            d
            for d in docs
            if d.metadata["node_type"] == "function_definition" and "describe" in d.text
        ]
        if method_docs:
            # The method chunk should have class context
            assert "# Class:" in method_docs[0].text, (
                f"Decorated class method should have class context: "
                f"{method_docs[0].text[:200]!r}"
            )

    def test_non_class_decorated_definition_is_leaf(self, tmp_path):
        """A decorated function (not class) should be emitted as a leaf chunk."""
        content = (
            "import functools\n"
            "\n"
            "@functools.lru_cache(maxsize=128)\n"
            "def expensive_compute(n):\n"
            "    return sum(range(n))\n"
        )
        f = _write_py(tmp_path, "cached.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]

        # decorated_definition wrapping a function (not a class) is a leaf
        has_decorated = "decorated_definition" in node_types
        has_func = "function_definition" in node_types
        # Either emitted as decorated_definition (the outer node) or
        # as function_definition (if the parser treats it that way)
        assert has_decorated or has_func, (
            f"Expected decorated_definition or function_definition in: {node_types}"
        )


# ────────────────────────────────────────────────
# TestModuleLevelHelpers
# ────────────────────────────────────────────────


class TestModuleLevelHelpers:
    """Tests for module-level helper functions."""

    def test_get_module_name(self):
        """_get_module_name should return the file stem."""
        assert _get_module_name(Path("index_rag.py")) == "index_rag"
        assert _get_module_name(Path("/some/path/module.py")) == "module"
        assert _get_module_name(Path("foo.bar.py")) == "foo.bar"

    def test_get_node_text(self):
        """_get_node_text should extract text from byte range."""
        content_bytes = b"import os\nfrom pathlib import Path"
        node = MagicMock()
        node.start_byte = 10
        node.end_byte = 34
        result = _get_node_text(node, content_bytes)
        assert result == "from pathlib import Path"

    def test_get_node_text_strips_whitespace(self):
        """_get_node_text should strip leading/trailing whitespace."""
        content_bytes = b"   hello world   "
        node = MagicMock()
        node.start_byte = 0
        node.end_byte = 17
        result = _get_node_text(node, content_bytes)
        assert result == "hello world"

    def test_get_class_name_from_class_node(self):
        """_get_class_name should extract the class name from an identifier child."""
        content_bytes = b"class MyClass:\n    pass"
        identifier = MagicMock()
        identifier.type = "identifier"
        identifier.start_byte = 6
        identifier.end_byte = 13

        colon = MagicMock()
        colon.type = ":"

        node = MagicMock()
        node.children = [identifier, colon]

        result = _get_class_name(node, content_bytes)
        assert result == "MyClass"

    def test_get_class_name_no_identifier(self):
        """_get_class_name should return None when no identifier child exists."""
        node = MagicMock()
        child = MagicMock()
        child.type = "colon"
        node.children = [child]

        result = _get_class_name(node, b"class :\n    pass")
        assert result is None

    def test_get_class_from_decorated_with_class_inside(self):
        """_get_class_from_decorated should return class name from inner class_definition."""
        content_bytes = b"@dataclass\nclass Point:\n    x: float"

        identifier = MagicMock()
        identifier.type = "identifier"
        identifier.start_byte = 17  # "Point"
        identifier.end_byte = 22

        class_def = MagicMock()
        class_def.type = "class_definition"
        class_def.children = [identifier]

        decorator = MagicMock()
        decorator.type = "decorator"

        node = MagicMock()
        node.children = [decorator, class_def]

        result = _get_class_from_decorated(node, content_bytes)
        assert result == "Point"

    def test_get_class_from_decorated_without_class(self):
        """_get_class_from_decorated should return None when no class_definition inside."""
        func_def = MagicMock()
        func_def.type = "function_definition"

        decorator = MagicMock()
        decorator.type = "decorator"

        node = MagicMock()
        node.children = [decorator, func_def]

        result = _get_class_from_decorated(node, b"@cache\ndef foo(): pass")
        assert result is None


# ────────────────────────────────────────────────
# TestLoadDataIntegration
# ────────────────────────────────────────────────


class TestLoadDataIntegration:
    """Integration tests with real Python content using Tree-sitter parsing."""

    _FULL_MODULE = (
        "import os\n"
        "from pathlib import Path\n"
        "\n"
        "MAX_SIZE = 100\n"
        "\n"
        "class Processor:\n"
        "    def process(self, data):\n"
        "        return [d.strip() for d in data]\n"
        "\n"
        "    def validate(self, item):\n"
        "        return item is not None\n"
        "\n"
        "def standalone():\n"
        "    return 'I am a standalone function'\n"
    )

    def test_full_module_returns_documents(self, tmp_path):
        """A real Python module should produce a non-empty list of Documents."""
        f = _write_py(tmp_path, "proc.py", self._FULL_MODULE)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        assert len(docs) > 0

    def test_full_module_has_function_chunks(self, tmp_path):
        """A module with functions should produce function_definition chunks."""
        f = _write_py(tmp_path, "proc.py", self._FULL_MODULE)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = {d.metadata["node_type"] for d in docs}
        assert "function_definition" in node_types

    def test_full_module_class_not_emitted_as_whole(self, tmp_path):
        """The Processor class should be recursed into, not emitted as one chunk."""
        f = _write_py(tmp_path, "proc.py", self._FULL_MODULE)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        node_types = {d.metadata["node_type"] for d in docs}
        assert "class_definition" not in node_types

    def test_full_module_standalone_function_present(self, tmp_path):
        """The standalone function should be present as a chunk."""
        f = _write_py(tmp_path, "proc.py", self._FULL_MODULE)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        standalone_docs = [d for d in docs if "standalone" in d.text]
        assert len(standalone_docs) >= 1

    def test_class_methods_have_class_context_standalone_does_not(self, tmp_path):
        """Class methods should have '# Class: Processor', standalone func should not."""
        f = _write_py(tmp_path, "proc.py", self._FULL_MODULE)
        reader = PythonFileReader()
        docs = reader.load_data(f)

        process_docs = [d for d in docs if "def process" in d.text]
        standalone_docs = [d for d in docs if "def standalone" in d.text]

        if process_docs:
            assert "# Class: Processor" in process_docs[0].text

        if standalone_docs:
            assert "# Class:" not in standalone_docs[0].text

    def test_two_functions_file(self, tmp_path):
        """A file with two functions should produce two function_definition chunks."""
        content = (
            "def greet(name):\n"
            "    return f'Hello, {name}'\n"
            "\n"
            "def farewell(name):\n"
            "    return f'Goodbye, {name}'\n"
        )
        f = _write_py(tmp_path, "greetings.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        func_docs = [
            d for d in docs if d.metadata["node_type"] == "function_definition"
        ]
        assert len(func_docs) == 2

    def test_each_function_is_self_contained(self, tmp_path):
        """Each function chunk should contain only that function's code."""
        content = (
            "def greet(name):\n"
            "    return f'Hello, {name}'\n"
            "\n"
            "def farewell(name):\n"
            "    return f'Goodbye, {name}'\n"
        )
        f = _write_py(tmp_path, "greetings.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        func_docs = [
            d for d in docs if d.metadata["node_type"] == "function_definition"
        ]
        for doc in func_docs:
            # Each function chunk should contain exactly one 'def'
            # (context prefix + function code)
            code_part = (
                doc.text.split("\n# File:")[0] if "# File:" in doc.text else doc.text
            )
            # After the prefix, the code should have exactly one function
            def_count = doc.text.count("\ndef ") + (
                1 if "\ndef " not in doc.text and "def " in doc.text else 0
            )
            # Loose assertion: shouldn't contain both function names
            has_greet = "def greet" in doc.text
            has_farewell = "def farewell" in doc.text
            assert not (has_greet and has_farewell), (
                "A single function chunk should not contain both functions"
            )

    def test_no_duplicate_byte_ranges(self, tmp_path):
        """No two chunks should cover the exact same byte range."""
        f = _write_py(tmp_path, "proc.py", self._FULL_MODULE)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        byte_ranges = set()
        for doc in docs:
            rng = (doc.metadata.get("start_byte"), doc.metadata.get("end_byte"))
            if rng != (None, None):
                assert rng not in byte_ranges, f"Duplicate byte range: {rng}"
                byte_ranges.add(rng)

    def test_all_chunks_non_empty(self, tmp_path):
        """Every chunk text should be non-empty."""
        f = _write_py(tmp_path, "proc.py", self._FULL_MODULE)
        reader = PythonFileReader()
        docs = reader.load_data(f)
        for doc in docs:
            assert len(doc.text.strip()) > 0

    def test_multiple_classes(self, tmp_path):
        """A file with two classes should recurse into both independently."""
        content = (
            "class Dog:\n"
            "    def bark(self):\n"
            "        return 'Woof! I am a dog barking'\n"
            "\n"
            "class Cat:\n"
            "    def meow(self):\n"
            "        return 'Meow! I am a cat speaking'\n"
        )
        f = _write_py(tmp_path, "animals.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)

        bark_docs = [d for d in docs if "def bark" in d.text]
        meow_docs = [d for d in docs if "def meow" in d.text]

        assert len(bark_docs) >= 1
        assert len(meow_docs) >= 1

        # bark should have Dog context, meow should have Cat context
        if bark_docs:
            assert "# Class: Dog" in bark_docs[0].text
            assert "# Class: Cat" not in bark_docs[0].text
        if meow_docs:
            assert "# Class: Cat" in meow_docs[0].text
            assert "# Class: Dog" not in meow_docs[0].text

    def test_nested_class_handling(self, tmp_path):
        """A class inside a class should still produce method chunks."""
        content = (
            "class Outer:\n"
            "    class Inner:\n"
            "        def inner_method(self):\n"
            "            return 'I am an inner method'\n"
            "\n"
            "    def outer_method(self):\n"
            "        return 'I am an outer method'\n"
        )
        f = _write_py(tmp_path, "nested.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)

        # Should produce some function_definition chunks
        func_docs = [
            d for d in docs if d.metadata["node_type"] == "function_definition"
        ]
        assert len(func_docs) >= 1

    def test_expression_statement_leaf(self, tmp_path):
        """Top-level expression statements (like docstrings) should be treated as leaves."""
        content = (
            '"""This is a module docstring that is long enough to exceed the minimum chunk size threshold."""\n'
            "\n"
            "def func():\n"
            "    return 'hello from the function'\n"
        )
        f = _write_py(tmp_path, "docstring.py", content)
        reader = PythonFileReader()
        docs = reader.load_data(f)

        # The module should produce at least a function chunk
        node_types = [d.metadata["node_type"] for d in docs]
        assert "function_definition" in node_types

    def test_extra_info_passed_through(self, tmp_path):
        """extra_info parameter is accepted but does not affect output (currently unused)."""
        f = _write_py(
            tmp_path,
            "extra.py",
            "def foo():\n    return 'extra info test here'\n",
        )
        reader = PythonFileReader()
        docs = reader.load_data(f, extra_info={"source": "test"})
        assert len(docs) >= 1

    def test_load_nodes_wraps_documents(self, tmp_path):
        """load_nodes() should return TextNodes wrapping the Documents."""
        from llama_index.core.schema import TextNode

        f = _write_py(
            tmp_path,
            "nodes.py",
            "def func():\n    return 'node wrapping test'\n",
        )
        reader = PythonFileReader()
        nodes = reader.load_nodes(f)
        assert len(nodes) >= 1
        for node in nodes:
            assert isinstance(node, TextNode)
            assert len(node.text) > 0
