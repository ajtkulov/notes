## Why

Users frequently want to paste note content into other apps. The TUI currently has no way to copy a note to the system clipboard, forcing users to open the markdown file externally or retype content.

## What Changes

- Add `Ctrl+C` / `Cmd+C` binding to copy the selected note's body to the system clipboard
- No-op when no note is selected
- **BREAKING:** Remove `Ctrl+C` as a quit shortcut; quit remains available via `q`
- Update help overlay to document copy and revised quit behavior
- Add TUI tests for copy action

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `tui`: Add copy-to-clipboard requirement; update quit and help requirements

## Impact

- `src/notes/tui/app.py` — new `action_copy_note`, binding, help text
- `tests/test_tui.py` — copy behavior tests
- `openspec/specs/tui/spec.md` — copy, quit, and help requirements
