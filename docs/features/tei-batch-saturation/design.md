# Feature Design: TEI Batch Saturation & Cross-File Chunk Pooling

**Date:** 2026-03-20
**Status:** Phase 1-4 + Optimization #1 implemented (2026-03-25). See `implementation-report.md` for benchmark results.
**Branch:** `master` (formerly `feature/tei-batch-saturation`)
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

Main-branch histograms are saved to `{index_path}/chunk_histogram.json` after the
chunking phase completes. Branch overlay histograms are saved separately as
`{index_path}/chunk_histogram_branch_<sanitized_name>.json` to prevent overwriting
the main-branch histogram.

The `--calculate-histogram` CLI flag generates histograms without embedding or Qdrant:

```bash
python src/index_rag.py --config <config-name> --calculate-histogram
```

This reads all source files through the reader pipeline (chunking only) and produces
`chunk_histogram.json` for the main branch plus per-branch variants for any configured
overlays. No embedding model, Docker, or Qdrant is needed.

Format:

```json
{
  "generated_at": "2026-03-20T14:30:00",
  "config_name": "config_myproject",
  "model_name": "jinaai/jina-embeddings-v2-base-code",
  "branch": "",
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

The `branch` field is empty for main-branch histograms and contains the branch name
(e.g., `"task/T37523"`) for overlay histograms.

### 5.3 Console Summary

After saving, log a human-readable summary:

```
Chunk length distribution (140,000 chunks from 12,400 files):
  Tokens:  P50=340  P90=1,200  P95=1,800  P99=3,100  Max=4,096
  Chars:   P50=1,200  P90=4,500  P95=6,000  P99=12,000  Max=24,000
  Saved to: index_myproject/chunk_histogram.json
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

### 6.1 Phase 2: Double-Buffered Pool Flush (Implemented)

**Goal:** Overlap Qdrant upsert I/O of pool N with dense embedding of pool N+1,
eliminating GPU idle time between pool flushes.

**Problem (measured from Phase 1 pooltest run):**
- Embedding takes 74% of wall-clock (907s), upsert takes 22% (271s).
- The synchronous flush cycle (embed → sparse → upsert → next pool) creates structural
  GPU starvation: 33.9% of GPU samples are idle (≤5% utilization).
- TEI logs show 51.7% of wall-clock spent in >1s gaps between embedding bursts.
- 73 sawtooth cycles visible in GPU utilization graph.

**Architecture: double-buffered upsert via background thread:**

```
Synchronous (Phase 1):
  [embed pool 1] [upsert pool 1] [embed pool 2] [upsert pool 2] ...
                  ^^^^^ GPU idle                  ^^^^^ GPU idle

Double-buffered (Phase 2):
  [embed pool 1] [embed pool 2    ] [embed pool 3    ] ...
                 [upsert pool 1   ] [upsert pool 2   ]
                  ^^^^^ overlapped   ^^^^^ overlapped
```

**Implementation:**

```python
from concurrent.futures import ThreadPoolExecutor, Future

# Single background thread for upsert I/O
_upsert_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="upsert-worker")
_pending_upsert: Optional[Future] = None

def _flush_pool():
    # 1. Wait for previous pool's upsert to finish (if any)
    _drain_pending_upsert()

    # 2. Embed current pool (GPU-bound — this is the critical path)
    all_docs, file_entries = pool.collect()
    dense_embeddings = embed_dense_batch(embed_model, all_docs, cfg=config)
    sparse_dicts = embed_sparse_batch(sparse_fn, all_docs, cfg=config)

    # 3. Build per-file upsert work items (CPU — fast, <1ms per file)
    upsert_work = prepare_upsert_work(pool, dense_embeddings, sparse_dicts)

    # 4. Submit upsert to background thread (I/O-bound, releases GIL)
    _pending_upsert = _upsert_executor.submit(_do_upsert_work, upsert_work)

    # 5. Main thread returns immediately → starts filling next pool
    pool.clear()

def _do_upsert_work(work_items):
    """Runs on background thread. Upserts per-file, updates manifest."""
    for item in work_items:
        client.upsert(collection_name, item.points)   # I/O, releases GIL
        manifest["files"][item.file_key] = ...         # dict update
    # [upsert-worker] log prefix on all messages

def _drain_pending_upsert():
    """Block until the previous upsert finishes. Propagate exceptions."""
    if _pending_upsert is not None:
        _pending_upsert.result()  # raises if upsert failed
```

