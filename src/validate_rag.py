"""
validate_rag.py -- Automated RAG validation test runner.

Loads per-config test cases from YAML files in project-configs/<config>/
and evaluates retrieval results against pass criteria.

Usage:
    python src/validate_rag.py --config config_myproject
    python src/validate_rag.py --config config_another_project
    python src/validate_rag.py --config config_myproject --category 1
    python src/validate_rag.py --config config_myproject --test T01
    python src/validate_rag.py --config config_myproject --alpha 0.7 --verbose
    python src/validate_rag.py --config config_myproject --json

Test cases are defined in:
    project-configs/<config_name>/validation_tests.yaml

Or pass --tests PATH to load a suite that lives outside this repository.
--config still selects the index. When --tests is omitted and the config sets
VALIDATION_TESTS_FILE to an absolute path, that file is used instead.

A test has either a legacy language-neutral ``query`` or ``query_pl`` /
``query_en``. ``--lang pl|en`` scores that language. ``--lang both`` scores
both against one index and prints the comparison. ``--strict-lang`` fails
when any test lacks either language. Omitting ``--lang`` keeps the previous
report for a legacy suite. Optional query_class does not affect scores.

See docs/validation/validation-tests-guide.md for YAML schema and authoring guide.
"""

import sys
import time
import os
import argparse
from typing import List, Optional

# Ensure the project root (for `import config`) and src/ (for `import shared`,
# `import config_loader`, etc.) are on sys.path when this script is invoked
# directly as `python src/validate_rag.py` from the project root.
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
for _p in (_root, _here):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared.validation.loader import load_test_cases
from shared.validation.output import (
    get_categories,
    output_bilingual_json,
    output_json,
    print_bilingual_summary,
    print_results,
)
from shared.reranker import rerank_profiles_for_config
from shared.query_shape import adaptive_result_fields
from shared.validation.runner import (
    attach_diagnostic,
    setup,
    run_query,
    evaluate_test,
    parse_overrides,
)
from shared.validation.models import TestCase, TestResult


def _configured_validation_tests_file(config_name: str):
    """Return VALIDATION_TESTS_FILE when the project config sets it.

    A missing config, or a blank/absent key, returns None so the validator
    keeps loading project-configs/<config>/validation_tests.yaml.
    """
    try:
        import config_loader

        cfg = config_loader.get_config(config_name=config_name)
    except Exception:
        return None
    raw = getattr(cfg, "VALIDATION_TESTS_FILE", None)
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _load_cases(config_name: str, yaml_path, lang, strict_lang: bool):
    """Load a suite or exit 1 with the error on stderr."""
    try:
        return load_test_cases(
            config_name,
            yaml_path=yaml_path,
            lang=lang,
            strict_lang=strict_lang,
        )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error loading test cases: {e}", file=sys.stderr)
        sys.exit(1)


def _note_legacy_both(test_cases: List[TestCase]) -> None:
    """Stderr note when --lang both has nothing language-specific to compare."""
    if any(tc.query_pl or tc.query_en for tc in test_cases):
        return
    print(
        "Note: suite has no language-specific queries; both passes use the same text.",
        file=sys.stderr,
    )


def _list_line(tc: TestCase, show_both: bool) -> str:
    """One --list row. Legacy rows stay in the previous format."""
    langs = []
    if tc.query_pl:
        langs.append("pl")
    if tc.query_en:
        langs.append("en")
    tag = f" [{','.join(langs)}]" if langs else ""
    if show_both and (tc.query_pl or tc.query_en):
        parts = []
        if tc.query_pl:
            parts.append(f"PL: {tc.query_pl}")
        if tc.query_en:
            parts.append(f"EN: {tc.query_en}")
        text = " | ".join(parts)
    else:
        text = tc.query
    return f"    {tc.id}  [{tc.difficulty:6s}] [{tc.aspect:8s}]{tag} {text}"


def _print_test_list(test_cases: List[TestCase], show_both: bool) -> None:
    categories = get_categories(test_cases)
    current_cat = None
    cat_num = 0
    for tc in test_cases:
        if tc.category != current_cat:
            current_cat = tc.category
            cat_num += 1
            print(f"\n  Category {cat_num}: {current_cat}")
        print(_list_line(tc, show_both))
    total = len(test_cases)
    print(f"\n  Total: {total} tests in {len(categories)} categories")


