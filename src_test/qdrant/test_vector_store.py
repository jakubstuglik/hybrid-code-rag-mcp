"""
Tests for qdrant/vector_store.py — BM25 CPU enforcement in get_sparse_encoder().

Tests cover:
    - BM25 model always loads on CPU regardless of device parameter
    - BM25 never triggers _ensure_torch_cuda_libs()
    - BM25 SparseTextEmbedding constructor called WITHOUT providers arg
    - Non-BM25 models respect device="cuda" (CUDAExecutionProvider)
    - Non-BM25 models respect device="cpu"
    - mode="dense" returns None immediately
    - Cache hit: second call returns the same function object
"""

import types
from unittest.mock import MagicMock, patch

import pytest

import qdrant.vector_store as vs_mod


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_cfg(**kwargs) -> types.ModuleType:
    """Create a fake config module with the given attributes."""
    cfg = types.ModuleType("fake_config")
    # Default to hybrid mode so the encoder is actually created
    kwargs.setdefault("INDEXING_MODE", "hybrid")
    kwargs.setdefault("INDEX_EMBED_DEVICE", "cpu")
    kwargs.setdefault("SPARSE_MODEL_NAME", "prithivida/Splade_PP_en_v1")
    for k, v in kwargs.items():
        setattr(cfg, k, v)
    return cfg


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the sparse encoder cache before each test."""
    vs_mod._sparse_encoder_cache.clear()
    yield
    vs_mod._sparse_encoder_cache.clear()


# ────────────────────────────────────────────────
# mode="dense" returns None
# ────────────────────────────────────────────────


class TestDenseMode:
    """When INDEXING_MODE is 'dense', get_sparse_encoder returns None."""

    def test_dense_mode_returns_none(self):
        cfg = _make_cfg(INDEXING_MODE="dense")
        result = vs_mod.get_sparse_encoder(cfg=cfg)
        assert result is None

    def test_dense_mode_does_not_import_fastembed(self):
        """Dense mode returns before reaching the SparseTextEmbedding import."""
        cfg = _make_cfg(INDEXING_MODE="dense")
        with patch(
            "fastembed.sparse.sparse_text_embedding.SparseTextEmbedding"
        ) as mock_cls:
            result = vs_mod.get_sparse_encoder(cfg=cfg)
            assert result is None
            mock_cls.assert_not_called()


# ────────────────────────────────────────────────
# BM25 CPU enforcement
# ────────────────────────────────────────────────


class TestBM25CpuEnforcement:
    """BM25 model always loads on CPU, regardless of device parameter."""

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_bm25_loads_on_cpu_when_device_cuda(self, mock_log, mock_cls):
        """BM25 with device='cuda' still loads on CPU."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="Qdrant/bm25")
        result = vs_mod.get_sparse_encoder(cfg=cfg, device="cuda")
        assert result is not None
        # SparseTextEmbedding called with just model_name, no providers
        mock_cls.assert_called_once_with("Qdrant/bm25")

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_bm25_loads_on_cpu_when_device_cpu(self, mock_log, mock_cls):
        """BM25 with device='cpu' loads on CPU."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="Qdrant/bm25")
        result = vs_mod.get_sparse_encoder(cfg=cfg, device="cpu")
        assert result is not None
        mock_cls.assert_called_once_with("Qdrant/bm25")

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "_ensure_torch_cuda_libs")
    @patch.object(vs_mod, "log")
    def test_bm25_never_calls_ensure_torch_cuda_libs(
        self, mock_log, mock_ensure, mock_cls
    ):
        """BM25 should never trigger _ensure_torch_cuda_libs even with device='cuda'."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="Qdrant/bm25")
        vs_mod.get_sparse_encoder(cfg=cfg, device="cuda")
        mock_ensure.assert_not_called()

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_bm25_no_providers_kwarg(self, mock_log, mock_cls):
        """BM25 SparseTextEmbedding constructor is called WITHOUT providers."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="Qdrant/bm25")
        vs_mod.get_sparse_encoder(cfg=cfg, device="cuda")
        # Verify the call — should be positional model_name only
        call_args = mock_cls.call_args
        assert call_args.args == ("Qdrant/bm25",)
        assert "providers" not in call_args.kwargs

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_bm25_case_insensitive(self, mock_log, mock_cls):
        """BM25 detection is case-insensitive (model_name.lower())."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="QDRANT/BM25")
        vs_mod.get_sparse_encoder(cfg=cfg, device="cuda")
        # Should still be treated as BM25 — no providers
        call_args = mock_cls.call_args
        assert "providers" not in call_args.kwargs

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_bm25_log_message(self, mock_log, mock_cls):
        """BM25 logs the correct CPU message."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="Qdrant/bm25")
        vs_mod.get_sparse_encoder(cfg=cfg, device="cuda")
        log_msgs = [c[0][0] for c in mock_log.call_args_list]
        assert any("BM25" in msg and "CPU" in msg for msg in log_msgs)


# ────────────────────────────────────────────────
# Non-BM25 models respect device parameter
# ────────────────────────────────────────────────


class TestNonBM25Device:
    """Non-BM25 sparse models respect the device parameter."""

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "_ensure_torch_cuda_libs")
    @patch.object(vs_mod, "log")
    def test_non_bm25_cuda_uses_cuda_provider(self, mock_log, mock_ensure, mock_cls):
        """Non-BM25 model with device='cuda' uses CUDAExecutionProvider."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="prithivida/Splade_PP_en_v1")
        vs_mod.get_sparse_encoder(cfg=cfg, device="cuda")
        mock_ensure.assert_called_once()
        mock_cls.assert_called_once_with(
            "prithivida/Splade_PP_en_v1",
            providers=["CUDAExecutionProvider"],
        )

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "_ensure_torch_cuda_libs")
    @patch.object(vs_mod, "log")
    def test_non_bm25_cpu_no_cuda_provider(self, mock_log, mock_ensure, mock_cls):
        """Non-BM25 model with device='cpu' does not use CUDAExecutionProvider."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="prithivida/Splade_PP_en_v1")
        vs_mod.get_sparse_encoder(cfg=cfg, device="cpu")
        mock_ensure.assert_not_called()
        mock_cls.assert_called_once_with("prithivida/Splade_PP_en_v1")

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "_ensure_torch_cuda_libs")
    @patch.object(vs_mod, "log_warn")
    @patch.object(vs_mod, "log")
    def test_non_bm25_cuda_fallback_on_error(
        self, mock_log, mock_log_warn, mock_ensure, mock_cls
    ):
        """Non-BM25 CUDA model falls back to CPU when CUDAExecutionProvider fails."""
        # First call (with providers) raises, second call (without) succeeds
        mock_cls.side_effect = [
            RuntimeError("CUDAExecutionProvider not available"),
            MagicMock(),
        ]
        cfg = _make_cfg(SPARSE_MODEL_NAME="prithivida/Splade_PP_en_v1")
        result = vs_mod.get_sparse_encoder(cfg=cfg, device="cuda")
        assert result is not None
        assert mock_cls.call_count == 2
        # Second call is the fallback — no providers
        fallback_call = mock_cls.call_args_list[1]
        assert fallback_call.args == ("prithivida/Splade_PP_en_v1",)
        assert "providers" not in fallback_call.kwargs
        mock_log_warn.assert_called_once()


# ────────────────────────────────────────────────
# Cache behavior
# ────────────────────────────────────────────────


class TestCacheBehavior:
    """Sparse encoder cache returns the same function on repeated calls."""

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_cache_hit_returns_same_function(self, mock_log, mock_cls):
        """Second call with same config returns the cached function."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="Qdrant/bm25")
        first = vs_mod.get_sparse_encoder(cfg=cfg, device="cpu")
        second = vs_mod.get_sparse_encoder(cfg=cfg, device="cpu")
        assert first is second
        # SparseTextEmbedding constructor called only once
        mock_cls.assert_called_once()

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_cache_key_includes_model_and_device(self, mock_log, mock_cls):
        """Different model names produce different cache entries."""
        mock_cls.return_value = MagicMock()
        cfg_bm25 = _make_cfg(SPARSE_MODEL_NAME="Qdrant/bm25")
        cfg_splade = _make_cfg(SPARSE_MODEL_NAME="prithivida/Splade_PP_en_v1")
        fn_bm25 = vs_mod.get_sparse_encoder(cfg=cfg_bm25, device="cpu")
        fn_splade = vs_mod.get_sparse_encoder(cfg=cfg_splade, device="cpu")
        assert fn_bm25 is not fn_splade
        assert mock_cls.call_count == 2

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_bm25_cache_key_uses_cpu_even_when_device_cuda(self, mock_log, mock_cls):
        """BM25 with device='cuda' caches under ('qdrant/bm25', 'cpu')."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(SPARSE_MODEL_NAME="Qdrant/bm25")
        vs_mod.get_sparse_encoder(cfg=cfg, device="cuda")
        # The cache key should use effective_device="cpu"
        assert ("Qdrant/bm25", "cpu") in vs_mod._sparse_encoder_cache


# ────────────────────────────────────────────────
# Default config fallbacks
# ────────────────────────────────────────────────


class TestDefaultFallbacks:
    """Tests for default config attribute resolution."""

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_default_device_from_config(self, mock_log, mock_cls):
        """When device is None, uses cfg.INDEX_EMBED_DEVICE."""
        mock_cls.return_value = MagicMock()
        cfg = _make_cfg(INDEX_EMBED_DEVICE="cpu")
        vs_mod.get_sparse_encoder(cfg=cfg, device=None)
        # Should load on CPU (the default from config)
        mock_cls.assert_called_once_with("prithivida/Splade_PP_en_v1")

    @patch("fastembed.sparse.sparse_text_embedding.SparseTextEmbedding")
    @patch.object(vs_mod, "log")
    def test_default_model_name(self, mock_log, mock_cls):
        """When SPARSE_MODEL_NAME is not set, uses default Splade model."""
        mock_cls.return_value = MagicMock()
        cfg = types.ModuleType("bare_cfg")
        cfg.INDEXING_MODE = "hybrid"
        result = vs_mod.get_sparse_encoder(cfg=cfg, device="cpu")
        assert result is not None
        mock_cls.assert_called_once_with("prithivida/Splade_PP_en_v1")
