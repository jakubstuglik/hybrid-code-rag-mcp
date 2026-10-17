# MCP server

## Starting the MCP server

All scripts require a config name. Two transports are available:

**Stdio** (for OpenCode, Claude Desktop, and other MCP clients):
```bash
# Windows
scripts\start_rag_mcp_stdio.bat my_project
scripts\start_rag_mcp_stdio.bat self-index

# Linux/Mac
scripts/start_rag_mcp_stdio.sh my_project
scripts/start_rag_mcp_stdio.sh self-index
```

**HTTP** (for debugging, remote clients, or browser-based tools):
```bash
# Windows
scripts\start_rag_mcp_http.bat my_project
scripts\start_rag_mcp_http.bat self-index

# Linux/Mac
scripts/start_rag_mcp_http.sh my_project
scripts/start_rag_mcp_http.sh self-index
```

**Manual launch** (without scripts):
```bash
python src/rag_mcp.py --config my_project --transport stdio
python src/rag_mcp.py --config my_project --transport streamable-http
python src/rag_mcp.py --config self-index --transport stdio
```

## OpenCode integration

To use this as an MCP tool inside another project, add to that project's `opencode.jsonc`:

```jsonc
{
  "mcp": {
    "my-project-rag": {
      "type": "local",
      "enabled": true,
      "command": [
        "powershell", "-Command",
        "cmd.exe /c 'for /f \"delims=\" %a in (''git rev-parse --show-toplevel'') do call \"%a\\..\\hybrid-code-rag-mcp\\scripts\\start_rag_mcp_stdio.bat\" my_project'"
      ]
    }
  }
}
```

The PowerShell wrapper resolves paths relative to the git root, so it works regardless of which subfolder OpenCode is launched from.

**Linux/Mac equivalent:**
```json
{
  "mcp": {
    "my-project-rag": {
      "type": "local",
      "enabled": true,
      "command": ["bash", "-c", "$(git rev-parse --show-toplevel)/../hybrid-code-rag-mcp/scripts/start_rag_mcp_stdio.sh my_project"]
    }
  }
}
```

For the self-index, this repository's own `opencode.json` uses the cross-platform Python launcher (paths are relative to the repo root):
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "self-rag": {
      "type": "local",
      "command": ["python", "scripts/start_self_rag.py"],
      "enabled": true,
      "timeout": 120000
    }
  }
}
```

`scripts/start_self_rag.py` switches to the repo root, prefers `.venv`'s Python and runs `src/rag_mcp.py --config self-index --transport stdio`. `scripts\start_self_rag.bat` and `scripts/start_self_rag.sh` do the same through the stdio script. Docker auto-start is handled by `src/rag_mcp.py`.

For a remote (HTTP) server, OpenCode uses `"type": "remote"` with a `url`, for example `{"type": "remote", "url": "http://localhost:8125/mcp", "oauth": false}`. See the [OpenCode MCP docs](https://opencode.ai/docs/mcp-servers/).

## Grok Build integration

Grok Build reads MCP servers from `[mcp_servers.<name>]` tables in `~/.grok/config.toml` and in project `.grok/config.toml` files (it walks from the current directory up to the git root). See the [Grok Build MCP docs](https://docs.x.ai/build/features/mcp-servers).

```bash
# stdio: everything after -- is the server command
grok mcp add my-project-rag -- /path/to/hybrid-code-rag-mcp/scripts/start_rag_mcp_stdio.sh my_project
# HTTP (start the server with scripts/start_rag_mcp_http.* first)
grok mcp add --transport http my-project-rag http://localhost:8125/mcp
# add --scope project to write ./.grok/config.toml instead of ~/.grok/config.toml
```

This repository ships a project-scoped config for the self-index in `.grok/config.toml`:

```toml
[mcp_servers.self-rag]
command = "python"
args = ["scripts/start_self_rag.py"]
enabled = true
# Cold start may start Qdrant/TEI containers + load BM25 encoder
startup_timeout_sec = 180
```

`startup_timeout_sec` defaults to 30 seconds; the first start can take longer because the Qdrant and TEI containers may have to be created. `grok mcp doctor <name>` diagnoses a server that does not connect, and stderr of stdio servers is captured under `~/.grok/logs/mcp/`.

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/start_qdrant.*` | Start Qdrant Docker container for a config (manual) | `scripts\start_qdrant.bat my_project` |
| `scripts/start_rag_mcp_stdio.*` | Start MCP server (stdio transport) | `scripts\start_rag_mcp_stdio.bat my_project` |
| `scripts/start_rag_mcp_http.*` | Start MCP server (HTTP transport) | `scripts\start_rag_mcp_http.bat self-index` |
| `scripts/start_self_rag.*` | Start self-index MCP server (stdio) | `scripts\start_self_rag.bat` |
| `scripts/start_self_rag.py` | Cross-platform Python launcher for self-index MCP | `python scripts/start_self_rag.py` |
| `src/refresh_guard.py` | Cron-safe indexing with skip/kill guard | `python src/refresh_guard.py --config my_project --yes` |
| `src/git_pull_guard.py` | Cron-safe git pull + indexing guard | `python src/git_pull_guard.py --config my_project` |
| `src/git_pull_all.py` | Simple git pull for all repos in a config | `python src/git_pull_all.py --config my_project` |

All shell scripts have `.bat` (Windows) and `.sh` (Linux/Mac) variants. Scripts except `start_self_rag` require a config name as the first argument.

**Note:** In local mode, `src/index_rag.py` and `src/rag_mcp.py` auto-start Docker containers, so `start_qdrant` is only needed for manual/diagnostic use.
