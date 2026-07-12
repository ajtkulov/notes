"""Search utilities for notes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from notes.config import DEFAULT_CONFIG_DIR
from notes.models import Note
from notes.storage import NoteStore

INDEX_FILE = DEFAULT_CONFIG_DIR / ".index.json"


@dataclass
class IndexEntry:
    id: str
    title: str
    path: str
    tags: list[str]
    body: str
    mtime: float


def _note_matches(note: Note, query: str) -> bool:
    needle = query.casefold()
    haystacks = [
        note.title,
        note.body,
        note.path,
        " ".join(sorted(note.tags)),
    ]
    return any(needle in value.casefold() for value in haystacks)


def search_notes(notes: list[Note], query: str) -> list[Note]:
    """Case-insensitive search across title, tags, body, and path."""
    if not query.strip():
        return notes
    return [note for note in notes if _note_matches(note, query)]


def _collect_index_entries(store: NoteStore) -> list[IndexEntry]:
    entries: list[IndexEntry] = []
    for file_path in store.root.rglob("*.md"):
        note = store._load_file(file_path)
        entries.append(
            IndexEntry(
                id=note.id,
                title=note.title,
                path=note.path,
                tags=sorted(note.tags),
                body=note.body,
                mtime=file_path.stat().st_mtime,
            )
        )
    return entries


def _index_is_valid(store: NoteStore, cached: list[IndexEntry]) -> bool:
    current = {entry.id: entry.mtime for entry in _collect_index_entries(store)}
    if len(current) != len(cached):
        return False
    for entry in cached:
        if current.get(entry.id) != entry.mtime:
            return False
    return True


def load_or_build_index(store: NoteStore) -> list[IndexEntry]:
    """Load cached index or rebuild it when stale."""
    if INDEX_FILE.exists():
        raw = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        cached = [IndexEntry(**entry) for entry in raw.get("entries", [])]
        if _index_is_valid(store, cached):
            return cached
    entries = _collect_index_entries(store)
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(
        json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(), "entries": [asdict(entry) for entry in entries]}),
        encoding="utf-8",
    )
    return entries


def search_store(store: NoteStore, query: str, *, use_cache: bool = True) -> list[Note]:
    """Search all notes in a store, optionally using the index cache."""
    if use_cache:
        entries = load_or_build_index(store)
        needle = query.casefold()
        matching_ids = [
            entry.id
            for entry in entries
            if needle
            in " ".join([entry.title, entry.body, entry.path, " ".join(entry.tags)]).casefold()
        ]
        return [store.load(note_id) for note_id in matching_ids]
    return search_notes(store.list_notes(), query)
