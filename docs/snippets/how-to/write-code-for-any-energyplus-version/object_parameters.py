from __future__ import annotations

# --8<-- [start:example]
from typing import TYPE_CHECKING

from idfkit import load_idf
from idfkit.document import AnyIDFDocument
from idfkit.versioned import IDFDocumentV9_4, as_version

if TYPE_CHECKING:
    # The object classes exist only in the stubs: import them for the type checker alone.
    from idfkit.document import AnyConstruction, AnyZone


def ceiling_height(zone: AnyZone) -> float | None:
    """A zone's ceiling height as entered, for a zone of any release."""
    height = zone.ceiling_height  # only fields every release has
    return height if isinstance(height, float) else None


def layer_names(construction: AnyConstruction) -> list[str]:
    return [name for name in (construction.outside_layer, construction.layer_2) if name]


def tall_zones(doc: AnyIDFDocument, minimum: float) -> list[str]:
    return [zone.name for zone in doc["Zone"] if (ceiling_height(zone) or 0.0) >= minimum]


ceiling_height(load_idf("model.idf")["Zone"]["Office"])  # a latest-release Zone
ceiling_height(as_version(load_idf("legacy.idf"), IDFDocumentV9_4)["Zone"]["Office"])  # a 9.4 zone
# --8<-- [end:example]
