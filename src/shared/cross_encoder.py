# SPDX-License-Identifier: Apache-2.0
"""Optional fastembed cross-encoder stage in front of the heuristic reranker.

Off unless ``RERANK_CROSS_ENCODER_MODEL`` names a model. Query-time only:
nothing is written to the index. The validation runner and the MCP search
tool both call ``begin_query_rank`` so the fused-pool size and the blend
cannot drift apart.

When the stage is on, each fused candidate (including symbol-lookup
additions) is scored by a ``TextCrossEncoder``. The blended score is

    w * sigmoid(cross-encoder logit) + (1 - w) * fused score

with ``w`` = ``RERANK_CROSS_ENCODER_WEIGHT``. The list is sorted by that
score, highest first, ties keeping the previous order. ``rerank_results``
then runs as usual and keeps that order when none of its rules change a
score. A missing, non-finite or short score list leaves those candidates
on their fused score.

The encoder is loaded once per process for each (model, device) pair.
``cuda`` asks onnxruntime for ``CUDAExecutionProvider`` and falls back to
CPU, with a warning, when that provider is unavailable. Model files come
from the local Hugging Face / fastembed cache and are downloaded only the
first time a model is used, the same way the BM25 sparse model is.
"""

import math
import threading
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple

from shared.log import log, log_warn

_DEFAULT_POOL = 32
_DEFAULT_WEIGHT = 0.5
_DEFAULT_DOC_CHARS = 1000
_DEFAULT_DEVICE = "cpu"
_DEFAULT_BATCH = 16
_DEVICES = ("cpu", "cuda")

_ENCODERS: dict = {}
_LOCK = threading.Lock()


@dataclass(frozen=True)
class CrossEncoderSettings:
    """Resolved ``RERANK_CROSS_ENCODER_*`` values. ``model`` None means off."""

    model: Optional[str]
    pool: int
    weight: float
    doc_chars: int
    device: str
    batch: int


def _raw(cfg: Any, name: str) -> Any:
    if cfg is None:
        return None
    return getattr(cfg, name, None)


def cross_encoder_model_name(cfg: Any) -> Optional[str]:
    """Model name, or None when the stage is off.

    None, a missing attribute and a blank string are off. Any other
    non-string is a configuration error.
    """
    raw = _raw(cfg, "RERANK_CROSS_ENCODER_MODEL")
    if raw is None:
        return None
    if isinstance(raw, str):
        name = raw.strip()
        return name or None
    raise ValueError(
        f"RERANK_CROSS_ENCODER_MODEL must be a model name or None, got {raw!r}."
    )


def _unit_interval(name: str, raw: Any, default: float) -> float:
    if raw is None:
        return default
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise ValueError(f"{name} must be a number in [0, 1], got {raw!r}.")
    number = float(raw)
    if not math.isfinite(number) or number < 0.0 or number > 1.0:
        raise ValueError(f"{name} must be a number in [0, 1], got {raw!r}.")
    return number


def _positive_int(name: str, raw: Any, default: int) -> int:
    if raw is None:
        return default
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
        raise ValueError(f"{name} must be an integer >= 1, got {raw!r}.")
    return raw


def _device(raw: Any) -> str:
    if raw is None:
        return _DEFAULT_DEVICE
    if isinstance(raw, str):
        device = raw.strip().lower()
    else:
        device = ""
    if device not in _DEVICES:
        raise ValueError(
            f"RERANK_CROSS_ENCODER_DEVICE must be 'cpu' or 'cuda', got {raw!r}."
        )
    return device


