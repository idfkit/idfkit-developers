from __future__ import annotations

# --8<-- [start:example]
from typing import TYPE_CHECKING

from idfkit.document import AnyIDFDocument

if TYPE_CHECKING:
    # The object classes exist only in the stubs: import them for the type checker alone.
    from idfkit.document import Construction


def layer_names(construction: Construction) -> list[str]:
    """Construction is declared the same way in every release, so its class fits them all."""
    return [name for name in (construction.outside_layer, construction.layer_2) if name]


def tall_zones(doc: AnyIDFDocument, minimum: float) -> list[str]:
    """Zone changed between releases: take the document and let it type each zone."""
    return [
        zone.name for zone in doc["Zone"] if isinstance(zone.ceiling_height, float) and zone.ceiling_height >= minimum
    ]


# --8<-- [end:example]
