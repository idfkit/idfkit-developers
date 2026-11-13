# Type-Safe Development

idfkit ships auto-generated type stubs for all 858 EnergyPlus object types.
Your IDE gets autocomplete, inline documentation, and error detection out of
the box — no plugins or configuration needed.

{{ parity("generated-object-types") }}

## IDE Autocomplete and Inline Docs

Every object type has a typed attribute accessor on `IDFDocument` and typed
fields on individual objects. Your IDE will show field names, types (including
`Literal` for enumerated choices), docstrings with units, defaults, and valid
ranges.

```python
--8<-- "docs/snippets/concepts/type-safety/autocomplete.py:example"
```

For example, hovering over `zone.ceiling_height` in your IDE will show:

```
(property) ceiling_height: float | Literal["", "Autocalculate"] | None
```

## Strict Field Access

By default, accessing a misspelled field name raises an `InvalidFieldError`.
Disable **strict mode** to fall back to returning `None` for unknown fields:

```python
--8<-- "docs/snippets/concepts/type-safety/strict_fields.py:example"
```

| Function | Parameter |
|----------|-----------|
| `new_document()` | `strict=True` (default) |
| `load_idf()` | `strict=True` (default) |
| `load_epjson()` | `strict=True` (default) |

!!! tip
    Strict mode is on by default. Disable it with `strict=False` when loading
    third-party IDF files that may contain non-standard fields.

## Undeclared Names Are Type Errors

Strict mode catches a misspelled field when the code runs. On a typed object, a
type checker catches it before, whatever `strict` is set to. A typed object is
one taken from `doc["Zone"]` or `doc.zones`, along with its extensible groups,
such as `surface.vertices[0]`. Its class declares the schema's snake_case field
names and nothing else:

```python
zone = doc["Zone"]["Office"]
zone.x_orgin = 0.0       # pyright and mypy report the assignment
print(zone.celing_height)  # pyright reports the read
```

The same holds for two spellings that work at run time: an eppy-style
capitalised name such as `zone.X_Origin`, and a field that exists only in an
EnergyPlus version older than the stubs, such as `Lights.watts_per_zone_floor_area`
up to 23.2. Reach such a field with item access, `lights["watts_per_zone_floor_area"]`,
or with `getattr`.

Objects from `doc.add()`, `doc.get_collection()` and the eppy API
(`doc.idfobjects[...]`, `newidfobject()`, `getobject()`) are plain `IDFObject`
and accept any attribute name, so in the snippet above `zone.x_orgin` is caught
only at run time.

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
    Under the hood, `doc["Zone"]` is typed via a `TypedDict` with all 858
    EnergyPlus object types as literal keys. This gives your type checker exact
    return types for each key — but `TypedDict` subscript access requires
    string *literals*, so a plain `str` variable won't type-check.
    An `@overload`-based approach was considered but rejected because 858
    overloads cause significant performance degradation in pyright.
    `get_collection()` is the lightweight escape hatch: it accepts any `str`
    and returns the base `IDFCollection[IDFObject]` type.

## Version Availability

Type stubs include **"Since: X.Y.Z"** annotations in docstrings for object
types and fields that were introduced after EnergyPlus 8.9.0. This helps you
avoid using features that don't exist in your target version:

```python
--8<-- "docs/snippets/concepts/type-safety/version_info.py:example"
```

Hovering over `SpaceHVACZoneReturnMixer` in your IDE shows the docstring
including "Since: 24.2.0", making it clear which minimum EnergyPlus version
is required.

## See Also

- [Version Compatibility](version-compatibility.md) — static linting for cross-version issues
- [API Reference: Document](../api/document.md) — full `IDFDocument` API
- [Build your first model](../tutorials/first-model.md) — build a model from scratch
