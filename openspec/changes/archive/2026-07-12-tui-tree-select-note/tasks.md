## 1. Selection sync

- [x] 1.1 Update `refresh_notes` to set `list_view.index` when auto-selecting the first note or a specific note by id
- [x] 1.2 Clear `selected_note` and detail panel when the folder has no notes

## 2. Tree navigation

- [x] 2.1 Extract folder-change logic into `_on_tree_folder(path)` with guard to skip if path unchanged
- [x] 2.2 Handle `Tree.NodeHighlighted` to refresh notes when cursor moves to a folder
- [x] 2.3 Handle tree root selection as `ROOT_PATH` in tree folder handler

## 3. Tests

- [x] 3.1 Add test: moving tree cursor to a folder updates detail with first note
- [x] 3.2 Add test: selecting tree root shows root-level note in detail
- [x] 3.3 Add test: empty folder shows empty-state message in detail
