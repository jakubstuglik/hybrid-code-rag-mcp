#!/usr/bin/env python3
"""Cross-platform launcher for self-rag MCP server."""

import sys
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if sys.platform == "win32":
    script = os.path.join(SCRIPT_DIR, "start_rag_mcp_stdio.bat")
    result = subprocess.run(["cmd", "/c", script, "self-index"], cwd=SCRIPT_DIR)
else:
    script = os.path.join(SCRIPT_DIR, "start_rag_mcp_stdio.sh")
    result = subprocess.run([script, "self-index"], cwd=SCRIPT_DIR)

sys.exit(result.returncode)
