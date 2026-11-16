#!/usr/bin/env python3
"""Strip variant labels before official grading. See METHOD.md §7."""
from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="Raw run JSONL (may contain variant).")
    ap.add_argument("--out", required=True, help="Anonymized answers JSONL.")
    ap.add_argument("--map", required=True, help="Hidden map JSON (operator only).")
    args = ap.parse_args()
    mapping = []
    answers = []
    for line in Path(args.raw).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        grade_id = secrets.token_hex(8)
        pred_files = raw.get("files_predicted") or raw.get("files") or []
        pred_syms = raw.get("symbols_predicted") or raw.get("symbols") or []
        answers.append(
            {
                "grade_id": grade_id,
                "question_id": raw.get("question_id") or raw.get("id"),
                "files": pred_files,
                "symbols": pred_syms,
                "notes": raw.get("notes") or "",
            }
        )
        mapping.append(
            {
                "grade_id": grade_id,
                "run_id": raw.get("run_id"),
                "question_id": raw.get("question_id") or raw.get("id"),
                "variant": raw.get("variant"),
                "repetition": raw.get("repetition"),
            }
        )
    Path(args.out).write_text(
        "\n".join(json.dumps(a, ensure_ascii=False) for a in answers) + "\n",
        encoding="utf-8",
    )
    Path(args.map).write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(answers)} anonymized answers and a hidden map")
    return 0


if __name__ == "__main__":
    sys.exit(main())
