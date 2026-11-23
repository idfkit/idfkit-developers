from __future__ import annotations

# --8<-- [start:example]
from idfkit import new_document
from idfkit.versioned import IDFDocumentV25_2

doc = new_document(IDFDocumentV25_2)

# SpaceHVAC:ZoneReturnMixer was added in EnergyPlus 24.2.0
# IDE docstring shows: "Since: 24.2.0"
mixer = doc["SpaceHVAC:ZoneReturnMixer"].add(
    "Return Mixer 1",
    zone_name="Office",
    zone_return_air_node_name="Office Return Node",
)
# --8<-- [end:example]
