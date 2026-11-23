from __future__ import annotations

# --8<-- [start:example]
from idfkit import load_idf
from idfkit.versioned import IDFDocumentV24_1

# A file's release is only known once it is read, so the model is typed
# AnyIDFDocument: what every supported release has in common.
model = load_idf("building.idf")
zones = model.zones  # IDFCollection[AnyZone]

# Name the release to type the model as that release declares its objects.
model = load_idf("building.idf", as_type=IDFDocumentV24_1)
zones = model.zones  # IDFCollection[Zone]

# O(1) lookup by name returns the typed object
zone = zones["Office"]

# Field access with IDE autocomplete and type info
print(zone.x_origin)  # float | None
print(zone.multiplier)  # float | int | None

# Subscript access also works
all_zones = model["Zone"]
# --8<-- [end:example]
