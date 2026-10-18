"""TEIEmbedding retries transient transport errors and nothing else."""

import http.client
import io
import json
import urllib.error
from unittest.mock import patch

import pytest

import shared.embedding as emb


class _Resp:
    status = 200

    def __init__(self, payload):
        self._b = json.dumps(payload).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _model():
    return emb.TEIEmbedding(tei_url="http://tei.invalid")


@patch.object(emb.time, "sleep")
def test_connection_reset_is_retried(mock_sleep):
    calls = [ConnectionResetError(10054, "reset"), http.client.RemoteDisconnected("gone"), _Resp([[0.1, 0.2]])]

    def fake(req, timeout=None):
        x = calls.pop(0)
        if isinstance(x, Exception):
            raise x
        return x

    with patch.object(emb.urllib.request, "urlopen", side_effect=fake):
        assert _model()._post_embed(["a"]) == [[0.1, 0.2]]
    assert [c.args[0] for c in mock_sleep.call_args_list] == [1.0, 2.0]


@patch.object(emb.time, "sleep")
def test_busy_http_status_is_retried(mock_sleep):
    busy = urllib.error.HTTPError("u", 503, "busy", {}, io.BytesIO(b"overloaded"))
    seq = [busy, _Resp([[1.0]])]

    def fake(req, timeout=None):
        x = seq.pop(0)
        if isinstance(x, Exception):
            raise x
        return x

    with patch.object(emb.urllib.request, "urlopen", side_effect=fake):
        assert _model()._post_embed(["a"]) == [[1.0]]
    assert mock_sleep.call_count == 1


@patch.object(emb.time, "sleep")
def test_client_error_is_not_retried(mock_sleep):
    bad = urllib.error.HTTPError("u", 413, "too large", {}, io.BytesIO(b"too big"))
    with patch.object(emb.urllib.request, "urlopen", side_effect=bad):
        with pytest.raises(RuntimeError, match="HTTP 413"):
            _model()._post_embed(["a"])
    mock_sleep.assert_not_called()


@patch.object(emb.time, "sleep")
def test_gives_up_after_max_retries(mock_sleep):
    with patch.object(emb.urllib.request, "urlopen", side_effect=ConnectionResetError("reset")):
        with pytest.raises(ConnectionResetError):
            _model()._post_embed(["a"])
    assert mock_sleep.call_count == emb.TEI_TRANSIENT_RETRIES
