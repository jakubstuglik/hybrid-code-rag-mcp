"""
shared.validation.runner -- Query execution and evaluation logic.

Provides setup() to initialize the retrieval pipeline, run_query() to
execute a single query, and evaluate_test() to score results against
PassCriteria. ``run_query`` delegates to ``shared.search``, the same
pipeline the MCP search tool uses. This module is config-agnostic -- it
works with any project's test cases.
"""

import os
import re
import sys
from typing import List, Optional, Tuple

import config_loader
from shared.embedding import get_embed_model
from qdrant.vector_store import get_qdrant_vector_store, detect_collection_mode
from llama_index.core import VectorStoreIndex
from shared.validation.models import PassCriteria, TestCase, TestResult


# ────────────────────────────────────────────────────────────────────
# Setup
# ────────────────────────────────────────────────────────────────────


def parse_overrides(pairs) -> dict:
    """Parse ``KEY=VALUE`` strings into a dict of config overrides.

    VALUE is read as a Python literal when possible (``20``, ``True``,
    ``["a/*"]``), otherwise kept as a string.
    """
    import ast

    out = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise ValueError(f"Override must be KEY=VALUE, got {pair!r}")
        key, raw = pair.split("=", 1)
        key = key.strip()
        if not key.isidentifier() or key.upper() != key:
            raise ValueError(f"Override key must be an UPPER_CASE config name: {key!r}")
        try:
            out[key] = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            out[key] = raw
    return out


def setup(config_name=None, alpha_override=None, overrides=None):
    """Load config, embedding model, and create the retriever index.

    Args:
        config_name: Config name or path (passed to config_loader).
        alpha_override: Override HYBRID_ALPHA from config. In fixed mode this
            is the alpha for every query. In adaptive mode it replaces
            HYBRID_ALPHA as the base for mixed and natural queries when
            HYBRID_ALPHA_MIXED / HYBRID_ALPHA_NL are unset; HYBRID_ALPHA_IDENT
            stays as configured.
        overrides: Optional dict of config attributes to set after loading
            (experiments / ablations without editing the config file).

    Returns:
        Tuple of (index, mode, alpha, config). ``alpha`` is the base alpha.
    """
    config = config_loader.get_config(config_name=config_name)
    for key, value in (overrides or {}).items():
        setattr(config, key, value)
        print(f"Config override: {key}={value!r}", file=sys.stderr)

    alpha = (
        alpha_override
        if alpha_override is not None
        else getattr(config, "HYBRID_ALPHA", 0.5)
    )

    print(f"Loading embedding model ({config.MODEL_NAME}) on cpu...", file=sys.stderr)
    embed_model = get_embed_model(device="cpu", cfg=config)

    storage_context, client, _ = get_qdrant_vector_store(
        text_key="text", cfg=config, device="cpu"
    )

    mode = detect_collection_mode(client, config.COLLECTION_NAME)
    from shared.query_shape import resolve_hybrid_alpha_mode

    if resolve_hybrid_alpha_mode(config) == "adaptive" and mode == "hybrid":
        alpha_label = f"adaptive (base={alpha})"
    else:
        alpha_label = alpha
    print(
        f"Collection: {config.COLLECTION_NAME}, mode: {mode}, alpha: {alpha_label}",
        file=sys.stderr,
    )

    index = VectorStoreIndex.from_vector_store(
        storage_context.vector_store, embed_model=embed_model
    )

    return index, mode, alpha, config


# ────────────────────────────────────────────────────────────────────
# Query execution
# ────────────────────────────────────────────────────────────────────


def run_query(index, mode, alpha, query, top_k=8, profiles=None, cfg=None, *, branch=""):
    """Execute a single retrieval query and return reranked nodes.

    This is ``shared.search.search``: the same branch filter, over-fetch,
    sparse precompute, symbol lookup, dedup and rerank as the MCP search
    tool. ``branch=""`` searches the configured main branch, matching a
    tool call that leaves ``branch`` empty.

    Args:
        index: VectorStoreIndex instance.
        mode: Collection mode ("hybrid" or "dense"). Only ``"hybrid"``
            turns on the sparse leg, as the MCP server does.
        alpha: Passed as ``base_alpha``. Fixed mode uses it for every
            query. Adaptive mode uses it as the mixed / natural fallback
            when those class settings are unset; ``HYBRID_ALPHA_IDENT``
            stays as configured. The MCP tool does not pass an override,
            so it uses ``HYBRID_ALPHA``. ``setup()`` returns that value
            unless ``--alpha`` replaces it, and passing the returned value
            selects the same retriever alpha as the tool. ``0.0`` is a
            real override, not "unset".
        query: Query text.
        top_k: Number of results to return.
        profiles: Active rerank profiles. None derives them from ``cfg``
            (``rerank_profiles_for_config``). It does not activate every
            registered profile.
        cfg: Loaded config. Required. Retrieval options such as
            ``HYBRID_PREFETCH_K`` and ``RERANK_CROSS_ENCODER_*`` are read
            here so ``--set`` applies. A cross-encoder model widens the
            fused pool before retrieval; per-leg prefetch stays
            ``HYBRID_PREFETCH_K``.
        branch: Overlay name. Empty is the main-branch filter only.

    Returns:
        List of reranked NodeWithScore objects.

    Raises:
        ValueError: If ``cfg`` is None, or a config value the shared
            pipeline validates is illegal.
    """
    from shared.search import search

    return search(
        index,
        query,
        cfg=cfg,
        top_k=top_k,
        hybrid=(mode == "hybrid"),
        base_alpha=alpha,
        profiles=profiles,
        branch=branch,
        verbose=False,
    )


