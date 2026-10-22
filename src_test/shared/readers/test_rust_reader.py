# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""
Tests for shared/readers/rust_reader.py - Rust reader with Tree-sitter AST.

Covers: registry wiring, ``// File / // Module / // Class`` prefix, struct and
enum summaries listing the methods of every impl in the same file, traits,
impls of foreign types and blanket impls, constructors, generics, lifetimes,
async functions, closures, nested modules, attributes and cfg, doc comments,
macros (definitions, item-level calls, call groups), extern blocks, symbols
and the symbol policy, unicode, empty and broken files, and the rerank
profile.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

import shared.reranker as rr
from shared import symbol_policy as sp
from shared.readers import READER_REGISTRY, get_reader
from shared.readers.rust_reader import RERANK_PROFILE, RustFileReader
from shared.symbol_policy import SymbolPolicy

SAMPLE = """//! Shapes and pairs used by the drawing code in this example crate.
use std::fmt::{self, Display};
extern crate alloc;
mod ext;

/// A pair of values.
#[derive(Debug, Clone)]
pub struct Pair<'a, T: Clone> {
    pub left: &'a T,
    right: u32,
}

pub enum Shape { Circle(f64), Rect { w: f64, h: f64 }, Empty }

/// Things that can be drawn.
pub trait Draw<T>: Display where T: Copy {
    const SIDES: u8;
    type Out;
    fn draw(&self) -> T;
    fn name(&self) -> String {
        String::from("draw")
    }
}

impl<'a, T: Clone> Pair<'a, T> {
    /// Make a pair.
    pub fn new(left: &'a T) -> Self { Pair { left, right: 0 } }
    pub async fn run(&mut self) -> Result<(), String> {
        let add = |a: u32| a + 1;
        self.right = add(self.right);
        Ok(())
    }
}

impl fmt::Display for Shape {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "shape") }
}

impl<T: Display> Draw<u8> for Vec<T> {
    const SIDES: u8 = 0;
    type Out = ();
    fn draw(&self) -> u8 { 1 }
}

impl<T: Display + Copy> Draw<T> for T {
    const SIDES: u8 = 1;
    type Out = T;
    fn draw(&self) -> T { *self }
}

pub type Bytes = Vec<u8>;
pub const MAX_LEN: usize = 64;
static mut COUNTER: i32 = 0;

macro_rules! square { ($x:expr) => { $x * $x }; }

thread_local! { static DEPTH: std::cell::Cell<u32> = std::cell::Cell::new(0); }

extern "C" { fn abs(x: i32) -> i32; fn labs(x: i64) -> i64; }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn makes_pair() {
        let p = Pair::new(&1);
        assert_eq!(p.right, 0);
    }

    mod inner {
        pub fn deep_helper_function() -> u32 { 42 }
    }
}

/// Grüße: unicode docs ✓
pub fn grüße(name: &str) -> String { format!("Hallo {name}") }
"""


def _write(tmp_path: Path, text: str, name: str = "lib.rs") -> Path:
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return f


def _docs(tmp_path: Path, text: str = SAMPLE, name: str = "lib.rs"):
    return RustFileReader().load_data(_write(tmp_path, text, name))


def _find(docs, node_type, **meta):
    out = []
    for d in docs:
        if d.metadata["node_type"] != node_type:
            continue
        if all(d.metadata.get(k) == v for k, v in meta.items()):
            out.append(d)
    return out


def _one(docs, node_type, **meta):
    found = _find(docs, node_type, **meta)
    assert len(found) == 1, (node_type, meta, [d.metadata for d in docs if d.metadata["node_type"] == node_type])
    return found[0]


@pytest.fixture(autouse=True)
def _reset_policy():
    before = sp.get_symbol_policy()
    yield
    sp.set_symbol_policy(before)


# ── registry ─────────────────────────────────────────────────────


def test_registered_for_rs_only():
    assert isinstance(READER_REGISTRY[".rs"], RustFileReader)
    assert isinstance(get_reader(Path("src/main.RS")), RustFileReader)
    assert ".rlib" not in READER_REGISTRY


def test_profile_selected_only_when_rs_is_configured():
    def names(*exts):
        cfg = SimpleNamespace(SOURCE_DIRS=[{"path": "/src", "extensions": list(exts)}])
        return rr.rerank_profiles_for_config(cfg).names

    assert names(".rs") == ("rust",)
    assert "rust" not in names(".go", ".py")
    assert names(".go") == ("go",)


# ── types and impls ──────────────────────────────────────────────


