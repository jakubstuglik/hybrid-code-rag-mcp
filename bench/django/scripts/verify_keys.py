#!/usr/bin/env python3
"""Verify that every frozen answer key exists in the pinned Django tree."""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path


def iter_defs(tree: ast.AST) -> list[tuple[str, int, int | None]]:
    """Return (qualified_or_simple_name, lineno, end_lineno) for classes, functions, assigns."""
    out: list[tuple[str, int, int | None]] = []

    def add(name: str, node: ast.AST) -> None:
        end = getattr(node, "end_lineno", None)
        out.append((name, getattr(node, "lineno", 0), end))

    class V(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            q = ".".join(self.stack + [node.name]) if self.stack else node.name
            add(node.name, node)
            if self.stack:
                add(q, node)
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._fn(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._fn(node)

        def _fn(self, node: ast.AST) -> None:
            name = node.name  # type: ignore[attr-defined]
            add(name, node)
            if self.stack:
                add(".".join(self.stack + [name]), node)
            self.stack.append(name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Assign(self, node: ast.Assign) -> None:
            for t in node.targets:
                if isinstance(t, ast.Name):
                    add(t.id, node)
            self.generic_visit(node)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            if isinstance(node.target, ast.Name):
                add(node.target.id, node)
            self.generic_visit(node)

    V().visit(tree)
    return out


def load_module_index(path: Path) -> tuple[str, list[tuple[str, int, int | None]]]:
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return src, [("_SYNTAX_ERROR_", 0, None)] if False else (_ for _ in ()).throw(e)
    return src, iter_defs(tree)


def symbol_hits(defs: list[tuple[str, int, int | None]], symbol: str) -> list[tuple[str, int, int | None]]:
    simple = symbol.split(".")[-1]
    hits = [d for d in defs if d[0] == symbol or d[0] == simple or d[0].endswith("." + simple)]
    # For qualified names like django.db.backends.mysql.base.DatabaseWrapper,
    # also accept DatabaseWrapper in that file.
    if not hits and "." in symbol:
        hits = [d for d in defs if d[0] == simple]
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--questions", required=True)
    args = ap.parse_args()
    repo = Path(args.repo)
    rows = [json.loads(l) for l in Path(args.questions).read_text(encoding="utf-8").splitlines() if l.strip()]
    errors = 0
    for row in rows:
        qid = row["id"]
        gts = [row["ground_truth"]] + list(row.get("acceptable_alternatives") or [])
        # Only the primary ground_truth must fully exist; alternatives are optional extras
        gt = row["ground_truth"]
        for rel in gt["files"]:
            path = repo / rel
            if not path.is_file():
                print(f"FAIL {qid}: missing file {rel}")
                errors += 1
        # symbol + span checks against listed files
        file_indexes: dict[str, tuple[str, list]] = {}
        for rel in gt["files"]:
            path = repo / rel
            if path.is_file():
                try:
                    file_indexes[rel] = load_module_index(path)
                except SyntaxError as e:
                    print(f"FAIL {qid}: syntax error in {rel}: {e}")
                    errors += 1
        for sym in gt.get("symbols") or []:
            hits_any = []
            for rel, (src, defs) in file_indexes.items():
                hits = symbol_hits(defs, sym)
                hits_any.extend((rel, h) for h in hits)
            if not hits_any:
                # settings / string constant fallback: regex assignment or class/def
                simple = sym.split(".")[-1]
                found = False
                for rel, (src, _defs) in file_indexes.items():
                    if re.search(rf"^(class|def|async def)\s+{re.escape(simple)}\b", src, re.M):
                        found = True
                        break
                    if re.search(rf"^{re.escape(simple)}\s*=", src, re.M):
                        found = True
                        break
                if not found:
                    print(f"FAIL {qid}: symbol {sym!r} not found in {gt['files']}")
                    errors += 1
                    continue
            # if we have spans, check overlap
        for span in gt.get("spans") or []:
            rel = span["file"]
            path = repo / rel
            if not path.is_file():
                print(f"FAIL {qid}: span file missing {rel}")
                errors += 1
                continue
            if rel not in file_indexes:
                try:
                    file_indexes[rel] = load_module_index(path)
                except SyntaxError as e:
                    print(f"FAIL {qid}: syntax error in span file {rel}: {e}")
                    errors += 1
                    continue
            src, defs = file_indexes[rel]
            start, end = span["lines"]
            text_lines = src.splitlines()
            n = len(text_lines)
            if start < 1 or end > n or start > end:
                print(f"FAIL {qid}: span {rel}:{start}-{end} out of range (file has {n} lines)")
                errors += 1
                continue
            sym = span.get("symbol")
            if not sym:
                continue
            hits = symbol_hits(defs, sym)
            overlap = [
                h
                for h in hits
                if h[1] <= end and (h[2] or h[1]) >= start
            ]
            if not overlap:
                # allow the span to cover the symbol start line
                starts = [h for h in hits if start <= h[1] <= end]
                if not starts:
                    # last resort: the name appears in the span text
                    chunk = "\n".join(text_lines[start - 1 : end])
                    simple = sym.split(".")[-1]
                    if not re.search(rf"\b{re.escape(simple)}\b", chunk):
                        print(
                            f"FAIL {qid}: span {rel}:{start}-{end} does not contain symbol {sym!r}; "
                            f"ast hits={[(h[0], h[1], h[2]) for h in hits[:8]]}"
                        )
                        errors += 1
        print(f"OK   {qid}")
    print(f"checked={len(rows)} failures={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
