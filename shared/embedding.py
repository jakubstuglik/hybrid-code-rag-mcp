from typing import Any, Callable, List

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import config


def get_embed_model(device: str | None = None) -> HuggingFaceEmbedding:
    """Get the embedding model based on config."""
    return HuggingFaceEmbedding(
        model_name=config.MODEL_NAME,
        device=device or config.INDEX_EMBED_DEVICE,
        model_kwargs=config.EMBED_MODEL_KWARGS,
    )


def cuda_clear_cache() -> None:
    """Clear GPU VRAM cache if CUDA is available."""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def cuda_vram_check(threshold: float = 0.90) -> bool:
    """Clear VRAM cache if GPU memory usage exceeds threshold fraction.

    Called before each embedding batch to prevent spilling into shared VRAM,
    which causes dramatic slowdowns on laptops and desktop GPUs with unified memory.

    Args:
        threshold: Fraction of total VRAM at which to trigger a cache clear (default 0.90).

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
    Documents are sorted by length for better memory locality.

    Args:
        embed_fn: Callable that takes a list of strings and returns a list of embeddings.
        documents: List of text documents to embed.
        batch_size: Max number of chunks per batch.
        max_tokens: Max total approximate tokens per batch (chars / 4).
        clear_cache_between_batches: If True, calls cuda_clear_cache() after each batch.
            VRAM usage is also checked before every batch regardless of this flag —
            if usage exceeds 90%, the cache is cleared before the batch runs.
        progress_callback: Optional callback(embedded_count, total_count).
        on_batch: Optional callback(original_indices, batch_embeddings) fired after each
            batch with the original (pre-sort) indices and their embeddings. Use this to
            flush results incrementally (e.g. to SQLite) without waiting for the full run.

    Returns:
        List of embeddings in the same order as the input documents.
    """
    if not documents:
        return []

    # Sort by length; keep original indices to restore order
    sorted_pairs = sorted(enumerate(documents), key=lambda x: len(x[1]))
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
        results_in_sorted_order.extend(batch_emb)
        embedded_count += len(batch_docs)
        if progress_callback:
            progress_callback(embedded_count, total)
        if on_batch:
            original_indices = [sorted_indices[si] for si in batch_sorted_indices]
            on_batch(original_indices, batch_emb)
        if clear_cache_between_batches:
            cuda_clear_cache()
        batch_docs = []
        batch_sorted_indices = []
        batch_chars = 0

    for sorted_pos, doc in enumerate(sorted_docs):
        doc_chars = len(doc)
        should_flush = (
            len(batch_docs) > 0 and (
                len(batch_docs) >= batch_size or
                batch_chars + doc_chars > max_tokens * 4
            )
        )
        if should_flush:
            flush_batch()
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
) -> List[Any]:
    """Embed documents using dense model with dynamic batching.

    Args:
        embed_model: The embedding model to use.
        documents: List of text documents to embed.
        batch_size: Max chunks per batch (default: DENSE_EMBED_BATCH_SIZE).
        max_tokens: Max approximate tokens per batch (default: EMBED_BATCH_MAX_TOKENS).
        progress_callback: Optional callback(embedded_count, total_count).
        on_batch: Optional callback(original_indices, batch_embeddings) fired after each
            batch. Use to flush results incrementally (e.g. to SQLite).

    Returns:
        List of dense embeddings in input order.
    """
    if batch_size is None:
        batch_size = int(getattr(config, "DENSE_EMBED_BATCH_SIZE", 64))
    if max_tokens is None:
        max_tokens = int(config.EMBED_BATCH_MAX_TOKENS)
    assert isinstance(batch_size, int)
    assert isinstance(max_tokens, int)

    return _embed_batched(
        embed_fn=embed_model.get_text_embedding_batch,
        documents=documents,
        batch_size=batch_size,
        max_tokens=max_tokens,
        clear_cache_between_batches=False,
        progress_callback=progress_callback,
        on_batch=on_batch,
    )


def embed_sparse_batch(
    sparse_encoder: Callable[[List[str]], tuple],
    documents: List[str],
    batch_size: int | None = None,
    max_tokens: int | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> List[Any]:
    """Embed documents using sparse model with dynamic batching.

    Same algorithm as embed_dense_batch but wraps the sparse encoder output
    into dicts with 'indices' and 'values' keys, and clears VRAM between batches.

    Args:
        sparse_encoder: Callable returning (indices, values) tuple per batch.
        documents: List of text documents to embed.
        batch_size: Max chunks per batch (default: SPARSE_EMBED_BATCH_SIZE).
        max_tokens: Max approximate tokens per batch (default: EMBED_BATCH_MAX_TOKENS).
        progress_callback: Optional callback(embedded_count, total_count).

    Returns:
        List of dicts with 'indices' and 'values' keys, in input order.
    """
    if batch_size is None:
        batch_size = int(getattr(config, "SPARSE_EMBED_BATCH_SIZE", 32))
    if max_tokens is None:
        max_tokens = int(config.EMBED_BATCH_MAX_TOKENS)
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
