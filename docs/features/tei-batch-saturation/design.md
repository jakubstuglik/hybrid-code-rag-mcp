# Feature Design: TEI Batch Saturation & Cross-File Chunk Pooling

**Date:** 2026-03-20
**Status:** Phase 1 implemented (2026-03-20). See `implementation-report.md` for benchmark results.
**Branch:** `feature/tei-batch-saturation`
**TODO:** #11

---

## 1. Problem Statement

The current indexing loop in `index_rag.py` embeds chunks **one file at a time**. For each
file, it calls `embed_dense_batch()` with only that file's chunks, then upserts, then moves
to the next file. This causes three performance problems:

### 1.1 Small Batch Payloads (GPU Starvation)

Many files produce few chunks (3-10). With `DENSE_EMBED_BATCH_SIZE=32` and
`EMBED_BATCH_MAX_TOKENS=16000`, a file with 5 chunks sends a batch at ~15% of capacity.
The GPU finishes in microseconds, then idles while the CPU parses the next file, builds
nodes, checks truncation, and generates IDs.

### 1.2 TEI Padding Waste

TEI (Text Embeddings Inference) pads all sequences in a batch to the length of the longest
sequence. Within a single file, chunk sizes can vary significantly (e.g., a `class_overview`
at 3000 chars alongside a `declUses` at 200 chars). The current code sorts by length
descending within a single file's chunks, but the pool is too small for effective grouping.

Cross-file pooling would let a batch contain 32 chunks that are all ~200 chars (from
various files), followed by another batch of 32 chunks all ~3000 chars. Padding waste drops
from potentially 15x to near zero.

### 1.3 HTTP Round-Trip Overhead (TEI Only)

Each `embed_dense_batch()` call for TEI involves: JSON serialization -> HTTP POST -> TEI
tokenizes -> TEI embeds -> HTTP response -> JSON deserialization. With small batches, this
overhead dominates. Larger, fuller batches amortize the fixed per-request cost.

### 1.4 Inter-File CPU Gaps

Between files, the CPU does: tree-sitter parsing, node building, truncation checking
(tokenization), ID generation. During all of this, the GPU (or TEI container) is idle.
Pooling decouples chunk preparation from embedding, reducing idle gaps.

---

## 2. Current Architecture (Before)

```
for each file in files_to_process:           ← sequential, file-by-file
    nodes = load_nodes_for_file(file_info)    ← CPU: parse + chunk
    documents = [node.text for node in nodes]
    check_truncation(embed_model, documents)  ← CPU: tokenize
    
    embeddings = embed_dense_batch(           ← GPU/TEI: embed THIS FILE'S chunks only
        embed_model, documents, cfg=config)   
    
    # _embed_batched() sorts by length descending internally,
    # but only within this single file's chunks
    
    sparse_dicts = embed_sparse_batch(...)    ← CPU: BM25 sparse
    
    # Build points, upsert to Qdrant, update manifest
    client.upsert(...)                        ← I/O: Qdrant HTTP
    manifest["files"][file_key] = {...}
```

**Key limitation:** `_embed_batched()` at `shared/embedding.py:809` sorts documents by
length and forms batches, but it only operates on the chunks of a single file. A file with
3 chunks produces 1 undersized batch regardless of parameters.

---

## 3. Proposed Architecture (After)

### 3.1 Phase 1: Cross-File Chunk Pooling (Synchronous)

