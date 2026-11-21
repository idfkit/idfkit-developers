# Type-Safe Development

idfkit ships auto-generated type stubs for all 858 EnergyPlus object types.
Your IDE gets autocomplete, inline documentation, and error detection out of
the box — no plugins or configuration needed.

{{ parity("generated-object-types") }}

## IDE Autocomplete and Inline Docs

Every object type has a typed attribute accessor on the document and typed
fields on individual objects. Your IDE will show field names, types (including
`Literal` for enumerated choices), docstrings with units, defaults, and valid
ranges.

Accessors are plural (`doc.zones`, `doc.materials`), except for the types a
model holds at most one of, which are singular (`doc.building`,
`doc.output_sqlite`). The plural spelling of those is deprecated. A misspelled
accessor, such as `doc.zonez`, is a type error.

```python
--8<-- "docs/snippets/concepts/type-safety/autocomplete.py:example"
```

For example, hovering over `zone.ceiling_height` in your IDE will show:

```
(property) ceiling_height: float | Literal["Autocalculate"] | None
```

A field is cleared with `None`, not with an empty string.

## Typed for a Release

A file's EnergyPlus release is only known once the file is read, so `load_idf()`
and `load_epjson()` return an `AnyIDFDocument`. Its objects declare the fields
every supported release shares, and its collections hold types such as
`AnyZone` and `AnyLights`. A field only some releases have is a type error on
them; its message names the fix, `_NotAFieldInEveryRelease_TypoOrNarrowWithAsVersion`.

State the release to type the model as that release declares it. Each release
has a document type in `idfkit.versioned`, from `IDFDocumentV8_9` to
`IDFDocumentV26_2`, which is `IDFDocument`:

```python
--8<-- "docs/snippets/concepts/type-safety/release_types.py:example"
```

- `new_document(IDFDocumentV9_4)` creates a model typed for that release.
  `new_document()` and `new_document(version=(25, 2, 0))` are typed as
  `IDFDocument`, the latest release, whatever version they create.
- `as_type=` on a loader, or `as_version(doc, ...)` on a document you hold,
  names one release or a tuple of them. `since=` and `before=` name a range.
  The release is checked at run time, and a mismatch raises `TypeError`.
- On a release-typed document, an object type or field that release lacks is a
  type error, so code written for 23.2 cannot reach a 24.1 field by accident.

## Strict Field Access

By default, accessing a misspelled field name raises an `InvalidFieldError`.
Strict mode also checks each value you assign, through attribute assignment or
`update()`, against the schema, as `add()` does: a wrong type, a choice the
field does not list, or a number out of range raises `ValidationFailedError`.
Disable **strict mode** to return `None` for unknown fields and store such
values as given:

```python
--8<-- "docs/snippets/concepts/type-safety/strict_fields.py:example"
```

| Function | Parameter |
|----------|-----------|
| `new_document()` | `strict=True` (default) |
| `load_idf()` | `strict=True` (default) |
| `load_epjson()` | `strict=True` (default) |

Some checks hold in either mode. NaN and infinity are refused, because neither
EnergyPlus nor epJSON can hold them. `update()` refuses a field name the type
does not have.

!!! tip
    Strict mode is on by default. Disable it with `strict=False` when loading
    third-party IDF files that may contain non-standard fields or values.

Required fields are typed without `None`: `material.thickness` is a `float`.
Reading one the model leaves unset raises `MissingRequiredFieldError`. Test it
with `material.get("thickness")`, which returns `None` instead.

## Undeclared Names Are Type Errors

Strict mode catches a misspelled field when the code runs. On a typed object, a
type checker catches it before, whatever `strict` is set to. A typed object is
one taken from `doc["Zone"]` or `doc.zones`, along with its extensible groups,
such as `surface.vertices[0]`. Its class declares the schema's snake_case field
names and nothing else:

```python
zone = doc["Zone"]["Office"]
zone.x_orgin = 0.0       # reported: not a field of Zone
print(zone.celing_height)  # reported
```

The same holds for an eppy-style capitalised name such as `zone.X_Origin`,
which works at run time. Use the snake_case name, or item access,
`zone["X_Origin"]`. A field that exists only in some releases, such as
`Lights.watts_per_zone_floor_area` up to 23.2, is reached by typing the document
for its release, as in [Typed for a Release](#typed-for-a-release).

Objects from `doc.add()`, `doc.get_collection()` and the eppy API
(`doc.idfobjects[...]`, `newidfobject()`, `getobject()`) are plain `IDFObject`
and accept any attribute name, so a typo on them is caught only at run time.

## Typed Creation

Create objects through their collection to have the fields checked as you write
them:

```python
zone = doc.zones.add("Office", ceiling_height=2.7, multiplier=1)  # returns Zone
wall = doc["BuildingSurface:Detailed"].add("Wall 1", surface_type="Wall", ...)
```

`collection.add(name, **fields)` takes the type's fields as keyword arguments,
so a misspelled or missing required field is a type error, and it returns the
typed object. It validates the values as `doc.add()` does; pass
`validate=False` to skip that. `doc.add("Zone", ...)` still works, but takes
any keyword and returns a plain `IDFObject`.

Passing an existing object to `collection.add(obj)` is deprecated; use
`doc.addidfobject(obj)`.

## Dynamic Key Access

When the object type is a string literal, `doc["Zone"]` returns a fully typed
collection. When the key comes from a variable, use `get_collection()` to get
a safely typed `IDFCollection[IDFObject]`:

```python
--8<-- "docs/snippets/concepts/type-safety/get_collection.py:example"
```

Use `doc["Zone"]` when you know the type at write time. Use
`doc.get_collection(obj_type)` in generic functions that accept any object type.

!!! note "Why `get_collection()`?"
    `doc["Zone"]` is typed by one `__getitem__` overload per object type, each
    keyed on a string literal. A plain `str` variable matches none of them, so
    it does not type-check. `get_collection()` is the escape hatch: it accepts
    any `str` and returns the base `IDFCollection[IDFObject]` type. To iterate
    over every collection in a document, use `doc.collections`.

## Version Availability

Type stubs include **"Since: X.Y.Z"** annotations in docstrings for object
types and fields that were introduced after EnergyPlus 8.9.0. This helps you
avoid using features that don't exist in your target version:

```python
--8<-- "docs/snippets/concepts/type-safety/version_info.py:example"
```

Hovering over `SpaceHVACZoneReturnMixer` in your IDE shows the docstring
including "Since: 24.2.0". On a document typed for an earlier release, such as
`IDFDocumentV23_2`, `doc["SpaceHVAC:ZoneReturnMixer"]` is a type error.

## See Also

- [Version Compatibility](version-compatibility.md) — static linting for cross-version issues
- [API Reference: Document](../api/document.md) — full `IDFDocument` API
- [Build your first model](../tutorials/first-model.md) — build a model from scratch
