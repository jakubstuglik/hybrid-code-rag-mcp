"""
Unified logging for hybrid-code-rag-mcp.

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


def _safe_write(stream, msg):
    """Write msg to stream; never raise on encoding errors (replace bad chars)."""
    try:
        stream.write(msg)
    except UnicodeEncodeError:
        enc = getattr(stream, "encoding", None) or "utf-8"
        try:
            stream.write(msg.encode(enc, errors="replace").decode(enc, errors="replace"))
        except Exception:
            pass
    except Exception:
        pass


def _safe_flush(stream):
    try:
        stream.flush()
    except Exception:
        pass


class TeeStream:
    """Write to two streams simultaneously (e.g., stdout + log file).

    Encoding-safe: a character the console code page can't encode (e.g. cp1250)
    is replaced instead of raising, and a failure on one stream never stops the
    other or the caller (indexing keeps running). Each write is flushed.
    """

    def __init__(self, primary: TextIO, secondary: TextIO) -> None:
        self.primary = primary
        self.secondary = secondary

    def write(self, msg: str) -> int:
        _safe_write(self.primary, msg)
        _safe_write(self.secondary, msg)
        return len(msg)

    def flush(self) -> None:
        _safe_flush(self.primary)
        _safe_flush(self.secondary)


def configure(stream: TextIO) -> None:
    """Set the output stream for all log functions."""
    global _stream
    _stream = stream


def configure_tee(log_file_path: str) -> None:
    """Tee all log output to both the current stream and a file.

    The log file is opened with line buffering (buffering=1) so every line
    is flushed to disk immediately — the file is safe to tail during a long
    indexing run without waiting for the OS write-back buffer to fill.
    """
    global _stream
    fh = open(log_file_path, "w", encoding="utf-8", errors="replace", buffering=1)
    _stream = TeeStream(_stream, fh)


def close_tee() -> None:
    """Close the tee file handle if active, revert to primary stream."""
    global _stream
    if isinstance(_stream, TeeStream):
        _stream.secondary.close()
        _stream = _stream.primary


def _emit(text: str) -> None:
    """Print one line to the active stream; logging must never crash the caller."""
    try:
        print(text, file=_stream, flush=True)
    except Exception:
        _safe_write(_stream, text + "\n")
        _safe_flush(_stream)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log(msg: str = "") -> None:
    """Print a timestamped message."""
    if msg:
        _emit(f"[{_timestamp()}] {msg}")
    else:
        _emit("")


def log_raw(msg: str = "") -> None:
    """Print without timestamp (for tables, separators, blank lines)."""
    _emit(msg)


def log_error(msg: str) -> None:
    """Print a timestamped error message."""
    _emit(f"[{_timestamp()}] [ERROR] {msg}")


def log_warn(msg: str) -> None:
    """Print a timestamped warning message."""
    _emit(f"[{_timestamp()}] [WARN] {msg}")
