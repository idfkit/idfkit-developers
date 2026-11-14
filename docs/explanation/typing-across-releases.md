# Why code for any release sees less

*This page is about the Python stubs. TypeScript makes the same trade-offs
differently, by leaving a document untyped until the caller names a release;
see [static types generated from the schema](generated-types.md).*

A function annotated to take a model of any EnergyPlus release cannot reach
`Space`, cannot read `People.zone_or_zonelist_or_space_or_spacelist_name`, and
reads one type from `WaterHeater:Mixed.heater_fuel_type` while accepting a
narrower one on assignment. This page explains why each of those is the
correct answer rather than a limitation to work around, and where the design
is still unfinished.

{{ parity("generated-object-types") }}

## A release is a fact about a file

The release a model is in is written in the file, in its `Version` object, and
a type checker never reads the file. Whatever a document's type says about its
release, the code said it, and the code can say three things.

It can say nothing. `load_idf` and `new_document()` return `IDFDocument`, typed
for the latest release. For a model the script created, or migrated before
touching it, that is true. For a file someone else wrote it is an optimistic
guess, and nothing checks it.

It can name one release with `as_version`. That claim is checked, once, at run
time, and from then on the checker holds every line to that release.

Or it can admit it does not know, with `AnyIDFDocument`. This is the honest
annotation for a reusable function, and everything below follows from taking
it seriously: if the function may be handed a model of any supported release,
the checker may only allow what is true of all of them.

## Why only the shared names

`AnyIDFDocument` is `IDFDocument | IDFDocumentAllVersions`, and the second half
offers the 789 object types every supported release defines. `Space` is not
one of them, because a 9.4 model has none, and a function that reads
`doc["Space"]` from a 9.4 model fails when it runs. Rejecting the lookup is the
checker refusing to certify code that is wrong for some of its callers.

The latest-release half of the union is there for the callers, not the
function. It lets a document from `load_idf` pass without ceremony, and it is
also why an editor still offers `Space` after `doc["`: completion lists what any
member of the union has, while the checker requires what every member has.

An earlier draft of these stubs declared the missing types as optional keys of
the any-release document instead. Pyright then reported `doc["Space"]` only as
a key that "may result in runtime exception", and typed the result as though
the lookup had succeeded, so the rest of the function looked checked when it
was not. Keeping those keys also cost a great deal: for every release's
document to stay assignable to the any-release one, each release's map had to
be declared closed, and pyright took about a minute on any file that named a
release type. Dropping the keys made the check both correct, a hard error with
an explicit escape hatch, and fast, a few seconds per file.

The object classes follow the same rule. `AnyZone` is a zone as every
supported release declares it, the class the latest `Zone` and each older
release's zone class derive from, so a parameter annotated `AnyZone` accepts a
zone of any release. Its fields are the shared ones. Because "every supported
release" grows when idfkit adopts a new EnergyPlus release, `Any<Class>` can
lose a field on an idfkit upgrade, which is the type checker reporting a real
change rather than an instability in the stubs.

Fields follow the same rule as object types. A field one release renamed or
dropped is not offered, and since idfkit types unknown attribute names as
errors on every typed object, a misspelling and a field another release lacks
are reported the same way.

## Why a changed field reads wide and writes narrow

When a field's accepted values differ between releases, there are two
questions, and they have different answers.

*What can a value read from this field be?* Anything a file of any supported
release may contain. For `heater_fuel_type` that is any string, because 8.9 to
9.2 accept any string there. So reading gives the union of every release's
values.

*What may be written to it?* Only what every release accepts, because the
document may be any of them. For the heater fuel that is ten values, none of
the district-heating spellings: `"Steam"` and `"DistrictHeating"` are gone from
23.2 on, and `"DistrictHeatingWater"` arrived after 23.1. So writing accepts
the intersection.

