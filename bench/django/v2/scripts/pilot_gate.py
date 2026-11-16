#!/usr/bin/env python3
"""Decide whether a graded pilot is good enough to start the official run.

Reads <log-dir>/<prefix>_aggjoin_scored_gated.jsonl (from grade_night.py) and
prints a JSON verdict. Exit codes: 0 GO, 10 NOT_DISCRIMINATING, 20 HARNESS_FAIL.

GO needs all of:
  - harness: <= 10% of runs error/timeout, <= 1 control protocol violation,
    and no retrieval variant with > 30% of runs zeroed by the retrieval gate;
  - discrimination: mean(none) <= --max-none (default 1.0) and
    best retrieval mean - mean(none) >= --min-gap (default 0.5).
`read_only` is reported but is not a gate (it may legitimately be strong).
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

RETRIEVAL = ("ripgrep", "hcr", "claude_context", "serena")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log-dir", required=True)
    ap.add_argument("--prefix", default="pilot")
    ap.add_argument("--max-none", type=float, default=1.0)
    ap.add_argument("--min-gap", type=float, default=0.5)
    ap.add_argument("--out", help="Write the verdict JSON here too.")
    args = ap.parse_args()
    p = Path(args.log_dir) / f"{args.prefix}_aggjoin_scored_gated.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    by = defaultdict(list)
    for r in rows:
        by[r["variant"]].append(r)
    mean = {v: sum(r["accuracy"] for r in rs) / len(rs) for v, rs in by.items()}
    n = len(rows)
    bad_status = [r for r in rows if r.get("status") in ("error", "timeout")]
    ctrl_viol = [r for r in rows if r["variant"] in ("none", "read_only") and r.get("status") == "protocol_violation"]
    gated = {v: sum(bool(r.get("retrieval_gate_applied")) for r in by[v]) / len(by[v]) for v in RETRIEVAL if by.get(v)}
    problems = []
    if n and len(bad_status) / n > 0.10:
        problems.append(f"{len(bad_status)}/{n} runs error/timeout")
    if len(ctrl_viol) > 1:
        problems.append(f"{len(ctrl_viol)} control protocol violations: " + ", ".join(f"{r['question_id']}/{r['variant']}" for r in ctrl_viol))
    for v, frac in gated.items():
        if frac > 0.30:
            problems.append(f"{v}: {frac:.0%} of runs zeroed by retrieval gate (classifier or prompt problem?)")
    best_v = max((v for v in RETRIEVAL if v in mean), key=lambda v: mean[v], default=None)
    none_m = mean.get("none")
    reasons = []
    if none_m is None:
        reasons.append("no `none` runs")
    else:
        if none_m > args.max_none:
            reasons.append(f"mean(none)={none_m:.2f} > {args.max_none}")
        if best_v and mean[best_v] - none_m < args.min_gap:
            reasons.append(f"gap {best_v}-none={mean[best_v]-none_m:.2f} < {args.min_gap}")
    verdict = "HARNESS_FAIL" if problems else ("NOT_DISCRIMINATING" if reasons else "GO")
    out = {
        "verdict": verdict, "n_runs": n,
        "mean": {k: round(v, 3) for k, v in sorted(mean.items())},
        "best_retrieval": best_v, "gated_fraction": {k: round(v, 2) for k, v in gated.items()},
        "harness_problems": problems, "not_discriminating_reasons": reasons,
        "error_timeout_runs": [f"{r['question_id']}/{r['variant']}:{r.get('status')}" for r in bad_status],
    }
    text = json.dumps(out, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    return {"GO": 0, "NOT_DISCRIMINATING": 10, "HARNESS_FAIL": 20}[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
