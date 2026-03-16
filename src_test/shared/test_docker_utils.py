"""
Tests for shared/docker_utils.py — Docker container management for Qdrant.

Tests cover:
    - get_container_name(): explicit name, auto-derived, default collection
    - get_volume_path(): explicit path, auto-derived, defaults, forward slashes
    - _run_docker(): command construction, check flag, timeout
    - _container_exists(): exists (rc=0) vs not (rc!=0)
    - _container_running(): running, stopped, not found
    - _create_container(): correct docker run args, port/volume mapping
    - _start_container(): correct docker start args
    - _wait_for_health(): success first try, retry, timeout, exceptions
    - ensure_qdrant_running(): all orchestration paths + error handling
"""

import subprocess
import types
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

import shared.docker_utils as docker_utils_mod


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_cfg(**kwargs) -> types.ModuleType:
    """Create a fake config module with the given attributes.

    Defaults to QDRANT_MODE="local" if not specified, since most tests
    exercise the local Docker path.
    """
    cfg = types.ModuleType("fake_config")
    kwargs.setdefault("QDRANT_MODE", "local")
    kwargs.setdefault("QDRANT_HOST", "localhost")
    kwargs.setdefault("QDRANT_PORT", 6333)
    for k, v in kwargs.items():
        setattr(cfg, k, v)
    return cfg


