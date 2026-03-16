# Model Tracking in Qdrant Collections

**TODO #5** — Store which dense and sparse embedding models were used to build a Qdrant collection, and auto-detect them at indexing and query time to prevent silent vector space mismatches.

---

## Problem Statement

When a Qdrant collection is queried, the query vector must be embedded with the **exact same model** that was used at index time. Dense and sparse vector spaces are model-specific and incompatible across models.

Currently, model names are read from `config.py` (`MODEL_NAME`, `SPARSE_MODEL_NAME`) at both index and query time. If a user:

1. Indexes a collection with model A
2. Changes `MODEL_NAME` in `config.py` to model B
3. Queries the collection (MCP server starts, loads model B)

→ Query vectors are in model B's space; collection vectors are in model A's space. Results will be **garbage** with no error or warning. This is a silent failure.

---

## What Needs to Be Tracked

| Field | Description |
|---|---|
| `dense_model` | HuggingFace model ID used for dense embedding (e.g., `jinaai/jina-embeddings-v2-base-code`) |
| `sparse_model` | Sparse model name (e.g., `Qdrant/bm25`) |
| `dense_dims` | Embedding dimension (e.g., 768) — useful for schema validation |
| `indexed_at` | ISO timestamp of last full indexing run |
| `indexer_version` | Optional: version string from the indexer to track breaking changes |

---

## Where to Store the Metadata

Qdrant does not have a native collection-level user metadata field. Three options:

### Option A — Sidecar JSON File

Store metadata in a `collection_meta.json` file in the same directory as the manifest file (e.g., `<BASE_PATH>/<COLLECTION_NAME>/collection_meta.json`).

```json
{
  "dense_model": "jinaai/jina-embeddings-v2-base-code",
  "sparse_model": "Qdrant/bm25",
  "dense_dims": 768,
  "indexed_at": "2026-03-16T14:23:05Z",
  "indexer_version": "1.0"
}
```

**Pros:** Simple. No Qdrant API changes. Sits next to the existing manifest JSON.  
**Cons:** File can get out of sync with the Qdrant collection if the Qdrant volume is moved or re-created. Requires the caller to have filesystem access.

### Option B — Qdrant "Meta" Point

Store metadata as a single Qdrant point with a reserved ID (e.g., ID `0` or a UUID constant) and `node_type = "_collection_meta"` payload. Indexer upserts this point on every run; MCP server retrieves it at startup.

```python
# Pseudo-code
meta_point = PointStruct(
    id=0,
    vector={"dense": [0.0] * dims},   # dummy zero vector (not searched)
    payload={
        "node_type": "_collection_meta",
        "dense_model": "jinaai/jina-embeddings-v2-base-code",
        "sparse_model": "Qdrant/bm25",
        "dense_dims": 768,
        "indexed_at": "2026-03-16T14:23:05Z",
    }
)
client.upsert(collection_name=COLLECTION_NAME, points=[meta_point])
```

**Pros:** Metadata is stored inside Qdrant — moves with the collection on backup/restore. Accessible without filesystem access.  
**Cons:** Slightly more complex. A zero-vector meta point might theoretically appear in search results (must be filtered out via `node_type != "_collection_meta"` in all queries — or use `must_not` filter). Requires Qdrant API version that supports payload filtering (current version does).

### Option C — Separate "Meta" Collection

A separate Qdrant collection named `<COLLECTION_NAME>_meta` stores one record per tracked collection.

**Pros:** Clean separation from data vectors.  
**Cons:** Two collections to manage. More overhead. Not worth the complexity.

**Recommendation: Option A (sidecar JSON) for simplicity**, with Option B as the upgrade path if portability becomes important. The sidecar file sits alongside the existing manifest files and uses the same read/write infrastructure.

---

## Behavior Design

### At Index Time (`index_rag.py`)

1. After successful embedding and upsert, write `collection_meta.json` with current model names
2. If `collection_meta.json` already exists and models differ from config → **warn** and prompt the user:
   - "Collection was built with model A. Config specifies model B. Continuing will corrupt the collection. Use `--clear` to rebuild from scratch."
   - If `--yes` is passed without `--clear`, abort with error
   - If `--clear --yes` is passed, proceed (full rebuild)

### At MCP Query Time (`rag_mcp.py`)

1. On startup, read `collection_meta.json`
2. Compare stored `dense_model` / `sparse_model` against current config values
3. If mismatch:
   - **Option 1 (strict):** Log error and exit — the server refuses to start with mismatched models
   - **Option 2 (auto-switch):** Log a warning, ignore config model names, and load the models from `collection_meta.json`
4. If `collection_meta.json` does not exist (old index without tracking):
   - Log a warning: "No model metadata found. Assuming config models match the index."
   - Proceed with config values (backward compatible)

**Recommendation:** Auto-switch (Option 2) at query time. The MCP server should always be able to serve queries; refusing to start is disruptive. Auto-switching with a clear warning is the better user experience. At index time, the strict check is appropriate because silently re-embedding with the wrong model is a data integrity problem.

---

## Implementation Plan

### 1. New module: `shared/collection_meta.py`

```python
def write_collection_meta(cfg, dense_model: str, sparse_model: str, dense_dims: int) -> None:
    """Write collection metadata to sidecar JSON."""

def read_collection_meta(cfg) -> dict | None:
    """Read collection metadata from sidecar JSON. Returns None if file missing."""

def check_model_mismatch(cfg, meta: dict) -> tuple[bool, str]:
    """Returns (has_mismatch, message). Returns (False, "") if models match."""
```

### 2. Changes to `src/index_rag.py`

- After successful indexing run: call `write_collection_meta(cfg, ...)`
- Before indexing (if `collection_meta.json` exists and models differ): warn/abort logic

### 3. Changes to `src/rag_mcp.py`

- At startup (in `_build_index()`): read `collection_meta.json`, compare, log warning if mismatch, use stored model names if auto-switching

### 4. Config path for sidecar file

```python
# collection_meta.json lives alongside the manifest
meta_path = Path(cfg.BASE_PATH) / cfg.COLLECTION_NAME / "collection_meta.json"
```

This is consistent with where `index_manifest.json` is stored today.

---

## Edge Cases

| Case | Behavior |
|---|---|
| First-ever index (no meta file yet) | Write meta file after successful run |
| Index with `--clear` | Delete old meta file, write new one after reindex |
| Meta file exists, models match | No-op, proceed normally |
| Meta file exists, models differ (index run) | Error with clear message, require `--clear --yes` |
| Meta file exists, models differ (MCP server) | Warning + auto-switch to stored models |
| Meta file missing (MCP server) | Warning "no metadata", use config models |
| Multiple branches in same collection | Single meta file covers all branches (same models) |

---

## Related TODOs
- **TODO #1** — Becomes critical when switching embedding models; model tracking prevents silent mismatches
- **TODO #3** — If library docs are indexed in a separate collection, each collection needs its own metadata
