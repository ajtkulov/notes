"""Configuration for notes storage location."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".notes"
DEFAULT_NOTES_DIR = DEFAULT_CONFIG_DIR / "notes"
CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"
ENV_NOTES_DIR = "NOTES_DIR"


def _read_config_notes_dir() -> Path | None:
    if not CONFIG_FILE.exists():
        return None
    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("notes_dir"):
            _, _, value = stripped.partition("=")
            value = value.strip().strip('"').strip("'")
            if value:
                return Path(value).expanduser()
    return None


def resolve_notes_dir(override: Path | str | None = None) -> Path:
    """Resolve the notes directory from override, env, config, or default."""
    if override is not None:
        return Path(override).expanduser().resolve()

    env_value = os.environ.get(ENV_NOTES_DIR)
    if env_value:
        return Path(env_value).expanduser().resolve()

    config_value = _read_config_notes_dir()
    if config_value is not None:
        return config_value.expanduser().resolve()

    return DEFAULT_NOTES_DIR.expanduser().resolve()


def ensure_notes_dir(notes_dir: Path | None = None) -> Path:
    """Return the notes directory, creating it if missing."""
    directory = notes_dir or resolve_notes_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return directory