# ────────────────────────────────────────────────────────────────────
# Node matching helpers
# ────────────────────────────────────────────────────────────────────


def _node_matches(node, criteria: PassCriteria) -> bool:
    """Check if a single retrieved node matches ALL specified criteria."""
    meta = node.node.metadata
    content = node.node.get_content() or ""
    node_type = meta.get("node_type", meta.get("type", ""))
    file_path = meta.get("file_path", "")
    class_name = meta.get("class_name", "")

    if criteria.node_types is not None:
        if node_type not in criteria.node_types:
            return False

    if criteria.file_pattern is not None:
        if not re.search(criteria.file_pattern, file_path):
            return False

    if criteria.text_pattern is not None:
        if not re.search(criteria.text_pattern, content):
            return False

    if criteria.class_name_pattern is not None:
        if not re.search(criteria.class_name_pattern, class_name or ""):
            return False

    return True


def _file_matches(node, criteria: PassCriteria) -> bool:
    """Check if just the file_path matches (for PARTIAL evaluation)."""
    if criteria.file_pattern is None:
        return False
    file_path = node.node.metadata.get("file_path", "")
    return bool(re.search(criteria.file_pattern, file_path))


def _type_matches(node, criteria: PassCriteria) -> bool:
    """Check if just the node_type matches (for PARTIAL evaluation)."""
    if criteria.node_types is None:
        return False
    node_type = node.node.metadata.get("node_type", node.node.metadata.get("type", ""))
    return node_type in criteria.node_types


def _text_matches(node, criteria: PassCriteria) -> bool:
    """Check if just the text_pattern matches (for PARTIAL evaluation)."""
    if criteria.text_pattern is None:
        return False
    content = node.node.get_content() or ""
    return bool(re.search(criteria.text_pattern, content))


def first_match_rank(nodes, criteria: PassCriteria, top_n: int) -> Optional[int]:
    """1-based rank of the first full criteria match within ``top_n``.

    ``None`` when no node in that window matches. This is the diagnostic rank.
    It does not apply ``max_position`` / ``partial_position`` and does not
    affect the scored PASS/PARTIAL/FAIL result.
    """
    if top_n < 1:
        return None
    for i, node in enumerate(nodes[:top_n], 1):
        if _node_matches(node, criteria):
            return i
    return None


def top_result_files(nodes, limit: int = 3) -> List[str]:
    """File paths of the first ``limit`` results (metadata only, no chunk text)."""
    files: List[str] = []
    for node in nodes[:limit]:
        meta = getattr(getattr(node, "node", node), "metadata", None) or {}
        files.append(meta.get("file_path") or "")
    return files


def attach_diagnostic(result: TestResult, nodes, criteria: PassCriteria, top_n: int) -> TestResult:
    """Record diagnostic rank and top-3 files on a result already scored.

    Scoring fields are left as ``evaluate_test`` set them. ``diag_top3_files``
    is always a list afterwards so JSON can tell a diagnostic run from a
    normal one (where the attribute stays None).
    """
    result.diag_rank = first_match_rank(nodes, criteria, top_n)
    result.diag_top3_files = top_result_files(nodes, 3)
    return result


# ────────────────────────────────────────────────────────────────────
# Documentation hints (informational metric, never scored)
# ────────────────────────────────────────────────────────────────────

_DOC_EXTENSIONS = (".md", ".markdown", ".rst", ".txt", ".adoc", ".asciidoc")
_DOC_NODE_TYPES = frozenset({"comment", "comment_split", "block_comment", "doc_comment"})
_HINT_STOP_WORDS = frozenset(
    "static inline const struct union enum class void return define include "
    "public private protected function def func self this none true false "
    "unsigned signed long short char bool null string".split()
)


