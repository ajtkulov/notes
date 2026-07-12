## ADDED Requirements

### Requirement: TUI launch

The system SHALL provide an interactive terminal UI launched via `notes tui` that runs until the user quits.

#### Scenario: Launch TUI

- **WHEN** the TUI is launched
- **THEN** the system displays a full-screen interface with a directory tree, note list, and detail area

#### Scenario: Quit TUI

- **WHEN** the user presses `q` or `Ctrl+C`
- **THEN** the system exits the TUI and returns to the shell

### Requirement: Directory tree panel

The system SHALL display a navigable directory tree reflecting the notes filesystem layout.

#### Scenario: Display tree

- **WHEN** the TUI loads
- **THEN** the system shows a tree panel with folders under the notes root

#### Scenario: Expand folder

- **WHEN** the user selects a folder and presses Enter or right arrow
- **THEN** the system expands the folder to show subdirectories

#### Scenario: Navigate tree

- **WHEN** the user presses `j`/`k` or arrow keys in the tree panel
- **THEN** the system moves selection up or down among tree nodes

#### Scenario: Select folder

- **WHEN** the user selects a folder in the tree
- **THEN** the note list panel updates to show notes in that directory

### Requirement: Note list panel

The system SHALL display notes in the currently selected directory, sorted by most recently updated.

#### Scenario: Display notes in directory

- **WHEN** a folder is selected in the tree
- **THEN** the system shows notes in that directory with title, tags, and relative updated time

#### Scenario: Navigate note list

- **WHEN** the user presses `j`/`k` or arrow keys in the note list
- **THEN** the system moves the selection highlight up or down

### Requirement: Note detail view

The system SHALL display the selected note's title, path, tags, timestamps, and body in a detail panel.

#### Scenario: Select note

- **WHEN** the user selects a note in the list
- **THEN** the system displays the note's full content in the detail panel

#### Scenario: Empty directory

- **WHEN** the selected directory has no notes
- **THEN** the system displays a message prompting the user to create a note

### Requirement: Create note in TUI

The system SHALL allow creating a new note in the currently selected directory.

#### Scenario: Create new note

- **WHEN** the user presses `n`
- **THEN** the system opens an input form for title and body, creates the note in the current directory path on submit, and selects it in the list

### Requirement: Edit note in TUI

The system SHALL allow editing the selected note's body in the TUI.

#### Scenario: Edit note body

- **WHEN** the user presses `e` on a selected note
- **THEN** the system opens an inline text editor for the note body and saves on submit

#### Scenario: Cancel edit

- **WHEN** the user presses `Escape` during editing
- **THEN** the system discards changes and returns to the detail view

### Requirement: Move note in TUI

The system SHALL allow moving the selected note to a different directory.

#### Scenario: Move note

- **WHEN** the user presses `m` on a selected note
- **THEN** the system opens a path picker and moves the note to the selected directory on confirm

### Requirement: Delete note in TUI

The system SHALL allow deleting the selected note with confirmation.

#### Scenario: Delete with confirmation

- **WHEN** the user presses `d` on a selected note
- **THEN** the system shows a confirmation prompt and deletes the note on approval

### Requirement: Search in TUI

The system SHALL provide an in-TUI search overlay to filter notes across the entire tree.

#### Scenario: Open search

- **WHEN** the user presses `/`
- **THEN** the system opens a search input overlay at the bottom of the screen

#### Scenario: Filter results

- **WHEN** the user types a search query and presses Enter
- **THEN** the system filters the note list to show matching notes from all paths

#### Scenario: Clear search

- **WHEN** the user presses `Escape` in search mode
- **THEN** the system clears the filter and restores the directory-scoped note list

### Requirement: Tag filter in TUI

The system SHALL allow filtering notes by tag across the entire tree.

#### Scenario: Filter by tag

- **WHEN** the user presses `t`
- **THEN** the system shows a tag picker with all unique tags and filters the note list on selection

### Requirement: Keyboard shortcuts help

The system SHALL display available keyboard shortcuts.

#### Scenario: Show help

- **WHEN** the user presses `?`
- **THEN** the system displays an overlay listing all keyboard shortcuts
