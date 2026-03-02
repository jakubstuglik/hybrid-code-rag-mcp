"""Placeholder fix-paths helper for CLI compatibility."""


def fix_absolute_paths() -> None:
    print(
        "Qdrant path fixing moved into qdrant/migrate. Run `uv run python -m qdrant.migrate`."
    )
