#!/usr/bin/env python3
"""Mark, on the rendered pages of a PR preview, what the pull request changed.

A reviewer of a large documentation diff should not have to read the Markdown to find what moved on
the page. This script compares two built sites, the pull request's and its base branch's, page by
page, and writes the difference into the pull request's copy:

    data-pv="added"     on a block that has no counterpart in the base build
    data-pv="changed"   on a block that replaced one, followed by the old block in a
                        <template class="pv-previous"> the reviewer can unfold
    <details class="pv-removed">   where a base block no longer exists, collapsed
    data-pv-page="new|changed"     on the <article>, for the banner

and it links `preview-changes/changes.css` and `preview-changes/changes.js` into every page, which
draw the highlights, the toggle and the previous/next controls.

HOW A PAGE IS COMPARED

Only Material's `<article class="md-content__inner">` is compared, so a page whose navigation or
footer changed because another page was added is not reported. The article is cut into blocks:
paragraphs, headings, lists, tables, code blocks, admonitions, tab sets. A plain `<div>` that only
groups other blocks is descended into rather than treated as one block, which is what splits a
mkdocstrings API page (one `div.doc-object` per module, class and function, nested) into its
docstring paragraphs and parameter tables, so a one-line docstring edit marks one block and not the
whole module. Each block is fingerprinted without what renumbers when something above it moves:
`id`, `for`, `name`, in-page `href`, and the line-number column of a code block, which shifts when
the "Source code" an API page shows moves within its module. The two fingerprint sequences are
aligned with difflib.

WHY THIS RUNS ONLY IN THE PREVIEW JOB, AND NEVER TOUCHES docs/

Production is built by `deploy-docs.yml` from `docs/` and `mkdocs.yml`, and neither this script nor
its two assets live there or are named there. The only caller is `deploy-pr-docs.yml`, after the
preview build and before the copy into `gh-pages/pr-preview/pr-N/`. A production build is therefore
byte-for-byte the build it was before this file existed.

Standard library only: html.parser and difflib.

Usage::

    python scripts/annotate_preview.py --base base/site --head site [--summary changes.json]

Exit codes: 0 the head site was annotated (whether or not anything changed), 2 it could not run.
"""

from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ASSETS = Path(__file__).resolve().parent / "preview_changes"
"""The stylesheet and script copied into the annotated site. Outside docs/, so never in production."""

ASSET_DIR = "preview-changes"
"""Where, under the site root, the assets and the summary are served."""

VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"})

ATOMIC_CLASSES = frozenset({
    "highlight",
    "highlighttable",
    "admonition",
    "tabbed-set",
    "mermaid",
    "arithmatex",
    "jp-Cell",
})
"""A `<div>` with one of these classes is one block, however many blocks it contains."""

SKIPPED_CLASSES = frozenset({"md-content__button"})
"""The edit and view buttons: chrome, not content."""

SKIPPED_TAGS = frozenset({"script", "style", "template"})

_RENUMBERED = re.compile(r'\s(?:id|for|name|aria-labelledby|aria-describedby|aria-controls)="[^"]*"')
_LINE_NUMBERS = re.compile(r'<td class="linenos">.*?</td>', re.DOTALL)
_IN_PAGE_HREF = re.compile(r'href="#[^"]*"')
_WHITESPACE = re.compile(r"\s+")
_ID = re.compile(r'\sid="[^"]*"')
_TAG = re.compile(r"<[^>]+>")


@dataclass
class Element:
    """One element inside the article, with its position in the page source."""

    tag: str
    classes: frozenset[str]
    start: int
    name_end: int
    """Offset just past the tag name in the start tag, where an attribute can be inserted."""
    end: int = -1
    """Offset just past the end tag (or the start tag, for a void element)."""
    children: list[Element] = field(default_factory=lambda: list[Element]())
    has_text: bool = False


