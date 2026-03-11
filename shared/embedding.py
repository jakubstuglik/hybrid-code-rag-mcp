import gc
import math
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from shared.log import log, log_warn


def sanitize_dense_vector(vector: List[float]) -> tuple[List[float], int]:
    """Sanitize a single dense embedding vector for Qdrant compatibility.

    Fixes IEEE 754 artifacts that cause Qdrant REST API 400 errors:
    - Replaces ``-0.0`` with ``0.0`` (primary fix for float16 underflow)
    - Replaces ``NaN`` with ``0.0`` (safety net)
    - Replaces ``Inf`` / ``-Inf`` with ``0.0`` (safety net)

    Args:
        vector: A single dense embedding (list of floats).

    Returns:
        Tuple of (sanitized_vector, count_of_fixed_values).
    """
    fixed = 0
    sanitized = []
    for v in vector:
        if v != v:  # NaN check (fastest: NaN != NaN)
            sanitized.append(0.0)
            fixed += 1
        elif math.isinf(v):
            sanitized.append(0.0)
            fixed += 1
        elif v == 0.0 and math.copysign(1.0, v) < 0:  # -0.0 check
            sanitized.append(0.0)
            fixed += 1
        else:
            sanitized.append(v)
    return sanitized, fixed


def sanitize_dense_vectors(
    vectors: List[List[float]],
) -> tuple[List[List[float]], List[int]]:
    """Sanitize a batch of dense embedding vectors.

    Applies :func:`sanitize_dense_vector` to each vector and logs a warning
    if any values were fixed.

    Args:
        vectors: List of dense embeddings.

    Returns:
        Tuple of (sanitized_vectors, per_vector_fix_counts).
        ``per_vector_fix_counts[i]`` is the number of bad values fixed in
        ``vectors[i]``.  When the count equals the vector dimension, the
        entire vector was bad (all-zero after sanitisation).
    """
    total_fixed = 0
    result = []
    fix_counts = []
    for vec in vectors:
        sanitized, fixed = sanitize_dense_vector(vec)
        total_fixed += fixed
        result.append(sanitized)
        fix_counts.append(fixed)
    if total_fixed > 0:
        log_warn(
            f"Sanitized {total_fixed} bad float values "
            f"(-0.0/NaN/Inf) across {len(vectors)} vectors"
        )
    return result, fix_counts


def is_zero_vector(vector: List[float]) -> bool:
    """Check if a dense vector is all zeros (no search value).

    Args:
        vector: A single dense embedding.

    Returns:
        True if every element is exactly 0.0.
    """
    return all(v == 0.0 for v in vector)


def get_embed_model(device: str | None = None, cfg: Any = None) -> HuggingFaceEmbedding:
    """Get the embedding model based on config.

    Note: ``trust_remote_code=True`` is required for models with custom
    architectures (e.g. jinaai/jina-embeddings-v2-base-code uses a custom
    ``JinaBertModel`` with ALiBi position embeddings).  Without it,
    LlamaIndex falls back to a generic ``BertModel``, loads only the
    standard-named weights, and randomly initializes the rest — producing
    near-constant embeddings that make dense retrieval useless.

    The ``max_length`` parameter caps the tokenizer output length.  The jinaai
    model's ALiBi attention materializes a ``[1, H, N, N]`` bias tensor every
    forward pass — O(N²) VRAM.  Capping N prevents VRAM spikes on long chunks.

    When ``EMBED_DYNAMIC_VRAM_CAP`` is enabled in config and the device is
    CUDA, the max sequence length is computed dynamically based on available
    VRAM via :func:`shared.vram_cap.resolve_embed_max_seq_length`.  For CPU
    devices (MCP server, query tools), the static ``EMBED_MAX_SEQ_LENGTH``
    from config is used directly (no VRAM constraint on CPU).

    When ``USE_OPENVINO_EMBEDDING`` is enabled in config, uses OpenVINO
    for Intel GPU acceleration. Requires installing requirements_openvino.txt.

    Args:
        device: Override device (cuda/cpu). If None, uses cfg.INDEX_EMBED_DEVICE.
        cfg: Merged config object (from config_loader.get_config()).
            Required — all config reads go through this parameter.
    """
    if cfg is None:
        raise ValueError(
            "cfg is required — pass the merged config from config_loader.get_config()"
        )

    use_openvino = getattr(cfg, "USE_OPENVINO_EMBEDDING", False)

    if use_openvino:
        from llama_index.embeddings.huggingface_openvino import OpenVINOEmbedding

        openvino_device = getattr(cfg, "OPENVINO_EMBED_DEVICE", "GPU")
        max_len = getattr(cfg, "EMBED_MAX_SEQ_LENGTH", None)

        model_kwargs = dict(getattr(cfg, "EMBED_MODEL_KWARGS", {}))
        model_kwargs.setdefault("trust_remote_code", True)

        kwargs: dict = dict(
            model_id_or_path=cfg.MODEL_NAME,
            device=openvino_device,
            model_kwargs=model_kwargs,
        )
        if max_len is not None:
            kwargs["max_length"] = int(max_len)

        return OpenVINOEmbedding(**kwargs)

    effective_device = device or cfg.INDEX_EMBED_DEVICE

    if effective_device.startswith("cuda") and getattr(
        cfg, "EMBED_DYNAMIC_VRAM_CAP", False
    ):
        from shared.vram_cap import resolve_embed_max_seq_length

        max_len = resolve_embed_max_seq_length(cfg)
    else:
        max_len = getattr(cfg, "EMBED_MAX_SEQ_LENGTH", None)

    kwargs = dict(
        model_name=cfg.MODEL_NAME,
        device=effective_device,
        trust_remote_code=True,
        model_kwargs=cfg.EMBED_MODEL_KWARGS,
    )
    if max_len is not None:
        kwargs["max_length"] = int(max_len)

    return HuggingFaceEmbedding(**kwargs)


