from __future__ import annotations

from idfkit import IDFDocument

model: IDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
model.add("Zone", "Office", x_orgin=0)  # Raises: unknown field 'x_orgin'
# model.zones.add("Office", x_orgin=0)  # Typed creation: a type error before it runs

# Disable validation for bulk operations where performance matters
model.add("Zone", "Office", x_origin=0, validate=False)
# --8<-- [end:example]
