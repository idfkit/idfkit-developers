from __future__ import annotations

from idfkit.weather import StationIndex

index: StationIndex = ...  # type: ignore[assignment]
# --8<-- [start:example]
# City name
results = index.search("New York")

# Airport code pattern
results = index.search("JFK")

# WMO number
results = index.search("725300")

# City + state or country code, as you would write an address
results = index.search("Denver, CO")
results = index.search("London, GBR")

# Accents are optional either way
results = index.search("Montréal")
# --8<-- [end:example]
