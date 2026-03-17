---
name: tune-embed-params
description: Fine-tune embedding indexing parameters (batch size, max tokens, seq length) for a given model and GPU. Run on test_sources, monitor VRAM via GPU stats CSV, and find the optimal settings before committing to a full corpus build.
---

# Tune Embedding Parameters Skill

This skill guides you through discovering safe and optimal values for:

- `EMBED_MAX_SEQ_LENGTH` — max tokens per chunk (controls truncation vs VRAM)
- `DENSE_EMBED_BATCH_SIZE` — max chunks per dense embedding batch
- `EMBED_BATCH_MAX_TOKENS` — max total approximate tokens per batch (the effective VRAM governor)

The goal: **maximize GPU utilization** without OOM, and **minimize truncation** without
spilling into shared VRAM (which is ~10x slower than dedicated VRAM).

---

## Step 0: Discover Your Hardware

Before tuning anything, characterize the GPU you are running on. The safe parameter
ranges depend entirely on dedicated VRAM, memory bandwidth, and whether Flash Attention
is available.

### Command

```bash
nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv,noheader
```

### Interpreting the output

| Column | Meaning | How it affects tuning |
|--------|---------|----------------------|
| `name` | GPU model | Identifies architecture family |
| `memory.total` | Dedicated VRAM in MiB | Primary constraint for seq_len and batch_size |
| `driver_version` | NVIDIA driver | Must be ≥ 520 for CUDA 12.x support |
| `compute_cap` | CUDA compute capability | 8.x = Ampere (RTX 30xx), 8.9 = Ada Lovelace (RTX 40xx) |

### Hardware baselines (measured on this project)

| GPU | Dedicated VRAM | Architecture | Flash Attn | Safe seq_len | Notes |
|-----|---------------|--------------|------------|--------------|-------|
| RTX 4060 Laptop | 8,188 MiB | Ada Lovelace (8.9) | Yes (torch) | 4096 (Jina/ALiBi) | This machine |
| RTX 4060 / 4070 Desktop | 8,192 MiB | Ada Lovelace | Yes | 4096 | Same VRAM, lower thermal throttle |
| RTX 3060 Laptop | 6,144 MiB | Ampere (8.6) | Yes | 2048 (ALiBi), 4096 (RoPE) | Tighter budget |
| RTX 3080 / 4080 | 10–16 GB | Ampere/Ada | Yes | 4096+ | More headroom |
| GTX 1080 Ti / 16xx | 11 GB | Pascal (6.1) | No | 2048 | No Flash Attn, O(N^2) |
| Apple M-series (MPS) | Shared RAM | — | No | 2048 | mps device, no nvidia-smi |
| CPU only | N/A | — | No | 512–1024 | Very slow; reduce batch aggressively |

**VRAM ceiling formula** (dedicated + 80% of shared):
```
safe_ceiling_mib = dedicated_total_mib + 0.8 * shared_total_mib
```
On RTX 4060 Laptop: 8,188 + 0.8 × 16,384 ≈ **21,295 MiB**. Shared VRAM is ~10x slower
than dedicated, so treat dedicated as the primary budget.

### Check shared VRAM

```bash
nvidia-smi --query-gpu=memory.total,memory.free --format=csv,noheader
```

Also check system RAM (shared VRAM is backed by system RAM):

```bash
# Windows
wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value

# Linux
free -m
```

### Identify the attention architecture

This matters because it determines whether seq_len causes O(N^2) VRAM growth:

| Model | Attention | VRAM scaling | Windows Flash Attn |
|-------|-----------|-------------|-------------------|
| `jinaai/jina-embeddings-v2-base-code` | ALiBi | **O(N^2)** | N/A (no flash-attn) |
| `nomic-ai/CodeRankEmbed` | RoPE + Flash Attn | O(N) on Linux, **O(N^2) on Windows** | No (`flash-attn` is Linux-only) |
| `Alibaba-NLP/gte-modernbert-base` | RoPE + ModernBERT Flash | O(N) everywhere | Yes (via transformers, no pip pkg) |
| `BAAI/bge-m3` | RoPE | O(N) | Yes |

**Rule:** If the model uses O(N^2) attention on your platform, halving seq_len reduces
the attention matrix VRAM by 4x. This is why Jina is capped at 4096 instead of 8192.

---

## Step 1: Set Up a Test Config

Always tune on `test_sources` (38 files, ~8,000 vectors, ~8 min at seq_len=4096).
**Never tune on the full corpus** — a bad parameter causes OOM after hours.

Create or edit `project-configs/test-sources/config.py` (or a model-specific variant):