@dataclass
class TruncationInfo:
    """Info about a single truncated chunk."""

    index: int  # position in the document list
    token_count: int  # actual token count before truncation
    max_length: int  # the cap that caused truncation
    char_count: int  # character count of the original text
    text_preview: str  # first 80 chars for identification


@dataclass
class TruncationStats:
    """Accumulated truncation statistics across an indexing run.

    Tracks how many chunks were truncated by the tokenizer's max_length cap,
    and how much text was lost.  Used for the indexing summary.
    """

    total_chunks: int = 0
    truncated_chunks: int = 0
    total_tokens_before: int = 0  # sum of actual token counts (before truncation)
    total_tokens_after: int = 0  # sum of token counts after truncation (capped)
    max_length: int = 0  # the cap value
    # Per-file details (only stored when verbose)
    truncated_details: list = field(default_factory=list)

    @property
    def tokens_lost(self) -> int:
        return self.total_tokens_before - self.total_tokens_after

    @property
    def truncation_pct(self) -> float:
        """Percentage of total tokens lost to truncation."""
        if self.total_tokens_before == 0:
            return 0.0
        return 100.0 * self.tokens_lost / self.total_tokens_before

    def merge(self, other: "TruncationStats") -> None:
        """Merge another TruncationStats into this one."""
        self.total_chunks += other.total_chunks
        self.truncated_chunks += other.truncated_chunks
        self.total_tokens_before += other.total_tokens_before
        self.total_tokens_after += other.total_tokens_after
        self.max_length = other.max_length or self.max_length
        self.truncated_details.extend(other.truncated_details)


def check_truncation(
    embed_model: HuggingFaceEmbedding,
    documents: List[str],
    verbose: bool = False,
) -> TruncationStats:
    """Check which documents will be truncated by the embedding model's max_length.

    Uses the model's own tokenizer to count actual tokens per document.
    Documents exceeding ``embed_model.max_length`` will be silently truncated
    by the model during embedding — this function makes that visible.

    Args:
        embed_model: The loaded embedding model (has ._model.tokenizer).
        documents: List of text documents to check.
        verbose: If True, store per-chunk TruncationInfo details.

    Returns:
        TruncationStats with counts and token totals.
    """
    max_len = embed_model.max_length
    stats = TruncationStats(max_length=max_len)

    if not documents:
        return stats

    # Access tokenizer - works for both HuggingFaceEmbedding and OpenVINOEmbedding
    if hasattr(embed_model, "_tokenizer"):
        tokenizer = embed_model._tokenizer
    else:
        tokenizer = embed_model._model.tokenizer

    # Batch-tokenize for efficiency (don't actually need the IDs, just lengths)
    encoded = tokenizer(
        documents,
        add_special_tokens=True,
        truncation=False,  # don't truncate — we want the real length
        return_attention_mask=False,
        return_length=True,
    )

    lengths = encoded["length"]  # list of int, one per document

    stats.total_chunks = len(documents)
    for i, token_count in enumerate(lengths):
        capped = min(token_count, max_len)
        stats.total_tokens_before += token_count
        stats.total_tokens_after += capped

        if token_count > max_len:
            stats.truncated_chunks += 1
            if verbose:
                preview = documents[i][:80].replace("\n", " ").strip()
                stats.truncated_details.append(
                    TruncationInfo(
                        index=i,
                        token_count=token_count,
                        max_length=max_len,
                        char_count=len(documents[i]),
                        text_preview=preview,
                    )
                )

    return stats