def _filter_tests(test_cases: List[TestCase], category_arg, test_arg):
    """Apply --test / --category. --test wins, matching the previous CLI."""
    categories = get_categories(test_cases)
    tests_to_run = list(test_cases)
    if test_arg:
        test_id = test_arg.upper()
        tests_to_run = [tc for tc in tests_to_run if tc.id == test_id]
        if not tests_to_run:
            print(f"Error: Test ID '{test_arg}' not found.", file=sys.stderr)
            all_ids = [tc.id for tc in test_cases]
            print(f"Valid IDs: {all_ids[0]}-{all_ids[-1]}", file=sys.stderr)
            sys.exit(1)
        return tests_to_run

    if not category_arg:
        return tests_to_run

    cat_filter = category_arg
    try:
        cat_num = int(cat_filter)
        if 1 <= cat_num <= len(categories):
            cat_name = categories[cat_num - 1]
            return [tc for tc in tests_to_run if tc.category == cat_name]
        print(
            f"Error: Category number {cat_num} out of range (1-{len(categories)}).",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError:
        matches = [
            tc for tc in tests_to_run if cat_filter.lower() in tc.category.lower()
        ]
        if matches:
            return matches
        print(f"Error: Category '{cat_filter}' not found.", file=sys.stderr)
        print("Available categories:", file=sys.stderr)
        for i, cat_name in enumerate(categories, 1):
            print(f"  {i}. {cat_name}", file=sys.stderr)
        sys.exit(1)


def _run_tests(
    tests_to_run: List[TestCase],
    index,
    mode,
    alpha,
    cfg,
    profiles,
    top_k: int,
    diag_rank: Optional[int],
    json_output: bool,
    label: Optional[str] = None,
) -> List[TestResult]:
    """Score one pass. ``label`` is a stderr progress prefix (``pl`` / ``en``)."""
    results: List[TestResult] = []
    total = len(tests_to_run)
    prefix = f"{label} " if label else ""
    for i, tc in enumerate(tests_to_run, 1):
        if not json_output:
            print(
                f"\r  Running {prefix}{tc.id} ({i}/{total})...",
                end="",
                file=sys.stderr,
                flush=True,
            )

        t0 = time.perf_counter()
        nodes = run_query(
            index, mode, alpha, tc.query, top_k=top_k, profiles=profiles, cfg=cfg
        )
        query_ms = (time.perf_counter() - t0) * 1000.0
        result = evaluate_test(tc, nodes, top_k=top_k)
        # Diagnostic fetch is a second call. Raising top_k on the scored call
        # would widen overview over-fetch, the cross-encoder pool and symbol
        # merge, which can reorder the scored top-k.
        if diag_rank:
            diag_nodes = run_query(
                index,
                mode,
                alpha,
                tc.query,
                top_k=diag_rank,
                profiles=profiles,
                cfg=cfg,
            )
            attach_diagnostic(result, diag_nodes, tc.pass_criteria, diag_rank)
        result.query_ms = round(query_ms, 1)
        fields = adaptive_result_fields(
            cfg, tc.query, alpha, hybrid=(mode == "hybrid")
        )
        if fields:
            result.query_shape = fields["query_shape"]
            result.alpha = fields["alpha"]
        results.append(result)

    if not json_output:
        print("\r" + " " * 40 + "\r", end="", file=sys.stderr, flush=True)
    return results


def _prepare_index(config_name: str, alpha_override, overrides):
    """Open the index once and print the active rerank profiles."""
    index, mode, alpha, cfg = setup(
        config_name=config_name, alpha_override=alpha_override, overrides=overrides
    )
    profiles = rerank_profiles_for_config(cfg)
    print(f"Rerank profiles: {', '.join(profiles.names)}", file=sys.stderr)
    return index, mode, alpha, cfg, profiles


def main():
    parser = argparse.ArgumentParser(
        description="Automated RAG validation test runner",
        epilog=(
            "Test cases load from project-configs/<config>/validation_tests.yaml, "
            "or from --tests PATH when the suite lives outside this repository."
        ),
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Config name (e.g. config_myproject, config_another_project)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=None,
        help=(
            "Override HYBRID_ALPHA (0.0=BM25 only, 1.0=dense only). "
            "In fixed mode this is the alpha for every query. In adaptive "
            "mode it replaces HYBRID_ALPHA as the base for mixed and "
            "natural-language queries when HYBRID_ALPHA_MIXED / "
            "HYBRID_ALPHA_NL are unset; HYBRID_ALPHA_IDENT is unchanged."
        ),
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=8,
        help="Override default top_k (default: 8)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Run only specific category by number or name",
    )
    parser.add_argument(
        "--test",
        type=str,
        default=None,
        help="Run only specific test by ID (T01, T02, etc.)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all result nodes even for PASS results",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON for programmatic use",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_tests",
        help="List all test cases without running them",
    )
    parser.add_argument(
        "--tests",
        type=str,
        default=None,
        help=(
            "Path to a validation YAML file. When set, cases are loaded from "
            "this file instead of project-configs/<config>/validation_tests.yaml. "
            "--config still selects the index to query. When omitted, "
            "VALIDATION_TESTS_FILE on the config is used if set."
        ),
    )
    parser.add_argument(
        "--diag-rank",
        type=int,
        default=None,
        metavar="N",
        help=(
            "After the scored search, run a separate search of N results and "
            "record diag_rank (1-based full criteria match, or null) plus "
            "diag_top3_files. Does not change scored results: a larger fetch "
            "can change fusion and rerank pools, so this is an extra call."
        ),
    )
    parser.add_argument(
        "--lang",
        choices=("pl", "en", "both"),
        default=None,
        help=(
            "Score Polish (pl), English (en), or both languages side by side. "
            "Omitted: legacy query text, or query_en when a bilingual test has one."
        ),
    )
    parser.add_argument(
        "--strict-lang",
        action="store_true",
        help=(
            "Fail if any test lacks query_pl or query_en, or if test ids are "
            "duplicated. With --list, lint the suite without opening an index."
        ),
    )
    parser.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Override a config value for this run (repeatable), e.g. "
            "--set HYBRID_PREFETCH_K=20. VALUE is parsed as a Python literal."
        ),
    )
    args = parser.parse_args()
    try:
        overrides = parse_overrides(args.overrides)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    if args.diag_rank is not None and args.diag_rank < 1:
        print("Error: --diag-rank must be >= 1", file=sys.stderr)
        sys.exit(2)

    config_name = args.config

    # --tests wins. Otherwise an absolute VALIDATION_TESTS_FILE on the config
    # selects the suite. Absent key keeps the config-directory default.
    yaml_path = args.tests
    if not yaml_path:
        yaml_path = _configured_validation_tests_file(config_name)

    # --list, and any single-language run, load once. --lang both (a real run)
    # loads Polish and English separately so each pass has its own query.
    if args.list_tests or args.lang != "both":
        load_lang = None if args.lang == "both" else args.lang
        test_cases = _load_cases(
            config_name, yaml_path, load_lang, args.strict_lang
        )
        if not args.json_output:
            print(
                f"Loaded {len(test_cases)} test cases for {config_name}",
                file=sys.stderr,
            )
        if args.lang == "both":
            _note_legacy_both(test_cases)
        if args.list_tests:
            _print_test_list(test_cases, show_both=(args.lang == "both"))
            return

        tests_to_run = _filter_tests(test_cases, args.category, args.test)
        index, mode, alpha, cfg, profiles = _prepare_index(
            config_name, args.alpha, overrides
        )
        results = _run_tests(
            tests_to_run,
            index,
            mode,
            alpha,
            cfg,
            profiles,
            args.top_k,
            args.diag_rank,
            args.json_output,
        )
        if args.json_output:
            output_json(results, alpha, config_name, test_cases, lang=args.lang)
        else:
            print_results(
                results,
                alpha,
                config_name,
                test_cases,
                verbose=args.verbose,
                lang=args.lang,
            )
        return

    cases_pl = _load_cases(config_name, yaml_path, "pl", args.strict_lang)
    cases_en = _load_cases(config_name, yaml_path, "en", args.strict_lang)
    if not args.json_output:
        print(
            f"Loaded {len(cases_pl)} test cases for {config_name}",
            file=sys.stderr,
        )
    _note_legacy_both(cases_pl)
    cases_pl = _filter_tests(cases_pl, args.category, args.test)
    cases_en = _filter_tests(cases_en, args.category, args.test)
    index, mode, alpha, cfg, profiles = _prepare_index(
        config_name, args.alpha, overrides
    )
    pl_results = _run_tests(
        cases_pl,
        index,
        mode,
        alpha,
        cfg,
        profiles,
        args.top_k,
        args.diag_rank,
        args.json_output,
        label="pl",
    )
    en_results = _run_tests(
        cases_en,
        index,
        mode,
        alpha,
        cfg,
        profiles,
        args.top_k,
        args.diag_rank,
        args.json_output,
        label="en",
    )
    if args.json_output:
        output_bilingual_json(
            pl_results, en_results, alpha, config_name, cases_pl, cases_en
        )
    else:
        if args.verbose:
            print_results(
                pl_results,
                alpha,
                config_name,
                cases_pl,
                verbose=True,
                lang="pl",
            )
            print_results(
                en_results,
                alpha,
                config_name,
                cases_en,
                verbose=True,
                lang="en",
            )
        print_bilingual_summary(
            pl_results, en_results, alpha, config_name, cases_pl
        )


if __name__ == "__main__":
    main()