class _ArticleParser(HTMLParser):
    """Build the element tree of the page's `<article class="md-content__inner">`, with offsets."""

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self._line_starts = [0]
        for index, char in enumerate(source):
            if char == "\n":
                self._line_starts.append(index + 1)
        self.article: Element | None = None
        self._stack: list[Element] = []
        self._done = False

    def _offset(self) -> int:
        line, column = self.getpos()
        return self._line_starts[line - 1] + column

    def _open(self, tag: str, attrs: list[tuple[str, str | None]], *, closed: bool) -> None:
        if self._done:
            return
        classes = frozenset(next((value or "" for key, value in attrs if key == "class"), "").split())
        start = self._offset()
        raw = self.get_starttag_text() or f"<{tag}>"
        element = Element(tag, classes, start, start + 1 + len(tag))
        if self.article is None:
            if tag == "article" and "md-content__inner" in classes:
                self.article = element
                self._stack.append(element)
            return
        self._stack[-1].children.append(element)
        if closed or tag in VOID:
            element.end = start + len(raw)
        else:
            self._stack.append(element)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs, closed=False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs, closed=True)

    def handle_endtag(self, tag: str) -> None:
        if self._done or not self._stack or tag in VOID:
            return
        if not any(element.tag == tag for element in self._stack):
            return
        end = self._offset() + len(f"</{tag}>")
        while self._stack:
            element = self._stack.pop()
            element.end = end
            if element.tag == tag:
                break
        if not self._stack:
            self._done = True

    def handle_data(self, data: str) -> None:
        if self._stack and not self._done and data.strip():
            self._stack[-1].has_text = True


def parse_article(source: str) -> Element | None:
    """The page's article element, or None for a page without one (the 404 page, a redirect)."""
    parser = _ArticleParser(source)
    parser.feed(source)
    parser.close()
    article = parser.article
    if article is None or article.end < 0:
        return None
    return article


def blocks(element: Element) -> list[Element]:
    """The blocks of an element, in document order."""
    found: list[Element] = []
    for child in element.children:
        if child.tag in SKIPPED_TAGS or child.classes & SKIPPED_CLASSES:
            continue
        groups_blocks = child.tag in {"div", "section"} and not child.classes & ATOMIC_CLASSES
        if groups_blocks and child.children and not child.has_text:
            found.extend(blocks(child))
        else:
            found.append(child)
    return found


def fingerprint(fragment: str) -> str:
    """The block's markup without what renumbers when something above it moves."""
    fragment = _LINE_NUMBERS.sub("", fragment)
    fragment = _RENUMBERED.sub("", fragment)
    fragment = _IN_PAGE_HREF.sub('href="#"', fragment)
    return _WHITESPACE.sub(" ", fragment).strip()


def _summary_text(fragment: str, limit: int = 80) -> str:
    text = _WHITESPACE.sub(" ", html.unescape(_TAG.sub(" ", fragment))).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _removed(fragment: str) -> str:
    inert = _ID.sub("", fragment)
    summary = html.escape(_summary_text(fragment) or "a block")
    return f'<details class="pv-removed" data-pv="removed"><summary>Removed: {summary}</summary>{inert}</details>'


@dataclass
class PageDiff:
    """What changed on one page, as insertions into the head page's source."""

    status: str
    """`new`, `changed` or `unchanged`."""
    insertions: list[tuple[int, str]]
    counts: dict[str, int]


def _removed_at(head: Element, head_blocks: list[Element], index: int) -> int:
    """Where base blocks removed before head block `index` go: before it, or after the last one."""
    if index < len(head_blocks):
        return head_blocks[index].start
    if head_blocks:
        return head_blocks[-1].end
    return head.end - len("</article>")


def _mark(
    base_source: str, base_blocks: list[Element], head_source: str, head: Element
) -> tuple[list[tuple[int, str]], dict[str, int]]:
    """Align the two block sequences and turn every difference into an insertion into the head page."""
    base_prints = [fingerprint(base_source[b.start : b.end]) for b in base_blocks]
    head_blocks = blocks(head)
    head_prints = [fingerprint(head_source[b.start : b.end]) for b in head_blocks]
    insertions: list[tuple[int, str]] = []
    counts = {"added": 0, "changed": 0, "removed": 0}
    matcher = difflib.SequenceMatcher(None, base_prints, head_prints, autojunk=False)
    for opcode, b1, b2, h1, h2 in matcher.get_opcodes():
        if opcode == "equal":
            continue
        # A replaced run is read as edits in place, pairwise; what is left over on either side was
        # added or removed.
        paired = min(b2 - b1, h2 - h1) if opcode == "replace" else 0
        for offset in range(paired):
            old, new = base_blocks[b1 + offset], head_blocks[h1 + offset]
            previous = _ID.sub("", base_source[old.start : old.end])
            insertions.append((new.name_end, ' data-pv="changed"'))
            insertions.append((new.end, f'<template class="pv-previous">{previous}</template>'))
            counts["changed"] += 1
        for index in range(h1 + paired, h2):
            insertions.append((head_blocks[index].name_end, ' data-pv="added"'))
            counts["added"] += 1
        gone = base_blocks[b1 + paired : b2]
        if gone:
            removed = "".join(_removed(base_source[b.start : b.end]) for b in gone)
            insertions.append((_removed_at(head, head_blocks, h1 + paired), removed))
            counts["removed"] += len(gone)
    return insertions, counts


