from __future__ import annotations

# --8<-- [start:example]
from idfkit.document import AnyIDFDocument
from idfkit.versioned import IDFDocumentV9_4, IDFDocumentV9_5, as_version


def set_people_zone(doc: AnyIDFDocument, people: str, zone: str) -> None:
    """Point a People object at a zone in a 9.4 or later model.

    9.6 renamed the field, so AnyIDFDocument offers neither name. as_version takes one
    release, so each release before the rename gets its own branch.
    """
    if doc.version[:2] == (9, 4):
        as_version(doc, IDFDocumentV9_4)["People"][people].update(zone_or_zonelist_name=zone)
    elif doc.version[:2] == (9, 5):
        as_version(doc, IDFDocumentV9_5)["People"][people].update(zone_or_zonelist_name=zone)
    elif doc.version >= (9, 6, 0):
        # Unchecked item access: no typed name fits every release from 9.6 on.
        doc["People"][people]["zone_or_zonelist_or_space_or_spacelist_name"] = zone
    else:
        msg = f"EnergyPlus {doc.version} is not handled"
        raise NotImplementedError(msg)


# --8<-- [end:example]
