# MCP Server — Additional Tool Methods

**TODO #4** — Add specialized search tools to the MCP server (e.g., `search_method_decl`, `search_method_def`) and provide documentation so AI agents know which tool to use when.

---

## Current State

The MCP server (`src/rag_mcp.py`) exposes a **single tool** configured by `MCP_TOOL_NAME` and `MCP_TOOL_DESCRIPTION` in `config.py`. For the self-index and project configs this is `search_rag` / `search_myproject`.

This single tool handles all query types: class overviews, method lookups, SQL procedure searches, DFM form searches, etc. The tool uses hybrid search + the reranker to surface the best chunks, but the AI agent has no way to express intent beyond a natural language query string.

---

## The Problem

Without specialized tools, agents must:
1. Use a single generic `search_rag` call and hope the reranker surfaces the right chunk type
2. Sometimes get a class overview when they wanted an implementation, or vice versa
3. Have no way to restrict results to a specific file type, code structure, or chunk type

**Example:**
- Agent wants the **declaration** of `PrepareDataSet` → generic search returns the implementation body
- Agent wants all **SQL procedures** touching a table → generic search mixes in Pascal code
- Agent wants the **form component list** for a DFM → generic search returns method bodies

---

## Proposed New Tools

All proposed tools are thin wrappers around the existing search pipeline with **Qdrant metadata filters** pre-applied. The `node_type` field is already stored on every chunk (62 values across all readers — see AGENTS.md).

### Tool Definitions

| Tool Name | Filter | Description |
|---|---|---|
| `search_method_decl` | `node_type IN [declProc, class_summary, class_summary_split]` | Find method/procedure **declarations** (interface section, signatures with parameters) |
| `search_method_def` | `node_type IN [defProc, method_group]` | Find method/procedure **implementations** (body/code) |
| `search_class` | `node_type IN [class_overview, class_summary, class_summary_split]` | Find class overviews and summaries |
| `search_sql` | `node_type IN [procedure_header, function_header, procedure_full, function_full, create_procedure, create_function, create_trigger, create_view]` | Find SQL stored procedures, functions, triggers, views |
| `search_form` | `node_type IN [dfm_form_header, dfm_object, dfm_object_group]` | Find DFM form structure and components |
| `search_uses` | `node_type = declUses` | Find uses clauses / import dependencies |

All tools share the same parameters as the existing `search_rag` tool:
- `query: str` — natural language search query
- `top_k: int` — number of results (default configurable)
- `branch: str` — optional git branch for branch-aware search

---

## Implementation Approach

### Option A — Static Tool Registration

Register each tool as a separate `@mcp.tool()` decorated function in `rag_mcp.py`. Each function calls the shared `_search()` helper with a hardcoded `node_type` filter.

```python
@mcp.tool()
async def search_method_decl(query: str, top_k: int = 5, branch: str = "") -> str:
    """Find method/procedure declarations (interface signatures, parameters)."""
    return await _search(query, top_k, branch, node_type_filter=["declProc", "class_summary", "class_summary_split"])

@mcp.tool()
async def search_method_def(query: str, top_k: int = 5, branch: str = "") -> str:
    """Find method/procedure implementations (body/code)."""
    return await _search(query, top_k, branch, node_type_filter=["defProc", "method_group"])
```

**Pros:** Explicit, discoverable by MCP clients via `list_tools`, no config changes needed.  
**Cons:** Hard-coded in `rag_mcp.py` — adding a new tool requires code change.

### Option B — Config-Driven Tool Registration

Define additional tools in `config.py` as a list of dicts:

```python
MCP_EXTRA_TOOLS = [
    {
        "name": "search_method_decl",
        "description": "Find method/procedure declarations...",
        "node_type_filter": ["declProc", "class_summary", "class_summary_split"],
    },
    ...
]
```

`rag_mcp.py` reads `MCP_EXTRA_TOOLS` at startup and dynamically registers them.

**Pros:** No code changes to add new tools — only config changes.  
**Cons:** Dynamic tool registration via FastMCP may be less straightforward; harder to type-check.

**Recommendation:** Start with Option A (explicit) for the first 4–5 tools. Move to Option B if the tool list grows substantially.

---

## Agent Documentation

The tool `description` field in FastMCP is what AI agents (OpenCode, Claude Desktop, etc.) read to decide which tool to call. Well-written descriptions eliminate the need for a separate documentation file.

### Recommended Description Template

```
[ONE-LINE SUMMARY — what this tool finds]

USE THIS TOOL WHEN:
- [specific use case 1]
- [specific use case 2]

DO NOT USE THIS TOOL FOR:
- [anti-case — use search_X instead]

Returns: [what the output looks like]
```

### Example: `search_method_decl`

```
Find method and procedure DECLARATIONS in Delphi Pascal source code.
Returns interface-section signatures with parameter names, types, and
visibility (public/private/protected/published).

USE THIS TOOL WHEN:
- You need to know what parameters a method accepts
- You need to find where a method is declared (which class/unit)
- You need to see the method signature without the implementation body

DO NOT USE THIS TOOL FOR:
- Finding the method body/code — use search_method_def instead
- Finding SQL procedures — use search_sql instead

Returns: code chunks with file path, class name, line number.
```

### Agent Decision Guide (in-tool or README)

A concise decision table should be included in either the `MCP_TOOL_DESCRIPTION` of the main `search_rag` tool or in a companion agent prompt:

```
Tool selection guide:
- Class structure / "what is TMyClass?" → search_class
- Method signature / parameters → search_method_decl  
- Method body / implementation → search_method_def
- SQL procedure / function / trigger → search_sql
- Form layout / component list → search_form
- Unit dependencies / uses clause → search_uses
- Everything else / cross-cutting → search_rag (main tool)
```

---

## Implementation Notes

- The Qdrant metadata filter for `node_type` uses `FieldCondition` with `MatchAny` (list of values) — already used in the branch-aware deduplication logic in `rag_mcp.py`
- The reranker (`shared/reranker.py`) should still run on filtered results — it provides additional score adjustments that remain useful even after pre-filtering
- `top_k` default for specialized tools can be lower (3–5) since pre-filtering increases precision
- The `MCP_EXTRA_TOOLS` config approach (Option B) pairs well with **TODO #5** (model tracking): the config can also store model metadata alongside tool definitions

---

## Related TODOs
- **TODO #5** — Model tracking in collection metadata does not block this TODO; tools can be added independently
