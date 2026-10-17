"""
Tests for shared/readers/csharp_reader.py - C# reader with Tree-sitter AST.

Covers: registry wiring, the ``// File / // Namespace / // Class`` prefix
(same layout as Java), block, nested and file-scoped namespaces, classes,
structs, interfaces, records, enums, partial and nested types, members
(methods, constructors, properties, fields, events, indexers, operators,
delegates), XML doc comments, using groups, trivial-method grouping,
class_overview for large types, top-level statements and fallbacks.
"""

from pathlib import Path

from shared.readers import READER_REGISTRY, get_reader
from shared.readers.csharp_reader import CSharpFileReader

SAMPLE = """using System;
using System.Collections.Generic;

namespace Acme.Orders
{
    /// <summary>Handles orders.</summary>
    [Serializable]
    public partial class OrderService : BaseService, IOrderService
    {
        private readonly IOrderRepository _repo;
        public int Count { get; private set; }
        public event EventHandler Changed;

        public OrderService(IOrderRepository repo)
        {
            _repo = repo;
        }

        /// <summary>Finds an order.</summary>
        public async Task<Order> FindAsync(int id)
        {
            var order = await _repo.GetAsync(id);
            if (order == null)
                throw new KeyNotFoundException();
            Changed?.Invoke(this, EventArgs.Empty);
            return order;
        }

        public int this[int i] => i;

        public class Line
        {
            public string Sku { get; set; }
        }
    }

    public interface IOrderService
    {
        Task<Order> FindAsync(int id);
    }

    public record Order(int Id, string Name);

    public enum Status { Open, Closed }

    public struct Money { public decimal Amount; }

    public delegate void OrderHandler(Order o);

    namespace Internal
    {
        internal static class Helpers
        {
            public static int A() => 1;
            public static int B() => 2;
            public static int C() => 3;
        }
    }
}
"""


def _load(tmp_path, text, name="OrderService.cs"):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return CSharpFileReader().load_data(f)


def _types(docs, t):
    return [d for d in docs if d.metadata["node_type"] == t]


def _summary(docs, cls):
    return [d for d in _types(docs, "class_summary") if d.metadata["class_name"] == cls][0]


class TestRegistry:
    def test_cs_registered(self):
        assert isinstance(READER_REGISTRY[".cs"], CSharpFileReader)
        assert isinstance(get_reader(Path("A.cs")), CSharpFileReader)


class TestPrefixAndNamespaces:
    def test_every_chunk_has_file_line(self, tmp_path):
        for d in _load(tmp_path, SAMPLE):
            assert d.text.startswith("// File: OrderService.cs\n")

    def test_block_namespace(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        s = _summary(docs, "OrderService")
        assert "// Namespace: Acme.Orders\n" in s.text
        assert s.metadata["namespace"] == "Acme.Orders"

    def test_nested_namespace_is_joined(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert _summary(docs, "Helpers").metadata["namespace"] == "Acme.Orders.Internal"

    def test_file_scoped_namespace(self, tmp_path):
        docs = _load(tmp_path, "namespace Acme.Billing;\n\npublic class Invoice\n{\n    public int Id { get; set; }\n}\n")
        s = _summary(docs, "Invoice")
        assert "// Namespace: Acme.Billing" in s.text

    def test_class_line_has_full_header(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        m = [d for d in docs if d.metadata.get("function_name") == "FindAsync" and d.metadata["node_type"] == "method_declaration"][0]
        assert "// Class: [Serializable] public partial class OrderService : BaseService, IOrderService" in m.text

    def test_nested_type_chain(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert "// Class: OrderService > public class Line" in _summary(docs, "Line").text


class TestTypes:
    def test_summary_has_signatures_without_bodies(self, tmp_path):
        s = _summary(_load(tmp_path, SAMPLE), "OrderService").text
        assert "public OrderService(IOrderRepository repo)" in s
        assert "public async Task<Order> FindAsync(int id)" in s
        assert "public int Count { get; private set; }" in s
        assert "public event EventHandler Changed;" in s
        assert "public class Line { ... }" in s
        assert "KeyNotFoundException" not in s

    def test_doc_comment_in_summary(self, tmp_path):
        assert "/// <summary>Handles orders.</summary>" in _summary(_load(tmp_path, SAMPLE), "OrderService").text

    def test_partial_flag(self, tmp_path):
        assert _summary(_load(tmp_path, SAMPLE), "OrderService").metadata["partial"] is True

    def test_interface_record_enum_struct(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert _summary(docs, "IOrderService").metadata["csharp_kind"] == "interface"
        assert "public record Order(int Id, string Name);" in _summary(docs, "Order").text
        e = _summary(docs, "Status").text
        assert "Open," in e and "Closed," in e
        assert _summary(docs, "Money").metadata["csharp_kind"] == "struct"

    def test_large_class_overview(self, tmp_path):
        methods = "\n".join(
            f"    public int Method{i}(int alpha, int beta, int gamma, int delta) {{ return alpha + beta + gamma + delta + {i}; }}"
            for i in range(120)
        )
        docs = _load(tmp_path, f"namespace N {{ public sealed class Big : Base {{\n{methods}\n}} }}")
        ov = _types(docs, "class_overview")
        assert ov and "Big is a C# sealed class inherits Base with 120 methods" in ov[0].text


class TestMembers:
    def test_member_node_types(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert _types(docs, "constructor_declaration")
        assert any("FindAsync" in d.text for d in _types(docs, "method_declaration"))
        fields = "\n".join(d.text for d in _types(docs, "field_declaration"))
        assert "_repo" in fields and "Count" in fields and "this[int i]" in fields
        assert _types(docs, "type_alias_declaration")[0].metadata["function_name"] == "OrderHandler"

    def test_doc_comment_kept_with_method(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        m = [d for d in _types(docs, "method_declaration") if d.metadata.get("function_name") == "FindAsync"][0]
        assert "/// <summary>Finds an order.</summary>\npublic async Task<Order> FindAsync" in m.text

    def test_trivial_methods_grouped(self, tmp_path):
        g = _types(_load(tmp_path, SAMPLE), "method_group")
        assert g and g[0].metadata["group_count"] == 3 and g[0].metadata["class_name"] == "Helpers"

    def test_using_group(self, tmp_path):
        imp = _types(_load(tmp_path, SAMPLE), "import_group")
        assert len(imp) == 1 and "using System.Collections.Generic;" in imp[0].text


class TestOther:
    def test_top_level_statements(self, tmp_path):
        docs = _load(tmp_path, 'using System;\nvar app = Builder.Create(args);\napp.MapGet("/", () => "Hello");\napp.Run();\n', "Program.cs")
        assert "app.Run();" in _types(docs, "script_body")[0].text

    def test_empty_file(self, tmp_path):
        assert _load(tmp_path, "\n\n") == []

    def test_comment_only_falls_back(self, tmp_path):
        docs = _load(tmp_path, "// short\n")
        assert docs[0].metadata["node_type"] == "full_file"

    def test_metadata_lines(self, tmp_path):
        for d in _load(tmp_path, SAMPLE):
            assert d.metadata["unit_name"] == "OrderService"
            assert 1 <= d.metadata["start_line"] <= d.metadata["end_line"]
