# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The visual identity of idfkit at `identity-2026.5`: a fifth pinned level,
  `[tool.idfkit.identity]`, the `material` derivation and the host files vendored under
  `docs/identity/`, the palette, stylesheets, mark and favicon read from them, the ownership line
  and the family links in the footer, the host's head tags on every page, and
  `check-identity.yml`, which holds the vendored bytes and the declaration to the tag.
- The README header of the `site` kind: the mark, the roster's sentence, the family links and
  the build and licence badges.
- The documentation site, moved from `idfkit/docs/` with its history intact, together with the
  seven scripts and the workflows that act on it.
- A fourth pinned level, `[tool.idfkit.library]`, naming the exact `idfkit` version the Python
  reference is generated from and the four weather-browser files are copied out of. The other
  three levels came with the site; this one is what lets the site name a library it no longer
  lives inside.
- `scripts/copy_shipped_assets.py`, which takes those four files out of the installed
  distribution at build time. They reached the page by symlink while the site and the library
  shared a repository, and a symlink does not survive a repository boundary.

### Changed

- `docs/stylesheets/extra.css` holds layout rules only; every colour, font and easing comes from
  the vendored derivation.
- The site serves its two typefaces itself from `docs/identity/material/fonts/` and no longer
  loads them from Google Fonts.
- `docs/tape/` is real committed content rather than a symlink to a directory beside the site.
- The mkdocstrings Python handler resolves the library from the installed distribution rather
  than from `src/`.

### Fixed

- The I/O API page gave `strict=False` as the default of `load_idf()` and `load_epjson()`; it is
  `strict=True`.
- The installation page, the common-errors page and the sizing-workflow notebook offered an
  `idfkit[weather]` extra that does not exist, and the installation page left out `async-s3`. They
  now list the extras `pyproject.toml` declares, with `pandas` ahead of its alias `dataframes`.
- The Scythe integration example raised `InvalidFieldError` on an EnergyPlus 24.2 model, the
  version its Docker image runs: it set `Thermal_Resistance` on a `Material`, which has no such
  field, and `Watts_per_Zone_Floor_Area` on `Lights`, a name EnergyPlus replaced in 24.1. It now
  sets `thermal_resistance` on the `Material:NoMass` insulation layer, and raises when the model
  has none rather than leaving every run unchanged. It also sets `watts_per_floor_area` on
  `Lights` together with the `Watts/Area` calculation method, without which EnergyPlus ignores
  the value. The R-value input now starts at 0.001, the smallest `thermal_resistance`
  EnergyPlus accepts.
