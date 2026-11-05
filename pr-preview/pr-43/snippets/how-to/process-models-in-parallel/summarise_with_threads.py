from __future__ import annotations

# --8<-- [start:example]
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from idfkit import load_idf
from idfkit.geometry import calculate_zone_floor_area


def summarise(path: Path) -> dict[str, object]:
    doc = load_idf(str(path))  # one document per call, so nothing is shared between threads
    zones = [zone.name for zone in doc["Zone"]]
    return {
        "file": path.name,
        "zones": len(zones),
        "floor_area": sum(calculate_zone_floor_area(doc, zone) for zone in zones),
    }


paths = sorted(Path("portfolio").glob("*.idf"))
with ThreadPoolExecutor(max_workers=8) as pool:
    rows = list(pool.map(summarise, paths))
# --8<-- [end:example]
