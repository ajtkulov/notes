## MODIFIED Requirements

### Requirement: Edit note in TUI

The system SHALL allow editing the selected note's body in the TUI with explicit Save and Cancel controls.

#### Scenario: Edit note body

- **WHEN** the user presses `e` on a selected note
- **THEN** the system opens an inline text editor for the note body with Save and Cancel buttons visible

#### Scenario: Save edits via button

- **WHEN** the user clicks Save during editing
- **THEN** the system persists the edited body, exits edit mode, and displays the updated note in the detail view

#### Scenario: Save edits via keyboard

- **WHEN** the user presses `Ctrl+S` during editing
- **THEN** the system persists the edited body and exits edit mode

#### Scenario: Cancel edit via button

- **WHEN** the user clicks Cancel during editing
- **THEN** the system discards changes and returns to the detail view without saving

#### Scenario: Cancel edit via Escape

- **WHEN** the user presses `Escape` during editing
- **THEN** the system discards changes and returns to the detail view without saving

### Requirement: Keyboard shortcuts help

The system SHALL display available keyboard shortcuts.

#### Scenario: Show help

- **WHEN** the user presses `?`
- **THEN** the system displays an overlay listing all keyboard shortcuts, including Save (`Ctrl+S`) and Cancel (`Escape`) during edit mode
