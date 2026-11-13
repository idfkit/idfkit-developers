from __future__ import annotations

# --8<-- [start:example]
from idfkit.weather import GeocodingError, geocode

try:
    lat, lon = geocode("Nonexistent Place XYZ123")
except GeocodingError as e:
    if e.kind == "not-found":
        # Nominatim answered and has no such place: retrying will not help.
        print(f"No place matches that address: {e}")
    else:
        # "unreachable", "http" (e.status holds the code) or "invalid-response".
        print(f"The geocoding service could not be reached; try again later: {e}")
# --8<-- [end:example]
