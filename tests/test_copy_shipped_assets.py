"""The weather browser's four files come from the library, and a missing one stops the build.

contracts/shipped-assets.md rule 4: if the installed distribution does not carry one of the
four, that is a change in what the library ships. It must surface as a build failure and NOT as
a page with a broken widget, because a broken widget is the kind of failure a reader finds
before a maintainer does.

The happy path is covered incidentally by every build. What needs a test is the failure path,
which nothing exercises until the day the library moves a file, and which must not be the day
anyone discovers this was written wrong.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from copy_shipped_assets import ASSETS, MissingAsset, copy_assets


@pytest.fixture
def fake_distribution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A directory shaped like an installed idfkit, carrying all four assets."""
    root = tmp_path / "site-packages" / "idfkit"
    for relative, _ in ASSETS:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f"contents of {relative}".encode())

    import copy_shipped_assets

    monkeypatch.setattr(copy_shipped_assets, "installed_package_root", lambda: root)
    return root


def test_all_four_are_copied(fake_distribution: Path, tmp_path: Path) -> None:
    destination = tmp_path / "docs" / "weather" / "browse"
    written = copy_assets(destination)

    assert len(written) == len(ASSETS) == 4
    for relative, name in ASSETS:
        assert (destination / name).read_bytes() == (fake_distribution / relative).read_bytes()


def test_the_destination_is_created(fake_distribution: Path, tmp_path: Path) -> None:
    destination = tmp_path / "does" / "not" / "exist" / "yet"
    assert not destination.exists()

    copy_assets(destination)

    assert destination.is_dir()


@pytest.mark.parametrize("absent", [relative for relative, _ in ASSETS])
def test_a_missing_asset_stops_the_build(fake_distribution: Path, tmp_path: Path, absent: str) -> None:
    """Each of the four, one at a time. A build must stop, not render a broken widget."""
    (fake_distribution / absent).unlink()
    destination = tmp_path / "docs" / "weather" / "browse"

    with pytest.raises(MissingAsset) as raised:
        copy_assets(destination)

    message = str(raised.value)
    assert absent in message, "the failure must name the file the library stopped shipping"
    assert "[tool.idfkit.library]" in message, "and say what fixes it"


def test_nothing_is_copied_when_one_is_missing(fake_distribution: Path, tmp_path: Path) -> None:
    """No partial copy. Three of four files is a page that half works, which is worse."""
    (fake_distribution / ASSETS[0][0]).unlink()
    destination = tmp_path / "docs" / "weather" / "browse"

    with pytest.raises(MissingAsset):
        copy_assets(destination)

    assert not destination.exists(), "the check must precede the first write, not follow it"


def test_the_four_are_the_ones_the_contract_names() -> None:
    """A fifth file, or a renamed one, is a contract change and should read as one here."""
    assert [name for _, name in ASSETS] == [
        "app.js",
        "index.html",
        "style.css",
        "stations.json.gz",
    ]
