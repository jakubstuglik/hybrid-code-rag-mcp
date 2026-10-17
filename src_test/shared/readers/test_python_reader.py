"""
Tests for shared/readers/python_reader.py - Python reader with Tree-sitter AST.

Covers: registry wiring (.py/.pyi), the ``# File: / # Module: / # Class:``
context prefix (same layout as the Java/Kotlin ``//`` prefix), dotted module
paths from package directories, class_summary / class_overview chunks,
decorated and nested classes, methods and constructors, trivial-method
grouping, assignment grouping (constants vs fields), import grouping, module
docstrings, script bodies, dedented method text, oversized splitting and
fallbacks.
"""

from pathlib import Path

import pytest

from shared.readers import READER_REGISTRY, get_reader
from shared.readers.python_reader import PythonFileReader, module_path


SAMPLE = '''"""Order handling module with a docstring long enough to be emitted."""
from __future__ import annotations

import logging
from typing import List

MAX_ITEMS = 100
DEFAULT_TIMEOUT = 5.0


@dataclass
class Order(BaseModel, metaclass=Meta):
    """An order placed by a customer.

    Second paragraph that must not appear in the summary.
    """

    id: int
    items: List[str] = []

    def __init__(self, id: int):
        self.id = id
        self.items = []
        self.closed = False
        self.log = logging.getLogger(__name__)
        self.total = 0
        self.extra = None

    @property
    def size(self) -> int:
        return len(self.items)

    def __len__(self):
        return self.size

    def __repr__(self):
        return f"Order({self.id})"

    async def submit(self, client, retries: int = 3) -> bool:
        """Send the order."""
        for attempt in range(retries):
            ok = await client.post(self)
            if ok:
                return True
            logging.warning("retry %s", attempt)
        return False

    class Line:
        sku: str

        def describe(self) -> str:
            text = "line " + self.sku
            return text


def compute_total(order: Order) -> float:
    total = 0.0
    for item in order.items:
        total += 1
    return total


if __name__ == "__main__":
    compute_total(Order(1))
'''


@pytest.fixture
def reader():
    return PythonFileReader()


def _load(tmp_path, text, name="orders.py", reader=None):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return (reader or PythonFileReader()).load_data(f)


def _by_type(docs, node_type):
    return [d for d in docs if d.metadata["node_type"] == node_type]


class TestRegistry:
    def test_py_and_pyi_registered(self):
        assert isinstance(READER_REGISTRY[".py"], PythonFileReader)
        assert isinstance(READER_REGISTRY[".pyi"], PythonFileReader)

    def test_get_reader_by_path(self):
        assert isinstance(get_reader(Path("pkg/mod.pyi")), PythonFileReader)


class TestModulePath:
    def test_plain_file_uses_stem(self, tmp_path):
        assert module_path(tmp_path / "script.py") == "script"

    def test_package_dirs_are_joined(self, tmp_path):
        pkg = tmp_path / "src" / "app" / "core"
        pkg.mkdir(parents=True)
        (tmp_path / "src" / "app" / "__init__.py").write_text("")
        (pkg / "__init__.py").write_text("")
        assert module_path(pkg / "orders.py") == "app.core.orders"

    def test_init_module_is_package(self, tmp_path):
        pkg = tmp_path / "app"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        assert module_path(pkg / "__init__.py") == "app"


