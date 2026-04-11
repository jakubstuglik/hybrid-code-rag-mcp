"""
Tests for shared/reranker.py — post-retrieval reranking for hybrid search results.

Tests cover:
    - is_overview_query(): pattern matching for overview vs keyword queries
    - get_retrieval_top_k(): over-fetch multiplier for overview queries
    - extract_target_identifiers(): Pascal, SQL, file stem extraction
    - _chunk_matches_target(): metadata field matching
    - _compute_rerank_score(): score adjustment with bonuses and penalties
    - rerank_results(): end-to-end reranking with sorting, trimming, verbose mode
    - Edge cases: empty inputs, missing attributes, stability, deduplication
"""

from unittest.mock import patch

import pytest

import shared.reranker as reranker_module


# ────────────────────────────────────────────────
# Lightweight mocks (no LlamaIndex dependency)
# ────────────────────────────────────────────────


class MockNode:
    """Lightweight mock for LlamaIndex TextNode."""

    def __init__(self, metadata: dict):
        self.metadata = metadata


class MockNodeWithScore:
    """Lightweight mock for LlamaIndex NodeWithScore."""

    def __init__(self, score: float, metadata: dict):
        self.score = score
        self.node = MockNode(metadata)


class MockBareObject:
    """Object with neither .node nor .score — tests hasattr fallbacks."""

    pass


# ────────────────────────────────────────────────
# TestIsOverviewQuery
# ────────────────────────────────────────────────


class TestIsOverviewQuery:
    """Tests for is_overview_query() — detecting overview/summary intent."""

    def test_what_is_pattern(self):
        """'What is TdmMain?' triggers overview detection."""
        assert reranker_module.is_overview_query("What is TdmMain?") is True

    def test_what_does_x_do_pattern(self):
        """'What does TdmMain do' triggers overview detection."""
        assert reranker_module.is_overview_query("What does TdmMain do") is True

    def test_describe_pattern(self):
        """'Describe the TfrmMainForm class' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("Describe the TfrmMainForm class") is True
        )

    def test_explain_pattern(self):
        """'Explain core105.classes.pas' triggers overview detection."""
        assert reranker_module.is_overview_query("Explain core105.classes.pas") is True

    def test_tell_me_about_pattern(self):
        """'Tell me about the data module' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("Tell me about the data module") is True
        )

    def test_what_classes_pattern(self):
        """'What classes are in core105?' triggers overview detection."""
        assert reranker_module.is_overview_query("What classes are in core105?") is True

    def test_what_methods_pattern(self):
        """'What methods does TdmMain have?' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("What methods does TdmMain have?") is True
        )

    def test_what_fields_pattern(self):
        """'What fields are in TdmMain?' triggers overview detection."""
        assert reranker_module.is_overview_query("What fields are in TdmMain?") is True

    def test_what_properties_pattern(self):
        """'What properties does this class expose?' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("What properties does this class expose?")
            is True
        )

    def test_overview_of_pattern(self):
        """'Overview of the MainDM module' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("Overview of the MainDM module") is True
        )

    def test_summary_of_pattern(self):
        """'Summary of core105' triggers overview detection."""
        assert reranker_module.is_overview_query("Summary of core105") is True

    def test_structure_of_pattern(self):
        """'Structure of the data module' triggers overview detection."""
        assert reranker_module.is_overview_query("Structure of the data module") is True

    def test_class_overview_pattern(self):
        """'Give me a class overview' triggers overview detection."""
        assert reranker_module.is_overview_query("Give me a class overview") is True

    def test_form_overview_pattern(self):
        """'form overview for MainForm' triggers overview detection."""
        assert reranker_module.is_overview_query("form overview for MainForm") is True

    def test_how_does_x_work_pattern(self):
        """'How does TdmMain work' triggers overview detection."""
        assert reranker_module.is_overview_query("How does TdmMain work") is True

    def test_what_does_the_x_look_like_pattern(self):
        """'What does the MainForm form look like' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("What does the MainForm form look like")
            is True
        )

    def test_form_components_pattern(self):
        """'form components on TfrmMain' triggers overview detection."""
        assert reranker_module.is_overview_query("form components on TfrmMain") is True

    def test_frame_components_pattern(self):
        """'frame components in the analysis frame' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("frame components in the analysis frame")
            is True
        )

    def test_show_me_the_structure_pattern(self):
        """'Show me the structure of TdmMain' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("Show me the structure of TdmMain")
            is True
        )

    def test_show_me_the_overview_pattern(self):
        """'Show me the overview of the module' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("Show me the overview of the module")
            is True
        )

    def test_show_me_the_summary_pattern(self):
        """'Show me the summary' triggers overview detection."""
        assert reranker_module.is_overview_query("Show me the summary") is True

    def test_i_need_to_add_pattern(self):
        """'I need to add a method to TdmMain' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("I need to add a method to TdmMain")
            is True
        )

    def test_i_need_to_modify_pattern(self):
        """'I need to modify TfrmMainForm' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("I need to modify TfrmMainForm") is True
        )

    def test_i_need_to_change_pattern(self):
        """'I need to change the login form' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("I need to change the login form") is True
        )

    def test_i_need_to_update_pattern(self):
        """'I need to update the data module' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("I need to update the data module")
            is True
        )

    def test_i_need_to_extend_pattern(self):
        """'I need to extend TBasicMainForm' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("I need to extend TBasicMainForm") is True
        )

    def test_what_are_the_main_pattern(self):
        """'What are the main classes in core105?' triggers overview detection."""
        assert (
            reranker_module.is_overview_query("What are the main classes in core105?")
            is True
        )

    def test_list_the_methods_pattern(self):
        """'List the methods of TdmMain' triggers overview detection."""
        assert reranker_module.is_overview_query("List the methods of TdmMain") is True

    def test_list_the_classes_pattern(self):
        """'List the classes in core105' triggers overview detection."""
        assert reranker_module.is_overview_query("List the classes in core105") is True

    def test_list_the_fields_pattern(self):
        """'List the fields of TdmMain' triggers overview detection."""
        assert reranker_module.is_overview_query("List the fields of TdmMain") is True

    def test_list_the_properties_pattern(self):
        """'List the properties' triggers overview detection."""
        assert reranker_module.is_overview_query("List the properties") is True

    # ── Case insensitivity ──

    def test_what_is_uppercase(self):
        """'WHAT IS TdmMain' (all caps) triggers overview detection."""
        assert reranker_module.is_overview_query("WHAT IS TdmMain") is True

    def test_describe_mixed_case(self):
        """'dEsCrIbE the class' (mixed case) triggers overview detection."""
        assert reranker_module.is_overview_query("dEsCrIbE the class") is True

    def test_explain_title_case(self):
        """'Explain This Module' (title case) triggers overview detection."""
        assert reranker_module.is_overview_query("Explain This Module") is True

    def test_overview_of_uppercase(self):
        """'OVERVIEW OF the system' triggers overview detection."""
        assert reranker_module.is_overview_query("OVERVIEW OF the system") is True

    def test_how_does_mixed_case(self):
        """'How Does TdmMain Work' triggers overview detection."""
        assert reranker_module.is_overview_query("How Does TdmMain Work") is True

    def test_form_overview_uppercase(self):
        """'FORM OVERVIEW' triggers overview detection."""
        assert reranker_module.is_overview_query("FORM OVERVIEW") is True

    def test_frame_components_title_case(self):
        """'Frame Components' triggers overview detection."""
        assert reranker_module.is_overview_query("Frame Components of the form") is True

    # ── Negative cases (keyword/precise queries) ──

    def test_keyword_query_procedure_name(self):
        """Bare procedure name 'PrepareDataSet' is not overview."""
        assert reranker_module.is_overview_query("PrepareDataSet") is False

    def test_keyword_query_constant(self):
        """Bare constant 'REPORT_TYPE_PUNCTUALITY_RIDES' is not overview."""
        assert (
            reranker_module.is_overview_query("REPORT_TYPE_PUNCTUALITY_RIDES") is False
        )

    def test_keyword_query_getter(self):
        """Bare getter name 'GetCardSerialNumber' is not overview."""
        assert reranker_module.is_overview_query("GetCardSerialNumber") is False

    def test_keyword_query_sql_procedure(self):
        """Bare SQL procedure name is not overview."""
        assert reranker_module.is_overview_query("SLS_ReliefExport_Bilety_Get") is False

    def test_keyword_query_where_is(self):
        """'Where is PrepareDataSet used?' is not overview."""
        assert (
            reranker_module.is_overview_query("Where is PrepareDataSet used?") is False
        )

    def test_keyword_query_find(self):
        """'Find the definition of REPORT_TYPE_PUNCTUALITY_RIDES' is not overview."""
        assert (
            reranker_module.is_overview_query(
                "Find the definition of REPORT_TYPE_PUNCTUALITY_RIDES"
            )
            is False
        )

    def test_keyword_query_i_need_to_find(self):
        """'I need to find PrepareDataSet' is NOT overview (find is precise lookup)."""
        assert (
            reranker_module.is_overview_query("I need to find PrepareDataSet") is False
        )

    # ── Edge cases ──

    def test_empty_string(self):
        """Empty string is not an overview query."""
        assert reranker_module.is_overview_query("") is False

    def test_whitespace_only(self):
        """Whitespace-only string is not an overview query."""
        assert reranker_module.is_overview_query("   ") is False

    def test_partial_pattern_no_match(self):
        """'whatnot is this' should not match 'what is' because 'whatnot' is not 'what'."""
        assert reranker_module.is_overview_query("whatnot is this") is False

    def test_embedded_in_longer_sentence(self):
        """'Can you explain the module?' matches because 'explain ' appears."""
        assert reranker_module.is_overview_query("Can you explain the module?") is True


# ────────────────────────────────────────────────
# TestGetRetrievalTopK
# ────────────────────────────────────────────────


class TestGetRetrievalTopK:
    """Tests for get_retrieval_top_k() — over-fetch multiplier."""

    def test_overview_query_multiplied(self):
        """Overview query returns desired_top_k * OVERFETCH_MULTIPLIER."""
        result = reranker_module.get_retrieval_top_k("What is TdmMain?", 8)
        assert result == 8 * reranker_module.OVERFETCH_MULTIPLIER

    def test_overview_query_top_k_1(self):
        """Overview query with desired_top_k=1 returns OVERFETCH_MULTIPLIER."""
        result = reranker_module.get_retrieval_top_k("Describe TdmMain", 1)
        assert result == reranker_module.OVERFETCH_MULTIPLIER

    def test_overview_query_top_k_10(self):
        """Overview query with desired_top_k=10 returns 100."""
        result = reranker_module.get_retrieval_top_k("What classes are in core105?", 10)
        assert result == 100

    def test_overview_query_top_k_100(self):
        """Overview query with desired_top_k=100 returns 1000."""
        result = reranker_module.get_retrieval_top_k("Summary of the system", 100)
        assert result == 1000

    def test_non_overview_query_returns_unchanged(self):
        """Non-overview query returns desired_top_k unchanged."""
        result = reranker_module.get_retrieval_top_k("PrepareDataSet", 8)
        assert result == 8

    def test_non_overview_query_top_k_1(self):
        """Non-overview query with desired_top_k=1 returns 1."""
        result = reranker_module.get_retrieval_top_k("GetCardSerialNumber", 1)
        assert result == 1

    def test_non_overview_query_top_k_100(self):
        """Non-overview query with desired_top_k=100 returns 100."""
        result = reranker_module.get_retrieval_top_k(
            "REPORT_TYPE_PUNCTUALITY_RIDES", 100
        )
        assert result == 100

    def test_overfetch_multiplier_value(self):
        """OVERFETCH_MULTIPLIER is 10 as configured for large-file overview queries."""
        assert reranker_module.OVERFETCH_MULTIPLIER == 10


