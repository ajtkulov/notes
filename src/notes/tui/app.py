"""Textual TUI for notes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from textual import events, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.keys import format_key
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Input, Label, ListItem, ListView, Static, TextArea, Tree

from notes.config import ensure_notes_dir
from notes.models import Note, ROOT_PATH, normalize_path, normalize_tags
from notes.storage import NoteStore
from notes.tree import list_path
from notes.tui.clipboard import copy_text


@dataclass
class NoteFormData:
    title: str
    path: str
    tags: set[str]
    body: str


# Backward-compatible alias
CreateNoteFormData = NoteFormData


def _format_pressed_key(key: str) -> str:
    """Format a key identifier for on-screen display."""
    modifier_labels = {
        "ctrl": "Ctrl",
        "shift": "Shift",
        "meta": "Cmd",
        "alt": "Alt",
    }
    binding = Binding(key, "action", "")
    modifiers, bare_key = binding.parse_key()
    key_label = format_key(bare_key)
    if modifiers:
        mod_labels = [modifier_labels.get(modifier, modifier.title()) for modifier in modifiers]
        return "+".join([*mod_labels, key_label])
    return key_label


def _update_key_displays(node, event: events.Key) -> None:
    """Update all key-press indicators under the given DOM node."""
    label = _format_pressed_key(event.key)
    for display in node.query(".key-press-display"):
        display.update(f"[bold]{label}[/bold]")
        display.add_class("-visible")


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
                        "n - create note (title, path, tags, body)",
                        "e - edit note (same form; Save/Ctrl+S, Cancel/Escape)",
                        "c - copy selected note body",
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


class NoteFormScreen(ModalScreen[NoteFormData | None]):
    DEFAULT_CSS = """
    NoteFormScreen {
        align: center middle;
    }
    #note-form-box {
        width: 80;
        height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #note-form-body {
        height: 1fr;
        min-height: 10;
    }
    #note-form-error {
        color: $error;
        height: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "submit", "Save", show=False),
    ]

    def __init__(
        self,
        mode: Literal["create", "edit"],
        *,
        initial_path: str = ROOT_PATH,
        initial: NoteFormData | None = None,
    ) -> None:
        super().__init__()
        self.mode = mode
        self.initial_path = initial_path
        self.initial = initial

    @classmethod
    def for_create(cls, initial_path: str = ROOT_PATH) -> NoteFormScreen:
        return cls("create", initial_path=initial_path)

    @classmethod
    def for_edit(cls, note: Note) -> NoteFormScreen:
        return cls(
            "edit",
            initial=NoteFormData(
                title=note.title,
                path=note.path,
                tags=set(note.tags),
                body=note.body,
            ),
        )

    def compose(self) -> ComposeResult:
        heading = "Create Note" if self.mode == "create" else "Edit Note"
        submit_label = "Create" if self.mode == "create" else "Save"
        title_value = self.initial.title if self.initial else ""
        path_value = self.initial.path if self.initial else self.initial_path
        tags_value = ", ".join(sorted(self.initial.tags)) if self.initial else ""
        body_value = self.initial.body if self.initial else ""
        yield Vertical(
            Static(f"[bold]{heading}[/bold]"),
            Label("Title"),
            Input(value=title_value, placeholder="Note title", id="note-form-title"),
            Label("Path"),
            Input(value=path_value, placeholder="work/meetings", id="note-form-path"),
            Label("Tags"),
            Input(value=tags_value, placeholder="work, meeting", id="note-form-tags"),
            Label("Body"),
            TextArea(body_value, id="note-form-body", language="markdown"),
            Static("", id="note-form-error"),
            Horizontal(
                Button(submit_label, id="note-form-submit", variant="primary"),
                Button("Cancel", id="note-form-cancel"),
            ),
            id="note-form-box",
        )

    def on_mount(self) -> None:
        self.query_one("#note-form-title", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "note-form-submit":
            self._submit()
        elif event.button.id == "note-form-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        if self.mode == "edit":
            self._submit()

    def _submit(self) -> None:
        title = self.query_one("#note-form-title", Input).value.strip()
        if not title:
            self.query_one("#note-form-error", Static).update("Title is required.")
            return
        path_value = self.query_one("#note-form-path", Input).value
        tags_value = self.query_one("#note-form-tags", Input).value
        body = self.query_one("#note-form-body", TextArea).text
        try:
            path = normalize_path(path_value)
        except ValueError as exc:
            self.query_one("#note-form-error", Static).update(str(exc))
            return
        tags = normalize_tags([part.strip() for part in tags_value.split(",") if part.strip()])
        self.dismiss(NoteFormData(title=title, path=path, tags=tags, body=body))


# Backward-compatible alias
CreateNoteScreen = NoteFormScreen


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
        height: 100%;
        padding: 1;
    }
    #footer-bar {
        dock: bottom;
        height: 1;
        width: 100%;
    }
    #footer-bar Footer {
        dock: initial;
        width: 1fr;
    }
    .key-press-display {
        width: auto;
        height: 1;
        padding: 0 1;
        margin-right: 1;
        color: $footer-key-foreground;
        background: $footer-key-background;
        display: none;
    }
    .key-press-display.-visible {
        display: block;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "copy_note", "Copy", priority=True),
        Binding("n", "create_note", "New"),
        Binding("e", "edit_note", "Edit"),
        Binding("d", "delete_note", "Delete"),
        Binding("m", "move_note", "Move"),
        Binding("slash", "search", "Search"),
        Binding("t", "filter_tag", "Tag"),
        Binding("question_mark", "help", "Help"),
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

    def compose(self) -> ComposeResult:
        yield Tree("Notes", id="tree-panel")
        yield Vertical(
            ListView(id="note-list"),
            VerticalScroll(Static("", id="detail-panel"), id="detail-container"),
            id="right-panel",
        )
        yield Horizontal(
            Footer(show_command_palette=False),
            Static("", classes="key-press-display"),
            id="footer-bar",
        )

    async def on_event(self, event: events.Event) -> None:
        if isinstance(event, events.Key):
            _update_key_displays(self, event)
        await super().on_event(event)

    def on_mount(self) -> None:
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

    def refresh_notes(self, *, select_note_id: str | None = None) -> None:
        if self.search_query:
            from notes.search import search_store

            self.notes = search_store(self.store, self.search_query, use_cache=False)
        elif self.tag_filter:
            self.notes = self.store.list_notes(tag=self.tag_filter)
        else:
            self.notes = self.store.list_notes(path=self.current_path)
        self._render_note_list()
        list_view = self.query_one("#note-list", ListView)
        if select_note_id:
            self.selected_note = next((note for note in self.notes if note.id == select_note_id), None)
            if self.selected_note:
                for index, note in enumerate(self.notes):
                    if note.id == select_note_id:
                        list_view.index = index
                        break
            else:
                list_view.index = None
        elif self.notes:
            self.selected_note = self.notes[0]
            list_view.index = 0
        else:
            self.selected_note = None
            list_view.index = None
        self._render_detail()

    def _render_note_list(self) -> None:
        list_view = self.query_one("#note-list", ListView)
        list_view.remove_children()
        for note in self.notes:
            label = f"{note.title}  ({self._relative_time(note.updated_at)})"
            if note.tags:
                label += f"  [{', '.join(sorted(note.tags))}]"
            list_view.append(ListItem(Label(label)))

    def _render_detail(self) -> None:
        detail = self.query_one("#detail-panel", Static)
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

    def _apply_form_edit(self, note: Note, form: NoteFormData) -> Note:
        current = note
        if form.path != note.path:
            current = self.store.move(note.id, form.path)
        updated = current.with_updates(title=form.title, body=form.body, tags=form.tags)
        self.store.save(updated)
        return updated

    def _relative_time(self, timestamp: datetime) -> str:
        delta = datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)
        seconds = int(delta.total_seconds())
        if seconds < 3600:
            return f"{max(seconds // 60, 1)}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"

    def _tree_node_path(self, node) -> str:
        if node.is_root:
            return ROOT_PATH
        return normalize_path(str(node.data))

    def _on_tree_folder(self, path: str) -> None:
        normalized = normalize_path(path)
        if (
            normalized == self.current_path
            and self.search_query is None
            and self.tag_filter is None
        ):
            return
        self.current_path = normalized
        self.search_query = None
        self.tag_filter = None
        self.refresh_notes()

    def _handle_tree_node(self, node) -> None:
        if node.data is not None or node.is_root:
            self._on_tree_folder(self._tree_node_path(node))

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        self._handle_tree_node(event.node)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        self._handle_tree_node(event.node)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index
        if index is not None and 0 <= index < len(self.notes):
            self.selected_note = self.notes[index]
            self._render_detail()

    def action_copy_note(self) -> None:
        if not self.selected_note:
            self.notify("No note selected", severity="warning", timeout=2)
            return
        body = self.selected_note.body
        if not copy_text(body):
            self.copy_to_clipboard(body)
        self.notify("Copied note body to clipboard", timeout=2)

    @work
    async def action_create_note(self) -> None:
        form = await self.push_screen_wait(NoteFormScreen.for_create(self.current_path))
        if form is None:
            return
        note = Note.create(
            title=form.title,
            body=form.body,
            path=form.path,
            tags=form.tags,
        )
        self.store.save(note)
        self.current_path = form.path
        self.search_query = None
        self.tag_filter = None
        self._populate_tree()
        self.refresh_notes(select_note_id=note.id)

    @work
    async def action_edit_note(self) -> None:
        if not self.selected_note:
            return
        note = self.selected_note
        form = await self.push_screen_wait(NoteFormScreen.for_edit(note))
        if form is None:
            return
        updated = self._apply_form_edit(note, form)
        self.current_path = updated.path
        self.search_query = None
        self.tag_filter = None
        self._populate_tree()
        self.refresh_notes(select_note_id=updated.id)

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
