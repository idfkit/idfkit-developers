from __future__ import annotations

# --8<-- [start:types]
# mypkg/_idf.py: the releases this package supports, in one module.
from typing import TYPE_CHECKING, TypeAlias, TypeVar

from idfkit import IDFDocument
from idfkit.document import AnyIDFDocument
from idfkit.versioned import (
    IDFDocumentV9_6,
    IDFDocumentV22_1,
    IDFDocumentV22_2,
    IDFDocumentV23_1,
    IDFDocumentV23_2,
    IDFDocumentV24_1,
    IDFDocumentV24_2,
    IDFDocumentV25_1,
    IDFDocumentV25_2,
    IDFDocumentV26_1,
    as_version,
)

# The same releases twice: a tuple for as_version, an alias for annotations. Keep them together.
SUPPORTED = (
    IDFDocumentV9_6,
    IDFDocumentV22_1,
    IDFDocumentV22_2,
    IDFDocumentV23_1,
    IDFDocumentV23_2,
    IDFDocumentV24_1,
    IDFDocumentV24_2,
    IDFDocumentV25_1,
    IDFDocumentV25_2,
    IDFDocumentV26_1,
    IDFDocument,
)
Model: TypeAlias = (
    IDFDocumentV9_6
    | IDFDocumentV22_1
    | IDFDocumentV22_2
    | IDFDocumentV23_1
    | IDFDocumentV23_2
    | IDFDocumentV24_1
    | IDFDocumentV24_2
    | IDFDocumentV25_1
    | IDFDocumentV25_2
    | IDFDocumentV26_1
    | IDFDocument
)
ModelT = TypeVar("ModelT", bound=Model)  # for functions that return the model they were given

if TYPE_CHECKING:
    # Object classes for the same releases. Any<Class> covers every supported release that has
    # the type; for a latest-only package, import the plain classes (Zone, Space) instead.
    from idfkit.document import AnySpace as Space
    from idfkit.document import AnyZone as Zone


def as_model(doc: AnyIDFDocument) -> Model:
    """Type a loaded model for the supported releases; raise TypeError for any other."""
    return as_version(doc, SUPPORTED)


# --8<-- [end:types]


# --8<-- [start:usage]
# mypkg/zones.py: annotates with the package's names, never with idfkit's.
def zones_without_spaces(model: Model) -> list[str]:
    spaced = {space.zone_name for space in model["Space"]}
    return [zone.name for zone in model["Zone"] if zone.name not in spaced]


def ceiling_height(zone: Zone) -> float | None:
    height = zone.ceiling_height
    return height if isinstance(height, float) else None


def space_type(space: Space) -> str | None:
    return space.space_type


def tag_model(model: ModelT) -> ModelT:
    for space in model["Space"]:
        space.space_type = space.space_type or "General"
    return model


# The package's public entry point: any loaded model, narrowed once.
def report(doc: AnyIDFDocument) -> list[str]:
    return zones_without_spaces(as_model(doc))


# --8<-- [end:usage]
