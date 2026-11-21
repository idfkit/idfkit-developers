# How to run batch simulations

The `simulate_batch()` function runs multiple EnergyPlus simulations in
parallel using a thread pool, ideal for parametric studies and sensitivity
analyses.

{{ parity("local-simulation") }}

## Basic Usage

```python
--8<-- "docs/snippets/simulation/batch/basic_usage.py:example"
```

## SimulationJob

Define individual simulations with `SimulationJob`:

```python
--8<-- "docs/snippets/simulation/batch/simulationjob.py:example"
```

### SimulationJob Attributes

Every field of [`SimulationJob`][idfkit.simulation.SimulationJob], with its type and its default, is in the API reference. It is generated from the source, so it cannot fall behind the way the table that used to sit here did.


## Parametric Studies

Create model variants for parametric analysis:

```python
--8<-- "docs/snippets/simulation/batch/parametric_studies.py:example"
```

## BatchResult

The `BatchResult` class aggregates results:

```python
--8<-- "docs/snippets/simulation/batch/batchresult.py:example"
```

### Cleaning Up

A job without an `output_dir` runs in a temporary directory that stays on disk
after the batch returns. `batch.cleanup()`, or leaving a
`with simulate_batch(jobs) as batch:` block, deletes those directories. A job's
own `output_dir` is never touched. Read the results you need first:

```python
with simulate_batch(jobs) as batch:
    temps = [r.sql.get_timeseries("Zone Mean Air Temperature", "ZONE 1") for r in batch.succeeded]
# the temporary run directories are gone here
```

## Progress Callbacks

Monitor progress with a callback function:

```python
--8<-- "docs/snippets/simulation/batch/progress_callbacks.py:example"
```

The callback receives:

| Parameter | Type | Description |
|-----------|------|-------------|
| `completed` | `int` | Number of completed jobs |
| `total` | `int` | Total number of jobs |
| `label` | `str` | Label of the just-completed job |
| `success` | `bool` | Whether the job succeeded |

The four are passed by keyword, so name the parameters exactly as above (or
take `**kwargs`). A callback that cannot accept them raises `TypeError` before
any job runs. With `fail_fast=True`, cancelled jobs are reported too, with
`success=False`.

### Rich Progress Bar

```python
--8<-- "docs/snippets/simulation/batch/rich_progress_bar.py:example"
```

## Parallelism

### Worker Count

Control concurrency with `max_workers`:

```python
--8<-- "docs/snippets/simulation/batch/worker_count.py:example"
```

Default: `min(len(jobs), os.cpu_count())`

### Thread vs Process

`simulate_batch` uses **threads** (not processes) because:

- EnergyPlus runs as a subprocess (releases GIL)
- Lower memory overhead than multiprocessing
- Simpler error handling

## Error Handling

Failed simulations don't stop the batch by default:

```python
--8<-- "docs/snippets/simulation/batch/error_handling.py:example"
```

A job that never reached EnergyPlus, because it was refused before the run or
cancelled, carries the reason in `result.refusal`, and its `errors.fatal` holds
one message with that reason.

### Stopping at the First Failure

With `fail_fast=True`, the first failed job stops the batch: queued jobs never
start and running EnergyPlus processes are killed. Those jobs land in
`batch.cancelled`, each with `cancelled` set and a `refusal` naming the job
that failed:

```python
batch = simulate_batch(jobs, fail_fast=True)
for result in batch.cancelled:
    print(result.refusal)
```

### Partial Failures

```python
if not batch.all_succeeded:
    print(f"{len(batch.failed)} jobs failed, {len(batch.cancelled)} cancelled")

    # Process only successful results
    for result in batch.succeeded:
        # ... analyze results
```

## Caching

Share a cache across batch jobs:

```python
--8<-- "docs/snippets/simulation/batch/caching.py:example"
```

## Cloud Storage

Store results in S3:

```python
--8<-- "docs/snippets/simulation/batch/cloud_storage.py:example"
```

With `fs`, every job needs an `output_dir`: if one lacks it, `simulate_batch()`
raises `ValueError` before any job runs.

## Best Practices

1. **Use labels** — Makes progress tracking and debugging easier
2. **Set timeouts** — Prevent runaway simulations from blocking
3. **Share caches** — Avoid redundant work across similar models
4. **Handle failures gracefully** — Check `result.success` before accessing outputs
5. **Start small** — Test with a few jobs before running thousands

## See Also

- [How to run a simulation](running.md) — Single simulation guide
- [How to cache simulation results](caching.md) — Content-addressed caching
- [Examples: Parametric Study](../examples/parametric-study.ipynb) — Complete example
