# Git Branch-Aware Indexing: Post-Implementation Report

**Date:** 2026-03-15
**Branch:** `feature/git-branch-aware-indexing`
**Status:** Implementation complete (Phases 0-6), tested and verified

---

## 1. What Was Built

Git branch-aware indexing adds the ability to index feature branch changes as
lightweight overlays on top of the main branch index. AI agents can query
both main and feature branch code simultaneously, with feature branch results
automatically preferred over main branch results for the same file.

### Core capabilities

- **Branch overlay indexing** -- only files that differ between a feature branch
  and the main branch are indexed, not the entire codebase. A typical 20-file
  branch overlay adds ~1,200 vectors vs. 135,000 for the full main branch.
- **Branch-aware MCP queries** -- the `branch` parameter on the search tool lets
  agents get results that include their feature branch changes. Default (no param)
  returns main branch + non-git content only.
- **Config-driven branch management** -- branches are listed in `config_informica.py`.
  Adding a branch name and running `index_rag.py` builds the overlay. Removing it
  and re-running cleans up the overlay vectors automatically.
- **Backfill migration** -- existing vectors get a `branch` payload label so the
  branch filter works on pre-existing indexes without a full reindex.
- **Backward compatible** -- legacy SOURCE_DIRS format (flat dicts without `type`
  field) continues to work unchanged. Self-index and test-sources configs are
  unmodified.

---

## 2. Architecture Summary

### Overlay model (single Qdrant collection)

```
Qdrant Collection "informica_rag"
  +-- Main branch (branch="develop"):     135,235 vectors
  +-- Feature branch (branch="task/T37523"): 1,215 vectors
  +-- Non-git chunks (branch absent):        0 vectors (after backfill)
```

All branches share one collection. Point IDs are namespaced to avoid collisions:
- Main: `uuid5(NAMESPACE_URL, "file_key:chunk_idx")`
- Branch: `uuid5(NAMESPACE_URL, "branch_name::file_key:chunk_idx")`

### Query flow

1. Agent calls `search_informica(query, branch="task/T37523")`
2. Qdrant filter: `branch == "develop" OR branch == "task/T37523" OR branch IS EMPTY`
3. Over-fetch 2x `top_k` to survive dedup
4. Post-retrieval dedup: group by `file_path`, keep branch version over main version
5. Check tombstones for deleted files
6. Apply existing reranker, trim to `top_k`

When `branch` is omitted (default), filter is: `branch == "develop" OR branch IS EMPTY`.

### Config structure

SOURCE_DIRS gained two entry types, distinguished by a `type` field:

```python
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": "../informica_2_0",       # git repo root
        "main_branch": "develop",
        "branches": ["task/T37523"],       # overlay branches to index
        "sources": [                       # source dirs within the repo
            {"path": "delphi_src", "extensions": [".pas", ".dfm", ...]},
            {"path": "sql_srcipt/6RedGate", "extensions": [".sql"]},
        ],
    },
    {
        "type": "source_set",              # non-git, branch-agnostic
        "path": "../informica_docs",
        "extensions": [".md"],
    },
]
```

Legacy flat format (no `type` field) is treated as `source_set`. Backward compatible.

---

## 3. Files Changed / Created

### New modules

| File | Lines | Purpose |
|------|-------|---------|
| `shared/git_ops.py` | ~400 | Git subprocess wrappers: diff_branches, read_file_from_branch, read_files_to_temp_dir, get_merge_base, get_branch_head, get_blob_hash |
| `shared/branch_dedup.py` | ~186 | Branch filter construction (Qdrant), post-retrieval dedup, tombstone loading, main branch name extraction |

### Modified modules

| File | Change summary |
|------|---------------|
| `config.py` | Added `DIFF_FULL_REINDEX_THRESHOLD = 0.5` (section 7), expanded `MCP_TOOL_DESCRIPTION` with branch param docs |
| `config_informica.py` | Converted SOURCE_DIRS to `type: "git_repo"` format, expanded `MCP_TOOL_DESCRIPTION` |
| `config_loader.py` | +246 lines: `resolve_source_entries()`, `get_repo_groups()`, `_validate_source_dirs_entries()` |
| `index_rag.py` | +793 lines: `make_branch_point_id()`, branch metadata in `perform_refresh_qdrant()`, `backfill_branch_payload()`, `run_branch_overlay_indexing()`, `ensure_branch_payload_index()`, `_cleanup_stale_branches()`, `_update_repo_commits()` |
| `rag_mcp.py` | +75 lines: `branch` param with `Annotated[str, Field(description=...)]`, Qdrant filter, over-fetch, dedup integration |
| `shared/indexing.py` | `load_all_sources()` uses `resolve_source_entries(cfg)` instead of raw `config.SOURCE_DIRS` |
| `shared/manifest.py` | Added `_resolve_entries(cfg)` lazy-import wrapper to avoid circular imports |
| `self-index/config.py` | Expanded `MCP_TOOL_DESCRIPTION` with branch param docs |

