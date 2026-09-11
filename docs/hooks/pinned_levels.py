"""Put the levels this site was built from in front of the reader, on every page (FR-063, SC-023).

A page of reference material describes some particular version of something. This site's
TypeScript reference is generated from an artifact pinned at a `docs-YYYY.N` tag, and its parity
and naming claims are read at a `governance-YYYY.N` tag, and both of those are invisible to a
reader looking at the page. SC-023 says they should not be: someone comparing what the site says
against what their installed copy does needs to know which copy the site is describing.

So four values reach every template through `config.extra`:

    conformance_level   the corpus level the Python library declares it passes (001-FR-024)
    governance_level    the tag the parity ledger and naming register were read at (001-FR-081)
    docs_level          the tag the TypeScript examples and reference came from (001-FR-062, -064)
    library_level       the exact idfkit version the Python reference was generated from, and the
                        weather browser's four files were copied out of (003-FR-025)

`library_level` is the newest of the four and exists because of where this file now lives. While
the site sat inside the Python library, the reference was generated from the checkout around it and
there was nothing to pin: the version was whatever the working tree was. Outside it, the library is
an input like the other three, and an input a page makes claims about has to be named.

WHERE THEY COME FROM, AND WHY NOT FROM mkdocs.yml

Every one of them is already declared in `pyproject.toml`, and restating them here would make two
facts out of one apiece. That failure has happened on this site before: `explanation/naming-map.md`
told readers it was generated at `governance-2026.6` while the release pinned 2026.7, because
advancing the pin had not re-rendered the page and nothing caught it.

A documentation tree copied out of the repository has no `pyproject.toml`, which is ordinary
rather than degraded: the portable build passes each level down through the environment, from the
same pin the repository declares. That is why every read here has an environment variable ahead of
it, and why this hook computes no path out of its own location.
"""

from __future__ import annotations

import os
import re

# tomllib unconditionally, with no tomli fallback. The fallback existed because this hook lived in
# a library that supports 3.10; this repository's floor is 3.12, declared in .python-version and in
# ruff's target-version, so the fallback branch was unreachable code claiming otherwise.
import tomllib
from importlib import metadata
from pathlib import Path
from typing import Any

#: `(config.extra key, [tool.idfkit.<section>] level, environment override)`.
_LEVELS: tuple[tuple[str, str, str], ...] = (
    ("conformance_level", "conformance", "IDFKIT_CONFORMANCE_LEVEL"),
    ("governance_level", "governance", "IDFKIT_GOVERNANCE_LEVEL"),
    ("docs_level", "docs", "IDFKIT_DOCS_LEVEL"),
    ("library_level", "library", "IDFKIT_LIBRARY_LEVEL"),
)


def _declared(section: str, pyproject: Path) -> str | None:
    if not pyproject.is_file():
        return None
    with pyproject.open("rb") as handle:
        document: dict[str, Any] = tomllib.load(handle)
    level = document.get("tool", {}).get("idfkit", {}).get(section, {}).get("level")
    return level if isinstance(level, str) and level else None


def on_config(config: Any) -> Any:
    """Resolve each pinned level and hand it to the templates."""
    # Path.cwd(), never a path derived from __file__. mkdocs runs from the directory holding
    # mkdocs.yml, which is the repository root here and the scratch directory in the portable
    # build; there, the file is absent and the environment answers instead.
    pyproject = Path.cwd() / "pyproject.toml"
    missing: list[str] = []
    for key, section, variable in _LEVELS:
        level = os.environ.get(variable) or _declared(section, pyproject)
        if level is None:
            missing.append(f"[tool.idfkit.{section}] level, or ${variable}")
            continue
        config.extra[key] = level
    if missing:
        # Not a warning. A site that silently omits the level it was built from is exactly what
        # SC-023 forbids, and a build that cannot state one has nothing useful to publish.
        raise SystemExit(
            "the site cannot state which levels it was built from. Declare each of:\n  " + "\n  ".join(missing)
        )
    _refuse_a_second_library_level(config.extra["library_level"])
    return config


def _spelling(version: str) -> str:
    """One spelling per release: [tool.idfkit.library] writes `1.0.0-rc.4`, the wheel `1.0.0rc4`."""
    text = version.strip().lower().removeprefix("v")
    return re.sub(r"[.\-]?(a|b|rc)[.\-]?(\d+)", r"\1\2", text)


def _refuse_a_second_library_level(declared: str) -> None:
    """Refuse to build when the page would state one library level and render another (004-FR-007).

    The library level is written twice, in `[tool.idfkit.library] level` and in the pinned
    dependency, and this hook states the first on every page while mkdocstrings renders the
    reference from whatever the second installed. If they differ the site describes one release and
    documents another, with nothing on the page to say so. `uv lock --locked` does not catch it,
    because uv ignores `[tool.*]` tables (measured in feature 004, T035), so the build refuses here,
    where both builds pass: the repository one reads the table, the portable one the environment.

    The unreleased-library override (IDFKIT_LIBRARY_DIR, 003-FR-023) builds against a working tree
    on purpose, and announces that the result is not evidence about the declared level. Under it
    this comparison would only restate that, so it stands aside.
    """
    if os.environ.get("IDFKIT_LIBRARY_DIR"):
        return
    try:
        installed = metadata.version("idfkit")
    except metadata.PackageNotFoundError:
        raise SystemExit("idfkit is not installed, so the Python reference cannot be generated at any level") from None
    if _spelling(installed) != _spelling(declared):
        raise SystemExit(
            f"the site states idfkit {declared} and the installed idfkit is {installed}. The two places the "
            "library level is written disagree (004-FR-007): [tool.idfkit.library] level and the pinned "
            "dependency. Move both together, as bump-idfkit.yml does."
        )
