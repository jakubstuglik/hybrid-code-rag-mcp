# SPDX-License-Identifier: Apache-2.0
"""Local PyTorch embedder: optional micro-batch and CUDA dtype cast.

Default behaviour stays the llama_index micro-batch of 10 and no cast when
HF_EMBED_BATCH_SIZE is unset or the device is CPU.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
import torch

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from shared import embedding as emb  # noqa: E402

PREFIX = "Represent this query for searching relevant code: "


def _cfg(**kw):
    values = dict(
        MODEL_NAME="org/embed",
        USE_TEI=False,
        EMBED_BACKEND=None,
        EMBEDDING_MODE="local",
        USE_OPENVINO_EMBEDDING=False,
        EMBED_MODEL_KWARGS={"torch_dtype": "float16"},
        EMBED_MAX_SEQ_LENGTH=8192,
        EMBED_DYNAMIC_VRAM_CAP=False,
        EMBED_QUERY_PREFIX=PREFIX,
        EMBED_TEXT_PREFIX=None,
        EMBED_CONFIG_KWARGS=None,
        EMBED_TRUNCATE_DIM=None,
        INDEX_EMBED_DEVICE="cpu",
    )
    values.update(kw)
    return types.SimpleNamespace(**values)


class _Recorder:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._model = torch.nn.Linear(2, 2)


def test_requested_dtype_names():
    assert emb.requested_torch_dtype(_cfg()) is torch.float16
    assert emb.requested_torch_dtype(_cfg(EMBED_MODEL_KWARGS={"torch_dtype": "half"})) is torch.float16
    assert emb.requested_torch_dtype(_cfg(EMBED_MODEL_KWARGS={"torch_dtype": "bfloat16"})) is torch.bfloat16
    assert emb.requested_torch_dtype(_cfg(EMBED_MODEL_KWARGS={"torch_dtype": "float32"})) is torch.float32
    assert emb.requested_torch_dtype(_cfg(EMBED_MODEL_KWARGS={"torch_dtype": torch.float16})) is torch.float16
    assert emb.requested_torch_dtype(_cfg(EMBED_MODEL_KWARGS={})) is None
    assert emb.requested_torch_dtype(_cfg(EMBED_MODEL_KWARGS={"torch_dtype": "int8"})) is None
    assert emb.requested_torch_dtype(_cfg(EMBED_MODEL_KWARGS=None)) is None


def test_micro_batch_default_is_unset():
    assert emb.huggingface_embed_batch_size(_cfg()) is None
    assert emb.huggingface_embed_batch_size(_cfg(HF_EMBED_BATCH_SIZE=16)) == 16
    with pytest.raises(ValueError, match="HF_EMBED_BATCH_SIZE"):
        emb.huggingface_embed_batch_size(_cfg(HF_EMBED_BATCH_SIZE=0))


def test_cuda_cast_applies_configured_dtype_once():
    model = _Recorder()
    emb.apply_configured_embed_dtype(model, "cuda:0", _cfg())
    assert next(model._model.parameters()).dtype is torch.float16
    emb.apply_configured_embed_dtype(model, "cuda:0", _cfg())
    assert next(model._model.parameters()).dtype is torch.float16


def test_cpu_keeps_loaded_dtype():
    model = _Recorder()
    emb.apply_configured_embed_dtype(model, "cpu", _cfg())
    assert next(model._model.parameters()).dtype is torch.float32


def test_get_embed_model_cpu_keeps_default_micro_batch(monkeypatch):
    monkeypatch.setattr(emb, "_resolve_pytorch_device", lambda _device: "cpu")
    seen = {}

    def fake(**kwargs):
        seen.update(kwargs)
        return _Recorder(**kwargs)

    monkeypatch.setattr(emb, "HuggingFaceEmbedding", fake)
    model = emb.get_embed_model(device="cpu", cfg=_cfg())
    assert "embed_batch_size" not in seen
    assert seen["trust_remote_code"] is True
    assert seen["query_instruction"] == PREFIX
    assert "text_instruction" not in seen
    assert seen["model_kwargs"] == {"torch_dtype": "float16"}
    assert seen["max_length"] == 8192
    assert seen["device"] == "cpu"
    assert next(model._model.parameters()).dtype is torch.float32


def test_get_embed_model_passes_micro_batch_and_casts_on_cuda(monkeypatch):
    monkeypatch.setattr(emb, "_resolve_pytorch_device", lambda _device: "cuda:0")
    seen = {}

    def fake(**kwargs):
        seen.update(kwargs)
        return _Recorder(**kwargs)

    monkeypatch.setattr(emb, "HuggingFaceEmbedding", fake)
    model = emb.get_embed_model(device="cuda", cfg=_cfg(HF_EMBED_BATCH_SIZE=16, INDEX_EMBED_DEVICE="cuda"))
    assert seen["embed_batch_size"] == 16
    assert next(model._model.parameters()).dtype is torch.float16
