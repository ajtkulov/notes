"""Directory tree navigation for notes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from notes.models import ROOT_PATH, normalize_path
from notes.storage import NoteStore


@dataclass
class TreeNode:
    """A node in the notes directory tree."""

    name: str
    path: str
    note_count: int = 0
    children: list[TreeNode] = field(default_factory=list)


@dataclass
class PathListing:
    """Directories and note ids at a given path."""

    path: str
    directories: list[str]
    note_ids: list[str]


def list_path(store: NoteStore, path: str = ROOT_PATH) -> PathListing:
    """List subdirectories and note ids at the given path."""
    normalized = normalize_path(path)
    base = store.root if normalized == ROOT_PATH else store.root / normalized
    if not base.exists():
        return PathListing(path=normalized, directories=[], note_ids=[])

    directories = sorted(
        entry.name
        for entry in base.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    )
    note_ids = sorted(
        store._note_id_from_file(entry)
        for entry in base.iterdir()
        if entry.is_file() and entry.suffix == ".md"
    )
    return PathListing(path=normalized, directories=directories, note_ids=note_ids)


def build_tree(store: NoteStore) -> TreeNode:
    """Build a directory tree with note counts per folder."""

    def build_node(path: str, name: str) -> TreeNode:
        listing = list_path(store, path)
        note_count = len(listing.note_ids)
        children = [build_node(f"{path}/{directory}" if path else directory, directory) for directory in listing.directories]
        for child in children:
            note_count += child.note_count
        return TreeNode(name=name or "/", path=path, note_count=note_count, children=children)

    return build_node(ROOT_PATH, "/")


def format_tree(node: TreeNode, prefix: str = "", is_root: bool = True) -> list[str]:
    """Render a tree node as indented text lines."""
    if is_root:
        lines = [f"/ ({node.note_count})"]
        child_prefix = ""
    else:
        lines = [f"{prefix}{node.name} ({node.note_count})"]
        child_prefix = prefix

    for index, child in enumerate(node.children):
        is_last = index == len(node.children) - 1
        branch = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "
        lines.append(f"{child_prefix}{branch}{child.name} ({child.note_count})")
        if child.children:
            lines.extend(format_tree(child, child_prefix + extension, is_root=False)[1:])
    return lines
