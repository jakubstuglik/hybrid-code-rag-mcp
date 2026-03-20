"""Docker container management for Qdrant and TEI (Text Embeddings Inference).

Provides ``ensure_qdrant_running()`` and ``ensure_tei_running()`` which check
if Docker containers exist, create or start them if needed, and wait for health
endpoints.  Used by index_rag.py and rag_mcp.py at startup.

Qdrant container naming:
    ``QDRANT_DOCKER_CONTAINER`` config setting, or auto-derived as
    ``qdrant-{COLLECTION_NAME}`` (e.g. ``qdrant-informica_rag``).

TEI container naming:
    Auto-derived as ``tei-{COLLECTION_NAME}`` (e.g. ``tei-informica_rag``).

Volume mounts:
    Qdrant: ``{BASE_PATH}/{MODEL_PATH}``
    TEI model cache: ``TEI_MODEL_DIR`` or ``{BASE_PATH}/tei_model_cache``
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from types import ModuleType
from typing import Optional

from shared.log import log, log_error, log_warn

# Qdrant Docker image — always pull latest
QDRANT_IMAGE = "docker.io/qdrant/qdrant:latest"

# Health check settings
HEALTH_CHECK_MAX_RETRIES = 30
HEALTH_CHECK_INTERVAL_S = 1.0


def get_container_name(cfg: ModuleType) -> str:
    """Derive the Docker container name from config.

    Uses ``QDRANT_DOCKER_CONTAINER`` if set, otherwise
    ``qdrant-{COLLECTION_NAME}``.
    """
    explicit = getattr(cfg, "QDRANT_DOCKER_CONTAINER", None)
    if explicit:
        return explicit
    collection = getattr(cfg, "COLLECTION_NAME", "default_rag")
    return f"qdrant-{collection}"


def get_volume_path(cfg: ModuleType) -> str:
    """Derive the Docker volume mount path from config.

    Uses ``QDRANT_DOCKER_VOLUME`` if set, otherwise
    ``{BASE_PATH}/{MODEL_PATH}``.  The path is resolved to an absolute
    path with forward slashes (required by Docker on Windows).
    """
    explicit = getattr(cfg, "QDRANT_DOCKER_VOLUME", None)
    if explicit:
        return str(Path(explicit).resolve()).replace("\\", "/")

    base_path = getattr(cfg, "BASE_PATH", "qdrant")
    model_path = getattr(cfg, "MODEL_PATH", "default_index")
    return str(Path(base_path, model_path).resolve()).replace("\\", "/")


def _run_docker(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a docker command, capturing output.

    Args:
        args: Command arguments after ``docker``.
        check: Raise CalledProcessError on non-zero exit.

    Returns:
        CompletedProcess with captured stdout/stderr.
    """
    cmd = ["docker"] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=check,
        timeout=60,
    )


def _container_exists(container_name: str) -> bool:
    """Check if a Docker container exists (running or stopped)."""
    result = _run_docker(
        ["inspect", "--format", "{{.State.Status}}", container_name],
        check=False,
    )
    return result.returncode == 0


def _container_running(container_name: str) -> bool:
    """Check if a Docker container is currently running."""
    result = _run_docker(
        ["inspect", "--format", "{{.State.Status}}", container_name],
        check=False,
    )
    if result.returncode != 0:
        return False
    return result.stdout.strip() == "running"


def _create_container(
    container_name: str,
    host_port: int,
    volume_path: str,
) -> None:
    """Create and start a new Qdrant Docker container.

    Args:
        container_name: Name for the container.
        host_port: Host port to map to container's 6333.
        volume_path: Host path to mount as Qdrant storage.
    """
    import sys
    import platform

    log(f"Creating Docker container '{container_name}'...")

    volume_arg = f"{volume_path}:/qdrant/storage"
    extra_args: list[str] = []

    if platform.system() != "Windows":
        extra_args.append("--privileged")

        try:
            selinux_enforcing = False
            try:
                with open("/sys/fs/selinux/enforce", "r") as f:
                    selinux_enforcing = f.read().strip() == "1"
            except (FileNotFoundError, PermissionError, IOError):
                pass

            if selinux_enforcing:
                volume_arg += ":Z"
        except (ImportError, AttributeError, OSError):
            pass

    _run_docker(
        [
            "run",
            "-d",
            "--name",
            container_name,
            "-p",
            f"{host_port}:6333",
            "-v",
            volume_arg,
        ]
        + extra_args
        + [QDRANT_IMAGE]
    )
    log(f"Container '{container_name}' created (port {host_port})")


def _start_container(container_name: str) -> None:
    """Start a stopped Docker container."""
    log(f"Starting Docker container '{container_name}'...")
    _run_docker(["start", container_name])
    log(f"Container '{container_name}' started")


