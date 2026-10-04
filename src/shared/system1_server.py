"""Start a local basal-serve for GPU or CPU, or check a remote URL.

``SYSTEM1_MODE=off`` does nothing. A failed start does not stop the MCP
server; search falls back to the numeric reranker.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from types import ModuleType
from typing import Optional

from shared.log import log, log_warn
from shared.system1_rerank import system1_base_url, system1_mode, system1_model_id

_proc: Optional[subprocess.Popen] = None


def container_name(cfg: ModuleType) -> str:
    """Docker name derived from the model id."""
    explicit = getattr(cfg, "SYSTEM1_DOCKER_CONTAINER", None)
    if explicit:
        return str(explicit)
    slug = system1_model_id(cfg).replace("/", "-").replace(".", "-")
    return f"system1-{slug}"[:60]


def gpu_index(cfg: ModuleType) -> Optional[str]:
    """Physical GPU index from ``SYSTEM1_GPU``, or None for CPU.

    ``auto`` picks the GPU with the most free VRAM. A specific index
    (``"0"``, ``"1"``, ...) is used as given. This never reads ``TEI_GPU``.
    """
    raw = str(getattr(cfg, "SYSTEM1_GPU", "auto")).strip().lower()
    if raw == "cpu":
        return None
    if raw not in {"", "auto"}:
        return raw
    from shared.docker_utils import _detect_available_gpus, _pick_best_gpu

    gpus = _detect_available_gpus()
    if not gpus:
        return None
    return str(_pick_best_gpu(gpus)["index"])


def basal_serve_mode(cfg: ModuleType) -> str:
    """Basal ``--mode`` value.

    ``SYSTEM1_SERVE_MODE`` wins when set. Otherwise GPU uses ``fast``
    (bf16, compiled) and CPU uses ``eager``. ``fast`` needs Triton.
    A host without it sets ``fast-nocompile``, which is the same bf16
    path without ``torch.compile``.
    """
    explicit = getattr(cfg, "SYSTEM1_SERVE_MODE", None)
    if explicit:
        return str(explicit)
    return "fast" if system1_mode(cfg) == "gpu" else "eager"


def basal_serve_argv(cfg: ModuleType) -> list[str]:
    """Command that serves ``/v1/systemone``."""
    binary = str(getattr(cfg, "SYSTEM1_BIN", "basal-serve"))
    port = str(int(getattr(cfg, "SYSTEM1_PORT", 8095)))
    return [
        binary,
        "--model",
        system1_model_id(cfg),
        "--mode",
        basal_serve_mode(cfg),
        "--host",
        "0.0.0.0",
        "--port",
        port,
    ]


def docker_run_args(cfg: ModuleType) -> list[str]:
    """``docker run`` arguments, not including the ``docker`` executable."""
    image = str(getattr(cfg, "SYSTEM1_DOCKER_IMAGE", "") or "")
    port = int(getattr(cfg, "SYSTEM1_PORT", 8095))
    name = container_name(cfg)
    args = [
        "run",
        "-d",
        "--name",
        name,
        "--restart",
        "unless-stopped",
        "-p",
        f"127.0.0.1:{port}:{port}",
    ]
    # On Windows Docker Desktop, --gpus device=N is not enough: the
    # container still sees every GPU. CUDA_VISIBLE_DEVICES pins the one
    # named by SYSTEM1_GPU. CPU mode sets the variable empty.
    if system1_mode(cfg) == "gpu":
        index = gpu_index(cfg)
        if index is not None:
            args.extend(
                ["--gpus", f"device={index}", "-e", f"CUDA_VISIBLE_DEVICES={index}"]
            )
    else:
        args.extend(["-e", "CUDA_VISIBLE_DEVICES="])
    cache = getattr(cfg, "SYSTEM1_MODEL_DIR", None)
    if cache:
        host = str(cache).replace("\\", "/")
        args.extend(["-v", f"{host}:/root/.cache/huggingface"])
    args.append(image)
    args.extend(basal_serve_argv(cfg)[1:])
    return args


def _ready(url: str, timeout: float = 3.0) -> bool:
    """True when /health answers, or a one-question /v1/systemone call does."""
    import json
    import urllib.request

    try:
        with urllib.request.urlopen(url + "/health", timeout=timeout) as response:
            if response.status == 200:
                return True
    except Exception:
        pass
    body = json.dumps(
        {
            "state": "ping",
            "questions": {"ok": {"type": "noul", "instructions": "Is this a ping?"}},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url + "/v1/systemone",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def ensure_system1_running(cfg: ModuleType) -> bool:
    """Return True when a decision server is reachable. Never raises."""
    global _proc
    mode = system1_mode(cfg)
    if mode == "off":
        return True
    base = system1_base_url(cfg)
    if not base:
        log_warn("SYSTEM1_MODE is set but no URL could be derived")
        return False
    if _ready(base):
        log(f"System1 already reachable at {base}")
        return True
    if mode == "remote" or not getattr(cfg, "SYSTEM1_MANAGE_DOCKER", True):
        log_warn(f"System1 at {base} is not reachable; numeric reranker will be used")
        return False

    image = getattr(cfg, "SYSTEM1_DOCKER_IMAGE", None)
    if image:
        from shared.docker_utils import (
            _container_exists,
            _container_running,
            _run_docker,
            _start_container,
        )

        name = container_name(cfg)
        try:
            if _container_running(name):
                pass
            elif _container_exists(name):
                _start_container(name)
            else:
                log(f"Creating System1 container {name}")
                _run_docker(docker_run_args(cfg))
        except (OSError, subprocess.CalledProcessError) as exc:
            log_warn(f"System1 Docker start failed: {exc}")
            return False
        for _ in range(60):
            if _ready(base, timeout=5.0):
                log(f"System1 ready at {base}")
                return True
            import time

            time.sleep(5)
        log_warn(f"System1 container did not become ready at {base}")
        return False

    binary = str(getattr(cfg, "SYSTEM1_BIN", "basal-serve"))
    if shutil.which(binary) is None and not os.path.isfile(binary):
        log_warn(
            f"{binary} is not on PATH and SYSTEM1_DOCKER_IMAGE is unset. "
            f"Install basal-serve or set SYSTEM1_URL to a running server."
        )
        return False
    env = os.environ.copy()
    if mode == "gpu":
        env["CUDA_VISIBLE_DEVICES"] = gpu_index(cfg) or ""
    else:
        env["CUDA_VISIBLE_DEVICES"] = ""
    log(f"Starting {binary} ({mode}) on {base}")
    _proc = subprocess.Popen(
        basal_serve_argv(cfg),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(12):
        if _ready(base, timeout=5.0):
            return True
        import time

        time.sleep(5)
    return False
