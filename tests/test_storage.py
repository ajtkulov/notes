"""Tests for note storage."""

from pathlib import Path

import pytest

from notes.models import Note
from notes.storage import NoteNotFoundError, NoteStore


@pytest.fixture
def store(tmp_path: Path) -> NoteStore:
    return NoteStore(tmp_path)


def test_save_and_load_note(store: NoteStore):
    note = Note.create(title="Standup", body="Updates", path="work/meetings", tags=["work"], short_id="a3f2")
    store.save(note)
    loaded = store.load(note.id)
    assert loaded.title == "Standup"
    assert loaded.body == "Updates"
    assert loaded.path == "work/meetings"
    assert loaded.tags == {"work"}


def test_list_notes_by_path_and_tag(store: NoteStore):
    store.save(Note.create(title="A", body="alpha", path="work", tags=["work"], short_id="1111"))
    store.save(Note.create(title="B", body="beta", path="work/meetings", tags=["meeting"], short_id="2222"))
    store.save(Note.create(title="C", body="gamma", path="personal", tags=["work"], short_id="3333"))

    assert len(store.list_notes(path="work")) == 1
    assert len(store.list_notes(path="work", recursive=True)) == 2
    assert len(store.list_notes(tag="work")) == 2


def test_move_note(store: NoteStore):
    note = Note.create(title="Move me", body="Body", path="work", short_id="abcd")
    store.save(note)
    moved = store.move(note.id, "personal/archive")
    assert moved.id == "personal/archive/move-me-abcd"
    assert store.load(moved.id).path == "personal/archive"
    with pytest.raises(NoteNotFoundError):
        store.load(note.id)


def test_delete_prunes_empty_directories(store: NoteStore):
    note = Note.create(title="Temp", body="Body", path="work/meetings", short_id="dead")
    store.save(note)
    note_path = store.root / "work" / "meetings" / "temp-dead.md"
    assert note_path.is_file()
    store.delete(note.id)
    assert not note_path.exists()
    assert not (store.root / "work" / "meetings").exists()
    assert not (store.root / "work").exists()