def cuda_clear_cache() -> None:
    """Clear GPU VRAM cache if CUDA is available."""
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def cuda_vram_check(threshold: float = 0.75) -> bool:
    """Clear VRAM cache if GPU memory usage exceeds threshold fraction.

    Called before each embedding batch to prevent spilling into shared VRAM,
    which causes dramatic slowdowns on laptops and desktop GPUs with unified memory.

    Args:
        threshold: Fraction of total VRAM at which to trigger a cache clear (default 0.75).

    Returns:
        True if cache was cleared, False otherwise.
    """
    try:
        import torch

        if not torch.cuda.is_available():
            return False
        free, total = torch.cuda.mem_get_info()
        used_fraction = (total - free) / total
        if used_fraction >= threshold:
            torch.cuda.empty_cache()
            return True
    except (ImportError, Exception):
        pass
    return False


def _embed_batched(
    embed_fn: Callable[[List[str]], List[Any]],
    documents: List[str],
    batch_size: int,
    max_tokens: int,
    clear_cache_between_batches: bool = False,
    progress_callback: Callable[[int, int], None] | None = None,
    on_batch: Callable[[List[int], List[Any]], None] | None = None,
) -> List[Any]:  # type: ignore[return]
    """Core dynamic batching algorithm for any embedding function.

    Batches are flushed when either the count limit (batch_size) or the
    approximate token limit (max_tokens) is reached, whichever comes first.

    Documents are sorted by length descending for optimal GPU utilization —
    longest chunks are processed first when VRAM is unfragmented, and batches
    of similar-length documents minimize padding waste in transformer attention.

    Args:
        embed_fn: Callable that takes a list of strings and returns a list of embeddings.
        documents: List of text documents to embed.
        batch_size: Max number of chunks per batch.
        max_tokens: Max total approximate tokens per batch (chars / 4).
        clear_cache_between_batches: If True, calls cuda_clear_cache() after each batch.
            VRAM usage is also checked before every batch regardless of this flag —
            if usage exceeds 75%, the cache is cleared before the batch runs.
        progress_callback: Optional callback(embedded_count, total_count).
        on_batch: Optional callback(original_indices, batch_embeddings) fired after each
            batch with the original (pre-sort) indices and their embeddings. Use this to
            flush results incrementally (e.g. to SQLite) without waiting for the full run.

    Returns:
        List of embeddings in the same order as the input documents.
    """
    if not documents:
        return []

    # Sort by length DESCENDING (longest first) for optimal GPU memory usage:
    # batches of similar-length documents minimize padding waste in transformer
    # attention, and processing longest chunks first when VRAM is unfragmented
    # prevents OOM on the last batch after cache accumulation from prior batches.
    sorted_pairs = sorted(enumerate(documents), key=lambda x: len(x[1]), reverse=True)
    sorted_indices = [i for i, _ in sorted_pairs]
    sorted_docs = [doc for _, doc in sorted_pairs]

    results_in_sorted_order: List[Any] = []
    batch_docs: List[str] = []
    batch_sorted_indices: List[int] = []
    batch_chars = 0
    embedded_count = 0
    total = len(sorted_docs)

    def flush_batch() -> None:
        nonlocal embedded_count, batch_docs, batch_chars, batch_sorted_indices
        cuda_vram_check()
        batch_emb: List[Any] = embed_fn(batch_docs)
        if on_batch:
            # When on_batch is provided, results are flushed incrementally (e.g. to
            # SQLite).  Don't accumulate them in memory — store None placeholders so
            # the returned list has correct length but negligible RAM cost.
            original_indices = [sorted_indices[si] for si in batch_sorted_indices]
            on_batch(original_indices, batch_emb)
            results_in_sorted_order.extend([None] * len(batch_emb))
            del batch_emb  # free immediately
        else:
            results_in_sorted_order.extend(batch_emb)
        embedded_count += len(batch_docs)
        if progress_callback:
            progress_callback(embedded_count, total)
        batch_docs = []
        batch_sorted_indices = []
        batch_chars = 0

    for sorted_pos, doc in enumerate(sorted_docs):
        doc_chars = len(doc)
        # Check if the NEXT batch (including this doc) would be large enough
        # to warrant clearing cache before starting it.  Only clear when
        # clear_cache_between_batches is enabled AND the upcoming batch looks
        # big (more than half the token budget).  This avoids hammering
        # empty_cache() after every tiny batch which kills throughput.
        should_flush = len(batch_docs) > 0 and (
            len(batch_docs) >= batch_size or batch_chars + doc_chars > max_tokens * 4
        )
        if should_flush:
            flush_batch()
            # Decide whether to clear cache based on how large the NEXT
            # document is — if the next chunk is big, we want VRAM freed.
            if clear_cache_between_batches and doc_chars > max_tokens * 2:
                gc.collect()
                cuda_clear_cache()
        batch_docs.append(doc)
        batch_sorted_indices.append(sorted_pos)
        batch_chars += doc_chars

    if batch_docs:
        flush_batch()

    # Restore original order
    result = [None] * total
    for sorted_pos, original_idx in enumerate(sorted_indices):
        result[original_idx] = results_in_sorted_order[sorted_pos]
    return result


