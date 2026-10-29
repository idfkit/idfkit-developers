from __future__ import annotations

from pathlib import Path


def summarise(path: Path) -> dict[str, object]: ...


# --8<-- [start:example]
from concurrent.futures import ProcessPoolExecutor

# The guard is required: workers started by spawn (Windows, macOS) or forkserver (Linux, from
# Python 3.14) import this module again, and without it each one would start a pool of its own.
if __name__ == "__main__":
    paths = sorted(Path("portfolio").glob("*.idf"))
    with ProcessPoolExecutor() as pool:
        rows = list(pool.map(summarise, paths))
# --8<-- [end:example]
