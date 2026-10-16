from __future__ import annotations

import warnings

from idfkit import load_idf

model = load_idf("model.idf", preserve_formatting=True)

# --8<-- [start:example]
if model.raw_text is None:
    warnings.warn(
        "This file was read without preserve_formatting, so saving will reformat it.",
        stacklevel=1,
    )
# --8<-- [end:example]
