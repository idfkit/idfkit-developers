from __future__ import annotations

# --8<-- [start:example]
from typing import TypeVar

from idfkit import load_idf
from idfkit.versioned import IDFDocumentV26_1, IDFDocumentV26_2, as_version

# 26.1 and later. Bound to the union, so each call hands back the caller's own type.
Since26_1 = TypeVar("Since26_1", bound="IDFDocumentV26_1 | IDFDocumentV26_2")


def use_district_steam(doc: Since26_1) -> Since26_1:
    for heater in doc["WaterHeater:Mixed"]:
        heater.heater_fuel_type = "DistrictHeatingSteam"  # both releases accept it
    return doc


latest = use_district_steam(load_idf("model.idf"))  # IDFDocument, which is IDFDocumentV26_2
older = use_district_steam(as_version(load_idf("older.idf"), IDFDocumentV26_1))  # IDFDocumentV26_1
# --8<-- [end:example]