def _wait_for_health_endpoint(
    url: str,
    max_retries: int = HEALTH_CHECK_MAX_RETRIES,
    interval: float = HEALTH_CHECK_INTERVAL_S,
    request_timeout: float = 5,
) -> bool:
    """Wait for an HTTP health endpoint to respond with 200.

    Generic health check used for both Qdrant (``/healthz``) and TEI
    (``/health``) containers.

    Args:
        url: Full URL to poll (e.g. "http://localhost:6333/healthz").
        max_retries: Maximum number of attempts.
        interval: Seconds between attempts.
        request_timeout: Timeout per HTTP request in seconds.

    Returns:
        True if healthy, False if timed out.
    """
    import urllib.request
    import urllib.error

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=request_timeout) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError, TimeoutError):
            pass
        time.sleep(interval)
    return False


def ensure_qdrant_running(
    cfg: ModuleType,
    stderr_prefix: Optional[str] = None,
) -> bool:
    """Ensure the local Qdrant Docker container is running.

    Only operates when ``QDRANT_MODE == "local"``.  For ``"remote"`` mode
    this is a no-op (returns True immediately).

    Steps for local mode:
    1. Check if the container exists and is running → done.
    2. Container exists but stopped → start it.
    3. Container doesn't exist → create it with ``docker run``.
    4. Wait for the health endpoint.

    Args:
        cfg: Merged config module (from config_loader).
        stderr_prefix: Optional prefix for log messages (e.g. "[MCP]").
            Used by rag_mcp.py where stdout is the JSON-RPC channel.

    Returns:
        True if Qdrant is ready (or mode is "remote").
        False if Docker operations failed.
    """
    mode = getattr(cfg, "QDRANT_MODE", "local")
    if mode != "local":
        return True  # Remote mode — caller handles connectivity

    prefix = f"{stderr_prefix} " if stderr_prefix else ""
    container_name = get_container_name(cfg)
    host = getattr(cfg, "QDRANT_HOST", "localhost")
    port = getattr(cfg, "QDRANT_PORT", 6333)
    volume_path = get_volume_path(cfg)

    try:
        if _container_running(container_name):
            log(f"{prefix}Qdrant container '{container_name}' is running")
        elif _container_exists(container_name):
            _start_container(container_name)
        else:
            # Ensure volume directory exists
            vol_dir = Path(volume_path)
            vol_dir.mkdir(parents=True, exist_ok=True)
            _create_container(container_name, port, volume_path)
    except subprocess.CalledProcessError as exc:
        log_error(
            f"{prefix}Docker command failed: {exc.cmd}\n"
            f"  stdout: {exc.stdout}\n"
            f"  stderr: {exc.stderr}"
        )
        return False
    except FileNotFoundError:
        log_error(
            f"{prefix}Docker is not installed or not in PATH. "
            f"Install Docker Desktop and ensure 'docker' is available."
        )
        return False
    except subprocess.TimeoutExpired:
        log_error(f"{prefix}Docker command timed out after 60 seconds.")
        return False

    # Wait for health
    log(f"{prefix}Waiting for Qdrant on {host}:{port}...")
    health_url = f"http://{host}:{port}/healthz"
    if _wait_for_health_endpoint(health_url, request_timeout=2):
        log(f"{prefix}Qdrant ready on {host}:{port}")
        return True
    else:
        log_error(
            f"{prefix}Qdrant not healthy after {HEALTH_CHECK_MAX_RETRIES} attempts. "
            f"Check: docker logs {container_name}"
        )
        return False


# ════════════════════════════════════════════════════════════════════
# TEI (Text Embeddings Inference) Docker management
# ════════════════════════════════════════════════════════════════════

# TEI Docker image patterns (latest)
TEI_IMAGE_CPU = "ghcr.io/huggingface/text-embeddings-inference:cpu-latest"
TEI_IMAGE_NVIDIA_TEMPLATE = "ghcr.io/huggingface/text-embeddings-inference:{cc}-latest"

# TEI health check settings (model loading can take 10-30s on first start)
TEI_HEALTH_CHECK_MAX_RETRIES = 60
TEI_HEALTH_CHECK_INTERVAL_S = 2.0

# Mapping of NVIDIA compute capability major.minor → TEI Docker tag prefix.
# Source: https://github.com/huggingface/text-embeddings-inference#docker-images
_NVIDIA_CC_TO_TEI_TAG = {
    "7.5": "75",  # Turing (RTX 2060-2080, T4)
    "8.0": "80",  # Ampere (A100)
    "8.6": "86",  # Ampere (RTX 3060-3090, A40)
    "8.9": "89",  # Ada Lovelace (RTX 4060-4090, L40)
    "9.0": "90",  # Hopper (H100)
}


