# How to access simulation results

The `SimulationResult` class provides structured access to all EnergyPlus
output files with lazy loading for efficient memory usage.

{{ parity("local-simulation") }}

## SimulationResult Overview

```python
--8<-- "docs/snippets/simulation/results/simulationresult_overview.py:example"
```

## Output File Paths

Access paths to specific output files:

```python
--8<-- "docs/snippets/simulation/results/output_file_paths.py:example"
```

Each returns `None` if the file wasn't produced.

The parsed accessors behave differently. `result.sql`, `csv`, `eso`, `mtr`,
`html` and `variables` never return `None`: when the run produced no such file
they raise `OutputNotFoundError` (from `idfkit.exceptions`, a
`FileNotFoundError` subclass), whose message names the output object to add to
the model. When an output is optional, test its path first:

```python
if result.sql_path is not None:
    sql = result.sql
```

## Error Report

Parse warnings and errors from the `.err` file:

```python
--8<-- "docs/snippets/simulation/results/error_report.py:example"
```

See [how to handle simulation errors](errors.md) for detailed error parsing.

## SQL Database

Query time-series and tabular data from the SQLite output:

```python
--8<-- "docs/snippets/simulation/results/sql_database.py:example"
```

See [how to query simulation SQL output](sql-queries.md) for detailed SQL parsing.

## Output Variables

Discover available output variables from `.rdd`/`.mdd` files:

```python
--8<-- "docs/snippets/simulation/results/output_variables.py:example"
```

See [how to discover output variables](output-discovery.md) for variable discovery.

## CSV Output

Parse CSV time-series output:

```python
--8<-- "docs/snippets/simulation/results/csv_output.py:example"
```

## HTML Tabular Output

Parse the HTML tabular summary file that EnergyPlus produces alongside every
simulation. Its name follows the run's `output_suffix`: `eplusTable.htm` by
default, `eplustbl.htm` for `"L"`, `eplus-table.htm` for `"D"`.

```python
--8<-- "docs/snippets/simulation/results/html_tabular_output.py:example"
```

Each `HTMLTable` holds its column headers in `header`, taken from the table's
first row when the file has no `<th>` cells, as EnergyPlus writes them. `rows`
excludes that header row, so do not skip `rows[0]`.

For the attributes and helper methods of each `HTMLTable`, see the
[`HTMLTable` reference](../api/simulation/results.md#htmltable).

You can also parse a standalone HTML file without a full simulation:

```python
--8<-- "docs/snippets/simulation/results/html_tabular_output_2.py:example"
```

This replaces eppy's `readhtml` module.

## Lazy Loading

Output files are parsed only when accessed:

```python
--8<-- "docs/snippets/simulation/results/lazy_loading.py:example"
```

This keeps memory usage low, especially for batch simulations where you
might only need specific outputs.

## Releasing File Handles

Accessing `result.sql` opens a SQLite connection on first use and caches it.
That connection holds an OS-level file handle on `eplus.sql`. On **Windows**,
the handle locks the file, so deleting the run directory while the result is
alive fails with `PermissionError [WinError 32]` — typically when the run
directory lives inside a `tempfile.TemporaryDirectory` or is removed with
`shutil.rmtree`. POSIX systems don't lock on open, so this only affects
Windows.

`SimulationResult` is a context manager: exiting the `with` (or `async with`)
block calls [`cleanup()`][idfkit.simulation.result.SimulationResult.cleanup].
It closes the connection and, when `simulate()` created a temporary run
directory because no `output_dir` was given, deletes that directory. A caller's
`output_dir`, a remote `fs` directory and a cache entry are never deleted
(`result.owns_run_dir` is `False` for them). Read everything you need inside the
block:

```python
--8<-- "docs/snippets/simulation/results/releasing_file_handles.py:example"
```

[`close()`][idfkit.simulation.result.SimulationResult.close] only releases the
connection and leaves `run_dir` in place. It is idempotent and resets the cached
connection, so touching `result.sql` afterwards transparently reopens it. The other accessors
(`errors`, `csv`, `eso`, `html`, `variables`) read their files eagerly and
hold no handles, so they need no cleanup.

## Reconstructing from Directory

Inspect results from a previous simulation. Pass `output_suffix=` when the
run used a style other than the default `"C"`:

```python
--8<-- "docs/snippets/simulation/results/reconstructing_from_directory.py:example"
```

## Full attribute and property reference

`SimulationResult` exposes many more attributes, lazy properties, and output
file paths than the recipes above use. For the complete, always-current list —
generated from the source — see the
[`SimulationResult` reference](../api/simulation/results.md#simulationresult).

## See Also

- [How to query simulation SQL output](sql-queries.md) — Detailed SQL database access
- [How to discover output variables](output-discovery.md) — Finding available variables
- [How to handle simulation errors](errors.md) — Parsing error reports
