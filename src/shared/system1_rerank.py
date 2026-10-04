"""Replace the numeric reranker with a System1 decision service.

When ``SYSTEM1_MODE`` is ``off`` the numeric reranker runs. When it is
``gpu``, ``cpu``, or ``remote`` and the service answers in time, the
numeric score adjustments are not applied. A failed or late call falls
back to ``rerank_results``.
"""

from __future__ import annotations

import json
import os
import time
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
_OVERVIEW_INSTRUCTIONS = (
    "Is this the chunk an engineer should open first to answer the query?"
)
_OVERVIEW_TRUE = (
    "It is the overview, summary, header, or form or report definition of the "
    "thing asked about, in the unit that owns it."
)
_OVERVIEW_FALSE = (
    "It is a method body, a call site, an import list, a comment, or a similar name "
    "in another unit."
)
_UNIT_INSTRUCTIONS = "Is this chunk from the unit that owns the thing named in the query?"
_UNIT_TRUE = "This file defines that class, form, report, or routine."
_UNIT_FALSE = "Another unit, or the name only appears in passing."


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


def system1_strategy(cfg: ModuleType) -> str:
    """``replace`` sorts by one Noul. ``blend`` keeps the numeric score and adds a nudge."""
    raw = str(getattr(cfg, "SYSTEM1_STRATEGY", "replace")).strip().lower()
    return raw if raw in {"replace", "blend"} else "replace"


def _state(query: str, node: Any, cfg: ModuleType) -> dict:
    meta = _meta(node)
    limit = int(getattr(cfg, "SYSTEM1_CHUNK_CHARS", 1200))
    return {
        "query": query,
        "file": meta.get("file_path") or meta.get("file_name") or "",
        "node_type": meta.get("node_type") or meta.get("type") or "",
        "text": _text(node, limit),
    }


def _noul_question(instructions: str, yes: str, no: str) -> dict:
    return {
        "type": "noul",
        "instructions": instructions,
        "criteria": {"true": yes, "false": no},
    }


def build_system1_body(query: str, node: Any, cfg: ModuleType) -> dict:
    """Pointwise Noul questions. The hybrid score is not included.

    ``replace`` asks whether the chunk is the defining source.
    ``blend`` asks whether to open it first, and whether this unit owns the name.
    """
    if system1_strategy(cfg) == "blend":
        questions = {
            "overview": _noul_question(_OVERVIEW_INSTRUCTIONS, _OVERVIEW_TRUE, _OVERVIEW_FALSE),
            "unit": _noul_question(_UNIT_INSTRUCTIONS, _UNIT_TRUE, _UNIT_FALSE),
        }
    else:
        instructions = str(getattr(cfg, "SYSTEM1_NOUL_INSTRUCTIONS", _DEFAULT_INSTRUCTIONS))
        questions = {
            "defines": _noul_question(instructions, _DEFAULT_TRUE, _DEFAULT_FALSE),
        }
    return {
        "model": system1_model_id(cfg),
        "state": _state(query, node, cfg),
        "questions": questions,
    }


def blend_nudge(overview: float, unit: float, cfg: ModuleType) -> float:
    """How far System1 may move a numeric score. Centered on 0.5 so a coin flip is zero."""
    overview_weight = float(getattr(cfg, "SYSTEM1_BLEND_OVERVIEW", 0.20))
    unit_weight = float(getattr(cfg, "SYSTEM1_BLEND_UNIT", 0.45))
    return overview_weight * (overview - 0.5) + unit_weight * (unit - 0.5)


def noul_from_response(payload: dict, name: str = "defines") -> Optional[float]:
    """Read ``answers.<name>.noul``. Return None if the body is unusable."""
    answers = payload.get("answers") if isinstance(payload, dict) else None
    if not isinstance(answers, dict):
        return None
    item = answers.get(name)
    if not isinstance(item, dict) or "noul" not in item:
        return None
    try:
        return float(item["noul"])
    except (TypeError, ValueError):
        return None


def order_by_noul(nodes: list, scores: list[float], top_k: int) -> list:
    """Sort by decision probability. Ties keep the hybrid retrieval order."""
    ranked = sorted(enumerate(nodes), key=lambda pair: (-scores[pair[0]], pair[0]))
    ordered = [node for _, node in ranked]
    if top_k and top_k > 0:
        return ordered[:top_k]
    return ordered


