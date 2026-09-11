"""The surface check must be able to fail on every rule it claims, and must never pass by not looking.

Nothing here touches the network: the web, the registries and the sources are fakes, so the tests
state exactly what a host answered and what a registry published (T073 to T076, T080 to T085).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_surfaces import (
    Consumer,
    Declaration,
    Register,
    Response,
    Surface,
    check_instruction,
    check_retired,
    exported_names,
    extract_instructions,
    parse_register,
    run,
)

REGISTER = """
[register]
schema_version = "1"
libraries = { python = "idfkit/idfkit", javascript = "idfkit/idfkit-js" }

[[consumer]]
id = "idfkit-developers"
repository = "idfkit/idfkit-developers"
role = "builds"
  [[consumer.libraries]]
  library = "python"
  entry_point = "pypi"
  means = "direct"
    [[consumer.libraries.declared_at]]
    path = "pyproject.toml"
    locator = "project.dependencies[idfkit]"
    form = "exact"
    [[consumer.libraries.declared_at]]
    path = "pyproject.toml"
    locator = "tool.idfkit.library.level"
    form = "exact"

[[consumer]]
id = "envelop"
repository = "idfkit/idfkit-app"
role = "builds"

[[consumer]]
id = "idfkit-com"
repository = "idfkit/idfkit.com"
role = "teaches"

[[surface]]
host = "developers.idfkit.com"
status = "serving"
published_by = "idfkit-developers"
states_level = true

