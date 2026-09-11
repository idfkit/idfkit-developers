"""Render the generated half of ``docs/explanation/consumers.md`` from the consumer register.

The register lives in ``idfkit/idfkit-conformance`` as ``governance/consumers.toml`` (feature 004).
It is the roster of every project in the workspace that resolves either library or teaches a reader
to install one, and it is read at the immutable ``governance-YYYY.N`` tag this release pins in
``[tool.idfkit.governance] level``, never from a moving branch, through the duplicated
``scripts/_governance_source.py``, exactly as the parity and naming pages are.

Nothing between the generated markers is written by hand. The page is a view of the file, so the
page a reader sees and the file every consumer's self-check reads cannot disagree.

THE PAGE STATES NO LEVEL, AND THAT IS THE POINT. The register never restates a consumer's level; it
says where the level is written (research R2). A page that looked the levels up and printed them
would be a second copy of numbers that move on every bump, rendered at a tag that does not. So the
page shows where each level lives, and a reader follows that to the consumer's own file. The
scheduled sweep in idfkit-conformance is what reads the levels and says who is behind.

Usage::

    uv run python scripts/render_consumers_page.py            # rewrite the generated region
    uv run python scripts/render_consumers_page.py --check    # fail if the page is stale

The register is located, in order: ``--register PATH`` (a working tree, and an announced override of
the pinned read), then ``--conformance-dir``, then ``$IDFKIT_CONFORMANCE_DIR``, then a sibling
``idfkit-conformance`` checkout next to this repository.
"""

from __future__ import annotations

import argparse
import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _governance_source import read_pinned

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = REPO_ROOT / "docs" / "explanation" / "consumers.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REGISTER_RELATIVE = Path("governance") / "consumers.toml"
REGISTER_REPO = "https://github.com/idfkit/idfkit-conformance"

BEGIN_MARKER = "<!-- BEGIN GENERATED FROM consumers.toml. Edit the register, not this page. -->"
END_MARKER = "<!-- END GENERATED FROM consumers.toml. -->"

ROLE_WORDS = {
    "builds": "builds against it",
    "delivers": "delivers it to a person",
    "teaches": "teaches a reader to install it",
}
MEANS_WORDS = {
    "direct": "declared directly",
    "through-consumer": "through another consumer",
    "image": "in a container image",
    "runtime-fetch": "fetched when an editor starts",
    "prose": "named in prose",
}
LIBRARY_WORDS = {"python": "Python", "javascript": "JavaScript"}
DOOR_WORDS = {"pypi": "`idfkit`", "shared-name": "the shared name", "scoped": "the scoped packages"}


@dataclass(frozen=True)
class Place:
    """Where one level is written."""

    path: str
    locator: str
    form: str
    package: str
    via: str


@dataclass(frozen=True)
class Lag:
    kind: str
    issue: str
    reason: str


@dataclass(frozen=True)
class Resolution:
    library: str
    entry_point: str
    means: str
    places: tuple[Place, ...]
    lag: Lag | None


@dataclass(frozen=True)
class Ungoverned:
    package: str
    note: str


@dataclass(frozen=True)
class Consumer:
    id: str
    repository: str
    role: str
    depends_on: tuple[str, ...]
    resolutions: tuple[Resolution, ...]
    ungoverned: tuple[Ungoverned, ...]
    formatting: str


@dataclass(frozen=True)
class Surface:
    host: str
    status: str
    published_by: str
    redirects_to: str


def _text(table: dict[str, Any], key: str) -> str:
    value = table.get(key, "")
    return " ".join(value.split()) if isinstance(value, str) else ""


def parse(text: str) -> tuple[list[Consumer], list[Surface]]:
    document: dict[str, Any] = tomllib.loads(text)
    consumers: list[Consumer] = []
    for row in document.get("consumer", []):
        resolutions: list[Resolution] = []
        for resolution in row.get("libraries", []):
            lag = resolution.get("lag")
            resolutions.append(
                Resolution(
                    library=_text(resolution, "library"),
                    entry_point=_text(resolution, "entry_point"),
                    means=_text(resolution, "means"),
                    places=tuple(
                        Place(
                            _text(d, "path"),
                            _text(d, "locator"),
                            _text(d, "form"),
                            _text(d, "package"),
                            _text(d, "via"),
                        )
                        for d in resolution.get("declared_at", [])
                    ),
                    lag=Lag(_text(lag, "kind"), _text(lag, "issue"), _text(lag, "reason"))
                    if isinstance(lag, dict)
                    else None,
                )
            )
        consumers.append(
            Consumer(
                id=_text(row, "id"),
                repository=_text(row, "repository"),
                role=_text(row, "role"),
                depends_on=tuple(str(d) for d in row.get("depends_on", [])),
                resolutions=tuple(resolutions),
                ungoverned=tuple(
                    Ungoverned(_text(o, "package"), _text(o, "note")) for o in row.get("out_of_scope", [])
                ),
                formatting=_text(row, "preserves_formatting"),
            )
        )
    surfaces = [
        Surface(_text(s, "host"), _text(s, "status"), _text(s, "published_by"), _text(s, "redirects_to"))
        for s in document.get("surface", [])
    ]
    return consumers, surfaces


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _place(place: Place) -> str:
    what = f" ({place.package} via `{place.via}`)" if place.package else ""
    form = "" if place.form == "exact" else f", {place.form}"
    return f"`{place.path}` at `{place.locator}`{what}{form}"


def _lag(lag: Lag | None) -> str:
    if lag is None:
        return "none"
    if lag.kind == "not-yet":
        return f"not yet, [tracked]({lag.issue})"
    return f"deliberate: {_cell(lag.reason)}"


