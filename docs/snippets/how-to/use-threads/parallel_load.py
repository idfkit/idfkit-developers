from __future__ import annotations

from idfkit import IDFDocument, ValidationResult

paths: list[str] = ...  # type: ignore[assignment]
docs: list[IDFDocument] = ...  # type: ignore[assignment]
results: list[ValidationResult] = ...  # type: ignore[assignment]
# --8<-- [start:example]
from concurrent.futures import ThreadPoolExecutor

from idfkit import load_idf, validate_document

with ThreadPoolExecutor() as pool:
    docs = list(pool.map(load_idf, paths))
    results = list(pool.map(validate_document, docs))
# --8<-- [end:example]
