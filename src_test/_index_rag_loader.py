# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""Load ``src/index_rag.py`` as a module for unit tests.

``index_rag.py`` is a script: after its function definitions it parses CLI
arguments, loads a config and starts Qdrant/TEI at module level. Importing it
directly would run all of that. This helper compiles only the definitions
part (everything before the first top-level ``if args.dry_run:``) under the
real file name, so coverage is attributed to ``src/index_rag.py``, with a
fake config and no CLI side effects. Nothing here touches Docker, Qdrant,
TEI or the network.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import patch

_SRC = Path(__file__).resolve().parent.parent / "src"
_ROOT = _SRC.parent
INDEX_RAG_PATH = _SRC / "index_rag.py"
_CUT_MARKER = "\nif args.dry_run:"

for _p in (str(_ROOT), str(_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def make_fake_config(tmp_dir: Path, **overrides: Any) -> types.SimpleNamespace:
    """Minimal config namespace used by the indexer functions under test."""
    index_dir = Path(tmp_dir) / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    values: dict[str, Any] = {
        "COLLECTION_NAME": "unit_test_collection",
        "INDEX_EMBED_DEVICE": "cpu",
        "INDEXING_MODE": "dense",
        "HYBRID_EMBED_SINGLE_PASS": True,
        "EMBED_POOL_SIZE": 512,
        "EMBED_POOL_MAX_FILES": 150,
        "EMBED_PIPELINE_DEPTH": 0,
        "EMBED_PARSE_QUEUE_SIZE": 4,
        "QDRANT_UPSERT_BATCH_SIZE": 500,
        "QDRANT_DELETE_TIMEOUT": 60,
        "MODEL_NAME": "unit-test-model",
        "SOURCE_DIRS": [],
        "get_index_path": lambda: str(index_dir),
    }
    values.update(overrides)
    return types.SimpleNamespace(**values)


def load_index_rag(fake_config: Any) -> types.ModuleType:
    """Return a fresh module object with index_rag's definitions loaded."""
    source = INDEX_RAG_PATH.read_text(encoding="utf-8")
    cut = source.find(_CUT_MARKER)
    if cut < 0:
        raise RuntimeError(
            "index_rag.py layout changed: top-level 'if args.dry_run:' not found"
        )
    # Keep line numbers identical to the real file for coverage reports.
    code = compile(source[:cut] + "\n", str(INDEX_RAG_PATH), "exec")

    module = types.ModuleType("index_rag_under_test")
    module.__file__ = str(INDEX_RAG_PATH)
    sys.modules[module.__name__] = module

    import config_loader

    with patch.object(sys, "argv", ["index_rag.py", "--config", "unit-test"]), patch.object(
        config_loader, "get_config", return_value=fake_config
    ):
        exec(code, module.__dict__)
    return module


class FakeQdrantClient:
    """In-memory stand-in for ``QdrantClient`` (records calls only)."""

    def __init__(self, fail_delete_on_calls: set[int] | None = None) -> None:
        self.delete_calls: list[dict] = []
        self.upserted_ids: list[str] = []
        self.update_collection_calls: list[dict] = []
        self._fail_delete_on_calls = fail_delete_on_calls or set()

    def get_collections(self):
        return types.SimpleNamespace(collections=[])

    def get_collection(self, collection_name: str):
        return types.SimpleNamespace(points_count=0)

    def update_collection(self, **kwargs):
        self.update_collection_calls.append(kwargs)

    def delete(self, **kwargs):
        call_no = len(self.delete_calls) + 1
        self.delete_calls.append(kwargs)
        if call_no in self._fail_delete_on_calls:
            raise RuntimeError(f"simulated delete failure on call {call_no}")

    def upsert(self, collection_name: str, points):
        self.upserted_ids.extend(str(p.id) for p in points)

    def count(self, **kwargs):
        return types.SimpleNamespace(count=0)


def delete_filter_parts(call: dict) -> tuple[list[str], str | None]:
    """Return (MatchAny file paths, branch value or None) of a delete call."""
    selector = call["points_selector"]
    paths: list[str] = []
    branch = None
    for cond in selector.must:
        if cond.key == "file_path":
            paths = list(cond.match.any)
        elif cond.key == "branch":
            branch = cond.match.value
    return paths, branch


def install_refresh_fakes(mod, monkeypatch, client, *, load_nodes=None, on_parsed=None):
    """Patch everything ``perform_refresh_qdrant`` reaches outside Python.

    ``load_nodes(file_info) -> list[TextNode]`` replaces the reader pipeline.
    ``on_parsed(documents)`` is called from the main loop, in queue order.
    """
    import qdrant.vector_store as vector_store

    monkeypatch.setattr(mod, "get_qdrant_client", lambda cfg: client)
    monkeypatch.setattr(mod, "get_qdrant_url", lambda cfg: "memory://unit-test")
    monkeypatch.setattr(mod, "get_embed_model", lambda **kw: object())
    monkeypatch.setattr(mod, "check_provenance_for_indexing", lambda *a, **k: None)
    monkeypatch.setattr(mod, "build_branch_resolver", lambda fixed_label=None: (lambda key: None))
    monkeypatch.setattr(mod, "cuda_clear_cache", lambda: None)
    monkeypatch.setattr(mod, "_print_refresh_summary", lambda **kw: None)
    monkeypatch.setattr(vector_store, "detect_collection_mode", lambda c, n: "dense")
    monkeypatch.setattr(
        mod,
        "embed_dense_batch",
        lambda model, docs, **kw: [[0.1, 0.2, 0.3] for _ in docs],
    )

    def _check_truncation(model, documents, verbose=False):
        if on_parsed is not None:
            on_parsed(list(documents))
        return mod.TruncationStats()

    monkeypatch.setattr(mod, "check_truncation", _check_truncation)
    if load_nodes is not None:
        monkeypatch.setattr(mod, "load_nodes_for_file", load_nodes)
