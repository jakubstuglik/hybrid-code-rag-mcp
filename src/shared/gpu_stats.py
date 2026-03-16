"""
GPU stats collection for indexing performance monitoring.

Collects dedicated VRAM (via nvidia-smi) and shared GPU memory (via Windows
performance counters) into a single CSV file.  Runs in a background thread
to avoid blocking the indexing loop.

Usage:
    from shared.gpu_stats import start_gpu_stats, stop_gpu_stats

    csv_path = start_gpu_stats(Path("output/gpu_stats.csv"), interval=2.0)
    # ... do indexing ...
    stop_gpu_stats()
"""

import csv
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from shared.log import log, log_warn


# ── Module state ─────────────────────────────────────────────────────
_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_csv_path: Optional[Path] = None

# LUID of the discrete GPU (auto-detected on first sample)
_gpu_luid: Optional[str] = None


def _detect_gpu_luid() -> Optional[str]:
    """Find the LUID of the discrete GPU that has dedicated VRAM in use.

    On a typical desktop with one discrete GPU and one or two integrated
    adapters, the discrete GPU is the one with substantial dedicated usage.
    """
    if sys.platform != "win32":
        return None
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-Counter '\\GPU Adapter Memory(*)\\Dedicated Usage' "
                    "-ErrorAction Stop "
                    "| Select-Object -ExpandProperty CounterSamples "
                    "| Sort-Object CookedValue -Descending "
                    "| Select-Object -First 1 "
                    "| Select-Object -ExpandProperty InstanceName"
                ),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _read_shared_vram_mb(instance: str) -> Optional[float]:
    """Read current shared GPU memory usage via Windows performance counter.

    Args:
        instance: The GPU adapter instance name (e.g. 'luid_0x00..._phys_0').

    Returns:
        Shared GPU memory in MiB, or None if unavailable.
    """
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    f"(Get-Counter '\\GPU Adapter Memory({instance})\\Shared Usage' "
                    "-ErrorAction Stop).CounterSamples[0].CookedValue"
                ),
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip()) / (1024 * 1024)  # bytes → MiB
    except Exception:
        pass
    return None


def _read_nvidia_smi() -> Optional[dict]:
    """Read current GPU stats from nvidia-smi.

    Returns:
        Dict with keys: gpu_util, mem_util, mem_used_mib, mem_total_mib, temp_c.
        Or None if nvidia-smi is unavailable.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,utilization.memory,"
                "memory.used,memory.total,temperature.gpu",
                "--format=csv,nounits,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = [p.strip() for p in result.stdout.strip().split(",")]
            if len(parts) >= 5:
                return {
                    "gpu_util": parts[0],
                    "mem_util": parts[1],
                    "mem_used_mib": parts[2],
                    "mem_total_mib": parts[3],
                    "temp_c": parts[4],
                }
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return None


def _collector_loop(csv_path: Path, interval: float) -> None:
    """Background thread that samples GPU stats and writes CSV rows."""
    global _gpu_luid

    # Auto-detect the discrete GPU LUID for shared VRAM queries
    if sys.platform == "win32" and _gpu_luid is None:
        _gpu_luid = _detect_gpu_luid()
        if _gpu_luid:
            log(f"GPU stats: detected adapter instance '{_gpu_luid}'")
        else:
            log_warn("GPU stats: could not detect GPU adapter for shared VRAM")

    # Write CSV header
    with open(str(csv_path), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "timestamp",
                "gpu_util_%",
                "mem_util_%",
                "dedicated_used_mib",
                "dedicated_total_mib",
                "shared_used_mib",
                "temp_c",
            ]
        )

    while not _stop_event.is_set():
        ts = time.strftime("%Y-%m-%d %H:%M:%S")

        # Dedicated VRAM from nvidia-smi
        nv = _read_nvidia_smi()

        # Shared VRAM from Windows perf counter
        shared_mib = None
        if _gpu_luid:
            shared_mib = _read_shared_vram_mb(_gpu_luid)

        if nv:
            row = [
                ts,
                nv["gpu_util"],
                nv["mem_util"],
                nv["mem_used_mib"],
                nv["mem_total_mib"],
                f"{shared_mib:.0f}" if shared_mib is not None else "",
                nv["temp_c"],
            ]
        else:
            # nvidia-smi unavailable — write shared-only if we have it
            row = [
                ts,
                "",
                "",
                "",
                "",
                f"{shared_mib:.0f}" if shared_mib is not None else "",
                "",
            ]

        try:
            with open(str(csv_path), "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception:
            pass  # Don't crash the indexer over stats

        _stop_event.wait(interval)


def start_gpu_stats(csv_path: Path, interval: float = 2.0) -> Path:
    """Start background GPU stats collection.

    Args:
        csv_path: Path to write the CSV file.
        interval: Seconds between samples (default 2.0).

    Returns:
        The csv_path for reference.
    """
    global _thread, _csv_path

    stop_gpu_stats()  # stop any previous collector

    _stop_event.clear()
    _csv_path = csv_path
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    _thread = threading.Thread(
        target=_collector_loop,
        args=(csv_path, interval),
        daemon=True,
        name="gpu-stats",
    )
    _thread.start()
    log(f"GPU stats collection started: {csv_path}")
    return csv_path


def stop_gpu_stats() -> None:
    """Stop background GPU stats collection."""
    global _thread

    if _thread is not None and _thread.is_alive():
        _stop_event.set()
        _thread.join(timeout=5)
        log("GPU stats collection stopped.")
    _thread = None
