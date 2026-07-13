## 1. Edit Mode UI

- [x] 1.1 Add edit toolbar with Save and Cancel buttons, shown only when `editing` is true
- [x] 1.2 Hide toolbar and text area when not in edit mode

## 2. Save and Cancel Behavior

- [x] 2.1 Implement Save handler — persist body via `store.save`, exit edit mode, refresh detail view
- [x] 2.2 Implement Cancel handler — discard changes, exit edit mode, restore detail view
- [x] 2.3 Remove auto-save on `TextArea` blur
- [x] 2.4 Add `Ctrl+S` binding to trigger Save during edit mode
- [x] 2.5 Wire `Escape` to Cancel during edit mode

## 3. Help and Tests

- [x] 3.1 Update help overlay with Save/Cancel edit-mode shortcuts
- [x] 3.2 Add TUI test: entering edit mode shows Save/Cancel buttons
- [x] 3.3 Add TUI test: Save persists edited body; Cancel discards changes