This is the ordinary rule for any mutable container, written out for
EnergyPlus fields: what comes out may be anything that was ever put in, and
what goes in must suit every reader.

Typing reads as the intersection instead would look tidier, and it is
dangerous. A `match` over the ten shared fuels, ending in `assert_never`, would
pass the checker, and the first real 9.4 file with a district-heated water
heater would stop it with `Expected code to be unreachable, but got:
'DistrictHeating'`. The wide read type is what makes the checker ask for the
branch that file needs.

When no value is valid in every release, the intersection is empty and the only
safe write is `None`, which clears the field. That is rare, and it is correct:
there is no value a release-agnostic function could write there without being
wrong for some model.

## Why the checker is the only guard on writes

Run time does not repeat this check. Assigning a choice the model's release
rejects is stored as given: a 9.4 document accepts `"DistrictHeatingWater"`
without complaint, and the mistake surfaces when EnergyPlus reads the file.
Strict mode catches an unknown field *name* at run time, but not an invalid
*value*. For values, a type error is the earliest and, before a simulation,
the only warning.

## Why some doors stay open

Two ways in are untyped on purpose. `doc.get_collection(name)` takes any string
and returns `IDFCollection[IDFObject]`, and item access, `obj["field"]`, takes
any key and returns `Any`. Typed lookups are keyed by string literals, so code
that computes a type or field name at run time cannot be typed by them at all;
these two methods are how such code, and code that deliberately reaches past
the shared names, says so. Neither is checked, which is the price.

## Why `as_version` and not `isinstance`

At run time each release's document type is a real class, and
`isinstance(doc, IDFDocumentV9_4)` answers correctly. In the stubs, though, a
document type is assembled from a `TypedDict` that maps each object type to its
collection, which is what lets `doc["Zone"]` be typed per key, and pyright does
not allow a `TypedDict` in an instance check or a class pattern. `as_version`
is the narrowing that works in both worlds: a run-time check of the version, and
a return type the checker trusts.

It takes a release type, or a tuple of them, the way `isinstance` takes a class
or a tuple of classes: a tuple is a plain value that run time can check one
member at a time, and that pyright reads as the union of its members. A union
named with a type alias is not accepted there by pyright, which is why
[the how-to](../how-to/write-code-for-any-energyplus-version.md#narrow-a-model-of-unknown-release-into-a-range)
keeps the tuple for `as_version` and the alias for annotations.

## Two checkers, two kinds of knowledge

`idfkit check` and pyright both report object types and choices that a release
lacks, and still catch different lines, because they know different things.

Pyright knows types. It follows a document through variables, function calls
and attribute access, so it sees an assignment to `heater.heater_fuel_type`
three calls away from the `load_idf` that produced the heater. It knows nothing
the types do not say: `doc.add("Space", ...)` takes a string and keywords, so
the string is just a string.

`idfkit check` knows schemas, and nothing about types. It reads string literals
where idfkit takes object-type names and choice values, and compares them with
the schemas of the releases you list. It needs no annotations, which suits a
script that has none, and it is the only one of the two that reads the
arguments of `add`. It cannot follow a value through a variable or into an
assignment.

So they overlap on typed lookups such as `doc["Space"]` and otherwise complement
each other, and code meant to span releases is best checked by both.

## Where the design is unfinished

One gap is known, and the how-to guides work around it. mypy reads the stubs
but:

- reports document methods such as `add`, `get_collection`, `version` and the
  accessors as missing;
- misses invalid assignments through a union of release types;
- collapses the union `as_version` returns for a tuple into what all its
  releases share.

pyright is the checker these stubs are tested against.

## See also

- [How to write code for any EnergyPlus version](../how-to/write-code-for-any-energyplus-version.md)
  to apply this
- [How to check idfkit code with pyright and `idfkit check`](../how-to/check-idfkit-code.md)
  to run both checks
- [Type-safe development](../concepts/type-safety.md) for what the stubs give
  an editor on any document
