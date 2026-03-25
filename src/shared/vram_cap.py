"""
Dynamic VRAM cap for embedding model sequence length.

The jinaai/jina-embeddings-v2-base-code model uses ALiBi (Attention with Linear
Biases) which materializes an O(N^2) bias tensor every forward pass.  On GPUs
with limited dedicated VRAM (e.g. 8 GB), the sequence length must be capped to
prevent spilling into shared (system RAM-backed) GPU memory, which is ~10x slower.

This module computes the maximum safe sequence length based on the GPU's VRAM
capacity and the model's architecture parameters.

VRAM breakdown per forward pass
--------------------------------
- Model weights:       params_millions * 1e6 * bytes_per_element / 1024^2  (MiB)
- ALiBi bias tensor:   1 * num_heads * N^2 * bytes_per_element / 1024^2    (MiB)
- KV/attention activations (approximate):
      batch_size * N * hidden_dim * num_layers * 2 * bytes_per_element / 1024^2  (MiB)
- CUDA context + framework overhead: ~700 MiB fixed

Usage:
    from shared.vram_cap import compute_max_seq_length, resolve_embed_max_seq_length

    # Direct computation with explicit parameters:
    max_n = compute_max_seq_length(batch_size=32, dedicated_vram_mb=8188)

    # Config-driven (reads EMBED_DYNAMIC_VRAM_CAP etc. from config module):
    import config
    max_n = resolve_embed_max_seq_length(config)
"""

import math
import subprocess
import sys
from typing import Any, Dict, Optional

from shared.log import log, log_warn

# ── Fixed overhead constants ─────────────────────────────────────────
# CUDA context allocation (driver, cuDNN, cuBLAS handles).
CUDA_CONTEXT_OVERHEAD_MB = 500
# PyTorch / HuggingFace framework overhead (computation graphs, autograd
# buffers, tokenizer state, etc.).
FRAMEWORK_OVERHEAD_MB = 200
# Combined fixed overhead used in VRAM budget calculations.
FIXED_OVERHEAD_MB = CUDA_CONTEXT_OVERHEAD_MB + FRAMEWORK_OVERHEAD_MB

# ── Model registry ───────────────────────────────────────────────────
# Architecture parameters for known embedding models.  Used by
# resolve_embed_max_seq_length() to look up defaults when the config
# specifies a MODEL_NAME but not explicit architecture params.
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "jinaai/jina-embeddings-v2-base-code": {
        "native_max": 8192,
        "num_heads": 12,
        "hidden_dim": 768,
        "num_layers": 12,
        "params_millions": 161.0,
    },
    "BAAI/bge-m3": {
        "native_max": 8192,
        "num_heads": 16,
        "hidden_dim": 1024,
        "num_layers": 24,
        "params_millions": 567.8,
    },
    "nomic-ai/CodeRankEmbed": {
        # RoPE attention (no ALiBi), O(N) VRAM scaling — can use full 8192 context.
        "native_max": 8192,
        "num_heads": 12,
        "hidden_dim": 768,
        "num_layers": 12,
        "params_millions": 137.0,
    },
    "Alibaba-NLP/gte-modernbert-base": {
        # ModernBERT-base: Flash Attention 2 + RoPE, O(N) VRAM scaling.
        # 22 transformer layers, 12 attention heads, 768 hidden dim.
        # Requires transformers>=4.48.0.
        "native_max": 8192,
        "num_heads": 12,
        "hidden_dim": 768,
        "num_layers": 22,
        "params_millions": 149.0,
    },
}


# ── GPU detection ────────────────────────────────────────────────────


