"""
shared.query_shape -- Query shape and the hybrid alpha that follows from it.

``HYBRID_ALPHA_MODE`` selects how the dense/sparse weight is chosen:

``"fixed"`` (default)
    Every query uses ``HYBRID_ALPHA`` (or an explicit base override). This is
    the behaviour of earlier versions: the same alpha, the same retriever
    kwargs.

``"adaptive"``
    Each query is classified as ``identifier``, ``mixed`` or ``natural`` and
    gets that class's alpha. Orthogonal to ``HYBRID_FUSION``: minmax, rrf and
    dbsf all consume the chosen number as their existing dense weight.
    Natural-language queries keep ``HYBRID_ALPHA`` unless
    ``HYBRID_ALPHA_NL`` is set, so a descriptive question does not move.
    Identifier-like queries use ``HYBRID_ALPHA_IDENT`` (default 0.3), which
    gives BM25 more of the blend. No classifier and no model: the rules
    below are the whole decision.

Classification
--------------
Identifier-like tokens reuse the code-identifier patterns from
``shared.reranker`` (``_QUALIFIED_IDENT``, ``_SNAKE_IDENT``,
``_CAMEL_IDENT``, ``_PASCAL_IDENT``, ``_FILE_EXTENSIONS``) and the symbol
lookup in ``shared.retrieval`` (``_KEYWORD_TARGET``, ``_CALL_FORM``,
``_BACKTICKED``, and ``_SYMBOL_STOP_WORDS``). A token counts when it is:

* snake_case, including a leading underscore and ``SCREAMING_SNAKE``
  (the reranker ``_SNAKE_IDENT`` pattern);
* camelCase, PascalCase with an inner capital, or any other single token
  with an inner capital (``HTTPServer``, ``IDisposable``) — the reranker
  camel/Pascal patterns plus one pattern for the shapes those two skip;
* ALL_CAPS of at least 3 characters (letters, digits, underscore), except
  a function word (``THE``, ``HOW``);
* a qualified name ``a::b``, ``a->b`` or ``a.b``, with the reranker's dot
  rule (a dotted name whose member is a file extension, or either side
  shorter than 2 characters, is not a qualified name);
* a call ``name()`` or ``a.b()``. ``name()`` uses the symbol-lookup call
  pattern (at least 3 characters, not a symbol-lookup stop word).
  ``a.b()`` counts even when the pieces are shorter than that;
* a path with a code extension (``foo/bar.c``, ``include/linux/sched.h``),
  a glob (``*.h``) or a dotted file name (``sched.h``). Extensions are the
  reranker's ``_FILE_EXTENSIONS`` set;
* a backticked name, with the symbol-lookup length and stop-word rule;
* a PHP variable ``$var``;
* a preprocessor directive ``#include``, ``#define``, ``#if``, ``#ifdef``,
  ``#ifndef``, ``#elif``, ``#endif``, ``#undef`` or ``#pragma``;
* a keyword form the symbol lookup already accepts (``struct foo``,
  ``function main``, ...), same length and stop-word rule;
* a leading-dunder identifier (``__init__``, ``__schedule``), the shape
  the C/C++ rerank profile adds on top of the core patterns.

A plain word is a run of letters (Unicode letters count, digits and
punctuation do not). Stop words are the symbol-lookup stop list plus a
short list of English function words. They still count toward the
natural-language word total. They do not count toward the plain-word
budget next to an identifier.

* ``identifier`` — at least one identifier-like token, and at most 3
  plain words outside those tokens that are not stop words. A query that
  is only a path or a symbol has no plain words left, so it is
  ``identifier``.
* ``natural`` — no identifier-like token, and at least 4 plain words.
* ``mixed`` — everything else. That includes a sentence that also names a
  symbol, a plain query of fewer than 4 words, an empty string, whitespace,
  numbers and punctuation.

A fully capitalized English sentence is ``identifier`` when its content
words are ALL_CAPS tokens of 3 or more characters. Function words in caps
stay stop words.

Alpha
-----
* ``HYBRID_ALPHA_IDENT`` — identifier queries. Default 0.3. Omitted and
  ``None`` both mean 0.3. A number in [0, 1]. ``bool`` and strings are
  rejected.
* ``HYBRID_ALPHA_MIXED`` — mixed queries. Default ``None``, which means
  the base alpha.
* ``HYBRID_ALPHA_NL`` — natural queries. Default ``None``, which means
  the base alpha.

The base alpha is ``HYBRID_ALPHA`` (default 0.5). An explicit base, such as
``validate_rag.py --alpha``, replaces that base for mixed and natural
defaults and, in fixed mode, is the alpha for every query.
``HYBRID_ALPHA_IDENT`` does not follow ``--alpha``. An explicit mixed or
natural value does not follow ``--alpha`` either.

Unknown ``HYBRID_ALPHA_MODE`` raises ``ValueError``, same as an unknown
``HYBRID_FUSION``. A dense-only collection ignores the mode.
"""

