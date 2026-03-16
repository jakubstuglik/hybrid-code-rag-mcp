"""Unified Qdrant client factory.

Replaces the ad-hoc ``if QDRANT_USE_DOCKER:`` branches scattered across
index_rag.py, rag_mcp.py, migrate_keys.py and qdrant/vector_store.py with
a single function that constructs the correct QdrantClient based on
``QDRANT_MODE`` in the config.

Two modes are supported:

* ``"local"``  — HTTP client to ``localhost:{QDRANT_PORT}``.  The caller
  is expected to have called ``ensure_qdrant_running()`` beforehand (or
  started Docker manually).
* ``"remote"`` — HTTP/gRPC client to ``{QDRANT_HOST}:{QDRANT_PORT}``
  with optional API key, HTTPS, and gRPC.
"""

from __future__ import annotations

from types import ModuleType
from typing import Optional, Tuple

from shared.log import log


def get_qdrant_client(
    cfg: ModuleType,
) -> "QdrantClient":
    """Create a sync QdrantClient from config settings.

    Args:
        cfg: Merged config module (from config_loader).

    Returns:
        A connected ``QdrantClient`` instance.

    Raises:
        RuntimeError: If ``QDRANT_MODE`` is invalid.
    """
    from qdrant_client import QdrantClient

    mode = getattr(cfg, "QDRANT_MODE", "local")
    kwargs = _build_client_kwargs(cfg, mode)
    return QdrantClient(**kwargs)


def get_async_qdrant_client(
    cfg: ModuleType,
) -> "AsyncQdrantClient":
    """Create an async QdrantClient from config settings.

    Args:
        cfg: Merged config module (from config_loader).

    Returns:
        A connected ``AsyncQdrantClient`` instance.

    Raises:
        RuntimeError: If ``QDRANT_MODE`` is invalid.
    """
    from qdrant_client import AsyncQdrantClient

    mode = getattr(cfg, "QDRANT_MODE", "local")
    kwargs = _build_client_kwargs(cfg, mode)
    return AsyncQdrantClient(**kwargs)


def get_qdrant_client_pair(
    cfg: ModuleType,
) -> Tuple["QdrantClient", "AsyncQdrantClient"]:
    """Create both sync and async QdrantClient from config settings.

    Convenience wrapper used by ``get_qdrant_vector_store()`` which needs
    both client types.

    Args:
        cfg: Merged config module (from config_loader).

    Returns:
        Tuple of (sync_client, async_client).
    """
    from qdrant_client import QdrantClient, AsyncQdrantClient

    mode = getattr(cfg, "QDRANT_MODE", "local")
    kwargs = _build_client_kwargs(cfg, mode)
    return QdrantClient(**kwargs), AsyncQdrantClient(**kwargs)


def _build_client_kwargs(cfg: ModuleType, mode: str) -> dict:
    """Build kwargs dict for QdrantClient / AsyncQdrantClient.

    Args:
        cfg: Merged config module.
        mode: ``"local"`` or ``"remote"``.

    Returns:
        Dict of keyword arguments for the Qdrant client constructor.

    Raises:
        RuntimeError: If mode is not ``"local"`` or ``"remote"``.
    """
    if mode not in ("local", "remote"):
        raise RuntimeError(f"QDRANT_MODE must be 'local' or 'remote', got {mode!r}")

    host = getattr(cfg, "QDRANT_HOST", "localhost")
    port = getattr(cfg, "QDRANT_PORT", 6333)

    if mode == "local":
        # Local Docker: always HTTP to localhost
        return {"host": host, "port": port}

    # Remote mode: supports API key, HTTPS, and gRPC
    api_key = getattr(cfg, "QDRANT_API_KEY", None)
    use_https = getattr(cfg, "QDRANT_HTTPS", False)
    prefer_grpc = getattr(cfg, "QDRANT_PREFER_GRPC", False)
    grpc_port = getattr(cfg, "QDRANT_GRPC_PORT", 6334)

    kwargs: dict = {}

    if use_https:
        # HTTPS URL: qdrant-client expects url= for https connections
        kwargs["url"] = f"https://{host}:{port}"
    else:
        kwargs["host"] = host
        kwargs["port"] = port

    if api_key:
        kwargs["api_key"] = api_key

    if prefer_grpc:
        kwargs["prefer_grpc"] = True
        kwargs["grpc_port"] = grpc_port

    return kwargs


def get_qdrant_url(cfg: ModuleType) -> str:
    """Return a human-readable Qdrant connection URL for log messages.

    Examples:
        ``"localhost:6333"``
        ``"https://my-cluster.qdrant.io:6333"``
        ``"my-server:6333 (gRPC:6334)"``
    """
    mode = getattr(cfg, "QDRANT_MODE", "local")
    host = getattr(cfg, "QDRANT_HOST", "localhost")
    port = getattr(cfg, "QDRANT_PORT", 6333)

    if mode == "local":
        return f"localhost:{port}"

    use_https = getattr(cfg, "QDRANT_HTTPS", False)
    prefer_grpc = getattr(cfg, "QDRANT_PREFER_GRPC", False)
    grpc_port = getattr(cfg, "QDRANT_GRPC_PORT", 6334)

    scheme = "https" if use_https else "http"
    url = f"{scheme}://{host}:{port}"
    if prefer_grpc:
        url += f" (gRPC:{grpc_port})"
    return url