def resolve_cross_encoder_settings(cfg: Any) -> CrossEncoderSettings:
    """Validated settings. Missing values are the defaults.

    Raises ``ValueError`` for a weight outside [0, 1], a pool / document
    length / batch below 1, or a device other than ``cpu`` or ``cuda``.
    Checked even when the model is unset, so a typo fails at config load
    and at query time (``validate_rag --set`` does not reload the config).
    """
    return CrossEncoderSettings(
        model=cross_encoder_model_name(cfg),
        pool=_positive_int(
            "RERANK_CROSS_ENCODER_POOL", _raw(cfg, "RERANK_CROSS_ENCODER_POOL"), _DEFAULT_POOL
        ),
        weight=_unit_interval(
            "RERANK_CROSS_ENCODER_WEIGHT",
            _raw(cfg, "RERANK_CROSS_ENCODER_WEIGHT"),
            _DEFAULT_WEIGHT,
        ),
        doc_chars=_positive_int(
            "RERANK_CROSS_ENCODER_DOC_CHARS",
            _raw(cfg, "RERANK_CROSS_ENCODER_DOC_CHARS"),
            _DEFAULT_DOC_CHARS,
        ),
        device=_device(_raw(cfg, "RERANK_CROSS_ENCODER_DEVICE")),
        batch=_positive_int(
            "RERANK_CROSS_ENCODER_BATCH",
            _raw(cfg, "RERANK_CROSS_ENCODER_BATCH"),
            _DEFAULT_BATCH,
        ),
    )


def validate_cross_encoder_settings(cfg: Any) -> None:
    """Raise ``ValueError`` when a cross-encoder setting is invalid."""
    resolve_cross_encoder_settings(cfg)


def sigmoid(value: float) -> float:
    """Logistic squash of a cross-encoder logit into (0, 1)."""
    if value >= 0.0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _fused_score(node: Any) -> float:
    score = getattr(node, "score", None)
    if score is None or isinstance(score, bool):
        return 0.0
    try:
        number = float(score)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return number