def _completed(
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess:
    """Build a CompletedProcess with the given fields."""
    return subprocess.CompletedProcess(
        args=["docker"], returncode=returncode, stdout=stdout, stderr=stderr
    )


# ────────────────────────────────────────────────
# Constants sanity check
# ────────────────────────────────────────────────


class TestConstants:
    """Verify module-level constants are as expected."""

    def test_qdrant_image(self):
        assert docker_utils_mod.QDRANT_IMAGE == "qdrant/qdrant:latest"

    def test_health_check_max_retries(self):
        assert docker_utils_mod.HEALTH_CHECK_MAX_RETRIES == 30

    def test_health_check_interval(self):
        assert docker_utils_mod.HEALTH_CHECK_INTERVAL_S == 1.0


# ────────────────────────────────────────────────
# get_container_name()
# ────────────────────────────────────────────────


class TestGetContainerName:
    """Tests for get_container_name()."""

    def test_explicit_name(self):
        """Uses QDRANT_DOCKER_CONTAINER when set."""
        cfg = _make_cfg(QDRANT_DOCKER_CONTAINER="my-qdrant")
        assert docker_utils_mod.get_container_name(cfg) == "my-qdrant"

    def test_auto_derived_from_collection(self):
        """Derives qdrant-{COLLECTION_NAME} when no explicit name."""
        cfg = _make_cfg(COLLECTION_NAME="informica_rag")
        assert docker_utils_mod.get_container_name(cfg) == "qdrant-informica_rag"

    def test_default_collection(self):
        """Falls back to 'default_rag' when COLLECTION_NAME not set."""
        cfg = _make_cfg()
        assert docker_utils_mod.get_container_name(cfg) == "qdrant-default_rag"

    def test_explicit_empty_string_uses_auto(self):
        """Empty string for QDRANT_DOCKER_CONTAINER is falsy — uses auto."""
        cfg = _make_cfg(QDRANT_DOCKER_CONTAINER="")
        assert docker_utils_mod.get_container_name(cfg) == "qdrant-default_rag"

    def test_explicit_none_uses_auto(self):
        """None for QDRANT_DOCKER_CONTAINER is falsy — uses auto."""
        cfg = _make_cfg(QDRANT_DOCKER_CONTAINER=None)
        assert docker_utils_mod.get_container_name(cfg) == "qdrant-default_rag"


# ────────────────────────────────────────────────
# get_volume_path()
# ────────────────────────────────────────────────


class TestGetVolumePath:
    """Tests for get_volume_path()."""

    def test_explicit_path(self):
        """Uses QDRANT_DOCKER_VOLUME when set, resolved to absolute."""
        cfg = _make_cfg(QDRANT_DOCKER_VOLUME="./my_data")
        result = docker_utils_mod.get_volume_path(cfg)
        assert "/" in result  # Forward slashes
        assert "\\" not in result
        # Should be absolute
        assert Path(result.replace("/", "\\")).is_absolute() or result.startswith("/")

    def test_auto_derived_from_base_and_model(self):
        """Derives {BASE_PATH}/{MODEL_PATH} when no explicit volume."""
        cfg = _make_cfg(BASE_PATH="qdrant_data", MODEL_PATH="my_index")
        result = docker_utils_mod.get_volume_path(cfg)
        # Should end with the combined path
        assert result.endswith("qdrant_data/my_index")
        assert "\\" not in result

    def test_defaults(self):
        """Falls back to 'qdrant/default_index' when neither is set."""
        cfg = _make_cfg()
        result = docker_utils_mod.get_volume_path(cfg)
        assert result.endswith("qdrant/default_index")
        assert "\\" not in result

    def test_forward_slash_conversion(self):
        """Backslashes in Windows paths are converted to forward slashes."""
        cfg = _make_cfg(QDRANT_DOCKER_VOLUME="C:\\Users\\test\\data")
        result = docker_utils_mod.get_volume_path(cfg)
        assert "\\" not in result

    def test_explicit_empty_string_uses_auto(self):
        """Empty QDRANT_DOCKER_VOLUME is falsy — falls back to auto."""
        cfg = _make_cfg(QDRANT_DOCKER_VOLUME="", BASE_PATH="qd", MODEL_PATH="idx")
        result = docker_utils_mod.get_volume_path(cfg)
        assert result.endswith("qd/idx")

    def test_result_is_absolute(self):
        """The returned path is always absolute."""
        cfg = _make_cfg(BASE_PATH="relative_dir", MODEL_PATH="sub")
        result = docker_utils_mod.get_volume_path(cfg)
        # On Windows it starts with drive letter; on Unix with /
        assert Path(result.replace("/", "\\")).is_absolute() or result.startswith("/")


# ────────────────────────────────────────────────
# _run_docker()
# ────────────────────────────────────────────────


class TestRunDocker:
    """Tests for _run_docker()."""

    @patch("subprocess.run")
    def test_command_construction(self, mock_run):
        """Prepends 'docker' to the args list."""
        mock_run.return_value = _completed()
        docker_utils_mod._run_docker(["ps", "-a"])
        mock_run.assert_called_once_with(
            ["docker", "ps", "-a"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )

    @patch("subprocess.run")
    def test_check_true_by_default(self, mock_run):
        """check=True is the default."""
        mock_run.return_value = _completed()
        docker_utils_mod._run_docker(["info"])
        _, kwargs = mock_run.call_args
        assert kwargs["check"] is True

    @patch("subprocess.run")
    def test_check_false(self, mock_run):
        """check=False is passed through."""
        mock_run.return_value = _completed(returncode=1)
        docker_utils_mod._run_docker(["inspect", "foo"], check=False)
        _, kwargs = mock_run.call_args
        assert kwargs["check"] is False

    @patch("subprocess.run")
    def test_timeout_is_60(self, mock_run):
        """Timeout is set to 60 seconds."""
        mock_run.return_value = _completed()
        docker_utils_mod._run_docker(["version"])
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 60

    @patch("subprocess.run")
    def test_returns_completed_process(self, mock_run):
        """Returns the CompletedProcess from subprocess.run."""
        expected = _completed(stdout="hello")
        mock_run.return_value = expected
        result = docker_utils_mod._run_docker(["info"])
        assert result is expected

    @patch("subprocess.run")
    def test_captures_output(self, mock_run):
        """capture_output=True and text=True are set."""
        mock_run.return_value = _completed()
        docker_utils_mod._run_docker(["ps"])
        _, kwargs = mock_run.call_args
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True


# ────────────────────────────────────────────────
# _container_exists()
# ────────────────────────────────────────────────


class TestContainerExists:
    """Tests for _container_exists()."""

    @patch.object(docker_utils_mod, "_run_docker")
    def test_exists_returncode_zero(self, mock_run):
        """Container exists when returncode is 0."""
        mock_run.return_value = _completed(returncode=0, stdout="running")
        assert docker_utils_mod._container_exists("my-qdrant") is True

    @patch.object(docker_utils_mod, "_run_docker")
    def test_not_exists_returncode_nonzero(self, mock_run):
        """Container doesn't exist when returncode is non-zero."""
        mock_run.return_value = _completed(returncode=1, stderr="not found")
        assert docker_utils_mod._container_exists("missing") is False

    @patch.object(docker_utils_mod, "_run_docker")
    def test_calls_inspect_with_check_false(self, mock_run):
        """Uses docker inspect with check=False."""
        mock_run.return_value = _completed()
        docker_utils_mod._container_exists("test-ctr")
        mock_run.assert_called_once_with(
            ["inspect", "--format", "{{.State.Status}}", "test-ctr"],
            check=False,
        )


# ────────────────────────────────────────────────
# _container_running()
# ────────────────────────────────────────────────


class TestContainerRunning:
    """Tests for _container_running()."""

    @patch.object(docker_utils_mod, "_run_docker")
    def test_running_status(self, mock_run):
        """Returns True when status is 'running'."""
        mock_run.return_value = _completed(stdout="running\n")
        assert docker_utils_mod._container_running("my-ctr") is True

    @patch.object(docker_utils_mod, "_run_docker")
    def test_stopped_status(self, mock_run):
        """Returns False when status is 'exited'."""
        mock_run.return_value = _completed(stdout="exited\n")
        assert docker_utils_mod._container_running("my-ctr") is False

    @patch.object(docker_utils_mod, "_run_docker")
    def test_container_not_found(self, mock_run):
        """Returns False when container doesn't exist (returncode != 0)."""
        mock_run.return_value = _completed(returncode=1)
        assert docker_utils_mod._container_running("missing") is False

    @patch.object(docker_utils_mod, "_run_docker")
    def test_created_status(self, mock_run):
        """Returns False for 'created' status (not yet started)."""
        mock_run.return_value = _completed(stdout="created\n")
        assert docker_utils_mod._container_running("my-ctr") is False

    @patch.object(docker_utils_mod, "_run_docker")
    def test_calls_inspect_with_check_false(self, mock_run):
        """Uses docker inspect with check=False."""
        mock_run.return_value = _completed(stdout="running")
        docker_utils_mod._container_running("ctr")
        mock_run.assert_called_once_with(
            ["inspect", "--format", "{{.State.Status}}", "ctr"],
            check=False,
        )


# ────────────────────────────────────────────────
# _create_container()
# ────────────────────────────────────────────────


class TestCreateContainer:
    """Tests for _create_container()."""

    @patch.object(docker_utils_mod, "log")
    @patch.object(docker_utils_mod, "_run_docker")
    def test_correct_docker_run_args(self, mock_run, mock_log):
        """Builds correct docker run command with all flags."""
        mock_run.return_value = _completed()
        docker_utils_mod._create_container("my-qdrant", 6333, "/data/qdrant")
        mock_run.assert_called_once_with(
            [
                "run",
                "-d",
                "--name",
                "my-qdrant",
                "-p",
                "6333:6333",
                "-v",
                "/data/qdrant:/qdrant/storage",
                "qdrant/qdrant:latest",
            ]
        )

    @patch.object(docker_utils_mod, "log")
    @patch.object(docker_utils_mod, "_run_docker")
    def test_custom_port_mapping(self, mock_run, mock_log):
        """Port mapping uses host_port:6333 format."""
        mock_run.return_value = _completed()
        docker_utils_mod._create_container("ctr", 6973, "/vol")
        args = mock_run.call_args[0][0]
        assert f"6973:6333" in args

    @patch.object(docker_utils_mod, "log")
    @patch.object(docker_utils_mod, "_run_docker")
    def test_volume_mapping(self, mock_run, mock_log):
        """Volume is mapped to /qdrant/storage inside the container."""
        mock_run.return_value = _completed()
        docker_utils_mod._create_container("ctr", 6333, "/my/vol")
        args = mock_run.call_args[0][0]
        assert "/my/vol:/qdrant/storage" in args

    @patch.object(docker_utils_mod, "log")
    @patch.object(docker_utils_mod, "_run_docker")
    def test_uses_qdrant_image(self, mock_run, mock_log):
        """Uses the QDRANT_IMAGE constant."""
        mock_run.return_value = _completed()
        docker_utils_mod._create_container("ctr", 6333, "/vol")
        args = mock_run.call_args[0][0]
        assert args[-1] == docker_utils_mod.QDRANT_IMAGE

    @patch.object(docker_utils_mod, "log")
    @patch.object(docker_utils_mod, "_run_docker")
    def test_logs_creation(self, mock_run, mock_log):
        """Logs creation and completion messages."""
        mock_run.return_value = _completed()
        docker_utils_mod._create_container("my-ctr", 6333, "/vol")
        assert mock_log.call_count == 2
        assert "Creating" in mock_log.call_args_list[0][0][0]
        assert "created" in mock_log.call_args_list[1][0][0]


# ────────────────────────────────────────────────
# _start_container()
# ────────────────────────────────────────────────


class TestStartContainer:
    """Tests for _start_container()."""

    @patch.object(docker_utils_mod, "log")
    @patch.object(docker_utils_mod, "_run_docker")
    def test_correct_start_args(self, mock_run, mock_log):
        """Calls docker start with the container name."""
        mock_run.return_value = _completed()
        docker_utils_mod._start_container("my-qdrant")
        mock_run.assert_called_once_with(["start", "my-qdrant"])

    @patch.object(docker_utils_mod, "log")
    @patch.object(docker_utils_mod, "_run_docker")
    def test_logs_start(self, mock_run, mock_log):
        """Logs starting and started messages."""
        mock_run.return_value = _completed()
        docker_utils_mod._start_container("ctr")
        assert mock_log.call_count == 2
        assert "Starting" in mock_log.call_args_list[0][0][0]
        assert "started" in mock_log.call_args_list[1][0][0]


# ────────────────────────────────────────────────
# _wait_for_health()
# ────────────────────────────────────────────────


class TestWaitForHealth:
    """Tests for _wait_for_health()."""

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_success_first_try(self, mock_urlopen, mock_sleep):
        """Returns True immediately if /healthz returns 200."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        assert docker_utils_mod._wait_for_health("localhost", 6333) is True
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_success_after_retries(self, mock_urlopen, mock_sleep):
        """Returns True after a few failures then a 200 response."""
        import urllib.error

        fail_resp = MagicMock()
        fail_resp.__enter__ = MagicMock(
            side_effect=urllib.error.URLError("connection refused")
        )
        fail_resp.__exit__ = MagicMock(return_value=False)

        ok_resp = MagicMock()
        ok_resp.status = 200
        ok_resp.__enter__ = MagicMock(return_value=ok_resp)
        ok_resp.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [
            urllib.error.URLError("refused"),
            urllib.error.URLError("refused"),
            ok_resp,
        ]
        result = docker_utils_mod._wait_for_health(
            "localhost", 6333, max_retries=5, interval=0.1
        )
        assert result is True
        assert mock_sleep.call_count == 2

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_timeout_returns_false(self, mock_urlopen, mock_sleep):
        """Returns False after exhausting all retries."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("refused")
        result = docker_utils_mod._wait_for_health(
            "localhost", 6333, max_retries=3, interval=0.01
        )
        assert result is False
        assert mock_sleep.call_count == 3

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_oserror_retries(self, mock_urlopen, mock_sleep):
        """Handles OSError (e.g. connection reset) and keeps retrying."""
        ok_resp = MagicMock()
        ok_resp.status = 200
        ok_resp.__enter__ = MagicMock(return_value=ok_resp)
        ok_resp.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [OSError("reset"), ok_resp]
        result = docker_utils_mod._wait_for_health(
            "localhost", 6333, max_retries=5, interval=0.01
        )
        assert result is True

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_timeout_error_retries(self, mock_urlopen, mock_sleep):
        """Handles TimeoutError and keeps retrying."""
        ok_resp = MagicMock()
        ok_resp.status = 200
        ok_resp.__enter__ = MagicMock(return_value=ok_resp)
        ok_resp.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [TimeoutError(), ok_resp]
        result = docker_utils_mod._wait_for_health(
            "localhost", 6333, max_retries=5, interval=0.01
        )
        assert result is True

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_uses_correct_url(self, mock_urlopen, mock_sleep):
        """Builds http://{host}:{port}/healthz URL."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("refused")
        docker_utils_mod._wait_for_health("myhost", 9999, max_retries=1, interval=0.01)
        req_obj = mock_urlopen.call_args[0][0]
        assert req_obj.full_url == "http://myhost:9999/healthz"

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_sleeps_with_correct_interval(self, mock_urlopen, mock_sleep):
        """Sleeps with the configured interval between retries."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("refused")
        docker_utils_mod._wait_for_health(
            "localhost", 6333, max_retries=2, interval=0.5
        )
        assert mock_sleep.call_args_list == [call(0.5), call(0.5)]

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_non_200_status_retries(self, mock_urlopen, mock_sleep):
        """Non-200 status codes cause sleep and retry."""
        resp_503 = MagicMock()
        resp_503.status = 503
        resp_503.__enter__ = MagicMock(return_value=resp_503)
        resp_503.__exit__ = MagicMock(return_value=False)

        resp_200 = MagicMock()
        resp_200.status = 200
        resp_200.__enter__ = MagicMock(return_value=resp_200)
        resp_200.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [resp_503, resp_200]
        result = docker_utils_mod._wait_for_health(
            "localhost", 6333, max_retries=3, interval=0.01
        )
        assert result is True
        # First attempt: 503 → sleep; second attempt: 200 → return True
        assert mock_sleep.call_count == 1


# ────────────────────────────────────────────────
# ensure_qdrant_running()
# ────────────────────────────────────────────────


class TestEnsureQdrantRunning:
    """Tests for ensure_qdrant_running() — main orchestrator."""

    # -- Remote mode --

    def test_remote_mode_returns_true(self):
        """Remote mode is a no-op — returns True immediately."""
        cfg = _make_cfg(QDRANT_MODE="remote")
        assert docker_utils_mod.ensure_qdrant_running(cfg) is True

    def test_non_local_mode_returns_true(self):
        """Any mode other than 'local' returns True."""
        cfg = _make_cfg(QDRANT_MODE="cloud")
        assert docker_utils_mod.ensure_qdrant_running(cfg) is True

    # -- Container already running --

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=True)
    @patch.object(docker_utils_mod, "log")
    def test_container_running_goes_to_health_check(
        self, mock_log, mock_running, mock_health
    ):
        """Running container → log + health check only."""
        cfg = _make_cfg(COLLECTION_NAME="test_col")
        result = docker_utils_mod.ensure_qdrant_running(cfg)
        assert result is True
        mock_running.assert_called_once_with("qdrant-test_col")
        mock_health.assert_called_once()

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=True)
    @patch.object(docker_utils_mod, "_start_container")
    @patch.object(docker_utils_mod, "_create_container")
    @patch.object(docker_utils_mod, "log")
    def test_container_running_no_start_no_create(
        self, mock_log, mock_create, mock_start, mock_running, mock_health
    ):
        """Running container does not call start or create."""
        cfg = _make_cfg()
        docker_utils_mod.ensure_qdrant_running(cfg)
        mock_start.assert_not_called()
        mock_create.assert_not_called()

    # -- Container exists but stopped --

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_exists", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=False)
    @patch.object(docker_utils_mod, "_start_container")
    @patch.object(docker_utils_mod, "log")
    def test_stopped_container_starts(
        self, mock_log, mock_start, mock_running, mock_exists, mock_health
    ):
        """Stopped container → _start_container then health check."""
        cfg = _make_cfg(QDRANT_DOCKER_CONTAINER="my-qdrant")
        result = docker_utils_mod.ensure_qdrant_running(cfg)
        assert result is True
        mock_start.assert_called_once_with("my-qdrant")
        mock_health.assert_called_once()

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_exists", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=False)
    @patch.object(docker_utils_mod, "_start_container")
    @patch.object(docker_utils_mod, "_create_container")
    @patch.object(docker_utils_mod, "log")
    def test_stopped_container_no_create(
        self, mock_log, mock_create, mock_start, mock_running, mock_exists, mock_health
    ):
        """Stopped container does not call create."""
        cfg = _make_cfg()
        docker_utils_mod.ensure_qdrant_running(cfg)
        mock_create.assert_not_called()

    # -- Container doesn't exist --

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_exists", return_value=False)
    @patch.object(docker_utils_mod, "_container_running", return_value=False)
    @patch.object(docker_utils_mod, "_create_container")
    @patch("pathlib.Path.mkdir")
    @patch.object(docker_utils_mod, "log")
    def test_no_container_creates(
        self, mock_log, mock_mkdir, mock_create, mock_running, mock_exists, mock_health
    ):
        """No container → mkdir + create then health check."""
        cfg = _make_cfg(
            COLLECTION_NAME="test",
            QDRANT_PORT=6333,
        )
        result = docker_utils_mod.ensure_qdrant_running(cfg)
        assert result is True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_create.assert_called_once()

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_exists", return_value=False)
    @patch.object(docker_utils_mod, "_container_running", return_value=False)
    @patch.object(docker_utils_mod, "_create_container")
    @patch("pathlib.Path.mkdir")
    @patch.object(docker_utils_mod, "log")
    def test_no_container_passes_correct_args_to_create(
        self, mock_log, mock_mkdir, mock_create, mock_running, mock_exists, mock_health
    ):
        """Create is called with container_name, port, volume_path."""
        cfg = _make_cfg(
            QDRANT_DOCKER_CONTAINER="ctr-42",
            QDRANT_PORT=6973,
            QDRANT_DOCKER_VOLUME="./vol",
        )
        docker_utils_mod.ensure_qdrant_running(cfg)
        args = mock_create.call_args[0]
        assert args[0] == "ctr-42"
        assert args[1] == 6973
        # Volume path is resolved to absolute with forward slashes
        assert "\\" not in args[2]

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_exists", return_value=False)
    @patch.object(docker_utils_mod, "_container_running", return_value=False)
    @patch.object(docker_utils_mod, "_create_container")
    @patch.object(docker_utils_mod, "_start_container")
    @patch("pathlib.Path.mkdir")
    @patch.object(docker_utils_mod, "log")
    def test_no_container_does_not_start(
        self,
        mock_log,
        mock_mkdir,
        mock_start,
        mock_create,
        mock_running,
        mock_exists,
        mock_health,
    ):
        """New container path does not call start."""
        cfg = _make_cfg()
        docker_utils_mod.ensure_qdrant_running(cfg)
        mock_start.assert_not_called()

    # -- Health check fails --

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=False)
    @patch.object(docker_utils_mod, "_container_running", return_value=True)
    @patch.object(docker_utils_mod, "log_error")
    @patch.object(docker_utils_mod, "log")
    def test_health_check_fails_returns_false(
        self, mock_log, mock_log_error, mock_running, mock_health
    ):
        """Returns False when health check exhausts retries."""
        cfg = _make_cfg()
        result = docker_utils_mod.ensure_qdrant_running(cfg)
        assert result is False
        mock_log_error.assert_called_once()
        assert "not healthy" in mock_log_error.call_args[0][0]

    # -- CalledProcessError --

    @patch.object(
        docker_utils_mod,
        "_container_running",
        side_effect=subprocess.CalledProcessError(
            1, "docker", output="out", stderr="err"
        ),
    )
    @patch.object(docker_utils_mod, "log_error")
    @patch.object(docker_utils_mod, "log")
    def test_called_process_error_returns_false(
        self, mock_log, mock_log_error, mock_running
    ):
        """CalledProcessError → returns False + log_error."""
        cfg = _make_cfg()
        result = docker_utils_mod.ensure_qdrant_running(cfg)
        assert result is False
        mock_log_error.assert_called_once()
        assert "Docker command failed" in mock_log_error.call_args[0][0]

    # -- FileNotFoundError (Docker not installed) --

    @patch.object(
        docker_utils_mod,
        "_container_running",
        side_effect=FileNotFoundError("docker not found"),
    )
    @patch.object(docker_utils_mod, "log_error")
    @patch.object(docker_utils_mod, "log")
    def test_file_not_found_returns_false(self, mock_log, mock_log_error, mock_running):
        """FileNotFoundError (Docker missing) → returns False + log_error."""
        cfg = _make_cfg()
        result = docker_utils_mod.ensure_qdrant_running(cfg)
        assert result is False
        mock_log_error.assert_called_once()
        assert "not installed" in mock_log_error.call_args[0][0]

    # -- TimeoutExpired --

    @patch.object(
        docker_utils_mod,
        "_container_running",
        side_effect=subprocess.TimeoutExpired("docker", 60),
    )
    @patch.object(docker_utils_mod, "log_error")
    @patch.object(docker_utils_mod, "log")
    def test_timeout_expired_returns_false(
        self, mock_log, mock_log_error, mock_running
    ):
        """TimeoutExpired → returns False + log_error."""
        cfg = _make_cfg()
        result = docker_utils_mod.ensure_qdrant_running(cfg)
        assert result is False
        mock_log_error.assert_called_once()
        assert "timed out" in mock_log_error.call_args[0][0]

    # -- stderr_prefix --

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=True)
    @patch.object(docker_utils_mod, "log")
    def test_stderr_prefix_in_log_messages(self, mock_log, mock_running, mock_health):
        """stderr_prefix is prepended to log messages."""
        cfg = _make_cfg()
        docker_utils_mod.ensure_qdrant_running(cfg, stderr_prefix="[MCP]")
        log_calls = [c[0][0] for c in mock_log.call_args_list]
        # All log calls should start with "[MCP] "
        for msg in log_calls:
            assert msg.startswith("[MCP] "), f"Missing prefix in: {msg!r}"

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=True)
    @patch.object(docker_utils_mod, "log")
    def test_no_prefix_when_none(self, mock_log, mock_running, mock_health):
        """No prefix when stderr_prefix is None."""
        cfg = _make_cfg()
        docker_utils_mod.ensure_qdrant_running(cfg, stderr_prefix=None)
        log_calls = [c[0][0] for c in mock_log.call_args_list]
        for msg in log_calls:
            assert not msg.startswith("["), f"Unexpected prefix in: {msg!r}"

    @patch.object(
        docker_utils_mod,
        "_container_running",
        side_effect=FileNotFoundError("nope"),
    )
    @patch.object(docker_utils_mod, "log_error")
    @patch.object(docker_utils_mod, "log")
    def test_stderr_prefix_in_error_messages(
        self, mock_log, mock_log_error, mock_running
    ):
        """stderr_prefix appears in error log messages too."""
        cfg = _make_cfg()
        docker_utils_mod.ensure_qdrant_running(cfg, stderr_prefix="[IDX]")
        err_msg = mock_log_error.call_args[0][0]
        assert err_msg.startswith("[IDX] ")

    # -- Default config values --

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=True)
    @patch.object(docker_utils_mod, "log")
    def test_default_host_and_port(self, mock_log, mock_running, mock_health):
        """Uses defaults: host=localhost, port=6333 when not in config."""
        cfg = types.ModuleType("bare_cfg")
        cfg.QDRANT_MODE = "local"
        docker_utils_mod.ensure_qdrant_running(cfg)
        mock_health.assert_called_once_with("localhost", 6333)

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=True)
    @patch.object(docker_utils_mod, "log")
    def test_custom_host_and_port(self, mock_log, mock_running, mock_health):
        """Uses custom host/port from config."""
        cfg = _make_cfg(QDRANT_HOST="192.168.1.10", QDRANT_PORT=6973)
        docker_utils_mod.ensure_qdrant_running(cfg)
        mock_health.assert_called_once_with("192.168.1.10", 6973)

    # -- Mode defaults to 'local' --

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_running", return_value=True)
    @patch.object(docker_utils_mod, "log")
    def test_mode_defaults_to_local(self, mock_log, mock_running, mock_health):
        """When QDRANT_MODE is absent, defaults to 'local' (runs Docker path)."""
        cfg = types.ModuleType("no_mode_cfg")
        result = docker_utils_mod.ensure_qdrant_running(cfg)
        assert result is True
        # Should have entered the Docker path (called _container_running)
        mock_running.assert_called_once()

    # -- Health check receives correct host/port for create path --

    @patch.object(docker_utils_mod, "_wait_for_health", return_value=True)
    @patch.object(docker_utils_mod, "_container_exists", return_value=False)
    @patch.object(docker_utils_mod, "_container_running", return_value=False)
    @patch.object(docker_utils_mod, "_create_container")
    @patch("pathlib.Path.mkdir")
    @patch.object(docker_utils_mod, "log")
    def test_health_check_uses_config_host_port(
        self, mock_log, mock_mkdir, mock_create, mock_running, mock_exists, mock_health
    ):
        """Health check uses host/port from config after container creation."""
        cfg = _make_cfg(QDRANT_HOST="10.0.0.1", QDRANT_PORT=7777)
        docker_utils_mod.ensure_qdrant_running(cfg)
        mock_health.assert_called_once_with("10.0.0.1", 7777)
