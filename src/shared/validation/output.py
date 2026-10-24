"""
shared.validation.output -- Result formatting for RAG validation tests.

Terminal table output and JSON export. All functions receive test_cases as
a parameter (no global state).
"""

import os
import json
from typing import List, Optional

from shared.validation.models import TestCase, TestResult


# ────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────


def _truncate(s: str, max_len: int) -> str:
    """Truncate a string to max_len, adding ellipsis if needed."""
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def _get_rating(score_pct: float) -> str:
    """Get a rating string from the score percentage."""
    if score_pct >= 95:
        return "Outstanding"
    elif score_pct >= 90:
        return "Excellent"
    elif score_pct >= 80:
        return "Good"
    elif score_pct >= 70:
        return "Acceptable"
    elif score_pct >= 60:
        return "Needs Improvement"
    else:
        return "Poor"


_QUERY_CLASS_ORDER = ("semantic", "exact", "mixed")


def _score_counts(results: List[TestResult]):
    """PASS=2, PARTIAL=1, FAIL=0. Returns counts and the percentage."""
    total = len(results)
    pass_count = sum(1 for r in results if r.result == "PASS")
    partial_count = sum(1 for r in results if r.result == "PARTIAL")
    fail_count = sum(1 for r in results if r.result == "FAIL")
    score = pass_count * 2 + partial_count
    max_score = total * 2
    score_pct = (score / max_score * 100) if max_score > 0 else 0.0
    return total, pass_count, partial_count, fail_count, score, max_score, score_pct


def query_class_summaries(
    results: List[TestResult], test_cases: List[TestCase]
) -> Optional[dict]:
    """Per-class score rows, or None when no test has a query_class.

    Only tests that were actually run are counted. Classes with n=0 are
    omitted. Unclassified tests stay out of every bucket.
    """
    tc_by_id = {tc.id: tc for tc in test_cases}
    buckets = {name: [] for name in _QUERY_CLASS_ORDER}
    any_set = False
    for result in results:
        tc = tc_by_id.get(result.id)
        label = tc.query_class if tc is not None else None
        if label in buckets:
            buckets[label].append(result)
            any_set = True
    if not any_set:
        return None
    out = {}
    for name in _QUERY_CLASS_ORDER:
        group = buckets[name]
        if not group:
            continue
        total, pass_count, partial_count, fail_count, score, max_score, score_pct = (
            _score_counts(group)
        )
        out[name] = {
            "n": total,
            "pass_count": pass_count,
            "partial_count": partial_count,
            "fail_count": fail_count,
            "score": score,
            "max_score": max_score,
            "score_pct": round(score_pct, 1),
        }
    return out


def get_categories(test_cases: List[TestCase]) -> List[str]:
    """Derive ordered category list from test cases (by first appearance)."""
    categories = []
    seen = set()
    for tc in test_cases:
        if tc.category not in seen:
            categories.append(tc.category)
            seen.add(tc.category)
    return categories


# ────────────────────────────────────────────────────────────────────
# Terminal output
# ────────────────────────────────────────────────────────────────────


