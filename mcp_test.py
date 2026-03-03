import anyio
from datetime import timedelta
import logging

from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("mcp.client.streamable_http").setLevel(logging.DEBUG)
    print("[CLIENT] connecting...")
    async with streamable_http_client("http://127.0.0.1:8123/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            print("[CLIENT] initializing...")
            try:
                with anyio.fail_after(60):
                    await session.initialize()
            except Exception as exc:
                print(f"[CLIENT] initialize failed: {type(exc).__name__}: {exc}")
                raise
            print("[CLIENT] initialized")
            print("[CLIENT] calling search_informica...")
            try:
                with anyio.fail_after(120):
                    result = await session.call_tool(
                        "search_informica",
                        {
                            "query": (
                                "what is TMoveableOptionsFrame and where it is used in Informica "
                                "(TURDUS) project?"
                            ),
                            "top_k": 8,
                        },
                        read_timeout_seconds=timedelta(seconds=120),
                    )
            except Exception as exc:
                print(f"[CLIENT] tool call failed: {type(exc).__name__}: {exc}")
                raise
            print("[CLIENT] tool response received")
            print(result)


if __name__ == "__main__":
    anyio.run(main)
