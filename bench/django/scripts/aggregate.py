#!/usr/bin/env python3
"""Report retrieval/localization accuracy with bootstrap CIs.

Official reporting (Zakładki AI review, 2026-11-14):
- The metric is named "retrieval/localization accuracy".
- Report per question and per category E / S / C (exact_lookup, semantic,
  cross_file). Do not present a single headline average across all questions.
- The no-retrieval variant `none` is a control and is printed in its own
  section, not mixed into a four-way "winner" table.
- 95% percentile bootstrap CIs: per question, over repetitions; per category,
  over that category's per-question means. With n < 2 the CI is undefined.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

METRIC_NAME = "retrieval/localization accuracy"
DEFAULT_BOOTSTRAP_SEED = 20261114
DEFAULT_N_BOOT = 10000

CATEGORY_LABELS = {
    "exact_lookup": "E",
    "semantic": "S",
    "cross_file": "C",
    "E": "E",
    "S": "S",
    "C": "C",
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def category_of(row: dict, key_index: dict[str, dict] | None) -> str:
    qid = row.get("question_id") or row.get("id") or ""
    if row.get("category"):
        raw = row["category"]
    elif key_index and qid in key_index:
        raw = key_index[qid].get("category") or ""
    else:
        raw = ""
        if qid[:1] in ("E", "P", "X", "S", "C") and len(qid) >= 3:
            # Pilot/external ids do not encode E/S/C; official E/S/C do.
            if qid[0] in CATEGORY_LABELS and qid[1:].isdigit():
                raw = qid[0]
    return CATEGORY_LABELS.get(raw, raw or "unknown")


def percentile_bootstrap_ci(
    samples: list[float],
    n_boot: int = DEFAULT_N_BOOT,
    alpha: float = 0.05,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> dict:
    n = len(samples)
    if n == 0:
        return {"n": 0, "mean": None, "ci95": None, "note": "no samples"}
    mean = sum(samples) / n
    if n < 2:
        return {
            "n": n,
            "mean": mean,
            "ci95": None,
            "note": "degenerate: n<2, 95% CI not defined",
        }
    # Independent RNG so call order does not shift later intervals.
    import random

    rng = random.Random(seed)
    means: list[float] = []
    for _ in range(n_boot):
        draw = [samples[rng.randrange(n)] for _ in range(n)]
        means.append(sum(draw) / n)
    means.sort()
    lo_i = int((alpha / 2) * n_boot)
    hi_i = int((1 - alpha / 2) * n_boot) - 1
    lo_i = max(0, min(n_boot - 1, lo_i))
    hi_i = max(0, min(n_boot - 1, hi_i))
    return {
        "n": n,
        "mean": mean,
        "ci95": [means[lo_i], means[hi_i]],
        "note": None,
        "n_boot": n_boot,
        "bootstrap_seed": seed,
    }


def fmt_ci(info: dict) -> str:
    if info.get("ci95") is None:
        m = info.get("mean")
        mean_s = "n/a" if m is None else f"{m:.3f}"
        return f"mean={mean_s} ci95=undefined ({info.get('note')})"
    lo, hi = info["ci95"]
    return f"mean={info['mean']:.3f} ci95=[{lo:.3f}, {hi:.3f}]"


def main() -> int:
    ap = argparse.ArgumentParser(description="Report retrieval/localization accuracy with bootstrap CIs.")
    ap.add_argument("--scored", required=True, help="JSONL with accuracy plus variant+repetition (joined via the hidden map).")
    ap.add_argument("--key", help="Optional questions.jsonl or answer_key.jsonl to resolve categories.")
    ap.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    ap.add_argument("--n-boot", type=int, default=DEFAULT_N_BOOT)
    ap.add_argument("--out", help="Optional JSON summary path.")
    args = ap.parse_args()

    rows = load_jsonl(Path(args.scored))
    key_index: dict[str, dict] = {}
    if args.key:
        for r in load_jsonl(Path(args.key)):
            key_index[r["id"]] = r

    by: dict[tuple[str, str], list[int]] = defaultdict(list)
    qcat: dict[str, str] = {}
    process: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        qid = r.get("question_id") or r.get("id")
        variant = r["variant"]
        by[(variant, qid)].append(int(r["accuracy"]))
        qcat[qid] = category_of(r, key_index)
        process[variant].append(r)

    variants = sorted({v for v, _ in by})
    controls = [v for v in variants if v in ("none", "read_only")]
    compared = [v for v in variants if v not in ("none", "read_only")]

    summary: dict = {
        "metric": METRIC_NAME,
        "bootstrap_seed": args.bootstrap_seed,
        "n_boot": args.n_boot,
        "note_no_headline_average": True,
        "per_question": {},
        "per_category": {},
        "process": {},
    }

    def report_variant(variant: str, heading: str) -> None:
        print(f"## {heading}")
        print()
        print(f"Metric: {METRIC_NAME}")
        qids = sorted({q for v, q in by if v == variant})
        summary["per_question"].setdefault(variant, {})
        for q in qids:
            scores = by[(variant, q)]
            # Distinct seed offset per (variant, question) so intervals are independent of print order.
            seed_q = (args.bootstrap_seed + 1009 * hash((variant, q, "q")) ) % (2**31 - 1)
            # hash() is salted per process; use a stable offset instead.
            seed_q = _stable_seed(args.bootstrap_seed, variant, q, "question")
            info = percentile_bootstrap_ci(scores, n_boot=args.n_boot, seed=seed_q)
            spread = f"min={min(scores)} median={statistics.median(scores)} max={max(scores)}"
            cat = qcat.get(q, "?")
            print(f"  {q} [{cat}]: scores={scores} {spread} {fmt_ci(info)}")
            summary["per_question"][variant][q] = {
                "category": cat,
                "scores": scores,
                **info,
            }
        print()
        print("### Per category (E / S / C)")
        summary["per_category"].setdefault(variant, {})
        cats = sorted({qcat[q] for q in qids if qcat.get(q)})
        for cat in ("E", "S", "C"):
            if cat not in cats:
                continue
            q_in = [q for q in qids if qcat.get(q) == cat]
            q_means = [sum(by[(variant, q)]) / len(by[(variant, q)]) for q in q_in]
            seed_c = _stable_seed(args.bootstrap_seed, variant, cat, "category")
            info = percentile_bootstrap_ci(q_means, n_boot=args.n_boot, seed=seed_c)
            pass3 = sum(1 for q in q_in if max(by[(variant, q)]) == 2)
            strict3 = sum(1 for q in q_in if min(by[(variant, q)]) == 2)
            print(
                f"  {cat}: questions={len(q_in)} {fmt_ci(info)} "
                f"pass@k={pass3}/{len(q_in)} strict@k={strict3}/{len(q_in)}"
            )
            summary["per_category"][variant][cat] = {
                "questions": q_in,
                "question_means": q_means,
                "pass_at_k": pass3,
                "strict_at_k": strict3,
                **info,
            }
        # Process metrics (not the accuracy headline).
        proc = process.get(variant) or []
        if proc:
            def _nums(field: str) -> list[float]:
                outn = []
                for r in proc:
                    if r.get(field) is not None:
                        try:
                            outn.append(float(r[field]))
                        except (TypeError, ValueError):
                            pass
                return outn

            print()
            print("### Process metrics (not retrieval/localization accuracy)")
            rowp: dict = {}
            for field, label in (
                ("wall_time_s", "wall_time_s"),
                ("tokens_total", "tokens_total"),
                ("tokens_input", "tokens_input"),
                ("tokens_output", "tokens_output"),
                ("tool_calls_total", "tool_calls_total"),
                ("tool_calls_retrieval", "tool_calls_retrieval"),
                ("tool_calls_read", "tool_calls_read"),
            ):
                vals = _nums(field)
                if not vals:
                    print(f"  {label}: n=0")
                    continue
                print(
                    f"  {label}: n={len(vals)} mean={sum(vals)/len(vals):.3f} "
                    f"min={min(vals):.3f} median={statistics.median(vals):.3f} max={max(vals):.3f}"
                )
                rowp[field] = {
                    "n": len(vals),
                    "mean": sum(vals) / len(vals),
                    "min": min(vals),
                    "median": statistics.median(vals),
                    "max": max(vals),
                }
            summary["process"][variant] = rowp
        print()

    print(f"# {METRIC_NAME}")
    print()
    print(
        "No single headline average is reported. Numbers below are per question "
        "and per category (E = exact_lookup, S = semantic, C = cross_file)."
    )
    print(
        f"Bootstrap: percentile 95% CI, n_boot={args.n_boot}, "
        f"seed={args.bootstrap_seed} (plus a stable per-cell offset)."
    )
    print()

    if compared:
        print("# Compared variants")
        print()
        for v in compared:
            report_variant(v, v)

    if controls:
        print("# Controls (`none` = pure memory, `read_only` = read_file only; no retrieval tools)")
        print()
        for v in controls:
            report_variant(v, f"{v} (control)")

    print(
        "Note: the `claude_context` variant in this benchmark uses Ollama "
        "`nomic-embed-text` and a local Milvus standalone. That is a no-cost local "
        "stand-in, not Claude Context's recommended / default configuration "
        "(typically a hosted embedder such as OpenAI or Voyage plus Zilliz Cloud). "
        "Read any table that includes this variant with that caveat."
    )

    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


def _stable_seed(base: int, *parts: str) -> int:
    import hashlib

    h = hashlib.sha256(("::".join(str(p) for p in (base,) + parts)).encode("utf-8")).hexdigest()
    return int(h[:8], 16)


if __name__ == "__main__":
    sys.exit(main())