**Why this works on Python 3.12 (with GIL):**
- Qdrant upsert is I/O-bound (HTTP/gRPC to Docker container) — the GIL is released
  during network I/O.
- While the background thread waits for Qdrant I/O, the main thread runs
  `embed_dense_batch()` which calls TEI (also I/O-bound HTTP) — no GIL contention.
- CPU work between flushes (parsing, chunking) is GIL-bound but finishes before the
  next flush, so there's no contention with the upsert thread.

**Why double-buffer, not full producer-consumer:**
- Upserts are fast and consistent: mean 0.83s, max 2s (from pooltest analysis).
- Double-buffer hides upsert for 86.5% of flush transitions (283 of 327).
- Full producer-consumer would save only 21s more (0.4 min) — 1.7% of wall-clock.
- The remaining 13.5% of stalls occur in the late SQL region where `EMBED_POOL_MAX_FILES`
  forces flushes with tiny pools (~100 chunks). Fixed by raising `EMBED_POOL_MAX_FILES`
  from 50 to 150 (see section 6.1.1).

**Thread safety considerations:**
- `manifest` dict is written by both main thread (delete phase) and upsert thread
  (add/modify phase). The `_drain_pending_upsert()` call at the start of each flush
  ensures no concurrent writes — double-buffer means at most one upsert in flight.
- `_save(manifest)` only runs after `_drain_pending_upsert()` completes.
- Qdrant client (`qdrant_client.QdrantClient`) is thread-safe for upsert operations.
- `processed_since_save` counter is only updated after drain, in the main thread.

**Error handling:**
- If upsert fails in the background thread, the exception is captured by the Future.
- `_drain_pending_upsert()` calls `future.result()` which re-raises the exception
  in the main thread before the next embed starts.
- On error, the main thread logs the failure and continues (same as synchronous path).

**Logging requirement:**
- All log messages from the background upsert thread are prefixed with `[upsert-worker]`.
- The main thread's embedding messages have no prefix (default).
- This makes interleaved log output from both threads distinguishable.

#### 6.1.1 Config Change: EMBED_POOL_MAX_FILES 50 → 150

Raising the file limit eliminates GPU stalls in the late SQL region where many tiny
files (1-2 chunks each) triggered frequent flushes with undersized pools.

**Memory safety analysis (from pooltest run):**
- VRAM: unaffected. TEI manages GPU memory via HTTP; pool size has zero effect on VRAM.
  5.2 GB headroom (63%).
- System RAM: worst-case double-buffered peak is ~33 MB (monster file) against 9.6 GB
  free. Pool size changes don't affect this — `EMBED_POOL_SIZE=512` is the binding
  constraint in >95% of flushes.
- With `MAX_FILES=150`: tiny-file flushes accumulate ~150 files × ~2 chunks = ~300 chunks
  (still under `POOL_SIZE=512`). Embedding time (~2-3s) exceeds upsert time (~1s),
  ensuring double-buffer fully hides upsert.

**Crash safety:** worst-case re-do grows from 50 to 150 files. Since those 150 files
are tiny (total ~300 chunks, ~3s of embedding), the re-do cost is negligible.

**Benchmark results (Phase 2, partial run — 2 minutes / 24 flush cycles):**

The double-buffer was benchmarked and proved to be **architecturally correct but solving
a non-problem.** The real bottleneck is not upsert I/O.

