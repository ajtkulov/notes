# Notes

Local-first notes tracker for the terminal. Notes are stored as markdown files in a directory tree, with optional tags for cross-cutting labels.

## Path vs tags

| | Path | Tags |
|---|---|---|
| Structure | Tree (one folder per note) | Set of labels |
| Stored in | Filesystem directories | YAML frontmatter |
| Example | `work/meetings/` | `work`, `urgent` |

**Path** answers "where does this note live?" **Tags** answer "what themes apply?"

## Installation

```bash
pip install -e ".[dev]"
```

## Configuration

Notes directory resolution order:

1. `--notes-dir` CLI flag
2. `NOTES_DIR` environment variable
3. `~/.notes/config.toml` with `notes_dir = "/path/to/notes"`
4. Default: `~/.notes/notes/`

Example config:

```toml
notes_dir = "~/Documents/notes"
```

## CLI usage

```bash
# Create
notes create --title "Standup" --body "Updates" --path work/meetings --tags work,meeting

# List and filter
notes list
notes list --path work --recursive
notes list --tag work

# Show, edit, move, delete
notes show work/meetings/standup-a3f2
notes edit work/meetings/standup-a3f2 --title "New title"
notes mv work/meetings/standup-a3f2 personal/archive
notes delete work/meetings/standup-a3f2 --yes

# Search and browse tree
notes search "project alpha"
notes tree

# Launch TUI
notes tui
```

Run `notes --help` for all commands.

## TUI

`notes tui` opens an interactive interface:

- Left: directory tree
- Right: note list and detail view
- `n` create, `e` edit, `d` delete, `m` move
- `/` search, `t` tag filter, `?` help, `q` quit

## Development

```bash
pytest
python -m notes --help
```

## Storage format

Each note is a `.md` file:

```markdown
---
title: Standup
tags:
  - work
  - meeting
created: 2026-07-12T12:00:00+00:00
updated: 2026-07-12T12:00:00+00:00
---

Note body in markdown.
```

Files live at `{notes_root}/{path}/{slug}-{id}.md`.
