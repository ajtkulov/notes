## 1. Create Note Screen

- [x] 1.1 Add `CreateNoteScreen` modal with title, path, tags inputs and body `TextArea`
- [x] 1.2 Layout form so body `TextArea` fills majority of modal height
- [x] 1.3 Add Create and Cancel buttons; wire `Escape` to cancel

## 2. Create Flow Integration

- [x] 2.1 Replace sequential `InputScreen` calls in `action_create_note` with `CreateNoteScreen`
- [x] 2.2 Pre-fill path from `current_path`; parse tags from comma-separated input
- [x] 2.3 Validate title is non-empty before create; call `Note.create` and `store.save`
- [x] 2.4 Select newly created note in list after successful create

## 3. Help and Tests (Create)

- [x] 3.1 Update help overlay to describe unified create form fields
- [x] 3.2 Update TUI create test for unified modal
- [x] 3.3 Add test: create with path and tags persists correctly
- [x] 3.4 Add test: cancel does not create note

## 4. Shared Note Form (Edit)

- [x] 4.1 Refactor `CreateNoteScreen` into shared `NoteFormScreen` with create/edit modes
- [x] 4.2 Edit mode pre-fills title, path, tags, and body from selected note
- [x] 4.3 Edit mode shows Save/Cancel; wire `Ctrl+S` and `Escape`
- [x] 4.4 On save: handle path move via `store.move`; update title, tags, body
- [x] 4.5 Remove inline edit toolbar, editor, and `editing` state from main screen

## 5. Help and Tests (Edit)

- [x] 5.1 Update help overlay for unified create/edit form
- [x] 5.2 Update edit tests to use modal form instead of inline editor
- [x] 5.3 Add test: edit path and tags persists correctly
- [x] 5.4 Add test: edit cancel discards all field changes
