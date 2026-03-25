"""
Tests for device validation in shared/embedding.py.

Tests cover:
    - DeviceCheckResult: dataclass defaults, ok/error/warning semantics
    - _check_cuda_available(): PyTorch CUDA detection, ImportError fallback
    - _check_cuda_device_name(): GPU name lookup, unavailable/ImportError fallback
    - _check_openvino_devices(): OpenVINO device enumeration, ImportError fallback
    - validate_device_config(): All branches:
        - OpenVINO path: not installed, GPU requested but missing, CUDA available warning
        - PyTorch path: CUDA requested but unavailable, CPU with CUDA available, CPU with OV GPU
        - Edge cases: missing config attributes, empty device lists, mixed hardware
"""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from shared.embedding import (
    DeviceCheckResult,
    _check_cuda_available,
    _check_cuda_device_name,
    _check_openvino_devices,
    validate_device_config,
)


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _cfg(**overrides) -> SimpleNamespace:
    """Create a minimal config namespace for testing."""
    defaults = {
        "USE_OPENVINO_EMBEDDING": False,
        "OPENVINO_EMBED_DEVICE": "GPU",
        "INDEX_EMBED_DEVICE": "cpu",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# Patch targets — these are the private helpers inside shared.embedding
_PATCH_CUDA = "shared.embedding._check_cuda_available"
_PATCH_CUDA_NAME = "shared.embedding._check_cuda_device_name"
_PATCH_OV = "shared.embedding._check_openvino_devices"


# ────────────────────────────────────────────────
# DeviceCheckResult
# ────────────────────────────────────────────────


class TestDeviceCheckResult:
    """Tests for the DeviceCheckResult dataclass."""

    def test_defaults(self):
        """Default result is ok=True with no errors or warnings."""
        r = DeviceCheckResult()
        assert r.ok is True
        assert r.errors == []
        assert r.warnings == []

    def test_with_errors(self):
        """Result with errors should be constructable."""
        r = DeviceCheckResult(ok=False, errors=["e1", "e2"])
        assert r.ok is False
        assert len(r.errors) == 2
        assert r.warnings == []

    def test_with_warnings(self):
        """Result with warnings but ok=True."""
        r = DeviceCheckResult(ok=True, warnings=["w1"])
        assert r.ok is True
        assert r.warnings == ["w1"]
        assert r.errors == []

    def test_independent_instances(self):
        """Each instance should have independent mutable lists."""
        r1 = DeviceCheckResult()
        r2 = DeviceCheckResult()
        r1.errors.append("e")
        assert r2.errors == []


# ────────────────────────────────────────────────
# _check_cuda_available
# ────────────────────────────────────────────────


class TestCheckCudaAvailable:
    """Tests for _check_cuda_available()."""

    def test_cuda_available(self):
        """Returns True when torch.cuda.is_available() is True."""
        with patch("shared.embedding.torch", create=True) as mock_torch:
            # We need to patch the import inside the function
            pass

        # The function does `import torch` internally, so we patch at the builtins level
        import types

        mock_torch = types.SimpleNamespace(
            cuda=types.SimpleNamespace(is_available=lambda: True)
        )
        with patch.dict("sys.modules", {"torch": mock_torch}):
            assert _check_cuda_available() is True

    def test_cuda_not_available(self):
        """Returns False when torch.cuda.is_available() is False."""
        import types

        mock_torch = types.SimpleNamespace(
            cuda=types.SimpleNamespace(is_available=lambda: False)
        )
        with patch.dict("sys.modules", {"torch": mock_torch}):
            assert _check_cuda_available() is False

    def test_torch_not_installed(self):
        """Returns False when torch is not importable."""
        import sys

        # Remove torch from modules if present, and block re-import
        with patch.dict("sys.modules", {"torch": None}):
            assert _check_cuda_available() is False

    def test_torch_import_error(self):
        """Returns False when importing torch raises ImportError."""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "torch":
                raise ImportError("No module named 'torch'")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            assert _check_cuda_available() is False


# ────────────────────────────────────────────────
# _check_cuda_device_name
# ────────────────────────────────────────────────


class TestCheckCudaDeviceName:
    """Tests for _check_cuda_device_name()."""

    def test_returns_name_when_available(self):
        """Returns GPU name string when CUDA is available."""
        import types

        mock_cuda = types.SimpleNamespace(
            is_available=lambda: True,
            device_count=lambda: 1,
            get_device_name=lambda idx: "NVIDIA GeForce RTX 3090",
        )
        mock_torch = types.SimpleNamespace(cuda=mock_cuda)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            assert _check_cuda_device_name() == "NVIDIA GeForce RTX 3090"

    def test_returns_none_when_not_available(self):
        """Returns None when CUDA is not available."""
        import types

        mock_cuda = types.SimpleNamespace(is_available=lambda: False)
        mock_torch = types.SimpleNamespace(cuda=mock_cuda)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            assert _check_cuda_device_name() is None

    def test_returns_none_when_torch_missing(self):
        """Returns None when torch is not importable."""
        with patch.dict("sys.modules", {"torch": None}):
            assert _check_cuda_device_name() is None

    def test_returns_none_on_runtime_error(self):
        """Returns None when get_device_name raises an exception."""
        import types

        def bad_name(idx):
            raise RuntimeError("CUDA error")

        mock_cuda = types.SimpleNamespace(
            is_available=lambda: True,
            get_device_name=bad_name,
        )
        mock_torch = types.SimpleNamespace(cuda=mock_cuda)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            assert _check_cuda_device_name() is None


# ────────────────────────────────────────────────
# _check_openvino_devices
# ────────────────────────────────────────────────


class TestCheckOpenvinoDevices:
    """Tests for _check_openvino_devices()."""

    def test_returns_devices(self):
        """Returns device list when OpenVINO is installed."""
        import types

        class MockCore:
            @property
            def available_devices(self):
                return ["CPU", "GPU"]

        mock_ov = types.ModuleType("openvino")
        mock_ov.Core = MockCore
        with patch.dict("sys.modules", {"openvino": mock_ov}):
            result = _check_openvino_devices()
            assert "CPU" in result
            assert "GPU" in result

    def test_returns_cpu_only(self):
        """Returns only CPU when no GPU is available."""
        import types

        class MockCore:
            @property
            def available_devices(self):
                return ["CPU"]

        mock_ov = types.ModuleType("openvino")
        mock_ov.Core = MockCore
        with patch.dict("sys.modules", {"openvino": mock_ov}):
            result = _check_openvino_devices()
            assert result == ["CPU"]

    def test_returns_empty_when_not_installed(self):
        """Returns empty list when openvino is not importable."""
        with patch.dict("sys.modules", {"openvino": None}):
            assert _check_openvino_devices() == []

    def test_returns_empty_on_exception(self):
        """Returns empty list when OpenVINO Core() raises."""
        import types

        class BadCore:
            def __init__(self):
                raise RuntimeError("OpenVINO init failed")

        mock_ov = types.ModuleType("openvino")
        mock_ov.Core = BadCore
        with patch.dict("sys.modules", {"openvino": mock_ov}):
            assert _check_openvino_devices() == []


# ────────────────────────────────────────────────
# validate_device_config — OpenVINO path
# ────────────────────────────────────────────────


class TestValidateDeviceConfigOpenVINO:
    """Tests for validate_device_config() when USE_OPENVINO_EMBEDDING=True."""

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_openvino_not_installed(self, _cuda, _name, _ov):
        """Error when OpenVINO is enabled but not installed."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True)
        result = validate_device_config(cfg)
        assert result.ok is False
        assert len(result.errors) == 1
        assert (
            "not installed" in result.errors[0].lower()
            or "OpenVINO" in result.errors[0]
        )

    @patch(_PATCH_OV, return_value=["CPU"])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_openvino_gpu_requested_but_only_cpu(self, _cuda, _name, _ov):
        """Error when GPU is requested but only CPU is available in OpenVINO."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True, OPENVINO_EMBED_DEVICE="GPU")
        result = validate_device_config(cfg)
        assert result.ok is False
        assert len(result.errors) == 1
        assert "GPU" in result.errors[0]
        assert "CPU" in result.errors[0]

    @patch(_PATCH_OV, return_value=["CPU", "GPU"])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_openvino_gpu_available_no_warnings(self, _cuda, _name, _ov):
        """No errors or warnings when OpenVINO GPU is correctly configured."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True, OPENVINO_EMBED_DEVICE="GPU")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []
        assert result.warnings == []

    @patch(_PATCH_OV, return_value=["CPU", "GPU"])
    @patch(_PATCH_CUDA_NAME, return_value="NVIDIA GeForce RTX 3090")
    @patch(_PATCH_CUDA, return_value=True)
    def test_openvino_with_cuda_available_warns(self, _cuda, _name, _ov):
        """Warning when OpenVINO is used but CUDA is also available."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True, OPENVINO_EMBED_DEVICE="GPU")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []
        assert len(result.warnings) == 1
        assert "NVIDIA" in result.warnings[0]
        assert "CUDA" in result.warnings[0]

    @patch(_PATCH_OV, return_value=["CPU"])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_openvino_cpu_device_ok(self, _cuda, _name, _ov):
        """No error when OpenVINO CPU backend is requested and available."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True, OPENVINO_EMBED_DEVICE="CPU")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []

    @patch(_PATCH_OV, return_value=["CPU", "GPU"])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_openvino_device_case_insensitive(self, _cuda, _name, _ov):
        """Device string is uppercased — 'gpu' should work like 'GPU'."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True, OPENVINO_EMBED_DEVICE="gpu")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []


# ────────────────────────────────────────────────
# validate_device_config — PyTorch (CUDA/CPU) path
# ────────────────────────────────────────────────


class TestValidateDeviceConfigPyTorch:
    """Tests for validate_device_config() when USE_OPENVINO_EMBEDDING=False."""

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_cuda_requested_but_not_available(self, _cuda, _name, _ov):
        """Error when CUDA device is requested but not available."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cuda")
        result = validate_device_config(cfg)
        assert result.ok is False
        assert len(result.errors) == 1
        assert "CUDA" in result.errors[0]
        assert (
            "not available" in result.errors[0].lower()
            or "not available" in result.errors[0]
        )

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_cuda_colon_device_requested_but_not_available(self, _cuda, _name, _ov):
        """Error when 'cuda:0' is requested but CUDA not available."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cuda:0")
        result = validate_device_config(cfg)
        assert result.ok is False
        assert len(result.errors) == 1

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value="NVIDIA GeForce RTX 3090")
    @patch(_PATCH_CUDA, return_value=True)
    def test_cuda_requested_and_available(self, _cuda, _name, _ov):
        """No error when CUDA is requested and available."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cuda")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []
        assert result.warnings == []

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value="NVIDIA GeForce RTX 3090")
    @patch(_PATCH_CUDA, return_value=True)
    def test_cpu_with_cuda_available_warns(self, _cuda, _name, _ov):
        """Warning when CPU is used but CUDA GPU is available."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cpu")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []
        assert len(result.warnings) == 1
        assert "NVIDIA" in result.warnings[0]
        assert "auto" in result.warnings[0].lower()

    @patch(_PATCH_OV, return_value=["CPU", "GPU"])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_cpu_with_openvino_gpu_warns(self, _cuda, _name, _ov):
        """Warning when CPU is used but Intel GPU is available via OpenVINO."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cpu")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []
        assert len(result.warnings) == 1
        assert "Intel GPU" in result.warnings[0]
        assert "OpenVINO" in result.warnings[0]

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_cpu_no_gpu_no_warnings(self, _cuda, _name, _ov):
        """No warnings when CPU is used and no GPU is available at all."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cpu")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []
        assert result.warnings == []

    @patch(_PATCH_OV, return_value=["CPU"])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_cpu_with_openvino_cpu_only_no_warning(self, _cuda, _name, _ov):
        """No warning when only OpenVINO CPU is available (no GPU benefit)."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cpu")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.warnings == []


# ────────────────────────────────────────────────
# validate_device_config — Edge cases
# ────────────────────────────────────────────────


class TestValidateDeviceConfigEdgeCases:
    """Edge cases and missing config attributes."""

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_missing_use_openvino_attr(self, _cuda, _name, _ov):
        """Config without USE_OPENVINO_EMBEDDING defaults to False (PyTorch path)."""
        cfg = SimpleNamespace(INDEX_EMBED_DEVICE="cpu")
        result = validate_device_config(cfg)
        assert result.ok is True

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_missing_openvino_device_attr(self, _cuda, _name, _ov):
        """Config without OPENVINO_EMBED_DEVICE defaults to 'GPU'."""
        cfg = SimpleNamespace(USE_OPENVINO_EMBEDDING=True)
        # No OV devices available — should error about OV not installed
        result = validate_device_config(cfg)
        assert result.ok is False

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_missing_index_device_attr(self, _cuda, _name, _ov):
        """Config without INDEX_EMBED_DEVICE defaults to 'cpu'."""
        cfg = SimpleNamespace(USE_OPENVINO_EMBEDDING=False)
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_empty_config(self, _cuda, _name, _ov):
        """Bare config with no relevant attributes uses all defaults — CPU, no OV."""
        cfg = SimpleNamespace()
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []
        assert result.warnings == []

    @patch(_PATCH_OV, return_value=["CPU", "GPU"])
    @patch(_PATCH_CUDA_NAME, return_value="NVIDIA GeForce RTX 3090")
    @patch(_PATCH_CUDA, return_value=True)
    def test_openvino_enabled_cuda_available_both_gpus(self, _cuda, _name, _ov):
        """System with both NVIDIA and Intel GPUs, OpenVINO enabled — warn about CUDA."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True, OPENVINO_EMBED_DEVICE="GPU")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert len(result.warnings) == 1
        assert "NVIDIA" in result.warnings[0]

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_openvino_not_installed_returns_early(self, _cuda, _name, _ov):
        """When OpenVINO is enabled but not installed, only one error, no warnings."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True)
        result = validate_device_config(cfg)
        assert result.ok is False
        assert len(result.errors) == 1
        assert result.warnings == []

    @patch(_PATCH_OV, return_value=["CPU"])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_openvino_gpu_missing_returns_early(self, _cuda, _name, _ov):
        """When GPU is requested but missing, only one error, no warnings."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True, OPENVINO_EMBED_DEVICE="GPU")
        result = validate_device_config(cfg)
        assert result.ok is False
        assert len(result.errors) == 1
        assert result.warnings == []

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_error_messages_contain_actionable_advice(self, _cuda, _name, _ov):
        """Error messages should contain installation/fix instructions."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cuda")
        result = validate_device_config(cfg)
        assert result.ok is False
        error = result.errors[0]
        # Should mention at least one fix option
        assert (
            "INDEX_EMBED_DEVICE" in error
            or "cpu" in error.lower()
            or "OpenVINO" in error
        )

    @patch(_PATCH_OV, return_value=[])
    @patch(_PATCH_CUDA_NAME, return_value=None)
    @patch(_PATCH_CUDA, return_value=False)
    def test_openvino_error_mentions_requirements(self, _cuda, _name, _ov):
        """OpenVINO not-installed error should mention requirements file."""
        cfg = _cfg(USE_OPENVINO_EMBEDDING=True)
        result = validate_device_config(cfg)
        assert "requirements_openvino" in result.errors[0]

    @patch(_PATCH_OV, return_value=["CPU", "GPU"])
    @patch(_PATCH_CUDA_NAME, return_value="NVIDIA GeForce RTX 3090")
    @patch(_PATCH_CUDA, return_value=True)
    def test_cuda_device_with_cuda_available_no_ov(self, _cuda, _name, _ov):
        """CUDA requested, CUDA available, OV not relevant — clean pass."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cuda")
        result = validate_device_config(cfg)
        assert result.ok is True
        assert result.errors == []
        assert result.warnings == []

    @patch(_PATCH_OV, return_value=["CPU", "GPU"])
    @patch(_PATCH_CUDA_NAME, return_value="NVIDIA GeForce RTX 3090")
    @patch(_PATCH_CUDA, return_value=True)
    def test_cpu_with_both_gpus_prefers_cuda_warning(self, _cuda, _name, _ov):
        """CPU with both NVIDIA and Intel GPUs — should warn about CUDA (not OV)."""
        cfg = _cfg(INDEX_EMBED_DEVICE="cpu")
        result = validate_device_config(cfg)
        assert result.ok is True
        # CUDA warning takes priority (first branch hit in the elif chain)
        assert len(result.warnings) == 1
        assert "NVIDIA" in result.warnings[0]