class TestContextPrefix:
    def test_every_chunk_has_file_and_module(self, tmp_path):
        for d in _load(tmp_path, SAMPLE):
            assert d.text.startswith("# File: orders.py\n# Module: orders")

    def test_method_chunks_carry_class_header(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        submit = [d for d in docs if d.metadata.get("function_name") == "submit"][0]
        assert "# Class: @dataclass class Order(BaseModel, metaclass=Meta)" in submit.text
        assert submit.metadata["class_name"] == "Order"

    def test_nested_class_chain(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        line = [d for d in _by_type(docs, "class_summary") if d.metadata["class_name"] == "Line"][0]
        assert "# Class: Order > class Line" in line.text

    def test_top_level_function_has_no_class_line(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        fn = [d for d in docs if d.metadata.get("function_name") == "compute_total"][0]
        assert "# Class:" not in fn.text
        assert "class_name" not in fn.metadata

    def test_prefix_layout_matches_java_reader(self, tmp_path):
        from shared.readers.java_reader import _build_context_prefix as java_prefix

        java = java_prefix("A.java", "com.x", "A", "class A").split("\n")
        py = PythonFileReader().build_prefix("a.py", "x.a", "A", "class A").split("\n")
        assert [ln.split(":")[0].lstrip("/# ") for ln in java] == ["File", "Package", "Class"]
        assert [ln.split(":")[0].lstrip("/# ") for ln in py] == ["File", "Module", "Class"]


class TestClassSummary:
    def test_summary_lists_member_signatures_without_bodies(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        summary = [d for d in _by_type(docs, "class_summary") if d.metadata["class_name"] == "Order"][0]
        text = summary.text
        assert "def __init__(self, id: int)" in text
        assert "@property def size(self) -> int" in text
        assert "async def submit(self, client, retries: int = 3) -> bool" in text
        assert "class Line: ..." in text
        assert "id: int" in text
        assert "await client.post" not in text

    def test_summary_has_first_docstring_paragraph_only(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        summary = [d for d in _by_type(docs, "class_summary") if d.metadata["class_name"] == "Order"][0]
        assert "An order placed by a customer." in summary.text
        assert "Second paragraph" not in summary.text

    def test_class_without_members_still_summarised(self, tmp_path):
        docs = _load(tmp_path, "class Empty(Exception):\n    pass\n")
        assert _by_type(docs, "class_summary")

    def test_large_class_gets_overview(self, tmp_path):
        methods = "\n".join(
            f"    def method_{i}(self, alpha, beta, gamma, delta, epsilon, zeta):\n"
            f"        value = alpha + beta + gamma\n        other = delta + epsilon\n"
            f"        more = zeta * 2\n        again = value + other\n        last = more + again\n"
            f"        return value + other + more + {i}\n"
            for i in range(120)
        )
        docs = _load(tmp_path, f"class Big(Base):\n    x = 1\n\n{methods}")
        ov = _by_type(docs, "class_overview")
        assert ov
        assert "Big is a Python class extends Base" in ov[0].text
        assert "120 methods" in ov[0].text


class TestMembers:
    def test_init_is_constructor(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert [d for d in _by_type(docs, "constructor_declaration") if d.metadata["function_name"] == "__init__"]

    def test_trivial_methods_are_grouped(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        groups = _by_type(docs, "method_group")
        assert groups and groups[0].metadata["group_count"] >= 3
        assert "# Method group:" in groups[0].text

    def test_method_text_is_dedented(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        submit = [d for d in docs if d.metadata.get("function_name") == "submit"][0]
        assert "\nasync def submit(" in submit.text
        assert "\n    for attempt in range(retries):" in submit.text

    def test_decorators_kept_in_method_text(self, tmp_path):
        src = "class A:\n    @staticmethod\n    def build(x, y):\n        z = x + y\n        w = z * 2\n        q = w - 1\n        r = q + 1\n        s = r * 3\n        return s\n"
        docs = _load(tmp_path, src)
        m = [d for d in docs if d.metadata.get("function_name") == "build"][0]
        assert "@staticmethod\ndef build(x, y):" in m.text
        assert m.metadata["decorators"] == ["@staticmethod"]


class TestModuleLevel:
    def test_import_group(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        imp = _by_type(docs, "import_group")
        assert len(imp) == 1
        assert "import logging" in imp[0].text and "from __future__ import annotations" in imp[0].text

    def test_upper_case_assignments_are_constants(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        const = _by_type(docs, "constant_declaration")
        assert const and "MAX_ITEMS = 100" in const[0].text and "DEFAULT_TIMEOUT" in const[0].text

    def test_other_assignments_are_fields(self, tmp_path):
        docs = _load(tmp_path, "logger = get_logger()\nconfig = {}\n")
        assert _by_type(docs, "field_declaration")

    def test_module_docstring_is_block_comment(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert "Order handling module" in _by_type(docs, "block_comment")[0].text

    def test_main_guard_is_script_body(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert 'if __name__ == "__main__":' in _by_type(docs, "script_body")[0].text

    def test_metadata(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        for d in docs:
            assert d.metadata["module_name"] == "orders"
            assert d.metadata["unit_name"] == "orders"
            assert d.metadata["start_line"] <= d.metadata["end_line"]


class TestStubsAndFallbacks:
    def test_pyi_stub_methods_grouped(self, tmp_path):
        src = "class Client:\n    def get(self, url: str) -> Response: ...\n    def post(self, url: str) -> Response: ...\n    def put(self, url: str) -> Response: ...\n"
        docs = _load(tmp_path, src, name="client.pyi")
        assert _by_type(docs, "class_summary") and _by_type(docs, "method_group")

    def test_empty_file(self, tmp_path):
        assert _load(tmp_path, "   \n") == []

    def test_comment_only_file_falls_back_to_full_file(self, tmp_path):
        docs = _load(tmp_path, "# just a comment that is long enough to matter here\n")
        assert docs[0].metadata["node_type"] == "full_file"

    def test_oversized_function_is_split(self, tmp_path):
        body = "\n".join(f"    value_{i} = compute_something_long(argument_{i}, other_{i})" for i in range(800))
        docs = _load(tmp_path, f"def huge():\n{body}\n")
        parts = _by_type(docs, "method_declaration_split")
        assert len(parts) > 1
        assert all(p.text.startswith("# File: orders.py") for p in parts)
