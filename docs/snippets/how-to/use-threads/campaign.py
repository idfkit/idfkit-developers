from __future__ import annotations

from idfkit import IDFDocument

base: IDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
from concurrent.futures import ThreadPoolExecutor

from idfkit.simulation import SimulationCache, SimulationJob, SimulationResult, simulate_batch

THICKNESSES = [0.05, 0.10, 0.15, 0.20]


def make_variant(thickness: float) -> IDFDocument:
    variant = base.copy()  # never change `base` itself: other threads are copying it
    variant["Material"]["Insulation"].thickness = thickness
    return variant


# 1. Build the variants. CPU-bound Python: parallel on a free-threaded build only.
with ThreadPoolExecutor() as pool:
    variants = list(pool.map(make_variant, THICKNESSES))

# 2. Simulate. EnergyPlus runs as a subprocess, so threads are enough on any build.
#    Do not touch `variants` again until the batch returns.
jobs = [
    SimulationJob(model=v, weather="site.epw", label=f"ins-{t}", annual=True) for v, t in zip(variants, THICKNESSES)
]
batch = simulate_batch(jobs, max_workers=4, cache=SimulationCache())


# 3. Read the results. Each worker opens, queries and closes its own result's SQL output:
#    the SQLite connection belongs to the thread that opened it.
def site_energy(result: SimulationResult) -> str:
    try:
        return result.sql.get_tabular_value(
            "AnnualBuildingUtilityPerformanceSummary", "Site and Source Energy", "Total Site Energy", "Total Energy"
        )
    finally:
        result.close()


with ThreadPoolExecutor() as pool:
    totals = list(pool.map(site_energy, batch.succeeded))
# --8<-- [end:example]
