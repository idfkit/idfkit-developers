from __future__ import annotations

# --8<-- [start:example]
from idfkit.document import AnyIDFDocument


def electrify_water_heaters(doc: AnyIDFDocument) -> list[str]:
    """Switch every gas-fired WaterHeater:Mixed to electricity; return the names changed."""
    changed: list[str] = []
    for heater in doc["WaterHeater:Mixed"]:
        fuel = heater.heater_fuel_type  # str | None: 8.9 to 9.2 accept any string here
        if fuel is not None and fuel.lower() == "naturalgas":
            heater.heater_fuel_type = "Electricity"  # a value every release accepts
            changed.append(heater.name)
    return changed


# --8<-- [end:example]
