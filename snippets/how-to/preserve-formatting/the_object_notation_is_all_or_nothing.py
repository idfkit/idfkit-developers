from __future__ import annotations

from pathlib import Path

# --8<-- [start:example]
from idfkit import load_epjson, write_epjson

model = load_epjson("model.epJSON", preserve_formatting=True)

write_epjson(model) == Path("model.epJSON").read_text()  # True, while nothing has changed

model.removeidfobject(model["Zone"]["Perimeter_ZN_1"])

# Any change at all falls the WHOLE document back to ordinary formatted output.
# The object notation has no statements, so there is nothing to anchor one
# object's own characters to and no way to reproduce one while reformatting
# another.
write_epjson(model) == Path("model.epJSON").read_text()  # False
# --8<-- [end:example]