def _ce_score(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _chunk_text(node: Any) -> str:
    inner = getattr(node, "node", None)
    if inner is None:
        return ""
    text = getattr(inner, "text", None)
    if isinstance(text, str):
        return text
    get_content = getattr(inner, "get_content", None)
    if not callable(get_content):
        return ""
    try:
        value = get_content()
    except Exception:  # noqa: BLE001 — a chunk that cannot be read is empty text
        return ""
    return value if isinstance(value, str) else ""


def _construct_cross_encoder(model_name: str, device: str) -> Any:
    """Build a fastembed ``TextCrossEncoder``. Downloads on first use only."""
    from fastembed.rerank.cross_encoder import TextCrossEncoder

    if device == "cuda":
        return TextCrossEncoder(model_name, providers=["CUDAExecutionProvider"])
    return TextCrossEncoder(model_name)


def _load_cross_encoder(model_name: str, device: str) -> Tuple[Any, str]:
    """Load ``model_name`` on ``device``. Returns ``(encoder, device_used)``."""
    if device == "cuda":
        try:
            model = _construct_cross_encoder(model_name, "cuda")
        except Exception as exc:  # noqa: BLE001 — any provider failure falls back to CPU
            log_warn(
                f"CUDAExecutionProvider unavailable for cross-encoder ({exc}); "
                "falling back to CPU"
            )
            model = _construct_cross_encoder(model_name, "cpu")
            log(f"Cross-encoder '{model_name}' loaded on cpu")
            return model, "cpu"
        log(f"Cross-encoder '{model_name}' loaded on cuda")
        return model, "cuda"
    model = _construct_cross_encoder(model_name, "cpu")
    log(f"Cross-encoder '{model_name}' loaded on cpu")
    return model, "cpu"


def get_cross_encoder(model_name: str, device: str) -> Any:
    """Cached encoder for ``(model_name, device)``. One load log per pair."""
    key = (model_name, device)
    with _LOCK:
        cached = _ENCODERS.get(key)
        if cached is not None:
            return cached
        model, used = _load_cross_encoder(model_name, device)
        _ENCODERS[(model_name, used)] = model
        _ENCODERS[key] = model
        return model


def score_and_blend(nodes: Sequence[Any], query: str, cfg: Any) -> List[Any]:
    """Return new ``NodeWithScore`` objects sorted by the blended score.

    Does not mutate ``nodes`` or their scores. An empty pool returns
    ``[]`` and does not load the model. The caller must set
    ``RERANK_CROSS_ENCODER_MODEL``.
    """
    if not nodes:
        return []
    settings = resolve_cross_encoder_settings(cfg)
    if not settings.model:
        raise ValueError(
            "RERANK_CROSS_ENCODER_MODEL is not set; score_and_blend requires a model."
        )
    documents = [_chunk_text(node)[: settings.doc_chars] for node in nodes]
    encoder = get_cross_encoder(settings.model, settings.device)
    raw = encoder.rerank(query, documents, batch_size=settings.batch)
    raw_scores = [] if raw is None else list(raw)
    if len(raw_scores) != len(nodes):
        log_warn(
            f"Cross-encoder returned {len(raw_scores)} scores for {len(nodes)} chunks; "
            "missing scores keep the fused score"
        )

    from llama_index.core.schema import NodeWithScore

    blended: List[Any] = []
    for index, node in enumerate(nodes):
        fused = _fused_score(node)
        ce_value = _ce_score(raw_scores[index]) if index < len(raw_scores) else None
        if ce_value is None:
            score = fused
        else:
            score = settings.weight * sigmoid(ce_value) + (1.0 - settings.weight) * fused
        inner = getattr(node, "node", node)
        blended.append(NodeWithScore(node=inner, score=score))
    blended.sort(
        key=lambda item: item.score if item.score is not None else float("-inf"),
        reverse=True,
    )
    return blended


class QueryRank:
    """Fused-pool size and the post-merge rank step for one query."""

    def __init__(
        self,
        cfg: Any,
        query: str,
        top_k: int,
        profiles: Any,
        base_fetch_k: int,
        fetch_k: int,
        enabled: bool,
    ) -> None:
        self.cfg = cfg
        self.query = query
        self.top_k = top_k
        self.profiles = profiles
        self.base_fetch_k = base_fetch_k
        self.fetch_k = fetch_k
        self.enabled = enabled

    def finish(self, nodes: list, *, verbose: bool = False) -> list:
        """Blend (when enabled) then ``rerank_results``.

        When the stage is off this is the same ``rerank_results`` call the
        query path made before the cross-encoder existed: same nodes, same
        ``desired_top_k``, ``verbose``, profiles and config options.
        """
        ranked = nodes
        if self.enabled:
            ranked = score_and_blend(nodes, self.query, self.cfg)
        from shared.reranker import rerank_options_for_config, rerank_results

        return rerank_results(
            ranked,
            self.query,
            desired_top_k=self.top_k,
            verbose=verbose,
            profiles=self.profiles,
            options=rerank_options_for_config(self.cfg),
        )


def begin_query_rank(cfg: Any, query: str, top_k: int, profiles: Any = None) -> QueryRank:
    """Shared entry for the validation runner and the MCP search tool.

    ``fetch_k`` is ``get_retrieval_top_k`` when the stage is off. When a
    model is set it is ``max(that, RERANK_CROSS_ENCODER_POOL)``, so an
    overview over-fetch is never shrunk. Pass ``fetch_k`` to retrieval as
    the fused size (``hybrid_top_k``). Per-leg prefetch stays
    ``HYBRID_PREFETCH_K``.
    """
    settings = resolve_cross_encoder_settings(cfg)
    from shared.reranker import get_retrieval_top_k

    base_fetch_k = get_retrieval_top_k(query, top_k, profiles)
    if settings.model:
        fetch_k = max(base_fetch_k, settings.pool)
    else:
        fetch_k = base_fetch_k
    return QueryRank(
        cfg,
        query,
        top_k,
        profiles,
        base_fetch_k,
        fetch_k,
        enabled=settings.model is not None,
    )
