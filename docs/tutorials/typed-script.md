# Build a type-checked script

In this tutorial we will write a short Python script that builds a two-zone
model, set up pyright to check it in strict mode, and watch the checker catch
two mistakes before the script ever runs: a misspelled field name and a choice
EnergyPlus would reject. At the end the script saves a model to `offices.idf`.

It takes about ten minutes. You need no EnergyPlus installation and no
knowledge of EnergyPlus: where the model needs a value, this page gives you one.

This tutorial is Python only. TypeScript reaches the same checks through the
type packages described in
[static types generated from the schema](../explanation/generated-types.md).

{{ parity("generated-object-types") }}

## Before we start

We need Python 3.12 or newer and [uv](https://docs.astral.sh/uv/). Open a
terminal in a directory where you can create a new folder.

## Step 1: Create the project

Create a folder for the project, make it a uv project, and add idfkit and
pyright to it:

```bash
mkdir typed-offices
cd typed-offices
uv init --bare
uv add idfkit pyright
```

`uv init --bare` writes a `pyproject.toml` and nothing else. Open it and add
these two lines at the end:

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

Strict mode makes pyright report everything it is unsure about, which is what
we want while we learn what it can see.

The pyright output on this page was captured with pyright 1.1.414. Run
`uv run pyright --version` to see yours; with another version the wording of
some messages may differ slightly.

## Step 2: Write the script

Create `offices.py` with this content:

```python
--8<--
docs/snippets/tutorials/typed-script.py:header
docs/snippets/tutorials/typed-script.py:zones
docs/snippets/tutorials/typed-script.py:save
--8<--
```

Notice the `if TYPE_CHECKING:` block. `Zone` is a class that exists only for
the type checker, so we import it there and nowhere else; the line
`from __future__ import annotations` lets us use it in the signature of
`describe` without Python ever looking it up.

Run the script:

```bash
uv run python offices.py
```

The output should be:

```text
Office: ceiling 2.7 m
Lobby: ceiling 4.0 m
Saved 2 zones to offices.idf
```

A file called `offices.idf` has appeared next to the script. Now run pyright
over the script:

```bash
uv run pyright offices.py
```

The last line of the output should be:

```text
0 errors, 0 warnings, 0 informations
```

## Step 3: Ask pyright what it sees

Add these three lines just before the `save_idf(...)` line, below the blank
line that follows the `for` loop:

```python
office = model["Zone"]["Office"]
reveal_type(office)
reveal_type(office.zone_inside_convection_algorithm)
```

Run pyright again:

```bash
uv run pyright offices.py
```

Pyright now reports two informations, one per `reveal_type`:

```text
offices.py:23:13 - information: Type of "office" is "Zone"
offices.py:24:13 - information: Type of "office.zone_inside_convection_algorithm" is "Literal['', 'ASTMC1340', 'AdaptiveConvectionAlgorithm', 'CeilingDiffuser', 'Simple', 'TARP', 'TrombeWall'] | None"
```

Notice that pyright knows `office` is a `Zone`, although we never annotated it,
and that it knows every value the convection field accepts. Your editor shows
the same list when you hover over the field or start typing a value.

Delete the two `reveal_type` lines and keep the `office = ...` line.

## Step 4: Misspell a field

In `describe`, change `zone.ceiling_height` to `zone.ceilng_height`, dropping
the second `i`, and run pyright:

```bash
uv run pyright offices.py
```

Pyright stops at the typo:

```text
offices.py:12:41 - error: Argument of type "Literal['ceilng_height']" cannot be assigned to parameter "key" of type "Never" in function "__getattr__"
    Type "Literal['ceilng_height']" is not assignable to type "Never" (reportArgumentType)
1 error, 0 warnings, 0 informations
```

The wording is indirect, but the error points at the misspelled name, and it
does so without running anything. If we ran the script instead, it would stop
at the same line with `InvalidFieldError: Invalid field 'ceilng_height' for
object type 'Zone'`.

Put the `i` back and run pyright once more. It reports `0 errors` again.

## Step 5: Choose a value EnergyPlus would reject

Add this line directly after `office = model["Zone"]["Office"]`:

```python
office.zone_inside_convection_algorithm = "Tarp"
```

Run pyright:

```bash
uv run pyright offices.py
```

The error begins like this. It lists the values the field accepts, and `"Tarp"`
is not among them:

```text
offices.py:23:43 - error: Cannot assign to attribute "zone_inside_convection_algorithm" for class "Zone"
    Type "Literal['Tarp']" is not assignable to type "Literal['', 'ASTMC1340', 'AdaptiveConvectionAlgorithm', 'CeilingDiffuser', 'Simple', 'TARP', 'TrombeWall'] | None"
```

This mistake matters more than the last one. Python does not reject the
assignment when the script runs: the model would be saved with `Tarp` in it,
and only EnergyPlus would complain, much later. Change the value to `"TARP"`,
so the two lines read:

```python
--8<-- "docs/snippets/tutorials/typed-script.py:convection"
```

## Step 6: Run the finished script

Run pyright, and then the script:

```bash
uv run pyright offices.py
uv run python offices.py
```

Pyright reports `0 errors, 0 warnings, 0 informations`, and the script prints
the same three lines as in step 2. Open `offices.idf` and find the `Office`
zone: its ceiling height is `2.7`, and its inside convection algorithm is now
`TARP`.

## What we built

We have a script that pyright checks in strict mode, a typed function that takes
a `Zone`, and two mistakes caught before the model was ever run. Every model in
this script was created with `new_document()`, so it is typed for the latest
EnergyPlus release.

Next:

- To check a whole package and run the check in CI, see
  [how to check idfkit code with pyright and `idfkit check`](../how-to/check-idfkit-code.md).
- To write functions that take models from older EnergyPlus releases, see
  [how to write code for any EnergyPlus version](../how-to/write-code-for-any-energyplus-version.md).
- To understand why some names are type errors on older models, read
  [why code for any release sees less](../explanation/typing-across-releases.md).
