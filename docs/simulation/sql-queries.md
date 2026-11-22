# How to query simulation SQL output

The `SQLResult` class provides structured access to EnergyPlus's SQLite
output database, containing time-series data, tabular reports, and metadata.

{{ parity("local-simulation") }}

## Opening the Database

```python
from idfkit.simulation import simulate

result = simulate(model, weather)

sql = result.sql  # raises OutputNotFoundError if the run wrote no .sql file
```

Or open directly:

```python
--8<-- "docs/snippets/simulation/sql-queries/opening_the_database_2.py:example"
```

## Time-Series Data

### Basic Query

```python
--8<-- "docs/snippets/simulation/sql-queries/basic_query.py:example"
```

A query returns a `TimeSeriesResult`. For its full list of attributes and
methods, see the
[`TimeSeriesResult` reference](../api/simulation/sql.md#timeseriesresult).

### Filtering by Environment

Specify which simulation environment to query:

```python
--8<-- "docs/snippets/simulation/sql-queries/filtering_by_environment.py:example"
```

The `environment` parameter accepts:

| Value | Description |
|-------|-------------|
| `None` | The run periods when the variable has data there, else the design days, so the two never mix (default) |
| `"annual"` | Weather-file run period data only |
| `"sizing"` | Design day data only |
| `"all"` | Design days and run periods, in run order |

Any other value raises `ValueError`. Asking for an environment the variable has
no data in raises `ResultLookupError`.

### Reading Several Series

Each `get_timeseries()` call scans the whole `ReportData` table.
[`get_timeseries_many()`][idfkit.simulation.parsers.sql.SQLResult.get_timeseries_many]
reads many series in a single scan and returns them in the order asked. Each
item is a variable name, a `(name, key)` or `(name, key, frequency)` tuple, or a
`VariableInfo` from `list_variables()`:

```python
series = sql.get_timeseries_many([("Zone Mean Air Temperature", zone) for zone in ["ZONE 1", "ZONE 2"]])
```

### Converting to DataFrame

```python
--8<-- "docs/snippets/simulation/sql-queries/converting_to_dataframe.py:example"
```

Requires pandas: `pip install idfkit[dataframes]`

### Plotting Time Series

```python
--8<-- "docs/snippets/simulation/sql-queries/plotting_time_series.py:example"
```

Requires matplotlib or plotly: `pip install idfkit[plot]`

## Tabular Data

### Query Tabular Reports

```python
--8<-- "docs/snippets/simulation/sql-queries/query_tabular_reports.py:example"
```

Each row is a `TabularRow`. Its `value` is the cell text with the padding
stripped; an empty cell is `""`. `row.as_float()` parses it as a number. For
its full list of attributes, see the
[`TabularRow` reference](../api/simulation/sql.md#tabularrow).

When filters are given and no row matches, `get_tabular_data()` raises
`ResultLookupError`, naming the filter that matches nothing. Without filters it
returns `[]` for a database with no tabular reports.

### Read a Single Number

`get_tabular_float()` returns one cell as a float. It and `get_tabular_value()`,
which returns the text, raise `ResultLookupError` when no row or several rows
match:

```python
area = sql.get_tabular_float(
    "AnnualBuildingUtilityPerformanceSummary",
    "Building Area",
    "Net Conditioned Building Area",
    "Area",
)
```

### Filter by Table

```python
--8<-- "docs/snippets/simulation/sql-queries/filter_by_table.py:example"
```

### Common Reports

| Report Name | Description |
|-------------|-------------|
| `AnnualBuildingUtilityPerformanceSummary` | Energy use summary |
| `InputVerificationandResultsSummary` | Model summary |
| `EnvelopeSummary` | Building envelope details |
| `LightingSummary` | Lighting power densities |
| `EquipmentSummary` | Equipment capacities |
| `HVACSizingSummary` | HVAC sizing results |
| `ZoneComponentLoadSummary` | Zone load components |

## Variable Metadata

### List Available Variables

```python
--8<-- "docs/snippets/simulation/sql-queries/list_available_variables.py:example"
```

Each entry is a `VariableInfo`. For its full list of attributes, see the
[`VariableInfo` reference](../api/simulation/sql.md#variableinfo).

### Search Variables

```python
--8<-- "docs/snippets/simulation/sql-queries/search_variables.py:example"
```

## Environment Metadata

### List Environments

```python
--8<-- "docs/snippets/simulation/sql-queries/list_environments.py:example"
```

### Environment Types

| Type | Value | Description |
|------|-------|-------------|
| Design Day | 1 | `SizingPeriod:DesignDay` simulation |
| Design Run Period | 2 | `SizingPeriod:WeatherFileDays` |
| Weather File Run Period | 3 | Regular `RunPeriod` simulation |

Each environment is an `EnvironmentInfo`. For its full list of attributes, see
the [`EnvironmentInfo` reference](../api/simulation/sql.md#environmentinfo).

## Timestamps

EnergyPlus uses a fixed reference year (2017) for timestamps. The SQLResult
automatically converts database timestamps to Python `datetime` objects.

### EnergyPlus Time Convention

- Hour 24 in the database → midnight of the next day
- Warmup days are filtered out automatically

```python
--8<-- "docs/snippets/simulation/sql-queries/energyplus_time_convention.py:example"
```

## Context Manager

`SQLResult` is a context manager for clean database cleanup:

```python
--8<-- "docs/snippets/simulation/sql-queries/context_manager.py:example"
```

`SimulationResult` — the usual entry point via `simulate()` — is also a
context manager. Exiting the `with` block closes the SQLite connection that
`result.sql` opened lazily, which matters on Windows where the open
connection locks `eplus.sql` and blocks deleting the run directory. When
`simulate()` ran in a temporary directory (no `output_dir`), the exit also
deletes that directory:

```python
--8<-- "docs/snippets/simulation/sql-queries/simulationresult_context_manager.py:example"
```

See [Releasing File Handles](results.md#releasing-file-handles) for details.

## Error Handling

```python
--8<-- "docs/snippets/simulation/sql-queries/error_handling.py:example"
```

`ResultLookupError` (from `idfkit.exceptions`) subclasses `KeyError`, so code
that catches `KeyError` keeps working. `get_timeseries()` also raises it when
several keys or frequencies match: pass `key_value` or `frequency` to pick one.

## Performance Tips

1. **Filter early** — Use the `environment` parameter to reduce data size
2. **Query once** — Store results in variables rather than re-querying
3. **Read several series together** — `get_timeseries_many()` scans the data once, where a loop of `get_timeseries()` scans it per call
4. **Use lazy loading** — Don't access `result.sql` if you don't need it

## See Also

- [How to access simulation results](results.md) — Overview of result parsing
- [How to plot simulation results](plotting.md) — Visualizing query results
- [How to discover output variables](output-discovery.md) — Finding available variables
