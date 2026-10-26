"""Tests for the C and C++ reader."""

from shared.readers.cpp_reader import (
    CppFileReader,
    _C_PARSER,
    _CPP_PARSER,
    _blank_annotation_lines,
    _blank_header_attributes,
    _definition_count,
    _error_bytes,
    _find_first,
    _node_text,
    _normalize_qt,
    _parse_best,
)


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


def _parse_like_reader(source: str, suffix: str):
    """Parse ``source`` the way ``CppFileReader.load_data`` parses it."""
    normalized = _normalize_qt(source)
    if len(normalized) != len(source):
        normalized = source
    annotated = _blank_annotation_lines(normalized)
    if len(annotated) == len(normalized):
        normalized = annotated
    data = source.encode("utf-8")
    parse = normalized.encode("utf-8")
    if len(parse) != len(data):
        parse = data
    parser = _C_PARSER if suffix == ".c" else _CPP_PARSER
    other = _C_PARSER if suffix == ".h" else None
    tree, _used = _parse_best(parser, other, parse)
    if tree.root_node.has_error:
        blanked = _blank_header_attributes(parse)
        if blanked != parse and len(blanked) == len(parse):
            alt, alt_used = _parse_best(parser, other, blanked)
            primary, secondary = _definition_count(alt), _definition_count(tree)
            if primary > secondary or (
                primary == secondary and _error_bytes(alt) < _error_bytes(tree)
            ):
                tree = alt
                _used = alt_used
                parse = blanked
    return tree, parse


def function_body_lines(source: str, suffix: str = ".cpp") -> list[int]:
    """1-based non-blank lines that belong to a function body.

    A body is the compound statement of a ``function_definition``, or a
    compound statement that follows a preprocessor conditional whose branches
    are an unfinished function signature (no ``;`` in the conditional, and the
    body was left outside it). Inner blocks of ``if`` / ``for`` / ``while``
    are part of the outer span and are not listed on their own.
    """
    tree, data = _parse_like_reader(source, suffix)
    lines = source.splitlines()
    needed: set[int] = set()

    def add_span(node) -> None:
        for line_no in range(node.start_point[0] + 1, node.end_point[0] + 2):
            if 1 <= line_no <= len(lines) and lines[line_no - 1].strip():
                needed.add(line_no)

    def is_split_signature(node) -> bool:
        if node.type not in ("preproc_ifdef", "preproc_ifndef", "preproc_if"):
            return False
        text = _node_text(node, data)
        if ";" in text or "(" not in text:
            return False
        if _find_first(node, {"compound_statement"}) is not None:
            return False
        return True

    def walk(node) -> None:
        if node.type == "compound_statement":
            parent = node.parent
            taken = False
            if parent is not None and parent.type == "function_definition":
                body = parent.child_by_field_name("body")
                if body is None or (
                    body.start_byte == node.start_byte and body.end_byte == node.end_byte
                ):
                    add_span(node)
                    taken = True
            else:
                prev = node.prev_sibling
                while prev is not None and (
                    prev.type in ("comment", "\n")
                    or (not prev.is_named and not _node_text(prev, data).strip())
                ):
                    prev = prev.prev_sibling
                if prev is not None and is_split_signature(prev):
                    add_span(node)
                    taken = True
            if taken:
                return
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return sorted(needed)


def uncovered_function_body_lines(source: str, docs, suffix: str = ".cpp") -> list[int]:
    """Non-blank function-body lines outside every chunk's line range.

    ``full_file`` chunks carry no line range, so a body that survived only as
    a whole-file fallback is still uncovered. Signature-only chunks cover the
    declarator lines and leave the body lines in the result.
    """
    covered: set[int] = set()
    for doc in docs:
        start = doc.metadata.get("start_line")
        end = doc.metadata.get("end_line")
        if not start or not end:
            continue
        covered.update(range(int(start), int(end) + 1))
    return [line for line in function_body_lines(source, suffix) if line not in covered]


def _core(docs):
    """Chunk identity used to detect an unintended reader change."""
    found = []
    for doc in docs:
        meta = doc.metadata
        found.append(
            (
                doc.text,
                meta.get("node_type"),
                meta.get("start_line"),
                meta.get("end_line"),
                meta.get("class_name"),
                meta.get("object_name"),
            )
        )
    return found


