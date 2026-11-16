#!/usr/bin/env python3
"""Attach exactly the MCP servers a variant needs in the isolated GROK_HOME.

Must run with cwd at a directory that has no project .grok/config.toml
(the Django checkout is fine) and with GROK_HOME set to
C:\\Apps\\hcr-bench\\grok-home. Uses --scope user so only that home is
changed. The user's everyday ~/.grok is not touched.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_GROK_HOME = os.environ.get("GROK_HOME") or str(Path.home() / "hcr-bench" / "grok-home")
DEFAULT_GROK = os.environ.get("GROK_BIN") or shutil.which("grok") or str(Path.home() / ".grok" / "bin" / "grok.exe")
DEFAULT_CWD = os.environ.get("HCR_BENCH_DJANGO") or str(Path.home() / "hcr-bench" / "django")

# MCP endpoints for this host. serena/hcr are streamable HTTP;
# claude-context 0.1.16 speaks stdio only, so it is added as a local command.
SERVERS = {
    "serena": {
        "name": "serena",
        "transport": "http",
        "url": "http://127.0.0.1:9121/mcp",
    },
    "hcr": {
        "name": "django-bench-rag",
        "transport": "http",
        "url": "http://127.0.0.1:19130/mcp",
    },
    # @zilliz/claude-context-mcp@0.1.16 is stdio-only (StdioServerTransport).
    "claude_context": {
        "name": "claude-context",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@zilliz/claude-context-mcp@0.1.16"],
        "env": {
            "EMBEDDING_PROVIDER": "Ollama",
            "EMBEDDING_MODEL": "nomic-embed-text",
            "OLLAMA_HOST": "http://127.0.0.1:11434",
            "EMBEDDING_DIMENSION": "768",
            "MILVUS_ADDRESS": "127.0.0.1:19530",
            "CLAUDE_CONTEXT_BACKGROUND_SYNC": "false",
        },
    },
}

VARIANT_SERVERS = {
    "none": [],
    "read_only": [],
    "ripgrep": [],
    "serena": ["serena"],
    "hcr": ["hcr"],
    "claude_context": ["claude_context"],
}


def grok_env(grok_home: str) -> dict[str, str]:
    env = os.environ.copy()
    env["GROK_HOME"] = grok_home
    env["GROK_MEMORY"] = "0"
    env["GROK_DISABLE_AUTOUPDATER"] = "1"
    return env


def run_grok(grok: str, args: list[str], env: dict[str, str], cwd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [grok, *args],
        env=env,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=60,
    )


def list_servers(grok: str, env: dict[str, str], cwd: str) -> list[dict]:
    proc = run_grok(grok, ["mcp", "list", "--json"], env, cwd)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout or "mcp list failed\n")
        raise SystemExit(f"grok mcp list failed: {proc.returncode}")
    text = (proc.stdout or "").strip()
    if not text:
        return []
    data = json.loads(text)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("servers", "mcp_servers", "items"):
            if isinstance(data.get(k), list):
                return data[k]
        # maybe name -> spec
        return [{"name": k, **(v if isinstance(v, dict) else {"raw": v})} for k, v in data.items()]
    return []


def server_name(entry: dict) -> str | None:
    for k in ("name", "id", "server"):
        if isinstance(entry.get(k), str):
            return entry[k]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True, choices=sorted(VARIANT_SERVERS))
    ap.add_argument("--grok-home", default=DEFAULT_GROK_HOME)
    ap.add_argument("--grok", default=DEFAULT_GROK)
    ap.add_argument("--cwd", default=DEFAULT_CWD, help="Process cwd with no project .grok")
    args = ap.parse_args()
    env = grok_env(args.grok_home)
    wanted_keys = VARIANT_SERVERS[args.variant]
    wanted_names = {SERVERS[k]["name"] for k in wanted_keys}

    current = list_servers(args.grok, env, args.cwd)
    current_names = []
    for e in current:
        n = server_name(e)
        if n:
            current_names.append(n)
    # Remove everything not wanted (and wanted ones we will re-add to be safe).
    for n in current_names:
        proc = run_grok(args.grok, ["mcp", "remove", "--scope", "user", n], env, args.cwd)
        if proc.returncode != 0:
            sys.stderr.write(f"warn: remove {n}: {proc.stderr or proc.stdout}\n")

    for key in wanted_keys:
        spec = SERVERS[key]
        transport = spec.get("transport", "http")
        cmd = ["mcp", "add", "--scope", "user", "--transport", transport, spec["name"]]
        if transport == "http":
            cmd.append(spec["url"])
        else:
            for k, v in (spec.get("env") or {}).items():
                cmd.extend(["-e", f"{k}={v}"])
            cmd.append("--")
            cmd.append(spec["command"])
            cmd.extend(spec.get("args") or [])
        proc = run_grok(args.grok, cmd, env, args.cwd)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr or proc.stdout or "")
            raise SystemExit(f"failed to add MCP {spec['name']}: {proc.returncode}")

    after = list_servers(args.grok, env, args.cwd)
    after_names = [server_name(e) for e in after if server_name(e)]
    print(json.dumps({
        "variant": args.variant,
        "wanted": sorted(wanted_names),
        "configured": after_names,
    }))
    # Fail if a wanted server is missing (name match).
    missing = wanted_names.difference(set(filter(None, after_names)))
    if missing:
        raise SystemExit(f"MCP servers missing after prep: {sorted(missing)}")
    extra = set(filter(None, after_names)).difference(wanted_names)
    if extra:
        raise SystemExit(f"unexpected MCP servers still configured: {sorted(extra)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
