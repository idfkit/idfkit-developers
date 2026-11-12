<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/idfkit/idfkit-brand/identity-2026.5/marks/mark-on-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/idfkit/idfkit-brand/identity-2026.5/marks/mark-on-light.svg">
    <img alt="idfkit" width="72" src="https://raw.githubusercontent.com/idfkit/idfkit-brand/identity-2026.5/marks/tile.png">
  </picture>
</p>

# idfkit-developers

The unified idfkit documentation site, for Python and JavaScript alike.

[idfkit](https://idfkit.com) · [Developers](https://developers.idfkit.com) · [EnergyPlus docs](https://docs.idfkit.com) · [Envelop](https://app.idfkit.com) · [MCP](https://mcp.idfkit.com) · [Shoebox](https://shoebox.idfkit.com) · [GitHub](https://github.com/idfkit)

[![Docs build](https://img.shields.io/github/actions/workflow/status/idfkit/idfkit-developers/docs.yml?branch=main&label=docs)](https://github.com/idfkit/idfkit-developers/actions/workflows/docs.yml?query=branch%3Amain) [![License](https://img.shields.io/github/license/idfkit/idfkit-developers)](https://github.com/idfkit/idfkit-developers/blob/main/LICENSE)

The source of <https://developers.idfkit.com>, the documentation site for idfkit in Python and
in JavaScript.

The site is not documentation *for* a library. It is documentation for a capability that two
libraries implement, so it lives in a repository that belongs to neither of them. A page about
loading a model is one page with two idioms on it, and the maintainers of both languages hold
the same standing over it.

## What is here

```text
docs/       the site: 114 pages (111 Markdown, 3 notebooks), the mkdocs hooks, the templates and overrides
mkdocs.yml  the site's configuration
scripts/    twelve that build, check, render and release the site, plus the duplicated governance reader
tests/      covers scripts/ and the parity and pinned-level hooks under docs/hooks/
```

There is no `src/`. This repository publishes a site, not a package.

## Getting started

```bash
make install     # create the virtual environment and install the pre-commit hooks
make docs        # copy the weather-browser files, then build and serve the site at http://127.0.0.1:8000
make docs-test   # build once, with --strict, exactly as CI does
make check       # the quality gate, listed below
```

`make check` runs the page-kind and capability-declaration checks, the engine-asset check (only
when a built `site/` exists), the vendored TypeScript artifacts against the `docs` level, the
duplicated governance reader against idfkit's, the parity, naming and consumer pages against the
`governance` level, lock-file consistency, pre-commit on all files, and pyright.

A build needs an `idfkit-conformance` checkout besides this repository. Every page that carries a
`{{ parity("id") }}` token is rendered from `governance/parity.toml`, read with `git show` at the
pinned `governance` tag, and `docs/hooks/parity_ledger.py` finds the checkout through
`IDFKIT_CONFORMANCE_DIR` or as a sibling directory named `idfkit-conformance`. The `portable` job
in `.github/workflows/docs.yml` builds from a scratch directory outside the checkout, with only
that conformance checkout and the toolchain exported from `uv.lock` beside it, which proves the
documentation tree needs nothing else from this repository.

## The five pinned levels

Everything the site renders that it did not write itself is pinned to an immutable identifier in
`pyproject.toml`, and the build refuses to start when it cannot state all five.

| Level | Points at | Gives the site |
| ----- | --------- | -------------- |
| `library` | an exact `idfkit` version on PyPI | the Python reference, and the four weather-browser files |
| `docs` | a `docs-YYYY.N` tag in `idfkit-js` | the TypeScript reference, and every TypeScript example |
| `governance` | a `governance-YYYY.N` tag in `idfkit-conformance` | the parity notices, the parity page, the naming map and the consumer page |
| `conformance` | a `conformance-YYYY.N` tag in `idfkit-conformance` | the corpus level the pages describe |
| `identity` | an `identity-YYYY.N` tag in `idfkit-brand` | the colours, type and mark of every page, vendored under `docs/identity/` |

A reader can see all five on the site. That is not decoration: a page that says how something
works is a claim about a version, and a claim about a version that does not name it is not
checkable.

Levels advance by pull request. Two are opened automatically when a library releases:
`bump-idfkit.yml` advances `library` and `bump-docs-level.yml` advances `docs`. The `governance`,
`conformance` and `identity` levels are advanced by a maintainer. The site's own checks then decide whether the pages survive the new version. A red result means a page gets
fixed, never that a check gets relaxed.

The two libraries the site documents release on their own schedules:

[![Python release](https://img.shields.io/github/v/release/idfkit/idfkit?label=python%20release)](https://github.com/idfkit/idfkit/releases)
[![TypeScript release](https://img.shields.io/github/v/release/idfkit/idfkit-js?filter=v*&label=typescript%20release)](https://github.com/idfkit/idfkit-js/releases)

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
