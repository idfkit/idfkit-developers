# How to migrate from eppy

idfkit provides a compatibility layer so most eppy code works with only
minor changes. You can migrate gradually -- all the eppy-style methods
listed below are available alongside the newer idfkit API.

{{ parity("eppy-compatibility") }}

## Loading a file

**eppy** requires you to locate and pass the IDD file yourself:

```python
--8<-- "docs/snippets/migration/loading_a_file.py:example"
```

**idfkit** bundles schemas and detects the version automatically:

```python
--8<-- "docs/snippets/migration/loading_a_file_2.py:example"
```

No IDD path is needed. If you want to target a specific EnergyPlus version:

```python
--8<-- "docs/snippets/migration/loading_a_file_3.py:example"
```

## Quick reference

The table below maps common eppy patterns to their idfkit equivalents.
The **eppy alias** column shows that the old spelling still works in idfkit
when one exists.

| Task | eppy | idfkit | eppy alias in idfkit? |
|------|------|--------|-----------------------|
| Load file | `IDF(idd, idf)` | `load_idf(path)` | -- |
| Create object | `idf.newidfobject("ZONE", Name=...)` | `doc.add("Zone", "name", ...)` | `doc.newidfobject(...)` |
| Get collection | `idf.idfobjects["ZONE"]` | `doc["Zone"]` or `doc.zones` | `doc.idfobjects[...]` |
| Get object by name | `idf.getobject("ZONE", "name")` | `doc["Zone"]["name"]` | `doc.getobject(...)` |
| Remove object | `idf.removeidfobject(obj)` | `doc.remove(obj)` | `doc.removeidfobject(obj)` |
| Remove by index | `idf.popidfobject("ZONE", 0)` | `doc.popidfobject("Zone", 0)` | `doc.popidfobject(...)` |
| Copy object | `idf.copyidfobject(obj)` | `doc.copyidfobject(obj)` | `doc.copyidfobject(obj)` |
| Object type | `obj.key` | `obj.obj_type` | `obj.key` |
| Object name | `obj.Name` | `obj.name` | `obj.Name` |
| Parent document | `obj.theidf` | `obj._document` | `obj.theidf` |
| Field names | `obj.fieldnames` | `obj.field_order` | `obj.fieldnames`[^fields] |
| Field values | `obj.fieldvalues` | `[obj.get(f) for f in obj.field_order]` | `obj.fieldvalues`[^fields] |
| Field IDD info | `obj.getfieldidd(name)` | `obj.get_field_idd(name)` | `obj.getfieldidd(name)` |
| Field range | `obj.getrange(name)` | `obj.getrange(name)` | `obj.getrange(name)` |
| Check range | `obj.checkrange(name)` | `obj.checkrange(name)` | `obj.checkrange(name)` |
| Follow reference | `obj.get_referenced_object(name)` | `obj.get_referenced_object(name)` | `obj.get_referenced_object(name)` |
| Find referrers | `obj.getreferingobjs()` | `obj.get_referring_objects()` | `obj.getreferingobjs()` |
| Group dict | `idf.getiddgroupdict()` | `doc.getiddgroupdict()` | `doc.getiddgroupdict()` |
| Get surfaces | `idf.getsurfaces()` | `doc.getsurfaces()` | `doc.getsurfaces()` |
| Save file | `idf.save()` | `doc.save()` | `doc.save()` |
| Save as | `idf.saveas(path)` | `doc.saveas(path)` | `doc.saveas(path)` |
| Save copy | `idf.savecopy(path)` | `doc.savecopy(path)` | `doc.savecopy(path)` |
| Output type | `idf.outputtype = "compressed"` | `doc.save(output_type="compressed")` | -- |
| Run simulation | `idf.run(weather)` | `simulate(doc, weather)` | `doc.run(weather)` |
| Batch update | `json_functions.updateidf(idf, d)` | `obj.field = value`, per field | `doc.update(d)`[^update] |
| HTML tables | `readhtml.titletable(html)` | `result.html.titletable()` | -- |
| Window-wall ratio | `idf.set_wwr(0.4)` | `set_wwr(doc, 0.4)` | -- |
| Match surfaces | `idf.intersect_match()` | `intersect_match(doc)` | -- |
| Surface geometry | `surface.area`, `.azimuth`, `.tilt`, `.coords` | `calculate_surface_area(surface)`, ... | `surface.area`, ... |

