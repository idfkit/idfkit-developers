"""Every surface a reader lands on teaches a level somebody declared (feature 004, User Story 5).

Two independent halves, separable on purpose because one can land today and the other cannot
(specs/004-integrate-unified-releases/contracts/published-surfaces.md).

HALF A, THE DOCUMENTATION HOSTS. Landable immediately.

* A host the register records as ``retired`` must answer with a permanent redirect (301 or 308)
  that reaches its ``redirects_to``. A 200 with content is a failure, and the failure names the host
  and what it served: its title, its size, and where its canonical link points (FR-031).
* A host recorded as ``serving`` must put a level in front of the reader, and that level must be the
  one the register points at for the consumer that publishes it (FR-030). For
  ``developers.idfkit.com`` that is ``[tool.idfkit.library] level`` in this repository, which
  ``docs/hooks/pinned_levels.py`` writes onto every page.
* A host that cannot be reached is reported as UNREACHABLE, never as a pass. Not-checked is not the
  same as clean, on the principle that keeps ``unreachable`` apart from ``strangers`` in the sweep.

HALF B, THE INSTALL INSTRUCTIONS. Lands green and waits.

* Every install instruction the workspace publishes, in the README of every repository the register
  lists and on the marketing page of every consumer that ``teaches``, must name what the unification
  publishes for its language (FR-026). A violation names the file, the line and the instruction
  (FR-027).
* It demands nothing for a name that has no published version (FR-028). The shared install name has
  zero versions on npm today, so every second-language instruction is DORMANT: counted, reported,
  and not failed. The moment the facade publishes, the same instructions are held to it, with no
  change here.
* Symbols an instruction shows are checked against what the named package exports at the version a
  reader following it would receive today (FR-029). See "What is not checkable" below.
* It reads instructions and nothing else. A consumer's own manifest is never read here, so a consumer
  on the scoped packages is never flagged for its entry point, and no instruction can be satisfied by
  migrating one (FR-037, FR-044).

WHERE THE SET OF SURFACES COMES FROM. The ``[[surface]]`` rows of ``governance/consumers.toml`` in
idfkit-conformance, read at the governance tag ``[tool.idfkit.governance] level`` pins, through the
duplicated ``_governance_source.read_pinned``. Never from a list in this file: a surface nobody
registered is found by registering it, not by editing a checker. The retired hosts are tracked for
retirement in idfkit/idfkit-developers#15, which is feature 003's obligation, not this check's
(004-FR-043); this check asserts the redirect and is indifferent to the mechanism.

WHAT IS NOT CHECKABLE, STATED RATHER THAN IMPLIED

* A symbol is checked against the version a reader installs today: PyPI's current release for
  Python, the ``latest`` dist-tag for npm. FR-029 asks for "the level the register declares for the
  project publishing the instruction", and the register declares no level for a consumer that only
  teaches. For a consumer that does declare one, the declaration lives in its manifest, and reading
  manifests is exactly what this check must not do (FR-044). So the check holds an instruction to what
  following it would install, which is the question the reader actually has.
* A Python symbol is checked against the installed ``idfkit`` only when that is the version a reader
  would receive. Otherwise it is reported as unverified, never as present.
* A JavaScript symbol is looked up in the type declarations the named subpath exports, following
  ``export * from`` into sibling declaration files. A name reached some other way is reported as
  unverified, never as missing.

Usage::

    uv run python scripts/check_surfaces.py                       # both halves, against the network
    uv run python scripts/check_surfaces.py --half a              # the documentation hosts only
    uv run python scripts/check_surfaces.py --workspace ..        # read instructions from sibling checkouts

Exit status: 0 every surface answered for itself, 1 at least one failure, 2 no failure but something
could not be reached, which is never a pass.
"""

from __future__ import annotations

import argparse
import base64
import html
import importlib
import io
import json
import re
import subprocess
import sys
import tarfile
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Protocol

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _governance_source import read_pinned

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REGISTER_RELATIVE = Path("governance") / "consumers.toml"
#: The consumer id of this repository in the register. Its levels are read from this checkout.
THIS_CONSUMER = "idfkit-developers"

