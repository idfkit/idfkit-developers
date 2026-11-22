from __future__ import annotations

from idfkit.versioned import AnyIDFDocument

model: AnyIDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
from idfkit import load_idf

# Load an existing IDF file
model = load_idf("building.idf")
print(f"Loaded {len(model)} objects")

# For migration-only tolerant loading of legacy/noisy files:
model = load_idf("legacy_building.idf", strict_parsing=False)
print(f"Tolerant load parsed {len(model)} objects")

# Type the model for the releases you expect, and read a legacy encoding
model = load_idf("building.idf", since="9.6", encoding="cp1252")
# --8<-- [end:example]