def test_struct_summary_lists_impl_methods(tmp_path):
    d = _one(_docs(tmp_path), "class_summary", class_name="Pair")
    assert d.text.startswith("// File: lib.rs\n// Class: pub struct Pair<'a, T: Clone>\n/// A pair of values.")
    assert "#[derive(Debug, Clone)]" in d.text
    assert "// Methods of Pair in lib.rs:" in d.text
    assert "impl<'a, T: Clone> Pair<'a, T> {" in d.text
    assert "    pub fn new(left: &'a T) -> Self" in d.text
    assert "    pub async fn run(&mut self) -> Result<(), String>" in d.text
    assert "let add" not in d.text  # signatures only
    assert d.metadata["object_name"] == "Pair"
    assert d.metadata["symbols"] == ["Pair", "new", "run"]
    assert d.metadata["rust_kind"] == "struct"
    assert d.metadata["start_line"] == 6  # starts at the doc comment


def test_enum_summary_has_variants_and_trait_impls(tmp_path):
    d = _one(_docs(tmp_path), "class_summary", class_name="Shape")
    assert "impl fmt::Display for Shape {" in d.text
    assert d.metadata["symbols"] == ["Shape", "Circle", "Rect", "Empty", "fmt"]
    m = _one(_docs(tmp_path), "method_declaration", function_name="fmt")
    assert m.metadata["class_name"] == "Shape"
    assert m.metadata["impl_trait"] == "Display"
    assert "// Class: impl fmt::Display for Shape" in m.text


def test_trait_summary_and_default_method(tmp_path):
    docs = _docs(tmp_path)
    d = _one(docs, "class_summary", class_name="Draw")
    assert "pub trait Draw<T>: Display where T: Copy {" in d.text
    for sig in ("const SIDES: u8", "type Out", "fn draw(&self) -> T", "fn name(&self) -> String"):
        assert f"    {sig}\n" in d.text
    assert "String::from" not in d.text
    m = _one(docs, "method_declaration", function_name="name")
    assert m.metadata["class_name"] == "Draw"
    assert "String::from" in m.text
    # A required method has no body chunk of its own; the only draw() chunk
    # of class Draw is the blanket impl's.
    draws = _find(docs, "method_declaration", function_name="draw", class_name="Draw")
    assert [d.metadata.get("impl_trait") for d in draws] == ["Draw"]


def test_impl_of_foreign_type_gets_its_own_summary(tmp_path):
    docs = _docs(tmp_path)
    d = _one(docs, "class_summary", class_name="Vec")
    assert d.metadata["rust_kind"] == "impl"
    assert d.metadata["impl_trait"] == "Draw"
    assert "impl<T: Display> Draw<u8> for Vec<T> {" in d.text
    assert _one(docs, "constant_declaration", class_name="Vec").metadata["object_name"] == "SIDES"
    assert _one(docs, "type_alias_declaration", class_name="Vec").metadata["object_name"] == "Out"


def test_blanket_impl_is_attached_to_the_trait(tmp_path):
    d = _one(_docs(tmp_path), "class_summary", class_name="Draw")
    assert "// Impls of Draw in lib.rs:" in d.text
    assert "impl<T: Display + Copy> Draw<T> for T {" in d.text


def test_constructor_and_async(tmp_path):
    docs = _docs(tmp_path)
    c = _one(docs, "constructor_declaration")
    assert c.metadata["function_name"] == "new" and c.metadata["class_name"] == "Pair"
    assert c.text.split("\n")[2] == "/// Make a pair."
    run = _one(docs, "method_declaration", function_name="run")
    assert run.metadata["is_async"] is True
    assert "is_async" not in c.metadata


def test_closures_do_not_make_chunks(tmp_path):
    docs = _docs(tmp_path)
    assert not [d for d in docs if d.metadata.get("function_name") == "add"]
    assert "let add = |a: u32| a + 1;" in _one(docs, "method_declaration", function_name="run").text


def test_trait_method_named_new_is_not_a_constructor(tmp_path):
    src = "struct A;\ntrait Make { fn new() -> Self; }\nimpl Make for A {\n    fn new() -> Self { A }\n}\n"
    docs = _docs(tmp_path, src)
    assert not _find(docs, "constructor_declaration")
    assert _one(docs, "method_declaration", function_name="new").metadata["impl_trait"] == "Make"


def test_new_returning_other_type_is_not_a_constructor(tmp_path):
    src = "pub struct A;\nimpl A {\n    pub fn new_reader(path: &str) -> std::io::Result<File> { todo!() }\n}\n"
    assert not _find(_docs(tmp_path, src), "constructor_declaration")


