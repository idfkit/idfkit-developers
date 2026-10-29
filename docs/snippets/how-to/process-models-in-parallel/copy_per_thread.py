from __future__ import annotations

# --8<-- [start:example]
from concurrent.futures import ThreadPoolExecutor

from idfkit import load_idf, write_idf

baseline = load_idf("office.idf")


def variant(thickness: float) -> str:
    model = baseline.copy()  # this thread's own document; the baseline is only read
    model["Material"]["Insulation"].thickness = thickness
    return write_idf(model)


with ThreadPoolExecutor() as pool:
    variants = list(pool.map(variant, [0.05, 0.10, 0.15, 0.20]))
# --8<-- [end:example]
