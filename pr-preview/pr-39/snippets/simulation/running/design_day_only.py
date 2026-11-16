from __future__ import annotations

from idfkit import IDFDocument
from idfkit.simulation import simulate

model: IDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
result = simulate(model, design_day=True)
# --8<-- [end:example]
