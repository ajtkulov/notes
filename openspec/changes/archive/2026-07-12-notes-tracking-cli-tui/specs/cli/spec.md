## ADDED Requirements

### Requirement: CLI entry point

The system SHALL provide a `notes` command-line tool installable via pip with subcommands for note operations.

#### Scenario: Show help

- **WHEN** `notes --help` is run
- **THEN** the system displays available subcommands and global options

#### Scenario: No arguments

- **WHEN** `notes` is run with no subcommand
- **THEN** the system displays help text

### Requirement: Create note command

The system SHALL provide `notes create` to create a new note from the command line.

#### Scenario: Create with title and body

- **WHEN** `notes create --title "My Note" --body "Content here"` is run
- **THEN** the system creates a new note at the root path and prints its id

#### Scenario: Create with path

- **WHEN** `notes create --path work/meetings --title "Standup" --body "Updates"` is run
- **THEN** the system creates the note at path `work/meetings` and prints its id

#### Scenario: Create with tags

- **WHEN** `notes create --title "Standup" --body "Updates" --tags work,meeting` is run
- **THEN** the system creates a note with tags `{"work", "meeting"}`

#### Scenario: Create with editor

- **WHEN** `notes create --title "Draft" --edit` is run
- **THEN** the system opens `$EDITOR` for body input and saves the note with the editor content

### Requirement: List notes command

The system SHALL provide `notes list` to display notes in the terminal.

#### Scenario: List all notes

- **WHEN** `notes list` is run
- **THEN** the system prints a table of notes showing id, title, path, tags, and updated_at

#### Scenario: List in path

- **WHEN** `notes list --path work/meetings` is run
- **THEN** the system prints only notes at path `work/meetings`

#### Scenario: List recursively

- **WHEN** `notes list --path work --recursive` is run
- **THEN** the system prints all notes under `work/` including nested paths

#### Scenario: List filtered by tag

- **WHEN** `notes list --tag work` is run
- **THEN** the system prints only notes whose tags include `"work"`

### Requirement: Show note command

The system SHALL provide `notes show <id>` to display a single note.

#### Scenario: Show existing note

- **WHEN** `notes show work/meetings/standup-a3f2` is run
- **THEN** the system prints the note's title, path, tags, timestamps, and body

#### Scenario: Show nonexistent note

- **WHEN** `notes show nonexistent-id` is run
- **THEN** the system prints an error message and exits with code 1

### Requirement: Edit note command

The system SHALL provide `notes edit <id>` to modify an existing note.

#### Scenario: Edit in external editor

- **WHEN** `notes edit work/meetings/standup-a3f2` is run
- **THEN** the system opens the note body in `$EDITOR` and saves changes on exit

#### Scenario: Edit title inline

- **WHEN** `notes edit work/meetings/standup-a3f2 --title "New Title"` is run
- **THEN** the system updates the note title without opening an editor

#### Scenario: Edit tags inline

- **WHEN** `notes edit work/meetings/standup-a3f2 --tags urgent,done` is run
- **THEN** the system replaces the note's tags with `{"urgent", "done"}`

### Requirement: Move note command

The system SHALL provide `notes mv <id> <path>` to move a note to a different directory in the tree.

#### Scenario: Move note

- **WHEN** `notes mv work/meetings/standup-a3f2 personal/archive` is run
- **THEN** the system moves the note to path `personal/archive` and prints the new id

### Requirement: Delete note command

The system SHALL provide `notes delete <id>` to remove a note.

#### Scenario: Delete with confirmation

- **WHEN** `notes delete work/meetings/standup-a3f2` is run
- **THEN** the system prompts for confirmation and deletes the note on approval

#### Scenario: Force delete

- **WHEN** `notes delete work/meetings/standup-a3f2 --yes` is run
- **THEN** the system deletes the note without prompting

### Requirement: Search command

The system SHALL provide `notes search <query>` to find notes by text.

#### Scenario: Search with results

- **WHEN** `notes search "project alpha"` is run
- **THEN** the system prints matching notes in a list format showing id, path, and title

#### Scenario: Search with no results

- **WHEN** `notes search "xyznonexistent"` is run
- **THEN** the system prints "No notes found" and exits with code 0

### Requirement: Tree command

The system SHALL provide `notes tree` to display the directory tree.

#### Scenario: Show tree

- **WHEN** `notes tree` is run
- **THEN** the system prints the directory tree under the notes root with note counts per folder

### Requirement: Launch TUI command

The system SHALL provide `notes tui` to launch the interactive terminal UI.

#### Scenario: Launch TUI

- **WHEN** `notes tui` is run
- **THEN** the system starts the Textual TUI application
