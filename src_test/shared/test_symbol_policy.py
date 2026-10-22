# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""SYMBOLS_PER_SPLIT_PART and SYMBOLS_MAX_PER_CHUNK.

The defaults must give byte-identical payloads to earlier versions (every
split part inherits the full ``symbols`` list). Opting in narrows each split
part to the names in its own text and/or caps the list length.
"""

from __future__ import annotations

import json
import types

import pytest

from shared import symbol_policy as sp
from shared.readers.cpp_reader import CppFileReader
from shared.symbol_policy import (
    SymbolMatcher,
    SymbolPolicy,
    apply_symbol_policy,
    configure_symbol_policy,
    policy_from_config,
    symbols_in_text,
)


@pytest.fixture(autouse=True)
def _reset_policy():
    before = sp.get_symbol_policy()
    yield
    sp.set_symbol_policy(before)


# ── pure helpers ───────────────────────────────────────────────────


class TestPolicyFromConfig:
    def test_defaults(self):
        pol = policy_from_config(types.SimpleNamespace())
        assert pol == SymbolPolicy(False, 0) and pol.is_default

    @pytest.mark.parametrize(
        "flag,cap,expected",
        [
            (True, 0, SymbolPolicy(True, 0)),
            ("true", "5", SymbolPolicy(True, 5)),
            ("off", -3, SymbolPolicy(False, 0)),
            (0, "bad", SymbolPolicy(False, 0)),
            (False, True, SymbolPolicy(False, 0)),
            (1, 2.7, SymbolPolicy(True, 2)),
        ],
    )
    def test_parsing(self, flag, cap, expected):
        cfg = types.SimpleNamespace(SYMBOLS_PER_SPLIT_PART=flag, SYMBOLS_MAX_PER_CHUNK=cap)
        assert policy_from_config(cfg) == expected

    def test_configure_sets_process_policy(self):
        configure_symbol_policy(types.SimpleNamespace(SYMBOLS_PER_SPLIT_PART=True))
        assert sp.get_symbol_policy().per_split_part is True
        configure_symbol_policy(types.SimpleNamespace())
        assert sp.get_symbol_policy().is_default


class TestSymbolsInText:
    def test_whole_identifier_tokens_only(self):
        assert symbols_in_text(["FOO", "FOO_BAR", "BAR"], "x FOO_BAR y") == ["FOO_BAR"]

    def test_keeps_list_order_and_duplicates(self):
        assert symbols_in_text(["B", "A", "B"], "A B") == ["B", "A", "B"]

    def test_non_identifier_symbols(self):
        text = "void ns::run(); operator+ x"
        assert symbols_in_text(["ns::run", "ns::stop", "operator+"], text) == [
            "ns::run",
            "operator+",
        ]
        assert symbols_in_text(["s::run"], text) == []  # glued to "n"

    def test_anchor_keeps_derived_alias(self):
        got = symbols_in_text(
            ["read", "sys_read", "sys_write"], "SYSCALL_DEFINE3(read, ...)",
            anchors={"sys_read": "read", "sys_write": "write"},
        )
        assert got == ["read", "sys_read"]

    def test_empty_inputs(self):
        assert symbols_in_text([], "A") == []
        assert symbols_in_text(["A", ""], "") == []

    def test_matcher_reused_for_many_parts(self):
        m = SymbolMatcher([f"R{i}" for i in range(1000)])
        assert m.kept("R5 R999 R1000") == ["R5", "R999"]
        assert m.kept("nothing") == []


class TestApplySymbolPolicy:
    META = {"file_path": "a.h", "symbols": ["A", "B", "C"], "node_type": "x_split"}

    def test_default_returns_same_object(self):
        meta = dict(self.META)
        assert apply_symbol_policy(meta, "A", policy=SymbolPolicy()) is meta
        assert apply_symbol_policy(meta, None) is meta  # process default

    def test_no_symbols_is_untouched(self):
        meta = {"file_path": "a.h"}
        assert apply_symbol_policy(meta, "A", policy=SymbolPolicy(True, 1)) is meta
        odd = {"symbols": "A,B"}  # not a list: left alone
        assert apply_symbol_policy(odd, "A", policy=SymbolPolicy(True, 1)) is odd

    def test_per_part_narrows_and_never_mutates(self):
        meta = dict(self.META)
        out = apply_symbol_policy(meta, "B and C", policy=SymbolPolicy(True, 0))
        assert out["symbols"] == ["B", "C"] and "symbols_truncated" not in out
        assert meta == self.META

    def test_per_part_without_part_text_is_unsplit_chunk(self):
        meta = dict(self.META)
        assert apply_symbol_policy(meta, None, policy=SymbolPolicy(True, 0)) is meta

    def test_part_without_symbols_drops_key(self):
        out = apply_symbol_policy(dict(self.META), "zzz", policy=SymbolPolicy(True, 0))
        assert "symbols" not in out and "symbols_truncated" not in out

    @pytest.mark.parametrize(
        "cap,expected,truncated",
        [(0, ["A", "B", "C"], False), (1, ["A"], True), (2, ["A", "B"], True),
         (3, ["A", "B", "C"], False), (10, ["A", "B", "C"], False)],
    )
    def test_cap(self, cap, expected, truncated):
        meta = dict(self.META)
        out = apply_symbol_policy(meta, None, policy=SymbolPolicy(False, cap))
        assert out["symbols"] == expected
        assert out.get("symbols_truncated", False) is truncated
        if not truncated:
            assert out is meta

    def test_cap_after_per_part(self):
        out = apply_symbol_policy(
            {"symbols": ["A", "B", "C", "D"]}, "D C B", policy=SymbolPolicy(True, 2)
        )
        assert out == {"symbols": ["B", "C"], "symbols_truncated": True}


# ── readers ────────────────────────────────────────────────────────


def _header(n: int) -> str:
    lines = ["/* generated register map */", "#ifndef REGS_H", "#define REGS_H", ""]
    lines += [f"#define BLOCK_REG_{i:05d}_OFFSET 0x{i * 4:08X}" for i in range(n)]
    lines += ["", "#endif"]
    return "\n".join(lines) + "\n"


def _cpp_docs(tmp_path, text, name="regs.h"):
    # Write once: the metadata carries the file timestamps.
    path = tmp_path / name
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")
    return CppFileReader().load_data(path)


_TIMES = ("creation_datetime", "modification_datetime")


def _dump(docs):
    # File timestamps can differ between two reads on some file systems.
    return [
        json.dumps(
            {"t": d.text, "m": {k: v for k, v in d.metadata.items() if k not in _TIMES}},
            sort_keys=True,
        )
        for d in docs
    ]


class TestCppReader:
    def test_default_split_parts_inherit_full_list_like_before(self, tmp_path):
        docs = _cpp_docs(tmp_path, _header(3000))
        parts = [d for d in docs if d.metadata.get("node_type", "").endswith("_split")]
        assert len(parts) > 3
        full = parts[0].metadata["symbols"]
        assert len(full) >= 3000
        assert all(p.metadata["symbols"] == full for p in parts)
        assert not any("symbols_truncated" in d.metadata for d in docs)

    def test_explicit_default_is_byte_identical(self, tmp_path):
        text = _header(3000)
        before = _dump(_cpp_docs(tmp_path, text))
        sp.set_symbol_policy(SymbolPolicy(False, 0))
        assert _dump(_cpp_docs(tmp_path, text)) == before

    def test_per_part_keeps_only_names_in_the_part(self, tmp_path):
        text = _header(3000)
        default_docs = _cpp_docs(tmp_path, text)
        sp.set_symbol_policy(SymbolPolicy(True, 0))
        docs = _cpp_docs(tmp_path, text)
        assert [d.text for d in docs] == [d.text for d in default_docs]  # same chunks
        parts = [d for d in docs if d.metadata.get("node_type", "").endswith("_split")]
        full = next(d for d in default_docs if d.metadata.get("symbols")).metadata["symbols"]
        union = set()
        for p in parts:
            syms = p.metadata.get("symbols", [])
            assert 0 < len(syms) < len(full)
            for s in syms:
                assert s in p.text
            union.update(syms)
        assert union == set(full)  # every defined name is still findable
        total = sum(len(p.metadata.get("symbols", [])) for p in parts)
        assert total < 2 * len(full)  # only the overlap repeats names

    def test_per_part_does_not_change_other_metadata(self, tmp_path):
        text = _header(2000)
        a = _cpp_docs(tmp_path, text)
        sp.set_symbol_policy(SymbolPolicy(True, 0))
        b = _cpp_docs(tmp_path, text)
        for x, y in zip(a, b):
            skip = ("symbols",) + _TIMES
            mx = {k: v for k, v in x.metadata.items() if k not in skip}
            my = {k: v for k, v in y.metadata.items() if k not in skip}
            assert mx == my

    def test_small_group_unsplit_unchanged_with_per_part(self, tmp_path):
        text = "#define QF_A 1\n#define QF_B 2\n#define QF_C 3\n"
        before = _dump(_cpp_docs(tmp_path, text))
        sp.set_symbol_policy(SymbolPolicy(True, 0))
        assert _dump(_cpp_docs(tmp_path, text)) == before

    @pytest.mark.parametrize("cap", [1, 2, 50])
    def test_cap_marks_truncated(self, tmp_path, cap):
        sp.set_symbol_policy(SymbolPolicy(False, cap))
        docs = _cpp_docs(tmp_path, "#define QF_A 1\n#define QF_B 2\n#define QF_C 3\n")
        group = next(d for d in docs if d.metadata.get("symbols"))
        expected = ["QF_A", "QF_B", "QF_C"][:cap]
        assert group.metadata["symbols"] == expected
        assert group.metadata.get("symbols_truncated", False) is (cap < 3)

    def test_syscall_alias_survives_per_part(self, tmp_path):
        body = "\n".join(f"\tx += {i};" for i in range(3000))
        text = f"SYSCALL_DEFINE3(read, unsigned int, fd, char *, buf, size_t, count)\n{{\n{body}\n}}\n"
        sp.set_symbol_policy(SymbolPolicy(True, 0))
        docs = _cpp_docs(tmp_path, text, name="rw.c")
        parts = [d for d in docs if d.metadata.get("node_type", "").endswith("_split")]
        assert len(parts) > 1
        assert parts[0].metadata["symbols"] == ["read", "sys_read"]
        # later parts don't mention "read": no symbols, object_name still set
        assert "symbols" not in parts[-1].metadata
        assert parts[-1].metadata.get("object_name") == "read"


class TestStructuredReader:
    def test_structured_split_applies_same_policy(self):
        from shared.readers._structured import RawChunk, StructuredReaderBase

        class _Reader(StructuredReaderBase):
            def load_data(self, file, extra_info=None):  # pragma: no cover
                return []

        reader = _Reader()
        names = [f"NAME_{i:05d}" for i in range(3000)]
        text = "\n".join(f"{n} = {i}" for i, n in enumerate(names))
        chunk = RawChunk(
            text=text, node_type="group", start_line=1, end_line=3000,
            start_byte=0, end_byte=len(text), extra={"symbols": names},
        )
        default = reader.make_documents(chunk, "f.x", {}, {})
        assert len(default) > 1 and all(d.metadata["symbols"] == names for d in default)
        sp.set_symbol_policy(SymbolPolicy(True, 0))
        narrowed = reader.make_documents(chunk, "f.x", {}, {})
        assert [d.text for d in narrowed] == [d.text for d in default]
        for d in narrowed:
            assert 0 < len(d.metadata["symbols"]) < len(names)
        sp.set_symbol_policy(SymbolPolicy(False, 5))
        capped = reader.make_documents(chunk, "f.x", {}, {})
        assert all(d.metadata["symbols"] == names[:5] for d in capped)
        assert all(d.metadata["symbols_truncated"] is True for d in capped)
