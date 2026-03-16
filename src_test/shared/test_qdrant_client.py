"""
Tests for shared/qdrant_client.py — unified Qdrant client factory.

Tests cover:
    - _build_client_kwargs(): local mode defaults, custom host/port, remote HTTP,
      remote HTTPS, API key, gRPC, all options combined, invalid mode
    - get_qdrant_client(): constructs sync QdrantClient with correct kwargs
    - get_async_qdrant_client(): constructs async AsyncQdrantClient with correct kwargs
    - get_qdrant_client_pair(): returns (sync, async) tuple with correct kwargs
    - get_qdrant_url(): human-readable URL for all mode/option combinations
    - Edge cases: missing config attributes use defaults, minimal config works
"""

import types
from unittest.mock import MagicMock, patch

import pytest

import shared.qdrant_client as qdrant_client_mod


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_cfg(**kwargs) -> types.ModuleType:
    """Create a fake config module with the given attributes.

    Any attribute not provided will be absent from the module,
    exercising the ``getattr(cfg, ..., default)`` fallback paths.
    """
    cfg = types.ModuleType("fake_config")
    for key, value in kwargs.items():
        setattr(cfg, key, value)
    return cfg


# ────────────────────────────────────────────────
# _build_client_kwargs()
# ────────────────────────────────────────────────


