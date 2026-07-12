"""CLI entry point for notes."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from notes.config import ensure_notes_dir
from notes.models import Note, normalize_tags
from notes.search import search_store
from notes.storage import NoteNotFoundError, NoteStore
from notes.tree import build_tree, format_tree

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Local-first notes tracker.")
console = Console()


def _get_store(ctx: typer.Context) -> NoteStore:
    notes_dir = ctx.obj.get("notes_dir") if ctx.obj else None
    directory = ensure_notes_dir(notes_dir)
    return NoteStore(directory)


def _parse_tags(tags: Optional[str]) -> set[str] | None:
    if tags is None:
        return None
    return normalize_tags([part.strip() for part in tags.split(",")])


def _edit_text(initial: str) -> str:
    editor = os.environ.get("EDITOR", "vi")
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as handle:
        handle.write(initial.encode("utf-8"))
        temp_path = handle.name
    try:
        subprocess.run([editor, temp_path], check=True)
        return Path(temp_path).read_text(encoding="utf-8")
    finally:
        Path(temp_path).unlink(missing_ok=True)


@app.callback()
def main(
    ctx: typer.Context,
    notes_dir: Annotated[
        Optional[Path],
        typer.Option("--notes-dir", help="Override notes storage directory"),
    ] = None,
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["notes_dir"] = notes_dir


@app.command("create")
def create_note(
    ctx: typer.Context,
    title: Annotated[str, typer.Option("--title", prompt=True)],
    body: Annotated[Optional[str], typer.Option("--body")] = "",
    path: Annotated[str, typer.Option("--path")] = "",
    tags: Annotated[Optional[str], typer.Option("--tags")] = None,
    edit: Annotated[bool, typer.Option("--edit")] = False,
) -> None:
    """Create a new note."""
    store = _get_store(ctx)
    content = body or ""
    if edit:
        content = _edit_text(content)
    note = Note.create(title=title, body=content, path=path, tags=_parse_tags(tags))
    store.save(note)
    console.print(note.id)


@app.command("list")
def list_notes(
    ctx: typer.Context,
    path: Annotated[Optional[str], typer.Option("--path")] = None,
    recursive: Annotated[bool, typer.Option("--recursive")] = False,
    tag: Annotated[Optional[str], typer.Option("--tag")] = None,
) -> None:
    """List notes."""
    store = _get_store(ctx)
    notes = store.list_notes(path=path, recursive=recursive, tag=tag)
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Path")
    table.add_column("Tags")
    table.add_column("Updated")
    for note in notes:
        table.add_row(
            note.id,
            note.title,
            note.path or "/",
            ", ".join(sorted(note.tags)),
            note.updated_at.isoformat(),
        )
    console.print(table)


@app.command("show")
def show_note(
    ctx: typer.Context,
    note_id: Annotated[str, typer.Argument(help="Note id")],
) -> None:
    """Show a note."""
    store = _get_store(ctx)
    try:
        note = store.load(note_id)
    except NoteNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    console.print(f"[bold]{note.title}[/bold]")
    console.print(f"ID: {note.id}")
    console.print(f"Path: {note.path or '/'}")
    console.print(f"Tags: {', '.join(sorted(note.tags)) or '-'}")
    console.print(f"Created: {note.created_at.isoformat()}")
    console.print(f"Updated: {note.updated_at.isoformat()}")
    console.print("")
    console.print(note.body)


@app.command("edit")
def edit_note(
    ctx: typer.Context,
    note_id: Annotated[str, typer.Argument(help="Note id")],
    title: Annotated[Optional[str], typer.Option("--title")] = None,
    body: Annotated[Optional[str], typer.Option("--body")] = None,
    tags: Annotated[Optional[str], typer.Option("--tags")] = None,
) -> None:
    """Edit a note."""
    store = _get_store(ctx)
    try:
        note = store.load(note_id)
    except NoteNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    new_body = body
    if new_body is None and title is None and tags is None:
        new_body = _edit_text(note.body)
    updated = note.with_updates(title=title, body=new_body, tags=_parse_tags(tags))
    store.save(updated)
    console.print(updated.id)


@app.command("mv")
def move_note(
    ctx: typer.Context,
    note_id: Annotated[str, typer.Argument(help="Note id")],
    path: Annotated[str, typer.Argument(help="Destination path")],
) -> None:
    """Move a note to another directory."""
    store = _get_store(ctx)
    try:
        moved = store.move(note_id, path)
    except NoteNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    console.print(moved.id)


@app.command("delete")
def delete_note(
    ctx: typer.Context,
    note_id: Annotated[str, typer.Argument(help="Note id")],
    yes: Annotated[bool, typer.Option("--yes", help="Skip confirmation")] = False,
) -> None:
    """Delete a note."""
    store = _get_store(ctx)
    if not yes and not typer.confirm(f"Delete {note_id}?"):
        raise typer.Exit(code=1)
    try:
        store.delete(note_id)
    except NoteNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc


@app.command("search")
def search_command(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="Search query")],
) -> None:
    """Search notes."""
    store = _get_store(ctx)
    results = search_store(store, query)
    if not results:
        console.print("No notes found")
        return
    for note in results:
        console.print(f"{note.id}\t{note.path or '/'}\t{note.title}")


@app.command("tree")
def tree_command(ctx: typer.Context) -> None:
    """Show the notes directory tree."""
    store = _get_store(ctx)
    root = build_tree(store)
    for line in format_tree(root):
        console.print(line)


@app.command("tui")
def tui_command(ctx: typer.Context) -> None:
    """Launch the interactive TUI."""
    from notes.config import resolve_notes_dir
    from notes.tui.app import run_tui

    notes_dir = ctx.obj.get("notes_dir") if ctx.obj else None
    run_tui(notes_dir or resolve_notes_dir())


def cli_main() -> None:
    app()


if __name__ == "__main__":
    cli_main()
