#!/usr/bin/env python3
"""Synthetic checks for the v2 grader (file+symbol+span ±N)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade_run import LINE_TOLERANCE, score_one

KEY = {
    "id": "E201",
    "ground_truth": {
        "files": ["django/tasks/base.py"],
        "symbols": ["TASK_MIN_PRIORITY"],
        "spans": [{"file": "django/tasks/base.py", "symbol": "TASK_MIN_PRIORITY", "lines": [20, 20]}],
    },
    "acceptable_alternatives": [],
}


def expect(ans, want, label):
    got = score_one(ans, KEY, n=LINE_TOLERANCE)
    if got != want:
        raise SystemExit(f"FAIL {label}: expected {want} got {got} for {ans}")
    print(f"ok {label} -> {got}")


expect(
    {"files": ["django/tasks/base.py"], "symbols": ["TASK_MIN_PRIORITY"],
     "spans": [{"file": "django/tasks/base.py", "symbol": "TASK_MIN_PRIORITY", "lines": [20, 20]}]},
    2, "exact hit",
)
expect(
    {"files": ["django/tasks/base.py"], "symbols": ["TASK_MIN_PRIORITY"],
     "spans": [{"file": "django/tasks/base.py", "lines": [15, 25]}]},
    2, "within ±10 contained overlap",
)
expect(
    {"files": ["django/tasks/base.py"], "symbols": ["TASK_MIN_PRIORITY"],
     "spans": [{"file": "django/tasks/base.py", "lines": [1, 30]}]},
    1, "range wider than gold±N",
)
expect(
    {"files": ["django/tasks/base.py"], "symbols": ["TASK_MIN_PRIORITY"],
     "spans": [{"file": "django/tasks/base.py", "lines": [40, 50]}]},
    1, "wrong lines same file",
)
expect(
    {"files": ["django/tasks/base.py"], "symbols": ["TASK_MIN_PRIORITY"]},
    1, "file+symbol, no span",
)
expect(
    {"files": ["django/tasks/exceptions.py"], "symbols": ["InvalidTask"],
     "spans": [{"file": "django/tasks/exceptions.py", "lines": [8, 9]}]},
    0, "wrong file",
)
expect({"files": [], "symbols": [], "spans": []}, 0, "empty")
print("all tests passed, N=", LINE_TOLERANCE)
