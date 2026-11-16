#!/usr/bin/env python3
"""Apply the v2 retrieval-tool gate after blind grading.

For variants other than `none`, if tool_calls_retrieval == 0 the accuracy
score is forced to 0, regardless of how well the structured answer matched
the key. The original blind score is preserved as accuracy_before_gate.

`none` (pure memory) and `read_only` (read_file only) are controls and are
not gated (0 retrieval calls is expected). A protocol_violation recorded on
a control run is handled by v2/scripts/grade_night.py (scored 0).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

RETRIEVAL_VARIANTS = {"ripgrep", "hcr", "claude_context", "serena"}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", required=True, help="JSONL from v2 grade_run.py (accuracy field).")
    ap.add_argument(
        "--runs",
        required=True,
        help="JSONL or a directory of per-run JSON files that still have variant and tool_calls_*.",
    )
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    scored = load_jsonl(Path(args.scored))
    runs_path = Path(args.runs)
    runs: list[dict] = []
    if runs_path.is_dir():
        for p in sorted(runs_path.glob("*.json")):
            runs.append(json.loads(p.read_text(encoding="utf-8")))
    else:
        runs = load_jsonl(runs_path)

    def key(r: dict):
        return (
            r.get("grade_id") or r.get("run_id") or r.get("session_id"),
            r.get("question_id") or r.get("id"),
            r.get("repetition"),
        )

    # Map by question_id + run_id/session if present, else question+rep+variant order.
    by_run_id = {}
    by_qvr = {}
    for r in runs:
        rid = r.get("run_id") or r.get("session_id") or r.get("grade_id")
        if rid:
            by_run_id[str(rid)] = r
        qvr = (r.get("question_id") or r.get("id"), r.get("variant"), r.get("repetition"))
        by_qvr[qvr] = r

    out = []
    for s in scored:
        meta = None
        gid = s.get("grade_id")
        if gid and str(gid) in by_run_id:
            meta = by_run_id[str(gid)]
        if meta is None:
            # anonymize_answers typically stores grade_id = run_id
            pass
        if meta is None:
            # Last resort: unique question_id if only one run matches
            matches = [r for r in runs if (r.get("question_id") or r.get("id")) == s.get("question_id")]
            if len(matches) == 1:
                meta = matches[0]
        variant = (meta or {}).get("variant", "")
        n_ret = (meta or {}).get("tool_calls_retrieval")
        if n_ret is None and meta is not None:
            n_ret = 0
        gated = False
        acc = s.get("accuracy", 0)
        before = acc
        if variant in RETRIEVAL_VARIANTS and (n_ret or 0) == 0:
            acc = 0
            gated = True
        row = dict(s)
        row["accuracy_before_gate"] = before
        row["accuracy"] = acc
        row["retrieval_gate_applied"] = gated
        row["variant"] = variant
        row["tool_calls_retrieval"] = n_ret
        row["tool_calls_total"] = (meta or {}).get("tool_calls_total")
        out.append(row)
        gate = " GATED->0" if gated else ""
        print(f"{s.get('question_id')} variant={variant or '?'} retrieval={n_ret} score={acc}{gate}")

    Path(args.out).write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
