"""Verified Python code for the "Build a type-checked script" tutorial.

Step 2 of the page shows the header, zones and save regions together, and step 5 inserts the
convection region before the save, so this file, in this order, is the finished script. The
deliberate mistakes the page makes in steps 4 and 5 are shown literally on the page, not here:
this file has to pass pyright strict.
"""

# --8<-- [start:header]
from __future__ import annotations

from typing import TYPE_CHECKING

from idfkit import new_document, save_idf

if TYPE_CHECKING:
    from idfkit.document import Zone


def describe(zone: Zone) -> str:
    return f"{zone.name}: ceiling {zone.ceiling_height} m"


# --8<-- [end:header]

# --8<-- [start:zones]
model = new_document()
model.add("Zone", "Office", ceiling_height=2.7)
model.add("Zone", "Lobby", ceiling_height=4.0)

for zone in model.zones:
    print(describe(zone))
# --8<-- [end:zones]

# --8<-- [start:convection]
office = model["Zone"]["Office"]
office.zone_inside_convection_algorithm = "TARP"
# --8<-- [end:convection]

# --8<-- [start:save]

save_idf(model, "offices.idf")
print(f"Saved {len(model.zones)} zones to offices.idf")
# --8<-- [end:save]
