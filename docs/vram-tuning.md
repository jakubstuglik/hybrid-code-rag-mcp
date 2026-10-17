# Tuning GPU memory (VRAM)

This section explains how each indexing parameter affects GPU memory, so you can size a configuration for your own card. The defaults in `config.py` fill almost all of a 12 GB GPU with the PyTorch backend (for example, a ~300M-parameter model in bfloat16 can reserve about 11.5 of 12 GB, as shown by `nvidia-smi`). With the same settings, an 8 GB card will usually run out of memory. An example configuration for 8 GB comes at the end of this section, but treat it as a starting point and measure on your own data.

## How memory is used

**PyTorch backend (`USE_TEI = False`).** All dense-embedding memory lives in the indexer process:

- **Model weights.** Parameters x bytes per value. This is a fixed cost; only the dtype or a different model changes it.
- **Activations of one forward pass.** This is the variable part and the usual cause of OOM. It grows linearly with *chunks in the pass x padded sequence length*. The attention part grows with the square of the sequence length, unless the model uses a memory-efficient attention kernel. It is freed after the pass.
- **PyTorch caching allocator.** Freed blocks stay *reserved* for reuse. `nvidia-smi` therefore shows the high-water mark plus fragmentation, not what the run currently has *allocated*. To measure the real peak, use `torch.cuda.max_memory_allocated()`.
- **Other processes on the same GPU.** The display, a browser, or a TEI container all take their share.

**How one forward pass is formed (PyTorch):**

1. Chunks are pooled across files and sorted longest-first.
2. The indexer cuts a *batch* that stops at `DENSE_EMBED_BATCH_SIZE` chunks or `EMBED_BATCH_MAX_TOKENS` approximate tokens (chars / 4), whichever comes first. A single chunk larger than the budget still forms its own batch.
3. llama_index `HuggingFaceEmbedding` splits the batch into forward passes of `embed_batch_size` chunks. That is the llama_index default of **10**; this project does not override it.
4. Each pass is padded to its longest chunk, capped at `EMBED_MAX_SEQ_LENGTH`.
5. Only one pass runs on the GPU at a time, because the PyTorch dense stage has a single worker.

```
chunks per pass  ~ min(10, DENSE_EMBED_BATCH_SIZE, chunks that fit in EMBED_BATCH_MAX_TOKENS)
padded length    = min(longest chunk in the pass, EMBED_MAX_SEQ_LENGTH)
peak activations ~ chunks per pass x padded length  (attention part: x padded length again)
peak VRAM        ~ weights + peak activations + allocator reserve/fragmentation + other processes
```

Because chunks are sorted longest-first, the first passes are the ones with the longest padding. An OOM therefore usually shows up early in a run, or on the first pool that contains very long chunks.

**TEI backend (`USE_TEI = True`).** The dense model runs inside the TEI Docker container. Its VRAM is roughly the weights plus buffers for one batch of up to `--max-batch-tokens` tokens. The indexer process uses no VRAM for dense embedding.

## Parameters, one by one

### `EMBED_MAX_SEQ_LENGTH` (default `4096`). PyTorch and OpenVINO
- **Controls:** the maximum number of tokens the model sees per chunk. The tokenizer truncates anything longer.
- **Mechanism:** sets the upper bound of the padded length of each pass. Activations scale linearly with it, and the attention part scales quadratically (N^2), so at long lengths this dominates.
- **Direction:** lower means less VRAM. Halving it at least halves the activation peak of the longest passes.
- **Trade-offs:**
  - The dense vector ignores text beyond the cap. BM25 still indexes the full chunk.
  - Vectors of truncated chunks change, so rebuild with `--clear` and re-run RAG validation.
  - Slightly faster.
- **Note:** chunks are limited by characters, not tokens, so some chunks exceed 4096 tokens. The cap is what bounds them.

### `EMBED_BATCH_MAX_TOKENS` (default `16000`). PyTorch, and TEI via `TEI_MAX_BATCH_TOKENS`
- **Controls:** the approximate token budget of one batch, counted as characters / 4.
- **Mechanism:** limits how many long chunks share a batch, and therefore a pass. With 4096-token chunks, a 16000 budget allows about 3-4 per batch. With short chunks the 10-chunk pass limit is reached first, and this budget has no effect.
- **Direction:** lower means less VRAM for passes of long chunks. Roughly linear.
- **Trade-offs:**
  - The vectors don't change; there is only floating-point noise, and no `--clear` is needed.
  - Smaller passes give lower GPU utilisation, so it is slower.
  - chars / 4 is an estimate. Code often has more real tokens than that, so the true size of a pass can exceed the budget. Keep headroom.
