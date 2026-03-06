import os
import sys
import types
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec


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
        override_path = Path(config_path)
    elif config_name:
        override_path = Path(config_name) / "config.py"
    elif os.getenv("RAG_CONFIG"):
        override_path = Path(os.getenv("RAG_CONFIG")) / "config.py"

    if override_path and override_path.exists():
        spec = spec_from_file_location("config_override", override_path)
        if spec is None or spec.loader is None:
            print(f"[config_loader] Could not load config from {override_path}")
            return base_config

        override_mod = module_from_spec(spec)
        try:
            spec.loader.exec_module(override_mod)
        except Exception as e:
            print(f"[config_loader] Error loading {override_path}: {e}")
            return base_config

        merged = types.ModuleType("config")
        merged.__dict__.update(base_config.__dict__)
        merged.__dict__.update(override_mod.__dict__)

        return merged

    return base_config