class TestBuildClientKwargs:
    """Tests for _build_client_kwargs() — core kwargs construction logic."""

    def test_local_mode_defaults(self):
        """Local mode with no overrides returns host=localhost, port=6333."""
        cfg = _make_cfg()
        result = qdrant_client_mod._build_client_kwargs(cfg, "local")
        assert result == {"host": "localhost", "port": 6333}

    def test_local_mode_custom_host_and_port(self):
        """Local mode respects QDRANT_HOST and QDRANT_PORT overrides."""
        cfg = _make_cfg(QDRANT_HOST="192.168.1.10", QDRANT_PORT=7777)
        result = qdrant_client_mod._build_client_kwargs(cfg, "local")
        assert result == {"host": "192.168.1.10", "port": 7777}

    def test_local_mode_ignores_remote_options(self):
        """Local mode ignores API key, HTTPS, gRPC settings."""
        cfg = _make_cfg(
            QDRANT_API_KEY="secret-key",
            QDRANT_HTTPS=True,
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=9999,
        )
        result = qdrant_client_mod._build_client_kwargs(cfg, "local")
        assert result == {"host": "localhost", "port": 6333}
        assert "api_key" not in result
        assert "url" not in result
        assert "prefer_grpc" not in result

    def test_remote_mode_plain_http(self):
        """Remote mode without HTTPS returns host= and port= kwargs."""
        cfg = _make_cfg(QDRANT_HOST="my-server", QDRANT_PORT=6333)
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert result == {"host": "my-server", "port": 6333}

    def test_remote_mode_plain_http_defaults(self):
        """Remote mode with no config attributes uses defaults."""
        cfg = _make_cfg()
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert result == {"host": "localhost", "port": 6333}

    def test_remote_mode_with_https(self):
        """Remote HTTPS uses url= instead of host=/port=."""
        cfg = _make_cfg(
            QDRANT_HOST="cluster.qdrant.io",
            QDRANT_PORT=6333,
            QDRANT_HTTPS=True,
        )
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert result == {"url": "https://cluster.qdrant.io:6333"}
        assert "host" not in result
        assert "port" not in result

    def test_remote_mode_with_api_key(self):
        """Remote mode with API key includes api_key in kwargs."""
        cfg = _make_cfg(
            QDRANT_HOST="my-server",
            QDRANT_PORT=6333,
            QDRANT_API_KEY="my-secret-key",
        )
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert result == {
            "host": "my-server",
            "port": 6333,
            "api_key": "my-secret-key",
        }

    def test_remote_mode_with_grpc(self):
        """Remote mode with gRPC adds prefer_grpc and grpc_port."""
        cfg = _make_cfg(
            QDRANT_HOST="my-server",
            QDRANT_PORT=6333,
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=6334,
        )
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert result == {
            "host": "my-server",
            "port": 6333,
            "prefer_grpc": True,
            "grpc_port": 6334,
        }

    def test_remote_mode_grpc_custom_port(self):
        """Remote gRPC uses custom grpc_port when specified."""
        cfg = _make_cfg(
            QDRANT_HOST="my-server",
            QDRANT_PORT=6333,
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=9999,
        )
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert result["grpc_port"] == 9999

    def test_remote_mode_all_options(self):
        """Remote mode with HTTPS + API key + gRPC includes all kwargs."""
        cfg = _make_cfg(
            QDRANT_HOST="cluster.qdrant.io",
            QDRANT_PORT=6333,
            QDRANT_HTTPS=True,
            QDRANT_API_KEY="my-secret",
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=6334,
        )
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert result == {
            "url": "https://cluster.qdrant.io:6333",
            "api_key": "my-secret",
            "prefer_grpc": True,
            "grpc_port": 6334,
        }

    def test_invalid_mode_raises_runtime_error(self):
        """Invalid QDRANT_MODE raises RuntimeError with descriptive message."""
        cfg = _make_cfg()
        with pytest.raises(RuntimeError, match="QDRANT_MODE must be"):
            qdrant_client_mod._build_client_kwargs(cfg, "cloud")

    def test_invalid_mode_includes_bad_value_in_message(self):
        """RuntimeError message includes the invalid mode value."""
        cfg = _make_cfg()
        with pytest.raises(RuntimeError, match=r"got 'bogus'"):
            qdrant_client_mod._build_client_kwargs(cfg, "bogus")

    def test_remote_mode_api_key_none_omitted(self):
        """API key that is None (default) is not included in kwargs."""
        cfg = _make_cfg(QDRANT_HOST="server", QDRANT_API_KEY=None)
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert "api_key" not in result

    def test_remote_mode_api_key_empty_string_omitted(self):
        """API key that is empty string is falsy, so not included."""
        cfg = _make_cfg(QDRANT_HOST="server", QDRANT_API_KEY="")
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert "api_key" not in result

    def test_remote_mode_prefer_grpc_false_omitted(self):
        """prefer_grpc=False (default) does not add gRPC kwargs."""
        cfg = _make_cfg(QDRANT_HOST="server", QDRANT_PREFER_GRPC=False)
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert "prefer_grpc" not in result
        assert "grpc_port" not in result

    def test_remote_mode_grpc_default_port(self):
        """gRPC without explicit grpc_port defaults to 6334."""
        cfg = _make_cfg(QDRANT_HOST="server", QDRANT_PREFER_GRPC=True)
        result = qdrant_client_mod._build_client_kwargs(cfg, "remote")
        assert result["grpc_port"] == 6334


# ────────────────────────────────────────────────
# get_qdrant_client()
# ────────────────────────────────────────────────


