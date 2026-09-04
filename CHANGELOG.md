# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

- `docs/tape/` is real committed content rather than a symlink to a directory beside the site.
- The mkdocstrings Python handler resolves the library from the installed distribution rather
  than from `src/`.
