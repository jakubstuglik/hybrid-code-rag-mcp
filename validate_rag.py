"""
validate_rag.py -- Automated RAG validation test runner.

Queries a Qdrant index and evaluates results against 44 predefined test cases.
Uses the same query infrastructure as query_test_index.py (embedding model,
retriever, reranker).

Usage:
    python validate_rag.py                           # Run all 44 tests
    python validate_rag.py --config self-index       # Use self-index config
    python validate_rag.py --category 1              # Run only category 1
    python validate_rag.py --test T01                # Run only test T01
    python validate_rag.py --alpha 0.7 --verbose     # Override alpha, verbose
    python validate_rag.py --json                    # JSON output
"""

import sys
import re
import os
import argparse
import asyncio
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

# ── Setup (same as query_test_index.py) ──────────────────────────────
import config_loader
from shared.embedding import get_embed_model
from qdrant.vector_store import get_qdrant_vector_store, detect_collection_mode
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from shared.reranker import rerank_results, get_retrieval_top_k


# ────────────────────────────────────────────────────────────────────
# Test case data structure
# ────────────────────────────────────────────────────────────────────


@dataclass
class PassCriteria:
    """Criteria for evaluating whether a retrieved node matches expectations."""

    node_types: Optional[List[str]] = None  # Acceptable node_type values (None = any)
    file_pattern: Optional[str] = None  # Regex to match file_path
    text_pattern: Optional[str] = None  # Regex to match chunk text content
    max_position: int = 3  # Position threshold for PASS
    partial_position: int = 5  # Position threshold for PARTIAL
    class_name_pattern: Optional[str] = None  # Regex to match class_name metadata
    multi_file: bool = False  # PASS requires results from >= 2 files


@dataclass
class TestCase:
    """A single RAG validation test case."""

    id: str  # T01-T44
    category: str  # Category name
    query: str  # Query text
    description: str  # What we expect
    pass_criteria: PassCriteria
    difficulty: str = "Medium"  # Easy/Medium/Hard
    aspect: str = "Hybrid"  # Dense/Sparse/Hybrid/Reranker


@dataclass
class TestResult:
    """Result of evaluating a single test case."""

    id: str
    category: str
    query: str
    result: str  # PASS / PARTIAL / FAIL
    match_position: Optional[int] = None
    match_node_type: Optional[str] = None
    match_file: Optional[str] = None
    match_score: Optional[float] = None
    detail: Optional[str] = None
    all_nodes: Optional[List[Dict[str, Any]]] = None


# ────────────────────────────────────────────────────────────────────
# All 44 test cases
# ────────────────────────────────────────────────────────────────────

