"""Cross-file chunk pooling for optimal GPU batching.

Accumulates chunks from multiple files and flushes them together so that
``_embed_batched()`` can sort by length across files — producing batches
with homogeneous chunk lengths that minimize padding waste in transformer
attention.

Usage::

    pool = ChunkPool(max_chunks=512, max_files=50)

    for file_key in files_to_process:
        nodes = load_nodes_for_file(...)
        ids = [make_id(file_key, i) for i in range(len(nodes))]
        documents = [node.text for node in nodes]
        pool.add(file_key, file_info, nodes, ids, documents, action_type)

        if pool.should_flush():
            all_docs, index_map = pool.collect()
            embeddings = embed_dense_batch(embed_model, all_docs, ...)
            per_file = pool.distribute(embeddings, sparse_dicts)
            for file_key, file_data in per_file.items():
                upsert(file_data)
            pool.clear()

    # Final flush for remaining chunks
    if pool.chunk_count > 0:
        ...same pattern...
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from shared.log import log, log_raw


# ────────────────────────────────────────────────────────────────────
# FileEntry: per-file data stored in the pool
# ────────────────────────────────────────────────────────────────────
@dataclass
class FileEntry:
    """Data for a single file in the chunk pool."""

    file_key: str
    file_info: dict
    nodes: list  # list of TextNode
    ids: list[str]  # vector IDs
    documents: list[str]  # node texts
    action_type: str  # "add" or "modify"
    # Range in the flattened document list [start, start + len(documents))
    global_start: int = 0


# ────────────────────────────────────────────────────────────────────
# ChunkPool
# ────────────────────────────────────────────────────────────────────
class ChunkPool:
    """Accumulates chunks from multiple files for cross-file batched embedding.

    Args:
        max_chunks: Flush threshold for total chunk count.  Set to 0 to
            disable pooling (each file is its own pool).
        max_files: Flush threshold for total file count.  Bounds how many
            files have their manifest update delayed.
    """

    def __init__(self, max_chunks: int = 512, max_files: int = 50) -> None:
        self.max_chunks = max_chunks
        self.max_files = max_files
        self._files: list[FileEntry] = []
        self._chunk_count: int = 0

    # ── Public API ────────────────────────────────────────────────

    @property
    def chunk_count(self) -> int:
        """Total number of chunks currently in the pool."""
        return self._chunk_count

    @property
    def file_count(self) -> int:
        """Number of files currently in the pool."""
        return len(self._files)

    @property
    def is_empty(self) -> bool:
        return self._chunk_count == 0

    def add(
        self,
        file_key: str,
        file_info: dict,
        nodes: list,
        ids: list[str],
        documents: list[str],
        action_type: str,
    ) -> None:
        """Add a file's chunks to the pool.

        Args:
            file_key: Manifest key for the file.
            file_info: Dict with file_path, mtime, hash, full_path.
            nodes: LlamaIndex TextNode list.
            ids: Vector IDs (one per node).
            documents: Text content of each node.
            action_type: "add" or "modify".
        """
        entry = FileEntry(
            file_key=file_key,
            file_info=file_info,
            nodes=nodes,
            ids=ids,
            documents=documents,
            action_type=action_type,
            global_start=self._chunk_count,
        )
        self._files.append(entry)
        self._chunk_count += len(documents)

    def should_flush(self) -> bool:
        """Return True if the pool has reached a flush threshold.

        When ``max_chunks == 0`` (pooling disabled), always returns True
        so each file is flushed immediately.
        """
        if self.max_chunks == 0:
            return True
        return (
            self._chunk_count >= self.max_chunks or len(self._files) >= self.max_files
        )

    def collect(self) -> Tuple[List[str], List[FileEntry]]:
        """Collect all documents from the pool into a flat list.

        Returns:
            Tuple of (all_documents, file_entries).
            ``all_documents[entry.global_start : entry.global_start + len(entry.documents)]``
            are the documents for ``entry``.
        """
        all_docs: list[str] = []
        for entry in self._files:
            all_docs.extend(entry.documents)
        return all_docs, self._files

    def distribute(
        self,
        dense_embeddings: List[Any],
        sparse_dicts: Optional[List[Any]] = None,
    ) -> List[Tuple[FileEntry, List[Any], Optional[List[Any]]]]:
        """Distribute embedding results back to per-file groups.

        Args:
            dense_embeddings: Flat list of dense embeddings (same order as
                the documents returned by ``collect()``).
            sparse_dicts: Flat list of sparse embedding dicts, or None if
                sparse embedding was not done.

        Returns:
            List of (FileEntry, file_dense_embeddings, file_sparse_dicts)
            tuples, one per file in insertion order.
        """
        result: list[Tuple[FileEntry, list[Any], Optional[list[Any]]]] = []
        for entry in self._files:
            start = entry.global_start
            end = start + len(entry.documents)
            file_dense = dense_embeddings[start:end]
            file_sparse = sparse_dicts[start:end] if sparse_dicts is not None else None
            result.append((entry, file_dense, file_sparse))
        return result

    def clear(self) -> None:
        """Remove all files and chunks from the pool."""
        self._files.clear()
        self._chunk_count = 0

    def files(self) -> List[FileEntry]:
        """Return the list of file entries (for iteration without collect)."""
        return list(self._files)


# ────────────────────────────────────────────────────────────────────
# Chunk-length histogram
# ────────────────────────────────────────────────────────────────────

# Bucket boundaries for the histogram (upper bound exclusive).
_CHAR_BUCKETS = [
    (0, 128),
    (128, 256),
    (256, 512),
    (512, 1024),
    (1024, 2048),
    (2048, 4096),
    (4096, 8192),
]
_CHAR_BUCKET_LABELS = [
    "0-128",
    "128-256",
    "256-512",
    "512-1024",
    "1024-2048",
    "2048-4096",
    "4096-8192",
    "8192+",
]

_TOKEN_BUCKETS = [
    (0, 64),
    (64, 128),
    (128, 256),
    (256, 512),
    (512, 1024),
    (1024, 2048),
    (2048, 4096),
]
_TOKEN_BUCKET_LABELS = [
    "0-64",
    "64-128",
    "128-256",
    "256-512",
    "512-1024",
    "1024-2048",
    "2048-4096",
    "4096+",
]


@dataclass
class ChunkHistogram:
    """Collects chunk-length statistics during indexing.

    Tracks both character lengths and token lengths for all chunks.
    Token lengths are only available when the embedding model has a local
    tokenizer (not TEI).
    """

    char_lengths: list[int] = field(default_factory=list)
    token_lengths: list[int] = field(default_factory=list)
    total_files: int = 0

    def add_char_lengths(self, lengths: Sequence[int]) -> None:
        """Add character lengths for a batch of chunks."""
        self.char_lengths.extend(lengths)

    def add_token_lengths(self, lengths: Sequence[int]) -> None:
        """Add token lengths for a batch of chunks."""
        self.token_lengths.extend(lengths)

    def increment_files(self, count: int = 1) -> None:
        self.total_files += count

    @property
    def total_chunks(self) -> int:
        return len(self.char_lengths)

    def to_dict(
        self,
        config_name: str = "",
        model_name: str = "",
        branch: str = "",
    ) -> dict:
        """Serialize to a JSON-compatible dict.

        Args:
            config_name: Name of the config used for indexing.
            model_name: Name of the embedding model.
            branch: Branch name (empty string for main branch).

        Returns:
            Dict matching the design doc schema.
        """
        result: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
            "config_name": config_name,
            "model_name": model_name,
            "branch": branch,
            "total_chunks": self.total_chunks,
            "total_files": self.total_files,
        }

        if self.char_lengths:
            result["char_lengths"] = _compute_stats(
                self.char_lengths, _CHAR_BUCKETS, _CHAR_BUCKET_LABELS
            )

        if self.token_lengths:
            result["token_lengths"] = _compute_stats(
                self.token_lengths, _TOKEN_BUCKETS, _TOKEN_BUCKET_LABELS
            )

        return result

    def save(
        self,
        index_path: str | Path,
        config_name: str = "",
        model_name: str = "",
        branch: str = "",
    ) -> Path:
        """Save histogram to JSON in the index directory.

        Args:
            index_path: Directory to write the histogram file into.
            config_name: Config name to include in the JSON metadata.
            model_name: Model name to include in the JSON metadata.
            branch: Branch name. When non-empty, the filename becomes
                ``chunk_histogram_branch_<sanitized>.json`` so that branch
                overlay histograms don't overwrite the main-branch histogram.

        Returns:
            Path to the saved file.
        """
        if branch:
            # Sanitize branch name for filename (same logic as git_ops.sanitize_branch_name)
            safe = branch
            for ch in '/\\:*?"<>| ':
                safe = safe.replace(ch, "_")
            filename = f"chunk_histogram_branch_{safe}.json"
        else:
            filename = "chunk_histogram.json"

        path = Path(index_path) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict(
            config_name=config_name, model_name=model_name, branch=branch
        )
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def log_summary(self) -> None:
        """Print a human-readable summary to the log."""
        if not self.char_lengths:
            return

        n = self.total_chunks
        f = self.total_files
        log_raw("")
        log(f"Chunk length distribution ({n:,} chunks from {f:,} files):")

        chars = sorted(self.char_lengths)
        log_raw(
            f"  Chars:   "
            f"P50={_percentile(chars, 50):,}  "
            f"P90={_percentile(chars, 90):,}  "
            f"P95={_percentile(chars, 95):,}  "
            f"P99={_percentile(chars, 99):,}  "
            f"Max={chars[-1]:,}"
        )

        if self.token_lengths:
            tokens = sorted(self.token_lengths)
            log_raw(
                f"  Tokens:  "
                f"P50={_percentile(tokens, 50):,}  "
                f"P90={_percentile(tokens, 90):,}  "
                f"P95={_percentile(tokens, 95):,}  "
                f"P99={_percentile(tokens, 99):,}  "
                f"Max={tokens[-1]:,}"
            )


# ── Helpers ──────────────────────────────────────────────────────


def _percentile(sorted_data: list[int], p: int) -> int:
    """Compute the p-th percentile from sorted data."""
    if not sorted_data:
        return 0
    k = (len(sorted_data) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[f]
    return round(sorted_data[f] * (c - k) + sorted_data[c] * (k - f))


def _compute_stats(
    values: list[int],
    buckets: list[tuple[int, int]],
    labels: list[str],
) -> dict:
    """Compute min/max/mean/median/percentiles and bucket counts."""
    if not values:
        return {}

    sorted_vals = sorted(values)
    n = len(sorted_vals)

    stats: dict[str, Any] = {
        "min": sorted_vals[0],
        "max": sorted_vals[-1],
        "mean": round(sum(sorted_vals) / n),
        "p10": _percentile(sorted_vals, 10),
        "p25": _percentile(sorted_vals, 25),
        "p50": _percentile(sorted_vals, 50),
        "p75": _percentile(sorted_vals, 75),
        "p90": _percentile(sorted_vals, 90),
        "p95": _percentile(sorted_vals, 95),
        "p99": _percentile(sorted_vals, 99),
    }
    stats["median"] = stats["p50"]

    # Bucket counts
    bucket_counts: dict[str, int] = {label: 0 for label in labels}
    for v in sorted_vals:
        placed = False
        for (lo, hi), label in zip(buckets, labels):
            if lo <= v < hi:
                bucket_counts[label] += 1
                placed = True
                break
        if not placed:
            # Overflow bucket (last label)
            bucket_counts[labels[-1]] += 1

    stats["buckets"] = bucket_counts
    return stats
