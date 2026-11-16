#!/usr/bin/env python3
"""Single-run harness for one (question, variant, repetition).

Refuses to launch Grok, Docker, or MCP servers unless
`--approved-by-operator` is passed.

Controls (v2.1, METHOD.md §18):

- `none` is the pure-memory control: no tools at all (read_file is denied
  too). Any tool call is a protocol violation.
- `read_only` is the read-only control: `read_file` of a path the model
  names itself, but no grep, directory listing, shell, or MCP server.
  This is what `none` was in v1/v2.

MCP calls arrive as the meta-tool `use_tool` with the real tool in
`rawInput.tool_name` (`<server>__<tool>`); they are classified by that
inner tool. Serena 2.x exposes one `serena_repl` tool, so its calls are
classified by the method invoked in the REPL code.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKOUT = r"C:\Apps\hcr-bench\django"
DEFAULT_GROK_HOME = r"C:\Apps\hcr-bench\grok-home"
GROK = r"C:\Users\jakub\.grok\bin\grok.exe"
DEFAULT_SYSTEM_PROMPT_PATH = ROOT / "prompts" / "system.txt"
DEFAULT_SCHEMA_PATH = ROOT / "prompts" / "answer.schema.json"

VARIANTS = ("none", "read_only", "ripgrep", "hcr", "claude_context", "serena")
CONTROL_VARIANTS = ("none", "read_only")

# Built-in tools that must never run in a graded session.
COMMON_DISALLOWED = (
    "Agent,web_search,web_fetch,write,search_replace,StrReplace,"
    "EditNotebook,Delete,GenerateImage,GenerateVideo,XSearch"
)

# MCP meta-tools stay available unless denied (Grok 1.0.70 headless docs).
# search_tool / use_tool are the names the model sees for GetMcpTools / CallMcpTool.
MCP_META_DISALLOW = (
    "search_tool,use_tool,GetMcpTools,CallMcpTool,"
    "FetchMcpResource,ListMcpResources"
)

# Extra denials so a retrieval variant cannot quietly fall back to another.
# `read_only` also loses grep, shell, directory listing, and MCP meta-tools.
# `none` additionally loses read_file: --disallowed-tools wins over --tools,
# so this removes every built-in tool (an empty --tools value is not used
# because some Grok builds treat it as absent and fail open).
_NO_SEARCH = (
    ",grep,run_terminal_cmd,run_terminal_command,Bash,Shell,"
    "list_dir,Glob,find,codebase_search," + MCP_META_DISALLOW
)
VARIANT_DISALLOWED = {
    "none": COMMON_DISALLOWED + _NO_SEARCH + ",read_file,read,view,cat",
    "read_only": COMMON_DISALLOWED + _NO_SEARCH,
    "ripgrep": COMMON_DISALLOWED + "," + MCP_META_DISALLOW,
    "hcr": COMMON_DISALLOWED + ",grep,run_terminal_cmd,run_terminal_command,Bash,Shell",
    "claude_context": COMMON_DISALLOWED + ",grep,run_terminal_cmd,run_terminal_command,Bash,Shell",
    "serena": COMMON_DISALLOWED + ",grep,run_terminal_cmd,run_terminal_command,Bash,Shell",
}

# Built-in tool allow-list. MCP servers are attached via GROK_HOME.
# --tools is an allowlist of built-in tools; MCP meta-tools remain unless denied.
VARIANT_TOOLS = {
    # Non-empty allowlist on purpose; read_file is then removed by the denylist.
    "none": "read_file",
    "read_only": "read_file",
    "ripgrep": "read_file,grep,list_dir,run_terminal_cmd",
    # MCP variants: read + list + the meta-tools that invoke the attached server.
    "hcr": "read_file,list_dir,use_tool,CallMcpTool,search_tool,GetMcpTools",
    "claude_context": "read_file,list_dir,use_tool,CallMcpTool,search_tool,GetMcpTools",
    "serena": "read_file,list_dir,use_tool,CallMcpTool,search_tool,GetMcpTools",
}

RETRIEVAL_TOOLS = {
    "grep", "rg", "ag", "ack", "findstr",
    "search_django", "search_rag", "search_code",
    "find_symbol", "find_declaration", "find_referencing_symbols",
    "find_implementations", "search_for_pattern", "get_symbols_overview",
    "codebase_search",
}
READ_TOOLS = {
    "read_file", "read", "read_file_tool", "cat", "view",
}


def load_question(path: Path, qid: str) -> dict:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["id"] == qid:
            return row
    raise SystemExit(f"question {qid} not found in {path}")


def planned_command(args: argparse.Namespace, question: dict, session_id: str) -> list[str]:
    user = (
        f"{question['question']}\n"
        f"The checkout path is {args.checkout}."
    )
    cmd = [
        args.grok,
        "-p",
        user,
        "--cwd",
        args.checkout,
        "--system-prompt-override",
        args.system_prompt_text,
        "--model",
        "grok-4.7",
        "--reasoning-effort",
        ("high" if args.variant != "none" else os.environ.get("BENCH_NONE_EFFORT", "low")),
        "--max-turns",
        "20",
        "--output-format",
        "streaming-json",
        "--json-schema",
        args.schema_text,
        "--disable-web-search",
        "--no-subagents",
        "--no-plan",
        "--no-auto-update",
        "--permission-mode",
        "bypassPermissions",
        "--disallowed-tools",
        VARIANT_DISALLOWED[args.variant],
        "-s",
        session_id,
    ]
    tools = VARIANT_TOOLS.get(args.variant)
    if tools:
        cmd.extend(["--tools", tools])
    return cmd


def isolated_env(grok_home: str) -> dict[str, str]:
    env = os.environ.copy()
    env["GROK_HOME"] = grok_home
    env["GROK_MEMORY"] = "0"
    env["GROK_DISABLE_AUTOUPDATER"] = "1"
    # ripgrep 15.2.0 may live in the WinGet links dir; make sure a fresh
    # process sees the current Machine+User Path plus that folder.
    extra = [
        r"C:\Users\jakub\AppData\Local\Microsoft\WinGet\Links",
        r"C:\Users\jakub\.local\bin",
        r"C:\Users\jakub\.grok\bin",
    ]
    path = env.get("Path") or env.get("PATH") or ""
    for p in extra:
        if p.lower() not in path.lower():
            path = p + os.pathsep + path
    env["Path"] = path
    env["PATH"] = path
    return env


def extract_json_objects(text: str) -> list[dict]:
    """Best-effort parse of streaming-json (JSONL) plus any embedded objects."""
    objs: list[dict] = []
    if not text:
        return objs
    for line in text.splitlines():
        s = line.strip()
        if not s or s[0] not in "{[":
            continue
        try:
            objs.append(json.loads(s))
        except json.JSONDecodeError:
            continue
    if not objs:
        # maybe the whole stdout is one JSON value
        try:
            val = json.loads(text)
            if isinstance(val, dict):
                objs.append(val)
            elif isinstance(val, list):
                objs.extend(x for x in val if isinstance(x, dict))
        except json.JSONDecodeError:
            pass
    return objs


def _tool_name(ev: dict) -> str | None:
    for key in ("toolName", "tool_name", "tool", "name"):
        v = ev.get(key)
        if isinstance(v, str) and v:
            return v
    fn = ev.get("function")
    if isinstance(fn, dict) and isinstance(fn.get("name"), str):
        return fn["name"]
    return None


def _inner_mcp_name(ev: dict) -> str | None:
    """If this is an MCP meta call (use_tool / CallMcpTool), return the inner tool."""
    raw = ev.get("rawInput") or ev.get("input") or ev.get("arguments") or {}
    if not isinstance(raw, dict):
        return None
    for key in ("tool_name", "tool", "toolName", "name", "mcp_tool", "server_tool"):
        v = raw.get(key)
        if isinstance(v, str) and v:
            return v
    return None


def _strip_server(name: str) -> str:
    """`django-bench-rag__search_django` -> `search_django`."""
    return name.split("__", 1)[1] if "__" in name else name


def _mcp_tool_input(ev: dict) -> dict:
    raw = ev.get("rawInput") or ev.get("input") or ev.get("arguments") or {}
    if not isinstance(raw, dict):
        return {}
    ti = raw.get("tool_input") or raw.get("arguments") or raw.get("input") or {}
    return ti if isinstance(ti, dict) else {}


# Serena 2.x: one `serena_repl` tool; classify by the API called in `code`.
SERENA_RETRIEVAL_RE = re.compile(
    r"\b(find_symbol|find_referencing_symbols|find_implementations|find_declaration|"
    r"search_for_pattern|get_symbols_overview|find_file|find_referencing_code_snippets)\s*\("
)
SERENA_READ_RE = re.compile(r"\bread_file\s*\(")


def classify_serena_repl(code: str) -> str:
    if SERENA_RETRIEVAL_RE.search(code or ""):
        return "retrieval"
    if SERENA_READ_RE.search(code or ""):
        return "read"
    return "other"


def classify_mcp_call(inner: str, tool_input: dict) -> str:
    """Class of an MCP call made through use_tool / CallMcpTool."""
    tool = _strip_server(inner).lower().replace("-", "_")
    if tool == "serena_repl":
        return classify_serena_repl(str(tool_input.get("code") or ""))
    # Index management and onboarding are not retrieval.
    if tool in {"index_codebase", "get_indexing_status", "clear_index",
                "initial_instructions", "onboarding", "check_onboarding_performed"}:
        return "other"
    return classify_tool(tool)


def classify_tool(name: str) -> str:
    n = name.strip()
    key = n.split(".")[-1].lower().replace("-", "_")
    raw = n.lower()
    if key in {t.lower() for t in RETRIEVAL_TOOLS} or raw in {t.lower() for t in RETRIEVAL_TOOLS}:
        return "retrieval"
    if key in {t.lower() for t in READ_TOOLS}:
        return "read"
    if "search" in key or key.startswith("find_") or key in {"rg", "grep"}:
        return "retrieval"
    if "read" in key or key in {"view", "cat"}:
        return "read"
    return "other"


def collect_usage(events: list[dict]) -> dict:
    usage = {}
    for ev in events:
        block = ev.get("usage") or ev.get("modelUsage") or ev.get("model_usage")
        if ev.get("type") in {"end", "result", "usage"} and isinstance(ev.get("usage"), dict):
            block = ev["usage"]
        if isinstance(block, dict):
            usage = block
        # flatten common aliases
        for src, dst in (
            ("input_tokens", "tokens_input"),
            ("inputTokens", "tokens_input"),
            ("output_tokens", "tokens_output"),
            ("outputTokens", "tokens_output"),
            ("cached_read_tokens", "tokens_cache_read"),
            ("cachedReadTokens", "tokens_cache_read"),
            ("cache_read_input_tokens", "tokens_cache_read"),
            ("cache_creation_tokens", "tokens_cache_write"),
            ("cacheCreationTokens", "tokens_cache_write"),
            ("cache_creation_input_tokens", "tokens_cache_write"),
            ("total_tokens", "tokens_total"),
            ("totalTokens", "tokens_total"),
            ("total_cost_usd", "cost_usd"),
            ("totalCostUsd", "cost_usd"),
        ):
            if src in ev and ev[src] is not None:
                usage.setdefault(dst if dst.startswith("tokens") or dst == "cost_usd" else src, ev[src])
                usage[src] = ev[src]
    # Normalise
    out = {}
    def pick(*keys):
        for k in keys:
            if usage.get(k) is not None:
                return usage[k]
        return None
    out["tokens_input"] = pick("tokens_input", "input_tokens", "inputTokens")
    out["tokens_output"] = pick("tokens_output", "output_tokens", "outputTokens")
    out["tokens_cache_read"] = pick("tokens_cache_read", "cached_read_tokens", "cachedReadTokens", "cache_read_input_tokens")
    out["tokens_cache_write"] = pick("tokens_cache_write", "cache_creation_tokens", "cacheCreationTokens", "cache_creation_input_tokens")
    out["tokens_total"] = pick("tokens_total", "total_tokens", "totalTokens")
    out["cost_usd"] = pick("cost_usd", "total_cost_usd", "totalCostUsd")
    if out["cost_usd"] is not None:
        out["cost_source"] = "cli"
    else:
        out["cost_source"] = "unreported"
    if out["tokens_total"] is None:
        parts = [out.get("tokens_input"), out.get("tokens_cache_read"), out.get("tokens_cache_write"), out.get("tokens_output")]
        if any(p is not None for p in parts):
            out["tokens_total"] = sum(int(p or 0) for p in parts)
    return out


MCP_META_TOOLS = {
    "search_tool", "use_tool", "getmcptools", "callmcptool",
    "get_mcp_tools", "call_mcp_tool", "fetchmcpresource",
    "listmcpresources", "fetch_mcp_resource", "list_mcp_resources",
}


def control_violations(variant: str, calls: list[dict]) -> tuple[bool, list[str]]:
    """`none` may not call any tool; `read_only` may only read_file."""
    if variant == "none" and calls:
        return True, ["none (pure memory) issued tool calls: " + ",".join(
            (c.get("inner") or c.get("name") or "?") for c in calls
        )]
    if variant == "read_only":
        bad = [c for c in calls if (c.get("inner") or c.get("name") or "").lower() not in {"read_file", "read"}]
        if bad:
            return True, ["read_only variant issued non-read tools: " + ",".join(
                (c.get("inner") or c.get("name") or "?") for c in bad
            )]
    return False, []


def collect_tool_calls(events: list[dict]) -> list[dict]:
    calls = []
    for ev in events:
        typ = str(ev.get("type") or ev.get("event") or ev.get("kind") or "")
        # Count only the start of a call, not the later tool_call_update events.
        if typ in {"tool_call_update", "tool_result"}:
            continue
        name = _tool_name(ev)
        if typ in {"tool_call", "tool_use", "tool-call", "function_call"}:
            if name:
                is_meta = name.lower() in MCP_META_TOOLS
                inner = _inner_mcp_name(ev) if is_meta else None
                # MCP catalog (GetMcpTools / search_tool) is "other", not retrieval.
                if is_meta and not inner:
                    cls = "other"
                elif inner:
                    cls = classify_mcp_call(inner, _mcp_tool_input(ev))
                else:
                    cls = classify_tool(name)
                calls.append({
                    "name": name,
                    "inner": inner,
                    "class": cls,
                    "raw_type": typ,
                    "raw_input": ev.get("rawInput") or ev.get("input") or {},
                })
            continue
        content = ev.get("content") or (ev.get("message", {}).get("content") if isinstance(ev.get("message"), dict) else ev.get("content"))
        if isinstance(content, list):
            for part in content:
                if not isinstance(part, dict):
                    continue
                ptype = str(part.get("type") or "")
                pname = _tool_name(part)
                if ptype in {"tool_use", "tool_call", "function_call"} and pname:
                    calls.append({"name": pname, "class": classify_tool(pname), "raw_type": ptype or typ})
    return calls


def iter_json_objects(text: str) -> list[str]:
    """Yield top-level JSON object literals, longest-first per start."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        depth = 0
        in_str = False
        esc = False
        for j in range(i, n):
            ch = text[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    out.append(text[i : j + 1])
                    i = j
                    break
        i += 1
    return out


def answer_fields(obj: dict) -> dict:
    spans = obj.get("spans") or obj.get("spans_predicted") or []
    if not isinstance(spans, list):
        spans = []
    return {
        "files": obj.get("files") or obj.get("files_predicted") or [],
        "symbols": obj.get("symbols") or obj.get("symbols_predicted") or [],
        "spans": spans,
        "notes": obj.get("notes") or "",
    }


def extract_answer_from_text(text: str) -> dict | None:
    if not text:
        return None
    # Fenced json first (last fence wins)
    fences = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    candidates = list(fences)
    for blob in iter_json_objects(text):
        if '"files"' in blob or '"symbols"' in blob or '"spans"' in blob:
            candidates.append(blob)
    # A slightly more nested object
    if not candidates:
        start = text.rfind("{")
        if start != -1:
            # walk braces
            depth = 0
            for i in range(start, -1, -1):
                if text[i] == "}":
                    continue
                if text[i] == "{":
                    # try from this i to the last }
                    end = text.rfind("}")
                    if end > i:
                        candidates.append(text[i : end + 1])
                    break
    for blob in reversed(candidates):
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and ("files" in obj or "symbols" in obj or "spans" in obj):
            return answer_fields(obj)
    return None


def assistant_text(events: list[dict], stdout: str) -> str:
    chunks: list[str] = []
    for ev in events:
        typ = str(ev.get("type") or ev.get("event") or "")
        for key in ("text", "content", "delta", "message", "result"):
            val = ev.get(key)
            if isinstance(val, str) and val.strip():
                if typ in {"assistant", "text", "message", "response", "result", "end", "delta"} or key in {"text", "result"}:
                    chunks.append(val)
            elif isinstance(val, dict):
                t = val.get("content") or val.get("text")
                if isinstance(t, str) and t.strip():
                    chunks.append(t)
                elif isinstance(t, list):
                    for part in t:
                        if isinstance(part, str):
                            chunks.append(part)
                        elif isinstance(part, dict) and isinstance(part.get("text"), str):
                            chunks.append(part["text"])
            elif isinstance(val, list):
                for part in val:
                    if isinstance(part, str):
                        chunks.append(part)
                    elif isinstance(part, dict) and isinstance(part.get("text"), str):
                        chunks.append(part["text"])
    if chunks:
        return "\n".join(chunks)
    return stdout or ""


def kill_tree(pid: int) -> None:
    if pid <= 0:
        return
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    else:
        try:
            os.kill(pid, 9)
        except OSError:
            pass


def launch(cmd: list[str], env: dict[str, str], timeout_s: int, log_path: Path, cwd: str) -> dict:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    creationflags = 0
    if sys.platform == "win32":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    # Process cwd must be the subject checkout (no project .grok).
    # Launching from C:\GitRepos\hcr-promo would otherwise attach that
    # repo's project MCP servers (brain-shared, teroplan-phabricator).
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(Path(cwd)),
        creationflags=creationflags,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    status = "ok"
    try:
        stdout, stderr = proc.communicate(timeout=timeout_s)
        rc = proc.returncode
        if rc != 0:
            status = "error"
    except subprocess.TimeoutExpired:
        status = "timeout"
        kill_tree(proc.pid)
        try:
            stdout, stderr = proc.communicate(timeout=15)
        except Exception:
            stdout, stderr = "", ""
        rc = proc.returncode
    wall = time.perf_counter() - t0
    raw = {
        "returncode": rc,
        "status": status,
        "wall_time_s": wall,
        "stdout": stdout or "",
        "stderr": stderr or "",
    }
    log_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return raw


def build_record(args, question, session_id, cmd, env_note, raw: dict) -> dict:
    events = extract_json_objects(raw.get("stdout") or "")
    text = assistant_text(events, raw.get("stdout") or "")
    answer = None
    for ev in reversed(events):
        so = ev.get("structuredOutput") or ev.get("structured_output")
        if isinstance(so, dict) and ("files" in so or "symbols" in so):
            answer = answer_fields(so)
            break
        if isinstance(so, str):
            try:
                obj = json.loads(so)
            except json.JSONDecodeError:
                obj = None
            if isinstance(obj, dict) and ("files" in obj or "symbols" in obj):
                answer = answer_fields(obj)
                break
    if answer is None:
        answer = extract_answer_from_text(text) or extract_answer_from_text(raw.get("stdout") or "")
    calls = collect_tool_calls(events)
    usage = collect_usage(events)
    n_ret = sum(1 for c in calls if c["class"] == "retrieval")
    n_read = sum(1 for c in calls if c["class"] == "read")
    n_other = sum(1 for c in calls if c["class"] == "other")
    protocol_violation, notes = control_violations(args.variant, calls)
    if args.variant == "ripgrep":
        banned = [c["name"] for c in calls if c["name"] not in {"read_file", "grep", "list_dir", "run_terminal_cmd", "rg"} and c["class"] == "retrieval" and "rg" not in c["name"].lower() and "grep" not in c["name"].lower()]
        # MCP tools appearing here would be a leak
        mcpish = [c["name"] for c in calls if any(x in c["name"].lower() for x in ("search_django", "search_code", "find_symbol", "search_for_pattern"))]
        if mcpish:
            protocol_violation = True
            notes.append("ripgrep variant used MCP tools: " + ",".join(mcpish))
    status = raw["status"]
    if status == "error" and any(ev.get("type") == "max_turns_reached" for ev in events if isinstance(ev, dict)):
        # The agent ran out of turns without answering: a scored model outcome (0), not a harness error.
        status = "max_turns"
    if protocol_violation:
        status = "protocol_violation"
    files = (answer or {}).get("files") or []
    symbols = (answer or {}).get("symbols") or []
    spans = (answer or {}).get("spans") or []
    if status in {"timeout", "error", "protocol_violation"} and not files and not symbols:
        pass
    record = {
        "run_id": session_id,
        "question_id": question["id"],
        "variant": args.variant,
        "repetition": args.repetition,
        "status": status,
        "files_predicted": files,
        "symbols_predicted": symbols,
        "spans_predicted": spans,
        "notes": (answer or {}).get("notes") or "",
        "harness_notes": notes,
        "tool_calls": calls,
        "tool_calls_total": len(calls),
        "tool_calls_retrieval": n_ret,
        "tool_calls_read": n_read,
        "tool_calls_other": n_other,
        "wall_time_s": raw["wall_time_s"],
        "returncode": raw.get("returncode"),
        "model": "grok-4.7",
        "session_id": session_id,
        **usage,
        "env": env_note,
        "command": cmd,
    }
    return record, events, text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", required=True)
    ap.add_argument("--id", required=True, help="Question id (E01, P01, X01, ...).")
    ap.add_argument("--variant", required=True, choices=list(VARIANTS))
    ap.add_argument("--repetition", type=int, default=1)
    ap.add_argument("--checkout", default=DEFAULT_CHECKOUT)
    ap.add_argument("--timeout-s", type=int, default=180)
    ap.add_argument("--grok-home", default=DEFAULT_GROK_HOME)
    ap.add_argument("--grok", default=GROK)
    ap.add_argument("--raw-out", help="Write the raw stdout/stderr JSON here.")
    ap.add_argument("--out", help="Write the structured run record JSON here.")
    ap.add_argument(
        "--system-prompt",
        default=str(DEFAULT_SYSTEM_PROMPT_PATH),
        help="System prompt file (default: frozen v1 prompts/system.txt).",
    )
    ap.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help="JSON schema file for the structured answer (default: frozen v1).",
    )
    ap.add_argument(
        "--approved-by-operator",
        action="store_true",
        help="Required to actually launch Grok.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned command and exit 0 without launching.",
    )
    args = ap.parse_args()
    args.system_prompt_text = Path(args.system_prompt).read_text(encoding="utf-8")
    args.schema_text = Path(args.schema).read_text(encoding="utf-8")
    if args.variant == "none":
        # pure-memory control reasons at length without tools; give it more wall time than the tool variants
        args.timeout_s = max(args.timeout_s, 420)
    question = load_question(Path(args.questions), args.id)
    session_id = str(uuid.uuid4())
    cmd = planned_command(args, question, session_id)
    env_note = {
        "GROK_HOME": args.grok_home,
        "GROK_MEMORY": "0",
        "GROK_DISABLE_AUTOUPDATER": "1",
    }
    print("planned env:", json.dumps(env_note))
    print("planned command:")
    print(json.dumps(cmd, indent=2))
    print(f"timeout_s={args.timeout_s} variant={args.variant} repetition={args.repetition}")
    if args.dry_run:
        return 0
    if not args.approved_by_operator:
        print(
            "refusing to launch: pass --approved-by-operator only for an "
            "operator-approved run (pilot or official). Frozen official "
            "questions must not be run until that approval is explicit.",
            file=sys.stderr,
        )
        return 2
    if not Path(args.grok).is_file():
        raise SystemExit(f"grok binary not found: {args.grok}")
    env = isolated_env(args.grok_home)
    raw_path = Path(args.raw_out) if args.raw_out else ROOT / "logs" / "raw" / f"{args.id}__{args.variant}__r{args.repetition}__{session_id}.raw.json"
    raw = launch(cmd, env, args.timeout_s, raw_path, cwd=args.checkout)
    record, events, text = build_record(args, question, session_id, cmd, env_note, raw)
    out_path = Path(args.out) if args.out else ROOT / "logs" / "raw" / f"{args.id}__{args.variant}__r{args.repetition}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": record["status"],
        "question_id": record["question_id"],
        "variant": record["variant"],
        "repetition": record["repetition"],
        "wall_time_s": record["wall_time_s"],
        "files_predicted": record["files_predicted"],
        "symbols_predicted": record["symbols_predicted"],
        "spans_predicted": record.get("spans_predicted") or [],
        "tool_calls_total": record["tool_calls_total"],
        "tool_calls_retrieval": record["tool_calls_retrieval"],
        "out": str(out_path),
        "raw": str(raw_path),
    }))
    return 0 if record["status"] in {"ok", "max_turns"} else 1


if __name__ == "__main__":
    sys.exit(main())