- **Measured scale (example):** with a ~300M-parameter model in bfloat16, peak *allocated* VRAM grew roughly linearly with this budget: about 2 GB at 8000, about 4.5 GB at 16000 and about 7 GB at 32000, and 64000 ran out of memory on 12 GB. Above 16000 the speed gain was only a few percent. For most cards 16000 is the sweet spot; on 8 GB, 32000 leaves no headroom.

### `DENSE_EMBED_BATCH_SIZE` (default `32`). PyTorch
- **Controls:** the maximum number of chunks per batch.
- **Mechanism:** only lowers VRAM when set **below 10**, because llama_index already limits each pass to 10 chunks. Between 10 and 32 it changes how often the token budget and the VRAM check are evaluated, not the size of a pass.
- **Direction:** lower means less VRAM only below 10. It mainly matters for many medium-length chunks.
- **Trade-offs:** slower at small values. Vectors are unchanged and no `--clear` is needed.
- **TEI:** not used on the TEI concurrent path, because TEI forms its own batches.

### `embed_batch_size` (llama_index, fixed at `10`). PyTorch
- **Controls:** chunks per `SentenceTransformer.encode` pass.
- **Mechanism:** the hard upper limit on chunks per pass.
- **Configuration:** not configurable in this project today. It is listed because it explains why `DENSE_EMBED_BATCH_SIZE` above 10 does not increase VRAM.
- **Throughput:** for corpora with many short chunks, 10 is a bottleneck. In an example measurement, raising it to 32 (with `DENSE_EMBED_BATCH_SIZE` 64) gave about 1.5x more chunks per second on short chunks with no increase in peak VRAM, because `EMBED_BATCH_MAX_TOKENS` still capped passes of long chunks. 64 gave no further gain.
- **Raising it (or calling `encode()` on a whole batch):** increases VRAM linearly unless the token budget caps the batch. During development, doing this together with two concurrent dense pools caused OOM on a 12 GB GPU.

### `EMBED_MODEL_KWARGS["torch_dtype"]` (default `"float16"`). PyTorch
- **Controls:** the precision of weights and activations.
- **Mechanism:** float16 and bfloat16 use 2 bytes per value instead of 4 for float32. That halves the weights and the activations.
- **Direction:** float16/bfloat16 use about half the VRAM of float32.
- **Trade-offs:**
  - Use bfloat16 for models trained in bf16 (for example Gemma-based embedders). It needs an Ampere or newer GPU.
  - Vectors differ between dtypes, so rebuild with `--clear`.
  - float32 is meant for CPU only.

### `EMBED_DYNAMIC_VRAM_CAP` (default `False`), with `EMBED_VRAM_SAFETY_MARGIN`, `EMBED_VRAM_DEDICATED_MB` and `EMBED_VRAM_SHARED_MB`. PyTorch on CUDA
- **Controls:** computes the sequence cap from the detected VRAM, using the quadratic model in `shared/vram_cap.py` (which assumes the Jina ALiBi attention).
- **Mechanism:** the result is clamped to `[EMBED_MAX_SEQ_LENGTH, model max]`, so it can only **raise** the cap.
- **Direction:** enabling it can increase VRAM, never decrease it. Leave it off on small cards.

### `INDEX_EMBED_DEVICE` (default `"auto"`) and `MCP_EMBED_DEVICE` (default `"cpu"`)
- **Controls:** which device holds the model during indexing and during MCP queries.
  - `"auto"` picks the GPU with the most free VRAM.
  - `"0"`, `"1"` and so on select a specific GPU.
  - `"cpu"` uses no VRAM.
- **Trade-offs:**
  - Prefer a GPU that isn't driving the display and isn't shared with TEI.
  - CPU always fits but is much slower.
  - Keep `MCP_EMBED_DEVICE = "cpu"` so a long-running server holds no VRAM.

### `TEI_MAX_BATCH_TOKENS` (default `None`, which means use `EMBED_BATCH_MAX_TOKENS`). TEI
- **Controls:** TEI's `--max-batch-tokens`, the largest GPU batch TEI will form.
- **Mechanism:** sets the size of TEI's activation buffers. Roughly linear.
- **Direction:** lower means less VRAM in the container.
- **Trade-offs:**
  - Slower. Vectors are unchanged.
  - It is applied when the container is **created**, so remove the container to apply a new value.

