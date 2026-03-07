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

To tee all output to both the current stream and a log file:
    from shared.log import configure_tee, close_tee
    configure_tee("/path/to/logfile.log")
    # ... do work ...
    close_tee()
"""

import sys
from datetime import datetime
from typing import TextIO

_stream: TextIO = sys.stdout


class TeeStream:
    """Write to two streams simultaneously (e.g., stdout + log file)."""

    def __init__(self, primary: TextIO, secondary: TextIO) -> None:
        self.primary = primary
        self.secondary = secondary

    def write(self, msg: str) -> int:
        self.primary.write(msg)
        self.secondary.write(msg)
        return len(msg)

    def flush(self) -> None:
        self.primary.flush()
        self.secondary.flush()


def configure(stream: TextIO) -> None:
    """Set the output stream for all log functions."""
    global _stream
    _stream = stream


def configure_tee(log_file_path: str) -> None:
    """Tee all log output to both the current stream and a file."""
    global _stream
    fh = open(log_file_path, "w", encoding="utf-8")
    _stream = TeeStream(_stream, fh)


def close_tee() -> None:
    """Close the tee file handle if active, revert to primary stream."""
    global _stream
    if isinstance(_stream, TeeStream):
        _stream.secondary.close()
        _stream = _stream.primary


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
