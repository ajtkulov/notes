# note-storage

## Purpose

Core note model, filesystem tree persistence, configuration, and search for the local-first notes tracker.

## Requirements

### Requirement: Note model

The system SHALL represent each note as a data object with fields: id, title, body (markdown), path (relative directory from notes root), tags (set of strings), created_at (ISO 8601), and updated_at (ISO 8601).

#### Scenario: Create note with defaults

- **WHEN** a new note is created with only a title and body
- **THEN** the system assigns a unique id, sets path to `/` (notes root), sets created_at and updated_at to the current time, and initializes tags as an empty set

#### Scenario: Create note with path

- **WHEN** a note is created with path `work/meetings`
- **THEN** the system stores the note at `{notes_root}/work/meetings/{filename}.md` and sets path to `work/meetings`

#### Scenario: Tags as a set

- **WHEN** a note is created with tags `["work", "meeting", "work"]`
- **THEN** the system stores tags as the deduplicated lowercase set `{"work", "meeting"}`

### Requirement: Filesystem tree persistence

The system SHALL persist notes as `.md` files in a directory tree under the configured notes root. The note's path determines its directory; the filename is `{slug}-{short_id}.md`.

#### Scenario: Save note to disk

- **WHEN** a note with path `work/meetings` is saved
- **THEN** the system creates the directory `{notes_root}/work/meetings/` if missing and writes `{slug}-{short_id}.md` with YAML frontmatter (title, tags, created, updated) and markdown body

#### Scenario: Load note from disk

- **WHEN** a note file exists at `{notes_root}/personal/ideas/vacation-d5e6.md`
- **THEN** the system reads the file, parses frontmatter and body, and returns a Note with path `personal/ideas` and id `personal/ideas/vacation-d5e6`

#### Scenario: Delete note

- **WHEN** a note is deleted by id
- **THEN** the system removes the corresponding file and prunes empty parent directories up to the notes root

### Requirement: Move note between paths

The system SHALL support moving a note to a different path in the tree, updating its id accordingly.

#### Scenario: Move note

- **WHEN** note `work/meetings/standup-a3f2` is moved to path `personal/archive`
- **THEN** the system moves the file to `{notes_root}/personal/archive/standup-a3f2.md`, updates the note's path and id, and prunes empty directories at the old location

### Requirement: Notes directory configuration

The system SHALL resolve the notes storage directory from (in priority order): `NOTES_DIR` environment variable, `~/.notes/config.toml` setting, or default `~/.notes/notes/`.

#### Scenario: Default directory

- **WHEN** no configuration is set
- **THEN** the system uses `~/.notes/notes/` as the storage directory and creates it if missing

#### Scenario: Environment override

- **WHEN** `NOTES_DIR=/tmp/my-notes` is set
- **THEN** the system uses `/tmp/my-notes` as the storage directory

### Requirement: Note update tracking

The system SHALL update the `updated_at` timestamp whenever a note's title, body, tags, or path are modified.

#### Scenario: Update note body

- **WHEN** a note's body is edited and saved
- **THEN** the system sets updated_at to the current time and preserves the original created_at

### Requirement: List and filter notes

The system SHALL provide operations to list notes, optionally scoped to a path prefix and/or filtered by tag.

#### Scenario: List all notes

- **WHEN** all notes are requested
- **THEN** the system returns all notes sorted by updated_at descending

#### Scenario: List notes in path

- **WHEN** notes are requested with path `work/meetings`
- **THEN** the system returns only notes whose path equals `work/meetings` (not recursive by default)

#### Scenario: List notes recursively

- **WHEN** notes are requested with path `work` and recursive flag
- **THEN** the system returns all notes whose path starts with `work/`

#### Scenario: Filter by tag

- **WHEN** notes are requested with tag filter `"work"`
- **THEN** the system returns only notes whose tags set includes `"work"`

### Requirement: Tree navigation

The system SHALL expose the directory tree under the notes root for browsing folders and discovering notes.

#### Scenario: List directories at path

- **WHEN** tree children are requested for path `work`
- **THEN** the system returns subdirectory names (e.g., `meetings`, `projects`) and note filenames at that path

#### Scenario: Root tree

- **WHEN** tree children are requested for path `/`
- **THEN** the system returns top-level directories and notes at the notes root

### Requirement: Full-text search

The system SHALL search notes by matching a query string against title, tags, body, and path (case-insensitive).

#### Scenario: Search by content

- **WHEN** search query `"meeting"` is submitted
- **THEN** the system returns all notes whose title, tags, body, or path contain `"meeting"` (case-insensitive)

#### Scenario: No results

- **WHEN** search query matches no notes
- **THEN** the system returns an empty list
