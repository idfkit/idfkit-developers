from __future__ import annotations

from idfkit.simulation import SQLResult

sql: SQLResult | None = ...  # type: ignore[assignment]
# --8<-- [start:example]
# Design day results only (use for design_day=True simulations)
ts = sql.get_timeseries(
    "Zone Mean Air Temperature",
    "ZONE 1",
    environment="sizing",
)

# Run period results only
ts = sql.get_timeseries(
    "Zone Mean Air Temperature",
    "ZONE 1",
    environment="annual",
)

# All environments (design days, then run periods)
ts = sql.get_timeseries(
    "Zone Mean Air Temperature",
    "ZONE 1",
    environment="all",
)
# --8<-- [end:example]
