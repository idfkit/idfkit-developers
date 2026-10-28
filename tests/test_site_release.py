"""Guard the site-release helper behind deploy-docs.yml and release-on-level-change.yml.

``scripts/site_release.py`` is a maintainer script rather than part of a package, so it is loaded
by path, the way ``tests/test_check_page_kinds.py`` loads the gate it guards. The two git-reading
commands run against a throwaway repository in ``tmp_path``, never this one.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _REPO_ROOT / "scripts" / "site_release.py"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


release = _load("site_release", _SCRIPT)


def levels(**pinned: str) -> dict[str, Any]:
    return {"tool": {"idfkit": {name: {"level": level} for name, level in pinned.items()}}}


class TestNextTag:
    def test_the_first_release_of_a_year_is_one(self) -> None:
        assert release.next_tag([], 2026) == "site-2026.1"

    def test_counts_numerically_not_lexically(self) -> None:
        assert release.next_tag(["site-2026.9", "site-2026.10"], 2026) == "site-2026.11"

    def test_the_counter_restarts_each_year(self) -> None:
        assert release.next_tag(["site-2025.14"], 2026) == "site-2026.1"

    def test_ignores_tags_of_another_shape(self) -> None:
        tags = ["docs-2026.8", "governance-2026.22", "v1.0.0", "site-2026.x", "site-2026.3-rc"]
        assert release.next_tag(tags, 2026) == "site-2026.1"


class TestChangedLevels:
    def test_nothing_changed(self) -> None:
        pinned = levels(library="1.1.1", docs="docs-2026.8")
        assert release.changed_levels(pinned, pinned) == []

    def test_a_library_bump(self) -> None:
        before = levels(library="1.1.1", docs="docs-2026.8")
        after = levels(library="1.2.0", docs="docs-2026.8")
        assert release.changed_levels(before, after) == ["library: 1.1.1 -> 1.2.0"]

    def test_every_moved_level_is_reported_in_name_order(self) -> None:
        before = levels(library="1.1.1", docs="docs-2026.8", governance="governance-2026.22")
        after = levels(library="1.2.0", docs="docs-2026.9", governance="governance-2026.22")
        assert release.changed_levels(before, after) == [
            "docs: docs-2026.8 -> docs-2026.9",
            "library: 1.1.1 -> 1.2.0",
        ]

    def test_a_level_declared_on_one_side_only_counts(self) -> None:
        assert release.changed_levels(levels(), levels(conformance="conformance-2026.15")) == [
            "conformance: (none) -> conformance-2026.15"
        ]

    def test_other_tool_tables_are_not_levels(self) -> None:
        before = {"tool": {"idfkit": {"library": {"level": "1.1.1"}}, "ruff": {"line-length": 120}}}
        after = {"tool": {"idfkit": {"library": {"level": "1.1.1"}}, "ruff": {"line-length": 100}}}
        assert release.changed_levels(before, after) == []


def _git(root: Path, *args: str) -> str:
    return subprocess.run(  # noqa: S603
        ["git", "-C", str(root), *args],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


@pytest.fixture
def repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _commit(root: Path, library: str, message: str) -> str:
    (root / "pyproject.toml").write_text(f'[tool.idfkit.library]\nlevel = "{library}"\n')
    _git(root, "add", "pyproject.toml")
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


class TestCommandLine:
    def test_levels_changed_reads_both_commits(self, repository: Path, capsys: pytest.CaptureFixture[str]) -> None:
        before = _commit(repository, "1.1.1", "pin 1.1.1")
        after = _commit(repository, "1.2.0", "bump to 1.2.0")
        assert release.main(["levels-changed", before, after]) == 0
        assert capsys.readouterr().out == "library: 1.1.1 -> 1.2.0\n"

    def test_levels_changed_is_silent_for_a_page_edit(
        self, repository: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        before = _commit(repository, "1.1.1", "pin 1.1.1")
        (repository / "page.md").write_text("a page edit\n")
        _git(repository, "add", "page.md")
        _git(repository, "commit", "-q", "-m", "edit a page")
        assert release.main(["levels-changed", before, "HEAD"]) == 0
        assert capsys.readouterr().out == ""

    def test_an_unreadable_commit_exits_2(self, repository: Path) -> None:
        _commit(repository, "1.1.1", "pin 1.1.1")
        with pytest.raises(SystemExit) as exited:
            release.main(["levels-changed", "0" * 40, "HEAD"])
        assert exited.value.code == 2

    def test_next_tag_reads_the_repository_tags(self, repository: Path, capsys: pytest.CaptureFixture[str]) -> None:
        _commit(repository, "1.1.1", "pin 1.1.1")
        _git(repository, "tag", "site-2026.1")
        _git(repository, "tag", "site-2026.2")
        assert release.main(["next-tag", "--year", "2026"]) == 0
        assert capsys.readouterr().out == "site-2026.3\n"
