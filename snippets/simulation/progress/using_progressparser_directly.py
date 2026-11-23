from __future__ import annotations

from idfkit import IDFDocument

model: IDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
from idfkit.simulation import ProgressParser
from idfkit.simulation.progress import environment_days

parser = ProgressParser(environment_days(model))

# Parse saved logs: stdout, then stderr (which carries the "complete" line)
for log in ("energyplus_stdout.log", "energyplus_stderr.log"):
    with open(log) as f:
        for line in f:
            event = parser.parse_line(line)
            if event is not None:
                print(f"{event.phase}: {event.message}")
# --8<-- [end:example]
