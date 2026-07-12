"""Tests for configuration."""

import os
from pathlib import Path

from notes import config


def test_resolve_notes_dir_from_env(monkeypatch, tmp_path: Path):
    monkeypatch.setenv(config.ENV_NOTES_DIR, str(tmp_path / "env-notes"))
    assert config.resolve_notes_dir() == (tmp_path / "env-notes").resolve()


def test_resolve_notes_dir_from_config(monkeypatch, tmp_path: Path):
    monkeypatch.delenv(config.ENV_NOTES_DIR, raising=False)
    config_dir = tmp_path / ".notes"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    monkeypatch.setattr(config, "CONFIG_FILE", config_file)
    config_file.write_text('notes_dir = "/tmp/config-notes"\n', encoding="utf-8")
    assert config.resolve_notes_dir() == Path("/tmp/config-notes").resolve()


def test_ensure_notes_dir_creates_directory(tmp_path: Path):
    target = tmp_path / "notes"
    created = config.ensure_notes_dir(target)
    assert created == target
    assert target.is_dir()
