from __future__ import annotations

from idfkit.weather import StationIndex

index: StationIndex = ...  # type: ignore[assignment]
# --8<-- [start:example]
# One result per station; its datasets are in .variants
result = index.search("725300")[0]  # Chicago O'Hare WMO
for s in result.variants:
    print(f"{s.dataset_variant}: {s.url}")
# --8<-- [end:example]