```python
# project-configs/test-sources-mymodel/config.py

# ── Model under test ─────────────────────────────────────────────────
MODEL_NAME = "jinaai/jina-embeddings-v2-base-code"  # change to your model
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}      # always float16 for GPU
TRUST_REMOTE_CODE = True                             # mandatory for Jina

# ── Parameters to tune ───────────────────────────────────────────────
EMBED_MAX_SEQ_LENGTH    = 4096   # <-- TUNE THIS
DENSE_EMBED_BATCH_SIZE  = 32     # <-- TUNE THIS
EMBED_BATCH_MAX_TOKENS  = 16000  # <-- TUNE THIS

# ── Fixed settings ────────────────────────────────────────────────────
SPARSE_EMBED_BATCH_SIZE = 32
SPARSE_MODEL_NAME = "Qdrant/bm25"
HYBRID_EMBED_SINGLE_PASS = False   # two-pass: dense → SQLite → sparse
INDEX_EMBED_DEVICE = "cuda"
MCP_EMBED_DEVICE = "cpu"

# ── Collection (isolated, won't touch production) ─────────────────────
COLLECTION_NAME = "test_sources_tune"
MODEL_PATH = "index_tune_test_sources"
QDRANT_MODE = "local"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6336          # pick an unused port
QDRANT_DOCKER_CONTAINER = "qdrant-test_sources_tune"

# ── Source ────────────────────────────────────────────────────────────
SOURCE_DIRS = [{"path": "test_sources", "extensions": [
    ".pas", ".dfm", ".dpr", ".dproj", ".sql", ".fr3", ".py"
]}]
```

---

## Step 2: Run the Calibration Build

```bash
.venv/Scripts/python src/index_rag.py --config test-sources-mymodel \
    --clear --yes --log-to-file --collect-perf-stats
```

Flags:
- `--clear` — ensures a fresh build (no incremental shortcuts)
- `--yes` — skips all prompts
- `--log-to-file` — writes a timestamped `.log` in the index directory
- `--collect-perf-stats` — writes a `gpu_stats_<timestamp>.csv` with per-second VRAM/utilization

Expected runtime on RTX 4060 Laptop:
- seq_len=1024: ~3 min
- seq_len=2048: ~5 min
- seq_len=3072: ~8 min
- seq_len=4096 (Jina/ALiBi): ~8 min
- seq_len=4096 (RoPE models): ~6 min

---

## Step 3: Analyze the GPU Stats CSV

The stats file is at `project-configs/test-sources-mymodel/qdrant/index_tune_test_sources/gpu_stats_<ts>.csv`.

### CSV columns

```
timestamp, gpu_util_%, mem_util_%, dedicated_used_mib, dedicated_total_mib, shared_used_mib, temp_c
```

### Key metrics to extract

```bash
# Peak dedicated VRAM
awk -F, 'NR>1 {print $4}' gpu_stats.csv | sort -n | tail -1

# Average GPU utilization (%)
awk -F, 'NR>1 {sum+=$2; n++} END {print sum/n}' gpu_stats.csv

# Time spent at 0% GPU (idle fraction)
awk -F, 'NR>1 {if($2==0) idle++; total++} END {print idle/total*100 "% idle"}' gpu_stats.csv

# Peak shared VRAM used
awk -F, 'NR>1 {print $6}' gpu_stats.csv | sort -n | tail -1
```

### Targets

| Metric | Target | Red flag |
|--------|--------|----------|
| Peak dedicated VRAM | < 95% of total | > 98% → risk of spill or OOM |
| Average GPU utilization | > 70% | < 40% → batches too small or CPU bottleneck |
| Idle fraction (0% util) | < 10% | > 25% → tokenization or I/O bottleneck |
| Peak shared VRAM | < 500 MiB | > 2,000 MiB → already spilling (check seq_len) |

---

## Step 4: Check the Indexing Log

```bash
tail -50 project-configs/test-sources-mymodel/qdrant/index_tune_test_sources/index_rag_<ts>.log
```

Look for:
- **Truncation warnings**: `[WARN] Truncated chunk ... tokens > EMBED_MAX_SEQ_LENGTH`
- **OOM errors**: `CUDA out of memory` → reduce seq_len or batch_size
- **Zero-vector warnings**: `Skipping zero-vector node` → model produces degenerate embeddings for some inputs

### Truncation table

```
grep -c "Truncated chunk" index_rag_<ts>.log
grep "total chunks" index_rag_<ts>.log   # look for the summary line
```

