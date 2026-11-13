# How to write code for any EnergyPlus version, or a range of them

*This guide is Python only. TypeScript reaches the same result by leaving a
document unparameterised, or by parameterising it with one release's type map;
see [static types generated from the schema](../explanation/generated-types.md).*

This guide shows you how to annotate functions and modules so that pyright
checks them against the EnergyPlus releases they will actually meet: the latest
release only, every supported release, or a range such as "9.6 and later". It
assumes the project already runs pyright in strict mode; if not, start with
[how to check idfkit code](check-idfkit-code.md).

{{ parity("generated-object-types") }}

## Pick the document type to annotate with

The annotation on a document parameter is a statement about which releases the
code handles. Pick the narrowest one that is true:

| The code handles models that are | Annotate the document as | For example |
|---|---|---|
| created with `new_document()`, or loaded and known to be the latest release, including models you migrated to it first | `IDFDocument`, or leave it inferred | a script that builds a new model; a pipeline that runs `migrate` on every input before anything else |
| of one known release | that release's type, such as `IDFDocumentV9_4`, given with `as_version` | a tool for a portfolio of 9.4 models; see [how to type a model for its EnergyPlus version](type-a-model-for-its-version.md) |
| of whatever release the caller hands over | `AnyIDFDocument` | a reusable function, a library, a command-line tool that opens users' files |
| of a range of releases | a union of release types | code that needs `Space`, which arrived in 9.6 |

Two consequences decide the hard cases:

- `load_idf` returns `IDFDocument` whatever the file's release, because the
  checker cannot read the file. Annotating a function `IDFDocument` is a claim
  that its callers only pass latest-release models; nothing checks that claim
  when a 9.4 file is loaded. If the code may see an older file, annotate
  `AnyIDFDocument`.
- `AnyIDFDocument` accepts every document: one from `load_idf` or
  `new_document()`, and any document typed with `as_version`. `IDFDocument`
  accepts only the latest release, and pyright rejects a 9.4 document passed to
  it. Taking `AnyIDFDocument` therefore costs callers nothing, and costs the
  function every name some release lacks.

## Accept a model of any release

Annotate the document `AnyIDFDocument` and let everything you reach through it
be inferred:

```python
--8<-- "docs/snippets/how-to/write-code-for-any-energyplus-version/accept_any_release.py:example"
```

Through `AnyIDFDocument`:

- `doc["Type"]` and accessors such as `doc.zones` accept the 789 object types
  every supported release defines. `Space` and `SpaceList`, new in 9.6, are not
  among them. Your editor still suggests them after `doc["`, because a
  latest-release document is part of the union, but choosing one is an error.
- Each object offers only the fields every release has. A field one release
  renamed, such as `People.zone_or_zonelist_or_space_or_spacelist_name`
  (`zone_or_zonelist_name` before 9.6), is an error to read or assign.
- `update()` keywords and values are checked the same way.

Import `AnyIDFDocument` from `idfkit.document` or `idfkit.versioned`; both
check equally fast. idfkit's own functions (`save_idf`, `simulate`, the
geometry and zoning helpers) take `AnyIDFDocument`, so any document passes to
them, and the ones that return the document they were given, such as
`expand_objects` and `doc.copy()`, return the type they received.

## Pass objects to helper functions

The object classes in the stubs describe the latest release. A parameter
annotated `Zone` accepts a zone from a latest-release document and rejects one
from anywhere else: a 9.4 zone is a `Zone_v8_9_to_v9_4`, and a zone reached
through `AnyIDFDocument` is `Zone | _ZoneBase`. There is no public name yet for
"a zone of any release".

So, in code for any release:

- When the helper needs an object whose type changed between releases, give it
  the document and let it reach the objects itself, as `tall_zones` does below.
- When the type was declared the same way in every release, the public class
  fits every release. That holds for 504 of the 789 shared types, among them
  `Construction`, `ZoneList` and `Schedule:Compact`. If pyright accepts the
  object from an `AnyIDFDocument`, the annotation is safe.
