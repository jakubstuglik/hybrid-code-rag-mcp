"""Docker container management for QDRANT_MODE='local'.

Provides ``ensure_qdrant_running()`` which checks if the Qdrant Docker
container exists, creates or starts it if needed, and waits for the health
endpoint.  Used by index_rag.py and rag_mcp.py before connecting to Qdrant.

Container naming convention:
    ``QDRANT_DOCKER_CONTAINER`` config setting, or auto-derived as
    ``qdrant-{COLLECTION_NAME}`` (e.g. ``qdrant-informica_rag``).

Volume mount:
    ``QDRANT_DOCKER_VOLUME`` config setting, or auto-derived as
    ``{BASE_PATH}/{MODEL_PATH}``.
"""

from __future__ import annotations

import os
import pwd
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
        try:
            import pwd

            user_info = pwd.getpwuid(os.getuid())
            extra_args.extend(["--user", f"{user_info.pw_uid}:{user_info.pw_gid}"])

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


def _wait_for_health(
    host: str,
    port: int,
    max_retries: int = HEALTH_CHECK_MAX_RETRIES,
    interval: float = HEALTH_CHECK_INTERVAL_S,
) -> bool:
    """Wait for Qdrant health endpoint to respond.

    Tries ``http://{host}:{port}/healthz`` up to ``max_retries`` times.
    Uses urllib to avoid requiring the ``requests`` package.

    Args:
        host: Qdrant host (usually "localhost").
        port: Qdrant port.
        max_retries: Maximum number of attempts.
        interval: Seconds between attempts.

    Returns:
        True if healthy, False if timed out.
    """
    import urllib.request
    import urllib.error

    url = f"http://{host}:{port}/healthz"
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
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
    if _wait_for_health(host, port):
        log(f"{prefix}Qdrant ready on {host}:{port}")
        return True
    else:
        log_error(
            f"{prefix}Qdrant not healthy after {HEALTH_CHECK_MAX_RETRIES} attempts. "
            f"Check: docker logs {container_name}"
        )
        return False
