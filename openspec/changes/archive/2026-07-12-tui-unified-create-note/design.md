## Context

Create flow uses `CreateNoteScreen` with title, path, tags, and body. Edit still uses an inline `TextArea` with Save/Cancel in the detail panel (body only). This change unifies both flows into the same modal form layout.

## Goals / Non-Goals

**Goals:**

- Single reusable note form modal for create and edit
- Fields: title, path, tags (comma-separated), body (large `TextArea`)
- Create mode: empty form (path pre-filled from tree); **Create** / **Cancel**
- Edit mode: form pre-filled from selected note; **Save** / **Cancel** with `Ctrl+S` / `Escape`
- Path change on edit triggers note move via `store.move`
- Title, tags, and body updates persisted on save

**Non-Goals:**

- Tag autocomplete or path tree picker
- Separate `m` (move) shortcut removal — keep as quick action, but path editable in form too
- External editor integration

## Decisions

### 1. Shared NoteFormScreen modal

Refactor `CreateNoteScreen` into `NoteFormScreen` with a `mode` (`"create"` | `"edit"`) and optional initial `NoteFormData`.

```
┌─ Create Note / Edit Note ─────────┐
│ Title:  [________________]        │
│ Path:   [work/meetings___]        │
│ Tags:   [work, meeting___]        │
│ Body:   ┌─────────────────────┐   │
│         │   (TextArea)        │   │
│         └─────────────────────┘   │
│         [Create|Save]  [Cancel]   │
└───────────────────────────────────┘
```

**Rationale:** One layout, two modes; reduces duplication and matches user expectation.

### 2. Edit save behavior

On Save in edit mode:

1. Validate title non-empty and path via `normalize_path`
2. If path changed → `store.move(note_id, new_path)` then update remaining fields
3. Else → `note.with_updates(title, body, tags)` and `store.save`
4. Refresh tree if path changed; re-select note in list

### 3. Remove inline edit UI

Delete `#edit-toolbar`, inline `#editor`, `editing` flag, and `action_save_edit` / `action_cancel_edit` from main screen. Edit opens modal via `@work` + `push_screen_wait`.

### 4. Keyboard shortcuts

- Create/Edit modal: `Escape` → cancel
- Edit modal only: `Ctrl+S` → save (Create mode: no Ctrl+S; use Create button)

### 5. Validation

Same as create: title required; path validated; tags normalized from comma-separated input.

## Risks / Trade-offs

- **[Risk] Path edit changes note id** → Mitigation: existing move semantics; refresh selection after save
- **[Trade-off] Modal vs inline edit** → Acceptable; consistency with create wins

## Open Questions

- None
