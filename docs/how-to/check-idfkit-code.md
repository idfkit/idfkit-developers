# How to check idfkit code with pyright and `idfkit check`

*This guide is Python only. In TypeScript the compiler does both jobs, through
the per-release type packages; see
[static types generated from the schema](../explanation/generated-types.md).*

This guide shows you how to catch EnergyPlus mistakes in Python code that uses
idfkit before the code runs: a misspelled field, a choice a release rejects, an
object type a release does not have. Two tools do this, and they look at
different things, so the first step is choosing between them.

{{ parity("generated-object-types") }}

{{ parity("schema-compatibility-check") }}

## Choose the check

**pyright checks types.** It reads the types idfkit's stubs give every
document and object, so it checks attribute names, assigned values, `update()`
keywords and values, `doc["Type"]` lookups and the document type a function
accepts. It needs nothing from you beyond typed code: a document from
`load_idf` or `new_document` is already typed, and a function parameter needs
an annotation. It checks against the release the type stands for, which is the
latest unless the code says otherwise.

**`idfkit check` checks string literals against releases you name.** It reads
your source without running it or understanding its types, finds object-type
names and choice values written as literals in `add(...)` calls and
`doc["..."]` lookups, and reports any that one of the target releases lacks
(`C001` for an object type, `C002` for a choice value). It needs no
annotations at all.

On one file they catch different lines. Here, `doc` is annotated
`AnyIDFDocument` and the targets are `--targets 9.4,26.2`:

| Line | pyright | `idfkit check` |
|------|---------|----------------|
| `doc.add("Space", "Open office", zone_name="Office")` | not reported: `add` takes any type name | `C001`: not in 9.4.0 |
| `doc.add("WaterHeater:Mixed", "Heater", heater_fuel_type="DistrictHeating")` | not reported: `add` takes any keywords | `C002`: not in 26.2.0 |
| `heater.heater_fuel_type = "Steam"` | error: not a value every release accepts | not reported: it checks literals in calls, not assignments |
| `doc["Space"]` | error: not a key every release has | `C001`: not in 9.4.0 |
| `doc.get_collection("Space")` | not reported | not reported |

Use them like this:

- For any code, run pyright. It is the check that sees attribute access,
  assignment and `update()`, which is most of what typed code does.
- Add `idfkit check` when the code builds objects with `doc.add(...)`, whose
  arguments pyright cannot check, or when you want to lint against an explicit
  list of releases without annotating anything.
- For a library or tool meant to work on several releases, run both in CI.

Neither tool checks `doc.get_collection(...)`, item access such as
`zone["ceiling_height"]`, or names built at run time. Those are the deliberate
escape hatches, and code that uses them is checked only when it runs.

## Turn on pyright strict mode

Add pyright to the project's development dependencies and set strict mode in
`pyproject.toml`:

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

In VS Code, Pylance reads the same section. To get the same errors in the
editor for a project without one, set `"python.analysis.typeCheckingMode":
"strict"` in the workspace settings.

Object classes such as `Zone` and `Construction` exist only in idfkit's stubs.
Import them from `idfkit.document`, inside an `if TYPE_CHECKING:` block, with
`from __future__ import annotations` at the top of the module:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from idfkit.document import Zone
```

Importing them from `idfkit` instead also works inside the block, but recent
pyright versions report it in strict mode. This is pyright 1.1.414; older
releases such as 1.1.408 accept the import:

```text
error: "Zone" is not exported from module "idfkit"
    Import from "idfkit._generated_types" instead (reportPrivateImportUsage)
