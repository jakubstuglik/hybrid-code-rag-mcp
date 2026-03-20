import gc
import json
import math
import urllib.error
import urllib.request
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from shared.log import log, log_warn


# ════════════════════════════════════════════════════════════════════
# TEI Embedding class (wraps TEI's /embed HTTP endpoint)
# ════════════════════════════════════════════════════════════════════


class TEIEmbedding(BaseEmbedding):
    """LlamaIndex-compatible embedding model backed by a TEI HTTP server.

    Sends text to ``TEI_URL/embed`` and returns dense vectors.  TEI handles
    tokenization, truncation, and batching internally.  This class presents
    the same interface as ``HuggingFaceEmbedding`` so it can be used as a
    drop-in replacement throughout the indexer and MCP server.

    The model dimension is auto-detected on first use via a probe embedding.

    Args:
        tei_url: Base URL of the TEI server (e.g. "http://localhost:8090").
        model_name: Model identifier (used for metadata/logging only — TEI
            already knows which model it's serving).
        timeout: HTTP request timeout in seconds per call.
        query_prefix: String prepended to query text before embedding.
            Some models (e.g. Nomic Embed V2) require ``"search_query: "``.
            None or ``""`` means no prefix.
        text_prefix: String prepended to document text before embedding.
            Some models (e.g. Nomic Embed V2) require ``"search_document: "``.
            None or ``""`` means no prefix.
    """

    model_name: str = "jinaai/jina-embeddings-v2-base-code"
    _tei_url: str = PrivateAttr()
    _timeout: float = PrivateAttr(default=120.0)
    _dimension: Optional[int] = PrivateAttr(default=None)
    _query_prefix: str = PrivateAttr(default="")
    _text_prefix: str = PrivateAttr(default="")

    def __init__(
        self,
        tei_url: str = "http://localhost:8090",
        model_name: str = "jinaai/jina-embeddings-v2-base-code",
        timeout: float = 120.0,
        query_prefix: Optional[str] = None,
        text_prefix: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(model_name=model_name, **kwargs)
        self._tei_url = tei_url.rstrip("/")
        self._timeout = timeout
        self._dimension = None
        self._query_prefix = query_prefix or ""
        self._text_prefix = text_prefix or ""

    def _post_embed(self, texts: List[str]) -> List[List[float]]:
        """Send a batch of texts to TEI's /embed endpoint.

        Args:
            texts: List of strings to embed.

        Returns:
            List of embedding vectors (list of floats).

        Raises:
            RuntimeError: If the TEI server returns a non-200 response.
        """
        url = f"{self._tei_url}/embed"
        payload = json.dumps({"inputs": texts}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                if resp.status != 200:
                    body = resp.read().decode("utf-8", errors="replace")
                    raise RuntimeError(
                        f"TEI /embed returned HTTP {resp.status}: {body[:500]}"
                    )
                result = json.loads(resp.read().decode("utf-8"))
                return result
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise RuntimeError(
                f"TEI /embed returned HTTP {exc.code}: {body[:500]}"
            ) from exc

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a single query string."""
        result = self._post_embed([self._query_prefix + query])
        return result[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text string."""
        result = self._post_embed([self._text_prefix + text])
        return result[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a batch of texts."""
        if not texts:
            return []
        if self._text_prefix:
            texts = [self._text_prefix + t for t in texts]
        return self._post_embed(texts)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Async query embedding (delegates to sync for simplicity)."""
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Async text embedding (delegates to sync for simplicity)."""
        return self._get_text_embedding(text)

    @property
    def dimension(self) -> int:
        """Auto-detect embedding dimension via a probe call."""
        if self._dimension is None:
            probe = self._get_text_embedding("dimension probe")
            self._dimension = len(probe)
        return self._dimension


# ════════════════════════════════════════════════════════════════════
# Embedding backend family detection
# ════════════════════════════════════════════════════════════════════


def get_embed_backend_family(cfg: Any) -> str:
    """Determine the embedding backend family from config.

    Two families produce incompatible vectors:
    - ``"pytorch"`` — PyTorch CUDA, PyTorch CPU, OpenVINO (same math/weights)
    - ``"tei"`` — Candle (Rust) inference engine (TEI NVIDIA, TEI CPU)

    Args:
        cfg: Merged config object.

    Returns:
        ``"tei"`` if USE_TEI is True, otherwise ``"pytorch"``.
    """
    use_tei = getattr(cfg, "USE_TEI", False)
    return "tei" if use_tei else "pytorch"


# ════════════════════════════════════════════════════════════════════
# Embedding provenance tracking
# ════════════════════════════════════════════════════════════════════
# Stores and checks the embedding backend family ("pytorch" or "tei")
# in Qdrant collection metadata via a sentinel point.  This prevents
# silently mixing vectors from incompatible inference engines.
# ════════════════════════════════════════════════════════════════════

# Well-known UUID for the provenance sentinel point
_PROVENANCE_POINT_ID = "00000000-0000-0000-0000-000000000001"


def get_collection_provenance(client: Any, collection_name: str) -> Optional[str]:
    """Read the embed_backend provenance from a Qdrant collection.

    Provenance is stored as a sentinel point with ``_PROVENANCE_POINT_ID``.

    Args:
        client: QdrantClient instance.
        collection_name: Name of the Qdrant collection.

    Returns:
        ``"pytorch"``, ``"tei"``, or ``None`` if no provenance is stored
        (legacy collections created before provenance tracking).
    """
    try:
        points = client.retrieve(
            collection_name=collection_name,
            ids=[_PROVENANCE_POINT_ID],
            with_payload=True,
            with_vectors=False,
        )
        if points:
            payload = points[0].payload or {}
            return payload.get("embed_backend")
    except Exception:
        pass

    return None


def set_collection_provenance(
    client: Any, collection_name: str, backend_family: str, dim: int
) -> None:
    """Store the embed_backend provenance in a Qdrant collection.

    Uses a sentinel point with ``_PROVENANCE_POINT_ID`` to store provenance
    metadata.  The point has a zero vector (not search-relevant) and carries
    the ``embed_backend`` payload field plus a ``_provenance_sentinel`` flag.

    Detects whether the collection uses named vectors (hybrid) or unnamed
    (dense-only) and creates the appropriate vector format.

    Args:
        client: QdrantClient instance.
        collection_name: Name of the Qdrant collection.
        backend_family: ``"pytorch"`` or ``"tei"``.
        dim: Embedding dimension (needed for the zero-vector).
    """
    from qdrant_client import models as qdrant_models

    # Detect whether the collection uses named vectors (hybrid) or unnamed
    try:
        info = client.get_collection(collection_name=collection_name)
        vectors_config = info.config.params.vectors
        is_hybrid = isinstance(vectors_config, dict) and len(vectors_config) > 0
    except Exception:
        is_hybrid = False

    if is_hybrid:
        vectors: Any = {"text-dense": [0.0] * dim}
    else:
        vectors = [0.0] * dim

    client.upsert(
        collection_name=collection_name,
        points=[
            qdrant_models.PointStruct(
                id=_PROVENANCE_POINT_ID,
                payload={
                    "embed_backend": backend_family,
                    "_provenance_sentinel": True,
                },
                vector=vectors,
            ),
        ],
    )
    log(f"Stored embedding provenance: embed_backend='{backend_family}'")


def check_provenance_for_indexing(client: Any, collection_name: str, cfg: Any) -> None:
    """Check provenance before indexing and hard-block on mismatch.

    If the collection was built with a different embedding backend family,
    indexing would produce vectors in a different vector space.  This
    function logs an error and returns False (caller should exit).

    Args:
        client: QdrantClient instance.
        collection_name: Name of the Qdrant collection.
        cfg: Merged config object.

    Returns:
        None.  Calls ``sys.exit(1)`` on mismatch.
    """
    import sys

    current_backend = get_embed_backend_family(cfg)
    stored_backend = get_collection_provenance(client, collection_name)

    if stored_backend is None:
        log(
            f"No provenance found in collection '{collection_name}' "
            f"(legacy or new collection)"
        )
        return

    if stored_backend != current_backend:
        from shared.log import log_error

        log_error(
            f"EMBEDDING BACKEND MISMATCH\n"
            f"  Collection '{collection_name}' was built with: {stored_backend}\n"
            f"  Current config uses: {current_backend}\n"
            f"  These produce INCOMPATIBLE vectors.\n"
            f"  Options:\n"
            f"    1. Switch config back to {stored_backend}\n"
            f"    2. Reindex with --clear to rebuild using {current_backend}\n"
            f"  Cannot mix vectors from different embedding engines."
        )
        sys.exit(1)

    log(f"Provenance check OK: collection and config both use '{current_backend}'")


def check_provenance_for_query(client: Any, collection_name: str, cfg: Any) -> None:
    """Check provenance for MCP queries and warn on mismatch.

    Unlike indexing, query-time mismatch is a WARNING (not a hard block)
    because the MCP server should still start — just with degraded results.

    Args:
        client: QdrantClient instance.
        collection_name: Name of the Qdrant collection.
        cfg: Merged config object.
    """
    current_backend = get_embed_backend_family(cfg)
    stored_backend = get_collection_provenance(client, collection_name)

    if stored_backend is None:
        return  # Legacy collection — no provenance, no warning

    if stored_backend != current_backend:
        log_warn(
            f"EMBEDDING BACKEND MISMATCH (query mode)\n"
            f"  Collection '{collection_name}' was built with: {stored_backend}\n"
            f"  Current config uses: {current_backend}\n"
            f"  Search results may be degraded (different vector spaces).\n"
            f"  For best results, match the config to the indexing backend."
        )
    else:
        log(f"Provenance check OK: collection and config both use '{current_backend}'")


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


@dataclass
class DeviceCheckResult:
    """Result of device configuration validation.

    Attributes:
        ok: True if the configuration is valid (possibly with warnings).
        errors: Fatal problems — indexing cannot proceed.
        warnings: Non-fatal suggestions — user may want to change config.
    """

    ok: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _check_cuda_available() -> bool:
    """Check if PyTorch CUDA is available."""
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def _check_cuda_device_name() -> Optional[str]:
    """Return the CUDA GPU name, or None if unavailable."""
    try:
        import torch

        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except (ImportError, Exception):
        pass
    return None


def _check_openvino_devices() -> List[str]:
    """Return list of OpenVINO devices, or empty if openvino not installed."""
    try:
        import openvino as ov

        return list(ov.Core().available_devices)
    except (ImportError, Exception):
        return []


def validate_device_config(cfg: Any) -> DeviceCheckResult:
    """Validate embedding device configuration against actual hardware.

    Checks for mismatches between what the config requests and what the
    system can provide, returning errors (fatal) and warnings (suggestions).

    Call this before ``get_embed_model()`` to give the user a clear message
    instead of a cryptic PyTorch/OpenVINO stack trace.

    Args:
        cfg: Merged config object (from config_loader.get_config()).
    """
    result = DeviceCheckResult()
    use_tei = getattr(cfg, "USE_TEI", False)
    use_openvino = getattr(cfg, "USE_OPENVINO_EMBEDDING", False)
    openvino_device = getattr(cfg, "OPENVINO_EMBED_DEVICE", "GPU").upper()
    index_device = getattr(cfg, "INDEX_EMBED_DEVICE", "cpu").lower()

    cuda_available = _check_cuda_available()
    cuda_name = _check_cuda_device_name() if cuda_available else None
    ov_devices = _check_openvino_devices()
    ov_has_gpu = "GPU" in ov_devices

    if use_tei:
        # ── TEI path ──────────────────────────────────────────────
        # TEI uses Docker — the container handles hardware detection.
        # We just warn about conflicting flags.
        if use_openvino:
            result.warnings.append(
                "Both USE_TEI=True and USE_OPENVINO_EMBEDDING=True are set.\n"
                "  TEI takes priority — OpenVINO embedding will be ignored."
            )
        return result

    elif use_openvino:
        # ── OpenVINO path ─────────────────────────────────────────
        if not ov_devices:
            result.ok = False
            result.errors.append(
                "USE_OPENVINO_EMBEDDING=True but OpenVINO is not installed or failed to load.\n"
                "  Install with: uv pip install -r requirements/requirements_openvino.txt"
            )
            return result

        if openvino_device == "GPU" and not ov_has_gpu:
            result.ok = False
            result.errors.append(
                f"OPENVINO_EMBED_DEVICE='GPU' but no Intel GPU found by OpenVINO.\n"
                f"  Available OpenVINO devices: {ov_devices}\n"
                f"  Set OPENVINO_EMBED_DEVICE='CPU' to use the OpenVINO CPU backend."
            )
            return result

        if cuda_available:
            result.warnings.append(
                f"NVIDIA GPU detected ({cuda_name}) but OpenVINO is enabled.\n"
                f"  CUDA is typically faster than OpenVINO for embedding.\n"
                f"  To use CUDA: set USE_OPENVINO_EMBEDDING=False and INDEX_EMBED_DEVICE='cuda'."
            )

    else:
        # ── PyTorch (CUDA / CPU) path ─────────────────────────────
        if index_device.startswith("cuda") and not cuda_available:
            result.ok = False
            result.errors.append(
                f"INDEX_EMBED_DEVICE='{index_device}' but CUDA is not available.\n"
                "  PyTorch was built without CUDA support, or no NVIDIA GPU was found.\n"
                "  Options:\n"
                "    - Set INDEX_EMBED_DEVICE='cpu' (slow but works everywhere)\n"
                "    - Install PyTorch with CUDA: uv pip install -r requirements/requirements_cuda.txt\n"
                "    - Enable OpenVINO for Intel GPU: set USE_OPENVINO_EMBEDDING=True"
            )
            return result

        if index_device == "cpu":
            if cuda_available:
                result.warnings.append(
                    f"NVIDIA GPU detected ({cuda_name}) but INDEX_EMBED_DEVICE='cpu'.\n"
                    f"  Set INDEX_EMBED_DEVICE='cuda' for significantly faster embedding."
                )
            elif ov_has_gpu:
                result.warnings.append(
                    "Intel GPU detected by OpenVINO but not being used.\n"
                    "  Set USE_OPENVINO_EMBEDDING=True and OPENVINO_EMBED_DEVICE='GPU'\n"
                    "  for significantly faster embedding (~15x vs CPU)."
                )

    return result


def get_embed_model(device: str | None = None, cfg: Any = None) -> BaseEmbedding:
    """Get the embedding model based on config.

    When ``USE_TEI`` is enabled, returns a :class:`TEIEmbedding` that delegates
    to the TEI HTTP server.  The ``device`` parameter is ignored in this case
    (TEI manages its own compute device inside Docker).

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
    for Intel GPU acceleration. Requires installing requirements/requirements_openvino.txt.

    Args:
        device: Override device (cuda/cpu). If None, uses cfg.INDEX_EMBED_DEVICE.
            Ignored when USE_TEI=True.
        cfg: Merged config object (from config_loader.get_config()).
            Required — all config reads go through this parameter.
    """
    if cfg is None:
        raise ValueError(
            "cfg is required — pass the merged config from config_loader.get_config()"
        )

    # Suppress the "optimum is not installed" warning from Jina's custom
    # configuration_bert.py — we don't use ONNX export, so this is noise.
    warnings.filterwarnings(
        "ignore",
        message="optimum is not installed",
        category=UserWarning,
    )

    use_tei = getattr(cfg, "USE_TEI", False)

    if use_tei:
        # ── TEI path ──────────────────────────────────────────────
        from shared.docker_utils import _get_tei_url

        tei_url = _get_tei_url(cfg)
        model_name = getattr(cfg, "MODEL_NAME", "jinaai/jina-embeddings-v2-base-code")
        query_prefix = getattr(cfg, "EMBED_QUERY_PREFIX", None)
        text_prefix = getattr(cfg, "EMBED_TEXT_PREFIX", None)
        log(f"Using TEI embedding backend at {tei_url}")
        if query_prefix or text_prefix:
            log(f"  Query prefix: {query_prefix!r}  Text prefix: {text_prefix!r}")
        return TEIEmbedding(
            tei_url=tei_url,
            model_name=model_name,
            query_prefix=query_prefix,
            text_prefix=text_prefix,
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
    # Per-chunk token lengths (before truncation) — used by ChunkHistogram.
    # Only populated when a local tokenizer is available (not TEI).
    token_lengths: list[int] = field(default_factory=list)
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
        self.token_lengths.extend(other.token_lengths)
        self.truncated_details.extend(other.truncated_details)


def check_truncation(
    embed_model: BaseEmbedding,
    documents: List[str],
    verbose: bool = False,
) -> TruncationStats:
    """Check which documents will be truncated by the embedding model's max_length.

    Uses the model's own tokenizer to count actual tokens per document.
    Documents exceeding ``embed_model.max_length`` will be silently truncated
    by the model during embedding — this function makes that visible.

    When the model is a :class:`TEIEmbedding`, truncation stats are unavailable
    (TEI handles truncation internally via ``--auto-truncate``).  Returns an
    empty TruncationStats with a log message.

    Args:
        embed_model: The loaded embedding model (has ._model.tokenizer).
        documents: List of text documents to check.
        verbose: If True, store per-chunk TruncationInfo details.

    Returns:
        TruncationStats with counts and token totals.
    """
    # TEI handles truncation internally — no local tokenizer available
    if isinstance(embed_model, TEIEmbedding):
        log(
            "Truncation stats unavailable (TEI handles truncation internally "
            "via --auto-truncate)"
        )
        return TruncationStats(total_chunks=len(documents))
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
    stats.token_lengths = list(lengths)  # expose for ChunkHistogram
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
    embed_model: BaseEmbedding,
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
