from __future__ import annotations

from idfkit import Scene

scene: Scene = ...  # type: ignore[assignment]
# --8<-- [start:example]
for item in scene.unresolved:
    # The reason is an enumerated value, not a message, so grouping on it is
    # stable and a reworded string cannot change what a consumer does.
    print(item.object_type, item.name, item.reason)

    # 'zone-not-found' and 'parent-surface-not-found' also name what the object
    # pointed at and the model does not hold. The reason says how to group the
    # failure; this says which name to go and look for.
    if item.missing_reference is not None:
        print("  names", item.missing_reference)
# --8<-- [end:example]
