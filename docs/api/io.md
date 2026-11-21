# I/O -- Parsers & Writers

Functions and classes for reading and writing EnergyPlus models in IDF
(text) and epJSON (JSON) formats.

## Convenience Loaders

Top-level convenience functions:

- `load_idf(path, version=None, *, as_type=None, since=None, before=None, strict_parsing=True, strict=True,
  preserve_formatting=False, normalize_choices=True, encoding=None)` for IDF files.
- `load_epjson(path, version=None, *, as_type=None, since=None, before=None, strict_parsing=True, strict=True,
  preserve_formatting=False, normalize_choices=True)` for epJSON files.

Both parse strictly by default: a malformed object or an unknown object type raises `IDFParseError`, and `strict_parsing=False`
skips it instead. Both return an `AnyIDFDocument` unless `as_type=`, `since=` or `before=` names the model's release;
see [Typed for a Release](../concepts/type-safety.md#typed-for-a-release).

`strict` governs field access on the loaded objects: an unknown field name raises `InvalidFieldError`, or returns `None`
with `strict=False`, and an assigned value the schema refuses raises `ValidationFailedError`.

`encoding=None` reads an IDF file as UTF-8 when its bytes are valid UTF-8, and as latin-1 otherwise. `save_idf()` writes
the document back in the same encoding.

`load_idf_with_diagnostics()` reads tolerantly and returns the document together with the recoverable findings it
skipped; it takes the arguments of `load_idf()` except `strict_parsing`.

::: idfkit.load_idf

::: idfkit.load_epjson

## IDF Parser

::: idfkit.idf_parser

## epJSON Parser

::: idfkit.epjson_parser

## Writers

::: idfkit.writers