### `TEI_DTYPE` (default `"float16"`) and `TEI_GPU` (default `"auto"`). TEI
- **Controls:** precision and GPU choice of the TEI container, with the same reasoning as `torch_dtype` and the device settings above.
- **Advice:** keep float16 on a GPU, and don't share the GPU with a PyTorch indexer.

### `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (environment variable, unset by default). PyTorch
- **Controls:** a standard PyTorch allocator mode that reduces fragmentation.
- **Mechanism:** less memory sits reserved but unusable, so a pass that would fail because of fragmentation can fit.
- **Effect:** does not lower allocated memory. Measure it on your own setup.

### Parameters with no VRAM effect (host RAM only)
- **`EMBED_PIPELINE_DEPTH`** (default `0`, pipeline off; opt in with e.g. `6` for TEI on GPU)
  - PyTorch/OpenVINO: there is exactly one dense worker, so depth only sets how many pools wait in host RAM.
  - TEI: extra pools only add queued HTTP requests, and TEI still batches within `--max-batch-tokens`.
  - Higher values use more host RAM; `0` uses the legacy serial path. On a GPU, enabling it removes idle gaps between pools.
- **`EMBED_PARSE_QUEUE_SIZE`** (default `400`): parsed files waiting in a Python queue. Applies with any depth, including `0`.
- **`EMBED_POOL_SIZE`** and **`EMBED_POOL_MAX_FILES`**: chunks collected in RAM before batching. Larger pools sort better and mean less padding per pass, which helps indirectly.
- **`QDRANT_UPSERT_BATCH_SIZE`**: points per upsert call.
- **`TEI_CONCURRENT_REQUESTS`**: client-side HTTP concurrency.
- **`SPARSE_EMBED_BATCH_SIZE`** and **`HYBRID_EMBED_SINGLE_PASS`**: the default sparse model `Qdrant/bm25` runs on CPU.

## Summary table

| Parameter | Backend | Default | VRAM scaling | Lower = less VRAM? | Needs `--clear`? |
|-----------|---------|---------|--------------|--------------------|------------------|
| `EMBED_MAX_SEQ_LENGTH` | PyTorch | `4096` | linear to quadratic per pass | yes, strongest | yes |
| `EMBED_BATCH_MAX_TOKENS` | PyTorch, TEI | `16000` | linear, for long-chunk passes | yes | no |
| `DENSE_EMBED_BATCH_SIZE` | PyTorch | `32` | linear only below 10 | only below 10 | no |
| `embed_batch_size` (llama_index) | PyTorch | `10` (fixed) | linear | yes (not configurable) | no |
| `torch_dtype` | PyTorch | `float16` | x2 for float32 | use fp16/bf16 | yes |
| `EMBED_DYNAMIC_VRAM_CAP` | PyTorch | `False` | can only raise the cap | keep off | yes, if the cap changes |
| `INDEX_EMBED_DEVICE` | PyTorch | `"auto"` | which GPU / CPU | `"cpu"` = none | no |
| `TEI_MAX_BATCH_TOKENS` | TEI | = token budget | linear | yes (recreate container) | no |
| `TEI_DTYPE` | TEI | `float16` | x2 for float32 | use fp16 | yes |
| `expandable_segments` | PyTorch | unset | lowers fragmentation | n/a | no |
| pipeline depth, parse queue, pool, upsert, TEI concurrency, sparse batch | all | various | none (host RAM) | no | no |

## Example configuration for an 8 GB card

This is an **example**, not a guaranteed preset. It was checked with a ~300M-parameter model in bfloat16 on 8 GB GPUs: peak allocated VRAM stayed around 2 GB, so it is conservative. For such a model, `EMBED_MAX_SEQ_LENGTH = 4096` with `EMBED_BATCH_MAX_TOKENS = 16000` also fit (about 4.5 GB allocated) and is faster on long chunks; larger models need the values below. It applies the levers above in order of effectiveness to a PyTorch run on an 8 GB GPU. Check peak VRAM on your own codebase (`nvidia-smi -l 1`, or `torch.cuda.max_memory_allocated()`) and adjust.

