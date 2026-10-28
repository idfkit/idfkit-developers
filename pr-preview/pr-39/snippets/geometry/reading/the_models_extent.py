from __future__ import annotations

from idfkit import Scene

scene: Scene = ...  # type: ignore[assignment]
# --8<-- [start:example]
bounds = scene.bounds

# Absent rather than zero when nothing was placed, so an empty model and a model
# sitting on the origin are distinguishable.
if bounds is None:
    print("nothing resolved")
else:
    print(bounds.min.x, bounds.min.y, bounds.min.z)
    print(bounds.max.x, bounds.max.y, bounds.max.z)

    centre_x = (bounds.min.x + bounds.max.x) / 2
    centre_y = (bounds.min.y + bounds.max.y) / 2
    print(centre_x, centre_y)
# --8<-- [end:example]
