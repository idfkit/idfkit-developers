from __future__ import annotations

from idfkit.weather import StationIndex

index: StationIndex = ...  # type: ignore[assignment]
# --8<-- [start:example]
# Ask for a zone by its code. The code is parsed out of the label rather than
# read off the front of it, which matters: 2,162 of the 69,638 bundled records
# are labelled "7A - ASHRAE Climate Zone could not be determined" or "8A - ...",
# and neither 7A nor 8A is an ASHRAE zone, since zones 7 and 8 carry no suffix.
zone_4a = index.filter(climate_zone="4A")
print(f"Zone 4A stations: {len(zone_4a)}")

# Combine with the other keys, which all narrow together.
seattle_area = index.filter(climate_zone="4C", country="USA", state="WA")
print(f"Zone 4C in Washington: {len(seattle_area)}")

# The stations whose zone upstream could not determine are reachable, and only
# this way: no climate_zone value returns them. Asking for them is a separate
# question because the zone key's domain is already every real code, so a
# reserved string could not be told apart from one.
undetermined = index.filter(climate_zone_determined=False)
print(f"Zone not determined upstream: {len(undetermined)}")

# Pick the warmest design dry-bulb in a zone.
hottest = max(index.filter(climate_zone="5A", country="USA"), key=lambda s: s.cooling_design_db_c)
print(f"{hottest.display_name}: {hottest.cooling_design_db_c} °C / {hottest.cooling_design_db_f:.1f} °F")
# --8<-- [end:example]
