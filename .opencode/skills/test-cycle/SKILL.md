---
name: test-cycle
description: Multi-agent test generation, validation, and execution cycle. Invoke after code changes to generate or update unit tests, validate them, run them, and iterate until all tests pass.
---

# Test Cycle Skill

You are orchestrating a multi-agent test cycle. This skill defines a repeatable
workflow for generating, validating, running, and fixing tests after code changes.

## When to Use

- After creating or modifying any Python module in this project
- When the user asks to add or update tests
- After refactoring that may break existing tests
- As part of a change cycle: code change -> test cycle -> commit

## Prerequisites

- **pytest** and **pytest-cov** must be installed (`uv pip install -r requirements/requirements_dev.txt`)
- Test files live in `src_test/` and follow the naming convention `test_<module>.py`
- The `pytest.ini` at project root configures test discovery and coverage

## Important: numpy/coverage Conflict

The `shared/__init__.py` imports heavy dependencies (llama_index, numpy). When
pytest-cov instruments early, numpy can fail with "cannot load module more than
once per process". Workarounds:

- Use `import shared.log` not `from shared import log` in test files (avoid
  triggering `shared/__init__.py` when possible)
- For coverage runs, use `--cov` (no module arg) instead of `--cov=shared.log`
  to avoid early instrumentation conflicts
- Run plain `pytest` first (fast), only add `--cov` for the final passing run

## Multi-Agent Flow

Execute these phases sequentially. Each phase is a Task sub-agent with a specific
role. You (the orchestrator) review each agent's output before proceeding.

### Phase 1: GENERATE (Agent: explore or general)

**Role:** Test author. Generates or updates the test file for the target module.

**Input to agent:**
- The full source code of the module under test
- The existing test file (if any)
- What changed (new functions, modified behavior, bug fixes)
- Project test conventions (see below)

**Agent instructions:**
```
You are a test generation agent. Your job is to write comprehensive pytest unit
tests for the given Python module.

Rules:
1. Read the module source carefully. Test EVERY public function and class.
2. Test categories (use these as test class names):
   - TestConfigure, TestFunctionName, etc. — one class per public function/class
   - TestEdgeCases — empty inputs, None, special chars, unicode, very long strings
   - TestFlush — verify flush=True behavior (if applicable)
   - TestIsolation — module state reset, no side effects between tests
   - TestIntegration — combined usage of multiple functions
3. Use fixtures with autouse for state reset (e.g., redirect output to StringIO)
4. Use `import shared.log as log_module` NOT `from shared import log` (avoids
   triggering shared/__init__.py and the numpy coverage conflict)
5. Each test must have a docstring explaining what it verifies
6. Use unittest.mock.patch sparingly — only for verifying call arguments (flush)
7. Never import heavy dependencies (llama_index, qdrant, etc.) in unit tests
8. Follow project style: 4-space indent, snake_case, type hints in signatures
9. Target 100% line coverage of the module under test
```

**Output:** The complete test file content.

### Phase 2: VALIDATE (Agent: general)

**Role:** Test reviewer. Reviews the generated tests for correctness and completeness.

**Input to agent:**
- The module source code
- The generated test file
- The project test conventions

**Agent instructions:**
```
You are a test validation agent. Review the test file for quality issues.

Check for:
1. CORRECTNESS: Do assertions match the actual module behavior? Any false positives
   (tests that pass but don't actually verify anything)?
2. COMPLETENESS: Is every public function tested? Every code path? Every branch?
   Are edge cases covered (empty input, None, special chars, boundaries)?
3. ISOLATION: Does each test clean up after itself? Are there shared mutable state
   issues? Will test order affect results?
4. CONVENTIONS: Does the test file follow project style? Proper imports? No heavy
   deps? Docstrings on every test?
5. FRAGILITY: Are there time-dependent tests that could flake? Tests that depend
   on execution speed or system locale?
6. REDUNDANCY: Are there duplicate tests that verify the same thing?

Return a structured report:
- PASS: No issues found, tests are ready to run
- ISSUES: List each issue with severity (CRITICAL/WARN) and fix instruction
```

