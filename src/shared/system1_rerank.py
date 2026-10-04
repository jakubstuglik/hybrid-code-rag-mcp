"""Replace the numeric reranker with a System1 decision service.

When ``SYSTEM1_MODE`` is ``off`` the numeric reranker runs. When it is
``gpu``, ``cpu``, or ``remote`` and the service answers in time, the
numeric score adjustments are not applied. A failed or late call falls
back to ``rerank_results``.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import ModuleType
from typing import Any, Optional

from shared.log import log, log_warn

_OFF = {"", "off", "disabled", "false", "0", "none"}

_DEFAULT_INSTRUCTIONS = (
    "Is this chunk the defining source for the query, rather than a passing mention?"
)
_DEFAULT_TRUE = (
    "The chunk declares, implements, or is the overview of the symbol or behavior asked about."
)
_DEFAULT_FALSE = (
    "The symbol only appears as a parameter, a type, a call, or a name repeated in documentation."
)


def system1_mode(cfg: ModuleType) -> str:
    """Return ``off``, ``gpu``, ``cpu``, or ``remote``."""
    raw = str(getattr(cfg, "SYSTEM1_MODE", "off")).strip().lower()
    if raw in _OFF:
        return "off"
    if raw in {"gpu", "cuda", "nvidia"}:
        return "gpu"
    if raw == "cpu":
        return "cpu"
    if raw in {"remote", "url"}:
        return "remote"
    log_warn(f"Unknown SYSTEM1_MODE {raw!r}; numeric reranker will be used")
    return "off"


def system1_base_url(cfg: ModuleType) -> Optional[str]:
    """Base URL with no trailing slash, or None when the mode is off."""
    if system1_mode(cfg) == "off":
        return None
    explicit = getattr(cfg, "SYSTEM1_URL", None)
    if explicit:
        return str(explicit).rstrip("/")
    port = int(getattr(cfg, "SYSTEM1_PORT", 8095))
    return f"http://127.0.0.1:{port}"


def system1_model_id(cfg: ModuleType) -> str:
    """Hugging Face id or server model name.

    Basal 1.5 is not published. The fallback is the public basal-1.0 1.5B
    checkpoint. A project config sets ``SYSTEM1_MODEL`` to the checkpoint
    that should actually be served.
    """
    return str(getattr(cfg, "SYSTEM1_MODEL", "Remek/basal-1.0-1.5B"))


def _meta(node: Any) -> dict:
    inner = getattr(node, "node", node)
    meta = getattr(inner, "metadata", None) or {}
    return meta if isinstance(meta, dict) else {}


def _text(node: Any, limit: int) -> str:
    inner = getattr(node, "node", node)
    getter = getattr(inner, "get_content", None)
    content = getter() if callable(getter) else getattr(inner, "text", "")
    return (content or "")[:limit]


def build_system1_body(query: str, node: Any, cfg: ModuleType) -> dict:
    """One pointwise Noul. The hybrid score is not included."""
    meta = _meta(node)
    limit = int(getattr(cfg, "SYSTEM1_CHUNK_CHARS", 1200))
    instructions = str(getattr(cfg, "SYSTEM1_NOUL_INSTRUCTIONS", _DEFAULT_INSTRUCTIONS))
    return {
        "model": system1_model_id(cfg),
        "state": {
            "query": query,
            "file": meta.get("file_path") or meta.get("file_name") or "",
            "node_type": meta.get("node_type") or meta.get("type") or "",
            "text": _text(node, limit),
        },
        "questions": {
            "defines": {
                "type": "noul",
                "instructions": instructions,
                "criteria": {
                    "true": _DEFAULT_TRUE,
                    "false": _DEFAULT_FALSE,
                },
            }
        },
    }


def noul_from_response(payload: dict) -> Optional[float]:
    """Read ``answers.defines.noul``. Return None if the body is unusable."""
    answers = payload.get("answers") if isinstance(payload, dict) else None
    if not isinstance(answers, dict):
        return None
    defines = answers.get("defines")
    if not isinstance(defines, dict) or "noul" not in defines:
        return None
    try:
        return float(defines["noul"])
    except (TypeError, ValueError):
        return None


def order_by_noul(nodes: list, scores: list[float], top_k: int) -> list:
    """Sort by decision probability. Ties keep the hybrid retrieval order."""
    ranked = sorted(enumerate(nodes), key=lambda pair: (-scores[pair[0]], pair[0]))
    ordered = [node for _, node in ranked]
    if top_k and top_k > 0:
        return ordered[:top_k]
    return ordered


def _post_json(url: str, body: dict, timeout: float) -> dict:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("system1 response is not an object")
    return parsed


def score_nodes(nodes: list, query: str, cfg: ModuleType) -> Optional[list[float]]:
    """Score every candidate. None if any call fails, so the caller can fall back."""
    base = system1_base_url(cfg)
    if not base or not nodes:
        return None
    endpoint = base + "/v1/systemone"
    per_call = float(getattr(cfg, "SYSTEM1_TIMEOUT_S", 1.5))
    # The cap is how many retrieved chunks get a decision. Workers is how
    # many of those calls are in flight. They are separate so an over-fetched
    # pool can be scored without opening one request per chunk at once.
    cap = int(getattr(cfg, "SYSTEM1_MAX_CANDIDATES", 12))
    capped = nodes[: max(0, cap)]
    if not capped:
        return None
    workers = max(1, min(len(capped), int(getattr(cfg, "SYSTEM1_WORKERS", 4))))
    scores: list[Optional[float]] = [None] * len(capped)

    def one(index: int) -> tuple[int, Optional[float]]:
        body = build_system1_body(query, capped[index], cfg)
        try:
            payload = _post_json(endpoint, body, per_call)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            log_warn(f"System1 candidate {index} failed: {exc}")
            return index, None
        return index, noul_from_response(payload)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(one, i) for i in range(len(capped))]
        for future in as_completed(futures):
            index, score = future.result()
            scores[index] = score
    if any(score is None for score in scores):
        return None
    return [float(score) for score in scores]


def apply_rerank(nodes: list, query: str, top_k: int, cfg: ModuleType) -> list:
    """Order nodes with System1, or with the numeric reranker when it is off or down."""
    from shared.reranker import rerank_results

    mode = system1_mode(cfg)
    if mode == "off" or not nodes:
        return rerank_results(nodes, query, desired_top_k=top_k, verbose=False)
    limit = int(getattr(cfg, "SYSTEM1_MAX_CANDIDATES", 12))
    pool = nodes[:limit]
    scores = score_nodes(pool, query, cfg)
    if scores is None:
        log_warn("System1 rerank unavailable; using the numeric reranker")
        return rerank_results(nodes, query, desired_top_k=top_k, verbose=False)
    log(f"[system1] mode={mode} model={system1_model_id(cfg)} scored={len(scores)}")
    return order_by_noul(pool, scores, top_k)
