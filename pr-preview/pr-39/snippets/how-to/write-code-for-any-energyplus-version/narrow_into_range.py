from __future__ import annotations

from typing import TypeAlias

from idfkit import IDFDocument
from idfkit.versioned import (
    IDFDocumentV9_6,
    IDFDocumentV22_1,
    IDFDocumentV22_2,
    IDFDocumentV23_1,
    IDFDocumentV23_2,
    IDFDocumentV24_1,
    IDFDocumentV24_2,
    IDFDocumentV25_1,
    IDFDocumentV25_2,
    IDFDocumentV26_1,
)

Since9_6: TypeAlias = (
    IDFDocumentV9_6
    | IDFDocumentV22_1
    | IDFDocumentV22_2
    | IDFDocumentV23_1
    | IDFDocumentV23_2
    | IDFDocumentV24_1
    | IDFDocumentV24_2
    | IDFDocumentV25_1
    | IDFDocumentV25_2
    | IDFDocumentV26_1
    | IDFDocument
)


def space_areas(doc: Since9_6) -> dict[str, float | None]:
    return {space.name: None for space in doc["Space"]}


# --8<-- [start:example]
from idfkit.document import AnyIDFDocument
from idfkit.versioned import as_version

SINCE_9_6 = (
    IDFDocumentV9_6,
    IDFDocumentV22_1,
    IDFDocumentV22_2,
    IDFDocumentV23_1,
    IDFDocumentV23_2,
    IDFDocumentV24_1,
    IDFDocumentV24_2,
    IDFDocumentV25_1,
    IDFDocumentV25_2,
    IDFDocumentV26_1,
    IDFDocument,
)


def as_since_9_6(doc: AnyIDFDocument) -> Since9_6 | None:
    """The document typed for its own release, or None for a release before 9.6."""
    for release in SINCE_9_6:
        try:
            return as_version(doc, release)  # checks the file's version at run time
        except TypeError:
            continue
    return None


def report_spaces(doc: AnyIDFDocument) -> dict[str, float | None]:
    since_9_6 = as_since_9_6(doc)
    if since_9_6 is None:
        return {}  # a model before 9.6 has no Space objects
    return space_areas(since_9_6)


# --8<-- [end:example]