def get_gpu_vram_info(gpu_index: int = 0) -> Dict[str, Any]:
    """Query nvidia-smi for dedicated VRAM and estimate shared VRAM.

    Dedicated VRAM is read from ``nvidia-smi --query-gpu=memory.total,
    memory.used,memory.free`` for the specified GPU index.  Shared VRAM
    (Windows resizable BAR / shared GPU memory) is estimated as
    ``min(system_ram / 2, 16384)`` MiB, which matches the typical Windows
    allocation policy.

    Args:
        gpu_index: Physical GPU index to query (default 0).  Pass the index
            of the GPU that will actually be used for embedding so the VRAM
            cap is computed for the right device.

    Returns:
        Dict with keys:
            - ``dedicated_total_mb`` (int): Total dedicated VRAM in MiB.
            - ``dedicated_used_mb`` (int): Currently used dedicated VRAM in MiB.
            - ``dedicated_free_mb`` (int): Currently free dedicated VRAM in MiB.
            - ``shared_total_mb`` (int): Estimated max shared VRAM in MiB.
            - ``detected`` (bool): True if nvidia-smi returned valid data.

        When the GPU cannot be detected, all numeric fields are 0 and
        ``detected`` is False.
    """
    result = {
        "dedicated_total_mb": 0,
        "dedicated_used_mb": 0,
        "dedicated_free_mb": 0,
        "shared_total_mb": 0,
        "detected": False,
    }

    # ── Dedicated VRAM via nvidia-smi ────────────────────────────────
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                f"--id={gpu_index}",
                "--query-gpu=memory.total,memory.used,memory.free",
                "--format=csv,nounits,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            parts = [p.strip() for p in proc.stdout.strip().split(",")]
            if len(parts) >= 3:
                result["dedicated_total_mb"] = int(parts[0])
                result["dedicated_used_mb"] = int(parts[1])
                result["dedicated_free_mb"] = int(parts[2])
                result["detected"] = True
    except FileNotFoundError:
        # nvidia-smi not on PATH — no NVIDIA GPU or driver not installed
        pass
    except Exception:
        pass

    # ── Shared VRAM estimate ─────────────────────────────────────────
    # Windows allocates up to half of system RAM as shared GPU memory,
    # capped at ~16 GB.  This is a reasonable heuristic; precise detection
    # would require WMI or DirectX queries.
    shared_mb = _estimate_shared_vram_mb()
    result["shared_total_mb"] = shared_mb

    return result


