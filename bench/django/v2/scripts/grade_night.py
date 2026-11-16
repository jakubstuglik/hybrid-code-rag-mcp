#!/usr/bin/env python3
"""Grade one log directory end to end (blind grade -> retrieval gate -> aggregate).

Committed version of the ad-hoc C:\\Temp\\hcr-night\\grade2.py used on 14/15.11.

    python v2/scripts/grade_night.py --log-dir logs/v21-pilot --key v2/pilot21_answer_key.jsonl
    python v2/scripts/grade_night.py --log-dir logs/v21 --key v2/answer_key.jsonl --prefix official

Outputs in --log-dir: anonymized_answers.jsonl, <prefix>_scored.jsonl,
<prefix>_scored_gated.jsonl, <prefix>_aggjoin_{scored,scored_gated}.jsonl,
<prefix>_aggregate_{scored,scored_gated}.{json,txt}, <prefix>_table.md.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAT = {"exact_lookup": "E", "semantic": "S", "cross_file": "C"}
ORDER = ["none", "read_only", "ripgrep", "hcr", "claude_context", "serena"]


def load_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def run(cmd: list[str]) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.stdout.write(r.stdout[-3000:])
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(r.returncode)
    return r.stdout


def table(rows: list[dict], keys: dict) -> str:
    by = defaultdict(list)
    for r in rows:
        by[r["variant"]].append(r)
    qids = sorted(keys)
    lines = ["variant | E | S | C | all | #2 | #0 | gated | violations | mean s",
             "---|---|---|---|---|---|---|---|---|---"]
    for v in [x for x in ORDER if x in by] + sorted(set(by) - set(ORDER)):
        rs = by[v]
        def mean(cat=None):
            xs = [r["accuracy"] for r in rs if cat is None or r["category"] == cat]
            return f"{sum(xs)/len(xs):.2f} (n={len(xs)})" if xs else "-"
        wall = [r["wall_time_s"] for r in rs if r.get("wall_time_s") is not None]
        lines.append(" | ".join([
            v, mean("E"), mean("S"), mean("C"), mean(),
            str(sum(r["accuracy"] == 2 for r in rs)), str(sum(r["accuracy"] == 0 for r in rs)),
            str(sum(bool(r.get("retrieval_gate_applied")) for r in rs)),
            str(sum(r.get("status") == "protocol_violation" for r in rs)),
            f"{sum(wall)/len(wall):.1f}" if wall else "-",
        ]))
    lines.append("")
    vs = [x for x in ORDER if x in by] + sorted(set(by) - set(ORDER))
    lines.append("question | " + " | ".join(vs))
    lines.append("---|" + "|".join("---" for _ in vs))
    cell = defaultdict(list)
    for r in rows:
        cell[(r["question_id"], r["variant"])].append(str(r["accuracy"]))
    for q in qids:
        lines.append(q + " | " + " | ".join("/".join(cell[(q, v)]) or "-" for v in vs))
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log-dir", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--runs", help="Run-record dir (default: <log-dir>/runs)")
    ap.add_argument("--prefix", default="pilot")
    args = ap.parse_args()
    L = Path(args.log_dir)
    runs = Path(args.runs) if args.runs else L / "runs"
    key = Path(args.key)
    keys = {r["id"]: r for r in load_jsonl(key)}
    py = sys.executable
    recs = {}
    anon = []
    for p in sorted(runs.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d["question_id"] not in keys:
            continue
        recs[d["run_id"]] = d
        anon.append({"grade_id": d["run_id"], "question_id": d["question_id"],
                     "files": d.get("files_predicted") or [], "symbols": d.get("symbols_predicted") or [],
                     "spans": d.get("spans_predicted") or [], "notes": d.get("notes") or ""})
    if not anon:
        raise SystemExit(f"no run records for this key in {runs}")
    anon_p = L / f"{args.prefix}_anonymized_answers.jsonl"
    anon_p.write_text("\n".join(json.dumps(a, ensure_ascii=False) for a in anon) + "\n", encoding="utf-8")
    pre = L / args.prefix
    scored = Path(f"{pre}_scored.jsonl")
    gated = Path(f"{pre}_scored_gated.jsonl")
    run([py, str(ROOT / "v2/scripts/grade_run.py"), "--answers", str(anon_p), "--key", str(key), "--out", str(scored)])
    run([py, str(ROOT / "v2/scripts/apply_retrieval_gate.py"), "--scored", str(scored), "--runs", str(runs), "--out", str(gated)])
    md = []
    for flavour, src in (("scored", scored), ("scored_gated", gated)):
        rows = load_jsonl(src)
        for r in rows:
            m = recs[r["grade_id"]]
            r["variant"] = m["variant"]
            r["repetition"] = m.get("repetition", 1)
            r["category"] = CAT[keys[r["question_id"]]["category"]]
            r["wall_time_s"] = m.get("wall_time_s")
            r["cost_usd"] = m.get("cost_usd")
            r["status"] = m.get("status")
            # A control that broke its protocol (searched / used a tool) scores 0.
            if m.get("status") == "protocol_violation" and m["variant"] in ("none", "read_only"):
                r["accuracy_before_violation"] = r["accuracy"]
                r["accuracy"] = 0
        jp = Path(f"{pre}_aggjoin_{flavour}.jsonl")
        jp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
        out = run([py, str(ROOT / "scripts/aggregate.py"), "--scored", str(jp), "--bootstrap-seed", "20261114",
                   "--n-boot", "10000", "--out", str(Path(f"{pre}_aggregate_{flavour}.json"))])
        Path(f"{pre}_aggregate_{flavour}.txt").write_text(out, encoding="utf-8")
        md.append(f"## {flavour}\n\n" + table(rows, keys))
    Path(f"{pre}_table.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print(f"graded {len(anon)} runs from {runs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
