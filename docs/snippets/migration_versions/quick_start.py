from __future__ import annotations

# --8<-- [start:example]
from idfkit import load_idf, migrate
from idfkit.simulation import find_energyplus

# Load an older IDF (e.g. v22.1.0) and migrate to the installed EnergyPlus.
model = load_idf("old_building.idf")
config = find_energyplus()

report = migrate(model, target_version=config.version, energyplus=config)

print(report.summary())

if not report.steps:
    print("Already at the target version")

# The migrated model has no filepath: save it to a new path
migrated = report.migrated_model
print(f"Migrated model version: {migrated.version}")
migrated.save("migrated_building.idf")
# --8<-- [end:example]