def print_results(
    results: List[TestResult],
    alpha: float,
    config_name: str,
    test_cases: List[TestCase],
    verbose: bool = False,
):
    """Print formatted test results to stdout.

    Args:
        results: List of TestResult objects.
        alpha: The hybrid alpha value used.
        config_name: Config name string for display.
        test_cases: Full list of TestCase definitions (for criteria display).
        verbose: Show all result nodes even for PASS results.
    """
    (
        total,
        pass_count,
        partial_count,
        fail_count,
        score,
        max_score,
        score_pct,
    ) = _score_counts(results)
    rating = _get_rating(score_pct)

    categories = get_categories(test_cases)

    # Build lookup for test case criteria display
    tc_by_id = {tc.id: tc for tc in test_cases}

    print(f"RAG Validation: {total} tests, alpha={alpha:.2f}, index={config_name}")
    print("=" * 70)

    current_category = None
    cat_num = 0
    for r in results:
        if r.category != current_category:
            current_category = r.category
            cat_num += 1
            print(f"\n  Category {cat_num}: {current_category}")

        # Status indicator
        if r.result == "PASS":
            status = "PASS  "
        elif r.result == "PARTIAL":
            status = "PARTIAL"
        else:
            status = "FAIL  "

        # Position / node_type / file info
        if r.match_position is not None:
            pos_str = f"[#{r.match_position}]"
            ntype = r.match_node_type or "?"
            fname = os.path.basename(r.match_file) if r.match_file else "?"
            query_display = _truncate(r.query, 50)
            print(
                f'    {r.id}  {status} {pos_str:5s} {ntype:25s} {fname:30s} "{query_display}"'
            )
        else:
            query_display = _truncate(r.query, 50)
            print(f'    {r.id}  {status}       {"":25s} {"":30s} "{query_display}"')

        # Detail for FAIL and PARTIAL
        if r.result in ("FAIL", "PARTIAL"):
            tc = tc_by_id.get(r.id)
            if tc:
                criteria = tc.pass_criteria
                expected_parts = []
                if criteria.file_pattern:
                    expected_parts.append(f"file_path~/{criteria.file_pattern}/")
                if criteria.node_types:
                    expected_parts.append(
                        f"node_type in {{{', '.join(criteria.node_types)}}}"
                    )
                if criteria.text_pattern:
                    expected_parts.append(f"text~/{criteria.text_pattern}/")
                if criteria.class_name_pattern:
                    expected_parts.append(f"class_name~/{criteria.class_name_pattern}/")
                if criteria.multi_file:
                    expected_parts.append("multi_file>=2")
                print(f"           Expected: {', '.join(expected_parts)}")

            if r.detail:
                print(f"           Reason: {r.detail}")

            # Show top nodes
            if r.all_nodes:
                for ni in r.all_nodes[:3]:
                    fname = (
                        os.path.basename(ni["file_path"])
                        if ni["file_path"] != "?"
                        else "?"
                    )
                    score_str = (
                        f"score={ni['score']:.4f}"
                        if ni["score"] is not None
                        else "score=?"
                    )
                    print(
                        f"           Got [#{ni['position']}]: {ni['node_type']:25s} "
                        f"{fname:30s} {score_str}"
                    )

        # Verbose: show all nodes even for PASS
        if verbose and r.result == "PASS" and r.all_nodes:
            for ni in r.all_nodes:
                fname = (
                    os.path.basename(ni["file_path"]) if ni["file_path"] != "?" else "?"
                )
                score_str = (
                    f"score={ni['score']:.4f}" if ni["score"] is not None else "score=?"
                )
                marker = " <-- MATCH" if ni["position"] == r.match_position else ""
                print(
                    f"           [#{ni['position']}]: {ni['node_type']:25s} "
                    f"{fname:30s} {score_str}{marker}"
                )

    # Summary
    print()
    print("=" * 70)
    print(f"Results: {pass_count} PASS, {partial_count} PARTIAL, {fail_count} FAIL")
    print(f"Score:  {score_pct:5.1f}%  ({score} / {max_score} points)")
    non_pass = total - pass_count
    doc_hints = sum(1 for r in results if r.doc_hint_position is not None)
    if non_pass:
        print(f"Doc hints: {doc_hints} of {non_pass} non-PASS tests have a doc chunk in top-k naming the expected file/symbol")
    print(f"Rating: {rating}")
    by_class = query_class_summaries(results, test_cases)
    if by_class:
        print("Query class:")
        for name, row in by_class.items():
            print(
                f"  {name:10s} {row['score_pct']:5.1f}%  "
                f"({row['pass_count']} PASS, {row['partial_count']} PARTIAL, "
                f"{row['fail_count']} FAIL, n={row['n']})"
            )
    print("=" * 70)

    # Category summary
    print()
    print("Category Summary:")
    for cat_idx, cat_name in enumerate(categories, 1):
        cat_results = [r for r in results if r.category == cat_name]
        cat_pass = sum(1 for r in cat_results if r.result == "PASS")
        cat_partial = sum(1 for r in cat_results if r.result == "PARTIAL")
        cat_fail = sum(1 for r in cat_results if r.result == "FAIL")
        cat_total = len(cat_results)

        details = []
        if cat_partial > 0:
            details.append(f"{cat_partial} PARTIAL")
        if cat_fail > 0:
            details.append(f"{cat_fail} FAIL")
        detail_str = f"  ({', '.join(details)})" if details else ""

        print(
            f"  {cat_idx}. {cat_name + ':':40s} {cat_pass}/{cat_total} PASS{detail_str}"
        )

    print()


