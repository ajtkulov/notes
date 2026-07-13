## Why

Creating and editing notes in the TUI use inconsistent UIs: create now uses a unified modal, but edit still opens an inline body-only editor. Users should see the same fields (title, path, tags, body) in both flows, with a large text area for the body.

## What Changes

- **Create** — unified modal with title, path, tags, body (implemented)
- **Edit** — replace inline body editor with the same modal layout, pre-filled from the selected note
- Shared form fields: title, path, tags (comma-separated), body (large `TextArea`)
- Edit uses **Save** / **Cancel** (plus `Ctrl+S` / `Escape`); create uses **Create** / **Cancel**
- On edit save, persist all field changes including path moves
- Remove inline edit toolbar and `TextArea` from the main detail panel

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `tui`: Create note in TUI — unified form with title, path, tags, and body fields
- `tui`: Edit note in TUI — same unified form as create, pre-filled with existing note data

## Impact

- `src/notes/tui/app.py` — shared `NoteFormScreen` (or reuse `CreateNoteScreen` in edit mode); remove inline edit UI
- `tests/test_tui.py` — update edit tests for modal form; add path/tags edit tests
- No CLI or storage API changes (uses existing `save` / `move`)
