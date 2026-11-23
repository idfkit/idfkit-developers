from __future__ import annotations

from idfkit.exceptions import ResultLookupError
from idfkit.simulation import CSVResult, SimulationResult

csv_result: CSVResult = ...  # type: ignore[assignment]
result: SimulationResult = ...  # type: ignore[assignment]
# --8<-- [start:example]
csv_result = result.csv

# List all columns
for col in csv_result.columns:
    print(f"{col.variable_name} ({col.key_value}) [{col.units}]")

# Get data for a specific column (frequency= picks one when several are reported)
try:
    column = csv_result.get_column("Zone Mean Air Temperature", "THERMAL ZONE 1", frequency="Hourly")
    values = column.values
except ResultLookupError as e:
    print(e)  # names the closest variables and the reported keys
# --8<-- [end:example]
