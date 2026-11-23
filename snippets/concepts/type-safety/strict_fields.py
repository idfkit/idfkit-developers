from __future__ import annotations

# --8<-- [start:example]
from idfkit import new_document

# Strict field access is on by default
doc = new_document()

zone = doc.zones.add("Office")
zone.x_origin = 0.0  # OK: a valid field and a valid value

# zone.x_orgin = 0.0    # InvalidFieldError: typo caught immediately
# zone.multiplier = 0   # ValidationFailedError: below the minimum of 1

# Also the default when loading files
# model = load_idf("building.idf")
# model = load_epjson("building.epJSON")
# --8<-- [end:example]
