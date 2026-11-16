from __future__ import annotations

from idfkit import IDFDocument, get_scene

doc: IDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
# One argument, one return value, no options. Reading touches no disk and does
# not modify the document: writing it out before and after yields the same bytes.
scene = get_scene(doc)

for surface in scene.surfaces:
    # object_type with name is the address. A name alone is not unique across
    # types, so a consumer that stored only the name has to search to get back.
    print(surface.object_type, surface.name, surface.zone)

    # The vertices are already in the frame the engine computes. Nothing here
    # has to be offset by a zone origin or turned by a north axis afterwards.
    for vertex in surface.polygon.vertices:
        print(vertex.x, vertex.y, vertex.z)

    print(surface.area, surface.normal)
# --8<-- [end:example]
