"""Tests for the rerank profile mechanism (generic core + per-reader profiles)."""

from types import SimpleNamespace

import pytest

import shared.reranker as rr
from shared.readers import READER_REGISTRY, all_rerank_profiles, get_reader
from shared.readers.text_reader import TextFileReader
from shared.rerank_profile import QueryDomain, RerankProfile, compile_all


def _cfg(*extensions, **extra):
    return SimpleNamespace(
        SOURCE_DIRS=[{"path": "/src", "extensions": list(extensions)}], **extra
    )


def _profiles(*extensions, **extra):
    return rr.rerank_profiles_for_config(_cfg(*extensions, **extra))


# ── registration ─────────────────────────────────────────────────


def test_every_code_reader_has_a_profile():
    for ext, reader in READER_REGISTRY.items():
        if isinstance(reader, TextFileReader):
            assert reader.rerank_profile is None, ext
        else:
            assert isinstance(reader.rerank_profile, RerankProfile), ext


def test_profile_names_unique():
    names = [p.name for p in all_rerank_profiles()]
    assert len(names) == len(set(names))


def test_none_means_all_profiles():
    assert set(rr.get_profile_set(None).names) == {p.name for p in all_rerank_profiles()}


# ── selection from config ────────────────────────────────────────


def test_selection_follows_extensions():
    names = set(_profiles(".java", ".hbm.xml", ".jrxml", ".sql", ".md").names)
    assert names == {"java", "hibernate_mapping", "jasperreports", "sql"}


def test_selection_is_case_insensitive_and_dedups():
    names = _profiles(".PAS", ".pas", ".dpr", ".dfm").names
    assert names == ("delphi", "delphi_forms")


def test_extension_without_dot_accepted():
    assert _profiles("go").names == ("go",)


def test_text_only_project_falls_back_to_all():
    assert set(_profiles(".md", ".txt").names) == set(rr.get_profile_set(None).names)


def test_override_list():
    ps = _profiles(".java", RERANK_PROFILES=["delphi", "sql"])
    assert ps.names == ("delphi", "sql")


def test_override_all():
    ps = _profiles(".java", RERANK_PROFILES="all")
    assert set(ps.names) == set(rr.get_profile_set(None).names)


def test_override_unknown_names_ignored():
    ps = _profiles(".java", RERANK_PROFILES=["java", "nope"])
    assert ps.names == ("java",)


# ── behaviour is scoped to active profiles ───────────────────────


def test_pascal_class_targets_only_with_delphi():
    q = "Tell me about the Orders"
    assert "tell" in rr.extract_target_identifiers(q, _profiles(".pas"))
    assert "tell" not in rr.extract_target_identifiers(q, _profiles(".java"))


def test_file_stem_patterns_only_for_active_languages():
    q = "What is OrderService.cs"
    assert "orderservice" in rr.extract_target_identifiers(q, _profiles(".cs"))
    # The capitalised-word rule still sees the name, but not as a stem.
    assert "orderservice.cs" not in rr.extract_target_identifiers(q, _profiles(".java"))


def test_generic_targets_always_active():
    ps = _profiles(".go")
    assert "base42" in rr.extract_target_identifiers("What classes are in base42?", ps)
    assert "router" in rr.extract_target_identifiers("Describe pkg/Router", ps)


def test_domain_only_when_profile_active():
    q = "Describe which table OrderEntity is mapped to"
    assert rr.detect_query_domain(q, _profiles(".java", ".hbm.xml")) == "hbm"
    assert rr.detect_query_domain(q, _profiles(".pas")) is None


def test_domain_priority_order():
    q = "report structure of Sales.fr3 build configuration"
    assert rr.detect_query_domain(q, _profiles(".fr3", ".dproj")) == "fr3"
    assert rr.detect_query_domain(q, _profiles(".dproj")) == "dproj"


def test_profile_overview_patterns_scoped():
    q = "report structure for invoices"
    assert rr.is_overview_query(q, _profiles(".fr3"))
    assert rr.is_overview_query(q, _profiles(".jrxml"))
    assert not rr.is_overview_query(q, _profiles(".go"))


def test_form_domain_merged_from_delphi_and_qt():
    ps = _profiles(".dfm", ".ui")
    form = ps.domains["form"]
    assert form.primary_types == {"dfm_form_header", "ui_form_header"}
    assert rr.is_domain_query("form", "the dlg.ui layout", ps)
    assert rr.is_domain_query("form", "the main DFM", ps)
    assert not rr.is_domain_query("form", "the main DFM", _profiles(".ui"))


def test_artifact_penalty_needs_class_predicate():
    meta = {"file_path": "src/TOrderForm.dfm"}
    targets = ["torderform"]
    with_delphi = rr._compute_rerank_score(
        0.5, "dfm_form_header", meta, True, None, targets, _profiles(".pas", ".dfm")
    )
    forms_only = rr._compute_rerank_score(
        0.5, "dfm_form_header", meta, True, None, targets, _profiles(".dfm")
    )
    assert forms_only - with_delphi == pytest.approx(rr._ARTIFACT_ON_CLASS_QUERY_PENALTY)


def test_inactive_types_get_no_adjustment():
    # cpp detail type in a Go-only index: neither detail penalty nor overview bonus
    score = rr._compute_rerank_score(0.5, "cpp_function", {}, True, None, [], _profiles(".go"))
    assert score == pytest.approx(0.5)


def test_rerank_results_accepts_profiles():
    class _N:
        def __init__(self, t, s):
            self.node = SimpleNamespace(metadata={"node_type": t, "file_path": "server.go"})
            self.score = s

    nodes = [_N("method_declaration", 0.9), _N("class_summary", 0.5)]
    out = rr.rerank_results(nodes, "What is Server?", desired_top_k=1, profiles=_profiles(".go"))
    assert out[0].node.metadata["node_type"] == "class_summary"


# ── custom profiles ──────────────────────────────────────────────


def test_custom_profile_domain_and_types():
    custom = RerankProfile(
        name="custom",
        target_patterns=compile_all([r"\b([A-Za-z]+)\.cfgx\b"]),
        artifact_overview_types=frozenset({"cfgx_overview"}),
        detail_types=frozenset({"cfgx_entry"}),
        domains=(
            QueryDomain(
                name="cfgx",
                priority=5,
                patterns=compile_all([r"\bsettings\s+file\b"]),
                primary_types=frozenset({"cfgx_overview"}),
            ),
        ),
    )
    ps = rr.ProfileSet([custom])
    q = "Describe the settings file app.cfgx"
    assert "app" in rr.extract_target_identifiers(q, ps)
    assert rr.detect_query_domain(q, ps) == "cfgx"
    s = rr._compute_rerank_score(0.5, "cfgx_overview", {"file_path": "app.cfgx"}, True, "cfgx", ["app"], ps)
    assert s == pytest.approx(0.5 + rr._PRIMARY_OVERVIEW_BONUS + rr._TARGET_MATCH_BONUS)
    s = rr._compute_rerank_score(0.5, "cfgx_entry", {"file_path": "app.cfgx"}, True, None, ["app"], ps)
    assert s == pytest.approx(0.5 + rr._TARGET_MATCH_BONUS - rr._DETAIL_PENALTY)


def test_get_reader_profile_for_compound_extension():
    assert get_reader(".hbm.xml").rerank_profile.name == "hibernate_mapping"