def test_large_struct_gets_overview(tmp_path):
    fields = "\n".join(f"    /// Field number {i} with a fairly long description.\n    pub field_{i}: u64," for i in range(120))
    src = f"#[derive(Clone, Debug)]\npub struct Big {{\n{fields}\n}}\nimpl Default for Big {{ fn default() -> Self {{ todo!() }} }}\n"
    docs = _docs(tmp_path, src)
    ov = _one(docs, "class_overview", class_name="Big")
    assert "// Big is a Rust struct with 120 fields, 1 methods, 3 traits." in ov.text
    assert "traits: Clone, Debug, Default" in ov.text
    assert "symbols" not in ov.metadata
    assert _find(docs, "class_summary_split", class_name="Big")


# ── items ────────────────────────────────────────────────────────


def test_simple_items(tmp_path):
    docs = _docs(tmp_path)
    assert _one(docs, "type_alias_declaration", object_name="Bytes").metadata["rust_kind"] == "type"
    assert _one(docs, "constant_declaration", object_name="MAX_LEN").text.endswith("pub const MAX_LEN: usize = 64;")
    assert _one(docs, "field_declaration", object_name="COUNTER").metadata["rust_kind"] == "static"
    assert _one(docs, "macro_definition", object_name="square").metadata["rust_kind"] == "macro"


def test_imports_per_module(tmp_path):
    docs = _docs(tmp_path)
    top = [d for d in _find(docs, "import_group") if "module_path" not in d.metadata]
    assert len(top) == 1
    assert top[0].text == "// File: lib.rs\nuse std::fmt::{self, Display};\nextern crate alloc;\nmod ext;"
    inner = _one(docs, "import_group", module_path="tests")
    assert inner.text == "// File: lib.rs\n// Module: tests\nuse super::*;"


def test_macro_call_and_extern_block(tmp_path):
    docs = _docs(tmp_path)
    tl = _one(docs, "macro_invocation", macro_name="thread_local")
    assert tl.metadata["object_name"] == "DEPTH"
    ext = _one(docs, "extern_block")
    assert ext.metadata["symbols"] == ["abs", "labs"]
    assert "object_name" not in ext.metadata


def test_macro_call_runs_are_grouped(tmp_path):
    calls = "\n".join(f'matches!(match{i}, "a{i}", "a{i}");' for i in range(5))
    src = f"macro_rules! matches {{ ($n:ident, $a:expr, $b:expr) => {{}}; }}\n{calls}\nother!(solo, 1);\n"
    docs = _docs(tmp_path, src)
    g = _one(docs, "macro_group")
    assert g.metadata["group_count"] == 5
    assert g.metadata["symbols"] == [f"match{i}" for i in range(5)]
    assert "// Macro group: 5 calls of matches!" in g.text
    assert "object_name" not in g.metadata
    assert _one(docs, "macro_invocation", macro_name="other").metadata["object_name"] == "solo"


def test_long_macro_calls_stay_separate(tmp_path):
    body = "\n".join(f"    let x{i} = {i};" for i in range(10))
    one = f"rgtest!(case_{{n}}, |dir: Dir, mut cmd: TestCommand| {{\n{body}\n}});"
    src = "\n\n".join(one.replace("{n}", str(n)) for n in range(3)) + "\n"
    docs = _docs(tmp_path, src)
    assert not _find(docs, "macro_group")
    assert [d.metadata["object_name"] for d in _find(docs, "macro_invocation")] == ["case_0", "case_1", "case_2"]


# ── modules, attributes, comments ────────────────────────────────


def test_nested_modules_prefix_and_cfg(tmp_path):
    docs = _docs(tmp_path)
    t = _one(docs, "method_declaration", function_name="makes_pair")
    assert t.text.startswith("// File: lib.rs\n// Module: tests\n#[test]\nfn makes_pair()")
    assert t.metadata["module_path"] == "tests"
    assert t.metadata["cfg"] == "test"
    deep = _one(docs, "method_declaration", function_name="deep_helper_function")
    assert deep.metadata["module_path"] == "tests::inner"
    assert deep.metadata["cfg"] == "test"
    assert "// Module: tests::inner" in deep.text
    m = _one(docs, "module_summary", object_name="tests")
    assert m.metadata["cfg"] == "test"
    assert "#[cfg(test)]\nmod tests {" in m.text
    assert "    fn makes_pair()\n" in m.text and "    mod inner\n" in m.text
    assert m.metadata["symbols"] == ["tests", "makes_pair", "inner"]
    assert "cfg" not in _one(docs, "method_declaration", function_name="run").metadata


