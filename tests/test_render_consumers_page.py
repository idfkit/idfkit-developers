"""The register page is a view of the register: every consumer, every place, and never a level (T094)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from render_consumers_page import BEGIN_MARKER, END_MARKER, parse, render, splice

REGISTER = """
[register]
schema_version = "1"
libraries = { python = "idfkit/idfkit", javascript = "idfkit/idfkit-js" }

[[consumer]]
id = "idfkit-docs"
repository = "idfkit/idfkit-docs"
role = "builds"
  [[consumer.libraries]]
  library = "python"
  entry_point = "pypi"
  means = "direct"
    [[consumer.libraries.declared_at]]
    path = "pyproject.toml"
    locator = "project.dependencies[idfkit]"
    form = "exact"
    [consumer.libraries.lag]
    kind = "not-yet"
    issue = "https://github.com/idfkit/idfkit-docs/pull/30"

[[consumer]]
id = "envelop"
repository = "idfkit/idfkit-app"
role = "builds"
preserves_formatting = "yes"
  [[consumer.libraries]]
  library = "javascript"
  entry_point = "scoped"
  means = "direct"
    [[consumer.libraries.declared_at]]
    path = "package.json"
    locator = 'dependencies["@idfkit/core"]'
    form = "exact"
  [[consumer.out_of_scope]]
  package = "@idfkit/engine"
  path = "package.json"
  locator = 'dependencies["@idfkit/engine"]'
  form = "exact"
  note = "Outside the unification."

[[consumer]]
id = "idfkit-plugin"
repository = "idfkit/idfkit-plugin"
role = "delivers"
depends_on = ["idfkit-mcp"]
  [[consumer.libraries]]
  library = "python"
  entry_point = "pypi"
  means = "runtime-fetch"
    [[consumer.libraries.declared_at]]
    path = ".mcp.json"
    locator = "mcpServers.idfkit.args[0]"
    form = "exact"
    package = "idfkit-mcp"
    via = "idfkit-mcp"

[[surface]]
host = "py.idfkit.com"
status = "retired"
published_by = "idfkit/idfkit"
redirects_to = "developers.idfkit.com"
"""


def _page() -> str:
    consumers, surfaces = parse(REGISTER)
    return render(consumers, surfaces, "governance-2026.18")


def test_every_consumer_and_place_appears() -> None:
    page = _page()
    for consumer in ("idfkit-docs", "envelop", "idfkit-plugin"):
        assert f"`{consumer}`" in page
    assert "`pyproject.toml` at `project.dependencies[idfkit]`" in page
    assert "(idfkit-mcp via `idfkit-mcp`)" in page


def test_lags_render_their_evidence_and_absence_means_none() -> None:
    page = _page()
    assert "not yet, [tracked](https://github.com/idfkit/idfkit-docs/pull/30)" in page
    assert re.search(r"\| `envelop` \| JavaScript \| the scoped packages \| declared directly \| .* \| none \|", page)


def test_out_of_scope_and_surfaces_are_shown() -> None:
    page = _page()
    assert "`@idfkit/engine`" in page and "governed by nothing here" in page
    assert "redirect permanently to `developers.idfkit.com`" in page


def test_the_page_states_no_level() -> None:
    # R2: the register never restates a level, and neither may its rendering. The only version-like
    # string on the page is the governance tag it was generated at.
    assert re.findall(r"\b\d+\.\d+\.\d+", _page()) == []


def test_splice_replaces_only_the_generated_region() -> None:
    page = f"prose\n\n{BEGIN_MARKER}\n\nold\n{END_MARKER}\nafter\n"
    spliced = splice(page, "new\n")
    assert spliced.startswith("prose") and spliced.endswith("after\n") and "old" not in spliced and "new" in spliced