Acceptable truncation: < 0.5% of all chunks. The full Informica corpus has ~135,000
vectors; 0.5% = 675 chunks. Above 1% is worth investigating (check if large chunks
can be split differently in the reader).

---

## Step 5: Parameter Decision Tree

Work through this in order. Stop at the first branch that applies.

### 5.1 Did you get OOM?

**Yes** → The seq_len is too high for this model on this GPU.

- If the model uses **O(N^2) attention** (Jina ALiBi, CodeRankEmbed on Windows):
  - Halve `EMBED_MAX_SEQ_LENGTH` (e.g. 4096 → 2048)
  - You cannot fix O(N^2) OOM by reducing `EMBED_BATCH_MAX_TOKENS` alone — a single
    large chunk can OOM regardless of batch token budget
  - Verify: `4096^2 * num_heads * 2 bytes / 1024^3` = GiB per sample (Jina: ~0.75 GiB; CodeRankEmbed: ~7.5 GiB)
- If the model uses **O(N) attention** (RoPE, Flash Attention):
  - First try halving `DENSE_EMBED_BATCH_SIZE` or `EMBED_BATCH_MAX_TOKENS`
  - If still OOM, reduce `EMBED_MAX_SEQ_LENGTH` by 25%

**No** → Continue to 5.2.

### 5.2 Is peak dedicated VRAM > 95% of total?

**Yes** → You are on the edge of spilling. Two options:

- **Option A (preferred)**: Reduce `EMBED_BATCH_MAX_TOKENS` by 25% (e.g. 16000 → 12000).
  This keeps seq_len the same (no extra truncation) but lowers per-batch VRAM.
- **Option B**: Reduce `DENSE_EMBED_BATCH_SIZE` by 25%.

Re-run calibration. If still > 95%, apply both options.

**No** → Continue to 5.3.

### 5.3 Is truncation > 1%?

**Yes** → Increase `EMBED_MAX_SEQ_LENGTH`.

- For O(N^2) models: increase by 512 at a time and re-calibrate. Each step is a
  separate build (~8 min on test_sources). Stop when VRAM approaches 90%.
- For O(N) models: you can be more aggressive — try doubling seq_len, then halve
  if VRAM becomes a concern.

The practical max for Jina on 8 GB is **4096** (ALiBi bias = ~384 MiB).
The theoretical max for RoPE models on 8 GB is **8192** (Flash Attn O(N)).

**No** → Continue to 5.4.

### 5.4 Is average GPU utilization < 40%?

**Yes** → The GPU is idle, likely due to CPU tokenization bottleneck or very small batches.

- Increase `DENSE_EMBED_BATCH_SIZE` (e.g. 32 → 64), recheck VRAM.
- Increase `EMBED_BATCH_MAX_TOKENS` (e.g. 16000 → 24000).
- If CPU is the bottleneck: nothing helps except a faster CPU or pre-tokenization caching.

**No** → Parameters are good. Go to Step 6.

---

## Step 6: Encode the Result in Config

Once calibration passes all targets, update the production config:

```python
# These are the tuned values — document WHY they are set here
EMBED_MAX_SEQ_LENGTH   = 4096   # Jina ALiBi: 4096^2 * 12 heads * 2B = 384 MiB bias tensor
                                 # Peak dedicated VRAM: 7,809 MiB / 8,188 MiB (95.4%)
DENSE_EMBED_BATCH_SIZE = 32     # 32 chunks × 4096 tokens each = 131k tokens/batch max
EMBED_BATCH_MAX_TOKENS = 16000  # Effective governor: limits actual batch to ~4k tokens avg
```

Add a comment with the calibration measurements so future sessions know the margin:

```python
# Calibration (2026-03-17, RTX 4060 Laptop 8GB, test_sources 38 files):
#   Peak VRAM:    7,809 MiB dedicated / 7,171 MiB shared
#   Avg GPU util: ~100% (GPU-bound throughout)
#   Truncation:   0/8,101 chunks (0%)
```

---

## Step 7: Validate on Full Corpus

If the model is a production challenger (not just a calibration exercise):

```bash
# Full build with tuned parameters
.venv/Scripts/python src/index_rag.py --config config_informica_mymodel \
    --clear --yes --log-to-file --collect-perf-stats

# Then validate quality
.venv/Scripts/python src/validate_rag.py --config config_informica_mymodel
```

Monitor the full build log for OOM. If OOM occurs mid-run, the test_sources
calibration was insufficient (some files in the full corpus have larger chunks).
Reduce `EMBED_BATCH_MAX_TOKENS` by 20% and rebuild.

---

