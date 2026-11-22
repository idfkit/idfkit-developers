"""The PR preview marks what the pull request changed, and nothing it did not.

The script runs only in the preview job, where a mistake is a reviewer misled rather than a broken
build, so nothing would notice it going wrong. These tests hold the comparison to what a reviewer
expects: an edited paragraph is changed, a new one added, a deleted one shown as removed, an edit
deep inside an API page marks one block and not the module, and blocks that only renumbered
because something was inserted above them are left alone.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from annotate_preview import apply, blocks, diff_page, fingerprint, main, page_url, parse_article


def _page(body: str) -> str:
    return (
        "<html><head><title>t</title></head><body><nav><p>nav</p></nav>"
        '<article class="md-content__inner md-typeset">'
        '<a href="edit" class="md-content__button">Edit</a>'
        f"{body}</article><footer>f</footer></body></html>"
    )


def _annotated(base: str, head: str) -> str:
    result = diff_page(_page(base), _page(head))
    assert result is not None
    return apply(_page(head), result.insertions)


def test_identical_pages_are_unchanged() -> None:
    body = "<h1 id='a'>A</h1><p>One.</p>"
    result = diff_page(_page(body), _page(body))
    assert result is not None
    assert result.status == "unchanged"
    assert result.insertions == []


def test_edited_paragraph_is_changed_and_keeps_the_old_version() -> None:
    out = _annotated("<p>Old text.</p><p>Same.</p>", "<p>New text.</p><p>Same.</p>")
    assert '<p data-pv="changed">New text.</p><template class="pv-previous"><p>Old text.</p></template>' in out
    assert "<p>Same.</p>" in out
    assert 'data-pv-page="changed"' in out


def test_inserted_and_removed_blocks() -> None:
    out = _annotated("<p>A</p><p>Gone</p><p>C</p>", "<p>A</p><p>C</p><p>D</p>")
    assert (
        '<details class="pv-removed" data-pv="removed"><summary>Removed: Gone</summary><p>Gone</p></details><p>C</p>'
        in out
    )
    assert '<p data-pv="added">D</p>' in out


def test_removed_block_drops_ids_so_anchors_stay_unique() -> None:
    out = _annotated('<h2 id="old">Old</h2><p>x</p>', "<p>x</p>")
    assert 'id="old"' not in out


def test_renumbered_ids_are_not_changes() -> None:
    base = '<div class="highlight"><pre id="__code_0"><a href="#__code_0_1">1</a></pre></div>'
    head = '<p>New.</p><div class="highlight"><pre id="__code_1"><a href="#__code_1_1">1</a></pre></div>'
    out = _annotated(base, head)
    assert '<p data-pv="added">' in out
    assert 'class="highlight" data-pv' not in out
    assert 'data-pv="changed"' not in out


def test_api_page_edit_marks_one_docstring_block() -> None:
    def api(doc: str) -> str:
        return (
            '<div class="doc doc-object"><h2 class="doc-heading">f</h2><div class="doc-contents">'
            f"<p>{doc}</p><table><tr><td>x</td></tr></table></div></div>"
        )

    out = _annotated(api("Old doc."), api("New doc."))
    assert '<p data-pv="changed">New doc.</p>' in out
    assert '<div class="doc doc-object">' in out
    assert "<table><tr>" in out


def test_atomic_blocks_are_not_split() -> None:
    article = parse_article(_page('<div class="admonition note"><p>a</p><p>b</p></div>'))
    assert article is not None
    found = blocks(article)
    assert [b.tag for b in found] == ["div"]


def test_edit_buttons_and_void_elements() -> None:
    source = _page("<p>a</p><hr><img src='x.png'/>")
    article = parse_article(source)
    assert article is not None
    assert [b.tag for b in blocks(article)] == ["p", "hr", "img"]
    assert [source[b.start : b.end] for b in blocks(article)][1:] == ["<hr>", "<img src='x.png'/>"]


def test_new_page_is_flagged_on_the_article() -> None:
    result = diff_page(None, _page("<p>x</p>"))
    assert result is not None
    assert result.status == "new"
    assert '<article data-pv-page="new" class=' in apply(_page("<p>x</p>"), result.insertions)


def test_page_without_article_is_skipped() -> None:
    assert diff_page(None, "<html><body>redirect</body></html>") is None


def test_fingerprint_ignores_whitespace_and_renumbering() -> None:
    assert fingerprint('<p id="a">x\n  y</p>') == fingerprint('<p id="b">x y</p>')


def test_page_url() -> None:
    assert page_url(Path("index.html")) == ""
    assert page_url(Path("guide/index.html")) == "guide/"
    assert page_url(Path("404.html")) == "404.html"


def test_annotate_writes_assets_summary_and_links(tmp_path: Path) -> None:
    base, head = tmp_path / "base", tmp_path / "head"
    for site in (base, head):
        (site / "guide").mkdir(parents=True)
        (site / "index.html").write_text(_page("<p>home</p>"), encoding="utf-8")
    (base / "guide" / "index.html").write_text(_page("<p>old</p>"), encoding="utf-8")
    (head / "guide" / "index.html").write_text(_page("<p>new</p>"), encoding="utf-8")
    (head / "fresh").mkdir()
    (head / "fresh" / "index.html").write_text(_page("<p>hi</p>"), encoding="utf-8")
    (base / "gone").mkdir()
    (base / "gone" / "index.html").write_text(_page("<p>bye</p>"), encoding="utf-8")

    assert main(["--base", str(base), "--head", str(head), "--summary", str(tmp_path / "s.json")]) == 0

    summary = json.loads((tmp_path / "s.json").read_text(encoding="utf-8"))
    assert summary["pages"]["guide/"]["status"] == "changed"
    assert summary["pages"]["fresh/"]["status"] == "new"
    assert "" not in summary["pages"]
    assert summary["removed"] == ["gone/"]
    for asset in ("changes.css", "changes.js", "summary.json"):
        assert (head / "preview-changes" / asset).is_file()
    home = (head / "index.html").read_text(encoding="utf-8")
    assert '<link rel="stylesheet" href="preview-changes/changes.css"></head>' in home
    assert '<script src="preview-changes/changes.js"></script></body>' in home
    guide = (head / "guide" / "index.html").read_text(encoding="utf-8")
    assert 'href="../preview-changes/changes.css"' in guide
    # The base site is read, never written.
    assert "preview-changes" not in (base / "guide" / "index.html").read_text(encoding="utf-8")


def test_main_refuses_a_directory_that_is_not_a_site(tmp_path: Path) -> None:
    assert main(["--base", str(tmp_path), "--head", str(tmp_path)]) == 2


def test_shifted_source_line_numbers_are_not_changes() -> None:
    def source(first: int) -> str:
        numbers = "".join(
            f'<span class="normal"><a href="#__codelineno-0-{n}">{n}</a></span>' for n in range(first, first + 2)
        )
        return (
            '<details class="quote"><summary>Source code</summary><div class="language-python highlight">'
            f'<table class="highlighttable"><tr><td class="linenos"><div class="linenodiv"><pre>{numbers}</pre></div></td>'
            '<td class="code"><pre><code>def f(): ...</code></pre></td></tr></table></div></details>'
        )

    result = diff_page(_page(source(64)), _page(source(72)))
    assert result is not None
    assert result.status == "unchanged"


def test_a_page_whose_only_change_is_outside_the_article_is_unchanged() -> None:
    base = _page("<p>Same.</p>")
    head = base.replace("<p>nav</p>", "<p>nav</p><p>a new page in the nav</p>")
    result = diff_page(base, head)
    assert result is not None
    assert result.status == "unchanged"


def test_a_base_page_without_an_article_makes_the_head_page_new() -> None:
    redirect = '<html><head><meta http-equiv="refresh" content="0; url=../x/"></head><body></body></html>'
    result = diff_page(redirect, _page("<p>Now a real page.</p>"))
    assert result is not None
    assert result.status == "new"
