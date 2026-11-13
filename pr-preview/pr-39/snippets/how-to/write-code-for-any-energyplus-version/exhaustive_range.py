from __future__ import annotations

# --8<-- [start:example]
from typing import TypeAlias

from typing_extensions import assert_never

from idfkit import IDFDocument
from idfkit.versioned import (
    IDFDocumentV23_2,
    IDFDocumentV24_1,
    IDFDocumentV24_2,
    IDFDocumentV25_1,
    IDFDocumentV25_2,
    IDFDocumentV26_1,
)

# Through these releases heater_fuel_type reads as 12 choices or None, so a match can be exhaustive.
Since23_2: TypeAlias = (
    IDFDocumentV23_2
    | IDFDocumentV24_1
    | IDFDocumentV24_2
    | IDFDocumentV25_1
    | IDFDocumentV25_2
    | IDFDocumentV26_1
    | IDFDocument
)


def is_district_heated(doc: Since23_2, heater_name: str) -> bool:
    fuel = doc["WaterHeater:Mixed"][heater_name].heater_fuel_type
    match fuel:
        case "DistrictHeatingWater" | "DistrictHeatingSteam":
            return True
        case (
            "Coal"
            | "Diesel"
            | "Electricity"
            | "FuelOilNo1"
            | "FuelOilNo2"
            | "Gasoline"
            | "NaturalGas"
            | "OtherFuel1"
            | "OtherFuel2"
            | "Propane"
            | None
        ):
            return False
        case _:
            assert_never(fuel)  # reported if a choice is left unhandled


# --8<-- [end:example]
