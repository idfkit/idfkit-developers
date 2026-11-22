from __future__ import annotations

# --8<-- [start:example]
from idfkit import IDFDocument, load_idf, write_idf

# Loaded once at start-up, then only ever read: every request thread may share it.
BASE = load_idf("office.idf")


def handle_request(insulation_m: float) -> str:
    """Called on whatever thread the web server picks, possibly many at once."""
    model: IDFDocument = BASE.copy()  # this request's private model
    model["Material"]["Insulation"].thickness = insulation_m
    return write_idf(model) or ""


# --8<-- [end:example]
