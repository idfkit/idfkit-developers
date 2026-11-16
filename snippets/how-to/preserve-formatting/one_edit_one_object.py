from __future__ import annotations

from idfkit import load_idf

model = load_idf("model.idf", preserve_formatting=True)

# --8<-- [start:example]
from idfkit import write_idf

model["Zone"]["Perimeter_ZN_1"].ceiling_height = 3.2

# Every other object comes back from the characters it was read from, and so
# does every comment, blank line and line ending between them.
written = write_idf(model)
# --8<-- [end:example]

_ = written