## Reference: Measured Results (This Project, RTX 4060 Laptop 8GB)

### jinaai/jina-embeddings-v2-base-code (production model)

| seq_len | Batch tokens | Peak VRAM (ded.) | Truncation | Avg GPU util |
|---------|-------------|-----------------|-----------|-------------|
| 2048 | 16000 | ~4,500 MiB | ~4% | ~90% |
| **4096** | **16000** | **~7,809 MiB** | **0%** | **~100%** | ← production
| 8192 | 16000 | OOM (ALiBi ~1.5 GiB bias tensor) | — | — |

**Conclusion**: seq_len=4096 is the maximum for Jina on 8 GB. Uses 95.4% of
dedicated VRAM. No headroom to increase further.

### nomic-ai/CodeRankEmbed (tested in iteration-009)

| seq_len | Batch tokens | Peak VRAM (ded.) | Peak VRAM (shared) | Truncation | Notes |
|---------|-------------|-----------------|-------------------|-----------|-------|
| 1024 | 16000 | 4,381 MiB | 214 MiB | 4.8% | Too much truncation |
| 2048 | 16000 | ~3,000 MiB | ~500 MiB | 1.0% | Safe ceiling on Windows |
| 3072 | 16000 | 7,941 MiB | 7,116 MiB | 0.4% | Tight; full corpus was killed |
| 4096 | 16000 | OOM on full corpus | — | — | Single chunk = 7.5 GiB attention (O(N^2)) |

**Conclusion**: CodeRankEmbed on Windows is O(N^2) (no `flash-attn`). seq_len=2048
is the practical ceiling for a full corpus build on 8 GB. seq_len=3072 works on
test_sources but OOMs on large files in the full Informica corpus.

**Windows-specific note**: `flash-attn` (the pip package) is Linux-only. On Windows,
`nomic-bert` falls back to standard `torch.matmul(Q, K^T)` attention which is O(N^2).
This is a hard platform limitation — not fixable by parameter tuning.

### Alibaba-NLP/gte-modernbert-base (tested in iteration-009)

| seq_len | Batch tokens | Peak VRAM (ded.) | Truncation | Notes |
|---------|-------------|-----------------|-----------|-------|
| 1024 | 16000 | 1,376 MiB | 4.9% | Too much truncation |
| 8192 | 16000 | 3,595 MiB | 0.0% | test_sources |
| **8192** | **16000** | **6,275 MiB** | **0.01%** | Full Informica 135k vectors |

**Conclusion**: ModernBERT's Flash Attention works on Windows via `transformers`
(no pip package needed). O(N) scaling confirmed. 8192 tokens fully usable on 8 GB GPU.

---

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|------------|-----|
| Tuning on full corpus first | Hours wasted before OOM | Always calibrate on test_sources |
| Not using `--collect-perf-stats` | No VRAM data → guessing | Always add this flag |
| Confusing O(N^2) vs O(N) models | Unexpected OOM or wrong ceiling | Check model attention architecture first |
| Assuming `EMBED_BATCH_MAX_TOKENS` fixes O(N^2) OOM | It doesn't — single-chunk OOM | Only seq_len can fix attention matrix OOM |
| Forgetting `--clear` on calibration builds | Incremental skips most files → no VRAM data | Always use `--clear` for calibration |
| Not checking shared VRAM | 10x slowdown goes unnoticed | Check `shared_used_mib` column in CSV |
| Upgrading transformers without retesting | Jina breaks at 5.x (loads as BertModel) | Pin transformers < 5.0 for Jina |

---

## Quick Reference Card

```
Hardware check:
  nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader

Attention VRAM cost per sample (O(N^2) models only):
  GiB = seq_len^2 * num_heads * 2 / 1024^3
  Jina (12 heads): 4096^2 * 12 * 2 / 1024^3 = 0.375 GiB   ← fits in 8 GB
  Jina (12 heads): 8192^2 * 12 * 2 / 1024^3 = 1.50 GiB    ← OOM risk
  CodeRankEmbed:   4096^2 * 12 * 2 / 1024^3 = 7.5 GiB     ← OOM on 8 GB

Calibration command:
  .venv/Scripts/python src/index_rag.py --config test-sources-mymodel \
      --clear --yes --log-to-file --collect-perf-stats

Peak VRAM from CSV:
  awk -F, 'NR>1 {print $4}' gpu_stats_*.csv | sort -n | tail -1

Truncation count from log:
  grep -c "Truncated chunk" index_rag_*.log

Decision: if peak VRAM < 90% of dedicated AND truncation < 0.5% → done
```
