#!/usr/bin/env python3
"""v2 deterministic 0/1/2 grader.

Score 2 requires the correct file(s) AND symbol(s) AND a line range
within ±N of each verified gold span (N = LINE_TOLERANCE, default 10).
An answer that omits an exact location, or whose predicted range is
outside that tolerance, scores at most 1.

This script must not be given a variant id. The retrieval-tool gate
(no tool call ⇒ 0 for ripgrep/hcr/claude_context/serena) is applied
afterwards by apply_retrieval_gate.py, which is allowed to see variant.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LINE_TOLERANCE = 10


def norm_path(p: str) -> str:
    s = p.replace("\\", "/").strip()
    s = re.sub(r"^[A-Za-z]:", "", s)
    s = s.lstrip("/")
    if "django/" in s:
        s = s[s.find("django/") :]
    return s


def norm_symbol(s: str) -> str:
    s = (s or "").strip()
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


def parse_lines(value) -> tuple[int, int] | None:
    if isinstance(value, (list, tuple)) and len(value) >= 1:
        try:
            a = int(value[0])
            b = int(value[1] if len(value) > 1 else value[0])
        except (TypeError, ValueError):
            return None
        if a <= 0 or b <= 0:
            return None
        return (a, b) if a <= b else (b, a)
    if isinstance(value, int):
        if value <= 0:
            return None
        return (value, value)
    if isinstance(value, str):
        m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+)\s*)?", value)
        if not m:
            return None
        a = int(m.group(1))
        b = int(m.group(2) or a)
        return (a, b) if a <= b else (b, a)
    return None


def iter_predicted_spans(answer: dict) -> list[dict]:
    out: list[dict] = []
    for sp in answer.get("spans") or answer.get("spans_predicted") or []:
        if not isinstance(sp, dict):
            continue
        lines = parse_lines(sp.get("lines") or sp.get("line") or sp.get("range"))
        file = sp.get("file") or sp.get("path")
        if not file or not lines:
            continue
        out.append({"file": file, "symbol": sp.get("symbol") or "", "lines": list(lines)})
    # Also accept "file:line" or "file:start-end" strings in a citations list.
    for cit in answer.get("citations") or []:
        if not isinstance(cit, str):
            continue
        m = re.search(r"([A-Za-z0-9_./\\-]+\.py):(\d+)(?:-(\d+))?", cit)
        if m:
            a = int(m.group(2))
            b = int(m.group(3) or a)
            out.append({"file": m.group(1), "symbol": "", "lines": [a, b] if a <= b else [b, a]})
    return out


def span_hit(pred: dict, gold: dict, n: int) -> bool:
    if norm_path(pred["file"]) != norm_path(gold["file"]):
        return False
    gsym = norm_symbol(gold.get("symbol") or "")
    psym = norm_symbol(pred.get("symbol") or "")
    if gsym and psym and psym != gsym:
        return False
    p0, p1 = pred["lines"]
    g0, g1 = gold["lines"]
    overlaps = p0 <= g1 and p1 >= g0
    contained = p0 >= (g0 - n) and p1 <= (g1 + n)
    return overlaps and contained


def all_gold_spans_hit(pred_spans: list[dict], gold_spans: list[dict], n: int) -> bool:
    if not gold_spans:
        return False
    for g in gold_spans:
        if not any(span_hit(p, g, n) for p in pred_spans):
            return False
    return True


def score_one(answer: dict, key: dict, n: int = LINE_TOLERANCE) -> int:
    files = answer.get("files") or answer.get("files_predicted") or []
    syms = answer.get("symbols") or answer.get("symbols_predicted") or []
    spans = iter_predicted_spans(answer)
    if not isinstance(files, list) or not isinstance(syms, list):
        return 0
    if not files and not syms and not spans:
        return 0
    sets = [key["ground_truth"]] + list(key.get("acceptable_alternatives") or [])
    best = 0
    for s in sets:
        req_f = s.get("files") or []
        req_s = s.get("symbols") or []
        req_sp = s.get("spans") or []
        has_files = files_match(files, req_f)
        has_syms = symbols_match(syms, req_s)
        has_loc = all_gold_spans_hit(spans, req_sp, n) if req_sp else False
        if has_files and has_syms and has_loc:
            return 2
        if has_files or has_syms or files_any(files, req_f) or (spans and any(
            norm_path(p["file"]) in {norm_path(f) for f in req_f} for p in spans
        )):
            best = max(best, 1)
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True, help="Anonymized JSONL (no variant field required).")
    ap.add_argument("--key", required=True, help="v2 answer_key.jsonl or questions.jsonl.")
    ap.add_argument("--out", help="Write scored JSONL here.")
    ap.add_argument("--tolerance", type=int, default=LINE_TOLERANCE, help="±N line tolerance (default 10).")
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
                "run scripts/anonymize_answers.py first (then apply_retrieval_gate.py)"
            )
        acc = score_one(ans, keys[qid], n=args.tolerance)
        row = {
            "grade_id": ans.get("grade_id"),
            "question_id": qid,
            "accuracy": acc,
            "files_predicted": ans.get("files") or ans.get("files_predicted") or [],
            "symbols_predicted": ans.get("symbols") or ans.get("symbols_predicted") or [],
            "spans_predicted": iter_predicted_spans(ans),
            "line_tolerance": args.tolerance,
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
