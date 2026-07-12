"""Smoke tests for the TUI."""

from pathlib import Path

import pytest
from textual.pilot import Pilot

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