- `IDFObject` accepts any object of any release, untyped.

```python
--8<-- "docs/snippets/how-to/write-code-for-any-energyplus-version/object_parameters.py:example"
```

Import the classes inside `if TYPE_CHECKING:`; they do not exist at run time.

## Read and write a field whose values changed

When a field accepts different values in different releases, the value you
read and the value you may write have different types through
`AnyIDFDocument`:

- Reading gives what a file of any release can contain: every release's values
  together. `WaterHeater:Mixed.heater_fuel_type` reads as `str | None`, because
  8.9 to 9.2 accept any string there.
- Writing, by assignment or `update()`, accepts only what every release accepts.
  For the heater fuel that is `Coal`, `Diesel`, `Electricity`, `FuelOilNo1`,
  `FuelOilNo2`, `Gasoline`, `NaturalGas`, `OtherFuel1`, `OtherFuel2`, `Propane`,
  or `None`. `"DistrictHeatingWater"` (which 9.3 to 23.1 reject) and `"Steam"`
  or `"DistrictHeating"` (which 23.2 and later reject) are errors to write.
- When no value is valid in every release, only `None`, which clears the field,
  is writable.

```python
--8<-- "docs/snippets/how-to/write-code-for-any-energyplus-version/changed_field.py:example"
```

Do not treat the type you read through `AnyIDFDocument` as a closed list.
Compare it with the values you handle and leave a branch for anything else. A
`match` that ends in `assert_never` cannot pass there, because the read type
includes `str`:

```text
error: Argument of type "str" cannot be assigned to parameter "arg" of type "Never" in function "assert_never"
```

