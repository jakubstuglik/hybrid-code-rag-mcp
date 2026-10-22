# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""``find_source_files``: one directory walk, same files and order as rglob.

The reference below is the classic scan (one ``rglob`` per extension,
``is_excluded`` and ``is_file`` per hit) that ``find_source_files``
replaces. Every test compares the full ordered lists, so a change in the
result set or in the order fails.
"""

from __future__ import annotations

import os
import random
from pathlib import Path

import pytest

from shared.manifest import _is_excluded_leaf, find_source_files, is_excluded


def _classic(dir_path: Path, extensions, exclude_patterns):
    out = []
    for ext in extensions:
        for f in Path(dir_path).rglob(f"*{ext}"):
            if is_excluded(f, exclude_patterns):
                continue
            try:
                if not f.is_file():
                    continue
            except Exception:
                continue
            out.append(f)
    return out


def _same(root, extensions, excludes):
    expected = _classic(root, extensions, excludes)
    got = find_source_files(root, extensions, excludes)
    assert [str(p) for p in got] == [str(p) for p in expected]
    assert all(isinstance(p, Path) for p in got)
    return got


def _touch(root: Path, rel: str, text: str = "x\n") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "repo"
    for rel in [
        "a.c",
        "a.h",
        "b.cpp",
        "notes.txt",
        "src/x.c",
        "src/x.h",
        "src/deep/one/two/y.c",
        "src/deep/one/two/y.hpp",
        "build/gen.c",
        "src/build/gen2.c",
        "node_modules/pkg/index.c",
        "drivers/gpu/amd/include/asic_reg/r.h",
        "drivers/gpu/amd/include/other/o.h",
        "drivers/net/asic_reg/keep.h",
        "web/app.min.js",
        "web/app.js",
        "web/types.d.ts",
        "web/index.ts",
        ".hidden/h.c",
        ".h",
        "weird name with spaces/z.c",
        "unicodé/ü.c",
    ]:
        _touch(root, rel)
    (root / "dir.h").mkdir()  # a directory whose name matches an extension
    (root / "dir.h" / "inner.h").write_text("x\n", encoding="utf-8")
    (root / "empty").mkdir()
    return root


class TestSameAsClassicScan:
    def test_no_excludes(self, tree):
        got = _same(tree, [".c", ".h", ".cpp", ".hpp"], [])
        assert len(got) > 10

    def test_single_segment_dir_excludes_are_pruned(self, tree):
        got = _same(tree, [".c", ".h"], ["build", "node_modules", ".hidden"])
        names = {p.name for p in got}
        assert "gen.c" not in names and "gen2.c" not in names
        assert "index.c" not in names and "h.c" not in names

    def test_multi_segment_pattern(self, tree):
        got = _same(tree, [".h"], ["gpu/amd/include/asic_reg"])
        assert "r.h" not in {p.name for p in got}
        assert "keep.h" in {p.name for p in got}
        assert "o.h" in {p.name for p in got}

    def test_multi_segment_pattern_with_wildcards(self, tree):
        got = _same(tree, [".h"], ["drivers/*/asic_reg", "*/amd/*"])
        names = {p.name for p in got}
        assert "keep.h" not in names and "r.h" not in names and "o.h" not in names

    def test_file_patterns(self, tree):
        got = _same(tree, [".js", ".ts"], ["*.min.js", "*.d.ts"])
        names = [p.name for p in got]
        assert names.count("app.js") == 1 and "app.min.js" not in names

    def test_backslash_pattern(self, tree):
        _same(tree, [".h"], ["gpu\\amd\\include\\asic_reg"])

    def test_overlapping_extensions_list_a_file_twice_like_rglob(self, tree):
        got = _same(tree, [".ts", ".d.ts"], [])
        assert [p.name for p in got].count("types.d.ts") == 2

    def test_extension_order_is_kept(self, tree):
        got = _same(tree, [".h", ".c"], [])
        groups = [0 if p.name.endswith(".h") else 1 for p in got]
        assert groups == sorted(groups) and 0 in groups and 1 in groups

    def test_dir_named_like_extension_is_descended_not_listed(self, tree):
        got = _same(tree, [".h"], [])
        assert tree / "dir.h" not in got
        assert tree / "dir.h" / "inner.h" in got

    def test_name_equal_to_extension_is_matched(self, tree):
        got = _same(tree, [".h"], [])
        assert tree / ".h" in got

    def test_mixed_case_extensions_follow_platform_rules(self, tmp_path):
        root = tmp_path / "case"
        for rel in ["UP.H", "low.h", "Mix.Cpp", "sub/K.C"]:
            _touch(root, rel)
        got = _same(root, [".h", ".cpp", ".c"], [])
        if os.path.normcase("Aa") == "Aa":  # POSIX: case-sensitive
            assert [p.name for p in got] == ["low.h"]
        else:  # Windows: case-insensitive, as rglob
            assert {p.name for p in got} == {"UP.H", "low.h", "Mix.Cpp", "K.C"}

    def test_missing_dir(self, tmp_path):
        assert find_source_files(tmp_path / "nope", [".c"], []) == []
        assert _classic(tmp_path / "nope", [".c"], []) == []

    def test_file_instead_of_dir(self, tmp_path):
        f = _touch(tmp_path, "single.c")
        assert find_source_files(f, [".c"], []) == _classic(f, [".c"], [])

    def test_empty_dir_and_empty_extensions(self, tree):
        assert find_source_files(tree / "empty", [".c"], []) == []
        assert find_source_files(tree, [], []) == []

    def test_root_itself_excluded(self, tree):
        got = _same(tree, [".c"], ["repo"])
        assert got == []

    def test_pattern_on_an_ancestor_of_root(self, tree):
        # The classic scan matches excludes against the full path, including
        # parts above the source dir; so does the walk.
        parent = tree.parent.name
        assert _same(tree / "src", [".c"], [parent]) == []
        assert _same(tree / "src", [".c"], [f"{parent}/repo/src"]) == []

    def test_accepts_str_path(self, tree):
        got = find_source_files(str(tree), [".c"], [])
        assert [str(p) for p in got] == [str(p) for p in _classic(tree, [".c"], [])]


def _symlinks_supported(tmp_path) -> bool:
    try:
        (tmp_path / "probe_target").write_text("x", encoding="utf-8")
        os.symlink(tmp_path / "probe_target", tmp_path / "probe_link")
        return True
    except (OSError, NotImplementedError):
        return False


class TestSymlinks:
    def test_symlink_semantics_match_rglob(self, tmp_path):
        if not _symlinks_supported(tmp_path):
            pytest.skip("symlinks not available (Windows without privilege)")
        root = tmp_path / "root"
        outside = tmp_path / "outside"
        _touch(outside, "far.c")
        _touch(outside, "deeper/far2.c")
        real = _touch(root, "real.c")
        os.symlink(real, root / "link_to_file.c")  # kept (is_file follows)
        os.symlink(root / "missing.c", root / "broken.c")  # dropped
        os.symlink(outside, root / "linkdir", target_is_directory=True)  # not descended
        os.symlink(outside / "deeper", root / "linkdir.c", target_is_directory=True)
        got = _same(root, [".c"], [])
        names = {p.name for p in got}
        assert "link_to_file.c" in names and "real.c" in names
        assert "broken.c" not in names and "linkdir.c" not in names
        assert "far.c" not in names and "far2.c" not in names


class TestRandomTrees:
    @pytest.mark.parametrize("seed", range(12))
    def test_random_tree_equivalence(self, tmp_path, seed):
        rng = random.Random(seed)
        root = tmp_path / f"r{seed}"
        dirs = ["", "a", "b", "build", "x/y", "x/build/z", "lib/vendor", "Lib/gen", "q.c"]
        exts = [".c", ".h", ".C", ".txt", ".hpp", ".min.h"]
        for i in range(rng.randint(5, 60)):
            d = rng.choice(dirs)
            depth = "/".join(f"d{rng.randint(0, 3)}" for _ in range(rng.randint(0, 3)))
            rel = "/".join(p for p in (d, depth, f"f{i}{rng.choice(exts)}") if p)
            _touch(root, rel)
        patterns = rng.sample(
            ["build", "vendor", "x/y", "*.min.h", "d1/d2", "Lib", "x/*/z", "d3"],
            rng.randint(0, 4),
        )
        _same(root, [".c", ".h", ".hpp"], patterns)


class TestLeafExclusion:
    """``_is_excluded_leaf`` equals ``is_excluded`` when the parent is clean."""

    PATTERNS = [
        [],
        ["build"],
        ["*.pyc"],
        ["a/b"],
        ["a/*/c"],
        ["x\\y"],
        ["build", "a/b", "*.min.js", "n*m"],
    ]

    @pytest.mark.parametrize("patterns", PATTERNS)
    def test_matches_full_check_for_clean_parents(self, patterns):
        rng = random.Random(1)
        parts_pool = ["a", "b", "c", "build", "x", "y", "nom", "f.pyc", "g.min.js", "h.c"]
        checked = 0
        for _ in range(2000):
            parts = [rng.choice(parts_pool) for _ in range(rng.randint(1, 6))]
            path = Path(*parts)
            if path.parent != Path(".") and is_excluded(path.parent, patterns):
                continue
            assert _is_excluded_leaf(path, patterns) == is_excluded(path, patterns), path
            checked += 1
        assert checked > 100


class TestWalkOrderByPythonVersion:
    """Both rglob walk orders, whatever Python runs the tests."""

    @staticmethod
    def _tree(tmp_path):
        root = tmp_path / "o"
        for rel in ["r.c", "a/a.c", "a/x/ax.c", "b/b.c", "b/y/by.c"]:
            _touch(root, rel)
        return root

    @staticmethod
    def _rel(root, files):
        return [p.relative_to(root).as_posix() for p in files]

    def _expected_scandir(self, root, last_first):
        # Reference walk written out: files of each subdirectory are listed
        # when its parent is visited; then the subdirectories are descended.
        def subdirs(d):
            return [Path(e.path) for e in os.scandir(d) if e.is_dir(follow_symlinks=False)]

        def files(d):
            return [Path(e.path) for e in os.scandir(d) if e.is_file() and e.name.endswith(".c")]

        out = files(root)
        stack = [root]
        while stack:
            d = stack.pop()
            subs = subdirs(d)
            for s in subs:
                out.extend(files(s))
            stack.extend(subs if last_first else list(reversed(subs)))
        return self._rel(root, out)

    @pytest.mark.parametrize("last_first", [True, False])
    def test_both_orders(self, tmp_path, monkeypatch, last_first):
        import shared.manifest as manifest_module

        root = self._tree(tmp_path)
        monkeypatch.setattr(manifest_module, "_RGLOB_LAST_SUBDIR_FIRST", last_first)
        got = self._rel(root, find_source_files(root, [".c"], []))
        assert got == self._expected_scandir(root, last_first)
        assert sorted(got) == sorted(self._rel(root, _classic(root, [".c"], [])))

    def test_running_python_matches_rglob(self, tmp_path):
        root = self._tree(tmp_path)
        _same(root, [".c"], [])