def embed_dense_batch(
    embed_model: HuggingFaceEmbedding,
    documents: List[str],
    batch_size: int | None = None,
    max_tokens: int | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    on_batch: Callable[[List[int], List[Any]], None] | None = None,
    cfg: Any = None,
) -> List[Any]:
    """Embed documents using dense model with dynamic batching.

    Args:
        embed_model: The embedding model to use.
        documents: List of text documents to embed.
        batch_size: Max chunks per batch (default: cfg.DENSE_EMBED_BATCH_SIZE).
        max_tokens: Max approximate tokens per batch (default: cfg.EMBED_BATCH_MAX_TOKENS).
        progress_callback: Optional callback(embedded_count, total_count).
        on_batch: Optional callback(original_indices, batch_embeddings) fired after each
            batch. Use to flush results incrementally (e.g. to SQLite).
        cfg: Merged config object. Required when batch_size/max_tokens are not
            explicitly provided.

    Returns:
        List of dense embeddings in input order.
    """
    if batch_size is None:
        if cfg is None:
            raise ValueError("cfg is required when batch_size is not provided")
        batch_size = int(getattr(cfg, "DENSE_EMBED_BATCH_SIZE", 64))
    if max_tokens is None:
        if cfg is None:
            raise ValueError("cfg is required when max_tokens is not provided")
        max_tokens = int(cfg.EMBED_BATCH_MAX_TOKENS)
    assert isinstance(batch_size, int)
    assert isinstance(max_tokens, int)

    return _embed_batched(
        embed_fn=embed_model.get_text_embedding_batch,
        documents=documents,
        batch_size=batch_size,
        max_tokens=max_tokens,
        clear_cache_between_batches=True,
        progress_callback=progress_callback,
        on_batch=on_batch,
    )


def embed_sparse_batch(
    sparse_encoder: Callable[[List[str]], tuple],
    documents: List[str],
    batch_size: int | None = None,
    max_tokens: int | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    cfg: Any = None,
) -> List[Any]:
    """Embed documents using sparse model with dynamic batching.

    Same algorithm as embed_dense_batch but wraps the sparse encoder output
    into dicts with 'indices' and 'values' keys, and clears VRAM between batches.

    Args:
        sparse_encoder: Callable returning (indices, values) tuple per batch.
        documents: List of text documents to embed.
        batch_size: Max chunks per batch (default: cfg.SPARSE_EMBED_BATCH_SIZE).
        max_tokens: Max approximate tokens per batch (default: cfg.EMBED_BATCH_MAX_TOKENS).
        progress_callback: Optional callback(embedded_count, total_count).
        cfg: Merged config object. Required when batch_size/max_tokens are not
            explicitly provided.

    Returns:
        List of dicts with 'indices' and 'values' keys, in input order.
    """
    if batch_size is None:
        if cfg is None:
            raise ValueError("cfg is required when batch_size is not provided")
        batch_size = int(getattr(cfg, "SPARSE_EMBED_BATCH_SIZE", 32))
    if max_tokens is None:
        if cfg is None:
            raise ValueError("cfg is required when max_tokens is not provided")
        max_tokens = int(cfg.EMBED_BATCH_MAX_TOKENS)
    assert isinstance(batch_size, int)
    assert isinstance(max_tokens, int)

    def sparse_fn(batch: List[str]) -> List[Any]:
        batch_indices, batch_values = sparse_encoder(batch)
        return [
            {"indices": idx, "values": vals}
            for idx, vals in zip(batch_indices, batch_values)
        ]

    return _embed_batched(
        embed_fn=sparse_fn,
        documents=documents,
        batch_size=batch_size,
        max_tokens=max_tokens,
        clear_cache_between_batches=True,
        progress_callback=progress_callback,
    )
