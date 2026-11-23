from __future__ import annotations

# --8<-- [start:example]
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

# Every release from 9.6, the one that introduced Space, to the latest.
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
    """Each Space's floor area, as entered. Typed through every release from 9.6 on."""
    areas: dict[str, float | None] = {}
    for space in doc["Space"]:  # a typed Space of whichever release the document is
        area = space.floor_area
        areas[space.name] = area if isinstance(area, float) else None
    return areas


# --8<-- [end:example]