| Metric | Phase 1 (measured) | Phase 2 (2 min sample) | Notes |
|--------|-------------------|------------------------|-------|
| Avg GPU util | 38.5% | 44.2% (+5.7pp) | Small sample, may include startup effects |
| Idle samples (0-5%) | 33.9% | 5.7% (-28pp) | Promising but sample too small |
| Sawtooth drops/min | 3.6 | 1.0 (-72%) | Sawtooth still present |
| Per-cycle upsert time | 0.83s avg | overlapped | Double-buffer works correctly |
| Per-cycle embed time | ~3s | ~3s | Unchanged — this is the critical path |
| Per-cycle CPU gap | ~1s | ~1s | NOT addressed by double-buffer |

**Key finding:** The sawtooth GPU pattern persists because it is caused by the **~1s CPU
gap between embedding passes** (file parsing, chunking, pool filling), not by upsert
blocking. The double-buffer hides the 0.83s average upsert, but the CPU gap was always
running concurrently with upsert anyway. Net savings: ~0.3s per flush cycle (~20s total
over a full run), which is negligible against the 20.4 min total.

**Flush cycle timeline (Phase 2):**
```
[embed ~3s GPU] → [drain ~0s] → [sparse BM25 ~0.04s] → [build points ~0s] → [submit upsert]
                                                                                ↓
                                                                     [background: upsert ~0.8s]
                                                                                ↓
[parse/chunk next files ~1s CPU] → [next embed ~3s GPU] → ...
      ↑ THIS is the actual bottleneck — GPU is idle during parse/chunk
```

**Decision (2026-03-20):** Keep Phase 2 as-is. The double-buffer is correct, low-risk,
adds ~50 lines of thread code. The negligible speedup doesn't justify reverting, and the
infrastructure supports future optimizations. But the sawtooth problem is deferred — see
section 6.4 for the proposed solution.

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

### 6.4 Parse-Ahead Thread (Implemented in Phase 4)

**Status:** Implemented and verified (2026-03-25, commit `f768736`). Combined with HNSW
deferral (Option C), achieved 11.7 min total indexing time (was 15.4 min, -23.8%).

**Root cause of sawtooth GPU pattern:** Between embedding passes, the main thread spends
~1s on CPU work (file parsing via tree-sitter, node building, truncation checking,
ID generation, pool accumulation). The GPU is idle during this time. The double-buffer
(Phase 2) hides upsert I/O but cannot hide CPU work that runs on the main thread.

**Proposed fix — parse-ahead thread:**

```
Main thread:              [embed pool N] [embed pool N+1] [embed pool N+2] ...
Parse-ahead thread:  [parse → pool N+1] [parse → pool N+2] [parse → pool N+3] ...
Upsert thread:            [upsert N-1 ] [upsert N    ] [upsert N+1   ] ...
```

The parse-ahead thread fills the next `ChunkPool` while the main thread is embedding
the current pool. When embedding finishes, the next pool is already full and ready to
embed immediately — eliminating the ~1s CPU gap.

**Implementation sketch:**
1. Two `ChunkPool` instances: `pool_current` (being embedded) and `pool_next` (being filled).
2. A `threading.Thread` runs the file-iteration loop, calling `load_nodes_for_file()` and
   `pool_next.add()`. When `pool_next` is full, it signals the main thread and blocks.
3. The main thread swaps pools: `pool_current, pool_next = pool_next, ChunkPool()`, then
   embeds `pool_current` while the parse thread resumes filling the new `pool_next`.

**GIL concern:** Tree-sitter parsing is a C extension that releases the GIL. The ~1s
parse/chunk time is mostly in tree-sitter and tokenizer C code, so true parallelism with
the embedding HTTP call is achievable even with the GIL. The Python-side overhead
(node building, ID generation) is small.

