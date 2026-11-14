# Why idfkit locks its caches and not your documents

*This page is about the Python library. The TypeScript library has no shared-memory threads.*

idfkit is safe to use from many threads in one sense and not in another. The schema and every
cache the library keeps for the whole process can be used from any number of threads at once. A
document cannot be changed by two of them. This page explains where that line falls and why it
falls there, and what threads buy on a regular and on a free-threaded build of Python.

To do the work rather than understand it, see
[How to use idfkit from several threads](../how-to/use-threads.md).

## What the threads actually share

Two threads that each load their own model share almost nothing. Each document has its own
objects, its own name indexes and its own reference graph. The one thing they share is the
schema: one `EpJSONSchema` per EnergyPlus version, loaded once per process and handed to every
document of that version. Around it sit a few process-wide caches, such as compiled validation
rules and parsed `Schedule:File` columns, which save work across documents.

That shared state is where a thread-safety bug costs most, because it is the only state a user
never asked to share. So it is the state the library protects.

## Why the schema is loaded under a lock

The schema is about 4 MB of JSON, and loading it is the slowest step in opening a model. When
sixteen threads ask for a version nobody has loaded yet, an unguarded loader reads the file
sixteen times and builds sixteen schemas. The waste is the lesser problem. The library relies on
there being one schema object per version: a document pickles its schema as a version number
rather than as 4 MB of content, and that works only for the schema the manager is known to have
handed out. Fifteen of the sixteen would be strangers, each pickled whole.

So each version has its own lock. The first thread to miss loads the file while the others wait,
and every thread leaves with the same object. Two different versions still load in parallel,
because they never wait on each other's lock.

The lazily built parts of a schema, such as the per-type parsing tables, take a cheaper route.
They are built whole and then published in one step. Two threads that race to build the same
table both do the work, one result wins, and neither thread can see half of one. Duplicated work
on a cold cache is a fair price for not taking a lock on every lookup.

## Why documents are not locked

A lock on every document would cost every program that never starts a thread, on every field
read and write. More decisively, it would not deliver what it seems to promise.

A model's consistency spans several structures at once. Adding a surface touches its type's
collection, the name index and the reference graph. Renaming a zone rewrites every reference to
it. A lock taken inside each method would make each of those calls atomic, but user code is
rarely one call. A thread that checks whether a zone exists and then adds a surface to it is
making two calls, and another thread can remove the zone in between. Only the code that knows
which calls belong together can hold a lock around them. A library-level lock would add the
cost and still leave that job to the user, while suggesting it had been done.

The alternative the library offers instead is copying. `doc.copy()` is a read, so many threads
may copy one base model at once, and a copy shares nothing that can change. For parametric work,
where each thread builds a variant of one model, that is also the natural shape of the job.

### Why the failure is not reliable

Python's dictionaries and sets protect their own internals, so two threads changing one document
do not crash the interpreter. They break the model, and they break it differently each time.
Sometimes a reader iterating a collection sees it change size and raises `RuntimeError`.
Sometimes the reference graph meets a name that another thread already removed and raises
`KeyError`. Most often nothing raises: an object goes missing, or a reference points at nothing.
A failure that appears only sometimes is the reason the rule is stated as a rule rather than
left to the exceptions.

Some libraries detect this instead, recording which thread is changing a document and raising
when a second one starts. That turns silent damage into an error at a cost of a few nanoseconds
per change. idfkit does not do it today. It would catch two writers, but not a reader racing a
writer, which is the more common mistake.

## What threads buy

On a regular build of CPython, the global interpreter lock (GIL) lets one thread execute Python
at a time. Threads still help when the waiting happens outside Python: `simulate_batch` runs
EnergyPlus as a subprocess, and a downloader waits on the network. For idfkit's own work, which
is all Python, a thread pool interleaves the jobs rather than running them together, and it
usually runs slightly slower than one thread.

Python 3.13 introduced a free-threaded build, written `python3.14t` for 3.14, that runs without
the GIL. There, threads do run in parallel. Measured with `benchmarks/bench_free_threading.py`
in the library repository, on 4 CPUs with 16 independent jobs, four threads parsed IDF files
about 2.6 times faster than one thread on the regular build. Workloads that copied a model per
job gained less, between 1.0 and 1.6 times, largely because copying a document is itself one of
the operations that scale worst. These are single runs, and the spread between runs is wide;
treat them as a direction, not a specification.

Two things limit the gain. A free-threaded interpreter is somewhat slower on a single thread, so
it pays only when two or more threads are busy. And every thread reads the same schema tables,
whose reference counts the threads now update concurrently. Parsing, which spends most of its
time on text the thread owns, scales best.

For CPU-bound work on a regular build, processes remain the answer. A document pickles cheaply
because its schema travels as a version number, and the worker that receives it finds that
version in its own manager.

## Locks and fork

A child process created with `fork` inherits every lock in the state the parent held it, but
not the thread that held it. A child forked while a schema was loading would therefore find that
version's lock taken by nobody and wait for it forever. Every process-wide lock in idfkit is
replaced with a fresh one in a forked child, the same way the standard library's `logging`
re-initialises its handler locks. Since Python 3.14, `multiprocessing` on Linux starts workers
with `forkserver` rather than `fork` by default, which avoids the question altogether.

## See also

- [How to use idfkit from several threads](../how-to/use-threads.md)
- [Content-addressed schemas](content-addressed-schemas.md): how the TypeScript library shares
  schema data.
- [Caching strategy](../concepts/caching.md)