def diff_page(base_source: str | None, head_source: str) -> PageDiff | None:
    """Compare one page's two builds. None when the head page has no article to annotate."""
    head = parse_article(head_source)
    if head is None:
        return None
    if base_source is None:
        return PageDiff("new", [(head.name_end, ' data-pv-page="new"')], {"added": 0, "changed": 0, "removed": 0})
    base = parse_article(base_source)
    base_blocks = blocks(base) if base is not None else []
    insertions, counts = _mark(base_source, base_blocks, head_source, head)
    if not insertions:
        return PageDiff("unchanged", [], counts)
    insertions.append((head.name_end, ' data-pv-page="changed"'))
    return PageDiff("changed", insertions, counts)


def apply(source: str, insertions: list[tuple[int, str]]) -> str:
    """Insert each text at its offset. Offsets refer to the original source; ties keep their order."""
    pieces: list[str] = []
    cursor = 0
    for offset, text in sorted(insertions, key=lambda item: item[0]):
        pieces.append(source[cursor:offset])
        pieces.append(text)
        cursor = offset
    pieces.append(source[cursor:])
    return "".join(pieces)


def link_assets(source: str, depth: int) -> str:
    """Link the stylesheet in the head and the script at the end of the body.

    The script goes after Material's own bundle, which defines `document$`. It is linked from every
    page, unchanged ones included, because instant navigation keeps the scripts of the first page a
    reviewer opens and only swaps the content after that.
    """
    prefix = "../" * depth + ASSET_DIR + "/"
    stylesheet = f'<link rel="stylesheet" href="{prefix}changes.css">'
    script = f'<script src="{prefix}changes.js"></script>'
    if "</head>" in source:
        source = source.replace("</head>", stylesheet + "</head>", 1)
    if "</body>" in source:
        head, _, tail = source.rpartition("</body>")
        source = head + script + "</body>" + tail
    return source


def page_url(relative: Path) -> str:
    """The page's address relative to the site root, as MkDocs links it."""
    text = relative.as_posix()
    if text == "index.html":
        return ""
    if text.endswith("/index.html"):
        return text[: -len("index.html")]
    return text


def annotate(base_site: Path, head_site: Path) -> dict[str, Any]:
    """Annotate every page of `head_site` against `base_site`, copy the assets, and summarise."""
    pages: dict[str, dict[str, object]] = {}
    for page in sorted(head_site.rglob("*.html")):
        relative = page.relative_to(head_site)
        if relative.parts[0] == ASSET_DIR or relative.as_posix() == "404.html":
            continue
        head_source = page.read_text(encoding="utf-8")
        base_page = base_site / relative
        base_source = base_page.read_text(encoding="utf-8") if base_page.is_file() else None
        result = diff_page(base_source, head_source)
        if result is not None and result.status != "unchanged":
            head_source = apply(head_source, result.insertions)
            pages[page_url(relative)] = {"status": result.status, **result.counts}
        page.write_text(link_assets(head_source, len(relative.parts) - 1), encoding="utf-8")

    removed = sorted(
        page_url(page.relative_to(base_site))
        for page in base_site.rglob("*.html")
        if not (head_site / page.relative_to(base_site)).is_file()
        and parse_article(page.read_text(encoding="utf-8")) is not None
    )
    summary: dict[str, Any] = {"pages": pages, "removed": removed}

    target = head_site / ASSET_DIR
    target.mkdir(parents=True, exist_ok=True)
    for asset in ("changes.css", "changes.js"):
        shutil.copyfile(ASSETS / asset, target / asset)
    (target / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    parser.add_argument("--base", type=Path, required=True, help="the base branch's built site")
    parser.add_argument("--head", type=Path, required=True, help="the pull request's built site, annotated in place")
    parser.add_argument("--summary", type=Path, help="also write the summary JSON here")
    args = parser.parse_args(argv)
    for site in (args.base, args.head):
        if not (site / "index.html").is_file():
            print(f"{site} is not a built site: it has no index.html", file=sys.stderr)
            return 2
    summary = annotate(args.base, args.head)
    if args.summary:
        args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Annotated {len(summary['pages'])} changed or new page(s) in {args.head}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
