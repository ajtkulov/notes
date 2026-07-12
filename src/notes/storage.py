"""Filesystem persistence for notes."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import frontmatter

from notes.models import Note, normalize_path, normalize_tags, parse_note_id


class NoteNotFoundError(FileNotFoundError):
    """Raised when a note id does not exist on disk."""


class NoteStore:
    """CRUD operations for notes stored as markdown files."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _file_path(self, note_id: str) -> Path:
        path_part, filename = parse_note_id(note_id)
        if path_part:
            return self.root / path_part / f"{filename}.md"
        return self.root / f"{filename}.md"

    def _note_id_from_file(self, file_path: Path) -> str:
        relative = file_path.relative_to(self.root)
        path_part = normalize_path(str(relative.parent)) if relative.parent != Path(".") else ""
        filename = relative.stem
        if path_part:
            return f"{path_part}/{filename}"
        return filename

    def _parse_datetime(self, value: object, fallback: datetime | None = None) -> datetime:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value
        if isinstance(value, str) and value:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed
        return fallback or datetime.now(timezone.utc)

    def save(self, note: Note) -> Note:
        """Persist a note to disk."""
        file_path = self._file_path(note.id)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "title": note.title,
            "tags": sorted(note.tags),
            "created": note.created_at.isoformat(),
            "updated": note.updated_at.isoformat(),
        }
        post = frontmatter.Post(note.body, **metadata)
        file_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        return note

    def load(self, note_id: str) -> Note:
        """Load a note from disk by id."""
        file_path = self._file_path(note_id)
        if not file_path.is_file():
            raise NoteNotFoundError(f"Note not found: {note_id}")
        return self._load_file(file_path)

    def _load_file(self, file_path: Path) -> Note:
        post = frontmatter.loads(file_path.read_text(encoding="utf-8"))
        note_id = self._note_id_from_file(file_path)
        path_part, _ = parse_note_id(note_id)
        tags_raw = post.metadata.get("tags") or []
        if isinstance(tags_raw, str):
            tags_raw = [tags_raw]
        created = self._parse_datetime(post.metadata.get("created"))
        updated = self._parse_datetime(post.metadata.get("updated"), created)
        return Note(
            id=note_id,
            title=str(post.metadata.get("title") or file_path.stem),
            body=post.content,
            path=path_part,
            tags=normalize_tags(tags_raw),
            created_at=created,
            updated_at=updated,
        )

    def delete(self, note_id: str) -> None:
        """Delete a note and prune empty parent directories."""
        file_path = self._file_path(note_id)
        if not file_path.is_file():
            raise NoteNotFoundError(f"Note not found: {note_id}")
        file_path.unlink()
        self._prune_empty_dirs(file_path.parent)

    def move(self, note_id: str, new_path: str) -> Note:
        """Move a note to a new directory path."""
        note = self.load(note_id)
        updated = note.with_updates(path=new_path)
        new_file = self._file_path(updated.id)
        old_file = self._file_path(note_id)
        new_file.parent.mkdir(parents=True, exist_ok=True)
        old_file.rename(new_file)
        self.save(updated)
        self._prune_empty_dirs(old_file.parent)
        return updated

    def update(self, note: Note) -> Note:
        """Update an existing note, handling path changes."""
        existing = self.load(note.id)
        if note.path != existing.path:
            return self.move(note.id, note.path)
        return self.save(note)

    def list_notes(
        self,
        *,
        path: str | None = None,
        recursive: bool = False,
        tag: str | None = None,
    ) -> list[Note]:
        """List notes with optional path scope and tag filter."""
        notes = [self._load_file(file_path) for file_path in sorted(self.root.rglob("*.md"))]
        normalized_path = normalize_path(path) if path is not None else None
        if normalized_path is not None:
            if recursive:
                prefix = normalized_path
                notes = [
                    note
                    for note in notes
                    if note.path == prefix or note.path.startswith(f"{prefix}/")
                ]
            else:
                notes = [note for note in notes if note.path == normalized_path]
        if tag:
            normalized_tag = normalize_tags([tag]).pop()
            notes = [note for note in notes if normalized_tag in note.tags]
        notes.sort(key=lambda note: note.updated_at, reverse=True)
        return notes

    def all_tags(self) -> set[str]:
        """Return all tags used across notes."""
        tags: set[str] = set()
        for note in self.list_notes():
            tags.update(note.tags)
        return tags

    def _prune_empty_dirs(self, directory: Path) -> None:
        current = directory.resolve()
        root = self.root.resolve()
        while current != root and current.is_relative_to(root):
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent
