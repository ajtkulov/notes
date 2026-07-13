## Why

Editing a note in the TUI currently saves only when the text area loses focus, which is unintuitive and easy to miss. Users need an explicit Save control to confirm changes and a visible Cancel option alongside the existing Escape shortcut.

## What Changes

- Add Save and Cancel buttons visible during note body edit mode
- Save persists the edited body and returns to the detail view
- Cancel discards unsaved changes and returns to the detail view
- Remove implicit save-on-blur behavior in favor of explicit Save
- Add `Ctrl+S` keyboard shortcut as an alternative to the Save button
- Update help overlay to document edit-mode controls

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `tui`: Edit note in TUI — add explicit Save/Cancel controls and update save/cancel behavior

## Impact

- `src/notes/tui/app.py` — edit mode UI, save/cancel handlers
- `tests/test_tui.py` — new tests for save and cancel during edit
- No CLI, storage, or dependency changes
