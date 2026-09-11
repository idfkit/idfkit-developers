"""The build refuses when the page would state one library level and render another (004-FR-007).

Feature 004 measured that `uv lock --locked` does not catch `[tool.idfkit.library] level` moving
alone, because uv ignores `[tool.*]` tables. So the pinned-levels hook compares the stated level
with the installed idfkit, and these tests hold it to that. The hook is imported by path, the way
MkDocs imports it.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

_HOOK = Path(__file__).resolve().parents[1] / "docs" / "hooks" / "pinned_levels.py"


def _hook() -> Any:
    spec = importlib.util.spec_from_file_location("pinned_levels_under_test", _HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _levels(monkeypatch: pytest.MonkeyPatch, library: str) -> SimpleNamespace:
    for variable, value in (
        ("IDFKIT_CONFORMANCE_LEVEL", "conformance-2026.1"),
        ("IDFKIT_GOVERNANCE_LEVEL", "governance-2026.1"),
        ("IDFKIT_DOCS_LEVEL", "docs-2026.1"),
        ("IDFKIT_LIBRARY_LEVEL", library),
    ):
        monkeypatch.setenv(variable, value)
    monkeypatch.delenv("IDFKIT_LIBRARY_DIR", raising=False)
    return SimpleNamespace(extra={})


def test_the_installed_level_in_either_spelling_builds(monkeypatch: pytest.MonkeyPatch) -> None:
    installed = metadata.version("idfkit")
    semver = installed.replace("rc", "-rc.")
    config = _hook().on_config(_levels(monkeypatch, semver))
    assert config.extra["library_level"] == semver


def test_a_level_that_is_not_the_installed_one_refuses_to_build(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit, match="FR-007"):
        _hook().on_config(_levels(monkeypatch, "0.0.1"))


def test_the_unreleased_library_override_stands_aside(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _levels(monkeypatch, "0.0.1")
    monkeypatch.setenv("IDFKIT_LIBRARY_DIR", "/somewhere/idfkit")
    assert _hook().on_config(config).extra["library_level"] == "0.0.1"
