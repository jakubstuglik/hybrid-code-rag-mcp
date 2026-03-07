1. Verify requirements, very specific pytorch packages required for CUDA and ROC to run. Tidy up.
2. Smaller models, what is the quality difference? Save generated vector db on bigger model first!!!
3. Different parameters on models to fit in VRAM and not used shared GPU memory etc.
# **Ok, optimization for batch sizes, chunk grouping, clearing cache is done. WHAT IS TO DO: Optimize code for maximum GPU saturation! This probably needs big change: worker(s) for preparing batches, feeding it to some queue and workers for feeding this to GPU to maximize saturation and feeding results for some consumer to persist**

## GPU Saturation Analysis (2026-03-07, 24,979 nodes, RTX 8GB)

Measured with nvidia-smi 2s sampling during full index run (optimized params):

### Dense (BGE-M3, batch=128, PyTorch/HuggingFace)
- Avg **70%** GPU util, 0% idle, 36% saturated (>=90%)
- VRAM: avg 4011 MiB, peak 7450 MiB / 8188 MiB
- Reasonably good. Dips are CPU tokenization between batches.

### Sparse (Splade_PP_en_v1, batch=64, ONNX Runtime)
- Avg **22%** GPU util, **51% idle**, 1% saturated (>=90%)
- VRAM: avg 4302 MiB, peak 5763 MiB / 8188 MiB
- Very poor. GPU idle more than half the time.

### Root cause
Splade via ONNX Runtime is **CPU-bound on batch preparation**. Between GPU inference
calls, the CPU tokenizes the next batch while the GPU waits. Batch=64 is already at the
VRAM cliff (batch=96 hits 8GB and thrashes), so we can't increase batch size to amortize.

### Proposed fix: pipelined double-buffered batching
While GPU processes batch N, CPU prepares batch N+1 in a background thread.

**Challenges:**
- The sparse encoder (`sparse_fn` from fastembed/qdrant-client) is a black-box callable —
  we don't control tokenization and inference steps separately
- Options to investigate:
  1. Patch into fastembed internals to separate tokenize from infer
  2. Use `concurrent.futures.ThreadPoolExecutor` to overlap entire `sparse_fn()` calls
     (but ONNX RT may hold the GIL during inference — needs testing)
  3. Use `multiprocessing` for CPU-side tokenization (avoids GIL, higher complexity)
- Potential speedup: ~2x on sparse phase (from 205s to ~100s), saving ~100s total

### Same approach may help dense too
Dense is at 70% avg — the same pipeline pattern could push it closer to 90%+.
PyTorch releases the GIL during GPU kernels, so threading should work better here.

4. Persistent MCP server setup - TESTING
5. Chunking of fr3 - why always two chunks? Check other XMLs too. Should be way more
6. Chunking SQLs - is there a way to chunk them more? how are they chunked now? View chunks for some files and check

# Rebuild README.md - this is now general RAG indexing and MCP project

7. Include somehow indexed project libraries in specific versions and docs for them from web and/or source codes
8. Indexing given branches on git repo using .git contents, not bu imdexing full contents bu checking out branch
9. **TESTS**
