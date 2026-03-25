"""
GPU and CPU stats collection for indexing performance monitoring.

Collects dedicated VRAM (via nvidia-smi), shared GPU memory (via Windows
performance counters), and CPU/RAM usage (via psutil) into a single CSV file.
Runs in a background thread to avoid blocking the indexing loop.

Supports targeting a specific GPU by nvidia-smi index (``gpu_index`` param),
which is critical on multi-GPU systems where the embedding backend may run on
a GPU other than index 0.

Usage:
    from shared.gpu_stats import start_gpu_stats, stop_gpu_stats

    csv_path = start_gpu_stats(Path("output/gpu_stats.csv"), interval=2.0, gpu_index=1)
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

try:
    import psutil

    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

from shared.log import log, log_warn


# ── Module state ─────────────────────────────────────────────────────
_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_csv_path: Optional[Path] = None

# Target GPU nvidia-smi index (None = all GPUs / first line)
_gpu_index: Optional[int] = None

# LUID of the discrete GPU (auto-detected on first sample)
_gpu_luid: Optional[str] = None


def _detect_gpu_luid(gpu_index: Optional[int] = None) -> Optional[str]:
    """Find the Windows perf-counter LUID for the target GPU.

    When ``gpu_index`` is given, we enumerate all GPU adapters by dedicated
    VRAM, sort them descending (discrete GPUs have more VRAM than integrated),
    and pick the entry at position ``gpu_index``.  This correlates nvidia-smi
    GPU ordering (by PCI bus) with Windows perf-counter adapter instances.

    When ``gpu_index`` is None, falls back to picking the adapter with the
    highest dedicated usage (original single-GPU behavior).
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
                    "| Select-Object -ExpandProperty InstanceName"
                ),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Lines are sorted by dedicated VRAM descending — same order as
            # nvidia-smi GPU indices on typical systems (discrete GPUs first).
            luids = [
                line.strip()
                for line in result.stdout.strip().splitlines()
                if line.strip()
            ]
            if gpu_index is not None and 0 <= gpu_index < len(luids):
                return luids[gpu_index]
            elif luids:
                return luids[0]
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