def test_cfg_values_combine(tmp_path):
    src = '#[cfg(unix)]\nmod sys {\n    #[cfg(target_os = "linux")]\n    pub fn page_size() -> usize { 4096 }\n}\n'
    d = _one(_docs(tmp_path, src), "method_declaration", function_name="page_size")
    assert d.metadata["cfg"] == 'unix && target_os = "linux"'


def test_module_doc_and_free_comments(tmp_path):
    docs = _docs(tmp_path)
    doc = _one(docs, "block_comment", rust_kind="module_doc")
    assert doc.text == "// File: lib.rs\n//! Shapes and pairs used by the drawing code in this example crate."
    assert doc.metadata["start_line"] == 1 and doc.metadata["end_line"] == 1


def test_comment_after_blank_line_is_not_a_doc_comment(tmp_path):
    src = "// A standalone note that explains the layout of this file in detail.\n\nfn f() -> u32 { 1 }\n"
    docs = _docs(tmp_path, src)
    c = _one(docs, "block_comment")
    assert c.metadata["end_line"] == 1
    assert "standalone" not in _one(docs, "method_declaration").text


def test_adjacent_comment_and_attributes_stay_with_item(tmp_path):
    src = "// Plain comment kept with the item below it.\n#[inline]\n#[must_use]\npub fn g() -> u8 { 2 }\n"
    docs = _docs(tmp_path, src)
    assert not _find(docs, "block_comment")
    d = _one(docs, "method_declaration")
    assert d.text == "// File: lib.rs\n// Plain comment kept with the item below it.\n#[inline]\n#[must_use]\npub fn g() -> u8 { 2 }"
    assert d.metadata["start_line"] == 1


def test_generics_lifetimes_and_where_clauses(tmp_path):
    src = (
        "pub struct Searcher<'s, M: Matcher + 's> { m: &'s M }\n"
        "impl<'s, M> Searcher<'s, M> where M: Matcher {\n"
        "    pub fn find<'b, I>(&self, hay: &'b [u8], it: I) -> Option<&'b [u8]> where I: Iterator<Item = u8> { None }\n"
        "}\n"
    )
    docs = _docs(tmp_path, src)
    s = _one(docs, "class_summary", class_name="Searcher")
    assert "impl<'s, M> Searcher<'s, M> where M: Matcher {" in s.text
    assert "pub fn find<'b, I>(&self, hay: &'b [u8], it: I) -> Option<&'b [u8]> where I: Iterator<Item = u8>" in s.text
    m = _one(docs, "method_declaration", function_name="find")
    assert m.metadata["class_name"] == "Searcher"


def test_scoped_and_reference_impl_types(tmp_path):
    src = "pub struct W;\nimpl<'a> std::io::Write for &'a mut W {\n    fn flush(&mut self) -> std::io::Result<()> { Ok(()) }\n}\n"
    docs = _docs(tmp_path, src)
    assert "impl<'a> std::io::Write for &'a mut W {" in _one(docs, "class_summary", class_name="W").text
    assert _one(docs, "method_declaration").metadata["impl_trait"] == "Write"


# ── grouping and symbols ─────────────────────────────────────────


TRIVIAL = """pub struct Opts { a: bool, b: bool, c: bool }
impl Opts {
    pub fn a(&self) -> bool { self.a }
    pub fn b(&self) -> bool { self.b }
    pub fn c(&self) -> bool { self.c }
}
"""


def test_trivial_methods_grouped_with_symbols(tmp_path):
    docs = _docs(tmp_path, TRIVIAL)
    g = _one(docs, "method_group")
    assert g.metadata["class_name"] == "Opts"
    assert g.metadata["symbols"] == ["a", "b", "c"]
    assert "object_name" not in g.metadata and "function_name" not in g.metadata


def test_symbols_per_split_part(tmp_path):
    methods = "\n".join(
        f"    /// Method {i} documentation line that is long enough to add text.\n"
        f"    pub fn method_{i}(&self, value: u64) -> u64 {{ value + {i} }}"
        for i in range(150)
    )
    src = f"pub struct Wide {{ x: u64 }}\nimpl Wide {{\n{methods}\n}}\n"
    default = _find(_docs(tmp_path, src), "class_summary_split", class_name="Wide")
    assert len(default) > 1
    full = default[0].metadata["symbols"]
    assert all(d.metadata["symbols"] == full for d in default)

    sp.set_symbol_policy(SymbolPolicy(per_split_part=True))
    parts = _find(_docs(tmp_path, src), "class_summary_split", class_name="Wide")
    assert len(parts) == len(default)
    for d in parts:
        assert d.metadata["symbols"]
        assert all(s in d.text for s in d.metadata["symbols"])
    assert len(parts[-1].metadata["symbols"]) < len(full)

    sp.set_symbol_policy(SymbolPolicy(max_per_chunk=3))
    capped = _find(_docs(tmp_path, src), "class_summary_split", class_name="Wide")
    assert all(len(d.metadata["symbols"]) == 3 and d.metadata["symbols_truncated"] for d in capped)