**Estimated improvement:** ~1s saved per flush cycle × ~70 cycles = ~70s (~5.7% of 20.4 min).
Modest but real. Actual measured result: 115.6s inter-flush gap reduction (201→85.4s),
plus 68.4s parse_file regression fix from HNSW deferral = 219s total savings (-23.8%).

**Implementation (Phase 4):**

Instead of the dual-pool approach sketched above, the actual implementation uses a
`queue.Queue(maxsize=2)` with `_ParsedFile` dataclass results:

1. A `_parser_thread_fn()` closure iterates `files_to_process`, calls
   `load_nodes_for_file()`, generates IDs/documents, puts results on the queue.
2. The main loop changed from `for file_index, file_key in enumerate(...)` to
   `while True: parsed = _parse_queue.get()` with `None` sentinel.
3. `TimingTracker.record()` method records pre-measured parse times from the background
   thread.
4. HNSW deferral (`indexing_threshold=200000`) runs before the processing loop, restored
   to 10000 after all upserts complete.

See `implementation-report.md` Phase 4 for full benchmark results.

---

## 7. Impact Assessment

### 7.1 TEI Path

| Metric | Before (per-file) | After Phase 1 (pooling) | After Phase 2 (double-buffer) | **After Phase 4 (parse-ahead + HNSW defer)** |
|--------|-------------------|------------------------|-----------------------|----------------------------------------------|
| Avg batch fullness | ~40% (many small files) | ~90%+ | ~90%+ | ~90%+ |
| Padding waste | High (mixed sizes per file) | Low (length-sorted) | Low | Low |
| HTTP overhead | High (many small requests) | Low (fewer, larger requests) | Low (unchanged from Phase 1) | Low |
| GPU idle time | High (CPU gaps between files) | Medium (CPU gaps between pools) | Medium (upsert overlapped, CPU gap remains) | **Low (parse overlapped, HNSW deferred)** |
| **Measured speedup** | baseline | **22.3%** (measured) | **~1.5% additional** (estimated from partial run) | **53.2% total vs baseline** (11.7 min) |

**Phase 2 conclusion:** The double-buffer correctly overlaps upsert I/O with embedding,
but upsert was never the dominant gap. The ~1s CPU gap (file parsing/chunking) between
embedding passes is the remaining bottleneck. See section 6.4 for proposed future fix.

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

### Phase 2 (This PR)

| Step | Description | Files | Priority |
|------|-------------|-------|----------|
| 2a | Double-buffered `_flush_pool()` with background upsert thread | `index_rag.py` | High |
| 2b | `[upsert-worker]` log prefix on background thread messages | `index_rag.py` | High |
| 2c | `EMBED_POOL_MAX_FILES` default 50 → 150 | `config.py` | High |
| 2d | `_drain_pending_upsert()` with error propagation | `index_rag.py` | High |
| 2e | Graceful executor shutdown on completion and error paths | `index_rag.py` | High |
| 2f | Unit tests for double-buffer logic | `src_test/` | High |
| 2g | Benchmark: synchronous vs double-buffered on production index | Manual | High |

### Phase 3 (Future, documented here)

- SQLite intermediate state for crash-resumable embedding (see section 6.2)
- Full producer-consumer pipeline (see section 6.3)
- Only if profiling justifies the complexity

---

## 10. Config Parameters (New)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_POOL_SIZE` | 512 | Max chunks to accumulate before flushing for cross-file batch embedding. Larger = better length homogeneity, more memory. |
| `EMBED_POOL_MAX_FILES` | 150 | Max files in pool before flush. Bounds manifest update delay. Raised from 50→150 in Phase 2 to eliminate GPU stalls in small-file regions. |
| `TEI_MAX_BATCH_TOKENS` | None | Override for TEI `--max-batch-tokens`. Auto-derived from `EMBED_BATCH_MAX_TOKENS` when None. |
| `TEI_TOKENIZATION_WORKERS` | None | Override for TEI `--tokenization-workers`. Auto-detected when None. |