_GUARD_CPP = """#ifndef WIDGET_H
#define WIDGET_H
#include <string>
#ifdef USE_EXTRA
#include "extra.h"
#else
#include "basic.h"
#endif
class Widget {
public:
    void close();
    int size() const;
};
#endif
"""

_NORMAL_CPP = """#include "widget.h"
namespace App {
void Widget::close() {
    open = false;
}
int Widget::size() const {
    return stored;
}
}
"""

_GUARD_CHUNKS = [
    (
        '// File: guard.cpp\n#include <string>\n#include "extra.h"\n#include "basic.h"',
        "include_group",
        1,
        1,
        None,
        None,
    ),
    (
        "// File: guard.cpp\n// Class: class Widget\nclass Widget {\npublic:\nvoid close();\nint size() const;\n}",
        "class_summary",
        9,
        13,
        "Widget",
        "Widget",
    ),
]

_NORMAL_CHUNKS = [
    (
        '// File: normal.cpp\n#include "widget.h"',
        "include_group",
        1,
        1,
        None,
        None,
    ),
    (
        "// File: normal.cpp\n// Namespace: App\n// Class: Widget\n"
        "void Widget::close() {\n    open = false;\n}",
        "cpp_function",
        3,
        5,
        "Widget",
        "close",
    ),
    (
        "// File: normal.cpp\n// Namespace: App\n// Class: Widget\n"
        "int Widget::size() const {\n    return stored;\n}",
        "cpp_function",
        6,
        8,
        "Widget",
        "size",
    ),
]


def _one(docs, node_type: str, name: str):
    found = [
        doc
        for doc in docs
        if doc.metadata.get("node_type") == node_type
        and doc.metadata.get("object_name") == name
    ]
    assert len(found) == 1, [(d.metadata.get("node_type"), d.metadata.get("object_name")) for d in docs]
    return found[0]