PERMANENT = frozenset({301, 308})
TEMPORARY = frozenset({302, 303, 307})
MAX_HOPS = 5

#: What the unification publishes for each language: one install name. Both are `idfkit`.
PUBLISHED_NAME = {"python": "idfkit", "javascript": "idfkit"}
SCOPED = frozenset({"@idfkit/core", "@idfkit/schemas", "@idfkit/weather", "@idfkit/language"})


# ---------------------------------------------------------------------------
# The register
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Surface:
    host: str
    status: str
    published_by: str
    states_level: bool = False
    redirects_to: str = ""


@dataclass(frozen=True)
class Declaration:
    path: str
    locator: str


@dataclass(frozen=True)
class Consumer:
    id: str
    repository: str
    role: str
    python_declarations: tuple[Declaration, ...] = ()


@dataclass(frozen=True)
class Register:
    surfaces: tuple[Surface, ...]
    consumers: tuple[Consumer, ...]
    libraries: tuple[str, ...]
    description: str

    def consumer(self, consumer_id: str) -> Consumer | None:
        return next((c for c in self.consumers if c.id == consumer_id), None)


def parse_register(text: str, description: str) -> Register:
    document: dict[str, Any] = tomllib.loads(text)
    surfaces = tuple(
        Surface(
            host=str(row["host"]),
            status=str(row["status"]),
            published_by=str(row["published_by"]),
            states_level=bool(row.get("states_level", False)),
            redirects_to=str(row.get("redirects_to", "")),
        )
        for row in document.get("surface", [])
    )
    consumers: list[Consumer] = []
    for row in document.get("consumer", []):
        declarations: list[Declaration] = []
        for resolution in row.get("libraries", []):
            if resolution.get("library") == "python":
                declarations += [
                    Declaration(str(d["path"]), str(d["locator"])) for d in resolution.get("declared_at", [])
                ]
        consumers.append(Consumer(str(row["id"]), str(row["repository"]), str(row["role"]), tuple(declarations)))
    libraries = tuple(str(v) for v in document.get("register", {}).get("libraries", {}).values())
    return Register(surfaces, tuple(consumers), libraries, description)


def governance_level(pyproject: Path = PYPROJECT_PATH) -> str:
    with pyproject.open("rb") as handle:
        level = tomllib.load(handle).get("tool", {}).get("idfkit", {}).get("governance", {}).get("level")
    if not isinstance(level, str) or not level:
        sys.exit("[tool.idfkit.governance] level is not declared, so the register cannot be read at a tag")
    return level


def load_register(explicit: Path | None, conformance_dir: Path | None) -> Register:
    """Read the register at the pinned tag, or from *explicit* as an announced override."""
    import os

    if explicit is not None:
        path = explicit
    else:
        root = conformance_dir or (
            Path(os.environ["IDFKIT_CONFORMANCE_DIR"]) if os.environ.get("IDFKIT_CONFORMANCE_DIR") else None
        )
        path = (root or REPO_ROOT.parent / "idfkit-conformance") / REGISTER_RELATIVE
    source = read_pinned(path, governance_level(), override=explicit is not None)
    if not source.pinned:
        print(f"note: reading {source.description}", file=sys.stderr)
    return parse_register(source.text, source.description)


# ---------------------------------------------------------------------------
# Levels
# ---------------------------------------------------------------------------

_PRE = re.compile(r"[.\-]?(alpha|beta|a|b|rc)[.\-]?(\d*)")


def normalize(version: str) -> str:
    """One spelling per release: the site writes `1.0.0-rc.4` and PyPI `1.0.0rc4`."""
    text = version.strip().lower().removeprefix("v")
    return _PRE.sub(lambda m: {"alpha": "a", "beta": "b"}.get(m.group(1), m.group(1)) + m.group(2), text)


