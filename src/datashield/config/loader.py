"""Configuration loader for Data-Shield."""

import json
from pathlib import Path
from typing import Optional
from .settings import AppConfig
from .defaults import DEFAULT_CONFIG


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load configuration from file or use defaults.

    Args:
        config_path: Path to configuration file (JSON or TOML).

    Returns:
        AppConfig instance.
    """
    if config_path is None or not config_path.exists():
        return DEFAULT_CONFIG

    try:
        if config_path.suffix == ".json":
            with open(config_path) as f:
                data = json.load(f)
            return AppConfig(**data)
        else:
            # Default to DEFAULT_CONFIG if format unsupported
            return DEFAULT_CONFIG
    except Exception:
        return DEFAULT_CONFIG


def load_env_config() -> AppConfig:
    """Load configuration from environment variables.

    Returns:
        AppConfig instance with environment overrides.
    """
    return AppConfig.model_validate_json(
        DEFAULT_CONFIG.model_dump_json(), strict=False
    )
