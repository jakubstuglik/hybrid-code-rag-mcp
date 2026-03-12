# Feature: Git Branch-Aware Indexing

**Date:** 2026-03-12
**Status:** Feasibility analysis complete, implementation plan ready
**Author:** AI agent (Claude)

---

## 1. Problem Statement

The RAG index is built from files on disk (via `SOURCE_DIRS` symlinks to the `informica_2_0`
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

### Key Constraint

We do **NOT** want a full separate copy of the index per branch. With ~140K vectors in the
main index, duplicating everything per branch would be wasteful. We want an **overlay** model:
main branch is the base, feature branches add/replace only the files they changed.

---

## 2. Feasibility Analysis

### 2.1 Can We Read Files from Git Without Checkout?

**YES — fully feasible.** Verified with the actual `informica_2_0` repository:

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

**Critical finding:** The source code lives in `informica_2_0`, not in `hybrid-code-rag-mcp`.
The indexer accesses it via symlinks (`source/` → `informica_2_0/delphi_src/`). The git
operations must target the `informica_2_0` repository, not the RAG tool's repository.

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
| Changed files per feature branch | 20-200 | Based on actual `informica_2_0` branches |
| Chunks per file (average) | ~11 | 140K chunks / 12.4K files |
| New vectors per branch | 220-2,200 | Tiny fraction of 140K base |
| Vector size (768-dim float32 + sparse) | ~6KB per point | Dense + sparse + payload |
| Storage overhead per branch | 1.3-13 MB | Negligible |

**Extreme case:** The `feature/km_tar_71717` branch has 4,421 changed files (massive refactor).
That would add ~48K vectors. Even this extreme case is manageable in a single collection
(188K total points — Qdrant handles millions easily).

---

## 3. Recommended Architecture

### 3.1 The Overlay Model (Single Collection)

```
┌─────────────────────────────────────────────────────┐
│                 Qdrant Collection                     │
│                 "informica_rag"                       │
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

### 3.3 How Querying Works

#### MCP Tool Interface Change

Current:
```python
async def search_informica(query: str, top_k: int = 8) -> str:
```

Proposed:
```python
async def search_informica(query: str, top_k: int = 8, branch: str = "") -> str:
```

The `branch` parameter defaults to empty string (= main branch only, current behavior).
When a branch name is provided, the search includes both main and that branch, with
post-retrieval dedup favoring the specified branch.

#### Query Flow

```
1. Agent calls: search_informica("What is TdmMain?", branch="feature/T12549")

2. MCP server constructs Qdrant filter:
   - should: [branch == "develop", branch == "feature/T12549"]
   (This retrieves vectors from BOTH branches)

3. Over-fetch: request 2x top_k to ensure enough candidates survive dedup

4. Post-retrieval dedup:
   - Group results by file_path
   - For each file_path that appears in both branches:
     keep ONLY the feature branch version
   - Check tombstones: remove results for files deleted on feature branch
   - Apply existing reranker

5. Return top_k results
```

#### Agent Tool Description Update

The MCP tool description should instruct agents to include the current branch:

```
Search the codebase for relevant context. When working on a feature branch,
pass the branch name to get results that include your branch's changes.
Use the output of `git branch --show-current` for the branch parameter.
If you're on the main branch (develop), omit the branch parameter.
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

3. **Branch cleanup (post-merge):**
   - `index_rag.py --remove-branch feature/T12549`
   - Deletes all Qdrant points where `branch == "feature/T12549"`
   - Deletes the branch manifest file
   - Main branch vectors are untouched

### 3.5 Configuration

New config parameters in `config.py`:

```python
# ════════════════════════════════════════════════════════════════════
# 10. GIT BRANCH INDEXING
# ════════════════════════════════════════════════════════════════════

# Name of the main/default branch. All files not on a feature branch
# are indexed under this branch label.
GIT_MAIN_BRANCH = "develop"

# Path to the git repository containing the indexed source code.
# If None, auto-detected from the first SOURCE_DIRS path's git root.
GIT_REPO_PATH = None

# Mapping from SOURCE_DIRS paths to their locations within the git repo.
# Needed because SOURCE_DIRS uses symlinks (e.g., "source" -> "delphi_src").
# Format: { "source_dir_path": "git_repo_relative_path" }
GIT_SOURCE_MAPPING = {
    "source": "delphi_src",
    "schemas": "sql_srcipt/6RedGate",
}

# List of feature branches to include in the index.
# Empty list = main branch only (default/current behavior).
GIT_FEATURE_BRANCHES = []
# Example:
# GIT_FEATURE_BRANCHES = ["feature/T12549_backup_create", "feature/km_tar_71717"]
```

---

## 4. Implementation Plan

### Phase 1: Core git integration layer (new module)

**New file:** `shared/git_integration.py`

Responsibilities:
- Auto-detect git repo path from SOURCE_DIRS symlinks
- Run `git diff --name-status` to find changed files between branches
- Run `git show` to read file content from a specific branch
- Write content to temp files for reader consumption
- Compute file hashes from git blob hashes (or content)
- Manage branch manifest files

**Estimated effort:** Medium. ~300-400 lines. Well-contained, no changes to existing code.

### Phase 2: Branch-aware indexing in index_rag.py

Changes to `index_rag.py`:
- New CLI flags: `--branch <name>`, `--remove-branch <name>`, `--list-branches`
- `--branch` triggers the branch overlay indexing flow
- Branch manifest loading/saving
- Point ID namespacing for branch vectors
- `branch` field added to every point's payload

Changes to `shared/indexing.py`:
- New function `load_branch_sources(branch, cfg)` alongside existing `load_all_sources(cfg)`
- Uses git_integration to read files from git, write to temp dir, run through readers

**Estimated effort:** Medium-High. ~200 lines of changes across 2 files. Careful integration
with existing incremental logic needed.

### Phase 3: Branch-aware querying in rag_mcp.py

Changes to `rag_mcp.py`:
- Add `branch` parameter to the search tool
- Construct Qdrant `should` filter when branch is specified
- Post-retrieval dedup: prefer feature branch results over main branch
- Tombstone checking for deleted files

Changes to `shared/reranker.py`:
- Branch dedup logic (or new module `shared/branch_dedup.py`)

**Estimated effort:** Medium. ~150 lines. Must integrate with existing reranker pipeline.

### Phase 4: Backfill main branch label

One-time migration: add `branch = "develop"` to all existing vectors in the collection.
Qdrant supports payload updates without re-embedding:

```python
client.set_payload(
    collection_name="informica_rag",
    payload={"branch": "develop"},
    points=models.FilterSelector(
        filter=models.Filter(
            must_not=[
                models.FieldCondition(
                    key="branch",
                    match=models.MatchAny(any=["*"]),  # has no branch field
                )
            ]
        )
    ),
)
```

This can run as a one-time migration step, or be done lazily (treat missing `branch`
field as main branch in query logic).

**Estimated effort:** Low. ~30 lines. Can be a simple migration script or flag.

### Phase 5: Testing and validation

- Unit tests for `shared/git_integration.py`
- Integration tests: index a test branch, query, verify results
- Validation: run RAG validation suite with branch overlay active
- Edge cases: binary files, encoding issues in git show output, very large branches

**Estimated effort:** Medium. ~200 lines of tests.

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

## 7. Open Questions

1. **Should the `branch` parameter be mandatory or optional in the MCP tool?**
   Recommendation: Optional, defaulting to empty string (main branch only). This preserves
   backward compatibility. Agents that don't know about branches get the same behavior as
   today.

2. **Should we create a Qdrant payload index on the `branch` field?**
   Yes — this makes filtered queries faster. One-time setup:
   ```python
   client.create_payload_index("informica_rag", "branch", models.PayloadSchemaType.KEYWORD)
   ```

3. **How to handle the `file_datetime` metadata?**
   Git doesn't preserve file timestamps. For branch-indexed files, we can use the commit
   timestamp instead, or omit the field. This is cosmetic — it doesn't affect search quality.

4. **Should branch indexing run on CUDA or CPU?**
   For small branches (< 200 files), CPU is fine (~2-5 min). For large branches, CUDA is
   preferred. Let the existing `INDEX_EMBED_DEVICE` config control this — no special handling
   needed.

5. **Can this work with the self-index (`--config self-index`) too?**
   Yes, the architecture is generic. The self-index repo IS the RAG tool itself
   (`hybrid-code-rag-mcp`), so `GIT_REPO_PATH` would point there and `GIT_SOURCE_MAPPING`
   would map `.` to `.`. Lower priority since the self-index repo is small.

---

## 8. Summary

| Question | Answer |
|----------|--------|
| Is it feasible to read files from git without checkout? | **Yes.** `git show` reads any file from any branch in ~14ms. |
| Is the overlay model (not full duplicate) achievable? | **Yes.** Only changed files get branch-specific vectors. |
| Does Qdrant support branch-aware queries? | **Yes.** Payload filters + post-retrieval dedup. |
| Do readers need major changes? | **No.** Temp files bridge git content to existing readers. |
| What's the storage overhead? | **Minimal.** 1-13 MB per typical feature branch. |
| What's the implementation effort? | **Medium.** ~5 files changed/added, ~1000 lines total. |
| What's the main risk? | **Encoding edge cases** and **LlamaIndex filter integration.** Both manageable. |

**Verdict: Fully feasible and practical. The overlay model avoids the storage waste of
full per-branch indices while providing the exact user experience requested.**
