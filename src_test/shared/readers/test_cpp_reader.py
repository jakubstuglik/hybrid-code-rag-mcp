"""Tests for the C and C++ reader."""

from shared.readers.cpp_reader import CppFileReader, _normalize_qt


_HEADER = """/*************** CVS data ***************
$Log: mainwindow.h,v $
Revision 1.2  Restored after disk failure
*********** CVS data - end **********/
#ifndef MAINWINDOW_H
#define MAINWINDOW_H
#include <QWidget>
#include "printer.h"
namespace App {
class MainWindow : public ModuleMainWindow
{
    Q_OBJECT
public:
    enum work_mode { NORMAL = 0, TEMPLATE };
    MainWindow(QWidget *parent);
    ~MainWindow();
    virtual void buildStatusBar(void);
private:
    int item_code;
    void personalize(void);
public: signals:
    void operatorAnswered(bool wynik);
private slots:
    void on_action_triggered();
};
}
#endif
"""

_CPP = """
#include "mainwindow.h"
void MainWindow::buildStatusBar(void) {
    delete device;
}
"""

_C_FILE = """
#include <stdio.h>
#define MAX 10
struct Point { int x; int y; };
int helper(int n);
int helper(int n) { return n + 1; }
"""


def _write(tmp_path, name: str, text: str):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _docs(tmp_path, name: str, text: str):
    return CppFileReader().load_data(_write(tmp_path, name, text))


def _by_type(docs, node_type: str):
    return [doc for doc in docs if doc.metadata["node_type"] == node_type]


class TestNormalizeQt:
    def test_replacement_keeps_length_and_newlines(self):
        text = "class T {\n    Q_OBJECT\npublic slots:\n    void a();\nsignals:\n};\n"
        out = _normalize_qt(text)
        assert len(out) == len(text)
        assert out.count("\n") == text.count("\n")
        assert "Q_OBJECT" not in out
        assert "slots" not in out


class TestCppHeader:
    def test_class_summary_keeps_signatures_and_drops_cvs_log(self, tmp_path):
        docs = _docs(tmp_path, "mainwindow.h", _HEADER)
        summary = _by_type(docs, "class_summary")
        assert len(summary) == 1
        text = summary[0].text
        assert "// File: mainwindow.h" in text
        assert "// Namespace: App" in text
        assert "class MainWindow : public ModuleMainWindow" in text
        assert "Q_OBJECT" in text
        assert "buildStatusBar" in text
        assert "item_code" in text
        assert "signals:" in text
        assert "operatorAnswered" in text
        assert "private slots:" in text
        assert "on_action_triggered" in text
        assert "Restored after disk failure" not in text
        assert "$Log:" not in text
        meta = summary[0].metadata
        assert meta["class_name"] == "MainWindow"
        assert meta["unit_name"] == "mainwindow"
        assert meta["start_line"] > 1

    def test_includes_are_one_group(self, tmp_path):
        docs = _docs(tmp_path, "mainwindow.h", _HEADER)
        groups = _by_type(docs, "include_group")
        assert len(groups) == 1
        assert "#include <QWidget>" in groups[0].text
        assert '#include "printer.h"' in groups[0].text
        assert "MAINWINDOW_H" not in groups[0].text

    def test_cvs_log_only_file_produces_no_chunks(self, tmp_path):
        text = "/* $Log: a.h,v $\nRevision 1.1 old\n*/\n"
        assert _docs(tmp_path, "a.h", text) == []

    def test_empty_file(self, tmp_path):
        assert _docs(tmp_path, "empty.cpp", "   \n") == []


class TestCppBodies:
    def test_out_of_line_method_carries_class_name(self, tmp_path):
        docs = _docs(tmp_path, "mainwindow.cpp", _CPP)
        funcs = _by_type(docs, "cpp_function")
        assert len(funcs) == 1
        assert "delete device" in funcs[0].text
        assert funcs[0].metadata["class_name"] == "MainWindow"
        assert funcs[0].metadata["object_name"] == "buildStatusBar"
        assert "// File: mainwindow.cpp" in funcs[0].text

    def test_inline_body_is_not_copied_into_the_summary(self, tmp_path):
        text = """
class Foo : public Bar {
public:
    void big() { delete device; int a; int b; }
};
"""
        docs = _docs(tmp_path, "foo.h", text)
        summary = _by_type(docs, "class_summary")[0].text
        assert "void big()" in summary
        assert "delete device" not in summary
        bodies = _by_type(docs, "cpp_function")
        assert len(bodies) == 1
        assert "delete device" in bodies[0].text

    def test_three_trivial_methods_become_one_group(self, tmp_path):
        text = """
int Foo::a() { return 1; }
int Foo::b() { return 2; }
int Foo::c() { return 3; }
int Foo::big() {
    int a = 1;
    int b = 2;
    int c = 3;
    int d = 4;
    int e = 5;
    int f = 6;
    return a + b + c + d + e + f;
}
"""
        docs = _docs(tmp_path, "foo.cpp", text)
        groups = _by_type(docs, "method_group")
        assert len(groups) == 1
        assert "Foo::a" in groups[0].text
        assert "Foo::c" in groups[0].text
        assert groups[0].metadata["class_name"] == "Foo"
        big = _by_type(docs, "cpp_function")
        assert len(big) == 1
        assert "Foo::big" in big[0].text

    def test_large_class_gets_an_overview(self, tmp_path):
        methods = "\n".join(
            "    void methodNumber"
            f"{i:03d}OfTheClassWithALongSignature(int value, const char *name);"
            for i in range(120)
        )
        text = f"class BigWindow : public ModuleMainWindow {{\npublic:\n{methods}\n}};\n"
        docs = _docs(tmp_path, "big.h", text)
        overviews = _by_type(docs, "class_overview")
        assert len(overviews) == 1
        assert "BigWindow is a C++ class inheriting from ModuleMainWindow" in (
            overviews[0].text
        )
        assert "120 methods" in overviews[0].text
        assert overviews[0].metadata["class_name"] == "BigWindow"