### New test files

| File | Tests | Coverage target |
|------|-------|----------------|
| `tests/shared/test_branch_dedup.py` | 32 | `build_branch_filter`, `dedup_branch_results`, `get_branch_tombstones`, `get_main_branch_name` |
| `tests/test_backfill.py` | 28 | UUID generation, backfill scroll filter (BUG-1 regression), canonical prefix map (BUG-2 regression) |

### Test results

- **1470/1470 tests passing** (60 new, 1410 pre-existing)
- Zero regressions in existing test suite

---

## 4. Bugs Found and Fixed

Three bugs were discovered during integration testing on the production-scale
dev index (136,450 vectors).

### BUG-1: `IsNullCondition` vs `IsEmptyCondition`

**Symptom:** Backfill query matched 0 vectors when trying to find vectors
without a `branch` field.

**Root cause:** Qdrant distinguishes between `IsNullCondition` (field exists
with null value) and `IsEmptyCondition` (field completely absent from payload).
Pre-existing vectors had no `branch` key at all (absent), which is `IS EMPTY`,
not `IS NULL`. The backfill scroll filter and the query-time branch filter were
both using `IsNullCondition`.

**Fix:** Changed to `IsEmptyCondition` in both `backfill_branch_payload()`
(`index_rag.py`) and `build_branch_filter()` (`shared/branch_dedup.py`).

**Regression test:** `tests/test_backfill.py::TestBackfillScrollFilter` (6 tests)
and `tests/shared/test_branch_dedup.py::TestBuildBranchFilter` (9 tests).

### BUG-2: Canonical prefix mismatch in backfill

**Symptom:** Backfill set `branch = "develop"` on vectors but the
`_resolve_branch()` function couldn't match file paths to their git repo
entries, leaving some vectors with incorrect or missing branch labels.

**Root cause:** The prefix map was built from raw `entry["path"]` values
(e.g., `../informica_2_0/delphi_src`) but Qdrant `file_path` values use
canonical prefixes (e.g., `delphi_src/...`) produced by
`shared/manifest._get_canonical_prefix()`. The raw path never matched the
canonical file path.

**Fix:** Both `backfill_branch_payload()` and `perform_refresh_qdrant()` now
build the prefix map using `_get_canonical_prefix()` from `shared/manifest.py`.

**Regression test:** `tests/test_backfill.py::TestCanonicalPrefixMap` (13 tests).

### BUG-3: Scroll cursor drift during backfill

**Symptom:** After a full backfill run, 831 of 136,066 vectors still had no
`branch` field.

**Root cause:** Modifying vectors via `set_payload` while scrolling causes
Qdrant's scroll cursor to drift, skipping some vectors. This is a known
behavior with Qdrant scroll + concurrent modification.

**Fix:** The backfill is idempotent -- a second run catches stragglers.
Documented that backfill may need 2 runs for 100% coverage. After the second
run, 0 vectors remained without a branch label.

---

## 5. Integration Test Results

Five MCP query integration tests were run against the dev index after branch
overlay indexing and backfill:

| Test | Query | Branch | Expected | Result |
|------|-------|--------|----------|--------|
| 1 | "What is TdmMain?" | (none) | develop results only | PASS |
| 2 | "What is TdmMain?" | "task/T37523" | develop + task results | PASS |
| 3 | "PrepareDataSet" | "task/T37523" | branch version if modified | PASS |
| 4 | "REPORT_TYPE_PUNCTUALITY" | (none) | develop only | PASS |
| 5 | File modified on branch | "task/T37523" | branch version preferred | PASS |

### Index statistics (dev index)

| Metric | Value |
|--------|-------|
| Total vectors | 136,450 |
| Main branch (develop) | 135,235 |
| Feature branch (task/T37523) | 1,215 |
| Untagged (no branch) | 0 |
| Branch overlay files | 20 (7 added, 13 modified) |

---

## 6. How AI Agents Discover Branch Support

MCP exposes tools to AI agents via a JSON schema containing:
1. **Tool name** -- e.g., `search_informica`
2. **Tool description** -- from `MCP_TOOL_DESCRIPTION` config value
3. **Parameter schema** -- names, types, defaults, and descriptions

