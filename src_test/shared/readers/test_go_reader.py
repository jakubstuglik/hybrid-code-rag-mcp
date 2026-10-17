"""
Tests for shared/readers/go_reader.py - Go reader with Tree-sitter AST.

Covers: registry wiring, ``// File / // Package / // Class`` prefix, struct
and interface types as class_summary with methods collected by receiver
(pointer and value), New<Type> constructors, other named types, functions,
methods, const/var blocks, imports, doc comments, trivial-method grouping,
class_overview for large types and fallbacks.
"""

from pathlib import Path

from shared.readers import READER_REGISTRY, get_reader
from shared.readers.go_reader import GoFileReader

SAMPLE = """// Package orders implements order storage and the HTTP handlers for it.
package orders

import (
	"errors"
	"fmt"
)

// MaxItems limits the number of items per order.
const MaxItems = 10

var ErrNotFound = errors.New("order not found")

// Order is a customer order.
type Order struct {
	ID    int
	Items []string
}

// Store persists orders.
type Store interface {
	Get(id int) (*Order, error)
	Put(o *Order) error
}

type ID int

type Handler func(o *Order) error

// NewOrder creates an order.
func NewOrder(id int) *Order {
	return &Order{ID: id}
}

// Total returns the number of items.
func (o *Order) Total() int {
	n := 0
	for range o.Items {
		n++
	}
	fmt.Println(n)
	return n
}

func (o Order) A() int { return 1 }
func (o Order) B() int { return 2 }
func (o Order) C() int { return 3 }

func Validate(o *Order) error {
	if len(o.Items) > MaxItems {
		return errors.New("too many items")
	}
	return nil
}
"""


def _load(tmp_path, text, name="store.go"):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return GoFileReader().load_data(f)


def _types(docs, t):
    return [d for d in docs if d.metadata["node_type"] == t]


def _summary(docs, cls):
    return [d for d in _types(docs, "class_summary") if d.metadata["class_name"] == cls][0]


class TestRegistry:
    def test_go_registered(self):
        assert isinstance(READER_REGISTRY[".go"], GoFileReader)
        assert isinstance(get_reader(Path("x/main.go")), GoFileReader)


class TestPrefix:
    def test_file_and_package_on_every_chunk(self, tmp_path):
        for d in _load(tmp_path, SAMPLE):
            assert d.text.startswith("// File: store.go\n// Package: orders")
            assert d.metadata["package_name"] == "orders"

    def test_method_has_receiver_class_line(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        m = [d for d in docs if d.metadata.get("function_name") == "Total"][0]
        assert "// Class: type Order struct" in m.text
        assert m.metadata["class_name"] == "Order" and m.metadata["receiver_type"] == "Order"

    def test_function_has_no_class_line(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        f = [d for d in docs if d.metadata.get("function_name") == "Validate"][0]
        assert "// Class:" not in f.text and f.metadata["node_type"] == "method_declaration"


class TestTypes:
    def test_struct_summary_collects_methods(self, tmp_path):
        s = _summary(_load(tmp_path, SAMPLE), "Order").text
        assert "type Order struct {" in s and "Items []string" in s
        assert "// Methods of Order in store.go:" in s
        assert "func NewOrder(id int) *Order" in s
        assert "func (o *Order) Total() int" in s
        assert "func (o Order) A() int" in s
        assert "n++" not in s

    def test_struct_doc_comment(self, tmp_path):
        assert "// Order is a customer order." in _summary(_load(tmp_path, SAMPLE), "Order").text

    def test_interface_summary(self, tmp_path):
        s = _summary(_load(tmp_path, SAMPLE), "Store")
        assert "Put(o *Order) error" in s.text and s.metadata["go_kind"] == "interface"

    def test_other_named_types(self, tmp_path):
        names = {d.metadata["class_name"] for d in _types(_load(tmp_path, SAMPLE), "type_alias_declaration")}
        assert {"ID", "Handler"} <= names

    def test_grouped_type_declaration(self, tmp_path):
        docs = _load(tmp_path, "package p\n\ntype (\n\tA struct{ X int }\n\tB = int\n)\n")
        assert _summary(docs, "A") and _types(docs, "type_alias_declaration")

    def test_large_struct_overview(self, tmp_path):
        fields = "\n".join(f"\tField{i} string `json:\"field_{i}_with_a_long_tag_name\"`" for i in range(200))
        docs = _load(tmp_path, f"package p\n\ntype Big struct {{\n{fields}\n}}\n")
        ov = _types(docs, "class_overview")
        assert ov and "Big is a Go struct with 200 fields" in ov[0].text


class TestFunctions:
    def test_new_function_is_constructor(self, tmp_path):
        c = _types(_load(tmp_path, SAMPLE), "constructor_declaration")
        assert c and c[0].metadata["class_name"] == "Order" and "// NewOrder creates an order." in c[0].text

    def test_trivial_methods_grouped(self, tmp_path):
        g = _types(_load(tmp_path, SAMPLE), "method_group")
        assert g and g[0].metadata["group_count"] == 3 and g[0].metadata["class_name"] == "Order"

    def test_doc_comment_kept_with_method(self, tmp_path):
        m = [d for d in _load(tmp_path, SAMPLE) if d.metadata.get("function_name") == "Total"][0]
        assert "// Total returns the number of items.\nfunc (o *Order) Total()" in m.text


class TestDeclarations:
    def test_const_and_var(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert "const MaxItems = 10" in _types(docs, "constant_declaration")[0].text
        assert "ErrNotFound" in _types(docs, "field_declaration")[0].text

    def test_import_group(self, tmp_path):
        imp = _types(_load(tmp_path, SAMPLE), "import_group")
        assert len(imp) == 1 and '"errors"' in imp[0].text

    def test_package_doc_is_block_comment(self, tmp_path):
        assert "Package orders implements" in _types(_load(tmp_path, SAMPLE), "block_comment")[0].text


class TestFallbacks:
    def test_empty(self, tmp_path):
        assert _load(tmp_path, "\n") == []

    def test_package_only_falls_back(self, tmp_path):
        assert _load(tmp_path, "package main\n")[0].metadata["node_type"] == "full_file"
