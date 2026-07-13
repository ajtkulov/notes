## Why

When navigating folders in the TUI directory tree, the note list updates but the detail panel does not reliably show a note from the newly selected folder. Users expect browsing a folder to immediately preview its most recent note without an extra click in the note list.

## What Changes

- When a tree folder is selected (including keyboard traversal), auto-select the first note in that folder's note list and update the detail panel
- Sync the note list highlight (`ListView` index) with the auto-selected note
- Handle root-level folder selection so notes at the notes root also refresh correctly
- Add TUI test coverage for tree navigation updating the detail view

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `tui`: Directory tree selection SHALL update both the note list and detail view with an auto-selected note

## Impact

- `src/notes/tui/app.py` — tree selection handler and `refresh_notes` list/detail sync
- `tests/test_tui.py` — new test for tree traversal updating detail view
- `openspec/specs/tui/spec.md` — clarify folder selection auto-selects a note
