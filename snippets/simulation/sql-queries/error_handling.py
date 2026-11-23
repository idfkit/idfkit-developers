from __future__ import annotations

from idfkit.exceptions import OutputNotFoundError, ResultLookupError
from idfkit.simulation import SimulationResult


# --8<-- [start:example]
def read_zone_temperature(result: SimulationResult) -> None:
    try:
        sql = result.sql
    except OutputNotFoundError as e:
        print(e)  # names the Output:SQLite object to add
        return

    # Get time series (raises ResultLookupError, a KeyError, if not found)
    try:
        ts = sql.get_timeseries("Nonexistent Variable", "ZONE 1")
    except ResultLookupError as e:
        print(e)  # the message names the closest variables and the reported keys
        print(e.suggestions)  # closest names, closest first
        print(e.available)  # keys or frequencies that could be passed instead


# --8<-- [end:example]
