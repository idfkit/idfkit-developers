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

# A tuple of the same release types, for as_version; the alias above is for annotations.
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


def report_spaces(doc: AnyIDFDocument) -> dict[str, float | None]:
    if doc.version < (9, 6, 0):
        return {}  # a model before 9.6 has no Space objects
    return space_areas(as_version(doc, SINCE_9_6))  # checked again at run time


# --8<-- [end:example]