def _request_headers(cfg: ModuleType) -> dict[str, str]:
    """JSON headers, plus a bearer token when one is configured.

    The token is read from ``SYSTEM1_API_KEY`` on the config or from the
    same environment variable. It is not written to logs.
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    key = getattr(cfg, "SYSTEM1_API_KEY", None) or os.environ.get("SYSTEM1_API_KEY")
    if key:
        headers["Authorization"] = "Bearer " + str(key).strip()
    return headers


def _post_json(url: str, body: dict, timeout: float, headers: Optional[dict] = None) -> dict:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers or {"Content-Type": "application/json", "Accept": "application/json"},
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
    wall_ms: list[float] = []
    server_ms: list[float] = []

    def one(index: int) -> tuple[int, Optional[float], float, Optional[float]]:
        body = build_system1_body(query, capped[index], cfg)
        started = time.perf_counter()
        try:
            payload = _post_json(endpoint, body, per_call, _request_headers(cfg))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            log_warn(f"System1 candidate {index} failed: {exc}")
            return index, None, (time.perf_counter() - started) * 1000.0, None
        elapsed = (time.perf_counter() - started) * 1000.0
        usage = payload.get("usage") if isinstance(payload, dict) else None
        reported = usage.get("latency_ms") if isinstance(usage, dict) else None
        try:
            reported_ms = float(reported) if reported is not None else None
        except (TypeError, ValueError):
            reported_ms = None
        return index, noul_from_response(payload), elapsed, reported_ms

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(one, i) for i in range(len(capped))]
        for future in as_completed(futures):
            index, score, elapsed, reported = future.result()
            scores[index] = score
            wall_ms.append(elapsed)
            if reported is not None:
                server_ms.append(reported)
    if any(score is None for score in scores):
        return None
    _log_system1_timing(cfg, len(scores), wall_ms, server_ms)
    return [float(score) for score in scores]


def _percentile(values: list[float], pct: float) -> float:
    """Nearest-rank percentile. ``values`` must be non-empty."""
    ordered = sorted(values)
    rank = min(len(ordered) - 1, max(0, int(round((pct / 100.0) * (len(ordered) - 1)))))
    return ordered[rank]


def _log_system1_timing(
    cfg: ModuleType,
    scored: int,
    wall_ms: list[float],
    server_ms: list[float],
) -> None:
    """Log client wait and the server's own latency_ms for one query."""
    wall = (
        f"wall_p50={_percentile(wall_ms, 50):.0f} "
        f"wall_p95={_percentile(wall_ms, 95):.0f} "
        f"wall_max={max(wall_ms):.0f}"
        if wall_ms
        else "wall=none"
    )
    server = (
        f"server_p50={_percentile(server_ms, 50):.0f} "
        f"server_p95={_percentile(server_ms, 95):.0f} "
        f"server_max={max(server_ms):.0f}"
        if server_ms
        else "server=none"
    )
    log(
        f"[system1] mode={system1_mode(cfg)} model={system1_model_id(cfg)} "
        f"scored={scored} {wall} {server}"
    )


def score_blend_nodes(
    nodes: list, query: str, cfg: ModuleType
) -> Optional[list[tuple[float, float]]]:
    """One request per chunk. Each answer is (overview Noul, unit Noul)."""
    if not nodes:
        return []
    endpoint = system1_base_url(cfg)
    if not endpoint:
        return None
    endpoint = endpoint + "/v1/systemone"
    per_call = float(getattr(cfg, "SYSTEM1_TIMEOUT_S", 1.5))
    workers = max(1, min(len(nodes), int(getattr(cfg, "SYSTEM1_WORKERS", 4))))
    pairs: list[Optional[tuple[float, float]]] = [None] * len(nodes)

    def one(index: int) -> tuple[int, Optional[tuple[float, float]], float, Optional[float]]:
        body = build_system1_body(query, nodes[index], cfg)
        started = time.perf_counter()
        try:
            payload = _post_json(endpoint, body, per_call, _request_headers(cfg))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            log_warn(f"System1 candidate {index} failed: {exc}")
            return index, None, (time.perf_counter() - started) * 1000.0, None
        elapsed = (time.perf_counter() - started) * 1000.0
        overview = noul_from_response(payload, "overview")
        unit = noul_from_response(payload, "unit")
        usage = payload.get("usage") if isinstance(payload, dict) else None
        reported = usage.get("latency_ms") if isinstance(usage, dict) else None
        try:
            reported_ms = float(reported) if reported is not None else None
        except (TypeError, ValueError):
            reported_ms = None
        if overview is None or unit is None:
            return index, None, elapsed, reported_ms
        return index, (overview, unit), elapsed, reported_ms

    wall_ms: list[float] = []
    server_ms: list[float] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(one, i) for i in range(len(nodes))]
        for future in as_completed(futures):
            index, pair, elapsed, reported = future.result()
            pairs[index] = pair
            wall_ms.append(elapsed)
            if reported is not None:
                server_ms.append(reported)
    if any(pair is None for pair in pairs):
        return None
    _log_system1_timing(cfg, len(pairs), wall_ms, server_ms)
    return [(float(pair[0]), float(pair[1])) for pair in pairs]  # type: ignore[index]


