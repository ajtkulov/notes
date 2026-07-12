"""Note domain model."""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone

ROOT_PATH = ""


def normalize_path(path: str) -> str:
    """Normalize a note directory path relative to the notes root."""
    cleaned = path.strip().strip("/")
    if cleaned in ("", "."):
        return ROOT_PATH
    segments = [segment.strip() for segment in cleaned.split("/") if segment.strip()]
    if not segments:
        return ROOT_PATH
    for segment in segments:
        if segment in (".", ".."):
            raise ValueError(f"Invalid path segment: {segment!r}")
    return "/".join(segments)


def normalize_tags(tags: set[str] | list[str] | tuple[str, ...] | None) -> set[str]:
    """Normalize tags to a lowercase, deduplicated set."""
    if not tags:
        return set()
    return {tag.strip().lower() for tag in tags if tag.strip()}


def slugify(title: str) -> str:
    """Convert a title into a filesystem-safe slug."""
    slug = title.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    return slug or "note"


def generate_short_id(length: int = 4) -> str:
    """Generate a short random hex id for note filenames."""
    byte_length = max(1, (length + 1) // 2)
    return secrets.token_hex(byte_length)[:length]


def build_note_id(path: str, slug: str, short_id: str) -> str:
    """Build a note id from path, slug, and short id."""
    filename = f"{slug}-{short_id}"
    normalized_path = normalize_path(path)
    if normalized_path == ROOT_PATH:
        return filename
    return f"{normalized_path}/{filename}"


def parse_note_id(note_id: str) -> tuple[str, str]:
    """Split a note id into (path, filename)."""
    cleaned = note_id.strip().strip("/")
    if not cleaned:
        raise ValueError("Note id cannot be empty")
    if "/" not in cleaned:
        return ROOT_PATH, cleaned
    path_part, filename = cleaned.rsplit("/", 1)
    return normalize_path(path_part), filename


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Note:
    """A note stored in the filesystem tree."""

    id: str
    title: str
    body: str
    path: str
    tags: set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        self.path = normalize_path(self.path)
        self.tags = normalize_tags(self.tags)
        path_from_id, _ = parse_note_id(self.id)
        if path_from_id != self.path:
            raise ValueError(
                f"Note id path {path_from_id!r} does not match note path {self.path!r}"
            )

    @classmethod
    def create(
        cls,
        title: str,
        body: str,
        *,
        path: str = ROOT_PATH,
        tags: set[str] | list[str] | tuple[str, ...] | None = None,
        short_id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> Note:
        """Create a new note with generated id and timestamps."""
        normalized_path = normalize_path(path)
        normalized_tags = normalize_tags(tags)
        slug = slugify(title)
        note_short_id = short_id or generate_short_id()
        note_id = build_note_id(normalized_path, slug, note_short_id)
        timestamp = created_at or _utc_now()
        updated = updated_at or timestamp
        return cls(
            id=note_id,
            title=title,
            body=body,
            path=normalized_path,
            tags=normalized_tags,
            created_at=timestamp,
            updated_at=updated,
        )

    def with_updates(
        self,
        *,
        title: str | None = None,
        body: str | None = None,
        path: str | None = None,
        tags: set[str] | list[str] | tuple[str, ...] | None = None,
        updated_at: datetime | None = None,
    ) -> Note:
        """Return a copy with updated fields and refreshed updated_at."""
        new_path = normalize_path(path) if path is not None else self.path
        new_title = title if title is not None else self.title
        new_body = body if body is not None else self.body
        new_tags = normalize_tags(tags) if tags is not None else set(self.tags)

        if path is not None and new_path != self.path:
            _, filename = parse_note_id(self.id)
            new_id = filename if new_path == ROOT_PATH else f"{new_path}/{filename}"
        else:
            new_id = self.id

        return Note(
            id=new_id,
            title=new_title,
            body=new_body,
            path=new_path,
            tags=new_tags,
            created_at=self.created_at,
            updated_at=updated_at or _utc_now(),
        )

    def has_tag(self, tag: str) -> bool:
        """Check whether the note includes a normalized tag."""
        return normalize_tags([tag]).pop() in self.tags if tag.strip() else False
