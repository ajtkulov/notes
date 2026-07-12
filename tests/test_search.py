"""Tests for search."""

from pathlib import Path

from notes.models import Note
from notes.search import search_notes, search_store
from notes.storage import NoteStore


def test_search_notes_case_insensitive():
    notes = [
        Note.create(title="Meeting Notes", body="Project Alpha", path="work", tags=["Work"]),
        Note.create(title="Personal", body="shopping", path="personal"),
    ]
    results = search_notes(notes, "project")
    assert len(results) == 1
    assert results[0].title == "Meeting Notes"


def test_search_store(tmp_path: Path):
    store = NoteStore(tmp_path)
    store.save(Note.create(title="Alpha", body="one", path="work", short_id="1111"))
    store.save(Note.create(title="Beta", body="two", path="personal", short_id="2222"))
    results = search_store(store, "alpha", use_cache=False)
    assert len(results) == 1
    assert results[0].title == "Alpha"
