"""Tests for TUI clipboard helpers."""

from notes.tui.clipboard import copy_text


def test_copy_text_uses_pbcopy_on_macos(monkeypatch):
    captured: list[bytes] = []

    def fake_run(command, input, check):  # noqa: ANN001
        captured.append(input)
        return None

    monkeypatch.setattr("notes.tui.clipboard.platform.system", lambda: "Darwin")
    monkeypatch.setattr("notes.tui.clipboard.subprocess.run", fake_run)

    assert copy_text("hello") is True
    assert captured == [b"hello"]
