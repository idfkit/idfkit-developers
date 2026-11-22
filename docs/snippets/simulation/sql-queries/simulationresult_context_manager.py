from __future__ import annotations

from idfkit import IDFDocument
from idfkit.simulation import simulate

model: IDFDocument = ...  # type: ignore[assignment]
weather: str = ...  # type: ignore[assignment]
# --8<-- [start:example]
with simulate(model, weather) as result:
    ts = result.sql.get_timeseries("Zone Mean Air Temperature", "ZONE 1")
    # On exit: SQLite connection closed, temporary run directory deleted
# --8<-- [end:example]