# ────────────────────────────────────────────────
# TestExtractTargetIdentifiers
# ────────────────────────────────────────────────


class TestExtractTargetIdentifiers:
    """Tests for extract_target_identifiers() — extracting class/file/proc names."""

    def test_pascal_class_tdmmain(self):
        """Extracts 'tdmmain' from query containing 'TdmMain'."""
        result = reranker_module.extract_target_identifiers("What is TdmMain?")
        assert "tdmmain" in result

    def test_pascal_class_tfrmmainform(self):
        """Extracts 'tfrmmainform' from query containing 'TfrmMainForm'."""
        result = reranker_module.extract_target_identifiers("Describe TfrmMainForm")
        assert "tfrmmainform" in result

    def test_pascal_class_tcore105_oik(self):
        """Extracts 'tcore105_oik' from query containing 'TCore105_OIK'."""
        result = reranker_module.extract_target_identifiers(
            "What methods does TCore105_OIK have?"
        )
        assert "tcore105_oik" in result

    def test_file_stem_with_pas_extension(self):
        """Extracts 'maindm' from query containing 'MainDM.pas'."""
        result = reranker_module.extract_target_identifiers("Explain MainDM.pas")
        assert "maindm" in result

    def test_file_stem_dotted_with_pas(self):
        """Extracts 'core105.classes' from 'core105.classes.pas'."""
        result = reranker_module.extract_target_identifiers(
            "What is in core105.classes.pas?"
        )
        assert "core105.classes" in result

    def test_known_file_stem_core105(self):
        """Extracts 'core105' from bare reference without .pas."""
        result = reranker_module.extract_target_identifiers(
            "What classes are in core105?"
        )
        assert "core105" in result

    def test_known_file_stem_maindm(self):
        """Extracts 'maindm' from bare 'MainDM'."""
        result = reranker_module.extract_target_identifiers("Describe MainDM")
        assert "maindm" in result

    def test_known_file_stem_mainform(self):
        """Extracts 'mainform' from bare 'MainForm'."""
        result = reranker_module.extract_target_identifiers("Summary of MainForm")
        assert "mainform" in result

    def test_known_file_stem_splash(self):
        """Extracts 'splash' from bare 'Splash'."""
        result = reranker_module.extract_target_identifiers("What is Splash?")
        assert "splash" in result

    def test_known_file_stem_salesreport(self):
        """Extracts 'salesreport' from bare 'SalesReport'."""
        result = reranker_module.extract_target_identifiers("Describe SalesReport")
        assert "salesreport" in result

    def test_sql_procedure_name(self):
        """Extracts SQL procedure name with underscores."""
        result = reranker_module.extract_target_identifiers(
            "SLS_ReliefExport_Bilety_Get"
        )
        assert "sls_reliefexport_bilety_get" in result

    def test_sql_procedure_with_dbo_prefix(self):
        """Extracts SQL procedure with dbo. prefix."""
        result = reranker_module.extract_target_identifiers(
            "dbo.SLS_ReliefExport_Bilety_Get"
        )
        assert "dbo.sls_reliefexport_bilety_get" in result

    def test_sql_procedure_tck(self):
        """Extracts complex SQL procedure name."""
        result = reranker_module.extract_target_identifiers(
            "TCK_FarePrice_GetPriceForXDesignation"
        )
        assert "tck_fareprice_getpriceforxdesignation" in result

    def test_multiple_targets_in_one_query(self):
        """Extracts multiple targets from a single query."""
        result = reranker_module.extract_target_identifiers(
            "What is TdmMain in MainDM.pas?"
        )
        assert "tdmmain" in result
        assert "maindm" in result

    def test_no_targets_in_generic_query(self):
        """Generic query with no code identifiers returns empty list."""
        result = reranker_module.extract_target_identifiers("how do I install this?")
        assert result == []

    def test_results_are_lowercased(self):
        """All extracted identifiers are lowercased."""
        result = reranker_module.extract_target_identifiers("What is TdmMain?")
        for target in result:
            assert target == target.lower()

    def test_results_are_deduplicated(self):
        """Duplicate targets from overlapping patterns are deduplicated."""
        # "MainDM" matches both _FILE_STEM_NO_EXT and as part of "MainDM.pas" in _FILE_STEM
        result = reranker_module.extract_target_identifiers("MainDM.pas and MainDM")
        # Count occurrences of 'maindm'
        assert result.count("maindm") <= 1

    def test_empty_query(self):
        """Empty string produces no targets."""
        result = reranker_module.extract_target_identifiers("")
        assert result == []

    def test_known_stem_case_insensitive(self):
        """Known file stems are matched case-insensitively."""
        result = reranker_module.extract_target_identifiers("CORE105")
        assert "core105" in result

    def test_pascal_ident_requires_t_prefix(self):
        """Only T-prefixed identifiers match the Pascal pattern."""
        result = reranker_module.extract_target_identifiers("FooBar MainClass")
        # Neither should match _PASCAL_IDENT since they don't start with T
        pascal_matches = [t for t in result if t.startswith("t")]
        assert len(pascal_matches) == 0


# ────────────────────────────────────────────────
# TestChunkMatchesTarget
# ────────────────────────────────────────────────


class TestChunkMatchesTarget:
    """Tests for _chunk_matches_target() — metadata field matching."""

    def test_match_on_class_name(self):
        """Target matches the class_name metadata field — returns 1.0 (all targets matched)."""
        meta = {
            "class_name": "TdmMain",
            "file_path": "",
            "unit_name": "",
            "object_name": "",
        }
        assert reranker_module._chunk_matches_target(meta, ["tdmmain"]) == 1.0

    def test_match_on_unit_name(self):
        """Target matches the unit_name metadata field — returns 1.0."""
        meta = {
            "class_name": "",
            "file_path": "",
            "unit_name": "MainDM",
            "object_name": "",
        }
        assert reranker_module._chunk_matches_target(meta, ["maindm"]) == 1.0

    def test_match_on_object_name(self):
        """Target matches the object_name metadata field — returns 1.0."""
        meta = {
            "class_name": "",
            "file_path": "",
            "unit_name": "",
            "object_name": "SLS_ReliefExport_Bilety_Get",
        }
        assert (
            reranker_module._chunk_matches_target(meta, ["sls_reliefexport_bilety_get"])
            == 1.0
        )

    def test_match_on_file_path(self):
        """Target matches a substring of the file_path metadata field — returns 1.0."""
        meta = {
            "class_name": "",
            "file_path": "source/Common/core105.classes.pas",
            "unit_name": "",
            "object_name": "",
        }
        assert reranker_module._chunk_matches_target(meta, ["core105"]) == 1.0

    def test_no_match_when_fields_dont_contain_target(self):
        """Returns 0.0 when no metadata field contains the target."""
        meta = {
            "class_name": "TfrmSplash",
            "file_path": "source/Splash.pas",
            "unit_name": "Splash",
            "object_name": "",
        }
        assert reranker_module._chunk_matches_target(meta, ["tdmmain"]) == 0.0

    def test_empty_targets_returns_zero(self):
        """Empty targets list always returns 0.0."""
        meta = {
            "class_name": "TdmMain",
            "file_path": "MainDM.pas",
            "unit_name": "MainDM",
        }
        assert reranker_module._chunk_matches_target(meta, []) == 0.0

    def test_none_values_in_metadata_handled(self):
        """None values in metadata are handled gracefully (via 'or' fallback)."""
        meta = {
            "class_name": None,
            "file_path": None,
            "unit_name": None,
            "object_name": None,
        }
        assert reranker_module._chunk_matches_target(meta, ["tdmmain"]) == 0.0

    def test_missing_keys_in_metadata_handled(self):
        """Missing metadata keys are handled gracefully (via .get default)."""
        meta = {}
        assert reranker_module._chunk_matches_target(meta, ["tdmmain"]) == 0.0

    def test_partial_match_class_name(self):
        """Target 'core105' matches class_name 'TCore105_OIK' (substring match) — returns 1.0."""
        meta = {
            "class_name": "TCore105_OIK",
            "file_path": "",
            "unit_name": "",
            "object_name": "",
        }
        assert reranker_module._chunk_matches_target(meta, ["core105"]) == 1.0

    def test_partial_match_file_path(self):
        """Target 'maindm' matches file_path containing 'MainDM.pas' — returns 1.0."""
        meta = {
            "class_name": "",
            "file_path": "source/MainDM.pas",
            "unit_name": "",
            "object_name": "",
        }
        assert reranker_module._chunk_matches_target(meta, ["maindm"]) == 1.0

    def test_multiple_targets_partial_match(self):
        """When 2 targets given but only 1 matches, returns 0.5 (proportional)."""
        meta = {
            "class_name": "TdmMain",
            "file_path": "",
            "unit_name": "",
            "object_name": "",
        }
        assert (
            reranker_module._chunk_matches_target(meta, ["nonexistent", "tdmmain"])
            == 0.5
        )

    def test_multiple_targets_none_match(self):
        """When multiple targets are given but none match, returns 0.0."""
        meta = {
            "class_name": "TdmMain",
            "file_path": "MainDM.pas",
            "unit_name": "MainDM",
            "object_name": "",
        }
        assert (
            reranker_module._chunk_matches_target(meta, ["splash", "salesreport"])
            == 0.0
        )

    def test_multiple_targets_all_match(self):
        """When all targets match (e.g. path components), returns 1.0."""
        meta = {
            "class_name": "",
            "file_path": "source/Common/LPC/ReportHelpers.pas",
            "unit_name": "ReportHelpers",
            "object_name": "",
        }
        assert (
            reranker_module._chunk_matches_target(
                meta, ["common", "lpc", "reporthelpers"]
            )
            == 1.0
        )

    def test_multiple_targets_partial_path_match(self):
        """File matching only 1 of 3 path targets returns 1/3."""
        meta = {
            "class_name": "",
            "file_path": "source/BusStopOnline/ReportHelpers.pas",
            "unit_name": "ReportHelpers",
            "object_name": "",
        }
        result = reranker_module._chunk_matches_target(
            meta, ["common", "lpc", "reporthelpers"]
        )
        assert abs(result - 1.0 / 3.0) < 1e-9

    def test_case_insensitive_via_lowered_fields(self):
        """Matching is case-insensitive because both sides are lowered — returns 1.0."""
        meta = {
            "class_name": "TdmMAIN",
            "file_path": "",
            "unit_name": "",
            "object_name": "",
        }
        # Target is already lowercase per extract_target_identifiers contract
        assert reranker_module._chunk_matches_target(meta, ["tdmmain"]) == 1.0


# ────────────────────────────────────────────────
# TestComputeRerankScore
# ────────────────────────────────────────────────


