from __future__ import annotations

# --8<-- [start:example]
from datetime import datetime

from idfkit import new_document
from idfkit.schedules import MalformedScheduleError, compact_problems, evaluate

doc = new_document()
draft = doc.add(
    "Schedule:Compact",
    "Draft Heating",
    data=[
        {"field": "Through: 6/30"},
        {"field": "For: AllDays"},
        {"field": "Until: 24:00"},
        {"field": "20"},
    ],
)

# List the problems without raising
for problem in compact_problems(draft):
    print(problem)

# Evaluating the schedule raises
try:
    evaluate(draft, datetime(2024, 1, 8, 10, 0))
except MalformedScheduleError as e:
    print(e)
# --8<-- [end:example]