import math
import re
from typing import Any, Dict, Optional, Tuple

from shared.reranker import (
    _CAMEL_IDENT,
    _FILE_EXTENSIONS,
    _PASCAL_IDENT,
    _QUALIFIED_IDENT,
    _SNAKE_IDENT,
)
from shared.retrieval import (
    _BACKTICKED,
    _CALL_FORM,
    _KEYWORD_TARGET,
    _SYMBOL_STOP_WORDS,
)

ALPHA_MODES = ("fixed", "adaptive")
DEFAULT_ALPHA_MODE = "fixed"
DEFAULT_ALPHA_IDENT = 0.3
DEFAULT_BASE_ALPHA = 0.5
QUERY_SHAPES = ("identifier", "mixed", "natural")
IDENTIFIER_MAX_PLAIN_WORDS = 3
NATURAL_MIN_WORDS = 4

# English function words. Union with the symbol-lookup stop list is the
# plain-word budget. Domain nouns (scheduler, cache, class, function) are
# not in this set: they count as content next to a symbol.
_FUNCTION_WORDS = frozenset(
    """
    a an the is of to in on by or it be as at its was were been being
    do did can could would should will than then there here also such only
    over after before between within without across per via not no we our
    you your they their these those who whom whose why about but if so just
    out up down during while because until onto off own same other another
    each every both few more most some any all
    """.split()
)
_PLAIN_STOP_WORDS = _SYMBOL_STOP_WORDS | _FUNCTION_WORDS

# Inner capital the two reranker patterns miss (HTTPServer, IDisposable).
_INNER_CAPITAL = re.compile(r"(?<![\w$])([A-Za-z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*)(?![\w$])")
# ALL_CAPS of at least 3 characters. Function words are filtered afterwards.
_ALL_CAPS = re.compile(r"(?<![\w$])([A-Z][A-Z0-9_]{2,})(?![\w$])")
# __schedule / __init__, always on (the C/C++ profile adds the same shape).
_DUNDER = re.compile(r"(?<![\w$])(__[A-Za-z][\w$]*)(?![\w$])")
# PHP $var / $sessionId.
_PHP_VAR = re.compile(r"(?<![\w\\])(\$[A-Za-z_][\w$]*)")
# a.b(  — short pieces count; the reranker drops short dotted names.
_DOT_CALL = re.compile(
    r"(?<![\w$])([A-Za-z_][\w$]*)\s*\.\s*(~?[A-Za-z_][\w$]*)\s*\("
)
_PREPROC = re.compile(
    r"(?<![\w$])#\s*(?:include|define|ifdef|ifndef|undef|pragma|elif|endif|if)\b",
    re.IGNORECASE,
)
_WORD = re.compile(r"[^\W\d_]+")


def _extension_group() -> str:
    exts = sorted(_FILE_EXTENSIONS, key=len, reverse=True)
    return "(?:" + "|".join(re.escape(ext) for ext in exts) + ")"


_EXT_GROUP = _extension_group()
# sched.h, *.h — a slash before the name belongs to the path pattern instead.
_DOTTED_FILE = re.compile(
    rf"(?<![\w/\\])([A-Za-z0-9_*?][\w*-]*\.{_EXT_GROUP})(?![\w])",
    re.IGNORECASE,
)
# include/linux/sched.h, foo/bar.c, src/*.h
_SLASH_PATH = re.compile(
    rf"(?<![\w])((?:[A-Za-z0-9_.*?-]+[/\\])+[A-Za-z0-9_.*?-]*\.{_EXT_GROUP})(?![\w])",
    re.IGNORECASE,
)