def _walk(document: Any, locator: str) -> str | None:
    """The key paths this register uses for this repository: `a.b.c` and `a.b[requirement]`."""
    node = document
    for part in re.findall(r"[^.\[\]]+|\[[^\]]+\]", locator):
        if part.startswith("["):
            name = part[1:-1].lower()
            hits = [
                e for e in node if isinstance(e, str) and re.split(r"[\s\[<>=!~;@]", e, maxsplit=1)[0].lower() == name
            ]
            if len(hits) != 1:
                return None
            node = hits[0]
        elif isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    if not isinstance(node, str):
        return None
    match = re.search(r"(?:==|@)?\s*v?(\d[\w.\-+]*)\s*$", node)
    return match.group(1) if match else None


def declared_level(consumer: Consumer, root: Path) -> tuple[str | None, str]:
    """The Python level *consumer* declares, read from its checkout at *root*, and a note why not."""
    levels: dict[str, str] = {}
    for declaration in consumer.python_declarations:
        path = root / declaration.path
        if not path.is_file() or not path.name.endswith(".toml"):
            return None, f"{declaration.path} is not a TOML file in {root}"
        with path.open("rb") as handle:
            level = _walk(tomllib.load(handle), declaration.locator)
        if level is None:
            return None, f"{declaration.path} at {declaration.locator} does not resolve"
        levels[f"{declaration.path} {declaration.locator}"] = level
    if not levels:
        return None, f"the register points at no Python declaration for {consumer.id}"
    if len({normalize(v) for v in levels.values()}) > 1:
        return None, "its declarations disagree (FR-007): " + "; ".join(f"{k} = {v}" for k, v in levels.items())
    return next(iter(levels.values())), ""


# ---------------------------------------------------------------------------
# The network, behind two small seams so the tests need neither
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Response:
    url: str
    status: int = 0
    location: str = ""
    body: str = ""
    error: str = ""


class Web(Protocol):
    def get(self, url: str) -> Response: ...


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


class UrllibWeb:
    """One request, redirects NOT followed, so each hop's status can be judged on its own."""

    def __init__(self) -> None:
        self._opener = urllib.request.build_opener(_NoRedirect)

    def get(self, url: str) -> Response:
        request = urllib.request.Request(url, headers={"User-Agent": "idfkit-developers check_surfaces"})  # noqa: S310
        try:
            with self._opener.open(request, timeout=30) as reply:
                return Response(
                    url, reply.status, reply.headers.get("Location", ""), reply.read().decode("utf-8", "replace")
                )
        except urllib.error.HTTPError as reply:
            return Response(
                url, reply.code, reply.headers.get("Location", "") or "", reply.read().decode("utf-8", "replace")
            )
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            return Response(url, error=str(getattr(error, "reason", error)))


class Registry(Protocol):
    def npm(self, package: str) -> dict[str, Any]: ...

    def pypi(self, package: str) -> dict[str, Any]: ...

    def npm_exports(self, package: str, version: str, subpath: str) -> set[str] | None: ...


class HttpRegistry:
    def _json(self, url: str) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(url, timeout=30) as reply:  # noqa: S310
                return json.loads(reply.read())
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return {}
            raise

    def npm(self, package: str) -> dict[str, Any]:
        return self._json(f"https://registry.npmjs.org/{package.replace('/', '%2F')}")

    def pypi(self, package: str) -> dict[str, Any]:
        return self._json(f"https://pypi.org/pypi/{package}/json")

    def npm_exports(self, package: str, version: str, subpath: str) -> set[str] | None:
        tarball = (self.npm(package).get("versions", {}).get(version) or {}).get("dist", {}).get("tarball")
        if not tarball:
            return None
        with urllib.request.urlopen(tarball, timeout=60) as reply:  # noqa: S310
            data = reply.read()
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            files = {m.name.removeprefix("package/"): m for m in archive.getmembers() if m.isfile()}

            def read(name: str) -> str | None:
                member = files.get(name)
                extracted = archive.extractfile(member) if member else None
                return extracted.read().decode("utf-8", "replace") if extracted else None

            return exported_names(read, subpath)


_DECLARED = re.compile(
    r"export\s+(?:declare\s+)?(?:async\s+)?(?:function|const|let|class|interface|type|enum|namespace)\s+(\w+)"
)
_LISTED = re.compile(r"export\s+(?:type\s+)?\{([^}]*)\}")
_STAR = re.compile(r"export\s+\*\s+from\s+['\"](\.[^'\"]+)['\"]")