def render(consumers: list[Consumer], surfaces: list[Surface], level: str) -> str:
    source_url = f"{REGISTER_REPO}/blob/{level}/governance/consumers.toml"
    lines = [
        f"Generated from [`governance/consumers.toml`]({source_url}) at `{level}`, the governance tag this",
        "release pins. Correct the register and regenerate; a correction made on this page would be",
        "overwritten, and it would never reach a consumer's self-check.",
        "",
        "## Every consumer { #every-consumer }",
        "",
        "| Consumer | Repository | Role | Depends on |",
        "| --- | --- | --- | --- |",
    ]
    for consumer in consumers:
        depends = ", ".join(f"`{d}`" for d in consumer.depends_on) or "nothing"
        lines.append(
            f"| `{consumer.id}` | [{consumer.repository}](https://github.com/{consumer.repository}) | "
            f"{ROLE_WORDS.get(consumer.role, consumer.role)} | {depends} |"
        )

    lines += [
        "",
        "## Where each level is written { #where-each-level-is-written }",
        "",
        "One row per consumer per library. Follow the place to read the level; the register never",
        'states it. A lag of "none" means nothing is wrong: it is the normal state.',
        "",
        "| Consumer | Library | Door | How | Where the level is written | Lag |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for consumer in consumers:
        for resolution in consumer.resolutions:
            places = (
                "<br>".join(_place(p) for p in resolution.places) or f"the level of {', '.join(consumer.depends_on)}"
            )
            lines.append(
                f"| `{consumer.id}` | {LIBRARY_WORDS.get(resolution.library, resolution.library)} | "
                f"{DOOR_WORDS.get(resolution.entry_point, resolution.entry_point)} | "
                f"{MEANS_WORDS.get(resolution.means, resolution.means)} | {places} | {_lag(resolution.lag)} |"
            )

    ungoverned = [(c.id, u) for c in consumers for u in c.ungoverned]
    if ungoverned:
        lines += [
            "",
            "## Recorded, and governed by nothing here { #ungoverned }",
            "",
            "Dependencies the constitution places outside the unification. They are listed so that a",
            "coordinated bump can see them, and no check in the register acts on them.",
            "",
            "| Consumer | Package | Note |",
            "| --- | --- | --- |",
        ]
        lines += [f"| `{cid}` | `{u.package}` | {_cell(u.note)} |" for cid, u in ungoverned]

    writers = [c for c in consumers if c.formatting]
    if writers:
        lines += [
            "",
            "## Does a save keep the user's formatting? { #formatting }",
            "",
            "What each consumer does today when it writes a model to disk, not what it should do or",
            "plans to. The register carries the reason beside each answer.",
            "",
            "| Consumer | Preserves formatting |",
            "| --- | --- |",
        ]
        lines += [f"| `{c.id}` | {c.formatting} |" for c in writers]

    lines += [
        "",
        "## Documentation surfaces { #surfaces }",
        "",
        "| Host | Status | Published by | Must |",
        "| --- | --- | --- | --- |",
    ]
    for surface in surfaces:
        must = (
            f"redirect permanently to `{surface.redirects_to}`"
            if surface.status == "retired"
            else "state the level it describes"
        )
        lines.append(f"| `{surface.host}` | {surface.status} | `{surface.published_by}` | {must} |")
    return "\n".join(lines) + "\n"


def splice(page: str, body: str) -> str:
    begin = page.find(BEGIN_MARKER)
    end = page.find(END_MARKER)
    if begin == -1 or end == -1 or end < begin:
        sys.exit(f"{PAGE_PATH}: the generated markers are missing or out of order")
    return f"{page[: begin + len(BEGIN_MARKER)]}\n\n{body}\n{page[end:]}"


def governance_level() -> str:
    from_env = os.environ.get("IDFKIT_GOVERNANCE_LEVEL")
    if from_env:
        return from_env
    with PYPROJECT_PATH.open("rb") as handle:
        level = tomllib.load(handle).get("tool", {}).get("idfkit", {}).get("governance", {}).get("level")
    if not isinstance(level, str) or not level:
        sys.exit("[tool.idfkit.governance] level is not declared, so the register cannot be read at a tag")
    return level


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--register", type=Path, help="consumers.toml from a working tree; overrides the pinned read")
    parser.add_argument("--conformance-dir", type=Path, help="Root of an idfkit-conformance checkout.")
    parser.add_argument("--check", action="store_true", help="Fail if the page on disk is not what this would write.")
    args = parser.parse_args(argv)

    if args.register is not None:
        path = args.register
    else:
        from_env = os.environ.get("IDFKIT_CONFORMANCE_DIR")
        root = args.conformance_dir or (Path(from_env) if from_env else REPO_ROOT.parent / "idfkit-conformance")
        path = root / REGISTER_RELATIVE
    level = governance_level()
    source = read_pinned(path, level, override=args.register is not None)
    if not source.pinned:
        print(f"note: reading {source.description}", file=sys.stderr)
    consumers, surfaces = parse(source.text)

    current = PAGE_PATH.read_text(encoding="utf-8")
    updated = splice(current, render(consumers, surfaces, level))
    if args.check:
        if updated != current:
            print(f"{PAGE_PATH} is stale. Run: uv run python scripts/render_consumers_page.py")
            return 1
        print(f"{PAGE_PATH} is up to date with {source.description} ({len(consumers)} consumers)")
        return 0
    if updated != current:
        PAGE_PATH.write_text(updated, encoding="utf-8")
        print(f"rewrote {PAGE_PATH} from {source.description} ({len(consumers)} consumers)")
    else:
        print(f"{PAGE_PATH} already matches {source.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
