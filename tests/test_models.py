"""Tests for the Note model."""

from datetime import datetime, timezone

import pytest

from notes.models import (
    Note,
    build_note_id,
    normalize_path,
    normalize_tags,
    parse_note_id,
    slugify,
)


def test_create_note_with_defaults():
    note = Note.create(title="Hello", body="World")

    assert note.title == "Hello"
    assert note.body == "World"
    assert note.path == ""
    assert note.tags == set()
    assert len(note.id.rsplit("-", 1)[-1]) == 4
    assert note.created_at.tzinfo is not None
    assert note.updated_at == note.created_at


def test_create_note_with_path():
    note = Note.create(title="Standup", body="Updates", path="work/meetings")

    assert note.path == "work/meetings"
    assert note.id.startswith("work/meetings/standup-")


def test_create_note_with_tags_deduplicates_and_lowercases():
    note = Note.create(title="Tagged", body="Body", tags=["Work", "meeting", "work"])

    assert note.tags == {"work", "meeting"}


def test_normalize_path_root():
    assert normalize_path("") == ""
    assert normalize_path("/") == ""
    assert normalize_path(".") == ""


def test_normalize_path_nested():
    assert normalize_path("work/meetings/") == "work/meetings"
    assert normalize_path("/work/meetings") == "work/meetings"


def test_normalize_path_rejects_parent_segments():
    with pytest.raises(ValueError, match="Invalid path segment"):
        normalize_path("work/../secret")


def test_build_and_parse_note_id():
    note_id = build_note_id("work/meetings", "standup", "a3f2")

    assert note_id == "work/meetings/standup-a3f2"
    assert parse_note_id(note_id) == ("work/meetings", "standup-a3f2")


def test_build_and_parse_root_note_id():
    note_id = build_note_id("", "vacation", "d5e6")

    assert note_id == "vacation-d5e6"
    assert parse_note_id(note_id) == ("", "vacation-d5e6")


def test_note_rejects_mismatched_id_and_path():
    with pytest.raises(ValueError, match="does not match"):
        Note(
            id="personal/ideas/vacation-d5e6",
            title="Vacation",
            body="Plans",
            path="work/meetings",
        )


def test_with_updates_refreshes_updated_at():
    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    note = Note.create(
        title="Original",
        body="Body",
        created_at=created,
        updated_at=created,
    )

    updated = note.with_updates(body="Changed")

    assert updated.body == "Changed"
    assert updated.created_at == created
    assert updated.updated_at > created


def test_with_updates_moves_path_and_id():
    note = Note.create(title="Standup", body="Body", path="work/meetings", short_id="a3f2")

    moved = note.with_updates(path="personal/archive")

    assert moved.path == "personal/archive"
    assert moved.id == "personal/archive/standup-a3f2"


def test_has_tag():
    note = Note.create(title="Tagged", body="Body", tags=["work"])

    assert note.has_tag("Work") is True
    assert note.has_tag("personal") is False


def test_slugify():
    assert slugify("Meeting Notes!") == "meeting-notes"
    assert slugify("---") == "note"
