#!/usr/bin/env python3
"""Split a recorded schedule into consecutive (repetition, block) groups.

Writes one sub-schedule per group (same items, same order numbers) and prints
one line per group: "<rep> <block> <n> <path>". Used by v2/night/run_night_v21.ps1
so stacks are swapped only at block boundaries.

    python v2/scripts/schedule_groups.py --schedule logs/v21-pilot/schedule-r1.json --out-dir logs/v21-pilot/groups [--drop-variant serena]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--drop-variant", action="append", default=[], help="Remove a variant (stack failed to start).")
    args = ap.parse_args()
    doc = json.loads(Path(args.schedule).read_text(encoding="utf-8"))
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    groups: list[tuple[int, str, list[dict]]] = []
    for it in doc["items"]:
        if it["variant"] in args.drop_variant:
            continue
        key = (it["repetition"], it.get("block") or "other")
        if not groups or (groups[-1][0], groups[-1][1]) != key:
            groups.append((key[0], key[1], []))
        groups[-1][2].append(it)
    for i, (rep, block, items) in enumerate(groups, 1):
        sub = dict(doc, items=items, n_runs=len(items), subset=f"r{rep}-{block}")
        p = out / f"g{i:02d}-r{rep}-{block}.json"
        p.write_text(json.dumps(sub, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{rep} {block} {len(items)} {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