```
pool = ChunkPool(max_size=EMBED_POOL_SIZE)   ← e.g. 512 chunks

for each file in files_to_process:
    nodes = load_nodes_for_file(file_info)
    check_truncation(embed_model, documents)
    pool.add(file_key, file_info, nodes, ids, action_type)
    
    if pool.chunk_count >= EMBED_POOL_SIZE:
        flush_pool(pool)                      ← embed + upsert + manifest

flush_pool(pool)                              ← final flush for remainder


def flush_pool(pool):
    # 1. Collect all (text, file_key, chunk_index) from pool
    all_docs, all_meta = pool.collect()
    
    # 2. embed_dense_batch() handles sorting by length internally
    #    Now it sorts across ALL pooled files — similar-length chunks
    #    from different files land in the same batch
    embeddings = embed_dense_batch(embed_model, all_docs, cfg=config)
    
    # 3. sparse embedding (BM25)
    sparse_dicts = embed_sparse_batch(sparse_fn, all_docs, cfg=config)
    
    # 4. Map embeddings back to files
    per_file_results = pool.distribute_results(embeddings, sparse_dicts)
    
    # 5. Upsert per-file (preserves manifest atomicity)
    for file_key, file_data in per_file_results.items():
        build_points(file_data)
        client.upsert(...)
        manifest["files"][file_key] = {...}
    
    pool.clear()
```

### 3.2 Why Sort-Then-Batch (Not Discrete Buckets)

Two approaches were considered for reducing padding waste:

**Discrete buckets:** Maintain N buckets by length range (0-128, 128-512, etc.), flush
each bucket independently when full. Creates homogeneous batches.

**Sort-then-batch (chosen):** Pool chunks from many files, sort all by length descending,
then greedily form batches using the existing dual-governor algorithm (count limit +
token limit). Adjacent chunks in sorted order are naturally similar in length.

Sort-then-batch was chosen because:
- **Same padding-reduction benefit.** After sorting 512 chunks by length, greedy batching
  produces batches where all chunks are within a narrow length range — effectively
  continuous bucketing without discrete boundaries.
- **No partial-bucket problem.** Discrete buckets can leave chunks stranded in nearly-empty
  buckets at the end. Sort-then-batch processes all pooled chunks in one pass.
- **No manifest complexity.** With discrete buckets, a file's chunks may flush at different
  times from different buckets, requiring intermediate state tracking. Sort-then-batch
  embeds the entire pool at once, then distributes results back to files.
- **Simpler implementation.** Reuses the existing `_embed_batched()` algorithm unchanged —
  only the caller changes (passes a larger document list).

### 3.3 Pool Flush Thresholds

The pool flushes when any of these conditions is met:

1. **Chunk count threshold:** `pool.chunk_count >= EMBED_POOL_SIZE` (default: 512).
   Ensures batches are full and length-sorted across enough variety.
2. **File count threshold:** `pool.file_count >= EMBED_POOL_MAX_FILES` (default: 50).
   Bounds the number of files whose manifest update is delayed.
3. **End of input:** After the last file is chunked, flush remaining chunks regardless
   of pool size.

No time-based threshold is needed — the CPU continuously feeds chunks with no idle gaps.

### 3.4 Manifest Updates (Phase 1)

Phase 1 uses **pool-then-upsert-per-file**: all chunks in the pool are embedded together
(cross-file batches), but upsert and manifest updates happen per-file after the pool flush.

```
flush_pool():
    embed all pooled chunks (cross-file batches)
    for each file in pool:
        upsert file's points to Qdrant
        manifest["files"][file_key] = {vector_ids, hash, mtime, ...}
    save_manifest()
```

**Crash safety:** If the process crashes during a pool flush, the manifest hasn't been
updated for any file in the current pool. On restart, all files in the pool are
re-processed (re-chunked, re-embedded, re-upserted). Qdrant upsert is idempotent, so
duplicate upserts are harmless. Maximum wasted work on crash: one pool's worth of files
(~50 files, ~30 seconds of embedding).

**Phase 2 alternative (not implemented):** SQLite intermediate state tracking per-chunk,
enabling per-chunk upsert and crash-resumable embedding. Documented in section 6.2.

### 3.5 Two-Pass Hybrid Mode Compatibility

The current two-pass mode (`HYBRID_EMBED_SINGLE_PASS=False`) stores dense vectors in
SQLite after each batch via the `on_batch` callback, then does a second pass for sparse
embedding. With cross-file pooling:

- The `on_batch` callback still works — it receives `(original_indices, batch_embeddings)`
  and maps them back to the correct file's nodes via the pool's metadata.
- The second pass (sparse) operates on the same pooled documents.
- SQLite storage uses `(vector_id, dense_embedding, payload)` tuples — file affiliation
  is encoded in the vector_id and payload, so no structural change is needed.

Note: `HYBRID_EMBED_SINGLE_PASS=True` is now the default. Two-pass is kept for backward
compatibility and constrained-VRAM scenarios.

---

## 4. BM25 Sparse Encoder: Hard-Wire to CPU

### 4.1 Problem

`get_sparse_encoder()` in `qdrant/vector_store.py:52` reads `INDEX_EMBED_DEVICE` and
attempts `CUDAExecutionProvider` for BM25 when device is `"cuda"`. BM25's ONNX model is
a vocabulary lookup — GPU acceleration provides zero benefit. This also breaks deployment
on GPU-less machines where TEI runs remotely but BM25 must run locally on CPU.

### 4.2 Solution

```python
# In get_sparse_encoder():
if model_name == "Qdrant/bm25":
    # BM25 is a vocabulary lookup — always CPU, no GPU benefit
    model = SparseTextEmbedding(model_name)
    log("Sparse encoder (BM25) loaded on CPU (always CPU)")
elif device == "cuda":
    # Neural sparse models (SPLADE, etc.) benefit from GPU
    model = SparseTextEmbedding(model_name, providers=["CUDAExecutionProvider"])
    ...
```

`INDEX_EMBED_DEVICE` continues to control the device for neural sparse models (SPLADE,
future alternatives). BM25 ignores it.

---

## 5. Chunk-Length Histogram

### 5.1 Collection

During the chunking phase (inside the file processing loop), collect
`(char_length, token_length)` for every chunk. Token length is obtained from the
truncation check that already runs (`check_truncation()` tokenizes all chunks).

### 5.2 Persistence

Always saved to `{index_path}/chunk_histogram.json` after the chunking phase completes.
Format:

```json
{
  "generated_at": "2026-03-20T14:30:00",
  "config_name": "config_informica_tei_jinaai",
  "model_name": "jinaai/jina-embeddings-v2-base-code",
  "total_chunks": 140000,
  "total_files": 12400,
  "char_lengths": {
    "min": 22,
    "max": 24000,
    "mean": 1850,
    "median": 1200,
    "p10": 180,
    "p25": 450,
    "p50": 1200,
    "p75": 2800,
    "p90": 4500,
    "p95": 6000,
    "p99": 12000,
    "buckets": {
      "0-128": 4200,
      "128-256": 3100,
      "256-512": 4500,
      "512-1024": 2100,
      "1024-2048": 1800,
      "2048-4096": 980,
      "4096-8192": 420,
      "8192+": 50
    }
  },
  "token_lengths": {
    "...same structure..."
  }
}
```

### 5.3 Console Summary

After saving, log a human-readable summary:

```
Chunk length distribution (140,000 chunks from 12,400 files):
  Tokens:  P50=340  P90=1,200  P95=1,800  P99=3,100  Max=4,096
  Chars:   P50=1,200  P90=4,500  P95=6,000  P99=12,000  Max=24,000
  Saved to: index_informica/chunk_histogram.json
```

### 5.4 Tune-Embed-Params Skill Redesign

The existing skill (`.opencode/skills/tune-embed-params/SKILL.md`) will be redesigned to:

1. **Load histogram if available.** If `chunk_histogram.json` exists for the target config,
   use its percentiles to recommend parameters instead of requiring a calibration build.