TEST_CASES: List[TestCase] = [
    # ── Category 1: Class Overview Queries ──────────────────────────
    TestCase(
        id="T01",
        category="Class Overview Queries",
        query="What is TdmMain?",
        description="Should find class summary/overview for TdmMain in MainDM.pas",
        pass_criteria=PassCriteria(
            node_types=["class_summary", "class_summary_split", "class_overview"],
            file_pattern=r"MainDM\.pas",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    TestCase(
        id="T02",
        category="Class Overview Queries",
        query="What classes are in emar105.classes.pas?",
        description="Should find class summary/overview in emar105",
        pass_criteria=PassCriteria(
            node_types=["class_summary", "class_overview"],
            file_pattern=r"emar105",
            max_position=2,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    TestCase(
        id="T03",
        category="Class Overview Queries",
        query="What is TfrmMainTurdus?",
        description="Should find class overview/summary in MainTurdus.pas",
        pass_criteria=PassCriteria(
            node_types=["class_overview", "class_summary", "class_summary_split"],
            file_pattern=r"MainTurdus\.pas",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    TestCase(
        id="T04",
        category="Class Overview Queries",
        query="Describe TfrmSplash",
        description="Should find class overview/summary in Splash.pas",
        pass_criteria=PassCriteria(
            node_types=["class_overview", "class_summary"],
            file_pattern=r"Splash\.pas",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    TestCase(
        id="T05",
        category="Class Overview Queries",
        query="What does TfrmBaseEditor do?",
        description="Should find class overview/summary in BaseEditorForm.pas",
        pass_criteria=PassCriteria(
            node_types=["class_overview", "class_summary", "class_summary_split"],
            file_pattern=r"BaseEditorForm\.pas",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    TestCase(
        id="T06",
        category="Class Overview Queries",
        query="How does TBasicMainForm work?",
        description="Should find class overview/summary in FormBasicMain.pas",
        pass_criteria=PassCriteria(
            node_types=["class_overview", "class_summary", "class_summary_split"],
            file_pattern=r"FormBasicMain\.pas",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    TestCase(
        id="T07",
        category="Class Overview Queries",
        query="Tell me about TSalesReport",
        description="Should find class overview/summary for TSalesReport",
        pass_criteria=PassCriteria(
            node_types=["class_overview", "class_summary"],
            file_pattern=r"SalesReport",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    TestCase(
        id="T08",
        category="Class Overview Queries",
        query="Overview of TEmar105_OIK class",
        description="Should find class overview/summary for TEmar105_OIK in emar105",
        pass_criteria=PassCriteria(
            node_types=["class_overview", "class_summary"],
            file_pattern=r"emar105",
            class_name_pattern=r"TEmar105_OIK",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    TestCase(
        id="T09",
        category="Class Overview Queries",
        query="What fields does TdmMain have?",
        description="Should find class summary/declSection for TdmMain in MainDM.pas",
        pass_criteria=PassCriteria(
            node_types=["class_summary", "class_summary_split", "declSection"],
            file_pattern=r"MainDM\.pas",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Reranker",
    ),
    # ── Category 2: Precise Identifier Search ───────────────────────
    TestCase(
        id="T10",
        category="Precise Identifier Search",
        query="REPORT_TYPE_PUNCTUALITY_RIDES",
        description="Should find constant definition/usage in .pas file",
        pass_criteria=PassCriteria(
            node_types=None,  # any node_type
            file_pattern=r"\.pas",
            text_pattern=r"REPORT_TYPE_PUNCTUALITY_RIDES",
            max_position=2,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T11",
        category="Precise Identifier Search",
        query="PrepareDataSet",
        description="Should find PrepareDataSet method implementation",
        pass_criteria=PassCriteria(
            node_types=["defProc", "defProc_split", "method_group"],
            text_pattern=r"PrepareDataSet",
            max_position=2,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T12",
        category="Precise Identifier Search",
        query="OpenConnection",
        description="Should find OpenConnection in MainDM.pas",
        pass_criteria=PassCriteria(
            node_types=["defProc", "defProc_split"],
            file_pattern=r"MainDM\.pas",
            text_pattern=r"OpenConnection",
            max_position=2,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T13",
        category="Precise Identifier Search",
        query="GetCardSerialNumber",
        description="Should find GetCardSerialNumber in emar105",
        pass_criteria=PassCriteria(
            node_types=["method_group", "method_group_split", "defProc"],
            file_pattern=r"emar",
            text_pattern=r"GetCardSerialNumber",
            max_position=4,
            partial_position=6,
        ),
        difficulty="Medium",
        aspect="Sparse",
    ),
    TestCase(
        id="T14",
        category="Precise Identifier Search",
        query="SLS_ReliefExport_Bilety_Get",
        description="Should find SQL procedure header/full for SLS_ReliefExport_Bilety_Get",
        pass_criteria=PassCriteria(
            node_types=["procedure_header", "procedure_full", "function_header"],
            file_pattern=r"SLS_ReliefExport_Bilety_Get",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T15",
        category="Precise Identifier Search",
        query="TCK_FarePrice_GetPriceForXDesignation",
        description="Should find SQL function header/full for TCK_FarePrice",
        pass_criteria=PassCriteria(
            node_types=["function_header", "function_full", "procedure_header"],
            file_pattern=r"TCK_FarePrice",
            max_position=2,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T16",
        category="Precise Identifier Search",
        query="ADMIN_ReportDef_AnalysisRoute",
        description="Should find SQL procedure for ADMIN_ReportDef_AnalysisRoute",
        pass_criteria=PassCriteria(
            node_types=["procedure_header", "procedure_full", "sql_batch"],
            file_pattern=r"ADMIN_ReportDef_AnalysisRoute",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T17",
        category="Precise Identifier Search",
        query="ADMIN_CompanyAllBranches",
        description="Should find SQL procedure for ADMIN_CompanyAllBranches",
        pass_criteria=PassCriteria(
            node_types=["procedure_header", "procedure_full", "sql_batch"],
            file_pattern=r"ADMIN_CompanyAllBranches",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T18",
        category="Precise Identifier Search",
        query="GetInfoText",
        description="Should find GetInfoText method",
        pass_criteria=PassCriteria(
            node_types=["defProc", "defProc_split", "method_group"],
            text_pattern=r"GetInfoText",
            max_position=4,
            partial_position=6,
        ),
        difficulty="Medium",
        aspect="Sparse",
    ),
    TestCase(
        id="T19",
        category="Precise Identifier Search",
        query="C_REPORT_",
        description="Should find constant declarations matching C_REPORT_",
        pass_criteria=PassCriteria(
            node_types=["declConst", "declConst_split", "declSection"],
            text_pattern=r"C_REPORT_",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Medium",
        aspect="Sparse",
    ),
    # ── Category 3: Cross-File / Dependency ─────────────────────────
    TestCase(
        id="T20",
        category="Cross-File / Dependency",
        query="uses clause MainDM",
        description="Should find uses clause chunk in MainDM.pas",
        pass_criteria=PassCriteria(
            node_types=["declUses"],
            file_pattern=r"MainDM\.pas",
            max_position=2,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T21",
        category="Cross-File / Dependency",
        query="what units does MainTurdus use",
        description="Should find uses clause in MainTurdus.pas",
        pass_criteria=PassCriteria(
            node_types=["declUses"],
            file_pattern=r"MainTurdus\.pas",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Hybrid",
    ),
    TestCase(
        id="T22",
        category="Cross-File / Dependency",
        query="TClientDataSet cdsStoredProc",
        description="Should find cdsStoredProc field in MainDM",
        pass_criteria=PassCriteria(
            file_pattern=r"MainDM",
            text_pattern=r"cdsStoredProc",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Sparse",
    ),
    TestCase(
        id="T23",
        category="Cross-File / Dependency",
        query="classes that inherit from TForm",
        description="Should find TForm references from multiple files",
        pass_criteria=PassCriteria(
            text_pattern=r"TForm",
            multi_file=True,
            max_position=5,
            partial_position=8,
        ),
        difficulty="Medium",
        aspect="Hybrid",
    ),
    TestCase(
        id="T24",
        category="Cross-File / Dependency",
        query="classes that inherit from TDataModule",
        description="Should find TDataModule references in MainDM",
        pass_criteria=PassCriteria(
            text_pattern=r"TDataModule",
            file_pattern=r"MainDM",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Medium",
        aspect="Hybrid",
    ),
    # ── Category 4: DFM Form Queries ────────────────────────────────
    TestCase(
        id="T25",
        category="DFM Form Queries",
        query="MainTurdus form components",
        description="Should find MainTurdus.dfm form header",
        pass_criteria=PassCriteria(
            node_types=["dfm_form_header"],
            file_pattern=r"MainTurdus\.dfm",
            max_position=2,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Reranker",
    ),
    TestCase(
        id="T26",
        category="DFM Form Queries",
        query="Splash form layout",
        description="Should find Splash.dfm form header or objects",
        pass_criteria=PassCriteria(
            node_types=["dfm_form_header", "dfm_object"],
            file_pattern=r"Splash\.dfm",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Reranker",
    ),
    TestCase(
        id="T27",
        category="DFM Form Queries",
        query="SFTP frame components",
        description="Should find WithFrame_SFTP.dfm form header",
        pass_criteria=PassCriteria(
            node_types=["dfm_form_header"],
            file_pattern=r"WithFrame_SFTP\.dfm",
            max_position=2,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Reranker",
    ),
    TestCase(
        id="T28",
        category="DFM Form Queries",
        query="TActionList in MainTurdus",
        description="Should find TActionList references in MainTurdus.dfm",
        pass_criteria=PassCriteria(
            file_pattern=r"MainTurdus\.dfm",
            text_pattern=r"TActionList",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Medium",
        aspect="Hybrid",
    ),
    # ── Category 5: SQL Schema / Procedure ──────────────────────────
    TestCase(
        id="T29",
        category="SQL Schema / Procedure",
        query="SLS_Ticket table columns",
        description="Should find SLS_Ticket CREATE TABLE or sql_batch",
        pass_criteria=PassCriteria(
            node_types=["create_table", "sql_batch"],
            file_pattern=r"SLS_Ticket",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Hybrid",
    ),
    TestCase(
        id="T30",
        category="SQL Schema / Procedure",
        query="parameters of ADMIN_ReportDef_ReliefTicketPayments",
        description="Should find procedure header with parameters",
        pass_criteria=PassCriteria(
            node_types=["procedure_header", "procedure_full"],
            file_pattern=r"ADMIN_ReportDef_ReliefTicketPayments",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Medium",
        aspect="Hybrid",
    ),
    TestCase(
        id="T31",
        category="SQL Schema / Procedure",
        query="body of SLS_ReliefExport_Bilety_Get procedure",
        description="Should find procedure body",
        pass_criteria=PassCriteria(
            node_types=["procedure_body", "procedure_full"],
            file_pattern=r"SLS_ReliefExport_Bilety_Get",
            max_position=4,
            partial_position=6,
        ),
        difficulty="Medium",
        aspect="Hybrid",
    ),
    TestCase(
        id="T32",
        category="SQL Schema / Procedure",
        query="SELECT statements in TCK_FarePrice_GetPriceForXDesignation",
        description="Should find SELECT in TCK_FarePrice procedure",
        pass_criteria=PassCriteria(
            file_pattern=r"TCK_FarePrice",
            text_pattern=r"SELECT",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Medium",
        aspect="Hybrid",
    ),
    # ── Category 6: Natural Language Code Understanding ──────────────
    TestCase(
        id="T33",
        category="Natural Language Code Understanding",
        query="How to connect to the database",
        description="Should find database connection code in MainDM.pas",
        pass_criteria=PassCriteria(
            file_pattern=r"MainDM\.pas",
            text_pattern=r"(?i)(Connection|Connect|database)",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Dense",
    ),
    TestCase(
        id="T34",
        category="Natural Language Code Understanding",
        query="Where are ticket prices calculated",
        description="Should find fare/ticket price code",
        pass_criteria=PassCriteria(
            file_pattern=r"(?i)(FarePrice|Ticket|SLS_Ticket)",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Dense",
    ),
    TestCase(
        id="T35",
        category="Natural Language Code Understanding",
        query="How to export relief tickets",
        description="Should find relief export code",
        pass_criteria=PassCriteria(
            file_pattern=r"(?i)(ReliefExport|Bilety)",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Dense",
    ),
    TestCase(
        id="T36",
        category="Natural Language Code Understanding",
        query="Where is the splash screen shown",
        description="Should find splash screen code",
        pass_criteria=PassCriteria(
            file_pattern=r"(?i)Splash\.(pas|dfm)",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Dense",
    ),
    # ── Category 7: Edge Cases / Stress Tests ────────────────────────
    TestCase(
        id="T37",
        category="Edge Cases / Stress Tests",
        query="TdmMain",
        description="Bare class name query",
        pass_criteria=PassCriteria(
            file_pattern=r"MainDM",
            max_position=3,
            partial_position=5,
        ),
        difficulty="Easy",
        aspect="Sparse",
    ),
    TestCase(
        id="T38",
        category="Edge Cases / Stress Tests",
        query="I need to understand the complete architecture of the main data module "
        "TdmMain in MainDM.pas including all its published components, stored "
        "procedures, database connections, event handlers, and how it interacts "
        "with other forms in the application",
        description="Long verbose query - should still find MainDM class overview",
        pass_criteria=PassCriteria(
            file_pattern=r"MainDM\.pas",
            node_types=["class_summary", "class_summary_split", "class_overview"],
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Reranker",
    ),
    TestCase(
        id="T39",
        category="Edge Cases / Stress Tests",
        query="TdmMian",
        description="Typo query (TdmMian instead of TdmMain) - may fail",
        pass_criteria=PassCriteria(
            file_pattern=r"MainDM",
            max_position=8,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Dense",
    ),
    TestCase(
        id="T40",
        category="Edge Cases / Stress Tests",
        query="procedure",
        description="Extremely generic query - should return results from multiple .sql files",
        pass_criteria=PassCriteria(
            multi_file=True,
            max_position=8,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Sparse",
    ),
    # ── Category 8: AI Agent Workflow ────────────────────────────────
    TestCase(
        id="T41",
        category="AI Agent Workflow",
        query="I need to modify the ticket export logic, where should I look?",
        description="Should find relief export / ticket files",
        pass_criteria=PassCriteria(
            file_pattern=r"(?i)(ReliefExport|Bilety|Ticket)",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Dense",
    ),
    TestCase(
        id="T42",
        category="AI Agent Workflow",
        query="Where are report types defined?",
        description="Should find REPORT_TYPE or C_REPORT_ constants",
        pass_criteria=PassCriteria(
            text_pattern=r"(?i)(REPORT_TYPE|C_REPORT_)",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Hybrid",
    ),
    TestCase(
        id="T43",
        category="AI Agent Workflow",
        query="I need to add a new field to the main data module, show me the structure",
        description="Should find MainDM class structure",
        pass_criteria=PassCriteria(
            file_pattern=r"MainDM",
            node_types=[
                "class_summary",
                "class_summary_split",
                "class_overview",
                "declSection",
            ],
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Reranker",
    ),
    TestCase(
        id="T44",
        category="AI Agent Workflow",
        query="What SQL procedures handle company data?",
        description="Should find Company-related SQL procedures",
        pass_criteria=PassCriteria(
            file_pattern=r"(?i)Company",
            max_position=5,
            partial_position=8,
        ),
        difficulty="Hard",
        aspect="Hybrid",
    ),
]

# Category ordering (by first appearance in TEST_CASES)
CATEGORIES = []
_seen_cats = set()
for _tc in TEST_CASES:
    if _tc.category not in _seen_cats:
        CATEGORIES.append(_tc.category)
        _seen_cats.add(_tc.category)


# ────────────────────────────────────────────────────────────────────
# Setup (mirrors query_test_index.py)
# ────────────────────────────────────────────────────────────────────


def setup(config_name=None, alpha_override=None):
    """Load config, embedding model, and create the retriever index."""
    config = config_loader.get_config(config_name=config_name)

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
    print(
        f"Collection: {config.COLLECTION_NAME}, mode: {mode}, alpha: {alpha}",
        file=sys.stderr,
    )

    index = VectorStoreIndex.from_vector_store(
        storage_context.vector_store, embed_model=embed_model
    )

    return index, mode, alpha, config


def run_query(index, mode, alpha, query, top_k=8):
    """Execute a single retrieval query and return reranked nodes."""
    fetch_k = get_retrieval_top_k(query, top_k)

    if mode == "hybrid":
        retriever = index.as_retriever(
            similarity_top_k=fetch_k,
            vector_store_query_mode=VectorStoreQueryMode.HYBRID,
            alpha=alpha,
            sparse_top_k=fetch_k,
        )
    else:
        retriever = index.as_retriever(similarity_top_k=fetch_k)

    nodes = asyncio.run(retriever.aretrieve(query))
    nodes = rerank_results(nodes, query, desired_top_k=top_k, verbose=False)
    return nodes


# ────────────────────────────────────────────────────────────────────
# Evaluation logic
# ────────────────────────────────────────────────────────────────────


def _node_matches(node, criteria: PassCriteria) -> bool:
    """Check if a single retrieved node matches all specified criteria."""
    meta = node.node.metadata
    content = node.node.get_content() or ""
    node_type = meta.get("node_type", meta.get("type", ""))
    file_path = meta.get("file_path", "")
    class_name = meta.get("class_name", "")

    # Check node_type (if specified)
    if criteria.node_types is not None:
        if node_type not in criteria.node_types:
            return False

    # Check file_path (if specified)
    if criteria.file_pattern is not None:
        if not re.search(criteria.file_pattern, file_path):
            return False

    # Check text content (if specified)
    if criteria.text_pattern is not None:
        if not re.search(criteria.text_pattern, content):
            return False

    # Check class_name metadata (if specified)
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


def evaluate_test(tc: TestCase, nodes, top_k: int = 8) -> TestResult:
    """Evaluate retrieval results against a test case's pass criteria."""
    criteria = tc.pass_criteria

    # Build node info list for detail output
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

    # Handle multi_file test: PASS requires matches from >= 2 different files
    if criteria.multi_file:
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
        elif (
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
                detail=f"Multi-file match at position {first_match_pos} (>{criteria.max_position}), {len(matched_files)} files",
                all_nodes=node_infos,
            )
        elif len(matched_files) == 1 and first_match_pos is not None:
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
        else:
            return TestResult(
                id=tc.id,
                category=tc.category,
                query=tc.query,
                result="FAIL",
                detail="No matching nodes found in top results",
                all_nodes=node_infos,
            )

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
        # Use the best partial match position
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


# ────────────────────────────────────────────────────────────────────
# Output formatting
# ────────────────────────────────────────────────────────────────────


def _truncate(s: str, max_len: int) -> str:
    """Truncate a string to max_len, adding ellipsis if needed."""
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def _get_rating(score_pct: float) -> str:
    """Get a rating string from the score percentage."""
    if score_pct >= 95:
        return "Outstanding"
    elif score_pct >= 90:
        return "Excellent"
    elif score_pct >= 80:
        return "Good"
    elif score_pct >= 70:
        return "Acceptable"
    elif score_pct >= 60:
        return "Needs Improvement"
    else:
        return "Poor"


def print_results(
    results: List[TestResult],
    alpha: float,
    config_name: str,
    verbose: bool = False,
):
    """Print formatted test results to stdout."""
    total = len(results)
    pass_count = sum(1 for r in results if r.result == "PASS")
    partial_count = sum(1 for r in results if r.result == "PARTIAL")
    fail_count = sum(1 for r in results if r.result == "FAIL")

    # Score: PASS=2, PARTIAL=1, FAIL=0
    score = pass_count * 2 + partial_count * 1
    max_score = total * 2
    score_pct = (score / max_score * 100) if max_score > 0 else 0.0
    rating = _get_rating(score_pct)

    print(f"RAG Validation: {total} tests, alpha={alpha:.2f}, index={config_name}")
    print("=" * 70)

    current_category = None
    cat_num = 0
    for r in results:
        if r.category != current_category:
            current_category = r.category
            cat_num += 1
            print(f"\n  Category {cat_num}: {current_category}")

        # Status indicator
        if r.result == "PASS":
            status = "PASS  "
        elif r.result == "PARTIAL":
            status = "PARTIAL"
        else:
            status = "FAIL  "

        # Position / node_type / file info
        if r.match_position is not None:
            pos_str = f"[#{r.match_position}]"
            ntype = r.match_node_type or "?"
            fname = os.path.basename(r.match_file) if r.match_file else "?"
            query_display = _truncate(r.query, 50)
            print(
                f'    {r.id}  {status} {pos_str:5s} {ntype:25s} {fname:30s} "{query_display}"'
            )
        else:
            query_display = _truncate(r.query, 50)
            print(f'    {r.id}  {status}       {"":25s} {"":30s} "{query_display}"')

        # Detail for FAIL and PARTIAL
        if r.result in ("FAIL", "PARTIAL"):
            # Print what was expected
            tc = next((t for t in TEST_CASES if t.id == r.id), None)
            if tc:
                criteria = tc.pass_criteria
                expected_parts = []
                if criteria.file_pattern:
                    expected_parts.append(f"file_path~/{criteria.file_pattern}/")
                if criteria.node_types:
                    expected_parts.append(
                        f"node_type in {{{', '.join(criteria.node_types)}}}"
                    )
                if criteria.text_pattern:
                    expected_parts.append(f"text~/{criteria.text_pattern}/")
                if criteria.class_name_pattern:
                    expected_parts.append(f"class_name~/{criteria.class_name_pattern}/")
                if criteria.multi_file:
                    expected_parts.append("multi_file>=2")
                print(f"           Expected: {', '.join(expected_parts)}")

            if r.detail:
                print(f"           Reason: {r.detail}")

            # Show top nodes
            if r.all_nodes:
                for ni in r.all_nodes[:3]:
                    fname = (
                        os.path.basename(ni["file_path"])
                        if ni["file_path"] != "?"
                        else "?"
                    )
                    score_str = (
                        f"score={ni['score']:.4f}"
                        if ni["score"] is not None
                        else "score=?"
                    )
                    print(
                        f"           Got [#{ni['position']}]: {ni['node_type']:25s} "
                        f"{fname:30s} {score_str}"
                    )

        # Verbose: show all nodes even for PASS
        if verbose and r.result == "PASS" and r.all_nodes:
            for ni in r.all_nodes:
                fname = (
                    os.path.basename(ni["file_path"]) if ni["file_path"] != "?" else "?"
                )
                score_str = (
                    f"score={ni['score']:.4f}" if ni["score"] is not None else "score=?"
                )
                marker = " <-- MATCH" if ni["position"] == r.match_position else ""
                print(
                    f"           [#{ni['position']}]: {ni['node_type']:25s} "
                    f"{fname:30s} {score_str}{marker}"
                )

    # Summary
    print()
    print("=" * 70)
    print(f"Results: {pass_count} PASS, {partial_count} PARTIAL, {fail_count} FAIL")
    print(f"Score:  {score_pct:5.1f}%  ({score} / {max_score} points)")
    print(f"Rating: {rating}")
    print("=" * 70)

    # Category summary
    print()
    print("Category Summary:")
    for cat_idx, cat_name in enumerate(CATEGORIES, 1):
        cat_results = [r for r in results if r.category == cat_name]
        cat_pass = sum(1 for r in cat_results if r.result == "PASS")
        cat_partial = sum(1 for r in cat_results if r.result == "PARTIAL")
        cat_fail = sum(1 for r in cat_results if r.result == "FAIL")
        cat_total = len(cat_results)

        details = []
        if cat_partial > 0:
            details.append(f"{cat_partial} PARTIAL")
        if cat_fail > 0:
            details.append(f"{cat_fail} FAIL")
        detail_str = f"  ({', '.join(details)})" if details else ""

        print(
            f"  {cat_idx}. {cat_name + ':':40s} {cat_pass}/{cat_total} PASS{detail_str}"
        )

    print()


def output_json(
    results: List[TestResult],
    alpha: float,
    config_name: str,
):
    """Output results as JSON to stdout."""
    total = len(results)
    pass_count = sum(1 for r in results if r.result == "PASS")
    partial_count = sum(1 for r in results if r.result == "PARTIAL")
    fail_count = sum(1 for r in results if r.result == "FAIL")

    score = pass_count * 2 + partial_count * 1
    max_score = total * 2
    score_pct = round(score / max_score * 100, 1) if max_score > 0 else 0.0
    rating = _get_rating(score_pct)

    tests_json = []
    for r in results:
        entry = {
            "id": r.id,
            "category": r.category,
            "query": r.query,
            "result": r.result,
            "match_position": r.match_position,
            "match_node_type": r.match_node_type,
            "match_file": r.match_file,
            "match_score": r.match_score,
        }
        if r.detail:
            entry["detail"] = r.detail
        tests_json.append(entry)

    output = {
        "alpha": alpha,
        "config": config_name,
        "total_tests": total,
        "pass_count": pass_count,
        "partial_count": partial_count,
        "fail_count": fail_count,
        "score": score,
        "max_score": max_score,
        "score_pct": score_pct,
        "rating": rating,
        "tests": tests_json,
    }

    print(json.dumps(output, indent=2))


# ────────────────────────────────────────────────────────────────────
# Main entry point
# ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Automated RAG validation test runner")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Config name or path (passed to config_loader.get_config())",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=None,
        help="Override HYBRID_ALPHA (0.0=BM25 only, 1.0=dense only)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=8,
        help="Override default top_k (default: 8)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Run only specific category by number (1-8) or name",
    )
    parser.add_argument(
        "--test",
        type=str,
        default=None,
        help="Run only specific test by ID (T01, T02, etc.)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all result nodes even for PASS results",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON for programmatic use",
    )
    args = parser.parse_args()

    # Filter test cases
    tests_to_run = list(TEST_CASES)

    if args.test:
        test_id = args.test.upper()
        tests_to_run = [tc for tc in tests_to_run if tc.id == test_id]
        if not tests_to_run:
            print(f"Error: Test ID '{args.test}' not found.", file=sys.stderr)
            print(f"Valid IDs: T01-T{len(TEST_CASES):02d}", file=sys.stderr)
            sys.exit(1)

    elif args.category:
        # Accept number or name
        cat_filter = args.category
        try:
            cat_num = int(cat_filter)
            if 1 <= cat_num <= len(CATEGORIES):
                cat_name = CATEGORIES[cat_num - 1]
                tests_to_run = [tc for tc in tests_to_run if tc.category == cat_name]
            else:
                print(
                    f"Error: Category number {cat_num} out of range (1-{len(CATEGORIES)}).",
                    file=sys.stderr,
                )
                sys.exit(1)
        except ValueError:
            # Try matching by name (case-insensitive partial match)
            matches = [
                tc for tc in tests_to_run if cat_filter.lower() in tc.category.lower()
            ]
            if matches:
                tests_to_run = matches
            else:
                print(
                    f"Error: Category '{cat_filter}' not found.",
                    file=sys.stderr,
                )
                print("Available categories:", file=sys.stderr)
                for i, c in enumerate(CATEGORIES, 1):
                    print(f"  {i}. {c}", file=sys.stderr)
                sys.exit(1)

    # Setup index
    config_name = args.config or "production"
    index, mode, alpha, cfg = setup(config_name=args.config, alpha_override=args.alpha)
    top_k = args.top_k

    # Run tests
    results: List[TestResult] = []
    total = len(tests_to_run)

    for i, tc in enumerate(tests_to_run, 1):
        if not args.json_output:
            print(
                f"\r  Running {tc.id} ({i}/{total})...",
                end="",
                file=sys.stderr,
                flush=True,
            )

        nodes = run_query(index, mode, alpha, tc.query, top_k=top_k)
        result = evaluate_test(tc, nodes, top_k=top_k)
        results.append(result)

    if not args.json_output:
        print("\r" + " " * 40 + "\r", end="", file=sys.stderr, flush=True)

    # Output
    if args.json_output:
        output_json(results, alpha, config_name)
    else:
        print_results(results, alpha, config_name, verbose=args.verbose)


if __name__ == "__main__":
    main()