class TestGetQdrantClient:
    """Tests for get_qdrant_client() — sync client construction."""

    @patch("qdrant_client.QdrantClient")
    def test_local_mode_constructs_client(self, mock_cls):
        """Constructs QdrantClient with local kwargs when mode is local."""
        cfg = _make_cfg(QDRANT_MODE="local")
        mock_cls.return_value = MagicMock(name="sync_client")

        result = qdrant_client_mod.get_qdrant_client(cfg)

        mock_cls.assert_called_once_with(host="localhost", port=6333)
        assert result is mock_cls.return_value

    @patch("qdrant_client.QdrantClient")
    def test_remote_mode_constructs_client(self, mock_cls):
        """Constructs QdrantClient with remote kwargs."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="remote-host",
            QDRANT_PORT=6333,
            QDRANT_API_KEY="key123",
        )
        mock_cls.return_value = MagicMock(name="sync_client")

        result = qdrant_client_mod.get_qdrant_client(cfg)

        mock_cls.assert_called_once_with(
            host="remote-host", port=6333, api_key="key123"
        )
        assert result is mock_cls.return_value

    @patch("qdrant_client.QdrantClient")
    def test_default_mode_is_local(self, mock_cls):
        """When QDRANT_MODE is absent, defaults to local."""
        cfg = _make_cfg()  # no QDRANT_MODE attribute
        mock_cls.return_value = MagicMock(name="sync_client")

        qdrant_client_mod.get_qdrant_client(cfg)

        mock_cls.assert_called_once_with(host="localhost", port=6333)

    @patch("qdrant_client.QdrantClient")
    def test_remote_https_constructs_with_url(self, mock_cls):
        """Remote HTTPS passes url= kwarg to QdrantClient."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="cluster.io",
            QDRANT_PORT=443,
            QDRANT_HTTPS=True,
        )
        mock_cls.return_value = MagicMock(name="sync_client")

        qdrant_client_mod.get_qdrant_client(cfg)

        mock_cls.assert_called_once_with(url="https://cluster.io:443")


# ────────────────────────────────────────────────
# get_async_qdrant_client()
# ────────────────────────────────────────────────


class TestGetAsyncQdrantClient:
    """Tests for get_async_qdrant_client() — async client construction."""

    @patch("qdrant_client.AsyncQdrantClient")
    def test_local_mode_constructs_async_client(self, mock_cls):
        """Constructs AsyncQdrantClient with local kwargs."""
        cfg = _make_cfg(QDRANT_MODE="local")
        mock_cls.return_value = MagicMock(name="async_client")

        result = qdrant_client_mod.get_async_qdrant_client(cfg)

        mock_cls.assert_called_once_with(host="localhost", port=6333)
        assert result is mock_cls.return_value

    @patch("qdrant_client.AsyncQdrantClient")
    def test_remote_mode_constructs_async_client(self, mock_cls):
        """Constructs AsyncQdrantClient with remote kwargs."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="remote-host",
            QDRANT_PORT=6333,
        )
        mock_cls.return_value = MagicMock(name="async_client")

        result = qdrant_client_mod.get_async_qdrant_client(cfg)

        mock_cls.assert_called_once_with(host="remote-host", port=6333)
        assert result is mock_cls.return_value

    @patch("qdrant_client.AsyncQdrantClient")
    def test_default_mode_is_local(self, mock_cls):
        """When QDRANT_MODE is absent, defaults to local."""
        cfg = _make_cfg()
        mock_cls.return_value = MagicMock(name="async_client")

        qdrant_client_mod.get_async_qdrant_client(cfg)

        mock_cls.assert_called_once_with(host="localhost", port=6333)

    @patch("qdrant_client.AsyncQdrantClient")
    def test_remote_all_options(self, mock_cls):
        """Remote HTTPS + API key + gRPC passes all kwargs."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="cluster.io",
            QDRANT_PORT=6333,
            QDRANT_HTTPS=True,
            QDRANT_API_KEY="secret",
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=6334,
        )
        mock_cls.return_value = MagicMock(name="async_client")

        qdrant_client_mod.get_async_qdrant_client(cfg)

        mock_cls.assert_called_once_with(
            url="https://cluster.io:6333",
            api_key="secret",
            prefer_grpc=True,
            grpc_port=6334,
        )


# ────────────────────────────────────────────────
# get_qdrant_client_pair()
# ────────────────────────────────────────────────