[^update]:
    `doc.update(d)` is part of the eppy compatibility surface; the native
    form assigns fields on the object (see [Batch updates](#batch-updates)).

[^fields]:
    `obj.fieldnames` and `obj.fieldvalues` reproduce eppy's layout: index 0 is
    the type key, index 1 the name, the names are eppy's capitalised spellings,
    extensible groups are flattened and trailing blanks trimmed. eppy's index
    arithmetic, such as `fieldvalues[2:]`, ports unchanged. `obj.field_order`
    is the schema's snake_case field order, without the type key or the name.

## Creating objects

**eppy:**

```python
--8<-- "docs/snippets/migration/creating_objects.py:example"
```

**idfkit:**

```python
--8<-- "docs/snippets/migration/creating_objects_2.py:example"
```

Or using the eppy-compatible method:

```python
--8<-- "docs/snippets/migration/creating_objects_3.py:example"
```

`newidfobject` takes eppy's field spellings, and the eppy idiom above, creating
a blank object and filling it afterwards, runs as it is. Unlike `doc.add()`, it
does not validate the object when it creates it: pass `validate=True`, or call
`validate_document(doc)` once the object is filled.

## Accessing fields

**eppy** uses the capitalised IDD field names:

```python
--8<-- "docs/snippets/migration/accessing_fields.py:example"
```

**idfkit** uses snake_case names:

```python
--8<-- "docs/snippets/migration/accessing_fields_2.py:example"
```

Both styles resolve to the same underlying data at run time, including eppy's
flattened extensible spellings such as `Vertex_1_Xcoordinate`, which work with
a `DeprecationWarning` naming the grouped form (`vertices[0].vertex_x_coordinate`).

A type checker is stricter on a typed object, such as one from
`doc["Zone"]["Office"]`: its class declares the snake_case names only, so
pyright reports `zone.X_Origin` and `zone.x_orign` alike, though the first one
runs. Objects reached through the eppy API (`doc.idfobjects["ZONE"]`,
`doc.newidfobject(...)`, `doc.getobject(...)`) are untyped and accept either
spelling, so eppy-style field access keeps type-checking while you move it to
snake_case.

## Reference tracking (new in idfkit)

eppy has no built-in way to find which objects reference a given name.
idfkit maintains a live reference graph:

```python
--8<-- "docs/snippets/migration/reference_tracking_new_in_idfkit.py:example"
```

## Renaming with cascading updates (new in idfkit)

In eppy, renaming a zone requires you to manually update every surface,
people, lights, and other object that references it. In idfkit the
reference graph handles this automatically:

```python
--8<-- "docs/snippets/migration/renaming_with_cascading_updates_new_in_idfkit.py:example"
```

## Validation (new in idfkit)

```python
--8<-- "docs/snippets/migration/validation_new_in_idfkit.py:example"
```

## Saving files

**eppy** saves through methods on the IDF object:

```python
--8<-- "docs/snippets/migration/saving_files.py:example"
```

**idfkit** supports the same methods:

```python
--8<-- "docs/snippets/migration/saving_files_2.py:example"
```

`save()` writes IDF text and refuses an `.epJSON` or `.json` path; use
`save_epjson()` for those.

Saving over the file the model was read from drops its `!` comments and
re-sorts its objects, and warns with `FormattingLossWarning`, unless the model
was loaded with `load_idf(path, preserve_formatting=True)`; see [Preserve a
file's formatting](how-to/preserve-formatting.md). A save keeps the file's
encoding unless you pass `encoding=`.

Or use the standalone writer for more control:

```python
--8<-- "docs/snippets/migration/saving_files_3.py:example"
```

## Output formatting modes

**eppy** controls output formatting with `idf.outputtype`:

```python
--8<-- "docs/snippets/migration/output_formatting_modes.py:example"
```

**idfkit** passes the mode to the writer:

```python
--8<-- "docs/snippets/migration/output_formatting_modes_2.py:example"
```

## Following references

**eppy** lets you follow a reference field to get the target object:

```python
--8<-- "docs/snippets/migration/following_references.py:example"
```

**idfkit** provides the same method:

```python
--8<-- "docs/snippets/migration/following_references_2.py:example"
```

## Finding referring objects

**eppy** finds all objects that reference a given object:

```python
--8<-- "docs/snippets/migration/finding_referring_objects.py:example"
```

**idfkit** provides both the eppy spelling and a corrected alias:

```python
--8<-- "docs/snippets/migration/finding_referring_objects_2.py:example"
```

## Range checking

**eppy** provides range checking on numeric fields:

```python
--8<-- "docs/snippets/migration/range_checking.py:example"
```

**idfkit** supports the same API:

```python
--8<-- "docs/snippets/migration/range_checking_2.py:example"
```

## Removing objects by index

**eppy** removes objects by index with `popidfobject`:

```python
--8<-- "docs/snippets/migration/removing_objects_by_index.py:example"
```

**idfkit:**

```python
--8<-- "docs/snippets/migration/removing_objects_by_index_2.py:example"
```

## Batch updates

**eppy** uses `json_functions.updateidf()` for parametric sweeps:

```python
--8<-- "docs/snippets/migration/batch_updates.py:example"
```

**idfkit** keeps the same call as part of its eppy compatibility surface. It
is `IDFDocument.update`, which takes `Type.Name.field` keys, and it exists so
that eppy code runs unchanged:

```python
--8<-- "docs/snippets/migration/batch_updates_2.py:example"
```

The native form fetches the object once and assigns its fields directly. Each
assignment is checked against the schema, and a type checker sees the field
names of the object type:

```python
--8<-- "docs/snippets/migration/batch_updates_3.py:example"
```

## Geometry

eppy relies on [geomeppy](https://github.com/jamiebull1/geomeppy) for
geometry operations. eppy's own surface attributes, `area`, `azimuth`, `tilt`,
`height`, `width` and `coords`, work on idfkit surfaces that have vertices. For
new code, idfkit ships its own `Vector3D` and `Polygon3D` classes and functions,
with no external dependencies:

```python
--8<-- "docs/snippets/migration/geometry.py:example"
```

### Building transforms

Translate or rotate all surfaces in the model:

```python
--8<-- "docs/snippets/migration/building_transforms.py:example"
```

### Window-wall ratio

**geomeppy** sets window-wall ratios as a method on the IDF:

```python
--8<-- "docs/snippets/migration/set_wwr.py:example"
```

**idfkit** uses a standalone function:

```python
--8<-- "docs/snippets/migration/set_wwr_2.py:example"
```

!!! tip "Construction preservation"
    When `construction` is not specified, `set_wwr` preserves the construction
    from any existing fenestration on each wall. Cross-references (e.g. from
    output variables) are also re-pointed to the new windows.

### Surface intersection and matching

**geomeppy** matches adjacent surfaces as a method on the IDF:

```python
--8<-- "docs/snippets/migration/intersect_match.py:example"
```

**idfkit** uses a standalone function:

```python
--8<-- "docs/snippets/migration/intersect_match_2.py:example"
```

## Strict field access (new in idfkit)

idfkit has two different strictness settings:

- **Strict parsing** (`load_idf(..., strict_parsing=True)`) validates IDF input while
  reading and is enabled by default.
- **Strict field access** (`load_idf(..., strict=True)`) raises on mistyped attribute
  names when reading or writing object fields, and checks each value you assign
  against the schema. This is on by default.

eppy silently returns an empty string when you mistype a field name,
making bugs hard to find. idfkit enables **strict field access** by
default to catch typos immediately:

```python
--8<-- "docs/snippets/migration/strict_mode.py:example"
```

eppy code that assigns loosely typed values, such as a number as a string,
now raises `ValidationFailedError` on assignment and
on `update()`: a wrong type, a choice the field does not list, or a number out
of range is refused, as `doc.add()` refuses it. Fix the value, or disable strict
field access with `strict=False` to store it as given, for example when loading
third-party IDF files that may contain non-standard fields.

When an eppy-only attribute such as `obj.obj` or `obj.objidd` is refused, the
`InvalidFieldError` carries a `hint` naming the idfkit way to get it.

## Running a simulation

**eppy** runs simulations directly on the IDF object:

```python
--8<-- "docs/snippets/migration/running_a_simulation.py:example"
```

**idfkit** uses a standalone `simulate()` function (recommended):

```python
--8<-- "docs/snippets/migration/running_a_simulation_2.py:example"
```

Or use the eppy-compatible convenience method:

```python
--8<-- "docs/snippets/migration/running_a_simulation_3.py:example"
```

## HTML tabular output

**eppy** parses HTML tabular output using `readhtml`:

```python
--8<-- "docs/snippets/migration/html_tabular_output.py:example"
```

**idfkit** parses HTML output as part of `SimulationResult`:

```python
--8<-- "docs/snippets/migration/html_tabular_output_2.py:example"
```

Or parse a standalone HTML file:

```python
--8<-- "docs/snippets/migration/html_tabular_output_3.py:example"
```
