# SPDX-License-Identifier: Apache-2.0
"""EMBEDDING_MODE = "remote" (OpenAI-compatible endpoint), retries, TEI gating."""

from __future__ import annotations

import json
import sys
import threading
import types
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

import pytest

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from shared import embedding as emb  # noqa: E402
from shared import openai_embedding as oe  # noqa: E402


def _cfg(**kw):
    values = dict(
        MODEL_NAME="org/model-a",
        USE_TEI=True,
        TEI_URL="http://127.0.0.1:1",  # must never be contacted in remote mode
        EMBED_BACKEND=None,
        EMBEDDING_MODE=None,
        EMBEDDING_URL=None,
        INDEX_EMBED_DEVICE="cuda",
        MCP_EMBED_DEVICE="cuda",
    )
    values.update(kw)
    return types.SimpleNamespace(**values)


# ── Mode resolution ──────────────────────────────────────────────


@pytest.mark.parametrize("raw", [None, "", "  ", "local", "LOCAL"])
def test_unset_or_local_mode(raw):
    assert emb.resolve_embedding_mode(_cfg(EMBEDDING_MODE=raw)) == "local"


def test_remote_mode_and_invalid():
    assert emb.resolve_embedding_mode(_cfg(EMBEDDING_MODE="Remote")) == "remote"
    with pytest.raises(ValueError, match="EMBEDDING_MODE"):
        emb.resolve_embedding_mode(_cfg(EMBEDDING_MODE="cloud"))


def test_missing_attribute_is_local():
    assert emb.resolve_embedding_mode(types.SimpleNamespace()) == "local"


def test_backend_family():
    assert emb.get_embed_backend_family(_cfg()) == "tei"
    assert emb.get_embed_backend_family(_cfg(USE_TEI=False)) == "pytorch"
    assert emb.get_embed_backend_family(_cfg(EMBED_BACKEND="openai")) == "openai"
    assert emb.get_embed_backend_family(_cfg(EMBEDDING_MODE="remote")) == "openai"


def test_uses_tei_container():
    assert emb.uses_tei_container(_cfg())  # default: unchanged behaviour
    assert not emb.uses_tei_container(_cfg(USE_TEI=False))
    assert not emb.uses_tei_container(_cfg(EMBEDDING_MODE="remote"))
    # The OpenAI-compatible backend never needs the TEI container
    assert not emb.uses_tei_container(_cfg(EMBED_BACKEND="openai"))


def test_validate_device_config_skipped_in_remote_mode():
    with patch.object(emb, "_check_cuda_available", side_effect=AssertionError("probed")):
        result = emb.validate_device_config(_cfg(EMBEDDING_MODE="remote"))
    assert not result.errors and not result.warnings


def test_api_key_from_config_or_env(monkeypatch):
    monkeypatch.delenv("HCR_EMBEDDING_API_KEY", raising=False)
    assert emb.embedding_api_key(_cfg()) is None
    monkeypatch.setenv("HCR_EMBEDDING_API_KEY", "env-key")
    assert emb.embedding_api_key(_cfg()) == "env-key"
    monkeypatch.setenv("MY_KEY", "other")
    assert emb.embedding_api_key(_cfg(EMBEDDING_API_KEY_ENV="MY_KEY")) == "other"
    assert emb.embedding_api_key(_cfg(EMBEDDING_API_KEY="cfg-key")) == "cfg-key"


# ── get_embed_model in remote mode ───────────────────────────────


def test_remote_mode_requires_url():
    with pytest.raises(ValueError, match="EMBEDDING_URL"):
        emb.get_embed_model(cfg=_cfg(EMBEDDING_MODE="remote"))


def test_remote_mode_ignores_tei_settings(monkeypatch):
    monkeypatch.delenv("HCR_EMBEDDING_API_KEY", raising=False)
    cfg = _cfg(
        EMBEDDING_MODE="remote",
        EMBEDDING_URL="http://embed.example:8080/",
        EMBEDDING_API_MODEL="served-name",
        EMBEDDING_TIMEOUT=12,
        EMBEDDING_REQUEST_RETRIES=2,
        EMBED_BACKEND="pytorch",
    )
    with patch.object(emb, "TEIEmbedding", side_effect=AssertionError("TEI used")):
        model = emb.get_embed_model(device="cuda", cfg=cfg)
    assert isinstance(model, oe.OpenAICompatEmbedding)
    assert model._tei_url == "http://embed.example:8080"
    assert model._api_model == "served-name"
    assert model._retries == 2 and model._timeout == 12


# ── OpenAI-compatible client against a local stub server ─────────