def _merge_spans(spans):
    """Merge overlapping [start, end) spans."""
    if not spans:
        return []
    ordered = sorted(spans)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def _overlaps(start: int, end: int, spans) -> bool:
    for span_start, span_end in spans:
        if span_start >= end:
            return False
        if start < span_end and end > span_start:
            return True
    return False


def _identifier_spans(query: str):
    """Spans of identifier-like tokens in ``query`` (original indexes)."""
    spans = []
    for match in _QUALIFIED_IDENT.finditer(query):
        owner, sep, member = match.group(1), match.group(2), match.group(3)
        if sep == "." and (
            member.lower() in _FILE_EXTENSIONS or len(owner) < 2 or len(member) < 2
        ):
            continue
        spans.append(match.span())
    for pattern in (_SNAKE_IDENT, _CAMEL_IDENT, _PASCAL_IDENT, _DUNDER, _PHP_VAR, _DOT_CALL):
        for match in pattern.finditer(query):
            spans.append(match.span())
    for match in _INNER_CAPITAL.finditer(query):
        token = match.group(1)
        # Pure capitals belong to _ALL_CAPS (length >= 3). "OK" is two
        # capitals and is a plain word, not an identifier.
        if any(ch.islower() for ch in token) and token.lower() not in _PLAIN_STOP_WORDS:
            spans.append(match.span())
    for match in _ALL_CAPS.finditer(query):
        if match.group(1).lower() not in _PLAIN_STOP_WORDS:
            spans.append(match.span())
    for match in _CALL_FORM.finditer(query):
        name = match.group(1)
        if name.lower() not in _SYMBOL_STOP_WORDS:
            spans.append(match.span())
    for match in _BACKTICKED.finditer(query):
        name = match.group(1)
        if len(name) >= 3 and name.lower() not in _SYMBOL_STOP_WORDS:
            spans.append(match.span())
    for match in _KEYWORD_TARGET.finditer(query):
        name = match.group(1)
        if len(name) >= 3 and name.lower() not in _SYMBOL_STOP_WORDS:
            spans.append(match.span(1))
    for pattern in (_DOTTED_FILE, _SLASH_PATH, _PREPROC):
        for match in pattern.finditer(query):
            spans.append(match.span())
    return _merge_spans(spans)


def classify_query(query: str) -> str:
    """Classify ``query`` as ``identifier``, ``mixed`` or ``natural``.

    ``None``, ``""`` and whitespace are ``mixed``. See the module docstring
    for the token and word-count rules.
    """
    if not isinstance(query, str):
        query = "" if query is None else str(query)
    if not query.strip():
        return "mixed"
    spans = _identifier_spans(query)
    plain_all = 0
    plain_content = 0
    for match in _WORD.finditer(query):
        if _overlaps(match.start(), match.end(), spans):
            continue
        plain_all += 1
        if match.group(0).lower() not in _PLAIN_STOP_WORDS:
            plain_content += 1
    if spans and plain_content <= IDENTIFIER_MAX_PLAIN_WORDS:
        return "identifier"
    if not spans and plain_all >= NATURAL_MIN_WORDS:
        return "natural"
    return "mixed"


def resolve_hybrid_alpha_mode(cfg: Any) -> str:
    """``"fixed"`` or ``"adaptive"``.

    Missing ``HYBRID_ALPHA_MODE`` and a missing config are ``"fixed"``.
    Any other value raises ``ValueError``.
    """
    raw = getattr(cfg, "HYBRID_ALPHA_MODE", None) if cfg is not None else None
    if raw is None:
        mode = DEFAULT_ALPHA_MODE
    elif isinstance(raw, str):
        mode = raw.strip().lower()
    else:
        mode = None
    if mode not in ALPHA_MODES:
        listed = ", ".join(repr(item) for item in ALPHA_MODES)
        raise ValueError(f"HYBRID_ALPHA_MODE must be one of {listed}, got {raw!r}.")
    return mode


