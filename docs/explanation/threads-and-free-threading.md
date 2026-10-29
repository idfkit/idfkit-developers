# Threads and free-threaded Python

*This page is about the Python library. JavaScript has no shared-memory threads
over ordinary objects: a worker receives a copy of what it is sent, so none of
what follows arises there.*

The Python library is pure Python and has no compiled extensions, so nothing in
it turns the global interpreter lock (GIL) back on. It is tested on free-threaded CPython 3.14
(`python3.14t`) with the GIL disabled, where Python threads run in parallel. That
raises two questions: what is safe to share between threads, and whether threads
make anything faster.

{{ parity("document-model") }}

## What is safe to share

| Shared between threads | Safe? |
|---|---|
| The schema manager, `get_schema()`, and the schema it returns | Yes. |
| Separate documents, one per thread | Yes. |
| One document that is only read | Yes, while no thread changes it. |
| One document changed by several threads, or by one while others read it | No. |
| `simulate_batch` and `async_simulate_batch` | Yes. |

The process-wide caches are safe from any number of threads: schemas,
Schedule:File data, and the compiled validation rules. A schema version that
many threads request at once is read from disk once, and every thread gets the
same instance. Before that was guaranteed, sixteen threads starting together
each loaded their own copy, even with the GIL. Each copy was correct, but they
were sixteen copies, and only one of them could be pickled by version.

## Why one document is not made thread-safe

A document changes in compound steps. Adding a surface puts it in its type's
collection, then registers every name it references in the reference graph.
Renaming a zone rewrites every field that names it. Each step is a sequence of
writes, and another thread can see the model halfway through one.

Making each step atomic would mean taking a lock on every field read and write.
Field access is the hottest path in the library, and nearly every program that
uses idfkit never shares a document between threads. That cost would fall on
all of them to protect a pattern few use, and that is easy to avoid with a copy
or a lock of your own.

So the rule is the one most Python collections follow: share for reading, not
for writing. The failure is worth knowing in advance, because it is silent. In
a stress test with the GIL off, several threads adding, renaming and removing
zones in one document raised nothing. The model was simply wrong afterwards:
zones lost, surfaces pointing at names that no longer existed, and a reference
graph that disagreed with the fields. On a GIL build the same test happened to
come out right, which does not make the pattern safe. The GIL protects single
bytecodes, not a rename.

## What threads buy

On regular CPython, nothing for CPU-bound work: one thread holds the GIL at a
time. Free-threaded CPython changes that, unevenly. These are 16 independent
jobs on 4 CPUs, against one thread on regular CPython 3.14:

| Workload | 1 thread, 3.14t | 4 threads, 3.14t |
|---|---|---|
| `load_idf` | 0.86x | 2.6x |
| `write_idf` | 0.84x | 1.6x |
| ESO parse | 1.1x | 1.5x |
| Geometry | 0.72x | 1.4x |
| Schedule evaluation | 0.77x | 1.4x |
| `validate_document` | 0.72x | 1.0x |

Two costs show up there. The free-threaded interpreter is 15 to 40 percent
slower on a single thread for everything but ESO parsing, so it pays only once
two or more threads are busy. And most work scales well short of linearly,
although four processes reach 3.6 to 3.9 times on the same machine. The
difference is contention. Every thread reads the same schema-derived tables,
and on 3.14 a read of a shared object updates its reference count, so all four
threads write to the same memory. Parsing touches those tables least and scales
best. Validation does almost nothing else and barely scales.

That is why the library offers no parallel API of its own. A thread-pool loader
would help on one interpreter and do nothing, or slightly worse, on the other. A process pool
already scales on regular CPython, and documents pickle cheaply because the
schema travels by version rather than by content.
[How to process many models in parallel](../how-to/process-models-in-parallel.md)
shows both pools.

## Optional extras

The core has no dependencies, but the extras do. Of them, only pandas before 3.0
turns the GIL back on: its compiled modules do not declare that they are safe
without it, so the interpreter re-enables the GIL when pandas is imported and
prints a warning. pandas 3, NumPy, matplotlib, plotly, boto3, aiobotocore, tqdm
and openpyxl leave it off.
