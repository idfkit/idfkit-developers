from __future__ import annotations

from idfkit.versioned import AnyIDFDocument

doc: AnyIDFDocument = ...  # type: ignore[assignment]
# --8<-- [start:example]
from idfkit import load_idf, new_document
from idfkit.versioned import IDFDocumentV9_4, IDFDocumentV23_2, as_version

# Create a model typed for one release
legacy = new_document(IDFDocumentV9_4)

# Load a file that must be one release, or any release in a range
model = load_idf("building.idf", as_type=IDFDocumentV23_2)
recent = load_idf("building.idf", since="22.1")

# Narrow a document you already hold; raises TypeError if it is another release
typed = as_version(doc, IDFDocumentV23_2)
lights = typed["Lights"]["Office Lights"]
print(lights.watts_per_zone_floor_area)  # declared in 23.2, renamed in 24.1
# --8<-- [end:example]
