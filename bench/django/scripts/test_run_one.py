#!/usr/bin/env python3
"""Unit tests for run_one.py tool-call classification and control rules.

Event shapes are copied from Grok 1.0.70 streaming-json in the v2 pilot
(logs/v2-pilot/raw). Run: python scripts/test_run_one.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_one  # noqa: E402


def ev(tool: str, raw: dict) -> dict:
    return {"type": "tool_call", "toolCallId": "c", "toolName": tool, "rawInput": raw}


def use(inner: str, tool_input: dict) -> dict:
    return ev("use_tool", {"tool_name": inner, "tool_input": tool_input})


def classes(events: list[dict]) -> list[str]:
    return [c["class"] for c in run_one.collect_tool_calls(events)]


class Classification(unittest.TestCase):
    def test_builtin_tools(self):
        self.assertEqual(
            classes([ev("grep", {"pattern": "x"}), ev("read_file", {"target_file": "a"}),
                     ev("list_dir", {"target_directory": "d"})]),
            ["retrieval", "read", "other"],
        )

    def test_mcp_catalog_is_other(self):
        self.assertEqual(classes([ev("search_tool", {"query": "serena find symbol", "limit": 5})]), ["other"])

    def test_hcr_search_is_retrieval(self):
        self.assertEqual(classes([use("django-bench-rag__search_django", {"query": "q", "top_k": 8})]), ["retrieval"])

    def test_claude_context(self):
        self.assertEqual(
            classes([
                use("claude-context__search_code", {"path": "C:\\x", "query": "q"}),
                use("claude-context__get_indexing_status", {"path": "C:\\x"}),
                use("claude-context__index_codebase", {"path": "C:\\x"}),
            ]),
            ["retrieval", "other", "other"],
        )

    def test_serena_repl_by_code(self):
        self.assertEqual(
            classes([
                use("serena__initial_instructions", {}),
                use("serena__serena_repl", {"session": "s", "code": 's.info("lsp.find_symbol")'}),
                use("serena__serena_repl", {"session": "s", "code": 's.lsp.find_symbol("X", include_body=True)'}),
                use("serena__serena_repl", {"session": "s", "code": 's.fs.search_for_pattern("X")'}),
                use("serena__serena_repl", {"session": "s", "code": 's.lsp.get_symbols_overview("a.py")'}),
                use("serena__serena_repl", {"session": "s", "code": 's.fs.read_file("a.py", start_line=0)'}),
            ]),
            ["other", "other", "retrieval", "retrieval", "retrieval", "read"],
        )

    def test_inner_name_recorded(self):
        calls = run_one.collect_tool_calls([use("django-bench-rag__search_django", {"query": "q"})])
        self.assertEqual(calls[0]["inner"], "django-bench-rag__search_django")

    def test_updates_not_double_counted(self):
        e = ev("grep", {"pattern": "x"})
        upd = dict(e, type="tool_call_update")
        self.assertEqual(len(run_one.collect_tool_calls([e, upd])), 1)


class Controls(unittest.TestCase):
    def calls(self, *events):
        return run_one.collect_tool_calls(list(events))

    def test_none_any_tool_is_violation(self):
        bad, _ = run_one.control_violations("none", self.calls(ev("read_file", {"target_file": "a"})))
        self.assertTrue(bad)
        self.assertEqual(run_one.control_violations("none", []), (False, []))

    def test_read_only(self):
        ok, _ = run_one.control_violations("read_only", self.calls(ev("read_file", {"target_file": "a"})))
        self.assertFalse(ok)
        bad, _ = run_one.control_violations("read_only", self.calls(ev("grep", {"pattern": "x"})))
        self.assertTrue(bad)

    def test_retrieval_variants_not_checked_here(self):
        self.assertFalse(run_one.control_violations("hcr", self.calls(ev("grep", {"pattern": "x"})))[0])

    def test_none_has_no_builtin_tools(self):
        allowed = set(run_one.VARIANT_TOOLS["none"].split(","))
        denied = set(run_one.VARIANT_DISALLOWED["none"].split(","))
        self.assertTrue(allowed, "allowlist must stay non-empty (empty --tools may fail open)")
        self.assertEqual(allowed - denied, set(), "every allowed built-in must be denied for none")

    def test_read_only_keeps_read_file(self):
        self.assertIn("read_file", run_one.VARIANT_TOOLS["read_only"].split(","))
        self.assertNotIn("read_file", run_one.VARIANT_DISALLOWED["read_only"].split(","))
        self.assertIn("grep", run_one.VARIANT_DISALLOWED["read_only"].split(","))


class LoomVariant(unittest.TestCase):
    def test_registered(self):
        self.assertIn("loom", run_one.VARIANTS)
        self.assertEqual(run_one.VARIANT_TOOLS["loom"], run_one.VARIANT_TOOLS["hcr"])
        self.assertEqual(run_one.VARIANT_DISALLOWED["loom"], run_one.VARIANT_DISALLOWED["hcr"])

    def test_classification(self):
        self.assertEqual(
            classes([use("loom__" + t, {}) for t in (
                "loom_code_search", "loom_code_grep", "loom_code_symbol", "loom_code_callers",
                "loom_code_context_pack", "loom_code_outline", "loom_code_enclosing")]),
            ["retrieval"] * 5 + ["read"] * 2,
        )

    def test_allowed_and_banned_disjoint(self):
        self.assertFalse(set(run_one.LOOM_ALLOWED) & set(run_one.LOOM_BANNED))
        self.assertIn("loom_context_pack", run_one.LOOM_BANNED)
        self.assertIn("loom_code_context_pack", run_one.LOOM_ALLOWED)

    def test_deny_rules_in_command(self):
        import argparse
        a = argparse.Namespace(grok="grok", checkout="C:/x", system_prompt_text="p", schema_text="{}", variant="loom")
        cmd = run_one.planned_command(a, {"question": "q"}, "s")
        denies = [cmd[i + 1] for i, x in enumerate(cmd) if x == "--deny"]
        for t in run_one.LOOM_BANNED:
            self.assertIn(f"MCPTool(loom__{t})", denies)
        a.variant = "hcr"
        self.assertNotIn("--deny", run_one.planned_command(a, {"question": "q"}, "s"))

    def test_banned_call_is_violation(self):
        calls = run_one.collect_tool_calls([use("loom__loom_code_ask", {"question": "q"})])
        self.assertTrue(run_one.control_violations("loom", calls)[0])

    def test_denied_banned_call_is_not_violation(self):
        # Shape from the Grok 1.0.91 smoke run (Q3P01, 23.11).
        e = dict(use("loom__loom_context_pack", {"query": "q"}), toolCallId="c1")
        upd = {"type": "tool_call_update", "toolCallId": "c1", "status": "failed", "content": [
            {"type": "content", "content": {"type": "text", "text":
             "Tool `use_tool` was not executed: Denied by permission policy: deny rule on mcp matching \"loom__loom_context_pack\""}}]}
        calls = run_one.collect_tool_calls([e, upd])
        run_one.mark_call_outcomes(calls, [e, upd])
        self.assertTrue(calls[0]["denied"] and calls[0]["failed"])
        bad, notes = run_one.control_violations("loom", calls)
        self.assertFalse(bad)
        self.assertIn("denied", notes[0])
        ok = run_one.collect_tool_calls([use("loom__loom_code_search", {"query": "q"})])
        self.assertFalse(run_one.control_violations("loom", ok)[0])

    def test_loom_call_elsewhere_is_violation(self):
        calls = run_one.collect_tool_calls([use("loom__loom_code_search", {"query": "q"})])
        self.assertTrue(run_one.control_violations("hcr", calls)[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
