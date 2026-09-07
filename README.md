# idfkit-developers

[![Python release](https://img.shields.io/github/v/release/idfkit/idfkit?label=python%20release)](https://github.com/idfkit/idfkit/releases)
[![TypeScript release](https://img.shields.io/github/v/release/idfkit/idfkit-js?filter=v*&label=typescript%20release)](https://github.com/idfkit/idfkit-js/releases)
[![Docs build](https://img.shields.io/github/actions/workflow/status/idfkit/idfkit-developers/docs.yml?branch=main&label=docs)](https://github.com/idfkit/idfkit-developers/actions/workflows/docs.yml?query=branch%3Amain)
[![License](https://img.shields.io/github/license/idfkit/idfkit-developers)](https://github.com/idfkit/idfkit-developers/blob/main/LICENSE)

The source of <https://developers.idfkit.com>, the documentation site for idfkit in Python and
in JavaScript.

The site is not documentation *for* a library. It is documentation for a capability that two
libraries implement, so it lives in a repository that belongs to neither of them. A page about
loading a model is one page with two idioms on it, and the maintainers of both languages hold
the same standing over it.

## What is here

```text
docs/       the site: ~580 authored pages, the mkdocs hooks, the templates and overrides
mkdocs.yml  the site's configuration
scripts/    the seven that act on the site, plus the duplicated governance reader
tests/      covers scripts/
```

There is no `src/`. This repository publishes a site, not a package.

## Getting started

```bash
make install     # create the virtual environment and install the pre-commit hooks
make docs        # build and serve the site at http://127.0.0.1:8000
make docs-test   # build once, with --strict, exactly as CI does
make check       # the quality gate: page kinds, capabilities, vendored artifacts, lint, types
```

`make docs-test` needs nothing beside this repository. That is the point, and the `portable`
job in `.github/workflows/docs.yml` proves it on every run by building from a scratch directory
outside the checkout.

## The four pinned levels

Everything the site renders that it did not write itself is pinned to an immutable identifier in
`pyproject.toml`, and the build refuses to start when it cannot state all four.

| Level | Points at | Gives the site |
| ----- | --------- | -------------- |
| `library` | an exact `idfkit` version on PyPI | the Python reference, and the four weather-browser files |
| `docs` | a `docs-YYYY.N` tag in `idfkit-js` | the TypeScript reference, and every TypeScript example |
| `governance` | a `governance-YYYY.N` tag in `idfkit-conformance` | the parity notices and the naming map |
| `conformance` | a `conformance-YYYY.N` tag in `idfkit-conformance` | the corpus level the pages describe |

A reader can see all four on the site. That is not decoration: a page that says how something
works is a claim about a version, and a claim about a version that does not name it is not
checkable.

Levels advance by pull request, opened automatically when either library releases. The site's own
checks then decide whether the pages survive the new version. A red result means a page gets
fixed, never that a check gets relaxed.

## Where things are not

Some things that look like they belong here do not, because an artifact follows its subject
rather than its current neighbours.

| Lives in `idfkit` | Why |
| ----------------- | --- |
| `redirects/`, `build_redirect_site.py` | they act on the retired host `py.idfkit.com`, which is the library's to serve |
| `old-sitemaps/` | evidence about retired hosts, kept beside the redirects that answer for them |
| `check_naming_register.py`, `check_parity_ledger.py` | they act on the library's own public surface |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: the hooks under `docs/hooks/` must
stay under `docs/`, and a failing documentation check is fixed by fixing the page.

## Licence

MIT. See [LICENSE](LICENSE).
