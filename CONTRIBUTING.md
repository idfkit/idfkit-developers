# Contributing

## Setting up

```bash
make install
make docs-test
```

You need no checkout of `idfkit` or `idfkit-js`. If the second command needs one, that is a bug
in this repository, and the `portable` job in CI exists to catch it before you do.

## The rules that are not style

### The hooks stay under `docs/`

`docs/hooks/*.py` MUST NOT move to `scripts/`, to a package, or anywhere else. The portable build
copies `docs/` and `mkdocs.yml` and nothing else, so a hook outside `docs/` cannot be resolved at
build time. Moving them looks like tidying and fails the portable job on the day it happens.

For the same reason, no file under `docs/` may compute a path above `docs/`. `make check` measures
the steps a path expression takes against the file's own depth and reports the file, the line, the
steps taken and the steps allowed.

### A failing check is fixed by fixing the page

When a level advances and a page stops building, the page is wrong. It describes an interface that
no longer exists under that name, or a signature that no longer accepts that argument. Fix the
page. Do not relax the check, do not pin the level back, and do not add an exception for the file.

This is the one rule the site cannot bend without becoming untrustworthy: every example runs, and
what it runs against is the version the page names.

### Vendored trees are not edited

`docs/typedoc/` and `docs/snippets/js/` come from a published release of `idfkit-js` and are
compared against it byte for byte. Change them by advancing `[tool.idfkit.docs] level` and running
`uv run python scripts/sync_js_artifacts.py`, never by hand. The pre-commit hooks are excluded from
those trees so that a stray trailing newline cannot make the comparison fail.

`docs/weather/browse/` is not vendored, it is copied out of the installed library at build time and
gitignored. There is nothing to update and nothing to commit.

### The governance reader is duplicated on purpose

`scripts/_governance_source.py` exists here and in `idfkit/scripts/`. Two library gates and two
site renderers read governance artifacts at a pinned tag, and after the move those four callers are
in two repositories. Publishing the ~90 lines as a package would make a release cycle out of a file
that changes twice a year; moving it into `idfkit-conformance` would make a data repository into a
code dependency of both libraries.

So it is duplicated, both copies say so in their header, and
`tests/test_governance_source_matches.py` compares them. A change to one MUST land in the other in
the same feature.

## Writing a page before the release it documents

Sometimes the page comes first. `scripts/build_docs.sh` reads `IDFKIT_LIBRARY_DIR`, and when it is
set the build resolves the library from that checkout instead of from the declared level.

```bash
IDFKIT_LIBRARY_DIR=../idfkit make docs-test
```

The build announces this loudly, in the same words `IDFKIT_GOVERNANCE_DIR` and `IDFKIT_TYPEDOC_JSON`
use, because of what it costs:

**A build under the override is not evidence about the declared level.** It proves the page renders
against a working tree that nobody can install. It does not prove the page is true of
`[tool.idfkit.library] level`, and it never will be until that level advances to a release
containing the interface. CI asserts the variable is unset in every job, so a green check is always
a statement about a released version.

The override is explicit only. It is never a fallback that engages because a lookup failed: a
fallback would make a build that should have stopped succeed quietly, which is the failure mode all
four pinned levels exist to prevent.

## Before you open a pull request

```bash
make check
make docs-test
```

Both run in CI. `make check` also runs the vendored comparison and the governance-reader drift test,
which are the two checks that reach outside this repository.
