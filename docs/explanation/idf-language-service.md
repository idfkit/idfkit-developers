---
title: A language service for IDF text
description: The five answers an editor needs about IDF text, why they are computed in one language only, and what that costs a reader in the other.
---

# A language service for IDF text

*This page is about the JavaScript library. The Python library has no
counterpart and will not acquire one; the reason is below.*

An editor holding a model file asks questions a reader of that file never asks.
Which statement is the cursor in. What may be written at this position. What
does this field mean. Where is this name declared. Which characters is this
finding about.

Reading the file answers none of them. A document is a set of objects with
values, and by the time it exists the text has been forgotten: nothing in it
records that the zone name was written at offset 4812, so nothing built on it
can underline the value that is wrong. These are questions about the text, and
they are answered from the text.

{{ parity("idf-language-service") }}

## The syntax layer and the five answers

Two pieces, split by who pays for them.

The **syntax layer** ships in the package everyone installs. `scanIdf` reads
the text once and records where every statement, every field and every comment
was written, as half-open offsets into the string; `classify` walks that layer
and yields one token per meaningful span, filling the gaps between them so that
every character of the file is covered exactly once. It is in the core package
because reading already scans the text and a source-preserving writer will read
the layer too.

The **five answers** ship as `@idfkit/language`, an opt-in package installed by
name and reached as `idfkit/language`. Installing the library under its shared
name places none of it on disk, deliberately: everything in the core package is
carried by everyone who reads a model, and most of them are not building an
editor.

Every answer is a function from text and an offset to a value:

```ts
--8<-- "docs/snippets/js/explanation/idf-language-service/the_five_answers.ts:cursor"
```

What may be written here, with the state that says why there is nothing:

```ts
--8<-- "docs/snippets/js/explanation/idf-language-service/the_five_answers.ts:completions"
```

An empty list and a missing schema are different results rather than the same
empty array. An editor that renders "no suggestions" identically for a field
that accepts free text and for a schema that failed to load teaches the reader
that the tool is broken in the first case and is silently wrong in the second.

What this means, and where the name under the cursor is declared:

```ts
--8<-- "docs/snippets/js/explanation/idf-language-service/the_five_answers.ts:meaning"
```

And the findings both the reader and the validator already produce, each with
the characters it concerns:

```ts
--8<-- "docs/snippets/js/explanation/idf-language-service/the_five_answers.ts:findings"
```

Neither the reader nor the validator changed to make that true. They produce
exactly what they produced before, and the regions are correlated onto them
afterwards, which is why the conformance corpus still compares the same
findings it always did.

## Why an answer is cheap enough for a keystroke

The grammar allows it. IDF is a flat sequence of statements terminated by a
semicolon, with no nesting, no string literals and no escapes, and a comment
runs from an exclamation mark to the end of its line. So the statement
containing an offset is found by scanning backwards to the nearest semicolon
that is not inside a comment, at a cost proportional to the statement rather
than to the file.

That is what removes the machinery an editor normally needs. There is no
incremental parser, no cache, and no document to keep in step with the buffer,
because a cursor answer never builds one. The answers are pure functions of
text and an offset, which is also why the same code runs in a browser worker,
in a Node process, and behind an editor server without a conditional import.

## What it is not

**Not a protocol.** Nothing in the service imports, depends on, or names a type
from any editor protocol library, and nothing in it ever will. A consumer
translates, and the translation is small: see below.

**Not a second opinion about the schema.** Offers are the schema's own list for
that field. An explanation is the schema's own prose and the same field facts
the introspection API returns. Reference candidates come from the document the
caller already holds. The service adds a position and a cursor, and nothing
else.

**Not stateful.** There is no service object to construct, because a service
object is where state would accumulate. Nothing here returns a promise, reads a
file, opens a socket, or consults a clock.

## Why the Python library has none, permanently

The answers are byte-offset arithmetic over this grammar, and a second
implementation of that arithmetic is the drift surface the conformance corpus
is least able to police. The corpus compares a finding on its code, its line
and its type name, and never on a column. Two implementations could disagree
about where a value starts for a long time with every gate green, and the first
report would come from a reader whose underline was in the wrong place.

That is a different kind of boundary from the one on
[browser simulation](browser-simulation.md), where a browser cannot start a
subprocess and the languages are separated by what their runtimes can do. Here
both languages could compute these answers. The decision is that only one of
them should, so that there is one answer to compare against rather than two to
reconcile.

The parity ledger records the absence as `never`, and `never` is terminal:
moving a capability out of it takes a constitutional amendment rather than an
edit to the ledger. A `not-yet` would have promised a port nobody intends, and
the gate would have demanded a tracked issue for work that is not going to be
done.

## One implementation, two servers

The editor extension serves both file kinds without a port. Its existing
server, written in Python, continues to serve Python source. A second server,
written in JavaScript, serves IDF text and wraps this capability. The extension
launches both, and a reader editing a model and a reader editing a script each
get a server that speaks their file.

So the thing a Python user usually wants from this capability, an editor that
understands the IDF file open in front of them, is not what the absence takes
away. What the absence takes away is calling these answers from Python code.

## What it costs a reader

These answers require a JavaScript runtime. `pip install idfkit` alone does not
provide them, and no future version of it will.

Concretely, what is absent in Python is the region on a finding, the four
cursor answers, and the classification of the text into tokens. What is not
absent is the finding itself: reading and validating report what they have
always reported, with the line number the corpus compares, in both languages.

## What a consumer still writes

Translation, debouncing, and rendering. No grammar, no schema tables, and no
position arithmetic.

That claim is worth more as a file than as a sentence, so the whole of a
language server's translation layer is one worked example. Its conversion from
the service's offsets to the protocol's positions is three lines:

```ts
--8<-- "docs/snippets/js/explanation/idf-language-service/translating_to_a_protocol.ts:range"
```

and the rest is lookup tables mapping the service's words onto the protocol's
numbers:

```ts
--8<-- "docs/snippets/js/explanation/idf-language-service/translating_to_a_protocol.ts:tables"
```

A completion is then the offer, verbatim, in the protocol's envelope:

```ts
--8<-- "docs/snippets/js/explanation/idf-language-service/translating_to_a_protocol.ts:completion"
```

`replaces` comes from the service rather than from this file, and that is not
politeness. An editor's own word rules break on this format in both directions:
type names contain colons, so `BuildingSurface:Detailed` is two words to most
of them, and values contain spaces, so `Office Zone 1` is three. A consumer
working the span out itself would be wrong on most real completions.

Diagnostics, hovers and go-to-definition are the same shape, and highlighting
is the case that shows what the boundary is for:

```ts
--8<-- "docs/snippets/js/explanation/idf-language-service/translating_to_a_protocol.ts:highlight"
```

Nothing there looks for a newline. A field value in this format may be written
across two lines, and no token encoding in use can express a span that crosses
one, so `classify` splits those regions itself and the consumer never learns
that the problem exists. Regions reported for a finding or a declaration stay
whole, because those identify a thing rather than something to draw.

The file contains no line or column computation of its own, which is the
property the example exists to demonstrate. If a consumer finds itself counting
commas, the service has a gap, and the gap is the service's to close.

## See also

- [Capability parity](parity.md), where this entry and its reason are recorded
- [The hazards of a positional format](positional-format-hazards.md), the same
  grammar seen from a reader's side rather than an editor's
- [A synchronous core with async edges](sync-core-async-edge.md), which is why
  every answer here is a function of text
- [Browser simulation](browser-simulation.md), the other capability that
  belongs to one language permanently
