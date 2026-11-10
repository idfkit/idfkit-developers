# How to use idfkit from several threads

This guide shows you how to load, check, change and write models on a thread pool without
corrupting them, and how to get real parallelism from it. It assumes you already have the work
split into jobs, one model or one variant each.

Everything here is Python. The TypeScript library has no shared-memory threads; its equivalent,
[parsing off the main thread](parse-in-the-browser.md#parse-off-the-main-thread), hands a worker
its own copy of the text.

{{ parity("document-model") }}

!!! note "Requires an idfkit release with the threading fixes"
    The rules below hold from the first idfkit release after 1.2.0, which loads each schema
    version once under a lock and makes its process-wide caches safe on a free-threaded build.

## Choose the kind of concurrency the job needs

Threads are one of four options, and often not the right one. Find the row that matches your
job before writing a thread pool.

| The job | Use | Why |
|---|---|---|
| Run many EnergyPlus simulations on one machine | `simulate_batch` (a thread pool) | The work happens in EnergyPlus subprocesses, so threads run them in parallel on any build of Python, and all of them share one simulation cache. |
| Run simulations from an async web server, or alongside other network calls | `async_simulate_batch` | It never blocks the event loop, and streams results as they finish. |
| Serve many requests from one base model (a web API, a desktop app) | Threads sharing a read-only base model, one copy per request | Loading once and copying per request is far cheaper than loading per request. See [the web-service example](#a-web-service-that-shares-one-base-model). |
| Load, validate, transform or write many models, CPU-bound, on a free-threaded build | A thread pool | Threads run in parallel without pickling models between processes. |
| The same CPU-bound work on a regular build | A process pool | The GIL lets only one thread run Python at a time, so threads would not be faster. |
| Download weather files or geocode addresses | One thread, or a pool over distinct stations | Geocoding is rate-limited to one request a second, so threads do not speed it up, and downloads of one station must not overlap (step 4). |
| Thousands of simulations, or more than one machine | A task queue or a distributed runner | One machine's cores are the limit. See [campaigns beyond one machine](#campaigns-beyond-one-machine). |

## 1. Decide what each thread may touch

Look up what your threads share in this table before writing any code. Everything not listed is
a document, and the last column is what to do with it.

| Threads share | Safe? | What to do |
|---|---|---|
| Nothing but the schema: one document per thread | Yes | Nothing: separate documents are independent. |
| One document that no thread changes | Yes | Nothing, as long as it stays unchanged for as long as the threads read it. |
| One document that some thread changes | **No** | Give each thread a `doc.copy()`, or guard every access with one lock. |
| A batch of simulation jobs | Yes | Leave each job's model unedited until the batch returns. |
| Weather downloads of the same station | **No** | Download each station once before the threads start. |

Reading includes writing a file (`write_idf`, `write_epjson`), validating, copying, following
references (`get_referencing`), attribute reads, and evaluating schedules. Changing includes
`add`, `removeidfobject`, `rename`, and assigning to any field.

A document changed by two threads at once does not fail reliably. Sometimes a reader raises
`RuntimeError: dictionary changed size during iteration`, or the reference graph raises
`KeyError`. As often, nothing raises and the model is simply wrong: an object missing, a
reference left dangling. Do not treat the absence of an exception as evidence that the sharing
was safe.

## 2. Give each thread its own document

When the jobs are independent models, load them on the pool. This is the case that parallelises
best.

```python
--8<-- "docs/snippets/how-to/use-threads/parallel_load.py:example"
```

When the threads only read one model, share it as is:

```python
--8<-- "docs/snippets/how-to/use-threads/shared_read.py:example"
```

## 3. Copy a shared model before changing it

When each thread needs a variant of one base model, give each thread a copy and change only
that copy. `doc.copy()` is a read, so many threads may copy the same base model at once.

```python
--8<-- "docs/snippets/how-to/use-threads/copy_per_thread.py:example"
```

If the threads must change one document together, put every access behind one lock you own,
the reads included: a thread that reads while another writes is as unsafe as two writers.

```python
--8<-- "docs/snippets/how-to/use-threads/lock.py:example"
```

## 4. Fetch weather files before fanning out

`WeatherDownloader.download` writes the archive and the extracted files in place, so two
threads or processes downloading the same station at once can read a truncated file. Download
each station once, then hand the paths to the pool:

```python
--8<-- "docs/snippets/how-to/use-threads/warm_stations.py:example"
```

`simulate_batch` and `async_simulate_batch` need no such care: each job copies its model when it
starts, and the simulation cache commits each entry with an atomic rename. A job that has not
started yet copies whatever its model holds by then, so do not edit a job's model until the
batch returns.

## 5. Run on a free-threaded build for parallel speed

On a regular build of CPython, the global interpreter lock (GIL) lets one thread run Python at a
time, so CPU-bound idfkit work on a pool runs no faster than on one thread. The steps above keep
it correct there; they do not make it faster.

To run threads in parallel, use the free-threaded build of Python 3.14:

```bash
uv python install 3.14t
uv venv --python 3.14t
```

Check that the GIL is really off in the environment your code runs in:

```python
--8<-- "docs/snippets/how-to/use-threads/check_build.py:example"
```

If `GIL enabled` prints `True` on a free-threaded build, an extension module re-enabled it at
import and the interpreter printed a `RuntimeWarning` naming it. idfkit itself never does. Of
its optional extras, only `pandas` before 3.0 does; upgrade to `pandas>=3.0`, or set
`PYTHON_GIL=0` to force the GIL off at your own risk.

For CPU-bound batch work on a regular build, use processes instead. A document pickles cheaply,
because its schema travels by version rather than by content:

```python
--8<-- "docs/snippets/how-to/use-threads/processes.py:example"
```

## Worked examples

### A web service that shares one base model

A web server calls its handlers on a pool of threads, several at once. Load the base model once
at start-up and never change it afterwards; every request works on its own copy.

```python
--8<-- "docs/snippets/how-to/use-threads/web_service.py:example"
```

Two things keep this safe. Nothing writes to `BASE` after start-up, so the copies taken by
concurrent requests are all copies of the same, unchanging model. And each request's changes
land on its own copy, which no other thread can see. If the base model must change while the
server runs, load the new version into a fresh document and swap the global name in one
assignment, rather than editing the shared one in place.

### A parametric campaign on one machine

A parametric study builds variants, simulates them, and reads the results back: three stages
with different concurrency needs.

```python
--8<-- "docs/snippets/how-to/use-threads/campaign.py:example"
```

- **Variants** are built on a thread pool from one shared base, each thread working on its own
  copy. On a regular build this stage gains nothing from threads, but it is safe; on a
  free-threaded build it runs in parallel.
- **Simulations** run through `simulate_batch`, whose threads spend their time waiting on
  EnergyPlus. Raise `max_workers` until the machine's cores are busy, not beyond: each worker
  holds one EnergyPlus process and its working directory. The shared `SimulationCache` skips
  any variant already run, in this process or another.
- **Results** are read by whichever thread will use them. A result opens its SQLite output on
  first access, and that connection belongs to the thread that opened it, so read, query and
  close a result on one thread.

### Campaigns beyond one machine

A campaign of thousands of simulations outgrows one machine's cores long before it outgrows
`simulate_batch`. Move the parallelism up a level: a queue hands each job to a worker process
on some machine, and each worker loads its own model and usually runs one simulation at a time. Nothing
is shared between workers but files, which is exactly the situation idfkit's process-safe
simulation cache is built for.

- [How to run simulations as Celery tasks](../examples/celery-integration.md): a task queue in
  front of a pool of workers.
- [How to run distributed simulations with Scythe](../examples/scythe.md): experiments defined
  as functions and fanned out over a cluster.
- [How to store simulation results in S3](../examples/cloud-simulations.md): a shared result
  store for workers that share no disk.

Inside each worker the rules on this page still hold. A worker that runs several simulations at
once is running `simulate_batch`, and a worker that also builds variants follows step 3.

## Verify

Run the work twice, once on one thread and once on the pool, and compare the outputs: written
files, validation results, or simulation results should be identical. On a free-threaded build,
also compare the wall time; if four threads are no faster than one, check that the GIL is off
(step 5).

## Related

- [Why idfkit locks its caches and not your documents](../explanation/threads-and-documents.md):
  why the rules are what they are, and how far threads scale.
- [How to run batch simulations](../simulation/batch.md): parallel EnergyPlus runs.
- [Caching strategy](../concepts/caching.md): which caches are shared between processes.