**Output:** Validation report. If ISSUES found, return to Phase 1 with fixes.

### Phase 3: RUN (Orchestrator runs directly via Bash)

Do NOT delegate this to a sub-agent. Run it yourself:

```bash
# Step 1: Quick syntax check
python -m py_compile src_test/test_<module>.py

# Step 2: Run tests (no coverage, fast)
.venv\Scripts\python -m pytest src_test/test_<module>.py -v --tb=short

# Step 3: If all pass, run with coverage
.venv\Scripts\python -m pytest src_test/test_<module>.py --cov --cov-report=term-missing -v --tb=short
```

**Output:** Test results and coverage report.

### Phase 4: ANALYZE (Agent: general)

**Role:** Results analyst. Only invoked if tests FAILED.

**Input to agent:**
- The test output (failures, tracebacks)
- The module source code
- The test file

**Agent instructions:**
```
You are a test results analyst. Tests have failed. Your job is to diagnose the
root cause and provide fix instructions.

For each failure:
1. Is this a TEST BUG (test has wrong assertion/setup) or a CODE BUG (the module
   has a real defect)?
2. Provide the exact fix needed — which file, which line, what to change
3. If it's a CODE BUG, flag it clearly — the orchestrator should fix the module,
   not the test

Return a structured diagnosis:
- For each failure: test name, root cause, classification (TEST_BUG/CODE_BUG),
  fix instruction
```

**Output:** Diagnosis with fix instructions.

### Phase 5: ITERATE

If Phase 4 produced fixes:
1. Apply the fixes (to test file or module code)
2. Go back to Phase 3 (RUN)
3. Maximum 3 iterations. If still failing after 3, stop and report to user.

## Test Conventions for This Project

### File structure
```
src_test/
    __init__.py
    test_log.py          # tests for shared/log.py
    test_manifest.py     # tests for shared/manifest.py (future)
    test_config_loader.py # tests for config_loader.py (future)
    ...
```

### Naming
- Test file: `test_<module_name>.py` (matching the source module name)
- Test class: `Test<FunctionOrClassName>` — one per public function/class
- Test function: `test_<what_it_verifies>` — descriptive, not `test_1`, `test_2`

### Imports in test files
```python
# CORRECT: direct module import, avoids shared/__init__.py
import shared.log as log_module
from shared.log import configure, log, log_error, log_raw, log_warn

# WRONG: triggers shared/__init__.py -> llama_index -> numpy issues with coverage
from shared import log as log_module
```

### Fixtures
- Use `autouse=True` fixtures for state reset (e.g., redirect log output)
- Always restore module state in fixture teardown (yield pattern)
- Prefer StringIO capture over capsys for this project's log functions

### Running tests
```bash
# All tests, verbose
.venv\Scripts\python -m pytest -v --tb=short

# Single test file
.venv\Scripts\python -m pytest src_test/test_log.py -v --tb=short

# With coverage (use --cov without module arg to avoid numpy conflict)
.venv\Scripts\python -m pytest src_test/test_log.py --cov --cov-report=term-missing -v --tb=short

# Single test
.venv\Scripts\python -m pytest src_test/test_log.py::TestLog::test_log_basic_message -v
```

### Coverage target
- Aim for 100% line coverage on the module under test
- `shared/log.py` is the reference: 18 statements, 0 missing, 100% coverage

## Flow Diagram

```
  [Code Changed]
       |
       v
  GENERATE ──> test file draft
       |
       v
  VALIDATE ──> issues? ──yes──> fix & re-GENERATE (max 2 rounds)
       |                            |
       no                           |
       |                            |
       v                            v
     RUN ────> failures? ──yes──> ANALYZE ──> fix & re-RUN (max 3 rounds)
       |                                         |
       no                                        |
       |                                         v
       v                              [still failing? report to user]
  [ALL GREEN ✓]
  Coverage report
  Done
```

## Output

When the cycle completes, report to the user:
- Number of tests: passed / failed / total
- Coverage: percentage and any missing lines
- Files created or modified
- Any code bugs found (if tests revealed real defects)
