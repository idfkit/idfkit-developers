from __future__ import annotations

# --8<-- [start:example]
from idfkit import new_document
from idfkit.versioned import IDFDocumentV9_4, as_version

blank = new_document(version=(9, 4, 0))  # a 9.4 model, but typed IDFDocument: the latest release
fixture = as_version(new_document(version=(9, 4, 0)), IDFDocumentV9_4)  # typed for 9.4
fixture.add("Zone", "Office")
fixture["Zone"]["Office"].update(ceiling_height=3.0)  # checked against 9.4's Zone
# --8<-- [end:example]
