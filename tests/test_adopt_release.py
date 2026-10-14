"""The command that lists an adopted EnergyPlus release, against the committed pages."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import adopt_release
from adopt_release import TUTORIAL, VERSIONS_PAGE, CannotList, Release, with_listed_tuple, with_table_row

NEXT = Release(99, 1, 0)
PAGE = VERSIONS_PAGE.read_text(encoding="utf-8")
NOTEBOOK = TUTORIAL.read_text(encoding="utf-8")


def test_the_release_takes_the_first_open_row_and_no_row_is_rewritten() -> None:
    listed = with_table_row(PAGE, NEXT)
    before, after = PAGE.splitlines(), listed.splitlines()
    assert len(after) == len(before)
    differing = [(old, new) for old, new in zip(before, after, strict=True) if old != new]
    assert len(differing) == 1
    old, new = differing[0]
    assert new.endswith("| 99.1       | `99.1.0`   |") and new.startswith(old[:25]) and len(new) == len(old)


def test_a_full_table_gains_a_row() -> None:
    full = PAGE
    for patch in range(1, 10):
        if adopt_release._OPEN_ROW.search(full) is None:
            break
        full = with_table_row(full, Release(98, patch, 0))
    listed = with_table_row(full, NEXT)
    assert len(listed.splitlines()) == len(full.splitlines()) + 1
    assert "|            |            | 99.1       | `99.1.0`   |" in listed


def test_the_tuple_is_appended_to_the_printed_list() -> None:
    listed = with_listed_tuple(NOTEBOOK, NEXT)
    assert listed.count("(99, 1, 0)]") == 1 and len(listed) == len(NOTEBOOK) + len(", (99, 1, 0)")


def test_listing_twice_changes_nothing() -> None:
    assert with_table_row(with_table_row(PAGE, NEXT), NEXT) == with_table_row(PAGE, NEXT)
    assert with_listed_tuple(with_listed_tuple(NOTEBOOK, NEXT), NEXT) == with_listed_tuple(NOTEBOOK, NEXT)


def test_a_release_the_library_does_not_list_is_refused(capsys: pytest.CaptureFixture[str]) -> None:
    assert adopt_release.main(["99.1.0"]) == 1
    assert "does not list 99.1.0" in capsys.readouterr().err
    assert VERSIONS_PAGE.read_text(encoding="utf-8") == PAGE


def test_a_page_without_the_table_is_an_error() -> None:
    with pytest.raises(CannotList):
        with_table_row("no table here", NEXT)
