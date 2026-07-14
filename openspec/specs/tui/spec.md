# tui

## Purpose

Interactive terminal UI for browsing the notes directory tree, managing notes, and filtering by search or tags.

## Requirements

### Requirement: TUI launch

The system SHALL provide an interactive terminal UI launched via `notes tui` that runs until the user quits.

#### Scenario: Launch TUI

- **WHEN** the TUI is launched
- **THEN** the system displays a full-screen interface with a directory tree, note list, and detail area

#### Scenario: Quit TUI

- **WHEN** the user presses `q`
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

#### Scenario: Tree navigation updates detail

- **WHEN** the user moves the tree cursor to a folder (via keyboard or click)
- **THEN** the system updates the note list for that folder, auto-selects the first note (most recently updated), highlights it in the list, and displays its content in the detail panel

#### Scenario: Select root folder

- **WHEN** the user moves the tree cursor to the notes root
- **THEN** the system updates the note list and detail view for root-level notes

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

#### Scenario: Auto-select on folder change

- **WHEN** the user navigates to a folder that contains notes
- **THEN** the system auto-selects the first note in the list and displays its content in the detail panel without requiring a separate list click

#### Scenario: Empty directory

- **WHEN** the selected directory has no notes
- **THEN** the system displays a message prompting the user to create a note

### Requirement: Create note in TUI

The system SHALL allow creating a new note via a single modal form with title, path, tags, and body fields.

#### Scenario: Open create form

- **WHEN** the user presses `n`
- **THEN** the system opens a create-note modal with fields for title, path, tags, and body

#### Scenario: Pre-filled path

- **WHEN** the create form opens while a directory is selected in the tree
- **THEN** the path field is pre-filled with the current directory path

#### Scenario: Body as large text area

- **WHEN** the create or edit form is displayed
- **THEN** the body field is a multi-line text area that occupies the majority of the form height

#### Scenario: Create note with all fields

- **WHEN** the user fills title, path, tags, and body and clicks Create
- **THEN** the system creates the note with normalized tags, saves it at the specified path, selects it in the list, and closes the modal

#### Scenario: Create with minimal fields

- **WHEN** the user enters only a title and clicks Create
- **THEN** the system creates the note with an empty body, no tags, and the pre-filled path

#### Scenario: Cancel create

- **WHEN** the user clicks Cancel or presses `Escape` on the create form
- **THEN** the system closes the modal without creating a note

#### Scenario: Title required

- **WHEN** the user attempts to create with an empty title
- **THEN** the system does not create a note and indicates that title is required

### Requirement: Edit note in TUI

The system SHALL allow editing a selected note via the same modal form used for create, with title, path, tags, and body fields pre-filled from the note.

#### Scenario: Open edit form

- **WHEN** the user presses `e` on a selected note
- **THEN** the system opens an edit modal with title, path, tags, and body pre-filled from the note

#### Scenario: Save edits via button

- **WHEN** the user modifies fields and clicks Save
- **THEN** the system persists all changes (including path moves), closes the modal, and displays the updated note

#### Scenario: Save edits via keyboard

- **WHEN** the user presses `Ctrl+S` on the edit form
- **THEN** the system persists all changes and closes the modal

#### Scenario: Cancel edit via button

- **WHEN** the user clicks Cancel on the edit form
- **THEN** the system closes the modal without saving changes

#### Scenario: Cancel edit via Escape

- **WHEN** the user presses `Escape` on the edit form
- **THEN** the system closes the modal without saving changes

#### Scenario: Edit path moves note

- **WHEN** the user changes the path field and clicks Save
- **THEN** the system moves the note to the new path and updates the note id accordingly

#### Scenario: Title required on edit

- **WHEN** the user clears the title and clicks Save
- **THEN** the system does not save and indicates that title is required

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

### Requirement: Copy note to clipboard

The system SHALL copy the selected note's body to the system clipboard when the user presses the copy shortcut.

#### Scenario: Copy selected note body

- **WHEN** a note is selected and the user presses `c`
- **THEN** the system copies the note body to the system clipboard

#### Scenario: No note selected

- **WHEN** no note is selected and the user presses `c`
- **THEN** the system does not copy anything

### Requirement: Keyboard shortcuts help

The system SHALL display available keyboard shortcuts.

#### Scenario: Show help

- **WHEN** the user presses `?`
- **THEN** the system displays an overlay listing shortcuts, including copy (`c` when a note is selected), create/edit form fields, and edit Save (`Ctrl+S`) and Cancel (`Escape`)
