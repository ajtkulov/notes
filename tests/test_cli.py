"""Integration tests for CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from notes.cli.app import app
from notes.models import Note
from notes.storage import NoteStore


runner = CliRunner()


def test_cli_create_list_show(tmp_path: Path):
    notes_dir = tmp_path / "notes"
    result = runner.invoke(
        app,
        ["--notes-dir", str(notes_dir), "create", "--title", "Hello", "--body", "World"],
    )
    assert result.exit_code == 0
    note_id = result.stdout.strip()

    list_result = runner.invoke(app, ["--notes-dir", str(notes_dir), "list"])
    assert list_result.exit_code == 0
    assert "Hello" in list_result.stdout

    show_result = runner.invoke(app, ["--notes-dir", str(notes_dir), "show", note_id])
    assert show_result.exit_code == 0
    assert "World" in show_result.stdout


def test_cli_search_and_tree(tmp_path: Path):
    notes_dir = tmp_path / "notes"
    store = NoteStore(notes_dir)
    store.save(Note.create(title="Project Alpha", body="details", path="work", short_id="aaaa"))

    search_result = runner.invoke(app, ["--notes-dir", str(notes_dir), "search", "alpha"])
    assert search_result.exit_code == 0
    assert "Project Alpha" in search_result.stdout

    tree_result = runner.invoke(app, ["--notes-dir", str(notes_dir), "tree"])
    assert tree_result.exit_code == 0
    assert "work" in tree_result.stdout


def test_cli_delete_and_mv(tmp_path: Path):
    notes_dir = tmp_path / "notes"
    store = NoteStore(notes_dir)
    note = Note.create(title="Move", body="body", path="work", short_id="bbbb")
    store.save(note)

    mv_result = runner.invoke(
        app,
        ["--notes-dir", str(notes_dir), "mv", note.id, "personal"],
    )
    assert mv_result.exit_code == 0
    assert "personal/move-bbbb" in mv_result.stdout

    delete_result = runner.invoke(
        app,
        ["--notes-dir", str(notes_dir), "delete", "personal/move-bbbb", "--yes"],
    )
    assert delete_result.exit_code == 0
