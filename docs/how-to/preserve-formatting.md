# How to save a file without reformatting it

Both libraries can read a model and write it back exactly as it was, and then
write it back with one object changed and only that object changed. This is what
a save button needs: an editor that reformats four thousand lines to record one
edit produces a diff nobody can review, and a version control history nobody can
read.

This guide reads a file keeping its source, writes it back unchanged, makes one
edit, and says what happens when you ask for preservation and reformatting at
the same time. It ends with the object notation, which preserves on different
terms, and that difference is the one thing on this page you could otherwise get
wrong.

{{ parity("lossless-round-trip") }}

## Read the file keeping its source

Preservation is off by default. A reader who does not ask for it pays neither
the time nor the memory, and gets exactly the document they got before.

=== "Python"

    ```python
    --8<-- "docs/snippets/how-to/preserve-formatting/read_keeping_the_source.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/how-to/preserve-formatting/read_keeping_the_source.ts:example"
    ```

## Write it back unchanged

A document read this way and written with nothing changed produces the text it
was read from, byte for byte.

=== "Python"

    ```python
    --8<-- "docs/snippets/how-to/preserve-formatting/write_it_back_unchanged.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/how-to/preserve-formatting/write_it_back_unchanged.ts:example"
    ```

That includes everything a formatter would otherwise decide for you: the
comments, the blank lines that group four hundred surfaces into rooms, the
indentation as the author left it, the line endings whatever they are, and
whether the file ends in a newline.

## Change one field, and change one object

An edit reformats the object it touched. Everything else, and everything between
the objects, comes back from the characters it was read from.

=== "Python"

    ```python
    --8<-- "docs/snippets/how-to/preserve-formatting/one_edit_one_object.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/how-to/preserve-formatting/one_edit_one_object.ts:example"
    ```

Renaming an object counts as changing every object that pointed at it, because
a rename rewrites those references. All of them are reformatted, and none of
them is left naming something that no longer exists.

Writing a field the value it already holds is not a change. The object is
reproduced from its own characters, so a `3.000` stays `3.000` rather than
becoming `3`.

## Ask whether a write will preserve

A document remembers whether it was read with preservation. That is how an
editor decides whether to warn before saving.

=== "Python"

    ```python
    --8<-- "docs/snippets/how-to/preserve-formatting/ask_whether_a_write_will_preserve.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/how-to/preserve-formatting/ask_whether_a_write_will_preserve.ts:example"
    ```

## Preserving and reformatting are refused together

Reproducing the original text and laying it out differently are contradictory
requests. One of them has to be dropped, and neither should be dropped in
silence, so asking for both raises.

=== "Python"

    ```python
    --8<-- "docs/snippets/how-to/preserve-formatting/preserving_and_reformatting_are_refused.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/how-to/preserve-formatting/preserving_and_reformatting_are_refused.ts:example"
    ```

The refused set is the same in both languages: the controls that change how an
object is laid out. Asking for a different output *form* is not refused, because
a form is a different artifact that the original text was never going to
express, so you get the form and preservation does not apply.

| Ask for | Together with | You get |
| --- | --- | --- |
| Preservation | Indent, comment column, ordering, version placement | An error naming both halves |
| Preservation | Compressed output, or output without field comments | That form, and no preservation |
| Preservation | A document read without it | Ordinary formatted output, and no error |
| A layout control | Nothing about preservation | The control, applied |

The third row is worth reading twice. Asking to preserve a document that has
nothing to preserve is not an error: nothing was promised, so you get ordinary
output.

## The object notation preserves on all-or-nothing terms

**This is the one thing on this page that differs between the two formats, and
it differs the same way in both languages.**

The text format preserves *per object*: change one, and one is reformatted. The
object notation cannot. It has no statements to anchor an object's own
characters to, so there is no way to reproduce one object while reformatting
another. The retained text is reproduced only while nothing has been touched,
nothing has been added and nothing has been removed, and any change at all falls
the whole document back to the ordinary writer.

=== "Python"

    ```python
    --8<-- "docs/snippets/how-to/preserve-formatting/the_object_notation_is_all_or_nothing.py:example"
    ```

=== "TypeScript"

    ```ts
    --8<-- "docs/snippets/js/how-to/preserve-formatting/the_object_notation_is_all_or_nothing.ts:example"
    ```

Removal counts, and it is the case a naive implementation gets wrong: every
object still in the document is untouched after you remove one, so asking only
the survivors says nothing changed and reproduces the original text with the
removed object still in it. Both libraries compare the object count as it was at
read time, which is what makes a removal visible at all.

## What "the same file" means here

Reproduction is defined against **the text the read was given**, not against a
file's bytes. If you decode a file yourself and hand over a string, you get that
string back. If you read through the library, you get back what the library's
own decoding produced, and decoding is where two known defects live: the
TypeScript reader refuses a file carrying a UTF-8 byte-order mark, and Python's
`save_idf` opens its destination without `newline=""`, so the standard library
translates line endings on the way out.

Neither is closed by preservation, and neither is visible to it. An editor that
needs byte identity end to end should decode and encode the file itself.
