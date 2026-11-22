from __future__ import annotations

from idfkit.simulation import SimulationCache

cache: SimulationCache = ...  # type: ignore[assignment]
# --8<-- [start:example]
# Total size of the stored entries
print(f"{cache.size_bytes() / 2**30:.1f} GiB")

# Evict entries unused for 30 days, then least recently used ones down to 10 GiB
removed = cache.prune(max_bytes=10 * 2**30, max_age=30 * 86400)

# Clear everything
cache.clear()
# --8<-- [end:example]
