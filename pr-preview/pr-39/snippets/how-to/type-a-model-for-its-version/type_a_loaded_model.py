from __future__ import annotations

# --8<-- [start:example]
from idfkit import load_idf
from idfkit.versioned import IDFDocumentV9_4, as_version

model = as_version(load_idf("legacy.idf"), IDFDocumentV9_4)  # TypeError unless the file is 9.4

people = model["People"]["Office"]
people.update(zone_or_zonelist_name="Office")  # the 9.4 name; 9.6 renamed it

heater = model["WaterHeater:Mixed"]["Heater"]
heater.heater_fuel_type = "DistrictHeating"  # a 9.4 choice; later releases split it in two
# --8<-- [end:example]