class _Stub:
    def __init__(self, fail_first: int = 0, status: int = 503, models: bool = True, info: bool = False):
        self.fail_first = fail_first
        self.status = status
        self.models = models
        self.info = info
        self.posts = 0
        self.auth = []
        stub = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, obj):
                body = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path == "/v1/models" and stub.models:
                    return self._send(200, {"data": [{"id": "org/model-a"}]})
                if self.path == "/info" and stub.info:
                    return self._send(200, {"model_id": "org/model-tei"})
                return self._send(404, {"error": "no"})

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length) or b"{}")
                stub.posts += 1
                stub.auth.append(self.headers.get("Authorization"))
                if stub.posts <= stub.fail_first:
                    return self._send(stub.status, {"error": "busy"})
                data = [{"index": i, "embedding": [1.0, float(len(t)), 0.5]}
                        for i, t in enumerate(body.get("input") or [])]
                return self._send(200, {"data": data, "model": body.get("model")})

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def stub_factory():
    made = []

    def make(**kw):
        s = _Stub(**kw)
        made.append(s)
        return s

    yield make
    for s in made:
        s.close()


def _model(url, **kw):
    return oe.OpenAICompatEmbedding(base_url=url, model_name="org/model-a", timeout=5, **kw)


def test_transient_errors_are_retried(stub_factory):
    stub = stub_factory(fail_first=2, status=503)
    with patch.object(oe, "TEI_TRANSIENT_BACKOFF_S", 0.0):
        vec = _model(stub.url, retries=3).get_query_embedding("abc")
    assert vec == [1.0, 3.0, 0.5] and stub.posts == 3


def test_retries_exhausted_raise(stub_factory):
    stub = stub_factory(fail_first=10, status=429)
    with patch.object(oe, "TEI_TRANSIENT_BACKOFF_S", 0.0), pytest.raises(RuntimeError, match="429"):
        _model(stub.url, retries=1)._embed_raw(["x"])
    assert stub.posts == 2


def test_non_transient_error_not_retried(stub_factory):
    stub = stub_factory(fail_first=10, status=400)
    with patch.object(oe, "TEI_TRANSIENT_BACKOFF_S", 0.0), pytest.raises(RuntimeError, match="400"):
        _model(stub.url, retries=3)._embed_raw(["x"])
    assert stub.posts == 1


def test_bearer_token_sent(stub_factory):
    stub = stub_factory()
    _model(stub.url, api_key="secret-value").get_query_embedding("a")
    _model(stub.url).get_query_embedding("a")
    assert stub.auth == ["Bearer secret-value", None]


def test_served_model_name(stub_factory):
    assert _model(stub_factory().url).served_model_name() == "org/model-a"
    assert _model(stub_factory(models=False, info=True).url).served_model_name() == "org/model-tei"
    assert _model(stub_factory(models=False).url).served_model_name() is None


def test_async_query_embedding_runs_off_loop(stub_factory):
    import asyncio

    stub = stub_factory()
    model = _model(stub.url)
    on_main = []
    orig = oe.OpenAICompatEmbedding._embed_raw

    def spy(self, texts):
        on_main.append(threading.current_thread() is threading.main_thread())
        return orig(self, texts)

    with patch.object(oe.OpenAICompatEmbedding, "_embed_raw", spy):
        vec = asyncio.run(model.aget_query_embedding("abcd"))
    assert vec == [1.0, 4.0, 0.5]
    assert on_main == [False]


# ── Indexer provenance gate ──────────────────────────────────────


class _Client:
    def __init__(self, payload):
        self.payload = payload

    def retrieve(self, **kw):
        if self.payload is None:
            return []
        return [types.SimpleNamespace(id=kw["ids"][0], payload=self.payload)]

    def get_collection(self, **kw):
        return types.SimpleNamespace(config=types.SimpleNamespace(metadata={}, params=None))


def test_indexing_legacy_tei_collection_accepts_openai_backend():
    client = _Client({"embed_backend": "tei", "_provenance_sentinel": True})
    emb.check_provenance_for_indexing(client, "c", _cfg(EMBEDDING_MODE="remote"))


def test_indexing_legacy_pytorch_collection_blocks_server_backend():
    client = _Client({"embed_backend": "pytorch", "_provenance_sentinel": True})
    with pytest.raises(SystemExit):
        emb.check_provenance_for_indexing(client, "c", _cfg())


def test_indexing_full_provenance_mismatch_blocks():
    prov = {"model_name": "org/other", "quant": None, "dimension": 3}
    client = _Client({"embed_backend": "tei", "hcr_provenance": prov})
    with pytest.raises(SystemExit):
        emb.check_provenance_for_indexing(client, "c", _cfg())


def test_indexing_no_provenance_passes():
    emb.check_provenance_for_indexing(_Client(None), "c", _cfg())
