# Common Errors

This page covers common errors you may encounter when using idfkit and how
to resolve them.

{{ parity("local-simulation") }}

## idfkit Errors

### EnergyPlusNotFoundError

```
EnergyPlusNotFoundError: Could not find EnergyPlus installation
```

**Cause:** idfkit cannot locate an EnergyPlus installation.

**Solutions:**

1. Install EnergyPlus from [energyplus.net/downloads](https://energyplus.net/downloads)

2. Set the `ENERGYPLUS_DIR` environment variable:
   ```bash
   export ENERGYPLUS_DIR=/path/to/EnergyPlus-24-1-0
   ```

3. Pass the path explicitly:
   ```python
   from idfkit.simulation import find_energyplus
   config = find_energyplus(path="/path/to/EnergyPlus")
   result = simulate(model, weather, energyplus=config)
   ```

### SimulationError

```
SimulationError: Weather file not found: /path/to/weather.epw
```

**Cause:** The specified weather file doesn't exist.

**Solutions:**

1. Verify the path is correct
2. Use absolute paths instead of relative
3. Download weather files using `WeatherDownloader`

### SimulationError (Timeout)

```
SimulationError: Simulation timed out after 3600 seconds
```

**Cause:** The simulation exceeded the timeout limit.

**Solutions:**

1. Increase the timeout:
   ```python
   result = simulate(model, weather, timeout=7200.0)
   ```

2. Use design-day-only mode for testing:
   ```python
   result = simulate(model, weather, design_day=True)
   ```

3. Check for infinite loops in the model

### NoDesignDaysError

```
NoDesignDaysError: No heating design days found in DDY file
```

**Cause:** The DDY file doesn't contain the requested design day type.

**Solutions:**

1. Check available design days:
   ```python
   ddm = DesignDayManager("file.ddy")
   print(ddm.summary())
   ```

2. Use a different percentile:
   ```python
   ddm.apply_to_model(model, heating="99%", cooling="1%")
   ```

### GeocodingError

```
GeocodingError: No results found for address: ...
```

**Cause:** The address couldn't be geocoded.

**Solutions:**

1. Try a more specific address
2. Try a different format (city name, ZIP code, landmark)
3. Use coordinates directly:
   ```python
   results = index.nearest(41.88, -87.63)
   ```

## Import Errors

### Missing Optional Dependencies

```
ImportError: pandas is required for DataFrame conversion
```

**Solutions:**

```bash
# Install specific extra
pip install idfkit[dataframes]

# Or install all extras
pip install idfkit[all]
```

Common extras:

| Feature | Install Command |
|---------|-----------------|
| DataFrames | `pip install idfkit[pandas]` |
| Plotting (matplotlib) | `pip install idfkit[plot]` |
| Plotting (plotly) | `pip install idfkit[plotly]` |
| Progress bars (tqdm) | `pip install idfkit[progress]` |
| S3 Storage | `pip install idfkit[s3]` |
| Async S3 Storage | `pip install idfkit[async-s3]` |

### boto3 Not Found

```
ImportError: boto3 is required for S3FileSystem
```

**Solution:**

```bash
pip install idfkit[s3]
```

## Validation Errors

### Reference to Non-Existent Object

```
[ERROR] People:'Zone1_People'.zone_or_zonelist_or_space_or_spacelist_name: Reference to non-existent object 'Zone 1' (looked up in SpaceAndSpaceListNames or ZoneAndZoneListNames). Did you mean 'Zone1'?
```

**Cause:** A field references an object name that doesn't exist. The message
quotes the value as written, names the reference lists it was looked up in,
and suggests a close name when there is one. The same check (`E009`) fires when
the name exists but belongs to an object of the wrong type:
`Reference to 'Always', which is a Schedule:Constant, not in SpaceAndSpaceListNames or ZoneAndZoneListNames`.

**Solutions:**

1. Check the object name spelling (case-insensitive)
2. Add the missing object:
   ```python
   model.add("Zone", "Zone1", ...)
   ```
3. Fix the reference:
   ```python
   people_obj.zone_name = "Correct_Zone_Name"
   ```

### `add()` Refused: Unknown Field

```
InvalidFieldError: add() of object type 'Zone' refused; nothing was added:
  - X Origin: unknown (spell it 'x_origin')
```

A misspelling adds a suggestion:

```
InvalidFieldError: add() of object type 'Zone' refused; nothing was added:
  - x_orgin: unknown (not a field of Zone)
Did you mean 'x_origin'?
```

**Cause:** A keyword given to `add()` is not a field of the object type.
`validate=False` skips value, required-field and range checks, but not field
names, so this is raised either way.

**Solutions:**

1. Use the snake_case schema key the message suggests: `x_origin`, not `"X Origin"`.
2. Pass the object's name as the `name` argument, not inside `fields`.
3. For a type with no Name field, such as `Output:Variable` or `Output:Meter`,
   pass no name and give its first field instead. A name given anyway is
   refused: `InvalidFieldError: Output:Variable has no Name field, so "x" would be dropped on write. Pass it as a field instead: key_value="x".`
   ```python
   model.add("Output:Meter", key_name="Electricity:Facility", reporting_frequency="Hourly")
   ```

### `add()` Refused: Malformed Extensible Group

```
TypeError: add() of object type 'Output:Table:SummaryReports' refused; nothing was added:
  - reports: wrapper-value (expected a list, got str)
```

**Cause:** An extensible group was given as something other than a list of
dicts, such as a string, a list of tuples or another object's live view, or a
group used a key the group does not define.

**Solution:** Pass a list of dicts keyed by the group's field names. Copy another
object's groups with `.as_list()`:

```python
model.add("Output:Table:SummaryReports", reports=[{"report_name": "AllSummary"}])
model.add("BuildingSurface:Detailed", "Wall 2", ..., vertices=wall.vertices.as_list())
```

### Object Not Found

```
ObjectNotFoundError: No Zone named 'Zone2'. Did you mean 'Zone1'?
  Zone names: Zone1
```

**Cause:** `doc["Zone"]["Zone2"]` looked up a name the collection does not
hold. The message suggests close names and lists the ones that exist. Use
`doc["Zone"].get("Zone2")` to get `None` instead.

### Unknown Object Type

```
UnknownObjectTypeWarning: Object type 'Zonee' is in no bundled EnergyPlus release; the collection is empty. Did you mean 'Zone'?
```

**Cause:** `doc["Zonee"]` named a type no EnergyPlus release has. Reading it
returns an empty collection and warns; adding to it raises.

### Assignment Refused in a Strict Document

```
ValidationFailedError: Validation failed with 1 error(s):
  1. [ERROR] Zone:'Office'.multiplier: Expected integer, got str
```

**Cause:** In a strict document, the default, an assigned value is checked
against the schema as `add()` checks it. A wrong type, a choice the field does
not list, a number out of range, or a blank name is refused.

**Solutions:**

1. Assign a value of the field's type and range.
2. Load or create the document with `strict=False` to store such values as given.

### NaN or Infinity Refused

```
InvalidFieldError: Zone 'Office' field 'x_origin' is nan. NaN and infinity are not numbers EnergyPlus or epJSON can hold; give a finite number.
```

**Cause:** A NaN or infinite value was assigned, often from a pandas column
with missing data. It is refused in either strictness mode. Fill or drop the
missing values (`fillna()`) before assigning.

### Required Field Read While Unset

```
MissingRequiredFieldError: Material 'M' has no value for its required field 'thickness'. EnergyPlus refuses an object without it; set it, or read it with obj.get('thickness') to get None when it is missing.
```

**Cause:** Required fields are typed without `None`, so reading one the model
leaves unset raises. Use `obj.get("thickness")` to test whether it is set.

### Required Field Missing

```
[ERROR] People:'Zone1_People'.activity_level_schedule_name: Required field is missing
```

**Cause:** A required field wasn't provided.

**Solution:**

```python
# Add the required field
model.add(
    "People", "Zone1_People",
    zone_or_zonelist_or_space_or_spacelist_name="Zone1",
    number_of_people_schedule_name="Always_On",
    activity_level_schedule_name="Activity_Schedule",  # Required!
    number_of_people_calculation_method="People",
    number_of_people=10,
)
```

## File Format Errors

### Invalid IDF Syntax

```
IDFParseError: Failed to parse object
```

**Cause:** `load_idf()` and `load_epjson()` use strict parsing by default
(`strict_parsing=True`) and found malformed content (for example unknown object
types, invalid bytes, or extra fields on non-extensible objects).

**Solutions:**

1. Check for unclosed objects (missing `;`)
2. Check for invalid field separators
3. Validate with EnergyPlus directly first
4. For migration or best-effort loading of legacy/noisy files, use
   tolerant parsing:
   ```python
   from idfkit import IDFParseError, load_idf

   try:
       doc = load_idf("file.idf")  # strict_parsing=True (default)
   except IDFParseError:
       doc = load_idf("file.idf", strict_parsing=False)
   ```

   For epJSON, `load_epjson("file.epJSON", strict_parsing=False)` does the same.

### Wrong File Format

```
FileFormatError: model.idf looks like an epJSON file (it starts with '{'), not IDF; use load_epjson() to read it
```

**Cause:** An epJSON file was passed to `load_idf()`, or an IDF file to
`load_epjson()`. The message names the format found and the loader to use.
`FileFormatError` is an `IDFParseError` and a `ValueError`, so code catching
either still catches it.

### Version Given as a String

```
TypeError: version must be a (major, minor, patch) tuple, e.g. (24, 1, 0); got '24.1'
```

**Solution:** Pass a tuple: `load_idf("file.idf", version=(24, 1, 0))`.

### Unsupported Schema Version

```
UnsupportedVersionError: EnergyPlus version 99.0.0 is not supported.
Supported versions: 8.9.0, 9.0.1, 9.1.0, ..., 26.1.0, 26.2.0
```

**Cause:** The IDF version isn't supported.

**Solutions:**

1. Check supported versions:
   ```python
   from idfkit import get_schema_manager
   print(get_schema_manager().get_available_versions())
   ```

2. Specify a supported version:
   ```python
   doc = load_idf("file.idf", version=(24, 1, 0))
   ```

### Simulation Version Mismatch

```
VersionMismatchError: Model version 22.1.0 does not match target EnergyPlus version 25.2.0.
Migration chain: 22.1.0->22.2.0 -> 22.2.0->23.1.0 -> ... -> 25.1.0->25.2.0
To fix it, pass auto_migrate=True to simulate() (or to each SimulationJob in a batch) to migrate a copy before the run, or call idfkit.migrate(model, target_version=(25, 2, 0)) to migrate it once and keep the result.
```

**Cause:** `simulate()` was called with a model whose `version` differs
from the installed EnergyPlus, and `auto_migrate` is `False` (the default).

**Solutions:**

1. Forward-migrate transparently inside `simulate()`:
   ```python
   result = simulate(model, weather, auto_migrate=True)
   print(result.migration_report.summary())
   ```

2. Migrate explicitly first so you can inspect the diff:
   ```python
   from idfkit import migrate
   report = migrate(model, target_version=(25, 2, 0))
   result = simulate(report.migrated_model, weather)
   ```

3. From the shell (no Python session required):
   ```bash
   idfkit migrate path/to/model.idf --to 25.2
   ```

!!! warning "Backward migration is not supported"
    EnergyPlus ships no reverse transition binaries, so a model *newer*
    than the installed EnergyPlus cannot be downgraded. Install a newer
    EnergyPlus or load the model explicitly at an older version.

See [how to migrate models between versions](../simulation/migrating-versions.md)
for the full workflow.

## Performance Issues

### Slow Station Index Loading

**Cause:** First load compiles the index from source files.

**Solution:** Subsequent loads are instant (uses cached index).

### Large Memory Usage

**Cause:** Loading many large models or keeping many results in memory.

**Solutions:**

1. Use `model = None` to release memory after use
2. Process batch results incrementally:
   ```python
   for result in batch:
       process(result)
       # Result memory released when loop continues
   ```

## See Also

- [EnergyPlus Issues](energyplus.md) — EnergyPlus-specific errors
- [How to handle simulation errors](../simulation/errors.md) — Detailed error parsing
