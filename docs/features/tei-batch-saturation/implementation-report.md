# TEI Batch Saturation: Implementation Report

**Date:** 2026-03-20
**Branch:** `feature/tei-batch-saturation`
**TODO:** #11
**Design document:** `docs/features/tei-batch-saturation/design.md`

---

## 1. Problem Statement

The indexing loop in `index_rag.py` embedded chunks **one file at a time**. Each file's
chunks (often 3-10) were sent as an undersized batch to TEI or PyTorch, causing:

- **GPU starvation** — small batches finish in microseconds, then the GPU idles while the
  CPU parses the next file.
- **TEI padding waste** — TEI pads all sequences in a batch to the longest. Within a single
  file, chunk sizes vary widely (200-char `declUses` alongside 3000-char `class_overview`).
- **HTTP round-trip overhead** — many small TEI requests instead of fewer, larger ones.
- **Inter-file CPU gaps** — GPU/TEI idle during tree-sitter parsing, node building,
  truncation checking, and ID generation between files.

See design.md sections 1.1-1.4 for the detailed analysis.

---

## 2. Solution Architecture

### 2.1 Cross-File Chunk Pooling (Phase 1)

The core change: accumulate chunks from multiple files into a `ChunkPool`, then embed
all pooled chunks together. The existing `_embed_batched()` sort-by-length algorithm
now operates across files, naturally grouping similar-length chunks into batches.

```
for each file in files_to_process:
    nodes = load_nodes_for_file(file_info)
    pool.add(file_key, file_info, nodes, ids, action_type)

    if pool.chunk_count >= EMBED_POOL_SIZE or pool.file_count >= EMBED_POOL_MAX_FILES:
        _flush_pool(pool)      # embed cross-file, upsert per-file, manifest per-file

_flush_pool(pool)              # final flush for remainder
```

Pool flush thresholds:
- **EMBED_POOL_SIZE** (default 512) — max chunks before flush
- **EMBED_POOL_MAX_FILES** (default 50) — max files before flush
- **End of input** — flush remainder after last file

### 2.2 Key Components

| Component | File | Description |
|-----------|------|-------------|
| `ChunkPool` | `src/shared/chunk_pool.py` | Accumulates `FileEntry` objects with nodes, IDs, and metadata. Provides `collect()` to gather all texts and `distribute_results()` to map embeddings back to files. |
| `ChunkHistogram` | `src/shared/chunk_pool.py` | Collects `(char_length, token_length)` per chunk during chunking. Saves to `chunk_histogram.json` with percentile stats. Used by tune-embed-params skill. |
| `_flush_pool()` | `src/index_rag.py` | Orchestrates: collect all texts -> embed dense (cross-file) -> embed sparse -> distribute back -> upsert per-file -> manifest per-file. |
| `_make_manifest_entry()` | `src/index_rag.py` | DRY helper for building manifest entry dicts (replaced 4 duplicate code paths). |
| `_sparse_dicts_to_vectors()` | `src/index_rag.py` | Converts sparse dicts to SparseVector objects (replaced 3 duplicate conversions). |
| `_build_qdrant_points()` | `src/index_rag.py` | Builds PointStruct objects from nodes + embeddings (replaced 2 duplicate builders). |
| `_upsert_and_record()` | `src/index_rag.py` | Upserts in batches of 500 and records in manifest (replaced 2 duplicate paths). |
| `build_branch_resolver()` | `src/index_rag.py` | Unified branch resolver factory (replaced per-source-type resolver construction). |

### 2.3 BM25 Hard-Wired to CPU

`get_sparse_encoder()` in `qdrant/vector_store.py` now always loads `Qdrant/bm25` on CPU
regardless of `INDEX_EMBED_DEVICE`. BM25 is a vocabulary lookup with zero GPU benefit.
Neural sparse models (SPLADE) still respect the device setting.

### 2.4 TEI Container Parameters

`ensure_tei_running()` in `docker_utils.py` now passes `--max-batch-tokens` and
`--tokenization-workers` to the TEI Docker container, derived from config parameters
`TEI_MAX_BATCH_TOKENS` and `TEI_TOKENIZATION_WORKERS`.

### 2.5 DRY Refactoring

