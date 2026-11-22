from __future__ import annotations

from idfkit.weather import StationIndex

index: StationIndex = ...  # type: ignore[assignment]
# --8<-- [start:example]
result = index.search("chicago ohare")[0]
print(result.station.dataset_variant)  # the newest dataset, e.g. TMYx.2011-2025

# Every dataset of the station, newest first
for s in result.variants:
    print(s.dataset_variant, s.dataset_years)

# Pick a specific year range
older = next(s for s in result.variants if s.dataset_years == (2007, 2021))
print(older.url)
# --8<-- [end:example]