2. **Model registry baseline.** The skill maintains a registry of known model characteristics:

   | Model | Attention | Max Native Seq | VRAM/token | Recommended dtype |
   |-------|-----------|---------------|------------|-------------------|
   | jinaai/jina-embeddings-v2-base-code | ALiBi O(N^2) | 8192 | ~0.09 MiB/token | float16 |
   | BAAI/bge-m3 | RoPE + Flash | 8192 | ~0.04 MiB/token | float16 |
   | nomic-ai/nomic-embed-text-v2-moe | RoPE | 8192 | ~0.03 MiB/token | float16 |

3. **Recommendation algorithm:**
   - `EMBED_MAX_SEQ_LENGTH`: Cover P99 of token lengths without exceeding VRAM budget.
     For ALiBi models, the O(N^2) bias tensor is the constraint. For RoPE/Flash, more
     headroom available.
   - `DENSE_EMBED_BATCH_SIZE`: Maximize GPU parallelism for the median chunk size.
     `floor(max_tokens * 4 / P50_char_length)` capped by VRAM.
   - `EMBED_BATCH_MAX_TOKENS`: Set to `DENSE_EMBED_BATCH_SIZE * P75_token_length` to
     ensure batches are full for typical chunks without VRAM overflow for long tails.
4. **Results saved per (codebase, model) pair** in the histogram JSON or a companion file.

---

## 6. Future Improvements (Not Implemented in Phase 1)

### 6.1 Phase 2: Async TEI HTTP Requests

**Goal:** Overlap TEI HTTP round-trips with CPU work (chunk preparation, Qdrant upsert).

**Architecture:**

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=3)

# Worker 1: TEI embed request (I/O-bound, releases GIL)
# Worker 2: Qdrant upsert (I/O-bound, releases GIL)
# Main thread: CPU parsing/chunking (holds GIL, but workers are in I/O wait)

