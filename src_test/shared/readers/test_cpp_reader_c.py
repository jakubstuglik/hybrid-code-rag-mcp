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


def _plain(docs):
    return [d for d in docs if d.metadata["node_type"] == "cpp_function"]


def _reader():
    r = CppFileReader()
    r.MIN_TRIVIAL_RUN = 10**6  # keep one chunk per function
    return r


def _docs1(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return _reader().load_data(path)


def test_swallowing_body_is_cut_at_column0_brace(tmp_path):
    # The macro calls inside the switch make the grammar miss the body's
    # closing brace; without the cut the first function swallows the rest.
    src = (
        "const char *cmd_name(int cmd)\n{\n"
        "#define N(val) case CMD_##val: return #val;\n"
        "\tswitch (cmd) {\n\tN(UP) N(DOWN)\n\tN(MOVE)\n\t}\n#undef N\n"
        "\treturn \"UNKNOWN\";\n}\nEXPORT_SYMBOL(cmd_name);\n\n"
        "static int notify(int val)\n{\n\tint ret = 0;\n\tret += val;\n\treturn ret;\n}\n\n"
        "int receive_one(void *pkt)\n{\n\tif (!pkt)\n\t\treturn -1;\n\treturn notify(1);\n}\n"
    )
    docs = _docs1(tmp_path, "cmd.c", src)
    names = [d.metadata.get("object_name") for d in _plain(docs)]
    assert names == ["cmd_name", "notify", "receive_one"]
    (first,) = _by_name(docs, "cmd_name")
    assert "receive_one" not in first.text and "notify(int val)" not in first.text
    (last,) = _by_name(docs, "receive_one")
    assert last.metadata["start_line"] == src.splitlines().index("int receive_one(void *pkt)") + 1
    raw = src.encode()
    assert raw[last.metadata["start_byte"]:last.metadata["end_byte"]].decode().startswith("int receive_one")


def test_clean_function_is_not_cut(tmp_path):
    src = "int f(int a)\n{\n\tif (a) {\n\t\ta++;\n\t}\n\treturn a;\n}\n"
    (doc,) = _plain(_docs1(tmp_path, "f.c", src))
    assert doc.metadata["object_name"] == "f" and doc.metadata["end_line"] == 7


def test_single_argument_macro_function_is_named(tmp_path):
    src = (
        "SYSCALL_DEFINE0(getpid)\n{\n\treturn current_pid();\n}\n\n"
        "DEFINE_IDTENTRY_ERRORCODE(exc_general_protection)\n{\n\thandle_gp(regs);\n}\n"
    )
    docs = _docs1(tmp_path, "sys.c", src)
    (getpid,) = _by_name(docs, "getpid")
    assert "sys_getpid" in getpid.metadata["symbols"]
    (gp,) = _by_name(docs, "exc_general_protection")
    assert "symbols" not in gp.metadata


def test_multi_argument_syscall_gets_sys_alias(tmp_path):
    src = "SYSCALL_DEFINE3(read, unsigned int, fd, char *, buf, size_t, count)\n{\n\treturn ksys_read(fd, buf, count);\n}\n"
    (doc,) = _by_name(_docs1(tmp_path, "rw.c", src), "read")
    assert doc.metadata["symbols"] == ["read", "sys_read"]


def test_attribute_macros_before_the_name(tmp_path):
    src = (
        "asmlinkage __visible void __softirq_entry __do_softirq(void)\n{\n\thandle_softirqs(false);\n}\n\n"
        "static void noinline __cold slow_path(int x)\n{\n\tx++;\n}\n\n"
        "static __u32 hash_it(__u32 v)\n{\n\treturn v * 3;\n}\n"
    )
    docs = _docs1(tmp_path, "softirq.c", src)
    (a,) = _by_name(docs, "__do_softirq")
    assert a.text.splitlines()[-4].startswith("asmlinkage __visible void")
    (b,) = _by_name(docs, "slow_path")
    assert "static void noinline __cold slow_path" in b.text
    assert _by_name(docs, "hash_it")


def test_function_returning_function_pointer_is_named(tmp_path):
    src = "void (*get_handler(int sig))(int)\n{\n\treturn handlers[sig];\n}\n"
    assert _by_name(_docs1(tmp_path, "h.c", src), "get_handler")
