"""
validate_rag.py -- Automated RAG validation test runner.

Loads per-config test cases from YAML files in project-configs/<config>/
and evaluates retrieval results against pass criteria.

Usage:
    python src/validate_rag.py --config config_informica_tei_jinaai
    python src/validate_rag.py --config config_epodroznik
    python src/validate_rag.py --config config_informica_tei_jinaai --category 1
    python src/validate_rag.py --config config_informica_tei_jinaai --test T01
    python src/validate_rag.py --config config_informica_tei_jinaai --alpha 0.7 --verbose
    python src/validate_rag.py --config config_informica_tei_jinaai --json

Test cases are defined in:
    project-configs/<config_name>/validation_tests.yaml

See docs/validation-tests-guide.md for YAML schema and authoring guide.
"""

import sys
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
from shared.validation.runner import setup, run_query, evaluate_test
from shared.validation.models import TestCase, TestResult


def main():
    parser = argparse.ArgumentParser(
        description="Automated RAG validation test runner",
        epilog="Test cases are loaded from project-configs/<config>/validation_tests.yaml",
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Config name (e.g. config_informica_tei_jinaai, config_epodroznik)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=None,
        help="Override HYBRID_ALPHA (0.0=BM25 only, 1.0=dense only)",
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
    args = parser.parse_args()

    config_name = args.config

    # Load test cases from YAML
    try:
        test_cases = load_test_cases(config_name)
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
    index, mode, alpha, cfg = setup(config_name=config_name, alpha_override=args.alpha)
    top_k = args.top_k

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

        nodes = run_query(index, mode, alpha, tc.query, top_k=top_k)
        result = evaluate_test(tc, nodes, top_k=top_k)
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