def _expected_hint_terms(criteria: PassCriteria) -> Tuple[List[str], List[str]]:
    """File names and symbols named by a test's criteria.

    Returns ``(file_terms, symbols)``: literal file names / stems pulled out of
    ``file_pattern`` (lowercased) and identifiers from ``text_pattern`` /
    ``class_name_pattern`` (case kept).  Regex syntax is stripped
    heuristically; short tokens and keywords are ignored.
    """
    files: List[str] = []
    if criteria.file_pattern:
        raw = criteria.file_pattern.replace("\\.", ".").replace("\\", "")
        for m in re.finditer(r"([A-Za-z0-9_\-]+)\.([A-Za-z0-9]{1,6})", raw):
            files.append(f"{m.group(1)}.{m.group(2)}".lower())
            if len(m.group(1)) >= 4:
                files.append(m.group(1).lower())
    symbols: List[str] = []
    for pat in (criteria.text_pattern, criteria.class_name_pattern):
        if not pat:
            continue
        cleaned = re.sub(r"\\[A-Za-z]", " ", pat)
        for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", cleaned):
            if tok.lower() not in _HINT_STOP_WORDS:
                symbols.append(tok)
    return sorted(set(files)), sorted(set(symbols))


def _is_doc_node(n) -> bool:
    meta = n.node.metadata or {}
    node_type = meta.get("node_type", meta.get("type", ""))
    path = (meta.get("file_path") or "").lower()
    return node_type in _DOC_NODE_TYPES or path.endswith(_DOC_EXTENSIONS)


def doc_hint_position(nodes, criteria: PassCriteria, top_k: int = 8) -> Optional[int]:
    """1-based position of the first documentation chunk in the top-k whose
    text names the expected file or symbol, or None."""
    files, symbols = _expected_hint_terms(criteria)
    if not files and not symbols:
        return None
    sym_res = [re.compile(r"(?<![A-Za-z0-9_])" + re.escape(s) + r"(?![A-Za-z0-9_])") for s in symbols]
    for i, n in enumerate(nodes[:top_k], 1):
        if not _is_doc_node(n):
            continue
        if criteria.file_pattern and re.search(criteria.file_pattern, n.node.metadata.get("file_path", "")):
            continue  # the doc chunk is itself the expected file
        text = n.node.get_content() or ""
        low = text.lower()
        if any(re.search(r"(?<![a-z0-9_])" + re.escape(f) + r"(?![a-z0-9_])", low) for f in files):
            return i
        if any(r.search(text) for r in sym_res):
            return i
    return None


# ────────────────────────────────────────────────────────────────────
# Evaluation
# ────────────────────────────────────────────────────────────────────


def _build_node_infos(nodes, top_k: int) -> list:
    """Build a list of node info dicts from retrieved nodes."""
    node_infos = []
    for i, n in enumerate(nodes[:top_k], 1):
        meta = n.node.metadata
        node_infos.append(
            {
                "position": i,
                "node_type": meta.get("node_type", meta.get("type", "?")),
                "file_path": meta.get("file_path", "?"),
                "score": round(n.score, 4) if n.score is not None else None,
                "class_name": meta.get("class_name", ""),
            }
        )
    return node_infos


def _evaluate_multi_file(
    tc: TestCase, nodes, criteria: PassCriteria, node_infos: list, top_k: int
) -> TestResult:
    """Evaluate a multi_file test case."""
    matched_files = set()
    first_match_pos = None
    first_match_info = None

    for i, n in enumerate(nodes[:top_k], 1):
        if _node_matches(n, criteria):
            file_path = n.node.metadata.get("file_path", "")
            basename = os.path.basename(file_path)
            matched_files.add(basename)
            if first_match_pos is None:
                first_match_pos = i
                first_match_info = node_infos[i - 1]

    if (
        len(matched_files) >= 2
        and first_match_pos is not None
        and first_match_pos <= criteria.max_position
    ):
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PASS",
            match_position=first_match_pos,
            match_node_type=first_match_info["node_type"],
            match_file=first_match_info["file_path"],
            match_score=first_match_info["score"],
            all_nodes=node_infos,
        )

    if (
        len(matched_files) >= 2
        and first_match_pos is not None
        and first_match_pos <= criteria.partial_position
    ):
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PARTIAL",
            match_position=first_match_pos,
            match_node_type=first_match_info["node_type"],
            match_file=first_match_info["file_path"],
            match_score=first_match_info["score"],
            detail=(
                f"Multi-file match at position {first_match_pos} "
                f"(>{criteria.max_position}), {len(matched_files)} files"
            ),
            all_nodes=node_infos,
        )

    if len(matched_files) == 1 and first_match_pos is not None:
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PARTIAL",
            match_position=first_match_pos,
            match_node_type=first_match_info["node_type"],
            match_file=first_match_info["file_path"],
            match_score=first_match_info["score"],
            detail=f"Only 1 file matched (need >=2): {matched_files}",
            all_nodes=node_infos,
        )

    return TestResult(
        id=tc.id,
        category=tc.category,
        query=tc.query,
        result="FAIL",
        detail="No matching nodes found in top results",
        all_nodes=node_infos,
    )


