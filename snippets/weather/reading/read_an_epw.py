from __future__ import annotations

from idfkit.weather import parse_epw

epw_text: str = ...  # type: ignore[assignment]
# --8<-- [start:example]
# Reading takes the text you already hold. No network, no filesystem, nothing
# asynchronous, so it costs a fraction of the retrieval that produced the text.
epw = parse_epw(epw_text)

print(epw.location.city)  # Chicago Ohare Intl Ap
print(epw.hours.row_count)  # 8760, taken from the file's declared data period

# Every numeric field is a named column, packed and the same length.
temperature = epw.hours.dry_bulb_temperature  # array("d"), degrees C
print(temperature[0])  # the first hour of 1 January

# The hour column runs 1 to 24, and hour 24 is the last hour of its OWN day
# rather than hour 0 of the next.
print(epw.hours.hour[23], epw.hours.day[23])  # 24.0 1.0
# --8<-- [end:example]
