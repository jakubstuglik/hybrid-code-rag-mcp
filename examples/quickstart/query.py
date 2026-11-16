#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One-shot search against the quickstart HTTP MCP server.

Run from the app container (recommended):

    docker compose exec app python examples/quickstart/query.py \
        "how is the discount calculated?"

Or from a host that has the `mcp` package and can reach the server:

    python examples/quickstart/query.py --url http://127.0.0.1:8125/mcp \
        "how is the discount calculated?"
"""

from __future__ import annotations

import argparse
import asyncio
import sys


async def _search(url: str, tool: str, query: str, top_k: int) -> int:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(url, timeout=120, sse_read_timeout=120) as (
        read,
        write,
        _,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()
            arguments: dict = {}
            if "index_state" not in tool:
                arguments = {"query": query, "top_k": top_k}
            result = await session.call_tool(tool, arguments)
            if getattr(result, "isError", False):
                print(f"Tool error: {result.content}", file=sys.stderr)
                return 1
            for block in result.content or []:
                text = getattr(block, "text", None)
                if text:
                    print(text)
            return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the quickstart MCP server.")
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Search query, in English (not required for an index-state tool).",
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8125/mcp",
        help="Streamable HTTP MCP URL (default: http://127.0.0.1:8125/mcp).",
    )
    parser.add_argument("--tool", default="search_quickstart")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    return asyncio.run(_search(args.url, args.tool, args.query, args.top_k))


if __name__ == "__main__":
    sys.exit(main())
