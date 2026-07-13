"""Smoke tests for the TUI."""

from pathlib import Path

import pytest
from textual.widgets import Button, Input, ListView, TextArea, Tree

from notes.models import Note
from notes.storage import NoteStore
from notes.tui.app import NoteFormScreen, NotesApp


def _detail_text(app: NotesApp) -> str:
    from textual.widgets import Static

    return str(app.query_one("#detail-panel", Static).render())


@pytest.mark.asyncio
async def test_tui_create_note_modal(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    store.save(Note.create(title="Existing", body="Body", path="work", short_id="1111"))

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, NoteFormScreen)
        assert app.screen.mode == "create"
        assert app.screen.query_one("#note-form-title", Input)
        assert app.screen.query_one("#note-form-path", Input)
        assert app.screen.query_one("#note-form-tags", Input)
        assert app.screen.query_one("#note-form-body", TextArea)


@pytest.mark.asyncio
async def test_tui_create_note_with_path_and_tags(tmp_path: Path):
    store_dir = tmp_path / "notes"
    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("n")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, NoteFormScreen)
        screen.query_one("#note-form-title", Input).value = "Standup"
        screen.query_one("#note-form-path", Input).value = "work/meetings"
        screen.query_one("#note-form-tags", Input).value = "work, meeting"
        screen.query_one("#note-form-body", TextArea).text = "Discuss roadmap"
        await pilot.click("#note-form-submit")
        await pilot.pause()

    notes = NoteStore(store_dir).list_notes(path="work/meetings")
    assert len(notes) == 1
    assert notes[0].title == "Standup"
    assert notes[0].body == "Discuss roadmap"
    assert notes[0].tags == {"work", "meeting"}


@pytest.mark.asyncio
async def test_tui_create_note_cancel(tmp_path: Path):
    store_dir = tmp_path / "notes"
    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("n")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, NoteFormScreen)
        screen.query_one("#note-form-title", Input).value = "Should not save"
        await pilot.click("#note-form-cancel")
        await pilot.pause()

    assert NoteStore(store_dir).list_notes() == []


@pytest.mark.asyncio
async def test_tui_help_modal(tmp_path: Path):
    app = NotesApp(tmp_path / "notes")
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("question_mark")
        await pilot.pause()
        assert "HelpScreen" in str(type(app.screen))


@pytest.mark.asyncio
async def test_tui_edit_mode_shows_unified_form(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    note = Note.create(title="Editable", body="Original", tags=["work"], short_id="1111")
    store.save(note)

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("e")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, NoteFormScreen)
        assert screen.mode == "edit"
        assert screen.query_one("#note-form-title", Input).value == "Editable"
        assert screen.query_one("#note-form-tags", Input).value == "work"
        assert screen.query_one("#note-form-body", TextArea).text == "Original"
        assert app.screen.query_one("#note-form-submit", Button).label == "Save"


@pytest.mark.asyncio
async def test_tui_save_persists_edit(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    note = Note.create(title="Editable", body="Original", short_id="2222")
    store.save(note)

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("e")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, NoteFormScreen)
        screen.query_one("#note-form-body", TextArea).text = "Updated body"
        await pilot.click("#note-form-submit")
        await pilot.pause()
        reloaded = store.load(note.id)
        assert reloaded.body == "Updated body"


@pytest.mark.asyncio
async def test_tui_edit_path_and_tags(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    note = Note.create(title="Move me", body="Body", path="work", tags=["old"], short_id="abcd")
    store.save(note)

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        tree = app.query_one("#tree-panel", Tree)
        work_node = next(node for node in tree.root.children if node.data == "work")
        tree.select_node(work_node)
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, NoteFormScreen)
        screen.query_one("#note-form-path", Input).value = "personal/archive"
        screen.query_one("#note-form-tags", Input).value = "new, urgent"
        await pilot.click("#note-form-submit")
        await pilot.pause()

    reloaded = store.load("personal/archive/move-me-abcd")
    assert reloaded.path == "personal/archive"
    assert reloaded.tags == {"new", "urgent"}


@pytest.mark.asyncio
async def test_tui_edit_cancel_discards_changes(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    note = Note.create(title="Editable", body="Original", tags=["keep"], short_id="3333")
    store.save(note)

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("e")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, NoteFormScreen)
        screen.query_one("#note-form-title", Input).value = "Changed title"
        screen.query_one("#note-form-body", TextArea).text = "Unsaved changes"
        screen.query_one("#note-form-tags", Input).value = "changed"
        await pilot.click("#note-form-cancel")
        await pilot.pause()

    reloaded = store.load(note.id)
    assert reloaded.title == "Editable"
    assert reloaded.body == "Original"
    assert reloaded.tags == {"keep"}


@pytest.mark.asyncio
async def test_tui_tree_navigation_updates_detail(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    store.save(Note.create(title="Root Note", body="At root", short_id="root"))
    store.save(Note.create(title="Work Note", body="In work folder", path="work", short_id="work"))

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        assert "Root Note" in _detail_text(app)
        tree = app.query_one("#tree-panel", Tree)
        tree.focus()
        await pilot.press("down")
        await pilot.pause()
        assert "Work Note" in _detail_text(app)
        assert app.query_one("#note-list", ListView).index == 0


@pytest.mark.asyncio
async def test_tui_tree_root_shows_root_note(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    store.save(Note.create(title="Root Note", body="At root", short_id="root"))
    store.save(Note.create(title="Work Note", body="In work folder", path="work", short_id="work"))

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        tree = app.query_one("#tree-panel", Tree)
        work_node = next(node for node in tree.root.children if node.data == "work")
        tree.select_node(work_node)
        await pilot.pause()
        assert "Work Note" in _detail_text(app)
        tree.select_node(tree.root)
        await pilot.pause()
        assert "Root Note" in _detail_text(app)


@pytest.mark.asyncio
async def test_tui_empty_folder_shows_empty_state(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    store.save(Note.create(title="Root Note", body="At root", short_id="root"))
    (store_dir / "work").mkdir()

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        tree = app.query_one("#tree-panel", Tree)
        work_node = next(node for node in tree.root.children if node.data == "work")
        tree.select_node(work_node)
        await pilot.pause()
        assert "No notes in this folder" in _detail_text(app)
        assert app.selected_note is None
