from __future__ import annotations

# --8<-- [start:example]
from idfkit.document import AnyIDFDocument


def space_names(doc: AnyIDFDocument) -> list[str]:
    """Name every Space, or none for a release before 9.6, which had no Space."""
    # get_collection takes any type name and returns IDFCollection[IDFObject], so it
    # type-checks against every release. For a release without the type it is empty.
    return [space.name for space in doc.get_collection("Space")]


# --8<-- [end:example]
