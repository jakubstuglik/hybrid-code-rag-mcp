# SPDX-License-Identifier: Apache-2.0
"""``asearch`` sends symbol-lookup candidates through branch dedup."""

import asyncio
import types

from llama_index.core.schema import NodeWithScore, TextNode

import shared.search as search_mod


def _cfg():
    return types.SimpleNamespace(
        HYBRID_ALPHA=0.5,
        HYBRID_ALPHA_MODE="fixed",
        RERANK_CROSS_ENCODER_MODEL=None,
        SYMBOL_LOOKUP_SCORE="bar",
        SOURCE_DIRS=[
            {
                "type": "git_repo",
                "path": "repo",
                "main_branch": "main",
                "sources": [{"path": "src", "extensions": [".py"]}],
            }
        ],
    )


def _node(node_id, score, file_path, branch=None):
    metadata = {"file_path": file_path, "node_type": "method_declaration"}
    if branch is not None:
        metadata["branch"] = branch
    inner = TextNode(id_=node_id, text="return 1\n", metadata=metadata)
    return NodeWithScore(node=inner, score=score)


class _Index:
    def __init__(self):
        self.kwargs = None

    def as_retriever(self, **kwargs):
        self.kwargs = kwargs
        return object()


def _pools():
    """Main retrieval plus a symbol leg that mixes good and stale hits.

    ``src/f001.py`` has its overlay copy only on the symbol leg.
    ``src/kept.py`` has its overlay copy only on the main leg.
    ``src/gone.py`` is tombstoned and appears only on the symbol leg.
    """
    nodes = [
        _node("main-f001", 0.9, "src/f001.py", "main"),
        _node("keep", 0.4, "src/keep.py", "main"),
        _node("overlay-kept", 0.7, "src/kept.py", "feat"),
        _node("low", 0.2, "src/low.py", "main"),
        _node("notes-main", 0.3, "docs/notes.md"),
    ]
    extra = [
        _node("sym-gone", None, "src/gone.py", "main"),
        _node("sym-stale-kept", None, "src/kept.py", "main"),
        _node("sym-overlay-f001", None, "src/f001.py", "feat"),
        _node("sym-notes", None, "docs/extra.md"),
    ]
    return nodes, extra


def _install(monkeypatch, nodes, extra):
    async def fake_retrieve(*_args, **_kwargs):
        return nodes, extra

    monkeypatch.setattr(
        "shared.retrieval.aretrieve_with_symbol_lookup", fake_retrieve
    )


def _ids(result):
    return [n.node.node_id for n in result]


def test_asearch_symbol_candidates_follow_branch_dedup(monkeypatch):
    """Overlay search must not return a tombstone or a shadowed main copy."""
    nodes, extra = _pools()
    _install(monkeypatch, nodes, extra)
    lines = []

    result = asyncio.run(
        search_mod.asearch(
            _Index(),
            "storage layout",
            cfg=_cfg(),
            top_k=8,
            hybrid=False,
            profiles=[],
            branch="feat",
            tombstones_for=lambda _name: ["src/gone.py"],
            timeout=None,
            log=lines.append,
        )
    )
    ids = _ids(result)

    assert "sym-gone" not in ids, ids
    assert "sym-stale-kept" not in ids, ids
    assert "main-f001" not in ids, ids
    assert "sym-overlay-f001" in ids
    assert "overlay-kept" in ids
    assert "keep" in ids
    assert "low" in ids
    assert "notes-main" in ids
    assert "sym-notes" in ids
    by_id = {n.node.node_id: n for n in result}
    assert by_id["sym-overlay-f001"].score == 0.2
    assert by_id["sym-notes"].score == 0.2
    assert by_id["overlay-kept"].score == 0.7
    assert any(
        "branch dedup: 5 -> 4 (tombstones=1, symbol_dropped=2)" in line
        for line in lines
    )


def test_asearch_without_branch_merges_symbol_candidates(monkeypatch):
    """No overlay: every symbol hit is appended with the pool's score bar."""
    nodes, extra = _pools()
    _install(monkeypatch, nodes, extra)
    lines = []

    result = asyncio.run(
        search_mod.asearch(
            _Index(),
            "storage layout",
            cfg=_cfg(),
            top_k=9,
            hybrid=False,
            profiles=[],
            branch="",
            timeout=None,
            log=lines.append,
        )
    )

    assert _ids(result) == [
        "main-f001",
        "keep",
        "overlay-kept",
        "low",
        "notes-main",
        "sym-gone",
        "sym-stale-kept",
        "sym-overlay-f001",
        "sym-notes",
    ]
    assert [n.score for n in result] == [
        0.9, 0.4, 0.7, 0.2, 0.3, 0.2, 0.2, 0.2, 0.2,
    ]
    assert not any("branch dedup:" in line for line in lines)