def _read_nvidia_smi(gpu_index: Optional[int] = None) -> Optional[dict]:
    """Read current GPU stats from nvidia-smi.

    Args:
        gpu_index: If given, query only this GPU via ``--id=N``.
            When None, queries all GPUs and returns the first line.

    Returns:
        Dict with keys: gpu_util, mem_util, mem_used_mib, mem_total_mib, temp_c.
        Or None if nvidia-smi is unavailable.
    """
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,utilization.memory,"
            "memory.used,memory.total,temperature.gpu",
            "--format=csv,nounits,noheader",
        ]
        if gpu_index is not None:
            cmd.insert(1, f"--id={gpu_index}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Take only the first line (relevant when no --id filter)
            first_line = result.stdout.strip().splitlines()[0]
            parts = [p.strip() for p in first_line.split(",")]
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
    """Background thread that samples GPU stats and writes CSV rows.

    Shared VRAM (Windows perf counter via powershell) is expensive (~1.3s per
    call).  To avoid inflating the sample interval, we only query it every
    ``_SHARED_VRAM_REFRESH`` samples and cache the last value in between.
    With interval=0.33 and refresh=30, shared VRAM updates every ~10 seconds.
    """
    global _gpu_luid

    # How often to refresh shared VRAM (every Nth sample)
    _SHARED_VRAM_REFRESH = 30

    # Auto-detect the discrete GPU LUID for shared VRAM queries
    if sys.platform == "win32" and _gpu_luid is None:
        _gpu_luid = _detect_gpu_luid(_gpu_index)
        if _gpu_luid:
            log(
                f"GPU stats: detected adapter instance '{_gpu_luid}' (gpu_index={_gpu_index})"
            )
        else:
            log_warn("GPU stats: could not detect GPU adapter for shared VRAM")

    # Write CSV header
    with open(str(csv_path), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "timestamp",
                "gpu_index",
                "gpu_util_%",
                "mem_util_%",
                "dedicated_used_mib",
                "dedicated_total_mib",
                "shared_used_mib",
                "temp_c",
                "cpu_util_%",
                "ram_used_mib",
                "ram_total_mib",
            ]
        )

    # Prime psutil's cpu_percent (first call always returns 0.0)
    if _HAS_PSUTIL:
        psutil.cpu_percent(interval=None)

    sample_count = 0
    cached_shared_mib: Optional[float] = None

    while not _stop_event.is_set():
        ts = (
            time.strftime("%Y-%m-%d %H:%M:%S")
            + f".{int(time.time() * 1000) % 1000:03d}"
        )

        # Dedicated VRAM from nvidia-smi (targeting specific GPU if set)
        nv = _read_nvidia_smi(_gpu_index)

        # Shared VRAM from Windows perf counter — only refresh every Nth sample
        # to keep actual sample interval close to the requested interval.
        if _gpu_luid:
            if sample_count % _SHARED_VRAM_REFRESH == 0:
                fresh = _read_shared_vram_mb(_gpu_luid)
                if fresh is not None:
                    cached_shared_mib = fresh
        shared_mib = cached_shared_mib

        # CPU and RAM from psutil
        cpu_pct = ""
        ram_used = ""
        ram_total = ""
        if _HAS_PSUTIL:
            cpu_pct = f"{psutil.cpu_percent(interval=None):.1f}"
            vm = psutil.virtual_memory()
            ram_used = f"{vm.used / (1024 * 1024):.0f}"
            ram_total = f"{vm.total / (1024 * 1024):.0f}"

        gpu_idx_str = str(_gpu_index) if _gpu_index is not None else ""

        if nv:
            row = [
                ts,
                gpu_idx_str,
                nv["gpu_util"],
                nv["mem_util"],
                nv["mem_used_mib"],
                nv["mem_total_mib"],
                f"{shared_mib:.0f}" if shared_mib is not None else "",
                nv["temp_c"],
                cpu_pct,
                ram_used,
                ram_total,
            ]
        else:
            # nvidia-smi unavailable — write shared-only if we have it
            row = [
                ts,
                gpu_idx_str,
                "",
                "",
                "",
                "",
                f"{shared_mib:.0f}" if shared_mib is not None else "",
                "",
                cpu_pct,
                ram_used,
                ram_total,
            ]

        try:
            with open(str(csv_path), "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception:
            pass  # Don't crash the indexer over stats

        sample_count += 1
        _stop_event.wait(interval)


def start_gpu_stats(
    csv_path: Path,
    interval: float = 2.0,
    gpu_index: Optional[int] = None,
) -> Path:
    """Start background GPU stats collection.

    Args:
        csv_path: Path to write the CSV file.
        interval: Seconds between samples (default 2.0).
        gpu_index: nvidia-smi GPU index to monitor. When None, monitors
            the first GPU returned by nvidia-smi (typically index 0).
            On multi-GPU systems, pass the index of the GPU that the
            embedding backend is using (TEI or PyTorch).

    Returns:
        The csv_path for reference.
    """
    global _thread, _csv_path, _gpu_index, _gpu_luid

    stop_gpu_stats()  # stop any previous collector

    _stop_event.clear()
    _csv_path = csv_path
    _gpu_index = gpu_index
    _gpu_luid = None  # reset — will be re-detected for the target GPU
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    _thread = threading.Thread(
        target=_collector_loop,
        args=(csv_path, interval),
        daemon=True,
        name="gpu-stats",
    )
    _thread.start()
    gpu_label = f" (GPU {gpu_index})" if gpu_index is not None else ""
    log(f"GPU stats collection started{gpu_label}: {csv_path}")
    return csv_path


def stop_gpu_stats() -> None:
    """Stop background GPU stats collection."""
    global _thread

    if _thread is not None and _thread.is_alive():
        _stop_event.set()
        _thread.join(timeout=5)
        log("GPU stats collection stopped.")
    _thread = None
