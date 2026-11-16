#!/usr/bin/env python3
"""Deterministic 0/1/2 grader. Reads anonymized answers and a frozen key.

This script must not be given a variant id. See METHOD.md and grading.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def norm_path(p: str) -> str:
    s = p.replace("\\", "/").strip()
    s = re.sub(r"^[A-Za-z]:", "", s)
    s = s.lstrip("/")
    if "django/" in s:
        s = s[s.find("django/") :]
    return s


def norm_symbol(s: str) -> str:
    s = s.strip()
    # ignore module prefixes: signing.TimestampSigner -> TimestampSigner
    return s.split(".")[-1] if s else s


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def files_match(predicted: list[str], required: list[str]) -> bool:
    pred = {norm_path(p) for p in predicted}
    return all(norm_path(r) in pred for r in required)


def symbols_match(predicted: list[str], required: list[str]) -> bool:
    pred = {norm_symbol(s) for s in predicted}
    return all(norm_symbol(r) in pred for r in required)


def files_any(predicted: list[str], required: list[str]) -> bool:
    pred = {norm_path(p) for p in predicted}
    return any(norm_path(r) in pred for r in required)


def set_satisfies(pred_files, pred_syms, required_files, required_syms, completeness: str) -> str:
    """Return 'full', 'partial', or 'none' for one file/symbol set."""
    has_all_files = files_match(pred_files, required_files)
    has_all_syms = symbols_match(pred_syms, required_syms)
    has_any_file = files_any(pred_files, required_files)
    if has_all_files and has_all_syms:
        return "full"
    if has_any_file or (has_all_syms and has_any_file):
        return "partial"
    if has_all_files and not has_all_syms:
        return "partial"
    return "none"


def score_one(answer: dict, key: dict) -> int:
    files = answer.get("files") or answer.get("files_predicted") or []
    syms = answer.get("symbols") or answer.get("symbols_predicted") or []
    if not isinstance(files, list) or not isinstance(syms, list):
        return 0
    if not files and not syms:
        return 0
    category = key.get("category", "")
    sets = [key["ground_truth"]] + list(key.get("acceptable_alternatives") or [])
    best = "none"
    for s in sets:
        req_f = s.get("files") or []
        req_s = s.get("symbols") or []
        # For alternatives that are marked as partial substitutes in notes,
        # still use the same all-files-and-symbols rule; notes are human/audit.
        rank = set_satisfies(files, syms, req_f, req_s, category)
        if rank == "full":
            return 2
        if rank == "partial":
            best = "partial"
    # Cross-file completeness often requires a minimum subset, recorded in
    # grading_notes. The automatic grader awards 2 only for a complete
    # listed set (ground truth or an acceptable_alternatives entry). A
    # missing subclass on C07-style items therefore scores at most 1 unless
    # an alternative set is listed. That is intentional and audited.
    return 1 if best == "partial" else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True, help="Anonymized JSONL (no variant field required).")
    ap.add_argument("--key", required=True, help="Frozen answer_key.jsonl or questions.jsonl.")
    ap.add_argument("--out", help="Write scored JSONL here.")
    args = ap.parse_args()
    keys = {r["id"]: r for r in load_jsonl(Path(args.key))}
    out_rows = []
    for ans in load_jsonl(Path(args.answers)):
        qid = ans.get("question_id") or ans.get("id")
        if qid not in keys:
            raise SystemExit(f"unknown question id: {qid}")
        if "variant" in ans:
            raise SystemExit(
                "refusing to grade a file that still contains 'variant' — "
                "run scripts/anonymize_answers.py first"
            )
        acc = score_one(ans, keys[qid])
        row = {
            "grade_id": ans.get("grade_id"),
            "question_id": qid,
            "accuracy": acc,
            "files_predicted": ans.get("files") or ans.get("files_predicted") or [],
            "symbols_predicted": ans.get("symbols") or ans.get("symbols_predicted") or [],
        }
        out_rows.append(row)
        print(f"{qid} {ans.get('grade_id') or '-'} score={acc}")
    if args.out:
        Path(args.out).write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in out_rows) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
