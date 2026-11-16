from __future__ import annotations

from idfkit import IDFDocument

doc: IDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
zone = doc["Zone"]["Office"]
zone.x_origin = 10.0
zone.y_origin = 5.0
# --8<-- [end:example]
