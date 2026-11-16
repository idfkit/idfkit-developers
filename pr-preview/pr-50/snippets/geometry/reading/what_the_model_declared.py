from __future__ import annotations

from idfkit import Scene

scene: Scene = ...  # type: ignore[assignment]
# --8<-- [start:example]
applied = scene.applied

# What the model stated, in the schema's spelling rather than the file's casing.
print(applied.coordinate_system)  # 'Relative' or 'World'
print(applied.vertex_entry_direction)  # 'Counterclockwise' or 'Clockwise'
print(applied.starting_vertex_position)  # 'UpperLeftCorner', and so on
print(applied.north_axis)  # degrees, clockwise from true north

# Two conditions worth asking about directly, since both change the answer.
print(applied.is_relative, applied.is_clockwise)

# Fields the model did not state, named rather than silently defaulted.
if "north_axis" in applied.defaulted:
    print("no Building north axis stated; resolution assumed 0")
# --8<-- [end:example]
