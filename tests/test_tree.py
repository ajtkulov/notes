"""Tests for tree navigation."""

from pathlib import Path

from notes.models import Note
from notes.storage import NoteStore
from notes.tree import build_tree, format_tree, list_path


def test_list_path_and_build_tree(tmp_path: Path):
    store = NoteStore(tmp_path)
    store.save(Note.create(title="Root note", body="root", short_id="1111"))
    store.save(Note.create(title="Work note", body="work", path="work", short_id="2222"))
    store.save(Note.create(title="Meeting", body="meet", path="work/meetings", short_id="3333"))

    root_listing = list_path(store, "")
    assert root_listing.directories == ["work"]
    assert len(root_listing.note_ids) == 1

    work_listing = list_path(store, "work")
    assert work_listing.directories == ["meetings"]
    assert len(work_listing.note_ids) == 1

    tree = build_tree(store)
    assert tree.note_count == 3
    assert tree.children[0].name == "work"
    assert tree.children[0].note_count == 2

    lines = format_tree(tree)
    assert lines[0].startswith("/ (3)")