# Pipeline:
#   Main thread prepares batch K+1 while Worker 1 embeds batch K
#   Worker 2 upserts batch K-1 results while Worker 1 embeds batch K
```

**Why this works on Python 3.12 (with GIL):**
- TEI HTTP calls are I/O-bound — the GIL is released during `urllib.request.urlopen()`.
- Qdrant upsert is I/O-bound — same GIL release.
- CPU work (parsing, building metadata) holds the GIL, but runs while I/O threads wait.
- Net effect: GPU/TEI is never idle waiting for CPU; CPU is never idle waiting for TEI.

**Why not in Phase 1:**
- Phase 1 (cross-file pooling) captures the biggest win: full batches + length homogeneity.
- Async adds complexity (error handling across threads, result ordering, cancellation).
- Measure Phase 1 results first — if GPU utilization is >80%, async isn't needed.

**Estimated additional improvement:** 10-20% throughput on top of Phase 1, for TEI only.
No benefit for PyTorch (in-process, GIL-bound tokenization is the bottleneck).

**Implementation sketch:**

```python
class AsyncTEIEmbedPipeline:
    """Overlaps TEI HTTP requests with CPU chunk preparation."""
    
    def __init__(self, embed_model, max_workers=2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.embed_model = embed_model
        self.pending_future = None
        self.pending_meta = None
    
    def submit_batch(self, documents, batch_meta):
        """Submit a batch for async embedding. Returns previous batch's results."""
        if self.pending_future is not None:
            # Wait for previous batch, return its results
            prev_results = self.pending_future.result()
            prev_meta = self.pending_meta
        else:
            prev_results = None
            prev_meta = None
        
        # Submit new batch
        self.pending_future = self.executor.submit(
            self.embed_model.get_text_embedding_batch, documents
        )
        self.pending_meta = batch_meta
        
        return prev_results, prev_meta
    
    def flush(self):
        """Wait for the last pending batch."""
        if self.pending_future is not None:
            results = self.pending_future.result()
            meta = self.pending_meta
            self.pending_future = None
            self.pending_meta = None
            return results, meta
        return None, None
```

### 6.2 Phase 3: SQLite Intermediate State for Crash-Resumable Embedding

**Goal:** Resume embedding from the last completed chunk on crash, instead of re-doing
the entire pool.

**Schema:**

```sql
CREATE TABLE chunk_state (
    file_key     TEXT NOT NULL,
    chunk_index  INTEGER NOT NULL,
    vector_id    TEXT NOT NULL,
    dense_vec    BLOB,          -- NULL until dense embedding completes
    sparse_vec   BLOB,          -- NULL until sparse embedding completes
    payload      TEXT NOT NULL,  -- JSON
    upserted     INTEGER DEFAULT 0,
    PRIMARY KEY (file_key, chunk_index)
);

CREATE INDEX idx_upserted ON chunk_state(upserted);
```

**Flow:**
1. After chunking, insert rows with `dense_vec=NULL, sparse_vec=NULL, upserted=0`.
2. After each embedding batch, update `dense_vec` (and/or `sparse_vec`) for the
   affected rows.
3. After upserting a file's points, set `upserted=1` for all that file's rows.
4. After manifest update, delete the file's rows from SQLite.
5. On crash recovery: query for `upserted=0` rows, re-embed those missing vectors,
   continue.

**Complexity:** High. Requires careful transaction management, crash-recovery testing,
and integration with both single-pass and two-pass modes.

**When to implement:** Only if Phase 1 + Phase 2 still show significant wasted work on
crash, or if pool sizes grow large enough that re-doing a pool on crash is costly
(>5 minutes).

### 6.3 Full Producer-Consumer Pipeline (Multiprocessing)

**Goal:** True CPU parallelism for parsing/chunking using `multiprocessing`, decoupled
from GPU embedding via queues.

```
[Process 1: Parse/Chunk] → mp.Queue → [Process 2: Embed (GPU)] → mp.Queue → [Process 3: Upsert]
```

**GIL considerations:**
- Python 3.12: GIL prevents thread-based CPU parallelism. `multiprocessing` is the only
  option for parallel parsing. High overhead for inter-process data transfer (pickle
  serialization of chunk texts and metadata).
- Python 3.13t (free-threaded, experimental): Could use threads instead. But 3.13t is
  not production-ready — many C extensions (numpy, torch, ONNX Runtime) have issues.
- Python 3.14+ (future): Free-threaded mode may stabilize. Revisit then.

**Estimated additional improvement:** 5-10% beyond Phase 2, mostly from overlapping
CPU parsing with GPU embedding. Diminishing returns — the bottleneck shifts to GPU
throughput once CPU stalls are eliminated.

**Not recommended** unless profiling shows CPU parsing is >20% of total wall time after
Phase 1 + Phase 2 optimizations.

---

## 7. Impact Assessment

### 7.1 TEI Path

| Metric | Before (per-file) | After Phase 1 (pooling) | After Phase 2 (async) |
|--------|-------------------|------------------------|-----------------------|
| Avg batch fullness | ~40% (many small files) | ~90%+ | ~90%+ |
| Padding waste | High (mixed sizes per file) | Low (length-sorted) | Low |
| HTTP overhead | High (many small requests) | Low (fewer, larger requests) | Minimal (pipelined) |
| GPU idle time | High (CPU gaps between files) | Medium (CPU gaps between pools) | Low (overlapped) |
| **Estimated speedup** | baseline | **20-40%** | **30-50%** |

### 7.2 PyTorch Path

| Metric | Before | After Phase 1 | Notes |
|--------|--------|--------------|-------|
| Avg batch fullness | ~40% | ~90%+ | Same benefit as TEI |
| Padding waste | Medium | Low | PyTorch also pads to max-in-batch |
| In-process overhead | Low | Low | No HTTP to amortize |
| **Estimated speedup** | baseline | **5-15%** | Less dramatic, no HTTP overhead |

### 7.3 Index Quality

**No change.** Embedding is deterministic per-text. Cross-file pooling changes which chunks
share a batch, not how individual chunks are embedded. The same text produces the same
vector regardless of batch composition.

### 7.4 Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Memory spike from pooling many chunks | Medium | `EMBED_POOL_SIZE` caps pool; flush thresholds prevent unbounded growth |
| Embedding error loses multiple files | Medium | Pool is bounded (~50 files); on crash, re-do pool (same as current save_batch_size behavior) |
| Manifest inconsistency on crash | Low | Manifest only updated after successful upsert per-file within pool flush |
| Two-pass `on_batch` callback needs pool awareness | Medium | Pass pool metadata to callback; reconstruct file affiliation from pool index mapping |
| Regression in embedding quality | None | Embedding is per-text deterministic; batch composition doesn't affect output |

---

## 8. TEI Container Parameter Tuning

TEI server-side parameters affect performance but **not embedding quality** (same model,
same vectors regardless of batch parameters).

### 8.1 Relevant Parameters

| Parameter | Current | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| `--max-batch-tokens` | TEI default (16384) | Match `EMBED_BATCH_MAX_TOKENS` or higher | Prevent TEI from splitting our already-sized batches |
| `--max-concurrent-requests` | TEI default (512) | 4-8 (Phase 2 async) | Pipeline parallelism for overlapped requests |
| `--tokenization-workers` | TEI default (platform) | 2-4 | Parallelize tokenization inside TEI container |
| `--auto-truncate` | Enabled | Keep enabled | TEI handles truncation at model's native max_length |
| `--dtype` | `float16` (GPU) / `float32` (CPU) | No change | Already correct |

### 8.2 Implementation

Update `ensure_tei_running()` in `shared/docker_utils.py` to pass `--max-batch-tokens`
and `--tokenization-workers` as Docker CMD arguments. Values derived from config.

---

## 9. Implementation Plan

### Phase 1 (This PR)

| Step | Description | Files | Priority |
|------|-------------|-------|----------|
| 1a | Chunk-length histogram collection + save to JSON | `index_rag.py` | Medium |
| 1b | `ChunkPool` class (pool, collect, distribute results) | `shared/chunk_pool.py` (new) | High |
| 1c | Refactor `index_rag.py` main loop to use ChunkPool | `index_rag.py` | High |
| 1d | Pool flush logic (embed cross-file, upsert per-file, manifest per-file) | `index_rag.py` | High |
| 1e | `EMBED_POOL_SIZE` config parameter | `config.py` | Medium |
| 1f | Two-pass hybrid mode compatibility with pooling | `index_rag.py` | High |
| 1g | TEI `--max-batch-tokens` and `--tokenization-workers` | `docker_utils.py` | Medium |
| 1h | BM25 hard-wired to CPU | `qdrant/vector_store.py` | Medium |
| 1i | Unit tests for ChunkPool, histogram, BM25 CPU | `src_test/` | High |
| 1j | Benchmark: per-file vs pooled on test_sources (TEI + PyTorch) | Manual | High |
| 1k | Redesign tune-embed-params skill (histogram + model registry) | `.opencode/skills/` | Medium |

### Phase 2 (Future PR, documented here)

- Async TEI HTTP requests via `ThreadPoolExecutor` (see section 6.1)
- Only if Phase 1 benchmark shows GPU utilization still <80%

### Phase 3 (Future, documented here)

- SQLite intermediate state for crash-resumable embedding (see section 6.2)
- Full producer-consumer pipeline (see section 6.3)
- Only if profiling justifies the complexity

---

## 10. Config Parameters (New)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_POOL_SIZE` | 512 | Max chunks to accumulate before flushing for cross-file batch embedding. Larger = better length homogeneity, more memory. |
| `EMBED_POOL_MAX_FILES` | 50 | Max files in pool before flush. Bounds manifest update delay. |
| `TEI_MAX_BATCH_TOKENS` | None | Override for TEI `--max-batch-tokens`. Auto-derived from `EMBED_BATCH_MAX_TOKENS` when None. |
| `TEI_TOKENIZATION_WORKERS` | None | Override for TEI `--tokenization-workers`. Auto-detected when None. |
