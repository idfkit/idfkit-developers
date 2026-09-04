# Two writers, one model

Both libraries write IDF. Hand them the same model and you get two files that
EnergyPlus reads identically and `diff` does not.

{{ parity("write") }}

That is not a defect in either one, and it is not going to be resolved. This
page says what the seven differences are, why they are not being removed, and
what to do instead of diffing.

## The seven differences, measured

Measured on `5ZoneAirCooled.idf` from EnergyPlus 26.1.0, read and written back
by each library with no options set: **359 objects, 4,031 lines against 4,125.**

A measured claim reads differently from an asserted one, so the number is
re-derivable: load the file, write it, count the lines.

| | Python | TypeScript |
| --- | --- | --- |
| Generator header | `!-Generator idfkit v…` and `!-Option SortedOrder` | none |
| Object ordering | sorted by type name, `Version` first | insertion order, `Version` first |
| Indent | two spaces | four spaces |
| Comment overflow | a long value pushes the comment right | the same, from a different padding calculation |
| Float rendering | `%g`, so `30.0` becomes `30` | the schema decides, so a number field keeps `30.0` |
| Comment capitalisation | every word title-cased, `Number Of Timesteps Per Hour` | minor words lowercased, `Number of Timesteps per Hour` |
| Extensible-group comment numbering | first group unsuffixed, then ` 2`, ` 3` | the same scheme, applied at a different point |

The two that surprise people are float rendering and comment capitalisation,
because they touch almost every line of a large file and neither looks like a
choice until you see the other one.

## Neither writer is more correct

Both outputs are valid IDF. Both are read by EnergyPlus without complaint. Both
have been published for long enough that somebody's diff, somebody's test
fixture and somebody's version-controlled model depend on the exact bytes.

So neither default moves. Changing Python's `%g` to match TypeScript would be
just as much of a break as the reverse, and picking a winner would mean picking
whose files churn.

**Byte-identical output across the two languages is not promised, and it is not
coming.** If a workflow depends on it, that workflow needs to change rather than
wait.

## What to do instead of diffing

Pass EnergyPlus the model. It is the thing that reads IDF, it does not care
which library wrote the file, and it is the only opinion that decides whether a
model runs.

When you do need to compare two models, compare them as models: read both files
and compare the parsed documents, which is what the conformance corpus does. It
re-reads each library's own output and compares the resulting documents field by
field, never the text. Two files that differ on all seven of the above compare
equal that way, because all seven are presentation.

## The controls, which do not change any of this

Five controls were closed by [feature 002](conformance.md), so that no control
sits on one writer with no answer on the other. Two of them are still spelled on
one side only: Python's `ordering` has no TypeScript counterpart, because that
writer keeps insertion order and offers no sort, and TypeScript's `versionFirst`
has no Python counterpart. They let you ask for output shaped differently. They
do not make the two writers agree, because none of them touches the seven
defaults above.

```python
--8<-- "docs/snippets/explanation/two_writers_one_model.py:controls"
```

The most aggressive is compressed output: one object per line, no comments, no
blank separators, no header.

```python
--8<-- "docs/snippets/explanation/two_writers_one_model.py:compressed"
```

The TypeScript half of both examples is written and type-checked in
`idfkit-js` at `docs-snippets/explanation/two-writers-one-model/controls.ts`. It
appears here as a tab beside the Python one once `idfkit-js` cuts the docs
release that carries it and `scripts/sync_js_artifacts.py` vendors it into
`docs/snippets/js/`; that directory is vendored wholesale from the pinned
`[tool.idfkit.docs]` level and must match it exactly, so the file cannot be
added here by hand.

Compressed output from the two libraries is still not byte-identical: it removes
comments, indentation and blank lines, and it does not touch float rendering.
What it does guarantee, and what the corpus checks, is that a document written
under any of these controls re-reads to the same document it came from.

## Where this is recorded

The parity record used to carry these seven differences in its `differences`
field, because `write` was a partial capability on both sides. Closing the five
controls made it complete, and the record does not keep a `differences` field on
a capability that is complete: a reader would have no way to tell a difference
that still matters from one that was left behind.

So they live here. If this page goes away, the information exists nowhere.
