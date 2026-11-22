# Versioned Documents

Document types for each EnergyPlus release, the check that narrows a document to one, and the types
of the release arguments the loaders take. See [Typed for a Release](../concepts/type-safety.md#typed-for-a-release)
for how to use them.

::: idfkit.versioned
    options:
      members: false
      show_root_heading: true
      # The module docstring is the generator's note to maintainers; this page says what it holds.
      show_docstring_description: false

## Release document types

Every supported release has a document type, a range type from it onward and a range type before
it. They are generated, one per release, and differ only in the release they name, so they are
summarised here rather than rendered one by one.

| Name | A document of | Example |
| --- | --- | --- |
| `IDFDocumentV<major>_<minor>` | exactly that release | `IDFDocumentV9_4` |
| `IDFDocumentSince<major>_<minor>` | that release or any later one | `IDFDocumentSince22_1` |
| `IDFDocumentBefore<major>_<minor>` | any release earlier than that one | `IDFDocumentBefore24_1` |

The releases run from 8.9 to 26.2, the ones in [Versions](versions.md). `IDFDocumentV26_2`, the
latest, is [IDFDocument][idfkit.document.IDFDocument] itself. `IDFDocumentSince8_9` covers every
release, and there is no `IDFDocumentBefore8_9`.

For a type checker each `IDFDocumentV<major>_<minor>` is a class carrying that release's object
types and fields; at run time it is a stand-in that [as_version][idfkit.versioned.as_version]
checks against. A range type is the union of the releases it covers.

::: idfkit.versioned.AnyIDFDocument
    options:
      show_root_heading: true

::: idfkit.versioned.as_version
    options:
      show_root_heading: true
      show_source: true

::: idfkit.versioned.DocumentTypeTarget
    options:
      show_root_heading: true

::: idfkit.versioned.ReleaseBound
    options:
      show_root_heading: true

::: idfkit.versioned.ReleaseDocumentT
    options:
      show_root_heading: true
