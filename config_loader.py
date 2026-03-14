import os
import sys
import types
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

from shared.log import log_warn


def get_config(config_path: str = None, config_name: str = None) -> types.ModuleType:
    """Load config with optional override.

    Args:
        config_path: Full path to config file (e.g., "./self-index/config.py")
        config_name: Just the name, assumes "./{name}/config.py" (e.g., "self-index")

    Priority: config_path > config_name > env var RAG_CONFIG
    """
    base_config = __import__("config")

    override_path = None
    if config_path:
        p = Path(config_path)
        if p.suffix == ".py":
            # Explicit .py file path — use directly
            override_path = p
        elif p.is_dir():
            # Directory — look for config.py inside it
            override_path = p / "config.py"
        else:
            # Name without extension (e.g. "self-index", "config_informica")
            # Try as directory first, then as root-level .py file
            dir_path = p / "config.py"
            file_path = p.with_suffix(".py")
            if dir_path.exists():
                override_path = dir_path
            elif file_path.exists():
                override_path = file_path
            else:
                override_path = dir_path  # Fall through to "not found" below
    elif config_name:
        p = Path(config_name)
        dir_path = p / "config.py"
        file_path = p.with_suffix(".py")
        if dir_path.exists():
            override_path = dir_path
        elif file_path.exists():
            override_path = file_path
        else:
            override_path = dir_path  # Fall through to "not found" below
    elif os.getenv("RAG_CONFIG"):
        env_val = os.getenv("RAG_CONFIG", "")
        env_p = Path(env_val)
        dir_path = env_p / "config.py"
        file_path = env_p.with_suffix(".py")
        if dir_path.exists():
            override_path = dir_path
        elif file_path.exists():
            override_path = file_path
        else:
            override_path = dir_path

    if override_path and override_path.exists():
        spec = spec_from_file_location("config_override", override_path)
        if spec is None or spec.loader is None:
            log_warn(f"[config_loader] Could not load config from {override_path}")
            return base_config

        override_mod = module_from_spec(spec)
        try:
            spec.loader.exec_module(override_mod)
        except Exception as e:
            log_warn(f"[config_loader] Error loading {override_path}: {e}")
            return base_config

        merged = types.ModuleType("config")
        merged.__dict__.update(base_config.__dict__)
        merged.__dict__.update(override_mod.__dict__)

        # Auto-set BASE_PATH based on override config location if not explicitly defined
        if "BASE_PATH" not in override_mod.__dict__:
            config_dir = override_path.parent.resolve()
            merged.__dict__["BASE_PATH"] = str(config_dir / "qdrant")

        # Rebind functions so they see the merged module's globals
        # (e.g. get_index_path() needs to read the overridden BASE_PATH)
        for key, value in list(merged.__dict__.items()):
            if isinstance(value, types.FunctionType):
                merged.__dict__[key] = types.FunctionType(
                    value.__code__,
                    merged.__dict__,
                    value.__name__,
                    value.__defaults__,
                    value.__closure__,
                )

        _validate_config(merged, override_path)
        return merged

    # No override - return base config with BASE_PATH auto-set to {config.py_dir}/qdrant
    if hasattr(base_config, "__file__") and base_config.__file__:
        base_dir = Path(base_config.__file__).parent.resolve()
        base_config.BASE_PATH = str(base_dir / "qdrant")
    _validate_config(base_config, None)
    return base_config


def _validate_config(cfg: types.ModuleType, source_path) -> None:
    """Validate the merged config for removed/renamed settings.

    Raises RuntimeError for fatal configuration errors.
    """
    # ── QDRANT_USE_DOCKER removed (replaced by QDRANT_MODE) ─────
    if hasattr(cfg, "QDRANT_USE_DOCKER"):
        source = f" (in {source_path})" if source_path else ""
        raise RuntimeError(
            f"QDRANT_USE_DOCKER has been removed{source}. "
            f"Replace with QDRANT_MODE = 'local' (Docker container) "
            f"or QDRANT_MODE = 'remote' (remote server). "
            f"See config.py for documentation."
        )

    # ── QDRANT_MODE must be valid ────────────────────────────────
    mode = getattr(cfg, "QDRANT_MODE", None)
    if mode not in ("local", "remote"):
        raise RuntimeError(
            f"QDRANT_MODE must be 'local' or 'remote', got {mode!r}. "
            f"See config.py for documentation."
        )
