## 1. Project Setup

- [x] 1.1 Create `pyproject.toml` with package metadata, Python 3.11+ requirement, and dependencies (typer, textual, python-frontmatter, rich)
- [x] 1.2 Create `src/notes/` package structure with `__init__.py` and `__main__.py`
- [x] 1.3 Configure entry points: `notes` CLI command and `python -m notes` support
- [x] 1.4 Create `tests/` directory with pytest configuration

## 2. Configuration

- [x] 2.1 Implement `config.py` — resolve notes directory from `NOTES_DIR` env, `~/.notes/config.toml`, or default `~/.notes/notes/`
- [x] 2.2 Auto-create notes directory on first access

## 3. Note Storage Core

- [x] 3.1 Implement `models.py` — `Note` dataclass with id, title, body, path, tags (`set[str]`), created_at, updated_at
- [x] 3.2 Implement `storage.py` — save note at `{root}/{path}/{slug}-{short_id}.md` with YAML frontmatter; auto-create directories
- [x] 3.3 Implement `storage.py` — load note from file, derive path and id from filesystem location
- [x] 3.4 Implement `storage.py` — delete note by id; prune empty parent directories
- [x] 3.5 Implement `storage.py` — move note between paths (update file location, path, id)
- [x] 3.6 Implement `storage.py` — list notes with optional path scope and recursive flag
- [x] 3.7 Implement `storage.py` — filter notes by tag (set membership)
- [x] 3.8 Implement id generation: `{path}/{slug}-{short_id}`; validate/sanitize path segments
- [x] 3.9 Normalize tags to lowercase set on write (dedupe)

## 4. Tree Navigation

- [x] 4.1 Implement `tree.py` — list subdirectories and notes at a given path
- [x] 4.2 Implement `tree.py` — build directory tree structure for TUI and `notes tree` command

## 5. Search

- [x] 5.1 Implement `search.py` — case-insensitive search across title, tags, body, and path
- [x] 5.2 Implement optional index cache in `~/.notes/.index.json` with mtime-based invalidation

## 6. CLI Implementation

- [x] 6.1 Implement `cli/app.py` — Typer app with global `--help` and notes directory option
- [x] 6.2 Implement `notes create` — with `--title`, `--body`, `--path`, `--tags`, and `--edit` flags
- [x] 6.3 Implement `notes list` — table output with id, title, path, tags, updated_at; `--path`, `--recursive`, `--tag` filters
- [x] 6.4 Implement `notes show <id>` — display note details including path; error on missing id
- [x] 6.5 Implement `notes edit <id>` — open `$EDITOR` or inline `--title`/`--body`/`--tags` update
- [x] 6.6 Implement `notes mv <id> <path>` — move note to new directory
- [x] 6.7 Implement `notes delete <id>` — with confirmation prompt and `--yes` flag
- [x] 6.8 Implement `notes search <query>` — print matching notes with path
- [x] 6.9 Implement `notes tree` — print directory tree with note counts
- [x] 6.10 Implement `notes tui` — delegate to TUI app

## 7. TUI Implementation

- [x] 7.1 Implement `tui/app.py` — Textual app with tree panel + note list + detail layout
- [x] 7.2 Implement directory tree panel — expandable folders, j/k navigation
- [x] 7.3 Implement note list panel — notes in selected directory, sorted by updated_at
- [x] 7.4 Implement note detail panel — show title, path, tags, timestamps, body
- [x] 7.5 Implement create note (`n`) — in current directory path
- [x] 7.6 Implement edit note (`e`) — inline text editor with save/cancel
- [x] 7.7 Implement move note (`m`) — path picker to relocate note
- [x] 7.8 Implement delete note (`d`) — confirmation prompt
- [x] 7.9 Implement search overlay (`/`) — filter notes across all paths
- [x] 7.10 Implement tag filter (`t`) — tag picker overlay
- [x] 7.11 Implement keyboard shortcuts help (`?`) overlay
- [x] 7.12 Implement quit (`q`, Ctrl+C)

## 8. Testing

- [x] 8.1 Write unit tests for note model, path handling, and tag set semantics
- [x] 8.2 Write unit tests for storage (create, read, update, delete, move, directory pruning)
- [x] 8.3 Write unit tests for tree navigation
- [x] 8.4 Write unit tests for search functionality
- [x] 8.5 Write unit tests for config resolution
- [x] 8.6 Write integration tests for CLI commands (using typer.testing.CliRunner)

## 9. Documentation

- [x] 9.1 Create README.md with installation, path vs tags explanation, CLI/TUI usage, and configuration