```

Do not follow that hint: `idfkit._generated_types` is private.
`idfkit.document` re-exports the same classes and works with every pyright
version. Importing them outside a
`TYPE_CHECKING` block raises `ImportError` when the module runs.

## Run pyright

Run it over the code you want checked:

```bash
uv run pyright src/
```

It exits non-zero when it reports an error, so the same command works as a CI
step. A file that names one or two release types (`IDFDocumentV9_4` and so on)
or `AnyIDFDocument` takes a few seconds to check.

## Run `idfkit check` against the releases you support

List the releases with `--targets`, or a migration's two ends with `--from` and
`--to`. The command takes files, not directories, so pass it the file list:

```bash
uv run idfkit check $(git ls-files 'src/*.py') --targets 9.4,24.2,26.2
```

It exits `1` when it reports anything. Every `C001` and `C002` diagnostic is a
warning, so do not add `--severity error`: it filters them all out and the run
passes. For the rest of the flags, see
[how to work across EnergyPlus versions](../concepts/version-compatibility.md#lint-your-source-before-you-migrate).

## Run both in CI

```yaml
# .github/workflows/check.yml
jobs:
  idfkit-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: uv run pyright src/
      - run: uv run idfkit check $(git ls-files 'src/*.py') --targets 9.4,24.2,26.2
```

Choose the targets from the releases your users' models are in. For code typed
with `AnyIDFDocument`, pyright already checks against every supported release,
and `idfkit check` adds the `add(...)` calls.

## Fix what pyright reports

Each error names the type that lacks what the code reached for. These are
pyright's words, which Pylance shows as well:

`"Space" is not a defined key in "IDFDocumentV9_4[bool]"`
:   The release has no such object type. If the code is meant for that release,
    the type name is wrong. If it is meant for later releases too, see
    [how to write code for any EnergyPlus version](write-code-for-any-energyplus-version.md#reach-an-object-type-some-releases-lack).

`"Space" is not a defined key in "IDFDocumentAllVersions[bool]"`
:   Some supported release lacks the type, and the document is
    `AnyIDFDocument`. Narrow the document to the releases that have it, or
    reach the type untyped with `get_collection`.

`Argument of type "Literal['zone_or_zonelist_or_space_or_spacelist_name']" cannot be assigned to parameter "key" of type "Never" in function "__getattr__"`
:   The object has no field by that name: a typo, or, through
    `AnyIDFDocument`, a field some release lacks or renamed. The name in the
    quotes is the one at fault.

`No parameter named "x_orign"`
:   The same, for an `update()` keyword.

`Cannot assign to attribute "heater_fuel_type" ...` followed by `Type "Literal['Steam']" is not assignable to type "Literal['Coal', 'Diesel', ...] | None"`
:   The value is not one the field accepts. The list after `to type` is every
    value you may write. Through `AnyIDFDocument` it is the values every
    release accepts, which can be shorter than any one release's list.

`Cannot access attribute "spaces" for class "IDFDocumentAllVersions[bool]"`
:   The accessor is for a type some release lacks. Use the same fixes as for
    the key.

## If the project uses mypy

mypy reads the same stubs and reports the same field, value, key and
`update()` mistakes, in its own words:

```text
error: Unexpected keyword argument "x_orign" for "update" of "_ZoneBase"; did you mean "x_origin", "y_origin", or "z_origin"?  [call-arg]
error: TypedDict "IDFDocumentAllVersions[bool]" has no key "Space"  [typeddict-item]
```

It also reports document methods and accessors as missing, which they are not:

```text
error: "IDFDocument[Literal[True]]" has no attribute "add"  [attr-defined]
error: "IDFDocument[Literal[True]]" has no attribute "zones"  [attr-defined]
```

The same happens for `get_collection` and `version`. mypy also misses an
invalid value assigned to a field through a union of release types, such as
`IDFDocumentV9_4 | IDFDocument`, although it reports the same value passed to
`update()`. Until that is fixed in
idfkit's stubs, pyright is the checker to rely on for idfkit code; if you keep
mypy, silence `attr-defined` on those lines rather than for the whole project.

## Related

- [How to write code for any EnergyPlus version](write-code-for-any-energyplus-version.md)
  for annotating functions so pyright checks them against the right releases
- [How to work across EnergyPlus versions](../concepts/version-compatibility.md)
  for every `idfkit check` flag, SARIF output and the pre-commit hook
- [Why code for any release sees less](../explanation/typing-across-releases.md)
  for why the two tools see different things
