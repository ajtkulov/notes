## MODIFIED Requirements

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

## MODIFIED Requirements

### Requirement: Keyboard shortcuts help

The system SHALL display available keyboard shortcuts.

#### Scenario: Show help

- **WHEN** the user presses `?`
- **THEN** the system displays an overlay listing shortcuts, including that create/edit forms use title, path, tags, and body fields, and edit supports Save (`Ctrl+S`) and Cancel (`Escape`)