11 DRY audit findings were identified, 9 fixed:
- 4 manifest entry construction sites -> `_make_manifest_entry()`
- 3 sparse dict conversion sites -> `_sparse_dicts_to_vectors()`
- 2 point building sites -> `_build_qdrant_points()`
- 2 upsert+record sites -> `_upsert_and_record()`
- 2 branch resolver construction sites -> `build_branch_resolver()`
- 2 health check functions in docker_utils.py -> `_wait_for_health_endpoint()`

2 findings were skipped (abstraction cost exceeded benefit):
- DRY #4: per-file vs pool embedding orchestration (structurally different loops)
- DRY #8: two-pass callback binding (one-liner, abstracting adds indirection)

---

## 3. Benchmark Results

### 3.1 Test Environment

- **Hardware:** GeForce RTX 4060 (8 GB VRAM), 32 GB system RAM
- **Embedding backend:** TEI GPU (Jina v2 base code, float16)
- **Corpus:** Informica 2.0 production codebase (12,400+ files, 136,500+ vectors)
- **Config:** `config_informica_tei_jinaai` (baseline) vs `config_informica_tei_jinaai_pooltest` (pooling)
- **Pool settings:** `EMBED_POOL_SIZE=512`, `EMBED_POOL_MAX_FILES=50`

### 3.2 Timing Comparison (main branch only)

| Metric | Baseline (no pooling) | With pooling | Change |
|--------|----------------------|--------------|--------|
| **Total time** | 1,576.11s (26.3 min) | 1,224.40s (20.4 min) | **-351.7s (-22.3%)** |
| **Dense embedding** | 1,155.75s | 906.56s | **-249.2s (-21.6%)** |
| Upsert | 271.26s | 271.48s | unchanged |
| Sparse embedding | 15.99s | 14.12s | -1.87s |

### 3.3 GPU Utilization

| Metric | Baseline | With pooling | Change |
|--------|----------|--------------|--------|
| **Avg GPU util** | 28.3% | **38.5%** | **+10.2pp (+36%)** |
| **Median GPU util** | 23% | **39%** | **+16pp (+70%)** |
| Samples <20% util | 45.3% | 35.4% | -9.9pp |
| Samples >=50% util | 16.8% | 38.2% | +21.4pp (2.3x more time at high utilization) |
| Peak VRAM | 2,440 MiB | 2,994 MiB | +554 MiB (well within 8 GB budget) |

### 3.4 TEI Container Gap Analysis

From the TEI container logs (18,922 embedding requests):
- **Avg gap between requests:** 96.6ms
- **P50 gap:** 37.8ms
- **352 gaps >1s** — correspond to pool flush boundaries (upsert between flushes)
- GPU starvation pattern reduced but not eliminated (upsert gaps remain — potential Phase 2 target)

### 3.5 Index Quality

| Metric | Baseline | With pooling |
|--------|----------|--------------|
| **Vector count** | 136,522 | 136,530 (+8, 0.006%) |
| **Validation score** | 139/156 (89.1%) | 139/156 (89.1%) |
| **Test breakdown** | 64 PASS, 11 PARTIAL, 3 FAIL | 64 PASS, 11 PARTIAL, 3 FAIL |

Zero regression. The +8 vectors are from minor hash/mtime differences between runs
(expected with incremental refresh on a live codebase).

---

## 4. What Changed

### 4.1 New Files

| File | Lines | Tests |
|------|-------|-------|
| `src/shared/chunk_pool.py` | ~280 | 70 tests (`src_test/shared/test_chunk_pool.py`) |
| `src_test/qdrant/test_vector_store.py` | ~180 | 16 tests (BM25 CPU enforcement) |
| `src_test/shared/test_truncation_stats.py` | ~200 | 24 tests (TruncationStats.token_lengths) |

### 4.2 Modified Files

| File | Key changes |
|------|-------------|
| `src/index_rag.py` | Main loop refactored with ChunkPool + 6 DRY helpers. `_flush_pool()` orchestrates cross-file embedding. Chunk histogram collection integrated. |
| `src/shared/embedding.py` | `TruncationStats` gained `token_lengths: list[int]` field for histogram. |
| `src/qdrant/vector_store.py` | `get_sparse_encoder()` hard-wires BM25 to CPU. |
| `config.py` | Added `EMBED_POOL_SIZE`, `EMBED_POOL_MAX_FILES`, `TEI_MAX_BATCH_TOKENS`, `TEI_TOKENIZATION_WORKERS`. |
| `src/shared/docker_utils.py` | Merged `_wait_for_health` + `_wait_for_tei_health` into `_wait_for_health_endpoint()`. TEI container gets `--max-batch-tokens` and `--tokenization-workers`. |
| `src_test/shared/test_docker_utils.py` | 22 broken tests fixed for merged health check, 2 new tests added. |
| `.opencode/skills/tune-embed-params/SKILL.md` | Redesigned with histogram + pool + TEI param awareness. |
| `AGENTS.md` | Updated BM25 device section, added pooling architecture section. |