[[surface]]
host = "py.idfkit.com"
status = "retired"
published_by = "idfkit/idfkit"
redirects_to = "developers.idfkit.com"
"""

MARKETING = """
<pre><code><span class="code-keyword">pip install</span> idfkit
<span class="code-keyword">from</span> idfkit <span class="code-keyword">import</span> load
</code></pre>
<pre><code>npm i @idfkit/core @idfkit/schemas
import { loadIdf, saveIdf } from '@idfkit/core/node';
</code></pre>
<code>npm install @idfkit/engine @idfkit/engine-assets@26.1</code>
<code>pip install idfkit-lsp</code>
"""


class FakeWeb:
    def __init__(self, answers: dict[str, Response]) -> None:
        self.answers = answers

    def get(self, url: str) -> Response:
        return self.answers.get(url, Response(url, error="connection refused"))


class FakeRegistry:
    def __init__(self, facade_versions: dict[str, Any] | None = None, exports: set[str] | None = None) -> None:
        self.facade_versions = facade_versions or {}
        self.exports = exports

    def npm(self, package: str) -> dict[str, Any]:
        if package == "idfkit":
            return {"versions": self.facade_versions, "dist-tags": {"latest": "1.0.0"} if self.facade_versions else {}}
        return {"versions": {"0.2.0": {}}, "dist-tags": {"latest": "0.2.0"}}

    def pypi(self, package: str) -> dict[str, Any]:
        return {"info": {"version": "0.0.0-not-installed"}}

    def npm_exports(self, package: str, version: str, subpath: str) -> set[str] | None:
        return self.exports


class FakeSources:
    def __init__(self, files: dict[tuple[str, str], str | None], unreachable: set[str] | None = None) -> None:
        self.files = files
        self.unreachable = unreachable or set()

    def read(self, repository: str, path: str) -> str | None:
        if repository in self.unreachable:
            raise ConnectionError(repository)
        return self.files.get((repository, path))


def _register() -> Register:
    return parse_register(REGISTER, "test register")


def _site(tmp_path: Path, level: str = "1.0.0-rc.4") -> Path:
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\ndependencies = ["idfkit=={level}"]\n[tool.idfkit.library]\nlevel = "{level}"\n'
    )
    return tmp_path


def _page(level: str) -> Response:
    return Response(
        "https://developers.idfkit.com/", 200, body=f"<html><footer>Built from <b>idfkit {level}</b></footer></html>"
    )


RETIRED_200 = Response(
    "https://py.idfkit.com/",
    200,
    body='<html><head><title>idfkit</title><link rel="canonical" href="https://py.idfkit.com/"></head>'
    + "x" * 900
    + "</html>",
)


# ── Half A ──────────────────────────────────────────────────────────────────────────────────────


def test_the_set_of_surfaces_comes_from_the_register() -> None:
    assert [s.host for s in _register().surfaces] == ["developers.idfkit.com", "py.idfkit.com"]


def test_a_retired_host_serving_content_fails_naming_what_it_served() -> None:
    [finding] = check_retired(_register().surfaces[1], FakeWeb({"https://py.idfkit.com/": RETIRED_200}))
    assert finding.kind == "failure"
    assert (
        "'idfkit'" in finding.message
        and "canonical https://py.idfkit.com/" in finding.message
        and "bytes" in finding.message
    )


def test_a_permanent_redirect_to_the_unified_host_passes() -> None:
    web = FakeWeb({
        "https://py.idfkit.com/": Response("https://py.idfkit.com/", 301, location="https://developers.idfkit.com/")
    })
    assert check_retired(_register().surfaces[1], web) == []


def test_a_chain_of_permanent_redirects_is_followed() -> None:
    web = FakeWeb({
        "https://py.idfkit.com/": Response("", 308, location="https://www.py.idfkit.com/"),
        "https://www.py.idfkit.com/": Response("", 301, location="https://developers.idfkit.com/"),
    })
    assert check_retired(_register().surfaces[1], web) == []


def test_a_temporary_redirect_is_not_a_retirement() -> None:
    web = FakeWeb({"https://py.idfkit.com/": Response("", 302, location="https://developers.idfkit.com/")})
    [finding] = check_retired(_register().surfaces[1], web)
    assert finding.kind == "failure" and "temporary" in finding.message


def test_a_redirect_somewhere_else_is_followed_to_its_content_and_fails() -> None:
    web = FakeWeb({
        "https://py.idfkit.com/": Response("", 301, location="https://elsewhere.example/"),
        "https://elsewhere.example/": Response("https://elsewhere.example/", 200, body="<title>Other</title>"),
    })
    assert check_retired(_register().surfaces[1], web)[0].kind == "failure"


def test_an_unreachable_host_is_never_a_pass(tmp_path: Path) -> None:
    report = run(_register(), FakeWeb({}), FakeSources({}), FakeRegistry(), _site(tmp_path), "a")
    assert {f.kind for f in report.findings} == {"unreachable"}
    assert report.exit_code == 2


def test_a_serving_host_stating_the_declared_level_passes(tmp_path: Path) -> None:
    web = FakeWeb({
        "https://developers.idfkit.com/": _page("1.0.0rc4"),
        "https://py.idfkit.com/": Response("", 301, location="https://developers.idfkit.com/"),
    })
    report = run(_register(), web, FakeSources({}), FakeRegistry(), _site(tmp_path), "a")
    assert report.findings == [] and report.exit_code == 0


def test_a_serving_host_stating_another_level_fails(tmp_path: Path) -> None:
    web = FakeWeb({
        "https://developers.idfkit.com/": _page("1.0.0-rc.3"),
        "https://py.idfkit.com/": Response("", 301, location="https://developers.idfkit.com/"),
    })
    report = run(_register(), web, FakeSources({}), FakeRegistry(), _site(tmp_path), "a")
    [finding] = report.findings
    assert "states idfkit 1.0.0-rc.3" in finding.message and "declares 1.0.0-rc.4" in finding.message


def test_a_serving_host_stating_no_level_fails(tmp_path: Path) -> None:
    web = FakeWeb({"https://developers.idfkit.com/": Response("", 200, body="<p>docs</p>")})
    register = Register(_register().surfaces[:1], _register().consumers, (), "t")
    [finding] = run(register, web, FakeSources({}), FakeRegistry(), _site(tmp_path), "a").findings
    assert "state no level" in finding.message


def test_declarations_that_disagree_are_not_a_level(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["idfkit==1.0.0rc4"]\n[tool.idfkit.library]\nlevel = "1.0.0-rc.3"\n'
    )
    web = FakeWeb({"https://developers.idfkit.com/": _page("1.0.0rc4")})
    register = Register(_register().surfaces[:1], _register().consumers, (), "t")
    [finding] = run(register, web, FakeSources({}), FakeRegistry(), tmp_path, "a").findings
    assert "FR-007" in finding.message


# ── Half B ──────────────────────────────────────────────────────────────────────────────────────


def test_instructions_are_read_out_of_html_with_their_symbols() -> None:
    found = extract_instructions("idfkit/idfkit.com:index.html", MARKETING, is_html=True)
    assert [(i.language, i.packages) for i in found] == [
        ("python", ("idfkit",)),
        ("javascript", ("@idfkit/core", "@idfkit/schemas")),
    ]
    assert [s.name for s in found[1].symbols] == ["loadIdf", "saveIdf"]
    assert [s.name for s in found[0].symbols] == ["load"]


def test_out_of_scope_and_server_packages_are_not_instructions_for_either_library() -> None:
    found = extract_instructions("x", "npm i @idfkit/engine\npip install idfkit-mcp\nnpm install\n")
    assert found == []


def test_half_b_demands_nothing_while_the_shared_name_is_unpublished() -> None:
    [js] = [
        i
        for i in extract_instructions("idfkit/idfkit.com:index.html", MARKETING, is_html=True)
        if i.language == "javascript"
    ]
    findings = check_instruction(js, FakeRegistry(exports={"loadIdf", "saveIdf"}))
    assert [f.kind for f in findings] == ["dormant"]


def test_half_b_activates_the_moment_the_facade_publishes() -> None:
    # T084: the same page, the same instruction, a registry where `idfkit` has a version.
    [js] = [
        i
        for i in extract_instructions("idfkit/idfkit.com:index.html", MARKETING, is_html=True)
        if i.language == "javascript"
    ]
    findings = check_instruction(js, FakeRegistry({"1.0.0": {}}, exports={"loadIdf", "saveIdf"}))
    [failure] = [f for f in findings if f.kind == "failure"]
    assert failure.subject == "idfkit/idfkit.com:index.html:5"
    assert "`npm i @idfkit/core @idfkit/schemas`" in failure.message


def test_an_instruction_naming_the_shared_name_passes_once_published() -> None:
    [js] = extract_instructions("r:README.md", "npm install idfkit\n")
    assert [f for f in check_instruction(js, FakeRegistry({"1.0.0": {}})) if f.kind == "failure"] == []


def test_a_symbol_the_package_does_not_export_fails() -> None:
    [js] = [i for i in extract_instructions("p", MARKETING, is_html=True) if i.language == "javascript"]
    findings = check_instruction(js, FakeRegistry(exports={"saveIdf"}))
    assert any(f.kind == "failure" and "loadIdf" in f.message for f in findings)


def test_an_unknowable_symbol_is_unverified_never_present() -> None:
    [js] = [i for i in extract_instructions("p", MARKETING, is_html=True) if i.language == "javascript"]
    findings = check_instruction(js, FakeRegistry(exports=None))
    assert {f.kind for f in findings} == {"dormant"} and any("could not be verified" in f.message for f in findings)


def test_exported_names_follow_star_reexports() -> None:
    files = {
        "package.json": json.dumps({"exports": {"./node": {"types": "./dist/node.d.ts"}}}),
        "dist/node.d.ts": "export * from './save.js';\nexport declare function loadIdf(p: string): void;\n",
        "dist/save.d.ts": "export { saveIdf, type Options as SaveOptions } from './impl.js';\n",
    }
    assert exported_names(files.get, "node") == {"loadIdf", "saveIdf", "SaveOptions"}


def test_every_readme_and_the_teaching_page_are_read(tmp_path: Path) -> None:
    sources = FakeSources(
        {("idfkit/idfkit.com", "index.html"): MARKETING, ("idfkit/idfkit", "README.md"): "pip install idfkit\n"},
        unreachable={"idfkit/idfkit-app"},
    )
    report = run(_register(), FakeWeb({}), sources, FakeRegistry(exports={"loadIdf", "saveIdf"}), _site(tmp_path), "b")
    assert any(f.kind == "unreachable" and "idfkit/idfkit-app" in f.subject for f in report.findings)
    assert any("idfkit/idfkit:README.md:1" in p for p in report.passed)


def test_a_consumers_entry_point_is_never_flagged_and_migrating_it_changes_nothing(tmp_path: Path) -> None:
    # FR-037, FR-044. The check reads instructions, never manifests. A scoped consumer's package.json
    # is invisible to it, so it cannot be flagged, and rewriting that manifest to the shared name
    # cannot turn a failing instruction green.
    registry = FakeRegistry({"1.0.0": {}}, exports={"loadIdf", "saveIdf"})

    def verdict(manifest: str) -> list[tuple[str, str]]:
        sources = FakeSources({
            ("idfkit/idfkit.com", "index.html"): MARKETING,
            ("idfkit/idfkit-app", "package.json"): manifest,
            ("idfkit/idfkit-app", "README.md"): "npm install\n",
        })
        findings = run(_register(), FakeWeb({}), sources, registry, _site(tmp_path), "b").findings
        return [(f.subject, f.kind) for f in findings]

    scoped = verdict(json.dumps({"dependencies": {"@idfkit/core": "0.3.0"}}))
    migrated = verdict(json.dumps({"dependencies": {"idfkit": "1.0.0"}}))
    assert scoped == migrated
    assert not any("idfkit-app" in subject for subject, _ in scoped)


@pytest.mark.parametrize("surface", [Surface("x", "paused", "idfkit-developers")])
def test_an_unknown_status_fails(surface: Surface, tmp_path: Path) -> None:
    register = Register(
        (surface,),
        (Consumer("idfkit-developers", "idfkit/idfkit-developers", "builds", (Declaration("p", "l"),)),),
        (),
        "t",
    )
    assert run(register, FakeWeb({}), FakeSources({}), FakeRegistry(), tmp_path, "a").exit_code == 1