```python
# project-configs/<name>/config.py
USE_TEI = False
EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}   # "bfloat16" for Gemma-based models
EMBED_MAX_SEQ_LENGTH = 2048     # strongest lever; longer chunks truncated for the dense vector -> --clear
EMBED_BATCH_MAX_TOKENS = 8000   # halves long-chunk passes; vectors unchanged
DENSE_EMBED_BATCH_SIZE = 16     # no VRAM effect above 10; set < 10 only if still OOM
EMBED_DYNAMIC_VRAM_CAP = False
INDEX_EMBED_DEVICE = "0"        # preferably a GPU without the display
# EMBED_PIPELINE_DEPTH: 0 by default; enabling it (e.g. 6) costs host RAM only, not VRAM
# Shell, before indexing:  set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

With TEI on 8 GB, the defaults (`TEI_MAX_BATCH_TOKENS` = 16000, float16) are usually enough for small (~150M-parameter) models, for example Jina v2 base code. For larger models, lower `TEI_MAX_BATCH_TOKENS` to 8000.

## TEI on CPU

VRAM does not matter when TEI runs on CPU, but a few parameters decide whether a CPU run works at all and how fast it is:

- **`EMBED_POOL_SIZE`: keep it clearly below TEI's `--max-concurrent-requests` (default 512).** A pool can overshoot `EMBED_POOL_SIZE`, because the last file is added whole. When one pool sends more inputs than TEI accepts, TEI answers `HTTP 429 Model is overloaded` and the run aborts. This applies to any `EMBED_PIPELINE_DEPTH`, including 0 (legacy). It shows up mostly on CPU, where requests stay queued for a long time. 256 is a safe value.
- **`TEI_MAX_BATCH_TOKENS`: start low (about 4096).** On CPU the batch buffers live in host RAM (or in the Docker VM's RAM), and float32 doubles them. A large budget can get the container OOM-killed during warm-up. Raise it only if the container has RAM to spare.
- **`EMBED_PIPELINE_DEPTH`: keep the default `0`.** Dense embedding dominates wall time and keeps all cores busy even with the legacy serial path, so there are almost no idle gaps for the pipeline to fill. Enabling it is safe once the pool size is small, but gains little.
- **`TEI_DTYPE`: must be `"float32"`** on CPU.

```python
# project-configs/<name>/config.py, TEI on CPU (example)
TEI_GPU = "cpu"
TEI_DTYPE = "float32"
TEI_MAX_BATCH_TOKENS = 4096
EMBED_POOL_SIZE = 256
EMBED_PIPELINE_DEPTH = 0   # default; pipelining gains little on CPU
```

## Reading `nvidia-smi` correctly

PyTorch's caching allocator keeps freed blocks reserved, so `nvidia-smi` usually shows the card almost full (often within a few hundred MB of the limit) even when the real working set is half that. In example measurements, peak *allocated* memory was 2-3x smaller than what `nvidia-smi` showed, and `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` did not change speed or the peak. Size settings by `torch.cuda.max_memory_allocated()` plus headroom, and treat OOM, not a full `nvidia-smi`, as the failure signal.

## OOM troubleshooting

1. **Confirm it is VRAM.** Look for `CUDA out of memory` / `torch.OutOfMemoryError` in the index log. Watch `nvidia-smi -l 1` during the run and check what else holds memory on that GPU.
2. **Free the GPU.** Close other CUDA processes. Don't run a TEI container and a PyTorch indexer on the same GPU. Use `INDEX_EMBED_DEVICE` to choose the card without the display.
3. **Halve `EMBED_BATCH_MAX_TOKENS`** (16000 -> 8000 -> 4000). It doesn't change vectors, and it is the first thing to try.
4. **Lower `DENSE_EMBED_BATCH_SIZE` below 10** (8 -> 4) if most chunks are medium-length. Values from 10 to 32 make no difference to VRAM.
5. **Lower `EMBED_MAX_SEQ_LENGTH`** (4096 -> 2048). This truncates long chunks for the dense vector, so rebuild with `--clear` and re-run RAG validation.
6. **Set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`** before starting the indexer if the error says a lot of memory is "reserved but unallocated" (fragmentation).
7. **Check dtype.** Make sure `EMBED_MODEL_KWARGS` sets float16/bfloat16; float32 doubles memory.
8. **Switch backend.** TEI usually needs less VRAM for the same model. CPU (`INDEX_EMBED_DEVICE = "cpu"`) always works but is much slower.
9. **Don't add parallelism to the PyTorch dense stage** (several concurrent pools, or larger `encode()` calls) without measuring peak VRAM. That combination can easily exceed 12 GB.
