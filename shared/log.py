"""
Unified logging for informica-rag.

Usage:
    from shared.log import log, log_raw, log_error, log_warn

    log("Starting indexing...")          # [2026-03-06 14:23:05] Starting indexing...
    log_raw("=" * 70)                    # ======...  (no timestamp, for tables)
    log_error("File not found: x.pas")   # [2026-03-06 14:23:05] [ERROR] File not found: x.pas
    log_warn("Skipping empty file")      # [2026-03-06 14:23:05] [WARN] Skipping empty file

To redirect all output to stderr (e.g., MCP stdio transport):
    from shared.log import configure
    configure(stream=sys.stderr)
"""

import sys
from datetime import datetime
from typing import TextIO

_stream: TextIO = sys.stdout


def configure(stream: TextIO) -> None:
    """Set the output stream for all log functions."""
    global _stream
    _stream = stream


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str = "") -> None:
    """Print a timestamped message."""
    if msg:
        print(f"[{_timestamp()}] {msg}", file=_stream, flush=True)
    else:
        print(file=_stream, flush=True)


def log_raw(msg: str = "") -> None:
    """Print without timestamp (for tables, separators, blank lines)."""
    print(msg, file=_stream, flush=True)


def log_error(msg: str) -> None:
    """Print a timestamped error message."""
    print(f"[{_timestamp()}] [ERROR] {msg}", file=_stream, flush=True)


def log_warn(msg: str) -> None:
    """Print a timestamped warning message."""
    print(f"[{_timestamp()}] [WARN] {msg}", file=_stream, flush=True)
