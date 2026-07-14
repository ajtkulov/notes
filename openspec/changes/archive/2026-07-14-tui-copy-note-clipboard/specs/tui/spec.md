## ADDED Requirements

### Requirement: Copy note to clipboard

The system SHALL copy the selected note's body to the system clipboard when the user presses the copy shortcut.

#### Scenario: Copy selected note body

- **WHEN** a note is selected and the user presses `Ctrl+C` (or `Cmd+C` on macOS)
- **THEN** the system copies the note body to the system clipboard

#### Scenario: No note selected

- **WHEN** no note is selected and the user presses `Ctrl+C`
- **THEN** the system does not copy anything

## MODIFIED Requirements

### Requirement: TUI launch

The system SHALL provide an interactive terminal UI launched via `notes tui` that runs until the user quits.

#### Scenario: Launch TUI

- **WHEN** the TUI is launched
- **THEN** the system displays a full-screen interface with a directory tree, note list, and detail area

#### Scenario: Quit TUI

- **WHEN** the user presses `q`
- **THEN** the system exits the TUI and returns to the shell

### Requirement: Keyboard shortcuts help

The system SHALL display available keyboard shortcuts.

#### Scenario: Show help

- **WHEN** the user presses `?`
- **THEN** the system displays an overlay listing shortcuts, including copy (`Ctrl+C` / `Cmd+C` when a note is selected), create/edit form fields, and edit Save (`Ctrl+S`) and Cancel (`Escape`)
