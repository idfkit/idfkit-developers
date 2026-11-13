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

A misspelled field name is a type error: the stubs declare every field an object
has, so pyright and Pylance report any other name before the code runs. At run
time, by default, accessing a misspelled field name raises an
`InvalidFieldError`.
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

A document is typed for the latest supported release unless you say
otherwise. To type a model of an older release as that release, see
[how to type a model for its EnergyPlus version](../how-to/type-a-model-for-its-version.md).
For a function that accepts a model of any release, annotate it
`AnyIDFDocument`, which offers only what every supported release has; see
[how to write code for any EnergyPlus version](../how-to/write-code-for-any-energyplus-version.md),
and [why code for any release sees less](../explanation/typing-across-releases.md)
for the reasons.

## See Also

- [Build a type-checked script](../tutorials/typed-script.md) — a first script under pyright strict mode
- [Type a model for its EnergyPlus version](../how-to/type-a-model-for-its-version.md) — types for an older release
- [Write code for any EnergyPlus version](../how-to/write-code-for-any-energyplus-version.md) — `AnyIDFDocument` and ranges of releases
- [Check idfkit code with pyright and `idfkit check`](../how-to/check-idfkit-code.md) — which check catches what
- [Version Compatibility](version-compatibility.md) — static linting for cross-version issues
- [API Reference: Document](../api/document.md) — full `IDFDocument` API
- [Build your first model](../tutorials/first-model.md) — build a model from scratch