def _evaluate_test(tc: TestCase, nodes, top_k: int = 8) -> TestResult:
    """Evaluate retrieval results against a test case's pass criteria.

    Args:
        tc: The test case definition.
        nodes: List of NodeWithScore from the retriever.
        top_k: Number of results to consider.

    Returns:
        TestResult with PASS / PARTIAL / FAIL and match details.
    """
    criteria = tc.pass_criteria
    node_infos = _build_node_infos(nodes, top_k)

    # Handle multi_file test: PASS requires matches from >= 2 different files
    if criteria.multi_file:
        return _evaluate_multi_file(tc, nodes, criteria, node_infos, top_k)

    # Standard (non multi_file) evaluation
    first_full_match_pos = None
    first_full_match_info = None
    first_partial_file_pos = None
    first_partial_type_pos = None
    first_partial_text_pos = None

    for i, n in enumerate(nodes[:top_k], 1):
        info = node_infos[i - 1]

        # Full match check
        if _node_matches(n, criteria):
            if first_full_match_pos is None:
                first_full_match_pos = i
                first_full_match_info = info

        # Partial match checks (file only, type only, text only)
        if first_partial_file_pos is None and _file_matches(n, criteria):
            first_partial_file_pos = i
        if first_partial_type_pos is None and _type_matches(n, criteria):
            first_partial_type_pos = i
        if first_partial_text_pos is None and _text_matches(n, criteria):
            first_partial_text_pos = i

    # PASS: full match at position <= max_position
    if (
        first_full_match_pos is not None
        and first_full_match_pos <= criteria.max_position
    ):
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PASS",
            match_position=first_full_match_pos,
            match_node_type=first_full_match_info["node_type"],
            match_file=first_full_match_info["file_path"],
            match_score=first_full_match_info["score"],
            all_nodes=node_infos,
        )

    # PARTIAL: full match at position <= partial_position
    if (
        first_full_match_pos is not None
        and first_full_match_pos <= criteria.partial_position
    ):
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PARTIAL",
            match_position=first_full_match_pos,
            match_node_type=first_full_match_info["node_type"],
            match_file=first_full_match_info["file_path"],
            match_score=first_full_match_info["score"],
            detail=f"Full match at position {first_full_match_pos} (>{criteria.max_position})",
            all_nodes=node_infos,
        )

    # PARTIAL: file_path matches but node_type doesn't (or vice versa)
    partial_reasons = []
    if (
        first_partial_file_pos is not None
        and first_partial_file_pos <= criteria.partial_position
    ):
        partial_reasons.append(f"file_path match at #{first_partial_file_pos}")
    # A node_type match on its own says nothing about the answer when the
    # test names the expected file (any chunk of an allowed type would earn
    # credit), so with a file_pattern it neither counts as a reason nor
    # decides the reported position.
    if criteria.file_pattern is not None:
        first_partial_type_pos = None
    if (
        first_partial_type_pos is not None
        and first_partial_type_pos <= criteria.partial_position
    ):
        partial_reasons.append(f"node_type match at #{first_partial_type_pos}")
    if (
        first_partial_text_pos is not None
        and first_partial_text_pos <= criteria.partial_position
    ):
        partial_reasons.append(f"text_pattern match at #{first_partial_text_pos}")

    if partial_reasons:
        best_pos = min(
            p
            for p in [
                first_partial_file_pos,
                first_partial_type_pos,
                first_partial_text_pos,
            ]
            if p is not None and p <= criteria.partial_position
        )
        best_info = node_infos[best_pos - 1]
        return TestResult(
            id=tc.id,
            category=tc.category,
            query=tc.query,
            result="PARTIAL",
            match_position=best_pos,
            match_node_type=best_info["node_type"],
            match_file=best_info["file_path"],
            match_score=best_info["score"],
            detail=f"Partial: {', '.join(partial_reasons)}",
            all_nodes=node_infos,
        )

    # FAIL: no matching node in top results
    return TestResult(
        id=tc.id,
        category=tc.category,
        query=tc.query,
        result="FAIL",
        detail="No matching nodes found in top results",
        all_nodes=node_infos,
    )


def evaluate_test(tc: TestCase, nodes, top_k: int = 8) -> TestResult:
    """Evaluate retrieval results against a test case's pass criteria.

    PASS / PARTIAL / FAIL come from the criteria (see ``_evaluate_test``).
    Non-PASS results additionally record ``doc_hint_position``.
    """
    result = _evaluate_test(tc, nodes, top_k=top_k)
    if result.result != "PASS":
        result.doc_hint_position = doc_hint_position(nodes, tc.pass_criteria, top_k)
    return result
