#!/usr/bin/env python3
"""Build a recorded (question, variant, repetition) run order.

Preferred protocol: shuffle the full Cartesian product with a recorded seed.

If exclusive services (HCR TEI vs Ollama/Milvus) cannot coexist under the
4 GB free-RAM floor, use blocked rotation: shuffle is preserved inside each
service block, and the block order rotates between repetitions.

Default seed: 20261114.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

DEFAULT_SEED = 20261114
DEFAULT_VARIANTS = ["none", "read_only", "ripgrep", "hcr", "claude_context", "serena"]

# Exclusive Docker/embedder services cannot share the 4060 or the RAM budget.
SERVICE_BLOCKS = {
    "light": ["none", "read_only", "ripgrep", "serena"],
    "hcr": ["hcr"],
    "claude_context": ["claude_context"],
}

# Rotation of exclusive blocks across repetitions (1-based).
BLOCK_ROTATIONS = {
    1: ["light", "hcr", "claude_context"],
    2: ["claude_context", "hcr", "light"],
    3: ["hcr", "light", "claude_context"],
}


def load_ids(path: Path) -> list[str]:
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        ids.append(json.loads(line)["id"])
    return ids


def full_shuffle(questions: list[str], variants: list[str], reps: list[int], seed: int) -> list[dict]:
    rng = random.Random(seed)
    triples = [(q, v, r) for q in questions for v in variants for r in reps]
    rng.shuffle(triples)
    return [{"question_id": q, "variant": v, "repetition": r, "block": _block_of(v)} for q, v, r in triples]


def blocked_rotation(
    questions: list[str],
    variants: list[str],
    reps: list[int],
    seed: int,
    skip_variants: list[str] | None = None,
) -> list[dict]:
    """Shuffle all triples, then emit them in per-rep rotated service blocks.

    Relative shuffled order inside a (repetition, block) is kept.
    """
    skip = set(skip_variants or [])
    variants = [v for v in variants if v not in skip]
    shuffled = full_shuffle(questions, variants, reps, seed)
    # Index into the shuffled list so we can take items in shuffled order.
    out: list[dict] = []
    for r in reps:
        names = list(BLOCK_ROTATIONS.get(r, BLOCK_ROTATIONS[1]))
        # Drop empty/skipped blocks, keep rotation of what remains.
        names = [n for n in names if any(v in SERVICE_BLOCKS[n] for v in variants)]
        for name in names:
            allowed = set(SERVICE_BLOCKS[name])
            chunk = [t for t in shuffled if t["repetition"] == r and t["variant"] in allowed]
            out.extend(chunk)
    # Anything not in a known block (shouldn't happen) is appended in shuffled order.
    seen = {(t["question_id"], t["variant"], t["repetition"]) for t in out}
    for t in shuffled:
        key = (t["question_id"], t["variant"], t["repetition"])
        if key not in seen:
            out.append(t)
    return out


def _block_of(variant: str) -> str:
    for name, members in SERVICE_BLOCKS.items():
        if variant in members:
            return name
    return "other"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", required=True)
    ap.add_argument("--variants", nargs="+", default=DEFAULT_VARIANTS)
    ap.add_argument("--repetitions", type=int, default=1)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument(
        "--mode",
        choices=["full_shuffle", "blocked_rotation"],
        default="blocked_rotation",
        help="full_shuffle if services can be interleaved; blocked_rotation when RAM forces exclusive stacks.",
    )
    ap.add_argument("--skip-variant", action="append", default=[], help="Drop a variant (e.g. claude_context if Milvus is RAM-blocked).")
    ap.add_argument("--out", required=True, help="Write the recorded schedule JSON here.")
    args = ap.parse_args()
    questions = load_ids(Path(args.questions))
    reps = list(range(1, args.repetitions + 1))
    if args.mode == "full_shuffle":
        items = full_shuffle(questions, args.variants, reps, args.seed)
    else:
        items = blocked_rotation(questions, args.variants, reps, args.seed, skip_variants=args.skip_variant)
    # Assign 1-based run order.
    for i, item in enumerate(items, 1):
        item["order"] = i
    doc = {
        "seed": args.seed,
        "mode": args.mode,
        "variants": args.variants,
        "skip_variants": args.skip_variant,
        "repetitions": args.repetitions,
        "n_runs": len(items),
        "block_rotations": BLOCK_ROTATIONS,
        "service_blocks": SERVICE_BLOCKS,
        "reason": (
            "Preferred protocol is a full shuffle of (question, variant, repetition) "
            "with this seed. blocked_rotation is used when HCR (TEI/Qdrant) and "
            "claude_context (Ollama nomic + Milvus) cannot stay up together without "
            "breaking the 4 GB free-RAM floor, and when switching stacks per run "
            "would dominate the 180 s budget. Light variants (none, read_only, ripgrep, serena) "
            "stay interleaved inside the light block. Block order rotates across "
            "repetitions as in block_rotations."
        ),
        "items": items,
    }
    Path(args.out).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out} mode={args.mode} seed={args.seed} n={len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
