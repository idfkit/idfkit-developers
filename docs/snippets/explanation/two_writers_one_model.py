from __future__ import annotations

# --8<-- [start:controls]
import idfkit

model = idfkit.load_idf("5ZoneAirCooled.idf")

# Every control, at a value that is not the default.
text = idfkit.write_idf(
    model,
    indent=4,
    comment_column=45,
    ordering="source",
)
# --8<-- [end:controls]

# --8<-- [start:compressed]
compact = idfkit.write_idf(model, output_type="compressed")
# --8<-- [end:compressed]

_ = text, compact
