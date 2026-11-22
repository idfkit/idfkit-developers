from __future__ import annotations

from pathlib import Path

from idfkit import load_idf

model = load_idf("model.idf", preserve_formatting=True)

# --8<-- [start:example]
from idfkit import save_idf

save_idf(model, "copy.idf")
Path("copy.idf").read_bytes() == Path("model.idf").read_bytes()  # True
# --8<-- [end:example]