class TestGetQdrantClientPair:
    """Tests for get_qdrant_client_pair() — returns (sync, async) tuple."""

    @patch("qdrant_client.AsyncQdrantClient")
    @patch("qdrant_client.QdrantClient")
    def test_returns_tuple_of_two_clients(self, mock_sync, mock_async):
        """Returns a 2-tuple of (sync_client, async_client)."""
        cfg = _make_cfg(QDRANT_MODE="local")
        mock_sync.return_value = MagicMock(name="sync")
        mock_async.return_value = MagicMock(name="async")

        result = qdrant_client_mod.get_qdrant_client_pair(cfg)

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is mock_sync.return_value
        assert result[1] is mock_async.return_value

    @patch("qdrant_client.AsyncQdrantClient")
    @patch("qdrant_client.QdrantClient")
    def test_both_clients_get_same_kwargs(self, mock_sync, mock_async):
        """Both sync and async clients are constructed with identical kwargs."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="server",
            QDRANT_PORT=6333,
            QDRANT_API_KEY="key",
        )

        qdrant_client_mod.get_qdrant_client_pair(cfg)

        expected = {"host": "server", "port": 6333, "api_key": "key"}
        mock_sync.assert_called_once_with(**expected)
        mock_async.assert_called_once_with(**expected)

    @patch("qdrant_client.AsyncQdrantClient")
    @patch("qdrant_client.QdrantClient")
    def test_default_mode_is_local(self, mock_sync, mock_async):
        """When QDRANT_MODE is absent, both clients use local defaults."""
        cfg = _make_cfg()

        qdrant_client_mod.get_qdrant_client_pair(cfg)

        expected = {"host": "localhost", "port": 6333}
        mock_sync.assert_called_once_with(**expected)
        mock_async.assert_called_once_with(**expected)

    @patch("qdrant_client.AsyncQdrantClient")
    @patch("qdrant_client.QdrantClient")
    def test_remote_https_grpc(self, mock_sync, mock_async):
        """Remote HTTPS + gRPC kwargs passed to both clients."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="cluster.io",
            QDRANT_PORT=443,
            QDRANT_HTTPS=True,
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=6334,
        )

        qdrant_client_mod.get_qdrant_client_pair(cfg)

        expected = {
            "url": "https://cluster.io:443",
            "prefer_grpc": True,
            "grpc_port": 6334,
        }
        mock_sync.assert_called_once_with(**expected)
        mock_async.assert_called_once_with(**expected)


# ────────────────────────────────────────────────
# get_qdrant_url()
# ────────────────────────────────────────────────


class TestGetQdrantUrl:
    """Tests for get_qdrant_url() — human-readable URL for logging."""

    def test_local_mode_default(self):
        """Local mode with defaults returns 'localhost:6333'."""
        cfg = _make_cfg(QDRANT_MODE="local")
        assert qdrant_client_mod.get_qdrant_url(cfg) == "localhost:6333"

    def test_local_mode_custom_port(self):
        """Local mode uses custom port in output."""
        cfg = _make_cfg(QDRANT_MODE="local", QDRANT_PORT=7777)
        assert qdrant_client_mod.get_qdrant_url(cfg) == "localhost:7777"

    def test_local_mode_ignores_host(self):
        """Local mode always shows 'localhost' regardless of QDRANT_HOST."""
        cfg = _make_cfg(QDRANT_MODE="local", QDRANT_HOST="custom-host")
        assert qdrant_client_mod.get_qdrant_url(cfg) == "localhost:6333"

    def test_default_mode_is_local(self):
        """When QDRANT_MODE absent, defaults to local URL format."""
        cfg = _make_cfg()
        assert qdrant_client_mod.get_qdrant_url(cfg) == "localhost:6333"

    def test_remote_mode_http(self):
        """Remote HTTP returns 'http://host:port'."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="my-server",
            QDRANT_PORT=6333,
        )
        assert qdrant_client_mod.get_qdrant_url(cfg) == "http://my-server:6333"

    def test_remote_mode_https(self):
        """Remote HTTPS returns 'https://host:port'."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="cluster.qdrant.io",
            QDRANT_PORT=6333,
            QDRANT_HTTPS=True,
        )
        url = qdrant_client_mod.get_qdrant_url(cfg)
        assert url == "https://cluster.qdrant.io:6333"

    def test_remote_mode_with_grpc(self):
        """Remote with gRPC appends ' (gRPC:port)' suffix."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="my-server",
            QDRANT_PORT=6333,
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=6334,
        )
        url = qdrant_client_mod.get_qdrant_url(cfg)
        assert url == "http://my-server:6333 (gRPC:6334)"

    def test_remote_mode_https_with_grpc(self):
        """Remote HTTPS + gRPC includes both scheme and gRPC suffix."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="cluster.io",
            QDRANT_PORT=443,
            QDRANT_HTTPS=True,
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=6334,
        )
        url = qdrant_client_mod.get_qdrant_url(cfg)
        assert url == "https://cluster.io:443 (gRPC:6334)"

    def test_remote_mode_grpc_custom_port(self):
        """gRPC suffix shows the custom grpc_port value."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="server",
            QDRANT_PORT=6333,
            QDRANT_PREFER_GRPC=True,
            QDRANT_GRPC_PORT=9999,
        )
        url = qdrant_client_mod.get_qdrant_url(cfg)
        assert url == "http://server:6333 (gRPC:9999)"

    def test_remote_mode_grpc_default_port(self):
        """gRPC without explicit QDRANT_GRPC_PORT defaults to 6334."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="server",
            QDRANT_PORT=6333,
            QDRANT_PREFER_GRPC=True,
        )
        url = qdrant_client_mod.get_qdrant_url(cfg)
        assert url == "http://server:6333 (gRPC:6334)"

    def test_remote_mode_no_grpc_no_suffix(self):
        """Remote without gRPC does NOT include the gRPC suffix."""
        cfg = _make_cfg(
            QDRANT_MODE="remote",
            QDRANT_HOST="server",
            QDRANT_PORT=6333,
        )
        url = qdrant_client_mod.get_qdrant_url(cfg)
        assert "(gRPC" not in url

    def test_remote_mode_defaults(self):
        """Remote mode with no overrides uses defaults."""
        cfg = _make_cfg(QDRANT_MODE="remote")
        url = qdrant_client_mod.get_qdrant_url(cfg)
        assert url == "http://localhost:6333"


