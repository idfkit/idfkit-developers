"""The naming map finds its register the way the parity page finds its ledger (feature 004, T117).

CI provides the conformance checkout through IDFKIT_CONFORMANCE_DIR and never through
IDFKIT_GOVERNANCE_DIR, which reads a working tree instead of the pinned tag. Until T117 the naming
map honoured only the second, so its `--check` could not run in CI at all.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import render_naming_map  # noqa: E402


def test_the_conformance_checkout_ci_provides_is_used(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("IDFKIT_GOVERNANCE_DIR", raising=False)
    monkeypatch.setenv("IDFKIT_CONFORMANCE_DIR", str(tmp_path))
    assert render_naming_map.resolve_register_path(None) == tmp_path.resolve() / "governance" / "naming.toml"


def test_the_override_still_wins_and_an_explicit_path_wins_over_both(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("IDFKIT_CONFORMANCE_DIR", str(tmp_path / "ci"))
    monkeypatch.setenv("IDFKIT_GOVERNANCE_DIR", str(tmp_path / "wt"))
    assert render_naming_map.resolve_register_path(None) == (tmp_path / "wt").resolve() / "naming.toml"
    explicit = tmp_path / "elsewhere.toml"
    assert render_naming_map.resolve_register_path(str(explicit)) == explicit.resolve()


def test_with_neither_the_sibling_checkout_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IDFKIT_GOVERNANCE_DIR", raising=False)
    monkeypatch.delenv("IDFKIT_CONFORMANCE_DIR", raising=False)
    expected = render_naming_map.REPO_ROOT.parent / "idfkit-conformance" / "governance" / "naming.toml"
    assert render_naming_map.resolve_register_path(None) == expected
