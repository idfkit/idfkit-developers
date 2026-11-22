from __future__ import annotations

from idfkit import IDFDocument

doc: IDFDocument = ...  # type: ignore[assignment]
texts: list[str] = ...  # type: ignore[assignment]
# --8<-- [start:example]
from concurrent.futures import ThreadPoolExecutor

from idfkit import write_idf


def render(_: int) -> str:
    return write_idf(doc) or ""


# Safe only while no thread changes `doc`.
with ThreadPoolExecutor() as pool:
    texts = list(pool.map(render, range(8)))
# --8<-- [end:example]