def _numeric_adjusted(nodes: list, query: str) -> tuple[list[float], bool]:
    """Same adjusted scores the numeric reranker sorts by. Second value is overview."""
    from shared.reranker import (
        _compute_rerank_score,
        extract_target_identifiers,
        is_dfm_query,
        is_dproj_query,
        is_fr3_query,
        is_hbm_query,
        is_jrxml_query,
        is_overview_query,
    )

    overview = is_overview_query(query)
    targets = extract_target_identifiers(query) if overview else []
    dfm_mode = is_dfm_query(query) if overview else False
    fr3_mode = is_fr3_query(query) if overview else False
    dproj_mode = is_dproj_query(query) if overview else False
    hbm_mode = is_hbm_query(query) if overview else False
    jrxml_mode = is_jrxml_query(query) if overview else False
    adjusted: list[float] = []
    for node in nodes:
        inner = getattr(node, "node", node)
        meta = getattr(inner, "metadata", None) or {}
        if not isinstance(meta, dict):
            meta = {}
        node_type = str(meta.get("node_type", meta.get("type", "text")))
        original = getattr(node, "score", 0.0) or 0.0
        adjusted.append(
            _compute_rerank_score(
                float(original),
                node_type,
                meta,
                overview,
                dfm_mode,
                fr3_mode,
                dproj_mode,
                hbm_mode,
                jrxml_mode,
                targets,
            )
        )
    return adjusted, overview


def _blend_order(nodes: list, query: str, top_k: int, cfg: ModuleType) -> Optional[list]:
    """Numeric score plus a System1 nudge on the numeric front of the pool."""
    from shared.reranker import rerank_results

    numeric, overview = _numeric_adjusted(nodes, query)
    if not overview:
        return rerank_results(nodes, query, desired_top_k=top_k, verbose=False)
    order = sorted(range(len(nodes)), key=lambda index: (-numeric[index], index))
    pool_size = int(getattr(cfg, "SYSTEM1_BLEND_POOL", 24))
    chosen = order[: max(0, min(len(order), pool_size))]
    pairs = score_blend_nodes([nodes[index] for index in chosen], query, cfg)
    if pairs is None:
        return None
    keyed = []
    for local, global_index in enumerate(chosen):
        overview_noul, unit_noul = pairs[local]
        keyed.append((numeric[global_index] + blend_nudge(overview_noul, unit_noul, cfg), global_index))
    for global_index in order[len(chosen) :]:
        keyed.append((numeric[global_index], global_index))
    keyed.sort(key=lambda item: (-item[0], item[1]))
    ordered = [nodes[index] for _, index in keyed]
    if top_k and top_k > 0:
        return ordered[:top_k]
    return ordered


def apply_rerank(nodes: list, query: str, top_k: int, cfg: ModuleType) -> list:
    """Order nodes with System1, or with the numeric reranker when it is off or down."""
    from shared.reranker import rerank_results

    mode = system1_mode(cfg)
    if mode == "off" or not nodes:
        return rerank_results(nodes, query, desired_top_k=top_k, verbose=False)
    if system1_strategy(cfg) == "blend":
        blended = _blend_order(nodes, query, top_k, cfg)
        if blended is None:
            log_warn("System1 rerank unavailable; using the numeric reranker")
            return rerank_results(nodes, query, desired_top_k=top_k, verbose=False)
        return blended
    limit = int(getattr(cfg, "SYSTEM1_MAX_CANDIDATES", 12))
    pool = nodes[:limit]
    scores = score_nodes(pool, query, cfg)
    if scores is None:
        log_warn("System1 rerank unavailable; using the numeric reranker")
        return rerank_results(nodes, query, desired_top_k=top_k, verbose=False)
    return order_by_noul(pool, scores, top_k)
