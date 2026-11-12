from __future__ import annotations

from idfkit import IDFDocument
from idfkit.simulation import OutputVariableIndex

model: IDFDocument = ...  # type: ignore[assignment]
variables: OutputVariableIndex | None = ...  # type: ignore[assignment]
# --8<-- [start:example]
# Search first, review, then add selectively
matches = variables.search("Heating")

# Filter to specific ones
selected = [v for v in matches if "Coil" in v.name]

# Add to model. Output:Variable has no Name field, so pass no name:
# a name raises InvalidFieldError. Its first field is key_value.
for var in selected:
    model.add(
        "Output:Variable",
        key_value="*",
        variable_name=var.name,
        reporting_frequency="Timestep",
    )
# --8<-- [end:example]
