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

For the self-index (used inside this project's own `opencode.json`):
```json
{
  "mcp": {
    "self-rag": {
      "type": "local",
      "command": ["cmd", "/c", "scripts\\start_self_rag.bat"],
      "enabled": true,
      "timeout": 120000
    }
  }
}
```

`scripts\start_self_rag.bat` (or `scripts/start_self_rag.sh` on Linux/Mac) delegates to the stdio script with the `self-index` config. Docker auto-start is handled by `src/rag_mcp.py`.

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
