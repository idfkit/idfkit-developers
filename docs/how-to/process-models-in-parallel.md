# How to process many models in parallel

*This guide is about the Python library. JavaScript has no shared-memory
threads over ordinary objects, so the question does not arise there.*

You have a folder of IDF files, or one model you want many variants of, and you
want the work done on every core. This guide shows which pool to use and how to
hand it the work without corrupting a model.

{{ parity("parse") }}

## Choose threads or processes

Which pool speeds CPU-bound idfkit work up depends on the interpreter, not on
idfkit:

| Interpreter | Use |
|---|---|
| Free-threaded CPython (`python3.14t`, GIL off) | A thread pool. |
| Regular CPython | A process pool. A thread pool runs no faster than one thread. |

Waiting work is the exception. `simulate_batch`, weather downloads and SQLite
result queries spend their time on a subprocess, a socket or a C library, so
threads speed them up on either interpreter. `simulate_batch` already uses a
thread pool for that reason; see [Run batch simulations](../simulation/batch.md).

Check which interpreter you have:

```bash
python -c "import sys; print(sys._is_gil_enabled())"
```

`False` means the GIL is off and threads run in parallel.

## Give each thread its own document

Load a separate document in each task. Separate documents share nothing but the
read-only schema, so there is nothing to lock:

```python
--8<-- "docs/snippets/how-to/process-models-in-parallel/summarise_with_threads.py:example"
```

Return small results, such as the summary here, rather than the documents, when
you can. On free-threaded Python, parsing is the step that gains most from
extra threads.

## Make variants of one model with a copy per thread

Many threads may read one document at the same time. None may change it while
another thread uses it. To make variants of a shared baseline, have each thread
change its own copy:

```python
--8<-- "docs/snippets/how-to/process-models-in-parallel/copy_per_thread.py:example"
```

`baseline` is only read, by `copy()`, so any number of threads can do this at
once.

## Lock a model that several threads must change

If the threads really must change the same document, put every access to it
behind one lock, reads included:

```python
--8<-- "docs/snippets/how-to/process-models-in-parallel/lock_shared_model.py:example"
```

Without the lock nothing raises. The model ends up inconsistent instead: objects
go missing, references dangle, and the reference graph stops matching the
fields.

## Use processes on regular CPython

Put the same task function in a process pool. Documents pickle cheaply, because
the schema travels by version rather than by content, and each worker loads its
own schema once:

```python
--8<-- "docs/snippets/how-to/process-models-in-parallel/summarise_with_processes.py:example"
```

A process pool pays for starting interpreters and for pickling what crosses
between them. On free-threaded Python, prefer threads when the results are large,
such as whole documents, or when the batch is short.

## Related

- [Threads and free-threaded Python](../explanation/threads-and-free-threading.md):
  what idfkit makes safe to share, and how much each workload gains.
- [How to install idfkit](../getting-started/installation.md#free-threaded-python):
  installing on a free-threaded interpreter.
