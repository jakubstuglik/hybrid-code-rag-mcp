# Git Overlays (Branches and Moving Tags)

When `SOURCE_DIRS` uses the `type: "git_repo"` format, the indexer can store branch and tag overlays on the main branch. Only files that differ are indexed under the overlay label. Unchanged files are served from the main-branch vectors.

**Config example:**

```python
SOURCE_DIRS = [
    {
        "type": "git_repo",
        "path": "../my-repo",
        "main_branch": "develop",
        "branches": ["feature/my-feature"],  # legacy: kind branch
        "overlays": [
            {"name": "feature/my-feature", "kind": "branch"},
            {
                "name": "current_release",
                "kind": "tag",
                "diff": "against_main_tip",
            },
        ],
        "sources": [
            {"path": "src", "extensions": [".py", ".js"]},
            {"path": "sql", "extensions": [".sql"], "sql_dialect": "tsql"},
        ],
    },
    # Non-git entries are included in every query
    {
        "type": "source_set",
        "path": "./docs",
        "extensions": [".md"],
    },
]
```

`name` is the label written on each point and the string passed to search. It is not parsed to decide whether the ref is a branch or a tag. `kind` decides that. `kind` defaults to `"branch"`; a tag overlay must also set `diff: "against_main_tip"`.

**Moving release tag.** The `tag` kind is meant for a tag such as `current_release` that you re-point as releases happen (for example `git tag -f current_release <commit>` followed by `git push -f origin current_release`). The overlay holds only the files where the release differs from the main tip. Because the tag moves along with main, the overlay stays small instead of growing with every release. Searching with `branch="current_release"` returns the released version of those files without a second full index.

**How it works:**

1. **Main branch indexing** runs first (full incremental refresh as usual). Every vector gets a `branch` payload field set to the `main_branch` name. This pass reads the working tree, so the checkout must be `main_branch`.
2. **Overlay indexing** runs for each configured overlay. Blobs are read with `git show` after the ref is peeled to a commit. Nothing is checked out and no worktree is created. A detached HEAD in the working copy does not affect the overlay. If the configured branch or tag does not exist in the repo, the run logs a warning and skips that overlay; its stored points stay.
   - **kind `branch`** (including every name in the legacy `branches` list): three-dot diff from the merge-base. That is the commits on the branch since it left main.
   - **kind `tag` with `diff: "against_main_tip"`**: `git diff` between the main tip and the tag commit. The set is every path whose content differs, including paths that exist on only one side. Annotated and lightweight tags both peel with `rev-parse <name>^{commit}`.
3. **Backfill migration** automatically adds `branch` metadata to any existing vectors that lack it (one-time, runs on every indexing pass until all vectors have the field).

> **Upgrade order.** Upgrade the MCP server(s) before or together with the indexer. Tombstones are published as reserved Qdrant points whose ids now include `INDEX_STATE_TOMBSTONES_PER_POINT`. A server from before this change (0.22.0 and older) cannot find those points: it logs `tombstone part ... is missing` and, with no local manifest, treats the overlay as having no tombstones, so a branch search can return chunks of files the overlay deleted. An older indexer with a newer server is safe, and state published by an older release is migrated by the next publish.

Point ids are `uuid5` of `{label}::{file_key}:{index}`. Two overlays that touch the same path get different points. A path deleted on the overlay side (present on main, missing at the overlay commit) is not embedded. It becomes a tombstone that hides the main-branch version at query time. Renames are split into a delete of the old path and an add of the new path.

**Overlay manifest.** Each overlay has its own `index_manifest_branch_<sanitized-name>.json` next to the main manifest. Tag overlays use the same file-name pattern.

| Field | Kind | Meaning |
|-------|------|---------|
| `branch` | both | Configured overlay name. |
| `kind` | both | `"branch"` or `"tag"`. A manifest written before this field existed counts as a tag when it has `last_resolved_commit`, otherwise as a branch. |
| `files` | both | Indexed paths with content hash and point ids. |
| `tombstones` | both | Paths the overlay deletes. |
| `indexed_at` | both | UTC time of the last completed run. |
| `overlay_signature` | both | Fingerprint used by the fast path (see below). |
| `merge_base`, `last_branch_commit` | branch | Merge-base with main and the branch head at the last run. Left `null` on tag manifests. |
| `last_resolved_commit` | tag | Commit the tag pointed at (peeled) at the last run. |

