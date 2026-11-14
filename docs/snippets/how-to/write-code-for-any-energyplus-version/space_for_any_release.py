from __future__ import annotations

# --8<-- [start:example]
from typing import TYPE_CHECKING

from idfkit import IDFDocument
from idfkit.document import AnyIDFDocument
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
    as_version,
)

if TYPE_CHECKING:
    from idfkit.document import AnySpace

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


def label_spaces(doc: AnyIDFDocument, space_type: str) -> int:
    """Public API: takes a model of any release. Returns how many spaces were labelled."""
    if doc.version < (9, 6, 0):
        return 0  # the one place that decides what a model without Space gets
    recent = as_version(doc, SINCE_9_6)
    for space in recent["Space"]:
        _label(space, space_type)
    return len(recent["Space"])


def _label(space: AnySpace, space_type: str) -> None:
    """Takes a Space of any release that has one; no version logic here."""
    space.space_type = space_type


# --8<-- [end:example]
