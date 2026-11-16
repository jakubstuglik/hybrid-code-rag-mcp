"""Repo-only config for the Django retrieval benchmark (HCR quickstart).

Index only the library package. The official test suite lives in the
top-level tests/ directory, which is outside this SOURCE_DIRS entry.
"""

SOURCE_DIRS = [
    {
        "path": "django",
        "extensions": [".py"],
        "excludes": [],
    }
]

MCP_SERVER_NAME = "django-bench-rag"
MCP_TOOL_NAME = "search_django"
MCP_TOOL_DESCRIPTION = (
    "Search the Django 6.1.3 library package (commit "
    "f16e25dcb9fe55734ba4ea2b00ac34405b7df74a) with hybrid BM25 + dense retrieval."
)
MCP_INDEX_STATE_TOOL_NAME = "get_django_index_state"