# ────────────────────────────────────────────────
# Edge cases / integration
# ────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases and integration scenarios."""

    def test_completely_empty_config_works(self):
        """A config with zero attributes uses all defaults (local mode)."""
        cfg = _make_cfg()
        kwargs = qdrant_client_mod._build_client_kwargs(cfg, "local")
        assert kwargs == {"host": "localhost", "port": 6333}

        url = qdrant_client_mod.get_qdrant_url(cfg)
        assert url == "localhost:6333"

    def test_invalid_mode_from_get_qdrant_client(self):
        """get_qdrant_client propagates RuntimeError for invalid mode."""
        cfg = _make_cfg(QDRANT_MODE="invalid")
        with pytest.raises(RuntimeError, match="QDRANT_MODE must be"):
            qdrant_client_mod.get_qdrant_client(cfg)

    def test_invalid_mode_from_get_async_qdrant_client(self):
        """get_async_qdrant_client propagates RuntimeError for invalid mode."""
        cfg = _make_cfg(QDRANT_MODE="invalid")
        with pytest.raises(RuntimeError, match="QDRANT_MODE must be"):
            qdrant_client_mod.get_async_qdrant_client(cfg)

    def test_invalid_mode_from_get_qdrant_client_pair(self):
        """get_qdrant_client_pair propagates RuntimeError for invalid mode."""
        cfg = _make_cfg(QDRANT_MODE="invalid")
        with pytest.raises(RuntimeError, match="QDRANT_MODE must be"):
            qdrant_client_mod.get_qdrant_client_pair(cfg)

    @patch("qdrant_client.QdrantClient")
    def test_port_as_integer_preserved(self, mock_cls):
        """Port value is passed through as-is (integer, not string)."""
        cfg = _make_cfg(QDRANT_MODE="local", QDRANT_PORT=9999)
        qdrant_client_mod.get_qdrant_client(cfg)
        _, kwargs = mock_cls.call_args
        assert kwargs["port"] == 9999
        assert isinstance(kwargs["port"], int)
