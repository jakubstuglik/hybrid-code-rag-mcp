"""
shared.validation -- Reusable RAG validation test infrastructure.

Provides data structures, YAML test loading, query evaluation, and output
formatting for per-config RAG validation test suites.

Modules:
    models  -- PassCriteria, TestCase, TestResult dataclasses
    loader  -- YAML test definition loading
    runner  -- Query setup, execution, evaluation logic
    output  -- Terminal and JSON result formatting
"""

from shared.validation.models import PassCriteria, TestCase, TestResult
from shared.validation.loader import load_test_cases

__all__ = ["PassCriteria", "TestCase", "TestResult", "load_test_cases"]
