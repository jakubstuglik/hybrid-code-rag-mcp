#!/usr/bin/env python3
"""Re-derive tool-call classes for existing run records from their raw stdout.

Uses the current scripts/run_one.py classifier (MCP `use_tool` calls are
classified by the inner tool; Serena `serena_repl` by the REPL method).
Writes corrected copies; the originals are not modified. The old count is
kept as tool_calls_retrieval_recorded.

    python v2/scripts/reclassify_runs.py --log-dir logs/v2-pilot --out logs/v2-pilot/runs_reclassified
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import run_one  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log-dir", required=True, help="Has runs/*.json and raw/*.raw.json")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    log = Path(args.log_dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    changed = 0
    n = 0
    for p in sorted((log / "runs").glob("*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        raw_p = log / "raw" / (p.stem + ".raw.json")
        if raw_p.is_file():
            raw = json.loads(raw_p.read_text(encoding="utf-8"))
            calls = run_one.collect_tool_calls(run_one.extract_json_objects(raw.get("stdout") or ""))
        else:  # fall back to the recorded calls (re-classify from raw_input)
            calls = run_one.collect_tool_calls([
                {"type": "tool_call", "toolName": c["name"], "rawInput": c.get("raw_input") or {}}
                for c in rec.get("tool_calls") or []
            ])
        new = dict(rec)
        new["tool_calls_retrieval_recorded"] = rec.get("tool_calls_retrieval")
        new["tool_calls"] = calls
        new["tool_calls_total"] = len(calls)
        new["tool_calls_retrieval"] = sum(c["class"] == "retrieval" for c in calls)
        new["tool_calls_read"] = sum(c["class"] == "read" for c in calls)
        new["tool_calls_other"] = sum(c["class"] == "other" for c in calls)
        if new["tool_calls_retrieval"] != rec.get("tool_calls_retrieval"):
            changed += 1
            print(f"{p.stem}: retrieval {rec.get('tool_calls_retrieval')} -> {new['tool_calls_retrieval']}")
        (out / p.name).write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        n += 1
    print(f"reclassified {n} runs, retrieval count changed in {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
