#!/usr/bin/env python3
"""Cross-platform launcher for self-rag MCP server (stdio).

Portable: no absolute paths. Resolves the repo root from this file's
location, prefers ``.venv``'s Python when present, and execs
``src/rag_mcp.py --config self-index --transport stdio``.

Used by:
  - opencode.json  → ``python scripts/start_self_rag.py``
  - .grok/config.toml → same
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _venv_python(root: Path) -> Path | None:
    if sys.platform == "win32":
        candidate = root / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = root / ".venv" / "bin" / "python"
    return candidate if candidate.is_file() else None


def main() -> int:
    root = _repo_root()
    os.chdir(root)

    # Match start_rag_mcp_stdio.bat / .sh
    src = root / "src"
    os.environ["PYTHONPATH"] = os.pathsep.join(
        [str(root), str(src), os.environ.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)

    rag_mcp = root / "src" / "rag_mcp.py"
    if not rag_mcp.is_file():
        print(f"ERROR: missing {rag_mcp}", file=sys.stderr)
        return 1

    py = _venv_python(root)
    if py is not None:
        # Replace this process with venv python running rag_mcp
        os.execv(str(py), [str(py), str(rag_mcp), "--config", "self-index", "--transport", "stdio"])
        return 1  # unreachable

    # Fallback: same interpreter that launched this script
    os.execv(
        sys.executable,
        [sys.executable, str(rag_mcp), "--config", "self-index", "--transport", "stdio"],
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
