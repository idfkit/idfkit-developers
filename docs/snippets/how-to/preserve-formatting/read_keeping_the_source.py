from __future__ import annotations

# --8<-- [start:example]
from idfkit import load_idf

model = load_idf("model.idf", preserve_formatting=True)
# --8<-- [end:example]

_ = model
