from __future__ import annotations

from idfkit import load_idf

model = load_idf("model.idf", preserve_formatting=True)

# --8<-- [start:example]
from idfkit import write_idf

# Refused: reproducing the original text and laying it out differently are
# contradictory requests, so one of them has to be dropped and neither should
# be dropped in silence.
try:
    write_idf(model, preserve_formatting=True, indent=4)
except ValueError as error:
    print(error)
    # preserve_formatting reproduces the original text, so it cannot also apply
    # indent, comment_column, ordering or version_first. Pass one or the other.

# Granted: a different output form is a different artifact, which the original
# text was never going to express.
write_idf(model, "compressed", preserve_formatting=True)
# --8<-- [end:example]
