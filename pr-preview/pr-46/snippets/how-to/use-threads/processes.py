from __future__ import annotations

from idfkit import IDFDocument

paths: list[str] = ...  # type: ignore[assignment]
docs: list[IDFDocument] = ...  # type: ignore[assignment]
# --8<-- [start:example]
from concurrent.futures import ProcessPoolExecutor

from idfkit import load_idf

if __name__ == "__main__":  # required: spawn and forkserver workers re-import this module
    with ProcessPoolExecutor() as pool:
        docs = list(pool.map(load_idf, paths))
# --8<-- [end:example]
