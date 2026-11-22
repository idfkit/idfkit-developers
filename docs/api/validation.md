# Validation

`validate_document()` checks a document against the epJSON schema: required
fields, value types, numeric ranges, enum choices, and reference integrity. It
also checks what EnergyPlus would stop on that the schema does not say: compact
schedules it cannot read, schedule values outside their limits, window
constructions, upside-down floors and roofs, and objects with no entries.

| Code | Severity | Reported for |
|------|----------|--------------|
| `E001` | error | A required field, or the name, is missing |
| `E002` | error | A value matches none of the field's accepted types |
| `E003` | error | A value of the wrong type, or NaN or infinity |
| `E004` | error | A choice the field does not list |
| `E005`, `E006` | error | A number below the minimum, or not above an exclusive one |
| `E007`, `E008` | error | A number above the maximum, or not below an exclusive one |
| `E009` | error | A reference to a name that does not exist, or that belongs to the wrong type |
| `E010` | error | More than one instance of a singleton type |
| `E011` | error | A compact schedule EnergyPlus cannot read |
| `E012` | error | A schedule value outside the limits of its `ScheduleTypeLimits` |
| `E013` | error | A window or glass door whose construction has only opaque layers |
| `W001` | warning | No schema available, so schema validation was skipped |
| `W002` | warning | An object type the schema does not have |
| `W003` | warning | A field the object type does not have |
| `W004` | warning | An object such as `OutdoorAir:NodeList` that holds only extensible entries and has none |
| `W005` | warning | A floor that faces up, or a roof or ceiling that faces down |
| `W006` | warning | A reference to a missing `ScheduleTypeLimits`, which EnergyPlus only warns about |

Each issue carries the object it was found on in `ValidationError.obj`, which
is how to tell apart issues on objects of a type with no Name field.

::: idfkit.validation