# ── edge cases ───────────────────────────────────────────────────


def test_unicode_identifiers_and_text(tmp_path):
    d = _one(_docs(tmp_path), "method_declaration", function_name="grüße")
    assert "/// Grüße: unicode docs ✓" in d.text
    assert d.metadata["object_name"] == "grüße"


def test_empty_and_whitespace_files(tmp_path):
    assert _docs(tmp_path, "") == []
    assert _docs(tmp_path, "  \n\t\n") == []


def test_comment_only_file_falls_back_to_full_file(tmp_path):
    docs = _docs(tmp_path, "// short\n")
    assert [d.metadata["node_type"] for d in docs] == ["full_file"]


def test_syntax_errors_keep_valid_items(tmp_path):
    src = "pub fn ok_one() -> u8 { 1 }\n\nfn broken( {\n\npub struct Still { a: u8 }\n\npub fn ok_two() -> u8 { 2 }\n"
    docs = _docs(tmp_path, src)
    names = {d.metadata.get("object_name") for d in docs}
    assert {"ok_one", "Still", "ok_two"} <= names


def test_garbage_falls_back_to_full_file(tmp_path):
    docs = _docs(tmp_path, "}}}} ))) ;;; not rust at all {{{{\n")
    assert [d.metadata["node_type"] for d in docs] == ["full_file"]
    assert docs[0].metadata["file_path"].endswith("lib.rs")


def test_crlf_line_endings(tmp_path):
    f = tmp_path / "crlf.rs"
    f.write_bytes(b"/// Doc line.\r\npub fn crlf() -> u8 {\r\n    1\r\n}\r\n")
    d = _one(RustFileReader().load_data(f), "method_declaration")
    assert d.metadata["start_line"] == 1 and d.metadata["end_line"] == 4
    assert "/// Doc line." in d.text


def test_load_nodes_line_and_byte_ranges(tmp_path):
    f = _write(tmp_path, SAMPLE)
    raw = f.read_bytes()
    for d in RustFileReader().load_data(f):
        m = d.metadata
        if m["node_type"] in ("method_group", "macro_group", "full_file"):
            continue
        assert 1 <= m["start_line"] <= m["end_line"]
        assert 0 <= m["start_byte"] < m["end_byte"] <= len(raw)


# ── rerank profile ───────────────────────────────────────────────


def _declared(text, path="src/lib.rs", **meta):
    names, _ = rr.chunk_declared_names({"file_path": path, **meta}, text, rr.get_profile_set(None))
    return names


@pytest.mark.parametrize(
    "line, name",
    [
        ("pub const MAX_LEN: usize = 64;", "max_len"),
        ("pub(crate) static mut COUNTER: i32 = 0;", "counter"),
        ("macro_rules! square {", "square"),
        ("pub(super) mod walk {", "walk"),
        ("pub async fn search_path<P: AsRef<Path>>(&self, p: P) {", "search_path"),
        ("pub unsafe trait Sink {", "sink"),
    ],
)
def test_declared_names(line, name):
    assert name in _declared(f"// File: lib.rs\n#[inline]\n{line}")


def test_profile_patterns_scoped_to_rs_files():
    assert "max_len" not in _declared("const MAX_LEN: usize = 64;", path="src/a.go")


def test_test_and_binding_paths():
    ps = rr.get_profile_set(None)
    assert rr._is_test_path("benches/search.rs", ps.profile_for_path("benches/search.rs"))
    assert rr._is_test_path("crates/x/src/tests.rs", RERANK_PROFILE)
    assert rr._is_test_path("crates/x/src/walk_test.rs", RERANK_PROFILE)
    assert not rr._is_test_path("crates/x/src/walk.rs", RERANK_PROFILE)
    assert rr._is_binding_chunk("crates/pcre2-sys/src/lib.rs", "", RERANK_PROFILE)
    assert not rr._is_binding_chunk("crates/pcre2/src/lib.rs", "", RERANK_PROFILE)


def test_file_stem_target():
    cfg = SimpleNamespace(SOURCE_DIRS=[{"path": "/src", "extensions": [".rs"]}])
    ps = rr.rerank_profiles_for_config(cfg)
    assert "walk" in rr.extract_target_identifiers("What does walk.rs do?", ps)
