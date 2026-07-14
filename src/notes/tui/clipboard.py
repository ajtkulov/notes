"""System clipboard helpers for the TUI."""

from __future__ import annotations

import platform
import subprocess


def copy_text(text: str) -> bool:
    """Copy text to the system clipboard. Returns True on success."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return True
        if system == "Linux":
            for command in (
                ["wl-copy"],
                ["xclip", "-selection", "clipboard"],
                ["xsel", "--clipboard", "--input"],
            ):
                try:
                    subprocess.run(command, input=text.encode("utf-8"), check=True)
                    return True
                except FileNotFoundError:
                    continue
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    return False