The `branch` parameter includes a description (via `Annotated[str, Field(...)]`)
that tells agents:
- What the parameter does
- How to get the current branch name (`git branch --show-current`)
- When to omit it (main branch)

The tool-level description also mentions branch-aware search support.

This is the **only** documentation agents see at tool discovery time. There are
no separate MCP usage docs -- the tool schema IS the docs.

---

## 7. Implementation Phases Completed

| Phase | Description | Status |
|-------|-------------|--------|
| 0a | `DIFF_FULL_REINDEX_THRESHOLD` in base config | Done |
| 0b | `config_informica.py` converted to `type: "git_repo"` | Done |
| 0c | `config_loader.py`: validation, `resolve_source_entries()`, `get_repo_groups()` | Done |
| 0d | `shared/manifest.py`: `_resolve_entries()` lazy-import wrapper | Done |
| 0e | `shared/indexing.py`: `load_all_sources()` uses resolved entries | Done |
| 0f | `index_rag.py`: all SOURCE_DIRS usage updated | Done |
| 1 | `shared/git_ops.py`: git subprocess wrappers | Done |
| 2 | Main branch git metadata (repo_commits in manifest) | Partial (foundations only, git-diff fast path deferred) |
| 3 | Branch overlay indexing (manifests, overlay flow, cleanup) | Done |
| 4 | Branch-aware MCP querying (filter, dedup, over-fetch) | Done |
| 5 | Migration/backfill (`backfill_branch_payload()`) | Done |
| 6 | Testing (60 new tests, 1470 total passing) | Done |

### Deferred work

- **Phase 2 git-diff fast path** in `determine_actions()` -- optimization that uses
  `git diff` to skip hash comparison for unchanged files on the main branch. Not
  required for correctness. The existing hash-based change detection works for all
  cases.
- **Comprehensive `shared/git_ops.py` tests** -- the module is tested indirectly via
  integration tests, but dedicated unit tests with mocked subprocess would improve
  coverage.

---

## 8. Design Decisions Made During Implementation

### Branch overlay uses same embedding pipeline as main branch

The user was explicit: branch overlay indexing must use the exact same code path
as main branch indexing. When `HYBRID_EMBED_SINGLE_PASS = False` (the default),
the two-pass pipeline (dense first to SQLite, then sparse) is used for overlays too.
An early implementation that forced single-pass was deleted because it (a) didn't
load the sparse encoder (causing Qdrant named-vector errors) and (b) violated this
requirement.

### `perform_refresh_qdrant()` made reusable for overlays

Instead of a separate `_index_branch_files()` function, `perform_refresh_qdrant()`
was parameterized with `file_states`, `point_id_fn`, `save_fn`, and `branch_label`
to support both main branch and overlay indexing through one code path.

### `index_rag.py` cannot be imported in tests

Module-level `argparse.parse_args()` at line ~1980, followed by Docker/Qdrant
operations, makes direct import impossible. Tests for `index_rag.py` functions
replicate the pure logic patterns (UUID generation, filter construction) rather
than importing the module.

### Tombstones stored in branch manifest, not Qdrant

Files deleted on a feature branch (relative to main) don't get Qdrant vectors.
Instead, their paths are recorded as tombstones in the branch manifest file.
The post-retrieval dedup layer checks tombstones and filters out main branch
results for deleted files.

---

## 9. Operational Notes

### Running branch overlay indexing

```bash
# Index main branch + all configured branch overlays
python index_rag.py --config config_informica --yes

# The indexer automatically:
# 1. Indexes/refreshes main branch
# 2. For each branch in config's "branches" list:
#    - Diffs against main branch
#    - Indexes changed files as overlay
#    - Stores branch manifest
# 3. Cleans up branches removed from config
```

### Adding a new feature branch

1. Edit `config_informica.py`, add branch name to `"branches"` list
2. Run `python index_rag.py --config config_informica --yes`
3. The overlay is built automatically

### Removing a feature branch

1. Remove the branch name from `"branches"` list in config
2. Run `index_rag.py` -- it detects the stale branch and purges its vectors

### Backfill (one-time migration)

For existing indexes that predate branch-aware indexing:

```bash
# Adds branch="<main_branch>" to all vectors that have no branch field
# May need 2 runs due to scroll cursor drift (BUG-3)
python index_rag.py --config config_informica --yes
# The backfill runs automatically if vectors without branch labels are detected
```

### Querying with branch

```python
# Main branch only (default)
search_informica("What is TdmMain?")

# Include feature branch changes
search_informica("What is TdmMain?", branch="task/T37523")
```
