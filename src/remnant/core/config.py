"""
remnant.core.config
-------------------
Handles loading and saving user configuration from
~/.config/remnant/config.toml
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

# Default locations following XDG Base Directory spec
CONFIG_DIR = Path.home() / ".config" / "remnant"
DATA_DIR = Path.home() / ".local" / "share" / "remnant"
CACHE_DIR = Path.home() / ".cache" / "remnant"

CONFIG_FILE = CONFIG_DIR / "config.toml"
DATABASE_FILE = DATA_DIR / "remnant.db"

DEFAULT_CONFIG: dict[str, Any] = {
    "core": {
        "editor": "nano",
        "color": True,
        "format": "human",
    },
    "drift": {
        "watch_paths": ["~/.config", "~/.bashrc", "~/.zshrc"],
        "package_manager": "auto",
    },
    "map": {
        "ignore": ["node_modules", ".git", "__pycache__", ".venv", "dist", "build"],
        "max_depth": 10,
    },
    "context": {
        "activity_window_days": 7,
    },
}


def ensure_dirs() -> None:
    """Create all required directories if they don't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load user config, falling back to defaults for missing keys."""
    ensure_dirs()

    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "rb") as f:
        user_config = tomllib.load(f)

    return _deep_merge(DEFAULT_CONFIG.copy(), user_config)


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def get(key_path: str, default: Any = None) -> Any:
    """
    Get a config value using dot notation.
    Example: get("core.color") -> True
    """
    config = load_config()
    keys = key_path.split(".")
    value = config

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value
