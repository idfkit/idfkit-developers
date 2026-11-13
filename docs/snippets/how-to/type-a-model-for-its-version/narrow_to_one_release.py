from __future__ import annotations

# --8<-- [start:example]
from idfkit.document import AnyIDFDocument
from idfkit.versioned import IDFDocumentV9_4, as_version


def assign_people_to_zone(doc: AnyIDFDocument, people: str, zone: str) -> None:
    """Point a People object at a zone, under whichever name the model's release uses."""
    if doc.version[:2] == (9, 4):
        legacy = as_version(doc, IDFDocumentV9_4)
        legacy["People"][people].update(zone_or_zonelist_name=zone)
    else:
        doc["People"][people]["zone_or_zonelist_or_space_or_spacelist_name"] = zone


# --8<-- [end:example]
