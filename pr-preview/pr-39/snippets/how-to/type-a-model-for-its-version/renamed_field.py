from __future__ import annotations

# --8<-- [start:example]
from idfkit import IDFDocument
from idfkit.document import AnyIDFDocument
from idfkit.versioned import (
    IDFDocumentV8_9,
    IDFDocumentV9_0,
    IDFDocumentV9_1,
    IDFDocumentV9_2,
    IDFDocumentV9_3,
    IDFDocumentV9_4,
    IDFDocumentV9_5,
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

# Tuples of release types, as isinstance takes: as_version accepts a document of any of them.
BEFORE_9_6 = (
    IDFDocumentV8_9,
    IDFDocumentV9_0,
    IDFDocumentV9_1,
    IDFDocumentV9_2,
    IDFDocumentV9_3,
    IDFDocumentV9_4,
    IDFDocumentV9_5,
)
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


def set_people_zone(doc: AnyIDFDocument, people: str, zone: str) -> None:
    """Point a People object at a zone, under whichever name the model's release uses."""
    if doc.version < (9, 6, 0):
        as_version(doc, BEFORE_9_6)["People"][people].update(zone_or_zonelist_name=zone)
    else:
        as_version(doc, SINCE_9_6)["People"][people].update(zone_or_zonelist_or_space_or_spacelist_name=zone)


# --8<-- [end:example]
