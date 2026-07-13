## Context

The TUI edit flow uses a `TextArea` that saves on blur when `editing` is true. There is no visible control to save or cancel, and the spec mentions Escape to cancel but blur-based save is ambiguous. This change makes edit actions explicit.

## Goals / Non-Goals

**Goals:**

- Show Save and Cancel buttons while editing a note body
- Save only when the user clicks Save or presses `Ctrl+S`
- Cancel via button or `Escape`, discarding unsaved edits
- Keep edit mode visually distinct from read-only detail view

**Non-Goals:**

- Editing title or tags inline in the TUI (body only, as today)
- Auto-save or draft recovery
- External editor integration in TUI

## Decisions

### 1. Edit toolbar with Save / Cancel buttons

When edit mode is active, show a horizontal toolbar above the `TextArea` with "Save" (primary) and "Cancel" buttons.

**Rationale:** Clear affordance; matches modal patterns used elsewhere in the app (ConfirmScreen, InputScreen).

### 2. Explicit save only — remove blur save

Remove `on_text_area_blur` auto-save. Saving happens only via Save button or `Ctrl+S`.

**Rationale:** Blur save is surprising (e.g., clicking the tree panel would save). Explicit save matches user expectation for a Save button.

**Alternatives considered:**
- Keep blur save as fallback — rejected; conflicts with explicit Save/Cancel UX

### 3. Cancel restores original body

Cancel (button or Escape) sets `editing = False` without calling `store.save`, re-rendering the detail view with the previously loaded note body.

### 4. Keyboard shortcuts in edit mode

- `Ctrl+S` — save (bind via `Binding` on app or edit container)
- `Escape` — cancel (existing spec scenario)

### 5. Help text update

Add to help overlay under edit section:
- `Ctrl+S` / Save button — save edits
- `Escape` / Cancel button — discard edits

## Risks / Trade-offs

- **[Risk] User forgets to save** → Mitigation: visible Save button; `Ctrl+S` for power users
- **[Trade-off] Extra click to save vs blur** → Acceptable for clarity

## Open Questions

- None