def _types_file(read: Any, subpath: str) -> str | None:
    """The declaration file a package's `exports` map names for *subpath*, or None."""
    manifest_text = read("package.json")
    if manifest_text is None:
        return None
    exports = json.loads(manifest_text).get("exports", {})
    key = "." if subpath in ("", ".") else f"./{subpath.lstrip('./')}"
    entry = exports.get(key) if isinstance(exports, dict) else None
    types = entry.get("types") if isinstance(entry, dict) else None
    return types.removeprefix("./") if isinstance(types, str) else None


def _names_in(text: str) -> set[str]:
    """Names one declaration file exports itself, declared or listed, under their exported alias."""
    names = set(_DECLARED.findall(text))
    for group in _LISTED.findall(text):
        for item in group.split(","):
            alias = item.strip().split(" as ")[-1].strip().removeprefix("type ").strip()
            if alias:
                names.add(alias)
    return names


def _star_targets(current: str, text: str) -> list[str]:
    """The sibling declaration files an `export * from './x.js'` in *current* can mean."""
    targets: list[str] = []
    for target in _STAR.findall(text):
        base = re.sub(r"\.js$", "", str(Path(Path(current).parent / target)))
        targets += [base + ".d.ts", base + "/index.d.ts"]
    return targets


def exported_names(read: Any, subpath: str) -> set[str] | None:
    """The names a package's *subpath* exports, from its type declarations. None when unknowable."""
    types = _types_file(read, subpath)
    if types is None:
        return None
    names: set[str] = set()
    seen: set[str] = set()
    pending = [types]
    while pending:
        current = pending.pop()
        text = None if current in seen else read(current)
        seen.add(current)
        if text is not None:
            names |= _names_in(text)
            pending += _star_targets(current, text)
    return names


class Sources(Protocol):
    """Where install instructions are read from."""

    def read(self, repository: str, path: str) -> str | None: ...


