## MODIFIED Requirements

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

#### Scenario: Tree navigation updates detail

- **WHEN** the user moves the tree cursor to a folder (via keyboard or click)
- **THEN** the system updates the note list for that folder, auto-selects the first note (most recently updated), highlights it in the list, and displays its content in the detail panel

#### Scenario: Select root folder

- **WHEN** the user moves the tree cursor to the notes root
- **THEN** the system updates the note list and detail view for root-level notes

### Requirement: Note detail view

The system SHALL display the selected note's title, path, tags, timestamps, and body in a detail panel.

#### Scenario: Select note

- **WHEN** the user selects a note in the list
- **THEN** the system displays the note's full content in the detail panel

#### Scenario: Auto-select on folder change

- **WHEN** the user navigates to a folder that contains notes
- **THEN** the system auto-selects the first note in the list and displays its content in the detail panel without requiring a separate list click

#### Scenario: Empty directory

- **WHEN** the selected directory has no notes
- **THEN** the system displays a message prompting the user to create a note
