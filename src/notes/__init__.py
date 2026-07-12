"""Notes tracker — local-first CLI/TUI note management."""

from notes.models import Note, normalize_path, normalize_tags

__all__ = ["Note", "normalize_path", "normalize_tags"]