**Re-runs and tag moves.** On each run the ref is resolved again and the diff is recomputed. The files in the diff are read and hash-compared with the manifest, and only new or changed files are embedded. Paths that drop out of the diff become deletes of that overlay's points. For a tag this covers moves in either direction: files that now match main lose their overlay points, and a tag that points at the main tip ends up as an empty overlay. A branch with an empty three-dot diff still skips and keeps its points, which is the previous behavior.

**Fast path for unchanged overlays.** Before any file is read, the indexer computes `overlay_signature`. It is a SHA-256 of the kind, the overlay commit, the base (merge-base for a branch, main tip for a tag) and the repo group's source settings (paths, extensions, excludes, SQL dialect and similar). The overlay lists are left out, so adding or removing another overlay does not invalidate it. If the signature equals the one stored by the last completed run and Qdrant still has points for the label (checked only when the manifest lists files), the overlay is skipped without `git show` or hashing:

```
[TAG] current_release overlay is up to date (refs unchanged)
```

For a tag, moving the tag or a new commit on main changes the signature. For a branch, a new branch commit or a new merge-base does (main commits that leave the merge-base alone do not, since they do not change the three-dot diff). A change to the group's source settings changes it for both. A changed signature runs the normal hash compare. Manifests written before the signature existed get one normal compare on their first run, which stores it. Neither the config nor the index needs changing. When the manifest lists files but Qdrant has no points for the label (for example after the collection was cleared), the fast path is not taken. Known limitation: a file that failed to embed is not retried while the refs and settings stay the same. It is picked up on the next run where they change, or after `--clear`.

Overlay log lines are prefixed `[BRANCH]` or `[TAG]` according to the overlay kind.

The indexer does not move tags; it reads the local ref. `src/git_pull_guard.py` (the pull step) force-updates every configured tag overlay from `origin` with `git fetch origin +refs/tags/<name>:refs/tags/<name>`, because a normal `git fetch` does not move a tag that already exists locally. Only configured tags are forced; other tags and branches are untouched. If that fetch fails (no remote, no credentials, tag missing on the remote), the pull step logs a warning and the indexer uses the local tag. Without the pull step, update the local tag yourself before running the indexer.

**Migrating existing branch overlays:**

Leave `branches: ["feature/example"]` as it is, or write the same name as `{"name": "feature/example", "kind": "branch"}`. Indexing results stay the same: point ids, `branch` payload, manifest file names, and the three-dot diff. No rebuild is required for those overlays. Add a tag overlay when you want a release label. The next index run creates it. Existing collections do not need `--clear`.

**Incremental main-branch comparison (Cases A/B/C):**

For `git_repo` entries, change detection uses git metadata in addition to file hashes:

- **Case A** (commit unchanged): The stored commit equals the current HEAD. Files with matching `mtime` are skipped without reading disk -- only new/modified files (different mtime) go through hash comparison.
- **Case B** (commit advanced): A `git diff` between the stored and current commit identifies exactly which files changed. Only those files (plus any with differing mtime outside the diff) are re-embedded. If the diff covers more than `DIFF_FULL_REINDEX_THRESHOLD` (default 50%) of indexed files, a full hash scan runs instead.
- **Case C** (no stored commit or git unavailable): Full hash scan against all files on disk. This is the baseline behavior used for `source_set` entries and as a fallback when git operations fail.

A `.sql` file whose `sql_dialect` differs from the manifest is re-chunked on every case, including when the hash and mtime match. A missing manifest value means `tsql`.

`source_set` entries always use Case C (hash comparison only).

**Querying:**

The MCP search tool takes an optional `branch` argument. There is no second parameter for tags. Pass a configured overlay name:

- **Empty**: main-branch chunks plus non-git chunks.
- **`branch="feature/example"`** or **`branch="current_release"`**: main plus that overlay, plus non-git chunks. Post-retrieval dedup keeps the overlay version of a path. Tombstones hide files the overlay deletes. The exact symbol lookup is in that pass: a main-branch hit is dropped when the overlay has the path or a tombstone hides it, whether the overlay copy came from the main retrieval or from the lookup. The reranker then runs on what remains.
- **Name never indexed**: the filter matches no extra points, so the result is the main branch (plus non-git chunks).

`git branch --show-current` is the right value when that branch is configured as an overlay. A tag overlay uses the tag's configured name, which is not the output of `git branch --show-current`.

**Cleanup:** removing an overlay from config and re-running the indexer deletes that label's points, its manifest and its chunk histogram (`chunk_histogram_branch_<sanitized-name>.json`). The cleanup log takes the kind from the manifest, for example `[TAG] Cleaning up removed tag: current_release`.