def _as_unit_interval(name: str, value: Any) -> float:
    """A finite float in [0, 1]. Booleans and strings are rejected."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number in [0, 1], got {value!r}.")
    number = float(value)
    if not math.isfinite(number) or number < 0.0 or number > 1.0:
        raise ValueError(f"{name} must be a number in [0, 1], got {value!r}.")
    return number


def _base_alpha(cfg: Any, base_alpha: Optional[float]) -> Any:
    """Explicit base, else ``HYBRID_ALPHA``, else 0.5.

    The base is not range-checked: fixed mode has always passed
    ``HYBRID_ALPHA`` through as configured.
    """
    if base_alpha is not None:
        return base_alpha
    if cfg is None:
        return DEFAULT_BASE_ALPHA
    raw = getattr(cfg, "HYBRID_ALPHA", DEFAULT_BASE_ALPHA)
    if raw is None:
        return DEFAULT_BASE_ALPHA
    return raw


def _optional_alpha(cfg: Any, name: str, base: Any) -> Any:
    """``None`` or a missing attribute means ``base``."""
    raw = getattr(cfg, name, None) if cfg is not None else None
    if raw is None:
        return base
    return _as_unit_interval(name, raw)


def resolve_hybrid_alphas(cfg: Any, base_alpha: Optional[float] = None) -> Dict[str, Any]:
    """``identifier`` / ``mixed`` / ``natural`` alphas for ``cfg``.

    Raises ``ValueError`` for an out-of-range, boolean or string class
    alpha. ``HYBRID_ALPHA_IDENT`` omitted or ``None`` is 0.3.
    ``HYBRID_ALPHA_MIXED`` and ``HYBRID_ALPHA_NL`` omitted or ``None`` use
    the base alpha (``base_alpha`` when given, else ``HYBRID_ALPHA``).
    """
    base = _base_alpha(cfg, base_alpha)
    raw_ident = getattr(cfg, "HYBRID_ALPHA_IDENT", None) if cfg is not None else None
    if raw_ident is None:
        ident: Any = DEFAULT_ALPHA_IDENT
    else:
        ident = _as_unit_interval("HYBRID_ALPHA_IDENT", raw_ident)
    return {
        "identifier": ident,
        "mixed": _optional_alpha(cfg, "HYBRID_ALPHA_MIXED", base),
        "natural": _optional_alpha(cfg, "HYBRID_ALPHA_NL", base),
    }


def validate_hybrid_alpha_settings(cfg: Any) -> None:
    """Raise ``ValueError`` when the mode or a class alpha is invalid.

    Missing keys are the defaults. Config load calls this for every
    collection mode, so a typo fails before the first query.
    """
    resolve_hybrid_alpha_mode(cfg)
    resolve_hybrid_alphas(cfg)


def alpha_for_query(
    cfg: Any, query: str, base_alpha: Optional[float] = None
) -> Tuple[str, Any]:
    """``(shape, alpha)`` actually used for ``query``.

    Fixed mode returns the base alpha for every shape. Adaptive mode
    returns the class alpha. ``base_alpha`` replaces ``HYBRID_ALPHA`` for
    the mixed and natural defaults and is the fixed-mode alpha; it does
    not replace ``HYBRID_ALPHA_IDENT`` or an explicit mixed / natural value.
    """
    shape = classify_query(query)
    mode = resolve_hybrid_alpha_mode(cfg)
    # Validates the class alphas in both modes so a bad setting fails even
    # when the caller did not go through config load.
    alphas = resolve_hybrid_alphas(cfg, base_alpha=base_alpha)
    if mode != "adaptive":
        return shape, _base_alpha(cfg, base_alpha)
    return shape, alphas[shape]


def adaptive_result_fields(
    cfg: Any, query: str, base_alpha: Optional[float], hybrid: bool
) -> Dict[str, Any]:
    """Per-test validation fields. Empty unless hybrid and adaptive.

    Fixed mode and a dense collection return ``{}`` so JSON output keeps
    its previous keys.
    """
    if not hybrid or resolve_hybrid_alpha_mode(cfg) != "adaptive":
        return {}
    shape, used = alpha_for_query(cfg, query, base_alpha=base_alpha)
    return {"query_shape": shape, "alpha": used}
