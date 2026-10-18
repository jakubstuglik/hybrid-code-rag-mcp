"""C-specific chunking in shared/readers/cpp_reader.py: leading comments,
macro-defined functions, initialized tables, annotation lines, header
grammar choice and parse-error recovery."""

from shared.readers.cpp_reader import CppFileReader, _blank_annotation_lines


def _docs(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return CppFileReader().load_data(path)


def _by_name(docs, name):
    return [d for d in docs if d.metadata.get("object_name") == name]


def test_leading_doc_comment_is_attached(tmp_path):
    src = (
        "/* SPDX-License-Identifier: MIT */\n\n"
        "/**\n * pool_get - take an entry\n * @p: the pool\n */\n"
        "static int pool_get(struct pool *p)\n{\n\treturn p->n--;\n}\n"
    )
    (doc,) = _by_name(_docs(tmp_path, "pool.c", src), "pool_get")
    assert "pool_get - take an entry" in doc.text
    assert "SPDX" not in doc.text
    assert doc.text.index("pool_get - take") < doc.text.index("static int pool_get")
    assert doc.metadata["start_line"] == 3


def test_detached_or_trailing_comment_not_attached(tmp_path):
    src = (
        "/* about the file */\n\n\n"
        "int a(void)\n{\n\treturn 1;\n}\n"
        "int x; /* trailing note */\n"
        "int b(void)\n{\n\treturn 2;\n}\n"
    )
    docs = _docs(tmp_path, "m.c", src)
    text = "\n".join(d.text for d in docs)
    assert "about the file" not in text
    (b,) = [d for d in docs if "int b(void)" in d.text]
    assert "trailing note" not in b.text


def test_struct_and_enum_get_comment(tmp_path):
    src = (
        "/* A queue of items. */\nstruct queue {\n\tint head;\n\tint tail;\n};\n\n"
        "/* Queue states. */\nenum queue_state {\n\tQ_IDLE,\n\tQ_BUSY,\n};\n"
    )
    docs = _docs(tmp_path, "q.h", src)
    assert any("A queue of items." in d.text for d in _by_name(docs, "queue"))
    assert any("Queue states." in d.text for d in _by_name(docs, "queue_state"))


def test_macro_defined_function_is_chunked(tmp_path):
    src = (
        "SYSCALL_DEFINE2(truncate, const char *, path, long, length)\n{\n"
        "\treturn do_truncate(path, length);\n}\n\n"
        "TEST(Parser, Empty) {\n  ASSERT_TRUE(parse(\"\"));\n}\n"
    )
    docs = _docs(tmp_path, "open.c", src)
    (t,) = _by_name(docs, "truncate")
    assert t.metadata["node_type"] == "cpp_function"
    assert "return do_truncate" in t.text
    assert _by_name(docs, "Parser")


def test_initialized_table_is_chunked(tmp_path):
    src = (
        "/* file ops */\n"
        "const struct file_ops demo_fops = {\n\t.open = demo_open,\n\t.read = demo_read,\n};\n"
        "static int tiny[] = { 1, 2 };\n"
    )
    docs = _docs(tmp_path, "demo.c", src)
    (t,) = _by_name(docs, "demo_fops")
    assert t.metadata["node_type"] == "variable_definition"
    assert ".read = demo_read" in t.text and "file ops" in t.text
    assert not _by_name(docs, "tiny")


def test_annotation_lines_blanked_same_length():
    src = "void f(struct x *p)\n\t__releases(p->lock) /* note */\n\t__acquires(p->lock)\n{\n}\n"
    out = _blank_annotation_lines(src)
    assert len(out) == len(src) and out.count("\n") == src.count("\n")
    assert "__releases" not in out and "{" in out


def test_annotated_function_keeps_annotation_text(tmp_path):
    src = (
        "static void unlock_both(struct rq *a)\n"
        "\t__context_unsafe(/* releases */)\n"
        "\t__releases(a->lock)\n{\n\traw_unlock(a);\n}\n"
    )
    (doc,) = _by_name(_docs(tmp_path, "s.c", src), "unlock_both")
    assert "__releases(a->lock)" in doc.text


def test_macro_groups_list_symbols(tmp_path):
    src = "#define QF_A 1\n#define QF_B 2\n#define QF_C 4\n"
    docs = _docs(tmp_path, "flags.h", src)
    groups = [d for d in docs if d.metadata.get("symbols")]
    assert groups and groups[0].metadata["symbols"] == ["QF_A", "QF_B", "QF_C"]


def test_parse_error_region_is_recovered(tmp_path):
    # an unknown loop macro breaks the grammar for the rest of the function
    broken = (
        "long broken(struct w *w)\n{\n\tdo {\n\t\tstep(w);\n\t} while_each(w, t);\n"
        + "".join(f"\tstep{i}(w);\n" for i in range(30))
        + "\treturn 0;\n}\n\n"
    )
    after = "".join(
        f"int after_{i}(int v)\n{{\n\treturn v + {i};\n}}\n\n" for i in range(5)
    )
    docs = _docs(tmp_path, "w.c", broken + after)
    names = {n for d in docs for n in (d.metadata.get("object_name") or "").split(", ")}
    for i in range(5):
        assert f"after_{i}" in names, i
