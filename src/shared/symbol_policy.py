# Copyright 2025-2026 Jakub Stuglik
# SPDX-License-Identifier: Apache-2.0

"""How the ``symbols`` payload list is attached to chunks.

Readers put every name a chunk defines into ``metadata["symbols"]`` (the
exact symbol lookup and the reranker read it). When a long chunk is split
into parts, each part used to inherit the whole list. For generated headers
with tens of thousands of ``#define`` lines that multiplies the list by the
number of parts: gigabytes of payload, slow Qdrant upserts and a symbol
lookup that matches every part of the file.

Two opt-in settings change that (both off by default, so payloads stay
byte-identical to earlier versions):

* ``SYMBOLS_PER_SPLIT_PART`` - a split part keeps only the symbols that
  appear in its own text (an alias is kept when the name it was derived
  from appears). Changes stored payloads: reindex C/C++ sources after
  enabling it.
* ``SYMBOLS_MAX_PER_CHUNK`` - upper bound on the list length of any chunk
  (0 = no limit). A longer list keeps its first N entries and the chunk
  gets ``symbols_truncated: True``.

The indexer calls ``configure_symbol_policy(config)`` once at start-up;
readers call ``apply_symbol_policy`` when they build chunk metadata.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional

SYMBOLS_KEY = "symbols"
TRUNCATED_KEY = "symbols_truncated"

_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass(frozen=True)
class SymbolPolicy:
    """Settings for the ``symbols`` payload list (defaults = old behaviour)."""

    per_split_part: bool = False
    max_per_chunk: int = 0

    @property
    def is_default(self) -> bool:
        return not self.per_split_part and self.max_per_chunk <= 0


_policy = SymbolPolicy()


def _as_bool(raw: Any) -> bool:
    if isinstance(raw, str):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    return bool(raw)


def _as_limit(raw: Any) -> int:
    if isinstance(raw, bool):
        return 0
    try:
        value = int(raw or 0)
    except (TypeError, ValueError):
        return 0
    return value if value > 0 else 0


def policy_from_config(cfg: Any) -> SymbolPolicy:
    """Read ``SYMBOLS_PER_SPLIT_PART`` / ``SYMBOLS_MAX_PER_CHUNK`` from ``cfg``.

    Missing, invalid, zero or negative values fall back to the defaults.
    """
    return SymbolPolicy(
        per_split_part=_as_bool(getattr(cfg, "SYMBOLS_PER_SPLIT_PART", False)),
        max_per_chunk=_as_limit(getattr(cfg, "SYMBOLS_MAX_PER_CHUNK", 0)),
    )


def configure_symbol_policy(cfg: Any) -> SymbolPolicy:
    """Set the process-wide policy from ``cfg`` and return it."""
    global _policy
    _policy = policy_from_config(cfg)
    return _policy


def set_symbol_policy(policy: SymbolPolicy) -> None:
    """Set the process-wide policy directly (tests, embedding callers)."""
    global _policy
    _policy = policy


def get_symbol_policy() -> SymbolPolicy:
    return _policy


class SymbolMatcher:
    """Find which entries of one ``symbols`` list occur in a piece of text.

    Built once per chunk and queried once per split part, so the cost per
    part follows the part's length, not the length of the list (generated
    headers can list tens of thousands of names per chunk).

    A plain identifier must occur as a whole identifier token (``FOO`` does
    not match ``FOO_BAR``). Other strings (``ns::name``, ``operator+``) must
    occur as a substring not glued to identifier characters. ``anchors``
    maps a derived name (an alias such as ``sys_read``) to the text that
    proves it is present (``read``).
    """

    def __init__(
        self, symbols: List[str], anchors: Optional[Mapping[str, str]] = None
    ) -> None:
        self._symbols = list(symbols)
        self._by_token: Dict[str, List[int]] = {}
        self._other: List[tuple] = []  # (index, compiled pattern)
        for index, sym in enumerate(self._symbols):
            for probe in (sym, (anchors or {}).get(sym)):
                if not probe:
                    continue
                if _IDENT.fullmatch(probe):
                    self._by_token.setdefault(probe, []).append(index)
                else:
                    pattern = re.compile(
                        r"(?<![A-Za-z0-9_])" + re.escape(probe) + r"(?![A-Za-z0-9_])"
                    )
                    self._other.append((index, pattern))

    def kept(self, text: str) -> List[str]:
        """The entries that occur in ``text``, in list order."""
        hits = set()
        for token in set(_IDENT.findall(text)):
            found = self._by_token.get(token)
            if found:
                hits.update(found)
        for index, pattern in self._other:
            if index not in hits and pattern.search(text):
                hits.add(index)
        return [self._symbols[i] for i in sorted(hits)]


def symbols_in_text(
    symbols: Iterable[str],
    text: str,
    anchors: Optional[Mapping[str, str]] = None,
) -> List[str]:
    """The entries of ``symbols`` that occur in ``text`` (see ``SymbolMatcher``)."""
    return SymbolMatcher(list(symbols), anchors).kept(text)


def apply_symbol_policy(
    metadata: Dict[str, Any],
    part_text: Optional[str] = None,
    anchors: Optional[Mapping[str, str]] = None,
    policy: Optional[SymbolPolicy] = None,
    matcher: Optional[SymbolMatcher] = None,
) -> Dict[str, Any]:
    """Return ``metadata`` with the ``symbols`` list shaped by the policy.

    Args:
        metadata: Chunk metadata. Never mutated.
        part_text: Text of a split part; ``None`` for an unsplit chunk
            (``SYMBOLS_PER_SPLIT_PART`` only affects split parts).
        anchors: Derived name -> source name, see ``SymbolMatcher``.
        policy: Defaults to the process-wide policy.
        matcher: A ``SymbolMatcher`` already built for this list; pass one
            when applying the policy to many parts of the same chunk.

    Returns:
        The same object when nothing changes (always the case with the
        default policy), otherwise a shallow copy. A split part that keeps
        no symbols has no ``symbols`` key, like a chunk that defines no
        names.
    """
    pol = policy if policy is not None else _policy
    symbols = metadata.get(SYMBOLS_KEY)
    if pol.is_default or not isinstance(symbols, list):
        return metadata
    kept = symbols
    if pol.per_split_part and part_text is not None:
        m = matcher if matcher is not None else SymbolMatcher(symbols, anchors)
        kept = m.kept(part_text)
    truncated = pol.max_per_chunk > 0 and len(kept) > pol.max_per_chunk
    if truncated:
        kept = kept[: pol.max_per_chunk]
    if kept is symbols and not truncated:
        return metadata
    out = dict(metadata)
    if kept:
        out[SYMBOLS_KEY] = list(kept)
    else:
        out.pop(SYMBOLS_KEY, None)
    if truncated:
        out[TRUNCATED_KEY] = True
    return out
