# How to read a model's geometry

You have a parsed model and you want to know where its surfaces are: to draw
them, to measure them, or to check what the file actually says. This guide
turns a document into a resolved scene, in one frame, without editing the model
to find out.

Reading geometry is the same operation in both languages and is spelled the
same way. What a coordinate resolves to is a property of the EnergyPlus input
format rather than of either library, so there is one set of instructions here
and only the fenced code changes.

{{ parity("geometry-extraction") }}

!!! info "In JavaScript, geometry is a separate install"
    `pip install idfkit` installs geometry support unconditionally.
    `npm install @idfkit/idfkit` does not. Add `@idfkit/geometry` by name. It
    reads no files and holds no state, so it runs in a browser tab, a worker or
    an edge runtime as readily as in Node.

## Read the scene

=== "Python"

    ```python
    --8<-- "docs/snippets/geometry/reading/read_the_scene.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/geometry/reading/read_the_scene.ts:example"
    ```

`get_scene` / `getScene` takes a document and returns a value. There is no
`include_shading` argument, no zone filter and no colour: filtering a list is
something you already know how to do, and a viewing decision belongs to the
thing doing the viewing.

The document is unchanged afterwards. Not "unchanged in the fields extraction
reads": unchanged. A preserving write before and after yields identical bytes,
which is what lets you resolve a model you are also editing.

## The vertices are in the engine's frame

A surface's vertices as written in the file are not usually where the surface
is. Up to three declarations move them, and all three are applied before you
see a polygon:

1. **The coordinate system.** Under `Relative`, a surface's vertices are
   measured from its zone's origin, and the zone's own `Direction of Relative
   North` turns them first. Under `World` neither applies.
2. **The building north axis.** `Building`'s `North Axis` turns every surface
   about the world origin. There is one exception, below.
3. **The entry direction.** When the model declares clockwise entry, the ring
   is reversed, so the outward normal follows the right-hand rule in every
   model.

The starting vertex is left where the author put it. Rotating a ring does not
change the surface, and renormalising it would silently discard which corner
the file names first.

!!! warning "`Shading:Site:Detailed` does not turn with the building"
    Clause 2 has exactly one exception, and it is measured rather than assumed.
    Site shading is fixed in space; `Shading:Building:Detailed` and
    `Shading:Zone:Detailed` are not. A square entered identically under both
    types in a model declaring a north axis of 158.434 comes back from
    EnergyPlus 26.1.0 where it was authored under the first and turned under the
    second, and the engine's own report labels them `Detached Shading:Fixed` and
    `Detached Shading:Building`.

## What the model declared, and what had to be assumed

A reader drawing a model usually wants the resolved vertices and nothing else.
A reader checking a model wants to know what was read to get them.

=== "Python"

    ```python
    --8<-- "docs/snippets/geometry/reading/what_the_model_declared.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/geometry/reading/what_the_model_declared.ts:example"
    ```

`defaulted` holds the names of fields the model did not state, in the schema's
spelling, so the strings are the same in both languages. A model that states no
`GlobalGeometryRules` at all is read under the format's documented defaults and
says so here, which is a different fact from a model that states them and
happens to agree.

A stated zero is a declaration and is not listed. An absent or blank field is.

## What could not be placed

A building with one bad wall is still a building you want to see, so nothing
raises. An object that could not be resolved is reported instead.

=== "Python"

    ```python
    --8<-- "docs/snippets/geometry/reading/what_could_not_be_placed.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/geometry/reading/what_could_not_be_placed.ts:example"
    ```

There are four reasons: `no-vertices`, `too-few-vertices`, `zone-not-found` and
`parent-surface-not-found`. The last two also carry the name the object pointed
at, because a reader fixing the model needs that name and should not have to
search the document a second time to get it.

Extraction raises only for a document it was not handed at all. Judging a model
is [validation's](../how-to/collect-diagnostics.md) job; this reports.

!!! warning "A coordinate that is not a number is not yet one of the four"
    Measured against both libraries, on a model whose vertex field holds
    `autosize` where a number belongs. Python raises `ValueError: could not
    convert string to float`, which contradicts the paragraph above. TypeScript
    does not raise and does something worse: it reports the surface as resolved
    with `NaN` coordinates, and because the resolution mixes axes, one bad
    coordinate leaves `scene.bounds` `NaN` in two axes for the whole model, so a
    consumer framing a view gets nothing and is told nothing.

    Neither is the documented answer, which is an entry in `unresolved`. The
    four reasons above do not include one for this, and adding a fifth is a
    registered concept in both languages rather than a local fix, so it is
    recorded here until it is decided.

## What was not read

Not every way of stating geometry is read yet. The simplified surface family
states a surface as an origin, a width, a height and a tilt, which is a second
rule set answerable only against a second set of engine output. Rather than
skipping those objects, the scene names the types and counts them.

=== "Python"

    ```python
    --8<-- "docs/snippets/geometry/reading/what_was_not_attempted.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/geometry/reading/what_was_not_attempted.ts:example"
    ```

That accounting is the guarantee worth relying on: every geometry object in the
model is resolved, unresolved with a reason, or of a type recorded as
unattempted. There is no fourth outcome, so a wall cannot go missing without a
word.

## The extent of what was placed

=== "Python"

    ```python
    --8<-- "docs/snippets/geometry/reading/the_models_extent.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/geometry/reading/the_models_extent.ts:example"
    ```

The bounds enclose the resolved vertices and nothing else. They are absent
rather than zero when nothing was placed, so a model with no geometry and a
model sitting on the origin are distinguishable.

## Rewriting the document instead (Python only)

Everything above reads. Python also has `translate_to_world`, which resolves
through the same rule and writes the result back into the document, then
restates what the vertices were resolved against so a second call applies
nothing again.

```python
--8<-- "docs/snippets/geometry/reading/rewrite_the_document.py:example"
```

Prefer the scene unless you specifically want the model changed. Everything
above is available from a document you are not allowed to edit; this is not.

!!! warning "It cannot make a mixed model consistent"
    `translate_to_world` rewrites only the five detailed vertex types, and it
    zeroes `Building.north_axis` when it is done. An object stated in the
    simplified surface family, and `Daylighting:ReferencePoint`, carries its own
    coordinate-system field, is not read, and is not rewritten. In a model that
    holds both, those objects keep the coordinates the author wrote while the
    declaration they were written against is removed from underneath them. The
    scene reports such types in `unattempted` instead of editing the document,
    and is the right tool there.

Until idfkit 1.0.0-rc.6 this function carried a resolution rule of its own and
disagreed with both the engine and the renderer. It now resolves through the
scene, so the two cannot drift apart again. Models it draws differently than
before are listed in the library's changelog.

## See also

- [What parity means](../explanation/parity.md) for how availability is
  recorded and where this capability stands
- [Geometry API reference](../api/geometry.md) for the Python surface in full
- [`@idfkit/geometry`](../reference/typescript/geometry.md) for the TypeScript
  surface in full
