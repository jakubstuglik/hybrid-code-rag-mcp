# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0
"""Single source of the hybrid-code-rag-mcp version.

The project follows Semantic Versioning in its 0.x form (see CHANGELOG.md):
PATCH = fixes that change neither results nor config; MINOR = new features or
default/behaviour changes, and (before 1.0) also changes that require a
reindex or break config compatibility, flagged "Reindex required" in the
changelog.

This module has no imports so it is cheap to read from anywhere.
"""

__version__ = "0.19.0"

# Manifest keys written by the indexer.  Both are additive: manifests written
# before they existed load and refresh normally, without a reindex.
MANIFEST_VERSION_KEY = "indexer_version"
MANIFEST_FIRST_VERSION_KEY = "first_indexer_version"


def stamp_manifest_version(manifest: dict, version: str = __version__) -> None:
    """Record the indexer version on the main index manifest.

    ``indexer_version`` is overwritten on every run.  ``first_indexer_version``
    is set only when missing: for an index built with ``--clear`` it is the
    version that built it; for a manifest written before versioning existed it
    is the first versioned release that refreshed it.
    """
    manifest[MANIFEST_VERSION_KEY] = version
    if not manifest.get(MANIFEST_FIRST_VERSION_KEY):
        manifest[MANIFEST_FIRST_VERSION_KEY] = version


def manifest_version_line(manifest: dict, server_version: str = __version__) -> str:
    """One markdown line for index-state reports: index vs. running version."""
    indexed = manifest.get(MANIFEST_VERSION_KEY) if isinstance(manifest, dict) else None
    first = manifest.get(MANIFEST_FIRST_VERSION_KEY) if isinstance(manifest, dict) else None
    text = f"- indexer_version: {indexed or 'unknown (index written before 0.10.0)'}"
    if first and first != indexed:
        text += f" (first: {first})"
    return text + f" | server_version: {server_version}"