class TestCFile:
    def test_struct_function_and_prototype(self, tmp_path):
        docs = _docs(tmp_path, "point.c", _C_FILE)
        summary = _by_type(docs, "class_summary")
        assert len(summary) == 1
        assert "struct Point" in summary[0].text
        assert "int x" in summary[0].text
        assert summary[0].metadata["class_name"] == "Point"
        funcs = _by_type(docs, "cpp_function")
        assert len(funcs) == 1
        assert "return n + 1" in funcs[0].text
        assert "class_name" not in funcs[0].metadata
        protos = _by_type(docs, "declaration_group")
        assert len(protos) == 1
        assert "int helper(int n);" in protos[0].text
        macros = _by_type(docs, "macro_group")
        assert any("MAX" in doc.text for doc in macros)

    def test_file_scope_enum(self, tmp_path):
        docs = _docs(tmp_path, "color.h", "enum Color { RED, BLUE };\n")
        enums = _by_type(docs, "enum_declaration")
        assert len(enums) == 1
        assert "Color" in enums[0].text
        assert enums[0].metadata["class_name"] == "Color"


class TestCppExtensionVariants:
    """.hpp/.hh/.hxx/.cc/.cxx/.ino are routed to the C++ reader and parsed as C++."""

    SRC = (
        "#include <string>\n\n"
        "namespace db {\n"
        "class Table {\n public:\n"
        "  explicit Table(const std::string& name);\n"
        "  int Rows() const;\n"
        " private:\n  std::string name_;\n};\n"
        "}  // namespace db\n"
    )

    def test_variants_registered(self):
        from shared.readers import READER_REGISTRY

        for ext in (".hpp", ".hh", ".hxx", ".cc", ".cxx", ".ino"):
            assert isinstance(READER_REGISTRY[ext], CppFileReader), ext

    def test_cc_and_hpp_files_produce_class_chunks(self, tmp_path):
        for name in ("table.hpp", "table.cc", "table.hh"):
            f = tmp_path / name
            f.write_text(self.SRC, encoding="utf-8")
            types = {d.metadata["node_type"] for d in CppFileReader().load_data(f)}
            assert "class_summary" in types, name


_ORDER_CPP = """class OrderCalculator {
public:
    int calc_order_discount(int amount);
};
"""

_SKIP_META = {"file_path", "creation_datetime", "modification_datetime"}


def _signature(docs):
    signed = []
    for doc in docs:
        meta = {key: value for key, value in doc.metadata.items() if key not in _SKIP_META}
        signed.append((doc.text, meta))
    return signed


class TestLeadingUtf8Bom:
    def test_class_detected_and_matches_file_without_bom(self, tmp_path):
        raw = _ORDER_CPP.encode("utf-8")
        bom_dir = tmp_path / "bom"
        plain_dir = tmp_path / "plain"
        bom_dir.mkdir()
        plain_dir.mkdir()
        bom_path = bom_dir / "order.cpp"
        plain_path = plain_dir / "order.cpp"
        bom_path.write_bytes(b"\xef\xbb\xbf" + raw)
        plain_path.write_bytes(raw)

        bom_docs = CppFileReader().load_data(bom_path)
        plain_docs = CppFileReader().load_data(plain_path)
        summary = _by_type(bom_docs, "class_summary")
        assert len(summary) == 1
        assert summary[0].metadata["class_name"] == "OrderCalculator"
        assert summary[0].metadata["start_line"] == 1
        assert plain_docs[0].metadata["start_line"] == 1
        assert "\ufeff" not in summary[0].text
        assert "\ufeff" not in summary[0].metadata["class_name"]
        assert _signature(bom_docs) == _signature(plain_docs)
