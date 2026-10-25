"""
shared.validation.output -- Result formatting for RAG validation tests.

Terminal table output and JSON export. All functions receive test_cases as
a parameter (no global state).

``build_json_output`` returns the single-language object. ``output_json``
prints it. A ``--lang both`` run reuses that object for each language and
adds the comparison in ``bilingual_payload``. Language keys are present
only when a language was requested.
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
    lang: Optional[str] = None,
):
    """Print formatted test results to stdout.

    Args:
        results: List of TestResult objects.
        alpha: The hybrid alpha value used.
        config_name: Config name string for display.
        test_cases: Full list of TestCase definitions (for criteria display).
        verbose: Show all result nodes even for PASS results.
        lang: Language label for the header. Omitted, the header is unchanged.
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

    header = f"RAG Validation: {total} tests, alpha={alpha:.2f}, index={config_name}"
    if lang:
        header += f", lang={lang}"
    print(header)
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


def build_json_output(
    results: List[TestResult],
    alpha: float,
    config_name: str,
    test_cases: List[TestCase],
    lang: Optional[str] = None,
) -> dict:
    """Build the single-language result object.

    ``lang`` adds a top-level ``lang`` key and a per-test ``lang`` (the
    language actually used, or None for a legacy query). When ``lang`` is
    omitted the object has the same keys as before language selection existed.

    Args:
        results: List of TestResult objects.
        alpha: The hybrid alpha value used.
        config_name: Config name string.
        test_cases: Test definitions that were loaded for this pass.
        lang: Requested language, or None when the CLI flag was absent.

    Returns:
        JSON-serialisable result dict.
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
        tc = tc_by_id.get(r.id)
        entry = {
            "id": r.id,
            "category": r.category,
            "query": r.query,
        }
        if lang is not None:
            entry["lang"] = None if tc is None else tc.lang
        entry["result"] = r.result
        entry["match_position"] = r.match_position
        entry["match_node_type"] = r.match_node_type
        entry["match_file"] = r.match_file
        entry["match_score"] = r.match_score
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
    }
    if lang is not None:
        output["lang"] = lang
    output.update(
        {
            "total_tests": total,
            "pass_count": pass_count,
            "partial_count": partial_count,
            "fail_count": fail_count,
            "score": score,
            "max_score": max_score,
            "score_pct": score_pct,
            "rating": rating,
            "latency_ms": _latency_summary(results),
            "doc_hint_count": sum(
                1 for r in results if r.doc_hint_position is not None
            ),
            "tests": tests_json,
        }
    )
    by_class = query_class_summaries(results, test_cases)
    if by_class:
        output["by_query_class"] = by_class
    return output


def output_json(
    results: List[TestResult],
    alpha: float,
    config_name: str,
    test_cases: List[TestCase],
    lang: Optional[str] = None,
):
    """Output results as JSON to stdout.

    Args:
        results: List of TestResult objects.
        alpha: The hybrid alpha value used.
        config_name: Config name string.
        test_cases: Full list of TestCase definitions (for criteria inclusion).
        lang: Requested language. Omitted, the JSON keys match a legacy run.
    """
    payload = build_json_output(results, alpha, config_name, test_cases, lang)
    print(json.dumps(payload, indent=2))


def _rounded_pct(results: List[TestResult]) -> float:
    """Score percentage rounded to one decimal, matching JSON ``score_pct``."""
    *_, score_pct = _score_counts(results)
    return round(score_pct, 1)


def _query_class_of(result: TestResult, tc_by_id: dict) -> Optional[str]:
    tc = tc_by_id.get(result.id)
    if tc is None:
        return None
    return tc.query_class


def language_delta(
    pl_results: List[TestResult],
    en_results: List[TestResult],
    test_cases: List[TestCase],
) -> dict:
    """EN-minus-PL score deltas, in percentage points, rounded to 1 decimal.

    ``by_query_class`` and ``by_category`` include only groups that have at
    least one result. Values are the difference of the rounded percentages
    each single-language report would show.
    """
    pl_summaries = query_class_summaries(pl_results, test_cases) or {}
    en_summaries = query_class_summaries(en_results, test_cases) or {}
    by_class = {}
    for name in _QUERY_CLASS_ORDER:
        if name not in pl_summaries and name not in en_summaries:
            continue
        pl_pct = pl_summaries.get(name, {}).get("score_pct", 0.0)
        en_pct = en_summaries.get(name, {}).get("score_pct", 0.0)
        by_class[name] = round(en_pct - pl_pct, 1)

    by_category = {}
    for cat in get_categories(test_cases):
        pl_group = [r for r in pl_results if r.category == cat]
        en_group = [r for r in en_results if r.category == cat]
        if not pl_group and not en_group:
            continue
        by_category[cat] = round(_rounded_pct(en_group) - _rounded_pct(pl_group), 1)

    return {
        "score_pct": round(_rounded_pct(en_results) - _rounded_pct(pl_results), 1),
        "by_query_class": by_class,
        "by_category": by_category,
    }


def changed_tests(
    pl_results: List[TestResult],
    en_results: List[TestResult],
    test_cases: List[TestCase],
) -> List[dict]:
    """Tests whose PASS/PARTIAL/FAIL or match position differs across languages."""
    en_by_id = {r.id: r for r in en_results}
    tc_by_id = {tc.id: tc for tc in test_cases}
    rows = []
    for pl in pl_results:
        en = en_by_id.get(pl.id)
        if en is None:
            continue
        if pl.result == en.result and pl.match_position == en.match_position:
            continue
        tc = tc_by_id.get(pl.id)
        rows.append(
            {
                "id": pl.id,
                "query_class": None if tc is None else tc.query_class,
                "pl_result": pl.result,
                "pl_position": pl.match_position,
                "en_result": en.result,
                "en_position": en.match_position,
            }
        )
    return rows


def _fallback_ids(cases: List[TestCase], requested: str) -> List[str]:
    """Ids that used the other language because the requested one was absent."""
    return [tc.id for tc in cases if tc.lang not in (None, requested)]


def bilingual_payload(
    pl_results: List[TestResult],
    en_results: List[TestResult],
    alpha: float,
    config_name: str,
    pl_cases: List[TestCase],
    en_cases: List[TestCase],
) -> dict:
    """Side-by-side JSON object for ``--lang both``.

    ``pl`` and ``en`` are the single-language objects, including their
    ``lang`` keys. Deltas are English minus Polish.
    """
    return {
        "lang": "both",
        "config": config_name,
        "alpha": alpha,
        "pl": build_json_output(pl_results, alpha, config_name, pl_cases, lang="pl"),
        "en": build_json_output(en_results, alpha, config_name, en_cases, lang="en"),
        "delta": language_delta(pl_results, en_results, pl_cases),
        "changed_tests": changed_tests(pl_results, en_results, pl_cases),
        "fallback_tests": {
            "pl": _fallback_ids(pl_cases, "pl"),
            "en": _fallback_ids(en_cases, "en"),
        },
    }


def output_bilingual_json(
    pl_results: List[TestResult],
    en_results: List[TestResult],
    alpha: float,
    config_name: str,
    pl_cases: List[TestCase],
    en_cases: List[TestCase],
):
    """Print the ``--lang both`` JSON object to stdout."""
    payload = bilingual_payload(
        pl_results, en_results, alpha, config_name, pl_cases, en_cases
    )
    print(json.dumps(payload, indent=2))


def _score_phrase(results: List[TestResult]) -> str:
    """One score line: percentage, PASS/PARTIAL/FAIL, and n."""
    total, passed, partial, failed, _score, _max, score_pct = _score_counts(results)
    pct = round(score_pct, 1)
    return (
        f"{pct:.1f}% ({passed} PASS, {partial} PARTIAL, {failed} FAIL, n={total})"
    )


def _result_at(result: str, position: Optional[int]) -> str:
    pos = "-" if position is None else str(position)
    return f"{result}@{pos}"


def print_bilingual_summary(
    pl_results: List[TestResult],
    en_results: List[TestResult],
    alpha: float,
    config_name: str,
    test_cases: List[TestCase],
):
    """Print the side-by-side PL/EN summary. Does not print per-test detail."""
    delta = language_delta(pl_results, en_results, test_cases)
    print(
        f"RAG Validation (lang=both): {len(pl_results)} tests, "
        f"alpha={alpha:.2f}, index={config_name}"
    )
    print("=" * 70)
    print(f"Overall PL: {_score_phrase(pl_results)}")
    print(f"Overall EN: {_score_phrase(en_results)}")
    print(f"Delta (EN-PL): {delta['score_pct']:+.1f} pp")

    tc_by_id = {tc.id: tc for tc in test_cases}
    if delta["by_query_class"]:
        print("Query class:")
        for name, class_delta in delta["by_query_class"].items():
            pl_group = [
                r for r in pl_results if _query_class_of(r, tc_by_id) == name
            ]
            en_group = [
                r for r in en_results if _query_class_of(r, tc_by_id) == name
            ]
            n = len(pl_group) or len(en_group)
            print(f"  {name} n={n}")
            print(f"    PL {_score_phrase(pl_group)}")
            print(f"    EN {_score_phrase(en_group)}")
            print(f"    delta {class_delta:+.1f} pp")

    if delta["by_category"]:
        print("Category:")
        for index, (cat, cat_delta) in enumerate(delta["by_category"].items(), 1):
            pl_group = [r for r in pl_results if r.category == cat]
            en_group = [r for r in en_results if r.category == cat]
            print(f"  {index}. {cat}")
            print(f"    PL {_score_phrase(pl_group)}")
            print(f"    EN {_score_phrase(en_group)}")
            print(f"    delta {cat_delta:+.1f} pp")

    print("Changed tests:")
    rows = changed_tests(pl_results, en_results, test_cases)
    if not rows:
        print("  (none)")
    for row in rows:
        label = row["query_class"] or "-"
        pl_at = _result_at(row["pl_result"], row["pl_position"])
        en_at = _result_at(row["en_result"], row["en_position"])
        print(f"  {row['id']}  {label}  PL {pl_at}  EN {en_at}")
    print("=" * 70)