class GitHubSources:
    """Each repository's default branch, through `gh api`. A private repository needs a token."""

    def read(self, repository: str, path: str) -> str | None:
        result = subprocess.run(  # noqa: S603
            ["gh", "api", f"repos/{repository}/contents/{path}"],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            if "404" in result.stderr or "Not Found" in result.stderr:
                return None
            raise ConnectionError(result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "gh api failed")
        return base64.b64decode(json.loads(result.stdout)["content"]).decode("utf-8")


class WorkspaceSources:
    """Sibling checkouts, keyed by repository name. Reads the WORKING TREE, uncommitted edits included."""

    #: The web editor's repository is idfkit-app and its workspace checkout is envelop.
    ALIASES: ClassVar[dict[str, str]] = {"idfkit-app": "envelop"}

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

    def read(self, repository: str, path: str) -> str | None:
        name = repository.split("/", 1)[1]
        directory = self.workspace / self.ALIASES.get(name, name)
        if not directory.is_dir():
            raise ConnectionError(f"no checkout at {directory}")
        target = directory / path
        return target.read_text(encoding="utf-8") if target.is_file() else None


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    subject: str
    message: str
    #: failure, unreachable, or dormant. Only the first two change the exit status.
    kind: str = "failure"

    def render(self) -> str:
        return f"  [{self.kind.upper()}] {self.subject}: {self.message}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    passed: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        if any(f.kind == "failure" for f in self.findings):
            return 1
        if any(f.kind == "unreachable" for f in self.findings):
            return 2
        return 0


# ---------------------------------------------------------------------------
# Half A: the documentation hosts
# ---------------------------------------------------------------------------


def _title(body: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", body, flags=re.IGNORECASE | re.DOTALL)
    return " ".join(html.unescape(match.group(1)).split()) if match else "(no title)"


def _canonical(body: str) -> str:
    for tag in re.findall(r"<link\b[^>]*>", body, flags=re.IGNORECASE):
        if re.search(r"rel=[\"']?canonical", tag, flags=re.IGNORECASE):
            href = re.search(r"href=[\"']([^\"']+)", tag)
            return href.group(1) if href else "(canonical with no href)"
    return "(no canonical link)"


def check_retired(surface: Surface, web: Web) -> list[Finding]:
    url = f"https://{surface.host}/"
    for _ in range(MAX_HOPS):
        reply = web.get(url)
        if reply.error:
            return [
                Finding(
                    surface.host,
                    f"unreachable ({reply.error}); a host that cannot be checked is not retired",
                    "unreachable",
                )
            ]
        if reply.status in PERMANENT and reply.location:
            url = urllib.parse.urljoin(url, reply.location)
            if urllib.parse.urlsplit(url).hostname == surface.redirects_to:
                return []
            continue
        if reply.status in TEMPORARY:
            return [
                Finding(
                    surface.host,
                    f"answers with a temporary redirect ({reply.status}) to {reply.location}. A retirement is a "
                    "permanent redirect (301 or 308): a temporary one tells every search engine to keep the old address.",
                )
            ]
        if 200 <= reply.status < 300:
            return [
                Finding(
                    surface.host,
                    f"is retired and still answers {reply.status} with content: {_title(reply.body)!r}, "
                    f"{len(reply.body.encode('utf-8')):,} bytes, canonical {_canonical(reply.body)}. It must redirect "
                    f"permanently to {surface.redirects_to} (FR-031). Tracked in idfkit/idfkit-developers#15.",
                )
            ]
        return [
            Finding(
                surface.host,
                f"answers {reply.status} at {url}, which is neither content nor a redirect to {surface.redirects_to}",
            )
        ]
    return [Finding(surface.host, f"more than {MAX_HOPS} permanent redirects without reaching {surface.redirects_to}")]


def stated_levels(body: str) -> list[str]:
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return re.findall(r"\bidfkit\s+v?(\d+\.\d+\.\d+[\w.\-+]*)", text)


def check_serving(surface: Surface, web: Web, register: Register, root: Path) -> list[Finding]:
    reply = web.get(f"https://{surface.host}/")
    if reply.error:
        return [Finding(surface.host, f"unreachable ({reply.error}); not checked is not clean", "unreachable")]
    if reply.status != 200:
        return [Finding(surface.host, f"is recorded as serving and answers {reply.status}")]
    stated = stated_levels(reply.body)
    if not stated:
        return [
            Finding(
                surface.host,
                "serves pages that state no level, so a reader cannot tell which release they describe (FR-030)",
            )
        ]
    publisher = register.consumer(surface.published_by)
    if publisher is None or publisher.id != THIS_CONSUMER:
        return [
            Finding(
                surface.host,
                f"states idfkit {stated[0]}, and the level {surface.published_by} declares cannot be read from this "
                "repository. Not checked is not clean.",
                "unreachable",
            )
        ]
    declared, why = declared_level(publisher, root)
    if declared is None:
        return [Finding(surface.host, f"states idfkit {stated[0]}, and the declared level cannot be read: {why}")]
    if normalize(declared) not in {normalize(s) for s in stated}:
        return [
            Finding(
                surface.host,
                f"states idfkit {', '.join(sorted(set(stated)))} and {publisher.id} declares {declared}. The published "
                "site describes a level the repository no longer declares; deploy it, or correct the declaration.",
            )
        ]
    return []


def half_a(register: Register, web: Web, root: Path, report: Report) -> None:
    for surface in register.surfaces:
        if surface.status == "retired":
            found = check_retired(surface, web)
        elif surface.status == "serving":
            found = check_serving(surface, web, register, root)
        else:
            found = [Finding(surface.host, f"has status {surface.status!r}, which is neither serving nor retired")]
        report.findings += found
        if not found:
            report.passed.append(f"{surface.host} ({surface.status})")


# ---------------------------------------------------------------------------
# Half B: the install instructions
# ---------------------------------------------------------------------------

_INSTALL = re.compile(r"\b(pip3? install|uv pip install|uv add|npm (?:i|install|add)|pnpm add|yarn add)\s+(.+)")
_JS_IMPORT = re.compile(r"""import\s+(?:type\s+)?\{([^}]*)\}\s+from\s+['"]([^'"]+)['"]""")
_PY_IMPORT = re.compile(r"^\s*from\s+([\w.]+)\s+import\s+([\w, ]+)")


@dataclass(frozen=True)
class Symbol:
    module: str
    name: str


@dataclass(frozen=True)
class Instruction:
    source: str
    line: int
    text: str
    language: str
    packages: tuple[str, ...]
    symbols: tuple[Symbol, ...] = ()


def _package_name(token: str, language: str) -> str:
    token = token.strip("`'\",;)(")
    if language == "python":
        return re.split(r"[\[<>=!~;]", token, maxsplit=1)[0].lower()
    # `@idfkit/engine-assets@26.1` is the scoped name and a version; `idfkit@1.0` the bare name and one.
    if token.startswith("@"):
        return "@" + token[1:].partition("@")[0]
    return token.partition("@")[0]


def _governed(package: str, language: str) -> bool:
    if language == "python":
        return package == "idfkit"
    return package == "idfkit" or package in SCOPED or package.startswith("@idfkit/types-")


def _plain_lines(text: str, is_html: bool) -> list[str]:
    if not is_html:
        return text.splitlines()
    return [html.unescape(re.sub(r"<[^>]+>", "", line)) for line in text.splitlines()]


def extract_instructions(source: str, text: str, *, is_html: bool = False) -> list[Instruction]:
    """Every install instruction naming either library, with the symbols shown right after it."""
    lines = _plain_lines(text, is_html)
    found: list[Instruction] = []
    for index, line in enumerate(lines):
        match = _INSTALL.search(line)
        if match is None:
            continue
        language = "python" if match.group(1).startswith(("pip", "uv")) else "javascript"
        tokens = [t for t in match.group(2).split() if t and not t.startswith("-")]
        packages = tuple(p for p in (_package_name(t, language) for t in tokens) if p and re.match(r"^[@\w]", p))
        if not any(_governed(p, language) for p in packages):
            continue
        symbols: list[Symbol] = []
        for follow in lines[index + 1 : index + 7]:
            if _INSTALL.search(follow):
                break
            js = _JS_IMPORT.search(follow)
            if js and language == "javascript":
                symbols += [
                    Symbol(js.group(2), n.strip().removeprefix("type ").strip())
                    for n in js.group(1).split(",")
                    if n.strip()
                ]
            py = _PY_IMPORT.search(follow)
            if py and language == "python":
                symbols += [Symbol(py.group(1), n.strip()) for n in py.group(2).split(",") if n.strip()]
        found.append(Instruction(source, index + 1, " ".join(line.split()), language, packages, tuple(symbols)))
    return found


def _split_module(module: str) -> tuple[str, str]:
    """`@idfkit/core/node` is package `@idfkit/core`, subpath `node`."""
    parts = module.split("/")
    if module.startswith("@"):
        return "/".join(parts[:2]), "/".join(parts[2:])
    return parts[0], "/".join(parts[1:])


def check_instruction(instruction: Instruction, registry: Registry) -> list[Finding]:
    where = f"{instruction.source}:{instruction.line}"
    findings: list[Finding] = []
    published = PUBLISHED_NAME[instruction.language]
    governed = [p for p in instruction.packages if _governed(p, instruction.language)]
    if instruction.language == "javascript":
        facade = registry.npm(published)
        if not facade.get("versions"):
            findings.append(
                Finding(
                    where,
                    f"`{instruction.text}` would be held to `{published}` once the shared name publishes on npm, "
                    "which it has not, so nothing is demanded yet (FR-028).",
                    "dormant",
                )
            )
        elif published not in governed:
            findings.append(
                Finding(
                    where,
                    f"`{instruction.text}` names {', '.join(governed)}. The unification publishes `{published}` for "
                    "JavaScript, and an install instruction names what the unification publishes (FR-026). The scoped "
                    "packages stay supported for code already written against them; the instruction a stranger reads "
                    "names the shared name.",
                )
            )
    findings += check_symbols(instruction, registry)
    return findings


def check_symbols(instruction: Instruction, registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    where = f"{instruction.source}:{instruction.line}"
    for symbol in instruction.symbols:
        package, subpath = _split_module(symbol.module)
        if instruction.language == "javascript":
            version = (registry.npm(package).get("dist-tags") or {}).get("latest")
            names = registry.npm_exports(package, version, subpath) if version else None
            if names is None:
                findings.append(Finding(where, f"{symbol.name} from {symbol.module} could not be verified", "dormant"))
            elif symbol.name not in names:
                findings.append(
                    Finding(
                        where,
                        f"shows {symbol.name} from {symbol.module}, which {package}@{version} does not export (FR-029)",
                    )
                )
        else:
            version = (registry.pypi(package).get("info") or {}).get("version")
            findings += _python_symbol(where, symbol, version)
    return findings


def _python_symbol(where: str, symbol: Symbol, version: str | None) -> list[Finding]:
    try:
        from importlib import metadata

        installed = metadata.version(symbol.module.split(".")[0])
    except Exception:
        installed = None
    if version is None or installed is None or normalize(installed) != normalize(version):
        return [
            Finding(
                where,
                f"{symbol.name} from {symbol.module} is unverified: the installed {symbol.module.split('.')[0]} is "
                f"{installed}, and a reader installing today receives {version}",
                "dormant",
            )
        ]
    module = importlib.import_module(symbol.module)
    if not hasattr(module, symbol.name):
        return [
            Finding(where, f"shows {symbol.name} from {symbol.module}, which idfkit {version} does not export (FR-029)")
        ]
    return []


def instruction_sources(register: Register) -> list[tuple[str, str]]:
    """Every (repository, path) that may carry an install instruction: every README the register
    reaches, and the marketing page of every consumer that only teaches."""
    repositories = [c.repository for c in register.consumers] + list(register.libraries)
    pages = [(repository, "README.md") for repository in dict.fromkeys(repositories)]
    pages += [(c.repository, "index.html") for c in register.consumers if c.role == "teaches"]
    return pages


def half_b(register: Register, sources: Sources, registry: Registry, report: Report) -> None:
    for repository, path in instruction_sources(register):
        label = f"{repository}:{path}"
        try:
            text = sources.read(repository, path)
        except ConnectionError as error:
            report.findings.append(
                Finding(label, f"unreachable ({error}); its instructions were not checked", "unreachable")
            )
            continue
        if text is None:
            continue
        instructions = extract_instructions(label, text, is_html=path.endswith(".html"))
        for instruction in instructions:
            found = check_instruction(instruction, registry)
            report.findings += found
            # Dormant is not passed: an instruction held to nothing yet has not been shown right.
            if not found:
                report.passed.append(f"{instruction.source}:{instruction.line} `{instruction.text}`")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(register: Register, web: Web, sources: Sources, registry: Registry, root: Path, half: str) -> Report:
    report = Report()
    if half in ("a", "both"):
        half_a(register, web, root, report)
    if half in ("b", "both"):
        half_b(register, sources, registry, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--register", type=Path, help="consumers.toml from a working tree; an announced override of the pinned read"
    )
    parser.add_argument("--conformance-dir", type=Path, help="an idfkit-conformance checkout with its tags")
    parser.add_argument("--workspace", type=Path, help="read instructions from sibling checkouts instead of GitHub")
    parser.add_argument("--half", choices=["a", "b", "both"], default="both")
    args = parser.parse_args(argv)

    register = load_register(args.register, args.conformance_dir)
    sources: Sources = WorkspaceSources(args.workspace) if args.workspace else GitHubSources()
    report = run(register, UrllibWeb(), sources, HttpRegistry(), REPO_ROOT, args.half)

    print(f"surface check against {register.description}")
    for passed in report.passed:
        print(f"  [PASS] {passed}")
    for finding in report.findings:
        print(finding.render())
    counts = {kind: sum(f.kind == kind for f in report.findings) for kind in ("failure", "unreachable", "dormant")}
    print(
        f"{len(report.passed)} passed, {counts['failure']} failed, {counts['unreachable']} unreachable, {counts['dormant']} dormant"
    )
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
