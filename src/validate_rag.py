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
The YAML schema is unchanged; optional query_class does not affect scores.

See docs/validation/validation-tests-guide.md for YAML schema and authoring guide.
"""

import sys
import time
import os
import argparse
from typing import List

# Ensure the project root (for `import config`) and src/ (for `import shared`,
# `import config_loader`, etc.) are on sys.path when this script is invoked
# directly as `python src/validate_rag.py` from the project root.
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
for _p in (_root, _here):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared.validation.loader import load_test_cases
from shared.validation.output import get_categories, print_results, output_json
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

    # Load test cases from YAML (config dir, or an external suite path)
    try:
        test_cases = load_test_cases(config_name, yaml_path=yaml_path)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error loading test cases: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.json_output:
        print(
            f"Loaded {len(test_cases)} test cases for {config_name}",
            file=sys.stderr,
        )

    categories = get_categories(test_cases)

    # List mode: just print test cases and exit
    if args.list_tests:
        current_cat = None
        cat_num = 0
        for tc in test_cases:
            if tc.category != current_cat:
                current_cat = tc.category
                cat_num += 1
                print(f"\n  Category {cat_num}: {current_cat}")
            print(f"    {tc.id}  [{tc.difficulty:6s}] [{tc.aspect:8s}] {tc.query}")
        print(f"\n  Total: {len(test_cases)} tests in {len(categories)} categories")
        return

    # Filter test cases
    tests_to_run = list(test_cases)

    if args.test:
        test_id = args.test.upper()
        tests_to_run = [tc for tc in tests_to_run if tc.id == test_id]
        if not tests_to_run:
            print(f"Error: Test ID '{args.test}' not found.", file=sys.stderr)
            all_ids = [tc.id for tc in test_cases]
            print(f"Valid IDs: {all_ids[0]}-{all_ids[-1]}", file=sys.stderr)
            sys.exit(1)

    elif args.category:
        cat_filter = args.category
        try:
            cat_num = int(cat_filter)
            if 1 <= cat_num <= len(categories):
                cat_name = categories[cat_num - 1]
                tests_to_run = [tc for tc in tests_to_run if tc.category == cat_name]
            else:
                print(
                    f"Error: Category number {cat_num} out of range (1-{len(categories)}).",
                    file=sys.stderr,
                )
                sys.exit(1)
        except ValueError:
            # Try matching by name (case-insensitive partial match)
            matches = [
                tc for tc in tests_to_run if cat_filter.lower() in tc.category.lower()
            ]
            if matches:
                tests_to_run = matches
            else:
                print(
                    f"Error: Category '{cat_filter}' not found.",
                    file=sys.stderr,
                )
                print("Available categories:", file=sys.stderr)
                for i, c in enumerate(categories, 1):
                    print(f"  {i}. {c}", file=sys.stderr)
                sys.exit(1)

    # Setup index
    index, mode, alpha, cfg = setup(
        config_name=config_name, alpha_override=args.alpha, overrides=overrides
    )
    top_k = args.top_k
    profiles = rerank_profiles_for_config(cfg)
    print(f"Rerank profiles: {', '.join(profiles.names)}", file=sys.stderr)

    # Run tests
    results: List[TestResult] = []
    total = len(tests_to_run)

    for i, tc in enumerate(tests_to_run, 1):
        if not args.json_output:
            print(
                f"\r  Running {tc.id} ({i}/{total})...",
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
        if args.diag_rank:
            diag_nodes = run_query(
                index,
                mode,
                alpha,
                tc.query,
                top_k=args.diag_rank,
                profiles=profiles,
                cfg=cfg,
            )
            attach_diagnostic(result, diag_nodes, tc.pass_criteria, args.diag_rank)
        result.query_ms = round(query_ms, 1)
        fields = adaptive_result_fields(
            cfg, tc.query, alpha, hybrid=(mode == "hybrid")
        )
        if fields:
            result.query_shape = fields["query_shape"]
            result.alpha = fields["alpha"]
        results.append(result)

    if not args.json_output:
        print("\r" + " " * 40 + "\r", end="", file=sys.stderr, flush=True)

    # Output
    if args.json_output:
        output_json(results, alpha, config_name, test_cases)
    else:
        print_results(results, alpha, config_name, test_cases, verbose=args.verbose)


if __name__ == "__main__":
    main()