### 4.3 Test Summary

| Test file | Tests |
|-----------|-------|
| `test_chunk_pool.py` | 70 |
| `test_truncation_stats.py` | 24 |
| `test_vector_store.py` | 16 |
| `test_docker_utils.py` (fixed) | 22 fixed, 2 new |
| **Total new/fixed** | **134** |
| **Total project tests** | **1663** (all passing) |

---

## 5. Config Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_POOL_SIZE` | 512 | Max chunks to accumulate before flushing for cross-file batch embedding. Set to 0 to disable pooling. |
| `EMBED_POOL_MAX_FILES` | 50 | Max files in pool before flush. Bounds manifest update delay on crash. |
| `TEI_MAX_BATCH_TOKENS` | None | TEI `--max-batch-tokens` override. Auto-derived from `EMBED_BATCH_MAX_TOKENS` when None. |
| `TEI_TOKENIZATION_WORKERS` | None | TEI `--tokenization-workers` override. Auto-detected when None. |

---

## 6. Design Decisions

### 6.1 Sort-Then-Batch Over Discrete Buckets

Chunks are pooled, sorted by length descending, then fed to the existing dual-governor
batch algorithm (`_embed_batched()`). This produces naturally homogeneous batches without
the partial-bucket problem of discrete length buckets. See design.md section 3.2.

### 6.2 Per-File Upsert Within Pool Flush

Although chunks are embedded cross-file, upsert and manifest updates happen per-file
within the flush. This preserves manifest atomicity: on crash, the worst case is re-doing
one pool's worth of files (~50 files, ~30s of embedding). Qdrant upsert is idempotent.

### 6.3 Two-Pass Compatibility

Two-pass hybrid mode (`HYBRID_EMBED_SINGLE_PASS=False`) is preserved as a backward-compat
path. When two-pass is active, the pool is bypassed and embedding reverts to per-file
mode. The pool only activates for single-pass mode.

---

## 7. Remaining Work

| Item | Priority | Description |
|------|----------|-------------|
| **Production deployment** | High | Apply pooling to `config_informica_tei_jinaai`, refresh index, remove pooltest config/containers. |
| **Self-index update** | Medium | Rebuild self-index with pooling enabled. |
| **Parse-ahead (future)** | Low | Overlap file parsing with embedding to eliminate the ~1s CPU gap between flushes. See design.md section 6.4. Deferred — current performance is acceptable. |

---

## 8. Conclusion

Phase 1 cross-file chunk pooling achieved a **22.3% reduction in total indexing time**
(26.3 min -> 20.4 min) and a **36% improvement in average GPU utilization** (28.3% -> 38.5%)
on the production Informica codebase with TEI GPU. Zero quality regression (89.1% validation
score unchanged). The implementation adds 280 lines of new pooling code, 134 new/fixed tests,
and cleans up 9 DRY violations in the indexing pipeline.

The design.md predicted 20-40% speedup for TEI; the measured 22.3% falls within that range,
weighted toward the lower end because upsert I/O (unchanged at 271s) now dominates the
remaining gap. Phase 2 async TEI + upsert pipelining could push utilization above 50%.

---

## Phase 2: Double-Buffered Upsert

### 9. Problem Statement (Phase 2)

Phase 1 achieved cross-file pooling but the flush cycle was still synchronous:
embed → sparse → upsert → next pool. The hypothesis was that overlapping Qdrant upsert
I/O with the next pool's embedding would eliminate GPU idle time between flushes.

### 10. Solution Architecture (Phase 2)

**Double-buffered upsert via `ThreadPoolExecutor`:**

```
Phase 1 (synchronous):
  [embed pool 1] [upsert pool 1] [embed pool 2] [upsert pool 2] ...
                  ^^^^^ GPU idle                  ^^^^^ GPU idle

Phase 2 (double-buffered):
  [embed pool 1] [embed pool 2    ] [embed pool 3    ] ...
                 [upsert pool 1   ] [upsert pool 2   ]
                  ^^^^^ overlapped   ^^^^^ overlapped
```

