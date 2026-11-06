# How to type a model for its EnergyPlus version

*This guide is Python only. TypeScript reaches the same result by parameterizing
a document with the type map of the version you installed; see
[static types generated from the schema](../explanation/generated-types.md).*

Every Python document is typed for the latest supported release. A model's
version is read from its file, so a type checker cannot know it on its own.
For a model of an older release that is wrong in small, specific ways: the
editor completes field names the file's release does not have, offers choices
it would reject, and stays quiet about object types it has never heard of.

This guide types a loaded model for its release, writes a function that
accepts a model of any release, and reaches an object type that some releases
lack. It needs a type checker (pyright, Pylance or mypy) and nothing else: the
types change nothing at run time.

{{ parity("generated-object-types") }}

## Type a loaded model for its release

`as_version` takes a document and a type from `idfkit.versioned`, checks the
document's version at run time, and returns the same document typed for that
release. A file of another release raises `TypeError` there, rather than being
typed as something it is not.

```python
--8<-- "docs/snippets/how-to/type-a-model-for-its-version/type_a_loaded_model.py:example"
```

`idfkit.versioned` has one type per supported release, named
`IDFDocumentV<major>_<minor>`: `IDFDocumentV8_9` through `IDFDocumentV26_2`.
The last one is `IDFDocument` itself. Through a release's type, the object
types, the field value types and choices, the `update()` keywords and the
accessors such as `model.zones` are that release's.

Patch releases share a type. A file states its version as `Version, 9.0;`, so
`IDFDocumentV9_0` covers EnergyPlus 9.0.1, the release idfkit carries for 9.0.

## Accept a model of any release

A function that works on any release takes `AnyIDFDocument`. It accepts a
latest-release document and any document typed with `as_version`, and offers
what every supported release has: the object types all of them define, each
field typed to admit every release's values, and no field that some release
lacks.

```python
--8<-- "docs/snippets/how-to/type-a-model-for-its-version/accept_any_release.py:example"
```

Import `AnyIDFDocument` from `idfkit.document`. `idfkit.versioned` re-exports
it, but importing anything from that module makes the type checker read the
stubs for every older release, about 1.2 MB more, which an editor pays for each
time it analyses the file from scratch. Import from `idfkit.versioned` only the
release types you name.

idfkit's own functions (`save_idf`, `simulate`, the geometry and zoning
helpers) take `AnyIDFDocument`, so a typed older model passes to them
unchanged. The ones that return the document they were given, such as
`expand_objects` and `doc.copy()`, return it with the type it came in with.

## Reach a type some releases lack

`Space` arrived in EnergyPlus 9.6. Through `AnyIDFDocument`, `doc["Space"]` is
reported, because a 9.4 model has no such key. When the code genuinely serves
every release, take the collection by name with `get_collection`, which accepts
any type name and is typed `IDFCollection[IDFObject]`. For a release without
the type, the collection is empty.

```python
--8<-- "docs/snippets/how-to/type-a-model-for-its-version/reach_a_type_some_release_lacks.py:example"
```

When the code is written for one release, type the model for it with
`as_version` instead, and the type and its fields come back fully typed.

## Read what the checker reports

Each error names the type that lacks what the code reached for, so the message
says which release the line does not hold for. These are pyright's words, which
Pylance shows as well:

```python
legacy["Space"]
# "Space" is not a defined key in "IDFDocumentV9_4[bool]"

legacy["People"]["Office"].update(zone_or_zonelist_or_space_or_spacelist_name="Office")
# No parameter named "zone_or_zonelist_or_space_or_spacelist_name"

doc["Space"]  # doc: AnyIDFDocument
# "Space" is not a required key in "IDFDocumentAllVersions[bool]",
# so access may result in runtime exception

doc.spaces
# Cannot access attribute "spaces" for class "IDFDocumentAllVersions[bool]"
```

`IDFDocumentAllVersions` is the name the checker uses for the every-release
half of `AnyIDFDocument`. `doc["Space"]` stays typed after the error, so one
missing type does not turn the rest of the function into unknowns.

Two things are not reported, on any release. Reading or setting a field name
the release does not have is not a type error, because idfkit resolves field
names at run time, where strict mode raises `InvalidFieldError`. A misspelled
or renamed field is caught statically through `update()`, whose keywords are
typed, as the second example shows.

## See also

- [Type-safe development](../concepts/type-safety.md) for what the stubs give
  an editor on any document
- [How to compare two EnergyPlus versions](compare-versions.md) for what changed
  between two releases, in data rather than in types
- [How to migrate models between EnergyPlus versions](../simulation/migrating-versions.md)
  for moving a model to the release its types describe
