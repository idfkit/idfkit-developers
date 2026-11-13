from __future__ import annotations

from idfkit import Scene

scene: Scene = ...  # type: ignore[assignment]
# --8<-- [start:example]
# A model whose geometry is stated in a form this reads nothing of comes back
# with no surfaces and a populated unattempted, which is a different answer from
# a model that holds no geometry at all.
if not scene.surfaces and scene.unattempted:
    for entry in scene.unattempted:
        print(f"{entry.object_type}: {entry.count} not read")

# Everything is accounted for: resolved, unresolved with a reason, or of a type
# recorded as unattempted. There is no fourth outcome and nothing is dropped.
total = len(scene.surfaces) + len(scene.unresolved) + sum(e.count for e in scene.unattempted)
print(total)
# --8<-- [end:example]
