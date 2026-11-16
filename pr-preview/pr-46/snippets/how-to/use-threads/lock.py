from __future__ import annotations

from idfkit import IDFDocument

doc: IDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
import threading
from concurrent.futures import ThreadPoolExecutor

doc_lock = threading.Lock()


def add_zone(name: str) -> None:
    with doc_lock:  # every read and every write of `doc`, not only the writes
        doc.add("Zone", name)


with ThreadPoolExecutor() as pool:
    list(pool.map(add_zone, ["North", "South", "East", "West"]))
# --8<-- [end:example]
