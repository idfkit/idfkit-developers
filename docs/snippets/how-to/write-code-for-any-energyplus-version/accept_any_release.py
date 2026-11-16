from __future__ import annotations

# --8<-- [start:example]
from idfkit import load_idf
from idfkit.document import AnyIDFDocument
from idfkit.versioned import IDFDocumentV9_4, as_version


def zone_ceiling_heights(doc: AnyIDFDocument) -> dict[str, float | None]:
    """Each zone's ceiling height, for a model of any supported release."""
    heights: dict[str, float | None] = {}
    for zone in doc["Zone"]:  # inferred from the document; no Zone annotation needed
        height = zone.ceiling_height  # float | "Autocalculate" | "" | None, as every release reads it
        heights[zone.name] = height if isinstance(height, float) else None
    return heights


zone_ceiling_heights(load_idf("model.idf"))  # a latest-release model
zone_ceiling_heights(as_version(load_idf("legacy.idf"), IDFDocumentV9_4))  # a 9.4 model
# --8<-- [end:example]
