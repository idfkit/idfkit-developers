# How to type a model for its EnergyPlus version

*This guide is Python only. TypeScript reaches the same result by parameterizing
a document with the type map of the version you installed; see
[static types generated from the schema](../explanation/generated-types.md).*

Every Python document is typed for the latest supported release, because a
model's version is read from its file and a type checker cannot see it. For a
model of an older release that is wrong in small, specific ways: the editor
completes field names the release does not have, offers choices it rejects,
and accepts object types it has never heard of.

This guide types a model for the one release it is in, so the checker holds
the code to that release. For code that must accept models of several
releases, see
[how to write code for any EnergyPlus version](write-code-for-any-energyplus-version.md).
The types change nothing at run time; you need pyright, Pylance or mypy to see
them.

{{ parity("generated-object-types") }}

## Type a loaded model for its release

Pass the document and the release's type to `as_version`. It checks the
document's version at run time and returns the same document, typed for that
release:

```python
--8<-- "docs/snippets/how-to/type-a-model-for-its-version/type_a_loaded_model.py:example"
```

If the file is another release, `as_version` raises `TypeError` rather than
typing it as something it is not:

```text
TypeError: The document is EnergyPlus 9.4.0, not 9.0.1, so it cannot be typed as IDFDocumentV9_0
```

The release types live in `idfkit.versioned`, one per supported release, named
`IDFDocumentV<major>_<minor>`: `IDFDocumentV8_9` through `IDFDocumentV26_2`. The
last one is `IDFDocument` itself. Patch releases share a type: a file states
its version as `Version, 9.0;`, so `IDFDocumentV9_0` covers EnergyPlus 9.0.1,
the release idfkit carries for 9.0.

Through a release's type, everything is that release's: the object types, the
field names, the value types and choices, the `update()` keywords, and the
accessors such as `model.zones`.

## Type a new document of an older release

`new_document(version=...)` builds a model of that release, but the checker
cannot see the argument, so the result is typed for the latest release like
any other document. Wrap it in `as_version` when the code, a test fixture for
example, should be checked against the older release:

```python
--8<-- "docs/snippets/how-to/type-a-model-for-its-version/new_document_for_a_release.py:example"
```

## Handle a renamed field inside general code

A function that takes models of any release sometimes needs a field that
releases spell differently. `People`'s zone field was renamed in 9.6, so
`AnyIDFDocument` offers neither name. Check the version, then type the model
for the releases on that side of the rename. `as_version` takes one release
type or a tuple of them:

```python
--8<-- "docs/snippets/how-to/type-a-model-for-its-version/renamed_field.py:example"
```

Under pyright, each `update()` is checked against every release in its tuple:
swapping the two names reports `No parameter named
"zone_or_zonelist_or_space_or_spacelist_name"` in the first branch and `No
parameter named "zone_or_zonelist_name"` in the second. Use `as_version` for
this, not `isinstance` or a `case` pattern: both work at run time, but pyright
rejects them for document types.

mypy rejects both names here, because it collapses a tuple's union to what all
its releases share. Under mypy, give each branch one release type, with one
branch per release before the rename.

To narrow to one release only, pass that release's type alone, as in the first
section.

## Read the release's errors

Through a release's type, a name the release lacks is reported with the
release's type in the message, so the error says which release the line does
not hold for:

```text
error: "Space" is not a defined key in "IDFDocumentV9_4[bool]"
```

`legacy.add("Space", ...)` is not reported, because `add` accepts any type name;
`idfkit check` catches it. For what each message means and how to fix it, see
[how to check idfkit code](check-idfkit-code.md#fix-what-pyright-reports).

## See also

- [Type-safe development](../concepts/type-safety.md) for what the stubs give
  an editor on any document
- [How to compare two EnergyPlus versions](compare-versions.md) for what changed
  between two releases, in data rather than in types
- [How to migrate models between EnergyPlus versions](../simulation/migrating-versions.md)
  for moving a model to the latest release, so it can be typed as
  `IDFDocument`
