#!/usr/bin/env python3
"""Orchestrate a scheduled bench run (pilot or official pool via --questions).

Runs whatever pool --questions points at. Requires
`--approved-by-operator`. Writes logs under logs/pilot/.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
DEFAULT_QUESTIONS = ROOT / "pilot_questions.jsonl"
DEFAULT_SCHEDULE_SEED = 20261114
WARSAW = timezone(timedelta(hours=1), name="Europe/Warsaw")  # CET; runner should prefer local now()


def now_label() -> str:
    # Prefer the host local clock (AO is Europe/Warsaw).
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Europe/Warsaw"


def past_stop(hhmm: str) -> bool:
    """True once local time is past HH:MM, treating 12:00-23:59 as 'before midnight'."""
    h, m = (int(x) for x in hhmm.split(":"))
    now = datetime.now()
    stop = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if now.hour >= 12 and h < 12:  # evening now, stop is tomorrow morning
        return False
    return now >= stop


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default=str(DEFAULT_QUESTIONS))
    ap.add_argument("--variants", nargs="+", default=["none", "read_only", "ripgrep", "hcr", "claude_context", "serena"])
    ap.add_argument("--repetitions", type=int, default=1)
    ap.add_argument("--seed", type=int, default=DEFAULT_SCHEDULE_SEED)
    ap.add_argument("--mode", choices=["full_shuffle", "blocked_rotation"], default="blocked_rotation")
    ap.add_argument("--skip-variant", action="append", default=[])
    ap.add_argument("--checkout", default=r"C:\Apps\hcr-bench\django")
    ap.add_argument("--timeout-s", type=int, default=180)
    ap.add_argument("--log-dir", default=str(ROOT / "logs" / "pilot"))
    ap.add_argument("--schedule", help="Reuse an already-written schedule JSON.")
    ap.add_argument("--approved-by-operator", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--start-from", type=int, default=1, help="1-based order to resume at.")
    ap.add_argument("--grok-home", default=r"C:\Apps\hcr-bench\grok-home")
    ap.add_argument(
        "--prep-mcp",
        default=str(SCRIPTS / "prep_variant_mcp.py"),
        help="Script that attaches the right MCP servers in GROK_HOME for a variant.",
    )
    ap.add_argument("--no-prep-mcp", action="store_true")
    ap.add_argument(
        "--system-prompt",
        help="System prompt for retrieval variants (v2: v2/prompts/system_v2.txt).",
    )
    ap.add_argument(
        "--system-prompt-none",
        help="System prompt for the none control (v2: v2/prompts/system_v2_none.txt).",
    )
    ap.add_argument(
        "--system-prompt-read-only",
        help="System prompt for the read_only control (v2.1: v2/prompts/system_v21_read_only.txt).",
    )
    ap.add_argument(
        "--stop-at",
        help="Local wall-clock HH:MM; do not start a new run after this time (e.g. 06:40).",
    )
    ap.add_argument(
        "--only-block",
        help="Run only schedule items whose block equals this (light, hcr, claude_context).",
    )
    ap.add_argument(
        "--schema",
        help="Structured-answer JSON schema (v2: v2/prompts/answer.schema.json).",
    )
    args = ap.parse_args()

    if not args.approved_by_operator and not args.dry_run:
        print("refusing to launch the pilot without --approved-by-operator", file=sys.stderr)
        return 2

    log_dir = Path(args.log_dir)
    raw_dir = log_dir / "raw"
    run_dir = log_dir / "runs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    if args.schedule:
        schedule_path = Path(args.schedule)
        doc = json.loads(schedule_path.read_text(encoding="utf-8"))
    else:
        schedule_path = log_dir / "schedule.json"
        cmd = [
            sys.executable,
            str(SCRIPTS / "schedule.py"),
            "--questions",
            args.questions,
            "--variants",
            *args.variants,
            "--repetitions",
            str(args.repetitions),
            "--seed",
            str(args.seed),
            "--mode",
            args.mode,
            "--out",
            str(schedule_path),
        ]
        for v in args.skip_variant:
            cmd.extend(["--skip-variant", v])
        subprocess.check_call(cmd)
        doc = json.loads(schedule_path.read_text(encoding="utf-8"))

    items = doc["items"]
    status_path = log_dir / "pilot_status.jsonl"
    print(f"{now_label()} pilot start n={len(items)} mode={doc.get('mode')} seed={doc.get('seed')} schedule={schedule_path}")

    failures = 0
    for item in items:
        order = item["order"]
        if order < args.start_from:
            continue
        if args.only_block and item.get("block") != args.only_block:
            continue
        if args.stop_at and not args.dry_run and past_stop(args.stop_at):
            print(f"{now_label()} stop-at {args.stop_at} reached; next order={order}")
            break
        qid = item["question_id"]
        variant = item["variant"]
        rep = item["repetition"]
        stem = f"{qid}__{variant}__r{rep}"
        out_path = run_dir / f"{stem}.json"
        raw_path = raw_dir / f"{stem}.raw.json"
        if out_path.is_file() and not args.dry_run:
            print(f"{now_label()} skip existing {stem}")
            continue
        if not args.no_prep_mcp and args.prep_mcp:
            prep = [
                sys.executable,
                args.prep_mcp,
                "--variant",
                variant,
                "--grok-home",
                args.grok_home,
                "--cwd",
                args.checkout,
            ]
            prc = subprocess.call(prep)
            if prc != 0:
                print(f"{now_label()} prep-mcp failed for {stem} rc={prc}", file=sys.stderr)
                failures += 1
                rec = {
                    "ts": now_label(),
                    "order": order,
                    "question_id": qid,
                    "variant": variant,
                    "repetition": rep,
                    "block": item.get("block"),
                    "rc": prc,
                    "elapsed_s": 0,
                    "out": str(out_path),
                    "phase": "prep_mcp",
                }
                with status_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                continue
        cmd = [
            sys.executable,
            str(SCRIPTS / "run_one.py"),
            "--questions",
            args.questions,
            "--id",
            qid,
            "--variant",
            variant,
            "--repetition",
            str(rep),
            "--checkout",
            args.checkout,
            "--timeout-s",
            str(args.timeout_s),
            "--grok-home",
            args.grok_home,
            "--out",
            str(out_path),
            "--raw-out",
            str(raw_path),
        ]
        prompt = args.system_prompt
        if variant == "none" and args.system_prompt_none:
            prompt = args.system_prompt_none
        elif variant == "read_only" and args.system_prompt_read_only:
            prompt = args.system_prompt_read_only
        if prompt:
            cmd.extend(["--system-prompt", prompt])
        if args.schema:
            cmd.extend(["--schema", args.schema])
        if args.dry_run:
            cmd.append("--dry-run")
        else:
            cmd.append("--approved-by-operator")
        t0 = time.perf_counter()
        print(f"{now_label()} start order={order} {stem} block={item.get('block')}")
        rc = subprocess.call(cmd)
        elapsed = time.perf_counter() - t0
        rec = {
            "ts": now_label(),
            "order": order,
            "question_id": qid,
            "variant": variant,
            "repetition": rep,
            "block": item.get("block"),
            "rc": rc,
            "elapsed_s": elapsed,
            "out": str(out_path),
        }
        with status_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"{now_label()} done order={order} {stem} rc={rc} elapsed={elapsed:.1f}s")
        if rc != 0:
            failures += 1
    print(f"{now_label()} pilot finished failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
