## Context

The TUI has three panels: directory tree, note list, and detail view. Selecting a folder calls `refresh_notes()`, which loads notes for `current_path`, sets `selected_note` to the first note, and calls `_render_detail()`. However, two gaps cause stale or empty detail views when browsing the tree:

1. **ListView index not synced** — `refresh_notes()` sets `selected_note` but does not set `list_view.index`, so the list highlight and detail can diverge.
2. **Tree highlight vs selection** — Textual fires `Tree.NodeHighlighted` when the user moves with `j`/`k`, but `Tree.NodeSelected` only on Enter/click. The app only handles `NodeSelected`, so traversing the tree without confirming leaves the note list and detail showing the previous folder.
3. **Root folder ignored** — `on_tree_node_selected` skips nodes where `data is None`, so selecting the tree root does not reload root-level notes.

## Goals / Non-Goals

**Goals:**

- Moving the tree cursor to a folder updates the note list and detail view immediately
- The first note (most recently updated) in the folder is auto-selected with matching list highlight
- Selecting the tree root shows root-level notes and detail
- Empty folders show the existing empty-state message

**Non-Goals:**

- Changing sort order or which note is "first"
- Auto-expanding tree nodes on cursor move
- Changing search/tag-filter behavior (those modes keep their own selection rules)

## Decisions

### 1. Handle `Tree.NodeHighlighted` in addition to `Tree.NodeSelected`

**Choice:** Extract folder-change logic into a shared method and invoke it from both event handlers.

**Rationale:** Keyboard tree traversal highlights nodes without selecting them. Responding to highlight matches user expectation that the right panel is a live preview of the highlighted folder.

**Alternative considered:** Only fix `NodeSelected` — rejected because it would still require Enter after every folder move.

### 2. Centralize selection sync in `refresh_notes`

**Choice:** After loading notes, always set `selected_note`, `list_view.index`, and detail together in one code path.

**Rationale:** Avoids duplicate logic and ensures list highlight and detail stay in sync for tree navigation, create, edit, and search flows.

**Alternative considered:** Separate `_select_first_note()` only for tree — rejected; the same bug affects any path that calls `refresh_notes()` without `select_note_id`.

### 3. Treat tree root as `ROOT_PATH`

**Choice:** When the highlighted/selected node is the tree root, set `current_path` to `ROOT_PATH` and refresh.

**Rationale:** Root represents the notes root directory; children already carry path data but root does not.

## Risks / Trade-offs

- **[Risk] Highlight-driven refresh may feel noisy when quickly skimming folders** → Acceptable for a notes browser; folders are small and refresh is local/fast.
- **[Risk] Duplicate refresh if both highlight and select fire for the same node** → Guard with a `current_path` check: skip refresh if path unchanged.
- **[Risk] Search/tag filter active while browsing tree** → Clear filters on tree navigation (existing behavior); document in spec.
