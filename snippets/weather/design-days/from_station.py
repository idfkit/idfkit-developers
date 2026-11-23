from __future__ import annotations

from idfkit.weather import DesignDayManager, StationIndex

index: StationIndex = ...  # type: ignore[assignment]
# --8<-- [start:example]
from idfkit.weather import DesignDayManager, StationIndex

index = StationIndex.load()
station = index.search("chicago ohare")[0].station  # newest dataset

# Download and parse the DDY of the station's own dataset
ddm = DesignDayManager.from_station(station)

# Or choose another dataset of the same station, by variant or by years
ddm = DesignDayManager.from_station(station, dataset="2007-2021")
# --8<-- [end:example]
