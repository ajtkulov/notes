## Why

Developers and knowledge workers need a fast, local-first way to capture, organize, and retrieve notes without leaving the terminal. Existing GUI note apps break flow; plain text files lack structure and search. A Python CLI/TUI notes tracker fills this gap with keyboard-driven workflows, a filesystem tree for hierarchical organization, and tags for cross-cutting labels.

## What Changes

- Add a new Python application for local note tracking with markdown file storage
- Organize notes in a **filesystem tree** — directories under the notes root represent folders; each note has a relative path (e.g., `work/meetings/`)
- Support **tags as a set of strings** — unordered, unique labels stored in frontmatter, independent of path
- Provide a CLI for scripting and quick one-shot commands (create, list, search, edit, delete, move)
- Provide a TUI for interactive tree browsing, editing, and navigation of notes
- Support full-text search and note metadata (created/updated timestamps)
- Store notes as individual markdown files in a configurable directory (default: `~/.notes/notes/`)

## Capabilities

### New Capabilities

- `note-storage`: Core note model (path + tags), markdown persistence, CRUD operations, tree navigation, and metadata
- `cli`: Command-line interface with subcommands for all note operations
- `tui`: Terminal UI for interactive tree browsing, editing, and management

### Modified Capabilities

- (none — greenfield project)

## Impact

- New Python package and project structure (pyproject.toml, src layout)
- Dependencies: CLI framework (Typer), TUI framework (Textual), python-frontmatter, rich
- No external services; all data stored locally on disk as a directory tree
- No breaking changes (new project)
