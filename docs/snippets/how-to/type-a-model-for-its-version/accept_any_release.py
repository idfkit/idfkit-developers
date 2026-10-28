from __future__ import annotations

# --8<-- [start:example]
from idfkit import load_idf
from idfkit.document import AnyIDFDocument
from idfkit.versioned import IDFDocumentV9_4, as_version


def people_count(doc: AnyIDFDocument) -> int:
    """Count People objects in a model of any supported release."""
    return len(doc["People"])


people_count(load_idf("model.idf"))  # a latest-release model
people_count(as_version(load_idf("legacy.idf"), IDFDocumentV9_4))  # a 9.4 model
# --8<-- [end:example]
