## 1. Copy action

- [x] 1.1 Add `ctrl+c` binding and `action_copy_note` that copies `selected_note.body` via `copy_to_clipboard`
- [x] 1.2 No-op when `selected_note` is None

## 2. Help and docs

- [x] 2.1 Update help overlay with copy shortcut and quit via `q` only

## 3. Tests

- [x] 3.1 Add test: copy with note selected calls clipboard with note body
- [x] 3.2 Add test: copy with no note selected does not call clipboard
