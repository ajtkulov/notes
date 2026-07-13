"""Textual TUI for notes."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Input, Label, ListItem, ListView, Static, TextArea, Tree

from notes.config import ensure_notes_dir
from notes.models import Note, ROOT_PATH, normalize_path
from notes.storage import NoteStore
from notes.tree import list_path


class HelpScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-box {
        width: 70;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    BINDINGS = [Binding("escape", "dismiss", "Close"), Binding("question_mark", "dismiss", "Close")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(
                "\n".join(
                    [
                        "[bold]Keyboard shortcuts[/bold]",
                        "j/k, arrows - navigate",
                        "Enter - expand/select tree folder",
                        "n - create note",
                        "e - edit note body",
                        "Ctrl+S / Save - save edits (edit mode)",
                        "Escape / Cancel - discard edits (edit mode)",
                        "d - delete note",
                        "m - move note",
                        "/ - search",
                        "t - filter by tag",
                        "? - this help",
                        "q - quit",
                    ]
                ),
                id="help-box",
            ),
            id="help-container",
        )


class ConfirmScreen(ModalScreen[bool]):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }
    #confirm-box {
        width: 60;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.message, id="confirm-box"),
            Horizontal(
                Button("Yes", id="yes", variant="primary"),
                Button("No", id="no"),
                id="confirm-buttons",
            ),
            id="confirm-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

    def action_cancel(self) -> None:
        self.dismiss(False)


class InputScreen(ModalScreen[str | None]):
    def __init__(self, title: str, initial: str = "") -> None:
        super().__init__()
        self.title = title
        self.initial = initial

    DEFAULT_CSS = """
    InputScreen {
        align: center middle;
    }
    #input-box {
        width: 70;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.title, id="input-label"),
            Input(value=self.initial, id="input-field"),
            Horizontal(Button("OK", id="ok", variant="primary"), Button("Cancel", id="cancel")),
            id="input-box",
        )

    def on_mount(self) -> None:
        self.query_one("#input-field", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.dismiss(self.query_one("#input-field", Input).value)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class NotesApp(App[None]):
    CSS = """
    Screen {
        layout: horizontal;
    }
    #tree-panel {
        width: 30%;
        border-right: solid $accent;
    }
    #right-panel {
        width: 70%;
    }
    #note-list {
        height: 35%;
        border-bottom: solid $accent;
    }
    #detail-panel {
        height: 65%;
        padding: 1;
    }
    #edit-toolbar {
        height: 3;
        padding: 0 1;
        align: left middle;
    }
    #editor {
        height: 1fr;
    }
    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "create_note", "New"),
        Binding("e", "edit_note", "Edit"),
        Binding("d", "delete_note", "Delete"),
        Binding("m", "move_note", "Move"),
        Binding("slash", "search", "Search"),
        Binding("t", "filter_tag", "Tag"),
        Binding("question_mark", "help", "Help"),
        Binding("ctrl+s", "save_edit", "Save", show=False),
        Binding("escape", "cancel_edit", "Cancel", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self, notes_dir: Path) -> None:
        super().__init__()
        self.store = NoteStore(ensure_notes_dir(notes_dir))
        self.current_path = ROOT_PATH
        self.notes: list[Note] = []
        self.selected_note: Note | None = None
        self.search_query: str | None = None
        self.tag_filter: str | None = None
        self.editing = False

    def compose(self) -> ComposeResult:
        yield Tree("Notes", id="tree-panel")
        yield Vertical(
            ListView(id="note-list"),
            VerticalScroll(
                Static("", id="detail-panel"),
                Horizontal(
                    Button("Save", id="save-edit", variant="primary"),
                    Button("Cancel", id="cancel-edit"),
                    id="edit-toolbar",
                ),
                TextArea(id="editor", language="markdown"),
                id="detail-container",
            ),
            id="right-panel",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#edit-toolbar").add_class("hidden")
        self.query_one("#editor", TextArea).add_class("hidden")
        self._populate_tree()
        self.refresh_notes()

    def _populate_tree(self) -> None:
        tree = self.query_one("#tree-panel", Tree)
        tree.clear()
        root = tree.root
        root.expand()
        self._add_tree_children(root, ROOT_PATH)

    def _add_tree_children(self, node, path: str) -> None:
        listing = list_path(self.store, path)
        for directory in listing.directories:
            child_path = f"{path}/{directory}" if path else directory
            child = node.add(f"{directory}/", data=child_path)
            self._add_tree_children(child, child_path)

    def refresh_notes(self) -> None:
        if self.search_query:
            from notes.search import search_store

            self.notes = search_store(self.store, self.search_query, use_cache=False)
        elif self.tag_filter:
            self.notes = self.store.list_notes(tag=self.tag_filter)
        else:
            self.notes = self.store.list_notes(path=self.current_path)
        self._render_note_list()
        self.selected_note = self.notes[0] if self.notes else None
        self._render_detail()

    def _render_note_list(self) -> None:
        list_view = self.query_one("#note-list", ListView)
        list_view.clear()
        for note in self.notes:
            label = f"{note.title}  ({self._relative_time(note.updated_at)})"
            if note.tags:
                label += f"  [{', '.join(sorted(note.tags))}]"
            list_view.append(ListItem(Label(label), id=f"note-{note.id}"))

    def _render_detail(self) -> None:
        detail = self.query_one("#detail-panel", Static)
        toolbar = self.query_one("#edit-toolbar")
        editor = self.query_one("#editor", TextArea)
        if self.editing and self.selected_note:
            detail.add_class("hidden")
            toolbar.remove_class("hidden")
            editor.text = self.selected_note.body
            editor.remove_class("hidden")
            editor.focus()
            return
        toolbar.add_class("hidden")
        editor.add_class("hidden")
        detail.remove_class("hidden")
        if not self.selected_note:
            detail.update("[dim]No notes in this folder. Press n to create one.[/dim]")
            return
        note = self.selected_note
        detail.update(
            "\n".join(
                [
                    f"[bold]{note.title}[/bold]",
                    f"ID: {note.id}",
                    f"Path: {note.path or '/'}",
                    f"Tags: {', '.join(sorted(note.tags)) or '-'}",
                    f"Updated: {note.updated_at.isoformat()}",
                    "",
                    note.body,
                ]
            )
        )

    def _save_edit(self) -> None:
        if not self.editing or not self.selected_note:
            return
        editor = self.query_one("#editor", TextArea)
        updated = self.selected_note.with_updates(body=editor.text)
        self.store.save(updated)
        self.selected_note = updated
        for index, note in enumerate(self.notes):
            if note.id == updated.id:
                self.notes[index] = updated
                break
        self.editing = False
        self._render_detail()

    def _cancel_edit(self) -> None:
        if not self.editing:
            return
        self.editing = False
        self._render_detail()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-edit":
            self._save_edit()
        elif event.button.id == "cancel-edit":
            self._cancel_edit()

    def action_save_edit(self) -> None:
        self._save_edit()

    def action_cancel_edit(self) -> None:
        self._cancel_edit()

    def _relative_time(self, timestamp: datetime) -> str:
        delta = datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)
        seconds = int(delta.total_seconds())
        if seconds < 3600:
            return f"{max(seconds // 60, 1)}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data is not None:
            self.current_path = normalize_path(str(event.node.data))
            self.search_query = None
            self.tag_filter = None
            self.refresh_notes()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index
        if index is not None and 0 <= index < len(self.notes):
            self.selected_note = self.notes[index]
            self.editing = False
            self._render_detail()

    @work
    async def action_create_note(self) -> None:
        title = await self.push_screen_wait(InputScreen("Note title"))
        if not title:
            return
        body = await self.push_screen_wait(InputScreen("Note body"))
        if body is None:
            return
        note = Note.create(title=title, body=body, path=self.current_path)
        self.store.save(note)
        self.refresh_notes()

    async def action_edit_note(self) -> None:
        if not self.selected_note:
            return
        self.editing = True
        self._render_detail()

    @work
    async def action_delete_note(self) -> None:
        if not self.selected_note:
            return
        confirmed = await self.push_screen_wait(
            ConfirmScreen(f"Delete {self.selected_note.id}?")
        )
        if confirmed:
            self.store.delete(self.selected_note.id)
            self.refresh_notes()

    @work
    async def action_move_note(self) -> None:
        if not self.selected_note:
            return
        new_path = await self.push_screen_wait(
            InputScreen("Destination path", self.selected_note.path)
        )
        if new_path is None:
            return
        moved = self.store.move(self.selected_note.id, new_path)
        self.selected_note = moved
        self.refresh_notes()

    @work
    async def action_search(self) -> None:
        query = await self.push_screen_wait(InputScreen("Search"))
        if query is None:
            self.search_query = None
        else:
            self.search_query = query
            self.tag_filter = None
        self.refresh_notes()

    @work
    async def action_filter_tag(self) -> None:
        tags = sorted(self.store.all_tags())
        if not tags:
            return
        tag = await self.push_screen_wait(InputScreen(f"Tag ({', '.join(tags)})"))
        if tag is None:
            self.tag_filter = None
        else:
            self.tag_filter = tag
            self.search_query = None
        self.refresh_notes()

    @work
    async def action_help(self) -> None:
        await self.push_screen(HelpScreen())


def run_tui(notes_dir: Path) -> None:
    NotesApp(notes_dir).run()