To handle every value exhaustively, restrict the function to releases whose
choices are fixed; see [handle every value of a field](#handle-every-value-of-a-field).

The checker is the only guard on writes. Assigning a value the model's release
rejects does not raise at run time: a 9.4 document stores
`"DistrictHeatingWater"` without complaint, and EnergyPlus rejects it later.

## Reach an object type some releases lack

When the code genuinely serves every release, take the collection by name with
`get_collection`. It accepts any type name and returns
`IDFCollection[IDFObject]`, untyped, and for a release without the type it is
empty:

```python
--8<-- "docs/snippets/how-to/write-code-for-any-energyplus-version/reach_a_type_some_release_lacks.py:example"
```

When the code needs the type's fields typed, restrict it to the releases that
have the type instead, as the next section does.

## Restrict a function to a range of releases

Name the releases in a type alias and annotate with it. Through the union, a
lookup is typed for each member, and only what every member has is offered:

```python
--8<-- "docs/snippets/how-to/write-code-for-any-energyplus-version/range_alias.py:example"
```

Here `doc["Space"]` is
`IDFCollection[Space_v9_6_to_v22_1] | IDFCollection[Space_v22_2_to_v26_1] | IDFCollection[Space]`,
so `space.floor_area` is checked against each.

The same pattern covers the other ranges. Pick the members from
`IDFDocumentV8_9` to `IDFDocumentV26_1`, plus `IDFDocument` for 26.2:

- **From a release on**: that release's type through `IDFDocument`, as above.
- **Before a release**: `IDFDocumentV8_9` up to the last release before it.
  `Before9_6` would be `IDFDocumentV8_9 | ... | IDFDocumentV9_5`.
- **Between two releases**: the types from the first to the last.

At the call site, a latest-release document and any member typed with
`as_version` pass. A document outside the range is rejected, with the first
few differences listed:

```text
error: Argument of type "IDFDocumentV9_4[bool]" cannot be assigned to parameter "doc" of type "Since9_6" in function "space_areas"
```

A document typed for a range is still a document of some release, so it
passes to every function that takes `AnyIDFDocument`.

Writes through a range follow the same rule as through `AnyIDFDocument`:
pyright accepts a value only if every release in the union accepts it. Through
`IDFDocumentV9_4 | IDFDocument`, `heater_fuel_type = "NaturalGas"` passes, while
`"DistrictHeatingWater"` is reported against 9.4's class and `"DistrictHeating"`
against the latest:

```text
error: Cannot assign to attribute "heater_fuel_type" for class "WaterHeaterMixed_v9_3_to_v23_1"
error: Cannot assign to attribute "heater_fuel_type" for class "WaterHeaterMixed"
```

mypy reports the same value passed to `update()`, but misses both assignments
through a union of release types. If the project runs mypy, write changed
fields in range code with `update()`.

The annotation is a claim the checker holds callers to; nothing checks it when
the code runs. To guard against a caller that passed an unchecked
`load_idf` result of another release, narrow with `as_version` as in the next
section.

## Hand the caller's type back from a range function

A function that returns the document it was given loses the caller's type if
it is annotated with the union: pyright infers the whole union as the return
type, and mypy, which does not infer return types, gives `Any`. Bind a
`TypeVar` to the union instead:

```python
--8<-- "docs/snippets/how-to/write-code-for-any-energyplus-version/range_typevar.py:example"
```

`latest` is `IDFDocument[Literal[True]]` and `older` is `IDFDocumentV26_1[bool]`
under pyright. A 9.4 document is still rejected, by both checkers:

```text
error: Argument of type "IDFDocumentV9_4[bool]" cannot be assigned to parameter "doc" of type "Since26_1@use_district_steam" in function "use_district_steam"
error: Value of type variable "Since26_1" of "use_district_steam" cannot be "IDFDocumentV9_4[Any]"  [type-var]
```

The first line is pyright's, the second mypy's. `IDFDocumentV26_2` is
`IDFDocument`, so a plain `load_idf` result passes without `as_version`.

## Handle every value of a field

Through a range in which every release lists the field's choices, the value
reads as those choices, and a `match` over them can be checked as exhaustive.
From 23.2 on, `heater_fuel_type` reads as twelve choices or `None`:

```python
--8<-- "docs/snippets/how-to/write-code-for-any-energyplus-version/exhaustive_range.py:example"
```

Leave a choice out and pyright names it at the `assert_never` call, for example
`Argument of type "Literal['Propane']" cannot be assigned to parameter "arg" of
type "Never"`. Add 9.4 to the range and the read type gains its own choices
(`"DistrictHeating"`, `"Steam"`), which the `match` then has to handle too.

## Narrow a model of unknown release into a range

A function that takes `AnyIDFDocument` and wants to call `space_areas` has to
establish that the model is 9.6 or later. `as_version` takes one release type,
not a union, so try the range's types in turn:

```python
--8<-- "docs/snippets/how-to/write-code-for-any-energyplus-version/narrow_into_range.py:example"
```

Each `as_version` call checks the model's version at run time and raises
`TypeError` on a mismatch, so the loop returns the model typed for its own
release, or `None` before 9.6.

Two shorter forms do not work:

- `as_version(doc, Since9_6)` is rejected: `Type "UnionType" is not assignable
  to type "type[_D@as_version]"`.
- `isinstance(doc, IDFDocumentV9_6)`, and `case IDFDocumentV9_6():` in a
  `match`, work at run time but pyright rejects them: `TypedDict class not
  allowed for instance or class checks`.

## Verify the result

Run pyright over the module. Then pass it a model of the oldest and the newest
release you claim to support; the type checker cannot see what `get_collection`
and item access such as `zone["ceiling_height"]` return. To lint the
`doc.add(...)` calls pyright cannot check, run `idfkit check` with the same
releases as targets; see [how to check idfkit code](check-idfkit-code.md).

## Related

- [How to type a model for its EnergyPlus version](type-a-model-for-its-version.md)
  for code written for one release
- [Why code for any release sees less](../explanation/typing-across-releases.md)
  for why `AnyIDFDocument` offers only shared names, and why reads and writes
  differ
- [Supported EnergyPlus versions](../reference/versions.md) for the releases
  each type stands for
