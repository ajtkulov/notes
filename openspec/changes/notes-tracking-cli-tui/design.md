## Context

This is a greenfield Python project for terminal-based note tracking. Notes are stored as markdown files in a directory tree on the local filesystem, accessed via both a scriptable CLI and an interactive TUI. The project targets Python 3.11+ and follows a standard `src/` layout with a single installable package.

## Goals / Non-Goals

**Goals:**

- Fast, keyboard-driven note capture and retrieval from the terminal
- Local-first storage with human-readable markdown files (portable, git-friendly)
- **Tree-based organization** via filesystem paths — directories are folders, notes live inside them
- **Tags as a set of strings** — cross-cutting labels independent of path; unordered, unique, normalized
- Shared core library used by both CLI and TUI interfaces
- Full-text search across title, tags, body, and path
- Configurable notes directory via environment variable or config file

**Non-Goals:**

- Cloud sync, multi-user collaboration, or web UI
- Rich WYSIWYG editing (plain markdown only)
- Mobile or desktop GUI
- Encryption at rest (may be added later)
- Import/export from third-party note apps (v1)
- Symlinks or virtual folders (path = real directory only)

## Decisions

### 1. Storage: Directory tree + markdown with YAML frontmatter

Notes live in a directory tree under the configured notes root. Each note is a `.md` file at `{root}/{path}/{filename}.md`. YAML frontmatter holds metadata (title, tags, created, updated); body is markdown.

**Example layout:**
```
~/.notes/notes/
├── work/
│   ├── meetings/
│   │   └── standup-a3f2.md
│   └── projects/
│       └── alpha-b1c4.md
└── personal/
    └── ideas/
        └── vacation-d5e6.md
```

**Rationale:** The filesystem tree is the source of truth for hierarchy. Users can browse/edit with any file manager or editor. Frontmatter adds structured metadata without a database.

**Alternatives considered:**
- Flat storage with path in frontmatter only — tree not visible outside the app
- SQLite — opaque, harder to edit outside the app

### 2. Path vs tags — two orthogonal axes

| | Path | Tags |
|---|---|---|
| Structure | Tree (one location per note) | Set (many labels per note) |
| Stored in | Filesystem directory | YAML frontmatter |
| Example | `work/meetings/` | `{"urgent", "standup"}` |
| Use case | "Where does this live?" | "What themes apply?" |

A note MUST have exactly one path (defaults to `/` i.e. notes root). A note MAY have zero or more tags.

### 3. Tags as a set of strings

Tags are stored as a YAML list in frontmatter but treated as an unordered set in code:
- Normalized to lowercase on write
- Deduplicated on write
- No ordering semantics

**Rationale:** Tags label notes across the tree; set semantics prevent duplicates and avoid implying order.

### 4. Note identity: relative path + filename

Each note's id is derived from its location: `{path}/{slug}-{short_id}` (e.g., `work/meetings/standup-a3f2`). Moving a note changes its id (path is part of identity).

**Alternatives considered:**
- UUID in frontmatter, stable across moves — adds indirection; defer to v2 if needed

### 5. CLI framework: Typer

Typer provides type-hint-based command definitions, auto-generated help, and good UX for subcommands.

### 6. TUI framework: Textual

Textual supports tree widgets (`Tree`/`DirectoryTree`) for folder navigation plus a detail pane.

**Layout:**
```
┌─────────────────┬──────────────────────────┐
│  Tree (paths)   │  Note list (current dir) │
│  ▼ work         │  standup-a3f2  2h ago    │
│    ▼ meetings   │  retro-b1c4    1d ago    │
│    projects     │                          │
│  personal       ├──────────────────────────┤
│                 │  Detail / Editor           │
└─────────────────┴──────────────────────────┘
```

### 7. Project layout

```
notes/
├── pyproject.toml
├── src/
│   └── notes/
│       ├── __init__.py
│       ├── __main__.py
│       ├── models.py         # Note dataclass (path, tags: set[str])
│       ├── storage.py        # CRUD, file I/O, move
│       ├── tree.py           # Directory tree operations
│       ├── search.py         # Full-text search
│       ├── config.py         # Notes dir resolution
│       ├── cli/
│       │   └── app.py
│       └── tui/
│           └── app.py
└── tests/
```

### 8. Search: in-memory scan with optional index cache

Scan all note files; match against title, tags, body, and path. Cache index in `~/.notes/.index.json`; rebuild if any file mtime differs.

## Risks / Trade-offs

- **[Risk] Moving notes changes id** → Mitigation: `notes mv` command; document that id includes path
- **[Risk] Large trees slow to render** → Mitigation: lazy-load tree nodes in TUI; list only current directory
- **[Risk] Concurrent edits corrupt files** → Mitigation: single-user assumption; warn on stale mtime
- **[Risk] Invalid path characters** → Mitigation: validate/sanitize path segments on create and move
- **[Trade-off] Path and tags overlap conceptually** → Document clearly: path = location, tags = labels

## Migration Plan

N/A — greenfield project. Initial install via `pip install -e .` creates notes directory on first use.

## Open Questions

- Should the TUI support split-pane live preview of rendered markdown? (Defer to post-v1)
- Should empty directories be preserved or auto-pruned on delete? (Recommend: prune empty dirs on note delete/move)
