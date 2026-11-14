from __future__ import annotations

from idfkit import IDFDocument

doc: IDFDocument = ...  # type: ignore[assignment]
variants: list[IDFDocument] = ...  # type: ignore[assignment]
# --8<-- [start:example]
from concurrent.futures import ThreadPoolExecutor


def make_variant(thickness: float) -> IDFDocument:
    variant = doc.copy()  # a private copy: this thread may change it freely
    variant["Material"]["Insulation"].thickness = thickness
    return variant


with ThreadPoolExecutor() as pool:
    variants = list(pool.map(make_variant, [0.05, 0.10, 0.15]))
# --8<-- [end:example]