# ────────────────────────────────────────────────────────────────────
# JSON output
# ────────────────────────────────────────────────────────────────────


def _latency_summary(results: List[TestResult]) -> Optional[dict]:
    """p50 / p95 / mean of per-query wall time, or None when not measured."""
    vals = sorted(r.query_ms for r in results if r.query_ms is not None)
    if not vals:
        return None

    def pct(p: float) -> float:
        idx = min(len(vals) - 1, max(0, int(round(p / 100.0 * len(vals) + 0.5)) - 1))
        return round(vals[idx], 1)

    return {
        "p50": pct(50),
        "p95": pct(95),
        "mean": round(sum(vals) / len(vals), 1),
        "n": len(vals),
    }


def output_json(
    results: List[TestResult],
    alpha: float,
    config_name: str,
    test_cases: List[TestCase],
):
    """Output results as JSON to stdout.

    Args:
        results: List of TestResult objects.
        alpha: The hybrid alpha value used.
        config_name: Config name string.
        test_cases: Full list of TestCase definitions (for criteria inclusion).
    """
    (
        total,
        pass_count,
        partial_count,
        fail_count,
        score,
        max_score,
        score_pct,
    ) = _score_counts(results)
    score_pct = round(score_pct, 1)
    rating = _get_rating(score_pct)

    tc_by_id = {tc.id: tc for tc in test_cases}

    tests_json = []
    for r in results:
        entry = {
            "id": r.id,
            "category": r.category,
            "query": r.query,
            "result": r.result,
            "match_position": r.match_position,
            "match_node_type": r.match_node_type,
            "match_file": r.match_file,
            "match_score": r.match_score,
        }
        if r.detail:
            entry["detail"] = r.detail
        if r.query_ms is not None:
            entry["query_ms"] = r.query_ms
        # Per-test alpha and shape are recorded only in adaptive mode
        # (the runner leaves them None otherwise, so fixed-mode JSON
        # keeps its previous keys).
        if r.alpha is not None:
            entry["alpha"] = r.alpha
        if r.query_shape is not None:
            entry["query_shape"] = r.query_shape
        if r.doc_hint_position is not None:
            entry["doc_hint_position"] = r.doc_hint_position
        if r.diag_top3_files is not None:
            entry["diag_rank"] = r.diag_rank
            entry["diag_top3_files"] = r.diag_top3_files
        if r.all_nodes:
            entry["all_nodes"] = r.all_nodes
        tc = tc_by_id.get(r.id)
        if tc:
            criteria = tc.pass_criteria
            entry["criteria"] = {
                "node_types": criteria.node_types,
                "file_pattern": criteria.file_pattern,
                "text_pattern": criteria.text_pattern,
                "max_position": criteria.max_position,
                "partial_position": criteria.partial_position,
                "class_name_pattern": criteria.class_name_pattern,
                "multi_file": criteria.multi_file,
            }
            entry["description"] = tc.description
            entry["difficulty"] = tc.difficulty
            entry["aspect"] = tc.aspect
            if tc.query_class:
                entry["query_class"] = tc.query_class
        tests_json.append(entry)

    output = {
        "alpha": alpha,
        "config": config_name,
        "total_tests": total,
        "pass_count": pass_count,
        "partial_count": partial_count,
        "fail_count": fail_count,
        "score": score,
        "max_score": max_score,
        "score_pct": score_pct,
        "rating": rating,
        "latency_ms": _latency_summary(results),
        "doc_hint_count": sum(1 for r in results if r.doc_hint_position is not None),
        "tests": tests_json,
    }
    by_class = query_class_summaries(results, test_cases)
    if by_class:
        output["by_query_class"] = by_class

    print(json.dumps(output, indent=2))
