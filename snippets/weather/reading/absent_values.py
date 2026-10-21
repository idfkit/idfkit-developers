from __future__ import annotations

import math

from idfkit.weather import WeatherFile, monthly_means

epw: WeatherFile = ...  # type: ignore[assignment]
# --8<-- [start:example]
# A measurement the file says was not taken is absent, not the number the format
# reserves for it. Absence is nan: no weather file can express one, so it is not
# a value the column could otherwise have held.
albedo = epw.hours.albedo
print(math.isnan(albedo[0]))  # True where the file wrote its missing value

# How many hours of a column are present is carried rather than recomputed.
print(epw.hours.present_count["albedo"])

# A monthly mean excludes the absent hours from the sum AND from the divisor, so
# it is the mean of the values that exist. The count says how many that was.
january = monthly_means(epw, "dry_bulb_temperature")[0]
print(january.mean)  # nan when the month held no measurement at all
print(january.count)  # and 0 beside it, which says why
# --8<-- [end:example]
