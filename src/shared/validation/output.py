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
    total = len(results)
    pass_count = sum(1 for r in results if r.result == "PASS")
    partial_count = sum(1 for r in results if r.result == "PARTIAL")
    fail_count = sum(1 for r in results if r.result == "FAIL")

    # Score: PASS=2, PARTIAL=1, FAIL=0
    score = pass_count * 2 + partial_count * 1
    max_score = total * 2
    score_pct = (score / max_score * 100) if max_score > 0 else 0.0
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
    print(f"Rating: {rating}")
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
    total = len(results)
    pass_count = sum(1 for r in results if r.result == "PASS")
    partial_count = sum(1 for r in results if r.result == "PARTIAL")
    fail_count = sum(1 for r in results if r.result == "FAIL")

    score = pass_count * 2 + partial_count * 1
    max_score = total * 2
    score_pct = round(score / max_score * 100, 1) if max_score > 0 else 0.0
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
        "tests": tests_json,
    }

    print(json.dumps(output, indent=2))