class TestIfdefSplitSignature:
    """A signature split by preprocessor branches keeps its body."""

    def test_parameter_list_differs_across_ifdef(self, tmp_path):
        text = """// Apply the selected mode.
#ifdef FEATURE_X
bool Widget::configure(const Options &opts, int mode)
#else
bool Widget::configure(const Options &opts)
#endif
{
    cache.insert(opts);
    return mode >= 0;
}
"""
        docs = _docs(tmp_path, "widget.cpp", text)
        func = _one(docs, "cpp_function", "configure")
        assert func.metadata["class_name"] == "Widget"
        assert func.metadata["start_line"] == 1
        assert func.metadata["end_line"] == 10
        assert "#ifdef FEATURE_X" in func.text
        assert "int mode" in func.text
        assert "const Options &opts)" in func.text
        assert "cache.insert(opts)" in func.text
        assert "return mode >= 0" in func.text
        assert "// Class: Widget" in func.text
        assert "Apply the selected mode" in func.text
        assert _by_type(docs, "declaration_group") == []
        assert uncovered_function_body_lines(text, docs) == []

    def test_return_type_differs_across_if_elif_else(self, tmp_path):
        text = """#if defined(FEATURE_X)
int Widget::size()
#elif defined(FEATURE_Y)
long Widget::size()
#else
short Widget::size()
#endif
{
    return stored;
}
"""
        docs = _docs(tmp_path, "widget.cpp", text)
        func = _one(docs, "cpp_function", "size")
        assert func.metadata["class_name"] == "Widget"
        assert func.metadata["start_line"] == 1
        assert func.metadata["end_line"] == 10
        assert "#if defined(FEATURE_X)" in func.text
        assert "#elif defined(FEATURE_Y)" in func.text
        assert "long Widget::size()" in func.text
        assert "short Widget::size()" in func.text
        assert "return stored" in func.text
        assert _by_type(docs, "full_file") == []
        assert uncovered_function_body_lines(text, docs) == []

    def test_ifndef_free_function(self, tmp_path):
        text = """#ifndef LEGACY
void reset_cache(Cache &cache, int flags)
#else
void reset_cache(Cache &cache)
#endif
{
    cache.clear();
}
"""
        docs = _docs(tmp_path, "cache.cpp", text)
        func = _one(docs, "cpp_function", "reset_cache")
        assert "class_name" not in func.metadata
        assert "#ifndef LEGACY" in func.text
        assert "int flags" in func.text
        assert "cache.clear()" in func.text
        assert func.metadata["start_line"] == 1
        assert func.metadata["end_line"] == 8
        assert uncovered_function_body_lines(text, docs) == []

    def test_nested_ifdef_and_single_branch(self, tmp_path):
        nested = """#ifdef OUTER
#ifdef INNER
bool Widget::open(int first, int second)
#else
bool Widget::open(int first)
#endif
#else
bool Widget::open()
#endif
{
    return ready;
}
"""
        docs = _docs(tmp_path, "widget.cpp", nested)
        func = _one(docs, "cpp_function", "open")
        assert func.metadata["class_name"] == "Widget"
        assert "#ifdef OUTER" in func.text
        assert "#ifdef INNER" in func.text
        assert "int second" in func.text
        assert "return ready" in func.text
        assert func.metadata["start_line"] == 1
        assert func.metadata["end_line"] == 12
        assert uncovered_function_body_lines(nested, docs) == []

        single = """#ifdef FEATURE_X
void Widget::close(int mode)
#endif
{
    open = false;
}
"""
        docs = _docs(tmp_path, "close.cpp", single)
        func = _one(docs, "cpp_function", "close")
        assert "open = false" in func.text
        assert "int mode" in func.text
        assert uncovered_function_body_lines(single, docs) == []

    def test_inline_method_in_class_keeps_neighbor_methods(self, tmp_path):
        text = """class Widget {
public:
    void reset() { stored = 0; }
#ifdef FEATURE_X
    bool configure(const Options &opts, int mode)
#else
    bool configure(const Options &opts)
#endif
    {
        return opts.valid;
    }
    int count() const { return stored; }
};
"""
        docs = _docs(tmp_path, "widget.h", text)
        summary = _by_type(docs, "class_summary")[0].text
        assert "bool configure(const Options &opts, int mode)" in summary
        assert "bool configure(const Options &opts)" in summary
        assert "return opts.valid" not in summary
        assert "#endif" not in summary
        assert "void reset()" in summary
        assert "int count() const" in summary
        configure = _one(docs, "cpp_function", "configure")
        assert configure.metadata["class_name"] == "Widget"
        assert "#ifdef FEATURE_X" in configure.text
        assert "int mode" in configure.text
        assert "return opts.valid" in configure.text
        assert "return stored" not in configure.text
        assert configure.metadata["start_line"] == 4
        assert configure.metadata["end_line"] == 11
        reset = _one(docs, "cpp_function", "reset")
        assert "stored = 0" in reset.text
        count = _one(docs, "cpp_function", "count")
        assert "return stored" in count.text
        assert uncovered_function_body_lines(text, docs, suffix=".h") == []

    def test_comment_branch_and_blank_line_before_body(self, tmp_path):
        text = """#ifdef FEATURE_X
// bool Widget::configure(const Options &opts, int mode)
#else
bool Widget::configure(const Options &opts)
#endif

{
    return opts.valid;
}
"""
        docs = _docs(tmp_path, "widget.cpp", text)
        func = _one(docs, "cpp_function", "configure")
        assert func.metadata["class_name"] == "Widget"
        assert "#ifdef FEATURE_X" in func.text
        assert "const Options &opts)" in func.text
        assert "return opts.valid" in func.text
        assert func.metadata["start_line"] == 1
        assert func.metadata["end_line"] == 9
        assert uncovered_function_body_lines(text, docs) == []

    def test_return_type_only_is_part_of_the_function(self, tmp_path):
        text = """#ifdef WIDE
long
#else
int
#endif
Cache::insert(const Key &key, const Value &value)
{
    table[key] = value;
    return 1;
}
"""
        docs = _docs(tmp_path, "cache.cpp", text)
        func = _one(docs, "cpp_function", "insert")
        assert func.metadata["class_name"] == "Cache"
        assert "#ifdef WIDE" in func.text
        assert "\nlong\n" in func.text or func.text.startswith("#ifdef WIDE\nlong\n")
        assert "table[key] = value" in func.text
        assert "return 1" in func.text
        assert func.metadata["start_line"] == 1
        assert func.metadata["end_line"] == 10
        assert uncovered_function_body_lines(text, docs) == []

    def test_c_file_and_extern_c(self, tmp_path):
        c_text = """#ifdef LEGACY
void reset_cache(int flags)
#else
void reset_cache(void)
#endif
{
    ready = flags;
}
"""
        docs = _docs(tmp_path, "cache.c", c_text)
        func = _one(docs, "cpp_function", "reset_cache")
        assert "ready = flags" in func.text
        assert "int flags" in func.text
        assert uncovered_function_body_lines(c_text, docs, suffix=".c") == []

        wrapped = """extern "C" {
#ifdef FEATURE_X
void reset_cache(int flags)
#else
void reset_cache(void)
#endif
{
    ready = flags;
}
}
"""
        docs = _docs(tmp_path, "cache.cpp", wrapped)
        func = _one(docs, "cpp_function", "reset_cache")
        assert "ready = flags" in func.text
        assert "#ifdef FEATURE_X" in func.text
        assert uncovered_function_body_lines(wrapped, docs) == []

    def test_whole_function_inside_ifdef_is_unchanged(self, tmp_path):
        text = """#ifdef FEATURE_X
bool Widget::configure(const Options &opts)
{
    return opts.valid;
}
#endif
void Widget::close()
{
    open = false;
}
"""
        docs = _docs(tmp_path, "widget.cpp", text)
        configure = _one(docs, "cpp_function", "configure")
        close = _one(docs, "cpp_function", "close")
        assert "#ifdef" not in configure.text
        assert "return opts.valid" in configure.text
        assert configure.metadata["start_line"] == 2
        assert configure.metadata["end_line"] == 5
        assert "open = false" in close.text
        assert close.metadata["start_line"] == 7
        assert uncovered_function_body_lines(text, docs) == []

    def test_conditional_declaration_does_not_steal_a_later_block(self, tmp_path):
        text = """#ifdef FEATURE_X
void helper(int value);
#endif
{
    int local = value;
}
void Widget::close()
{
    open = false;
}
"""
        docs = _docs(tmp_path, "widget.cpp", text)
        groups = _by_type(docs, "declaration_group")
        assert len(groups) == 1
        assert "void helper(int value);" in groups[0].text
        assert _by_type(docs, "cpp_function")
        close = _one(docs, "cpp_function", "close")
        assert "open = false" in close.text
        assert "int local" not in close.text
        assert uncovered_function_body_lines(text, docs) == []

    def test_constructor_without_return_type(self, tmp_path):
        source = """#ifdef FEATURE_X
Widget::Widget(const Options &opts, int mode)
#else
Widget::Widget(const Options &opts)
#endif
{
    ready = true;
}
"""
        docs = _docs(tmp_path, "widget.cpp", source)
        func = _one(docs, "cpp_function", "Widget")
        assert func.metadata["class_name"] == "Widget"
        assert func.metadata["start_line"] == 1
        assert func.metadata["end_line"] == 8
        assert "#ifdef FEATURE_X" in func.text
        assert "int mode" in func.text
        assert "ready = true" in func.text
        assert uncovered_function_body_lines(source, docs) == []
        assert _by_type(docs, "declaration_group") == []

    def test_inline_constructor_keeps_neighbor(self, tmp_path):
        source = """class Widget {
public:
#ifdef FEATURE_X
    Widget(int mode)
#else
    Widget()
#endif
    { ready = mode; }
    void reset() { ready = false; }
};
"""
        docs = _docs(tmp_path, "widget.h", source)
        func = _one(docs, "cpp_function", "Widget")
        assert func.metadata["class_name"] == "Widget"
        assert "#ifdef FEATURE_X" in func.text
        assert "ready = mode" in func.text
        assert "ready = false" not in func.text
        reset = _one(docs, "cpp_function", "reset")
        assert "ready = false" in reset.text
        summary = _one(docs, "class_summary", "Widget")
        assert "ready = mode" not in summary.text
        assert uncovered_function_body_lines(source, docs, ".h") == []

    def test_normal_file_and_include_guard_stay_identical(self, tmp_path):
        guard = _docs(tmp_path, "guard.cpp", _GUARD_CPP)
        normal = _docs(tmp_path, "normal.cpp", _NORMAL_CPP)
        assert _core(guard) == _GUARD_CHUNKS
        assert _core(normal) == _NORMAL_CHUNKS
        assert uncovered_function_body_lines(_NORMAL_CPP, normal) == []
        assert uncovered_function_body_lines(_GUARD_CPP, guard) == []


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
