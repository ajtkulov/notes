## Context

The TUI displays a selected note's body in the detail panel. Textual provides `App.copy_to_clipboard(text)` for system clipboard access. Currently `Ctrl+C` is documented as a quit shortcut alongside `q`, which conflicts with the conventional copy meaning of that key chord.

## Goals / Non-Goals

**Goals:**

- Copy selected note body to system clipboard via `Ctrl+C` / `Cmd+C`
- Do nothing when no note is selected
- Quit only via `q` on the main screen
- Document copy in help overlay

**Non-Goals:**

- Copying title, tags, or frontmatter (body only)
- Copy from edit modal (Save/Cancel already use other bindings)
- Visual toast/notification beyond optional brief footer feedback

## Decisions

### 1. Copy note body only

**Choice:** Copy `selected_note.body` as plain text.

**Rationale:** Matches the most common use case (paste into email, chat, editor). Metadata is visible in the detail panel but rarely needed in clipboard.

**Alternative considered:** Full markdown with frontmatter — rejected as surprising for paste targets.

### 2. Rebind `Ctrl+C` to copy; quit via `q` only

**Choice:** Add `Binding("ctrl+c", "copy_note", "Copy")` on `NotesApp`. Remove `Ctrl+C` from quit scenarios in spec.

**Rationale:** User explicitly requested Cmd/Ctrl+C for copy. Terminal users still have `q` and can use terminal-level interrupt if needed.

**Alternative considered:** Separate `y` yank binding — rejected; user asked for Cmd/Ctrl+C.

### 3. Use Textual `copy_to_clipboard`

**Choice:** Call `self.copy_to_clipboard(note.body)` in `action_copy_note`.

**Rationale:** Built-in Textual API; works cross-platform without extra dependencies.

### 4. Guard when no selection

**Choice:** Return early if `selected_note is None`.

**Rationale:** Avoids copying empty string; no error dialog needed.

## Risks / Trade-offs

- **[Risk] Users expect Ctrl+C to quit** → Mitigated by keeping `q` and documenting in help; breaking change noted in proposal.
- **[Risk] Clipboard unavailable in headless test environments** → Mock `copy_to_clipboard` in unit tests.
- **[Risk] Modal screens may intercept Ctrl+C** → Binding is on main `NotesApp`; modals use Escape/Ctrl+S and do not bind copy.
