#!/usr/bin/env python3
"""Name the next and the latest site release, and say which pinned levels two commits disagree on.

developers.idfkit.com is published from a release of this repository, never from a merge, not even
one that moves a pinned level (deploy-docs.yml). A maintainer decides when to release.

``next-tag`` prints the tag the next release takes. Site releases are tagged ``site-YYYY.N``: the
year, and a counter that starts at 1 each year. The same shape as the ``docs-YYYY.N``,
``governance-YYYY.N`` and ``conformance-YYYY.N`` tags this repository already pins, with a prefix
that says which of them it is. It is a date and a count, not a semantic version, because a site
has no API whose compatibility a version number could promise anything about.

``latest-tag`` prints the most recent ``site-YYYY.N`` tag: the release the live site should be
serving. surfaces.yml checks the live site against the levels that release declares
(``scripts/check_surfaces.py --declared-at``), so a level merged to ``main`` but not yet released
is not a failure.

``levels-changed BEFORE AFTER`` prints every ``[tool.idfkit.*] level`` in ``pyproject.toml`` that
differs between two commits, one per line, and nothing when none does. surfaces.yml calls it with
the latest release and ``main``, and warns, without failing, while ``main`` declares a level no
release has published: a release is due.

Exit status: 0 on success, 2 when a commit or ``pyproject.toml`` cannot be read.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

TAG_PATTERN = re.compile(r"site-(\d{4})\.(\d+)")


def next_tag(tags: Iterable[str], year: int) -> str:
    """The tag after the highest ``site-<year>.N`` in *tags*, or ``site-<year>.1`` when there is none.

    Tags from other years, and anything not shaped ``site-YYYY.N``, are ignored.

    >>> next_tag([], 2026)
    'site-2026.1'
    >>> next_tag(["site-2026.1", "site-2026.10", "site-2026.9", "site-2025.40", "v1.0.0"], 2026)
    'site-2026.11'
    """
    counts = [
        int(match.group(2))
        for tag in tags
        if (match := TAG_PATTERN.fullmatch(tag.strip())) is not None and int(match.group(1)) == year
    ]
    return f"site-{year}.{max(counts, default=0) + 1}"


def latest_tag(tags: Iterable[str]) -> str | None:
    """The most recent ``site-YYYY.N`` tag in *tags*, by year and then count, or None.

    >>> latest_tag(["site-2026.9", "site-2026.10", "site-2025.40", "v1.0.0"])
    'site-2026.10'
    >>> latest_tag(["v1.0.0"]) is None
    True
    """
    shaped = [
        (int(match.group(1)), int(match.group(2)), tag.strip())
        for tag in tags
        if (match := TAG_PATTERN.fullmatch(tag.strip())) is not None
    ]
    return max(shaped)[2] if shaped else None


def pinned_levels(pyproject: Mapping[str, Any]) -> dict[str, str]:
    """Every ``[tool.idfkit.<name>] level`` in a parsed ``pyproject.toml``, keyed by ``<name>``."""
    tables = pyproject.get("tool", {}).get("idfkit", {})
    return {
        name: str(table["level"]) for name, table in tables.items() if isinstance(table, Mapping) and "level" in table
    }


def changed_levels(before: Mapping[str, Any], after: Mapping[str, Any]) -> list[str]:
    """``<name>: <old> -> <new>`` for each pinned level that differs, sorted by name.

    A level present on only one side counts as changed, shown as ``(none)`` on the other.

    >>> old = {"tool": {"idfkit": {"library": {"level": "1.1.1"}, "docs": {"level": "docs-2026.8"}}}}
    >>> new = {"tool": {"idfkit": {"library": {"level": "1.2.0"}, "docs": {"level": "docs-2026.8"}}}}
    >>> changed_levels(old, new)
    ['library: 1.1.1 -> 1.2.0']
    >>> changed_levels(old, old)
    []
    """
    old, new = pinned_levels(before), pinned_levels(after)
    return [
        f"{name}: {old.get(name, '(none)')} -> {new.get(name, '(none)')}"
        for name in sorted(old.keys() | new.keys())
        if old.get(name) != new.get(name)
    ]


def _pyproject_at(commit: str) -> dict[str, Any]:
    shown = subprocess.run(  # noqa: S603
        ["git", "show", f"{commit}:pyproject.toml"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if shown.returncode != 0:
        sys.stderr.write(f"cannot read pyproject.toml at {commit}: {shown.stderr.strip()}\n")
        raise SystemExit(2)
    return tomllib.loads(shown.stdout)


def _tags() -> list[str]:
    listed = subprocess.run(
        ["git", "tag", "--list", "site-*"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if listed.returncode != 0:
        sys.stderr.write(f"cannot list tags: {listed.stderr.strip()}\n")
        raise SystemExit(2)
    return listed.stdout.split()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    tag = commands.add_parser("next-tag", help="print the tag the next site release takes")
    tag.add_argument("--year", type=int, help="the release year; default the current UTC year")

    commands.add_parser("latest-tag", help="print the most recent site release tag")

    levels = commands.add_parser("levels-changed", help="print the pinned levels two commits disagree on")
    levels.add_argument("before", help="the commit before the change")
    levels.add_argument("after", help="the commit after the change")

    args = parser.parse_args(argv)
    if args.command == "next-tag":
        year = args.year if args.year is not None else datetime.now(tz=UTC).year
        print(next_tag(_tags(), year))
    elif args.command == "latest-tag":
        latest = latest_tag(_tags())
        if latest is None:
            sys.stderr.write("no site-YYYY.N release tag found\n")
            return 2
        print(latest)
    else:
        for line in changed_levels(_pyproject_at(args.before), _pyproject_at(args.after)):
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