Key components:
- `_upsert_executor`: `ThreadPoolExecutor(max_workers=1)` — single background thread
- `_pending_upsert`: `Optional[Future]` — at most one upsert in flight
- `_drain_pending_upsert()`: blocks until previous upsert completes, applies counter
  deltas (vectors_added, files_added, etc.) to main-thread state
- `_do_background_upsert()`: runs on background thread, upserts per-file, returns
  counter deltas. All log messages prefixed with `[upsert-worker]`
- `try/finally` block for graceful executor shutdown on both normal and error paths

Additional change: `EMBED_POOL_MAX_FILES` raised from 50 → 150 to eliminate GPU stalls
in the late SQL region where many tiny files triggered frequent undersized flushes.

### 11. Benchmark Results (Phase 2)

#### 11.1 Test Environment

Same as Phase 1 (RTX 4060, TEI GPU, Informica production corpus). The Phase 2 run was
intentionally interrupted after ~2 minutes / 24 flush cycles — enough to measure the
per-cycle behavior and confirm the double-buffer is working.

#### 11.2 GPU Utilization (2-minute sample)

| Metric | Phase 1 (20.4 min, complete) | Phase 2 (2 min, partial) |
|--------|------------------------------|--------------------------|
| Avg GPU util | 38.5% | 44.2% (+5.7pp) |
| Idle samples (0-5%) | 33.9% | 5.7% (-28pp) |
| Sawtooth drops/min | 3.6 | 1.0 (-72%) |

**Caveat:** The 2-minute sample is too small for statistical confidence. The idle
reduction may partly be due to startup effects (early flushes process large .pas files
that fill pools well).

#### 11.3 Key Finding: Upsert Was Never the Bottleneck

The benchmark conclusively proved that the **double-buffer is architecturally correct
but solves a non-problem:**

1. **Double-buffer IS working** — `[upsert-worker]` log messages interleave with
   "Processing file" messages at the same timestamps, confirming concurrent execution.
2. **Negligible savings** — upsert averages 0.83s per pool, embedding averages ~3s.
   Net savings: ~0.3s per flush cycle. Over a full run (~70 cycles): ~20s = 1.6% of
   20.4 min total.
3. **Sawtooth persists** — GPU drops to 0-5% between flush cycles. The cause is the
   ~1s CPU gap (file parsing, chunking, pool filling) between embedding passes, not
   upsert blocking.

**Flush cycle timeline:**
```
[embed ~3s GPU] → [drain ~0s] → [BM25 ~0.04s] → [build ~0s] → [submit upsert]
                                                                  ↓ (background)
[parse/chunk ~1s CPU] → [next embed ~3s GPU]
 ↑ THIS is the gap
```

### 12. What Changed (Phase 2)

#### 12.1 Modified Files

| File | Key changes |
|------|-------------|
| `src/index_rag.py` | `_flush_pool()` refactored to 5-step double-buffer. Added `_do_background_upsert()`, `_drain_pending_upsert()`, `_upsert_executor`, `_pending_upsert`. `try/finally` for executor shutdown. |
| `config.py` | `EMBED_POOL_MAX_FILES` default 50 → 150, comment block with Phase 2 rationale. |

#### 12.2 New Files

| File | Lines | Tests |
|------|-------|-------|
| `src_test/test_double_buffer.py` | ~400 | 35 tests (counter logic, batching, error handling, manifest updates, log prefixes, thread safety, overlap verification) |

#### 12.3 Test Summary

| Scope | Tests |
|-------|-------|
| New (Phase 2) | 35 |
| Total project | 1698 (all passing) |

### 13. Decision

**Keep Phase 2 as-is.** Rationale:
- The code is correct, tested (35 unit tests), and low-risk.
- Adds ~50 lines of thread code — manageable complexity.
- The ~20s savings is negligible but not harmful.
- The infrastructure (`_do_background_upsert`, `_drain_pending_upsert`) supports future
  optimizations (e.g., parse-ahead) without additional refactoring.
- Reverting would lose the infrastructure for no meaningful benefit.

**The sawtooth problem is deferred.** The proposed parse-ahead solution (overlap file
parsing with embedding on a background thread) would save ~70s (5.7%), but the current
20.4 min is acceptable. See design.md section 6.4.