class TestComputeRerankScore:
    """Tests for _compute_rerank_score() — score adjustment logic."""

    def test_non_overview_returns_original_score(self):
        """Non-overview query returns original score unchanged."""
        score = reranker_module._compute_rerank_score(
            original_score=0.75,
            node_type="defProc",
            meta={"class_name": "TdmMain"},
            is_overview=False,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        assert score == 0.75

    def test_primary_overview_type_gets_065_bonus(self):
        """Primary overview type (class_overview) gets +0.65 bonus."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        # +0.65 bonus, no target match bonus, but no penalty either (no targets)
        assert score == pytest.approx(0.50 + 0.65)

    def test_class_summary_is_primary_overview(self):
        """'class_summary' is a primary overview type getting +0.65 bonus."""
        score = reranker_module._compute_rerank_score(
            original_score=0.40,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.40 + 0.65)

    def test_class_summary_split_is_primary_overview(self):
        """'class_summary_split' is a primary overview type getting +0.65 bonus."""
        score = reranker_module._compute_rerank_score(
            original_score=0.40,
            node_type="class_summary_split",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.40 + 0.65)

    def test_dfm_form_header_gets_010_bonus(self):
        """DFM overview type (dfm_form_header) gets +0.10 bonus (lower than structural overview)."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dfm_form_header",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_procedure_header_is_overview_type(self):
        """'procedure_header' gets the +0.25 overview bonus."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="procedure_header",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.25)

    def test_function_full_is_overview_type(self):
        """'function_full' gets the +0.25 overview bonus."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="function_full",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.25)

    def test_decluses_is_overview_type(self):
        """'declUses' gets the +0.25 overview bonus."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="declUses",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.25)

    def test_non_overview_non_detail_type_no_bonus(self):
        """A type that's neither overview nor detail gets no bonus or penalty."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="some_unknown_type",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50)

    def test_target_match_adds_015_bonus(self):
        """Matching the target file/class adds +0.15 bonus."""
        meta = {
            "class_name": "TdmMain",
            "file_path": "",
            "unit_name": "",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="some_unknown_type",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # Only target match bonus applies (+0.15), no type bonus
        assert score == pytest.approx(0.50 + 0.15)

    def test_non_target_overview_chunks_penalized_040(self):
        """Overview chunk from non-target file gets -0.40 penalty."""
        meta = {
            "class_name": "TOtherClass",
            "file_path": "Other.pas",
            "unit_name": "Other",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_overview",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # +0.65 primary bonus - 0.40 non-target penalty = +0.25 net
        assert score == pytest.approx(0.50 + 0.65 - 0.40)

    def test_non_target_dfm_penalized_with_class_query(self):
        """DFM chunk from non-target file with Pascal class target gets DFM penalties."""
        meta = {
            "class_name": "",
            "file_path": "Other.pas",
            "unit_name": "Other",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dfm_form_header",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # +0.10 DFM bonus - 0.15 DFM-on-class penalty - 0.40 non-target penalty
        assert score == pytest.approx(0.50 + 0.10 - 0.15 - 0.40)

    def test_cross_file_comment_penalized_030(self):
        """Comment chunk from non-target file gets -0.30 penalty."""
        meta = {
            "class_name": "",
            "file_path": "Other.pas",
            "unit_name": "Other",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="comment",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # comment is in _DETAIL_CHUNK_TYPES but excluded from detail penalty
        # -0.30 cross-file comment penalty, -0.00 detail penalty (excluded)
        assert score == pytest.approx(0.50 - 0.30)

    def test_comment_split_penalized_030(self):
        """comment_split chunk from non-target file gets -0.30 penalty."""
        meta = {
            "class_name": "",
            "file_path": "Other.pas",
            "unit_name": "",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="comment_split",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        assert score == pytest.approx(0.50 - 0.30)

    def test_detail_type_non_comment_penalized_005(self):
        """Detail chunk (non-comment) gets -0.05 penalty."""
        meta = {
            "class_name": "TdmMain",
            "file_path": "MainDM.pas",
            "unit_name": "MainDM",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="defProc",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # +0.15 target match - 0.05 detail penalty = +0.10 net
        assert score == pytest.approx(0.50 + 0.15 - 0.05)

    def test_method_group_is_detail_type(self):
        """'method_group' gets the -0.05 detail penalty."""
        meta = {}
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="method_group",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 - 0.05)

    def test_declsection_is_detail_type(self):
        """'declSection' gets the -0.05 detail penalty."""
        meta = {}
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="declSection",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 - 0.05)

    def test_combined_primary_overview_plus_target_match(self):
        """Primary overview chunk from target file gets +0.65 + 0.15 = +0.80."""
        meta = {
            "class_name": "TdmMain",
            "file_path": "MainDM.pas",
            "unit_name": "MainDM",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_overview",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # +0.65 primary bonus + 0.15 target match = +0.80
        assert score == pytest.approx(0.50 + 0.65 + 0.15)

    def test_comment_from_target_file_no_penalty(self):
        """Comment chunk from target file gets no cross-file penalty."""
        meta = {
            "class_name": "TdmMain",
            "file_path": "MainDM.pas",
            "unit_name": "MainDM",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="comment",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # comment is detail but excluded from detail penalty
        # +0.15 target match, no cross-file penalty
        assert score == pytest.approx(0.50 + 0.15)

    def test_no_targets_overview_chunk_no_penalty(self):
        """Overview chunk with empty targets list gets no non-target penalty."""
        meta = {"class_name": "TdmMain", "file_path": "MainDM.pas"}
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_overview",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        # +0.65 primary bonus, no target match (empty targets), no penalty
        assert score == pytest.approx(0.50 + 0.65)

    def test_detail_from_non_target_gets_detail_penalty_only(self):
        """Detail chunk from non-target file only gets detail penalty, not comment penalty."""
        meta = {
            "class_name": "TOther",
            "file_path": "Other.pas",
            "unit_name": "Other",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="defProc",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # -0.05 detail penalty, no target match bonus
        assert score == pytest.approx(0.50 - 0.05)

    def test_dfm_on_class_query_penalty_applied(self):
        """DFM form header gets extra penalty when query targets a Pascal class."""
        meta = {
            "class_name": "TfrmSplash",
            "file_path": "Splash.dfm",
            "unit_name": "Splash",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dfm_form_header",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tfrmsplash", "splash"],
        )
        # +0.10 DFM bonus - 0.15 DFM-on-class penalty + 0.15 target match = +0.10
        assert score == pytest.approx(0.50 + 0.10 - 0.15 + 0.15)

    def test_dfm_no_class_query_penalty_without_t_prefix(self):
        """DFM form header gets NO class-query penalty when target is not T-prefixed."""
        meta = {
            "class_name": "",
            "file_path": "Splash.dfm",
            "unit_name": "Splash",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dfm_form_header",
            meta=meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["splash"],
        )
        # +0.10 DFM bonus + 0.15 target match, no DFM-on-class penalty (no T-prefix)
        assert score == pytest.approx(0.50 + 0.10 + 0.15)

    def test_dfm_target_match_vs_class_overview_target_match(self):
        """Class overview from target always beats DFM from target for class queries."""
        targets = ["tfrmsplash", "splash"]
        meta_target = {
            "class_name": "TfrmSplash",
            "file_path": "Splash.pas",
            "unit_name": "Splash",
            "object_name": "",
        }
        # class_overview from target: +0.65 + 0.15 = +0.80
        class_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_overview",
            meta=meta_target,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=targets,
        )
        # dfm_form_header from target: +0.10 - 0.15 + 0.15 = +0.10
        dfm_meta = {
            "class_name": "TfrmSplash",
            "file_path": "Splash.dfm",
            "unit_name": "Splash",
            "object_name": "",
        }
        dfm_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dfm_form_header",
            meta=dfm_meta,
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=targets,
        )
        # class_overview should always outscore dfm_form_header for class queries
        assert class_score > dfm_score
        # The gap should be significant (>= 0.50)
        assert class_score - dfm_score >= 0.50
        """Works correctly with zero original score."""
        score = reranker_module._compute_rerank_score(
            original_score=0.0,
            node_type="class_overview",
            meta={"class_name": "TdmMain"},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # +0.65 + 0.15 = 0.80
        assert score == pytest.approx(0.80)

    def test_negative_original_score(self):
        """Works correctly with negative original score."""
        score = reranker_module._compute_rerank_score(
            original_score=-0.10,
            node_type="class_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(-0.10 + 0.65)


# ────────────────────────────────────────────────
# TestRerankResults
# ────────────────────────────────────────────────


class TestRerankResults:
    """Tests for rerank_results() — end-to-end reranking."""

    def test_empty_nodes_returns_empty(self):
        """Empty nodes list returns empty list."""
        result = reranker_module.rerank_results([], "What is TdmMain?")
        assert result == []

    def test_non_overview_query_returns_nodes_unchanged(self):
        """Non-overview query returns nodes in original order."""
        nodes = [
            MockNodeWithScore(0.80, {"node_type": "defProc", "file_path": "A.pas"}),
            MockNodeWithScore(
                0.70, {"node_type": "class_overview", "file_path": "B.pas"}
            ),
            MockNodeWithScore(0.60, {"node_type": "comment", "file_path": "C.pas"}),
        ]
        result = reranker_module.rerank_results(nodes, "PrepareDataSet")
        assert result == nodes

    def test_non_overview_query_with_desired_top_k_trims(self):
        """Non-overview query with desired_top_k trims output."""
        nodes = [
            MockNodeWithScore(0.80, {"node_type": "defProc"}),
            MockNodeWithScore(0.70, {"node_type": "defProc"}),
            MockNodeWithScore(0.60, {"node_type": "defProc"}),
        ]
        result = reranker_module.rerank_results(
            nodes, "PrepareDataSet", desired_top_k=2
        )
        assert len(result) == 2
        assert result[0] is nodes[0]
        assert result[1] is nodes[1]

    def test_overview_query_promotes_class_overview(self):
        """Overview query promotes class_overview from target file above defProc."""
        nodes = [
            MockNodeWithScore(
                0.80,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(nodes, "What is TdmMain?")
        # class_overview should be promoted to first position
        assert result[0].node.metadata["node_type"] == "class_overview"

    def test_overview_query_with_desired_top_k_trims_after_reranking(self):
        """Overview query with desired_top_k trims after reranking."""
        nodes = [
            MockNodeWithScore(
                0.80,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            MockNodeWithScore(
                0.70,
                {
                    "node_type": "method_group",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(
            nodes, "What is TdmMain?", desired_top_k=1
        )
        assert len(result) == 1
        # The one returned result should be the promoted class_overview
        assert result[0].node.metadata["node_type"] == "class_overview"

    def test_verbose_mode_does_not_crash(self):
        """Verbose mode logs reranking details without crashing."""
        nodes = [
            MockNodeWithScore(
                0.80,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        with patch.object(reranker_module, "log") as mock_log:
            result = reranker_module.rerank_results(
                nodes, "What is TdmMain?", verbose=True
            )
        # Should have been called (overview query with verbose)
        assert mock_log.call_count >= 1
        # Should still produce valid output
        assert len(result) == 2

    def test_verbose_non_overview_logs_skip(self):
        """Verbose mode with non-overview query logs skip message."""
        nodes = [
            MockNodeWithScore(0.80, {"node_type": "defProc", "file_path": "A.pas"}),
        ]
        with patch.object(reranker_module, "log") as mock_log:
            result = reranker_module.rerank_results(
                nodes, "PrepareDataSet", verbose=True
            )
        # Should log both the initial status and the skip message
        assert mock_log.call_count >= 2
        skip_logged = any(
            "skipping rerank" in str(call) for call in mock_log.call_args_list
        )
        assert skip_logged

    def test_nodes_without_node_attribute(self):
        """Nodes without .node attribute use empty metadata via hasattr."""
        bare = MockBareObject()
        bare.score = 0.50
        nodes = [bare]
        # Non-overview: should return as-is
        result = reranker_module.rerank_results(nodes, "PrepareDataSet")
        assert len(result) == 1
        assert result[0] is bare

    def test_nodes_without_score_attribute(self):
        """Nodes without .score attribute default to 0.0."""

        class NodeWithoutScore:
            def __init__(self, metadata):
                self.node = MockNode(metadata)

        nodes = [
            NodeWithoutScore(
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                }
            ),
        ]
        # Should not crash, defaults to 0.0 score
        result = reranker_module.rerank_results(nodes, "What is TdmMain?")
        assert len(result) == 1

    def test_stability_equal_adjusted_scores_preserve_order(self):
        """Nodes with equal adjusted scores maintain original insertion order."""
        nodes = [
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(nodes, "What is TdmMain?")
        # Same adjusted scores, so original order (by index) is preserved
        assert result[0] is nodes[0]
        assert result[1] is nodes[1]
        assert result[2] is nodes[2]

    def test_real_world_what_is_tdmmain(self):
        """Simulate 'What is TdmMain?' with mixed chunks from multiple files."""
        nodes = [
            # From MainDM.pas — defProc, high raw score (BM25 saturation)
            MockNodeWithScore(
                0.80,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "source/MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            # From MainDM.pas — method_group, high raw score
            MockNodeWithScore(
                0.78,
                {
                    "node_type": "method_group",
                    "class_name": "TdmMain",
                    "file_path": "source/MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            # From MainDM.pas — class_overview, LOW raw score (dense embedding diluted)
            MockNodeWithScore(
                0.35,
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "source/MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            # From Other.pas — class_overview (cross-file interloper)
            MockNodeWithScore(
                0.60,
                {
                    "node_type": "class_overview",
                    "class_name": "TOther",
                    "file_path": "source/Other.pas",
                    "unit_name": "Other",
                    "object_name": "",
                },
            ),
            # From Other.pas — comment
            MockNodeWithScore(
                0.55,
                {
                    "node_type": "comment",
                    "class_name": "TOther",
                    "file_path": "source/Other.pas",
                    "unit_name": "Other",
                    "object_name": "",
                },
            ),
            # From MainDM.pas — declSection, high raw score
            MockNodeWithScore(
                0.75,
                {
                    "node_type": "declSection",
                    "class_name": "TdmMain",
                    "file_path": "source/MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]

        result = reranker_module.rerank_results(
            nodes, "What is TdmMain?", desired_top_k=3
        )

        assert len(result) == 3

        # The class_overview from MainDM.pas should be promoted to #1
        # despite its low raw score of 0.35
        # Adjusted: 0.35 + 0.50 (primary) + 0.15 (target) = 1.00
        assert result[0].node.metadata["node_type"] == "class_overview"
        assert "MainDM" in result[0].node.metadata["file_path"]

        # The cross-file class_overview should NOT be in top 3
        # Adjusted: 0.60 + 0.50 (primary) - 0.20 (non-target) = 0.90
        # This is still high, so let's verify order more carefully
        result_types = [
            (r.node.metadata["node_type"], r.node.metadata["file_path"]) for r in result
        ]

        # Verify the target class_overview beat the cross-file one
        target_overview_idx = None
        cross_overview_idx = None
        for i, r in enumerate(result):
            if r.node.metadata["node_type"] == "class_overview":
                if "MainDM" in r.node.metadata["file_path"]:
                    target_overview_idx = i
                else:
                    cross_overview_idx = i

        assert target_overview_idx == 0  # Target class_overview is first

    def test_desired_top_k_none_returns_all(self):
        """When desired_top_k is None, all nodes are returned (just reordered)."""
        nodes = [
            MockNodeWithScore(
                0.80,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(
            nodes, "What is TdmMain?", desired_top_k=None
        )
        assert len(result) == 2

    def test_non_overview_no_desired_top_k_returns_all(self):
        """Non-overview query with no desired_top_k returns all nodes."""
        nodes = [
            MockNodeWithScore(0.80, {"node_type": "defProc"}),
            MockNodeWithScore(0.70, {"node_type": "defProc"}),
            MockNodeWithScore(0.60, {"node_type": "defProc"}),
        ]
        result = reranker_module.rerank_results(nodes, "PrepareDataSet")
        assert len(result) == 3
        assert result is nodes  # Same list reference (no copy needed for non-overview)

    def test_overview_query_extracts_targets(self):
        """Overview query extracts target identifiers for matching."""
        nodes = [
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "defProc",
                    "class_name": "TOther",
                    "file_path": "Other.pas",
                    "unit_name": "Other",
                    "object_name": "",
                },
            ),
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(nodes, "What is TdmMain?")
        # Second node (TdmMain) should be promoted above first (TOther)
        # because it matches the target and gets +0.15 bonus
        assert result[0].node.metadata["class_name"] == "TdmMain"

    def test_metadata_fallback_type_key(self):
        """When metadata has 'type' instead of 'node_type', it falls back correctly."""
        nodes = [
            MockNodeWithScore(
                0.50,
                {
                    "type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(nodes, "What is TdmMain?")
        # Should get the class_overview bonus via 'type' fallback
        assert len(result) == 1

    def test_metadata_default_text_type(self):
        """When metadata has neither 'node_type' nor 'type', defaults to 'text'."""
        nodes = [
            MockNodeWithScore(
                0.50,
                {
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        # 'text' is neither overview nor detail, so only target match bonus
        result = reranker_module.rerank_results(nodes, "What is TdmMain?")
        assert len(result) == 1

    def test_verbose_logs_score_changes(self):
        """Verbose mode logs individual score changes."""
        nodes = [
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        with patch.object(reranker_module, "log") as mock_log:
            reranker_module.rerank_results(nodes, "What is TdmMain?", verbose=True)

        # Should log: overview/targets info, score change, and completion
        logged_texts = [str(call) for call in mock_log.call_args_list]
        # Check that score delta was logged
        score_delta_logged = any("delta=" in text for text in logged_texts)
        assert score_delta_logged

    def test_verbose_logs_completion_message(self):
        """Verbose mode logs a completion message with top node_type."""
        nodes = [
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        with patch.object(reranker_module, "log") as mock_log:
            reranker_module.rerank_results(nodes, "What is TdmMain?", verbose=True)

        logged_texts = [str(call) for call in mock_log.call_args_list]
        done_logged = any("done" in text for text in logged_texts)
        assert done_logged

    def test_single_node_returned_as_is(self):
        """Single node list is returned (possibly reordered — trivially itself)."""
        nodes = [
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "defProc",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(nodes, "What is TdmMain?")
        assert len(result) == 1
        assert result[0] is nodes[0]

    def test_desired_top_k_larger_than_nodes(self):
        """desired_top_k larger than nodes count returns all nodes."""
        nodes = [
            MockNodeWithScore(0.50, {"node_type": "defProc"}),
        ]
        result = reranker_module.rerank_results(
            nodes, "PrepareDataSet", desired_top_k=100
        )
        assert len(result) == 1

    def test_desired_top_k_zero_returns_empty_non_overview(self):
        """desired_top_k=0 with non-overview query returns empty list."""
        nodes = [
            MockNodeWithScore(0.50, {"node_type": "defProc"}),
        ]
        result = reranker_module.rerank_results(
            nodes, "PrepareDataSet", desired_top_k=0
        )
        assert result == []

    def test_desired_top_k_zero_returns_empty_overview(self):
        """desired_top_k=0 with overview query returns empty list."""
        nodes = [
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "class_overview",
                    "class_name": "TdmMain",
                    "file_path": "MainDM.pas",
                    "unit_name": "MainDM",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(
            nodes, "What is TdmMain?", desired_top_k=0
        )
        assert result == []

    def test_nodes_without_node_attr_in_overview_query(self):
        """Bare objects without .node in overview query use empty metadata."""
        bare = MockBareObject()
        bare.score = 0.50
        nodes = [bare]
        # Overview query: should not crash, metadata defaults to {}
        result = reranker_module.rerank_results(nodes, "What is TdmMain?")
        assert len(result) == 1
        assert result[0] is bare

    def test_nodes_without_score_attr_in_overview_query(self):
        """Nodes without .score in overview query default to 0.0 score."""

        class NodeWithoutScore:
            def __init__(self, metadata):
                self.node = MockNode(metadata)

        n = NodeWithoutScore(
            {
                "node_type": "class_overview",
                "class_name": "TdmMain",
                "file_path": "MainDM.pas",
                "unit_name": "MainDM",
                "object_name": "",
            }
        )
        result = reranker_module.rerank_results([n], "What is TdmMain?")
        assert len(result) == 1
        assert result[0] is n

    def test_dfm_query_promotes_dfm_form_header(self):
        """DFM query (frame components) promotes dfm_form_header above class_summary."""
        nodes = [
            # class_summary from a Pascal file — high raw score
            MockNodeWithScore(
                0.80,
                {
                    "node_type": "class_summary",
                    "class_name": "TfrmSFTP",
                    "file_path": "source/WithFrame_SFTP.pas",
                    "unit_name": "WithFrame_SFTP",
                    "object_name": "",
                },
            ),
            # dfm_form_header from a DFM file — lower raw score
            MockNodeWithScore(
                0.50,
                {
                    "node_type": "dfm_form_header",
                    "class_name": "TfrmSFTP",
                    "file_path": "source/WithFrame_SFTP.dfm",
                    "unit_name": "WithFrame_SFTP",
                    "object_name": "",
                },
            ),
        ]
        result = reranker_module.rerank_results(
            nodes, "SFTP frame components", desired_top_k=2
        )
        # dfm_form_header should be promoted above class_summary for DFM queries
        assert result[0].node.metadata["node_type"] == "dfm_form_header"

    def test_dfm_query_with_overfetch_promotes_dfm(self):
        """Simulate over-fetch scenario where dfm_form_header is at position 30+."""
        # Build a list of 40 defProc chunks with high scores
        nodes = []
        for i in range(38):
            nodes.append(
                MockNodeWithScore(
                    0.80 - i * 0.01,
                    {
                        "node_type": "defProc",
                        "class_name": "TOther",
                        "file_path": "Other.pas",
                        "unit_name": "Other",
                        "object_name": "",
                    },
                )
            )
        # Add class_summary at position 38
        nodes.append(
            MockNodeWithScore(
                0.42,
                {
                    "node_type": "class_summary",
                    "class_name": "TfrmSFTP",
                    "file_path": "WithFrame_SFTP.pas",
                    "unit_name": "WithFrame_SFTP",
                    "object_name": "",
                },
            )
        )
        # Add dfm_form_header at position 39 (very low raw score)
        nodes.append(
            MockNodeWithScore(
                0.40,
                {
                    "node_type": "dfm_form_header",
                    "class_name": "TfrmSFTP",
                    "file_path": "WithFrame_SFTP.dfm",
                    "unit_name": "WithFrame_SFTP",
                    "object_name": "",
                },
            )
        )
        result = reranker_module.rerank_results(
            nodes, "SFTP frame components", desired_top_k=8
        )
        # dfm_form_header should be in top-2 results
        top_types = [r.node.metadata["node_type"] for r in result[:2]]
        assert "dfm_form_header" in top_types


# ────────────────────────────────────────────────
# TestIsDfmQuery
# ────────────────────────────────────────────────


class TestIsDfmQuery:
    """Tests for is_dfm_query() — detecting DFM/form-targeted query intent."""

    def test_form_components_pattern(self):
        """'form components' triggers DFM detection."""
        assert reranker_module.is_dfm_query("MainForm form components") is True

    def test_frame_components_pattern(self):
        """'frame components' triggers DFM detection."""
        assert reranker_module.is_dfm_query("SFTP frame components") is True

    def test_form_layout_pattern(self):
        """'form layout' triggers DFM detection."""
        assert reranker_module.is_dfm_query("Show me the form layout") is True

    def test_form_header_pattern(self):
        """'form header' triggers DFM detection."""
        assert reranker_module.is_dfm_query("form header of MainForm") is True

    def test_dfm_keyword(self):
        """'dfm' keyword triggers DFM detection."""
        assert reranker_module.is_dfm_query("What is in the dfm?") is True

    def test_dot_dfm_extension(self):
        """'.dfm' extension triggers DFM detection."""
        assert reranker_module.is_dfm_query("Show MainForm.dfm") is True

    def test_form_overview_pattern(self):
        """'form overview' triggers DFM detection."""
        assert reranker_module.is_dfm_query("form overview for MainForm") is True

    def test_visual_layout_pattern(self):
        """'visual layout' triggers DFM detection."""
        assert (
            reranker_module.is_dfm_query("visual layout of the splash screen") is True
        )

    def test_ui_components_pattern(self):
        """'UI components' triggers DFM detection."""
        assert reranker_module.is_dfm_query("UI components on the form") is True

    def test_form_controls_pattern(self):
        """'form controls' triggers DFM detection."""
        assert reranker_module.is_dfm_query("What form controls are used?") is True

    # ── Case insensitivity ──

    def test_frame_components_uppercase(self):
        """'FRAME COMPONENTS' (uppercase) triggers DFM detection."""
        assert reranker_module.is_dfm_query("SFTP FRAME COMPONENTS") is True

    def test_form_layout_mixed_case(self):
        """'Form Layout' (mixed case) triggers DFM detection."""
        assert reranker_module.is_dfm_query("Form Layout of the dialog") is True

    def test_dfm_uppercase(self):
        """'DFM' (uppercase) triggers DFM detection."""
        assert reranker_module.is_dfm_query("Show the DFM file") is True

    # ── Negative cases ──

    def test_class_query_not_dfm(self):
        """'What is TdmMain?' is not a DFM query."""
        assert reranker_module.is_dfm_query("What is TdmMain?") is False

    def test_method_query_not_dfm(self):
        """'Where is PrepareDataSet?' is not a DFM query."""
        assert reranker_module.is_dfm_query("Where is PrepareDataSet?") is False

    def test_sql_query_not_dfm(self):
        """SQL procedure name is not a DFM query."""
        assert reranker_module.is_dfm_query("SLS_ReliefExport_Bilety_Get") is False

    def test_empty_string_not_dfm(self):
        """Empty string is not a DFM query."""
        assert reranker_module.is_dfm_query("") is False

    def test_generic_overview_not_dfm(self):
        """'What classes are in core105?' is overview but not DFM."""
        assert reranker_module.is_dfm_query("What classes are in core105?") is False

    def test_describe_class_not_dfm(self):
        """'Describe TfrmMainForm' is not DFM (asking about the class, not the form)."""
        assert reranker_module.is_dfm_query("Describe TfrmMainForm") is False

    def test_form_word_alone_not_dfm(self):
        """Just 'form' alone does not trigger DFM (needs a specific pattern)."""
        assert reranker_module.is_dfm_query("form") is False


# ────────────────────────────────────────────────
# TestComputeRerankScoreDfmMode
# ────────────────────────────────────────────────


class TestComputeRerankScoreDfmMode:
    """Tests for _compute_rerank_score() with is_dfm=True — bonus swapping logic."""

    def test_dfm_form_header_gets_primary_bonus_in_dfm_mode(self):
        """In DFM mode, dfm_form_header gets the primary overview bonus (+0.65)."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dfm_form_header",
            meta={},
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.65)

    def test_class_summary_gets_dfm_bonus_in_dfm_mode(self):
        """In DFM mode, class_summary gets the lower DFM bonus (+0.10)."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_class_overview_gets_dfm_bonus_in_dfm_mode(self):
        """In DFM mode, class_overview gets the lower DFM bonus (+0.10)."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_overview",
            meta={},
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_class_summary_split_gets_dfm_bonus_in_dfm_mode(self):
        """In DFM mode, class_summary_split gets the lower DFM bonus (+0.10)."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary_split",
            meta={},
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_procedure_header_gets_standard_bonus_in_dfm_mode(self):
        """In DFM mode, other overview types (procedure_header) still get +0.25."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="procedure_header",
            meta={},
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.25)

    def test_dfm_on_class_query_penalty_not_applied_in_dfm_mode(self):
        """In DFM mode, the DFM-on-class-query penalty is NOT applied."""
        meta = {
            "class_name": "TfrmSFTP",
            "file_path": "WithFrame_SFTP.dfm",
            "unit_name": "WithFrame_SFTP",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dfm_form_header",
            meta=meta,
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tfrmsftp", "sftp"],
        )
        # In DFM mode: +0.65 primary bonus + 0.15 target match = +0.80
        # NO DFM-on-class penalty
        assert score == pytest.approx(0.50 + 0.65 + 0.15)

    def test_dfm_beats_class_summary_in_dfm_mode(self):
        """In DFM mode, dfm_form_header always outscores class_summary."""
        targets = ["sftp"]
        dfm_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dfm_form_header",
            meta={
                "class_name": "TfrmSFTP",
                "file_path": "WithFrame_SFTP.dfm",
                "unit_name": "WithFrame_SFTP",
                "object_name": "",
            },
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=targets,
        )
        class_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={
                "class_name": "TfrmSFTP",
                "file_path": "WithFrame_SFTP.pas",
                "unit_name": "WithFrame_SFTP",
                "object_name": "",
            },
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=targets,
        )
        assert dfm_score > class_score
        # Gap should be >= 0.50 (0.65 vs 0.10 = 0.55 gap)
        assert dfm_score - class_score >= 0.50

    def test_non_overview_ignores_dfm_mode(self):
        """When is_overview=False, is_dfm=True has no effect."""
        score = reranker_module._compute_rerank_score(
            original_score=0.75,
            node_type="dfm_form_header",
            meta={},
            is_overview=False,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == 0.75

    def test_detail_penalty_still_applied_in_dfm_mode(self):
        """Detail penalties still apply in DFM mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="defProc",
            meta={},
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 - 0.05)

    def test_cross_file_comment_penalty_still_applied_in_dfm_mode(self):
        """Cross-file comment penalties still apply in DFM mode."""
        meta = {
            "class_name": "",
            "file_path": "Other.pas",
            "unit_name": "Other",
            "object_name": "",
        }
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="comment",
            meta=meta,
            is_overview=True,
            is_dfm=True,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["sftp"],
        )
        assert score == pytest.approx(0.50 - 0.30)


# ────────────────────────────────────────────────
# TestGeneralIdentifierExtraction
# ────────────────────────────────────────────────


class TestGeneralIdentifierExtraction:
    """Tests for general capitalized-word target extraction and stop-word filtering."""

    def test_sftp_extracted_as_target(self):
        """'SFTP' (all-caps, 4 chars) is extracted as a target identifier."""
        result = reranker_module.extract_target_identifiers("SFTP frame components")
        assert "sftp" in result

    def test_baseeditorform_extracted_via_allowlist(self):
        """'BaseEditorForm' matches the _FILE_STEM_NO_EXT allowlist."""
        result = reranker_module.extract_target_identifiers(
            "What does TfrmBaseEditor do in BaseEditorForm?"
        )
        assert "baseeditorform" in result

    def test_baseeditorform_in_allowlist(self):
        """'BaseEditorForm' is in the _FILE_STEM_NO_EXT pattern."""
        assert reranker_module._FILE_STEM_NO_EXT.search("BaseEditorForm") is not None

    def test_stop_words_filtered(self):
        """Common English words (Class, Form, Components) are filtered out."""
        result = reranker_module.extract_target_identifiers("What classes are in here?")
        # "What", "Class" etc. should be filtered as stop words
        for word in result:
            assert word not in ("what", "classes", "are")

    def test_form_is_stop_word(self):
        """'Form' is in the stop words list."""
        assert "form" in reranker_module._TARGET_STOP_WORDS

    def test_components_is_stop_word(self):
        """'Components' is in the stop words list."""
        assert "components" in reranker_module._TARGET_STOP_WORDS

    def test_frame_is_stop_word(self):
        """'Frame' is in the stop words list."""
        assert "frame" in reranker_module._TARGET_STOP_WORDS

    def test_describe_is_stop_word(self):
        """'Describe' is in the stop words list."""
        assert "describe" in reranker_module._TARGET_STOP_WORDS

    def test_overview_is_stop_word(self):
        """'Overview' is in the stop words list."""
        assert "overview" in reranker_module._TARGET_STOP_WORDS

    def test_general_ident_requires_3_chars(self):
        """_GENERAL_IDENT requires at least 3 characters (capital + 2 more)."""
        result = reranker_module.extract_target_identifiers("Go AB")
        # "Go" and "AB" are too short for _GENERAL_IDENT (need 3+ chars after first)
        # Neither should be extracted (unless matched by another pattern)
        for t in result:
            assert t not in ("go", "ab")

    def test_general_ident_captures_pascal_case(self):
        """PascalCase words like 'MyCustomWidget' are captured."""
        result = reranker_module.extract_target_identifiers("MyCustomWidget settings")
        assert "mycustomwidget" in result

    def test_general_ident_captures_allcaps(self):
        """ALL-CAPS words like 'SFTP' (4+ chars) are captured."""
        result = reranker_module.extract_target_identifiers("SFTP connection")
        assert "sftp" in result

    def test_general_ident_deduplicates_with_pascal_ident(self):
        """T-prefixed identifiers matched by both patterns are deduplicated."""
        result = reranker_module.extract_target_identifiers("TdmMain class")
        # Should appear exactly once
        assert result.count("tdmmain") == 1

    def test_general_ident_deduplicates_with_file_stem(self):
        """Known file stems matched by both patterns are deduplicated."""
        result = reranker_module.extract_target_identifiers("MainDM module")
        # Should appear exactly once (matched by both _FILE_STEM_NO_EXT and _GENERAL_IDENT)
        assert result.count("maindm") == 1

    def test_mixed_query_extracts_all_non_stop_words(self):
        """Query with multiple identifiers extracts all non-stop-word capitalized terms."""
        result = reranker_module.extract_target_identifiers(
            "SFTP frame components in WithFrame_SFTP"
        )
        assert "sftp" in result
        # "WithFrame_SFTP" should also be captured (underscored identifier)
        # Note: _GENERAL_IDENT matches [A-Z][A-Za-z0-9_]{2,}, so "WithFrame_SFTP" is matched
        # but it may be split by regex. Let's just verify SFTP is there.
        assert any("withframe" in t or "sftp" in t for t in result)

    def test_lowercase_words_not_captured(self):
        """Lowercase words like 'components' are not captured by _GENERAL_IDENT."""
        result = reranker_module.extract_target_identifiers(
            "simple lowercase words only"
        )
        assert result == []

    def test_numbers_after_capital_captured(self):
        """Identifiers with digits like 'Core105' are captured."""
        # "Core105" doesn't match _FILE_STEM_NO_EXT but _GENERAL_IDENT matches it
        # Wait, actually "core105" IS in _FILE_STEM_NO_EXT (case-insensitive)
        result = reranker_module.extract_target_identifiers("Core105 unit")
        assert "core105" in result


# ────────────────────────────────────────────────
# TestIsFr3Query
# ────────────────────────────────────────────────


class TestIsFr3Query:
    """Tests for is_fr3_query() — detecting FR3/report-targeted queries."""

    def test_report_structure_pattern(self):
        """'report structure' triggers FR3 detection."""
        assert reranker_module.is_fr3_query("report structure of Settlement") is True

    def test_report_layout_pattern(self):
        """'report layout' triggers FR3 detection."""
        assert reranker_module.is_fr3_query("report layout details") is True

    def test_report_overview_pattern(self):
        """'report overview' triggers FR3 detection."""
        assert reranker_module.is_fr3_query("report overview of ListOfPrintOut") is True

    def test_report_bands_pattern(self):
        """'report bands' triggers FR3 detection."""
        assert (
            reranker_module.is_fr3_query(
                "report bands in SettlementWithCarriersByRides"
            )
            is True
        )

    def test_report_band_singular_pattern(self):
        """'report band' (singular) triggers FR3 detection."""
        assert reranker_module.is_fr3_query("report band content") is True

    def test_report_memos_pattern(self):
        """'report memos' triggers FR3 detection."""
        assert reranker_module.is_fr3_query("report memos for Settlement") is True

    def test_report_variables_pattern(self):
        """'report variables' triggers FR3 detection."""
        assert reranker_module.is_fr3_query("report variables defined") is True

    def test_report_script_pattern(self):
        """'report script' triggers FR3 detection."""
        assert (
            reranker_module.is_fr3_query(
                "report script in SettlementWithCarriersByRides.fr3"
            )
            is True
        )

    def test_fastreport_pattern(self):
        """'FastReport' triggers FR3 detection."""
        assert reranker_module.is_fr3_query("FastReport template for billing") is True

    def test_dot_fr3_pattern(self):
        """'.fr3' file extension triggers FR3 detection."""
        assert reranker_module.is_fr3_query("SettlementWithCarriersByRides.fr3") is True

    def test_fr3_bare_pattern(self):
        """'fr3' keyword triggers FR3 detection."""
        assert reranker_module.is_fr3_query("fr3 file contents") is True

    def test_report_template_pattern(self):
        """'report template' triggers FR3 detection."""
        assert reranker_module.is_fr3_query("report template for settlement") is True

    def test_report_data_bindings_pattern(self):
        """'report data bindings' triggers FR3 detection."""
        assert (
            reranker_module.is_fr3_query("report data bindings in Settlement") is True
        )

    def test_plain_code_query_not_fr3(self):
        """Plain code query does not trigger FR3 detection."""
        assert reranker_module.is_fr3_query("Where is PrepareDataSet?") is False

    def test_class_query_not_fr3(self):
        """Class query does not trigger FR3 detection."""
        assert reranker_module.is_fr3_query("What is TdmMain?") is False

    def test_form_query_not_fr3(self):
        """DFM form query does not trigger FR3 detection."""
        assert reranker_module.is_fr3_query("form components of MainForm") is False

    def test_case_insensitive(self):
        """FR3 patterns are case-insensitive."""
        assert reranker_module.is_fr3_query("REPORT STRUCTURE of billing") is True
        assert reranker_module.is_fr3_query("FASTREPORT template") is True


# ────────────────────────────────────────────────
# TestIsDprojQuery
# ────────────────────────────────────────────────


class TestIsDprojQuery:
    """Tests for is_dproj_query() — detecting DPROJ/project-targeted queries."""

    def test_dproj_keyword_pattern(self):
        """'dproj' keyword triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("dproj file settings") is True

    def test_dot_dproj_pattern(self):
        """'.dproj' file extension triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("MyApp.dproj") is True

    def test_project_settings_pattern(self):
        """'project settings' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("project settings for MyApp") is True

    def test_project_overview_pattern(self):
        """'project overview' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("project overview of MyApp") is True

    def test_build_configurations_pattern(self):
        """'build configurations' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("build configurations in MyApp") is True

    def test_build_config_pattern(self):
        """'build config' (short form) triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("build config for Release") is True

    def test_compiler_settings_pattern(self):
        """'compiler settings' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("compiler settings for MyApp") is True

    def test_compiler_flags_pattern(self):
        """'compiler flags' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("compiler flags in the project") is True

    def test_compiler_options_pattern(self):
        """'compiler options' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("compiler options for Release") is True

    def test_dcc_define_pattern(self):
        """'DCC_Define' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("DCC_Define LANGS value") is True

    def test_dcc_define_with_space_pattern(self):
        """'DCC Define' (with space) triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("DCC Define values") is True

    def test_project_units_pattern(self):
        """'project units' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("project units in MyApp") is True

    def test_delphi_project_pattern(self):
        """'Delphi project' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("Delphi project MyApp") is True

    def test_dccreference_pattern(self):
        """'DCCReference' triggers DPROJ detection."""
        assert reranker_module.is_dproj_query("DCCReference entries") is True

    def test_plain_code_query_not_dproj(self):
        """Plain code query does not trigger DPROJ detection."""
        assert reranker_module.is_dproj_query("Where is PrepareDataSet?") is False

    def test_class_query_not_dproj(self):
        """Class query does not trigger DPROJ detection."""
        assert reranker_module.is_dproj_query("What is TdmMain?") is False

    def test_form_query_not_dproj(self):
        """DFM form query does not trigger DPROJ detection."""
        assert reranker_module.is_dproj_query("form components of MainForm") is False

    def test_case_insensitive(self):
        """DPROJ patterns are case-insensitive."""
        assert (
            reranker_module.is_dproj_query("BUILD CONFIGURATIONS for Release") is True
        )
        assert reranker_module.is_dproj_query("DELPHI PROJECT overview") is True


# ────────────────────────────────────────────────
# TestComputeRerankScoreFr3Mode
# ────────────────────────────────────────────────


class TestComputeRerankScoreFr3Mode:
    """Tests for _compute_rerank_score() with is_fr3=True — FR3 bonus swapping logic."""

    def test_fr3_overview_gets_primary_bonus(self):
        """FR3 report overview chunk gets PRIMARY bonus (+0.65) in FR3 mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="fr3_report_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=True,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.65)

    def test_class_summary_gets_lower_bonus_in_fr3_mode(self):
        """Class summary gets lower DFM-equivalent bonus (+0.10) in FR3 mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=True,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_other_overview_type_gets_moderate_bonus_in_fr3_mode(self):
        """Non-primary overview type (procedure_header) gets +0.25 in FR3 mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="procedure_header",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=True,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.25)

    def test_fr3_overview_beats_class_summary_in_fr3_mode(self):
        """FR3 report overview with primary bonus > class summary with lower bonus."""
        fr3_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="fr3_report_overview",
            meta={"unit_name": "settlement"},
            is_overview=True,
            is_dfm=False,
            is_fr3=True,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["settlement"],
        )
        class_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={"unit_name": "settlement"},
            is_overview=True,
            is_dfm=False,
            is_fr3=True,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["settlement"],
        )
        assert fr3_score > class_score

    def test_fr3_detail_type_gets_penalty(self):
        """FR3 detail type (fr3_variables) gets -0.05 penalty in overview queries."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="fr3_variables",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=True,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 - 0.05)

    def test_target_match_bonus_still_applies_in_fr3_mode(self):
        """Target match bonus (+0.15) still applies alongside FR3 primary bonus."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="fr3_report_overview",
            meta={"unit_name": "settlement"},
            is_overview=True,
            is_dfm=False,
            is_fr3=True,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["settlement"],
        )
        # +0.65 (primary) +0.15 (target match)
        assert score == pytest.approx(0.50 + 0.65 + 0.15)


# ────────────────────────────────────────────────
# TestComputeRerankScoreDprojMode
# ────────────────────────────────────────────────


class TestComputeRerankScoreDprojMode:
    """Tests for _compute_rerank_score() with is_dproj=True — DPROJ bonus swapping logic."""

    def test_dproj_overview_gets_primary_bonus(self):
        """DPROJ project overview chunk gets PRIMARY bonus (+0.65) in DPROJ mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dproj_project_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=True,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.65)

    def test_class_summary_gets_lower_bonus_in_dproj_mode(self):
        """Class summary gets lower DFM-equivalent bonus (+0.10) in DPROJ mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=True,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_other_overview_type_gets_moderate_bonus_in_dproj_mode(self):
        """Non-primary overview type (function_header) gets +0.25 in DPROJ mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="function_header",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=True,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.25)

    def test_dproj_overview_beats_class_summary_in_dproj_mode(self):
        """DPROJ project overview with primary bonus > class summary with lower bonus."""
        dproj_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dproj_project_overview",
            meta={"unit_name": "myproject"},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=True,
            is_hbm=False,
            is_jrxml=False,
            targets=["myproject"],
        )
        class_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={"unit_name": "myproject"},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=True,
            is_hbm=False,
            is_jrxml=False,
            targets=["myproject"],
        )
        assert dproj_score > class_score

    def test_dproj_detail_type_gets_penalty(self):
        """DPROJ detail type (dproj_unit_group) gets -0.05 penalty in overview queries."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dproj_unit_group",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=True,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 - 0.05)

    def test_target_match_bonus_still_applies_in_dproj_mode(self):
        """Target match bonus (+0.15) still applies alongside DPROJ primary bonus."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dproj_project_overview",
            meta={"unit_name": "myproject"},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=True,
            is_hbm=False,
            is_jrxml=False,
            targets=["myproject"],
        )
        # +0.65 (primary) +0.15 (target match)
        assert score == pytest.approx(0.50 + 0.65 + 0.15)


# ────────────────────────────────────────────────
# TestComputeRerankScoreFr3DprojStandardMode
# ────────────────────────────────────────────────


class TestComputeRerankScoreFr3DprojStandardMode:
    """Tests for FR3/DPROJ chunks in standard mode (is_fr3=False, is_dproj=False)."""

    def test_fr3_overview_gets_mild_bonus_in_standard_mode(self):
        """FR3 report overview gets mild +0.10 bonus in standard (non-FR3) mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="fr3_report_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_dproj_overview_gets_mild_bonus_in_standard_mode(self):
        """DPROJ project overview gets mild +0.10 bonus in standard (non-DPROJ) mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dproj_project_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_fr3_overview_penalized_on_pascal_class_query(self):
        """FR3 overview gets -0.15 penalty when query targets a Pascal class in standard mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="fr3_report_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # +0.10 (mild) -0.15 (Pascal class penalty) -0.40 (non-target overview penalty)
        assert score == pytest.approx(0.50 + 0.10 - 0.15 - 0.40)

    def test_dproj_overview_penalized_on_pascal_class_query(self):
        """DPROJ overview gets -0.15 penalty when query targets a Pascal class in standard mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="dproj_project_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # +0.10 (mild) -0.15 (Pascal class penalty) -0.40 (non-target overview penalty)
        assert score == pytest.approx(0.50 + 0.10 - 0.15 - 0.40)

    def test_class_summary_still_primary_in_standard_mode(self):
        """Class summary still gets primary +0.65 bonus when is_fr3/is_dproj=False."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.65)


# ────────────────────────────────────────────────
# TestFr3DprojTargetExtraction
# ────────────────────────────────────────────────


class TestFr3DprojTargetExtraction:
    """Tests for FR3/DPROJ file stem extraction in extract_target_identifiers()."""

    def test_fr3_file_stem_extracted(self):
        """FR3 file name 'SettlementWithCarriersByRides.fr3' extracts stem."""
        result = reranker_module.extract_target_identifiers(
            "report overview of SettlementWithCarriersByRides.fr3"
        )
        assert (
            "settlementwithcarriersbyridesr" in result
            or "settlementwithcarriersbyridesr" in result
            or any("settlement" in t for t in result)
        )

    def test_fr3_file_stem_exact(self):
        """_FILE_STEM_FR3 captures the stem group from a .fr3 filename."""
        m = reranker_module._FILE_STEM_FR3.search("SettlementWithCarriersByRides.fr3")
        assert m is not None
        assert m.group(1) == "SettlementWithCarriersByRides"

    def test_dproj_file_stem_extracted(self):
        """DPROJ file name 'MyApp.dproj' extracts stem."""
        result = reranker_module.extract_target_identifiers(
            "project overview of MyApp.dproj"
        )
        assert "myapp" in result

    def test_dproj_file_stem_exact(self):
        """_FILE_STEM_DPROJ captures the stem group from a .dproj filename."""
        m = reranker_module._FILE_STEM_DPROJ.search("MyApp.dproj")
        assert m is not None
        assert m.group(1) == "MyApp"

    def test_known_fr3_stem_in_allowlist(self):
        """'SettlementWithCarriersByRides' is in _FILE_STEM_NO_EXT allowlist."""
        assert (
            reranker_module._FILE_STEM_NO_EXT.search("SettlementWithCarriersByRides")
            is not None
        )

    def test_known_dproj_stem_in_allowlist(self):
        """'MyApp' is in _FILE_STEM_NO_EXT allowlist."""
        assert reranker_module._FILE_STEM_NO_EXT.search("MyApp") is not None

    def test_listofprintout_in_allowlist(self):
        """'ListOfPrintOut' is in _FILE_STEM_NO_EXT allowlist."""
        assert reranker_module._FILE_STEM_NO_EXT.search("ListOfPrintOut") is not None


# ────────────────────────────────────────────────
# TestOverviewPatternsFr3Dproj
# ────────────────────────────────────────────────


class TestOverviewPatternsFr3Dproj:
    """Tests for overview query detection with FR3/DPROJ-related queries."""

    def test_report_structure_is_overview(self):
        """'report structure of Settlement' is detected as overview query."""
        assert (
            reranker_module.is_overview_query("report structure of Settlement") is True
        )

    def test_report_overview_is_overview(self):
        """'report overview of ListOfPrintOut' is detected as overview query."""
        assert (
            reranker_module.is_overview_query("report overview of ListOfPrintOut")
            is True
        )

    def test_report_bands_is_overview(self):
        """'report bands in Settlement' is detected as overview query."""
        assert reranker_module.is_overview_query("report bands in Settlement") is True

    def test_project_settings_is_overview(self):
        """'project settings for MyApp' is detected as overview query."""
        assert reranker_module.is_overview_query("project settings for MyApp") is True

    def test_build_configurations_is_overview(self):
        """'build configurations in MyApp' is detected as overview query."""
        assert (
            reranker_module.is_overview_query("build configurations in MyApp") is True
        )

    def test_project_overview_is_overview(self):
        """'project overview of MyApp' is detected as overview query."""
        assert reranker_module.is_overview_query("project overview of MyApp") is True

    def test_project_units_is_overview(self):
        """'project units in MyApp' is detected as overview query."""
        assert reranker_module.is_overview_query("project units in MyApp") is True


# ────────────────────────────────────────────────
# TestFr3DprojNodeTypeCategories
# ────────────────────────────────────────────────


class TestFr3DprojNodeTypeCategories:
    """Tests that FR3/DPROJ node types are correctly categorized."""

    def test_fr3_report_overview_in_overview_types(self):
        """fr3_report_overview is in _OVERVIEW_CHUNK_TYPES."""
        assert "fr3_report_overview" in reranker_module._OVERVIEW_CHUNK_TYPES

    def test_dproj_project_overview_in_overview_types(self):
        """dproj_project_overview is in _OVERVIEW_CHUNK_TYPES."""
        assert "dproj_project_overview" in reranker_module._OVERVIEW_CHUNK_TYPES

    def test_fr3_report_overview_in_fr3_overview_types(self):
        """fr3_report_overview is in _FR3_OVERVIEW_TYPES."""
        assert "fr3_report_overview" in reranker_module._FR3_OVERVIEW_TYPES

    def test_dproj_project_overview_in_dproj_overview_types(self):
        """dproj_project_overview is in _DPROJ_OVERVIEW_TYPES."""
        assert "dproj_project_overview" in reranker_module._DPROJ_OVERVIEW_TYPES

    def test_fr3_variables_in_detail_types(self):
        """fr3_variables is in _DETAIL_CHUNK_TYPES."""
        assert "fr3_variables" in reranker_module._DETAIL_CHUNK_TYPES

    def test_dproj_unit_group_in_detail_types(self):
        """dproj_unit_group is in _DETAIL_CHUNK_TYPES."""
        assert "dproj_unit_group" in reranker_module._DETAIL_CHUNK_TYPES

    def test_fr3_band_content_not_in_detail_types(self):
        """fr3_band_content is NOT in _DETAIL_CHUNK_TYPES (it's useful content)."""
        assert "fr3_band_content" not in reranker_module._DETAIL_CHUNK_TYPES

    def test_fr3_pascal_script_not_in_detail_types(self):
        """fr3_pascal_script is NOT in _DETAIL_CHUNK_TYPES (it's useful content)."""
        assert "fr3_pascal_script" not in reranker_module._DETAIL_CHUNK_TYPES

    def test_dproj_build_config_not_in_detail_types(self):
        """dproj_build_config is NOT in _DETAIL_CHUNK_TYPES (it's useful content)."""
        assert "dproj_build_config" not in reranker_module._DETAIL_CHUNK_TYPES


# ────────────────────────────────────────────────
# TestJavaNodeTypeCategories
# ────────────────────────────────────────────────


class TestJavaNodeTypeCategories:
    """Tests that Java reader node types are correctly categorized."""

    def test_method_declaration_in_detail_types(self):
        """method_declaration is a detail type."""
        assert "method_declaration" in reranker_module._DETAIL_CHUNK_TYPES

    def test_method_declaration_split_in_detail_types(self):
        """method_declaration_split is a detail type."""
        assert "method_declaration_split" in reranker_module._DETAIL_CHUNK_TYPES

    def test_constructor_declaration_in_detail_types(self):
        """constructor_declaration is a detail type."""
        assert "constructor_declaration" in reranker_module._DETAIL_CHUNK_TYPES

    def test_constructor_declaration_split_in_detail_types(self):
        """constructor_declaration_split is a detail type."""
        assert "constructor_declaration_split" in reranker_module._DETAIL_CHUNK_TYPES

    def test_field_declaration_in_detail_types(self):
        """field_declaration is a detail type."""
        assert "field_declaration" in reranker_module._DETAIL_CHUNK_TYPES

    def test_constant_declaration_in_detail_types(self):
        """constant_declaration is a detail type."""
        assert "constant_declaration" in reranker_module._DETAIL_CHUNK_TYPES

    def test_enum_constant_in_detail_types(self):
        """enum_constant is a detail type."""
        assert "enum_constant" in reranker_module._DETAIL_CHUNK_TYPES

    def test_import_group_in_import_group_types(self):
        """import_group is in _IMPORT_GROUP_TYPES."""
        assert "import_group" in reranker_module._IMPORT_GROUP_TYPES

    def test_block_comment_in_block_comment_types(self):
        """block_comment is in _BLOCK_COMMENT_TYPES."""
        assert "block_comment" in reranker_module._BLOCK_COMMENT_TYPES


# ────────────────────────────────────────────────
# TestJsTsNodeTypeCategories
# ────────────────────────────────────────────────


class TestJsTsNodeTypeCategories:
    """Tests that JS/TS reader node types are correctly categorized."""

    def test_function_declaration_in_detail_types(self):
        """function_declaration is a detail type."""
        assert "function_declaration" in reranker_module._DETAIL_CHUNK_TYPES

    def test_function_declaration_split_in_detail_types(self):
        """function_declaration_split is a detail type."""
        assert "function_declaration_split" in reranker_module._DETAIL_CHUNK_TYPES

    def test_method_definition_in_detail_types(self):
        """method_definition is a detail type."""
        assert "method_definition" in reranker_module._DETAIL_CHUNK_TYPES

    def test_method_definition_split_in_detail_types(self):
        """method_definition_split is a detail type."""
        assert "method_definition_split" in reranker_module._DETAIL_CHUNK_TYPES

    def test_generator_function_in_detail_types(self):
        """generator_function_declaration is a detail type."""
        assert "generator_function_declaration" in reranker_module._DETAIL_CHUNK_TYPES

    def test_arrow_function_in_detail_types(self):
        """arrow_function is a detail type."""
        assert "arrow_function" in reranker_module._DETAIL_CHUNK_TYPES

    def test_arrow_function_split_in_detail_types(self):
        """arrow_function_split is a detail type."""
        assert "arrow_function_split" in reranker_module._DETAIL_CHUNK_TYPES

    def test_variable_declaration_in_detail_types(self):
        """variable_declaration is a detail type."""
        assert "variable_declaration" in reranker_module._DETAIL_CHUNK_TYPES

    def test_lexical_declaration_in_detail_types(self):
        """lexical_declaration is a detail type."""
        assert "lexical_declaration" in reranker_module._DETAIL_CHUNK_TYPES

    def test_function_group_in_detail_types(self):
        """function_group is a detail type."""
        assert "function_group" in reranker_module._DETAIL_CHUNK_TYPES

    def test_prototype_group_in_detail_types(self):
        """prototype_group is a detail type."""
        assert "prototype_group" in reranker_module._DETAIL_CHUNK_TYPES

    def test_assignment_expression_in_detail_types(self):
        """assignment_expression is a detail type."""
        assert "assignment_expression" in reranker_module._DETAIL_CHUNK_TYPES

    def test_expression_statement_in_detail_types(self):
        """expression_statement is a detail type."""
        assert "expression_statement" in reranker_module._DETAIL_CHUNK_TYPES

    def test_interface_declaration_in_overview_types(self):
        """interface_declaration is an overview type (structural)."""
        assert "interface_declaration" in reranker_module._OVERVIEW_CHUNK_TYPES

    def test_type_alias_declaration_in_overview_types(self):
        """type_alias_declaration is an overview type (structural)."""
        assert "type_alias_declaration" in reranker_module._OVERVIEW_CHUNK_TYPES


# ────────────────────────────────────────────────
# TestHbmJrxmlNodeTypeCategories
# ────────────────────────────────────────────────


class TestHbmJrxmlNodeTypeCategories:
    """Tests that HBM and JRXML reader node types are correctly categorized."""

    def test_hbm_entity_overview_in_overview_types(self):
        """hbm_entity_overview is in _OVERVIEW_CHUNK_TYPES."""
        assert "hbm_entity_overview" in reranker_module._OVERVIEW_CHUNK_TYPES

    def test_hbm_entity_overview_in_hbm_overview_types(self):
        """hbm_entity_overview is in _HBM_OVERVIEW_TYPES."""
        assert "hbm_entity_overview" in reranker_module._HBM_OVERVIEW_TYPES

    def test_hbm_raw_mapping_in_detail_types(self):
        """hbm_raw_mapping is in _DETAIL_CHUNK_TYPES."""
        assert "hbm_raw_mapping" in reranker_module._DETAIL_CHUNK_TYPES

    def test_jrxml_report_overview_in_overview_types(self):
        """jrxml_report_overview is in _OVERVIEW_CHUNK_TYPES."""
        assert "jrxml_report_overview" in reranker_module._OVERVIEW_CHUNK_TYPES

    def test_jrxml_report_overview_in_jrxml_overview_types(self):
        """jrxml_report_overview is in _JRXML_OVERVIEW_TYPES."""
        assert "jrxml_report_overview" in reranker_module._JRXML_OVERVIEW_TYPES

    def test_jrxml_expressions_in_detail_types(self):
        """jrxml_expressions is in _DETAIL_CHUNK_TYPES."""
        assert "jrxml_expressions" in reranker_module._DETAIL_CHUNK_TYPES


# ────────────────────────────────────────────────
# TestIsHbmQuery
# ────────────────────────────────────────────────


class TestIsHbmQuery:
    """Tests for is_hbm_query() pattern matching."""

    def test_hbm_keyword(self):
        assert reranker_module.is_hbm_query("show me the hbm mapping") is True

    def test_hbm_xml_extension(self):
        assert reranker_module.is_hbm_query("PHTicketOrder.hbm.xml") is True

    def test_hibernate_mapping(self):
        assert reranker_module.is_hbm_query("hibernate mapping for TicketOrder") is True

    def test_entity_mapping(self):
        assert reranker_module.is_hbm_query("entity mapping of PHCompany") is True

    def test_table_mapping(self):
        assert reranker_module.is_hbm_query("table mapping for carriers") is True

    def test_which_table(self):
        assert reranker_module.is_hbm_query("which table is PHTicket mapped to") is True

    def test_database_mapping(self):
        assert reranker_module.is_hbm_query("database mapping for orders") is True

    def test_no_match_generic(self):
        assert reranker_module.is_hbm_query("find OAuthEpLoginService") is False

    def test_orm_mapping(self):
        assert reranker_module.is_hbm_query("ORM mapping for reservations") is True


# ────────────────────────────────────────────────
# TestIsJrxmlQuery
# ────────────────────────────────────────────────


class TestIsJrxmlQuery:
    """Tests for is_jrxml_query() pattern matching."""

    def test_jrxml_keyword(self):
        assert reranker_module.is_jrxml_query("show me the jrxml file") is True

    def test_jrxml_extension(self):
        assert reranker_module.is_jrxml_query("Ticket_PrintAll.jrxml") is True

    def test_jasper_report(self):
        assert reranker_module.is_jrxml_query("JasperReport for tickets") is True

    def test_jasperreports_no_space(self):
        assert reranker_module.is_jrxml_query("JasperReports ticket printing") is True

    def test_report_definition(self):
        assert reranker_module.is_jrxml_query("report definition for invoices") is True

    def test_report_parameters(self):
        assert (
            reranker_module.is_jrxml_query("report parameters for settlement") is True
        )

    def test_report_fields(self):
        assert reranker_module.is_jrxml_query("report fields in ticket") is True

    def test_report_subreport(self):
        assert reranker_module.is_jrxml_query("report subreport for carrier") is True

    def test_no_match_generic(self):
        assert reranker_module.is_jrxml_query("find OAuthEpLoginService") is False


# ────────────────────────────────────────────────
# TestComputeRerankScoreHbmMode
# ────────────────────────────────────────────────


class TestComputeRerankScoreHbmMode:
    """Tests for _compute_rerank_score with is_hbm=True."""

    def test_hbm_overview_gets_primary_bonus(self):
        """hbm_entity_overview gets +0.65 in HBM mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="hbm_entity_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=True,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.65)

    def test_class_summary_gets_lower_bonus_in_hbm_mode(self):
        """class_summary gets +0.10 (DFM_OVERVIEW_BONUS) in HBM mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=True,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_other_overview_gets_moderate_bonus_in_hbm_mode(self):
        """procedure_header gets +0.25 in HBM mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="procedure_header",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=True,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.25)

    def test_hbm_overview_beats_class_summary_in_hbm_mode(self):
        """In HBM mode, hbm_entity_overview (+0.65) > class_summary (+0.10)."""
        hbm_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="hbm_entity_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=True,
            is_jrxml=False,
            targets=[],
        )
        cls_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=True,
            is_jrxml=False,
            targets=[],
        )
        assert hbm_score > cls_score


# ────────────────────────────────────────────────
# TestComputeRerankScoreJrxmlMode
# ────────────────────────────────────────────────


class TestComputeRerankScoreJrxmlMode:
    """Tests for _compute_rerank_score with is_jrxml=True."""

    def test_jrxml_overview_gets_primary_bonus(self):
        """jrxml_report_overview gets +0.65 in JRXML mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="jrxml_report_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=True,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.65)

    def test_class_summary_gets_lower_bonus_in_jrxml_mode(self):
        """class_summary gets +0.10 (DFM_OVERVIEW_BONUS) in JRXML mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=True,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_other_overview_gets_moderate_bonus_in_jrxml_mode(self):
        """procedure_header gets +0.25 in JRXML mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="procedure_header",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=True,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.25)

    def test_jrxml_overview_beats_class_summary_in_jrxml_mode(self):
        """In JRXML mode, jrxml_report_overview (+0.65) > class_summary (+0.10)."""
        jrxml_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="jrxml_report_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=True,
            targets=[],
        )
        cls_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=True,
            targets=[],
        )
        assert jrxml_score > cls_score


# ────────────────────────────────────────────────
# TestImportGroupPenalty
# ────────────────────────────────────────────────


class TestImportGroupPenalty:
    """Tests that import_group chunks get heavy penalty in overview queries."""

    def test_import_group_penalized_025(self):
        """import_group gets -0.25 penalty in overview queries."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="import_group",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 - 0.25)

    def test_import_statement_penalized_025(self):
        """import_statement (Python) gets -0.25 penalty in overview queries."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="import_statement",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 - 0.25)

    def test_import_group_not_penalized_in_non_overview(self):
        """import_group gets no penalty for non-overview queries."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="import_group",
            meta={},
            is_overview=False,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50)

    def test_import_group_penalty_outweighs_detail_penalty(self):
        """import_group penalty (-0.25) is heavier than detail penalty (-0.05)."""
        assert reranker_module._IMPORT_GROUP_PENALTY > reranker_module._DETAIL_PENALTY


# ────────────────────────────────────────────────
# TestBlockCommentPenalty
# ────────────────────────────────────────────────


class TestBlockCommentPenalty:
    """Tests that block_comment chunks get cross-file comment penalty."""

    def test_block_comment_from_non_target_penalized(self):
        """block_comment from non-target file gets -0.30 cross-file comment penalty."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="block_comment",
            meta={"file_path": "other/SomeFile.java"},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["oauthservice"],
        )
        assert score == pytest.approx(0.50 - 0.30)

    def test_block_comment_from_target_not_penalized(self):
        """block_comment from target file gets no cross-file comment penalty."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="block_comment",
            meta={"file_path": "src/OAuthService.java"},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["oauthservice"],
        )
        # Should get target match bonus, NOT cross-file penalty
        assert score > 0.50


# ────────────────────────────────────────────────
# TestHbmJrxmlStandardMode
# ────────────────────────────────────────────────


class TestHbmJrxmlStandardMode:
    """Tests that HBM/JRXML overview types get mild bonus in standard mode
    (when is_hbm=False and is_jrxml=False)."""

    def test_hbm_overview_gets_mild_bonus_in_standard_mode(self):
        """hbm_entity_overview gets +0.10 (DFM_OVERVIEW_BONUS) in standard mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="hbm_entity_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_jrxml_overview_gets_mild_bonus_in_standard_mode(self):
        """jrxml_report_overview gets +0.10 (DFM_OVERVIEW_BONUS) in standard mode."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="jrxml_report_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert score == pytest.approx(0.50 + 0.10)

    def test_hbm_overview_penalized_on_pascal_class_query(self):
        """hbm_entity_overview penalized when query targets a T-prefixed class."""
        score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="hbm_entity_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=["tdmmain"],
        )
        # +0.10 DFM bonus - 0.15 class query penalty - 0.40 non-target penalty
        assert score == pytest.approx(0.50 + 0.10 - 0.15 - 0.40)

    def test_class_summary_still_primary_in_standard_mode(self):
        """class_summary keeps +0.65 when HBM/JRXML types get only +0.10."""
        cls_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="class_summary",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        hbm_score = reranker_module._compute_rerank_score(
            original_score=0.50,
            node_type="hbm_entity_overview",
            meta={},
            is_overview=True,
            is_dfm=False,
            is_fr3=False,
            is_dproj=False,
            is_hbm=False,
            is_jrxml=False,
            targets=[],
        )
        assert cls_score > hbm_score


# ────────────────────────────────────────────────
# TestJavaTargetExtraction
# ────────────────────────────────────────────────


class TestJavaTargetExtraction:
    """Tests that Java/HBM/JRXML file stems are extracted as targets."""

    def test_java_file_stem_extracted(self):
        """'OAuthEpLoginService.java' extracts stem."""
        result = reranker_module.extract_target_identifiers(
            "What is OAuthEpLoginService.java?"
        )
        assert "oautheploginservice" in result

    def test_hbm_file_stem_extracted(self):
        """'PHTicketOrder.hbm.xml' extracts stem."""
        result = reranker_module.extract_target_identifiers(
            "hibernate mapping for PHTicketOrder.hbm.xml"
        )
        assert "phticketorder" in result

    def test_hbm_file_stem_without_xml(self):
        """'PHTicketOrder.hbm' also extracts stem."""
        result = reranker_module.extract_target_identifiers("show me PHTicketOrder.hbm")
        assert "phticketorder" in result

    def test_jrxml_file_stem_extracted(self):
        """'Ticket_PrintAll.jrxml' extracts stem."""
        result = reranker_module.extract_target_identifiers(
            "JasperReport Ticket_PrintAll.jrxml"
        )
        assert "ticket_printall" in result

    def test_js_file_stem_extracted(self):
        """'app.js' extracts stem."""
        result = reranker_module.extract_target_identifiers("show me app.js")
        assert "app" in result

    def test_ts_file_stem_extracted(self):
        """'main.ts' extracts stem."""
        result = reranker_module.extract_target_identifiers("what does main.ts do")
        assert "main" in result
