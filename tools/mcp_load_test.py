#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Concurrent-client load test for the HTTP MCP server.

Opens N independent MCP sessions (streamable HTTP) and lets each one call
the search tool in a loop over a query list. Reports throughput and latency
percentiles per concurrency level. Read-only: it only calls tools.

Examples:
    python tools/mcp_load_test.py --url http://127.0.0.1:8123/mcp
    python tools/mcp_load_test.py --url http://127.0.0.1:8123/mcp \
        --clients 1,4,8,16 --requests 32 --queries queries.txt --json out.json

Queries come from --queries (one per line) or a small generic built-in list.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

DEFAULT_QUERIES = [
    "where is the configuration file parsed",
    "function that opens a network connection",
    "error handling when a file cannot be read",
    "class responsible for logging",
    "how are command line arguments handled",
    "memory allocation helper",
    "unit test for string parsing",
    "retry with exponential backoff",
]


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct / 100.0
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


async def _client(url: str, tool: str, queries: list[str], n: int, offset: int,
                  top_k: int, branch: str, latencies: list[float], errors: list[str],
                  barrier: asyncio.Event) -> None:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(url, timeout=600, sse_read_timeout=600) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await barrier.wait()
            for i in range(n):
                q = queries[(offset + i) % len(queries)]
                args = {"query": q, "top_k": top_k}
                if branch:
                    args["branch"] = branch
                t0 = time.perf_counter()
                try:
                    res = await session.call_tool(tool, args)
                    if getattr(res, "isError", False):
                        errors.append(str(res.content)[:200])
                        continue
                except Exception as exc:  # noqa: BLE001 - counted and reported
                    errors.append(f"{type(exc).__name__}: {exc}"[:200])
                    continue
                latencies.append(time.perf_counter() - t0)


async def run_level(url: str, tool: str, queries: list[str], clients: int, requests: int,
                    top_k: int, branch: str) -> dict:
    latencies: list[float] = []
    errors: list[str] = []
    barrier = asyncio.Event()
    per_client = max(1, requests // clients)
    tasks = [
        asyncio.create_task(
            _client(url, tool, queries, per_client, c * per_client, top_k, branch,
                    latencies, errors, barrier)
        )
        for c in range(clients)
    ]
    await asyncio.sleep(1.0)  # sessions initialize before the clock starts
    t0 = time.perf_counter()
    barrier.set()
    await asyncio.gather(*tasks)
    wall = time.perf_counter() - t0
    return {
        "clients": clients,
        "requests": len(latencies),
        "errors": len(errors),
        "first_errors": errors[:3],
        "wall_s": round(wall, 3),
        "throughput_rps": round(len(latencies) / wall, 3) if wall > 0 else None,
        "latency_mean_s": round(statistics.fmean(latencies), 3) if latencies else None,
        "latency_p50_s": round(_percentile(latencies, 50), 3),
        "latency_p95_s": round(_percentile(latencies, 95), 3),
        "latency_max_s": round(max(latencies), 3) if latencies else None,
    }


async def main_async(args) -> list[dict]:
    queries = DEFAULT_QUERIES
    if args.queries:
        queries = [q.strip() for q in Path(args.queries).read_text(encoding="utf-8").splitlines() if q.strip()]
    results = []
    if args.warmup:
        await run_level(args.url, args.tool, queries, 1, args.warmup, args.top_k, args.branch)
    for level in [int(x) for x in args.clients.split(",") if x.strip()]:
        requests = max(args.requests, level)
        res = await run_level(args.url, args.tool, queries, level, requests, args.top_k, args.branch)
        print(
            f"clients={res['clients']:>3} requests={res['requests']:>4} errors={res['errors']} "
            f"rps={res['throughput_rps']} p50={res['latency_p50_s']}s "
            f"p95={res['latency_p95_s']}s max={res['latency_max_s']}s",
            flush=True,
        )
        results.append(res)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default="http://127.0.0.1:8123/mcp")
    ap.add_argument("--tool", default="search_rag")
    ap.add_argument("--clients", default="1,4,8,16")
    ap.add_argument("--requests", type=int, default=32, help="requests per level (split across clients)")
    ap.add_argument("--warmup", type=int, default=4)
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--branch", default="")
    ap.add_argument("--queries", help="file with one query per line")
    ap.add_argument("--json", help="write results to this file")
    args = ap.parse_args()
    results = asyncio.run(main_async(args))
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0 if all(r["errors"] == 0 for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
