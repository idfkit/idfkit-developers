from __future__ import annotations

from idfkit import IDFDocument
from idfkit.geometry import translate_to_world

doc: IDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
# Python only, and a mutation rather than a reading. It resolves through the same
# rule and writes the resolved vertices back into the document, then restates
# what they were resolved against so that a second call applies nothing again.
translate_to_world(doc)

# An object the resolution could not place is left in the frame it was authored
# in, and is named in a warning on the idfkit logger rather than dropped.
# --8<-- [end:example]
