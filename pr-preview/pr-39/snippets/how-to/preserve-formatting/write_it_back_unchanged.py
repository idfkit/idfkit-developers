from __future__ import annotations

from pathlib import Path

from idfkit import load_idf

model = load_idf("model.idf", preserve_formatting=True)

# --8<-- [start:example]
from idfkit import write_idf

write_idf(model) == Path("model.idf").read_text(encoding="latin-1")  # True
# --8<-- [end:example]