def _detect_nvidia_compute_capability() -> Optional[str]:
    """Detect NVIDIA GPU compute capability via nvidia-smi.

    Returns:
        Compute capability string like "8.9", or None if no NVIDIA GPU
        or nvidia-smi is not available.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=compute_cap",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        # First GPU's compute capability (e.g. "8.9")
        cc = result.stdout.strip().split("\n")[0].strip()
        if cc and "." in cc:
            return cc
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        pass
    return None


def _detect_tei_image(cfg: ModuleType) -> str:
    """Auto-detect the correct TEI Docker image based on hardware.

    Checks for NVIDIA GPU first; falls back to CPU image.

    Args:
        cfg: Merged config module.

    Returns:
        Docker image string (e.g. "ghcr.io/huggingface/text-embeddings-inference:89-1.9").
    """
    explicit = getattr(cfg, "TEI_DOCKER_IMAGE", None)
    if explicit:
        return explicit

    cc = _detect_nvidia_compute_capability()
    if cc:
        # Find the best matching TEI tag for this compute capability
        tag = _NVIDIA_CC_TO_TEI_TAG.get(cc)
        if tag:
            image = TEI_IMAGE_NVIDIA_TEMPLATE.format(cc=tag)
            log(f"Detected NVIDIA GPU (CC {cc}) -> TEI image: {image}")
            return image
        else:
            # Unknown CC — try using the raw digits (e.g. "9.0" → "90")
            raw_tag = cc.replace(".", "")
            image = TEI_IMAGE_NVIDIA_TEMPLATE.format(cc=raw_tag)
            log_warn(
                f"NVIDIA compute capability {cc} not in known list. "
                f"Attempting TEI image: {image}"
            )
            return image

    log("No NVIDIA GPU detected -> using TEI CPU image")
    return TEI_IMAGE_CPU


def get_tei_container_name(cfg: ModuleType) -> str:
    """Derive the TEI Docker container name from config.

    Pattern: ``tei-{COLLECTION_NAME}``.
    """
    collection = getattr(cfg, "COLLECTION_NAME", "default_rag")
    return f"tei-{collection}"


def _get_tei_model_dir(cfg: ModuleType) -> str:
    """Get the host directory for TEI model cache.

    Uses ``TEI_MODEL_DIR`` if set, otherwise ``{BASE_PATH}/tei_model_cache``.
    Returns an absolute path with forward slashes (required by Docker on Windows).
    """
    explicit = getattr(cfg, "TEI_MODEL_DIR", None)
    if explicit:
        return str(Path(explicit).resolve()).replace("\\", "/")

    base_path = getattr(cfg, "BASE_PATH", "qdrant")
    return str(Path(base_path, "tei_model_cache").resolve()).replace("\\", "/")


def _get_tei_url(cfg: ModuleType) -> str:
    """Get the TEI server URL from config or auto-derive it.

    Returns:
        URL string like "http://localhost:8090".
    """
    explicit = getattr(cfg, "TEI_URL", None)
    if explicit:
        return explicit.rstrip("/")
    port = getattr(cfg, "TEI_DOCKER_PORT", 8090)
    return f"http://localhost:{port}"


def _resolve_hf_token(cfg: ModuleType) -> Optional[str]:
    """Resolve a HuggingFace API token for gated model access.

    Checks in order:
    1. ``TEI_HF_TOKEN`` config attribute (explicit override)
    2. ``HF_TOKEN`` environment variable
    3. Cached token file at ``~/.cache/huggingface/token``

    Returns:
        Token string, or None if no token is found.
    """
    # 1. Explicit config override
    token = getattr(cfg, "TEI_HF_TOKEN", None)
    if token:
        return token

    # 2. Environment variable
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token

    # 3. Cached token file (written by `huggingface-cli login`)
    token_file = Path.home() / ".cache" / "huggingface" / "token"
    if token_file.is_file():
        try:
            token = token_file.read_text(encoding="utf-8").strip()
            if token:
                return token
        except OSError:
            pass

    return None


def _create_tei_container(
    container_name: str,
    cfg: ModuleType,
) -> None:
    """Create and start a new TEI Docker container.

    Handles GPU passthrough (--gpus all) for NVIDIA images and mounts
    the model cache directory.

    Args:
        container_name: Name for the container.
        cfg: Merged config module.
    """
    image = _detect_tei_image(cfg)
    port = getattr(cfg, "TEI_DOCKER_PORT", 8090)
    dtype = getattr(cfg, "TEI_DTYPE", "float16")
    model_name = getattr(cfg, "MODEL_NAME", "jinaai/jina-embeddings-v2-base-code")
    model_dir = _get_tei_model_dir(cfg)
    hf_token = _resolve_hf_token(cfg)

    # TEI server-side batching parameters
    max_batch_tokens = getattr(cfg, "TEI_MAX_BATCH_TOKENS", None)
    if max_batch_tokens is None:
        # Auto-derive from our client-side token budget so TEI doesn't
        # split batches we already sized to fit.
        max_batch_tokens = getattr(cfg, "EMBED_BATCH_MAX_TOKENS", None)
    tokenization_workers = getattr(cfg, "TEI_TOKENIZATION_WORKERS", None)

    log(f"Creating TEI container '{container_name}' (image: {image})...")

    # Ensure model cache directory exists
    Path(model_dir).mkdir(parents=True, exist_ok=True)

    # Build docker run command
    docker_args = [
        "run",
        "-d",
        "--name",
        container_name,
        "-p",
        f"{port}:80",
        "-v",
        f"{model_dir}:/data",
    ]

    # Add GPU passthrough for NVIDIA images (not CPU)
    is_nvidia = "cpu" not in image.split(":")[-1]
    if is_nvidia:
        docker_args.extend(["--gpus", "all"])

    # The Docker image is the last arg before TEI CLI args
    docker_args.append(image)

    # TEI CLI arguments (after the image)
    docker_args.extend(
        [
            "--model-id",
            model_name,
            "--dtype",
            dtype,
            "--auto-truncate",
        ]
    )

    # Server-side batching parameters
    if max_batch_tokens is not None:
        docker_args.extend(["--max-batch-tokens", str(int(max_batch_tokens))])
    if tokenization_workers is not None:
        docker_args.extend(["--tokenization-workers", str(int(tokenization_workers))])

    # Pass HF token for gated models (e.g. google/embeddinggemma-300m)
    if hf_token:
        docker_args.extend(["--hf-token", hf_token])

    _run_docker(docker_args)
    extras = []
    if max_batch_tokens is not None:
        extras.append(f"max_batch_tokens={max_batch_tokens}")
    if tokenization_workers is not None:
        extras.append(f"tokenization_workers={tokenization_workers}")
    extra_str = f", {', '.join(extras)}" if extras else ""
    log(
        f"TEI container '{container_name}' created (port {port}, dtype={dtype}{extra_str})"
    )


def ensure_tei_running(
    cfg: ModuleType,
    stderr_prefix: Optional[str] = None,
) -> bool:
    """Ensure the TEI Docker container is running and healthy.

    Only operates when ``USE_TEI == True``.  When TEI is disabled,
    returns True immediately (no-op).

    Steps:
    1. Check if the container exists and is running → health check.
    2. Container exists but stopped → start it → health check.
    3. Container doesn't exist → create it → health check.

    Args:
        cfg: Merged config module (from config_loader).
        stderr_prefix: Optional prefix for log messages (e.g. "[MCP]").

    Returns:
        True if TEI is ready (or TEI is disabled).
        False if Docker operations failed or health check timed out.
    """
    use_tei = getattr(cfg, "USE_TEI", False)
    if not use_tei:
        return True  # TEI disabled — nothing to do

    prefix = f"{stderr_prefix} " if stderr_prefix else ""
    container_name = get_tei_container_name(cfg)
    tei_url = _get_tei_url(cfg)

    try:
        if _container_running(container_name):
            log(f"{prefix}TEI container '{container_name}' is running")
        elif _container_exists(container_name):
            _start_container(container_name)
        else:
            _create_tei_container(container_name, cfg)
    except subprocess.CalledProcessError as exc:
        log_error(
            f"{prefix}Docker command failed for TEI: {exc.cmd}\n"
            f"  stdout: {exc.stdout}\n"
            f"  stderr: {exc.stderr}"
        )
        return False
    except FileNotFoundError:
        log_error(
            f"{prefix}Docker is not installed or not in PATH. "
            f"Install Docker Desktop and ensure 'docker' is available."
        )
        return False
    except subprocess.TimeoutExpired:
        log_error(f"{prefix}Docker command timed out after 60 seconds.")
        return False

    # Wait for health (TEI needs to load the model — can take 10-30s on first start)
    log(f"{prefix}Waiting for TEI on {tei_url}...")
    health_url = f"{tei_url}/health"
    if _wait_for_health_endpoint(
        health_url,
        max_retries=TEI_HEALTH_CHECK_MAX_RETRIES,
        interval=TEI_HEALTH_CHECK_INTERVAL_S,
    ):
        log(f"{prefix}TEI ready on {tei_url}")
        return True
    else:
        log_error(
            f"{prefix}TEI not healthy after {TEI_HEALTH_CHECK_MAX_RETRIES} attempts "
            f"({TEI_HEALTH_CHECK_MAX_RETRIES * TEI_HEALTH_CHECK_INTERVAL_S:.0f}s). "
            f"Check: docker logs {container_name}"
        )
        return False
