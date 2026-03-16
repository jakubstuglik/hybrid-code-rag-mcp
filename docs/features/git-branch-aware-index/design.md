# Feature Design: Git Branch-Aware Indexing

**Date:** 2026-03-12 (initial), 2026-03-15 (revised)
**Status:** Implemented -- see [post-implementation.md](post-implementation.md) for results
**Author:** AI agent (Claude)

---

## 1. Problem Statement

The RAG index is built from files on disk (via `SOURCE_DIRS` symlinks to the `my_project`
repository). The index reflects whichever branch is currently checked out. When a developer
works on a feature branch for a week or more, the index becomes stale relative to their
changes unless they manually reindex.

### Use Cases

**UC1 — Solo developer on a feature branch:**
Developer works on `feature/T12549_backup_create` for a week, commits regularly. They want
their local RAG index to include the feature branch changes so AI agents can find their
new/modified code alongside the main branch code.

**UC2 — Team working on a shared feature branch:**
A team works on `feature/km_tar_71717`. The RAG MCP server serves the main branch index
to everyone. The team wants a branch-aware index that includes their feature branch changes
so their AI agents see up-to-date code, while developers on other branches still get the
main branch results.

**UC3 — Post-merge cleanup:**
After the feature branch merges into `develop`, the branch-specific index entries should
be removable (or left to decay — user's choice).

**UC4 — Multi-repo index with non-git sources:**
An index covers source code from `my_project` (git-backed) AND documentation from a
separate folder (not in any git repo). Branch-awareness applies only to git-backed
SOURCE_DIRS. Non-git sources are indexed from disk as today.

**UC5 — Main branch advances (differential refresh):**
After a sprint, `develop` has 200 new commits. Rather than full reindex (~2 hours),
the system diffs old-develop vs new-develop and only re-embeds changed files. If the
diff is too large (e.g., >50% of indexed files changed), it falls back to full reindex.

**UC6 — Adding/removing feature branches via config:**
User edits `config_my_project.py` to add `"feature/T12549"` to the branch list. Next
`index_rag.py` run picks it up and builds the overlay. Removing the branch from config
and re-running cleans up the overlay vectors automatically.

### Key Constraint

We do **NOT** want a full separate copy of the index per branch. With ~140K vectors in the
main index, duplicating everything per branch would be wasteful. We want an **overlay** model:
main branch is the base, feature branches add/replace only the files they changed.

---

## 2. Feasibility Analysis

### 2.1 Can We Read Files from Git Without Checkout?

**YES — fully feasible.** Verified with the actual `my_project` repository:

| Operation | Git Command | Tested | Performance |
|-----------|------------|--------|-------------|
| List all files on a branch | `git ls-tree -r --name-only <branch> -- <path>` | Yes | Fast (10K+ files in <1s) |
| Read file content from branch | `git show <branch>:<path>` | Yes | ~14ms per file |
| Diff two branches (changed files) | `git diff --name-status <base> <branch> -- <paths>` | Yes | Fast |
| Find merge-base | `git merge-base <main> <feature>` | Yes | Instant |
| Get blob hash (change detection) | `git ls-tree <branch> -- <path>` → blob hash | Yes | Fast |

**Performance for batch reading:** 10 files via `git show` takes ~137ms (~14ms/file). For a
typical feature branch with 50-200 changed files, reading all changed file contents would
take 0.7s-2.8s — negligible compared to embedding time.

**Critical finding:** The source code lives in `my_project`, not in `hybrid-code-rag-mcp`.
The indexer accesses it via symlinks (`source/` → `my_project/delphi_src/`). The git
operations must target the `my_project` repository, not the RAG tool's repository.

### 2.2 Can Readers Consume Content Without Files on Disk?

**PARTIALLY — requires adaptation.** Current readers take a `Path` object and call
`file.read_text()` or `file.read_bytes()` internally:

```python
# BaseFileReader interface (shared/readers/_base.py)
class BaseFileReader(ABC):
    def load_data(self, file: Path, extra_info: Optional[dict] = None) -> List[Document]:
        ...
    def load_nodes(self, file: Path, extra_info: Optional[dict] = None) -> List[TextNode]:
        ...
```

**Two approaches to handle this:**

| Approach | Description | Effort | Risk |
|----------|-------------|--------|------|
| **A. Temp files** | Write `git show` content to a temp file, pass to reader | Low | Disk I/O overhead, but trivial for <200 files |
| **B. Content-based API** | Add `load_nodes_from_content(content: str, filename: str)` to readers | Medium | Must audit all 7 readers for `Path.stat()`, `Path.read_text()` calls |

**Recommendation: Approach A (temp files) for v1.** It's simpler, lower risk, and the
performance penalty is negligible (writing 200 temp files is milliseconds). Approach B
can be a v2 optimization if needed.

### 2.3 Can Qdrant Support Branch-Aware Queries?

**YES — via payload filtering.** Qdrant supports filtering on payload fields during search.
Current payloads already have `file_path` metadata. Adding a `branch` field is trivial:

```python
# Current payload structure (per point):
{
    "file_path": "delphi_src/Common/BaseEditorForm.pas",
    "node_type": "defProc",
    "class_name": "TBaseEditorForm",
    "unit_name": "BaseEditorForm",
    "text": "...",
    # ... other metadata
}

# Proposed: add branch field
{
    "branch": "develop",           # or "feature/T12549_backup_create"
    # ... everything else unchanged
}
```

**Query-time filtering options:**

1. **No branch filter** — returns results from all branches (main + features). Simple but
   could cause confusion when the same file exists in both main and feature branch.

2. **Branch priority filter** — query with: "give me results from branch X, falling back
   to main for files not on branch X". This is the ideal behavior.

3. **Qdrant implementation:** Qdrant does NOT natively support "prefer branch X, fall back
   to main" in a single query. But we can achieve this with two strategies:

   **Strategy A — Single collection, post-retrieval dedup:**
   - All branches live in one collection. Every point has `branch` metadata.
   - Query without branch filter (get results from all branches).
   - Post-retrieval: if a result exists from both main and feature branch for the same
     file, keep only the feature branch version.
   - Pro: Simple. One collection. Works with existing hybrid search.
   - Con: Over-fetching needed to ensure enough feature-branch results survive dedup.

   **Strategy B — Single collection, query-time filter:**
   - Index feature branch files with `branch = "feature/X"`.
   - At query time, use Qdrant `should` filter: `branch IN [requested_branch, "main"]`.
   - Post-retrieval: deduplicate by file_path, preferring the requested branch.
   - Pro: Qdrant does less work (pre-filters). Still one collection.
   - Con: Slightly more complex filter construction.

   **Strategy C — Separate collection per branch:**
   - Each branch gets its own Qdrant collection.
   - Query fans out to both collections, merges results.
   - Pro: Clean separation. Easy cleanup on merge.
   - Con: Duplicate main branch vectors in every collection. Wasteful. Fan-out query is
     slower and harder to implement with LlamaIndex.

### 2.4 Storage Overhead Analysis

For a typical feature branch:

| Metric | Typical Range | Notes |
|--------|--------------|-------|
| Changed files per feature branch | 20-200 | Based on actual `my_project` branches |
| Chunks per file (average) | ~11 | 140K chunks / 12.4K files |
| New vectors per branch | 220-2,200 | Tiny fraction of 140K base |
| Vector size (768-dim float32 + sparse) | ~6KB per point | Dense + sparse + payload |
| Storage overhead per branch | 1.3-13 MB | Negligible |

**Extreme case:** A large refactor branch may have 4,000+ changed files.
That would add ~48K vectors. Even this extreme case is manageable in a single collection
(188K total points — Qdrant handles millions easily).

---

## 3. Recommended Architecture

### 3.1 The Overlay Model (Single Collection)

```
┌─────────────────────────────────────────────────────┐
│                 Qdrant Collection                     │
│                 "my_project_rag"                      │
│                                                       │
│  ┌──────────────────────────────┐                    │
│  │  Main branch ("develop")     │  ~140K vectors     │
│  │  branch = "develop"          │  (base index)      │
│  └──────────────────────────────┘                    │
│                                                       │
│  ┌──────────────────────────────┐                    │
│  │  Feature branch overlay      │  ~200-2K vectors   │
│  │  branch = "feature/T12549"   │  (changed files    │
│  │                              │   only)            │
│  └──────────────────────────────┘                    │
│                                                       │
│  ┌──────────────────────────────┐                    │
│  │  Another feature branch      │  ~500 vectors      │
│  │  branch = "feature/km_tar"   │  (changed files    │
│  │                              │   only)            │
│  └──────────────────────────────┘                    │
└─────────────────────────────────────────────────────┘
```

**Key principle:** Only files that differ between the feature branch and main branch get
indexed under the feature branch label. Unchanged files are served from main branch vectors.

### 3.2 How Indexing Works

#### Step 1: Determine changed files

```bash
# Find the merge-base (point where feature branch diverged from main)
MERGE_BASE=$(git merge-base develop feature/T12549)

# Get files changed on the feature branch since divergence
git diff --name-status $MERGE_BASE feature/T12549 -- delphi_src/ sql_srcipt/
```

This produces a list like:
```
A   delphi_src/NewModule/NewUnit.pas       # Added
M   delphi_src/Common/BaseEditorForm.pas   # Modified
D   delphi_src/OldModule/Deprecated.pas    # Deleted
```

#### Step 2: Read file contents from git

For Added and Modified files:
```bash
git show feature/T12549:delphi_src/Common/BaseEditorForm.pas > /tmp/BaseEditorForm.pas
```

Write to temp files, then pass to existing readers. No reader changes needed.

#### Step 3: Embed and upsert with branch metadata

Same embedding pipeline as today, but every point gets `branch = "feature/T12549"` in
its payload. Point IDs are namespaced to avoid collision:
```python
# Current: uuid5(NAMESPACE_URL, "source/Common/BaseEditorForm.pas:0")
# Branch:  uuid5(NAMESPACE_URL, "feature/T12549::source/Common/BaseEditorForm.pas:0")
```

#### Step 4: Handle deletions

For files deleted on the feature branch: we don't need to do anything special. The main
branch vectors still exist. When querying for the feature branch, the post-retrieval
dedup layer will NOT find a feature-branch version, so it falls back to the main branch
version. If the file was truly deleted on the feature branch and should not appear in
results, we store a **tombstone** marker in the manifest (not in Qdrant — no vector to
store). The post-retrieval layer checks tombstones and filters out main-branch results
for deleted files.

### 3.3 How Querying Works (Revised)

#### MCP Tool Interface Change

Current:
```python
async def search_my_project(query: str, top_k: int = 8) -> str:
```

Proposed:
```python
async def search_my_project(query: str, top_k: int = 8, branch: str = "") -> str:
```

The `branch` parameter defaults to empty string. When empty, the MCP server queries
the **main branch** of each repo group (as defined in their `main_branch`
config). This is the default experience — same as today plus branch metadata filtering.

When a branch name is provided, the search includes both main and that branch, with
post-retrieval dedup favoring the specified branch.

#### Query Filter Construction

The filter must handle three categories of vectors:

1. **Git-backed, main branch:** `branch == "develop"` (or whatever main_branch is)
2. **Git-backed, feature branch:** `branch == "feature/T12549"`
3. **Non-git (disk-only):** `branch` field is NULL / missing

```python
# Query with no branch parameter (default = main branch):
filter = Should([
    FieldCondition(key="branch", match=MatchValue(value="develop")),
    # Include non-git chunks (no branch field):
    IsNullCondition(key="branch"),
])

# Query with branch="feature/T12549":
filter = Should([
    FieldCondition(key="branch", match=MatchValue(value="develop")),
    FieldCondition(key="branch", match=MatchValue(value="feature/T12549")),
    IsNullCondition(key="branch"),
])
```

**Note on IsNull:** Qdrant supports `IsNullCondition` for filtering points where a
payload field doesn't exist. This handles non-git chunks cleanly. However, after
Phase 5 backfill (which adds `branch` to ALL existing vectors), only newly-indexed
non-git chunks would have NULL branch. Alternative: set `branch = "__none__"` for
non-git chunks explicitly, then filter with `MatchAny`. Simpler filter logic, no
NULL handling needed.

#### Query Flow (Revised)

```
1. Agent calls: search_my_project("What is TdmMain?", branch="feature/T12549")

2. MCP server resolves default: if branch="" → use main branch names from config

3. Constructs Qdrant filter:
   should: [branch == "develop", branch == "feature/T12549", branch IS NULL]

4. Over-fetch: request 2x top_k (to survive dedup)

5. Post-retrieval dedup (shared/branch_dedup.py):
   - Group results by file_path
   - For each file_path present in BOTH main and feature branch:
     keep ONLY the feature branch version
   - Check tombstones: remove results for files deleted on feature branch
   - Non-git chunks (branch=NULL): always kept (no dedup needed)

6. Apply existing reranker

7. Return top_k results
```

#### Agent Tool Description Update

The MCP tool description should instruct agents to include the current branch:

```
Search the codebase for relevant context. When working on a feature branch,
pass the branch name to get results that include your branch's changes.
Use the output of `git branch --show-current` for the branch parameter.
If you're on the main branch or unsure, omit the branch parameter.
```

### 3.4 How Incremental Updates Work

Branch indexing is incremental, just like main branch indexing:

1. **Branch manifest:** Stored alongside main manifest as
   `index_manifest_branch_<sanitized_name>.json`. Contains:
   - Branch name
   - Commit hash at last index time
   - Main branch commit hash (merge-base) at last index time
   - Per-file entries (same format as main manifest)
   - Tombstones (deleted files)

2. **Incremental refresh:**
   - Compare current branch HEAD commit to last-indexed commit
   - `git diff --name-status <last_indexed_commit> <current_HEAD>` gives the delta
   - Only re-embed changed files since last branch index run
   - If the merge-base changed (main branch advanced), also pick up files that changed
     on main since our last merge-base (these might conflict with or be overridden by
     feature branch changes)

3. **Branch cleanup (post-merge or config removal):**
   - When a branch is removed from a git_repo entry's `branches` list in config and `index_rag.py` runs,
     it detects branches in the manifest that are no longer in config.
   - Deletes all Qdrant points where `branch == "feature/T12549"`
   - Deletes the branch manifest file
   - Main branch vectors are untouched
   - Also available as explicit CLI: `index_rag.py --remove-branch feature/T12549`

### 3.5 Main Branch Differential Refresh (New)

When the main branch itself advances (e.g., `develop` gets 200 new commits after a
sprint), we want to avoid a full reindex. The system uses git-based change detection:

#### Flow

```
1. Manifest stores: main_branch_commit = <commit hash at last index time>

2. On next index_rag.py run:
   a. current_commit = git rev-parse <main_branch>
   b. If current_commit == main_branch_commit → nothing to do (for git-backed dirs)
   c. If different:
      git diff --name-status <old_commit> <current_commit> -- <git_prefixes>
      → list of A/M/D files

3. Threshold check:
   changed_ratio = len(changed_files) / len(total_indexed_files_in_repo_group)
   If changed_ratio > DIFF_FULL_REINDEX_THRESHOLD (default 0.5 = 50%):
     → Fall back to full reindex for this repo group
     → Log: "Main branch diff too large (N/M files = X%), doing full reindex"
   Else:
     → Differential: only re-embed changed files, delete removed files' vectors

4. Update manifest with new main_branch_commit
```

#### Interaction with disk-based change detection

Today the manifest uses SHA-256 file hashes for change detection. For git-backed dirs,
we have two change detection sources:
- **Git diff:** knows exactly what changed between commits (fast, authoritative)
- **File hash:** works for non-git dirs and as a fallback

For git-backed dirs, git diff takes priority. The hash-based detection remains as a
safety net (e.g., if someone modified a file on disk without committing).

#### The hybrid approach for main branch

The main branch is special because its files exist on disk (the working copy). So
for main branch indexing of git-backed dirs:

1. **First pass:** `git diff` between stored commit and current HEAD → changed files
2. **Second pass:** For any files NOT covered by git diff (uncommitted changes, new files
   not yet committed), fall back to hash comparison against disk
3. **Union** both sets → files to re-embed

This preserves the current behavior (uncommitted changes are indexed) while adding
git-diff acceleration for the committed portion. Non-git SOURCE_DIRS skip step 1
and use hash comparison only (unchanged behavior).

#### Config

```python
# In SOURCE_DIRS git_repo entry or as top-level default:
# Threshold ratio above which a main branch diff triggers full reindex
# instead of differential. 0.5 = if >50% of files changed, full reindex.
DIFF_FULL_REINDEX_THRESHOLD = 0.5
```

### 3.6 Configuration (Final — Two Entry Types)

The original design (2026-03-12) used flat config keys. The revised design uses
**two distinct entry types** in SOURCE_DIRS, distinguished by a `type` field:

- **`type: "git_repo"`** — a git repository with one or more source paths inside it
- **`type: "source_set"`** — a standalone directory (not git-backed)

Duplicate `git_repo` entries with the same `path` are a **config error** (not merged).
This eliminates ambiguity about main_branch conflicts.

#### Final Config Structure

```python
# config_my_project.py — FINAL
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": "../my_project",                 # git repo root (required)
        "main_branch": "develop",                 # optional, default: "master"
        "branches": [                             # optional, default: []
            "feature/T12549_backup_create",
            "feature/km_tar_71717",
        ],
        "diff_full_reindex_threshold": 0.5,       # optional, override global default
        "sources": [
            {
                "path": "delphi_src",             # relative to git_repo path
                "extensions": [".pas", ".dpr", ".dfm", ".fr3", ".dproj"],
                "exclude": ["TURDUS/ENG", "TURDUS/SRM", "TURDUS/UKR"],
            },
            {
                "path": "sql_srcipt/6RedGate",    # relative to git_repo path
                "map_to_path": "sql_srcipt/6RedGate",
                "extensions": [".sql"],
            },
        ],
    },
    {
        "type": "source_set",
        "path": "../my_project_docs/user_guides",  # absolute or relative
        "extensions": [".md", ".txt"],
        # No git backing. Indexed from disk. Branch-agnostic.
    },
]
```

#### Entry Type Rules

1. **`git_repo` entry:** Has `type: "git_repo"`, a `path` to the repo root, git
   config fields (`main_branch`, `branches`, `diff_full_reindex_threshold`), and a
   `sources` list (one or more source paths within that repo). Each source path is
   **relative to the git_repo `path`**. This means `path: "delphi_src"` resolves to
   `../my_project/delphi_src`. Each source can have its own `extensions`,
   `exclude`, and `map_to_path`.

2. **`source_set` entry:** Has `type: "source_set"`, a `path`, `extensions`,
   optional `exclude` and `map_to_path`. Indexed from disk. No branch awareness.
   Chunks from source_sets appear in ALL queries (branch-agnostic).

3. **Duplicate git_repo paths = config error.** If two entries both have
   `path: "../my_project"` with `type: "git_repo"`, `config_loader.py` raises
   `RuntimeError`. This prevents conflicting main_branch or branches definitions.

4. **Defaults:** `main_branch` defaults to `"master"`. `branches` defaults to `[]`.
   `diff_full_reindex_threshold` defaults to the global `DIFF_FULL_REINDEX_THRESHOLD`
   from `config.py`.

5. **Git-relative path derivation:** For `git diff` and `git show` commands, the
   source `path` IS the git-relative prefix (since it's already relative to the
   git_repo `path`). No additional mapping needed.

6. **Canonical keys / manifest keys:** The `map_to_path` or last segment of `path`
   continues to be the canonical prefix for Qdrant payload `file_path` and manifest
   keys, exactly as today's `normalize_file_key()` works.

#### Backward Compatibility

The current flat SOURCE_DIRS format (without `type` field) continues to work as
today — treated as `source_set` (disk-only indexing). The new format is opt-in.
Migration path:

```python
# OLD (still works, no branch awareness):
SOURCE_DIRS = [
    {"path": "../my_project/delphi_src", "extensions": [".pas"]},
]

# NEW (adds branch awareness):
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": "../my_project",
        "main_branch": "develop",
        "sources": [{"path": "delphi_src", "extensions": [".pas"]}],
    },
]
```

`config_loader.py` detects which format is used per entry:
- Has `"type": "git_repo"` → git_repo entry
- Has `"type": "source_set"` → source_set entry
- No `type` field → legacy flat format, treated as source_set

#### Self-index example

```python
# self-index/config.py — with branch awareness
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": ".",                        # this project IS the git repo
        "main_branch": "main",
        "branches": [],
        "sources": [
            {
                "path": ".",                # index from repo root
                "extensions": [".py", ".bat", ".md", ".json"],
                "exclude": [".venv", ".git", "test_sources", "__pycache__"],
            },
        ],
    },
]
```

---

## 4. Implementation Plan (Revised)

### Phase 0: Config schema extension (two entry types)

**Files:** `config_my_project.py`, `config_loader.py`, `shared/manifest.py`

- Define the two entry types: `type: "git_repo"` (with nested `sources`) and `type: "source_set"`
- `config_loader.py`:
  - Detect entry type by `type` field (git_repo / source_set / missing = legacy flat)
  - Validate: git_repo path exists and is a git repo, no duplicate git_repo paths
  - Normalize: convert legacy flat entries to source_set internally
  - New function `resolve_source_entries(cfg)` that returns a unified list of
    normalized entries (each with `type`, `repo_path` or None, `sources` list, etc.)
  - Validate `main_branch`, `branches` (branch names exist in the repo — warning only,
    branch may not exist yet at config-write time)
- `shared/manifest.py`: store `main_branch_commit` per repo group in manifest
- Existing `get_source_files(cfg)` must work with BOTH old and new format
  (iterate over resolved source entries, build file list the same way)
- No changes to existing indexing/query code yet — this is purely additive
- Add `DIFF_FULL_REINDEX_THRESHOLD = 0.5` to base `config.py`

**Estimated effort:** Medium. ~250 lines. Needs careful backward compat handling.

### Phase 1: Core git integration layer (new module)

**New file:** `shared/git_ops.py`

Responsibilities:
- `get_repo_group_info(repo_path)` → validate repo, get current branch
- `get_branch_head(repo_path, branch)` → commit hash
- `diff_branches(repo_path, base, target, paths)` → list of (status, file_path)
- `read_file_from_branch(repo_path, branch, file_path)` → bytes
- `read_files_to_temp_dir(repo_path, branch, file_list)` → temp dir path
- `get_merge_base(repo_path, branch_a, branch_b)` → commit hash
- `get_blob_hash(repo_path, branch, file_path)` → hash (for manifest)

All functions are thin wrappers around `subprocess.run(["git", ...])`.
No state, no side effects beyond temp files. Easy to test with mocks.

**Estimated effort:** Medium. ~300 lines. Well-contained, no changes to existing code.

### Phase 2: Main branch git-accelerated refresh

**Files:** `index_rag.py`, `shared/manifest.py`

This phase makes main branch indexing faster for git-backed dirs WITHOUT adding
any branch overlay functionality. It's a standalone improvement:

- Manifest gains `main_branch_commit` field per repo group
- `determine_actions()` gains a git-diff fast path for git-backed dirs:
  if stored commit matches current HEAD → skip hash comparison for unchanged files
- Diff threshold check: if ratio > `DIFF_FULL_REINDEX_THRESHOLD` → full reindex
- Non-git dirs continue to use hash-based detection (unchanged)
- Uncommitted changes still detected via hash fallback

**Estimated effort:** Medium. ~200 lines across 2 files.

**Key benefit:** This phase is independently valuable — it speeds up regular
incremental indexing even without branch overlays. Can be shipped and tested alone.

### Phase 3: Branch overlay indexing

**Files:** `index_rag.py`, `shared/indexing.py`, `shared/git_ops.py`

- New indexing flow: for each repo group, for each branch in `branches`:
  1. `diff_branches(repo_path, main_branch, branch, git_prefixes)` → changed files
  2. `read_files_to_temp_dir(repo_path, branch, changed_files)` → temp dir
  3. Run existing readers on temp files → nodes
  4. Add `branch` metadata to all nodes
  5. Namespace point IDs: `uuid5(NS, "branch::file_path:chunk_idx")`
  6. Embed and upsert
  7. For deleted files: store tombstones in branch manifest, delete old vectors
- Branch manifests: `index_manifest_branch_<sanitized_name>.json`
- Branch cleanup: detect branches in manifests but not in config → purge vectors
- `branch` field added to ALL points (main branch too — backfill existing)
- Create Qdrant payload index on `branch` field

**Estimated effort:** High. ~400 lines across 3 files. Core of the feature.

### Phase 4: Branch-aware querying

**Files:** `rag_mcp.py`, `shared/branch_dedup.py` (new)

- MCP search tool gains `branch` parameter (optional, default = "")
- Default behavior: `branch=""` → query main branch only (filter: `branch == main`
  OR `branch IS NULL` for non-git chunks)
- Branch query: filter `branch IN [main, requested_branch]` + non-git chunks
  (which have no branch field)
- Post-retrieval dedup in new `shared/branch_dedup.py`:
  - Group by `file_path`
  - For duplicates: keep requested branch version, discard main branch version
  - Check tombstones: filter out main branch results for files deleted on branch
- Over-fetch: 2x `top_k` when branch is specified (to survive dedup)
- Integrate with existing reranker pipeline

**Estimated effort:** Medium. ~250 lines across 2 files.

### Phase 5: Migration and backfill

- One-time: add `branch = "develop"` (or whatever main_branch is) to all existing
  vectors that have no `branch` field. Qdrant `set_payload` with filter.
- Alternative: treat missing `branch` field as main branch in query logic (lazy).
  Recommendation: do the backfill — it's simpler to reason about at query time.
- Create `branch` payload index on the collection.

**Estimated effort:** Low. ~50 lines. Can be a CLI flag: `--migrate-branch-field`.

### Phase 6: Testing and validation

- Unit tests for `shared/git_ops.py` (mocked subprocess)
- Unit tests for `shared/branch_dedup.py`
- Unit tests for repo group resolution in `config_loader.py`
- Integration test: create a test branch in a temp git repo, index it, query it
- Run existing RAG validation suite with branch overlay active
- Edge cases: binary files, encoding, very large branches, non-git mixed with git dirs

**Estimated effort:** Medium-High. ~400 lines of tests.

---

## 5. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Encoding issues** in `git show` output | Readers expect specific encodings (UTF-8, Windows-1250). Git show outputs raw bytes. | Write temp files in binary mode. Readers already handle multi-encoding fallback. |
| **Large feature branches** (4K+ files) | Embedding 48K+ vectors takes time (~30 min on CUDA) | Accept this for initial index. Incremental updates are fast (only new changes). |
| **Merge-base drift** | Main branch advances while feature branch is indexed. Some "changed" files may have changed on main too. | Re-check merge-base on each incremental run. If it moved, re-diff and update affected files. |
| **Stale branch index** | Developer forgets to reindex after commits | Document workflow. Optionally: git hook that triggers reindex. |
| **Query performance with many branches** | Qdrant filter with many branch values | Qdrant handles `should` filters efficiently. Even 10 branches is trivial. |
| **LlamaIndex filter support** | LlamaIndex `QdrantVectorStore` may not expose all Qdrant filter capabilities | Use `qdrant_client` directly for filtered queries if LlamaIndex wrapper is insufficient. Verified: LlamaIndex supports `MetadataFilters` which map to Qdrant filters. |
| **Point ID collisions** | Branch-namespaced UUIDs must not collide with main | uuid5 with different input string guarantees uniqueness. |

---

## 6. Alternatives Considered and Rejected

### 6.1 Separate Collection Per Branch

Each branch gets its own full Qdrant collection containing ALL files (main + branch changes).

**Rejected because:**
- Duplicates ~140K vectors per branch (wasteful)
- Requires fan-out queries across collections (complex, slower)
- LlamaIndex doesn't natively support multi-collection queries
- Storage grows linearly with branch count

### 6.2 Git Worktrees

Use `git worktree add` to create a temporary checkout of the feature branch, then index
from that worktree directory.

**Rejected because:**
- Creates a full working copy on disk (consumes disk space)
- Requires checkout (explicitly not wanted per requirements)
- Worktree management adds complexity
- Doesn't solve the "overlay" problem — still need separate indexing logic

### 6.3 Sparse Checkout

Use `git sparse-checkout` to partially checkout only changed files.

**Rejected because:**
- Still modifies the working directory
- Doesn't work alongside the existing full checkout
- Requires careful management of sparse-checkout filters
- `git show` is simpler and has no side effects

### 6.4 Full Re-index on Branch Switch

Just reindex everything when switching branches.

**Rejected because:**
- Full reindex takes ~2 hours
- Doesn't support multiple branches simultaneously
- Doesn't support the team use case (UC2)

---

## 7. Open Questions (Revised)

### Resolved from original analysis

1. **Should the `branch` parameter be mandatory or optional in the MCP tool?**
   **RESOLVED: Optional.** Defaults to empty string = main branch for each repo group
   as defined in config. Backward compatible.

2. **Should we create a Qdrant payload index on the `branch` field?**
   **RESOLVED: Yes.** Created during Phase 5 migration.

3. **How to handle the `file_datetime` metadata?**
   **RESOLVED:** Use git commit timestamp for git-sourced files. Cosmetic only.

4. **Should branch indexing run on CUDA or CPU?**
   **RESOLVED:** Use existing `INDEX_EMBED_DEVICE`. No special handling.

5. **Can this work with the self-index (`--config self-index`) too?**
   **RESOLVED: Yes.** Add `type: "git_repo"` to self-index SOURCE_DIRS entry:
   ```python
   {"type": "git_repo", "path": ".", "main_branch": "main", "branches": [], "sources": [...]}
   ```

### New questions (2026-03-15)

6. **How should git_repo properties merge across SOURCE_DIRS entries in the same group?**
   **RESOLVED: No merging.** Two distinct entry types (`type: "git_repo"` and
   `type: "source_set"`). Duplicate git_repo entries with the same `path` are a config
   error — not merged. Each git_repo entry owns its own `main_branch` and `branches`
   list. No ambiguity.

7. **Should the `branch` MCP parameter accept repo-qualified names?**
   **RESOLVED: (A) — unqualified names.** The branch name is applied to ALL repo groups
   that have it in their `branches` list. If a repo group doesn't have the branch
   configured, it falls back to that group's main branch. In practice, branch names are
   unique across repos within one index config, so disambiguation is unnecessary.

8. **What about non-git SOURCE_DIRS in branch queries?**
   When querying with `branch="feature/X"`, chunks from non-git dirs (which have no
   `branch` field) should still appear in results. They're branch-agnostic content.
   The Qdrant filter must be: `(branch == main OR branch == feature/X) OR branch IS NULL`.
   **Confirmed: this is the design.**

9. **DIFF_FULL_REINDEX_THRESHOLD — should this be configurable per repo group?**
   **RESOLVED: Yes.** Global default `DIFF_FULL_REINDEX_THRESHOLD = 0.5` in `config.py`.
   Overridable per `git_repo` entry via `diff_full_reindex_threshold` key.

10. **Should we store the main branch label as a literal branch name or a special sentinel?**
    **RESOLVED: (A) — literal branch names.** Store `branch = "develop"` (the actual
    branch name). Simple, grep-friendly, readable in Qdrant payloads. Branch renames
    are rare; if one happens, a `set_payload` migration handles it.

---

## 8. Summary (Revised)

| Question | Answer |
|----------|--------|
| Is it feasible to read files from git without checkout? | **Yes.** `git show` reads any file from any branch in ~14ms. |
| Is the overlay model (not full duplicate) achievable? | **Yes.** Only changed files get branch-specific vectors. |
| Does Qdrant support branch-aware queries? | **Yes.** Payload filters + post-retrieval dedup. |
| Do readers need major changes? | **No.** Temp files bridge git content to existing readers. |
| Can multiple git repos coexist in one index? | **Yes.** `type: "git_repo"` entries in SOURCE_DIRS group by repo. |
| Can non-git SOURCE_DIRS coexist with git-backed ones? | **Yes.** `type: "source_set"` = disk-only, branch-agnostic. |
| Can main branch refresh be differential? | **Yes.** Git diff + threshold check for full reindex fallback. |
| Are branches config-driven (add/remove by editing config)? | **Yes.** Cleanup is automatic on next index run. |
| What's the storage overhead? | **Minimal.** 1-13 MB per typical feature branch. |
| What's the implementation effort? | **Medium-High.** ~7 phases, ~1800 lines total (code + tests). |
| What's the main risk? | **Encoding edge cases** and **query filter complexity** for mixed git/non-git. |

**Verdict: Fully feasible. The revised design supports multiple repos, non-git dirs,
config-driven branch management, and differential main branch refresh — all within the
single-collection overlay model.**

---

## 9. Revision History

| Date | Change |
|------|--------|
| 2026-03-12 | Initial feasibility analysis and implementation plan |
| 2026-03-15 | Major revision: repo groups model, non-git source dirs, config-driven branch lists, main branch differential refresh, updated implementation plan (7 phases), new open questions |
| 2026-03-15 | Config flattened: replaced wrapper keys (`"git_repo": {...}`) with `type` field (`"type": "git_repo"`) for cleaner structure |