def _estimate_shared_vram_mb() -> int:
    """Estimate max shared GPU memory from system RAM.

    On Windows, the GPU shared memory pool is typically
    ``min(physical_ram / 2, 16384 MiB)``.  On non-Windows platforms or
    when detection fails, returns 0.

    Returns:
        Estimated shared VRAM in MiB.
    """
    try:
        if sys.platform == "win32":
            # Use wmic to query total physical memory (bytes)
            proc = subprocess.run(
                ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0:
                lines = [
                    ln.strip()
                    for ln in proc.stdout.strip().splitlines()
                    if ln.strip() and not ln.strip().startswith("Total")
                ]
                if lines:
                    total_bytes = int(lines[0])
                    total_mb = total_bytes // (1024 * 1024)
                    return min(total_mb // 2, 16384)
        else:
            # Linux / macOS: read /proc/meminfo or sysctl
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            # MemTotal is in kB
                            kb = int(line.split()[1])
                            total_mb = kb // 1024
                            return min(total_mb // 2, 16384)
            except (FileNotFoundError, PermissionError):
                pass
    except Exception:
        pass
    return 0


# ── Core VRAM cap solver ─────────────────────────────────────────────


def compute_max_seq_length(
    model_native_max: int = 8192,
    num_heads: int = 12,
    hidden_dim: int = 768,
    num_layers: int = 12,
    bytes_per_element: int = 2,
    model_params_millions: float = 161.0,
    batch_size: int = 32,
    dedicated_vram_mb: int = 8188,
    shared_vram_mb: int = 16384,
    safety_margin_pct: float = 0.15,
    base_cap: int = 4096,
    enable_dynamic: bool = True,
) -> int:
    """Compute the maximum safe sequence length for an embedding model.

    Solves the VRAM budget equation for the largest sequence length N that
    fits within the GPU's dedicated + shared VRAM (minus a safety margin).

    The VRAM model is::

        total_available = (dedicated + shared) * (1 - safety_margin)
        usable = total_available - fixed_overhead - model_weights
        usable = alibi_bias(N) + activations(batch_size, N)

    Where::

        alibi_bias(N) = num_heads * N^2 * bytes_per_element  (bytes → MiB)
        activations(batch_size, N) = batch_size * N * hidden_dim * num_layers
                                     * 2 * bytes_per_element  (bytes → MiB)

    This yields a quadratic in N::

        a * N^2 + b * N - c = 0

    Solved via the standard quadratic formula::

        N = (-b + sqrt(b^2 + 4ac)) / (2a)

    The result is rounded DOWN to the nearest multiple of 128 (tensor
    alignment), then clamped to ``[base_cap, model_native_max]``.

    Args:
        model_native_max: Model's native maximum sequence length.
        num_heads: Number of attention heads (ALiBi bias shape dimension).
        hidden_dim: Hidden dimension of the transformer.
        num_layers: Number of transformer layers.
        bytes_per_element: 2 for float16, 4 for float32.
        model_params_millions: Model parameter count in millions.
        batch_size: Number of chunks per embedding batch.
        dedicated_vram_mb: Dedicated GPU VRAM in MiB (from nvidia-smi).
        shared_vram_mb: Max shared GPU VRAM in MiB.
        safety_margin_pct: Fraction of total VRAM to reserve (0.0 - 1.0).
        base_cap: Fallback / minimum sequence length cap.
        enable_dynamic: If False, return ``base_cap`` immediately.

    Returns:
        The maximum safe sequence length (int), rounded to a multiple of 128.
    """
    if not enable_dynamic:
        return base_cap

    # ── Step 1: Total available VRAM budget (MiB) ────────────────────
    total_vram_mb = dedicated_vram_mb + shared_vram_mb
    available_mb = total_vram_mb * (1.0 - safety_margin_pct)

    # ── Step 2: Subtract fixed costs ─────────────────────────────────
    model_weights_mb = model_params_millions * 1e6 * bytes_per_element / (1024 * 1024)
    remaining_mb = available_mb - FIXED_OVERHEAD_MB - model_weights_mb

    if remaining_mb <= 0:
        log_warn(
            f"VRAM cap: insufficient VRAM after fixed overhead. "
            f"Available={available_mb:.0f} MiB, overhead={FIXED_OVERHEAD_MB} MiB, "
            f"model_weights={model_weights_mb:.0f} MiB. Falling back to base_cap={base_cap}."
        )
        return base_cap

    # ── Step 3: Solve quadratic for N ────────────────────────────────
    # Convert remaining_mb to bytes for the quadratic (avoid fractional MiB
    # precision loss in the discriminant).
    remaining_bytes = remaining_mb * 1024 * 1024

    # Quadratic coefficients: a*N^2 + b*N - c = 0
    # alibi_bias(N) = num_heads * N^2 * bytes_per_element  (bytes)
    a = num_heads * bytes_per_element  # coefficient for N^2

    # activations(batch_size, N) = batch_size * N * hidden_dim * num_layers * 2 * bytes_per_element
    b = (
        batch_size * hidden_dim * num_layers * 2 * bytes_per_element
    )  # coefficient for N

    c = remaining_bytes  # available bytes budget

    # Discriminant: b^2 + 4ac
    discriminant = b * b + 4 * a * c
    if discriminant < 0:
        # Should not happen with positive a, c, but guard against it
        log_warn(
            f"VRAM cap: negative discriminant ({discriminant}). "
            f"Falling back to base_cap={base_cap}."
        )
        return base_cap

    # Positive root of the quadratic: N = (-b + sqrt(b^2 + 4ac)) / (2a)
    n_float = (-b + math.sqrt(discriminant)) / (2 * a)

    if n_float <= 0:
        log_warn(
            f"VRAM cap: solver returned non-positive N ({n_float:.1f}). "
            f"Falling back to base_cap={base_cap}."
        )
        return base_cap

    # ── Step 4: Round down to nearest multiple of 128 ────────────────
    n_aligned = int(n_float // 128) * 128
    if n_aligned < 128:
        n_aligned = 128  # absolute minimum

    # ── Step 5: Clamp to [base_cap, model_native_max] ────────────────
    n_clamped = max(base_cap, min(n_aligned, model_native_max))

    # ── Logging ──────────────────────────────────────────────────────
    alibi_mb = num_heads * n_clamped * n_clamped * bytes_per_element / (1024 * 1024)
    act_mb = (
        batch_size
        * n_clamped
        * hidden_dim
        * num_layers
        * 2
        * bytes_per_element
        / (1024 * 1024)
    )
    total_est_mb = FIXED_OVERHEAD_MB + model_weights_mb + alibi_mb + act_mb

    log(
        f"VRAM cap: computed max_seq_length={n_clamped} "
        f"(solver raw={n_float:.0f}, aligned={n_aligned})"
    )
    log(
        f"  VRAM budget: dedicated={dedicated_vram_mb} MiB + shared={shared_vram_mb} MiB "
        f"= {total_vram_mb} MiB, usable (after {safety_margin_pct:.0%} margin) "
        f"= {available_mb:.0f} MiB"
    )
    log(
        f"  Estimated usage at N={n_clamped}: "
        f"overhead={FIXED_OVERHEAD_MB} + weights={model_weights_mb:.0f} + "
        f"alibi={alibi_mb:.0f} + activations={act_mb:.0f} = {total_est_mb:.0f} MiB"
    )

    if n_clamped != base_cap:
        log(f"  Dynamic cap differs from base_cap: {n_clamped} vs {base_cap}")

    return n_clamped


# ── Config integration ───────────────────────────────────────────────


def resolve_embed_max_seq_length(config_module: Any) -> int:
    """Read config settings and compute the effective max sequence length.

    This is the main integration point.  It reads relevant attributes from
    the config module (with safe defaults) and delegates to
    :func:`compute_max_seq_length`.

    Config attributes read:
        - ``EMBED_MAX_SEQ_LENGTH`` (int or None): Base cap.  None means use
          the model's native max.
        - ``EMBED_DYNAMIC_VRAM_CAP`` (bool): Enable dynamic VRAM-based cap.
          Default False (just return base_cap).
        - ``EMBED_VRAM_SAFETY_MARGIN`` (float): Safety margin fraction.
          Default 0.15.
        - ``EMBED_VRAM_DEDICATED_MB`` (int or None): Override dedicated VRAM.
          None = auto-detect via nvidia-smi.
        - ``EMBED_VRAM_SHARED_MB`` (int or None): Override shared VRAM.
          None = auto-detect.
        - ``DENSE_EMBED_BATCH_SIZE`` (int): Batch size for the activation
          VRAM estimate.
        - ``EMBED_MODEL_KWARGS`` (dict): Checked for ``torch_dtype`` to
          determine ``bytes_per_element`` (2 for float16, 4 for float32).
        - ``MODEL_NAME`` (str): Used to look up model-specific architecture
          parameters in :data:`MODEL_REGISTRY`.

    Args:
        config_module: The config module (or any object with the attributes
            listed above).

    Returns:
        The effective max sequence length (int).
    """
    # ── Read config values with safe defaults ────────────────────────
    enable_dynamic: bool = getattr(config_module, "EMBED_DYNAMIC_VRAM_CAP", False)
    base_cap_raw = getattr(config_module, "EMBED_MAX_SEQ_LENGTH", None)
    safety_margin: float = getattr(config_module, "EMBED_VRAM_SAFETY_MARGIN", 0.15)
    dedicated_override = getattr(config_module, "EMBED_VRAM_DEDICATED_MB", None)
    shared_override = getattr(config_module, "EMBED_VRAM_SHARED_MB", None)
    batch_size: int = getattr(config_module, "DENSE_EMBED_BATCH_SIZE", 32)
    model_kwargs: dict = getattr(config_module, "EMBED_MODEL_KWARGS", {})
    model_name: str = getattr(config_module, "MODEL_NAME", "")

    # ── Determine bytes_per_element from torch_dtype ─────────────────
    torch_dtype = model_kwargs.get("torch_dtype", "float32")
    if torch_dtype in ("float16", "half"):
        bytes_per_element = 2
    elif torch_dtype in ("bfloat16",):
        bytes_per_element = 2
    elif torch_dtype in ("float32", "float"):
        bytes_per_element = 4
    else:
        bytes_per_element = 2  # default to float16 (most common for inference)

    # ── Look up model architecture ───────────────────────────────────
    model_info = MODEL_REGISTRY.get(model_name, {})
    native_max: int = model_info.get("native_max", 8192)
    num_heads: int = model_info.get("num_heads", 12)
    hidden_dim: int = model_info.get("hidden_dim", 768)
    num_layers: int = model_info.get("num_layers", 12)
    params_millions: float = model_info.get("params_millions", 161.0)

    # base_cap: if config says None, use the model's native max
    base_cap: int = native_max if base_cap_raw is None else int(base_cap_raw)

    # ── Short-circuit if dynamic cap is disabled ─────────────────────
    if not enable_dynamic:
        log(f"VRAM cap: dynamic cap disabled, using base_cap={base_cap}")
        return base_cap

    # ── Auto-detect GPU VRAM if not overridden ───────────────────────
    # Resolve which GPU index is actually being used for embedding so we
    # query VRAM for the right device (important on multi-GPU systems).
    if dedicated_override is not None:
        dedicated_vram_mb = int(dedicated_override)
        shared_vram_mb = int(shared_override) if shared_override is not None else 16384
    else:
        # Extract GPU index from INDEX_EMBED_DEVICE setting
        device_raw = (
            str(getattr(config_module, "INDEX_EMBED_DEVICE", "auto")).strip().lower()
        )
        gpu_index = 0
        if device_raw.startswith("cuda:"):
            try:
                gpu_index = int(device_raw.split(":")[1])
            except (ValueError, IndexError):
                gpu_index = 0
        elif device_raw.isdigit():
            gpu_index = int(device_raw)
        elif device_raw in ("auto", "cuda"):
            # Try to find the best GPU index via nvidia-smi
            try:
                from shared.docker_utils import _detect_available_gpus, _pick_best_gpu

                gpus = _detect_available_gpus()
                if gpus:
                    gpu_index = _pick_best_gpu(gpus)["index"]
            except Exception:
                gpu_index = 0

        gpu_info = get_gpu_vram_info(gpu_index)
        if not gpu_info["detected"]:
            log_warn(
                "VRAM cap: no GPU detected (nvidia-smi unavailable). "
                f"Falling back to base_cap={base_cap}."
            )
            return base_cap
        dedicated_vram_mb = gpu_info["dedicated_total_mb"]
        shared_vram_mb = (
            int(shared_override)
            if shared_override is not None
            else gpu_info["shared_total_mb"]
        )

    log(
        f"VRAM cap: model={model_name}, "
        f"dedicated={dedicated_vram_mb} MiB, shared={shared_vram_mb} MiB, "
        f"batch_size={batch_size}, bytes_per_element={bytes_per_element}"
    )

    if model_name and model_name not in MODEL_REGISTRY:
        log_warn(
            f"VRAM cap: model '{model_name}' not in MODEL_REGISTRY. "
            f"Using default architecture params (num_heads={num_heads}, "
            f"hidden_dim={hidden_dim}, num_layers={num_layers}, "
            f"params={params_millions}M)."
        )

    # ── Compute ──────────────────────────────────────────────────────
    return compute_max_seq_length(
        model_native_max=native_max,
        num_heads=num_heads,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        bytes_per_element=bytes_per_element,
        model_params_millions=params_millions,
        batch_size=batch_size,
        dedicated_vram_mb=dedicated_vram_mb,
        shared_vram_mb=shared_vram_mb,
        safety_margin_pct=safety_margin,
        base_cap=base_cap,
        enable_dynamic=True,
    )
