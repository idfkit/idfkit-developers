#!/usr/bin/env python3
"""List a newly adopted EnergyPlus release on the two pages that enumerate every release.

Two places in this site enumerate the supported releases one by one, so an adoption adds an entry
to each and rewrites none:

1.  The table of releases in `docs/reference/versions.md`. The release takes the first row whose
    right-hand pair of cells is empty, or a new row when none is.
2.  The printed output of the cell under "Available schema versions" in
    `docs/getting-started/core-tutorial.ipynb`. The release's tuple is appended to the list.

The command refuses unless the installed `idfkit` lists the release, because both places state what
the pinned library supports. It is idempotent: a release that is already listed changes nothing.

Exit codes: 0 both places list the release, 1 the release cannot be listed, 2 the arguments are wrong.

Usage::

    python scripts/adopt_release.py 26.2.0
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSIONS_PAGE = ROOT / "docs" / "reference" / "versions.md"
TUTORIAL = ROOT / "docs" / "getting-started" / "core-tutorial.ipynb"

_TABLE_HEADER = "| EnergyPlus | Schema key | EnergyPlus | Schema key |"
_OPEN_ROW = re.compile(r"^(?P<left>\|[^|\n]*\|[^|\n]*\|) {12}\| {12}\|$", re.MULTILINE)
_LISTING = re.compile(r"(?P<head>Available schema versions: \[)(?P<items>[^\]\n]*)(?P<tail>\])")


class CannotList(ValueError):
    """The release cannot be listed, with the reason."""


@dataclass(frozen=True, slots=True)
class Release:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, text: str) -> Release:
        found = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", text)
        if found is None:
            raise CannotList(f"{text!r} is not a release written as X.Y.Z")
        return cls(int(found[1]), int(found[2]), int(found[3]))

    def full(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def line(self) -> str:
        return f"{self.major}.{self.minor}"

    def as_tuple(self) -> str:
        return f"({self.major}, {self.minor}, {self.patch})"

    def cells(self) -> str:
        """The pair of table cells for this release, padded as the table's other rows are."""
        return f" {self.line():<10} | {f'`{self.full()}`':<10} |"


@dataclass(frozen=True, slots=True)
class Change:
    path: Path
    text: str
    changed: bool


def with_table_row(text: str, release: Release) -> str:
    """The versions page with the release in its table of releases."""
    start = text.find(_TABLE_HEADER)
    if start == -1:
        raise CannotList("the table of releases was not found in docs/reference/versions.md")
    end = text.find("\n\n", start)
    end = len(text) if end == -1 else end
    table = text[start:end]
    if f"`{release.full()}`" in table:
        return text
    opened = _OPEN_ROW.search(table)
    if opened is not None:
        table = table[: opened.start()] + opened["left"] + release.cells() + table[opened.end() :]
    else:
        table += f"\n| {'':<10} | {'':<10} |" + release.cells()
    return text[:start] + table + text[end:]


def with_listed_tuple(text: str, release: Release) -> str:
    """The tutorial notebook with the release in the printed list of schema versions."""
    found = _LISTING.search(text)
    if found is None:
        raise CannotList("the printed list of schema versions was not found in the core tutorial")
    if release.as_tuple() in found["items"]:
        return text
    return text[: found.end("items")] + f", {release.as_tuple()}" + text[found.end("items") :]


def require_listed(release: Release) -> None:
    """Refuse a release the installed library does not list."""
    from idfkit.versions import ENERGYPLUS_VERSIONS

    if (release.major, release.minor, release.patch) not in ENERGYPLUS_VERSIONS:
        raise CannotList(
            f"the installed idfkit does not list {release.full()}, so the site cannot state that it is supported"
        )


def changes(release: Release) -> tuple[Change, ...]:
    page = VERSIONS_PAGE.read_text(encoding="utf-8")
    notebook = TUTORIAL.read_text(encoding="utf-8")
    listed_page, listed_notebook = with_table_row(page, release), with_listed_tuple(notebook, release)
    return (
        Change(VERSIONS_PAGE, listed_page, listed_page != page),
        Change(TUTORIAL, listed_notebook, listed_notebook != notebook),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("release", help="the EnergyPlus release, as X.Y.Z")
    arguments = parser.parse_args(argv)
    try:
        release = Release.parse(arguments.release)
        require_listed(release)
        planned = changes(release)
    except CannotList as error:
        print(f"adopt_release: {error}", file=sys.stderr)
        return 1
    for change in planned:
        if change.changed:
            change.path.write_text(change.text, encoding="utf-8")
        print(
            f"{change.path.relative_to(ROOT)}: {'listed ' + release.full() if change.changed else 'already lists ' + release.full()}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
