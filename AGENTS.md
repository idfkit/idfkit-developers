# AGENTS.md

Instructions for AI agents and CI environments working with this repository.

## Quick Start

```bash
uv sync
make check && make docs-test
```

## Project Summary

**idfkit-developers** is the source of <https://developers.idfkit.com>, the documentation site for
idfkit in Python and in JavaScript. It contains a site and the tooling that builds and checks it.
It contains no library.

The site documents a capability that two libraries implement, which is why it lives in a repository
belonging to neither. A page about loading a model is one page with two idioms on it.

## Repository Layout

| Path | Purpose |
|---|---|
| `docs/` | the site: authored pages, hooks, templates, overrides |
| `docs/hooks/` | mkdocs hooks. **Must stay under `docs/`** — see Rules |
| `docs/typedoc/`, `docs/snippets/js/` | vendored from `idfkit-js` at the pinned `docs` level; never edited by hand |
| `docs/weather/browse/` | copied from the installed library at build time; gitignored |
| `mkdocs.yml` | site configuration |
| `scripts/` | the seven scripts that act on the site, plus the duplicated governance reader |
| `tests/` | covers `scripts/` |

There is no `src/`. Do not create one.

## Rules an agent will otherwise break

1. **Never move `docs/hooks/*.py` out of `docs/`.** It looks like scaffold conformance. The
   portable build copies `docs/` and `mkdocs.yml` and nothing else, so a hook in `scripts/` or in a
   package is unreachable at build time and the `portable` job fails immediately.
2. **Never make a file under `docs/` compute a path above `docs/`.** `make check` measures the
   steps a path expression takes against the file's own depth.
3. **Never edit the vendored trees.** Advance `[tool.idfkit.docs] level` and run
   `scripts/sync_js_artifacts.py`. A hand edit fails the byte comparison.
4. **Never fix a failing documentation check by relaxing the check.** When a level advances and a
   page stops building, the page is describing an interface that changed. Fix the page.
5. **Never edit one copy of `scripts/_governance_source.py` alone.** The other copy is in
   `idfkit/scripts/` and `tests/test_governance_source_matches.py` compares them.
6. **Never commit anything under `docs/weather/browse/`.** It is generated, and a committed copy
   is a snapshot that drifts silently: it does not fail a build, it shows a reader a weather
   browser the library no longer has.

## The four pinned levels

Declared in `pyproject.toml` under `[tool.idfkit.*]`. The build refuses to start when it cannot
state all four.

| Level | Subject | Read by |
|---|---|---|
| `library` | exact `idfkit` version on PyPI | mkdocstrings, `copy_shipped_assets.py` |
| `docs` | `docs-YYYY.N` tag in `idfkit-js` | `sync_js_artifacts.py`, `typedoc_shim.py` |
| `governance` | `governance-YYYY.N` tag in `idfkit-conformance` | `parity_macro.py`, `render_parity_page.py`, `render_naming_map.py` |
| `conformance` | `conformance-YYYY.N` tag in `idfkit-conformance` | stated on the site |

## Commands

| Command | What it does |
|---|---|
| `make install` | virtual environment plus pre-commit hooks |
| `make docs` | build and serve at <http://127.0.0.1:8000> |
| `make docs-test` | one strict build, exactly as CI does |
| `make check` | page kinds, capabilities, engine assets, vendored trees, governance reader, lint, types |
| `make test` | pytest over `tests/` |

## Building against an unreleased library

`IDFKIT_LIBRARY_DIR=../idfkit make docs-test` resolves the library from a local checkout. The build
announces it, and **such a build is not evidence about the declared level**. CI asserts the variable
is unset in every job.
