from __future__ import annotations

# --8<-- [start:example]
import threading
from concurrent.futures import ThreadPoolExecutor

from idfkit import load_idf

model = load_idf("office.idf")
model_lock = threading.Lock()


def add_zone(name: str) -> None:
    with model_lock:  # every read and every write of `model` goes through this lock
        model.add("Zone", name)


with ThreadPoolExecutor() as pool:
    list(pool.map(add_zone, ["North", "South", "East", "West"]))
# --8<-- [end:example]
