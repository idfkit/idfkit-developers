# How to migrate models between EnergyPlus versions

EnergyPlus ships a new release roughly twice a year, and each release can
rename objects, drop fields, or alter defaults. idfkit's
[`migrate()`][idfkit.migration.runner.migrate] orchestrates the
`Transition-VX-to-VY` binaries shipped in `PreProcess/IDFVersionUpdater` to
forward-migrate an IDF model across one or more version steps in a single
call.

There are two ways to migrate a model:

| Approach | When to use |
|----------|-------------|
| Explicit `migrate(model, target_version=...)` | You want to inspect the migrated model, the structural diff, or per-step diagnostics before doing anything else. |
| `simulate(model, ..., auto_migrate=True)` | You want to run a simulation against the installed EnergyPlus and don't care about the intermediate steps. |

!!! note "Forward only"
    EnergyPlus does not ship reverse transition binaries. Asking to migrate
    *backwards* (target older than source) always raises
    [`VersionMismatchError`][idfkit.exceptions.VersionMismatchError] with
    `direction == "backward"`.

{{ parity("version-migration") }}

## Explicit Migration

Call [`migrate()`][idfkit.migration.runner.migrate] directly when you need
the migrated [`IDFDocument`][idfkit.document.IDFDocument] in hand:

```python
--8<-- "docs/snippets/migration_versions/quick_start.py:example"
```

The returned [`MigrationReport`][idfkit.migration.report.MigrationReport] gives
you the migrated `migrated_model`, the `source_version`/`target_version` range
actually traversed, per-step `steps` diagnostics, a structural `diff`, a
`success` flag, and a `summary()` for logs. For the full field list, see the
[Migration API reference](../api/migration.md).

`migrated_model` is always a document. When the model is already at the target,
no step runs, `report.steps` is empty and `migrated_model` is a copy of the
input. It has no `filepath`, so a bare `save()` raises `ValueError` rather than
overwrite the original with a model at another version: save it to an explicit
path.

Pass a document type from `idfkit.versioned` as the target to type the result
for that release: `migrate(model, IDFDocumentV25_2)` makes
`report.migrated_model` an `IDFDocumentV25_2`. A version tuple or string gives
an `AnyIDFDocument`.

### Caching

`migrate()` remembers the result of each migration in the running process. A
second migration of the same content to the same target reuses it without
running the transition binaries; `report.from_cache` is then `True` and `steps`
are the records of the earlier run. Pass `cache=False` to always run them, or
call `clear_migration_cache()` from `idfkit.migration` to forget every result.
The cache is bypassed when `work_dir` or `keep_work_dir` is given, because those
ask for the per-step files.

## CLI

The `idfkit migrate` subcommand is a thin wrapper over `migrate()` for shell
users. It loads the input IDF, forward-migrates it through the installed
`IDFVersionUpdater` transition binaries, and writes the result to disk.

### Basic usage

```bash
# Migrate to the installed EnergyPlus version; e.g. writes old-v25-2-0.idf next to input
idfkit migrate old.idf

# Explicit target and output path
idfkit migrate old.idf --to 25.2 -o new.idf

# Machine-readable report (suppresses stderr progress output)
idfkit migrate old.idf --to 25.2 --json
```

When `--to` is omitted the target is the version of the EnergyPlus installation
that runs the transition binaries (`--energyplus`, or the one found
automatically), which is the newest release that installation can simulate;
with no installation found the command exits with status 2. A `--to` naming a
release idfkit does not support is refused with status 2, not moved to the
nearest one. When `--output` is omitted the result is written to
`<stem>-v<major>-<minor>-<patch>.idf` next to the input. When the model is
already at the target, nothing is written unless `--output` is given, in which
case the input is copied there.

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Migration succeeded (or source version equals target: a no-op, which writes no file without `--output`) |
| `1` | Migration runtime failure (a transition binary exited non-zero) |
| `2` | Argument or configuration error (bad version, missing input, EnergyPlus not found) |

### Flag reference

| Flag | Description |
|------|-------------|
| `INPUT` | Path to the source IDF file (positional, required) |
| `-o`, `--output OUTPUT` | Output IDF path. Defaults to `<stem>-v<target>.idf` next to the input. |
| `--to VERSION` | Target EnergyPlus version (e.g. `25.2`). Defaults to the version of the EnergyPlus installation used. |
| `--energyplus PATH` | Path to the EnergyPlus install or executable. Auto-discovered via `$ENERGYPLUS_DIR`, `PATH`, and platform defaults when omitted. |
| `--work-dir DIR` | Directory in which to stage per-step transition output. Defaults to a temporary directory. |
| `--keep-work-dir` | Preserve intermediate files for inspection (only meaningful with the default temp directory). |
| `--json` | Emit a JSON report on stdout instead of the human-readable summary. Also suppresses stderr progress output. |
| `-q`, `--quiet` | Suppress progress output. |

## Transparent Migration During `simulate()`

When you only want a simulation result, pass `auto_migrate=True` and
`simulate()` will forward-migrate the model on your behalf if the
installed EnergyPlus version differs:

```python
--8<-- "docs/snippets/migration_versions/auto_migrate_simulate.py:example"
```

The resulting [`SimulationResult.migration_report`][idfkit.simulation.result.SimulationResult.migration_report]
is populated whenever a migration ran, and `None` otherwise. Without
`auto_migrate=True`, a version mismatch raises
[`VersionMismatchError`][idfkit.exceptions.VersionMismatchError] before the
simulation starts.

## Async Migration

Both APIs have async counterparts with identical semantics:

- [`async_migrate()`][idfkit.migration.async_runner.async_migrate] — non-blocking
  equivalent of `migrate()`, useful inside FastAPI handlers or other async
  contexts where you want only the migration.
- [`async_simulate(..., auto_migrate=True)`][idfkit.simulation.async_runner.async_simulate]
  — accepts the same `auto_migrate` flag and populates `migration_report`
  on the returned `SimulationResult`.

## Partial Failures

If a transition step fails midway,
[`MigrationError`][idfkit.exceptions.MigrationError] is raised. The
exception carries `from_version`, `to_version`, the binary's `exit_code`
and `stderr`, and `completed_steps` — the prefix of `(from, to)` pairs that
ran successfully — so you can recover partial progress or report exactly
which transition broke.

## See Also

- [Migration API](../api/migration.md) — full reference for `migrate`, `MigrationReport`, and the `Migrator` protocol.
- [Version Compatibility](../concepts/version-compatibility.md) — the sibling `idfkit check` subcommand for *statically* linting your Python code for cross-version breakage before you migrate.
- [How to run a simulation](running.md) — full `simulate()` parameter reference.
- [How to handle simulation errors](errors.md) — handling `VersionMismatchError` from `simulate()`.
