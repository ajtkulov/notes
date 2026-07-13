"""Smoke tests for the TUI."""

from pathlib import Path

import pytest
from textual.widgets import Button, TextArea

from notes.models import Note
from notes.storage import NoteStore
from notes.tui.app import NotesApp


@pytest.mark.asyncio
async def test_tui_create_note_modal(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    store.save(Note.create(title="Existing", body="Body", path="work", short_id="1111"))

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("n")
        await pilot.pause()
        assert "InputScreen" in str(type(app.screen))


@pytest.mark.asyncio
async def test_tui_help_modal(tmp_path: Path):
    app = NotesApp(tmp_path / "notes")
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("question_mark")
        await pilot.pause()
        assert "HelpScreen" in str(type(app.screen))


@pytest.mark.asyncio
async def test_tui_edit_mode_shows_save_cancel_buttons(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    note = Note.create(title="Editable", body="Original", short_id="1111")
    store.save(note)

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("e")
        await pilot.pause()
        toolbar = app.query_one("#edit-toolbar")
        assert "hidden" not in toolbar.classes
        assert app.query_one("#save-edit", Button)
        assert app.query_one("#cancel-edit", Button)
        assert "hidden" not in app.query_one("#editor", TextArea).classes


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
        editor = app.query_one("#editor", TextArea)
        editor.text = "Updated body"
        await pilot.click("#save-edit")
        await pilot.pause()
        assert not app.editing
        reloaded = store.load(note.id)
        assert reloaded.body == "Updated body"


@pytest.mark.asyncio
async def test_tui_cancel_discards_edit(tmp_path: Path):
    store_dir = tmp_path / "notes"
    store = NoteStore(store_dir)
    note = Note.create(title="Editable", body="Original", short_id="3333")
    store.save(note)

    app = NotesApp(store_dir)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("e")
        await pilot.pause()
        app.query_one("#editor", TextArea).text = "Unsaved changes"
        await pilot.click("#cancel-edit")
        await pilot.pause()
        assert not app.editing
        reloaded = store.load(note.id)
        assert reloaded.body == "Original"
        detail_text = str(app.query_one("#detail-panel").render())
        assert "Original" in detail_text
