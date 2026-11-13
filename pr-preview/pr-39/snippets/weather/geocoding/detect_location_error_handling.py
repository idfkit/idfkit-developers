from __future__ import annotations

# --8<-- [start:example]
from idfkit.weather import GeocodingError, detect_location

try:
    lat, lon = detect_location()
except GeocodingError as e:
    # e.kind is "not-found" for an IP ipapi.co cannot place (some VPNs, reserved
    # addresses), "http" with e.status 429 for a rate limit, and "unreachable"
    # or "invalid-response" when the service could not be used at all.
    print(f"Could not detect location ({e.kind}): {e}")
    # Fall back to an explicit prompt or a hard-coded default.
    lat, lon = 41.85, -87.65  # Chicago
# --8<-- [end:example]
